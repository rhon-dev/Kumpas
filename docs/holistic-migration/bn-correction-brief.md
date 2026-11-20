# Phase 4 bounded BatchNorm correction and fresh tiny proof

AGENT: Model/Training implementation, independent specification/quality review, then parent actual-source execution.
PHASE: Holistic Migration Phase4 continuation, not phone/export work.
OBJECTIVE: Correct the diagnosed tiny-run BatchNorm moving-statistic mismatch without weakening the gate; preserve ordinary inference and prove a new saved/reloaded actual-source tiny candidate.

## Authority

After the completed fit-only diagnosis, the owner said **`continue task\n/caveman`**. This resumes the proposed bounded fit-only BatchNorm-statistics correction/experiment and genuine tiny proof. The owner explicitly requires **8/8 correct AND mean crossentropy <=0.1**, unchanged. This is not permission to relabel, merge classes, lengthen300 optimizer epochs, deploy training-mode inference, change architecture/features/data/labels or silently proceed through a failed prerequisite.

The implementer prepares/tests software using synthetic inputs only. Independent complete affected-scope review and parent verification precede a new real-source tiny invocation. Parent owns real-data operations and acceptance. This package stops at the verified new tiny proof or its retained failure; all-50 fitting/test scoring are not worker-authorized and must not be launched by this package. Historical overall Phase4 scope remains documented separately.

## Inputs and preserved baselines

Repository `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`, branch `holistic-migration`, current HEAD `3b1f1d8efa29d1e717833f3869c77872e4df021c`.

External root `../holistic-migration-data/evidence/phase-4-20261116/`:
- `DIAGNOSIS_SUMMARY.md`, `diagnosis-parent-verification.json`.
- `diagnosis-mode/diagnose.py`, `native_control.py`, results and report: fixed learned weights distinguish the exact eight fit tensors when only BatchNorm moment sources change. Ordinary stored-statistic inference still fails7/8,CE1.1409778411001894; diagnostic batch-dependent8/8 is NOT a qualifying proof.
- `software-acceptance.json`, `software-review-v1/manifest.json` and original worker source snapshots bind accepted pre-correction tooling.
- `tiny-source-v1/` failed checkpoint SHA-256 `9322911fd1565f2ca895c8f6f2af63a8346661493587dce74ea41561cdc75686` must remain unchanged. No original proof exists.
- `face-training-admission-v1.json` and accepted hm1588 bundle remain unchanged.
- `bn-correction-v1/baseline.json` and `before/` retain exact current preimages.

Existing interpreter `~/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python`; no installs. Use approved scratch TMPDIR and CPU/one-thread environment from FACE_TRAINING.md. Available free disk about3.17GB, host8GiB RAM.

## Exact bounded correction

Add a generic, tested native helper `batchnorm_calibration.py` and integrate it into **tiny fitting only**. Do not alter full fitting/callback/augmentation/validation selection semantics or introduce full-model normalization changes here.

