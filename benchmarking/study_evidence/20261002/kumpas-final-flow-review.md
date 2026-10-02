# Kumpas final study-readiness flow review

## Verdicts

- **Spec compliance: NOT YET COMPLIANT / study readiness remains BLOCKED.** Managed deletion, shared-lock attempt-result invalidation, same-attempt mastery, scoped release dependency repair, and named native clock boundaries are substantially present. The production benchmark trigger does not cover startup stalls or expose its run identity, and capture startup is not fully bounded. Required final integrated execution and physical-phone/owner/adviser gates are not certified by this review.
- **Code quality: REQUEST CHANGES.** A remaining high-priority persistence contract defect can silently lose attempts/assessments while reporting success. Important lifecycle/error-delivery and benchmark handoff defects also remain. This is not a claim that managed deletion itself currently returns false success.
- **Privacy deletion sub-verdict: source-level PASS with evidence limits.** The current production call graph serializes purge/export/result persistence, invalidates pending attempt identities, verifies transactional deletion, propagates cleanup errors, retains a migration marker, rotates to a fresh identity, and explains external-copy limits. Runtime integration is a separate gate.
- **Release dependency sub-verdict: source-level PASS; release execution NOT VERIFIED here.** The repair excludes only the named AutoValue processor dependency from MediaPipe, without replacing MediaPipe or suppressing R8 diagnostics wholesale.

## Scope and method

Repository: `/Users/ahronjanl.rafaelahron.0804icloudcom/Documents/Thesis/kumpas`.

Reviewed working tree against HEAD `693c9852f4c476659e6f359c6e1b5055b3713b83`, the supplied review package, AGENTS.md, PRD, approved `docs/superpowers/specs/2026-10-01-study-readiness-design.md`, implementation plan, and relevant unchanged consumers. Worker reports were read for context, but findings and positive conclusions below are grounded in current source and read-only artifact inspection, not worker verdicts/test totals.

**Restrictions followed:** no code changes, commits, tests/builds, installations, participant-store access, emulator/device actions, or network research. Only this requested scratch report was written. Existing generated manifests/resources and bundled model/reference files were read; those are not participant stores. No project code was executed. Read-only Git commands and a standard-library hashing/XML-comparison script were used.

File/line references below are repository-relative, using the source read during this review. P1 = high priority before study data collection; P2 = important repair before software/handoff sign-off; P3 = nonblocking improvement or explicit deviation to resolve.

## Important findings

### F1 — P1: SQLite insertion failure is swallowed by the session layer, so the UI can report an unsaved attempt or assessment as successful

**Locations:**
- `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/SessionDatabase.kt:122-129,193-215,241-248`
- `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/SessionManager.kt:82-92,145-165,198-201`
- `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/MainActivity.kt:92-96,153-164`

The database insertion methods return the result of `SQLiteDatabase.insert`, but `startSession`, `recordAttempt`, and `saveAssessment` discard it. A failed insert can return a failure row ID instead of throwing. The new MainActivity persistence-error translation catches exceptions only. Consequently, an insert failure can leave no saved attempt while `attempt_result` is still delivered and acknowledged; assessment submission can likewise receive a successful channel response without a stored assessment. A failed session insert is cached as an active UUID and subsequent inserts can be associated with a nonexistent session.

This is **pre-existing in the unchanged SessionManager insertion consumers**, but remains important to the new integration's claim that persistence failure reaches the UI. The new verified `clearAll()` transaction does not fix write-side success reporting.

**Required direction:** fail explicitly on unsuccessful session/attempt/assessment insertion, propagate the failure through the existing structured channel/error paths, and do not retain a failed session as active. Validate this with isolated synthetic persistence failures, including a silently ignored insert; no real participant store is needed.

**Evidence limit:** source-level control-flow defect; no database failure was injected or executed in this review.

### F2 — P2: the settings benchmark trigger never starts a timed run when the camera stalls before its first complete window

**Locations:**
- `app/lib/ui/profile_screen.dart:495-502`
- `app/lib/ui/practice_screen.dart:57-65,164-184`
- `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/VisionEngine.kt:213-238`
- `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/BenchmarkMode.kt:29-58`
- `app/test/practice_flow_test.dart:162-172`

