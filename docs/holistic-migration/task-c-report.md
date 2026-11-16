# Task C — append-only execution ledger

Scope: offline only; no camera/GUI, installs, fitting, bulk real inference, optimization, commits or provider changes. Accepted Task A/B are immutable.

Initial preflight: branch holistic-migration; HEAD 4d901693642af5f572455b2c75ba095b0ec65c7f; all 11 protected hashes matched; all 10 owned paths initially absent; tracked diff empty.

Evidence directory: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844`. Runtime: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B`. Synthetic tests are not FSL evidence.

## 01-clock-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_sequence.py -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/01-clock-RED.log`.

```text
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'training.holistic_migration.sequence'
import_ = <function _gcd_import at 0x102d2fd80>

>   ???
E   ModuleNotFoundError: No module named 'training.holistic_migration.sequence'

<frozen importlib._bootstrap>:1140: ModuleNotFoundError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_sequence.py::test_clock_first_and_due_slot
============================== 1 failed in 0.20s ===============================
```

## 01-clock-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_sequence.py -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/01-clock-GREEN.log`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
cachedir: .pytest_cache
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 1 item

training/holistic_migration/tests/test_sequence.py::test_clock_first_and_due_slot PASSED [100%]

============================== 1 passed in 0.15s ===============================
```

## 02-clock-boundaries-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_sequence.py -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/02-clock-boundaries-RED.log`.

```text
        assert not clock.admit(1)
>       with pytest.raises(ValueError):
E       Failed: DID NOT RAISE ValueError

training/holistic_migration/tests/test_sequence.py:25: Failed
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_sequence.py::test_clock_validates_skipped_inputs_without_mutation[True]
FAILED training/holistic_migration/tests/test_sequence.py::test_clock_validates_skipped_inputs_without_mutation[2.0]
FAILED training/holistic_migration/tests/test_sequence.py::test_clock_validates_skipped_inputs_without_mutation[-1]
FAILED training/holistic_migration/tests/test_sequence.py::test_clock_validates_skipped_inputs_without_mutation[0]
FAILED training/holistic_migration/tests/test_sequence.py::test_clock_validates_skipped_inputs_without_mutation[1]
========================= 5 failed, 4 passed in 0.14s ==========================
```

## 02-clock-boundaries-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_sequence.py -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/02-clock-boundaries-GREEN.log`.

```text

training/holistic_migration/tests/test_sequence.py::test_clock_first_and_due_slot PASSED [ 11%]
training/holistic_migration/tests/test_sequence.py::test_clock_quantization[30] PASSED [ 22%]
training/holistic_migration/tests/test_sequence.py::test_clock_quantization[60] PASSED [ 33%]
training/holistic_migration/tests/test_sequence.py::test_clock_validates_skipped_inputs_without_mutation[True] PASSED [ 44%]
training/holistic_migration/tests/test_sequence.py::test_clock_validates_skipped_inputs_without_mutation[2.0] PASSED [ 55%]
training/holistic_migration/tests/test_sequence.py::test_clock_validates_skipped_inputs_without_mutation[-1] PASSED [ 66%]
training/holistic_migration/tests/test_sequence.py::test_clock_validates_skipped_inputs_without_mutation[0] PASSED [ 77%]
training/holistic_migration/tests/test_sequence.py::test_clock_validates_skipped_inputs_without_mutation[1] PASSED [ 88%]
training/holistic_migration/tests/test_sequence.py::test_clock_long_gap_has_no_fabrication PASSED [100%]

============================== 9 passed in 0.15s ===============================
```

## 03-capture-positive-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_sequence.py -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/03-capture-positive-RED.log`.

```text
_______________ test_capture_positive_exact_accepted_resampling ________________

    def test_capture_positive_exact_accepted_resampling():
        observed = frames()
>       result = importlib.import_module('training.holistic_migration.sequence').prepare_capture(observed)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: module 'training.holistic_migration.sequence' has no attribute 'prepare_capture'

training/holistic_migration/tests/test_sequence.py:46: AttributeError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_sequence.py::test_capture_positive_exact_accepted_resampling
========================= 1 failed, 9 passed in 0.14s ==========================
```

## 03-capture-positive-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_sequence.py -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/03-capture-positive-GREEN.log`.

```text
training/holistic_migration/tests/test_sequence.py::test_clock_first_and_due_slot PASSED [ 10%]
training/holistic_migration/tests/test_sequence.py::test_clock_quantization[30] PASSED [ 20%]
training/holistic_migration/tests/test_sequence.py::test_clock_quantization[60] PASSED [ 30%]
training/holistic_migration/tests/test_sequence.py::test_clock_validates_skipped_inputs_without_mutation[True] PASSED [ 40%]
training/holistic_migration/tests/test_sequence.py::test_clock_validates_skipped_inputs_without_mutation[2.0] PASSED [ 50%]
training/holistic_migration/tests/test_sequence.py::test_clock_validates_skipped_inputs_without_mutation[-1] PASSED [ 60%]
training/holistic_migration/tests/test_sequence.py::test_clock_validates_skipped_inputs_without_mutation[0] PASSED [ 70%]
training/holistic_migration/tests/test_sequence.py::test_clock_validates_skipped_inputs_without_mutation[1] PASSED [ 80%]
training/holistic_migration/tests/test_sequence.py::test_clock_long_gap_has_no_fabrication PASSED [ 90%]
training/holistic_migration/tests/test_sequence.py::test_capture_positive_exact_accepted_resampling PASSED [100%]

============================== 10 passed in 0.18s ==============================
```

## 04-capture-coverage-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_sequence.py -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/04-capture-coverage-RED.log`.

```text
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_sequence.py::test_capture_trims_only_ends_and_keeps_internal_missing_hands
FAILED training/holistic_migration/tests/test_sequence.py::test_capture_fixed_coverage_reasons[empty-no_hands]
FAILED training/holistic_migration/tests/test_sequence.py::test_capture_fixed_coverage_reasons[handless-no_hands]
FAILED training/holistic_migration/tests/test_sequence.py::test_capture_fixed_coverage_reasons[few-too_few_observations]
FAILED training/holistic_migration/tests/test_sequence.py::test_capture_fixed_coverage_reasons[few_hands-too_few_hand_observations]
FAILED training/holistic_migration/tests/test_sequence.py::test_capture_fixed_coverage_reasons[short-too_short]
FAILED training/holistic_migration/tests/test_sequence.py::test_capture_fixed_coverage_reasons[long-too_long]
FAILED training/holistic_migration/tests/test_sequence.py::test_capture_fixed_coverage_reasons[gap-observation_gap]
FAILED training/holistic_migration/tests/test_sequence.py::test_capture_fixed_coverage_reasons[pose-invalid_pose]
FAILED training/holistic_migration/tests/test_sequence.py::test_capture_gap_boundary[251-False]
======================== 10 failed, 20 passed in 0.27s =========================
```

## 04-capture-coverage-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_sequence.py -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/04-capture-coverage-GREEN.log`.

```text
training/holistic_migration/tests/test_sequence.py::test_capture_gap_boundary[251-False] PASSED [ 70%]
training/holistic_migration/tests/test_sequence.py::test_capture_inclusive_duration[400] PASSED [ 73%]
training/holistic_migration/tests/test_sequence.py::test_capture_inclusive_duration[5000] PASSED [ 76%]
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[bool_timestamp] PASSED [ 80%]
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[float_timestamp] PASSED [ 83%]
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[duplicate] PASSED [ 86%]
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[nonfinite] PASSED [ 90%]
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[shape] PASSED [ 93%]
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[masked] PASSED [ 96%]
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[matrix] PASSED [100%]

============================== 30 passed in 0.22s ==============================
```

## 05-image-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_sequence.py -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/05-image-RED.log`.

```text
>           importlib.import_module('training.holistic_migration.sequence').prepare_image(image, cv2)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E           AttributeError: module 'training.holistic_migration.sequence' has no attribute 'prepare_image'

training/holistic_migration/tests/test_sequence.py:137: AttributeError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_sequence.py::test_plain_rgb_resize_uses_area_and_preserves_rgb
FAILED training/holistic_migration/tests/test_sequence.py::test_image_rejects_semantic_or_invalid_arrays[image0]
FAILED training/holistic_migration/tests/test_sequence.py::test_image_rejects_semantic_or_invalid_arrays[image1]
FAILED training/holistic_migration/tests/test_sequence.py::test_image_rejects_semantic_or_invalid_arrays[image2]
FAILED training/holistic_migration/tests/test_sequence.py::test_image_rejects_semantic_or_invalid_arrays[image3]
========================= 5 failed, 30 passed in 0.57s =========================
```

## 05-image-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_sequence.py -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/05-image-GREEN.log`.

```text
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[duplicate] PASSED [ 74%]
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[nonfinite] PASSED [ 77%]
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[shape] PASSED [ 80%]
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[masked] PASSED [ 82%]
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[matrix] PASSED [ 85%]
training/holistic_migration/tests/test_sequence.py::test_plain_rgb_resize_uses_area_and_preserves_rgb PASSED [ 88%]
training/holistic_migration/tests/test_sequence.py::test_image_rejects_semantic_or_invalid_arrays[image0] PASSED [ 91%]
training/holistic_migration/tests/test_sequence.py::test_image_rejects_semantic_or_invalid_arrays[image1] PASSED [ 94%]
training/holistic_migration/tests/test_sequence.py::test_image_rejects_semantic_or_invalid_arrays[image2] PASSED [ 97%]
training/holistic_migration/tests/test_sequence.py::test_image_rejects_semantic_or_invalid_arrays[image3] PASSED [100%]

============================== 35 passed in 0.47s ==============================
```

## 06-codec-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_dataset.py -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/06-codec-RED.log`.

```text
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'training.holistic_migration.dataset'
import_ = <function _gcd_import at 0x10072fd80>

>   ???
E   ModuleNotFoundError: No module named 'training.holistic_migration.dataset'

<frozen importlib._bootstrap>:1140: ModuleNotFoundError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_dataset.py::test_raw_codec_roundtrip_exact_none_and_variable_face
============================== 1 failed in 0.17s ===============================
```

## 06-codec-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_dataset.py -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/06-codec-GREEN.log`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
cachedir: .pytest_cache
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 1 item

training/holistic_migration/tests/test_dataset.py::test_raw_codec_roundtrip_exact_none_and_variable_face PASSED [100%]

============================== 1 passed in 0.23s ===============================
```

## 07-codec-corruption-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_dataset.py -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/07-codec-corruption-RED.log`.

```text
training/holistic_migration/tests/test_dataset.py:68: Failed
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[offset]
FAILED training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[float_timestamp]
FAILED training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[bool_presence]
FAILED training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[absent_block]
FAILED training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[absent_face]
FAILED training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[nonfinite]
FAILED training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[extra]
FAILED training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[duplicate_time]
FAILED training/holistic_migration/tests/test_dataset.py::test_raw_writer_rejects_masked_and_nonmonotonic
========================= 9 failed, 3 passed in 0.25s ==========================
```

