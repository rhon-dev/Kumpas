# Independent final quality/security/correctness review — 2026-10-07

## Verdicts

- **Spec compliance: NOT YET COMPLIANT / REQUEST CHANGES.** The four original diagnostic-field probes are repaired, but the broader untrusted recognized-string requirement is not closed (Q1). The advertised diagnostic disposition of late benchmark starts is not implemented in the producer/consumer contract (Q2). The named SessionManager initialization repair and committed-target rename-failure repair are present.
- **Code quality/security/correctness: CHANGES REQUIRED.** Q1–Q4 are Important source defects, not a request to substitute physical testing for source repair. Q3/Q4 concern unchanged supporting code in the resource-ownership paths and are explicitly not claimed as newly introduced regressions.
- **Critical:** none identified. **Important:** Q1–Q4. **Minor:** Q5–Q6.
- No acceptance, checklist closure, participant authorization, or physical performance pass is granted by this review. Parent owns fixes and acceptance.

## Scope and grounding

Read the entire frozen `controller/review-package-2.diff`, lines 1–2004, in three non-overlapping pages, including all tracked changes and all three new source/test files. Read the closure plan, repair report, snapshot manifest and verification JSON; traced supporting production BenchmarkMode/MainActivity/AttemptBoundary/PipelineMetrics/SessionManager/VisionEngine/CameraPreviewView, Dart channel/practice logic, both collectors and history writer. Read the complete producer tests and collector tests necessary to assess the contracts.

Read parent native-full-1/full-2, Flutter-full-2, Python-full-1 and release-build logs. Independently parsed existing native XML: **13 suites / 121 tests / 0 failures / 0 errors / 0 skips**. Parent full-2 logs show forced instrumentation-source compilation and debug/test APK builds; Flutter log shows **21 tests and clean analysis**; Python log shows **38 tests**; release log shows an ARM64 release build, not installation. No suites were rerun.

Independently checked HEAD `6b8b1b6770e46bea7728a8e9ca4ae6d78e857640`, all **20** manifest file hashes (no mismatches), and protected manifest hashes (no mismatches). This includes the new sources/tests. After the parent supplied `controller/artifact-verification-1.json`, independently rehashed all **82** enumerated protected files against its original expected hashes: zero mismatches, including the three git-ignored detector/model assets omitted from the earlier 79-file manifest. The artifact record documents ZIP/model/Flutter-ABI checks for debug/test/release APKs and an exit-0 ARM64 release build: **66,967,306 bytes**, SHA-256 `6efb93fe68eec50da28b14ba5dcf19e0e9fa1584001f9f156e7a729d9b44261f`, embedded model SHA-256 `1f4543b8fb159dbe9a662f0b37e64b096f717d7527c45b2d7778f34bc0885aeb`. Artifact identity is parent build evidence, not independent runtime execution or code approval; verdicts are unchanged. Existing compiler/dependency deprecations are not a pristine rebuild claim. No default/installed participant stores, ADB, device, plot or history operations were performed. Only review report is written.

Two read-only Python probes imported synthetic fixture constructors and actual collector functions with bytecode writes disabled. They did not execute unittest suites. The second probe mocked ADB entirely and replaced `append_entry` with a Python list, exercising actual `read_report → validation/assessment → log_collection` without creating history files. Its output is recorded below. Kotlin/Dart scenario findings are static source traces, not invented runtime observations.

## Important findings

### Q1 — Recognized metadata still persists private/forged text and can pass both gates

**Location:** `benchmarking/collect_fps.py:359–379,417–445,448–470`; selected-device comparison at `320–328,455–458`; camera validation at `67–68`. Coupled consumer: `collect_latency.py:36–49,106–108`.

**Scenario:** Keep the independently obtained fingerprint and APK digest unchanged, but place private text in report `device.model`, `device.manufacturer`, `build.version_name`, or `camera.camera_id`. These recognized fields use generic TEXT, not independently bound identity or the producer's camera-ID format. `safe_payload` accepts them, `read_report` compares only the report fingerprint, and `log_collection` again checks only fingerprint/APK. The comment claiming device/identity strings are independently compared is therefore too broad. Report-side model/manufacturer text is neither replaced with nor compared to the actual selected-device values.

