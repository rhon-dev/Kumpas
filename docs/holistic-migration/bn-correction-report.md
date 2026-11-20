# Bounded tiny BatchNorm correction — worker report

Status: **DONE_WITH_CONCERNS — synthetic software verified; independent review and actual-source proof pending.** No phase acceptance or actual-source invocation.

## Scope and policy

Six-path brief honored. Added the versioned native `tiny_fit_layerwise_exact_moments_v1` helper and tests; modified only face trainer/tests and its protocol documentation. Full fit/evaluator implementations remain unchanged. The evaluator's new-target path already calls the actual trainer `_verify_tiny` before reserving output or accessing test content; focused rebinding tests exercise that path without evaluator edits. Existing completed-target readback policy is unchanged.

Tiny still builds fresh with seed20260705,50 outputs, original topology and≤300 full-batch optimizer epochs; early success remains8/8 AND meanCE≤0.1. Every native result then receives the same one-time label-free layerwise population-moment correction on its exact selected fit X. All forwards are ordinary inference; Dropout stays disabled. Only BN moving mean/variance change. Frozen weights/optimizer/configuration and exact pre/post statistics are receipted; exceptions restore snapshotted variables and preserve the primary error. No warm start or real-source fixture access.

A separate pre-calibration probability artifact and receipt retain optimizer-only final metrics; optimizer history is never rewritten. Final saved/reloaded ordinary probabilities and singleton/eight-example invariance are required before publishing the unchanged gate. Producer and actual consumer bind receipt protocol, source, selected tensors/IDs, checkpoint, probabilities, history and optimizer steps; native receipt verification recomputes each layer's input moments read-only. Unsupported native models cannot receive synthetic no-op receipts. Explicit lifecycle fixtures remain synthetic-only.

## Strict vertical TDD evidence

External evidence root: `../holistic-migration-data/evidence/phase-4-20261116/bn-correction-v1/worker/`.

Each command has exact arguments/environment, return code, source hashes and per-command snapshots, log and JUnit XML. Observed behavioral RED/GREEN slices:

- `01`→`02`: missing helper to independent scalar population-moment oracle, sequential second-BN dependency, disabled Dropout, frozen trainables/Adam/config and save/reload batch independence.
- `03`/corrected `04`→`05`: rollback and finite/input/model guards. `03` exposed two test-harness defects (uncompiled Functional fixture and Keras-wrapped exception identity); `04` corrected the harness before implementation and observed intended rollback/family RED. One dimension guard was already-green coverage.
- `06`→`09`: native and explicit synthetic-only tiny producer receipt, pre-history separation and checkpoint/source/input binding.
- `07`→`08`: native saved/reloaded receipt consumer.
- `10`→`11`: exact schema/order, invalid pre-moments, and recomputed-moment denial even when checkpoint/receipt post-moments are rebound. Six other mutations were already-green coverage.
- `12`→`13`: actual tiny/full prerequisite consumer rejects rebound calibration source/protocol/selection/checkpoint/steps/pre-evidence/kind/schema and batch dependence. Missing/tampered-byte controls were already-green.
- `15`→`16`: shared-layer family rejection; four other native-family variants were already-green coverage.
- `14`: additional coverage-only actual native positive optimizer/control, unchanged CE/300 gates, no partial success and unchanged separate evaluator consumer-before-test-access.

The synthetic positive exact-family native control achieved8/8, meanCE0.012166036565517839,81 optimizer epochs/steps, including the actual `_verify_tiny` consumer. This is synthetic-only software evidence, never a real tiny proof. Native one-epoch nonseparable synthetic controls still fail the final gate and retain failure/checkpoint evidence.

## Resource and preservation boundary

No installs, environment configuration edits, Git operations, media/dataset operations or parent status/admission writes. Tests use the existing interpreter and per-command CPU/one-thread environment. Only fresh owned pytest fixture roots may be cleaned after source/command/log/XML and critical small native artifacts are retained. The external bounded pytest wrapper leaves every existing test definition intact, finalizes fixtures, then removes only each owned per-test temp directory; session fixtures survive until suite completion. Retained evidence budget≤200MiB.

