# Study-readiness review closure implementation plan

> **For agentic workers:** Use `subagent-driven-development` and `test-driven-development`. This is ONE cohesive repair task with vertical RED/GREEN slices. Do not dispatch overlapping implementers.

**Goal:** Repair the remaining verified privacy, report-retention, request-lifecycle, cleanup and setup-contract defects, add missing regression coverage, and obtain fresh independent software review without claiming participant or physical-device acceptance.

**Architecture:** Preserve the existing Android/Dart channels, native monotonic clock, immutable run identity, SQLite ownership and CameraX pipeline. Tighten trust boundaries, committed-file verification and identity-scoped asynchronous cleanup. Keep diagnostic runs usable while failing physical gates closed.

**Tech stack:** Existing Flutter/Dart, Kotlin/Android, SQLite/Robolectric/JUnit and Python unittest. No dependency changes or installations.

## Global constraints

- User explicitly authorized repairs on 2026-10-07 after verification-only work. Preserve unrelated edits, model/reference assets, feedback mathematics, XP and approved UI layout.
- Starting HEAD: `6b8b1b6770e46bea7728a8e9ca4ae6d78e857640`; working tree clean immediately before this plan/checkpoint. Continue the existing repository; no worktree, reset, clean, stash, commit or push.
- No participant records, raw video or raw landmark payloads. Tests use synthetic isolated roots. Never initialize, read, clear or export default installed study stores.
- No APK installation, device operation or physical measurements in this repair task. Parent owns later runtime verification.
- Remain explicit: analyzer-entry/event/ACK boundaries are not sensor exposure or physical display timing. Physical phone, expert validation and participant-study authorization remain separate gates.
- Model asset SHA-256: `1f4543b8fb159dbe9a662f0b37e64b096f717d7527c45b2d7778f34bc0885aeb`. Historical benchmark history must remain byte-identical.
- Do not retrain, replace model assets or modify training/evaluation files. Do not rewrite historical accuracy figures or old evidence.
- Existing pre-repair fresh results: forced 112 JVM tests, 16 Flutter tests, 36 benchmarking Python tests; Flutter analysis clean. These do not prove repaired code.

## Task 1: Complete the latest review findings in vertical slices

**Production files in scope:**
- `benchmarking/collect_fps.py`, `collect_latency.py`, `log_utils.py` only where required for the identified trust/cleanup defects.
- `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/{BenchmarkMode,MainActivity,SessionManager,VisionEngine,CameraPreviewView,AttemptBoundary}.kt`; narrow pure helpers may be added when they are wired into production and improve testability.
- `app/lib/ui/practice_screen.dart`, `app/lib/feedback_engine/kumpas_channel.dart` only for bounded control requests and identity-safe terminal classification.
- `benchmarking/README.md`, `environment_protocol.md` for the actual setup workflow.

**Tests in scope:**
- `benchmarking/test_collectors.py`, `test_history.py`, `test_plot_history.py`, `test_handoff.py`.
- Android `BenchmarkModeTest.kt`, `MainActivityBoundaryTest.kt`, `SessionManagerTest.kt`, `DataExporterTest.kt` and narrowly necessary cleanup tests.
- Flutter `practice_flow_test.dart`; a focused assessment-save-failure test if needed for existing behavior coverage.

**Interfaces:** Keep `startAttempt` and `startBenchmark` returning identities; cancellation/report/stop remain identity-scoped. Preserve named latency fields and generic coded errors. Diagnostic/missing-setup runs remain collectable but cannot pass physical gates. Any required error-code/schema changes must be wired consistently through native producers, both host collectors and tests.

### Slice A — Persisted error-field privacy (P1; checklist 15)

