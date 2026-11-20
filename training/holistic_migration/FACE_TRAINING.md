# hm1588-v1 Phase 4 tooling

## Boundary

These additive entry points accept the reviewed full face-inclusive bundle, not the historical hm153 bundle. Historical code and the builder's `training_qualified=false` remain unchanged. A separate parent-owned admission binds the existing dataset acceptance. CLI admission requires `source_video`; there is no synthetic, backend, epoch, architecture, or class-count CLI override.

The implementation worker executes synthetic tests only. Parent review, actual eight-source tiny proof, fresh all50 fitting, and separate exploratory test evaluation remain parent-owned. A synthetic lifecycle fixture is never evidence of real learning. No camera, extraction, participant, phone, export, activation, Git publication, or research/live acceptance is implied.

## Admission contract

`face_train.read_admitted(bundle, admission)` checks the exact admission keys below, strict JSON duplicate/nonfinite handling and schema types, approved bundle path and data-manifest digest, and the exact existing parent acceptance path. It binds current face implementation plus historical producer contracts, runtime, original source graph/inventory/partition/decoder/model metadata digests, literal dense/original/class identities, source campaign ledgers, capture presence/count/exclusion reconciliation, and complete unaugmented full hm1588 metadata. Failed/incomplete bundles and campaigns are denied.

Only fit and validation tensor contents are opened/hashed by training admission and its rechecks. Test shape/dtype/digest metadata and source/partition ledgers are allowed; test arrays and raw observation NPZ contents are not accessed. Neither `face_dataset.validate_bundle` nor the all-source `dataset.validate_campaign` is called from training. Parent's prior raw-to-tensor acceptance remains the provenance authority, rather than silently reproducing test transformation within a classifier-training command.

The admission is a new parent-owned JSON object with **exactly**:

```python
{
    'schema_version': 1,
    'status': 'accepted_face_dataset_for_training',
    'purpose': 'face_fit_validation_only',
    'bundle': str(bundle),
    'data_manifest_sha256': sha256(bundle / 'data_manifest.json'),
    'dataset_acceptance': str(existing_parent_acceptance),
    'dataset_acceptance_sha256': sha256(existing_parent_acceptance),
    'campaign_manifest_sha256': manifest['campaign_manifest_sha256'],
    'implementation': manifest['implementation'],
    'graph_sha256': canonical_hash(manifest['graph']),
    'classes': manifest['classes'],
    'tensor_contract': 'Float32[N,30,1588] hm1588-v1',
}
```

Here `sha256` and `canonical_hash` are unchanged `training.holistic_migration.dataset` helpers. Use exclusive `dataset.write_json` at a fresh parent-chosen external path. Do not edit or relabel the existing dataset acceptance or manifest. Existing acceptance status remains `accepted_bounded_face_inclusive_dataset` and `training_qualified=false`.

Exact real bundle: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/hm1588-canonical-bundle-20261116-v1`.

Exact approved manifest: `71c644b4de78f7031f96f7b25b1d5766f18fa611c33ad12f2a40a353b1c6c19a`.

Existing acceptance: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/face-data-parent-20261116/dataset-acceptance.json`.

## Fixed family and resources

Input30×1588; Conv1D64/128, kernel3/same/ReLU with BatchNorm after each; MaxPool2; LSTM128(return_sequences)/64, dropout0.4 after each; Dense128/ReLU/dropout0.4; Dense50/softmax. Fresh weights, Adam0.001, sparse categorical crossentropy, seed20260705. Parameter count526194. No architecture search, class reduction, or warm start from tiny weights.

The native backend uses explicit bounded NumPy batches and `train_on_batch`, not implicit `tf.data` pools. Set the CPU/thread environment identically for tiny, full and evaluation; its values, host, interpreter, Python and installed package versions are part of frozen identities. No environment installation/configuration is required. A later runtime/source change (including the new calibration helper) invalidates retained proofs/selections; historical artifacts must keep their original source snapshots and interpretation, never be restamped as current. This correction does not rehabilitate the old failed checkpoint. Resolve changed identities by parent review, not silently relaxing identity checks.

## Tiny proof

`tiny-fit` chooses the literal lexicographically first **eligible fit** ID for each dense class0…7. Exactly eight source examples retain all50 outputs. No augmentation or validation/test optimization. The hard budget is300 full-batch epochs, with early success only when inference obtains8/8 correct and mean CE≤0.1. The final checkpoint must save/reload and reproduce its probabilities before publication. After the unchanged optimizer loop (including its existing early-success behavior), every native tiny result receives exactly one `tiny_fit_layerwise_exact_moments_v1` correction before the final save and gate. A pre-calibration success is not final qualification.

