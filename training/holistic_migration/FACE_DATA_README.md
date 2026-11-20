# hm1588-v1 additive preprocessing and raw reuse

Engineering candidate only. The approved numerical/missingness contract is
`docs/holistic-migration/FEATURES_FACE.md`. Historical hm153-v1 source, artifacts,
contracts, tests and trainer/evaluator remain unchanged. **The accepted trainer is
153-specific; it cannot consume these tensors.** No fitting, real-source dataset
rebuild, detector, camera, phone or research acceptance is authorized by this
software delivery.

## APIs

`face_features.py` exports `FEATURE_VERSION='hm1588-v1'`, `FEATURE_COUNT=1588`,
`pack_frame(frame)`, `resample_frames(frames, steps=30)` and
`prepare_capture(frames)`. It consumes the unchanged `RawFrame` and
`CaptureResult`, and delegates historical capture reason precedence to the
accepted capture implementation. The first153 values are bit-exact historical
features. All478 face XYZ points are shoulder-relative in XY and face-mean-relative
in Z. Absent face never becomes an eligible bounded capture; malformed face is an
error even outside the hand-bounded interval. No observations are interpolated or
deleted to manufacture eligibility. One missing hand remains permitted.

`face_dataset.build_dataset(*, campaign, output, diagnostic_fit_only=False)` reads
only a completed full historical campaign and lossless numeric raw observations.
It uses the actual unchanged `dataset.validate_campaign` and `read_raw`: no media
is decoded and no detector/model is loaded. It binds both new module bytes, the
approved face contract, all historical producer contract dependencies, current
runtime, source graph, campaign manifest and raw digests. `source_video` and
`synthetic_in_process` provenance labels are inherited unchanged, never guessed.

`face_dataset.validate_bundle(output)` is a read-only **full-bundle** consumer. It
checks failed/incomplete disposition, exact schema types, required artifact
coverage/digests/shapes/dtypes, current implementation/runtime/campaign graph,
frozen class/partition order, raw-derived capture summaries, every ordered tensor,
labels/IDs and fit/validation support. It is intentionally costly: it revalidates
all historical raw files and recomputes face tensors one source at a time. This is
not independent parent acceptance; parent must still independently recompute the
approved mathematics from raw observations. Consumer validation never deletes an
established completion after a transient read failure.

## Diagnostic before full execution

The diagnostic selects the literal lexicographically first frozen fit `clip_id`
per dense class, ordered by the frozen class map. It writes `selected_ids.json`
before **any new face preparation**. Historical provenance validation still reads
all raw files first. Only50 selected recordings receive new feature preparation;
other declared rows retain `not_selected`, unknown new presence summaries, and all
class/partition denominators. Their eligibility is not presumed.

A diagnostic writes `diagnostic_manifest.json`, never `data_manifest.json`. Its
`diagnostic_eligible` describes only selected feasibility. Infeasibility is retained
and the CLI exits2: stop and obtain a parent decision; do not replace the selected
source or relax missingness. A diagnostic can never pass `validate_bundle`, even
if its manifest is renamed. Successful diagnostic completion is not a full build,
training qualification or physical/linguistic acceptance.

Full rebuilding retains all frozen labels, original IDs and membership without
splitting, augmentation or new windows. Sources with unusable captures remain in
the ledger and ineligible/re-recording list, never zero-valued training examples.
Missing eligible fit or validation support for any class saves denominators and
`support_failure.json` without successful completion. An entirely ineligible test
partition is valid storage with `X_test.npy` shape `[0,30,1588]`, not evidence of
model evaluation. Signer IDs remain unknown where the source says unknown.

## Output and failure publication

Use a fresh absolute external directory whose parent already exists. Repository,
input-tree, campaign overlap, symlinks and retries of prior targets are rejected.
Never delete/reuse a previous attempt.

