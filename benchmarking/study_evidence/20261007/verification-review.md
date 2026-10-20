# Pre-repair verification and findings — 2026-10-07

## Scope and executed evidence

Parent inspected HEAD `6b8b1b6770e46bea7728a8e9ca4ae6d78e857640`, starting clean. Forced `:app:testDebugUnitTest --rerun :app:compileDebugAndroidTestKotlin` succeeded: XML confirms 112 JVM tests, zero failures/errors/skips. Flutter analysis reports no issues; 16 Flutter tests passed. Full `benchmarking/test_*.py` discovery passed 36 tests. These are pre-repair software results, not APK installation, continuous camera/channel/UI/export/delete acceptance, physical measurements or human validation.

Machine-readable primary evidence: `verification-before-repair.json`. Native full actual output: `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/terminal-output/out-1791345633-1939-6060.log`; parsed suite results are in the JSON. Flutter/Python outputs were actual terminal results in this session; this summary is not a reconstructed full command log.

The parent did not modify tracked files, detector/model assets, default study stores or benchmark history during verification. Current plots were visually inspected and show no measured camera-pipeline data, physical-device acceptance BLOCKED, historical/interpreter exclusions and no conversion of missing/rejected data to zeros. Quarantine hashes match provenance. Existing blank forms match the actual dense 50-class label map: 2 candidate slots, 6 condition cells, 300 trial rows and 300 confusion rows; 15,000 prediction cells are blank. These are not acquired phones or observations.

## Latest independent reviews

Read-only batch `deleg_aad57df3` completed both native/Dart and host/setup reviewers. Both require changes. Full completion text is preserved in conversation history; tool transcripts are `.hermes/cache/delegation/live/deleg_aad57df3/task-0.log` and `task-1.log`. Neither reviewer edited files or ran tests. Their source/test-definition evidence does not substitute for the parent's execution.

## Findings requiring repair

1. **P1 collector trust boundary (checklist 15):** recognized `storage_error`, `model.metadata_error`, `setup_errors[]`, `excluded_samples[].reason` use unrestricted bounded TEXT. Parent executed 12 isolated sink probes (each field across FPS/latency/interpreter diagnostics); the synthetic marker persisted in every rejected record. No real participant leakage was inspected or observed. Primary locations: `benchmarking/collect_fps.py:368–379,409–440`.
2. **P1 report retention/publication (checklist 8):** immutable/latest AtomicFile finishWrite is treated as commit success without exact target readback. Nonthrowing final rename/sync failures are not covered. This is source-derived; the app-level fault path has not yet been reproduced. Primary location: `BenchmarkMode.kt:280–315`. Require actual committed bytes/run identity before declaring publication and preserve non-gating partial evidence.
3. **P2 pending capture timeout accounting (checklists 3/7):** the UI timer restores capture, but a late returned identity is cancelled with default cancelled rather than its known timeout reason. Replacement cancellation protection must survive the repair. `practice_screen.dart:153–162,206–215`; `kumpas_channel.dart:43–44`.
4. **P2 exception-safe cleanup (checklist 11):** sequential VisionEngine closes and CameraPreview clear/unbind can skip later cleanup; Activity exceptions can skip super.onDestroy. SessionManager initialization has no own-helper cleanup when ensureParticipant/migration throws. Fresh JVM output includes CloseGuard warnings at constructor and fixture paths; do not label every warning production leakage without isolating ownership. `VisionEngine.kt:322–327`; `CameraPreviewView.kt:118–125`; `MainActivity.kt:211–225`; `SessionManager.kt:37,50–55`.
5. **P2 setup operational/qualification gaps (checklist 13):** required app-private `benchmarks/next_setup.json` schema/provisioning is missing from README/environment protocol. Native checks APK digest syntax only and can expose a weaker native physical flag; host independently compares installed APK and rejects disagreement. No host false pass demonstrated. `BenchmarkMode.kt:74–148,277`; `collect_fps.py:295–306,425–426`.
6. **P2 unbounded benchmark control start (checklist 5):** warmup is bounded, but the awaited native start response has no deadline and leaves _benchmarkStarting blocking retry. `practice_screen.dart:172–190`.

## Coverage and verified behavior, not reasons to restart

Checked insertions, migration rollback, posted camera generation filtering, valid benchmark UUID/copy/report/stop identity, producer/host half-open windows/censor accounting and latency alias are substantially implemented and existing tests pass. Keep them. Additional production EventSink persistence-fault/retry and assessment save-failure coverage are missing. Direct native and mocked Flutter tests still do not prove a continuous CameraX/user flow.

Parent additional history fault probes for serialization, partial write, fsync and replace all preserved original bytes, cleaned temporary files, released the lock and allowed retry. Repository history hash stayed unchanged. These behaviors are verified, but permanent regressions for these fault paths are absent; add coverage-only tests without inventing behavioral RED evidence.

## Authorization and next gate

User explicitly selected: **Repair defects using regression-first tests; preserve unrelated edits, model assets and participant stores.** Applicable plan: `docs/superpowers/plans/2026-10-07-review-closure.md`. One cohesive implementer, no commits or overlapping source writes. Require report/command ledger early, real behavioral RED/GREEN for new repairs, fresh complete suites and independent re-review. Do not label study readiness approved. Physical phone, human validation and participant collection remain unavailable/unapproved respectively.
