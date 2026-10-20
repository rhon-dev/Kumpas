# A2b incremental implementation report

Status: in progress; host-only, no broader acceptance. Source ownership per task-brief.md. Existing accepted edits preserved.

Design: production-used MainActivity initialization transaction after super.configureFlutterEngine and permission request, encompassing acquisition and channel/view registration. Synthetic owned handles avoid default stores/native inference. Channel cleanup registered before handler installation; platform registry has no unregister API, so failed/superseded factories must be fenced. Actual Flutter framework registration/device release remains unexecuted.

Evidence follows append-only.
- `activity-acquisition-red`: exit 1; log `activity-acquisition-red.log`; exact command in ledger.
- `activity-acquisition-green`: exit 0; log `activity-acquisition-green.log`; exact command in ledger.
- `activity-registration-red`: exit 1; log `activity-registration-red.log`; exact command in ledger.
- `activity-registration-green`: exit 0; log `activity-registration-green.log`; exact command in ledger.
- `stream-camera-coverage`: exit 0; log `stream-camera-coverage.log`; exact command in ledger.
- `activity-queued-retry-red`: exit 1; log `activity-queued-retry-red.log`; exact command in ledger.
- `activity-queued-retry-delivery-red`: exit 1; log `activity-queued-retry-delivery-red.log`; exact command in ledger.
- `activity-queued-retry-green`: exit 0; log `activity-queued-retry-green.log`; exact command in ledger.
- `registry-rejection-red`: exit 1; log `registry-rejection-red.log`; exact command in ledger.
- `displaced-owner-red`: exit 1; log `displaced-owner-red.log`; exact command in ledger.
- `focused-final`: exit 0; log `focused-final.log`; exact command in ledger.
- `full-jvm-instrumentation-compile`: exit 0; log `full-jvm-instrumentation-compile.log`; exact command in ledger.

## Regression slices and boundaries

- Before first RED: extracted acquisition-only ActivityResourceFactory/initializeResources, wired directly into configureFlutterEngine, retaining the missing rollback. This extraction introduced the callable test seam; it was not claimed as a behavioral fix. `activity-acquisition-red` compiled then failed the release-count assertion (expected session+benchmark, none released). Minimal rollback then `activity-acquisition-green` passed.
- `activity-registration-red` compiled and failed missing subscription detachment. Added initialization ownership, channel-detach registration, current-owner-only field clearing, idempotent transfer/release, owner-fenced event/control/view callbacks. `activity-registration-green` passed with preexisting boundary/cleanup suites. Newer-owner test initially already passed (coverage-only), and was strengthened with owner identity and live attempt assertions.
- `activity-queued-retry-red` failed because an attempt survived rollback. After adding invalidation, `activity-queued-retry-delivery-red` failed because the posted event crossed retry when the same subscriber object was reused. Capturing initialization identity at final posted delivery fixed the latter; `activity-queued-retry-green` passed.
- `registry-rejection-red` compiled and failed because the actual production-used registry call ignored false. Now false throws and triggers rollback; retained factory is owner-fenced. Verified GREEN in focused-final.
- `displaced-owner-red` failed because failed replacement registration leaked the previously displaced owner's acquired handles. Catch now releases the displaced owner only when publication occurred, without restoring stale fields. Verified GREEN in focused-final. Early acquisition failure still preserves the viable previous owner.
- `stream-camera-coverage` passed on its first execution: coverage-only GREEN, not defect evidence. No VisionEngine.kt or camera production changes were needed. Constructor model/labels close-only and read+close faults preserve primary/suppressed errors while releasing acquired native wrappers; runtime labels/gold close-only and read+close faults close streams exactly once and leave engine usable until explicit close.
- Camera coverage executes the actual constructor-registered callback after SettableFuture completion on an explicit main Handler queue. Provider future failure and shadowed bindToLifecycle failure are distinct; stale/disposed callbacks never bind or emit. Real Preview/ImageAnalysis instances are passed to shadowed unbind on disposal after bind failure, executor shuts down, repeated dispose is safe. Shadow hasCamera/bind/unbind replace driver access only. This is not CameraX hardware release evidence.

