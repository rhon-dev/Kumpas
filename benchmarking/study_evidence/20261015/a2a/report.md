# A2a incremental implementation evidence

Scope: host lifecycle/cache race closure and A1Q1 coverage strengthening only. Existing dirty source preserved. No installed integration or acceptance claim.

Initial inspection: read binding brief first, design/plan and current session production/tests. Existing JDK17 and Flutter located. Behavioral hypotheses remain unconfirmed until actual regression runs below. No source edits yet.
- `timer-red`: exit 1; log `timer-red.log`; exact command in ledger.
- `timer-red-2`: exit 1; log `timer-red-2.log`; exact command in ledger.

Timer RED confirmed: 42 executed, 2 behavioral failures (foreground session closed; original callback still queued after close). Initial close assertion used isIdle, which excludes future queued timers; corrected to Handler.hasCallbacks against the captured original runnable before production edits. Exact 60s control passed.
- `timer-green`: exit 0; log `timer-green.log`; exact command in ledger.
- `clear-late-red`: exit 1; log `clear-late-red.log`; exact command in ledger.

Timer GREEN: 42 SessionManager tests passed. Policy: retain first background deadline, deduplicate pause callbacks. Clear-late RED: both success and partial-failure cases restored removed-session after delayed lookup/start/sync completion.
- `clear-late-green`: exit 0; log `clear-late-green.log`; exact command in ledger.
- `response-order-red`: exit 1; log `response-order-red.log`; exact command in ledger.

Clear-late GREEN: 3 focused tests passed including original success test. Cache policy: invalidate on clear entry and in finally, including partial failure; pre/during purge requests cannot repopulate after completion. Old callers receive their own response payload, not a claim of current identity. Response-order RED: delayed first start overwrote the later native session despite command-side model already owning session-1.
- `response-order-green`: exit 0; log `response-order-green.log`; exact command in ledger.
- `lifecycle-pending-red`: exit 1; log `lifecycle-pending-red.log`; exact command in ledger.

Response-order GREEN: 4 tests passed. Session cache commits only for newest issued session command in current clear epoch; channel calls retain issuance order and are not rolled back by delayed replies. Lifecycle pending RED: 5 tests failed (three duplicate starts, and no end after pending start on leave/paused/hidden/detached).
- `lifecycle-pending-green`: exit 0; log `lifecycle-pending-green.log`; exact command in ledger.
- `lifecycle-errors-red`: exit 1; log `lifecycle-errors-red.log`; exact command in ledger.

Lifecycle pending GREEN: 9 focused tests passed. Observer serializes its owned start/end and retains departure intent while replies are pending; identity comparison skips obsolete cleanup. Error RED: both fire-and-forget start and end produced unhandled PlatformException; retry behavior itself remained reachable.
- `lifecycle-errors-green`: exit 0; log `lifecycle-errors-green.log`; exact command in ledger.
- `a1q1-coverage-green`: exit 0; log `a1q1-coverage-green.log`; exact command in ledger.
- `lifecycle-cached-intent-red`: exit 1; log `lifecycle-cached-intent-red.log`; exact command in ledger.

Lifecycle errors GREEN: 7 tests passed; fixed diagnostic only, no arbitrary channel details; later event retries. A1Q1 coverage-only GREEN: original borrowed handles captured before each covered failed export and checked before getter reuse; no exporter production change. Additional cached-intent RED: immediate practice true/false while cached reconciliation Future completed lost the leave event (1/8 failing).
- `lifecycle-cached-intent-green`: exit 0; log `lifecycle-cached-intent-green.log`; exact command in ledger.
- `additional-combinations-coverage`: exit 0; log `additional-combinations-coverage.log`; exact command in ledger.

Cached-intent GREEN: 8 lifecycle tests passed after draining intent changes and releasing pending work in the same continuation. Additional characterization GREEN: 32 focused Dart tests; independent clear entry/finish fences for participant/start/sync on success/partial failure; independent old-end/old-sync replacement tests; inactive, exit/re-entry serialization, external replacements and observer-clear combinations. No new production changes were needed for these added combinations. Source dispatch inspection: MainActivity lines85-113 performs native session effects synchronously before result.success under pipelineLock. Mock tests independently model dispatch effects vs withheld responses; they are not actual platform dispatch/integration tests.
- `final-focused-jvm`: exit 0; log `final-focused-jvm.log`; exact command in ledger.
- `final-focused-dart`: exit 0; log `final-focused-dart.log`; exact command in ledger.
- `full-flutter-analyze`: exit 1; log `full-flutter-analyze.log`; exact command in ledger.
- `full-flutter-tests`: exit 0; log `full-flutter-tests.log`; exact command in ledger.
- `full-flutter-analyze-green`: exit 0; log `full-flutter-analyze-green.log`; exact command in ledger.
- `full-flutter-tests-final`: exit 0; log `full-flutter-tests-final.log`; exact command in ledger.

