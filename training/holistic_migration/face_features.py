"""Additive hm1588-v1 image landmarks; historical hm153-v1 is unchanged."""
from dataclasses import replace
import numpy as np
from .sequence import CaptureResult, prepare_capture as prepare_historical
from .features import RawFrame, pack_frame as pack_historical

FEATURE_VERSION = 'hm1588-v1'
FEATURE_COUNT = 1588


def pack_frame(frame: RawFrame) -> np.ndarray:
    """Retain the exact historical prefix and shoulder-relative full face."""
    prefix = pack_historical(frame)
    if frame.face is not None and frame.face.shape != (478, 3):
        raise ValueError('face must have exact shape (478, 3)')
    row = np.zeros(FEATURE_COUNT, dtype=np.float32)
    row[:153] = prefix
    if prefix[152] == 0 or frame.face is None:
        return row
    with np.errstate(over='ignore', invalid='ignore', divide='ignore'):
        pose = frame.pose.astype(np.float64)
        center = (pose[11, :2] + pose[12, :2]) / 2
        delta = pose[11, :2] - pose[12, :2]
        width = np.hypot(delta[0], delta[1])
        face = frame.face.astype(np.float64)
        face[:, :2] = (face[:, :2] - center) / width
        face[:, 2] = (face[:, 2] - face[:, 2].mean()) / width
        row[153:1587] = face.ravel()
    row[1587] = 1
    if not np.isfinite(row).all():
        raise ValueError('normalized Float32 face features contain nonfinite values')
    return row


def resample_frames(frames, steps=30):
    """Nearest actual observations, integer grid, earlier-observation ties."""
    if type(steps) is not int or steps < 2:
        raise ValueError('steps must be a built-in int at least 2 (not bool)')
    frames = list(frames)
    if len(frames) < 2:
        raise ValueError('at least two actual observations are required')
    rows = [pack_frame(f) for f in frames]
    if any(row[152] != 1 or row[1587] != 1 for row in rows):
        raise ValueError('every observation requires usable pose and face; gaps cannot be bridged')
    if any(b.timestamp_ms <= a.timestamp_ms for a, b in zip(frames, frames[1:])):
        raise ValueError('timestamps must be strictly increasing')
    denominator = steps - 1
    start, end = frames[0].timestamp_ms, frames[-1].timestamp_ms
    indices = [min(range(len(frames)), key=lambda j: abs(
        frames[j].timestamp_ms * denominator - (start * denominator + i * (end - start))))
        for i in range(steps)]
    return np.stack([rows[i] for i in indices])


def prepare_capture(frames) -> CaptureResult:
    """Preserve historical reason precedence and bounded hand interval exactly."""
    frames = list(frames)
    rows = [pack_frame(f) for f in frames]  # validate even outside bounded interval
    result = prepare_historical(frames)
    if result.reason != 'eligible':
        return result
    present = [i for i, f in enumerate(frames)
               if f.left_hand is not None or f.right_hand is not None]
    lo, hi = present[0], present[-1] + 1
    if any(row[1587] != 1 for row in rows[lo:hi]):
        return replace(result, tensor=None, reason='invalid_face')
    return replace(result, tensor=resample_frames(frames[lo:hi]))
