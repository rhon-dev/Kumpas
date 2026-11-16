"""Lazy MediaPipe Tasks adapter; conversion itself has no native side effects."""
from numbers import Real
from pathlib import Path

import numpy as np

from .features import RawFrame, _validate_component, _validate_timestamp


def frame_from_result(result, timestamp_ms: int) -> RawFrame:
    """Copy normalized image landmarks from the flat Tasks Holistic result lists."""
    _validate_timestamp(timestamp_ms)

    def convert(name, pose=False):
        expected = 33 if pose else (None if name == "face_landmarks" else 21)
        try:
            points = getattr(result, name)
            if points is None or len(points) == 0:
                return None
            if expected is not None and len(points) != expected:
                raise ValueError(f"expected {expected} landmarks, received {len(points)}")
            rows = []
            for point in points:
                row = [point.x, point.y, point.z]
                if pose:
                    visibility = getattr(point, "visibility", None)
                    row.append(0.0 if visibility is None else visibility)
                if any(not isinstance(value, Real) or isinstance(value, (bool, np.bool_))
                       for value in row):
                    raise ValueError("landmark coordinates/visibility must be real numeric scalars")
                rows.append(row)
            array = np.array(rows, dtype=np.float64)
            _validate_component(name, array, (expected, 4 if pose else 3))
            return array
        except (AttributeError, TypeError, ValueError, OverflowError) as error:
            raise ValueError(f"malformed {name}: {error}") from error

    return RawFrame(timestamp_ms, convert("pose_landmarks", pose=True),
                    convert("left_hand_landmarks"), convert("right_hand_landmarks"),
                    convert("face_landmarks"))


class HolisticDetector:
    """One VIDEO-mode native tracker per unrelated clip/session; never share sessions."""

    def __init__(self, model_path: Path):
        if not isinstance(model_path, Path) or not model_path.is_file():
            raise ValueError("model_path must be a Path to an existing model bundle file")
        import mediapipe as mp

        options = mp.tasks.vision.HolisticLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=str(model_path), delegate=mp.tasks.BaseOptions.Delegate.CPU),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            output_face_blendshapes=False,
            output_segmentation_mask=False,
        )
        self._mp = mp
        self._last_timestamp_ms = None
        self._landmarker = mp.tasks.vision.HolisticLandmarker.create_from_options(options)

    def detect(self, rgb: np.ndarray, timestamp_ms: int) -> RawFrame:
        """Synchronously observe an unmirrored RGB image using VIDEO tracking."""
        if self._landmarker is None:
            raise RuntimeError("detector is closed; create a new instance for a new session")
        if (not isinstance(rgb, np.ndarray) or rgb.dtype != np.uint8
                or rgb.ndim != 3 or rgb.shape[2] != 3
                or rgb.shape[0] == 0 or rgb.shape[1] == 0):
            raise ValueError("rgb must be a nonempty H×W×3 RGB uint8 ndarray")
        _validate_timestamp(timestamp_ms)
        if self._last_timestamp_ms is not None and timestamp_ms <= self._last_timestamp_ms:
            raise ValueError("timestamp_ms must be strictly increasing per detector instance")
        image = self._mp.Image(image_format=self._mp.ImageFormat.SRGB,
                               data=np.ascontiguousarray(rgb))
        # Native tracking may have consumed this timestamp even if detection raises.
        self._last_timestamp_ms = timestamp_ms
        result = self._landmarker.detect_for_video(image, timestamp_ms)
        return frame_from_result(result, timestamp_ms)

    def close(self) -> None:
        """Release the owned tracker once, including on exceptional context exit."""
        landmarker = self._landmarker
        self._landmarker = None
        if landmarker is not None:
            landmarker.close()

    def __enter__(self) -> "HolisticDetector":
        if self._landmarker is None:
            raise RuntimeError("detector is closed")
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        self.close()
        return False




