"""SDK-shaped fixtures test the adapter, not native runtime or human anatomy."""
import dataclasses
import importlib
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
import unittest
from unittest import mock

import numpy as np

from training.holistic_migration import detector
from training.holistic_migration.features import RawFrame


def landmarks(count, visibility=0.8):
    return [SimpleNamespace(x=i / 100, y=i / 200, z=-i / 50,
                            visibility=visibility) for i in range(count)]


def sdk_result(**changes):
    values = dict(pose_landmarks=landmarks(33), left_hand_landmarks=landmarks(21),
                  right_hand_landmarks=landmarks(21), face_landmarks=landmarks(478),
                  pose_world_landmarks=landmarks(33, 0.01),
                  left_hand_world_landmarks=landmarks(21),
                  right_hand_world_landmarks=landmarks(21))
    values.update(changes)
    return SimpleNamespace(**values)


@dataclasses.dataclass
class FakeBaseOptions:
    model_asset_path: str
    delegate: object
    Delegate = SimpleNamespace(CPU=object())


@dataclasses.dataclass
class FakeHolisticOptions:
    base_options: FakeBaseOptions
    running_mode: object
    output_face_blendshapes: bool
    output_segmentation_mask: bool


class FakeNative:
    def __init__(self):
        self.calls = []
        self.close_calls = 0
        self.failure = None
        self.result = sdk_result()

    def detect_for_video(self, image, timestamp_ms):
        self.calls.append((image, timestamp_ms))
        if self.failure is not None:
            raise self.failure
        return self.result

    def close(self):
        self.close_calls += 1


def fake_sdk():
    """Strict public-signature fakes based on installed MediaPipe 1.2.0 source."""
    sdk = ModuleType("mediapipe")
    native = FakeNative()
    created = []
    images = []
    def create_from_options(options):
        created.append(options)
        return native
    def image(*, image_format, data):
        value = SimpleNamespace(image_format=image_format, data=data)
        images.append(value)
        return value
    sdk.Image = image
    sdk.ImageFormat = SimpleNamespace(SRGB=object())
    sdk.tasks = SimpleNamespace(BaseOptions=FakeBaseOptions, vision=SimpleNamespace(
        HolisticLandmarkerOptions=FakeHolisticOptions,
        RunningMode=SimpleNamespace(VIDEO=object()),
        HolisticLandmarker=SimpleNamespace(create_from_options=create_from_options)))
    return sdk, native, created, images


