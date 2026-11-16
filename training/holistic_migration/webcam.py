"""Visible tracking-only Mac preview; imports/preflight never access the runtime.

Run from the repository root with the existing combined environment:
python -E -B -m training.holistic_migration.webcam --model /absolute/official.task \
    --build-dir /absolute/external/build --duration 60
No classifier, recordings, default camera, or implicit operational report.
"""
import argparse
from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Any
import time
import uuid

from . import camera


@dataclass(frozen=True)
class Options:
    model: Path
    build_dir: Path
    duration: float = 60.
    report: Path | None = None


def validate_options(options):
    if (isinstance(options.duration, bool) or not isinstance(options.duration, (int, float))
            or not math.isfinite(options.duration) or not 0 < options.duration <= 300):
        raise ValueError("duration must be finite and in (0, 300] seconds")
    camera.external_directory(options.build_dir)
    if (not isinstance(options.model, Path) or not options.model.is_absolute()
            or not options.model.is_file() or options.model.stat().st_size == 0):
        raise ValueError("model must be an absolute path to a nonempty official .task bundle")
    if options.report is not None:
        report = options.report
        if not isinstance(report, Path) or not report.is_absolute() or report.suffix != ".json":
            raise ValueError("report must be an absolute .json path")
        camera.external_directory(report.parent)
        if not report.parent.is_dir() or report.exists() or report.is_symlink():
            raise ValueError("report parent must exist; overwrite is forbidden")
    return options


def main(argv=None):
    parser = argparse.ArgumentParser(description="Built-in MacBook only; tracking, not sign recognition")
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--build-dir", type=Path, required=True)
    parser.add_argument("--duration", type=float, default=60.)
    parser.add_argument("--report", type=Path, default=None,
                        help="optional exclusive operational JSON, never frames or landmarks")
    args = parser.parse_args(argv)
    try:
        options = validate_options(Options(**vars(args)))
    except ValueError as error:
        parser.error(str(error))
    return run_preview(options)


# Standard SDK landmark topology; no detector/feature implementation is duplicated.
POSE_CONNECTIONS = ((0,1),(1,2),(2,3),(3,7),(0,4),(4,5),(5,6),(6,8),
                    (9,10),(11,12),(11,13),(13,15),(15,17),(15,19),(15,21),
                    (17,19),(12,14),(14,16),(16,18),(16,20),(16,22),(18,20),
                    (11,23),(12,24),(23,24),(23,25),(24,26),(25,27),(26,28),
                    (27,29),(28,30),(29,31),(30,32),(27,31),(28,32))
HAND_CONNECTIONS = ((0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),
                    (5,9),(9,10),(10,11),(11,12),(9,13),(13,14),(14,15),(15,16),
                    (13,17),(0,17),(17,18),(18,19),(19,20))


def prepare_rgb(payload, metadata, cv):
    import numpy as np
    width, height = metadata["width"], metadata["height"]
    if len(payload) != width * height * 4:
        raise ValueError("actual BGRA payload length mismatch")
    bgra = np.frombuffer(payload, dtype=np.uint8).reshape(height, width, 4)
    rgb = np.ascontiguousarray(bgra[:, :, [2, 1, 0]])
    return cv.resize(rgb, (640, 360), interpolation=cv.INTER_AREA)


def render(rgb, frame, features, metadata, metrics, mirrored, cv):
    """Draw observations, then mirror pixels, then draw readable text."""
    image = cv.cvtColor(rgb, cv.COLOR_RGB2BGR)
    height, width = image.shape[:2]
    def draw(points, connections, color, pose=False):
        if points is None:
            return
        def pixel(point):
            return (int(min(1., max(0., point[0])) * (width-1)),
                    int(min(1., max(0., point[1])) * (height-1)))
        for left, right in connections:
            if not pose or (points[left,3] >= .5 and points[right,3] >= .5):
                cv.line(image, pixel(points[left]), pixel(points[right]), color, 1, cv.LINE_AA)
        for point in points:
            if not pose or point[3] >= .5:
                cv.circle(image, pixel(point), 2, color, -1, cv.LINE_AA)
    draw(frame.pose, POSE_CONNECTIONS, (80,220,80), pose=True)
    draw(frame.left_hand, HAND_CONNECTIONS, (255,180,40))
    draw(frame.right_hand, HAND_CONNECTIONS, (40,180,255))
    if mirrored:
        image = cv.flip(image, 1)
    count = lambda points: 0 if points is None else len(points)
    lines = ["TRACKING ONLY - no sign classifier",
             f"source {metadata['width']}x{metadata['height']} BGRA -> process 640x360 RGB",
             f"elapsed {metrics['elapsed']:.1f}s | processed {metrics['fps']:.1f} FPS",
             f"detector {metrics['detector_ms']:.1f}ms | packing {metrics['packing_ms']:.2f}ms",
             f"pose={count(frame.pose)} SDK L={count(frame.left_hand)} R={count(frame.right_hand)} face={count(frame.face)}",
             "candidate masks L/R/P=" + "/".join(str(int(x)) for x in features[150:153]),
             "SDK left/right: anatomy unverified",
             f"m: display mirror {'ON' if mirrored else 'OFF'} | q/Esc: quit"]
    for i, text in enumerate(lines):
        position = (8, 18 + 19*i)
        cv.putText(image, text, position, cv.FONT_HERSHEY_SIMPLEX, .43, (0,0,0), 3, cv.LINE_AA)
        cv.putText(image, text, position, cv.FONT_HERSHEY_SIMPLEX, .43, (255,255,255), 1, cv.LINE_AA)
    return image


