"""Automatic hand-presence Mac confidence viewer; never an accepted rejection policy."""
import argparse
from dataclasses import dataclass
import functools
import json
import math
from pathlib import Path
import time
from types import SimpleNamespace
from . import camera
from .webcam import HAND_CONNECTIONS, POSE_CONNECTIONS, prepare_rgb
from .recognition import PresenceCapture, presentation_rows
from .verify_recognition import AuditRun
import uuid
from .sequence import ObservationClock

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT.parent / 'holistic-migration-data'
FROZEN = DATA / 'evidence/phase-4-20261116/full-source-v1'
WINDOW = 'Kumpas - UNCALIBRATED confidence diagnostic'


@dataclass(frozen=True)
class Options:
    duration: float = 600.
    diagnostic_uncalibrated: bool = False
    classifier: Path = FROZEN / 'model.keras'
    detector: Path = DATA / 'holistic_landmarker.task'
    build_dir: Path = DATA / 'evidence/live-confidence-20261118/native'
    binding: Path | None = None
    status: Path | None = None
    audit_dir: Path | None = None


def validate_options(o):
    if (isinstance(o.duration, bool) or not isinstance(o.duration, (int, float))
            or not math.isfinite(o.duration) or not 0 < o.duration <= 900):
        raise ValueError('duration must be finite in (0,900]')
    if o.diagnostic_uncalibrated is not True:
        raise ValueError('--diagnostic-uncalibrated required: UNKNOWN/rejection unavailable')
    camera.external_directory(o.build_dir)
    for p in (o.classifier, o.detector):
        if not isinstance(p, Path) or not p.is_absolute():
            raise ValueError('asset paths must be absolute')
    if o.audit_dir is not None:
        camera.external_directory(o.audit_dir)
        if not o.audit_dir.is_absolute() or o.audit_dir.exists() or o.audit_dir.is_symlink():
            raise ValueError("audit directory must be new, absolute and external")
    if o.status:
        camera.external_directory(o.status.parent)
        if (not o.status.is_absolute() or o.status.suffix != '.json'
                or not o.status.parent.is_dir() or o.status.exists() or o.status.is_symlink()):
            raise ValueError('status must be a new external absolute .json file with existing parent')
    return o


def verify_assets(o):
    assets = {
        'classifier': (o.classifier, 'ea50489a27353cbf4f4e9b53b1a6252fa7c5c6a9f0021660347f7dcc1b1cda47'),
        'detector': (o.detector, 'e2dab61191e2dcd0a15f943d8e3ed1dce13c82dfa597b9dd39f562975a50c3f8'),
        'features': (ROOT/'docs/holistic-migration/FEATURES_FACE.md', 'f0c8021bd0ca8a227aa84169991345672966faa3648e75e0a62ea27155362c45'),
        'labels': (DATA/'hm1588-canonical-bundle-20261116-v1/class_metadata.json', 'b634bdeb19b2fbf7482bdd46f791f16725d6510275e5d552f29f3bfc7c628eb6'),
        'policy': (FROZEN/'policy.json', 'cfc992711743499f0d48eef01e44b17f14fe1173edce0a9728ee8cade067e035')}
    identities = {}
    for name, (path, expected) in assets.items():
        if camera.digest(path) != expected:
            raise ValueError('frozen asset identity mismatch: ' + name)
        identities[name] = expected
    classes = json.loads(assets['labels'][0].read_text())
    if len(classes) != 50 or [c['dense_id'] for c in classes] != list(range(50)):
        raise ValueError('invalid frozen dense label ordering')
    return [c['label'] for c in classes], identities


def load_runtime(o):
    import cv2
    import tensorflow as tf
    from .detector import HolisticDetector
    model = tf.keras.models.load_model(o.classifier, compile=False)
    if tuple(model.input_shape) not in ((None,30,1588), (1,30,1588)) or tuple(model.output_shape) not in ((None,50), (1,50)):
        raise ValueError('frozen model signature mismatch')
    return SimpleNamespace(cv=cv2, clock=time.monotonic, model=model,
                           capture=camera.OwnedCapture, detector=HolisticDetector,
                           build=camera.build_helper)