## Final verification

One final broad invocation at the final code/test revision ran the complete `training/holistic_migration/tests` and `training/tests` suites: **790 passed,582 subtests passed,221 warnings**, no failures/errors/skips. JUnit has1372 testcases (790+582). Runtime194.41s. Command/log/XML: `17-final-migration-and-original-command.json`, `.log`, `.xml` under the worker root. No broad-suite rerun. The existing synthetic export regression tests were included in the required original suite; no product/real checkpoint export or activation occurred.

Warnings remain disclosed:220 Keras/NumPy `__array__(copy=...)` deprecations, plus one existing TensorFlow Lite Interpreter deprecation from the original frozen-export synthetic test. Added native controls increase occurrences of the existing Keras warning; no new warning category in final verification. The exploratory negative runs' warnings remain in their own logs, including intentional nonfinite/empty guards before their fix. Editor Pyright used an unrelated environment and reported missing pytest/imports; real verification used the approved installed interpreter and passed.

The final current-source native positive control independently retained a **healthy, unmodified** proof/checkpoint/receipt copy in `native-controls/bn-worker-17-final-migration-and-original/test_native_positive_synthetic0/native-positive-original/`. Its original optimizer-only ordinary-inference result was8/8,CE0.09940986816036765 at81 epochs/steps; calibrated saved/reloaded ordinary inference was8/8,CE0.012166036565517839. All proof file hashes were rechecked. The adjacent `native-positive/` directory is an intentional rebound-receipt denial fixture, **not healthy evidence**; earlier retained mutation fixtures are likewise not qualifying artifacts. Other final controls retain genuine failing native results, helper-oracle models and unchanged protocol-fixture evidence. No real-source learning result is claimed.

`verification.json` checks all1802 protected baseline hashes unchanged, all8 exact existing preimages either authorized-edited or protected unchanged, and every historical failed-run artifact unchanged (including model/candidate SHA-256 `9322911fd1565f2ca895c8f6f2af63a8346661493587dce74ea41561cdc75686`). Every existing face-training test/helper/class AST definition remains unchanged; new tests are additive. Existing trainer changes are limited to `source_binding`, `_execute` tiny path and `_verify_tiny`; the model builder, TensorFlow backend, `_full_execute`, callback, admission, and failure/publication helpers are unchanged. FAMILY/POLICY/SEED AST values are unchanged. The evaluator file/tests are untouched.

Final artifact index: **`worker/manifest.json`**, with owned source hashes/current snapshots, suite/dependency input hashes, exact brief/baseline bindings, command/log/XML hashes, retained native control hashes, preservation receipts and evidence-size accounting. The final report is documentation-only completion after the broad command; all tested code/test hashes remain identical to the final suite's snapshots. Owned temporary test fixtures were cleaned only after retaining logs/XML/source/critical small native controls; no unrelated scratch or historical evidence was deleted.

## Remaining concerns / required parent action

- No actual-source calibrated tiny run has been performed; real success is unknown. The exact8/8 AND CE≤0.1 gate,≤300 optimizer epochs and eight original literal-first eligible fit inputs remain mandatory. Calibration may still fail on real data.
- Independent complete specification/quality review and parent current-source verification are mandatory before the new actual-source tiny invocation. No worker phase acceptance, parent status/admission changes or full50/evaluation run on real data.
- Current source identity intentionally invalidates old tooling proofs/selections. Keep original historical snapshots/interpretation and failed-run bytes; do not restamp/relabel them. The docs show a proposed fresh parent tiny path, not an execution authorization.
- Full fitting deliberately remains uncalibrated and unchanged. Separate new evaluations still call the actual strict tiny consumer before test access. Existing completed-evaluation readback-only behavior is preserved; this package does not broaden its semantics.
- Filesystem publication/rollback has the same bounded local guarantees as prior tooling. Native rollback attempts every snapshotted variable and attaches restoration errors to the original exception; it cannot promise successful restoration under simultaneous low-level assignment failure, and it never publishes a successful receipt/proof after such failure.