**Executed evidence:** For each of those four fields, in both FPS and camera-latency modes, the synthetic value `PRIVATE patient text` survived the actual mocked reader/collector-to-entry path. All eight combinations returned `status 0`, `gate True`, `private retained True`, and `collection errors []`, despite host device metadata being `independent-device-value`. The camera text contains spaces and cannot be emitted by native `BenchmarkMode.recordCamera`'s `[A-Za-z0-9_.:-]{1,128}` contract (`BenchmarkMode.kt:152–155`), yet host qualification accepts it. Earlier in-memory probes also showed unrestricted recognized setup/identity text surviving the sanitizer; a syntax-valid opaque ID is not by itself proof of trustworthy provenance.

**Impact:** This is both a retained private-text bypass and acceptance of forged metadata, not just omitted coverage. The 12 added error-field cases cover different keys and do not close this sink. It affects the shared FPS/latency/interpreter storage schema; interpreter remains non-gating but must still be privacy-safe.

**Fix:** Bind report device metadata to independent host metadata before persistence (retain the verified values, not mismatched untrusted copies), and reject mismatches. Verify build fields against installed package metadata or omit/normalize unsupported report text. Apply exact producer identity formats to camera/attempt/run/setup fields, and use trusted provisioning/identity references where semantics require them; do not indiscriminately strip legitimate independently verified device names. Add reader-to-history regressions for these recognized fields in all three modes, including malformed IDs and diagnostic rejected rows. Rejected text must be absent, numeric diagnostics retained, and evidence non-gating. No general protection against semantically private text can be inferred merely from a permissive identifier regex.

**Spec:** Slice A's explicit broader fixed-contract-field review and prohibition on untrusted private text/forged metadata becoming success.

### Q2 — A timed-out benchmark start can remain a qualifying completed report

**Location:** `app/lib/ui/practice_screen.dart:185–207`; `MainActivity.kt:113–115`; `BenchmarkMode.kt:70,273–318,342–344`; host `collect_fps.py:31–69,114–193,448–461`.

**Scenario:** Native starts run A, but its start response remains unresolved past Dart's 30-second watchdog. Native reaches its measurement deadline and publishes A normally before Dart receives its identity (or the subsequent stop is delayed until after that deadline). The UI promises “any late run is diagnostic.” Upon eventual identity resolution, however, Dart sends only `stopBenchmark(runId: A)`. There is no timeout/disposal disposition argument, cancellation record, or producer qualification downgrade. If A is already closed, `BenchmarkMode.stop` simply returns its previously completed report. If stop itself stalls, `.timeout` stops waiting in Dart; it does not cancel or mark the native run. A full-window report can retain `qualified_setup/latest_published` and a true producer/host gate.

**Evidence:** Static end-to-end trace above; `stop`'s completed-run branch at 344 is explicit. The added widget fake returns `{"complete":false}` unconditionally for stop and does not exercise actual completed-run retention. The producer's auto-deadline tests establish normal full-window completion separately, but no coupled regression tests a timed-out control request resolving after the native deadline. No executed phone timing is claimed.

**Impact:** The diagnostic promise and request-generation state exist only in widget memory/snackbars. They are absent from retained/USB evidence, which can consequently qualify a request the flow classified as timed out. Logging a cleanup failure does not change that evidence. Identity safety of stop is correct, but identity safety alone does not implement terminal disposition.

**Fix:** Define and persist an identity-scoped abandoned/control-timeout disposition, wire it through native report qualification and both collectors, without mutating an immutable measurement payload or stopping replacement B. If an already-published report needs a separate trustworthy disposition record, the collector must require/check that record. Add cases where response and/or stop resolve after the measurement deadline, plus disposal and replacement; require retained diagnostics to be non-gating. Do not erase measured timings or rewrite censor outcomes.

