# Isolated hm153 training and frozen evaluation

This is **executable software preparation tested on explicit synthetic fixtures**, not a real-source tiny proof, fitted candidate, dataset admission, model/research acceptance or live recognition claim. The parent must independently review Task D and admit the completed canonical dataset before executing any real optimization. No model activation, conversion, camera, phone or participant work is authorized here.

## Interpreter and entry points

Run from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration` with the existing environment; do not install dependencies or execute the historical trainer. TensorFlow is lazy: CLI help and rejected admission do not import it. All paths must be explicit, absolute, traversal-free and nonsymlink. Output must be a **new** directory with an existing parent below `../holistic-migration-data/evidence` or `~/.hermes/cache/scratch`, outside input trees. Existing runs never resume, overwrite or append historical logs.

```sh
export TMPDIR="$HOME/.hermes/cache/scratch"
export CUDA_VISIBLE_DEVICES=-1
export TF_NUM_INTRAOP_THREADS=1 TF_NUM_INTEROP_THREADS=1 OMP_NUM_THREADS=1
PY="$HOME/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python"
"$PY" -E -B -m training.holistic_migration.train --help
"$PY" -E -B -m training.holistic_migration.train tiny-fit --help
"$PY" -E -B -m training.holistic_migration.train fit --help
"$PY" -E -B -m training.holistic_migration.evaluate --help
```

The following are **parent execution templates, NOT real commands executed by this worker**. Replace the descriptive uppercase absolute paths with the admitted inputs and exclusively fresh outputs:

```sh
"$PY" -E -B -m training.holistic_migration.train tiny-fit \
  --bundle /ABS/CANONICAL_BUNDLE --admission /ABS/PARENT_ADMISSION.json \
  --output /ABS/NEW_TINY_RUN
"$PY" -E -B -m training.holistic_migration.train fit \
  --bundle /ABS/CANONICAL_BUNDLE --admission /ABS/PARENT_ADMISSION.json \
  --tiny-proof /ABS/RETAINED_TINY_RUN/tiny-proof.json --output /ABS/NEW_FIT_RUN
"$PY" -E -B -m training.holistic_migration.evaluate \
  --run /ABS/FROZEN_FIT_RUN --bundle /ABS/CANONICAL_BUNDLE \
  --admission /ABS/PARENT_ADMISSION.json --output /ABS/NEW_EVALUATION