Predeclared policy `tiny_fit_layerwise_exact_moments_v1`:
1. A new actual tiny run trains from the same fresh seeded CNN-LSTM construction on the same eight literal-first eligible fit sources, same50 outputs, no augmentation, at most300 full-batch optimizer epochs. No warm start from failed weights. Preserve existing early-success behavior, then apply the same one-time calibration policy before final save/gate for every native tiny result.
2. With optimizer and trainable parameters held fixed, use only these exact eight fit tensors to estimate finite channel-wise population mean/variance for each BatchNorm input across batch/time axes. Process normalization layers in graph order: freeze the first layer's new moving statistics before measuring the next layer's inputs. All layer forwards use ordinary inference, with Dropout disabled. No additional optimizer step, label feedback, validation/test data, augmentation, threshold search or architecture change is permitted.
3. Assign only BatchNorm moving_mean/moving_variance. Keep gamma/beta, every trainable parameter, optimizer variables/iterations and layer configuration unchanged. Validate input/model/family, finite values and nonnegative variance. On failure, restore all attempt-owned state changes and retain the original exception. Native helper must not leave partial calibration treated as success.
4. Preserve the exact pre/post statistics, selected-input identity, algorithm/version/source binding, finite checks and unchanged optimizer/trainable-state receipts in a hash-bound `batchnorm-calibration.json`. The producer and actual `_verify_tiny` consumer must verify this receipt and its relationship to the saved candidate. A successful receipt or batch-mode score alone cannot qualify anything.
5. Save a fresh candidate/checkpoint; reload it and score with `training=False`. Verify predictions are invariant to single-example vs eight-example inference within the already declared Float32 tolerance. Only actual8/8 and meanCE<=0.1 can publish a new qualifying tiny proof. The proof must bind new trainer/helper/protocol/configuration, calibration receipt, exact original fit tensors/labels/IDs, saved model/probabilities/history and actual optimizer steps. Record pre-calibration failure separately from final calibrated ordinary-inference evidence; do not rewrite history as if the optimizer alone produced calibrated metrics.
6. Full entry and separate evaluator must fail closed on missing/stale/tampered/calibration-protocol-incompatible tiny artifacts. Retain all prior failure/publication protections. Do not stamp current identity onto old proofs or edit historical acceptance, failed-run bytes or source-bound reports. If the new source invalidates historical identities, retain original snapshots/receipt interpretation rather than claiming old artifacts were produced by new code.
7. Explicit synthetic lifecycle backends may remain protocol fixtures, but any calibration no-op/unsupported-native behavior must be explicitly labeled synthetic-only and cannot qualify real provenance. Native synthetic tests must exercise actual calibration and ordinary saved/reloaded predictions; do not fabricate native success or hide unsupported native models behind dummy receipts.

## Required verification

Strict vertical TDD: observe intended behavioral RED before implementation for each new behavior; already-green assertions are coverage-only. Include:
- Small independently calculated deterministic channel moments and sequential second-layer dependency.
- Dropout remains disabled, only moving moments change, all trainables/optimizer/configuration unchanged, no optimizer update, inference batch-independence after save/reload.
- Failure/nonfinite/model/input guards and rollback, no partial successful receipt/proof.
- Tiny producer/proof consumer binding, missing/tampered/stale receipt denial and unchanged exact8/8/CE/max300 criteria.
- Existing tiny/full/evaluation lifecycle, failure-phase/publication and no-test-content controls continue passing. Preserve existing test definitions/coverage; do not delete or weaken them.
- Full affected/migration/original training suites with current-source-bound logs/XML and disclosed warnings. Use focused tests per slice, broad suites only once at final revision. Keep a retained evidence budget200MiB; temporary owned pytest fixtures may be cleaned only after retaining command/log/XML/source identities and small native control artifacts. Do not delete unrelated scratch or old evidence. Do not recursively copy historical campaigns/evidence.

## Ownership

WRITE SET ONLY:
- NEW `training/holistic_migration/batchnorm_calibration.py`
- NEW `training/holistic_migration/tests/test_batchnorm_calibration.py`
- MODIFY `training/holistic_migration/face_train.py`
- MODIFY `training/holistic_migration/tests/test_face_train.py`
- MODIFY `training/holistic_migration/FACE_TRAINING.md`
- NEW `docs/holistic-migration/bn-correction-report.md`

The evaluator code/tests are protected unless a concrete consumer-boundary necessity is reported and parent explicitly expands ownership. Existing source binding and call to actual `_verify_tiny` may suffice without evaluator edits; inspect, do not assume. All historical producer/shared feature/data/model/app files remain protected. Parent alone owns authority/brief/baseline/status/admission/actual-source outputs and final acceptance. Never modify `.git`, installed environments/provider/model configuration, SDKs or other worktrees. No camera/phone/media/extraction/export/activation/participant/Git/paid operation.

OUTPUT: incremental report in `docs/holistic-migration/bn-correction-report.md`; focused new command/log/XML/source manifests below external `bn-correction-v1/worker/`. Return concise DONE/DONE_WITH_CONCERNS/BLOCKED, exact manifest/report paths, test counts and concerns. Independent specification/quality review is mandatory before the parent actual run. No acceptance by implementer, no commits.