def read_binding(path):
    value = json.loads(path.read_text())
    binding = camera.NativeBinding(Path(value['source']), Path(value['binary']), path,
                                   value['source_sha256'], value['binary_sha256'])
    return camera.verify_binding(binding)


@functools.cache
def face_contours():
    from mediapipe.tasks.python.vision.face_landmarker import FaceLandmarksConnections
    return tuple((c.start, c.end) for c in FaceLandmarksConnections.FACE_LANDMARKS_CONTOURS)


def render_view(rgb, frame, c, fps, mirrored, cv):
    """Reference-video layout: full camera frame, landmarks, status line, bottom-left state."""
    image = cv.resize(cv.cvtColor(rgb, cv.COLOR_RGB2BGR), (1280, 720))
    def pixel(point):
        return int(min(1., max(0., point[0]))*1279), int(min(1., max(0., point[1]))*719)
    def lines(points, edges, color, width, visible=lambda i: True):
        if points is None:
            return
        for a, b in edges:
            if visible(a) and visible(b):
                cv.line(image, pixel(points[a]), pixel(points[b]), color, width, cv.LINE_AA)
    lines(frame.face, face_contours(), (150,230,150), 1)
    lines(frame.pose, POSE_CONNECTIONS, (235,235,235), 1, lambda i: frame.pose[i,3] >= .5)
    for hand in (frame.left_hand, frame.right_hand):
        lines(hand, HAND_CONNECTIONS, (255,120,60), 3)  # one colour: SDK left/right anatomy unverified
    if mirrored:
        image = cv.flip(image, 1)  # display only; detector input stays unmirrored
    def text(s, x, y, color=(255,255,255), scale=.6, thickness=1):
        cv.putText(image, s, (x,y), cv.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv.LINE_AA)
    cv.rectangle(image, (0,0), (1280,34), (0,0,0), -1)
    text(f"FPS {fps:.1f}  mirror {'ON' if mirrored else 'OFF'}  q quit  m mirror  r reset  space end", 12, 23)
    text('UNCALIBRATED - no UNKNOWN', 990, 23, (0,190,255), .55)
    if c.state == 'CAPTURING':
        text(f'REC {(c.last_timestamp-c.started)/1000:.1f} s', 20, 690, (60,60,255), 1.1, 3)
    elif c.presentation:
        for j, row in enumerate(c.presentation):
            text(row['display_text'], 20, 610+j*40, (90,230,90) if j == 0 else (255,255,255),
                 1.1 if j == 0 else .8, 3 if j == 0 else 2)
    else:
        if c.reason:
            text('Not scored: '+c.reason, 20, 640, (0,190,255), .7, 2)
        text('Raise your hands to sign' if c.armed else 'Lower your hands; keep face and shoulders in view',
             20, 690, scale=1., thickness=2)
    return image