- [ ] Add a failing test using a synthetic marker inside each of `storage_error`, `model.metadata_error`, `setup_errors[]`, `excluded_samples[].reason` for FPS, camera latency and interpreter diagnostics.
- [ ] Assert rejected history contains no marker, while safe numeric timing and known diagnostic codes survive. Include actual `read_report`/collector-to-history paths, not only a detached sanitizer.
- [ ] Run the focused test and record its behavioral RED. Parent reproduced marker persistence in all 12 isolated combinations.
- [ ] Replace unrestricted diagnostic/error text with fixed code vocabularies or generic rejection codes. Unknown content must be dropped or normalized and make the evidence non-gating. Review other fixed-contract text fields for the same class of bypass; do not arbitrarily strip legitimate independently verified device identity.
- [ ] Run GREEN and the complete collector suite. Retain generic parse/collection errors; never echo untrusted keys or raw logcat text.

### Slice B — Verify actual committed report targets (P1; checklist 8)

- [ ] Add behavioral regressions for nonthrowing final-target rename failure for BOTH immutable run publication and `latest.json`, not merely blocked `.new` paths. Use nonempty synthetic target directories/sentinels or a real equivalent fault seam.
- [ ] Record RED. A finishWrite return alone is not evidence of commit success.
- [ ] Read back the exact committed target after each write, verify bytes/expected run identity, and only then advance publication state/path. Fail closed on unreadable, mismatched, absent or incomplete targets.
- [ ] Preserve the pessimistic immutable-only stage; do not promise successful latest publication inside the immutable file. A failed immutable commit must not allow a qualifying latest report. Partial failure must retain safe diagnostics and downgrade the gate/path.
- [ ] Test ordinary successful readback, partial failure, recovery/retry and unchanged unrelated sentinels. Record GREEN and covering native suites.

### Slice C — Pending capture-start timeout reason (P2; checklists 3/7)

- [ ] Extend widget tests to assert a start request timing out before its identity returns later cancels with `outcome: timeout`, not default `cancelled`.
- [ ] Cover no replacement, a newer replacement, ordinary cancellation and disposal. Record RED only for the missing behavior.
- [ ] Retain the request's terminal reason by request/generation until resolution. Late identities must never cancel replacement captures. Wire native ledger accounting so a known old timeout can be recorded safely for a recognized old attempt without invalidating the current one; preserve censoring once a run has closed.
- [ ] Add production-boundary tests for exact outcome, duplicate rejection and preservation of replacement identity. Record GREEN.

### Slice D — Bound pending benchmark start (P2; checklist 5)

- [ ] Add a failing widget regression for a never-returning native benchmark start and a late valid UUID after retry/disposal.
- [ ] Use a 30-second control-response watchdog, separate from the >=60-second measurement deadline. Warmup remains bounded at its existing three-second fallback. UI must recover to the existing retry action without adding a screen or changing layout.
- [ ] Correlate request generation and late run ID. Cleanup may stop only that returned old run; never stop a replacement. Surface/retain failed or partial run diagnostics without claiming a full-duration pass. Avoid unhandled late futures.
- [ ] Record GREEN for stall, retry, late-response, replacement and disposal cases.

### Slice E — Exception-safe resource ownership (P2; checklist 11)

- [ ] Add behavioral fault-injection tests for an early detector close, camera clear/unbind, engine/benchmark Activity teardown and SessionManager constructor/legacy-migration initialization failure.
- [ ] Production cleanup must attempt all owned resources even when an earlier action fails; preserve meaningful errors instead of silently claiming success. Ensure `super.onDestroy()` is attempted. Keep safe repeat-close behavior and resource ownership explicit.
- [ ] Constructor initialization failure must close its own helper before throwing; borrowed handles must not be closed by the wrong owner.
- [ ] Close every synthetic manager/helper created by tests. Existing fresh output contains SQLite CloseGuard warnings; distinguish and eliminate constructor leaks and fixture ownership leaks, not suppress the warning.
- [ ] Record RED/GREEN at the actual production seam. Pure helper tests alone do not prove the helper is wired through engine/camera/Activity paths.

