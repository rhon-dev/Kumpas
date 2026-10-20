# Model/QA host audit — tasks 6, 8, 9, 10

Date: 2026-10-15. Scope: read-only offline evaluation planning; only this report written. No tests, training, conversion, builds, installations, device/emulator commands, model predictions, asset replacements, or historical-result changes performed. Read AGENTS.md, full docs/PRD.md, docs/phase-gates.md and the kumpas-study-readiness skill. The current explicit no-device/no-build instruction overrides the PRD's general emulator fallback. Existing unrelated dirty worktree files were left alone.

## Outcome and acceptance boundary

| Task | Existing | Missing / smallest next deliverable |
|---|---|---|
| 6: expanded FIVE/THREE parity | Hashed PNG preparation, Python Holistic reference, strict vector dimensions, Android production-engine replay, one historical THREE fixture | Six validation-clip fixture manifests/references and synthetic malformed-input coverage; new Android outputs cannot be produced host-only. Anatomy remains unverified. |
| 8: model error investigation | Frozen selection, aggregate per-class Keras report, historical confusion/prediction files, detection metadata, existing validation/test arrays | Immutable clip-level validation predictions and error table separating detector, normalization, temporal, classifier and export hypotheses; no confirmed anatomical cause. |
| 9: bounded experiments | Original-clip-grouped fit/validation protocol and validation-only selector; two prior candidates | Approval, predeclared budget, isolated outputs/logs, stronger input provenance. Default training command currently modifies an existing protected log. No retraining authorized by this audit. |
| 10: evaluation/export provenance | Candidate checkpoint/selection/manifest/label-map/artifact hashes; exporter never deploys | Bind derived arrays and label semantics to freeze; clip-level output records; explicit conversion acceptance policy; exact historical checkpoint-to-app export chain remains absent. |

Neither existing nor planned host evidence closes ≥90% final-test, signer independence, anatomical correctness, device runtime/performance, expert validation or participant-study gates.

## Exact local inputs and verified identities

All relative paths below resolve from `/Users/ahronjanl.rafaelahron.0804icloudcom/Documents/Thesis/kumpas`.

- Public dataset root: `../FSL-105 A dataset for recognizing 105 Filipino sign language videos/`, containing `labels.csv`, `train.csv`, `test.csv`, `clips.zip`.
- Already extracted raw clips: `../kumpas-data/clips_raw/clips/22/{0..19}.MOV` (THREE) and `../kumpas-data/clips_raw/clips/24/{0..19}.MOV` (FIVE). No extraction or copies needed. The ZIP does not use the landmark `clips_22_*.npz` naming convention; resolve paths through CSV `vid_path`, not guessed NPZ-style archive names.
- Landmarks: `../kumpas-data/landmarks/clips_<source-class>_<clip>.npz`. Inspected six target validation NPZs: each has `landmarks` float32 `(244,1662)`, scalar `class_id`, `split`, `fps`, `brightness`, and four `detection_rates`. These provide detector observations, not independent anatomical labels.
- `../kumpas-data/sequences/{X_train,y_train,X_test,y_test}.npy`, `clips_train.json`, `clips_test.json`, `label_map.json`; historical augmented arrays also exist but must not be substituted for protocol fit data.
- `../kumpas-data/sequences/evaluation-v1/{manifest.json,augmentations.json,X_fit.npy,y_fit.npy,X_val.npy,y_val.npy}`. Observed shapes: original train `(813,30,1662)`, test `(203,30,1662)`, fit `(2652,30,1662)`, validation `(150,30,1662)`. Manifest has 663 fit originals, 150 validation originals; each class has three validation clips.
- Dense labels: THREE=`22`, FIVE=`24` (both also source IDs for these specific classes). Do not assume source and dense IDs coincide for every class. `sequences/label_map.json`, `tflite/label_map.json`, and `app/android/app/src/main/assets/label_map.json` have identical bytes, SHA-256 `4fff4f4bf4df480d257a04f4d125fca5fc2c3c1f3c86970857fb815f239fffb0`.
- Frozen selection: `training/models/protocol_selection_evaluation_v1.json`; selected checkpoint `../kumpas-data/models/20260930_153819_protocol_v1_no_face_baseline.keras`. Read-only `verified_selection(...)` actually succeeded, validating current source hashes, reconstructed manifest and checkpoint. Checkpoint SHA-256 `55ba7bb86dab621ea85112073e805818b7f5f417ed6dd9e116db92fe8d61288d`; manifest `77cc0cdd49cd9bb29a3c6172ff96eb30050c8fae9fadba02459dd22eeecbef99`; selection `512f9eb32321d1b24b9d40cb5b5cafff8fda99281c9868832a0029a51922be1c`.
- Candidate: `../kumpas-data/tflite/evaluation-v1-candidate/kumpas_50sign_20260930_153819_protocol_v1_no_face_baseline_builtins_dynamic.tflite`, adjacent `provenance.json`. Actual binary hash matched recorded `9d8a8035fc0085ca4bd95f3d3fdc9d2f3a9e6439b89789c64305f908536b0468`; selection hash also matched candidate provenance.
- App source asset `app/android/app/src/main/assets/kumpas_50sign.tflite` currently hashes to `1f4543b8fb159dbe9a662f0b37e64b096f717d7527c45b2d7778f34bc0885aeb`, different from candidate. No installed APK/device checked in this audit.
- Other checkpoint inputs: historical four July models and `../kumpas-data/models/20260930_154059_protocol_v1_no_face_wider.keras`. Prior protocol log selects baseline over wider by macro-F1 after both obtained validation accuracy 0.96. Preserve both.

