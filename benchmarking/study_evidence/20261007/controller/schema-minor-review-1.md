# Independent narrow schema-minor review

## Outcome

**APPROVED within the narrow schema-type repair scope; no blocking findings.** The FPS and camera-latency validators require the exact built-in integer `2`, not Python equality alone. Noninteger main schema values are removed and marked unsafe at raw-reader and sink boundaries, with numeric diagnostics retained. This closes the stated quality-review-3 R1 schema issue; it is not acceptance of the surrounding uncommitted repair set.

## Scope and source reasoning

Reviewed the specified additions in `benchmarking/collect_fps.py` and `benchmarking/test_collectors.py`, following their use through `collect_latency.py`. Existing unrelated uncommitted edits were preserved.

- `collect_fps.py:121–127`: exact `type(...) is int` requirement plus existing value comparison rejects `2.0`, booleans, strings, null, containers and wrong integer versions. Only integer `2` qualifies.
- `collect_fps.py:407,477–478`: `REPORT['schema_version'] = int` and a dedicated exact-type branch reject nonintegers before the generic nullable primitive branch. The dictionary sanitizer omits the rejected field and propagates unsafe status without discarding unrelated measurements.
- `collect_fps.py:331–336,553–570`: reader rejection remains in collection errors after sanitation; the history sink revalidates type for direct unsanitized input and suppresses a claimed passing gate. Rebinding does not erase the collection rejection.
- `collect_latency.py:36–49,89–95`: camera latency shares `validate_report`; interpreter acquisition shares the strict REPORT sanitizer and records a fixed diagnostic-field rejection. Interpreter-only results remain non-gating.
- `test_collectors.py:53–61,151–201`: new exact-integer regression exercises both FPS and camera-latency validation; the `report_schema_float` fault exercises FPS, latency and interpreter reader-to-real-isolated-history paths, retaining analyzer count and event timing and requiring rejection reasons.

The sanitizer is intentionally a type boundary, not an exact-version validator: it retains integer versions `1` and `3`, which the FPS/camera-latency validators reject. This review does not claim that `safe_payload` alone enforces version 2, nor change the existing interpreter schema semantics.

## Fresh independent execution

Repository workdir: `/Users/ahronjanl.rafaelahron.0804icloudcom/Documents/Thesis/kumpas`.

1. `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s benchmarking -p 'test_collectors.py' -v`
   - **27 tests passed**, exit 0, including both named schema regressions and isolated real-history fault coverage.
2. Additional independent inline Python probe, exit 0:
   - Validator matrix: `2`, `2.0`, `True`, `False`, `'2'`, `None`, `1`, `3`, `[]`, `{}`. Both FPS and camera latency passed only integer `2`; sanitizer rejected every noninteger and retained integer values without coercion.
   - Raw-reader/sink matrix: eight values (`2`, `2.0`, both booleans, `'2'`, null, list, dict), three paths (FPS, camera latency, interpreter diagnostic), and two sink inputs (reader-sanitized and direct raw report). All assertions passed.
   - ADB was mocked and real subprocess execution explicitly blocked during reader probes. History append was captured in memory for these extra probes. No actual device operations occurred.
   - Every invalid schema yielded reader errors, omitted the schema field, produced nonempty sink rejection reasons and exit 1. Valid integer-2 FPS/latency controls passed; interpreter remained non-gating.
   - Numeric diagnostics remained exactly `analyzer_count=1800`, `final_analyzer_to_event_ms=100`, and `p95_ms=2` in raw-reader reports and both sink input variants.
3. Broad default-Python discovery was also attempted:
   - `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s benchmarking -p 'test_*.py' -v`
   - **Not a full-suite GREEN:** 34 reported entries, including four import errors from missing `numpy`/`matplotlib` in the system Python 3.9 environment; the remaining 30 test entries passed. No installations were performed. This environment limitation does not invalidate the independently passing narrow collector suite.

## Supplied evidence checked

Read `schema-minor-red-1.log`, `schema-minor-red-sink-1.log`, and `schema-minor-green-full-1.log` in this controller directory. The saved RED logs show floating schema validation wrongly succeeding, FPS/latency sink exits wrongly succeeding, and interpreter rejection diagnostics missing. The saved GREEN log reports 43 passing tests. That 43-test result is supplied historical evidence, not a full-suite result independently reproduced in this review's default interpreter.

## Reviewed hashes and limits

SHA-256 before and after the independent probe matched:

- `benchmarking/collect_fps.py`: `7e0db7bc3aa468703ecab977ec07ab69009e842f96a042fb1017f315422e54f0`
- `benchmarking/collect_latency.py`: `29554278483dca6c9ebdd6d62c873aec947a47b15e3281bc0b9a2693e552057e`
- `benchmarking/test_collectors.py`: `f593b71a2fb8da038c60d73b15853758bd1d4865ddb9fdfaf8e94d59352f000a`

Only this requested review document was created intentionally. No source edits, commits, installations, device operations, model changes or default participant/history-store operations were performed. Test suites used isolated synthetic fixtures; bytecode writing was disabled. Approval is limited to the reviewed schema-type additions and host synthetic behavior, not native/Flutter integration, physical FPS/latency measurements, participant readiness or broader package4 acceptance.
