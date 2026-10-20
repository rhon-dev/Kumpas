# A2b — activity/resource acquisition and stream fault closure

## Context and authority

Owner approved host-only design and continued execution. A1 exporter/questionnaire and A2a lifecycle/cache are independently accepted at bounded host scope; preserve them. Full design/plan in docs/superpowers/{specs/2026-10-15-host-completion-design.md,plans/2026-10-15-host-completion.md}. Discovery app-host-audit.md sections4 and1 identify actual staged Activity gap. No emulator/phone/ADB/default stores/installations/commits/reset/clean/stash/worktree/model/training/math/XP/layout changes.

## Deliverable and ownership

Own only native MainActivity.kt, narrow adjacent Activity initialization resource factory/helper if necessary, VisionEngine.kt only for demonstrated stream faults, and corresponding host tests ActivityInitializationTest.kt/VisionInitializationTest.kt/ResourceCleanupTest.kt/CameraViewOwnershipTest.kt/MainActivityBoundaryTest.kt. Existing camera production file/factory changes only if a reproduced callback failure requires it; report exact need before editing any other source. One implementer; preserve existing accepted postimages and all82 protected hashes. No Dart/session/export source edits.

## Behavioral acceptance

1. Actual production-used staged MainActivity collaborator acquisition must clean every acquired owned resource if a later acquisition or registration fails. Inspect configureFlutterEngine: SessionManager then exporter/benchmark then VisionEngine and channel/view registration. onDestroy is not guaranteed after failed configuration. Prove with injected stage failures through a callable initialization seam actually invoked by configureFlutterEngine, not a disconnected helper test or arbitrary Unsafe bypass. Test initialization and clean retry with isolated synthetic contexts/fake owned handles; never configure default participant stores. Production factory must still construct real existing collaborators using correct context/lock/event wiring.
2. Failed initialization must not publish phantom/stale collaborators, keep failed event subscriptions live, or overwrite a newer replacement owner. Preserve original failure; every later cleanup attempt occurs even if an earlier close fails, with suppressed diagnostics. Normal onDestroy/framework cleanup semantics remain. Avoid duplicate ownership/double-close from published stale fields after rollback. If a narrower contract is appropriate because actual Flutter framework registration cannot be hosted safely, explicitly separate tested seams and unexecuted framework boundaries.
3. Expand existing VisionEngine constructor/runtime asset tests for model/labels/gold streams whose close itself fails, combined read+close faults, and rollback release faults. Original primary failure preserved; close faults suppressed, all acquired native wrappers still released. Expected existing correct behavior is coverage-only GREEN; repair only after behavioral RED. No detector/math/model changes.
4. Characterize asynchronous camera provider completion failure and bind failure after listener registration at actual queued callback path where feasible using existing factories. Existing bind-disabled tests are not CameraX driver release evidence. Preserve current per-view ownership, stale subscriber fencing, constructor rollback and later cleanup attempts. If no production change is necessary, label coverage only. No actual camera acquisition on host.
5. Existing MainActivity event persistence/subscriber/view tests must remain green. Injected context/resources must not silently fall back to global/default stores. Capture original exception/cleanup counts and independent ownership assertions.

## Design guardrails

Use smallest production seam following current VisionResourceFactory and CameraViewResourceFactory patterns. Do not copy configure business logic into tests, overhaul channel contracts, swap dependencies or introduce generic frameworks. Future A3 will need actual control dispatch with isolated export helper; do not implement that unrelated harness now, but avoid blocking its later narrow extraction. Explicitly record where the chosen seam sits relative to super.configureFlutterEngine, permission request, channels and view registration. No claim that fake close handles prove MediaPipe/TFLite/CameraX driver release.

## Regression-first execution

Read existing code/tests and prior resource helpers first. Create a2b/report.md and append-only command-ledger.jsonl before source edits. One vertical failing behavior then minimal fix then GREEN; preserve all failed logs and label already-correct behavior honestly. No compilation error counts as behavioral RED.

Use existing JDK17/SDK/cached Gradle with --offline and exclusive fcntl lock ~/.hermes/cache/scratch/kumpas-gradle.lock, TMPDIR under session scratch. Runners a1/a2a demonstrate env/locking but do not overwrite old evidence. Force targeted JVM test task with --rerun and relevant tests; then full native suite with no --tests filters plus instrumentation Kotlin source compilation (not device execution). Report XML parsed totals/failures/errors/skips, actual commands/exits and source hashes. Host compilation is authorized; no APK installation or runtime instrumentation. Compare82 protected hashes against controller/host-baseline.json; git diff --check. Parent independently verifies and obtains spec/quality review before acceptance.

Return DONE/DONE_WITH_CONCERNS/BLOCKED, exact changes/tests and remaining testability boundaries. Do not claim all host04 or broader app/study acceptance without mapping every named requirement to evidence.
