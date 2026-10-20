# Mobile/QA: host tasks 1–5 discovery

Date: 2026-10-15. Scope: read-only source/test audit plus this report; no implementation, suites, builds, installs, ADB, emulator, device, or participant/default-store access. Base HEAD verified as `6b8b1b6770e46bea7728a8e9ca4ae6d78e857640`; accepted dirty repairs and untracked tests are part of the inspected source, not discarded. Read AGENTS.md, full docs/PRD.md, docs/phase-gates.md, kumpas-study-readiness skill, and the approved 20261007/controller/schema-minor-review-1.md. The user's host-only restriction controls over PRD emulator fallback. Historical 137 JVM / 35 Flutter / 43 Python results are not fresh execution here.

## Outcome

Most individual fault and ownership contracts already have substantial tests. The principal missing deliverable is a reproducible, isolated **layered host contract harness** joining native-produced artifacts to Flutter consumption and actual SQLite/export/delete/reopen observations. It cannot establish installed CameraX→Flutter integration. Do not redo the approved receipt-commit policy, strict metadata policy, or integer-schema repair.

Paths below are repo-relative. Kotlin production/test abbreviations: `K = app/android/app/src/main/kotlin/com/kumpas/kumpas_app/`; `T = app/android/app/src/test/kotlin/com/kumpas/kumpas_app/`.

## 1. Isolated native-result / Flutter / persistence / export / delete / reopen

**Existing evidence/seams**
- `T/MainActivityBoundaryTest.kt:176–226` injects real SessionManager/SessionDatabase plus BenchmarkMode into MainActivity, invokes production `handleVisionEvent`, drains Handler/EventSink, proves failed insert → failure event/no row/no trace and successful retry → row/result/trace. This is constructed JSON, not executed recognition.
- `K/MainActivity.kt:154–209` is the actual terminal acceptance/persistence/posted delivery seam. Method dispatch remains inline in `configureFlutterEngine` (52–131); directly constructing MainActivity avoids configuring a real FlutterEngine but does not exercise those method handlers.
- `T/SessionManagerTest.kt` covers real SQLite migration, both export roots, deletion, identity rotation, and reopening; `T/DataExporterTest.kt` covers contents, participant filtering, fallback storage, borrowed-helper ownership, write failure and empty export after clear.
- `app/test/practice_flow_test.dart:119–142,250–263` encodes hand-authored EventChannel envelopes and verifies one feedback sheet/one ACK, including wrong recognition. `app/test/session_clear_test.dart` tests successful repository cache reset only. These are separate mocked channel tests.
- `app/android/app/src/androidTest/kotlin/com/kumpas/kumpas_app/SessionDeletionTest.kt:19–47` supplies a useful isolation recipe: override application/files/external roots, both database-open overloads, database delete, namespaced preferences, and handle cleanup. Do not execute this instrumentation test in this phase.

**Genuine gap**: no current JVM-to-Dart artifact handoff for attempt results and state snapshots, and no single host scenario correlates persisted result, Flutter ACK, export, purge, and reopened identity/history. Existing attempt history omits attemptId (`K/SessionManager.kt:183–201`); do not assert a nonexistent durable attempt UUID column or change schema just for the harness.

**Minimal proposed design/files**
- New `T/HostStudyFixture.kt`: fresh synthetic root, isolated prefs/database/internal+external exports, fail-fast canonical containment checks, explicit handle ownership, close in finally. No fallback to application/default stores. Reuse the instrumentation isolation pattern rather than its fixture lifetime omissions.
- New `T/HostStudyFlowTest.kt`: inject fixture-owned collaborators, execute production event handler/Handler sink, query actual SQLite, export real JSON, cancel/invalidate through production control, clear, close every owner, reopen fresh helpers, export empty state. Persist a versioned *test envelope* containing exact delivered event string, control identities, history/assessment responses, export summary and before/after identities; keep fixture schema separate from production report schema. Use unique synthetic field combinations and row counts for history correlation.
- New `app/test/host_study_flow_test.dart`: load the emitted envelope, feed its exact event to the existing binary-messenger mechanism, return native-produced history/identity snapshots through the explicitly mocked control channel, assert feedback/ACK and cache invalidation. No in-memory mock pretending to be SQLite.
- Small optional production refactor only if authorized: extract `MainActivity` inline method handler into an internal callable used by both registration and tests; inject a context-scoped export helper factory. This is preferable to duplicating the switch in tests. Existing export handler constructs its helper from `applicationContext`, so an isolated manager alone is insufficient. Do not call configureFlutterEngine against default stores to obtain coverage.