The correction uses **only the exact eight selected fit tensors**, without labels, augmentation, validation/test inputs or optimizer updates. The native helper traverses supported Float32 Sequential layers in graph order, computes channel-wise population mean/variance over batch/time using Float64 reductions cast once to Float32, assigns only `moving_mean`/`moving_variance`, then forwards that layer at `training=False` before estimating the next layer. Dropout stays off. Gamma/beta, all other weights, optimizer slots/iterations and model/optimizer configuration are hash-receipted unchanged. Invalid model/input/nonfinite state is denied; an interrupted attempt restores snapshotted variables and re-raises the original exception (rollback failures are attached as notes, never treated as success). This is a **persistent frozen-statistic candidate change**, not batch-mode serving.

`batchnorm-calibration.json` records exact pre/post moments, helper protocol/source hash, input/selected identities, current trainer source binding, finite checks, locked-state hashes, optimizer steps, pre-calibration metrics/probability digest, and final model digest. `history.json` remains optimizer-only inference; `pre_calibration_probabilities.npy` separately preserves the final pre-correction probabilities. The producer and actual `_verify_tiny` consumer verify the receipt against the reloaded checkpoint and recompute population moments read-only. They additionally clone the unchanged final native weights, assign **only the clone's recorded pre-moments**, and replay ordinary `training=False` inference against the retained `pre_calibration_probabilities.npy` at Float32 `rtol=1e-6, atol=1e-7`. This binds the native pre-state to the independently hash-bound optimizer-only probability/metric/history evidence; finite plausible pre-moment mutations cannot qualify just by rebinding a receipt digest. The calibrated candidate is never restored to pre-state, recompiled or optimized: every candidate variable (including Dropout RNG and optimizer slots/iterations), model/compile/optimizer configuration is checked unchanged even when replay fails. This is consistency verification, not hostile-writer authenticity. Both compare singleton and eight-example ordinary-inference probabilities at Float32 `rtol=1e-6, atol=1e-7`. The unchanged final gate is **8/8 AND mean CE≤0.1**. Calibration can fail that gate; a receipt alone never qualifies a run.

Synthetic lifecycle backends receive the explicit `synthetic_lifecycle_only_no_calibration` receipt with `native=null`; this is never native learning or real-source evidence. Native synthetic controls exercise real Adam, moment assignment and saved/reloaded ordinary inference. The full fitting algorithm/callbacks/selection, architecture,50 labels and closed-set policy are unchanged; full fitting never calls calibration.

Retained artifacts: `batchnorm-calibration.json`, `pre_calibration_probabilities.npy`, `start.json`, `config.json`, `history.json`, `candidate.keras`, `model.keras`, `selected_X.npy`, `selected_y.npy`, `selected_ids.npy`, `selected_probabilities.npy`, and only on success `tiny-proof.json`. Proof binds exact selected source IDs/tensor digests, source/runtime/dataset identities, actual optimizer steps/epochs, and retained file hashes. Failed learning still retains actual checkpoint/progress and `failure.json`, never a qualifying proof. Full entry rehashes proof artifacts, reloads its model, checks actual optimizer state and exact original fit-only examples again before reserving a new full run.

## Full fit and freeze

`fit` creates a fresh model and a two-copy fit corpus: each unmodified fit original plus exactly one source-ID-seeded XY rotation within±5°. One angle per whole sequence is shared by hands, visible pose and present face XY. Depth, visibility, masks and absent/invisible blocks remain unchanged. `augmentation.json` retains source IDs, angles and policy. No mirroring, swapping, invented observations, or validation/test/tiny augmentation.

Budget120 epochs, batch32, deterministic seeded shuffling; explicit original validation. Native callbacks: EarlyStopping val_accuracy/max/patience15; ReduceLROnPlateau val_loss/min/patience6/factor0.5. Earliest maximum validation accuracy wins exact ties. `history.json` records epoch, cumulative optimizer steps, `loss`, `accuracy`, `val_loss`, `val_accuracy`. Epoch train metrics are explicit inference-mode measurements over the augmented fit corpus, not rolling `train_on_batch` metrics; validation metrics use original unaugmented validation.

The best checkpoint is reloaded, its validation probabilities checked, then frozen with ordered classes in `selection.json` identity and explicit `policy.json`. `selection-disposition.json` is required after successful selection publication; only then are fit/validation reports produced. `complete.json` denotes complete fit reports, not deployment/readiness. `candidate.keras` and `model.keras` may be local hard links; do not edit either after freezing.

## Reports and test separation

