# Task A — incremental foundation report

## Scope and starting point

- Authorized additive foundation only, on `holistic-migration`, source HEAD `4d901693642af5f572455b2c75ba095b0ec65c7f`.
- Read task brief, hm153-v1 FEATURES contract, AGENTS, full PRD, original extractor/builder and selected classes. Original pipeline and its class labels/IDs remain unchanged.
- Only the six owned package/test files and this report may be written. No installs, downloads, camera/data operations, training, commits or other-worktree access.
- Initial `git status --short`: only parent-owned `docs/holistic-migration/` was untracked.
- Interpreter: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python`.
- Every test invocation uses `TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch`, `-E -B`, and unittest (no bytecode/cache writes).

## Evidence convention

Every production-changing vertical slice records its actual RED and GREEN outcomes before the next implementation behavior is introduced. Additional regression properties already implied by those slices are honestly marked `PASS (existing behavior; no production edit)` rather than inventing a RED or deliberately breaking working code. Command alias `TEST` below means exactly:

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch PYTHONDONTWRITEBYTECODE=1 /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest discover -s training/holistic_migration/tests -v
```

## Incremental RED/GREEN evidence

Runtime/model-bundle smoke and anatomical/FSL correctness are not established by fixture tests; they remain separate acceptance work.

### A01 frozen raw observation — RED

Command: `TEST` (exact command above). Exit: `1`.

```text
test_raw_frame_is_frozen_with_optional_face (test_features.RawFrameTests.test_raw_frame_is_frozen_with_optional_face) ... FAIL

======================================================================
FAIL: test_raw_frame_is_frozen_with_optional_face (test_features.RawFrameTests.test_raw_frame_is_frozen_with_optional_face)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_features.py", line 12, in test_raw_frame_is_frozen_with_optional_face
    self.assertTrue(hasattr(features, "RawFrame"), "missing RawFrame contract")
AssertionError: False is not true : missing RawFrame contract

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (failures=1)
```

### A01 frozen raw observation — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

### A02 exact packed layout — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
test_exact_layout_float32_row_major (test_features.PackFrameTests.test_exact_layout_float32_row_major) ... FAIL
test_raw_frame_is_frozen_with_optional_face (test_features.RawFrameTests.test_raw_frame_is_frozen_with_optional_face) ... ok

======================================================================
FAIL: test_exact_layout_float32_row_major (test_features.PackFrameTests.test_exact_layout_float32_row_major)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_features.py", line 27, in test_exact_layout_float32_row_major
    self.assertTrue(hasattr(features, "pack_frame"), "missing pack_frame")
AssertionError: False is not true : missing pack_frame

----------------------------------------------------------------------
Ran 2 tests in 0.000s

FAILED (failures=1)
```

### A02 exact packed layout — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 2 tests in 0.027s

OK
```

### A03 independent hand absence — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
AttributeError: 'NoneType' object has no attribute 'copy'

======================================================================
ERROR: test_individual_missing_hands_keep_zero_block_and_other_hand (test_features.PackFrameTests.test_individual_missing_hands_keep_zero_block_and_other_hand) (absent='right_hand')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_features.py", line 32, in test_individual_missing_hands_keep_zero_block_and_other_hand
    actual = features.pack_frame(observation(**{absent: None}))
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/features.py", line 25, in pack_frame
    normalized = hand.copy()
                 ^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'copy'

----------------------------------------------------------------------
Ran 3 tests in 0.018s

FAILED (errors=2)
```

### A03 independent hand absence — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 3 tests in 0.026s

OK
```

### A04 missing pose invalidates entire observation — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
test_raw_frame_is_frozen_with_optional_face (test_features.RawFrameTests.test_raw_frame_is_frozen_with_optional_face) ... ok

======================================================================
ERROR: test_missing_pose_is_invalid_even_with_observed_hands (test_features.PackFrameTests.test_missing_pose_is_invalid_even_with_observed_hands)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_features.py", line 39, in test_missing_pose_is_invalid_even_with_observed_hands
    actual = features.pack_frame(observation(pose=None))
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/features.py", line 21, in pack_frame
    center = (pose[11, :3] + pose[12, :3]) / 2
              ~~~~^^^^^^^^
TypeError: 'NoneType' object is not subscriptable

----------------------------------------------------------------------
Ran 4 tests in 0.019s

FAILED (errors=1)
```

### A04 missing pose invalidates entire observation — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 4 tests in 0.028s

OK
```

### A05 shoulder confidence and width boundaries — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
    raise AssertionError(msg)
AssertionError: 
Arrays are not equal

