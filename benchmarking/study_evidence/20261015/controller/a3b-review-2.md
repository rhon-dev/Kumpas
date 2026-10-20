# Independent QA — Phase A3b re-review 2

## Verdicts

- **Specification compliance: APPROVE — bounded A3b host-artifact consumer scope.** F1 is closed. The malformed producer-ledger containers now fail closed before membership, with regression coverage through both public preflight and bundle boundaries. Previously reviewed exact binding, byte transfer, Flutter UI/repository consumers and Python reader-to-isolated-history requirements remain preserved.
- **Code quality: APPROVE — no remaining blocking finding identified in this scope.** The four-line validator change is minimal, readable and correctly ordered. Added tests cover malformed container and element types without changing producer artifacts, application production code or dependencies.

These are independent QA verdicts for the frozen A3b postimages, not a new A3a acceptance decision, installed-runtime acceptance, whole-task 01/03/05 completion or participant-study authorization. Controller acceptance remains a separate decision.

## Review scope and frozen identity

Read `a3b/task-brief.md`, `a3b/review-fix-brief-1.md`, review 1, fix report/ledger and retained RED logs, review package 2, parent verification 2 and its execution ledger/logs. Reviewed current complete Python sources and both Dart consumer files. Compared package 1 to package 2: production delta is only the four lines guarding the two ledger fields; test delta adds `ProducerLedgerCliTypes`. All four current files match their package 2 sections and parent verification 2 hashes, independently checked before and after narrow execution:

| Source | SHA256 |
|---|---|
| `benchmarking/host_fixture_replay.py` | `08e259ba337a10eabc05be184386a1e1c52fabb33ffd0b848779a3c2e795819f` |
| `benchmarking/test_host_producer_replay.py` | `07a0754b66ad97a10dd12731b65c6e906e8870ada2270a7ce02553fd1c66450f` |
| `app/test/host_study_flow_test.dart` | `332bd04f11120334ceaf95f30222de43d92b157a4426400b7066b6b09a9ea831` |
| `app/test/support/host_fixture.dart` | `2d7de2a0c04c8ef5688af85ae1172892c89f858ac3517d61521920efd21605e6` |

Authoritative binding remains `controller/a3a-acceptance-and-consumer-binding.json`, exclusively selecting parent run `323291af-c067-46dc-bae1-067d62fab10b` and manifest:

`benchmarking/study_evidence/20261015/a3a/handoff-parent-1/323291af-c067-46dc-bae1-067d62fab10b/manifest.json`

SHA256: `3279cb7d01075a9192f2566ae5573dd6137a23c6710ef1d0a590b78564fe0fed`.

No latest/worker-run substitution or native regeneration was made. This review verifies continued consumer binding; it does not reopen accepted A3a implementation review.

## F1 disposition — closed

At `host_fixture_replay.py:159–162`, each selected ledger field is required to be a list with every element a string before any membership test at lines 163–166. This eliminates substring and dictionary-key membership acceptance and rejects mixed arrays. JSON decoding produces built-in containers, so the `isinstance` guards enforce the required JSON array/string contract without needing a broader Python-object threat model. Existing exact integer exit 0, source-map, required target/output, producer XML and successful log checks remain unchanged. Both guards use fixed `producer_ledger_mismatch`, not interpolated payload text.

At `test_host_producer_replay.py:336–401`, tests substitute only selected ledger bytes in memory; all other validation uses real bound evidence. For both `preflight` and `bundle`, they cover membership-bearing strings and objects, integer/float scalars, booleans, null, empty arrays and arrays containing nonstring scalar/object/list elements. Assertions require exit 2, empty stdout, exact fixed stderr and no private marker. Controls retain unchanged accepted arrays and valid string arrays with additional safe strings.

Fresh reviewer execution from repository `benchmarking/`:

```text
/opt/homebrew/bin/python3.11 -B -E -m unittest -v test_host_producer_replay.ProducerLedgerCliTypes
Ran 3 tests in 0.992s
OK
exit 0
```

This executed 56 negative public-main invocations and six positive controls. Thus the original string-container failure is covered for both output surfaces, not merely by a private helper assertion. The existing empty-array rejection is coverage, not newly repaired behavior.

The retained `review-fix-1-red-command.log` and `review-fix-1-red-outputs.log` each show meaningful assertion failures and `FAILED (failures=26)`, not import/syntax failures. Their ledger records sequential RED/GREEN slices. These are historical implementer executions inspected by this reviewer; no source rollback or new RED execution was attempted against frozen sources.

## Preserved bounded consumer requirements

