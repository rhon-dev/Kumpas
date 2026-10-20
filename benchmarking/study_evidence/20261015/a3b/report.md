# A3b consumer execution report

Status: IN PROGRESS; not accepted. Sole consumer writer. Parent verification/review required.

Authority: controller/a3a-acceptance-and-consumer-binding.json supersedes historical worker selection without rewriting it. Pinned run 323291af-c067-46dc-bae1-067d62fab10b, manifest SHA256 3279cb7d01075a9192f2566ae5573dd6137a23c6710ef1d0a590b78564fe0fed.

Scope: separate executed native producer plus mocked Python transport and Dart platform-channel replay. No installed E2E, physical performance, recognition, inference, participant stores, device/ADB, training or study acceptance. Native sources and existing production consumers are frozen. New tests/helpers only; no dependency changes or commits.

Command evidence is append-only in command-ledger.jsonl with actual exits and retained logs. Existing unrelated changes were observed and are preserved. Initial attempted binding path at repository/controller was absent; authoritative evidence/controller file was found and read before task brief.

- preflight-feature-red: `/opt/homebrew/bin/python3.11 -m unittest discover -s benchmarking -p test_host_producer_replay.py -v`; exit 1; log `benchmarking/study_evidence/20261015/a3b/preflight-feature-red.log`.

- preflight-green-attempt1: `/opt/homebrew/bin/python3.11 -m unittest discover -s benchmarking -p test_host_producer_replay.py -v`; exit 1; log `benchmarking/study_evidence/20261015/a3b/preflight-green-attempt1.log`.

- preflight-green2: `/opt/homebrew/bin/python3.11 -m unittest discover -s benchmarking -p test_host_producer_replay.py -v`; exit 1; log `benchmarking/study_evidence/20261015/a3b/preflight-green2.log`.

- preflight-green3: `/opt/homebrew/bin/python3.11 -m unittest discover -s benchmarking -p test_host_producer_replay.py -v`; exit 0; log `benchmarking/study_evidence/20261015/a3b/preflight-green3.log`.

- preflight-negatives-coverage: `/opt/homebrew/bin/python3.11 -m unittest discover -s benchmarking -p test_host_producer_replay.py -v`; exit 0; log `benchmarking/study_evidence/20261015/a3b/preflight-negatives-coverage.log`.

- reader-replay-red: `/opt/homebrew/bin/python3.11 -m unittest discover -s benchmarking -p test_host_producer_replay.py -v`; exit 1; log `benchmarking/study_evidence/20261015/a3b/reader-replay-red.log`.

- reader-replay-green: `/opt/homebrew/bin/python3.11 -m unittest discover -s benchmarking -p test_host_producer_replay.py -v`; exit 0; log `benchmarking/study_evidence/20261015/a3b/reader-replay-green.log`.

- collector-faults-coverage: `/opt/homebrew/bin/python3.11 -m unittest discover -s benchmarking -p test_host_producer_replay.py -v`; exit 1; log `benchmarking/study_evidence/20261015/a3b/collector-faults-coverage.log`.

- verified-bundle-red: `/opt/homebrew/bin/python3.11 -m unittest discover -s benchmarking -p test_host_producer_replay.py -v`; exit 1; log `benchmarking/study_evidence/20261015/a3b/verified-bundle-red.log`.

- verified-bundle-green: `/opt/homebrew/bin/python3.11 -m unittest discover -s benchmarking -p test_host_producer_replay.py -v`; exit 0; log `benchmarking/study_evidence/20261015/a3b/verified-bundle-green.log`.

- dart-fixture-loader-red: `/opt/homebrew/bin/flutter test --no-pub test/host_study_flow_test.dart --reporter expanded`; exit 1; log `benchmarking/study_evidence/20261015/a3b/dart-fixture-loader-red.log`.

- dart-fixture-loader-green: `/opt/homebrew/bin/flutter test --no-pub test/host_study_flow_test.dart --reporter expanded`; exit 0; log `benchmarking/study_evidence/20261015/a3b/dart-fixture-loader-green.log`.

- dart-consumer-coverage1: `/opt/homebrew/bin/flutter test --no-pub test/host_study_flow_test.dart --reporter expanded`; exit 1; log `benchmarking/study_evidence/20261015/a3b/dart-consumer-coverage1.log`.

- dart-consumer-coverage-green2: `/opt/homebrew/bin/flutter test --no-pub test/host_study_flow_test.dart --reporter expanded`; exit 0; log `benchmarking/study_evidence/20261015/a3b/dart-consumer-coverage-green2.log`.

