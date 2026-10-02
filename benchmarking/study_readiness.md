# Kumpas study-readiness evidence — 2026-10-02

## Verdict

The initial focused software repair landed, and the checks below were executed before final independent review. **Study readiness is not approved; software acceptance remains blocked by important review findings.** Both final reviews have returned: privacy/flow is **NOT YET COMPLIANT / REQUEST CHANGES**; measurement is **PARTIAL / CHANGES REQUIRED**. One consolidated remediation worker is addressing the findings, with regression tests and renewed verification still required. A physical target-class phone is unavailable; live recognition, physical-device sustained throughput, and real camera/display performance remain unverified. No participant collection was performed or authorized.

The results below are a **pre-remediation execution snapshot**, not evidence that the later review findings are fixed. Important findings include silent persistence failure, unbounded capture/benchmark startup, discarded benchmark identity, stale camera-error delivery, misleading retained figures, missing failure/cancellation outcomes, stale/current report isolation, trace-window handling, run-bound setup metadata and concurrent history append. Full independent reports and the remediation brief are retained in `benchmarking/study_evidence/20261002/`.

The owner authorized final verification after an earlier tool-approval timeout. The timed-out command did not run; subsequent verification below ran with renewed authorization. No commits were made. Model/reference assets, feedback math, XP, and unrelated training/evaluation work were outside this repair.

## Interrupted remediation recovery checkpoint

Worker `deleg_8acdfcf2` failed with provider HTTP 429 after editing files; it did not complete the combined remediation or write its final report. The parent recovered the actual transcript, source and command ledger rather than restarting or trusting a completion claim.

Before dispatching recovery batch `deleg_f9058aec`, the parent independently executed the landed partial state on 2026-10-02:

- Forced native suite and Android test compilation: `python3.11 <scratch>/kumpas-privacy-gradle.py recovery-20261002-native.log :app:testDebugUnitTest --rerun :app:compileDebugAndroidTestKotlin`; BUILD SUCCESSFUL, **104 JVM tests, 0 failures/errors/skips**, parsed from 12 XML files in `app/build/app/test-results/testDebugUnitTest/`.
- `flutter analyze --no-pub && flutter test --reporter expanded`: **No issues found; 16 tests passed**.
- `python3.11 -m unittest discover -s benchmarking -p 'test_*.py' -v`: **25 tests passed**. This broader scope includes collector/history concurrency, normalization, parity and reference tests; it is not a like-for-like replacement of the earlier 15 collector tests.

Checked insertion/rollback, pending-capture deadline, late-ID cancellation, posted camera-generation guards, benchmark UUID/copy/correlated completion/report/stop, bounded warmup/retry, outcome accounting, active-report isolation, producer trace bounds/alias, owned-helper teardown and interprocess history locking are landed and covered by this checkpoint. Important plotting, run-bound setup/camera/handoff, safe rejected-report storage, and host/producer window/censoring work remains assigned to the recovery worker. These results are **not** a final post-recovery verification or independent re-review. APKs and instrumentation in the earlier table remain earlier snapshots; no default installed study stores were opened or cleared by the recovery unit-test commands.

Actual native log, inherited command ledger, source hashes and recovery requirements are retained in `benchmarking/study_evidence/20261002/recovery_checkpoint/`. Flutter/Python counts are from actual parent terminal output in this session; no reconstructed full log is represented as an original command capture.

## Pre-review parent execution snapshot

Commands are run from the repository unless another working directory is stated. Scratch means `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch`.

| Check | Actual result | Boundary proved |
|---|---|---|
| `flutter analyze --no-pub` from `app/` | No issues found | Dart static analysis only |
| `flutter test --reporter expanded` from `app/` | 12 tests passed | Mastery, mocked native event/UI flow, timeout/cancellation, cache invalidation, and shell behavior |
| `python3 <scratch>/kumpas-privacy-gradle.py study-final-native-executed-20261002.log :app:testDebugUnitTest --rerun :app:assembleDebug :app:assembleDebugAndroidTest` | BUILD SUCCESSFUL; 88 JVM tests, 0 failures/errors/skips, parsed from 11 test XML files | Actual forced JVM execution, debug/test APK builds; not physical performance |
| `/opt/homebrew/bin/python3.11 -m unittest discover -s benchmarking -p test_collectors.py -v` | 15 tests, OK | Fail-closed collectors, explicit device/run identity, malformed evidence, and isolated history append behavior |
| `python3 <scratch>/kumpas-flutter-release-verify.py` | Release build exit 0 | Executes `flutter build apk --release --target-platform android-arm64`; not release runtime acceptance |
| `python3 <scratch>/kumpas-final-emulator-verify.py` | Exit 0; instrumentation `OK (2 tests)` plus replay `OK (1 test)` | Reinstalled debug/test artifacts on designated emulator, checked installed APK identity, ran isolated deletion and synthetic vision contracts plus hashed 30-frame replay |
| Default study-file SHA-256 snapshots before/after emulator installation and tests | Equal | Existing database/WAL/journal, session preferences and legacy-file presence/bytes preserved where present; not a forensic or logical-store audit |
| Collector validators applied to saved emulator camera report, without invoking history-writing CLI | FPS and latency gates rejected | Emulator cannot pass physical gate; insufficient throughput and missing latency traces cannot become success |