Outputs include Float32 `X_<partition>.npy`, int64 `y_<partition>.npy`, pickle-free
Unicode `clip_ids_<partition>.npy`, `class_metadata.json`, `capture_rows.json`,
`eligibility.json`, `ineligible.json`, `selected_ids.json`, `attempt.json`, exact
`FEATURES_FACE.md` copy, and the appropriate completion manifest. Captures retain
source/raw identity, actual/bounded observation counts, component presence, face
missingness/cardinality counts and a separate derived-row count. Success metadata
always keeps `training_qualified=false`, `live_ready=false`, and
`model_evaluated=false`.

An attempt-owned `incomplete.json` admission barrier exists from preparation until
successful publication/readback. Failed source preparation preserves all declared
identities in `error_rows.json`, distinguishing error from unprocessed rows, when
I/O permits. Failure attempts retain a fixed best-effort `failure.json` disposition.
A full success has neither barrier nor failure disposition.

The new module owns its publication: stage JSON, read it back, exclusively hard-link
the completion, verify digest/JSON again, and retain `.pending` bytes. A failed new
publication is revoked only if it is still the just-linked inode. Rollback and
failure-reporting exceptions cannot replace the primary exception. If both rollback
and failure persistence fail, the incomplete barrier still blocks consumption.
Consumers do not rely on marker absence or filename presence alone. These are
bounded local I/O semantics, **not crash/power-loss/hostile-writer atomicity**.

Preparation reads one source at a time; raw campaigns are not bulk-loaded or copied.
Eligible derived tensors are held in bounded lists and stacked one partition at a
time; the consumer uses memory-mapped arrays. Actual large-campaign runtime/memory
has not been measured by this worker. Historical validation does a full raw readback
before preparation, including for diagnostics.

## Exercised commands and retained evidence

Working directory:
`/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.

Verified interpreter:
`/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python`.
All execution uses `-E -B` and
`TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch`.
No installs were performed.

Evidence root:
`/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/face-data-worker-20261116T015146800861Z`.
Its `runner.py` retains exact expanded commands, stdout, exits, UTC/monotonic
intervals, JUnit and source snapshots/hashes per stage. Stages01–41 include actual
vertical behavioral RED/GREEN cycles and separately identified coverage-only
controls. The report and final `handoff.json` bind all retained receipts.

Final verification invocation patterns (the runner records their exact expansion):

```sh
PY=/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python
E=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/face-data-worker-20261116T015146800861Z
export TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch
"$PY" -E -B "$E/runner.py" 42-final-new training/holistic_migration/tests/test_face_features.py training/holistic_migration/tests/test_face_dataset.py -q --basetemp "$E/42-final-new/pytest"
"$PY" -E -B "$E/runner.py" 43-migration-regression training/holistic_migration/tests -q --deselect training/holistic_migration/tests/test_train.py::test_lazy_architecture_actual_bounded_optimizer_save_reload
"$PY" -E -B "$E/runner.py" 44-original-training training/tests -q
```

The one explicitly deselected migration test performs an actual TensorFlow
optimizer update on synthetic input and is outside this worker's no-fitting
boundary. It is not claimed as passed. Existing synthetic-only historical tests
remain unmodified. No human camera or real detector test is invoked.

The new CLI is exercised in real subprocesses with `--help`, one full synthetic
success, diagnostic success/infeasibility, relative-path, collision and overlap
rejections. Exact expanded CLI commands/stdout/exits are retained in
`42-final-new/pytest/**/cli-results.json` and `diagnostic-cli.json`.

Operational CLI syntax for a separately authorized parent invocation is:

```text
python -E -B -m training.holistic_migration.face_dataset --campaign ABS --output FRESH_ABS [--diagnostic-fit-only]
```

This syntax is not a claim that any real-source invocation ran. Before real
rebuilding, parent must independently review source/spec/quality, freeze bindings,
check storage, decide diagnostic feasibility and preserve all prior evidence.
Actual training, expert/anatomical/linguistic validation, negative data, signer
independence and physical/live/device/model gates remain outside this delivery.