- flutter-analyze1: `/opt/homebrew/bin/flutter analyze --no-pub`; exit 1; log `benchmarking/study_evidence/20261015/a3b/flutter-analyze1.log`.

- producer-target-red: `/opt/homebrew/bin/python3.11 -m unittest discover -s benchmarking -p test_host_producer_replay.py -v`; exit 1; log `benchmarking/study_evidence/20261015/a3b/producer-target-red.log`.

- producer-target-green: `/opt/homebrew/bin/python3.11 -m unittest discover -s benchmarking -p test_host_producer_replay.py -v`; exit 0; log `benchmarking/study_evidence/20261015/a3b/producer-target-green.log`.

- flutter-full1: `/opt/homebrew/bin/flutter test --no-pub --reporter expanded`; exit 0; log `benchmarking/study_evidence/20261015/a3b/flutter-full1.log`.

- python-full1: `/opt/homebrew/bin/python3.11 -m unittest discover -s benchmarking -p test_*.py -v`; exit 1; log `benchmarking/study_evidence/20261015/a3b/python-full1.log`.

- python-full-cleanenv: `/opt/homebrew/bin/python3.11 -E -m unittest discover -s benchmarking -p test_*.py -v`; exit 0; log `benchmarking/study_evidence/20261015/a3b/python-full-cleanenv.log`.

- flutter-analyze-green: `/opt/homebrew/bin/flutter analyze --no-pub`; exit 0; log `benchmarking/study_evidence/20261015/a3b/flutter-analyze-green.log`.

- fixture-replay-cli: `/opt/homebrew/bin/python3.11 -E benchmarking/host_fixture_replay.py replay --output /Users/ahronjanl.rafaelahron.0804icloudcom/Documents/Thesis/kumpas/benchmarking/study_evidence/20261015/a3b/replay-1`; exit 0; log `benchmarking/study_evidence/20261015/a3b/fixture-replay-cli.log`.

- output-containment-red: `/opt/homebrew/bin/python3.11 -E -m unittest discover -s benchmarking -p test_host_producer_replay.py -v`; exit 1; log `benchmarking/study_evidence/20261015/a3b/output-containment-red.log`.

- output-containment-green: `/opt/homebrew/bin/python3.11 -E -m unittest discover -s benchmarking -p test_host_producer_replay.py -v`; exit 0; log `benchmarking/study_evidence/20261015/a3b/output-containment-green.log`.

- dart-format: `/opt/homebrew/bin/dart format test/host_study_flow_test.dart test/support/host_fixture.dart`; exit 0; log `benchmarking/study_evidence/20261015/a3b/dart-format.log`.

- flutter-full-final: `/opt/homebrew/bin/flutter test --no-pub --machine`; exit 0; log `benchmarking/study_evidence/20261015/a3b/flutter-full-final.log`.

- python-full-final: `/opt/homebrew/bin/python3.11 -E -m unittest discover -s benchmarking -p test_*.py -v`; exit 0; log `benchmarking/study_evidence/20261015/a3b/python-full-final.log`.

- flutter-analyze-final: `/opt/homebrew/bin/flutter analyze --no-pub`; exit 1; log `benchmarking/study_evidence/20261015/a3b/flutter-analyze-final.log`.

- fixture-replay-final: `/opt/homebrew/bin/python3.11 -E benchmarking/host_fixture_replay.py replay --output /Users/ahronjanl.rafaelahron.0804icloudcom/Documents/Thesis/kumpas/benchmarking/study_evidence/20261015/a3b/replay-final`; exit 0; log `benchmarking/study_evidence/20261015/a3b/fixture-replay-final.log`.

- payload-types-red: `/opt/homebrew/bin/python3.11 -E -m unittest discover -s benchmarking -p test_host_producer_replay.py -v`; exit 1; log `benchmarking/study_evidence/20261015/a3b/payload-types-red.log`.

- payload-types-green: `/opt/homebrew/bin/python3.11 -E -m unittest discover -s benchmarking -p test_host_producer_replay.py -v`; exit 0; log `benchmarking/study_evidence/20261015/a3b/payload-types-green.log`.

- dart-focused-final: `/opt/homebrew/bin/flutter test --no-pub test/host_study_flow_test.dart --machine`; exit 0; log `benchmarking/study_evidence/20261015/a3b/dart-focused-final.log`.

- flutter-full-final2: `/opt/homebrew/bin/flutter test --no-pub --machine`; exit 0; log `benchmarking/study_evidence/20261015/a3b/flutter-full-final2.log`.

