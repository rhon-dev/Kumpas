# A1 implementation evidence

Status: A1 implementation and focused host verification complete; parent independent review/acceptance still required.

Baseline: existing dirty repairs preserved. Read binding brief/design and exporter/form tests before editing. SessionManager matcher and caller serialization inspected; no changes authorized outside A1.

- `scoped-red`: exit 1; [scoped-red.log](scoped-red.log); command in ledger.
- `scoped-green`: exit 0; [scoped-green.log](scoped-green.log); command in ledger.
- `unique-red`: exit 1; [unique-red.log](unique-red.log); command in ledger.
- `unique-green`: exit 0; [unique-green.log](unique-green.log); command in ledger.
- `partial-red`: exit 1; [partial-red.log](partial-red.log); command in ledger.
- `partial-green`: exit 0; [partial-green.log](partial-green.log); command in ledger.
- `publication-red`: exit 1; [publication-red.log](publication-red.log); command in ledger.
- `publication-green`: exit 0; [publication-green.log](publication-green.log); command in ledger.
- `readback-red`: exit 1; [readback-red.log](readback-red.log); command in ledger.
- `readback-green`: exit 0; [readback-green.log](readback-green.log); command in ledger.
- `cleanup-coverage-green`: exit 0; [cleanup-coverage-green.log](cleanup-coverage-green.log); command in ledger.
- `optional-red`: exit 1; [optional-red.log](optional-red.log); command in ledger.
- `optional-green`: exit 0; [optional-green.log](optional-green.log); command in ledger.
- `final-jvm`: exit 0; [final-jvm.log](final-jvm.log); command in ledger.
- `final-flutter`: exit 0; [final-flutter.log](final-flutter.log); command in ledger.

## Outcome and changed paths

- `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/DataExporter.kt`: summary counts are computed from the participant-scoped nested arrays. UUID-suffixed names retain the managed prefix; exclusive destination/staging reservation prevents overwriting previous exports. Stream close completes before publication; exact staging and destination bytes are read back before a success path is returned. Failures remove owned new artifacts without closing the borrowed database.
- New adjacent `ExportPublication.kt`: narrow open/publish/read fault seam; production publication uses same-directory rename to its exclusively reserved destination.
- `app/android/app/src/test/kotlin/com/kumpas/kumpas_app/DataExporterTest.kt`: isolated synthetic SQLite/export roots, fixed-time repetition, scoped counts, partial/close/publication/readback faults, retry/borrowed-helper checks, sentinel preservation and actual managed purge of observed staging/final names in external and internal roots.
- `app/lib/ui/assessment_screen.dart`: only removed the optional-feedback nonempty completion condition. Required confidence/signs/SUS checks and layout remain unchanged.
- `app/test/assessment_save_failure_test.dart`: preserved the prior save-failure/retry test; added real widget interactions proving missing required answers block submission and all required answers plus empty feedback persist the expected post payload.
- Evidence: this report, append-only command ledger, per-run logs, final XML snapshots, `verify.py`, `verification.json`, `diff-check.log`, and a reproducible runner copy.

## Regression evidence (actual executions)

| Slice | RED | GREEN |
| --- | --- | --- |
| Participant-scoped count | scoped-red: 52 tests, 1 failure (global count vs nested rows) | scoped-green: exit 0 |
| Same-time export preservation | unique-red: 53 tests, 1 failure (same returned file) | unique-green: exit 0; subsequently fixed clock made repetition deterministic |
| Partial-write artifact cleanup | partial-red: 54 tests, 1 failure (new partial artifact remains) | partial-green: exit 0 |
| Staged publication failure | publication-red: 56 tests, 1 failure (success returned without publication seam) | publication-green: exit 0 |
| Committed readback/corruption | readback-red: 59 tests, 2 failures (success despite read fault/corrupt bytes) | readback-green: exit 0 |
| Empty optional post feedback | optional-red: 1 widget failure, existing retry test passed; completed form button remained disabled | optional-green: 2 widget tests passed |

Close failure and error-after-rename coverage were already GREEN under the shared failure cleanup when added; they are not claimed as separate independently reproduced defects. Silent-short-write verification and exact managed-name purge are likewise coverage-only GREEN. The publication seam was introduced as a behavior-preserving I/O extraction before injected behavioral RED runs; no compilation failures are counted as RED.

## Fresh verification

- `final-jvm.log`: targeted command from the brief, forced test task execution with `--rerun`, exit 0. Parsed XML: **22 DataExporter + 39 SessionManager = 61 tests**, zero failures/errors/skips.
- `final-flutter.log`: `flutter test --no-pub test/assessment_save_failure_test.dart --reporter expanded`, exit 0, **2 tests passed**.
- `verify.py`: exit 0; **82/82 protected expected SHA-256 hashes match**. Exact source hashes and copied final XML are recorded in `verification.json`.
- `git diff --check`: exit 0 (`diff-check.log`). Own source/test diff and adjacent helper reviewed. Full baseline comparison finds only four assigned existing paths plus `.superpowers/sdd/progress.md`; this agent did not modify the latter. The new helper is included in the source hash map.
- Existing JDK17 and Android SDK were discovered locally. Every Gradle/Flutter run used session scratch TMPDIR and an exclusive Python `fcntl.flock` on `~/.hermes/cache/scratch/kumpas-gradle.lock` (no flock CLI was installed). No downloads or installs.

## Compatibility and limits

- Inspected `MainActivity`: export/persistence/purge share `pipelineLock`; caller owns the database and closes it in finally. No caller or SessionManager changes made.
- `SessionManager.clearAllData` delegates to `StudyDataFiles.purge`; its exact filename matcher accepts both the UUID destination and `stage-` name in the alphanumeric/hyphen identity segment. Executed the real purge against observed names in isolated fixture roots, retaining unrelated sentinels. No matcher changes needed.
- Reservation may leave an empty destination or staging artifact after process interruption; both are managed/purge-recognized. No successful export path is returned until closed bytes are published and verified. This is failure-safe host behavior, **not a forensic-erasure or power-loss durability guarantee**. Cleanup errors remain errors and retain a suppressed retry-purge diagnostic; no broad cleanup is performed.
- Initial Gradle run warned about SDK XML version compatibility; final JVM run reports existing Gradle deprecations. Both completed their tests; warnings are retained in logs.
- No emulator, phone, ADB, APK rebuild, default installed participant store, training, schema/math/XP/layout/model/reference/history edits, commits or pushes. This slice does not accept remaining host tasks, installed runtime or study/physical-performance gates.
- Parent must independently review and verify A1 before proceeding with coupled work.
- `parent-jvm-1`: exit 0; [parent-jvm-1.log](parent-jvm-1.log); command in ledger.
- `parent-flutter-1`: exit 0; [parent-flutter-1.log](parent-flutter-1.log); command in ledger.