## Automatic repair 1 — BN-REVIEW-001 (2026-11-16)

**DONE_WITH_CONCERNS — synthetic repair verified; renewed independent review and parent verification required. No acceptance or actual-source tiny invocation.** This append supersedes the earlier report's implication that all native pre-state/history relationships were already verified. The original 9,296 report bytes remain unchanged, SHA-256 `80bbdd5a072c6930761c2b0f0374bb34711801d49a98c291bc6171a016ba3707`; the rejected review, earlier evidence and historical failed run remain historical.

### Repair and bounded semantics

Added `batchnorm_calibration.verify_precalibration`. It first checks the existing complete native receipt/post-state/frozen-weight/source/input relationship, then creates an isolated native clone with the final unchanged nonmoment weights. Only that clone receives the recorded pre-mean/pre-variance values. Ordinary `training=False` replay must reproduce retained pre-calibration probabilities at the existing Float32 `rtol=1e-6, atol=1e-7`. The actual producer calls this before publishing its calibration receipt; the actual `_verify_tiny` consumer calls it through `_verify_calibration`, whose separate digest/metric/history/step checks remain intact. Thus the native pre-state and optimizer-only final history are now connected through the same retained probability artifact.

The calibrated candidate never receives pre-moments and is not recompiled or optimized. A `finally` check binds every candidate variable (including Dropout RNG, all model weights and optimizer slots/iterations) and model/compile/optimizer configuration across success and failure. Model family, calibration algorithm/protocol, original eight-input selection, labels, all 50 outputs, optimizer budget/early stop and **8/8 AND mean CE≤0.1 / max300** remain unchanged. There is no extra optimizer step, training-mode inference or real-data operation in the repair. Full-fit, evaluator, admission, publication/failure and existing helper definitions are unchanged. This repairs audit consistency, not an asserted hostile-writer authenticity boundary.

### Observed RED → GREEN and supporting coverage

Fresh evidence root: `../holistic-migration-data/evidence/phase-4-20261116/bn-correction-v1/fix1-worker/`.

- `01-consumer-red`: **two intended behavioral failures** before production edits. Fresh current-source native exact-family training generated healthy proofs accepted by the actual consumer. Independent ordinary-inference pre-state replay matched saved pre-probabilities; finite first-BN pre-mean and positive pre-variance mutations broke that relationship while preserving checkpoint, probability, history, selected-input and current-source identities. Rebinding only the receipt/proof digest still reached consumer acceptance (`DID NOT RAISE`), reproducing BN-REVIEW-001 rather than stale-source rejection.
- `02-consumer-green`: the same two regressions passed after the coherent producer/consumer repair. Each requires the intended replay mismatch, then tests actual tiny rejection, rejection **before full output reservation**, and the unmodified separate evaluator's rejection **before a new evaluation target/test access**. Full-selection setup is explicitly a symbolic synthetic lifecycle fixture, not a native full fit or validation-selected learning result.
- `03-supporting-coverage` → corrected `04-supporting-coverage-green`: **10 coverage-only controls passed**, including healthy saved/reloaded replay, finite mutations, shape/nonfinite expected probabilities, clone/assignment/inference faults, complete calibrated-model/optimizer/configuration preservation, and producer denial before receipt/proof publication. The first run had one harness assertion error: native Keras wraps a `Sequential.__call__` inference exception, so object identity is not preserved at that native boundary. The corrected test checks its diagnostic and candidate preservation; clone/assignment and calibration rollback still assert primary identity. No production change was made for this harness issue, and it is not counted as product RED.
- Review suggestion S002 is covered by an already-green additive control: a secondary rollback assignment failure attaches a note to the original primary exception, while every later snapshot restoration is attempted and verified. It does not claim restoration must succeed under low-level assignment failure.

