"""In-memory, self-paced diagnostic capture; not calibrated recognition."""
import numpy as np
import time
from .face_features import prepare_capture, pack_frame
from .verify_recognition import prepare_tensor


class ManualCapture:
    def __init__(self, model):
        self.model = model
        self.enabled = False
        self.state = 'TRACKING'
        self.frames = []
        self.result = None
        self.started = None
        self.submissions = 0
        self.prompt = 0
        self.inference_ms = self.decision_ms = self.collection_ms = 0.
        self.last_observed_wall = None

    def enable(self):
        self.enabled = True
        self.state = 'READY'

    def space(self, timestamp_ms):
        if not self.enabled:
            return
        if self.state != 'CAPTURING':
            self.frames = []
            self.result = None
            self.presentation = []
            self.started = timestamp_ms
            self.state = 'CAPTURING'
            return
        self.expire(timestamp_ms)
        if self.state != 'CAPTURING':
            return
        if self.frames and timestamp_ms-self.frames[-1].timestamp_ms > 250:
            self.cancel('observation_gap'); return
        self.collection_ms = timestamp_ms-self.started
        result = prepare_capture(self.frames)
        self.frames = []
        self.state = result.reason
        if result.tensor is not None:
            self.submissions += 1
            before = time.monotonic()
            output = np.asarray(self.model(result.tensor[None].astype(np.float32), training=False))
            self.inference_ms = (time.monotonic()-before)*1000
            if (output.shape != (1, 50) or not np.isfinite(output).all()
                    or (output < 0).any() or (output > 1).any()
                    or not np.isclose(output.sum(), 1., atol=1e-5)):
                self.state = 'invalid_probabilities'
                raise ValueError('classifier must return finite normalized (1,50) probabilities')
            self.result = output[0].copy()
            self.decision_ms = (time.monotonic()-self.last_observed_wall)*1000
            self.state = 'RESULT'

    def cancel(self, reason=None):
        self.frames = []
        self.result = None
        self.state = reason or ('READY' if self.enabled else 'TRACKING')

    def next_prompt(self, direction):
        self.cancel()
        self.prompt = (self.prompt + direction) % 50

    def expire(self, timestamp_ms):
        if self.state == 'CAPTURING' and timestamp_ms - self.started > 5000:
            self.cancel('too_long')

    def observe(self, frame):
        if self.state != 'CAPTURING':
            return
        self.expire(frame.timestamp_ms)
        if self.state != 'CAPTURING':
            return
        if self.frames and frame.timestamp_ms - self.frames[-1].timestamp_ms > 250:
            self.cancel('observation_gap'); return
        row = pack_frame(frame)
        if row[152] != 1:
            self.cancel('invalid_pose'); return
        if row[1587] != 1:
            self.cancel('invalid_face'); return
        if len(self.frames) >= 76:
            self.cancel('too_long'); return
        self.frames.append(frame)
        self.last_observed_wall = time.monotonic()


RAISE_MARGIN_Y = 0.02
RAISE_DEBOUNCE_FRAMES = 3
SEQUENCE_LENGTH = 30


class RaisedCapture(ManualCapture):
    """Confirmation observation starts the 30-row window; no debounce pre-roll."""
    def __init__(self, model):
        super().__init__(model)
        self.enabled = True
        self.state = 'WAITING_FOR_HAND'
        self.raised_count = self.lowered_count = 0
        self.armed = True
        self.last_timestamp = None
        self.presentation = []

    def cancel(self, reason=None):
        self.frames = []
        self.result = None
        self.state = 'WAITING_FOR_HAND'
        self.presentation = []
        self.raised_count = self.lowered_count = 0
        self.started = None

    def space(self, timestamp_ms):
        pass  # Keyboard input cannot start or finish automatic capture.

    def expire(self, timestamp_ms):
        if self.last_timestamp is not None and timestamp_ms-self.last_timestamp > 250:
            self.cancel()
        elif self.state == 'CAPTURING' and self.started is not None and timestamp_ms-self.started > 5000:
            self.cancel()

    def observe(self, frame):
        try:
            row = pack_frame(frame)
            timestamp = frame.timestamp_ms
            if (row[152] != 1 or row[1587] != 1
                    or not (row[150] == 1 or row[151] == 1)):
                self.cancel(); return
            if self.last_timestamp is not None and (timestamp <= self.last_timestamp
                    or timestamp-self.last_timestamp > 250):
                self.last_timestamp = timestamp
                self.cancel(); return
        except (ValueError, TypeError, AttributeError, IndexError, OverflowError):
            self.cancel(); return
        self.last_timestamp = timestamp
        threshold = float((frame.pose[11,1]+frame.pose[12,1])/2) - RAISE_MARGIN_Y
        raised = any(h is not None and h[0,1] < threshold
                     for h in (frame.left_hand, frame.right_hand))
        if self.state != 'CAPTURING':
            if not self.armed:
                # Absent hands never reach this known-visible-lowering branch.
                lowered = all(h is None or h[0,1] >= threshold + RAISE_MARGIN_Y
                              for h in (frame.left_hand, frame.right_hand))
                self.lowered_count = self.lowered_count + 1 if lowered else 0
                if self.lowered_count >= RAISE_DEBOUNCE_FRAMES:
                    self.armed = True
                    self.raised_count = 0
                return
            self.raised_count = self.raised_count + 1 if raised else 0
            if self.raised_count < RAISE_DEBOUNCE_FRAMES:
                return
            self.result = None
            self.presentation = []
            self.started = timestamp
            self.state = 'CAPTURING'
            self.armed = False
        self.frames.append(frame)
        self.last_observed_wall = time.monotonic()
        if timestamp-self.started > 5000:
            self.cancel(); return
        if len(self.frames) != SEQUENCE_LENGTH:
            return
        self._submit(timestamp)

    def _submit(self, timestamp):
        """One shared-seam inference of the buffered attempt; ineligible input cancels."""
        try:
            tensor = prepare_tensor(self.frames)
        except ValueError as error:
            self.cancel(str(error)); return
        self.collection_ms = timestamp-self.started
        self.frames = []
        try:
            self.submissions += 1
            before = time.monotonic()
            output = np.asarray(self.model(tensor[None], training=False))
            self.inference_ms = (time.monotonic()-before)*1000
            if (output.shape != (1,50) or not np.isfinite(output).all()
                    or (output < 0).any() or (output > 1).any()
                    or not np.isclose(output.sum(),1.,atol=1e-5)):
                raise ValueError('classifier must return finite normalized (1,50) probabilities')
            self.result = output[0].copy()
            self.decision_ms = (time.monotonic()-self.last_observed_wall)*1000
            self.state = 'RESULT'
        except BaseException:
            self.cancel()
            raise