**Acceptance**: native successful result produces exactly one row/result; duplicate and stale result cannot add rows; Dart displays precisely that result and ACKs once; export agrees with independent row counts; both managed export roots and migration residue are purged; unrelated synthetic sentinels survive; reopened history/assessments empty, exactly one fresh participant, new identity durable across reopen. State which calls were native dispatch versus replayed mocks. Record fixture/output hashes and source snapshot. No installed end-to-end claim.

## 2. Lifecycle / race coverage

**Already covered**
- `T/AttemptBoundaryTest.kt`: once-only terminal, clear/replacement invalidation, stale cancellation, ACK scope.
- `T/MainActivityBoundaryTest.kt:33–79`: already-posted view events, subscriber replacement, old camera error versus replacement attempt. `T/CameraViewOwnershipTest.kt:30–53` actually emits via VisionEngine with view owner before replacing view and draining Handler; 108–146 covers disposal/callback ownership.
- `T/SessionManagerTest.kt`: recovery, normal pause timeout/resume cancellation, monitor serialization; Flutter practice tests cover pending-start timeout/disposal, late identity-scoped cleanup, duplicate feedback, owned benchmark completion, confirmation uncertainty and delayed stop timeout. These are not missing contracts.

**Missing combinations / hypotheses to reproduce, not confirmed defects**
1. Real terminal persist succeeds, then clear/view replacement/subscriber replacement occurs before Handler drain: assert durable state versus suppressed UI separately. Combine with export and reopen, not only standalone AttemptBoundary calls.
2. Repeated native `onPause()` before resume: `K/SessionManager.kt:125–144` replaces the runnable reference without removing its predecessor. Deterministically check pause/pause/resume and pause/close followed by looper advancement for a surviving old timer.
3. Pending Dart `startSession`, participant lookup or `sync()` resolves after clear; out-of-order start/end/resume promises. `app/lib/session/session_repository.dart:25–47,67–75` has no visible generation fencing around these awaits. `app/lib/session/session_lifecycle.dart:16–61` has async start/end requests with no in-flight serialization. Characterize actual reachable ordering before proposing repair.
4. Exercise actual lifecycle observer transitions (resumed/paused/hidden/detached/inactive), not only screen disposal, and ensure no unhandled failed channel future.

**Files**: extend `T/MainActivityBoundaryTest.kt`, `T/SessionManagerTest.kt`; new `app/test/session_lifecycle_race_test.dart`, extend `app/test/session_clear_test.dart`. Change the corresponding production files only after a real failing reproduction and parent approval. Acceptance: deterministic Completers/Looper (no sleeps), replacement remains usable, no obsolete session/identity resurrects after successful clear, no late UI result or duplicated terminal/ACK, surviving persisted rows reported honestly. Specify ordering explicitly; do not require already committed success to be retroactively undone merely by navigation.

## 3. Persistence faults

**Already covered**
- `T/SessionDatabaseTest.kt:47–82`: delete transaction rollback for abort and silent trigger retention.
- `T/SessionManagerTest.kt:132–170`: ignored session/attempt/assessment/participant/migration inserts fail, migration rollback retains retry source. 495–650 covers inaccessible roots/listing, delete failure, DB failure after file removal, preference-commit failure, redirected paths, and fresh-participant persistence. Close-after-summary failure also tested.
- `T/MainActivityBoundaryTest.kt:176–226`: real failed attempt write does not produce successful feedback event. `app/test/assessment_save_failure_test.dart` keeps the form on failed save and succeeds on retry.
- `benchmarking/test_history.py`: serialization/write/fsync/replace faults preserve original bytes, remove temp, release lock, permit retry (separate host history sink, not app SQLite/export).

**Gaps/minimal additions**
- Drive actual native control dispatch for assessment/export/clear failures and encode its result to a Dart replay; existing widget failure is manufactured independently of real native failure.
- Add Dart partial-clear failure cache invalidation/revision assertion and pending-read race above; only success currently covered in session_clear_test.
- `K/DataExporter.kt:36–42,85–91` writes directly to a second-resolution final filename. Existing blocked-directory failure does not prove behavior on partial write/close failure or same-second re-export. Characterize whether a prior export can be overwritten/truncated; choose explicitly whether acceptance requires atomic export publication. If so, add a narrow output writer/clock seam and regression first; do not mislabel host log_utils atomicity as app export atomicity.
- Include fresh reopen after every retryable purge stage in the combined fixture. A failed purge may already have removed files: acceptance is truthful failure + no stale visible cache + safe retry, not impossible all-or-nothing filesystem/SQLite/preferences rollback.