## 07-codec-corruption-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_dataset.py -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/07-codec-corruption-GREEN.log`.

```text
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[float_timestamp] PASSED [ 25%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[bool_presence] PASSED [ 33%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[absent_block] PASSED [ 41%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[absent_face] PASSED [ 50%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[nonfinite] PASSED [ 58%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[object] PASSED [ 66%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[extra] PASSED [ 75%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[duplicate_time] PASSED [ 83%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[digest] PASSED [ 91%]
training/holistic_migration/tests/test_dataset.py::test_raw_writer_rejects_masked_and_nonmonotonic PASSED [100%]

============================== 12 passed in 0.24s ==============================
```

## 08-graph-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_dataset.py -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/08-graph-RED.log`.

```text
tmp_path = PosixPath('/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/pytest-of-ahronjanl.rafaelahron.0804icloudcom/pytest-4/test_public_preflight_validate0')

    def test_public_preflight_validates_complete_synthetic_graph(tmp_path):
        kwargs=graph_fixture(tmp_path/'source')
>       graph=dataset().preflight(**kwargs,output=tmp_path/'campaign')
              ^^^^^^^^^^^^^^^^^^^
E       AttributeError: module 'training.holistic_migration.dataset' has no attribute 'preflight'

training/holistic_migration/tests/test_dataset.py:134: AttributeError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_validates_complete_synthetic_graph
========================= 1 failed, 12 passed in 0.31s =========================
```

## 08-graph-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_dataset.py -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/08-graph-GREEN.log`.

```text
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[bool_presence] PASSED [ 30%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[absent_block] PASSED [ 38%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[absent_face] PASSED [ 46%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[nonfinite] PASSED [ 53%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[object] PASSED [ 61%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[extra] PASSED [ 69%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[duplicate_time] PASSED [ 76%]
training/holistic_migration/tests/test_dataset.py::test_raw_codec_rejects_corruption_even_rebound_digest[digest] PASSED [ 84%]
training/holistic_migration/tests/test_dataset.py::test_raw_writer_rejects_masked_and_nonmonotonic PASSED [ 92%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_validates_complete_synthetic_graph PASSED [100%]

============================== 13 passed in 0.31s ==============================
```

## 09-graph-schema-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_dataset.py -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/09-graph-schema-RED.log`.

```text
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[traversal-clip_id]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[bad_token-source_token]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[test_to_fit-official]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[identity-identity]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[archive-archive]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[decode_count-source_count]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[pixel_duplicate-duplicate]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[upstream_count-count]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[class_order-class]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[class_bool-class]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[partition-partition]
======================== 17 failed, 13 passed in 0.95s =========================
```

## 09-graph-schema-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_dataset.py -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/09-graph-schema-GREEN.log`.

```text
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[bad_token-source_token] PASSED [ 70%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[test_to_fit-official] PASSED [ 73%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[identity-identity] PASSED [ 76%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[archive-archive] PASSED [ 80%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[decode_count-source_count] PASSED [ 83%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[pixel_duplicate-duplicate] PASSED [ 86%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[upstream_count-count] PASSED [ 90%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[class_order-class] PASSED [ 93%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[class_bool-class] PASSED [ 96%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[partition-partition] PASSED [100%]

============================== 30 passed in 0.87s ==============================
```

## 10-path-preflight-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_dataset.py -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/10-path-preflight-RED.log`.

```text
training/holistic_migration/tests/test_dataset.py:223: AssertionError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[existing-exists]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[inside_raw-overlap]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[inside_repo-repository]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[ancestor-overlap]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[symlink-symlink]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[raw_symlink-symlink]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[relative-absolute]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[dataless-DATALESS]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[stale-digest]
========================= 9 failed, 30 passed in 1.20s =========================
```

## 10-path-preflight-corrected-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_dataset.py -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/10-path-preflight-corrected-RED.log`.

```text

training/holistic_migration/tests/test_dataset.py:223: Failed
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[existing-exists]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[inside_raw-overlap]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[inside_repo-repository]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[ancestor-overlap]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[symlink-symlink]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[raw_symlink-symlink]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[relative-absolute]
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[dataless-DATALESS]
========================= 8 failed, 31 passed in 1.47s =========================
```

## 10-path-preflight-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_dataset.py -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/10-path-preflight-GREEN.log`.

```text
training/holistic_migration/tests/test_dataset.py::test_public_preflight_rebound_tampering[partition-partition] PASSED [ 76%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[existing-exists] PASSED [ 79%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[inside_raw-overlap] PASSED [ 82%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[inside_repo-repository] PASSED [ 84%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[ancestor-overlap] PASSED [ 87%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[symlink-symlink] PASSED [ 89%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[raw_symlink-symlink] PASSED [ 92%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[relative-absolute] PASSED [ 94%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[dataless-DATALESS] PASSED [ 97%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[stale-digest] PASSED [100%]

============================== 39 passed in 1.47s ==============================
```

## 11-extraction-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_extract.py -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/11-extraction-RED.log`.

```text
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'training.holistic_migration.extract'
import_ = <function _gcd_import at 0x1002d7d80>

>   ???
E   ModuleNotFoundError: No module named 'training.holistic_migration.extract'

<frozen importlib._bootstrap>:1140: ModuleNotFoundError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_extract.py::test_extraction_complete_production_path_synthetic
============================== 1 failed in 0.60s ===============================
```

## 11-extraction-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_extract.py -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/11-extraction-GREEN.log`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
cachedir: .pytest_cache
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 1 item

training/holistic_migration/tests/test_extract.py::test_extraction_complete_production_path_synthetic PASSED [100%]

============================== 1 passed in 1.71s ===============================
```

## 12-diagnostic-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_extract.py -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/12-diagnostic-RED.log`.

```text
inputs = {'partition_manifest': PosixPath('/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/pytest-of-ahronjanl...ache/scratch/pytest-of-ahronjanl.rafaelahron.0804icloudcom/pytest-13/test_diagnostic_selects_litera0/source/raw'), ...}

    def run_extraction(*, output, video_factory=None, detector_factory=None, cv=None, **inputs):
        """Trusted Python injection only for synthetic tests; never a CLI module loader."""
>       graph=preflight(**inputs,output=output)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: preflight() got an unexpected keyword argument 'diagnostic_fit_only'

training/holistic_migration/extract.py:13: TypeError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_extract.py::test_diagnostic_selects_literal_first_fit_only_before_inference
========================= 1 failed, 1 passed in 1.72s ==========================
```

## 12-diagnostic-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_extract.py -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/12-diagnostic-GREEN.log`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
cachedir: .pytest_cache
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 2 items

training/holistic_migration/tests/test_extract.py::test_extraction_complete_production_path_synthetic PASSED [ 50%]
training/holistic_migration/tests/test_extract.py::test_diagnostic_selects_literal_first_fit_only_before_inference PASSED [100%]

============================== 2 passed in 1.39s ===============================
```

## 13-extraction-errors-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_extract.py -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/13-extraction-errors-RED.log`.

```text
FAILED training/holistic_migration/tests/test_extract.py::test_extraction_failure_ledger_all_declared_cleanup_no_completion[nan-timestamp_error]
FAILED training/holistic_migration/tests/test_extract.py::test_extraction_failure_ledger_all_declared_cleanup_no_completion[negative-timestamp_error]
FAILED training/holistic_migration/tests/test_extract.py::test_extraction_failure_ledger_all_declared_cleanup_no_completion[duplicate-timestamp_error]
FAILED training/holistic_migration/tests/test_extract.py::test_extraction_failure_ledger_all_declared_cleanup_no_completion[pixel-decode_error]
FAILED training/holistic_migration/tests/test_extract.py::test_extraction_failure_ledger_all_declared_cleanup_no_completion[short-decode_error]
FAILED training/holistic_migration/tests/test_extract.py::test_extraction_failure_ledger_all_declared_cleanup_no_completion[detection-detection_error]
FAILED training/holistic_migration/tests/test_extract.py::test_extraction_failure_ledger_all_declared_cleanup_no_completion[source-source_error]
FAILED training/holistic_migration/tests/test_extract.py::test_video_timestamp_rejects_invalid_without_rounding_it_away[True]
FAILED training/holistic_migration/tests/test_extract.py::test_video_timestamp_rejects_invalid_without_rounding_it_away[inf]
FAILED training/holistic_migration/tests/test_extract.py::test_video_timestamp_rejects_invalid_without_rounding_it_away[-0.001]
FAILED training/holistic_migration/tests/test_extract.py::test_video_timestamp_rejects_invalid_without_rounding_it_away[12]
========================= 11 failed, 4 passed in 1.68s =========================
```

## 13-extraction-errors-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_extract.py -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/13-extraction-errors-GREEN.log`.

```text
training/holistic_migration/tests/test_extract.py::test_extraction_failure_ledger_all_declared_cleanup_no_completion[pixel-decode_error] PASSED [ 40%]
training/holistic_migration/tests/test_extract.py::test_extraction_failure_ledger_all_declared_cleanup_no_completion[short-decode_error] PASSED [ 46%]
training/holistic_migration/tests/test_extract.py::test_extraction_failure_ledger_all_declared_cleanup_no_completion[detection-detection_error] PASSED [ 53%]
training/holistic_migration/tests/test_extract.py::test_extraction_failure_ledger_all_declared_cleanup_no_completion[source-source_error] PASSED [ 60%]
training/holistic_migration/tests/test_extract.py::test_extraction_public_preflight_before_runtime_factories PASSED [ 66%]
training/holistic_migration/tests/test_extract.py::test_video_timestamp_rejects_invalid_without_rounding_it_away[True] PASSED [ 73%]
training/holistic_migration/tests/test_extract.py::test_video_timestamp_rejects_invalid_without_rounding_it_away[nan] PASSED [ 80%]
training/holistic_migration/tests/test_extract.py::test_video_timestamp_rejects_invalid_without_rounding_it_away[inf] PASSED [ 86%]
training/holistic_migration/tests/test_extract.py::test_video_timestamp_rejects_invalid_without_rounding_it_away[-0.001] PASSED [ 93%]
training/holistic_migration/tests/test_extract.py::test_video_timestamp_rejects_invalid_without_rounding_it_away[12] PASSED [100%]

============================== 15 passed in 3.74s ==============================
```

## 14-extraction-cli-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_extract.py -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/14-extraction-cli-RED.log`.

```text
            if name in ['cv2','mediapipe']: raise AssertionError('native import before preflight')
            return real(name,*args,**kw)
        monkeypatch.setattr(builtins,'__import__',guarded)
>       assert extract().main(cli_args(kwargs,out))==2
               ^^^^^^^^^^^^^^
E       AttributeError: module 'training.holistic_migration.extract' has no attribute 'main'

training/holistic_migration/tests/test_extract.py:165: AttributeError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_extract.py::test_extraction_cli_help_and_invalid_preflight_in_real_process
FAILED training/holistic_migration/tests/test_extract.py::test_extraction_main_preflight_failure_never_imports_native
========================= 2 failed, 15 passed in 3.55s =========================
```

