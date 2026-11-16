# Task D — isolated hm153 trainer/evaluator preparation

## Goal and authorization boundary

Prepare and execute meaningful synthetic tests of the isolated 50-output CNN-LSTM trainer, fit-only masked augmentation, retained tiny-overfit proof lifecycle and separately frozen exploratory evaluator. This implements section4 of the approved root HOLISTIC_MIGRATION_PLAN.md; it does not authorize this worker to run real-data fitting, inference, evaluation or model activation.

A/B/C software are independently accepted. The parent's actual first-literal frozen-fit diagnostic passed50/50 examples with3057 observations; full1016-source extraction/canonical building runs separately. Its complete real support and parent dataset admission are NOT yet established. Code preparation with synthetic fixtures is independent; real tiny-fit/full training must wait for verified full dataset support, D review and parent execution. Do not read real canonical arrays, source videos or model weights in this worker. Published metadata and code may be read. No phone/app/camera/GUI, participant stores, installs, provider changes, commits/pushes, historical log/model/reference edits or actual-source optimization.

## Owned additions only

Before edits verify all8 destinations absent and parent protection receipt exact. Create only:
1. training/holistic_migration/train.py
2. training/holistic_migration/evaluate.py
3. training/holistic_migration/augmentation.py
4. training/holistic_migration/tests/test_train.py
5. training/holistic_migration/tests/test_evaluate.py
6. training/holistic_migration/tests/test_augmentation.py
7. training/holistic_migration/TRAINING.md
8. docs/holistic-migration/task-d-report.md (create first; incremental append-only commands/exits/evidence)

All existing A/B/C sources/tests/README/specifications/acceptance/report files and legacy training sources are protected. Do not edit package __init__.py or existing tests. New files do not change C contract_binding(): its source list is explicit, not a directory glob. Parent's source-data job must keep that exact contract stable. Output/checkpoints/fixtures/logs live in fresh exclusive directories under ../holistic-migration-data/evidence or approved scratch, never historical defaults or the cloud checkout.

## Required architecture and interfaces

Read the exact legacy builder training/models/train_cnn_lstm.py:65-87; never call its main or historical data/log/export paths. New constructor must reproduce that verified family with fresh weights and fixed candidate input/output: Float32[batch,30,153] and50 softmax outputs in canonical dense order. Conv1D64 and128, kernel3/same/ReLU, BatchNorm after each, MaxPool1D2 after final Conv; LSTM128(return_sequences=True), dropout0.4, LSTM64, dropout0.4; Dense128/ReLU, dropout0.4, Dense50/softmax. Adam learning_rate0.001 and sparse categorical crossentropy. Existing executed shape smoke counts250674 parameters. Verify layers/configuration/parameter count with a real synthetic forward and bounded optimizer step in the existing TF2.19.0 environment. Do not silently alter the architecture, output order, feature channels, normalization or masks. Lazy TensorFlow imports follow input/path admission.

New code may use accepted dataset.safe_path/sha256/canonical_hash/runtime_binding and immutable C artifact schemas, but must not modify them or call validate_campaign during fit admission: that consumer reads all partitions, including test raw data. Real training opens fit/validation only. Read dataset.py:455-513 and README canonical section for actual artifact schema before implementing readers.

Provide explicit commands documented in TRAINING.md, using existing interpreter -E -B:
- train tiny-fit --bundle ABS --admission ABS --output NEW_ABS
- train fit --bundle ABS --admission ABS --tiny-proof ABS --output NEW_ABS
- evaluate --run FROZEN_RUN_ABS --bundle ABS --admission ABS --output NEW_ABS
No implicit roots, arbitrary command/module loading or synthetic CLI bypass. Document actual tested signatures and artifact layouts; preserve these operation meanings if parser wording differs.

## Dataset admission and held-out boundary

Real CLI requires a separate parent-created admission JSON, not a changed C data manifest. Freeze this minimal exact schema so parent can produce it after full-source readback:

```json
{
  "schema_version": 1,
  "status": "accepted_canonical_dataset_for_training",
  "purpose": "fit_validation_only",
  "bundle": "/absolute/canonical-bundle",
  "data_manifest_sha256": "64 lowercase hex",
  "campaign_manifest_sha256": "64 lowercase hex",
  "source_contract_sha256": "944e7b7acb495899bd78a937d3a453e2e188812c9a747ce05b9667537ccb15bc",
  "class_map_sha256": "e8089f5c0186bfe6fd9ec63a5150f8094645c1686509f23c1716453b5f9ce0d5",
  "classes": 50
}
```

Require exact keys/types (built-in integer1/50, not bool or equal floats), absolute nonsymlink scope and matching manifest/campaign/class/contract bindings. C data_manifest remains training_qualified=false: parent admission opens the bounded dataset gate separately and does not imply physical/research/model approval. Real manifest must be schema1/status complete/source_video/augmentation none, exact class metadata and current C contract. Reject stale/copied admissions, altered class order or model dimensions before importing TensorFlow/creating output.

Training reader verifies and loads only X_fit/y_fit/clip_ids_fit, X_validation/y_validation/clip_ids_validation and their required JSON metadata. Hash/read no test arrays or labels, including indirect all-artifact verification. Full manifest/capture-row/class/eligibility metadata may be read. Fit/validation IDs must be unique, disjoint and match eligible metadata/order/dense labels. Require all50 classes supported in both, finite plain Float32[N,30,153], int64 labels in0..49, pickle-free Unicode IDs and mask/absent-block invariants. No zero placeholders or reconstruction from unavailable sources. Do not mutate canonical arrays.