Opening the settings action only pushes a practice screen. `_startBenchmark()` is deferred until a `prediction` or `no_signer` event; those require a full native buffer. A zero-frame camera, early bind failure, or stall before the first full window therefore creates **no run ID, no deadline, and no retained failed/zero-frame report**. The pure/native benchmark deadline is correct **after `start()` is called**, but that does not cover this production trigger path. The widget test explicitly encodes waiting for a full window rather than testing the zero-frame trigger contract.

This leaves the approved end-to-end startup-stall reporting incomplete, despite the README saying an idle/stalled run finishes with honest zeros.

**Required direction:** separate optional camera warmup from initiating the bounded run. An explicit benchmark request must either start a deadline regardless of incoming frames, or record a bounded startup failure as a retained run. Test the actual settings-to-practice trigger without delivering any prediction event.

### F3 — P2: the UI discards the benchmark run ID required by both collectors

**Locations:**
- `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/MainActivity.kt:116`
- `app/lib/feedback_engine/kumpas_channel.dart:50-52`
- `app/lib/ui/practice_screen.dart:116-123,164-176`
- `benchmarking/README.md:30-38`
- `benchmarking/collect_fps.py:230-235`
- `benchmarking/collect_latency.py:89-100`

Native `startBenchmark` returns its UUID, but the unchanged Dart wrapper returns `Future<void>` and the new UI retains/displays no identifier. Completion also shows only a generic message despite receiving a report payload. The documented instruction to retain the returned `$RUN_ID` therefore cannot be followed through the newly exposed settings flow. Both collectors require the independently expected ID to reject stale reports.

A researcher could manually inspect `latest.json`, but that is an undocumented workaround and deriving the expected identity from the artifact being validated weakens the intended start-to-collection binding.

**Required direction:** return/store the native UUID through Dart and expose it in the benchmark handoff UI or another explicit operator-readable channel. Keep expected-run-ID validation; do not remove it to make collection easier.

### F4 — P2: an old unversioned `camera_error` can cancel a replacement attempt

**Locations:**
- `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/CameraPreviewView.kt:80-83,96-99`
- `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/VisionEngine.kt:308-310`
- `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/MainActivity.kt:140-152,166-179`
- `app/lib/ui/practice_screen.dart:66-74,114-115,187-211`

Attempt progress/result/failure are identity-checked twice, including before posted delivery. Camera errors carry no attempt/camera generation, however, and are classified as non-attempt events, so their posted delivery is never invalidated after cancellation, clear, or replacement.

Concrete permitted ordering: analyzer A reports a camera error and posts its delivery while the main thread is already waiting to start attempt B under `pipelineLock`; A releases the lock, B starts successfully, and the queued old error is then sent. Dart `_captureError()` cancels whichever attempt is now current, i.e. B. Bitmap conversion also occurs outside the engine lock, so a stale frame conversion failure can reach `reportCameraError()` after replacement and cancel the replacement natively.

**Required direction:** bind camera/error delivery to an appropriate camera/request generation, or explicitly prevent/reject replacement while an unrecovered camera failure is current. Retain the legitimate UI error, but do not let a stale callback act as cancellation of a different capture. Add a production-boundary ordering regression, not only an AttemptBoundary helper test.

**Evidence limit:** source-derived interleaving, not an executed race reproduction.

### F5 — P2: attempt timeout begins only after the native start response, leaving startup capture unbounded

**Locations:**
- `app/lib/ui/practice_screen.dart:139-156`
- `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/MainActivity.kt:53-65`
- `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/VisionEngine.kt:154-164,195-210`
- `app/test/practice_flow_test.dart:174-184`

`_attemptRunning` is set before awaiting `startAttempt`, but the 30-second timer is installed only after that Future resolves. Native start waits on the same lock held through synchronous detector processing. A stalled start response therefore leaves capture active without any timeout. Existing timeout coverage mocks an immediately successful start and only exercises post-response collection.

This is **already present in HEAD**, not introduced by the benchmark additions, but does not satisfy the complete bounded-attempt requirement.

**Required direction:** bound the request phase as well as sample collection, preserve the generation check, and still cancel a late returned native identity without affecting a newer attempt. A pending-channel Future regression is sufficient to demonstrate the Dart gap; do not claim it proves native deadlock recovery.

## Lower-priority observations

