"""Pure NumPy hm153-v1 feature and temporal primitives."""
from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class RawFrame:
    """An observed timestamp and normalized image landmarks, not world coordinates."""

    timestamp_ms: int
    pose: np.ndarray | None
    left_hand: np.ndarray | None
    right_hand: np.ndarray | None
    face: np.ndarray | None = None


def _validate_component(name: str, array: np.ndarray | None, shape: tuple) -> None:
    if array is None:
        return
    if (type(array) is not np.ndarray or array.dtype.kind not in "iuf"
            or array.ndim != 2 or array.shape[1] != shape[1]
            or (shape[0] is not None and array.shape[0] != shape[0])):
        raise ValueError(f"{name} must be a plain real numeric ndarray of shape {shape}")
    if not np.isfinite(array).all():
        raise ValueError(f"{name} contains nonfinite values")


def _validate_timestamp(timestamp_ms: int) -> None:
    if type(timestamp_ms) is not int or timestamp_ms < 0:
        raise ValueError("timestamp_ms must be a nonnegative built-in int (not bool)")


def pack_frame(frame: RawFrame) -> np.ndarray:
    """Pack image landmarks into the exact hm153-v1 row-major layout."""
    if not isinstance(frame, RawFrame):
        raise ValueError("frame must be a RawFrame")
    _validate_timestamp(frame.timestamp_ms)
    for name, shape in (("pose", (33, 4)), ("left_hand", (21, 3)),
                        ("right_hand", (21, 3)), ("face", (None, 3))):
        _validate_component(name, getattr(frame, name), shape)
    pose = frame.pose
    if pose is None:
        return np.zeros(153, dtype=np.float32)
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        pose = pose.astype(np.float64)
        center = (pose[11, :3] + pose[12, :3]) / 2
        shoulder_delta = pose[11, :2] - pose[12, :2]
        width = np.hypot(shoulder_delta[0], shoulder_delta[1])
        if (pose[11, 3] < 0.5 or pose[12, 3] < 0.5
                or not np.isfinite(width) or width < 0.0001):
            return np.zeros(153, dtype=np.float32)
        hands = []
        for hand in (frame.left_hand, frame.right_hand):
            if hand is None:
                hands.append(np.zeros(63))
                continue
            normalized = hand.astype(np.float64)
            normalized[:, :2] = (normalized[:, :2] - center[:2]) / width
            normalized[:, 2] = (normalized[:, 2] - normalized[0, 2]) / width
            hands.append(normalized.ravel())
        selected = pose[11:17].copy()
        selected[:, :3] = (selected[:, :3] - center) / width
        selected[pose[11:17, 3] < 0.5] = 0
        masks = [frame.left_hand is not None, frame.right_hand is not None, 1]
        packed = np.concatenate((*hands, selected.ravel(), masks)).astype(np.float32)
    if not np.isfinite(packed).all():
        raise ValueError("normalized Float32 features contain nonfinite values")
    return packed


def resample_frames(frames: Sequence[RawFrame], steps: int = 30) -> np.ndarray:
    """Nearest actual observations on an even time grid; ties choose the earlier row."""
    if type(steps) is not int or steps < 2:
        raise ValueError("steps must be a built-in int at least 2 (not bool)")
    if len(frames) < 2:
        raise ValueError("at least two actual observations are required")
    rows = [pack_frame(frame) for frame in frames]
    if any(row[152] != 1 for row in rows):
        raise ValueError("every observed frame must have usable pose; gaps cannot be bridged")
    if any(later.timestamp_ms <= earlier.timestamp_ms
           for earlier, later in zip(frames, frames[1:])):
        raise ValueError("timestamps must be strictly increasing")
    denominator = steps - 1
    start, end = frames[0].timestamp_ms, frames[-1].timestamp_ms
    indices = [min(range(len(frames)),
                   key=lambda j: abs(frames[j].timestamp_ms * denominator
                                     - (start * denominator + i * (end - start))))
               for i in range(steps)]
    return np.stack([rows[index] for index in indices])