- **Provenance/preflight:** Exact manifest pin, strict schemas, synthetic success, artifact set/kind/identity, duplicate-key and path/symlink rejection, lengths/digests, source snapshot, successful non-skipped producer target/XML/stdout/ledger/log checks remain intact. Fresh reviewer `bundle` CLI execution with existing Python `-B -E` returned exit 0, empty stderr, expected run/digest, 42 sources, five producer tests and 11 artifacts. Independently decoded every returned base64 payload and matched its SHA256 to the returned verified artifact receipt. This is consumer preflight against preserved native evidence, not fresh native test execution.
- **Same-execution bytes:** Python transfers the verified in-memory payload objects; Dart consumes those bytes from stdout without rereading mutable artifact paths or adding crypto dependencies. Every `HostFixture.load()` invokes validation; missing/failed binding throws rather than skipping. Default full Flutter discovery includes these tests without an external stale-preflight switch.
- **Flutter UI and repository:** Unchanged tests inject the exact native event text through mocked EventChannel into actual channel/model/PracticeScreen/FeedbackSheet; assert recognized target, match/items, displayed 80%, native-identity single ACK and stale/duplicate/post-dismiss suppression. Captured controls exercise real repository parsing, assessments/history, `CONTROL_FAILED`, `EXPORT_FAILED`, `CLEAR_FAILED`, cache invalidation/revisions, replacement/reopen identity and computed LearnerStats/mastery. Platform view/control transport is mocked; constructed startAttempt/lifecycle responses are labeled. No rendered ProfileScreen or Dart SQLite execution is claimed.
- **Exports and staged errors:** Retained external/internal export bytes are checked against scoped independent native rows, including real foreign-participant data exclusion and reopened empty export. Historical deleted paths are not dereferenced. Failed-clear SQL retention is not presented as transactional filesystem rollback. Replaying an earlier successful export or initialized identity after a later failure is explicitly staged transport ordering, not a newly executed consecutive native session.
- **Collector path:** Current replay uses actual report reader, FPS/camera-latency assessment and isolated real history sink with mocked ADB/declarative synthetic metadata and blocked subprocess calls. Faulted companion acquisition raises a read error with no fabricated companion JSON. Original report bytes are not edited into hardware attestation. Existing fault/direct-sink coverage retains safe counts/traces and fixed diagnostics. Interpreter input uses the declared newline-only logcat adapter; its digest refers to adapted bytes and remains diagnostic, not native interpreter-only census or camera qualification.

## Parent evidence inspected, not rerun here

Parent execution ledger timestamps are **October 16, 2026**, around 11:07–11:08 UTC+08:00. These are preserved parent runs, not fresh reviewer suite runs:

| Evidence under `a3b/` | Checked result |
|---|---|
| `parent-fix1-python.log` | 77 tests, OK; ledger exit 0 |
| `parent-fix1-flutter.log` | Parsed 79 nonhidden test completions, zero failures/skips, final done success true; ledger exit 0 |
| `parent-fix1-analyze.log` | No issues found; ledger exit 0 |
| `parent-fix1-replay/` | Six history rows and six mode/type observations; all collector exits 1, all gates false; harness ledger exit 0 |

Read the replay history and observation ledger: every row retains analyzer count 1,800; all six report transport hashes equal their immutable artifact hashes. Gate false is expected, not a test failure or a measured physical pass. Native publication-unverified and unconfirmed/missing-disposition restrictions remain operative.

Parent verification 2 records 42 native source, 11 original artifact, 82 protected and eight A2a hashes matching, plus both unchanged Dart consumers. The 42-source/11-artifact continued binding was also exercised by fresh consumer preflight here. The broader 82/eight preservation assertions are credited to the parent record/context, not claimed as a new independent full protected-file audit.

## Limits, recovery issues and changes

Only this new report was intentionally written. No source, binding, historical evidence or accepted producer output was modified; no build/install/Flutter/Gradle/full-suite rerun, ADB/emulator/device operation, default participant/history access, model/training action or commit was performed. Narrow tests operate on in-memory ledger substitutions and read-only bound inputs.

The interrupted predecessor's HTTP429/permission timeout supplied no saved review-2 verdict; this report is based on current reads and fresh narrow execution. During this recovery a read-only Flutter log summary initially assumed every JSON line was an object; one was an array. The parser was corrected to flatten arrays and filter objects, yielding the counts above. This was reviewer evidence parsing, not a product failure; it did not block completion.

Trust remains local Python interpreter/checkout/stdout-pipe integrity, not Dart cryptographic/executable attestation, hostile concurrent-filesystem atomicity or durable publication. Separate native producer evidence, mocked Flutter/ADB transport and isolated sinks do not prove uninterrupted installed CameraX → native messenger → Flutter → persistence/export/purge. Accepted A2b differing-messenger/retry limits remain unchanged. Actual camera/detector/interpreter lifecycle, physical FPS/latency/thermal/recognition, sensor-exposure/physical-display timing, model/expert/anatomical validity, human-learning outcomes and participant-study authorization remain outside these verdicts. No broader runtime, physical or study gate is closed.
