# A2a — host lifecycle/cache race closure

## Authorization and scope

Owner approved host-only completion design and asked to continue. This is the next bounded slice after accepted A1. Full design: docs/superpowers/specs/2026-10-15-host-completion-design.md; execution plan: docs/superpowers/plans/2026-10-15-host-completion.md. Discovery/app-host-audit.md sections2–3 identify hypotheses, not confirmed defects. A1 acceptance: controller/a1-acceptance-20261016.json. Do not restart prior accepted work.

## Ownership

May modify:
- app/android/app/src/main/kotlin/com/kumpas/kumpas_app/SessionManager.kt and corresponding SessionManagerTest.kt.
- app/lib/session/session_repository.dart and session_lifecycle.dart.
- app/test/session_clear_test.dart; new app/test/session_lifecycle_race_test.dart and narrowly named repository race tests if clearer.
- app/android/app/src/test/kotlin/com/kumpas/kumpas_app/DataExporterTest.kt ONLY to strengthen reviewer Q1 borrowed-handle assertions; no A1 production export change.
- Evidence under benchmarking/study_evidence/20261015/a2a/.

Do not change MainActivity/resource/benchmark/model/training code in this slice; activity initialization and stream failures belong to A2b. Preserve existing participant/source protections, math, XP, approved layout, strict metadata, receipt commitment and prior tests. No emulator/phone/ADB/default stores/installations/commits/push/worktree/reset/clean/stash. Use existing dependencies and shared Gradle lock. Temporary roots under ~/.hermes/cache/scratch.

## Behavioral acceptance

1. Repeated native pause/pause then resume cannot leave an obsolete timer that closes a foreground/replacement session. Repeated pause then close must not leave a callback that touches closed helper state. Test deterministic main-looper advancement, not sleeps; preserve ordinary60-second timeout semantics.
2. Pending participant lookup, startSession or sync response arriving after clear must not repopulate cached pre-clear participant/session state. Cache invalidation covers both successful and partial failed clear. New post-clear operations remain usable. Guard invalidation when clear begins as well as when it finishes if required by reachable ordering; explain policy explicitly. Do not suppress real native purge errors or fabricate native rollback.
3. Out-of-order start/end/sync responses must not clear/overwrite a later session's cache. Characterize actual native command order independently from response completion; generation guards do not undo side effects. Preserve public method signatures and reasonable existing usage.
4. Lifecycle resumed/practice entry must not launch duplicate uncoordinated sessions; leaving/paused/hidden/detached during pending start must eventually end the owned session without closing a newer replacement from obsolete continuation. Inactive remains transitional. Catch or surface fire-and-forget channel errors safely, avoid unhandled future errors, and allow deterministic retry. Test actual observer methods and controllable channel Completers. No distributed atomicity claims.
5. Partial clear failure increments dataRevision and invalidates cached identities/session as designed. Late reads cannot restore removed state. Existing success-flow tests remain green.
6. A1 reviewer Q1: capture original borrowed SQLite handle before each covered failed export, assert original handle remains open BEFORE any helper getter could reopen it. This is test-strengthening and expected coverage-only GREEN; do not claim a new production defect.

## Workflow and evidence

Create report.md plus append-only command-ledger.jsonl before source edits. One vertical behavioral RED/GREEN slice at a time. First read current production/tests and caller usages. Record exact commands/exits/logs immediately; passing characterization stays coverage-only. Minimal fixes, no broad refactor or arbitrary new behavior. If contradictory policy or a missing externally required decision blocks progress, report it rather than guess; complete independent cases first.

Use deterministic Looper/Completer control, isolate/reset repository singleton state in tests and restore messenger handlers. No real participant IDs or raw video. No test should silently accept stale cache just because a mock returned it.

Target commands (through lock for Gradle, existing environments):
- app/android: ./gradlew --offline :app:testDebugUnitTest --rerun --tests 'com.kumpas.kumpas_app.SessionManagerTest' --tests 'com.kumpas.kumpas_app.DataExporterTest'
- app: flutter test --no-pub test/session_clear_test.dart test/session_lifecycle_race_test.dart --reporter expanded (include additional new repository test if created).
- app: flutter analyze --no-pub and full flutter test --no-pub --reporter expanded after focused green.

Do not label targeted JVM count as full native suite. Parent will independently run verification and review. At completion compare all82 protected hashes from controller/host-baseline.json, git diff --check, report changed paths and unresolved combinations. Return DONE/DONE_WITH_CONCERNS/BLOCKED plus concise actual counts. This slice does not complete all host02/03/04 tasks or installed integration.
