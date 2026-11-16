# Task D bounded repair 2 — D-R2-001

## Scope and repair budget

This is the second and final automatic Task D repair/reverification cycle under the existing review workflow. It addresses the sole blocker in complete `task-d-review-2.json` (SHA-256 `5a2deb33961787c6bed3611d2fefeb88f0bae81c2107a322c1aaebeac75fb3be`): D-R2-001. Both specification and quality verdicts reject. D-R1-001 is resolved for its original failed-target promotion mechanism and must remain resolved. Transport interruptions were not additional repair cycles. If a complete subsequent re-review still has blocking findings, stop for the owner's decision; do not start a third automatic fix.

Only editable repository paths:
- `training/holistic_migration/evaluate.py`
- `training/holistic_migration/tests/test_evaluate.py`
- `docs/holistic-migration/task-d-report.md`, append-only

All other source/tests/docs and historical evidence remain unchanged. In particular, `dataset.py` and its publisher are protected; changing them would change the accepted C contract. Do not alter train.py, augmentation, model architecture, class map, TRAINING.md, package initialization or runtime dependencies. No actual-source arrays/model access, real optimizer/inference/evaluation, extraction/SDK/video/camera/GUI/phone/participant operations, installs/provider/model/config changes, commits or pushes. Explicit synthetic fixtures and existing venv only.

## Verified starting authority

Parent independently read and adjudicated complete8-path/19-requirement/8-interface review2, matched all143 input hashes and the fixed candidate. Source/evidence freeze and mappings are under `../holistic-migration-data/evidence/task-d-before-fix2-20261114/`:
- `parent-review2-adjudication.json`
- `snapshot-index.json`: exact8 current owned postimages plus final review2
- `repair-protection.json`: exact3 editable paths,49 protected paths, current8 hashes and report-prefix snapshot
- `test_retained_publication_cleanup.py`: original behavioral regression bytes, SHA-256 `ef1c1c1977df2fdb40d771ef8579620456445f49ccaaf57137f0bbb0905ab589`

Current report prefix is **114,202 bytes**, SHA-256 `487a9a49f58d91c8c9b5f08fa8b7b2eebe5f98e1baf63feb14b5322b7a15c281`. Preserve the entire prefix, including repair1 history, not only the older77,458-byte prefix. Current evaluator SHA-256 `67e42ac9ff6bcbc83488ac70663652e8a9bb847ee4dadfe2942be277a7df0fcf`. Full candidate package and original requirements remain in `evidence/task-d-fix1-parent-20261114/` and `task-d-brief.md`.

Separate real dataset evidence is already parent-accepted; this does not waive D acceptance or real tiny-proof gates. Parent copied/protected canonical manifests/admission and campaign acceptance. No real tiny proof or fitted FSL candidate exists from this task.

## Actual defect and required behavior

At completion publication, protected dataset.publish_json links the final marker, then performs readback. If that readback raises the primary OSError and its cleanup unlink also raises PermissionError, the helper propagates the secondary exception before evaluate.py sets completion_published. The evaluator currently raises and records that secondary error. Both reviewer and independent parent reached this exact fault with synthetic fixtures:1 behavioral failure/0errors; retry stays denied, frozen selection preserved. This is error precedence, not renewed retry promotion.

Preserve the exact original publication/readback exception object through that actual ownership boundary and record the original failure rather than cleanup as the main error. Handle the owned evaluator publication boundary without modifying protected C code or globally monkeypatching its functions. Do not blanket-unwrap arbitrary exception.__context__, because a genuine primary can have an unrelated prior context. A minimal evaluator-owned publication primitive or other inspected composition is permitted inside evaluate.py; preserve exclusive staged publication/readback and pending evidence semantics. Do not create a new general framework or module.

Retain meaningful permanent combined-fault regression coverage. Observe behavioral RED before the corresponding production change, then immediate GREEN. Verify injection after link/pending creation, exact primary identity, correct failure record, retained diagnostics/predictions/start, unchanged frozen selection, retry denial with no test/backend access, and no marker overwrite or deletion of another/preexisting established completion. If sharing the new primitive with report publication, test the relevant shared behavior without expanding scope. Preserve all existing repair1 controls, including ordinary cleanup/failure-write faults and transient read failures on established completed evaluations. Preserve explicit simultaneous permanent persistence/hostile-writer/crash limits rather than claiming universal durability.

## Execution and handoff

Before editing, verify all49 protection hashes,9 snapshots and the114,202-byte report prefix; append a recovery/repair2 entry first. Follow strict vertical TDD. Label already-passing variants coverage-only GREEN. Do not edit old RED/GREEN receipts or silently rebind old proofs to new evaluator source; D source hashes are part of proof identity.

Use `~/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B`, approved scratch TMPDIR, deterministic CPU/thread limits and `-p no:cacheprovider`. Run new regressions, retained D-R2 parent regression, retained D-R1 parent regression, complete evaluator tests, all D modules, full migration and original training pytest suites. Parse actual cases/subtests/warnings/XML separately. Keep original67/3 upstream warnings visible; do not install or suppress them. Use fresh exclusive external evidence and preserve meaningful synthetic checkpoints/receipts; avoid unnecessary duplicate fixture archives. No source pyc/cache.

Append actual command, exit and evidence immediately after each tracer. Final handoff must bind exactly3 changed postimages, all protected/unchanged hashes, report prefix, current source/runtime/C identity, executed stage/final receipts/logs/XML, preserved snapshots and limitations. Retain all old evidence unchanged. Parent verification and complete affected-scope independent re-review remain mandatory; worker grants no acceptance or real-data authority. Return only exact handoff path/hash, changed paths, real executed results and concerns.