**Spec:** Slice D's failed/partial-run diagnostic retention, and this repair's stated late-run diagnostic policy. A 30-second control deadline is not interchangeable with the observation duration.

### Q3 — VisionEngine partial construction still leaks already-created native resources

**Location:** `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/VisionEngine.kt:107–130,322–328`; caller `MainActivity.kt:42–50`.

**Scenario:** Pose creation succeeds, then hand creation throws; or both detectors succeed and model loading/Interpreter construction/label parsing throws. No constructor rollback closes the resources already created. The assignment `visionEngine = VisionEngine(...)` never completes, so later Activity teardown cannot reach that partial object. The new `closeActions` list is initialized only after this constructor work and is useful only on a constructed instance. Asset reads at 124/129 also lack `use`; Kotlin `readBytes` does not establish ownership closure.

**Evidence:** Static control-flow/resource-ownership proof, not an executed MediaPipe fault. The new test allocates an engine using `Unsafe.allocateInstance`, replaces `closeActions`, and then invokes `close`; it necessarily bypasses precisely this failing initialization path. SessionManager's constructor rollback is correctly implemented but cannot close a different object's native resources. This is unchanged supporting code, not a claimed new regression.

**Impact:** Failed camera-engine setup can retain detector/interpreter resources and open asset streams. “All owned resources are attempted” is true for the wired constructed-instance close path, not for failed engine construction.

**Fix:** Stage acquired resources with rollback that attempts every acquired close and preserves the original exception/suppressed failures; transfer ownership to final fields only after successful initialization. Use `use` for asset streams. Add a narrow production constructor factory seam and fault tests after each acquisition; no model/reference/math changes required. Retain the existing constructed-instance cleanup tests and their honest runtime limits.

**Spec/quality:** Resource-ownership review (checklist 11). The plan specifically names SessionManager constructor failures; that named repair passes. This additional source defect must nevertheless be resolved or explicitly scoped by parent rather than claimed covered by constructor-bypass tests.

### Q4 — Old CameraPreviewView disposal still cancels the shared replacement engine

**Location:** `CameraPreviewView.kt:118–127`; factory `MainActivity.kt:130–134`; `VisionEngine.kt:99–104`; `BenchmarkMode.kt:152–163`.

**Scenario:** Factory creates more than one platform view over the Activity's single engine/benchmark (for example a replacement view while old platform-view disposal is outstanding). View B has begun a replacement capture/bound camera. Disposing old view A unbinds only A's use cases correctly, but then calls unscoped `engine.cancelAttempt()` and writes global camera state `unknown/unbound`. Those operations are not limited to A's attempt/camera ownership. A's `disposed` flag only protects duplicate A disposal, not B.

**Evidence:** Deterministic static two-view scenario: factory passes the same `visionEngine!!` and `benchmarkMode` to every view. `cancelAttempt(null)` always clears current `attemptTarget`/samples; it does not use the request-generation checks employed by camera-error delivery. ResourceCleanupTest replaces `disposalActions` and checks cancellation, not actual default action ownership across two views. No claim that this specific ordering was observed on a device.

**Impact:** Stale cleanup can silently abort replacement capture without updating MainActivity's attempt boundary/terminal accounting; replacement waits for UI timeout or is censored. It can also incorrectly invalidate B's setup camera snapshot. Exception-safe execution of every action does not make these shared side effects owned.

**Fix:** Give view registrations explicit ownership/generation tokens. Dispose should clear global camera/capture state only if that view still owns it, routed through the identity-scoped Activity boundary so outcomes remain coherent. Continue attempting A's analyzer clear, A's use-case unbind and A's executor shutdown regardless of ownership or earlier exceptions. Add a two-view stale-disposal regression against default production action wiring. This is an existing weakness retained in the modified teardown, not a newly introduced unconditional cancel.

**Spec/quality:** Generation-safe captures and exception-safe *owned* teardown (checklists 4/11), separate from physical CameraX acceptance.

## Minor findings