The first native command in this verification round reported the test task UP-TO-DATE. It is **not** the fresh execution evidence. The next command used task option `--rerun`, and the log records `:app:testDebugUnitTest` executed.

### Emulator fixtures

- `SessionDeletionTest.clearsOnlyIsolatedStudyStoresAfterRealMigrationExportAndReopen`: real SQLite migration, synthetic records, actual generated external/internal exports, repeated clear, reopen, fresh identity, and unrelated sentinel preservation. Fixture uses unique target-sandbox roots, database paths and preference namespaces. It does not open the default participant database/preferences.
- `VisionAttemptContractTest.noSignerCancellationAndInvalidTargetKeepAttemptIdentity`: blank synthetic bitmap, invalid target rejection, no-signer terminal identity, cancellation, recycled-bitmap ownership, and repeated engine close. No participant image is used.
- `PipelineParityTest.replayHashedFrames`, `-e targetClass 22`: 30 SHA-checked dataset PNGs through production extraction and attempt result; matching attempt identity and monotonic ordering asserted. **Recorded input, not a live camera or accuracy trial.** Anatomical left/right correctness remains unverified.

Flutter tests mock native channels. Native replay tests call VisionEngine directly. These complementary checks do **not** execute one continuous CameraX → MainActivity channel → Flutter feedback → persisted study session → export/delete user interaction. Final integration/race review and a fully isolated cross-boundary runtime test remain separate acceptance items; no broad end-to-end pass is claimed.

## What changed

### Privacy and deletion

Managed cleanup covers all prior SQLite study rows, original/migrated legacy JSONL and recognized app-owned exports in both storage roots. Successful clear creates one new anonymous participant and retains a completed migration marker. SQLite deletion verifies all four tables are empty before committing, including silent `RAISE(IGNORE)` retention; failed verification rolls back and supports retry. File/DB/preferences cannot be one atomic operation, so partial failures are exposed and Flutter caches are invalidated even on error. Backup/extraction exclusions are tested against compiled resources. Export borrows its database helper; production caller closes it in `finally` under the shared pipeline lock.

Clear does not revoke researcher-held/shared copies, existing remote backups, or guarantee forensic erasure. Those limitations remain explicit.

### Learner/build flow

Shared mastery requires `overallMatch >= 0.8 && recognizedAsTarget` on the same attempt. Identity checks reject stale/duplicate terminal delivery after cancel, clear or replacement. Capture has error/lifecycle recovery and a post-start-response timeout; independent review found that the pending start request is not yet bounded and stale camera errors can invalidate replacement captures. Both are open remediation items. Native target IDs are validated. The R8 repair excludes only the transitive AutoValue compiler processor from MediaPipe runtime; no broad missing-class suppression was added. RGBA frame packing respects row/pixel stride and bounds.

### Measurement

Schema-v2 reports separate analyzer, selected, processed and event rates, full monotonic observation windows, every second bin including silence/stalls, and independent failure counters. The native deadline finishes even without frames once a run starts. Review found that the Flutter warmup gate can prevent such a run from starting, and Dart discards the returned run ID. Native reports retain unique run IDs and model/build/device metadata, but these integration gaps remain open. Trace copying uses a primitive timing-field allowlist; no raw images, landmarks or participant payloads are included.

Latency origin is `analyzer_entry_not_sensor_exposure`. Endpoint `final_analyzer_to_event_ms` includes final-frame work and native feedback dispatch, not sensor acquisition or physical display. Multi-frame collection is separate. Optional native post-frame ACK is an upper bound with endpoint `post_frame_native_ack_upper_bound_not_physical_display`, not display photons. Interpreter-only timing cannot pass the camera gate.

## Camera diagnostic already recorded on emulator

Artifact outside Git: `../kumpas-data/parity/study_20261002_emulator_fps.json` (repository-root relative).