- python-full-final2: `/opt/homebrew/bin/python3.11 -E -m unittest discover -s benchmarking -p test_*.py -v`; exit 0; log `benchmarking/study_evidence/20261015/a3b/python-full-final2.log`.

- flutter-analyze-final2: `/opt/homebrew/bin/flutter analyze --no-pub`; exit 0; log `benchmarking/study_evidence/20261015/a3b/flutter-analyze-final2.log`.

- fixture-preflight-final: `/opt/homebrew/bin/python3.11 -E benchmarking/host_fixture_replay.py preflight`; exit 0; log `benchmarking/study_evidence/20261015/a3b/fixture-preflight-final.log`.

- fixture-replay-final2: `/opt/homebrew/bin/python3.11 -E benchmarking/host_fixture_replay.py replay --output /Users/ahronjanl.rafaelahron.0804icloudcom/Documents/Thesis/kumpas/benchmarking/study_evidence/20261015/a3b/replay-final2`; exit 0; log `benchmarking/study_evidence/20261015/a3b/fixture-replay-final2.log`.

## Final handoff — DONE_WITH_CONCERNS (worker implementation only)

Parent independent execution, specification compliance and code-quality review remain required. This is not host task01/03/05 acceptance.

### Implemented / executed

- New `benchmarking/host_fixture_replay.py`: pinned exact parent manifest/run; strict JSON key/schema checks; exact 11 artifact kind/identity/path/length/hash checks; symlink/escape refusal; all42 native source hashes against current checkout and producer precompile ledger; successful non-skipped named producer testcase, full5-case suite, matching stdout/run/ledger/log. Fixed rejection codes. `bundle` transfers verified in-memory bytes alongside their receipt. `replay` mocks only ADB transport/declarative synthetic metadata and forbids real subprocess.run while invoking actual readers/assessors/log_collection and real isolated atomic history.
- New `benchmarking/test_host_producer_replay.py`:31 tests, including mutated isolated manifest/source/producer inputs and real reader→history rejection retention. No valid_report reconstructed positive baseline. Captured native confirmed/unconfirmed/faulted modes each run through FPS and camera-latency collectors; absent faulted companion produces an actual mocked read failure, not JSON. Retained1800 analyzer count, one trace,50ms final-analyzer→event,1ms diagnostic inference; mode/run IDs and byte hashes correlate. All6 collector exits1 are expected rejection, not physical success: immutable native reports say `immutable_only_latest_unverified`, and two modes lack confirmed ownership.
- New `app/test/host_study_flow_test.dart` and `app/test/support/host_fixture.dart`: exact event UTF-8 from current execution's verified bundle enters actual binary messenger EventChannel/model/PracticeScreen; actual sheet content/80%/item and exactly one native-ID ACK verified; stale/duplicate/after-dismiss events rejected. Captured control strings and real native CONTROL_FAILED/EXPORT_FAILED/CLEAR_FAILED codes exercise actual channel/repository models, safe retries, failure/success cache invalidation and revisions, participant replacement/reopen and profile/mastery. Retained exports recomputed against independent scoped native SQLite rows, including actual foreign-participant data and reopened empty export. No Dart SQLite imitation or historical export-path dereference.

### Final verified results

| Evidence | Actual result |
|---|---|
| `payload-types-green.log` |31 focused Python tests,0 failures/errors/skips |
| `python-full-final2.log` |74 full benchmarking tests,0 failures/errors/skips |
| `dart-focused-final.log` |4 tests,4 passed,0 skipped/failed; parsed machine events |
| `flutter-full-final2.log` |79 tests,79 passed,0 skipped/failed; parsed machine events |
| `flutter-analyze-final2.log` |exit0, No issues found |
| `fixture-preflight-final.log` |exit0, exact pinned receipt |
| `fixture-replay-final2.log` |exit0 harness;6 real isolated history rows, six expected collector rejection exits1 |

Machine-parsed counts, consumer source postimages and preservation checks: `final-verification.json`. Durable final receipt: `replay-final2/receipt.json`; history: `replay-final2/synthetic-history.json`; per-mode actual collector stdout and transport/output ledger: `replay-final2/*-stdout.json`, `replay-final2/replay-ledger.json`. Earlier replay roots are retained prior executions, not implicit latest selection.

Exact accepted binding remains run `323291af-c067-46dc-bae1-067d62fab10b`, manifest SHA256 `3279cb7d01075a9192f2566ae5573dd6137a23c6710ef1d0a590b78564fe0fed`. All11 original artifact digests/sizes and42 native source hashes match; all82 protected files and8 accepted A2a files match frozen expected hashes. All908 initially snapshotted existing repository/evidence files unchanged. Historical producer/interface/review/binding records were not rewritten. No production source, dependencies/pubspec/lockfiles/native/Gradle/models/math/XP/layout/history changed.