class DetectorPreflightTests(unittest.TestCase):
    def test_construction_uses_tasks_video_cpu_and_disabled_optional_outputs(self):
        sdk, native, created, images = fake_sdk()
        with mock.patch.dict(sys.modules, {"mediapipe": sdk}):
            instance = detector.HolisticDetector(Path(__file__))
        self.addCleanup(instance.close)
        self.assertEqual(len(created), 1)
        options = created[0]
        self.assertEqual(options.base_options.model_asset_path, str(Path(__file__)))
        self.assertIs(options.base_options.delegate, FakeBaseOptions.Delegate.CPU)
        self.assertIs(options.running_mode, sdk.tasks.vision.RunningMode.VIDEO)
        self.assertIs(options.output_face_blendshapes, False)
        self.assertIs(options.output_segmentation_mask, False)
        self.assertEqual(native.calls, [])
        self.assertEqual(images, [])
        self.assertIsNotNone(instance)

    def test_detect_feeds_unmirrored_rgb_to_video_and_returns_converted_frame(self):
        sdk, native, created, images = fake_sdk()
        with mock.patch.dict(sys.modules, {"mediapipe": sdk}):
            instance = detector.HolisticDetector(Path(__file__))
        self.addCleanup(instance.close)
        self.assertTrue(hasattr(instance, "detect"), "missing detect")
        rgb = np.arange(2 * 4 * 3, dtype=np.uint8).reshape(2, 4, 3)
        before = rgb.copy()
        actual = instance.detect(rgb, 0)
        self.assertEqual(len(native.calls), 1)
        self.assertEqual(native.calls[0][1], 0)
        self.assertIs(images[0].image_format, sdk.ImageFormat.SRGB)
        np.testing.assert_array_equal(images[0].data, before)
        np.testing.assert_array_equal(rgb, before)
        self.assertEqual(actual.timestamp_ms, 0)
        np.testing.assert_array_equal(actual.pose[11], [0.11, 0.055, -0.22, 0.8])

    def test_invalid_api_rgb_or_timestamp_is_rejected_before_any_native_call(self):
        sdk, native, created, images = fake_sdk()
        with mock.patch.dict(sys.modules, {"mediapipe": sdk}):
            instance = detector.HolisticDetector(Path(__file__))
        self.addCleanup(instance.close)
        invalid_rgb = [None, [[[0, 0, 0]]], np.zeros((3, 3), np.uint8),
                       np.zeros((3, 3, 4), np.uint8), np.zeros((0, 3, 3), np.uint8),
                       np.zeros((3, 0, 3), np.uint8), np.zeros((1, 2, 3, 3), np.uint8),
                       np.zeros((3, 3, 3), np.float32), np.zeros((3, 3, 3), np.int8)]
        for rgb in invalid_rgb:
            with self.subTest(shape=getattr(rgb, "shape", None), dtype=getattr(rgb, "dtype", None)):
                with self.assertRaisesRegex(ValueError, "RGB|rgb"):
                    instance.detect(rgb, 0)
        rgb = np.zeros((2, 2, 3), np.uint8)
        for stamp in (-1, True, False, 1.0, np.int64(1), None, "1"):
            with self.subTest(stamp=stamp):
                with self.assertRaisesRegex(ValueError, "timestamp"):
                    instance.detect(rgb, stamp)
        self.assertEqual(native.calls, [])
        self.assertEqual(images, [])
        self.assertEqual(instance.detect(rgb, 0).timestamp_ms, 0)

    def test_timestamps_strictly_increase_per_instance_and_new_instance_resets(self):
        sdk, native, created, images = fake_sdk()
        with mock.patch.dict(sys.modules, {"mediapipe": sdk}):
            instance = detector.HolisticDetector(Path(__file__))
        self.addCleanup(instance.close)
        rgb = np.zeros((2, 2, 3), np.uint8)
        instance.detect(rgb, 10)
        for stamp in (10, 9, 0):
            with self.subTest(stamp=stamp):
                with self.assertRaisesRegex(ValueError, "timestamp|increasing"):
                    instance.detect(rgb, stamp)
        self.assertEqual(len(native.calls), 1)
        self.assertEqual(len(images), 1)
        instance.detect(rgb, 11)
        second_sdk, second_native, _, _ = fake_sdk()
        with mock.patch.dict(sys.modules, {"mediapipe": second_sdk}):
            second = detector.HolisticDetector(Path(__file__))
        self.addCleanup(second.close)
        self.assertEqual(second.detect(rgb, 0).timestamp_ms, 0)
        self.assertEqual([stamp for _, stamp in native.calls], [10, 11])
        self.assertEqual([stamp for _, stamp in second_native.calls], [0])

    def test_context_manager_closes_once_on_body_exception_and_is_not_reusable(self):
        sdk, native, created, images = fake_sdk()
        with mock.patch.dict(sys.modules, {"mediapipe": sdk}):
            instance = detector.HolisticDetector(Path(__file__))
        self.addCleanup(instance.close)
        self.assertTrue(hasattr(instance, "__enter__"), "missing context ownership")
        with self.assertRaisesRegex(RuntimeError, "body failure"):
            with instance as owned:
                self.assertIs(owned, instance)
                raise RuntimeError("body failure")
        self.assertEqual(native.close_calls, 1)
        instance.close()
        self.assertEqual(native.close_calls, 1)
        with self.assertRaisesRegex(RuntimeError, "closed"):
            instance.detect(np.zeros((1, 1, 3), np.uint8), 0)
        with self.assertRaisesRegex(RuntimeError, "closed"):
            with instance:
                self.fail("closed instances cannot be reopened")
        self.assertEqual(native.calls, [])
        self.assertEqual(images, [])

    def test_native_failure_consumes_timestamp_and_context_still_closes(self):
        sdk, native, created, images = fake_sdk()
        with mock.patch.dict(sys.modules, {"mediapipe": sdk}):
            instance = detector.HolisticDetector(Path(__file__))
        self.addCleanup(instance.close)
        native.failure = RuntimeError("native failure")
        rgb = np.zeros((1, 1, 3), np.uint8)
        with self.assertRaisesRegex(RuntimeError, "native failure"):
            instance.detect(rgb, 5)
        native.failure = None
        with self.assertRaisesRegex(ValueError, "timestamp|increasing"):
            instance.detect(rgb, 5)
        self.assertEqual(len(native.calls), 1)
        with instance:
            self.assertEqual(instance.detect(rgb, 6).timestamp_ms, 6)
        self.assertEqual(native.close_calls, 1)

    def test_conversion_failure_inside_context_releases_tracker(self):
        sdk, native, created, images = fake_sdk()
        native.result = sdk_result(pose_landmarks=landmarks(32))
        with mock.patch.dict(sys.modules, {"mediapipe": sdk}):
            instance = detector.HolisticDetector(Path(__file__))
        self.addCleanup(instance.close)
        with self.assertRaisesRegex(ValueError, "pose_landmarks"):
            with instance:
                instance.detect(np.zeros((1, 1, 3), np.uint8), 0)
        self.assertEqual(native.close_calls, 1)
        instance.close()
        self.assertEqual(native.close_calls, 1)

    def test_native_failure_inside_context_releases_tracker(self):
        sdk, native, created, images = fake_sdk()
        native.failure = RuntimeError("native context failure")
        with mock.patch.dict(sys.modules, {"mediapipe": sdk}):
            instance = detector.HolisticDetector(Path(__file__))
        self.addCleanup(instance.close)
        with self.assertRaisesRegex(RuntimeError, "native context failure"):
            with instance:
                instance.detect(np.zeros((1, 1, 3), np.uint8), 0)
        self.assertEqual(native.close_calls, 1)

    def test_package_imports_are_lazy_without_mediapipe_or_tensorflow(self):
        import subprocess
        script = """
import builtins
import sys
original = builtins.__import__
def guarded(name, *args, **kwargs):
    if name.split('.')[0] in {'mediapipe', 'tensorflow'}:
        raise AssertionError('forbidden eager native import: ' + name)
    return original(name, *args, **kwargs)
builtins.__import__ = guarded
import training.holistic_migration.features
import training.holistic_migration.detector
assert 'mediapipe' not in sys.modules
assert 'tensorflow' not in sys.modules
print('lazy imports verified')
"""
        result = subprocess.run([sys.executable, "-E", "-B", "-c", script],
                                cwd=Path(__file__).resolve().parents[3],
                                text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), "lazy imports verified")

    def test_noncontiguous_rgb_keeps_channel_order_and_observations(self):
        sdk, native, created, images = fake_sdk()
        with mock.patch.dict(sys.modules, {"mediapipe": sdk}):
            instance = detector.HolisticDetector(Path(__file__))
        self.addCleanup(instance.close)
        rgb = np.arange(3 * 6 * 3, dtype=np.uint8).reshape(3, 6, 3)[:, ::2, :]
        self.assertFalse(rgb.flags.c_contiguous)
        with instance:
            actual = instance.detect(rgb, 0)
        self.assertTrue(images[0].data.flags.c_contiguous)
        np.testing.assert_array_equal(images[0].data, rgb)
        self.assertEqual(actual.pose.shape, (33, 4))
        self.assertEqual(native.close_calls, 1)

    def test_invalid_model_path_rejected_before_any_mediapipe_import(self):
        self.assertTrue(hasattr(detector, "HolisticDetector"), "missing HolisticDetector")
        import builtins
        real_import = builtins.__import__
        imports = []
        def guarded_import(name, *args, **kwargs):
            if name == "mediapipe" or name.startswith("mediapipe."):
                imports.append(name)
                raise AssertionError("invalid path must not import native SDK")
            return real_import(name, *args, **kwargs)
        with mock.patch("builtins.__import__", side_effect=guarded_import):
            for path in (None, "model.task", 1, Path(__file__).parent,
                         Path(__file__).parent / "absent-model.task"):
                with self.subTest(path=path):
                    with self.assertRaisesRegex(ValueError, "model_path"):
                        detector.HolisticDetector(path)
        self.assertEqual(imports, [])