All pre-existing test bytes are preserved verbatim as prefixes; no earlier test/helper/class definition was changed or removed. The final code/test revision includes 12 additional collected cases over the rejected package.

### Complete synthetic re-verification

- `05-current-affected`: current helper + trainer + protected evaluator tests: **136 passed, 305 warnings**, no failures/errors/skips; 126.00s.
- `06-final-migration-and-original`: complete migration and original training suites, **once at the final code/test revision**: **802 passed, 582 subtests passed, 375 warnings**, no failures/errors/skips; 221.09s. JUnit serializes **802 `<testcase>` elements**; its suite counter is **1,384 assertion events**, comprising those parent cases plus the 582 subtests. Exact commands/environment, source snapshots, logs and XML are retained.
- S001 erratum for the immutable earlier report: its 790 collected/serialized parent cases plus 582 subtests explain the 1,372 suite-counter events. The earlier phrase “JUnit has1372 testcases” was imprecise; it did not mean 1,372 serialized `<testcase>` elements.
- Warnings remain the existing Keras/NumPy `__array__(copy=...)` deprecation and the original synthetic frozen-export test's TensorFlow Lite Interpreter deprecation; no new warning category. Increased Keras occurrences reflect additional native controls. Required original-suite synthetic export regressions are not product/real-checkpoint export operations.
- Final-suite healthy native controls again obtained **8/8, calibrated CE0.012166036565517839, 81 optimizer epochs/steps**, with pre-calibration CE0.09940986816036765. Healthy copies live under `native-controls/bn-worker-fix1-06-final-migration-and-original/test_native_replay_denies_fini{0,1}/native-replay-original/`; adjacent `native-replay/` artifacts are intentionally inconsistent rejection fixtures, not healthy proofs.
- A separate **unmocked retained-artifact readback** (`verify_native_controls.py`, `native-readback-command.json`, `native-readback.log`, `native-control-readback.json`) rechecked all healthy/rebound file digests, current-source actual `_verify_tiny`, and independent pre-state reconstruction. Both healthy copies were accepted and replayed bit-for-bit (max difference0). Both rebound copies were denied specifically with `pre-calibration replay probabilities differ`. The pre-mean mismatch was0.9495365023612976; positive pre-variance mismatch6.9141387939453125e-06 exceeded declared tolerance. This readback performed no optimizer/training/full-fit or real-source operation.

### Preservation, artifacts and remaining concerns

`pre-report-verification.json` and final `verification.json` verify all **1,802 protected hashes**, all **228 old worker evidence-file hashes**, all six fix1 preimages and every historical failed-run artifact unchanged. The original report prefix is exact. Relative to fix1 preimages, trainer definition changes are limited to `_execute` and `_verify_calibration`; the generic helper only adds `verify_precalibration`. Protected full-fit/evaluator code/tests, model/backend/callback/failure helpers and all original test definitions remain unchanged. Only the six authorized paths and fresh fix1-worker evidence were written.

`fix1-worker/manifest.json` is the new source/dependency/evidence index; `current-source/`, `protected-interfaces/`, `suite-inputs.json`, `fix1.diff`, per-command receipts and native readback provide exact identities. The final report append postdates testing; tested code/test/documentation hashes otherwise match both final affected and broad receipts. Retention remains below **200MiB** with exact accounting in the manifest. The validated cleanup wrapper was reused on fresh owned paths with additive native-replay artifact retention; `cleanup-final.json` records only this repair's disposable fixture cleanup. No old evidence or unrelated scratch was cleaned.

No actual-source result is known. Parent must re-verify current sources/protections, obtain renewed complete independent specification/quality review, and only then decide the separately owned actual-source tiny invocation. No admission/status edits, real full50 fit, real evaluation, environment/provider/install/Git/device changes, acceptance, or repair-budget reset occurred. This remains automatic repair **1 of at most2** for this package. Existing bounded filesystem/rollback guarantees and the inability to guarantee restoration after a low-level restoration failure remain unchanged.

