# Independent QA — Phase A3b review 1

## Verdicts

- **Specification compliance: REQUEST CHANGES — one bounded producer-ledger type-validation gap (F1).** Exact-artifact binding, current-execution byte transfer, Flutter consumer assertions and actual reader-to-isolated-history replay otherwise meet the reviewed host-only requirements. The actual selected producer evidence is valid; F1 is a reproduced failure of the required malformed-input rejection contract, not a claim that the selected native execution failed.
- **Code quality: REQUEST CHANGES — Medium F1; no Critical/High finding.** Correct the small provenance-validator gap and add regression coverage before bounded A3b acceptance. No production/dependency/native change or regenerated producer artifact is needed.

These are review verdicts, not acceptance of installed runtime integration, physical measurements, participant collection or tasks 01/03/05 as a whole.

## Scope and evidence examined

Reviewed the four complete new files against `a3b/task-brief.md`, `a3b/report.md`, the authoritative `controller/a3a-acceptance-and-consumer-binding.json`, A3a review/interface, actual native payloads/XML/producer ledger/log, actual production Dart/collector/history consumer code and parent execution outputs. Loaded study-readiness and review guidance.

All four current source hashes match `controller/a3b-parent-verification-1.json`; each entire source also matches its section in `controller/a3b-review-package-1.txt`:

| File | SHA256 |
|---|---|
| `benchmarking/host_fixture_replay.py` | `884a8c7bfe2e70b75441b3500de61734bcf9554b0ea63b758ace6b848d0070ef` |
| `benchmarking/test_host_producer_replay.py` | `fc10972b4c5451f36f9cea42ed380a54cb7719cf8e7c7f2ce6239112bd9c4235` |
| `app/test/host_study_flow_test.dart` | `332bd04f11120334ceaf95f30222de43d92b157a4426400b7066b6b09a9ea831` |
| `app/test/support/host_fixture.dart` | `2d7de2a0c04c8ef5688af85ae1172892c89f858ac3517d61521920efd21605e6` |

Reviewer independently executed read-only digest/observation checks, fresh `validate()` preflight and nine in-memory negative-probe executions using the existing Python 3.11 with `-B -E`. Probes intercepted only `read_regular` for selected synthetic byte substitutions; no evidence file was mutated or history written. Seven rejected with fixed codes and no stdout; two incorrectly emitted successful receipts (F1). Fresh preflight and source/artifact hashes still matched afterward. No full-suite rerun was necessary or performed. Only this review report is intentionally written.

## Blocking finding

### F1 — Medium: malformed producer-ledger containers pass preflight

**Location:** `benchmarking/host_fixture_replay.py`, `validate()`, producer-ledger checks around lines 156–163; missing regression in `PreflightNegatives.test_ledger_nonzero_bool_and_wrong_sources`.

The validator checks membership in `row['command']` and `row['fixture_outputs']` without validating that either value is an array of strings. Python applies substring membership to strings. Consequently, malformed producer provenance can still emit a successful preflight receipt, contrary to the malformed/type fail-closed requirement for this preflight boundary.

Independent reproduction, each changing just one field of the selected `parent-explicit-1` ledger row in memory while leaving the real manifest, XML, log, sources and artifacts untouched:

| Mutation | Actual `main(['preflight'])` result |
|---|---|
| `command = '--tests com.kumpas.kumpas_app.HostStudyFlowTest'` (JSON string, not argv array) | exit **0**, receipt emitted, empty stderr |
| `fixture_outputs = 'HOST_STUDY_FIXTURE_MANIFEST ' + str(ROOT / MANIFEST)` (JSON string, not output array) | exit **0**, receipt emitted, empty stderr |

This is not an adversarial filesystem/attestation extension: it exercises ordinary malformed JSON field types in the expressly reviewed producer-preflight input. Pinning the genuine manifest and passing XML does not make the malformed ledger structure valid. The actual preserved ledger has proper arrays, so these probes do **not** invalidate the observed successful parent run or imply payload alteration.

