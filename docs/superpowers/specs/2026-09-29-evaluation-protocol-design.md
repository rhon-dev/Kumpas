# Evaluation protocol repair — design

Date: 2026-09-29
Status: Design approved in conversation (Approach A); written spec pending user review before implementation.
Scope: Offline model-selection integrity and the wording of evaluation claims. No new participant clips or app changes.
Authorization: The requester reports PM Cabrera and adviser Abella approved the protocol change. This document does not stand in for their signed record; update the project's gate evidence separately when available.

## Decision and alternatives

Preserve the published FSL-105 train/test CSV split and the existing 813/203 selected-class sequence arrays. Do not revise source clip labels or silently rewrite historic results. A full 1,016-clip re-split would lose comparability and cannot make previously examined examples genuinely untouched; cross-validation is useful later but is not required for this repair. Prior test evaluations were consulted across four model variants, so the 203-clip test set is **historical/exploratory**. No new clips are available. No post-hoc procedure may describe it as a pristine final holdout.

## Data flow and boundaries

1. Keep `build_sequences.py`'s `X_train.npy`, `y_train.npy`, `clips_train.json`, and test equivalents as immutable source arrays. Verify equal lengths, unique source clip names, labels, and the original train/test clip-name disjointness. Detect manifest/array drift with hashes and fail closed.
2. A deterministic, class-stratified splitter partitions *original train clips* into fitting and validation groups (nominal 20% validation, minimum two originals per class, fixed seed 20260705). Write a versioned manifest containing source clip name, original array index, class ID, partition, seed, split algorithm/version, source-file digests, and per-class counts. The manifest is the sole authority for all subsequent steps. Never use an augmented row as the unit of partition.
3. Produce the fit arrays by selecting source originals whose manifest partition is `fit`, then append geometric augmentations **only for fit**. Validation arrays contain exactly the untouched original `validation` rows; test arrays are not read by the splitter or augmenter. Preserve the current transform semantics and log source clip, partition, copy index, and transform parameters. Use new output names/protocol directory so the old `X_train_aug.npy` and historic runs remain intact.
4. Training loads explicit fit and validation arrays, never `validation_split` on augmented data; early stopping, learning-rate decisions, and model ranking use validation measurements only. Do not load `X_test.npy`/`y_test.npy` or call model.predict on test in the train/model-selection path. Record run ID, model parameters, seed, manifest/dataset hashes, training environment, validation metric, and chosen checkpoint in a new experiment record, not by editing four historic runs.
5. A separate explicit evaluation command accepts a frozen run ID, selected checkpoint, protocol manifest, and selection record; it refuses mismatches, computes accuracy/macro metrics/per-class support and uncertainty on the existing 203 test clips, and marks its report **exploratory: previously used for model selection**. It must not choose a run by maximum test score. `eval_report.py` must require an explicit run ID for historic reports or use the frozen validation-selected run in the new protocol; remove its existing `max(test_accuracy)` default. No subsequent model change is justified using this test score without declaring the result exploratory.

## Signer-identity decision

The source CSVs have `vid_path,id_label,label,category`, not signer IDs. Indices 0–21 occur in both source train and test, but identical indices are not proof of a shared person. Check the primary dataset documentation or obtain an authoritative creator-provided signer map; a manual visual audit may yield qualified evidence but must follow dataset-use/privacy constraints and retain an auditable method. Do not infer identity solely from filename indices, geometry clustering, or model accuracy. Until independently verified metadata exists, say: “Accuracy on the specified FSL-105 clip split; signer-independent generalization not established.” If authoritative IDs become available, publish a separately versioned signer-disjoint evaluation protocol rather than silently changing this one.

## Reporting and provenance

- Preserve the original 95.07% (193/203) calculation as a historic exploratory benchmark. Its old 100% validation score came from augmented siblings crossing validation; it is not an independent validation result.
- Add a prominent note to README, phase gates, and the thesis-facing report that the existing test was consulted repeatedly, per-class support is usually four, and signer independence is unknown. Never claim a new `>=90%` gate from newly selected weights without qualifying these limitations.
- Future result tables distinguish `validation-selected / exploratory reused test` from a truly new external evaluation, should one become available. Record counts and confidence intervals only with stated assumptions (clip-level independence is not verified).
- Existing `.npy` training arrays, historical predictions/reports/log entries, and app model artifacts remain unchanged. A new offline result does not automatically replace the shipped TFLite model.

## Failure handling and verification

- Tests: same seed/input produces identical manifest and fit/validation membership; classes retain fit and validation support; duplicate or inconsistent clip metadata fails; each augmented fit row traces to an original fit clip; no validation/test source appears among augmented fit rows; an altered source digest fails closed; training receives an explicit unaugmented validation set; model selection has no test-data dependency; evaluation rejects absent/contradictory freeze records and never ranks by test accuracy.
- Run the targeted test suite and then the complete training-side test suite. Perform a lightweight real-data dry run of manifest/partition/augmentation (without launching a full model retrain), check split counts and source overlap, and verify prior files are untouched. Full retraining and external evaluation are distinct tasks requiring compute/data, and cannot be claimed merely because pipeline tests pass.

## Out of scope

No signer identity assertion without evidence; no invented unseen test set; no automatic model deployment; no field-device benchmark, app UI change, new FSL clip capture, or change to the existing 50-class selection.