```

Help exits0; parser/admission refusal exits2; a runtime failure retains its start/config/partial artifacts and returns an error. Actual CLI subprocess tests exercise synthetic-admission rejection; there is **no synthetic CLI option**, epoch override, dynamic module loader, implicit data root or ungated full-fit operation.

## Parent-created admission: exact frozen schema

After independent full-source support and canonical readback, the parent may create this separate JSON. It must have exactly these nine keys, strict built-in integer schema1/classes50 (not boolean or equal float), literal status/purpose and lowercase SHA256 values:

```json
{
  "schema_version": 1,
  "status": "accepted_canonical_dataset_for_training",
  "purpose": "fit_validation_only",
  "bundle": "/absolute/canonical-bundle",
  "data_manifest_sha256": "REPLACE_WITH_64_LOWERCASE_HEX",
  "campaign_manifest_sha256": "REPLACE_WITH_64_LOWERCASE_HEX",
  "source_contract_sha256": "944e7b7acb495899bd78a937d3a453e2e188812c9a747ce05b9667537ccb15bc",
  "class_map_sha256": "e8089f5c0186bfe6fd9ec63a5150f8094645c1686509f23c1716453b5f9ce0d5",
  "classes": 50
}
```

Do not change C's `data_manifest.json`: `training_qualified=false` remains mandatory and the separate admission opens only this bounded dataset gate. Require schema1/complete/source_video/augmentation none, fixed `Float32[N,30,153] hm153-v1`, current C source contract, exact ordered50 metadata, and matching bundle/campaign/class hashes. Duplicate JSON keys and nonfinite constants are refused. A copied/stale admission, synthetic evidence, unsupported class or changed mapping cannot qualify.

The reader independently checks required JSON metadata, frozen partition membership, full declared capture/eligibility denominators and hashes/shapes/dtypes/order of **only** `X_fit/y_fit/clip_ids_fit` and `X_validation/y_validation/clip_ids_validation`. Both partitions need all50 eligible classes, unique/disjoint IDs, plain finite Float32 tensors, int64 labels0–49 and Unicode IDs without pickle. Masks, absent individual hands, invisible pose slots, wrist-local depth and shoulder midpoint/2D scale are checked; inputs are made read-only. No zero placeholders, reconstruction, test-array hashing/loading or C `validate_campaign()` occurs in training. Test *metadata* and unopened artifact records may be validated; test *contents* remain separate.

## Fixed family and augmentation

Fresh weights, input `[batch,30,153]`, canonical dense50 softmax outputs; Conv1D64/128 kernel3/same/ReLU with BatchNorm each, MaxPool2, LSTM128(sequence)/64 with dropout0.4 after each, Dense128/ReLU + dropout0.4 + Dense50. Adam0.001, sparse categorical crossentropy. The executed TF2.19.0 constructor has **250674 parameters**. Source/runtime versions and fixed family are frozen with seed20260705.

Full fit uses original fit sequences plus **one independently source-ID-seeded XY rotation copy** per original, uniform within ±5 degrees, one angle for its whole sequence. Only present hand XY and usable pose XY rotate. Z, visibility and masks remain bitwise unchanged; absent individual hands and invisible slots stay zero. No mirror, swap, translation, interpolation or invented hand. Shoulder midpoint/2D scale and local-depth conventions are preserved. Validation/test and tiny memorization are not augmented. Receipt records seed/policy/source IDs/angles/derived count and `real_observations_added=0`. This is experimental augmentation, not expert linguistic validation.

## Tiny, full fit and exclusive publication

Tiny selection is the literal-first eligible fit ID for each dense0–7, exactly8 examples with the unchanged50-output model. No prediction/loss/test-based selection. One full batch per epoch, up to300 epochs. `tiny-proof.json` is published only after saved checkpoint reload gives8/8 correct and mean sparse crossentropy≤0.1 on those exact tensors. Failure is retained, not silently retried. A full fit verifies this retained proof's source/runtime/dataset/admission/class/feature/config/IDs/tensor/checkpoint/prediction bindings and **reruns fit-only checkpoint readback**, then builds a fresh model rather than using tiny or legacy weights.

Full fit is at most120 epochs, batch32, seeded shuffle; explicit untouched validation is supplied to the callback bridge. Bounded `train_on_batch` avoids implicit tf.data worker pools. Keras EarlyStopping monitors `val_accuracy`/max, patience15; ReduceLROnPlateau monitors `val_loss`/min, patience6/factor0.5. Best validation accuracy wins; exact ties keep the earliest checkpoint. Only the working `candidate.keras` can be replaced. Final checkpoint/config/history/probability/ID/report receipts are exclusively published and read back. Actual epochs and optimizer iterations are recorded, including interrupted partial progress; unknown failed step readback is null, never fabricated.

Tiny layout: `start.json`, `config.json`, `history.json`, `candidate.keras`, `model.keras`, `selected_probabilities.npy`, `selected_ids.npy`, and successful `tiny-proof.json` only if its criterion passes. Full layout: start/config/history/candidate/model plus `policy.json`, `augmentation.json`, `validation_probabilities.npy`, `validation_ids.npy`, frozen `selection.json`; then `fit_probabilities.npy`, `fit_ids.npy`, `fit-report.json`, `validation-report.json`, and `complete.json`. Exclusive JSON publication retains `.pending` evidence. Failure adds `failure.json`, does not reuse an output and cannot create successful gating receipts. A later report failure preserves an already frozen model/selection but does not claim report completion.

The policy is `closed_set_argmax`, `unknown_rejection=unmeasured_no_observed_validation_negatives`, `live_ready=false`. Negative count/FAR/safe-unknown fields are null with explicit status, not measured zeros. No rejection threshold is mined from test or outside the approved50 signs.

## Separate exploratory evaluator

The separate evaluator verifies frozen model/policy/config/source/runtime/dataset identities and the earliest validation-best history before reserving an evaluation. It creates `evaluation-start.json` **before any test-array hash/load/inference**. It rechecks checkpoint validation predictions, then reads only the explicit test partition for this frozen model. There is no implicit ranking, best-test selection or tuning.

Output: `evaluation-start.json`, `probabilities.npy` `[eligible,50]`, `predictions.npy` dense argmax, `eligible_ids.npy`, `eligible_labels.npy`, `report.json`, `evaluation-complete.json`. Probability shape/finite/range/unit sum, ordered ID mapping and exclusive artifact readbacks are checked. All50 literal dense/original/label/category mappings remain unchanged. Report includes per-class precision/recall/F1/support, macro-F1 over all50, confusion, exclusions and declared/eligible/ineligible/unknown-missing denominators; missing sources are not zero tensors or inferred predictions. Precision/recall/F1 zero denominators use0; empty accuracy is null. This convention is distinct from **unmeasured negative/FAR fields**, which remain null.

Test has historical exposure: report always says `exploratory_reused_test`, `fresh_untouched_holdout=false`, `tuning_allowed=false`. Completed exact-target evaluations may be artifact-hash/readback-only without reopening test content or loading a model. Existing/incomplete targets never silently rerun. A reporting/publication failure retains its start/partial artifacts and no completed receipt. Local hashes, callbacks and trusted in-process synthetic seams are **not** an OS sandbox or signed provenance.

## Verification and evidence

```sh
"$PY" -E -B -m pytest -p no:cacheprovider \
  training/holistic_migration/tests/test_augmentation.py \
  training/holistic_migration/tests/test_train.py \
  training/holistic_migration/tests/test_evaluate.py -v
"$PY" -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests -v
"$PY" -E -B -m pytest -p no:cacheprovider training/tests -v
```

Tests use explicit synthetic provenance, not fabricated source_video receipts. Real TF forward/optimizer/save-reload and bounded actual synthetic lifecycle execution prove executability only. Synthetic oracle/fault seams exercise successful gating and failures without pretending to measure learning; a separately labeled actual-TF full-lifecycle test uses an explicit trusted synthetic proof seam, not a real tiny proof. CLI still rejects all synthetic admissions. Review `docs/holistic-migration/task-d-report.md` for incremental RED/GREEN versus coverage-only GREEN, source-bound commands/exits, unsuppressed warnings, retained external artifacts and immutable handoff. No Task D acceptance or real/tiny/full/test/human gate is granted by this worker.
