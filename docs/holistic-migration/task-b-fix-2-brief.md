# Task B fix2 — preserve primary failures through diagnostic/report I/O

## Queue, scope and repair budget

This is the second bounded B fix-and-reverify cycle after independent Review2. Dispatch only after the active C codec/test-fixture fixer delivers its protected-baseline handoff; its20 protected inputs include B source/tests/report. Do not change those files mid-C-task or run two implementers concurrently. Parent supplies fresh delivered-C protection first.

Work in `~/KumpasBuilds/holistic-migration`, branch `holistic-migration`. Own only:
- `training/holistic_migration/webcam.py`
- `training/holistic_migration/tests/test_webcam.py`
- Append-only `docs/holistic-migration/task-b-report.md`.

Preserve camera.py/test_camera.py (L01/L02 closed), camera.swift, accepted A, C source/tests/report/contracts, original source/data and historical receipts. No camera/GUI, phone/app, real model/dataset inference, fitting/export, installs, commits/pushes or provider changes. Human webcam check remains explicitly deferred.

## Reviewed finding and parent confirmation

Read full `task-b-review-2.json`, original preview brief and fix1 brief. Review2 independently closes L01/MR01 and L02 by complete source/evidence review; it rejects specification and quality for **L03/MR02**. Optional report write/flush/close can replace an already captured source CaptureError, losing that object and its EOFError cause. Resources otherwise close and native stderr remains; no child leak or false-success finding is asserted.

Parent independently exercised actual run_preview finalization using in-memory source/detector/report fault injections and inert resource/GUI hooks. Actual RED:13tests,7failures,0errors,exit1. Six failures cover report write/flush/close with source or detector primary. All healthy reporting-first-error controls already fail nonzero correctly; no-report-fault controls preserve the original primary.

Parent additionally reproduced the same finalization defect at diagnostic stderr: failing native-tail sys.stderr.write replaces the source primary and bypasses the already-acquired report stream's close. The capture/detector/window close hooks had already run. Treat this as the same bounded secondary-I/O precedence class (L03a), not a real native child leak. Cover it in this repair to avoid preserving the primary for one output sink while losing it at the other.

## Retained exact preimages and RED

Immutable five-source/report/review snapshot:
`~/KumpasBuilds/holistic-migration-data/evidence/task-b-before-fix2-1447c3d21f7e4d5aa834c7a89a64cd47/snapshot-index.json`.

Parent source `parent_report_red.py`, result `parent_report_red.result.json`, complete log `parent-report-red.log` in that same directory. The result is exclusive; copy the script to a fresh external run directory for corrected execution. Its source-only injected test is explicitly not production-pipe/hardware evidence; Review2 separately retained production OwnedCapture pipe probes.

## Required behavior

1. Add owned behavioral tests and execute actual RED before production changes. Exercise source and detector primaries with each serialization/write/flush/close failure, healthy report-only error controls, and diagnostic-stderr failure with a source primary. Preserve meaningful original exception identity/cause and all existing L01/L02 tests.
2. Treat diagnostic/report finalization errors as secondary when a primary already exists. Keep the original exception object/cause as the raised primary; retain secondary stage/type/cause information as attached/chained diagnostics. Do not store arbitrary exception strings in structured operational JSON.
3. If diagnostic/report I/O is the first failure, preserve nonzero failure; never suppress it or claim successful report completion. When multiple reporting operations fail, preserve the first failure and attach later ones.
4. Always attempt report close even after serialization/write/flush or diagnostic-stderr failure, alongside already required capture/detector/window cleanup. Do not falsely mark an unclosed or incompletely written report successful. Preserve partial failed artifacts; do not add auto-retry/overwrite publication.
5. Keep normal quit/Escape/deadline/window-close, source/native exit reconciliation, constructor rollback, owned-child shutdown, cleanup retry and current fixed metadata semantics. Do not refactor unrelated lifecycle or add new capture/recording behavior.

## Verification and handoff

Append recovery status and actual RED/GREEN commands/exits/results to the existing report immediately. Its exact old reviewed bytes are already preserved; keep the prior prefix verbatim.

Run a fresh copy of the parent13-case precedence script, original6-case source/cleanup harness, SourceReconciliationTests, named B tests and full pytest migration/original suites with existing interpreter `-E -B`, scratch TMPDIR and `-p no:cacheprovider`. C function tests require pytest, not unittest discovery. Preserve actual log/artifact/source hashes and separate cases/subtests/warnings. No real camera/GUI or inference is needed.

Check every parent-supplied protected C/A/camera/Swift path before/after and leave tracked original/index diff empty. Return exact changed postimages, actual tests and report path/limits. Parent obtains independent affected webcam/test/report re-review with unchanged camera/native coverage explicitly mapped by hash. If the second fix cycle still leaves blocking findings, preserve the result and report the unresolved gate rather than starting an unlimited third automatic fix wave.