**Files**: extend `T/DataExporterTest.kt`, `T/SessionManagerTest.kt`, `T/MainActivityBoundaryTest.kt`, `app/test/session_clear_test.dart`, `app/test/assessment_save_failure_test.dart`; reuse HostStudyFlow fixture. Production seam candidates `K/DataExporter.kt`, `K/MainActivity.kt`. Acceptance: no success reply for failed durable operation, preserved unrelated fixture data, no duplicate retry rows, all helpers closed on every path; record exactly which failure stage was injected.

## 4. Constructor / cleanup coverage

**Already supported, do not reopen as absent**
- `T/VisionInitializationTest.kt:77–105` executes the actual VisionEngine constructor with fake owned resources through pose/hand/model open/read/interpreter/labels open/read/parse failures, suppressed cleanup exceptions, successful transfer and repeated close. 38–73 covers runtime labels/gold stream closure. This is stronger than the separate Unsafe constructor-bypassed close helper test in ResourceCleanupTest, but still not actual MediaPipe/TFLite release.
- `T/CameraViewOwnershipTest.kt:56–105` executes actual CameraPreviewView constructor at preview/executor/provider/listener failure, includes newer-owner publication during failure and cleanup faults. Early failure preserves A; post-publication failure must not restore dead A or cancel newer C. Existing executor shutdown is asserted.
- `T/SessionManagerTest.kt:106–128` fails actual constructor participant/migration DB work, checks owned helper closed and borrowed probe open; `ResourceCleanupTest` checks later cleanup and framework teardown despite earlier errors.

**Incremental gaps**
- Add model/labels stream close-failure combinations against constructor rollback and original-exception precedence; factory close failures currently target detector/interpreter releases, not an explicit close-only stream matrix.
- Add staged `MainActivity.configureFlutterEngine` collaborator acquisition/rollback test only after extracting a safe injected initialization seam: SessionManager is assigned at line43 before VisionEngine acquisition at51, with no local rollback visible. A thrown configure is not proof onDestroy runs. This is a candidate gap, not a verified leak on installed Android.
- Camera provider-future completion failure and binding failure after listener registration need actual callback-path characterization beyond a factory that throws in `listen`; avoid claiming bind-disabled mocks test CameraX hardware acquisition.

**Files**: extend `T/VisionInitializationTest.kt`, `T/CameraViewOwnershipTest.kt`, `T/ResourceCleanupTest.kt`; optional new `T/ActivityInitializationTest.kt` plus `K/MainActivity.kt` injection seam. Acceptance: original failure preserved, each acquired owned resource receives one cleanup attempt, later cleanup/framework teardown still attempted, borrowed probes/newer owner untouched, successful retry works. Resource accounting is host fake-handle evidence, not native driver leak proof.

## 5. Producer / collector replay

**Already supported**
- `T/BenchmarkModeTest.kt:37–87` executes full synthetic native windows for confirmed/unconfirmed/faulted disposition and prints `NATIVE_RECEIPT_FIXTURE`; arbitrary OEM camera text is transformed to structured digest, reports preserve immutable identity after replacement.
- `benchmarking/study_evidence/20261007/owner_closure_2/replay-executed-producer.py` reads actual JVM XML stdout, writes extracted fixture JSON, and replays both FPS/latency assessment and real isolated history sinks. Missing/unconfirmed/float/extra companion variants fail. It calls `log_collection` directly; it does **not** exercise `read_report` with those exact producer artifacts. It also reconstructs trusted metadata from the report itself, so it is not independent device/build attestation.
- `benchmarking/test_collectors.py` separately covers reader-to-real-history acquisition/privacy/schema/companion faults through mocked subprocess responses. Those tests are not a continuous native producer run. Strict schema minor is already approved.

