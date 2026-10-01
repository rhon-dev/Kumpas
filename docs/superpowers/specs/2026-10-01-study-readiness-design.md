# Study readiness repair — approved scope

Date: 2026-10-01. Owner approved the full focused repair in conversation and confirmed no phone is available. Subsequent instruction: continue the interrupted task. This authorizes software repairs and isolated synthetic-data tests, not collection of participant data or a physical-device pass.

## Boundaries

Keep the installed historical model, training/evaluation work, feedback comparison math, XP, and approved visual layout unchanged. Use the existing Android/Flutter stack. No real participant data or video in tests or Git. No claim of forensic erasure, deletion of researcher-held copies, linguistic validation, signer independence, or physical-device performance. Existing expert-documentation and model/feature-parity gates remain separate.

## 1. Study-data deletion

Clear All cancels/invalidate pending attempts and serializes persistence, export, and purge operations. It removes prior participants, sessions, attempts, and assessments from SQLite; both `attempt_history.jsonl` and `attempt_history.jsonl.migrated`; and only Kumpas-generated export files in both app-specific external storage and the internal `filesDir/exports` fallback. Handle all prior participant prefixes. Preserve unrelated files and bundled model/reference assets. Keep one fresh anonymous participant after a successful clear, matching the existing identity contract. Retain a completed migration marker so old history cannot silently reimport.

Delete is idempotent and verifies managed-file absence. A missing file is success; inaccessible storage, failed file deletion, or failed persistence must return an error, not an all-data-deleted success. Filesystem and database operations cannot be one atomic transaction: surface partial failure and allow safe retry. Use a transaction for database row deletion and a synchronous identity preference commit. Close export database handles. Prevent in-flight pre-clear results from repopulating the cleared database. Refresh cached Flutter history/statistics/assessment state after success. The confirmation explains that copies already transferred elsewhere require separate deletion. Do not promise forensic flash sanitization or revocation of existing remote backups.

Explicit Android legacy and modern backup/extraction exclusions protect study stores from future cloud backup/device transfer. Verify merged manifest/resources, not just source XML. Synthetic regression cases cover real export paths, migration residue, repeat clear, reopen, preservation of an unrelated sentinel, and failed cleanup.

## 2. Build and learner flow

Repair the release build's confirmed transitive AutoValue annotation-processor runtime dependency without suppressing all R8 diagnostics or replacing MediaPipe. Update the stale shell smoke test to exercise the current app shell. Implement the already-approved same-attempt mastery predicate (`overallMatch >= 0.8 && recognizedAsTarget`) across count/category/next-sign consumers; do not alter feedback scores or XP.

Add coverage for attempt success, classifier mismatch, no signer, cancellation, start errors, and duplicate/stale results. Introduce attempt identity where necessary; invalid class IDs fail explicitly. Camera callbacks always close ImageProxy; camera/processing errors reach the UI instead of indefinite capture. Native cancellation and sample completion must be serialized. Use bounded attempt timeout/retry and lifecycle cleanup. A synthetic event test proves UI logic only; recorded-frame replay proves the native extraction/feedback path only. Neither is a live recognition measurement.

## 3. Honest performance measurement

Measure with native monotonic time at analyzer entry before bitmap conversion through extraction, classifier, feedback, persistence, and main-thread feedback dispatch. Name this `analyzer_to_feedback_ms`; it excludes sensor/driver acquisition before analyzer delivery. Record the multi-frame collection interval separately. Optional Flutter post-frame acknowledgment uses native elapsed time on the return callback and is labeled presentation-ack upper bound, not exact display photons or subtraction of unrelated clocks.

Count delivered analyzer frames, stride-selected frames, completed processed frames, and emitted result events separately. Analyzer throughput is not sensor FPS, display FPS, or full-detector throughput. A wall-clock deadline closes the benchmark even with zero frames. Fixed per-second windows include zeros and trailing stalls. Use app-specific storage and unique run IDs; failed/stalled runs are retained. Provide an explicit trigger, collect device/condition/build/model metadata, and correct the host's application ID. Collector validation rejects short (<60s), malformed, stale, empty, emulator-as-physical, and boundary-mismatched reports. Preserve legacy interpreter-only benchmark as diagnostic, never label it camera-to-feedback.

Keep PRD targets ≥90% recognition, <150ms latency, sustained 24–30 FPS. Report p50/p95 for the named latency boundary; do not weaken targets using the contradictory old 80%/20FPS QA allowances. Do not imply the stride-sampled detector processes 24–30 samples/s.

## 4. Verification and phone handoff

Run failing regressions before each behavior repair, then full Flutter, JVM, Python collector tests, release/debug builds, and targeted synthetic Android instrumentation. Installation/readback must confirm APK/model hashes. Do not clear arbitrary installed user data; device deletion tests use an isolated fixture context/storage or disposable test application. Verify full attempt/feedback UI with recorded test events separately from actual native replay/persistence. Record evidence and failures in a readiness report.

Phone matrix remains BLOCKED: no phone available. Prepare named target-class Helio G/Snapdragon 6, ≥4GB RAM checklist, front-camera selection, conditions optimal (>300 lux/plain), low light (<100 lux/plain), cluttered (>300 lux/complex), consistent 60–90cm distance, ≥60s sustained runs, per-sign attempts/confusions including FIVE, failed/cancelled trials, app/APK/model hashes and thermal state. All 50 signs and multiple consenting signers require actual observed trials; no invented counts/results. Do not collect study participants until privacy, app flow, required device evidence, and owner/adviser gates are satisfied.

## Baseline evidence

`flutter analyze --no-pub`: passed. `:app:testDebugUnitTest`: 44 tests passed. `flutter test`: one stale shell assertion failed. ARM64 release build: failed at R8; dependencyInsight traces `com.google.auto.value:auto-value:1.8.1` to MediaPipe tasks-vision 0.10.14 runtime. ADB: only emulator-5554. Source confirms no export/JSONL cleanup and event-counted FPS. None of these are post-repair verification.
