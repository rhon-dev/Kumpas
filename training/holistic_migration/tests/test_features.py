"""Behavioral contract tests; synthetic coordinates are not anatomical evidence."""
import dataclasses
import unittest

import numpy as np

from training.holistic_migration import features


def observation(timestamp_ms=0, **changes):
    pose = np.zeros((33, 4), dtype=np.float64)
    pose[:, 3] = 0.9
    pose[11] = [0.25, 0.5, 2.0, 0.8]
    pose[12] = [0.75, 0.5, 4.0, 0.9]
    pose[13:17, :3] = [[0.2, 0.3, 1], [0.8, 0.3, 5],
                         [0.1, 0.2, 0], [0.9, 0.2, 6]]
    left = np.arange(63, dtype=np.float64).reshape(21, 3) / 100
    right = left + [0.5, 0.25, 10]
    values = dict(timestamp_ms=timestamp_ms, pose=pose, left_hand=left,
                  right_hand=right, face=None)
    values.update(changes)
    return features.RawFrame(**values)


class PackFrameTests(unittest.TestCase):
    def test_individual_missing_hands_keep_zero_block_and_other_hand(self):
        complete = features.pack_frame(observation())
        for absent, missing_slice, kept_slice, masks in (
                ("left_hand", slice(0, 63), slice(63, 126), [0, 1, 1]),
                ("right_hand", slice(63, 126), slice(0, 63), [1, 0, 1])):
            with self.subTest(absent=absent):
                actual = features.pack_frame(observation(**{absent: None}))
                np.testing.assert_array_equal(actual[missing_slice], np.zeros(63))
                np.testing.assert_array_equal(actual[kept_slice], complete[kept_slice])
                np.testing.assert_array_equal(actual[126:150], complete[126:150])
                np.testing.assert_array_equal(actual[150:], masks)

    def test_missing_pose_is_invalid_even_with_observed_hands(self):
        actual = features.pack_frame(observation(pose=None))
        np.testing.assert_array_equal(actual, np.zeros(153, dtype=np.float32))
        self.assertEqual(actual.dtype, np.dtype(np.float32))

    def test_unreliable_shoulders_invalidate_without_hip_requirement(self):
        for shoulder in (11, 12):
            frame = observation()
            frame.pose[shoulder, 3] = 0.49999
            with self.subTest(shoulder=shoulder):
                np.testing.assert_array_equal(features.pack_frame(frame), np.zeros(153))
        for width in (0.0, 0.000099):
            frame = observation()
            frame.pose[12, :2] = frame.pose[11, :2] + [width, 0]
            with self.subTest(width=width):
                np.testing.assert_array_equal(features.pack_frame(frame), np.zeros(153))
        boundary = observation()
        boundary.pose[11:13, 3] = 0.5
        boundary.pose[11, :2] = [0, 0]
        boundary.pose[12, :2] = [0.0001, 0]
        boundary.pose[23:25] = 0  # hips are not a prerequisite
        self.assertEqual(features.pack_frame(boundary)[152], 1)

    def test_low_visibility_pose_points_are_entirely_zeroed(self):
        frame = observation()
        frame.pose[13, 3] = 0.49999
        frame.pose[14, 3] = 0.5
        actual = features.pack_frame(frame)[126:150].reshape(6, 4)
        np.testing.assert_array_equal(actual[2], np.zeros(4))
        np.testing.assert_array_equal(actual[3], np.array([0.6, -0.4, 4, 0.5], np.float32))

    def test_component_shapes_and_real_numeric_ndarrays_are_required(self):
        for component, shape in (("pose", (33, 4)), ("left_hand", (21, 3)),
                                 ("right_hand", (21, 3))):
            invalid = [np.zeros((shape[0] - 1, shape[1])),
                       np.zeros((shape[0] + 1, shape[1])),
                       np.zeros((shape[0], shape[1] + 1)), np.zeros(np.prod(shape)),
                       np.zeros(shape).tolist(), np.zeros(shape, dtype=object),
                       np.zeros(shape, dtype=complex), np.zeros(shape, dtype=bool),
                       np.full(shape, "0"), "bad"]
            for value in invalid:
                with self.subTest(component=component, shape=getattr(value, "shape", None),
                                  kind=str(getattr(value, "dtype", type(value)))):
                    with self.assertRaisesRegex(ValueError, component):
                        features.pack_frame(observation(**{component: value}))
        for face in (np.zeros((468, 4)), np.zeros(9), [[0, 0, 0]],
                     np.zeros((2, 3), dtype=object)):
            with self.subTest(face_shape=getattr(face, "shape", None)):
                with self.assertRaisesRegex(ValueError, "face"):
                    features.pack_frame(observation(face=face))
        with self.assertRaisesRegex(ValueError, "left_hand"):
            features.pack_frame(observation(pose=None, left_hand=np.zeros((20, 3))))

    def test_semantic_ndarray_subclasses_are_rejected_before_array_semantics(self):
        class SemanticArray(np.ndarray):
            @property
            def dtype(self):
                raise AssertionError("subclass dtype accessed before rejection")

            def __array_ufunc__(self, *args, **kwargs):
                raise AssertionError("subclass ufunc called before rejection")

            def __getitem__(self, key):
                raise AssertionError("subclass indexing called before rejection")

            def astype(self, *args, **kwargs):
                raise AssertionError("subclass conversion called before rejection")

        frame = observation(face=np.ones((7, 3)))
        for component in ("pose", "left_hand", "right_hand", "face"):
            plain = getattr(frame, component)
            partial_mask = np.zeros(plain.shape, dtype=bool)
            partial_mask[1, 0] = True
            partially_masked = np.ma.array(plain, mask=partial_mask, copy=True)
            nan_mask = np.zeros(plain.shape, dtype=bool)
            nan_mask[0, 0] = True
            masked_nan = np.ma.array(plain, mask=nan_mask, copy=True)
            masked_nan.data[0, 0] = np.nan  # pose point 0 is not packed
            for kind, array in (("partially_masked", partially_masked),
                                ("masked_nan", masked_nan),
                                ("matrix", plain.view(np.matrix)),
                                ("overridden_semantics", plain.view(SemanticArray))):
                with self.subTest(component=component, kind=kind):
                    with self.assertRaisesRegex(ValueError, component):
                        features.pack_frame(dataclasses.replace(frame, **{component: array}))

    def test_plain_numeric_arrays_and_strided_readonly_views_keep_packed_behavior(self):
        frame = observation(face=np.ones((7, 3)))
        frame.pose[:, 3] = 1
        frame.pose[11] = [0, 0, 2, 1]
        frame.pose[12] = [2, 0, 4, 1]
        for dtype in (np.int32, np.int64, np.uint16, np.float16, np.float32, np.float64):
            arrays = {name: getattr(frame, name).astype(dtype)
                      for name in ("pose", "left_hand", "right_hand", "face")}
            expected = features.pack_frame(dataclasses.replace(frame, **arrays))
            self.assertEqual(expected[152], 1)
            for layout in ("plain", "strided", "readonly_strided"):
                inputs = {}
                for name, array in arrays.items():
                    if layout == "plain":
                        view = array.copy()
                    else:
                        backing = np.empty((array.shape[0], array.shape[1] * 2), dtype=dtype)
                        view = backing[:, ::2]
                        view[:] = array
                        self.assertFalse(view.flags.c_contiguous)
                    if layout == "readonly_strided":
                        view.flags.writeable = False
                    self.assertIs(type(view), np.ndarray)
                    inputs[name] = view
                with self.subTest(dtype=np.dtype(dtype).name, layout=layout):
                    actual = features.pack_frame(dataclasses.replace(frame, **inputs))
                    self.assertIs(type(actual), np.ndarray)
                    self.assertEqual(actual.dtype, np.dtype(np.float32))
                    np.testing.assert_array_equal(actual, expected)
                    for name, array in inputs.items():
                        np.testing.assert_array_equal(array, arrays[name])
                        self.assertFalse(np.shares_memory(actual, array))

    def test_nonfinite_raw_arrays_raise_even_when_pose_is_unusable(self):
        for component, shape in (("pose", (33, 4)), ("left_hand", (21, 3)),
                                 ("right_hand", (21, 3)), ("face", (478, 3))):
            for value in (np.nan, np.inf, -np.inf):
                array = np.zeros(shape)
                array[-1, -1] = value
                changes = {component: array}
                if component != "pose":
                    changes["pose"] = None
                with self.subTest(component=component, value=value):
                    with self.assertRaisesRegex(ValueError, component):
                        features.pack_frame(observation(**changes))

    def test_raw_timestamp_requires_nonnegative_exact_builtin_int(self):
        for stamp in (-1, True, False, 0.0, np.int64(0), None, "0", np.nan):
            with self.subTest(stamp=stamp):
                with self.assertRaisesRegex(ValueError, "timestamp"):
                    features.pack_frame(observation(timestamp_ms=stamp))
        self.assertEqual(features.pack_frame(observation(timestamp_ms=0))[152], 1)
        with self.assertRaisesRegex(ValueError, "RawFrame"):
            features.pack_frame(None)

    def test_finite_input_with_nonfinite_normalized_output_raises(self):
        for target in ("float64_arithmetic", "float32_cast"):
            frame = observation()
            frame.pose[11, :2] = [0, 0]
            frame.pose[12, :2] = [0.0001, 0]
            frame.left_hand[1, 0] = (np.finfo(np.float64).max
                                     if target == "float64_arithmetic" else 1e38)
            with self.subTest(target=target):
                with self.assertRaisesRegex(ValueError, "normaliz|finite"):
                    features.pack_frame(frame)

    def test_integer_arrays_normalize_in_float_without_truncation(self):
        frame = observation()
        pose = np.zeros((33, 4), dtype=np.int64)
        pose[:, 3] = 1
        pose[11, :3] = [0, 0, 0]
        pose[12, :3] = [2, 0, 0]
        hand = np.ones((21, 3), dtype=np.int64)
        actual = features.pack_frame(dataclasses.replace(frame, pose=pose,
                                                         left_hand=hand, right_hand=None))
        np.testing.assert_array_equal(actual[:3], np.array([0, 0.5, 0], np.float32))

    def test_valid_idle_observation_has_pose_and_no_hand_masks(self):
        actual = features.pack_frame(observation(left_hand=None, right_hand=None))
        np.testing.assert_array_equal(actual[:126], np.zeros(126))
        np.testing.assert_array_equal(actual[150:], [0, 0, 1])
        self.assertTrue(np.any(actual[126:150]))

    def test_translation_positive_scale_and_distinct_depth_origins(self):
        frame = observation()
        baseline = features.pack_frame(frame)
        pose = frame.pose.copy()
        left = frame.left_hand.copy()
        right = frame.right_hand.copy()
        pose[:, :3] = pose[:, :3] * 3 + [7, -2, 100]
        left[:, :3] = left[:, :3] * 3 + [7, -2, -500]
        right[:, :3] = right[:, :3] * 3 + [7, -2, 900]
        transformed = dataclasses.replace(frame, pose=pose, left_hand=left, right_hand=right)
        np.testing.assert_allclose(features.pack_frame(transformed), baseline, atol=1e-6)
        self.assertEqual(baseline[2], 0)  # left wrist origin, not pose origin
        self.assertEqual(baseline[65], 0)  # independent right wrist origin
        self.assertEqual(baseline[128], -2)  # pose shoulder-midpoint origin
        self.assertEqual(baseline[132], 2)

    def test_does_not_mutate_or_alias_readonly_inputs_and_excludes_face(self):
        frame = observation(face=np.full((478, 3), 9.0))
        snapshots = {}
        for name in ("pose", "left_hand", "right_hand", "face"):
            array = getattr(frame, name)
            snapshots[name] = array.copy()
            array.flags.writeable = False
        result = features.pack_frame(frame)
        for name, snapshot in snapshots.items():
            np.testing.assert_array_equal(getattr(frame, name), snapshot)
            self.assertFalse(np.shares_memory(result, getattr(frame, name)))
        for count in (0, 1, 468, 478, 512):
            with self.subTest(face_count=count):
                changed = dataclasses.replace(frame, face=np.zeros((count, 3)))
                np.testing.assert_array_equal(features.pack_frame(changed), result)

    def test_large_but_finite_shoulder_width_is_not_lost_to_squaring_overflow(self):
        frame = observation()
        frame.pose[11, :3] = [-1e200, 0, 0]
        frame.pose[12, :3] = [1e200, 0, 0]
        actual = features.pack_frame(frame)
        self.assertEqual(actual[152], 1)
        self.assertEqual(actual[126], -0.5)
        self.assertEqual(actual[130], 0.5)
        self.assertTrue(np.isfinite(actual).all())
        impossible = observation()
        impossible.pose[11, 0] = -np.finfo(np.float64).max
        impossible.pose[12, 0] = np.finfo(np.float64).max
        np.testing.assert_array_equal(features.pack_frame(impossible), np.zeros(153))

    def test_exact_layout_float32_row_major(self):
        self.assertTrue(hasattr(features, "pack_frame"), "missing pack_frame")
        frame = observation()
        expected_left = frame.left_hand.copy()
        expected_left[:, :2] = (expected_left[:, :2] - [0.5, 0.5]) / 0.5
        expected_left[:, 2] = (expected_left[:, 2] - frame.left_hand[0, 2]) / 0.5
        expected_right = frame.right_hand.copy()
        expected_right[:, :2] = (expected_right[:, :2] - [0.5, 0.5]) / 0.5
        expected_right[:, 2] = (expected_right[:, 2] - frame.right_hand[0, 2]) / 0.5
        expected_pose = frame.pose[11:17].copy()
        expected_pose[:, :3] = (expected_pose[:, :3] - [0.5, 0.5, 3]) / 0.5
        expected = np.concatenate((expected_left.ravel(), expected_right.ravel(),
                                   expected_pose.ravel(), [1, 1, 1])).astype(np.float32)
        actual = features.pack_frame(frame)
        self.assertEqual(actual.shape, (153,))
        self.assertEqual(actual.dtype, np.dtype(np.float32))
        np.testing.assert_array_equal(actual, expected)