## 14-extraction-cli-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_extract.py -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/14-extraction-cli-GREEN.log`.

```text
training/holistic_migration/tests/test_extract.py::test_extraction_failure_ledger_all_declared_cleanup_no_completion[detection-detection_error] PASSED [ 47%]
training/holistic_migration/tests/test_extract.py::test_extraction_failure_ledger_all_declared_cleanup_no_completion[source-source_error] PASSED [ 52%]
training/holistic_migration/tests/test_extract.py::test_extraction_public_preflight_before_runtime_factories PASSED [ 58%]
training/holistic_migration/tests/test_extract.py::test_video_timestamp_rejects_invalid_without_rounding_it_away[True] PASSED [ 64%]
training/holistic_migration/tests/test_extract.py::test_video_timestamp_rejects_invalid_without_rounding_it_away[nan] PASSED [ 70%]
training/holistic_migration/tests/test_extract.py::test_video_timestamp_rejects_invalid_without_rounding_it_away[inf] PASSED [ 76%]
training/holistic_migration/tests/test_extract.py::test_video_timestamp_rejects_invalid_without_rounding_it_away[-0.001] PASSED [ 82%]
training/holistic_migration/tests/test_extract.py::test_video_timestamp_rejects_invalid_without_rounding_it_away[12] PASSED [ 88%]
training/holistic_migration/tests/test_extract.py::test_extraction_cli_help_and_invalid_preflight_in_real_process PASSED [ 94%]
training/holistic_migration/tests/test_extract.py::test_extraction_main_preflight_failure_never_imports_native PASSED [100%]

============================== 17 passed in 3.86s ==============================
```

## 15-bundle-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_dataset.py::test_canonical_bundle_production_flow_exact_ids_and_tensors -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/15-bundle-RED.log`.

```text
142/150 clips/73/0.MOV eligible
143/150 clips/73/1.MOV eligible
144/150 clips/73/2.MOV eligible
145/150 clips/8/0.MOV eligible
146/150 clips/8/1.MOV eligible
147/150 clips/8/2.MOV eligible
148/150 clips/9/0.MOV eligible
149/150 clips/9/1.MOV eligible
150/150 clips/9/2.MOV eligible
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_dataset.py::test_canonical_bundle_production_flow_exact_ids_and_tensors
============================== 1 failed in 1.33s ===============================
```

## 15-bundle-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_dataset.py::test_canonical_bundle_production_flow_exact_ids_and_tensors -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/15-bundle-GREEN.log`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
cachedir: .pytest_cache
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 1 item

training/holistic_migration/tests/test_dataset.py::test_canonical_bundle_production_flow_exact_ids_and_tensors PASSED [100%]

============================== 1 passed in 1.83s ===============================
```

## 16-bundle-guards-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_dataset.py -k bundle -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/16-bundle-guards-RED.log`.

```text
149/150 clips/9/1.MOV eligible
150/150 clips/9/2.MOV eligible
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[diagnostic]
FAILED training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[disguised_diagnostic]
FAILED training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[row_missing]
FAILED training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[row_duplicate]
FAILED training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[row_identity]
FAILED training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[raw_traversal]
FAILED training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[raw_symlink]
FAILED training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[count_float]
================= 8 failed, 7 passed, 39 deselected in 15.75s ==================
```

## 16-bundle-guards-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_dataset.py -k bundle -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/16-bundle-guards-GREEN.log`.

```text
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[row_missing] PASSED [ 40%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[row_duplicate] PASSED [ 46%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[row_identity] PASSED [ 53%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[raw_traversal] PASSED [ 60%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[raw_symlink] PASSED [ 66%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[count_float] PASSED [ 73%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[raw_digest] PASSED [ 80%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[capture] PASSED [ 86%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[existing] PASSED [ 93%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[current_contract] PASSED [100%]

====================== 15 passed, 39 deselected in 13.48s ======================
```

## 17-eligibility-support-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_dataset.py -k support or all_test_ineligibility -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/17-eligibility-support-RED.log`.

```text
143/150 clips/73/1.MOV eligible
144/150 clips/73/2.MOV eligible
145/150 clips/8/0.MOV eligible
146/150 clips/8/1.MOV eligible
147/150 clips/8/2.MOV eligible
148/150 clips/9/0.MOV eligible
149/150 clips/9/1.MOV eligible
150/150 clips/9/2.MOV eligible
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_dataset.py::test_bundle_requires_all_class_support_retains_failed_denominators[fit]
FAILED training/holistic_migration/tests/test_dataset.py::test_bundle_requires_all_class_support_retains_failed_denominators[validation]
================== 2 failed, 1 passed, 54 deselected in 3.31s ==================
```

## 17-eligibility-support-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_dataset.py -k support or all_test_ineligibility -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/17-eligibility-support-GREEN.log`.

```text
143/150 clips/73/1.MOV eligible
144/150 clips/73/2.MOV eligible
145/150 clips/8/0.MOV eligible
146/150 clips/8/1.MOV eligible
147/150 clips/8/2.MOV eligible
148/150 clips/9/0.MOV eligible
149/150 clips/9/1.MOV eligible
150/150 clips/9/2.MOV eligible
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_dataset.py::test_bundle_requires_all_class_support_retains_failed_denominators[fit]
FAILED training/holistic_migration/tests/test_dataset.py::test_bundle_requires_all_class_support_retains_failed_denominators[validation]
================== 2 failed, 1 passed, 54 deselected in 3.77s ==================
```

## 17-eligibility-support-corrected-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_dataset.py -k support or all_test_ineligibility -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/17-eligibility-support-corrected-GREEN.log`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
cachedir: .pytest_cache
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 57 items / 54 deselected / 3 selected

training/holistic_migration/tests/test_dataset.py::test_bundle_requires_all_class_support_retains_failed_denominators[fit] PASSED [ 33%]
training/holistic_migration/tests/test_dataset.py::test_bundle_requires_all_class_support_retains_failed_denominators[validation] PASSED [ 66%]
training/holistic_migration/tests/test_dataset.py::test_bundle_reports_all_test_ineligibility_without_zero_examples PASSED [100%]

======================= 3 passed, 54 deselected in 3.62s =======================
```

## 18-final-readback-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_dataset.py -k final_readback -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/18-final-readback-RED.log`.

```text
145/150 clips/8/0.MOV eligible
146/150 clips/8/1.MOV eligible
147/150 clips/8/2.MOV eligible
148/150 clips/9/0.MOV eligible
149/150 clips/9/1.MOV eligible
150/150 clips/9/2.MOV eligible
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_dataset.py::test_bundle_final_readback_rejects_midbuild_tamper[X_fit.npy]
FAILED training/holistic_migration/tests/test_dataset.py::test_bundle_final_readback_rejects_midbuild_tamper[X_validation.npy]
FAILED training/holistic_migration/tests/test_dataset.py::test_bundle_final_readback_rejects_midbuild_tamper[eligibility.json]
FAILED training/holistic_migration/tests/test_dataset.py::test_bundle_final_readback_rejects_midbuild_tamper[campaign_raw]
======================= 4 failed, 57 deselected in 4.77s =======================
```

## 18-final-readback-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_dataset.py -k final_readback -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/18-final-readback-GREEN.log`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
cachedir: .pytest_cache
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 61 items / 57 deselected / 4 selected

training/holistic_migration/tests/test_dataset.py::test_bundle_final_readback_rejects_midbuild_tamper[X_fit.npy] PASSED [ 25%]
training/holistic_migration/tests/test_dataset.py::test_bundle_final_readback_rejects_midbuild_tamper[X_validation.npy] PASSED [ 50%]
training/holistic_migration/tests/test_dataset.py::test_bundle_final_readback_rejects_midbuild_tamper[eligibility.json] PASSED [ 75%]
training/holistic_migration/tests/test_dataset.py::test_bundle_final_readback_rejects_midbuild_tamper[campaign_raw] PASSED [100%]

======================= 4 passed, 57 deselected in 4.68s =======================
```

## 19-builder-cli-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_dataset.py -k bundle_cli -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/19-builder-cli-RED.log`.

```text
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'training.holistic_migration.build_dataset'
import_ = <function _gcd_import at 0x1021c3d80>

>   ???
E   ModuleNotFoundError: No module named 'training.holistic_migration.build_dataset'

<frozen importlib._bootstrap>:1140: ModuleNotFoundError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_dataset.py::test_bundle_cli_help_success_failure_and_no_native_imports
======================= 1 failed, 61 deselected in 0.28s =======================
```

## 19-builder-cli-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_dataset.py -k bundle_cli -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/19-builder-cli-GREEN.log`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
cachedir: .pytest_cache
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 62 items / 61 deselected / 1 selected

training/holistic_migration/tests/test_dataset.py::test_bundle_cli_help_success_failure_and_no_native_imports PASSED [100%]

======================= 1 passed, 61 deselected in 3.12s =======================
```

## 20-audit-byte-format-readback-no-inference

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -c from pathlib import Path
import json,hashlib,numpy as np,cv2
from training.holistic_migration.dataset import safe_path,sha256
root=Path('/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data')
rows=json.loads((root/'candidate-partitions-v1.json').read_text())['rows']
row=next(r for r in rows if r['clip_id']=='clips/0/0.MOV' and r['partition']=='fit')
p=safe_path(root/'clips_raw'/row['clip_id'],must_exist=True)
assert sha256(p)==row['video_sha256'] and p.stat().st_size==row['video_bytes']
audit=next(json.loads(x) for x in (root/'decoded-source-audit-v1/records.jsonl').read_text().splitlines() if json.loads(x)['clip_id']==row['clip_id'])
cap=cv2.VideoCapture(str(p)); h={kind:hashlib.sha256() for kind in ['<i4','<i8']}; count=0
try:
 while True:
  ok,bgr=cap.read()
  if not ok: break
  count+=1
  for kind,d in h.items():
   d.update(np.asarray(bgr.shape,dtype=kind).tobytes());d.update(np.ascontiguousarray(bgr).tobytes())
finally: cap.release()
print({'clip_id':row['clip_id'],'decoded_count':count,'audit_count':audit['decoded_frames'],'audit_digest':audit['decoded_bgr_sha256'],'candidate_digests':{k:v.hexdigest() for k,v in h.items()},'inference_calls':0})
assert count==audit['decoded_frames']
assert h['<i4'].hexdigest()==audit['decoded_bgr_sha256']
`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/20-audit-byte-format-readback-no-inference.log`.

```text
{'clip_id': 'clips/0/0.MOV', 'decoded_count': 245, 'audit_count': 245, 'audit_digest': '539b7b9534b42aa6b752b6973dc655c4afde0d1f69cae37d28d86f24f8de38c1', 'candidate_digests': {'<i4': '539b7b9534b42aa6b752b6973dc655c4afde0d1f69cae37d28d86f24f8de38c1', '<i8': '340df48f1f7da36cb6a472e2e5248a8eafa2489bd1bbbd026299e8fdf50457d2'}, 'inference_calls': 0}
```

## 21-real-graph-preflight-no-media-open

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -c from pathlib import Path
from collections import Counter
from training.holistic_migration.dataset import preflight
r=Path('/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration')
d=r.parent/'holistic-migration-data'
g=preflight(partition_manifest=d/'candidate-partitions-v1.json',source_inventory=d/'verified-video-byte-inventory.json',decode_summary=d/'decoded-source-audit-v1/summary.json',raw_root=d/'clips_raw',classes=r/'training/preprocessing/selected_classes.json',model=d/'holistic_landmarker.task')
print({'sources':len(g.rows),'partitions':dict(Counter(r['partition'] for r in g.rows)),'classes':len(g.classes),'dense25':g.classes[25],'bindings':g.bindings})
`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/21-real-graph-preflight-no-media-open.log`.

```text
{'sources': 1016, 'partitions': {'fit': 663, 'test': 203, 'validation': 150}, 'classes': 50, 'dense25': {'dense_id': 25, 'original_id': 49, 'label': 'TODAY', 'category': 'DAYS'}, 'bindings': {'partition_manifest': 'a80620494894701c9f4f2dfde5a3050f4f80b5532b04004c0761c7945300275f', 'source_inventory': '0ff0c09c7df877c860258049427243aacc03d5f35ef11526715366f28940d41e', 'decode_summary': '57c5e676fab823a5d96d2cedf44bb4b69f03b6530dc557817553a383f1b44035', 'classes': 'e8089f5c0186bfe6fd9ec63a5150f8094645c1686509f23c1716453b5f9ce0d5', 'model': 'e2dab61191e2dcd0a15f943d8e3ed1dce13c82dfa597b9dd39f562975a50c3f8', 'decode_records': 'a1926b7f0d3ecc7788db4126fd435a287c867519e642ff9770aeddcc74f63e3b', 'upstream_inventory': '23697b80445fe1daedd9dfb1d1127e02e1a474eb13144ff5fcad9e4d589701ca'}}
```

## 22-lossless-strictness-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_dataset.py training/holistic_migration/tests/test_sequence.py -k loss_or_unsafe or equal_float or source_denominator -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/22-lossless-strictness-RED.log`.

