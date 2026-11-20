"""hm211-v1 and hm337-v1 (docs/holistic-migration/FEATURES_ARMS_V2.md). hm153-v1 and hm1588-v1 are unchanged."""
import numpy as np

from .. import sequence
from ..features import RawFrame, pack_frame as pack_hm153

ANCHORS = (10, 1, 152, 234, 454, 33, 133, 362, 263, 70, 105, 107, 336, 334, 300, 61, 291, 13, 14)
WIDTH = {'hm211': 211, 'hm337': 337}
FACE = slice(153, 210)
FACE_MASK = 210


def pack_frame(frame: RawFrame) -> np.ndarray:
    """hm153 prefix, 19 shoulder-relative face anchors (z relative to the 478-point face mean), face mask."""
    prefix = pack_hm153(frame)
    if frame.face is not None and frame.face.shape != (478, 3):
        raise ValueError('face must have exact shape (478, 3)')
    row = np.zeros(211, dtype=np.float32)
    row[:153] = prefix
    if prefix[152] == 0 or frame.face is None:
        return row
    # same float64 expressions as face_features.pack_frame, then the anchor subset
    pose = frame.pose.astype(np.float64)
    center = (pose[11, :2] + pose[12, :2]) / 2
    delta = pose[11, :2] - pose[12, :2]
    width = np.hypot(delta[0], delta[1])
    face = frame.face.astype(np.float64)
    face[:, :2] = (face[:, :2] - center) / width
    face[:, 2] = (face[:, 2] - face[:, 2].mean()) / width
    row[FACE] = face[list(ANCHORS)].ravel()
    row[FACE_MASK] = 1
    if not np.isfinite(row).all():
        raise ValueError('normalized Float32 face anchors contain nonfinite values')
    return row


def grid_indices(timestamps, steps=30):
    """sequence/features nearest-observation rule on the integer grid; ties choose the earlier row."""
    t = [int(v) for v in timestamps]
    den, start, end = steps - 1, t[0], t[-1]
    return np.array([min(range(len(t)), key=lambda j: abs(t[j] * den - (start * den + i * (end - start))))
                     for i in range(steps)])


def bounded_observations(frames):
    """(timestamps, hm211 rows) of the actual observations in the hand interval of an eligible capture."""
    frames = list(frames)
    result = sequence.prepare_capture(frames)
    if result.reason != 'eligible':
        raise ValueError(f'capture is not eligible: {result.reason}')
    present = [i for i, f in enumerate(frames) if f.left_hand is not None or f.right_hand is not None]
    bounded = frames[present[0]:present[-1] + 1]
    return (np.array([f.timestamp_ms for f in bounded], dtype=np.int64),
            np.stack([pack_frame(f) for f in bounded]))


def prepare_capture(frames) -> sequence.CaptureResult:
    """hm153 eligibility and interval exactly; the face is optional."""
    from dataclasses import replace
    frames = list(frames)
    for f in frames:
        pack_frame(f)  # validate every observation, as the historical packers do
    result = sequence.prepare_capture(frames)
    if result.reason != 'eligible':
        return result
    t, rows = bounded_observations(frames)
    return replace(result, tensor=rows[grid_indices(t)])


def add_hand_local(x):
    """hm211 -> hm337: each present hand relative to its wrist, scaled by wrist-to-middle-MCP XY distance.
    Computed from the Float32 hm211 values, so it applies unchanged after augmentation."""
    x = np.asarray(x, dtype=np.float32)
    out = np.zeros(x.shape[:-1] + (337,), dtype=np.float32)
    out[..., :211] = x
    for start, mask, dest in [(0, 150, 211), (63, 151, 274)]:
        h = x[..., start:start + 63].reshape(x.shape[:-1] + (21, 3)).astype(np.float64)
        d = np.hypot(h[..., 9, 0] - h[..., 0, 0], h[..., 9, 1] - h[..., 0, 1])
        ok = (x[..., mask] == 1) & (d >= 1e-6)  # shortcut: degenerate hands get zero local channels, mask kept
        local = np.zeros_like(h)
        safe = np.where(ok, d, 1.0)[..., None, None]
        local[..., :2] = (h[..., :2] - h[..., 0:1, :2]) / safe
        local[..., 2] = h[..., 2] / safe[..., 0]
        local[~ok] = 0
        out[..., dest:dest + 63] = local.reshape(x.shape[:-1] + (63,))
    return out