class ResultConversionTests(unittest.TestCase):
    def test_empty_components_are_none_and_one_handed_results_remain_distinct(self):
        empty = detector.frame_from_result(sdk_result(pose_landmarks=[],
                    left_hand_landmarks=[], right_hand_landmarks=[], face_landmarks=[]), 0)
        for name in ("pose", "left_hand", "right_hand", "face"):
            self.assertIsNone(getattr(empty, name))
        for missing, observed in (("left_hand", "right_hand"), ("right_hand", "left_hand")):
            with self.subTest(missing=missing):
                frame = detector.frame_from_result(sdk_result(**{missing + "_landmarks": []}), 1)
                self.assertIsNone(getattr(frame, missing))
                self.assertEqual(getattr(frame, observed).shape, (21, 3))
                self.assertEqual(frame.pose.shape, (33, 4))
        frame = detector.frame_from_result(sdk_result(pose_landmarks=None,
                     left_hand_landmarks=None, right_hand_landmarks=None, face_landmarks=None), 2)
        self.assertIsNone(frame.pose)
        self.assertIsNone(frame.face)

    def test_requires_exact_pose_hand_counts_and_flat_sdk_shape(self):
        for name, count in (("pose_landmarks", 33), ("left_hand_landmarks", 21),
                            ("right_hand_landmarks", 21)):
            for wrong in (1, count - 1, count + 1):
                with self.subTest(name=name, count=wrong):
                    with self.assertRaisesRegex(ValueError, name):
                        detector.frame_from_result(sdk_result(**{name: landmarks(wrong)}), 0)
            with self.subTest(name=name, nested=True):
                with self.assertRaisesRegex(ValueError, name):
                    detector.frame_from_result(sdk_result(**{name: [landmarks(count)]}), 0)
        with self.assertRaisesRegex(ValueError, "pose_landmarks"):
            detector.frame_from_result(SimpleNamespace(), 0)

    def test_missing_or_none_pose_visibility_is_zero_not_fabricated_confidence(self):
        result = sdk_result()
        del result.pose_landmarks[11].visibility
        result.pose_landmarks[12].visibility = None
        frame = detector.frame_from_result(result, 0)
        self.assertEqual(frame.pose[11, 3], 0)
        self.assertEqual(frame.pose[12, 3], 0)
        self.assertEqual(frame.pose[10, 3], 0.8)
        from training.holistic_migration.features import pack_frame
        np.testing.assert_array_equal(pack_frame(frame), np.zeros(153))

    def test_nonfinite_or_nonnumeric_sdk_coordinates_raise_clear_value_error(self):
        for name in ("pose_landmarks", "left_hand_landmarks", "right_hand_landmarks", "face_landmarks"):
            for invalid in (np.nan, np.inf, -np.inf, None, "0.25", True, [0.25]):
                result = sdk_result()
                getattr(result, name)[0].x = invalid
                with self.subTest(name=name, invalid=invalid):
                    with self.assertRaisesRegex(ValueError, name):
                        detector.frame_from_result(result, 0)
        result = sdk_result()
        result.pose_landmarks[0].visibility = np.nan
        with self.assertRaisesRegex(ValueError, "pose_landmarks"):
            detector.frame_from_result(result, 0)

    def test_conversion_timestamp_is_exact_nonnegative_builtin_int(self):
        for stamp in (-1, False, True, 1.0, np.int64(1), None, "1"):
            with self.subTest(stamp=stamp):
                with self.assertRaisesRegex(ValueError, "timestamp"):
                    detector.frame_from_result(sdk_result(), stamp)

    def test_reads_flat_normalized_landmarks_not_world_coordinates(self):
        self.assertTrue(hasattr(detector, "frame_from_result"), "missing conversion helper")
        result = sdk_result()
        result.pose_landmarks[11] = SimpleNamespace(x=0.125, y=0.25, z=-0.75, visibility=0.6)
        result.left_hand_landmarks[0].z = 33.0
        result.right_hand_landmarks[0].z = -99.0
        result.pose_world_landmarks[11].x = 999.0
        frame = detector.frame_from_result(result, 123)
        self.assertIsInstance(frame, RawFrame)
        self.assertEqual(frame.timestamp_ms, 123)
        self.assertEqual(frame.pose.shape, (33, 4))
        self.assertEqual(frame.left_hand.shape, (21, 3))
        self.assertEqual(frame.right_hand.shape, (21, 3))
        self.assertEqual(frame.face.shape, (478, 3))
        np.testing.assert_array_equal(frame.pose[11], [0.125, 0.25, -0.75, 0.6])
        self.assertEqual(frame.left_hand[0, 2], 33)
        self.assertEqual(frame.right_hand[0, 2], -99)
        np.testing.assert_array_equal(frame.face[1], [0.01, 0.005, -0.02])
