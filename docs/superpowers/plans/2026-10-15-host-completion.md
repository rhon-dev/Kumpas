# Host-only Completion Implementation Plan

> For agentic workers: use subagent-driven-development with one source implementer at a time, task-scoped independent reviews and final whole-change review. No commits are authorized.

**Goal:** Finish the approved host-only portions of all16 owner tasks with executed evidence and explicit blocked dispositions for research/training decisions.

**Architecture:** Reuse production native/Dart/Python seams; join executed artifacts across explicitly separate host processes. Synthetic fixtures use isolated roots and fresh manifests. No mocked transport is described as installed integration.

**Tech Stack:** Existing Flutter/Dart, Kotlin/JVM/Robolectric, Python3.11, TensorFlow environment, MediaPipe environment and Android build tools; no installations.

## Authorization and global constraints

The owner replied `continue` after reviewing the written design and approval question. This authorizes the recommended host-only implementation in docs/superpowers/specs/2026-10-15-host-completion-design.md. Actual retraining and unapproved research scoring remain separate gates, exactly as presented.

- Work in the verified existing dirty repository; no worktree/reset/clean/stash/commit/push.
- No emulator, phone, ADB or default participant-store operations.
- Preserve all82 protected original hashes, model/reference assets, historical evidence, feedback mathematics, XP, approved layout and unrelated work.
- Record actual RED/GREEN output incrementally; already-green characterization is not a repair.
- Use session scratch TMPDIR; existing environments only. Serialize Gradle/build and compute-heavy execution.
- Parent owns status/index/final acceptance. Implementers write only their assigned source/tests and evidence folders.
- Every task requires source/test review and parent verification, not worker self-report alone.

## Execution order

### Package A1: export and questionnaire contracts (host tasks3 and11, partial)

Files: app/android/app/src/main/kotlin/com/kumpas/kumpas_app/DataExporter.kt; corresponding src/test/kotlin/.../DataExporterTest.kt; app/lib/ui/assessment_screen.dart; app/test/assessment_save_failure_test.dart. A small adjacent export-publication helper and its tests are allowed if needed for injected faults.

Interfaces remain `DataExporter(context).export(participantId, db): String` and AssessmentScreen(isPost: true). Database helper is borrowed; callers retain ownership. Existing export JSON structure and purge-recognized filename prefix remain compatible.

- [ ] Inspect existing tests, SessionManager managed-export matcher and caller serialization before editing.
- [ ] RED: create two participants with attempts; export one and independently sum its nested attempts. Assert summary total equals that scoped payload, not global DB count.
- [ ] GREEN: derive total_attempts from the exported session arrays. Do not widen data inclusion or change DB schema.
- [ ] RED: partial/close/publication failures cannot corrupt prior completed export; repeated same-time exports cannot overwrite prior data. Verify no success path is returned on failure and borrowed DB remains usable.
- [ ] GREEN: introduce minimal injected publication seam, unique destinations and safe staging/publication/readback with cleanup. Preserve unrelated sentinels and recognize every temporary artifact in owned cleanup. Never claim forensic/power-loss guarantees.
- [ ] RED: post form with required answers but empty optional feedback can submit; missing required response cannot submit. Existing save-failure/retry remains.
- [ ] GREEN: remove only `_openFeedback.isNotEmpty` from completion requirement; keep required response checks and layout.
- [ ] Run focused JVM exporter/SessionManager tests and Flutter assessment tests; append commands/exits/log paths after each slice.
- [ ] Parent independently verifies and reviews A1 before remaining coupled app changes.

Illustrative summary assertion, adapted to existing fixture API rather than inventing one:
```kotlin
val payload = JSONObject(File(exporter.export(participantA, database)).readText())
val sessions = payload.getJSONArray("sessions")
val actualCount = (0 until sessions.length()).sumOf {
    sessions.getJSONObject(it).getJSONArray("attempts").length()
}
assertEquals(actualCount, payload.getJSONObject("summary").getInt("total_attempts"))
```

Target command from app/android under shared lock:
```sh
./gradlew --offline :app:testDebugUnitTest --rerun --tests 'com.kumpas.kumpas_app.DataExporterTest' --tests 'com.kumpas.kumpas_app.SessionManagerTest'
```
From app:
```sh
flutter test --no-pub test/assessment_save_failure_test.dart --reporter expanded
```

### Package A2: lifecycle/resource gaps (host tasks2,3,4)

Inputs: discovery/app-host-audit.md sections2–4, SessionManager.kt and tests, session_repository.dart, session_lifecycle.dart, session_clear_test.dart, VisionInitializationTest.kt, CameraViewOwnershipTest.kt, MainActivity.kt.