### F6 — P3: the implementation uses a different latency field name than the approved spec

**Locations:** `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/PipelineTrace.kt:36-38`; `benchmarking/collect_latency.py:36-48`; approved spec `:25`.

The spec explicitly names `analyzer_to_feedback_ms`; implementation and collectors consistently use `final_analyzer_to_event_ms`. The implemented boundary is clearly explained and includes the intended final analyzer entry through main-thread event dispatch, so this is not evidence of clock mixing or a false sensor-to-display claim. Add a compatible named field or obtain/document approval for the naming deviation rather than declaring literal spec compliance.

### F7 — P3: the long-lived SessionManager database helper has no explicit Activity teardown closure

**Locations:** `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/SessionManager.kt:37`; `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/MainActivity.kt:198-207`.

Temporary export-helper ownership is correctly repaired, but Activity destruction only ends the session; SessionManager provides no explicit close operation for its owned helper. Repeated Activity recreation can retain open helper resources until collection. This is a pre-existing lifecycle-quality concern, distinct from export closure and not evidence of failed deletion.

## Positive source and artifact checks

### Managed deletion / serialization

- `MainActivity.kt:27-29,50,53,99-114,140-181` supplies its **actual production** `pipelineLock` to VisionEngine. Control-channel persistence/export/purge and native event persistence use this same lock; this is not merely a test lock.
- `MainActivity.kt:107-113` invalidates the AttemptBoundary and pending trace and cancels collection before attempting purge, including on a subsequently reported partial cleanup failure.
- `AttemptBoundary.kt:11-37` rejects invalid targets, duplicate terminals, stale cancellation/ACK, and delivery after invalidation/replacement. `MainActivity.kt:145-147,169` checks incoming and posted attempt events. An old attempt result cannot repopulate the database after a successful clear through this call path.
- `MainActivity.kt:99-105` closes the borrowed export helper in `finally`; `DataExporter.kt:30-43` documents borrowed ownership and propagates file-write exceptions.
- `StudyDataFiles.kt:9-35` limits deletion to recognized export basenames across prior prefixes and the two exact legacy history paths. It covers app-specific external and internal fallback roots, rejects redirected/uninspectable/unexpected storage, verifies deletion absence, and preserves unrelated files rather than recursively wiping storage.
- `SessionDatabase.kt:262-281` performs and verifies four-table deletion within one transaction. `SessionManager.kt:211-226` commits a new UUID and completed migration marker synchronously, verifies fresh participant persistence, and throws on incomplete cleanup. Cross-store atomicity is not falsely promised.
- `app/lib/session/session_repository.dart:67-75` invalidates identity/session cache and signals a revision even after partial native failure. `profile_screen.dart:31-46,536-551` refreshes visible statistics and successful-clear assessment state. `app/lib/ui/app_shell.dart:9-12,27-35` rebuilds other tabs on switching, so absent Home/Learn revision listeners do not by themselves imply post-clear stale tabs.
- `profile_screen.dart:515-519,538-550` explains transferred-copy limits and distinguishes success from failure. No forensic erasure or remote-backup revocation claim is made there.

### Backup and fixture isolation

- Source manifest `:7-9` has legacy/modern policy references and `allowBackup=false`; both XML resources exclude databases, identity preferences, legacy/migrated history, internal exports and external app storage.
- **Independent read-only generated-artifact check:** existing debug merged manifest `app/build/app/intermediates/merged_manifests/debug/processDebugManifest/AndroidManifest.xml:47-55` retains these values. The existing release merged manifest at the analogous release path also parsed to `allowBackup=false`, `fullBackupContent=@xml/study_backup_rules`, `dataExtractionRules=@xml/study_data_extraction_rules`. Both packaged debug/release XML files compared byte-equal to their source counterparts. These artifacts were not rebuilt here; freshness and final APK packaging remain the parent's responsibility.
- `SessionDeletionTest.kt:19-46,54-59,60-96` routes database/files/external roots and preferences to per-run fixture namespaces even though it uses targetContext as its base. The source does **not** open or delete the default participant DB/preferences. It closes tracked fixture handles and removes only its fixture roots/names. This directly corrects the worker report's stale wording about a test-APK context.
- `VisionAttemptContractTest.kt:16-42` uses blank synthetic bitmaps and a local event callback, not SessionManager. `PipelineParityTest.kt:23-92` uses standalone engines and replay artifacts; it does not prove MainActivity persistence or Flutter delivery.