### Slice F — Actual APK/setup qualification and usable handoff (P2; checklist 13)

- [ ] Add producer regression for a correctly shaped but wrong setup APK digest; assert diagnostic/non-gating results.
- [ ] Bind setup digest to the actual installed APK identity using an appropriate existing application source path and streaming digest, with isolated synthetic application-info/file fixtures for JVM tests. Missing/unreadable/unsupported identity is diagnostic, not fabricated qualification. Do this before the timed observation window or explicitly preserve timing semantics.
- [ ] Preserve host independent fingerprint/APK/condition checks and immutable start-time setup capture. Do not imply a manual boolean proves hardware or environment measurement.
- [ ] Document `files/benchmarks/next_setup.json` schema, safe pre-run provisioning, verification sources, actual camera reporting, captured snapshot behavior and retry/error handling. Give a blank/diagnostic template, not invented lux, hardware, APK hashes or verified flags. Examples must be labelled templates, not observed phone data.
- [ ] Record RED/GREEN and producer/consumer contract checks. Existing blank 50-class forms should not be regenerated unless their schema genuinely changes.

### Slice G — Missing permanent failure/boundary coverage

- [ ] Add isolated history serialization, partial-write, fsync and replace failure tests: original bytes survive, temporary files cleaned, lock released and retry succeeds. Parent probes already pass; label these coverage-only GREEN, not invented prior RED.
- [ ] Add actual MainActivity persistence-failure EventSink/accounting and safe retry coverage using synthetic SQLite faults. Existing database failure behavior may pass immediately; record that honestly.
- [ ] Cover assessment save failure without successful navigation if the current test suite lacks it. Keep existing correct behavior unchanged.
- [ ] Reassess all 16 checklist items against final code; report limitations of mocked/channel/direct-native tests. Do not claim a continuous CameraX/Flutter/export/delete acceptance flow without executing one.

### Slice H — Fresh final software verification and self-review

- [ ] Run the forced complete native JVM suite and instrumentation-source compilation through the shared Gradle lock helper. Parse XML tests/failures/errors/skips; distinguish genuine execution from UP-TO-DATE tasks.
- [ ] Run `flutter analyze --no-pub` and `flutter test --no-pub --reporter expanded` from `app/`.
- [ ] Run `/opt/homebrew/bin/python3.11 -m unittest discover -s benchmarking -p 'test_*.py' -v` from repo root, synthetic fixtures only.
- [ ] Inspect full output/warnings and `git diff --check`; self-review scope, identities, privacy, timing and ownership. Do not update readiness/gates to accepted.

## Commands and durable handoff

Use `/opt/homebrew/bin/python3.11`. Gradle wrapper: `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/kumpas-locked-gradle.py LOG TASKARGS...`. It sets JDK 17/SDK and serializes builds with the existing scratch lock. Example tasks: `:app:testDebugUnitTest --rerun --tests com.kumpas.kumpas_app.BenchmarkModeTest`; final `:app:testDebugUnitTest --rerun :app:compileDebugAndroidTestKotlin`.

Create the report **before editing production** at `benchmarking/study_evidence/20261007/repair/repair-report.md`. Append each finding's current state, exact test, RED/coverage-only distinction, GREEN command, exit code and log path immediately after that slice. Keep native/full test logs and an append-only command ledger in that directory so interruption does not lose evidence. Never overwrite old reports/logs.

Worker owns source/tests/setup docs and `20261007/repair/`. Parent owns `.superpowers/sdd/progress.md`, `benchmarking/study_readiness.md`, `docs/phase-gates.md`, consolidated verification evidence and reviewer packages. Parent performs independent verification/re-review after the worker; no acceptance is delegated.

Return DONE / DONE_WITH_CONCERNS / BLOCKED, report path, actual covering/full results and explicit unresolved checklist IDs. Do not return a success claim without a report/evidence. No commits. If interrupted, partial code is not accepted; the report must already describe landed slices.