## Final host verification snapshot

- Targeted JVM: 64 passed (42 SessionManager, 22 DataExporter), no failures/errors/skips. This is NOT the full native suite. XML copied into `final-jvm-xml/`.
- Focused Dart: 32 passed; full Flutter: 67 passed; full analyze exit0, no issues. Initial analyze found one new test braces lint, fixed and rerun; failure log preserved.
- Protected hashes: 82 compared, 0 mismatches; `git diff --check` exit0. Source hashes in `source-manifest.json`.
- Formatting command: `/opt/homebrew/bin/dart format app/lib/session/session_repository.dart app/lib/session/session_lifecycle.dart app/test/session_clear_test.dart app/test/session_lifecycle_race_test.dart app/test/session_repository_race_test.dart`, exit0; subsequent diff check exit0.

### A2a source paths

- `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/SessionManager.kt`
- `app/android/app/src/test/kotlin/com/kumpas/kumpas_app/SessionManagerTest.kt`
- `app/android/app/src/test/kotlin/com/kumpas/kumpas_app/DataExporterTest.kt`
- `app/lib/session/session_repository.dart`
- `app/lib/session/session_lifecycle.dart`
- `app/test/session_clear_test.dart`
- `app/test/session_lifecycle_race_test.dart`
- `app/test/session_repository_race_test.dart`

## Handoff and boundaries

Implementation status: **DONE** for bounded A2a host slice; independent parent verification/review remains required. This is not acceptance of A2a or completion of all host02/03/04 work.

- Timer policy retains the first 60-second background deadline across duplicate pause notifications. Resume, replacement start, clear and close remove that one callback. The strengthened timeout test repeats pause at30s and checks59,999ms versus60,000ms.
- Clear policy invalidates cached identities/session immediately on entry and again in finally; dataRevision increments once at completion even on native partial failure. Old asynchronous callers still receive their own payload; only cache commitment is fenced. Operations during clear are not a cross-process transaction; post-clear calls are usable. Real native errors propagate from repository clear unchanged, with no fabricated native rollback.
- Latest-issued session command controls cache commitment. It is not native command cancellation. Observer serializes its own start/end work and retains departure intent; cleanup is sent only while its owned identity still matches the current repository cache. Error diagnostics use a fixed message and later observer events retry.
- Unresolved/unexercised boundaries: permanently lost channel replies are not given new deadlines in this slice; native side effects cannot be inferred or undone from response loss. Native command dispatch was inspected in source; independently controllable reply order is exercised via mocked transport, not a running installed MethodChannel. No installed lifecycle/camera/device/physical claims.
- A2b activity initialization and stream/resource faults were not changed. No MainActivity, model/training/benchmark, feedback mathematics, XP or UI layout edits in this slice. No emulator, phone, ADB, participant/default installed stores, installation, commits, reset/clean/stash or worktrees used. Gradle's normal generated merge-assets task is not a requested repository clean operation.
- New evidence: append-only report/ledger and per-command logs, execution runner, verification snapshot script/summary, source/protected hash manifests and copied final targeted JVM XML. Existing A1 evidence untouched. Prior accepted native changes remain in the dirty source; a HEAD diff includes those changes and is not an A2a-only patch.
- `parent-jvm-1`: exit 0; log `parent-jvm-1.log`; exact command in ledger.
- `parent-analyze-1`: exit 0; log `parent-analyze-1.log`; exact command in ledger.
- `parent-full-flutter-1`: exit 0; log `parent-full-flutter-1.log`; exact command in ledger.
- `review-fix-1-red-handoff`: exit 1; log `review-fix-1-red-handoff.log`; exact command in ledger.
- `review-fix-1-green-handoff`: exit 0; log `review-fix-1-green-handoff.log`; exact command in ledger.
- `review-fix-1-red-end-failure`: exit 1; log `review-fix-1-red-end-failure.log`; exact command in ledger.
- `review-fix-1-green-end-failure`: exit 0; log `review-fix-1-green-end-failure.log`; exact command in ledger.
- `review-fix-1-focused`: exit 0; log `review-fix-1-focused.log`; exact command in ledger.
- `review-fix-1-analyze`: exit 1; log `review-fix-1-analyze.log`; exact command in ledger.
- `review-fix-1-full`: exit 0; log `review-fix-1-full.log`; exact command in ledger.
- `review-fix-1-analyze-final`: exit 0; log `review-fix-1-analyze-final.log`; exact command in ledger.
- `review-fix-1-full-final`: exit 0; log `review-fix-1-full-final.log`; exact command in ledger.
- `parent-fix1-analyze`: exit 0; log `parent-fix1-analyze.log`; exact command in ledger.
- `parent-fix1-flutter`: exit 0; log `parent-fix1-flutter.log`; exact command in ledger.