### Integration / scoring / release

- Camera analyzer `CameraPreviewView.kt:54-88` closes ImageProxy in `finally`, recycles local bitmaps, reports processing errors, and measures analyzer entry before conversion. `dispose():105-111` unbinds its owned use cases and shuts down its executor.
- `VisionEngine.kt:81-98,154-164,195-210,313-318` serializes attempt start/cancel/sample completion, closes MPImage in `finally`, and makes engine close idempotent. The timestamp guard prevents a pre-start analyzer frame from becoming the first sample of a newer attempt.
- Main-thread event delivery/ACK is measured using native elapsed time (`MainActivity.kt:75-82,170-174`). Dart ACK is post-frame (`practice_screen.dart:95-103`), labeled an upper bound, not physical display time. Optional missing ACKs are not replaced by zero.
- `stats.dart:3-14,39-51,70-73` applies the same-attempt `overallMatch >= 0.8 && recognizedAsTarget` predicate to count/category/next-sign consumers; Learn uses nextPracticeSign at `learn_screen.dart:186`. XP remains score-only at `learn_screen.dart:63`.
- `widget_test.dart:8-31` now targets the current five-tab shell. Source coverage exists for mismatch, no-signer, cancellation, duplicate result, start exception and post-response timeout; those tests were not run in this review.
- `build.gradle.kts:59-63` excludes only `com.google.auto.value:auto-value` from MediaPipe 0.10.14. The reviewed build diff introduces no blanket `dontwarn`, alternative detector, or runtime replacement. Existing debug signing for release (`:40-45`) remains a separate production-release concern, not a new regression.

### Preservation checks

Read-only Git inspection showed no working tracked diff for training, evaluation, native asset paths, FeedbackEngine/FeatureNormalizer, stats, Home or Learn scoring consumers. VisionEngine's reviewed diff changes serialization, resource/error handling, identity and timing, not feature geometry or feedback comparison math.

The current bundled model SHA-256 was independently computed as `1f4543b8fb159dbe9a662f0b37e64b096f717d7527c45b2d7778f34bc0885aeb`, matching the deployed historical model identity in `docs/phase-gates.md:42`. Current `gold_standards.bin` SHA-256 is `6373ae694a06416b0ccae465ad218dc4f51904ecbccdd21f98b708e0c33617e2`. No independent earlier gold-standard digest was established in this review; do not elevate no tracked asset diff into proof that every ignored artifact byte was preserved.

## Evidence limits and remaining gates

1. **No execution-based acceptance from this reviewer.** I did not rerun Flutter/JVM/Python tests, Gradle/R8, APK builds/install/readback, replay or Android instrumentation. Worker reports' test totals are contextual historical assertions, not my independent test results.
2. The helper tests and mocked Flutter events are useful but do not establish MainActivity-to-SQLite-to-Flutter behavior under persistence failure or the stale camera-error ordering. `AttemptBoundaryTest.kt` tests the helper, not production dispatch scheduling. `session_clear_test.dart:8-34` covers successful repository invalidation, not visible confirmation/error or partial-failure UI behavior.
3. Existing generated backup artifacts corroborate policy merge only; they do not prove a fresh final APK, physical/OEM backup behavior, deletion of past remote copies, or forensic erasure.
4. Required exact APK identity/readback and a successful final release dependency/R8 run remain outside this read-only review. No completion claim is based on the existence of a build artifact alone.
5. **Phone matrix remains BLOCKED.** No phone is available. No physical throughput/latency/recognition, all-50-sign trial, signer-independent score, consented participant result, expert linguistic validation, or owner/adviser approval is inferred. The approved spec `:33-35` keeps these gates separate and prohibits collecting study participants before they are satisfied.
6. The separate model/expert/feature-parity limitations recorded in `docs/phase-gates.md:24-26,35-43` remain untouched. Focused software repair must not be represented as closing those research gates.

## Report deliverable

Created only `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/kumpas-final-flow-review.md`. No repository files were written or committed. Parent should resolve F1-F5 or explicitly justify scope/deviations, then rerun affected tests and final integration verification under its separate authorization. This report does not authorize participant collection or a physical-device pass.