## Task 6 — parity fixtures

Implementation: `benchmarking/pipeline_parity.py`; unit coverage `benchmarking/test_pipeline_parity.py`; Android producer `app/android/app/src/androidTest/kotlin/com/kumpas/kumpas_app/benchmark/PipelineParityTest.kt`.

Current external evidence: `../kumpas-data/parity/clips_22_10/manifest.json` and full PNG sequence; sampled `clips_22_10_30/manifest.json`; `clips_22_10_30_python.json`; `clips_22_10_30_android_emulator{,_full}.json`; corresponding `*_emulator{,_full}_report.json`. Clip 22/10 is **fit**, not validation. Existing report matches 30 frames, records one left-hand presence disagreement and labels anatomy unverified. It is historical emulator evidence, not current-source Android execution.

Use all existing validation originals for the two requested signs, declared before predictions:

| Dense label | Validation landmark filenames | Exact raw paths under `../kumpas-data/clips_raw/clips/` |
|---|---|---|
| THREE 22 | `clips_22_14.npz`, `clips_22_8.npz`, `clips_22_9.npz` | `22/14.MOV`, `22/8.MOV`, `22/9.MOV` |
| FIVE 24 | `clips_24_10.npz`, `clips_24_11.npz`, `clips_24_18.npz` | `24/10.MOV`, `24/11.MOV`, `24/18.MOV` |

Proposed output root after authorization: `../kumpas-data/parity/20261015-validation-v1/`, one new directory per source clip. Keep PNGs and landmark vectors external; repository gets only safe aggregate evidence/hashes. Preserve manifest frame hashes/source indices/video hash, selected source partition, class map hash, extractor/package versions, normalization source hash and sampling mode.

Example future host preparation (NOT executed):

```sh
PYTHONDONTWRITEBYTECODE=1 training/.venv/bin/python benchmarking/pipeline_parity.py prepare ../kumpas-data/clips_raw/clips/22/14.MOV ../kumpas-data/parity/20261015-validation-v1/three-14-30 --max-frames 30
PYTHONDONTWRITEBYTECODE=1 training/.venv/bin/python benchmarking/pipeline_parity.py reference ../kumpas-data/parity/20261015-validation-v1/three-14-30 ../kumpas-data/parity/20261015-validation-v1/three-14-python.json
```

The generator's 30-frame uniform sampling changes Holistic VIDEO tracking relative to full-video extraction. Distinguish (a) full-video landmarks normalized/resampled by existing training code from (b) detecting only 30 sampled PNGs. Compare both host paths without declaring differences a production normalization defect. Android replay currently asserts exactly 30 frames and uses synthetic increasing millisecond timestamps, so full-video replay needs an explicitly separate design later. No new Android parity pass can be claimed without an Android runtime.

Small fixture-hardening design: test duplicates, nonfinite vectors, invalid presence flags, empty/missing digests, malformed digest strings, bool-as-index/feature, reordered frames, absent/wrong schema, source/frame identity mismatch. Existing comparator allows equal missing `sha256` values, accepts Python booleans as integers/numbers, and does not validate schema/digest format or declared clip identity. Existing tests cover image-hash mismatch, missing frames, wrong dimension, endpoint sampling and actual PNG byte hashes. Add fail-closed validation without altering normalization/math. `compare_vectors` only checks top-level `prediction`; Android emits `attempt_result`, so prediction comparison needs a deliberate adapter rather than assuming current output contains agreement.

## Task 8 — error investigation

