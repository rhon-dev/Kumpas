# A2a R1 review fix — incremental evidence

Status: in progress; parent re-review required, no acceptance claim.

Read binding review-fix brief, original task brief, full independent review (including exact R1/B1 probes), current repository/observer and three scoped tests, runner and git status. Loaded study-readiness and TDD skills. Existing unrelated changes are preserved. Source ownership is restricted to the two Dart session files and three existing session test files; native/export frozen.

## Regression synchronization

The two-observer test preserves reviewer ordering: old screen enters/resumes, dispose dispatches native end, replacement enters/resumes before end reply, release reply, drain. Unlike the exact probe, capture rather than await replacement resume before releasing the blocked old end: a correct shared coordinator may legitimately wait for that prerequisite. Native state changes occur at command dispatch, not reply delivery. Finite withheld replies only.

## Execution ledger

Exact runner records are appended to existing command-ledger.jsonl/report.md by the unchanged runner; fix-specific copies and verification records are retained in review-fix-1-ledger.jsonl. New labels/logs only. Prior reviewer report remains untouched.

- Actual RED: `review-fix-1-red-handoff`, exit 1, one behavioral failure: commands lacked replacement start after finite end reply. Production unchanged at RED. Exact command/log in fix ledger. Initial ledger filter met older records without label (KeyError); corrected to optional-key filter, no source effect.

- GREEN handoff: exit 0, 1/1; shared repository queue now coordinates actual observer reconciliation turns across screen lifetimes, without serializing arbitrary direct repository callers.

- Actual second RED: `review-fix-1-red-end-failure`, exit 1, both before-effect and after-effect error cases fail missing replacement start. Queue releases on error, but cached uncertain end identity is still adoptable; next minimal change marks that identity unavailable for adoption while retaining existing retry cache/ownership behavior.

- GREEN failure slice: exit 0, 2/2, both native-effect/error positions. Ending identity remains cached for same-observer retry but is non-adoptable; successful latest start/sync/end or clear resets marker under existing fences. No extra unscoped cleanup command added. One ambiguous patch was atomically refused; reapplied with unique context.

- Focused GREEN: 40/40, exit 0, including new departure/reentry and successful/partial-failed clear handoffs plus B1 characterization (coverage-only GREEN, no invented RED). Full Flutter: 75/75, exit 0. Analysis first run exit 1 for one informational unnecessary_underscores lint in new error callback; preserving log and correcting parameter spelling before final reruns.

- Final reruns after lint-only correction: analysis exit 0 (no issues), full Flutter exit 0 (75/75). Protected comparison: all 82 match expected digests, zero mismatches; git diff --check exit 0. Exact digest map saved in review-fix-1-verification.json. No JVM rerun: native/export sources frozen; earlier JVM evidence is prior evidence only.

## Final handoff (not acceptance)

Status: DONE_WITH_CONCERNS; implementation and requested host checks returned, awaiting parent independent verification/specification and quality re-review.

### Mechanism and preserved boundary

Repository owns the shared observer reconciliation tail, so a replacement screen cannot adopt or start while the old observer's end is awaiting a reply. Every queued turn re-reads current screen intent. Errors release the queue instead of poisoning later screens. The ending-ID marker survives an end failure because native effect may already have happened; a replacement starts a new session instead of adopting an uncertain one. The old cached ID remains available for existing same-observer retry, and existing identity comparison prevents an obsolete screen from ending a committed replacement. Existing clear epoch/command guards still fence all marker/cache commits; no public method signature changed and no additional unscoped end was introduced.

Only actual lifecycle observer operations join this queue. B1 is deliberately characterized as still non-atomic for arbitrary external direct repository callers: native end remains unscoped, and cache equality is not native identity atomicity. Such a concurrent external start caller is not present in the reviewed production caller graph. Permanent reply loss has no new deadline and can now stall the shared observer queue; this is an explicit excluded case, not finite-reply R1 recovery. Fresh-screen lifecycle seeding, concurrent clears/transport reorder, native timeout failure, installed integration, phone measurements and broader host/study acceptance remain unproved/out of scope.

### New tests and evidence

Eight new tests: finite-success two-screen handoff (genuine RED then GREEN); end failure before/after native effect (two genuine RED then GREEN cases, obsolete-owner retry and replacement departure); replacement departure/reentry while old end pending; success/partial-failed clear during handoff; B1 characterization. Last five are coverage-only GREEN, not claimed new RED. Existing same-observer end retry, clear/order tests and full receipt/metadata tests passed unchanged.

Focused: 40 passed. Final full Flutter: 75 passed. Final analysis: no issues. All commands use --no-pub and unchanged locked host runner; unique logs preserve both behavioral RED runs and first analyzer info failure. No dependency installation, JVM execution, emulator/phone/ADB/default-store operation or commit. Native timeout/export behavior has not been freshly re-executed here. All 82 protected hashes match; reviewed SessionManager source/test, DataExporterTest and unchanged session_clear/repository_race tests match parent frozen hashes.

### Exact task changes

Source/test changed: `app/lib/session/session_repository.dart`, `app/lib/session/session_lifecycle.dart`, `app/test/session_lifecycle_race_test.dart`. No other repository source/test was changed by this fix.

Evidence created under a2a: `review-fix-1-report.md`, `review-fix-1-ledger.jsonl`, `review-fix-1-verification.json`, and unique `review-fix-1-*.log` files. Unchanged runner appended its exact execution records to existing `command-ledger.jsonl` and `report.md`; existing content/logs and reviewer report were not replaced. Current default-profile study-readiness skill gained the general two-observer regression/synchronization lesson (outside repository).