WINDOW = "Kumpas - built-in Holistic tracking only"


def load_runtime():
    """Only called after argument/path admission; no classifier imports."""
    import cv2
    from importlib.metadata import version
    from types import SimpleNamespace
    from .detector import HolisticDetector
    from .features import pack_frame
    return SimpleNamespace(build=camera.build_helper, capture=camera.OwnedCapture,
                           detector=HolisticDetector, pack=pack_frame, cv=cv2,
                           clock=time.monotonic, detector_version=version("mediapipe"),
                           gui_version=cv2.__version__)


def run_preview(options, *, runtime=None):
    """One bounded tracking session; injection isolates hardware/GUI in unit tests.

    Deadlines bound pipe waits and loop admission; synchronous SDK inference and
    OS GUI calls are trusted and cannot be forcibly preempted inside this process.
    """
    validate_options(options)
    report_stream = options.report.open("x", encoding="utf-8") if options.report else None
    summary: dict[str, Any] = dict(schema=1, run_uuid=str(uuid.uuid4()), mode="tracking_only",
                   live_acceptance=False, terminal="error", source_failure=False,
                   duration_requested_s=options.duration,
                   processing_dimensions=[640,360], identities={},
                   counts=dict(processed=0,pose_frames=0,left_hand_frames=0,right_hand_frames=0,
                               face_frames=0,usable_pose_frames=0,mirror_toggles=0,
                               native_received=0,latest_overwrites=0,cleanup_errors=0),
                   timing=dict(elapsed_s=0.,processed_fps=0.,detector_mean_ms=None,
                               detector_max_ms=None,packing_mean_ms=None,packing_max_ms=None))
    capture = detector = None
    window_owned = False
    started = None
    primary = None
    cleanup_errors = []
    detector_total = packing_total = detector_max = packing_max = 0.

    def retain_finalization_error(stage, error):
        nonlocal primary
        if primary is None:
            primary = error
            summary["terminal"] = "interrupted" if isinstance(error, KeyboardInterrupt) else "error"
        else:
            # Keep actual secondary objects/causes off the structured operational JSON.
            primary.finalization_errors = (*getattr(primary, "finalization_errors", ()),
                                           (stage, error))
            primary.add_note(f"secondary {stage}: {type(error).__name__}")

    try:
        runtime = load_runtime() if runtime is None else runtime
        summary["identities"] = dict(model_sha256=camera.digest(options.model),
                                     mediapipe_version=runtime.detector_version,
                                     opencv_version=runtime.gui_version,
                                     sources={name:camera.digest(Path(__file__).with_name(name))
                                              for name in ("webcam.py","camera.py","camera.swift",
                                                           "detector.py","features.py")})
        binding = runtime.build(options.build_dir)
        summary["identities"]["native"] = dict(source_sha256=binding.source_sha256,
                                                  binary_sha256=binding.binary_sha256,
                                                  receipt=str(binding.receipt))
        started = runtime.clock()
        deadline = started + options.duration
        capture = runtime.capture(binding, duration=options.duration,
                                  startup_timeout=min(10., options.duration),
                                  frame_timeout=min(3., options.duration))
        metadata = camera.validate_handshake(capture.metadata)
        # No arbitrary handshake extension fields reach the operational report.
        summary["native_camera"] = {key:metadata[key] for key in
                                    ("width","height","pixel_format","frame_bytes",
                                     "device_type","continuity","device_sha256")}
        detector = runtime.detector(options.model)
        window_owned = True  # Attempt teardown even if window creation partially fails.
        runtime.cv.namedWindow(WINDOW, runtime.cv.WINDOW_AUTOSIZE)
        mirrored = True
        counts = summary["counts"]
        summary["terminal"] = "deadline"
        while runtime.clock() < deadline:
            try:
                timestamp, payload = capture.next_frame(min(deadline, runtime.clock()+.05))
            except TimeoutError:
                pass  # Keep the GUI responsive; native reader has its own fatal frame deadline.
            else:
                rgb = prepare_rgb(payload, metadata, runtime.cv)
                before = runtime.clock()
                frame = detector.detect(rgb, timestamp)
                detected = runtime.clock()
                features = runtime.pack(frame)
                packed = runtime.clock()
                detector_ms, packing_ms = (detected-before)*1000, (packed-detected)*1000
                detector_total += detector_ms; packing_total += packing_ms
                detector_max = max(detector_max, detector_ms); packing_max = max(packing_max, packing_ms)
                counts["processed"] += 1
                for component, key in ((frame.pose,"pose_frames"),(frame.left_hand,"left_hand_frames"),
                                       (frame.right_hand,"right_hand_frames"),(frame.face,"face_frames")):
                    counts[key] += int(component is not None and len(component) > 0)
                counts["usable_pose_frames"] += int(features[152] == 1)
                elapsed = max(packed-started, 1e-9)
                metrics = dict(elapsed=elapsed, fps=counts["processed"]/elapsed,
                               detector_ms=detector_ms, packing_ms=packing_ms)
                image = render(rgb, frame, features, metadata, metrics, mirrored, runtime.cv)
                runtime.cv.imshow(WINDOW, image)
            key = runtime.cv.waitKey(1) & 0xff
            if key in (ord("q"),27):
                summary["terminal"] = "quit"
                break
            if key == ord("m"):
                mirrored = not mirrored
                counts["mirror_toggles"] += 1
            if runtime.cv.getWindowProperty(WINDOW, runtime.cv.WND_PROP_VISIBLE) < 1:
                summary["terminal"] = "window_closed"
                break
    except BaseException as error:
        primary = error
        summary["terminal"] = "interrupted" if isinstance(error, KeyboardInterrupt) else "error"
    finally:
        if started is not None:
            summary["timing"]["elapsed_s"] = max(0., runtime.clock()-started)
        for resource in (capture, detector):
            if resource is not None:
                try:
                    resource.close()
                except BaseException as error:
                    cleanup_errors.append(error)
        if window_owned:
            try:
                runtime.cv.destroyWindow(WINDOW)
            except BaseException as error:
                cleanup_errors.append(error)
        if capture is not None:
            try:
                capture.raise_if_failed()
            except camera.CaptureError as error:
                summary["source_failure"] = True
                if primary is None:
                    primary = error
                    summary["terminal"] = "error"
            summary["counts"]["native_received"] = capture.received
            summary["counts"]["latest_overwrites"] = capture.dropped
            summary["native_exit"] = capture.process.returncode
        summary["counts"]["cleanup_errors"] = len(cleanup_errors)
        if cleanup_errors and primary is None:
            primary = cleanup_errors[0]
            summary["terminal"] = "cleanup_error"
        if capture is not None and capture.stderr_tail:
            import sys
            try:
                sys.stderr.write("native stderr tail:\n" + capture.stderr_tail.decode(errors="replace") + "\n")
            except BaseException as error:
                retain_finalization_error("diagnostic.stderr", error)
        count = summary["counts"]["processed"]
        elapsed = summary["timing"]["elapsed_s"]
        summary["timing"]["processed_fps"] = count/elapsed if elapsed else 0.
        if count:
            summary["timing"].update(detector_mean_ms=detector_total/count,detector_max_ms=detector_max,
                                     packing_mean_ms=packing_total/count,packing_max_ms=packing_max)
        if report_stream is not None:
            stage = "report.serialize"
            try:
                payload = json.dumps(summary, sort_keys=True, allow_nan=False)+"\n"
                stage = "report.write"
                report_stream.write(payload)
                stage = "report.flush"
                report_stream.flush()
            except BaseException as error:
                retain_finalization_error(stage, error)
            finally:
                try:
                    report_stream.close()
                except BaseException as error:
                    retain_finalization_error("report.close", error)
    if primary is not None:
        raise primary
    return summary


if __name__ == "__main__":
    main()
