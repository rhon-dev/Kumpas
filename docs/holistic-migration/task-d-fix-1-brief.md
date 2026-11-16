# Task D bounded repair 1 — D-R1-001

## Authority and scope

Repair only the completed independent Task D rejection `task-d-review-1.json`, finding D-R1-001. This is the first bounded D repair/reverification cycle, not acceptance or real-data fitting authority. Original `task-d-brief.md` remains controlling; preserve its exact architecture, data boundaries, provenance and output semantics.

Only editable repository paths:
- `training/holistic_migration/evaluate.py`
- `training/holistic_migration/tests/test_evaluate.py`
- `docs/holistic-migration/task-d-report.md` (append-only)

No other source/test/document edits. In particular train.py, augmentation, TRAINING.md, existing tests, A/B/C sources and all historical assets/receipts remain unchanged. No installs, provider/model changes, camera/GUI/phone, source-data writes, actual-source arrays/model access, classifier fitting/inference/evaluation, participant stores, commits or pushes. The independent campaign evidence reviewer may run concurrently: C's explicit immutable source contract excludes these D additions; preserve every protected input.

## Verified starting candidate and defect

Parent read the complete8-path independent review, matched all69 input hashes,8 owned postimages and36 protected bindings. Review SHA-256: `b4d2c103ac392233977c54bcecc191ab33b290b14556f1162b96b2b00b82f1b3`. Both verdicts REJECT.

`evaluate.py:142-146` publishes `evaluation-complete.json`, then final `_evaluation_readback` can fail. The handler retains that new success marker and writes failure.json. An existing-target call can subsequently report successful completion after a transient read failure clears. This violates the explicit no-success-on-final-readback-failure contract, even though it does not repeat inference.

Parent reproduced the actual intended fault with only synthetic fixtures:1 failed assertion,0 errors/skips, exit1 after post-publication injection. Canonical retained regression bytes SHA-256 `f2c3e1f252c02fd5564046bdab3aff38090c9491f5d8f45c0457d7a5cef33539`.

Evidence root `../holistic-migration-data/evidence/task-d-before-fix1-20261114/` contains:
- `snapshot-index.json`: original path/preimage path/size/SHA mappings for all8 owned additions plus immutable review1;
- `repair-protection.json`: editable paths, absolute protected hash map and old report-prefix snapshot;
- `test_parent_final_readback.py`, `parent-red.command.json`, `parent-red.log`, `parent-red.xml` and fresh synthetic `red-fixtures/`.

No source was changed during reproduction. Parent pre-repair full suites passed360 migration+293subtests/67warnings,51 original+289subtests/3warnings, but do not cover this fault and are not acceptance. Preserve their identities; create fresh corrected evidence.

## Required bounded behavior

Make newly reserved evaluation publication/final readback fail closed. On a failure after publication, invalidate only the new completion marker owned by this attempt; retain its start, saved predictions/IDs/report/pending/failure evidence and preserve the preexisting frozen model selection exactly. A failed/incomplete exact target must never silently become gating or perform another test hash/load/inference on retry. Keep healthy completed-target retry readback-only. Do not delete or rewrite previously established completed evaluations merely because a later readback call encounters a transient read error. Preserve the primary failure rather than replacing it with diagnostic-writing errors where feasible within this bounded path.

Permanently retain substantive coverage of the review fault and subsequent exact-target denial. Assert the injection occurred after completion publication before claiming product RED. Verify marker absence/non-gating disposition, saved evidence, frozen selection identity and no repeated test access/backend load. Cover healthy controls and existing incomplete/pre-publication failure behavior. Keep trusted in-process fixtures explicitly synthetic; no fabricated source_video receipts. Do not loosen validators, hide warnings or weaken the existing reporter tests.

Use strict vertical TDD: append recovery entry first; land one behavioral test and run RED before its minimal production change; run GREEN immediately. Subsequent variants that already pass are coverage-only GREEN. The review's nonblocking rising-validation-then-tie suggestion remains explicitly deferred to final review; test_train.py is not editable in this repair. Preserve synthetic/real caveats unchanged.

## Execution and handoff

Use `~/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B`, approved scratch TMPDIR, `-p no:cacheprovider`, deterministic CPU/thread limits. Run new owned regressions, retained original parent regression, full `test_evaluate.py`, all three D test modules, complete migration pytest and original training pytest. Record actual command/exits/cases/subtests/warnings separately; do not assume counts. No pyc/cache or historical defaults.

Before writes verify repair-protection.json exactly and the historical report prefix against its snapshot. Preserve every preimage and old receipt; append report commands/exits/results immediately after each tracer. Fresh exclusive external evidence only; retain actual synthetic fixtures when needed for independent readback. Handoff must bind the exact3 changed postimages, all unchanged/protected inputs, report prefix, every executed receipt and raw log/XML, source/runtime/C-contract identities and limitations. Parent must verify and obtain full affected-file re-review before acceptance. Return paths/hashes/results, not approval.