Source reports: `training/models/reports/20260930_protocol_v1_no_face/{evaluation.json,evaluation.md,provenance.md}`. Historical July predictions/confusion outputs are in `training/models/reports/20260705_*`; they are not September frozen predictions.

Recorded, not rerun: selected Keras 181/203; candidate TFLite 177/203 on reused exploratory test. FIVE Keras 2/4 with one THREE and one FOUR error; THREE 1/4. Validation FIVE 3/3, THREE 2/3; only three clips per target class, so neither broad robustness nor a reliable subgroup accuracy estimate follows. Existing exporter provenance reports 0/150 validation top-1 disagreements but maximum absolute probability difference 0.18056738376617432. Top-1 agreement is not probability equivalence and can matter to confidence-dependent behavior.

Minimal new **validation-only**, read-only-input analysis entry point should:

1. Validate selection/manifest/checkpoint/label map; load validation in manifest order, compare it exactly to source originals (reuse `load_protocol_data` validation checks or factor them into a standalone reader).
2. Emit immutable clip-level records: partition, source ID, dense label, Keras and candidate top-k/probabilities/margins, disagreement, detector presence rates, sequence length and source/frame/array/model hashes. Include aggregate confusion across all 50 classes, not only chosen failures.
3. Relate target errors to missing hands, normalization/scale, temporal subsampling and conversion probability drift. Label each a hypothesis until controlled evidence separates it; no mirrored-hand/anatomy conclusion from self-reported detector handedness.
4. Keep already-observed test errors in a separate historical diagnostic appendix. Do not recompute test to rank experiments or tune thresholds. A new untouched, preferably signer-identified assessment is still required.

Missing: verified signer identities, expert anatomy/left-right labels, completed expert rubric, unseen final split, current clip-level frozen prediction artifact. `evaluation/` currently only contains `.gitkeep`, not an analysis pipeline. Avoid `benchmarking/accuracy_benchmark.py` CLI: it reads historical test and appends to benchmark history, and defaults to historical builtins rather than the frozen candidate.

## Task 9 — bounded experiment decision, not permission

First authorize only non-training validation diagnostics and provenance hardening. Thereafter, if PM/adviser explicitly approves local training deviation and limited retraining, predeclare at most two new sequential variants against the unchanged frozen baseline: same CNN-LSTM/no-face shape, same existing grouped split and seed; one regularization change (e.g. dropout 0.5), one learning-rate change (e.g. 0.0005). Change one factor per variant, maximum 60 epochs each, batch 32, existing early-stop patience 15, and hard 15-minute wall-clock limit per run. These limits are proposed policy, not existing enforcement or promised runtime. No test peeking, post-hoc sweeps, new split searching, automatic promotion or new architecture.

Rank by the already declared validation accuracy, macro-F1, then run-ID rule. Report numerator/denominator and all 50 classes; do not make acceptance solely FIVE/THREE accuracy. Reused validation itself limits confidence after repeated tuning. If no predeclared improvement, stop; do not add variants automatically.

`training/models/train_cnn_lstm.py` has explicit `--protocol-dir`, `--drop-face`, `--epochs`, `--batch`, `--dropout`, `--lr`, but **hardcodes** `PROTOCOL_LOG` to existing `training/models/protocol_experiments_log.json`, checkpoint output root and seed. Therefore do not run its default CLI under the current preservation rule. Small implementable change in a separately authorized code task: explicit new output/log/seed and wall-clock budget options, exclusive-create run directories, atomic append-only campaign records, hyperparameter/environment/source hashes and finite metric validation. A separate campaign runner can instead call existing model/data functions and keep all new artifacts outside protected historical paths. Record exact runner command only once implemented and verified; do not invent unsupported flags.

## Task 10 — protections and gaps

Existing actual code protections:

- `training/models/evaluation_protocol.py`: original clip split before augmentation; rejects duplicate/overlapping train/test clip names, source digest changes, inconsistent manifest rows/counts; deterministic reconstructed manifest; new protocol directory required.
- `load_protocol_data` in `train_cnn_lstm.py`: validation arrays must exactly equal original selected rows and labels; feature/length checks; no test array loading (manifest validation still reads test clip-name list).
- `freeze_selection.py`: matches protocol and checkpoint hashes, ranks validation only, refuses existing selection path, preserves exploratory reused-test notice.
- `evaluate_frozen.py`: requires freeze, validates checkpoint/manifest/test clip list and dimensions, emits source-array hashes and explicit reused-test/signer uncertainty; new report directory required.
- `export_frozen.py`: verifies checkpoint/manifest/label-map agreement, 30x258 shape and class count, builtins-only conversion, validates interpreter shape, records validation comparisons and TF version, writes new candidate directory with `deployed:false`.