Tests use isolated explicitly synthetic fixtures and trusted in-process seams only. A synthetic success artifact must retain synthetic provenance and must never satisfy real CLI full-training/tiny-proof admission. No hidden --allow-synthetic production switch or fabricated source_video receipts. Exercise denial of every test-array/label read in both tiny-fit and fit using an instrumented open/load seam.

## Fit-only masked augmentation

Implement a conservative, seeded in-plane XY rotation, one independently derived copy per original fit sequence, bounded by5 degrees, with one angle across that sequence. Rotate only present hand XY coordinates and usable pose XY coordinates; leave Z, pose visibility and all3 masks unchanged. Missing individual-hand blocks and invisible pose values stay exactly zero; no mirroring, semantic hand swap, translations, temporal interpolation, hand invention or test/validation augmentation. Rotation preserves shoulder midpoint/2D scale and wrist/shoulder-local depth conventions. Record seed/angle policy/source IDs/derived counts separately from real observations. Canonical tensors remain unchanged. Keep tiny memorization unaugmented. This is an experimental training augmentation, not expert linguistic validation.

Required tests cover one missing hand while the other is present, both-hand missing rows, invisible pose slots, asymmetric inputs, mask/Z/visibility preservation, determinism, source immutability and validation/test exclusion. Do not reuse the historical concatenated-hand transform that corrupts absent individual slices.

## Tiny proof, full fit and publication

Use seed20260705. Freeze config/source/runtime/dataset/class identities and chosen source IDs before optimizer use. Tiny rule: one literal-first eligible fit ID for each of dense0..7 (8 examples,50-output model). No selection by predictions, loss or test content. Before accepting full fitting, require a retained real-source tiny checkpoint that reloads and achieves8/8 correct with mean sparse crossentropy<=0.1 on those exact8 inputs. Tiny max300 epochs; full fit max120 epochs/batch32, early stopping patience15 on val_accuracy/mode max and ReduceLROnPlateau patience6/factor0.5 on val_loss. Preserve exact configuration before computation; no automatic hyperparameter sweep or retry that erases failed runs. Record actual epochs/optimizer steps, not claimed progress from saved code.

The real tiny proof binds current training/augmentation/evaluation sources, dataset/admission/class/feature identities, the exact selected fit tensors/IDs, saved checkpoint bytes and reloaded predictions/loss. A boolean, missing/altered checkpoint, synthetic proof, changed trainer/config family or different dataset cannot unlock real full fit. Tests must exercise those rejections before fit. Worker may exercise this lifecycle synthetically but must not create a real tiny proof or read the parent's actual-source arrays.

Full fit creates a fresh random model, not the tiny/legacy weights. Add original plus rotated fit examples only; validation stays unaugmented, untouched, explicitly passed to callbacks. Select only best validation accuracy with earliest exact tie; retain actual best checkpoint and verify reload predictions before publishing a frozen selection. Checkpointer may update only its own working candidate inside the newly reserved run; final model/selection/config/history/prediction receipts are exclusively published. Never overwrite an existing run or append historical experiment logs. Retain incomplete/failed start receipts and partial artifacts; no successful gating receipt if final readback fails. Preserve report commands/exits immediately after each vertical tracer.

A frozen closed_set_argmax policy must explicitly mark unknown rejection unmeasured_no_observed_validation_negatives and live_ready=false: no usable negatives are currently admitted, so FAR/safe unknown or autonomous-idle claims are unavailable, not zero. Do not read outside the approved50 classes or mine test examples for rejection thresholds. Model activation/export/phone conversion is out of this worker's scope.

## Evaluation and honest denominators

Train emits fit/validation reports only. Separately invoked evaluator requires the frozen selected checkpoint/policy/config/source/dataset identities and an exclusive evaluation-start receipt before any test content access. No implicit test ranking/default best-test selection. Test is historically exposed and remains exploratory reused-test evaluation, not a fresh untouched holdout. Never tune from its outcomes.

Persist eligible predictions/probabilities/ordered IDs and verify probability shape/finite/range/sum and index mapping. Report per-class precision/recall/F1/support, macro-F1, confusion and exclusions for eligible sources; also report all-declared source denominators with ineligible sources unknown/missing, never zero tensors or silently removed classes. Define zero-denominator conventions explicitly and retain unmeasured negative/FAR fields as null with status, not numeric0. Verify metrics against deterministic small fixtures, including ineligibility and sparse original IDs. Keep all50 output labels/categories literal and unchanged.

An existing completed evaluation may be receipt-readback-only without reopening test data; an incomplete/existing target cannot silently rerun test inference. Preserve successful model selection even if later report generation fails, but never mark failed report publication successful. Trusted in-process callbacks and local hashes are not an OS sandbox or signed provenance.

## Verification, review and handoff

Follow strict vertical TDD; behavioral RED before each new production slice, coverage-only GREEN labeled honestly. Use synthetic fixtures only, with deterministic CPU/thread-bounded tests. Actual small TF forward/optimizer/save-reload establishes executable architecture/lifecycle only, never real learning or a real-source tiny proof.

Run named new tests and complete current pytest migration/original suites with approved interpreter -E -B, scratch TMPDIR and -p no:cacheprovider. Baseline before D is285 migration cases/293 subtests,51 original cases/289 subtests with3 original warnings; report actual collected counts, not these expected numbers. No installs or warning suppression. Verify all parent protected hashes, source-data contract digest unchanged, tracked/index diff empty and no pyc/cache in the migration source.

Report exactly changed8 additions, current owned/source/runtime/protected hashes, actual commands/exits/logs and stage limitations. Freeze a verifiable handoff in fresh external evidence. Worker grants no D acceptance, real dataset admission, real fitting/evaluation, webcam, deployment or research approval. Parent must independently verify/review the complete new task before any real optimization.
