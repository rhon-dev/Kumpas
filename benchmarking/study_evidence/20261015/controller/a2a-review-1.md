# A2a independent host QA review

## Verdicts

- **Specification: REQUEST CHANGES for A2a lifecycle/cache closure.** Clear fencing, reply-order cache guards, native timer behavior and A1Q1 strengthening are supported. R1 below leaves a reachable screen-lifetime handoff unreconciled even when every reply eventually arrives.
- **Code quality: REQUEST CHANGES.** The per-observer drain is coherent within one observer, but its cached-session adoption is not coordinated with another observer's pending departure. Add a deterministic two-observer regression and resolve R1 before calling the bounded lifecycle race work complete.
- Neither verdict addresses broader runtime/study acceptance. No installed integration, physical performance, research scoring, training or participant authorization is accepted here.

## Review basis and verification

Read the binding `a2a/task-brief.md`, implementation `a2a/report.md`, complete `controller/a2a-review-package.diff`, all three current production files and five scoped test files, `controller/a2a-parent-verification.json`, host design, `controller/host-baseline.json`, and accepted A1 review/acceptance context. Inspected actual PracticeScreen construction/disposal and native session dispatch/attempt fallback. The package is HEAD-relative and includes carried SessionManager/resource and A1 exporter-test changes; those are not all newly attributed to A2a.

Independent checks performed:

- Recomputed SHA-256 for all **8 scoped files**: all match the frozen parent source hashes, including after the probes.
- Recomputed all **82 protected hashes** against each baseline entry's `expected` digest: **0 mismatches**.
- `git diff --check`: exit **0**.
- Inspected parent logs: targeted JVM test task executed (not merely UP-TO-DATE); analyzer says no issues; full Flutter log ends `+67: All tests passed!`. Parsed preserved targeted JVM XML: **42 SessionManager + 22 DataExporter**, zero failures/errors/skips. These are parent/package executions, **not this reviewer's fresh suite executions and not the full native suite**.
- Executed a fresh scratch-only Flutter probe against the unchanged production repository and observer: **2 probes, 1 failed behavioral assertion (R1), 1 passing boundary characterization (B1)**; command exit **1**. Repeated the same narrow command to retain its output; same result. No full suite was repeated.

Exact independent command (working directory `app/`):

```text
/opt/homebrew/bin/flutter test --no-pub /Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/a2a-independent-qa-hfbg6dt0/lifecycle_probe_test.dart --reporter expanded
```

Probe source SHA-256: `40211be6283054efeeceb679f48f155cad04844969ff4de6f2abd1144b28dc01`.
Exact scratch output: `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/a2a-independent-qa-hfbg6dt0/probe.log`. Scratch files are ephemeral; complete probe source is retained below for reproduction.

## Blocking finding

### R1 — Medium / blocking: a new screen adopts the old screen's already-ending cached session

**Locations:** `app/lib/session/session_lifecycle.dart:12,41–43,76–78,92–98`; `app/lib/session/session_repository.dart:52–59`. Actual caller: `app/lib/ui/practice_screen.dart:53–58,303–312` creates a new observer per screen and does not await the previous observer's departure.

`_pending` serializes only one observer instance. `endSession()` keeps the old ID cached while its reply is pending, even though the native end has already executed. A new observer treats that cache as an active, adoptable session at lines76–78 and returns. When the previous observer's successful end reply arrives, the repository clears the cache, but the new observer has no remaining work or notification to reconcile its foreground intent.

Deterministic reproduced order, using only the production observer/repository public methods:

1. Old screen is active/resumed; start returns `session-1`.
2. Old screen calls `setPracticeActive(false)` as its actual dispose does. Native `endSession` takes effect at dispatch, setting native state to null; withhold only the reply.
3. Construct the replacement screen's observer, call `setPracticeActive(true)`, and deliver `resumed` while the old reply is pending. It adopts cached `session-1` and sends no start.
4. Deliver the old end reply successfully. Drain all futures. Replacement remains in practice/foreground, but native and cached session are both null; only one start ever occurred.

Actual output:

```text
QA_HANDOFF commands=[startSession, endSession] native=null cache=null starts=1
Expected: not null
Actual: <null>
foreground replacement must not adopt a session whose end already dispatched
```

This is a finite delayed-reply case, **not** a permanently lost reply, fabricated command reordering or a claim that a late reply undoes a native effect. Both commands take effect in their ordinary issuance order. The callback pattern is reachable across disposed/recreated PracticeScreen instances; a subsequent resume may occur before the old reply settles. No arbitrary external repository caller is needed. The existing re-entry test reuses the same observer and therefore exercises a stronger serialization guarantee than actual route recreation gets.