Reports include all50 precision/recall/F1/support, recall as per-class accuracy, macro-F1 including zero-support classes,50×50 confusion, crossentropy and overall eligible-source accuracy. Excluded source IDs/reasons and all-declared/eligible denominators are explicit. `all_declared_bounds` gives lower/upper accuracy bounds, **not measured accuracy** on excluded sources; missing sources never receive fabricated predictions.

`closed_set_argmax` rejects zero scored positives by policy, which is distinct from data exclusions. Annotated validation negatives do not exist: false-accept, idle/unknown safety, rejection calibration/threshold and negative count remain null/unmeasured. `live_ready=false` throughout. Existing19 data exclusions remain authoritative accepted data accounting, not19 policy rejections.

`face_evaluate` is a separate command. Before a new evaluation target it checks frozen selection/config/model/current source bindings and re-verifies the tiny proof. It exclusively writes/readbacks `evaluation-start.json` **before any test array hash/load/inference**. It checks reloaded frozen validation predictions, then loads the test partition. Outputs: `probabilities.npy`, `predictions.npy`, `eligible_ids.npy`, `eligible_labels.npy`, `report.json`, and `evaluation-complete.json`.

Every test report is `evaluation_kind=exploratory_reused_test`, `fresh_untouched_holdout=false`, `tuning_allowed=false`. Do not rank candidates, tune thresholds or retune from test results. Existing complete targets are readback-only, without model reload or test access. Failed/incomplete targets cannot implicitly rerun; preserve them and refer failure disposition to the parent.

## Publication/failure semantics

Fresh exclusive output directories only under the external Phase4 evidence root (explicit synthetic in-process tests additionally use approved scratch). Symlink/relative/overlapping paths are denied. Staged JSON publication uses exclusive link plus digest/JSON readback and retains pending evidence. Failed tiny, selection or affirmative disposition publication denies residual success at the actual consumer, even when rollback cannot remove its marker but failure diagnostics persist. Successful selection remains consumable after later fit-report failure only with exact source-bound `phase=fit_reports, frozen=true` failure disposition. Reporting failure never claims complete reports. A newly failed evaluation readback revokes its success marker when possible and persists failure; established completed-target readback never mutates an old target.

These are bounded local semantics, **not** hostile-writer, power-loss, permanent-media or crash guarantees. Simultaneous rollback and diagnostic-persistence failure cannot be claimed universally fail-closed. Native optimizer interruption may retain only completed epochs plus actual partial optimizer-step diagnostics; no steps are invented.

## Parent commands after independent review

Run from the repository, not the Thesis directory. Paths below must be fresh; reserve/adjudicate them as parent. Do not execute the full command unless actual tiny proof passes, or the evaluation command before frozen full selection is reviewed. These examples were not executed on real sources by the implementer.

```bash
cd /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration
PY="$HOME/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python"
export TMPDIR="$HOME/.hermes/cache/scratch"
export OMP_NUM_THREADS=1 TF_NUM_INTRAOP_THREADS=1 TF_NUM_INTEROP_THREADS=1
export OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export CUDA_VISIBLE_DEVICES=-1 TF_ENABLE_ONEDNN_OPTS=0
PHASE4=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/phase-4-20261116
BUNDLE=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/hm1588-canonical-bundle-20261116-v1
ADMISSION="$PHASE4/face-training-admission-v1.json" # parent creates exact object above
TINY="$PHASE4/tiny-source-bn-correction-v1" # proposed fresh parent-owned path; never reuse failed tiny-source-v1
FIT="$PHASE4/full-source-v1"
EVALUATION="$PHASE4/exploratory-reused-test-v1"

"$PY" -E -B -m training.holistic_migration.face_train tiny-fit   --bundle "$BUNDLE" --admission "$ADMISSION" --output "$TINY"

# Only after actual tiny proof succeeds and is checked:
"$PY" -E -B -m training.holistic_migration.face_train fit   --bundle "$BUNDLE" --admission "$ADMISSION"   --tiny-proof "$TINY/tiny-proof.json" --output "$FIT"

# Separately invoked, only after validation selection freezes and is checked:
"$PY" -E -B -m training.holistic_migration.face_evaluate   --run "$FIT" --bundle "$BUNDLE" --admission "$ADMISSION" --output "$EVALUATION"
```

For software verification with the same bounded environment:

```bash
"$PY" -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests
"$PY" -E -B -m pytest -p no:cacheprovider training/tests
```

Keep warnings and exact commands/logs/JUnit/source hashes. Review includes separate specification and quality verdicts and exact consumed input bindings. Parent verifies protected-source preservation and reruns current tests before any actual fitting. Do not edit implementation between tiny/full/evaluation to rescue a failed candidate.