```text
>       assert (result.source_observation_count,result.source_start_ms,result.source_end_ms)==(8,0,469)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'CaptureResult' object has no attribute 'source_observation_count'

training/holistic_migration/tests/test_sequence.py:145: AttributeError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_dataset.py::test_codec_rejects_loss_or_unsafe_read[unrepresentable_face]
FAILED training/holistic_migration/tests/test_dataset.py::test_codec_rejects_loss_or_unsafe_read[timestamp_range]
FAILED training/holistic_migration/tests/test_dataset.py::test_codec_rejects_loss_or_unsafe_read[symlink_read]
FAILED training/holistic_migration/tests/test_dataset.py::test_rebound_capture_equal_float_count_is_not_integer
FAILED training/holistic_migration/tests/test_sequence.py::test_capture_reports_source_denominator_even_when_no_bounded_interval
======================= 5 failed, 97 deselected in 1.49s =======================
```

## 22-lossless-strictness-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_dataset.py training/holistic_migration/tests/test_sequence.py -k loss_or_unsafe or equal_float or source_denominator -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/22-lossless-strictness-GREEN.log`.

```text
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
cachedir: .pytest_cache
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 102 items / 97 deselected / 5 selected

training/holistic_migration/tests/test_dataset.py::test_codec_rejects_loss_or_unsafe_read[unrepresentable_face] PASSED [ 20%]
training/holistic_migration/tests/test_dataset.py::test_codec_rejects_loss_or_unsafe_read[timestamp_range] PASSED [ 40%]
training/holistic_migration/tests/test_dataset.py::test_codec_rejects_loss_or_unsafe_read[symlink_read] PASSED [ 60%]
training/holistic_migration/tests/test_dataset.py::test_rebound_capture_equal_float_count_is_not_integer PASSED [ 80%]
training/holistic_migration/tests/test_sequence.py::test_capture_reports_source_denominator_even_when_no_bounded_interval PASSED [100%]

======================= 5 passed, 97 deselected in 0.90s =======================
```

## 23-real-binding-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_extract.py -k real_entry -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/23-real-binding-RED.log`.

```text
args = ({'__name__': 'training.holistic_migration.extract', '__doc__': 'Exclusive source-video extraction. Native dependencie...tic_migration', '__loader__': <_frozen_importlib_external.SourceFileLoader object at 0x10ad04550>, ...}, None, None, 0)
kw = {}

    def guarded(name,*args,**kw):
>       if name in ['cv2','mediapipe']: raise AssertionError('must reject nonfrozen inputs before native runtime')
                                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AssertionError: must reject nonfrozen inputs before native runtime

training/holistic_migration/tests/test_extract.py:175: AssertionError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_extract.py::test_real_entry_rejects_nonfrozen_synthetic_inputs_before_native_or_output
======================= 1 failed, 17 deselected in 0.27s =======================
```

## 23-real-binding-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_extract.py -k real_entry -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/23-real-binding-GREEN.log`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 18 items / 17 deselected / 1 selected

training/holistic_migration/tests/test_extract.py::test_real_entry_rejects_nonfrozen_synthetic_inputs_before_native_or_output PASSED [100%]

======================= 1 passed, 17 deselected in 0.25s =======================
```

## 24-installed-runtime-metadata

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -c import importlib.metadata as m,sys,platform
print(sys.version)
print(platform.platform())
for name in ['numpy','opencv-contrib-python','mediapipe','pytest']:
 print(name+'=='+m.version(name))
print('mediapipe requirements:',m.requires('mediapipe'))
`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/24-installed-runtime-metadata.log`.

```text
3.11.15 (main, Mar  3 2026, 00:52:57) [Clang 17.0.0 (clang-1700.6.3.2)]
macOS-26.6-arm64-arm-64bit
numpy==2.1.3
opencv-contrib-python==5.0.0.93
mediapipe==1.2.0
pytest==9.2.0
mediapipe requirements: ['absl-py~=2.3', 'certifi', 'numpy', 'sounddevice~=0.5', 'flatbuffers~=25.9', 'opencv-contrib-python', 'matplotlib']
```

## 25-manifest-publication-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_dataset.py -k failed_manifest -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/25-manifest-publication-RED.log`.

```text
143/150 clips/73/1.MOV eligible
144/150 clips/73/2.MOV eligible
145/150 clips/8/0.MOV eligible
146/150 clips/8/1.MOV eligible
147/150 clips/8/2.MOV eligible
148/150 clips/9/0.MOV eligible
149/150 clips/9/1.MOV eligible
150/150 clips/9/2.MOV eligible
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_dataset.py::test_failed_manifest_readback_never_leaves_completed_publication[data_manifest.json]
FAILED training/holistic_migration/tests/test_dataset.py::test_failed_manifest_readback_never_leaves_completed_publication[extraction_manifest.json]
======================= 2 failed, 66 deselected in 2.14s =======================
```

## 25-manifest-publication-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_dataset.py -k failed_manifest -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/25-manifest-publication-GREEN.log`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 68 items / 66 deselected / 2 selected

training/holistic_migration/tests/test_dataset.py::test_failed_manifest_readback_never_leaves_completed_publication[data_manifest.json] PASSED [ 50%]
training/holistic_migration/tests/test_dataset.py::test_failed_manifest_readback_never_leaves_completed_publication[extraction_manifest.json] PASSED [100%]

======================= 2 passed, 66 deselected in 2.18s =======================
```

## 26-contract-completeness-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_dataset.py -k contract_cannot or receipt_hashes -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/26-contract-completeness-RED.log`.

```text
        receipt=dataset().graph_receipt(g)
        for name in ['runtime','contract']:
            expected=hashlib.sha256(json.dumps(receipt[name],sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()).hexdigest()
>           assert receipt[name+'_sha256']==expected
                   ^^^^^^^^^^^^^^^^^^^^^^^
E           KeyError: 'runtime_sha256'

training/holistic_migration/tests/test_dataset.py:422: KeyError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_dataset.py::test_contract_cannot_silently_drop_missing_source_inputs
FAILED training/holistic_migration/tests/test_dataset.py::test_graph_receipt_hashes_runtime_and_contract_canonically
======================= 2 failed, 68 deselected in 0.26s =======================
```

## 26-contract-completeness-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_dataset.py -k contract_cannot or receipt_hashes -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/26-contract-completeness-GREEN.log`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 70 items / 68 deselected / 2 selected

training/holistic_migration/tests/test_dataset.py::test_contract_cannot_silently_drop_missing_source_inputs PASSED [ 50%]
training/holistic_migration/tests/test_dataset.py::test_graph_receipt_hashes_runtime_and_contract_canonically PASSED [100%]

======================= 2 passed, 68 deselected in 0.31s =======================
```

## 27-upstream-counts-RED

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_dataset.py -k requires_upstream -v`

Exit **1**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/27-upstream-counts-RED.log`.

```text

    def test_public_preflight_requires_upstream_official_counts(tmp_path):
        root=tmp_path/'source';kwargs=graph_fixture(root)
        upstream=json.loads((root/'selected-source-inventory.json').read_text());upstream.pop('counts')
        rebind(root,upstream=upstream)
>       with pytest.raises(ValueError,match='counts'): dataset().preflight(**kwargs)
E       Failed: DID NOT RAISE ValueError

training/holistic_migration/tests/test_dataset.py:430: Failed
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_dataset.py::test_public_preflight_requires_upstream_official_counts
======================= 1 failed, 70 deselected in 0.27s =======================
```

## 27-upstream-counts-GREEN

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_dataset.py -k requires_upstream -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/27-upstream-counts-GREEN.log`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 71 items / 70 deselected / 1 selected

training/holistic_migration/tests/test_dataset.py::test_public_preflight_requires_upstream_official_counts PASSED [100%]

======================= 1 passed, 70 deselected in 0.21s =======================
```

## 28-full-migration-suite

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/28-full-migration-suite.log`.

```text
training/holistic_migration/tests/test_webcam.py::PixelsAndOverlayTests::test_actual_bgra_conversion_resize_and_no_input_mirror PASSED [ 96%]
training/holistic_migration/tests/test_webcam.py::PixelsAndOverlayTests::test_missing_components_real_counts_masks_connections_and_readable_text PASSED [ 97%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_additional_failure_stages_keep_disposition_and_teardown 
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_additional_failure_stages_keep_disposition_and_teardown PASSED [ 97%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_default_runtime_binds_actual_shared_detector_and_packer_without_loading_sdk PASSED [ 98%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_errors_cleanup_fault_and_handshake_admission_before_detector 
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_errors_cleanup_fault_and_handshake_admission_before_detector PASSED [ 98%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_no_implicit_report_and_main_uses_same_runner PASSED [ 99%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_quit_escape_window_close_and_deadline_release_all 
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_quit_escape_window_close_and_deadline_release_all PASSED [100%]

================== 186 passed, 252 subtests passed in 39.97s ===================
```

## 29-original-training-suite

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/tests -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/29-original-training-suite.log`.

```text
    return np.array(x)