HAND_OUT_OBSERVATIONS = 5  # consecutive valid hand-free 15 Hz observations, about 0.33 s


class PresenceCapture(RaisedCapture):
    """Owner-approved reference behavior. Hands out of view for HAND_OUT_OBSERVATIONS arm;
    a hand entering view starts an attempt; hands out of view again (or the optional
    SPACE) scores it once."""
    def __init__(self, model):
        super().__init__(model)
        self.armed = False  # hands must be out of view before every attempt, the first included
        self.absent = self.attempts = 0
        self.reason = None

    def cancel(self, reason=None):
        super().cancel()
        self.armed = False
        self.absent = 0
        self.reason = reason

    def space(self, timestamp_ms):
        if self.state == 'CAPTURING':
            self._submit(timestamp_ms)

    def expire(self, timestamp_ms):
        if self.state == 'CAPTURING' and timestamp_ms-self.last_timestamp > 250:
            self.cancel('observation_gap')

    def observe(self, frame):
        try:
            row = pack_frame(frame)
            gap = (self.last_timestamp is not None
                   and not 0 < frame.timestamp_ms-self.last_timestamp <= 250)
            self.last_timestamp = frame.timestamp_ms
            fault = ('observation_gap' if gap else 'invalid_pose' if row[152] != 1
                     else 'invalid_face' if row[1587] != 1 else None)
        except (ValueError, TypeError, AttributeError, IndexError, OverflowError):
            fault = 'invalid_observation'
        if fault:
            if self.state == 'CAPTURING':
                self.cancel(fault)
            else:  # hands can move unseen during a fault: require a fresh hands-out period
                self.armed, self.absent = False, 0
            return
        hand = frame.left_hand is not None or frame.right_hand is not None
        self.absent = 0 if hand else self.absent+1
        if self.state != 'CAPTURING':
            if not (hand and self.armed):
                self.armed = self.armed or self.absent >= HAND_OUT_OBSERVATIONS
                return
            self.result, self.presentation, self.reason = None, [], None
            self.frames, self.started = [], frame.timestamp_ms
            self.state, self.armed = 'CAPTURING', False
            self.attempts += 1
        self.frames.append(frame)
        self.last_observed_wall = time.monotonic()
        if hand and frame.timestamp_ms-self.started > 5000:
            self.cancel('too_long')
        elif self.absent >= HAND_OUT_OBSERVATIONS:
            self._submit(frame.timestamp_ms)
            self.armed = True  # both hands are already out of view


def presentation_rows(probabilities, labels):
    """Exactly three raw probabilities; dense index breaks equal-score ties."""
    p = np.asarray(probabilities)
    if (p.shape != (50,) or not np.isfinite(p).all() or (p < 0).any()
            or (p > 1).any() or not np.isclose(p.sum(),1.,atol=1e-5)
            or len(labels) != 50):
        raise ValueError('invalid probabilities or labels')
    indices = sorted(range(50), key=lambda i: (-float(p[i]), i))[:3]
    return [dict(rank=rank, index=i, label=labels[i], score=float(p[i]),
                 display_text=f"{rank}. {labels[i]}: {float(p[i]):.2f}".replace('’', "'"))
            for rank,i in enumerate(indices,1)]