Important gaps for minimal provenance design:

- Protocol hashes bind original training arrays and clip lists, **not** derived fit/validation arrays, augmentation log, label map or test arrays. Training compares validation against source but does not reconstruct/verify fit augmentations. Export reads validation directly without the training loader's exact-original equality check. Tampered shape-compatible validation can therefore supply misleading conversion evidence.
- Evaluator records test array hashes only after loading; it does not compare them to a preregistered expected digest. Test labels/class map are not bound to selection; semantic class mapping, label ranges, finite probabilities and output-class dimension need explicit checks.
- Freeze trusts metric fields without robust finite/range/type checking or recomputing evidence; no cryptographic signature is implied. Existing exclusive-path checks are not complete concurrent atomic publication protections.
- Export records disagreement/max error but imposes no numerical acceptance threshold. Separate successful export from acceptance; require a predeclared top-1/probability/calibration policy before promotion.
- Evaluator does not save per-clip predictions/confusion or full runtime/source lineage. Export lacks full source/runtime/derived-array lineage. Add versioned immutable campaign manifest binding all arrays, labels, ordered clip IDs, preprocessing/augmentation source, checkpoint, selection, converter flags, runtime dependencies, outputs and status. Never retrofit historical records as though hashes were preregistered then.
- Exact historical checkpoint-to-current-app-byte chain remains unproved; matching predictions or filename conventions are not a substitute. Keep current app asset untouched.

Read tests: `training/tests/test_evaluation_protocol.py`, `test_training_protocol.py`, `test_evaluate_frozen.py`, `test_export_frozen.py`. Existing cases cover original grouping/fit augmentation, duplicates/overlap/digest mismatch, explicit validation loading, validation-not-test ranking, missing/conflicting freezes, exploratory wording, changed checkpoint/protocol rejection and synthetic TF export consistency. New regression cases should target each gap above before any production changes. No current test pass is claimed; suites were inspected, not executed.

Future test commands after separate permission to create isolated temporary fixtures:

```sh
PYTHONDONTWRITEBYTECODE=1 "$HOME/.kumpas-venvs/tf/bin/python" -m unittest discover -s training/tests -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 training/.venv/bin/python -m unittest discover -s benchmarking -p 'test_pipeline_parity.py' -v
```

The training suite includes actual synthetic TensorFlow model save/conversion, so it is not a pure metadata read. Use the session scratch TMPDIR and retain real exits/skips; no default stores. Existing evaluator/exporter CLIs have explicit `--freeze`, `--protocol-dir`, and new report/output destination flags, but are **not recommended to execute now**: evaluator opens reused test, exporter converts an artifact, both write outputs.

## Host resources and unresolved decisions

Actual discovery: 8 logical CPUs, 8,589,934,592 bytes physical RAM, filesystem reports 29 GiB available. `X_fit.npy` is 528,915,008 bytes before slicing and TensorFlow allocations. Run one compute process at a time; avoid decoding several videos simultaneously (current `prepare_video` holds all decoded BGR frames in memory even with `--max-frames 30`). Avoid broad ZIP extraction and installations.

Two existing environments are complementary:

- `$HOME/.kumpas-venvs/tf/bin/python`: executable Python 3.11.15; package metadata TensorFlow 2.19.0, Keras 3.15.1, NumPy 2.1.3, scikit-learn 1.9.1; no MediaPipe or OpenCV package. Successfully ran NumPy metadata and read-only provenance validation here. TensorFlow import/model load not exercised.
- `training/.venv/bin/python`: package metadata NumPy 2.4.6, MediaPipe 0.10.14, opencv-python 5.0.0.93; TensorFlow/scikit-learn absent. Metadata availability does not prove MediaPipe/OpenCV import compatibility. Run a bounded import probe before authorizing extraction, not an install. Historical trainer comment says Keras 3.10; current installed metadata differs, so record environment drift rather than promise byte-identical reproduction.

Decisions needed: approve six-clip external fixture generation and validation-only inference; define numerical conversion tolerances; authorize isolated tool hardening; decide if bounded retraining is allowed and local-versus-Colab deviation accepted; obtain signer/anatomy/expert evidence and untouched assessment plan independently. New Android replay, actual device performance and any model deployment remain explicitly deferred.

Verification performed in this audit: real filesystem/path and NumPy shape reads, package metadata discovery, current source inspection, successful read-only freeze/protocol/checkpoint validation, candidate hash verification, matching class-map hashes and app-source-asset hash. No model score was newly measured. Only this discovery report was created.