training/tests/test_export_frozen.py::FrozenExportTests::test_frozen_export_preserves_validation_predictions_and_hashes
  /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/lib/python3.11/site-packages/tensorflow/lite/python/interpreter.py:457: UserWarning:     Warning: tf.lite.Interpreter is deprecated and is scheduled for deletion in
      TF 2.20. Please use the LiteRT interpreter from the ai_edge_litert package.
      See the [migration guide](https://ai.google.dev/edge/litert/migration)
      for details.
      
    warnings.warn(_INTERPRETER_DELETION_WARNING)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
============= 51 passed, 3 warnings, 289 subtests passed in 8.79s ==============
```

## 30-persistent-synthetic-production-flow

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -c from pathlib import Path
import json
from training.holistic_migration.tests.test_extract import synthetic_campaign,SyntheticVideo,SyntheticDetector
from training.holistic_migration.extract import run_extraction
from training.holistic_migration.dataset import write_json
root=Path('/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/synthetic-smoke');root.mkdir()
kwargs,campaign,code=synthetic_campaign(root)
assert code==0
full=json.loads((campaign/'extraction_manifest.json').read_text())
diagnostic=root/'diagnostic'
code=run_extraction(**kwargs,output=diagnostic,diagnostic_fit_only=True,video_factory=SyntheticVideo,detector_factory=SyntheticDetector)
assert code==0
diag=json.loads((diagnostic/'extraction_manifest.json').read_text())
assert diag['status']=='diagnostic_fit_only' and diag['full_campaign_qualification'] is False
write_json(root/'smoke_receipt.json',dict(evidence_kind='synthetic_in_process',full_counts=full['counts'],diagnostic_counts=diag['counts'],diagnostic_status=diag['status'],real_inference_calls=0))
(root/'existing-target').mkdir()
print(json.dumps(json.loads((root/'smoke_receipt.json').read_text()),sort_keys=True))
`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/30-persistent-synthetic-production-flow.log`.

```text
140/150 clips/72/1.MOV not_selected
141/150 clips/72/2.MOV not_selected
142/150 clips/73/0.MOV eligible
143/150 clips/73/1.MOV not_selected
144/150 clips/73/2.MOV not_selected
145/150 clips/8/0.MOV eligible
146/150 clips/8/1.MOV not_selected
147/150 clips/8/2.MOV not_selected
148/150 clips/9/0.MOV eligible
149/150 clips/9/1.MOV not_selected
150/150 clips/9/2.MOV not_selected
{"diagnostic_counts": {"declared": 150, "errors": 0, "processed": 50, "selected": 50}, "diagnostic_status": "diagnostic_fit_only", "evidence_kind": "synthetic_in_process", "full_counts": {"declared": 150, "errors": 0, "processed": 150, "selected": 150}, "real_inference_calls": 0}
```

## 31-persistent-synthetic-builder-CLI

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m training.holistic_migration.build_dataset --campaign /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/synthetic-smoke/campaign --output /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/synthetic-smoke/bundle`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/31-persistent-synthetic-builder-CLI.log`.

```text
completed /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/synthetic-smoke/bundle/data_manifest.json; {'fit': {'declared': 50, 'eligible': 50, 'ineligible': 0, 'reasons': {}}, 'validation': {'declared': 50, 'eligible': 50, 'ineligible': 0, 'reasons': {}}, 'test': {'declared': 50, 'eligible': 50, 'ineligible': 0, 'reasons': {}}}
```

## 32-extract-help

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m training.holistic_migration.extract --help`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/32-extract-help.log`.

```text
options:
  -h, --help            show this help message and exit
  --partition-manifest PARTITION_MANIFEST
  --source-inventory SOURCE_INVENTORY
  --decode-summary DECODE_SUMMARY
  --raw-root RAW_ROOT
  --classes CLASSES
  --model MODEL
  --output OUTPUT
  --diagnostic-fit-only
                        Only literal first frozen fit clip per class; never a
                        full dataset
```

## 33-builder-help

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m training.holistic_migration.build_dataset --help`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/33-builder-help.log`.

```text
usage: build_dataset.py [-h] --campaign CAMPAIGN --output OUTPUT

Build unaugmented canonical arrays from a completed full extraction campaign.

options:
  -h, --help           show this help message and exit
  --campaign CAMPAIGN
  --output OUTPUT
```

## 34-extract-real-CLI-existing-target-rejection

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m training.holistic_migration.extract --partition-manifest /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/candidate-partitions-v1.json --source-inventory /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/verified-video-byte-inventory.json --decode-summary /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/decoded-source-audit-v1/summary.json --raw-root /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/clips_raw --classes /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/training/preprocessing/selected_classes.json --model /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/holistic_landmarker.task --output /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/synthetic-smoke/existing-target --diagnostic-fit-only`

Exit **2**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/34-extract-real-CLI-existing-target-rejection.log`.

```text
extraction rejected: output already exists; never reuse an attempt
```

## 35-builder-diagnostic-CLI-refusal

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m training.holistic_migration.build_dataset --campaign /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/synthetic-smoke/diagnostic --output /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/synthetic-smoke/diagnostic-never-bundle`

Exit **2**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/35-builder-diagnostic-CLI-refusal.log`.

```text
dataset rejected: only a complete full campaign is a dataset; diagnostic refused
```

## 36-cache-cleanup-and-source-scope-check

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -c from pathlib import Path
import hashlib,json,subprocess,ast,shutil,datetime
r=Path('/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration'); e=Path('/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844')
cache=r/'.pytest_cache'
if cache.exists():
 print('pytest cache birth',datetime.datetime.fromtimestamp(cache.stat().st_birthtime).isoformat())
 assert cache.stat().st_birthtime>=e.stat().st_birthtime
 shutil.rmtree(cache)
 print('removed only pytest cache created during this Task C run')
p=json.loads(Path('/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-preflight-e04637b40648410da2dfdfbc11cc1cc7/protected.json').read_text())
checks={name:hashlib.sha256((r/name).read_bytes()).hexdigest()==expected for name,expected in p['protected_source_sha256'].items()}
requirements={name:hashlib.sha256((r/name).read_bytes()).hexdigest()==expected for name,expected in p['requirements_sha256'].items()}
print('protected',checks,'requirements',requirements)
assert len(checks)==11 and all(checks.values()) and all(requirements.values())
assert len(p['new_owned_paths'])==10 and all((r/name).is_file() for name in p['new_owned_paths'])
for name in p['new_owned_paths']:
 if name.endswith('.py'):
  tree=ast.parse((r/name).read_text())
  if '/tests/' not in name:
   deps=[node.module for node in ast.walk(tree) if isinstance(node,ast.ImportFrom)]
   assert not any(mod and ('camera' in mod or 'webcam' in mod) for mod in deps)
   print(name,'from-imports',deps)
assert not list((r/'training/holistic_migration').rglob('*.pyc'))
for cmd in [['git','diff','--check'],['git','diff','--exit-code'],['git','diff','--cached','--exit-code']]:
 result=subprocess.run(cmd,cwd=r,capture_output=True,text=True)
 print(cmd,'exit',result.returncode,result.stdout,result.stderr); assert result.returncode==0
print('Scope: no Task B edits/imports in production data modules. Existing tests do not establish B approval; parent-reported B software fixes and human gate remain separate.')
`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/36-cache-cleanup-and-source-scope-check.log`.

```text
pytest cache birth 2026-11-13T04:48:51.807640
removed only pytest cache created during this Task C run
protected {'training/holistic_migration/__init__.py': True, 'training/holistic_migration/detector.py': True, 'training/holistic_migration/features.py': True, 'training/holistic_migration/tests/__init__.py': True, 'training/holistic_migration/tests/test_detector.py': True, 'training/holistic_migration/tests/test_features.py': True, 'training/holistic_migration/camera.py': True, 'training/holistic_migration/camera.swift': True, 'training/holistic_migration/webcam.py': True, 'training/holistic_migration/tests/test_camera.py': True, 'training/holistic_migration/tests/test_webcam.py': True} requirements {'docs/holistic-migration/CAPTURE_CANDIDATE.md': True, 'docs/holistic-migration/task-c-brief.md': True}
training/holistic_migration/sequence.py from-imports ['dataclasses', 'features']
training/holistic_migration/dataset.py from-imports ['collections', 'dataclasses', 'pathlib', 'features', 'sequence']
training/holistic_migration/extract.py from-imports ['pathlib', 'numbers', 'dataset', 'sequence', 'detector']
training/holistic_migration/build_dataset.py from-imports ['pathlib', 'dataset']
['git', 'diff', '--check'] exit 0  
['git', 'diff', '--exit-code'] exit 0  
['git', 'diff', '--cached', '--exit-code'] exit 0  
Scope: no Task B edits/imports in production data modules. Existing tests do not establish B approval; parent-reported B software fixes and human gate remain separate.
```

## 37-final-full-migration-suite

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/37-final-full-migration-suite.log`.

```text
training/holistic_migration/tests/test_webcam.py::PixelsAndOverlayTests::test_actual_bgra_conversion_resize_and_no_input_mirror PASSED [ 96%]
training/holistic_migration/tests/test_webcam.py::PixelsAndOverlayTests::test_missing_components_real_counts_masks_connections_and_readable_text PASSED [ 97%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_additional_failure_stages_keep_disposition_and_teardown 
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_additional_failure_stages_keep_disposition_and_teardown PASSED [ 97%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_default_runtime_binds_actual_shared_detector_and_packer_without_loading_sdk PASSED [ 98%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_errors_cleanup_fault_and_handshake_admission_before_detector 
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_errors_cleanup_fault_and_handshake_admission_before_detector PASSED [ 98%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_no_implicit_report_and_main_uses_same_runner PASSED [ 99%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_quit_escape_window_close_and_deadline_release_all 
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_quit_escape_window_close_and_deadline_release_all PASSED [100%]

================== 186 passed, 252 subtests passed in 41.81s ===================
```

## 38-final-original-training-suite

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/tests -v`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/38-final-original-training-suite.log`.

```text
    return np.array(x)

training/tests/test_export_frozen.py::FrozenExportTests::test_frozen_export_preserves_validation_predictions_and_hashes
  /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/lib/python3.11/site-packages/tensorflow/lite/python/interpreter.py:457: UserWarning:     Warning: tf.lite.Interpreter is deprecated and is scheduled for deletion in
      TF 2.20. Please use the LiteRT interpreter from the ai_edge_litert package.
      See the [migration guide](https://ai.google.dev/edge/litert/migration)
      for details.
      
    warnings.warn(_INTERPRETER_DELETION_WARNING)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
============= 51 passed, 3 warnings, 289 subtests passed in 9.03s ==============
```

## 39-final-artifact-and-protected-readback

`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -c from pathlib import Path
import json,hashlib,subprocess,collections,numpy as np
from training.holistic_migration.dataset import validate_campaign,sha256,read_raw,preflight
r=Path('/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration');d=r.parent/'holistic-migration-data';e=Path('/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844');s=e/'synthetic-smoke'
protected=json.loads((d/'evidence/task-c-preflight-e04637b40648410da2dfdfbc11cc1cc7/protected.json').read_text())
actual={name:sha256(r/name) for name in protected['protected_source_sha256']}
assert actual==protected['protected_source_sha256'] and len(actual)==11
for name,value in protected['requirements_sha256'].items(): assert sha256(r/name)==value
assert len(protected['new_owned_paths'])==10 and all((r/name).is_file() for name in protected['new_owned_paths'])
branch=subprocess.check_output(['git','branch','--show-current'],cwd=r,text=True).strip()
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()
assert branch=='holistic-migration' and head==protected['base']
assert not subprocess.check_output(['git','diff'],cwd=r)
assert not subprocess.check_output(['git','diff','--cached'],cwd=r)
subprocess.run(['git','diff','--check'],cwd=r,check=True)
assert not (r/'.pytest_cache').exists()
g,m,rows=validate_campaign(s/'campaign');assert len(rows)==150
bundle=json.loads((s/'bundle/data_manifest.json').read_text());assert bundle['evidence_kind']=='synthetic_in_process'
for name,rec in bundle['artifacts'].items(): assert sha256(s/'bundle'/name)==rec['sha256']
shapes={p:list(np.load(s/'bundle'/f'X_{p}.npy',allow_pickle=False).shape) for p in ['fit','validation','test']}
assert all(v==[50,30,153] for v in shapes.values())
diag=json.loads((s/'diagnostic/extraction_manifest.json').read_text());assert diag['status']=='diagnostic_fit_only' and diag['full_campaign_qualification'] is False
for row in [json.loads(x) for x in (s/'diagnostic/rows.jsonl').read_text().splitlines()]:
 if 'raw_file' in row: assert row['partition']=='fit';read_raw(s/'diagnostic'/row['raw_file'],row['raw_sha256'])
assert not (s/'diagnostic-never-bundle').exists()
real=preflight(partition_manifest=d/'candidate-partitions-v1.json',source_inventory=d/'verified-video-byte-inventory.json',decode_summary=d/'decoded-source-audit-v1/summary.json',raw_root=d/'clips_raw',classes=r/'training/preprocessing/selected_classes.json',model=d/'holistic_landmarker.task')
assert len(real.rows)==1016 and real.classes[25]['original_id']==49 and real.classes[25]['label']=='TODAY'
print(json.dumps(dict(protected_hashes_matched=len(actual),branch=branch,head=head,owned_paths=10,tracked_diff_bytes=0,staged_diff_bytes=0,synthetic_full=m['counts'],synthetic_diagnostic=diag['counts'],synthetic_bundle_shapes=shapes,real_metadata_sources=len(real.rows),real_metadata_partitions=dict(collections.Counter(row['partition'] for row in real.rows))),sort_keys=True))
`

Exit **0**; full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/39-final-artifact-and-protected-readback.log`.

```text
{"branch": "holistic-migration", "head": "4d901693642af5f572455b2c75ba095b0ec65c7f", "owned_paths": 10, "protected_hashes_matched": 11, "real_metadata_partitions": {"fit": 663, "test": 203, "validation": 150}, "real_metadata_sources": 1016, "staged_diff_bytes": 0, "synthetic_bundle_shapes": {"fit": [50, 30, 153], "test": [50, 30, 153], "validation": [50, 30, 153]}, "synthetic_diagnostic": {"declared": 150, "errors": 0, "processed": 50, "selected": 50}, "synthetic_full": {"declared": 150, "errors": 0, "processed": 150, "selected": 150}, "tracked_diff_bytes": 0}
```

## Final immutable-baseline handoff — Task C ready for independent review

### Outcomes and actual validation

- Implemented only the ten owned new repository paths from the brief. Four production modules, three synthetic test modules, README, installed direct-runtime pins and this append-only report. No accepted source was replaced. Production dependencies are accepted Task A features/detector only, never camera/webcam.
- Shared 15Hz actual-observation clock, plain RGB 640×360 INTER_AREA preparation and bounded capture policy return exact accepted resampling; malformed source values raise, coverage failures retain explicit fixed reasons and input/bounded denominators.
- Source graph validates all class/source/partition/decode companions, exact built-in integer schema values, identities, counts, duplicates, literal tokens, official-test isolation and protected paths/DATALESS flags. Raw NPZ is numeric-only, Float64 blocks with explicit presence and ragged full face values/offsets. None and present-empty faces remain distinct; no face truncation or silent value loss.
- Real extractor entry is implemented with full-stream OpenCV audit, actual presentation times, fresh accepted Tasks VIDEO tracker per clip, cleanup, source-byte checks, raw readback, append-only source ledger and exclusive completion publication. Default runtime path enforces frozen input/model identities before native loading. Only injected synthetic production flows were inferred here.
- Diagnostic selection is frozen-fit-only (one literal-first clip/class), recorded before runtime; synthetic diagnostic completed with declared150/selected50/processed50/errors0 and full-campaign qualification false. Validation/test videos were not opened by the diagnostic fixture. Real builder CLI refused that diagnostic with exit2.
- Complete synthetic campaign recorded declared150/selected150/processed150/errors0. The real bundle CLI produced Float32[50,30,153] for each partition, int64 labels, ordered Unicode IDs, all50 dense/original/literal classes and denominator reports; artifacts were reopened and all listed digests checked. Synthetic data is not FSL evidence and is not training-qualified.
- Real frozen metadata graph preflight passed:1016 sources (fit663/validation150/test203),50 classes, dense25 original49/TODAY and exact frozen hashes. To resolve the audit framing precisely, one already-frozen fit source clips/0/0.MOV was decoded with **zero inference**:245 frames and the existing digest matched little-endian int32 H/W/C framing. This was not a diagnostic extraction/fit run or capture-quality claim.

### Final test receipts

- Full migration: **186 passed; 252 subtests passed; exit0**, no warnings reported. Task C own cases: **125** ({'test_dataset.py': 71, 'test_extract.py': 18, 'test_sequence.py': 36}). Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/37-final-full-migration-suite.log`.
- Original training suite: **51 passed; 289 subtests passed; 3 warnings; exit0**. Existing Keras/NumPy and TensorFlow Lite deprecation warnings are preserved, not suppressed. Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/38-final-original-training-suite.log`. Existing synthetic test fixtures are not a source-data training/export campaign.
- `--help` for both CLIs exited0. Exact real-source extractor existing-target rejection exited2 before runtime; synthetic builder success exited0; diagnostic builder refusal exited2. Full command/exit receipts are entries31–35 above. Test subprocesses also exercised relative input, rebound malformed schema, unsupported fit/validation class, raw/ledger/tensor/readback tampering, duplicate and source/path contamination boundaries.
- Every actual RED/GREEN command and exit is preserved above and in external full verbose logs. The first support GREEN failed on tuple-versus-JSON-list readback; the corrected GREEN is retained separately. The initial stale-digest test changed archive identity instead of a stale companion, so its corrected RED is also preserved. No earlier output was overwritten or re-described as success.

### Exact interfaces and usable entry points

From `~/KumpasBuilds/holistic-migration`, interpreter `~/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B`, TMPDIR `~/.hermes/cache/scratch`:

```text
python -E -B -m training.holistic_migration.extract
  --partition-manifest ABSOLUTE_JSON --source-inventory ABSOLUTE_JSON
  --decode-summary ABSOLUTE_SUMMARY_JSON --raw-root ABSOLUTE_DIRECTORY
  --classes ABSOLUTE_JSON --model ABSOLUTE_TASK --output NEW_ABSOLUTE_EXTERNAL_DIRECTORY
  [--diagnostic-fit-only]
python -E -B -m training.holistic_migration.build_dataset
  --campaign ABSOLUTE_COMPLETED_FULL_CAMPAIGN --output NEW_ABSOLUTE_EXTERNAL_DIRECTORY
```

Full absolute exercised command lines are in the receipts, including the successful persistent synthetic builder CLI. README has the full parent-owned real diagnostic invocation (explicitly not claimed as run). Public helpers: `ObservationClock.admit(timestamp_ms)`, `prepare_image(rgb,cv)`, `prepare_capture(frames)->CaptureResult`, `preflight(**source_paths,output=None)->SourceGraph`, `write_raw(path,frames)->sha256`, `read_raw(path,sha256)->list[RawFrame]`, `run_extraction(...)->int`, `validate_campaign(campaign)->(graph,manifest,rows)`, `build_dataset(campaign=...,output=...)->dict`. Tests inject trusted in-process factories, not a CLI loader.

Persistent synthetic artifacts: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/synthetic-smoke` (`campaign/`, `diagnostic/`, `bundle/`, `smoke_receipt.json`). All remain explicitly synthetic. External evidence/handoff: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844`.

### Scope/integrity and remaining gates

- Final readback verified all **11** protected Task A/B SHA-256 values and both requirement hashes unchanged, all ten owned files present, branch holistic-migration, HEAD4d901693642af5f572455b2c75ba095b0ec65c7f, tracked and staged source diff empty; `git diff --check` exit0. Details: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-20261113T044844/39-final-artifact-and-protected-readback.log`. The pytest cache created by this worker was removed after checking its creation time; subsequent suites used `-p no:cacheprovider`, and no package pyc files were left.
- Parent reported two reproduced Task B source-terminal/partial-thread-cleanup defects. This worker neither repaired nor imported Task B in the data pipeline. Existing suite success does **not** establish Task B software approval. Separate B repair/review and the deferred human/physical gate remain open.
- Parent owns independent Task C review, the **real** fit-only diagnostic and the full real campaign. None was run here; all-class real eligibility, real-source tiny-overfit, recognition, linguistic/anatomical acceptance and live handedness/performance remain unestablished. Do not train from the synthetic bundle. Later training must use only fit/validation; test is for separate frozen-model evaluation.
- Detector-derived hand-observed bounds are not annotations. Trusted Python callbacks and a locally writable filesystem are not a sandbox; SHA checks are not signatures or hostile-writer race protection. The codec deliberately rejects values beyond exact Float64/int64 representation; pins describe direct installed runtime versions, not a transitive environment lock. Process interruption preserves actual partial attempt/ledger and cannot qualify or resume it by filename.
- No camera/GUI launch, bulk real inference, source-data fitting, optimization, installations, commits/pushes or model/provider configuration changes were performed. The original cloud checkout and Recognition V2 worktree were not modified.


## Task C fix1 recovery started — acceptance remains pending

B delivery prerequisite is satisfied per parent handoff; no implementer overlaps this bounded repair. Complete failing recovery review L-C01/MR-C01 and included test-only S-C01 have been read; prior statements of losslessness above are superseded by the reproduced integer-maxima defect, not treated as approval. Before any source/test edits, all 11 exact preimages (including this original report) matched `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-before-fix-570ad20c8af34710b1cba83dc83c55c2/snapshot-index.json`; all 20 newly supplied protected postimages matched `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-b-review-fixed-6229865bbcbc4de1a38bfdee1854c2fc/task-c-fix-protection.json`. Original report preimage SHA-256: b58d02dd4b6407d125238c2dbca261c4b83355285a8a00144e02483fee053f3f.

Fresh exclusive external repair evidence: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26`; preflight command/state retained in preflight.json. Scope is the five owned paths only, report append-only. Actual maxima RED is required before production changes; S-C01 gets its own honest RED/GREEN. Old source-bound receipts remain immutable. No real inference/fitting, camera/GUI, phone/app, installs, commits/pushes or provider changes authorized.

### fix1 01-maxima-RED

Command (cwd `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`, TMPDIR `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch`):

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_dataset.py -k raw_integer_maximum_rejected_before_open -v
```

Actual exit **1**. Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/01-maxima-RED.log`. Exact command, execution times and source bindings: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/01-maxima-RED.command.json`.

```text
        path = tmp_path/'must-not-publish.npz'
        opened = []
        real_open = Path.open
        def track_open(target, *args, **kwargs):
            if target == path:
                opened.append((args, kwargs))
            return real_open(target, *args, **kwargs)
        monkeypatch.setattr(Path, 'open', track_open)
>       with pytest.raises(ValueError, match='losslessly'):
E       Failed: DID NOT RAISE ValueError

training/holistic_migration/tests/test_dataset.py:78: Failed
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_dataset.py::test_raw_integer_maximum_rejected_before_open[signed]
FAILED training/holistic_migration/tests/test_dataset.py::test_raw_integer_maximum_rejected_before_open[unsigned]
======================= 2 failed, 71 deselected in 1.56s =======================
```

### fix1 02-maxima-GREEN

Command (cwd `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`, TMPDIR `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch`):

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_dataset.py -k raw_integer_maximum_rejected_before_open -v
```

Actual exit **0**. Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/02-maxima-GREEN.log`. Exact command, execution times and source bindings: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/02-maxima-GREEN.command.json`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 73 items / 71 deselected / 2 selected

training/holistic_migration/tests/test_dataset.py::test_raw_integer_maximum_rejected_before_open[signed] PASSED [ 50%]
training/holistic_migration/tests/test_dataset.py::test_raw_integer_maximum_rejected_before_open[unsigned] PASSED [100%]

======================= 2 passed, 71 deselected in 1.51s =======================
```

### fix1 03-retention-RED

Command (cwd `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`, TMPDIR `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch`):

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_dataset.py -k repeated_extract_helpers_keep_compact_closed_evidence -v
```

Actual exit **1**. Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/03-retention-RED.log`. Exact command, execution times and source bindings: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/03-retention-RED.command.json`.

```text
>           assert retained_bytes == [0, 0]
E           AssertionError: assert [5529600, 11059200] == [0, 0]
E             
E             At index 0 diff: 5529600 != 0
E             
E             Full diff: (-: missing in left side, +: extra in left side)
E               [
E             -     0,
E             -     0,...
E             
E             ...Full output truncated, use '-vv' to show

training/holistic_migration/tests/test_dataset.py:362: AssertionError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_dataset.py::test_repeated_extract_helpers_keep_compact_closed_evidence
====================== 1 failed, 142 deselected in 1.85s =======================
```

### fix1 04-retention-GREEN

Command (cwd `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`, TMPDIR `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch`):

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_dataset.py -k repeated_extract_helpers_keep_compact_closed_evidence -v
```

Actual exit **0**. Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/04-retention-GREEN.log`. Exact command, execution times and source bindings: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/04-retention-GREEN.command.json`.

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.2.0, pluggy-1.7.0 -- /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
rootdir: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
collecting ... collected 143 items / 142 deselected / 1 selected

training/holistic_migration/tests/test_dataset.py::test_repeated_extract_helpers_keep_compact_closed_evidence PASSED [100%]

====================== 1 passed, 142 deselected in 0.56s =======================
```

### fix1 05-parent-maxima-GREEN

Command (cwd `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`, TMPDIR `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch`):

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/parent-codec-fresh/parent_codec_red.py
```

Actual exit **0**. Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/05-parent-maxima-GREEN.log`. Exact command, execution times and source bindings: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/05-parent-maxima-GREEN.command.json`.

```text
test_signed_maximum_rejected_before_publication (__main__.ExactIntegerCodecTests.test_signed_maximum_rejected_before_publication) ... ok
test_unsigned_maximum_rejected_before_publication (__main__.ExactIntegerCodecTests.test_unsigned_maximum_rejected_before_publication) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.002s

OK
PARENT_CODEC_RECEIPT /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/parent-codec-fresh/parent_codec_red.result.json
```

### fix1 06-codec-controls-coverage-GREEN

Command (cwd `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`, TMPDIR `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch`):

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_dataset.py -k 'raw_ or codec_' -v
```

Actual exit **0**. Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/06-codec-controls-coverage-GREEN.log`. Exact command, execution times and source bindings: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/06-codec-controls-coverage-GREEN.command.json`.

```text
training/holistic_migration/tests/test_dataset.py::test_raw_exact_float_width_controls[float16] PASSED [ 85%]
training/holistic_migration/tests/test_dataset.py::test_raw_exact_float_width_controls[float32] PASSED [ 86%]
training/holistic_migration/tests/test_dataset.py::test_raw_exact_float_width_controls[float64] PASSED [ 87%]
training/holistic_migration/tests/test_dataset.py::test_raw_exact_float_width_controls[longdouble] PASSED [ 89%]
training/holistic_migration/tests/test_dataset.py::test_raw_rejection_preserves_existing_target PASSED [ 90%]
training/holistic_migration/tests/test_dataset.py::test_raw_writer_rejects_masked_and_nonmonotonic PASSED [ 91%]
training/holistic_migration/tests/test_dataset.py::test_public_preflight_path_and_byte_boundaries[raw_symlink-symlink] PASSED [ 92%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[raw_byte] PASSED [ 93%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[raw_traversal] PASSED [ 94%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[raw_symlink] PASSED [ 95%]
training/holistic_migration/tests/test_dataset.py::test_bundle_rejects_incomplete_tampered_campaign_public_path[raw_digest] PASSED [ 96%]
training/holistic_migration/tests/test_dataset.py::test_codec_rejects_loss_or_unsafe_read[unrepresentable_face] PASSED [ 97%]
training/holistic_migration/tests/test_dataset.py::test_codec_rejects_loss_or_unsafe_read[timestamp_range] PASSED [ 98%]
training/holistic_migration/tests/test_dataset.py::test_codec_rejects_loss_or_unsafe_read[symlink_read] PASSED [100%]

====================== 91 passed, 52 deselected in 5.10s =======================
```

### fix1 07-affected-suite

Command (cwd `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`, TMPDIR `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch`):

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_dataset.py training/holistic_migration/tests/test_extract.py training/holistic_migration/tests/test_sequence.py -v --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/07-affected.xml
```

Actual exit **0**. Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/07-affected-suite.log`. Exact command, execution times and source bindings: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/07-affected-suite.command.json`.

```text
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[bool_timestamp] PASSED [ 93%]
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[float_timestamp] PASSED [ 94%]
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[duplicate] PASSED [ 94%]
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[nonfinite] PASSED [ 95%]
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[shape] PASSED [ 95%]
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[masked] PASSED [ 96%]
training/holistic_migration/tests/test_sequence.py::test_capture_validates_all_even_trimmed_rows[matrix] PASSED [ 96%]
training/holistic_migration/tests/test_sequence.py::test_plain_rgb_resize_uses_area_and_preserves_rgb PASSED [ 97%]
training/holistic_migration/tests/test_sequence.py::test_image_rejects_semantic_or_invalid_arrays[image0] PASSED [ 97%]
training/holistic_migration/tests/test_sequence.py::test_image_rejects_semantic_or_invalid_arrays[image1] PASSED [ 98%]
training/holistic_migration/tests/test_sequence.py::test_image_rejects_semantic_or_invalid_arrays[image2] PASSED [ 98%]
training/holistic_migration/tests/test_sequence.py::test_image_rejects_semantic_or_invalid_arrays[image3] PASSED [ 99%]
training/holistic_migration/tests/test_sequence.py::test_capture_reports_source_denominator_even_when_no_bounded_interval PASSED [100%]

- generated xml file: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/07-affected.xml -
============================= 197 passed in 39.21s =============================
```

### fix1 09-original-suite

Command (cwd `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`, TMPDIR `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch`):

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/tests -v --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/09-original.xml
```

Actual exit **0**. Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/09-original-suite.log`. Exact command, execution times and source bindings: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/09-original-suite.command.json`.

```text
training/tests/test_export_frozen.py::FrozenExportTests::test_frozen_export_preserves_validation_predictions_and_hashes
training/tests/test_export_frozen.py::FrozenExportTests::test_frozen_export_preserves_validation_predictions_and_hashes
  /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/lib/python3.11/site-packages/keras/src/backend/tensorflow/core.py:172: DeprecationWarning: __array__ implementation doesn't accept a copy keyword, so passing copy=False failed. __array__ must implement 'dtype' and 'copy' keyword arguments.
    return np.array(x)

training/tests/test_export_frozen.py::FrozenExportTests::test_frozen_export_preserves_validation_predictions_and_hashes
  /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/lib/python3.11/site-packages/tensorflow/lite/python/interpreter.py:457: UserWarning:     Warning: tf.lite.Interpreter is deprecated and is scheduled for deletion in
      TF 2.20. Please use the LiteRT interpreter from the ai_edge_litert package.
      See the [migration guide](https://ai.google.dev/edge/litert/migration)
      for details.
      
    warnings.warn(_INTERPRETER_DELETION_WARNING)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
- generated xml file: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/09-original.xml -
============= 51 passed, 3 warnings, 289 subtests passed in 8.90s ==============
```

### fix1 08-full-migration-suite

Command (cwd `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`, TMPDIR `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch`):

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests -v --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/08-migration.xml
```

Actual exit **0**. Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/08-full-migration-suite.log`. Exact command, execution times and source bindings: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/08-full-migration-suite.command.json`.

```text
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_default_runtime_binds_actual_shared_detector_and_packer_without_loading_sdk PASSED [ 96%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_errors_cleanup_fault_and_handshake_admission_before_detector 
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_errors_cleanup_fault_and_handshake_admission_before_detector PASSED [ 96%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_no_implicit_report_and_main_uses_same_runner PASSED [ 97%]
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_quit_escape_window_close_and_deadline_release_all 
training/holistic_migration/tests/test_webcam.py::PreviewLoopTests::test_quit_escape_window_close_and_deadline_release_all PASSED [ 97%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_healthy_deadline_deliberately_terminates_owned_child PASSED [ 97%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_healthy_quit_deliberately_terminates_owned_child PASSED [ 98%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_deadline PASSED [ 98%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_escape PASSED [ 98%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_quit PASSED [ 99%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_observed_source_failure_then_window_close PASSED [ 99%]
training/holistic_migration/tests/test_webcam.py::SourceReconciliationTests::test_unexpected_child_exit_before_reader_publishes_error PASSED [100%]

- generated xml file: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/08-migration.xml -
================== 271 passed, 252 subtests passed in 41.59s ===================
```

### fix1 10-synthetic-producer

Command (cwd `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`, TMPDIR `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch`):

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/generate_synthetic.py
```

Actual exit **0**. Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/10-synthetic-producer.log`. Exact command, execution times and source bindings: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/10-synthetic-producer.command.json`.

```text
136/150 clips/71/0.MOV eligible
137/150 clips/71/1.MOV not_selected
138/150 clips/71/2.MOV not_selected
139/150 clips/72/0.MOV eligible
140/150 clips/72/1.MOV not_selected
141/150 clips/72/2.MOV not_selected
142/150 clips/73/0.MOV eligible
143/150 clips/73/1.MOV not_selected
144/150 clips/73/2.MOV not_selected
145/150 clips/8/0.MOV eligible
146/150 clips/8/1.MOV not_selected
147/150 clips/8/2.MOV not_selected
148/150 clips/9/0.MOV eligible
149/150 clips/9/1.MOV not_selected
150/150 clips/9/2.MOV not_selected
{"campaign": {"counts": {"declared": 150, "errors": 0, "processed": 150, "selected": 150}, "exact_raw_observations": 1200, "manifest_sha256": "04bbe5f2b1ce64de11e3e3e661bd7714802430dd9b538221602f39c56eb0b151"}, "diagnostic": {"counts": {"declared": 150, "errors": 0, "processed": 50, "selected": 50}, "exact_raw_observations": 400, "manifest_sha256": "5040abd868b62e0772d8cba62e8ba9777cf989486a85b464e14b9a40f432cd92"}}
```

### fix1 11-synthetic-builder-CLI

Command (cwd `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`, TMPDIR `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch`):

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m training.holistic_migration.build_dataset --campaign /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/synthetic-corrected/campaign --output /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/synthetic-corrected/bundle
```

Actual exit **0**. Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/11-synthetic-builder-CLI.log`. Exact command, execution times and source bindings: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/11-synthetic-builder-CLI.command.json`.

```text
completed /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/synthetic-corrected/bundle/data_manifest.json; {'fit': {'declared': 50, 'eligible': 50, 'ineligible': 0, 'reasons': {}}, 'validation': {'declared': 50, 'eligible': 50, 'ineligible': 0, 'reasons': {}}, 'test': {'declared': 50, 'eligible': 50, 'ineligible': 0, 'reasons': {}}}
```

### fix1 12-diagnostic-builder-refusal

Command (cwd `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`, TMPDIR `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch`):

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m training.holistic_migration.build_dataset --campaign /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/synthetic-corrected/diagnostic --output /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/synthetic-corrected/diagnostic-must-not-bundle
```

Actual exit **2**. Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/12-diagnostic-builder-refusal.log`. Exact command, execution times and source bindings: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/12-diagnostic-builder-refusal.command.json`.

```text
dataset rejected: only a complete full campaign is a dataset; diagnostic refused
```

### fix1 13-final-readback

Command (cwd `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`, TMPDIR `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch`):

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/verify_readback.py
```

Actual exit **0**. Full log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/13-final-readback.log`. Exact command, execution times and source bindings: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/13-final-readback.command.json`.

```text
    "artifact_digests_checked": 13,
    "contract_sha256": "944e7b7acb495899bd78a937d3a453e2e188812c9a747ce05b9667537ccb15bc",
    "full_manifest_sha256": "04bbe5f2b1ce64de11e3e3e661bd7714802430dd9b538221602f39c56eb0b151",
    "bundle_manifest_sha256": "b4ae36b830732c09bd9777fb68dede78c27b9f705dc8410b7bcfca409ef8054b",
    "diagnostic_manifest_sha256": "5040abd868b62e0772d8cba62e8ba9777cf989486a85b464e14b9a40f432cd92",
    "diagnostic_builder_exit": 2,
    "refused_output_absent": true,
    "historical_campaign_refusal": "campaign input/current contract/runtime mismatch"
  },
  "float_widths": {
    "float16": 10,
    "float32": 23,
    "float64": 52,
    "longdouble": 52
  }
}
```

## Task C fix1 delivered candidate — independent affected-scope re-review pending

### Repair and honest test-first evidence

- **L-C01/MR-C01:** Before production edits, `01-maxima-RED` exercised actual public NPZ writes: signed/unsigned maximum cases both failed because ValueError was not raised (2 failures, exit1). `02-maxima-GREEN` passed the same 2 tests after the narrow repair. `write_raw` now checks finite Float64 conversion then compares each integer using unbounded Python int/int semantics. It does not rely on saturating integer cast-back, mixed NumPy float/integer equality, an integer ban or a 2**53 ceiling. Every other dataset AST node and the public writer arguments remain unchanged.
- Added coverage-only GREEN controls for all four raw components: signed minimum, large exactly representable signed/unsigned powers/multiples, ordinary integer widths, neighboring nonrepresentable integers, late-invalid frames before output opening and existing-target preservation. Exact scalar ratios verify integer raw values; Float64 hexadecimal scalar checks preserve float values/signs. Original None/present-empty/478/variable-face and corruption/timestamp/semantic-array cases remain unchanged. Normalized equality is retained but never substitutes for raw equality. Runtime longdouble has the same 52 fraction bits as Float64; the longdouble control is not a wider-precision claim.
- **S-C01, bounded test-only:** `03-retention-RED` reached two actual `extract_one` helper calls from the dataset test module, with all detectors closed/videos released and cadence checked, before failing on reachable RGB ndarray bytes `[5529600, 11059200]`. After compact full-image SHA-256/shape/dtype/contiguity/timestamp evidence replaced copies, `04-retention-GREEN` passed with `[0,0]`. Local extraction registry reset now also tears down after assertions. All previous dataset test functions are AST-identical; extraction geometry/channel/cadence checks were strengthened to compare independently expected full-image digests for every admitted frame in all 150 clips. No new top-level fixture import cycle, conftest or production test machinery was introduced.
- Parent's original two-case script was copied byte-for-byte to a fresh exclusive `parent-codec-fresh/` directory and passed **2 tests, 0 failures/errors, exit0**. Its new result binds current dataset.py; both maxima are rejected and no output is published. Historical RED source/results/logs remain untouched.

### Actual final suites (counts kept distinct)

| Scope | Cases passed | Subtests passed | Warnings | Exit |
| --- | ---: | ---: | ---: | ---: |
| affected dataset/extract/sequence | 197 | 0 | 0 | 0 |
| complete migration, including delivered B | 271 | 252 | 0 | 0 |
| original training | 51 | 289 | 3 | 0 |

All three suites had zero failures/errors/skips. XML readback matched 197/271/51 testcase elements and 197/523/340 suite-test totals respectively. Original warnings are the two existing Keras/NumPy copy-keyword deprecations and TensorFlow Lite interpreter deprecation; none was suppressed. Existing training tests use isolated synthetic fixtures, not real-source fitting or model promotion. Complete exact commands, runtime flags, source bindings, exits, logs and XML are retained in `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26`; `readback.json` contains parsed results. All invocations used the existing interpreter with `-E -B`, approved scratch TMPDIR and pytest `-p no:cacheprovider`.

### Fresh explicitly synthetic producer/bundle/diagnostic

Fresh exclusive root: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/synthetic-corrected`. Production extraction used only trusted in-process synthetic callbacks and stub model/source bytes, never the SDK or real FSL videos. Full campaign: declared150/selected150/processed150/errors0. Diagnostic: declared150/selected50/processed50/errors0, fit-only selection, qualification false. Exact readback verified **1600 raw observations**, including Float64/None/empty/478/variable faces, signed minimum and large exactly representable unsigned face values. Complete CLI bundle: three Float32[50,30,153] partitions, ordered IDs/int64 labels, **150 exact shared-capture tensors**, **13 artifact digests** verified. Evidence remains `synthetic_in_process`, `training_qualified=false`; no research/training qualification follows.

Builder CLI success exited0; diagnostic builder refusal exited2 with its requested output absent. Corrected contract SHA-256: `944e7b7acb495899bd78a937d3a453e2e188812c9a747ce05b9667537ccb15bc`. Fresh manifests:
- campaign: `04bbe5f2b1ce64de11e3e3e661bd7714802430dd9b538221602f39c56eb0b151`
- bundle: `b4ae36b830732c09bd9777fb68dede78c27b9f705dc8410b7bcfca409ef8054b`
- diagnostic: `5040abd868b62e0772d8cba62e8ba9777cf989486a85b464e14b9a40f432cd92`

Old source-bound synthetic manifests retain their exact historical hashes. The old campaign now honestly rejects as `campaign input/current contract/runtime mismatch`; no source hash was retrofitted to make it current.

### Changed files, preservation and remaining boundaries

Only these four repository source/test/document paths and this append-only report changed:

| Path | Final SHA-256 |
| --- | --- |
| `training/holistic_migration/README.md` | `6750c2ed933dd76cc5b05129758063e46931844ad16b31fb06cbefd398ac1c46` |
| `training/holistic_migration/dataset.py` | `741a3f8c12d6fe3fd80f56f930c066237662b9fde58075bbb46facb4adfd3809` |
| `training/holistic_migration/tests/test_dataset.py` | `b72df50ad53f86261decaf92e3340e7366e26f1261c65fe6bfecee0a20505099` |
| `training/holistic_migration/tests/test_extract.py` | `729f38aecad2d53d4875508b1443fb6f89bea4f92e6dc33de007eb02eea55fd3` |

The final report postimage/hash is frozen externally in `handoff.json` after this append (no impossible self-hash in the report). `repair-source.diff` covers the four source/test/document changes; `repair-report.append.md` preserves the exact appended ledger; `postimages/` holds the five delivered bytes. Finalization command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-c-fix1-00ffe6b02d21421f86d86ba5fc208a26/finalize_handoff.py`.

All **20** supplied protected postimages matched, all **11** immutable before-fix snapshots matched, original report bytes remain an exact prefix, original metadata/model/class-map and historical review/producer/parent receipts retain their bound hashes. Original tracked and staged diffs remain empty, `git diff --check` passes, HEAD/branch are unchanged, and no migration pyc/cache files were left. Unchanged sequence.py/test_sequence.py/features.py and producer/builder bytes map exactly through the protection receipt; only raw writer body behavior changed, not their public interfaces. Parent may carry sequence review findings forward only by that explicit mapping, not a new approval claim.

Remaining: parent packaging, independent complete affected data-group re-review and source-hash matching, then parent adjudication. This worker grants no C acceptance or real-source qualification. Dataset-helper registries can retain compact metadata until reset; full RGB ndarray retention is eliminated, not a measured RSS/native-memory/OOM claim. Actual SDK Float64/FSL corruption was never claimed. Real fit-only/full extraction, all-class real support, tiny-overfit, training/evaluation, human webcam/anatomical/linguistic/signer-independent/live and physical gates remain unestablished or deferred. No real inference/fitting, camera/GUI, phone/app, installs, commits/pushes, original-input edits or provider changes were performed. Trusted callbacks/filesystem integrity hashes are not a sandbox/signatures/hostile-writer race protection.