def run_viewer(o, *, runtime=None):
    validate_options(o)
    labels, identities = verify_assets(o)
    status = dict(schema=1, mode='diagnostic_uncalibrated', live_ready=False,
                  terminal='starting', state='WAITING_FOR_HAND', processed=0, submissions=0,
                  attempts=0, identities=identities, source_failure=False)
    stream = o.status.open('x', encoding='utf-8') if o.status else None
    capture = detector = None; window = False; primary = None; c = None
    def publish():
        if stream:
            stream.seek(0); stream.write(json.dumps(status, sort_keys=True, allow_nan=False)+'\n')
            stream.truncate(); stream.flush()
    def retain(error):
        nonlocal primary
        if primary is None: primary = error
        else: primary.add_note('secondary cleanup/status failure: '+type(error).__name__)
        status['terminal'] = 'error'
    def persist(previous):
        """Save a new result before it is rendered; a failed save clears it and stops."""
        if c.result is not None and c.submissions > previous:
            try:
                rows = presentation_rows(c.result, labels)
                audit.save(c.result, rows)
                c.presentation = rows
            except BaseException:
                c.cancel()
                c.presentation = []
                raise
    try:
        publish()
        runtime = load_runtime(o) if runtime is None else runtime
        binding = read_binding(o.binding) if o.binding else runtime.build(o.build_dir)
        audit = AuditRun(o.audit_dir or DATA/"recognition-audits"/str(uuid.uuid4()), labels, identities)
        c = PresenceCapture(runtime.model)
        c.presentation = []
        started = runtime.clock(); deadline = started+o.duration
        capture = runtime.capture(binding, duration=900., startup_timeout=min(10.,o.duration))
        metadata = camera.validate_handshake(capture.metadata)
        detector = runtime.detector(o.detector)
        cv = runtime.cv; window = True
        cv.namedWindow(WINDOW, cv.WINDOW_NORMAL); cv.resizeWindow(WINDOW,1280,720)
        clock = ObservationClock(); mirrored = True; shown = False; last = 0
        last_wall = first_wall = None
        status['terminal'] = 'running'
        while runtime.clock() < deadline:
            capture.raise_if_failed()
            if last_wall is not None and c.last_timestamp is not None:
                c.expire(c.last_timestamp+int((runtime.clock()-last_wall)*1000))
            try:
                timestamp, payload = capture.next_frame(min(deadline,runtime.clock()+.05))
            except TimeoutError:
                pass
            else:
                if clock.admit(timestamp):
                    rgb = prepare_rgb(payload,metadata,cv)
                    f = detector.detect(rgb,timestamp)
                    previous = c.submissions
                    c.observe(f); last = timestamp
                    persist(previous)
                    last_wall = runtime.clock()
                    first_wall = last_wall if first_wall is None else first_wall
                    status['processed'] += 1
                    fps = (status['processed']-1)/max(last_wall-first_wall,1e-9)  # excludes camera startup
                    cv.imshow(WINDOW,render_view(rgb,f,c,fps,mirrored,cv))
                    shown = True
            key = cv.waitKey(1)&255
            capture.raise_if_failed()
            if key in (ord('q'),27): status['terminal']='quit'; break
            if cv.getWindowProperty(WINDOW,cv.WND_PROP_VISIBLE)<1:
                status['terminal']='window_closed'; break
            if key == ord('r'): c.cancel()
            if key == ord(' '):
                previous = c.submissions; c.space(last); persist(previous)
            if key == ord('m'): mirrored = not mirrored
            status.update(state=c.state,submissions=c.submissions,attempts=c.attempts)
            publish()
        else:
            status['terminal']='deadline'
    except BaseException as error:
        retain(error)
    finally:
        if capture is not None:
            try: capture.raise_if_failed()
            except BaseException as error:
                status['source_failure']=True; retain(error)
        for resource in (capture, detector):
            if resource is not None:
                try: resource.close()
                except BaseException as error: retain(error)
        if window:
            try: runtime.cv.destroyWindow(WINDOW)
            except BaseException as error: retain(error)
        if capture is not None:
            try: capture.raise_if_failed()
            except BaseException as error:
                status['source_failure']=True; retain(error)
        if c is not None:
            status.update(state=c.state,submissions=c.submissions,attempts=c.attempts)
            c.cancel()
        try: publish()
        except BaseException as error: retain(error)
        if stream:
            try: stream.close()
            except BaseException as error: retain(error)
    if primary is not None: raise primary
    return status


def main(argv=None):
    parser = argparse.ArgumentParser(description='Automatic hand-in/hand-out diagnostic; output-only audit')
    parser.add_argument('--diagnostic-uncalibrated', action='store_true')
    parser.add_argument('--duration', type=float, default=600.)
    parser.add_argument('--classifier', type=Path, default=Options.classifier)
    parser.add_argument('--detector', type=Path, default=Options.detector)
    parser.add_argument('--build-dir', type=Path, default=Options.build_dir)
    parser.add_argument('--binding', type=Path, help='verified native binding.json; skips compilation')
    parser.add_argument('--status', type=Path, help='new external operational JSON; no predictions/history')
    parser.add_argument('--audit-dir', type=Path, help='new external audit run; default fresh UUID')
    args = parser.parse_args(argv)
    try: options = validate_options(Options(**vars(args)))
    except ValueError as error: parser.error(str(error))
    return run_viewer(options)


if __name__ == '__main__': main()