class ResampleFramesTests(unittest.TestCase):
    def test_requires_two_actual_observations_and_exact_integer_steps(self):
        for frames in ([], [observation()]):
            with self.subTest(observations=len(frames)):
                with self.assertRaisesRegex(ValueError, "two|2|observations"):
                    features.resample_frames(frames)
        for steps in (0, 1, -3, 2.0, True, False, np.int64(2), None):
            with self.subTest(steps=steps):
                with self.assertRaisesRegex(ValueError, "steps"):
                    features.resample_frames([observation(0), observation(100)], steps=steps)
        self.assertEqual(features.resample_frames([observation(0), observation(1)], steps=2).shape,
                         (2, 153))

    def test_timestamps_must_be_strictly_increasing_without_sorting(self):
        for stamps in ((0, 0), (1, 0), (0, 100, 50), (0, True),
                       (0, -1), (0, np.int64(100)), (0, 100.0)):
            with self.subTest(stamps=stamps):
                with self.assertRaisesRegex(ValueError, "timestamp"):
                    features.resample_frames([observation(stamp) for stamp in stamps])

    def test_unusable_observation_breaks_sequence_even_when_not_sampled(self):
        for position in (0, 1, 2):
            frames = [observation(0), observation(1), observation(1000)]
            frames[position] = dataclasses.replace(frames[position], pose=None)
            with self.subTest(position=position):
                with self.assertRaisesRegex(ValueError, "pose|unusable"):
                    features.resample_frames(frames, steps=2)

    def test_missing_hands_and_idle_are_preserved_as_observations(self):
        frames = [observation(0, left_hand=None), observation(10, right_hand=None),
                  observation(30, left_hand=None, right_hand=None)]
        actual = features.resample_frames(frames, steps=7)
        expected_indices = [0, 0, 1, 1, 1, 2, 2]
        expected = np.stack([features.pack_frame(frames[i]) for i in expected_indices])
        np.testing.assert_array_equal(actual, expected)
        np.testing.assert_array_equal(actual[:, 150:], expected[:, 150:])
        idle = features.resample_frames([observation(0, left_hand=None, right_hand=None),
                                        observation(9, left_hand=None, right_hand=None)])
        np.testing.assert_array_equal(idle[:, 150:], np.tile([0, 0, 1], (30, 1)))

    def test_large_timestamp_origin_does_not_lose_nearest_ties(self):
        origin = 10 ** 30
        frames = [observation(origin), observation(origin + 2)]
        frames[1].right_hand[:, 0] += 1
        actual = features.resample_frames(tuple(frames), steps=3)
        np.testing.assert_array_equal(actual, np.stack([features.pack_frame(frames[i])
                                                       for i in (0, 0, 1)]))

    def test_default_resampling_is_nearest_time_with_earlier_ties(self):
        self.assertTrue(hasattr(features, "resample_frames"), "missing resample_frames")
        frames = [observation(0), observation(100), observation(900)]
        frames[1].left_hand[:, 0] += 1
        frames[2].left_hand[:, 0] += 2
        rows = [features.pack_frame(frame) for frame in frames]
        actual = features.resample_frames(frames)
        self.assertEqual(actual.shape, (30, 153))
        self.assertEqual(actual.dtype, np.dtype(np.float32))
        # Independent exact-integer nearest-distance oracle, not frame-index sampling.
        expected = [rows[min(range(3), key=lambda j: abs(frames[j].timestamp_ms * 29 - i * 900))]
                    for i in range(30)]
        np.testing.assert_array_equal(actual, np.stack(expected))
        tie = features.resample_frames([frames[0], frames[2]], steps=3)
        np.testing.assert_array_equal(tie, np.stack([rows[0], rows[0], rows[2]]))


class RawFrameTests(unittest.TestCase):
    def test_raw_frame_is_frozen_with_optional_face(self):
        self.assertTrue(hasattr(features, "RawFrame"), "missing RawFrame contract")
        frame = features.RawFrame(0, None, None, None)
        self.assertIsNone(frame.face)
        self.assertEqual([f.name for f in dataclasses.fields(frame)],
                         ["timestamp_ms", "pose", "left_hand", "right_hand", "face"])
        with self.assertRaises(dataclasses.FrozenInstanceError):
            frame.timestamp_ms = 1