### Chosen Activity seam

The transaction begins after super.configureFlutterEngine and permission request. It stages SessionManager, DataExporter (non-closeable/no owned native handle), BenchmarkMode and VisionEngine through the production Android factory using the existing applicationContext, pipelineLock, generation provider and event callbacks. It then publishes fields and invokes the real channel/view-registration closure. Channel detach actions are enrolled before installation; platform registration false is failure. No dispatcher contracts were moved into tests or changed.

Tests call that same transaction with synthetic owned handles, plus a real VisionEngine constructor using synthetic native handles for publication/close assertions. They never call the default AndroidActivityResourceFactory or full configureFlutterEngine on host, so there is no fallback to installed/default participant stores. Existing full native tests run in Robolectric's synthetic sandbox, not installed app data.

### Explicit testability concerns

- Full FlutterActivity/FlutterEngine startup, actual BinaryMessenger channel installation/removal, permission dispatch and a functioning Flutter superclass delegate are not executed. The real superclass teardown is attempted on bare test Activities; its missing-delegate exception is retained as evidence of attempted framework cleanup, not successful framework lifecycle execution.
- PlatformViewRegistry offers no unregister API. Retained failed/superseded factories are inert via initialization identity. Transaction retry is tested; a clean fresh registry can accept registration. Retry against a registry that already retained the same ID may reject and safely roll back, rather than silently pretend success. Full same-engine retry is not established.
- A stale initialization skips its registration-detach actions so it cannot remove replacement handlers. Same-messenger installation overwrites the old channel handlers; differing-engine/messenger replacement is not exercised. Owner guards render retained old callbacks inert, but actual cross-engine handler removal is not claimed.
- Fake release handles establish orchestration/counts/exception preservation only; no MediaPipe/TFLite/CameraX driver release, installed E2E flow, physical measurements, participant collection or broader study acceptance is claimed.
- `focused-handoff`: exit 0; log `focused-handoff.log`; exact command in ledger.
- `full-handoff`: exit 0; log `full-handoff.log`; exact command in ledger.

## Final handoff — DONE_WITH_CONCERNS

- Focused JVM: {'tests': 33, 'failures': 0, 'errors': 0, 'skipped': 0}. Full native JVM (no filters): {'tests': 162, 'failures': 0, 'errors': 0, 'skipped': 0}. Fresh XML snapshots in the corresponding `*-xml/` directories.
- Instrumentation Kotlin source compile exit0, task executed (not UP-TO-DATE). No instrumentation/device runtime executed. Final source compile/tests followed formatting and stronger coverage assertions.
- Protected assets/contracts: 82 checked, no mismatches. All 8 A2a accepted source hashes unchanged. `git diff --check` exit0.
- Five A2b source paths and preserved neighbors are hashed in source-manifest.json. No Dart/session/export/model/benchmark production changes; no camera or VisionEngine production changes in A2b.
- Exact commands, exits, lock, TMPDIR and log paths in command-ledger.jsonl. Earlier RED run XML was not snapshotted before subsequent runs; behavioral failures and test names/counts remain in original logs. Final focused/full XML is retained. Gradle reported its existing deprecation warning in an early failed run; no install was attempted.
- Parent independent verification and spec/quality review are still required. This is an implementation handoff, not broader acceptance.

### A2b source changes

- `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/MainActivity.kt`
- `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/ActivityResourceFactory.kt`
- `app/android/app/src/test/kotlin/com/kumpas/kumpas_app/ActivityInitializationTest.kt`
- `app/android/app/src/test/kotlin/com/kumpas/kumpas_app/VisionInitializationTest.kt`
- `app/android/app/src/test/kotlin/com/kumpas/kumpas_app/CameraViewOwnershipTest.kt`
- `parent-full-1`: exit 0; log `parent-full-1.log`; exact command in ledger.
- `parent-fix1-full`: exit 0; log `parent-fix1-full.log`; exact command in ledger.
