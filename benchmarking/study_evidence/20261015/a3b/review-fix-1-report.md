# A3b review fix 1 — F1 strict producer ledger containers

Status: DONE — F1 repair and requested covering execution complete; independent parent verification/re-review pending.

Scope: only host_fixture_replay.py, test_host_producer_replay.py and new fix evidence. Preserve selected run 323291af-c067-46dc-bae1-067d62fab10b, manifest digest 3279cb7d01075a9192f2566ae5573dd6137a23c6710ef1d0a590b78564fe0fed, native/Dart/artifacts and historical evidence. No installed/device/default-store operations, dependencies or commits.

F1: command and fixture_outputs must be lists of strings before membership. Add behavioral captured public-main preflight/bundle regressions, execute RED before minimal production change, then covering suites and isolated replay. Actual accepted ledger is valid and must remain unchanged.

Exact execution records will be appended to review-fix-1-ledger.jsonl with unique logs. Malformed fixtures stay in memory or scratch only. Host synthetic results do not establish physical or participant-study qualification.

- `red-command` exit 1: `review-fix-1-red-command.log`; exact command/environment in fix ledger.

- `green-command` exit 0: `review-fix-1-green-command.log`; exact command/environment in fix ledger.

- `red-outputs` exit 1: `review-fix-1-red-outputs.log`; exact command/environment in fix ledger.

- `green-types` exit 0: `review-fix-1-green-types.log`; exact command/environment in fix ledger.

- `python-focused` exit 0: `review-fix-1-python-focused.log`; exact command/environment in fix ledger.

- `python-full` exit 0: `review-fix-1-python-full.log`; exact command/environment in fix ledger.

- `replay` exit 0: `review-fix-1-replay.log`; exact command/environment in fix ledger.

- `flutter-focused` exit 0: `review-fix-1-flutter-focused.log`; exact command/environment in fix ledger.

- `flutter-full` exit 0: `review-fix-1-flutter-full.log`; exact command/environment in fix ledger.

- `analyze` exit 0: `review-fix-1-analyze.log`; exact command/environment in fix ledger.

- `verification` exit 0: `review-fix-1-verification.log`; exact command/environment in fix ledger.

## Behavioral repair and execution results

- Production delta is four lines: explicitly require each selected ledger field to be a list whose elements are all strings, before any membership. Retains existing exit/source/target/output/log/XML validation and fixed `producer_ledger_mismatch`; no arbitrary value echo.
- Strict vertical execution: command regression RED (exit 1, 26 failed subtests), command guard then GREEN; fixture_outputs regression RED (exit 1, 26 failed subtests), fixture_outputs guard then combined GREEN (3 tests). These are real assertion failures: membership-bearing strings/objects and mixed lists returned success; scalar/null cases also exposed inconsistent generic rejection. No syntax/import errors. Existing correctly rejected empty arrays remain negative coverage, not claimed as newly failing behavior.
- Both public `main(['preflight'])` and `main(['bundle'])` run with captured stdout/stderr against real bound inputs and only an in-memory ledger-byte substitution. Tests cover string/object/integer/float/bool/null/empty/mixed-list shapes, require exit 2, empty stdout (no receipt/bundle), exact fixed diagnostic and no private marker. Unchanged accepted ledger and valid string-array controls succeed for both actions. Original ledger is never written.
- Focused Python: **34 tests OK** (previous 31 plus 3); full discovery: **77 tests OK**. Flutter byte-bridge focused: **4 tests**, full suite: **79 tests**, all success, zero skips/failures; analyzer: **No issues found**. Machine-event counts parsed and asserted by verification script, excluding hidden loading completions.
- Actual fresh CLI replay: `review-fix-1-replay/receipt.json`, `replay-ledger.json`, `synthetic-history.json` and six collector stdout records. Six distinct mode/type rows; all collector exits **1**, all physical gates **false**, each retains 1,800 analyzer entries and exact transport/artifact digest correlation. Harness exit 0 means successful replay assertions, not qualification. No marker in retained history.

## Preservation and frozen postimages

`review-fix-1-verification.json` records actual results and hashes. **42 native sources, 11 original artifacts, 82 protected files, 8 A2a accepted files and both Dart consumer files match**; pinned manifest digest/run unchanged. Among 963 initial snapshotted files, only the two authorized Python files changed (961 others unchanged). Snapshot excludes fix-evidence filenames. All original binding/producer ledger/XML/logs remain untouched. `git diff --check` exit 0.

| Changed source | SHA256 |
|---|---|
| `benchmarking/host_fixture_replay.py` | `08e259ba337a10eabc05be184386a1e1c52fabb33ffd0b848779a3c2e795819f` |
| `benchmarking/test_host_producer_replay.py` | `07a0754b66ad97a10dd12731b65c6e906e8870ada2270a7ce02553fd1c66450f` |

Full frozen source contents: `review-fix-1-source-postimages.txt`. New execution scripts, initial snapshot, unique logs, command ledger, verification and isolated replay are fix evidence only. Existing Python 3.11 `-E`, scratch TMPDIR and shared exclusive fcntl lock were used; no dependency install, pub operation, native rebuild, commit/reset or default-store/device operation.

## Issues and remaining limits

No execution blockers. Expected behavioral RED logs retained. Independent parent verification/re-review remains required; this is not acceptance of A3b/tasks01/03/05 as a whole. Separate native-produced artifacts, trusted-local Python stdout byte bridge, mocked Flutter/ADB transport and isolated real collector histories do not prove uninterrupted installed CameraX→Flutter→persistence/export/purge, hostile-filesystem attestation, physical FPS/latency/thermal/recognition, model/expert/anatomical validity, learning outcomes or participant-study authorization.