**Minimal gap closure**
- New `benchmarking/test_host_producer_replay.py` and optional `benchmarking/host_fixture_replay.py`: parameterized fresh XML/manifest input, explicit isolated output directory; reject absent/stale/duplicate mode fixtures, failing/skipped producer tests, invalid IDs or unparseable output. Preserve exact native report/control bytes with hashes; no reconstruction of those payloads.
- Replay through actual `read_report` by mocking only its transport/metadata acquisition. Use separately declared synthetic device/build/setup fixtures and label them as synthetic independent inputs, not hardware attestation; intentionally mismatch them for negative controls. Forbid real subprocess/device execution during this replay. Run FPS/camera-latency/interpreter diagnostic reader-to-sink paths as applicable; interpreter remains diagnostic. Keep direct-sink variants as additional coverage.
- Retain actual baseline producer output separately from intentionally mutated consumer-negative fixtures. Test missing/wrong-run companion, report/companion schema types, publication errors, partial/early windows, dropped response after native confirmation side effect; do not infer undo from RPC timeout. Add native variants only where absent.

**Acceptance**: fresh producer modes extracted exactly once, identity/content provenance retained, both relevant collectors preserve safe counts/traces and fixed rejection reasons, rejected variants never qualify, private markers absent in retained files, original native immutable bytes unchanged after replacement/replay. Any synthetic positive qualification is validator behavior only, never a physical gate closure. Existing historical replay script must not be rerun unchanged because it writes into the old evidence campaign.

## Proposed commands and execution contract (NOT RUN)

Run only after implementation authorization; coordinate the shared build lock with parent. Tests need normal compilation, but no APK build/install/device target. Use the already provisioned Flutter/JDK/project Python; if unavailable, record a blocker rather than install. Define `PYTHON` as the parent's verified Python3.11 executable; system Python3.9 previously lacked broad-suite dependencies.

```sh
# cwd: repo/app/android; targeted host JVM suites, force fresh execution
./gradlew :app:testDebugUnitTest --rerun-tasks --no-build-cache \
  --tests 'com.kumpas.kumpas_app.HostStudyFlowTest' \
  --tests 'com.kumpas.kumpas_app.MainActivityBoundaryTest' \
  --tests 'com.kumpas.kumpas_app.SessionManagerTest' \
  --tests 'com.kumpas.kumpas_app.SessionDatabaseTest' \
  --tests 'com.kumpas.kumpas_app.DataExporterTest' \
  --tests 'com.kumpas.kumpas_app.CameraViewOwnershipTest' \
  --tests 'com.kumpas.kumpas_app.VisionInitializationTest' \
  --tests 'com.kumpas.kumpas_app.ResourceCleanupTest' \
  --tests 'com.kumpas.kumpas_app.BenchmarkModeTest'
# cwd: repo/app; after proposed fixture emission and Dart files exist
flutter test --no-pub test/host_study_flow_test.dart test/session_lifecycle_race_test.dart test/session_clear_test.dart test/practice_flow_test.dart test/assessment_save_failure_test.dart
# cwd: repo; after proposed replay file exists and fresh XML copied to run evidence
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -B -m unittest discover -s benchmarking -p 'test_host_producer_replay.py' -v
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -B -m unittest discover -s benchmarking -p 'test_collectors.py' -v
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -B -m unittest discover -s benchmarking -p 'test_history.py' -v
```

Implementation must add explicit fixture-path transport before these commands become executable acceptance: recommended Gradle test system property `kumpas.hostFixtureDir` passed from a project property of the same name, Flutter `--dart-define=KUMPAS_HOST_FIXTURE_DIR=<same absolute isolated path>`, and Python `KUMPAS_HOST_FIXTURE_DIR` environment variable. These are **proposed new plumbing**, not existing flags. Require a unique scratch/evidence run root with sentinel; refuse default/old-evidence output. Add ActivityInitializationTest to targeted execution if implemented. Parent then performs fresh full suites/analysis, parses XML/machine results rather than trusting cached counts, and reviews diffs/source hashes.

## Remaining choices / blockers

1. Authorize minimal native control/initialization/export injection seams versus accept narrower event-handler-only coverage; do not duplicate business logic in the harness.
2. Decide atomic export preservation requirement before asserting it as an existing contract.
3. Implement a producer manifest/path transport so Flutter/Python cannot silently consume stale fixtures. No fresh result is available from this discovery-only pass.
4. Installed uninterrupted CameraX/channel/UI/store flow, real detector/resource release, hardware timing/thermal, all-sign/multi-signer/model/expert and participant authorization remain outside host closure.

Only this report was intentionally created. No source, existing evidence, protected assets, model/reference/math/XP/layout, or history files were modified.