**Required fix:** before membership tests, require both fields to be lists containing only strings, using a fixed rejection code; retain existing exit/source/stdout/target checks. Add regression-first string/object/scalar/null container cases through the public CLI error boundary (or equivalent captured `main()` execution). Assert nonzero exit, no success receipt/bundle and no raw payload leakage. Keep a positive control for the unchanged accepted ledger. Do not replace or regenerate native output, relax pinned digests, or change existing production consumers.

Other independent negatives behaved correctly: malformed ledger JSON → `invalid_json`; a nonobject ledger row/root → `fixture_invalid`; absent selected output field → `producer_ledger_mismatch`; missing producer XML → `missing_regular_file`; stale XML stdout UUID → `producer_stdout_mismatch`; changed artifact bytes → `artifact_digest_mismatch`. All returned exit 2, fixed JSON stderr and no stdout. The last artifact probe is a digest rejection, not a claim of deeper payload-parser coverage.

## Specification findings otherwise satisfied

### Exact execution and successful producer provenance

The selected input is exclusively:

`benchmarking/study_evidence/20261015/a3a/handoff-parent-1/323291af-c067-46dc-bae1-067d62fab10b/manifest.json`

- Run: `323291af-c067-46dc-bae1-067d62fab10b`.
- Independently computed manifest SHA256: `3279cb7d01075a9192f2566ae5573dd6137a23c6710ef1d0a590b78564fe0fed`.
- Independently checked all **42** native source hashes and all **11** artifact hashes/lengths against current files. The preflight also enforces exact integer schemas, synthetic/success identity, exact artifact kinds/names, duplicate-key refusal, path containment/no symlinks, source snapshot and payload/index/event correlations.
- Read the actual bound producer XML: five named executed tests, zero failures/errors/skips, including `executedStudyAndBenchmarkProducer`; stdout names this exact manifest. The selected `parent-explicit-1` ledger has exit 0, its full source map matches the manifest and its command/output records match the target/run. The actual producer log has an executed `> Task :app:testDebugUnitTest` line and `BUILD SUCCESSFUL`.
- Historical worker selection in `handoff-interface-v1.md` is explicitly superseded by the authoritative binding; there is no implicit latest/worker discovery.

The wider 82 protected/eight A2a preservation checks are credited to the parent's verification record, not represented as a new independent reviewer audit of those files. Existing unrelated Git changes remain untouched.

### Python-to-Dart bridge and actual UI

`bundle` base64-encodes the same in-memory artifact byte objects returned by the successful Python verification. Dart consumes that stdout bundle rather than rereading mutable payload paths. No crypto dependency was added. This is a trusted local interpreter/checkout/stdout-pipe handoff, **not** Dart cryptographic or executable attestation, hostile-filesystem atomicity or a durable publication guarantee.

The actual event contains the native attempt identity `0a3f6b32-940e-4398-884f-476184fbe0d9`, numeric severity 0.25, right-hand/string prompt, recognized-as-target true and match 0.8. The Flutter test sends its exact UTF-8 string via the binary messenger's EventChannel envelope into the existing channel, model and PracticeScreen. Assertions check actual FeedbackSheet content, 80% display and exactly one ACK with that native identity; stale, duplicate and post-dismiss events do not add sheets/ACKs. Platform view/control transport is explicitly mocked. The startAttempt response is an expressly constructed mapping from native direct AttemptBoundary setup, not an executed native camera-permission/startAttempt RPC.

### Captured control/errors, caches and retained exports

Read all 25 actual native control records and independent SQLite observation snapshots. Tests use captured history/assessment/identity/session responses through the real channel/repository, with genuine captured `CONTROL_FAILED`, `EXPORT_FAILED` and `CLEAR_FAILED` codes. They assert assessment/export retry, clear-failure cache invalidation/revision increment, successful clear increment and replacement identity, empty history/assessments, reopen identity and existing LearnerStats/mastery calculations. This exercises computed profile statistics, not a rendered ProfileScreen or live Dart SQLite persistence.