**Impact:** the new practice screen can remain without a tracked session until another relevant lifecycle event. Native `recordAttempt` may later create a session on demand (`SessionManager.kt:153–161`), but that does not reconcile the Dart cache/ownership or make foreground departure cleanup reliable. This does not establish lost attempt rows or data corruption.

**Required follow-up:** coordinate the ending-session/in-flight state across observer lifetimes, or otherwise prevent adoption of a session whose end is pending and ensure new foreground intent is reconciled after that operation settles. Preserve current signatures and identity-safe cleanup; simply issuing an unscoped extra end is not a safe fix. Add a two-observer regression matching the actual construct/dispose pattern. This is an unclosed in-scope race, not a claim that A2a newly introduced the pre-existing cross-screen problem.

## Requirement-by-requirement assessment

| Brief requirement | Reviewed evidence | Assessment |
| --- | --- | --- |
| Duplicate native pause and original 60-second deadline | `SessionManager.kt:124–147`; tests `SessionManagerTest.kt:330–371` cover pause/pause/resume, replacement, original runnable removal after close, and repeated pause at30s with59,999/60,000ms assertions. | Supported under the actual main-looper lifecycle dispatch. No sleep-based timing claim. |
| Clear entry/finally fences | Repository `:30–47,64–70,90–105`; repository tests independently exercise participant/start/sync pre-clear and during-clear requests for success and partial failure. | Supported for cache commitment. Both fences are needed: entry blocks pre-clear completions during purge; finally blocks operations issued in the intermediate epoch. A during-clear completion may be transiently cached before finally; the policy is not an atomic purge/read transaction. |
| Partial failure, revision and usability | Repository `:90–99`; `session_clear_test.dart` validates error code, revision change, fresh identity and subsequent start. | Supported: one revision increment per completed clear attempt, including failure; original native purge error propagates. No rollback fabricated. |
| Out-of-order start/end/sync replies | Repository `:41–70`; repository race tests model effects at dispatch separately from withheld replies. | Supported for latest-issued-command cache commitment in a clear epoch. Older callers still receive their own start payload, not proof of current ownership. See B1 for the limit of cache-only cleanup. |
| Lifecycle duplicate work and departure during start | Observer `:41–98`; lifecycle tests use actual methods and Completers, cover duplicate resume/entry, leave/paused/hidden/detached, inactive and same-observer re-entry. | Supported within one observer; **not complete across actual screen-instance handoff (R1)**. |
| Fire-and-forget errors and retry | Observer `:50–58,92–98`; tests exercise start and end exceptions and repeat the same observer event. | Errors are caught with fixed text; an end failure retains ownership for a subsequent event. No automatic retry or retry-after-disposal guarantee: actual disposal removes the observer, so a future event on that instance is not assured. Do not generalize the same-instance test to disposed-screen recovery. |
| A1Q1 original borrowed handle | `DataExporterTest.kt:348–367,395–407`. Original handle captured at355/401, checked at364/407 before another helper getter can reopen it. | **Resolved, coverage-only GREEN**. The fallback-success getter check at391 is not a failed-export assertion and is not a remaining Q1 failure. No A1 production export change. |

## Unsupported boundaries / non-blocking observations

### B1 — Low / boundary: cache equality is not a native identity-scoped end

**Locations:** `session_lifecycle.dart:94–96`; repository `:41–47,52–59`; native dispatch `MainActivity.kt:86–91`.

The additional passing characterization deliberately starts an external replacement while the old cached ID is still visible, withholds the replacement reply, and then departs the old observer. Native commands are `[startSession, startSession, endSession]`; the old observer's cache-equality check passes and the unscoped end closes the native replacement. The latest command guard correctly leaves the cache null afterward. Existing tests protect *completed/cache-visible* external replacement, not a replacement with a pending reply.

Read-only production caller search finds repository start/end calls only in SessionLifecycleObserver; no separate arbitrary external start API consumer currently exists. Therefore this particular synthetic external-caller ordering is **not asserted as a second independently reachable production defect**, and does not add another blocking finding. It does prove that neither the guard nor mocked reply-order tests establish native identity atomicity for arbitrary overlapping callers. A change for R1 must account for this boundary rather than blindly ending whatever native session is active.

Other limits:

- Native effects run synchronously under the actual control/pipeline lock before `result.success`; the mocks establish a specified dispatch/reply schedule, not actual installed MethodChannel ordering or uninterrupted integration.
- Permanent reply loss deliberately has no new deadline in this slice. An observer may remain pending and unable to make later progress; that approved exclusion is not used as R1's basis.
- Fresh observer `_foreground` starts false and PracticeScreen does not seed the binding's already-current lifecycle state. Ordinary route entry without a newly delivered resume is not newly proved to start a session. This is carried behavior, not a newly attributed A2a regression; R1 explicitly supplies a resume and does not depend on this issue.
- No arbitrary concurrent clears/transport reordering, process-death durability, database failure on the main-looper timeout callback, or automatic recovery after a disposed observer's failed end is accepted from these tests.
- A2b activity/resource/stream work, installed behavior and physical/study gates remain outside this review.

## Changes made by reviewer

Only this report was added inside the repository. No reviewed production/test source, baseline, source manifest, parent evidence or protected file was edited. The standalone synthetic probe and its log were created only under the authorized Hermes scratch root. No installation, Gradle/build command, ADB, emulator, default participant store, training or commit operation was performed. Flutter host-test execution may update its ordinary generated test cache; it is not an app/artifact build acceptance.

One read attempted an absent optional `a2a/run_command.py`; the actual evidence runner is `run-host-tests.py` and was read successfully. An initial protected-map comparison used the whole metadata object rather than its `expected` digest; corrected comparison above independently checked all82 digest values with zero mismatches. Neither read-only diagnostic affected source or the finding.

## Appendix: exact independent probe

```dart
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kumpas_app/feedback_engine/kumpas_channel.dart';
import 'package:kumpas_app/session/session_repository.dart';
import 'package:kumpas_app/session/session_lifecycle.dart';
void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  final messenger = TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger;
  final repo = SessionRepository.instance;
  late Future<Object?> Function(MethodCall) handler;
  setUp(() async {
    handler = (_) async => null;
    messenger.setMockMethodCallHandler(KumpasChannel.control, (call) => handler(call));
    await repo.clearAllData();
  });
  tearDown(() async {
    handler = (_) async => null;
    await repo.clearAllData();
    messenger.setMockMethodCallHandler(KumpasChannel.control, null);
  });
  test('replacement screen must acquire a live session after prior owned end settles', () async {
    final endReply = Completer<void>();
    final commands = <String>[];
    String? nativeSession;
    var starts = 0;
    handler = (call) async {
      commands.add(call.method);
      if (call.method == 'startSession') {
        nativeSession = 'session-${++starts}';
        return nativeSession;
      }
      if (call.method == 'endSession') {
        nativeSession = null; // effect at dispatch, before withheld reply
        await endReply.future;
      }
      return null;
    };
    final oldScreen = SessionLifecycleObserver();
    oldScreen.setPracticeActive(true);
    await oldScreen.didChangeAppLifecycleState(AppLifecycleState.resumed);
    oldScreen.setPracticeActive(false); // PracticeScreen.dispose
    await pumpEventQueue();
    final replacement = SessionLifecycleObserver();
    replacement.setPracticeActive(true); // new PracticeScreen.initState
    await replacement.didChangeAppLifecycleState(AppLifecycleState.resumed);
    endReply.complete();
    await pumpEventQueue();
    print('QA_HANDOFF commands=$commands native=$nativeSession cache=${repo.activeSessionId} starts=$starts');
    expect(nativeSession, isNotNull, reason: 'foreground replacement must not adopt a session whose end already dispatched');
    expect(repo.activeSessionId, nativeSession);
    replacement.setPracticeActive(false);
    await pumpEventQueue();
  });
  test('pending external replacement demonstrates limit of cache-only cleanup guard', () async {
    final replacementReply = Completer<String>();
    final commands = <String>[];
    String? nativeSession;
    var starts = 0;
    handler = (call) async {
      commands.add(call.method);
      if (call.method == 'startSession') {
        nativeSession = 'session-${++starts}';
        if (starts == 2) return replacementReply.future;
        return nativeSession;
      }
      if (call.method == 'endSession') nativeSession = null;
      return null;
    };
    final observer = SessionLifecycleObserver();
    observer.setPracticeActive(true);
    await observer.didChangeAppLifecycleState(AppLifecycleState.resumed);
    final external = repo.startSession();
    await pumpEventQueue();
    observer.setPracticeActive(false);
    await pumpEventQueue();
    replacementReply.complete('session-2');
    await external;
    print('QA_EXTERNAL commands=$commands native=$nativeSession cache=${repo.activeSessionId}');
    // Characterization only: no additional external start caller exists today.
    expect(nativeSession, isNull);
    expect(commands, ['startSession', 'startSession', 'endSession']);
  });
}
```