### Q5 — Producer exception-code census is wider than host retained failure vocabulary

**Location:** `CameraPreviewView.kt:84–86,108–110`; `BenchmarkMode.kt:178–180`; `PipelineMetrics.kt:21–23`; `collect_fps.py:374–388`.

The producer records arbitrary exception simple class names in numeric `failures`. The host recognizes SecurityException/FileNotFoundException for error fields but not for failure counters. Read-only probe of a report with `failures={"SecurityException":1}, failure_count=1` returned `unsafe=True`, retained `failures={}`, and retained `failure_count=1`. Thus a legitimate coded producer diagnostic loses its category and becomes internally inconsistent in retained evidence. This fails closed, so it is not a success bypass; it is a retention/contract-quality defect. Normalize producer failure classes to a shared fixed vocabulary with a generic fallback and ensure both collectors retain all emitted codes; test known and unknown classes without retaining exception messages.

### Q6 — Never-returning late-stop cleanup branch lacks permanent deadline coverage

**Location:** `practice_screen.dart:198–205`; `app/test/practice_flow_test.dart` late-cleanup-failure test (diff lines 1388–1407).

The test makes stop throw immediately. It does not test a Future that never returns, the second 30-second timeout, or a stop failure arriving after the timeout. Add completer-based deadline tests and verify one coded diagnostic, no unhandled Future errors, no replacement stop and no status corruption after disposal. The repair report explicitly discloses this omission; it is not a hidden failing suite. Q2 is a separate source-level retention defect, not merely this missing test.

## Contracts that are substantively improved / no additional defect identified

- Immutable and latest final targets now get exact-byte/run-ID readback; nonthrowing final-target rename failures are exercised for both targets, with untouched sentinels and new-run retry. Pessimistic immutable-only files are deliberately non-gating; no inference of successful latest publication from them. `reportPath` remains null on publication failure. No crash/power-loss durability proof is claimed.
- Start/stop/report UUID correlation, stale posted camera-error guards, retained pending capture timeout reason, duplicate/unknown timeout accounting and closed-run censor preservation have real production-boundary tests. These do not close Q4's different stale-disposal path.
- APK streaming hash and setup validation occur before PipelineMetrics starts; wrong/missing/split identity is diagnostic. Run setup is copied once. Host independently compares fingerprint/APK/condition. Blank provisioning template is explicitly non-qualifying; flags do not prove hardware/lux. Q1 identifies the remaining metadata trust boundary, not a reason to discard legitimate verified names.
- Named analyzer/event/ACK clock contracts remain intact. Half-open windows and full-duration zero bins are preserved. Latency rejects censored/unaccounted work and does not fabricate censor latency. Analyzer entry is not sensor exposure; post-frame/native ACK is not physical display time.
- `completeCleanup` really is called by constructed engine/camera/Activity methods, aggregates later exceptions and attempts `super.onDestroy`. Test closure injection is not detached-helper-only testing, but cannot prove actual detector/CameraX release or initialization rollback. SessionManager closes its own helper after participant/migration initialization failures; fixture manager closure is improved.
- Permanent history serialization/partial-write/fsync/replace tests are appropriately labeled coverage-only GREEN. Existing lock/temporary/replace logic preserves original bytes and retry under those tested faults. No historical history or plots were regenerated by this review.
- Native SQLite persistence-failure EventSink/accounting/retry and assessment-save form retention are meaningful layered coverage, not uninterrupted CameraX/channel/Flutter/persistence/export/delete proof. No feedback math, XP/layout, model/reference or training/history changes were identified in the repair scope/hash checks.

## Remaining gates and next ownership

Parent should resolve Important findings and obtain fresh coupled producer/consumer regressions/re-review before accepting repairs. Physical target-phone measurement, actual resource release/provisioning, uninterrupted integrated flow, all-sign/multiple-signer trials, model numerical gate, expert/anatomical validation, consent/privacy and participant authorization remain open. Those external gates do not excuse Q1–Q4. This report changes no tracked readiness/progress/gate disposition and closes no work item.
