# Phase 4 — Face-inclusive candidate-model status

## Current disposition

**Offline candidate execution and final handoff are accepted within the approved bounded scope.** Complete independent specification and quality review passed; parent verified all175 consumed inputs,92 manifest inputs and17 package paths before accepting the handoff. Receipt: external `all50-campaign-v1/phase4-offline-acceptance.json`; review: `all50-campaign-v1/final-review/review.json`. This is Holistic Migration Phase 4, model changes and all-gesture retraining, not PRD Phase 4 export/device work. It does not establish calibrated rejection, live recognition, signer-independent generalization, adviser approval or device acceptance.

The owner authorized the complete offline sequence and subsequently requested all remaining Phase 4 tasks. The canonical repository is `~/KumpasBuilds/holistic-migration`, branch `holistic-migration`, HEAD `3b1f1d8efa29d1e717833f3869c77872e4df021c`. Exact authority and preservation bindings are retained in external `evidence/phase-4-20261116/all50-campaign-v1/execution-authority-and-baseline.json`. The interrupted archive/readback check did not rerun training or evaluation; after owner continuation, it completed successfully.

## Executed stages

| Stage | Verified disposition | Evidence under external `evidence/phase-4-20261116/` |
|---|---|---|
| Compatible additive tooling | Accepted after complete specification and quality review; historical code remains protected | `software-acceptance.json`, `bn-correction-v1/software-acceptance.json` |
| Actual-source tiny prerequisite | Passed unchanged 8/8 and mean crossentropy <=0.1 within 300 optimizer epochs; ordinary saved-model reload verified | `bn-correction-v1/tiny-parent-verification.json` |
| Fresh all-50 training | Completed 69 epochs / 2,829 optimizer steps; no tiny-weight warm start or full-model moment calibration | `full-source-v1/{config,history,complete}.json` |
| Validation-only freezing | Earliest maximum validation accuracy at epoch 54; checkpoint contains 2,214 optimizer steps | `full-source-v1/selection.json`, `all50-campaign-v1/full-freeze-parent-verification.json` |
| Independent frozen-artifact review | Specification PASS, quality APPROVED; parent matched 120 consumed-input hashes and all 37 manifest inputs before evaluation | `all50-campaign-v1/freeze-review/review.json`, `freeze-review-acceptance.json` |
| Separate exploratory reused-test scoring | Command exited 0; exclusive start and complete receipts retained; no subsequent tuning or additional inference for reporting | `exploratory-reused-test-v1/`, `exploratory-test-v1/` |
| Parent metrics/report verification | Recomputed all 50 classes from saved probabilities/labels/IDs; verified support, exclusions and complete confusion matrices | `all50-campaign-v1/evaluation-parent-verification.json` |
| Report delivery | 50-row per-gesture CSV, three confusion CSV/SVG pairs, history CSV/SVG, exclusions, summary and report produced; 14-member archive verified | `all50-campaign-v1/reports/`, `phase4-reports.zip` |
| Final handoff review | Specification PASS, quality APPROVED; bounded parent acceptance applied | `all50-campaign-v1/final-review/review.json`, `all50-campaign-v1/phase4-offline-acceptance.json` |

The original failed tiny run remains unchanged: 7/8 correct, mean crossentropy 1.1409778411001894. The approved tiny-only BatchNorm correction produced a fresh qualifying run: 8/8, mean crossentropy 0.00025213306938494064 at 300 optimizer steps. Parent independently verified fit-derived moments, source identities, saved-model inference, singleton/batch parity, and unchanged trainable parameters/optimizer relative to the preserved failed run. This did not lower the tiny criterion, add optimizer steps or alter the full-training procedure. Detailed correction history remains in `bn-correction-v1/` and the pre-closure status snapshot.

## Frozen candidate and results

- Feature contract: hm1588-v1, Float32 `[batch,30,1588]`, all 50 exact approved labels in fixed order.
- Unchanged CNN-LSTM family; fresh full weights, seed `20260705`, max 120 epochs, batch 32, explicit unaugmented validation and early stopping. Exactly one coherent source-seeded rotation per fit original; no validation/test/tiny augmentation.
- Checkpoint: `~/KumpasBuilds/holistic-migration-data/evidence/phase-4-20261116/full-source-v1/model.keras`.
- SHA-256: `ea50489a27353cbf4f4e9b53b1a6252fa7c5c6a9f0021660347f7dcc1b1cda47`.
- Labels, contract, source/runtime/configuration identities and policy are frozen. No candidate ranking, threshold tuning or retraining followed test outcomes.

| Partition | Correct / eligible | Declared | Excluded | Eligible accuracy | Macro-F1 |
|---|---:|---:|---:|---:|---:|
| Fit originals | 644/649 | 663 | 14 | 99.229584% | 0.992267 |
| Validation | 142/145 | 150 | 5 | 97.931034% | 0.977429 |
| Exploratory reused test | 193/203 | 203 | 0 | 95.073892% | 0.949039 |

The overall reused-test numeric accuracy target of >=90% is met. It is not an untouched-holdout, signer-independent or per-gesture live acceptance result. All 50 classes have support. SON and GRANDFATHER each have test recall 2/4; HELLO, YOURE WELCOME, YES, FIVE, YESTERDAY and BLACK each have 3/4. Validation BLUE recall is 1/3 and FOUR is 2/3; minimum validation support is 1. Every error and denominator remains in the reports.

The accepted dataset retains 1,016 declared sources and 997 eligible sequences: 649/663 fit, 145/150 validation and 203/203 test. All 19 `invalid_face` exclusions remain explicit; missing-source outcome bounds are not measured classifier accuracy. Test sources have historical exposure and the result remains `exploratory_reused_test`, `fresh_untouched_holdout=false`, `tuning_allowed=false`.

## Rejection and remaining acceptance limits

The frozen policy is `closed_set_argmax`, `live_ready=false`. Zero scored-positive policy rejections are a consequence of that policy, not a safety measurement. No observed annotated validation negatives exist; rejection calibration, negative count, unknown/idle false acceptance and safe unknown rate are explicitly unmeasured/null. No zero rate or threshold is invented. Actual rejection calibration needs separately approved negative evidence; it is not completed by this offline campaign.

Signer identity, expert linguistic/anatomical validity and live recognition remain unestablished. The separate historical tracking-only session is not candidate recognition or physical acceptance. Phase 5 webcam trials and Phase 6 phone-readiness work were not executed by this authorization. No new camera/recording, phone/SDK, app or detector changes, participant processing, export/activation, paid resources, Git commit/push/merge or deployed-model replacement occurred.

Current-source and 1,802 protected-source hashes, all 13 tiny artifacts and the frozen checkpoint were matched again during closure recovery. Full reports and their original hashes are preserved. Prior mutable status bytes are retained under `all50-campaign-v1/closure-status-preimages/`; immutable historical source, reviews, failures and execution receipts are not rewritten.
