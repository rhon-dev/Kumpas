# Study readiness implementation plan

> For agentic workers: use subagent-driven-development with strict test-driven-development. Owner approved full focused repair; no physical phone is available.

**Goal:** Repair privacy, app-flow and measurement blockers, verify executable software, and explicitly leave physical-device acceptance pending.
**Architecture:** Keep existing Flutter/native channels and SQLite storage. A narrow managed-file purge and serialized attempt boundary protect deletion; separate monotonic trace/FPS counters replace misleading metrics. No model or feedback-math changes.
**Tech Stack:** Flutter/Dart, Kotlin/Android, CameraX/MediaPipe/LiteRT, Robolectric/JUnit, Python unittest.

## Global constraints
- Preserve model/reference bytes and training/evaluation artifacts; preserve unrelated edits.
- No real participant records, raw video, physical-device claims, or external-copy deletion promises.
- One fresh anonymous participant remains after clear; completed migration marker persists.
- Mastery requires same-attempt `overallMatch >= 0.8 && recognizedAsTarget`; XP/math unchanged.
- Performance boundaries and analyzer/processed/event rates must remain distinct; minimum 60s and real-phone evidence for physical gate.
- Fixes remain uncommitted for user review unless explicitly requested. Record exact commands and red/green output; parent independently verifies.

## Task 1 — managed data purge and backup policy
**Files:** SessionManager.kt, SessionDatabase.kt, DataExporter.kt; new StudyDataFiles.kt if needed; AndroidManifest.xml + res/xml backup rules; SessionManagerTest.kt, DataExporterTest.kt, isolated SessionDeletionTest.kt.
**Consumes:** existing `clearAllData(): Unit`, `export(participantId, db): String` contracts.
**Produces:** same public contracts, synchronous verified cleanup or exception; helper and tests scoped to app-owned paths. Parent handles MainActivity serialization/error integration.

- [ ] Add a regression to existing Robolectric SessionManagerTest creating actual exports plus migration residue and an unrelated sentinel. Example core expectation:
```kotlin
manager.clearAllData()
assertFalse(File(context.filesDir, "attempt_history.jsonl.migrated").exists())
assertFalse(File(context.filesDir, "exports/kumpas_export_old_20260101.json").exists())
assertTrue(File(context.filesDir, "keep.txt").exists())
assertEquals("[]", manager.historyJson())
```
- [ ] Run `./gradlew :app:testDebugUnitTest --tests '*SessionManagerTest*'`; preserve expected absence-assertion failure before production edits.
- [ ] Implement only managed file cleanup, both roots/all prefixes, failure reporting, serialized manager methods, transactional row deletion and durable UUID/migration preference update. Verify a missing file is idempotent; never recursively erase arbitrary app storage. Exclude study stores from legacy/modern backup and transfer. Close export helper via parent integration.
- [ ] Add unavailable storage/deletion failure, repeated clear, reopen, fallback export tests and isolated Android synthetic-data smoke test (never touch default installed participant stores).
- [ ] Run focused and full native suite. Report files, APIs, precise failure semantics and test counts to parent.

## Task 2 — release build, Flutter mastery and attempt handling
**Files:** app/android/app/build.gradle.kts; app/lib/ui/{stats,learn_screen,practice_screen,profile_screen,app_shell}.dart as needed; session repository; app/test/*.
**Produces:** release dependency correction, shared mastery predicate, safe event/error handling, immediate invalidation after clear.
- [ ] Use observed R8 failure as build regression; exclude only `com.google.auto.value:auto-value` processor from MediaPipe runtime while retaining annotations; verify release build rather than blanket `dontwarn`.
- [ ] Add high-score wrong-class mastery regression, run RED, then shared predicate for overall/category/next-sign selection; test exact threshold, cross-attempt noncombination, duplicate and later attempts.
- [ ] Repair smoke test to check actual shell/navigation. Add event-stream tests for success/mismatch/failure/cancel/start error/stale events and clear confirmation/error. Use channel mocks only at platform boundary, not stats logic.
- [ ] Add lifecycle-safe cancellation, bounded timeout and errors; refresh cached stats when clear succeeds. Use `attemptId` echoed by native; ignore stale events after cancellation/disposal. Parent coordinates Kotlin channel contract.
- [ ] Run `flutter test --reporter expanded`, `flutter analyze --no-pub`, and release build after native integration.

## Task 3 — camera/native integration and measured benchmark
**Files:** CameraPreviewView.kt, VisionEngine.kt, MainActivity.kt, BenchmarkMode.kt, new PipelineTrace.kt if needed; corresponding JVM tests; Flutter channel/benchmark trigger; benchmarking/collect_fps.py, collect_latency.py, new collector tests.
**Produces:** `attemptId` per capture; explicit analyzer timing trace and independent counters; monotonic duration-complete report even on stall; app-specific output and fail-closed host collector.
- [ ] Add pure metric tests using supplied timestamps/counts: idle window = zero, ≥60s required, events do not count as frames, trailing zero windows included, invalid duration rejected. Run RED first.
- [ ] Implement wall-clock deadline and separate analyzer/sample/completion/event recording. Avoid retaining raw images/features in reports. Include unique run ID, elapsed duration, counts, per-second rates and failures.
- [ ] Serialize attempts/cancellation and purge against result persistence; validate class ID; close images in finally; report errors. Trace analyzer entry before bitmap work to main-thread event delivery, plus collection interval. UI ack is separately labeled; never subtract native/Dart clock epochs.
- [ ] Integrate narrow channel entry points with structured errors and export helper closure. Add explicit benchmark trigger without replacing approved UI layout (existing settings action is appropriate).
- [ ] Add Python tests for empty/malformed/short/stale/emulator and missing-boundary reports, preserving failed results and serial selection. Correct legacy package ID; interpreter-only results remain diagnostics.
- [ ] Run native/Python tests, compile instrumentation, run isolated emulator paths. Never present emulator metrics as target-phone results.

## Task 4 — integrated verification, review and evidence
**Files:** targeted instrumentation tests, `benchmarking/study_readiness.md`, docs/phase-gates.md (only relevant rows).
- [ ] Run all relevant test suites and `git diff --check`; parse test XML for exact totals.
- [ ] Build ARM64 release and debug/test APKs. Verify embedded model digest unchanged. Install only designated local emulator artifacts, read back installed APK identity/hash.
- [ ] Run isolated deletion instrumentation, existing same-frame replay, and UI success/failure/cancellation/export/clear synthetic tests. State which boundaries are synthetic versus actually camera-fed.
- [ ] Independent spec/quality review of task diffs; resolve important findings and rerun affected tests.
- [ ] Record executable commands/artifacts and remaining blockers. Device testing stays blocked until an actual target-class phone and consenting calibration/trial participants are available; prepare the three-condition checklist without fabricating observations.
