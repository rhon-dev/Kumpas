"""Shared unmirrored RGB, observation cadence and bounded capture contract."""
from dataclasses import dataclass
import numpy as np
from .features import pack_frame, resample_frames


class ObservationClock:
    """Admit at most one real observation per quantized 15Hz slot."""

    def __init__(self):
        self.origin = None
        self.next_slot = 0
        self.last = None

    def admit(self, timestamp_ms: int) -> bool:
        if (type(timestamp_ms) is not int or timestamp_ms < 0
                or (self.last is not None and timestamp_ms <= self.last)):
            raise ValueError('timestamps must be nonnegative strictly increasing built-in ints')
        self.last = timestamp_ms
        if self.origin is None:
            self.origin = timestamp_ms
        slot = ((2 * (timestamp_ms - self.origin) + 1) * 15) // 2000
        if slot < self.next_slot:
            return False
        self.next_slot = slot + 1
        return True


@dataclass(frozen=True)
class CaptureResult:
    tensor: np.ndarray | None
    reason: str
    observation_count: int
    hand_count: int
    start_ms: int | None
    end_ms: int | None
    source_observation_count: int
    source_start_ms: int | None
    source_end_ms: int | None


def prepare_capture(frames) -> CaptureResult:
    """Prepare one bounded actual observed interval; never infer sign boundaries."""
    frames = list(frames)
    rows = [pack_frame(f) for f in frames]
    if any(b.timestamp_ms <= a.timestamp_ms for a, b in zip(frames, frames[1:])):
        raise ValueError('timestamps must be strictly increasing')
    present = [i for i, f in enumerate(frames)
               if f.left_hand is not None or f.right_hand is not None]
    source=(len(frames),frames[0].timestamp_ms if frames else None,frames[-1].timestamp_ms if frames else None)
    if not present:
        return CaptureResult(None, 'no_hands', 0, 0, None, None, *source)
    lo, hi = present[0], present[-1] + 1
    bounded, rows = frames[lo:hi], rows[lo:hi]
    n, hands = len(bounded), len(present)
    start, end = bounded[0].timestamp_ms, bounded[-1].timestamp_ms
    reason = 'eligible'
    if n < 8:
        reason = 'too_few_observations'
    elif hands < 4:
        reason = 'too_few_hand_observations'
    elif end - start < 400:
        reason = 'too_short'
    elif end - start > 5000:
        reason = 'too_long'
    elif any(b.timestamp_ms - a.timestamp_ms > 250 for a, b in zip(bounded, bounded[1:])):
        reason = 'observation_gap'
    elif any(row[152] != 1 for row in rows):
        reason = 'invalid_pose'
    tensor = resample_frames(bounded, steps=30) if reason == 'eligible' else None
    return CaptureResult(tensor, reason, n, hands, start, end, *source)



def prepare_image(rgb, cv) -> np.ndarray:
    """Plain RGB uint8, no mirror/color conversion, INTER_AREA 640 by 360."""
    if (type(rgb) is not np.ndarray or rgb.dtype != np.uint8 or rgb.ndim != 3
            or rgb.shape[2] != 3 or not rgb.shape[0] or not rgb.shape[1]):
        raise ValueError('rgb must be a plain nonempty HxWx3 uint8 ndarray')
    return np.ascontiguousarray(cv.resize(rgb, (640, 360), interpolation=cv.INTER_AREA))