### RED/GREEN integrity and issues

Feature RED→GREEN is retained for missing preflight CLI, missing reader replay command, missing verified bundle, unimplemented Dart loader, missing named executed producer check, unsafe lexical output escape (mkdir intercepted: no unauthorized output written), and nonobject payload fixed rejection. Existing collector/UI coverage tests are coverage-only; no fabricated production RED. The first collector fault coverage run expected the detailed raw-reader code at the history layer; actual sink intentionally reduces it to `collection read rejected`. Test assertions were corrected to verify both actual boundaries without changing production. Initial Dart harness failures were gauge animation timing and identity-based map matcher usage; corrected only tests. Analyzer-only unnecessary assertions and formatter-expanded if statements were corrected in new tests/helpers; final analysis is clean.

The first full Python run inherited Hermes Python3.14 PIL via environment into Python3.11, causing one dependency import error. No install attempted. Existing `/opt/homebrew/bin/python3.11 -E` ignores injected PYTHON* settings and executes the complete suite successfully; failure log retained. The Dart bridge uses this same `-E` mode.

### Trust/testability limits

- Separate frozen executed JVM producer and currently executed mocked Flutter/Python consumers, not uninterrupted installed CameraX/BinaryMessenger E2E. Native real SQLite/preferences observations belong to the frozen producer, not recreated live persistence in Dart. Transport controls are explicitly staged snapshots; UI startAttempt identity is mapped from native direct AttemptBoundary setup, and UI-only end/cancel transport responses are explicitly synthetic lifecycle scaffolding.
- Local trusted Python stdlib preflight performs cryptography/native-source validation; Dart does NOT claim to implement source verification. Same verified in-memory bytes are sent as base64 and consumed without mutable-path reread. This removes the stale-boolean/payload reread gap, but trusts interpreter, checkout, OS and stdout pipe. It is not an adversarial concurrent-filesystem, executable-authenticity or power-loss proof.
- Native fixture model/device metadata remains robolectric. No synthetic payload is altered to qualify hardware. Native timing is analyzer-entry/event/native UI-ACK semantics, not sensor exposure or physical display.
- Legacy interpreter reader coverage uses an explicitly whitespace-only single-line logcat adapter over the native camera-report bytes and synthetic instrumentation-status transport. No native interpreter-only output/census exists here, none is invented; `diagnostic_valid` is false and this path cannot close any latency gate. Main FPS/camera reader transport is byte-exact and hash checked.
- Mutants exist only in fresh TMPDIR synthetic test roots and are removed by TemporaryDirectory; retained test logs identify executed negative cases. No private markers survive history rows. Historical participant stores are never used.
- No installs/downloads/devices/emulator/ADB/default stores/commits/reset/clean/worktrees/training. Physical, recognition, model/expert/human/study and accepted A2b transport limitations remain open.

### Reproduction

From repository root with existing tooling and scratch TMPDIR:

```sh
/opt/homebrew/bin/python3.11 -E benchmarking/host_fixture_replay.py preflight
/opt/homebrew/bin/python3.11 -E -m unittest discover -s benchmarking -p test_host_producer_replay.py -v
/opt/homebrew/bin/python3.11 -E -m unittest discover -s benchmarking -p 'test_*.py' -v
/opt/homebrew/bin/python3.11 -E benchmarking/host_fixture_replay.py replay --output /absolute/FRESH/path/under/benchmarking/study_evidence/20261015/a3b/NAME
```

Run Flutter commands from app, holding exclusive fcntl lock on `$HOME/.hermes/cache/scratch/kumpas-gradle.lock`, as recorded in command-ledger.jsonl. Use scratch `$HOME/.hermes/cache/scratch/kumpas-a3b` as TMPDIR. No pub invocation:

```sh
/opt/homebrew/bin/flutter test --no-pub test/host_study_flow_test.dart --machine
/opt/homebrew/bin/flutter analyze --no-pub
/opt/homebrew/bin/flutter test --no-pub --machine
```

No fixture environment variable or stale receipt is needed: default discovery and explicit focused/full invocations synchronously invoke pinned preflight/bundle and fail rather than skip if missing/unbound. Replay output must be a fresh canonical nonsymlink path under a3b evidence or Hermes scratch. Parent should freeze the4 new source postimages in final-verification.json while reviewing.