Mismatched elements: 148 / 153 (96.7%)
Max absolute difference among violations: 30303.03125
Max relative difference among violations: inf
 ACTUAL: array([-2.525752e+03, -4.949495e+03,  0.000000e+00, -2.222722e+03,
       -4.646465e+03,  3.030303e+02, -1.919692e+03, -4.343435e+03,
        6.060606e+02, -1.616662e+03, -4.040404e+03,  9.090909e+02,...
 DESIRED: array([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,...

----------------------------------------------------------------------
Ran 5 tests in 0.025s

FAILED (failures=4)
```

### A05 shoulder confidence and width boundaries — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 5 tests in 0.029s

OK
```

### A06 low-visibility pose points — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
  File "/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/contextlib.py", line 81, in inner
    return func(*args, **kwds)
           ^^^^^^^^^^^^^^^^^^^
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/lib/python3.11/site-packages/numpy/testing/_private/utils.py", line 889, in assert_array_compare
    raise AssertionError(msg)
AssertionError: 
Arrays are not equal

Mismatched elements: 4 / 4 (100%)
Max absolute difference among violations: 4.
Max relative difference among violations: inf
 ACTUAL: array([-0.6    , -0.4    , -4.     ,  0.49999], dtype=float32)
 DESIRED: array([0., 0., 0., 0.])

----------------------------------------------------------------------
Ran 6 tests in 0.020s

FAILED (failures=1)
```

### A06 low-visibility pose points — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 6 tests in 0.019s

OK
```

### A07 exact component shapes and numeric array types — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_features.py", line 86, in test_component_shapes_and_real_numeric_ndarrays_are_required
    with self.assertRaisesRegex(ValueError, "face"):
AssertionError: ValueError not raised

======================================================================
FAIL: test_component_shapes_and_real_numeric_ndarrays_are_required (test_features.PackFrameTests.test_component_shapes_and_real_numeric_ndarrays_are_required)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_features.py", line 88, in test_component_shapes_and_real_numeric_ndarrays_are_required
    with self.assertRaisesRegex(ValueError, "left_hand"):
AssertionError: ValueError not raised

----------------------------------------------------------------------
Ran 7 tests in 0.023s

FAILED (failures=20, errors=15)
```

### A07 exact component shapes and numeric array types — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 7 tests in 0.029s

OK
```

### A08 nonfinite raw components fail closed — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_features.py", line 101, in test_nonfinite_raw_arrays_raise_even_when_pose_is_unusable
    with self.assertRaisesRegex(ValueError, component):
AssertionError: ValueError not raised

======================================================================
FAIL: test_nonfinite_raw_arrays_raise_even_when_pose_is_unusable (test_features.PackFrameTests.test_nonfinite_raw_arrays_raise_even_when_pose_is_unusable) (component='face', value=-inf)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_features.py", line 101, in test_nonfinite_raw_arrays_raise_even_when_pose_is_unusable
    with self.assertRaisesRegex(ValueError, component):
AssertionError: ValueError not raised

----------------------------------------------------------------------
Ran 8 tests in 0.020s

FAILED (failures=12)
```

### A08 nonfinite raw components fail closed — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 8 tests in 0.029s

OK
```

### A09 raw timestamp and frame type validation — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_features.py", line 107, in test_raw_timestamp_requires_nonnegative_exact_builtin_int
    with self.assertRaisesRegex(ValueError, "timestamp"):
AssertionError: ValueError not raised

======================================================================
FAIL: test_raw_timestamp_requires_nonnegative_exact_builtin_int (test_features.PackFrameTests.test_raw_timestamp_requires_nonnegative_exact_builtin_int) (stamp=nan)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_features.py", line 107, in test_raw_timestamp_requires_nonnegative_exact_builtin_int
    with self.assertRaisesRegex(ValueError, "timestamp"):
AssertionError: ValueError not raised

----------------------------------------------------------------------
Ran 9 tests in 0.021s

FAILED (failures=8, errors=1)
```

### A09 raw timestamp and frame type validation — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 9 tests in 0.034s

OK
```

### A10 reject overflow during normalization or Float32 conversion — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_features.py", line 121, in test_finite_input_with_nonfinite_normalized_output_raises
    with self.assertRaisesRegex(ValueError, "normaliz|finite"):
AssertionError: ValueError not raised

======================================================================
FAIL: test_finite_input_with_nonfinite_normalized_output_raises (test_features.PackFrameTests.test_finite_input_with_nonfinite_normalized_output_raises) (target='float32_cast')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_features.py", line 121, in test_finite_input_with_nonfinite_normalized_output_raises
    with self.assertRaisesRegex(ValueError, "normaliz|finite"):
AssertionError: ValueError not raised

----------------------------------------------------------------------
Ran 10 tests in 0.023s

FAILED (failures=2)
```

### A10 reject overflow during normalization or Float32 conversion — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 10 tests in 0.029s

OK
```

### A11 integer numeric arrays normalize without truncation — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
  File "/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/contextlib.py", line 81, in inner
    return func(*args, **kwds)
           ^^^^^^^^^^^^^^^^^^^
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/lib/python3.11/site-packages/numpy/testing/_private/utils.py", line 889, in assert_array_compare
    raise AssertionError(msg)
AssertionError: 
Arrays are not equal

Mismatched elements: 1 / 3 (33.3%)
Max absolute difference among violations: 0.5
Max relative difference among violations: 1.
 ACTUAL: array([0., 0., 0.], dtype=float32)
 DESIRED: array([0. , 0.5, 0. ], dtype=float32)

----------------------------------------------------------------------
Ran 11 tests in 0.022s

FAILED (failures=1)
```

### A11 integer numeric arrays normalize without truncation — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 11 tests in 0.029s

OK
```

### A12 idle coverage of existing missing-hand behavior — PASS (existing behavior; no production edit)

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 12 tests in 0.020s

OK
```

### A13 geometry and separate depth origins coverage — PASS (existing behavior; no production edit)

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 13 tests in 0.019s

OK
```

### A14 immutability aliasing and variable excluded face coverage — PASS (existing behavior; no production edit)

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 14 tests in 0.030s

OK
```

### A15 nearest-time resampling and earlier ties — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
test_translation_positive_scale_and_distinct_depth_origins (test_features.PackFrameTests.test_translation_positive_scale_and_distinct_depth_origins) ... ok
test_unreliable_shoulders_invalidate_without_hip_requirement (test_features.PackFrameTests.test_unreliable_shoulders_invalidate_without_hip_requirement) ... ok
test_valid_idle_observation_has_pose_and_no_hand_masks (test_features.PackFrameTests.test_valid_idle_observation_has_pose_and_no_hand_masks) ... ok
test_raw_frame_is_frozen_with_optional_face (test_features.RawFrameTests.test_raw_frame_is_frozen_with_optional_face) ... ok
test_default_resampling_is_nearest_time_with_earlier_ties (test_features.ResampleFramesTests.test_default_resampling_is_nearest_time_with_earlier_ties) ... FAIL

======================================================================
FAIL: test_default_resampling_is_nearest_time_with_earlier_ties (test_features.ResampleFramesTests.test_default_resampling_is_nearest_time_with_earlier_ties)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_features.py", line 194, in test_default_resampling_is_nearest_time_with_earlier_ties
    self.assertTrue(hasattr(features, "resample_frames"), "missing resample_frames")
AssertionError: False is not true : missing resample_frames

----------------------------------------------------------------------
Ran 15 tests in 0.020s

FAILED (failures=1)
```

### A15 nearest-time resampling and earlier ties — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 15 tests in 0.035s

OK
```

### A16 resampling observation and step prerequisites — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text

Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_features.py", line 200, in test_requires_two_actual_observations_and_exact_integer_steps
    with self.assertRaisesRegex(ValueError, "steps"):
AssertionError: "steps" does not match "need at least one array to stack"

======================================================================
FAIL: test_requires_two_actual_observations_and_exact_integer_steps (test_features.ResampleFramesTests.test_requires_two_actual_observations_and_exact_integer_steps) (steps=np.int64(2))
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_features.py", line 200, in test_requires_two_actual_observations_and_exact_integer_steps
    with self.assertRaisesRegex(ValueError, "steps"):
AssertionError: ValueError not raised

----------------------------------------------------------------------
Ran 16 tests in 0.025s

FAILED (failures=7, errors=3)
```

### A16 resampling observation and step prerequisites — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 16 tests in 0.031s

OK
```

### A17 strict temporal order — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_features.py", line 209, in test_timestamps_must_be_strictly_increasing_without_sorting
    with self.assertRaisesRegex(ValueError, "timestamp"):
AssertionError: ValueError not raised

======================================================================
FAIL: test_timestamps_must_be_strictly_increasing_without_sorting (test_features.ResampleFramesTests.test_timestamps_must_be_strictly_increasing_without_sorting) (stamps=(0, 100, 50))
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_features.py", line 209, in test_timestamps_must_be_strictly_increasing_without_sorting
    with self.assertRaisesRegex(ValueError, "timestamp"):
AssertionError: ValueError not raised

----------------------------------------------------------------------
Ran 17 tests in 0.021s

FAILED (failures=3)
```

### A17 strict temporal order — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 17 tests in 0.030s

OK
```

### A18 invalid observations cannot be dropped or bridged — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_features.py", line 217, in test_unusable_observation_breaks_sequence_even_when_not_sampled
    with self.assertRaisesRegex(ValueError, "pose|unusable"):
AssertionError: ValueError not raised

======================================================================
FAIL: test_unusable_observation_breaks_sequence_even_when_not_sampled (test_features.ResampleFramesTests.test_unusable_observation_breaks_sequence_even_when_not_sampled) (position=2)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_features.py", line 217, in test_unusable_observation_breaks_sequence_even_when_not_sampled
    with self.assertRaisesRegex(ValueError, "pose|unusable"):
AssertionError: ValueError not raised

----------------------------------------------------------------------
Ran 18 tests in 0.023s

FAILED (failures=3)
```

### A18 invalid observations cannot be dropped or bridged — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 18 tests in 0.023s

OK
```

### A19 resampled absence and all-idle coverage — PASS (existing behavior; no production edit)

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 19 tests in 0.023s

OK
```

### A20 exact integer target arithmetic coverage — PASS (existing behavior; no production edit)

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 20 tests in 0.024s

OK
```

### A21 SDK-shaped normalized result conversion — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
test_large_timestamp_origin_does_not_lose_nearest_ties (test_features.ResampleFramesTests.test_large_timestamp_origin_does_not_lose_nearest_ties) ... ok
test_missing_hands_and_idle_are_preserved_as_observations (test_features.ResampleFramesTests.test_missing_hands_and_idle_are_preserved_as_observations) ... ok
test_requires_two_actual_observations_and_exact_integer_steps (test_features.ResampleFramesTests.test_requires_two_actual_observations_and_exact_integer_steps) ... ok
test_timestamps_must_be_strictly_increasing_without_sorting (test_features.ResampleFramesTests.test_timestamps_must_be_strictly_increasing_without_sorting) ... ok
test_unusable_observation_breaks_sequence_even_when_not_sampled (test_features.ResampleFramesTests.test_unusable_observation_breaks_sequence_even_when_not_sampled) ... ok

======================================================================
FAIL: test_reads_flat_normalized_landmarks_not_world_coordinates (test_detector.ResultConversionTests.test_reads_flat_normalized_landmarks_not_world_coordinates)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_detector.py", line 31, in test_reads_flat_normalized_landmarks_not_world_coordinates
    self.assertTrue(hasattr(detector, "frame_from_result"), "missing conversion helper")
AssertionError: False is not true : missing conversion helper

----------------------------------------------------------------------
Ran 21 tests in 0.022s

FAILED (failures=1)
```

### A21 SDK-shaped normalized result conversion — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 21 tests in 0.022s

OK
```

### A22 absent SDK components and independent hands — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
test_large_timestamp_origin_does_not_lose_nearest_ties (test_features.ResampleFramesTests.test_large_timestamp_origin_does_not_lose_nearest_ties) ... ok
test_missing_hands_and_idle_are_preserved_as_observations (test_features.ResampleFramesTests.test_missing_hands_and_idle_are_preserved_as_observations) ... ok
test_requires_two_actual_observations_and_exact_integer_steps (test_features.ResampleFramesTests.test_requires_two_actual_observations_and_exact_integer_steps) ... ok
test_timestamps_must_be_strictly_increasing_without_sorting (test_features.ResampleFramesTests.test_timestamps_must_be_strictly_increasing_without_sorting) ... ok
test_unusable_observation_breaks_sequence_even_when_not_sampled (test_features.ResampleFramesTests.test_unusable_observation_breaks_sequence_even_when_not_sampled) ... ok

======================================================================
FAIL: test_empty_components_are_none_and_one_handed_results_remain_distinct (test_detector.ResultConversionTests.test_empty_components_are_none_and_one_handed_results_remain_distinct)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_detector.py", line 34, in test_empty_components_are_none_and_one_handed_results_remain_distinct
    self.assertIsNone(getattr(empty, name))
AssertionError: array([], dtype=float64) is not None

----------------------------------------------------------------------
Ran 22 tests in 0.015s

FAILED (failures=1)
```

### A22 absent SDK components and independent hands — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 22 tests in 0.022s

OK
```

### A23 strict SDK list counts and shape — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_detector.py", line 51, in test_requires_exact_pose_hand_counts_and_flat_sdk_shape
    with self.assertRaisesRegex(ValueError, name):
AssertionError: ValueError not raised

======================================================================
FAIL: test_requires_exact_pose_hand_counts_and_flat_sdk_shape (test_detector.ResultConversionTests.test_requires_exact_pose_hand_counts_and_flat_sdk_shape) (name='right_hand_landmarks', count=22)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_detector.py", line 51, in test_requires_exact_pose_hand_counts_and_flat_sdk_shape
    with self.assertRaisesRegex(ValueError, name):
AssertionError: ValueError not raised

----------------------------------------------------------------------
Ran 23 tests in 0.022s

FAILED (failures=9, errors=4)
```

### A23 strict SDK list counts and shape — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 23 tests in 0.023s

OK
```

### A24 fail-closed optional pose visibility — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_detector.py", line 63, in test_missing_or_none_pose_visibility_is_zero_not_fabricated_confidence
    frame = detector.frame_from_result(result, 0)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/detector.py", line 23, in frame_from_result
    return RawFrame(timestamp_ms, convert("pose_landmarks", pose=True),
                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/detector.py", line 21, in convert
    raise ValueError(f"malformed {name}: {error}") from error
ValueError: malformed pose_landmarks: 'types.SimpleNamespace' object has no attribute 'visibility'

----------------------------------------------------------------------
Ran 24 tests in 0.020s

FAILED (errors=1)
```

### A24 fail-closed optional pose visibility — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 24 tests in 0.024s

OK
```

### A25 reject nonfinite and malformed SDK scalars — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_detector.py", line 76, in test_nonfinite_or_nonnumeric_sdk_coordinates_raise_clear_value_error
    with self.assertRaisesRegex(ValueError, name):
AssertionError: ValueError not raised

======================================================================
FAIL: test_nonfinite_or_nonnumeric_sdk_coordinates_raise_clear_value_error (test_detector.ResultConversionTests.test_nonfinite_or_nonnumeric_sdk_coordinates_raise_clear_value_error)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_detector.py", line 80, in test_nonfinite_or_nonnumeric_sdk_coordinates_raise_clear_value_error
    with self.assertRaisesRegex(ValueError, "pose_landmarks"):
AssertionError: ValueError not raised

----------------------------------------------------------------------
Ran 25 tests in 0.027s

FAILED (failures=25)
```

### A25 reject nonfinite and malformed SDK scalars — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 25 tests in 0.035s

OK
```

### A26 conversion timestamp validation — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_detector.py", line 86, in test_conversion_timestamp_is_exact_nonnegative_builtin_int
    with self.assertRaisesRegex(ValueError, "timestamp"):
AssertionError: ValueError not raised

======================================================================
FAIL: test_conversion_timestamp_is_exact_nonnegative_builtin_int (test_detector.ResultConversionTests.test_conversion_timestamp_is_exact_nonnegative_builtin_int) (stamp='1')
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_detector.py", line 86, in test_conversion_timestamp_is_exact_nonnegative_builtin_int
    with self.assertRaisesRegex(ValueError, "timestamp"):
AssertionError: ValueError not raised

----------------------------------------------------------------------
Ran 26 tests in 0.038s

FAILED (failures=7)
```

### A26 conversion timestamp validation — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 26 tests in 0.039s

OK
```

### A27 model preflight before lazy native import — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
test_large_timestamp_origin_does_not_lose_nearest_ties (test_features.ResampleFramesTests.test_large_timestamp_origin_does_not_lose_nearest_ties) ... ok
test_missing_hands_and_idle_are_preserved_as_observations (test_features.ResampleFramesTests.test_missing_hands_and_idle_are_preserved_as_observations) ... ok
test_requires_two_actual_observations_and_exact_integer_steps (test_features.ResampleFramesTests.test_requires_two_actual_observations_and_exact_integer_steps) ... ok
test_timestamps_must_be_strictly_increasing_without_sorting (test_features.ResampleFramesTests.test_timestamps_must_be_strictly_increasing_without_sorting) ... ok
test_unusable_observation_breaks_sequence_even_when_not_sampled (test_features.ResampleFramesTests.test_unusable_observation_breaks_sequence_even_when_not_sampled) ... ok

======================================================================
FAIL: test_invalid_model_path_rejected_before_any_mediapipe_import (test_detector.DetectorPreflightTests.test_invalid_model_path_rejected_before_any_mediapipe_import)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_detector.py", line 31, in test_invalid_model_path_rejected_before_any_mediapipe_import
    self.assertTrue(hasattr(detector, "HolisticDetector"), "missing HolisticDetector")
AssertionError: False is not true : missing HolisticDetector

----------------------------------------------------------------------
Ran 27 tests in 0.033s

FAILED (failures=1)
```

### A27 model preflight before lazy native import — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 27 tests in 0.040s

OK
```

### A28 explicit Tasks Holistic VIDEO CPU construction — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
test_large_timestamp_origin_does_not_lose_nearest_ties (test_features.ResampleFramesTests.test_large_timestamp_origin_does_not_lose_nearest_ties) ... ok
test_missing_hands_and_idle_are_preserved_as_observations (test_features.ResampleFramesTests.test_missing_hands_and_idle_are_preserved_as_observations) ... ok
test_requires_two_actual_observations_and_exact_integer_steps (test_features.ResampleFramesTests.test_requires_two_actual_observations_and_exact_integer_steps) ... ok
test_timestamps_must_be_strictly_increasing_without_sorting (test_features.ResampleFramesTests.test_timestamps_must_be_strictly_increasing_without_sorting) ... ok
test_unusable_observation_breaks_sequence_even_when_not_sampled (test_features.ResampleFramesTests.test_unusable_observation_breaks_sequence_even_when_not_sampled) ... ok

======================================================================
FAIL: test_construction_uses_tasks_video_cpu_and_disabled_optional_outputs (test_detector.DetectorPreflightTests.test_construction_uses_tasks_video_cpu_and_disabled_optional_outputs)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_detector.py", line 90, in test_construction_uses_tasks_video_cpu_and_disabled_optional_outputs
    self.assertEqual(len(created), 1)
AssertionError: 0 != 1

----------------------------------------------------------------------
Ran 28 tests in 0.035s

FAILED (failures=1)
```

### A28 explicit Tasks Holistic VIDEO CPU construction — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 28 tests in 0.039s

OK
```

### A29 RGB VIDEO detection through shared result conversion — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
test_large_timestamp_origin_does_not_lose_nearest_ties (test_features.ResampleFramesTests.test_large_timestamp_origin_does_not_lose_nearest_ties) ... ok
test_missing_hands_and_idle_are_preserved_as_observations (test_features.ResampleFramesTests.test_missing_hands_and_idle_are_preserved_as_observations) ... ok
test_requires_two_actual_observations_and_exact_integer_steps (test_features.ResampleFramesTests.test_requires_two_actual_observations_and_exact_integer_steps) ... ok
test_timestamps_must_be_strictly_increasing_without_sorting (test_features.ResampleFramesTests.test_timestamps_must_be_strictly_increasing_without_sorting) ... ok
test_unusable_observation_breaks_sequence_even_when_not_sampled (test_features.ResampleFramesTests.test_unusable_observation_breaks_sequence_even_when_not_sampled) ... ok

======================================================================
FAIL: test_detect_feeds_unmirrored_rgb_to_video_and_returns_converted_frame (test_detector.DetectorPreflightTests.test_detect_feeds_unmirrored_rgb_to_video_and_returns_converted_frame)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_detector.py", line 105, in test_detect_feeds_unmirrored_rgb_to_video_and_returns_converted_frame
    self.assertTrue(hasattr(instance, "detect"), "missing detect")
AssertionError: False is not true : missing detect

----------------------------------------------------------------------
Ran 29 tests in 0.035s

FAILED (failures=1)
```

### A29 RGB VIDEO detection through shared result conversion — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 29 tests in 0.041s

OK
```

### A30 detect preflight rejects invalid API input before native calls — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
======================================================================
FAIL: test_invalid_api_rgb_or_timestamp_is_rejected_before_any_native_call (test_detector.DetectorPreflightTests.test_invalid_api_rgb_or_timestamp_is_rejected_before_any_native_call)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_detector.py", line 134, in test_invalid_api_rgb_or_timestamp_is_rejected_before_any_native_call
    self.assertEqual(native.calls, [])
AssertionError: Lists differ: [(namespace(image_format=<object object at[2661 chars]'1')] != []

First list contains 16 additional elements.
First extra element 0:
(namespace(image_format=<object object at 0x102f7a8c0>, data=array([None], dtype=object)), 0)

Diff is 3181 characters long. Set self.maxDiff to None to see it.

----------------------------------------------------------------------
Ran 30 tests in 0.047s

FAILED (failures=10)
```

### A30 detect preflight rejects invalid API input before native calls — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 30 tests in 0.044s

OK
```

### A31 per-instance strict VIDEO timestamps — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_detector.py", line 146, in test_timestamps_strictly_increase_per_instance_and_new_instance_resets
    with self.assertRaisesRegex(ValueError, "timestamp|increasing"):
AssertionError: ValueError not raised

======================================================================
FAIL: test_timestamps_strictly_increase_per_instance_and_new_instance_resets (test_detector.DetectorPreflightTests.test_timestamps_strictly_increase_per_instance_and_new_instance_resets)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_detector.py", line 148, in test_timestamps_strictly_increase_per_instance_and_new_instance_resets
    self.assertEqual(len(native.calls), 1)
AssertionError: 4 != 1

----------------------------------------------------------------------
Ran 31 tests in 0.040s

FAILED (failures=4)
```

### A31 per-instance strict VIDEO timestamps — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 31 tests in 0.046s

OK
```

### A32 exception-safe context and idempotent close ownership — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
test_large_timestamp_origin_does_not_lose_nearest_ties (test_features.ResampleFramesTests.test_large_timestamp_origin_does_not_lose_nearest_ties) ... ok
test_missing_hands_and_idle_are_preserved_as_observations (test_features.ResampleFramesTests.test_missing_hands_and_idle_are_preserved_as_observations) ... ok
test_requires_two_actual_observations_and_exact_integer_steps (test_features.ResampleFramesTests.test_requires_two_actual_observations_and_exact_integer_steps) ... ok
test_timestamps_must_be_strictly_increasing_without_sorting (test_features.ResampleFramesTests.test_timestamps_must_be_strictly_increasing_without_sorting) ... ok
test_unusable_observation_breaks_sequence_even_when_not_sampled (test_features.ResampleFramesTests.test_unusable_observation_breaks_sequence_even_when_not_sampled) ... ok

======================================================================
FAIL: test_context_manager_closes_once_on_body_exception_and_is_not_reusable (test_detector.DetectorPreflightTests.test_context_manager_closes_once_on_body_exception_and_is_not_reusable)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_detector.py", line 162, in test_context_manager_closes_once_on_body_exception_and_is_not_reusable
    self.assertTrue(hasattr(instance, "__enter__"), "missing context ownership")
AssertionError: False is not true : missing context ownership

----------------------------------------------------------------------
Ran 32 tests in 0.039s

FAILED (failures=1)
```

### A32 exception-safe context and idempotent close ownership — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 32 tests in 0.045s

OK
```

### A33 native exceptions cannot allow timestamp reuse — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
test_large_timestamp_origin_does_not_lose_nearest_ties (test_features.ResampleFramesTests.test_large_timestamp_origin_does_not_lose_nearest_ties) ... ok
test_missing_hands_and_idle_are_preserved_as_observations (test_features.ResampleFramesTests.test_missing_hands_and_idle_are_preserved_as_observations) ... ok
test_requires_two_actual_observations_and_exact_integer_steps (test_features.ResampleFramesTests.test_requires_two_actual_observations_and_exact_integer_steps) ... ok
test_timestamps_must_be_strictly_increasing_without_sorting (test_features.ResampleFramesTests.test_timestamps_must_be_strictly_increasing_without_sorting) ... ok
test_unusable_observation_breaks_sequence_even_when_not_sampled (test_features.ResampleFramesTests.test_unusable_observation_breaks_sequence_even_when_not_sampled) ... ok

======================================================================
FAIL: test_native_failure_consumes_timestamp_and_context_still_closes (test_detector.DetectorPreflightTests.test_native_failure_consumes_timestamp_and_context_still_closes)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_detector.py", line 187, in test_native_failure_consumes_timestamp_and_context_still_closes
    with self.assertRaisesRegex(ValueError, "timestamp|increasing"):
AssertionError: ValueError not raised

----------------------------------------------------------------------
Ran 33 tests in 0.042s

FAILED (failures=1)
```

### A33 native exceptions cannot allow timestamp reuse — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 33 tests in 0.046s

OK
```

### A34 conversion exception cleanup coverage — PASS (existing behavior; no production edit)

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 34 tests in 0.040s

OK
```

### A35 native exception cleanup coverage — PASS (existing behavior; no production edit)

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 35 tests in 0.041s

OK
```

### A36 stable finite 2D shoulder width — RED

Command: `TEST` (exact command above). Exit: `1`. Actual output excerpt:

```text
test_large_timestamp_origin_does_not_lose_nearest_ties (test_features.ResampleFramesTests.test_large_timestamp_origin_does_not_lose_nearest_ties) ... ok
test_missing_hands_and_idle_are_preserved_as_observations (test_features.ResampleFramesTests.test_missing_hands_and_idle_are_preserved_as_observations) ... ok
test_requires_two_actual_observations_and_exact_integer_steps (test_features.ResampleFramesTests.test_requires_two_actual_observations_and_exact_integer_steps) ... ok
test_timestamps_must_be_strictly_increasing_without_sorting (test_features.ResampleFramesTests.test_timestamps_must_be_strictly_increasing_without_sorting) ... ok
test_unusable_observation_breaks_sequence_even_when_not_sampled (test_features.ResampleFramesTests.test_unusable_observation_breaks_sequence_even_when_not_sampled) ... ok

======================================================================
FAIL: test_large_but_finite_shoulder_width_is_not_lost_to_squaring_overflow (test_features.PackFrameTests.test_large_but_finite_shoulder_width_is_not_lost_to_squaring_overflow)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/holistic_migration/tests/test_features.py", line 178, in test_large_but_finite_shoulder_width_is_not_lost_to_squaring_overflow
    self.assertEqual(actual[152], 1)
AssertionError: np.float32(0.0) != 1

----------------------------------------------------------------------
Ran 36 tests in 0.051s

FAILED (failures=1)
```

### A36 stable finite 2D shoulder width — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 36 tests in 0.048s

OK
```

### A37 clean-process dependency-free import coverage — PASS (existing behavior; no production edit)

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 37 tests in 0.189s

OK
```

### A38 strided RGB safety coverage — PASS (existing behavior; no production edit)

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 38 tests in 0.181s

OK
```

### Post-GREEN readability and fixture-ownership refactor — GREEN

Command: `TEST` (exact command above). Exit: `0`. Actual output excerpt:

```text
----------------------------------------------------------------------
Ran 38 tests in 0.189s

OK
```

## Final verification and outcome

- Implemented the additive hm153-v1 feature/detector foundation only.
- Actual production-changing RED→GREEN slices: **29**. Additional existing-behavior regression extensions: **9**, explicitly identified above (no manufactured failing runs). A01 first establishes the frozen observation, then each implementation behavior was added only after its observed failing test. Post-GREEN refactoring was separately rerun.
- Fresh final required discovery command: `TEST`; exit **0**. Actual terminal result:

```text
Ran 38 tests in 0.199s

OK
```

- Final discovery: **38 passed, zero failures/errors/skips**, with no emitted warnings. A separate AST count independently found 38 `test_` definitions in exactly six package/test Python files. No `.pyc`, `__pycache__`, `.pytest_cache`, or trailing-whitespace lines under the new package.
- `git diff --check && git diff --exit-code` exited 0: all existing tracked source files remain unchanged. Branch/HEAD remain `holistic-migration` / `4d901693642af5f572455b2c75ba095b0ec65c7f`. Parent-created migration plan/docs are untracked and were not edited by this task.
- The parent's pre-task 51-test old-training baseline is context only, **not** represented as a new execution by this worker.

## Owned created files

1. `training/holistic_migration/__init__.py`
2. `training/holistic_migration/features.py`
3. `training/holistic_migration/detector.py`
4. `training/holistic_migration/tests/__init__.py`
5. `training/holistic_migration/tests/test_features.py`
6. `training/holistic_migration/tests/test_detector.py`
7. `docs/holistic-migration/task-a-report.md`

## Contract coverage and implementation decisions

| Contract area | Exercised behavior |
| --- | --- |
| RawFrame | Frozen dataclass; exact field order; optional face; built-in nonnegative timestamp validation at packing/conversion/detection boundaries |
| Exact vector | Float32 `(153,)`; SDK left/right row-major blocks; ordered pose 11–16 XYZ/visibility; three masks; face excluded |
| Normalization | Shoulder XY midpoint and finite 2D width; independent wrist-local hand Z and shoulder-midpoint pose Z; positive-scale/translation invariance; integer arrays promote before arithmetic; stable hypot avoids unnecessary width squaring overflow |
| Invalid observations | Missing pose/unreliable shoulders/narrow or nonfinite computed width return all-zero vectors; confidence and width inclusive boundaries tested; no hips needed |
| Missingness | Each missing hand while the other is present; both-hands-absent idle; low-visibility pose points entirely zero; absence preserved through sampling |
| Input integrity | Exact pose/hand counts and channels; real numeric ndarrays; invalid types and nonfinite raw arrays rejected even without usable pose; nonfinite normalized/Float32 output rejected; read-only input and no alias/mutation coverage |
| Time | At least two actual observations; exact-int steps at least two; strictly increasing exact-int timestamps; exact-integer nearest distances avoid large-origin precision loss; earlier ties; all supplied observations packed and checked, including an unsampled invalid interior gap |
| Result conversion | Flat SDK normalized lists, not world outputs or legacy `.landmark` wrappers; pose33/hands21; variable face count; absent/empty components stay None; observed XYZ/visibility copied; missing/None visibility becomes zero; malformed SDK scalars rejected |
| Detector API | Lazy dependency import; existing Path preflight before SDK import; explicit Tasks Holistic VIDEO/CPU, blendshapes and segmentation disabled; RGB uint8/nonempty shape/timestamp preflight before image/native calls; strided RGB copied contiguously without mirror/channel swap |
| Ownership | One tracker and timestamp history per instance; fresh instances reset; timestamps are consumed at native-call entry even if native detection raises; idempotent close, normal/exceptional context cleanup, no reuse after closing |

## SDK inspection and bounded claims

Read the installed MediaPipe source under `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/lib/python3.11/site-packages/mediapipe/`:

- `__init__.py` reports 1.2.0 and exports `tasks`, `Image`, `ImageFormat`.
- `tasks/python/vision/holistic_landmarker.py` defines flat normalized result lists, ctypes `from_ctypes`, public `HolisticLandmarkerOptions`, singular Python `output_segmentation_mask`, `create_from_options`, `detect_for_video`, and `close`.
- `tasks/python/core/base_options.py` defines `BaseOptions.Delegate.CPU`.

The adapter uses these public APIs only. No installed package edits, old-version private result adapters, legacy Solutions, independent Pose/Hands, or TensorFlow imports were introduced. One source-search tool attempt returned a process error; direct file reading supplied the needed source successfully.

## Concerns / intentionally not established

- **No native model-bundle/blank-frame smoke was run here.** SDK-shaped conversion fixtures and strict-signature fakes establish host adapter behavior, not SDK execution, model compatibility, recognition or anatomical correctness. The parent owns the separate official compatible bundle/runtime smoke.
- Face/non-manual sufficiency, SDK anatomical left/right, live capture eligibility/rate/duration, signer independence, all-sign accuracy and mobile/physical performance remain unvalidated. No historical phase gate is newly closed.
- No CLI was added in this foundation-only scope; preflight tests exercise the requested constructor/detect API boundaries. A future CLI must validate its own inputs before constructing a detector.
- No data extraction, camera access, training, downloads, dependency installs, phone/app operations, asset changes, commits, pushes or other-worktree access occurred.

## Task A fix 1 — L01 / REQ-A-INPUT-INTEGRITY (2026-11-13)

- Bounded follow-up to `task-a-fix-1-brief.md`; the earlier report/evidence above remains historical. No reconstruction of prior TDD history or repository re-audit.
- Pre-fix evidence mapping supplied by the parent: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-a-before-fix-3ecdfe36991c4588bf3ce732470c4ea2/snapshot-index.json`. It identifies the preserved, parent-read-back-hash-verified 12-file pre-fix snapshot, not repaired source. This worker did not overwrite or reverify that snapshot; old hashes do not cover this fix.
- One cohesive type-boundary slice: component-specific rejection of partially masked arrays, masked NaNs (including unselected pose point 0), matrices and an ndarray subclass trapping dtype/ufunc/indexing/conversion. Each type is exercised in pose, left_hand, right_hand and face. Positive controls cover ordinary numeric arrays and noncontiguous/read-only views, Float32 output, no mutation or aliasing. Existing SDK conversion tests remain unchanged.
- Every invocation below runs from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration` using this exact command, abbreviated `FIX_TEST`:

```sh
TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch ~/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest discover -s training/holistic_migration/tests -v
```

### Fix 1 — initial RED (production unchanged)

Command: `FIX_TEST`. Exit: **1**. Actual terminal summary:

```text
Ran 40 tests in 0.874s

FAILED (failures=15, errors=1)
```

All existing tests and the new plain-array positive-control test passed. The new subclass-rejection test had 15 failing subtests and one error: partially masked hands and masked NaN at pose point 0 were accepted; matrix pose raised `IndexError: index 1 is out of bounds for axis 0 with size 1`; the custom subclass reached its overridden dtype and raised `AssertionError: subclass dtype accessed before rejection`. Other failures included non-component-specific normalization/concatenation ValueErrors. These are the targeted missing boundary, not test import/setup failures.

The editor separately flagged mask-property indexing in two fixture lines (`MaskType` typing). Before any production edit, fixture mask construction was changed to explicit ordinary boolean arrays; behavior and assertions are unchanged. RED is rerun below on the final fixture form.

### Fix 1 — confirmed RED (final fixture form; production unchanged)

Command: `FIX_TEST`. Exit: **1**. Actual terminal summary:

```text
Ran 40 tests in 0.698s

FAILED (failures=15, errors=1)
```

The same 16 subclass-rejection subtests reproduced the boundary failure; all existing tests and plain-array controls still passed. This is the observed RED immediately preceding the minimal production change. No test/import/setup error or warning was emitted; the one test ERROR is the reproduced matrix-pose production IndexError.

### Fix 1 — minimal guard and GREEN

Changed only the shared component validator's `isinstance(array, np.ndarray)` admission to exact `type(array) is np.ndarray`, retaining the explicit None path and every shape/dtype/finiteness/normalization rule. Short-circuit evaluation now rejects subclasses before reading overridden dtype/shape or invoking ufuncs, indexing or conversion. The component-specific error now explicitly says "plain real numeric ndarray". No coercion, mask removal or fabricated values were introduced.

Command: `FIX_TEST`. Exit: **0**. Actual terminal summary:

```text
Ran 40 tests in 0.622s

OK
```

All 16 subclass-rejection subtests and ordinary numeric/plain/strided/read-only controls pass. Existing conversion, missing-component, finite-check, geometry, no-mutation and temporal tests remain green. No warnings, failures, errors or skips were emitted. No unrelated refactor or detector edit was made.

### Fix 1 — final package discovery and outcome

Fresh final command: `FIX_TEST`. Exit: **0**. Actual terminal summary:

```text
Ran 40 tests in 0.247s

OK
```

- Final package discovery: **40 passed**, no failures/errors/skips or emitted warnings. The type-boundary slice contributes two new test methods; the rejection method exercises 16 component/type subtests. The positive-control method passes for int32, int64, uint16, float16, float32 and float64 arrays in plain, strided and read-only-strided layouts. Those plain-array properties already passed during RED; the only production change is subclass admission/error wording.
- Additional command: `git diff --check && git diff --exit-code && git status --short && git branch --show-current`; exit **0**. Tracked diff remains empty. Status still lists only `?? HOLISTIC_MIGRATION_PLAN.md`, `?? docs/holistic-migration/`, `?? training/holistic_migration/`; branch remains `holistic-migration`. Because the package/report are untracked, the tracked-diff result is not claimed to identify every changed untracked file.
- Files written by this bounded fix: `training/holistic_migration/features.py`, `training/holistic_migration/tests/test_features.py`, and append-only additions to this report. No new files were created. Existing test methods, detector source/tests, FEATURES.md, reviews and requirements were not edited. The optional unused-import cleanup was deliberately left alone.
- No installs, commits, downloads, native detector/model/camera/data operations, other-worktree access, preview, extraction or training dispatch occurred. Only synthetic in-memory fixtures and the required package tests were used. The minor fixture typing diagnostic was corrected before the confirmed RED; no remaining blocker was encountered in this fix.
- L01's boundary regression is now green, but acceptance remains pending the parent's fresh review package and independent re-review. Previous runtime/anatomical/data/linguistic/training/mobile gates remain open. No dependent phase is authorized by these unit results.