- [ ] Reproduce repeated pause/pause/resume timer and pending response-after-clear cases using deterministic Looper/Completer orderings.
- [ ] Repair only demonstrated races with generation/ownership guards or timer cancellation consistent with existing terminal ownership policy.
- [ ] Add partial-clear failure cache invalidation and safe retry coverage.
- [ ] Add acquired-stream close faults and activity construction rollback through minimal production-used seams.
- [ ] Preserve original exceptions, later cleanup attempts, newer ownership and borrowed handles.
- [ ] Focused execution, complete findings ledger and independent review.

Exact code edits depend on reproduced behavior; a task-local brief must be written from current source before dispatch. No hypothesis is marked a verified defect in advance.

### Package A3: cross-process host artifacts (host tasks1,5)

New HostStudyFixture.kt/HostStudyFlowTest.kt, app/test/host_study_flow_test.dart, benchmarking/host_fixture_replay.py and test_host_producer_replay.py; narrow MainActivity control dispatch seam and Gradle fixture-path forwarding if needed.

- [ ] Generate fresh versioned native event/control/export/clear/reopen envelopes under unique isolated roots.
- [ ] Manifest binds source hashes, run identity, producer success and artifact hashes; negative tests reject stale/missing/duplicate/failed/skipped outputs.
- [ ] Consume exact event bytes in Flutter with explicit mocked transport; assert UI/ACK and actual native state snapshots without claiming shared runtime SQLite.
- [ ] Replay exact native benchmark output through readers, assessment and isolated history with real subprocesses forbidden and independent synthetic metadata controls.
- [ ] Preserve existing confirmed/unconfirmed/publication-fault outputs and diagnostics, then execute complete layered scenario and review.

### Package B: external parity and provenance (host tasks6,8,10; task9 tooling only)

Inputs: discovery/model-host-audit.md. Files: benchmarking/pipeline_parity.py and tests; training/models/{evaluation_protocol,freeze_selection,evaluate_frozen}.py; training/tflite_export/export_frozen.py; training/tests/. New analysis/campaign helpers should remain narrow and versioned.

- [ ] Tighten schema, digest, identity, exact-type and finite-vector validation regression-first.
- [ ] Bind derived arrays, original-row equality, label semantics and finite metric checks through a new immutable campaign manifest. Do not rewrite old freezes.
- [ ] Run import probes in existing environments; generate six validation clip PNG/reference fixtures outside Git, sequentially.
- [ ] Run validation-only frozen Keras/candidate diagnostics and record real per-clip/class results and drift; do not tune on reused test.
- [ ] Prepare isolated bounded experiment tooling without running retraining. Log task9 as awaiting separate local-training/budget approval.
- [ ] Execute relevant unit suites, inspect actual outputs and obtain review. Keep anatomical/signer/final-test limits explicit.

### Package C: artifact and research utilities (host tasks7,11–12)

New benchmarking/inspect_release.py and test_inspect_release.py; evaluation/ explicit-file validator/descriptive modules and synthetic tests. Reference discovery/tooling-host-audit.md.

- [ ] Test malformed manifests, protected mismatches, ZIP duplicate/missing entries, wrong ABI/model/label assets and immutable output behavior before implementation.
- [ ] Inspect existing and final built APKs, separating historical hash match from fresh source provenance.
- [ ] Test actual legacy exporter shape including JSON-encoded responses, UUID relations, duplicates, finite/range rules and independently computed counts.
- [ ] Add safe diagnostics and synthetic paired/descriptive plumbing, no free-text echo or guessed group/consent/withdrawal.
- [ ] Keep human rubric scoring/inferential analysis blocked pending approved instrument/missingness/rater/statistical decisions. Do not use model confidence as a human score.
- [ ] Execute tests and sample synthetic CLI paths; independent review.

### Package D: documentation and final acceptance (host tasks13–16)

Parent-owned current status/index, reproducible handoff, proposed architecture records and final evidence.

- [ ] Reconcile all16 dispositions against actual implementation/execution/review; preserve historical reports.
- [ ] Link existing blank handoff forms; keep hardware/trial/approval values blank.
- [ ] Record architecture deviations as proposed approval-pending, never forged approval.
- [ ] Run full Flutter analysis/tests, forced JVM, broad Python/training/evaluation tests using appropriate existing environments.
- [ ] Compile instrumentation sources, build debug/test and ARM64 release through shared lock; no installation.
- [ ] Parse counts/exits, inspect ZIP/model/ABI identity, compare82 protected hashes, freeze all changed tracked/untracked source and obtain broad independent reviews.
- [ ] Report only verified completion; retain installed/physical/human gates and specifically blocked conditional tasks.

## Durable execution records

Each package gets benchmarking/study_evidence/20261015/<package>/report.md, command-ledger.jsonl and unique actual logs. Reports begin before source changes and are appended after every slice. Baseline file hashes live in controller/host-baseline.json. Parent reads full reports and source deltas before acceptance. A failed worker is recovered from landed state, never restarted blindly.