Actual export artifacts agree with scoped native rows: selected participant has one session, one attempt and two assessments; the foreign participant has real data and is excluded. External/internal export bytes agree. The reopened export is empty and binds the replacement participant. The tests inspect retained manifest artifacts, never dereference disposed historical export paths. Partial purge genuinely retains three SQL attempts across two participants while filesystem removal is partial; no transactional rollback is claimed.

Control selection deliberately reorders captured stages to exercise retry. In particular, export failure is followed by replay of an earlier captured successful response, and the old initialized identity is replayed after failed clear. This is openly staged transport replay, not proof that the frozen native producer executed those newly ordered RPCs consecutively.

### Actual readers and isolated history

Read the real `parent-replay-2/synthetic-history.json` and replay ledger. There are exactly **six** real sink rows, one FPS and one camera-latency row for each of three distinct native mode UUIDs. All retain analyzer count 1,800 and a run-bound numeric trace with 50 ms final-analyzer-to-event and 1 ms inference diagnostic. Latency summaries retain those numeric values; absent UI-ACK observations remain null/zero-count summaries rather than invented measurements.

Main transport hashes equal the immutable native report hashes. The production `collect_fps.read_report`, FPS validation, camera-latency assessment, `log_collection` and atomic history utility are actually used; only ADB/declarative synthetic metadata are mocked and subprocess execution is forbidden inside replay. Faulted companion acquisition genuinely raises a read error because there are no companion bytes, rather than returning fabricated failure JSON.

All six collector exits are **1** and all six gates are **false**, correctly: every original immutable report says `immutable_only_latest_unverified`; unconfirmed/faulted modes also lack confirmed authoritative disposition. Harness exit 0 means successful assertions/replay, not physical performance qualification. Robolectric metadata remains unchanged, including its synthetic is_emulator value; it is not independently attested hardware.

The separate interpreter test removes only newline whitespace for the legacy one-line logcat parser and compares parsed JSON/hash to the adapted bytes. It declares synthetic instrumentation-status transport, has no native interpreter-only output/census, retains `diagnostic_valid == false` and cannot close a camera-latency gate.

## Execution evidence credited and checked

Parsed actual parent logs, not only the worker's summary:

| Parent evidence | Result |
|---|---|
| `a3b/parent-python-2.log` | 74 tests, OK |
| `a3b/parent-flutter-2.log` | 79 nonhidden test completions, all success, zero skipped; final done success true; all four host consumer tests present |
| `a3b/parent-analyze-2.log` | No issues found |
| `a3b/parent-replay-2/` | Six actual history rows, zero passing gates; ledger/report byte correlations checked |

Commands/exits are recorded in `a3b/parent-command-ledger-2.json`. The parent's initial console parser error and the worker's earlier Python ABI/environment import error are retained evidence-tool/environment issues, not hidden product failures; final parent suites pass. This reviewer did not independently rerun those suites and does not convert their passing status into coverage of F1.

The retained feature RED logs show meaningful missing CLI/replay behavior, not syntax errors; existing collector/UI additions are appropriately described as coverage-only. The earlier payload-type RED exposed an AttributeError and subsequent code added object guards. F1 demonstrates one remaining unchecked container shape despite those improvements.

## Whole-task boundaries and disposition

After F1 is fixed and re-reviewed against frozen postimages, bounded host-consumer approval can be reconsidered without new native artifacts. The already valid execution results remain useful evidence.

Still outside this review/acceptance: installed uninterrupted CameraX → native messenger → Flutter → persistence/export/delete integration; native registration/startup and accepted A2b differing-messenger/retry limits; actual camera/detector/interpreter operation/release; physical FPS/latency/thermal/recognition; sensor-exposure or physical-display timing; model/expert/anatomical/human-learning validation; participant-study authorization. Synthetic setup fields, mocked ACK transport and layered successful suites cannot close these gates. No installed-runtime or study acceptance is given.

No source edits, dependency changes, installs, builds, Gradle/Flutter reruns, ADB/emulator/device access, default participant/history stores, model/training operations or commits were performed by this reviewer.