- Run ID: `398562f5-b4a8-4ebb-b8c4-ffe2bfba7c9b`.
- Complete duration: 60 seconds.
- Analyzer frames: 407; mean analyzer throughput: 6.783333333333333 FPS.
- Selected: 102; processed: 101; emitted events: 101; recorded failures: 0.
- Latency traces: 0. Latency p50/p95 are null, not zero.
- Physical FPS gate: false. Host validator also rejects sustained throughput below 24 FPS.

This is a real emulator observation, **not** a target-phone result. It neither satisfies the throughput target nor establishes physical performance. It does not populate or rewrite historical benchmark rows.

## Binary identity

| Artifact | SHA-256 |
|---|---|
| Built debug APK and installed emulator base APK | `5ed5c186a862f48c0a7dbee234ff94d13bbb44e5c498405d6e0e5b9eeebf1595` |
| Release APK | `286bbbee5658d3481970416a821039fd670a3d61ada1680abc9a8fe0e27cf39c` |
| Historical model embedded in both APKs | `1f4543b8fb159dbe9a662f0b37e64b096f717d7527c45b2d7778f34bc0885aeb` |

Release `libapp.so` and `libflutter.so` are ARM64. Other dependency libraries include additional ABIs; that is not evidence of additional supported Flutter targets. Release was built and inspected, not installed for runtime verification. The below-gate offline candidate was not deployed.

## Remaining gates

1. **Independent reviews returned changes required:** important privacy/flow and measurement findings remain under remediation. Batch `deleg_8acdfcf2` failed after partial edits; recovery batch `deleg_f9058aec` is completing the outstanding slices. Regressions, fresh parent verification and independent re-review remain required before software acceptance.
2. **Full isolated native/channel/UI persistence/export/delete flow:** layered unit/instrumentation evidence above is not a single integrated user-flow execution. Cancellation/purge/delivery race acceptance remains separate.
3. **Physical device BLOCKED:** owner has no phone; only `emulator-5554` was connected. Require Helio G/Snapdragon 6-class Android, ≥4GB RAM, front camera, 60–90cm distance, ≥60-second runs and actual lighting/background measurements. Follow `environment_protocol.md`: optimal (>300 lux/plain), low_light (<100 lux/plain), cluttered (>300 lux/complex). Record all 50 signs, multiple consenting signers, confusions including FIVE, failure/cancellation trials, thermal state, serial, APK/model hashes and immutable run IDs. Do not fabricate counts or collect study participants without separate authorization.
4. **Recognition gate remains not met for the newly selected model:** prior frozen Keras 181/203 (89.16%), candidate TFLite 177/203 (87.19%), exploratory reused test only. This repair does not retrain/reselect or resolve untouched-test/signer-independent evidence.
5. **Human/evidence gates remain:** expert linguistic/anatomical correctness, completed validation documentation, study consent/privacy approval and owner/adviser authorization. Software tests do not close these.

Phase 4/5/9a physical performance and Phase 9 full sign/signer matrix remain open. Phase 11 participant collection is not approved. No phone fallback converts emulator checks into these passes.

## Evidence locations

- Durable parent summaries and actual command outputs: `benchmarking/study_evidence/20261002/verification.json`, `emulator_collector_assessment.json`, and the six `study-final-*.log` files in that directory. These contain software/diagnostic evidence, not participant records or raw landmarks. Scratch copies remain available but are not the sole record.
- Worker reports: `<scratch>/kumpas-privacy-resume-report.md`, `<scratch>/kumpas-benchmark-resume-report.md`. Their 77/88 test totals describe different recorded snapshots, not conflicting final totals.
- Parent machine-readable summary: `<scratch>/study-final-evidence-20261002.json`.
- Parent test/build logs: `<scratch>/study-final-native-executed-20261002.log`, `study-final-release-20261002.log`, `study-final-isolated-instrumentation-20261002.log`, `study-final-replay-instrumentation-20261002.log`.
- Before/after hashes: `<scratch>/study-default-store-{before,after}-20261002.json`.
- Saved emulator collector rejection: `<scratch>/study-emulator-collector-assessment-20261002.json`.
- Independent review dispatch `deleg_2fad2803` completed. Full reports are retained as `kumpas-final-flow-review.md` and `kumpas-final-metrics-review.md` in the durable evidence directory. Both request changes; no review is presented as approval. Consolidated remediation batch: `deleg_8acdfcf2`; requirements retained as `kumpas-final-remediation-brief.md`.

Obsidian vault discovery was unsuccessful earlier; no vault note has been created. This repository report is the durable record, not a claim of Obsidian synchronization.
