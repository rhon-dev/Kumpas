# Independent consolidated quality/security/correctness rereview

Review date: October 8, 2026, following the parent verification recorded at 00:54:33 +0800. Repository: `/Users/ahronjanl.rafaelahron.0804icloudcom/Documents/Thesis/kumpas`.

## Independent verdicts

- **Code quality/security/correctness: CHANGES REQUIRED.** The fixes materially improve retention, trust binding, construction rollback and stale-view disposal. Four Important residual defects prevent approval: confirmation-response disposition (R1), posted view-event ownership (R2), failed view-construction ownership (R3), and unsupported device-field rejection lost during binding (R4).
- **Specification: NOT FULLY COMPLIANT / REQUEST CHANGES.** The new bounded confirmation await does not guarantee correspondence between failed UI start and retained qualification. View ownership is not carried to the last posted delivery boundary or rolled back on early construction failure. Unsupported untrusted fields can now disappear without making evidence non-gating.
- **Critical findings:** none identified. **Important:** R1–R4. **Minor:** R5, a preexisting supporting asset-stream leak, not a constructor-rollback regression.
- **Runtime/physical/human/study acceptance: OPEN / UNEXECUTED.** These source findings are not unavailable-phone excuses. Conversely, correcting them will not establish real CameraX/native-resource release, continuous end-to-end flow, physical performance, human validation or participant authorization.

## Snapshot and method

Read the complete frozen `controller/review-package-3.diff`, all **3,829 lines**, including the tracked changes and seven untracked source/test files. Read the final fix brief, prior quality/specification reviews, closure plan, full fixer report, coupled live BenchmarkMode/MainActivity/VisionEngine/resource factory/camera ownership/view/Dart control/practice/collectors/history code and the new regression definitions. No empty BASE..HEAD shortcut was used: HEAD remains `6b8b1b6770e46bea7728a8e9ca4ae6d78e857640`, with the repair in the working tree.

Independently reconstructed each of the **27 frozen diff postimages** against HEAD and compared it to the live file: zero mismatches. The package is **234,814 bytes**, SHA-256 `3f0fe259e576ec85e2546ef0e3df555df74e75426f5097498094317ae295c5c0`. Independently rehashed the parent's **27 file identities** and **82 protected original identities**, at entry and again before this report: zero mismatches. Model/reference/training/evaluation/history/plots/handoff preservation is supported by those exact hashes, not a fixer assertion.

Read the actual parent native/Flutter/Python/release logs. Independently parsed existing JVM XML: **15 suites, 132 tests, zero failures/errors/skips**. Native parent log shows actual forced JVM execution and instrumentation-source compilation, successful debug/test packaging and assembly; it is not a clean-from-scratch build or instrumentation execution. Flutter parent output records clean analysis and **27 passing tests**. Python parent output records **41 tests, OK**. Release output records an ARM64 release build. Rehashed all three actual APKs against the parent manifest: debug **212,206,433 bytes**, test **382,400 bytes**, release **66,969,546 bytes**, all SHA-256 matches. Both application APKs contain the protected model with the expected SHA-256 `1f4543b8fb159dbe9a662f0b37e64b096f717d7527c45b2d7778f34bc0885aeb`. The earlier duplicate-generated-DEX failure remains separately preserved; successful final output does not erase it.

**No tests/builds were rerun.** Independent Python `-B` probes used synthetic fixture constructors, entirely mocked ADB and list-intercepted `append_entry`; no disk history/default stores/device/network/plots were exercised. They executed actual reader, binding, sanitizer, assessment and sink logic, not unittest suites. Kotlin/Dart race and fault findings below are static production control-flow proofs, explicitly not newly executed platform faults. This report is the sole write.

## Important remaining findings

### R1 — Native confirmation can qualify a start that the UI subsequently reports failed

**Locations:** `app/lib/ui/practice_screen.dart:209–225,285–303`; `app/lib/feedback_engine/kumpas_channel.dart` confirmation wrapper; `BenchmarkMode.kt:90–99,325,341`; `MainActivity.kt:114–117`; `collect_fps.py:35–36,533–544`. Related requirement: final fix brief slice 2, persistent diagnostic disposition and bounded confirmation; `environment_protocol.md:174–180` states that confirmation-response failure does not establish successful control ownership.

**Scenario:** Start's valid UUID reaches the current widget before its initial watchdog. Dart cancels that timer, sends confirmation, and awaits the response for another 30 seconds. Native promptly writes/readbacks `confirmed` and sets `controlConfirmed=true`, but the RPC response is lost, stalls or errors after that native side effect. Dart times out/errors and presents **“Benchmark could not start”**. It never assigns `_benchmarkRunId` or `_benchmarkStarted`, because those assignments are after the await. Neither the catch/finally nor disposal records an abandoned disposition or cleans up this already-known identity. Native can finish the full observation with confirmed report/companion and qualify it. Retrying while it remains active encounters busy; this is also lost run-identity/recovery state.

Disposal during confirmation has the same missing control-disposition path: the post-await mounted/generation check simply returns. Normal current-camera disposal may independently invalidate camera qualification, so this review does **not** claim every disposed-widget run passes. The mounted timeout/error scenario alone establishes the blocker.

**Evidence:** Native writes the authoritative status before `result.success`; the UI decides success only after its response. There is no revocation/failed-owner method or native expiration of an already confirmed run. An independent synthetic report representing that confirmed full-window state passed the actual mocked reader→assessment→sink in **both FPS and camera latency**: `status=0`, `gate=True`, no rejection reasons. This establishes that host qualification has no separate evidence of successful UI receipt. It is a consumer probe plus source trace, **not** a claim that a real Kotlin/Flutter RPC was made to hang.

**Coverage limitation:** The widget mock always immediately returns true for `confirmBenchmarkStart`. Native confirmation-deadline/publication tests exercise producer acceptance and readback failure, not “native committed successfully, response hangs/errors.” The native unconfirmed A→host replay is useful but tests a different state.

**Fix guidance:** Retain the received identity before entering confirmation and define an ownership commit/terminal-disposition protocol whose UI classification agrees with durable qualification. Do not turn uncertain confirmation into UI failure while leaving an irreversible confirmed qualification behind. A scoped revocable/expiring disposition checked by collectors, or a deliberately revised UI ownership-commit ordering with retained identity and conservative uncertainty handling, must cover lost replies and disposal. Merely issuing a best-effort stop after timeout is not enough when that call also hangs or the immutable report is already closed. Add producer/consumer plus widget regressions for native successful confirmation with never-returning/error/late response, before/after deadline, disposal and replacement B. Preserve immutable measured bytes, samples/censors, and B ownership.

### R2 — View token stops analyzer/provider work, but not its already-posted Activity event

**Locations:** `CameraPreviewView.kt:34–35,64–95`; `CameraViewOwnership.kt:8–12`; `VisionEngine.kt:203–247`; `MainActivity.kt:154–203`, especially the posted closure at **186–200**. Related requirement: final fix brief slice 4, final shared-state callback boundary rather than only pre-asynchronous checks.

**Scenario:** A current analyzer runs under `runOwned(A)` and invokes `handleVisionEvent`, which posts a prediction/warmup/no-signer event. Before that Handler runnable executes, the main thread registers replacement view B and/or switches the event subscription/run. At execution, the closure reads the **current** eventSink and benchmarkMode; ordinary camera events are not attempt events, and have neither a view token nor a delivery-generation check. It therefore delivers A's stale label/visibility/warmup into B and calls `recordEvent()` against the current benchmark. B registration changes only `CameraViewOwnership.current`; it does not change the Activity attempt generation or supply a token to the queued event. Stale A disposal deliberately no longer invalidates B, so it does not remedy this queue.

**Evidence:** Static two-boundary trace. The source passes no view token through onFrame/onResult/handleVisionEvent. The posted predicate checks attempt identity and, for camera_error only, attempt generation; it cannot consult A/B ownership. This is a retained supporting asynchronous defect, not a claim that the now-correct stale default disposal still unconditionally cancels B.

**Coverage limitation:** `CameraViewOwnershipTest.queuedCallbacksCannotMutateReplacement...` invokes `a.runOwned(callback)` **after** B exists. It never posts an A event while A is current, then registers B before draining the Handler. The synthetic engine's `onResult={}` also excludes actual Activity emission from those callback assertions.

**Fix guidance:** Carry view ownership to the posted delivery boundary and recheck it under the Activity's pipeline lock immediately before UI delivery/event counting. Preserve independently justified terminal persistence/accounting; do not erase completed samples just to hide stale UI. Add a real Handler/EventSink regression with A emission queued while current, B registered before queue drain, and assertions that B receives no A label/visibility/error or event count. Include unchanged attempt-generation cases, since view identity is intentionally distinct from capture generation.

### R3 — A failed replacement view construction leaves an unreachable current owner

**Locations:** `CameraPreviewView.kt:34–48,124–139`; `CameraViewOwnership.kt:8`; factory `MainActivity.kt:132–136`.

**Scenario:** Live view A exists. Construct replacement B: `ownership.register()` immediately makes B current, **before** PreviewView creation, executor setup and the unguarded `ProcessCameraProvider.getInstance`/listener-registration calls. Any later synchronous initialization exception makes the constructor fail, so the factory never returns a disposable B. There is no rollback of that token or the executor. A is now stale and all its analyzer/provider `runOwned` calls are refused, while disposal of A cannot release the phantom B or coherently cancel its shared state. An executor allocated before the failure has no teardown owner. The `disposalActions` field is initialized after the init block, so it cannot rescue this failure path.

**Evidence:** Static acquisition/ownership ordering; no real provider fault was injected in this review. This consequence is introduced by registering shared ownership ahead of fallible construction. It is separate from VisionEngine's now-correct staged native constructor rollback.

**Coverage limitation:** All new default ownership tests construct views with `bindCamera=false`; their injected faults are clear/unbind during disposal. They do not exercise a failing provider acquisition/listener registration or view construction before a PlatformView is returned. The brief explicitly requested early-exception coverage.

**Fix guidance:** Stage fallible owned initialization, then publish ownership, or add a constructor rollback protocol that releases B's owned resources and restores a still-valid prior owner (or coherently invalidates through the Activity boundary) without touching a newer C. Ensure executor and any acquired use cases are attempted even when cleanup fails; preserve the original exception. Use a narrow production acquisition seam to cover these faults and A/B/C identity outcomes, not a detached helper test.

### R4 — Identity binding silently removes unsupported device fields before fail-closed validation

**Locations:** `collect_fps.py:329–333,443–454,486–499,527–544`; shared consumer `collect_latency.py:87–94`. Related requirement: closure plan slice A — unknown content must be omitted/normalized **and** non-gating.

**Scenario:** A otherwise-valid untrusted camera report contains `device.raw_video="PRIVATE patient text"` (or another unsupported device member), with all legitimate device identity fields matching the selected host. `bind_report_metadata` reconstructs `device` using only trusted names plus sdk/emulator fields, silently discarding all other source keys. The subsequent allowlist sees no unknown key, and binding returned no rejection. Both reader and sink repeat this loss of the unsafe indicator. The report can now qualify, although the previous direct sanitizer would have rejected the unsupported member.

**Executed evidence:** Independent actual mocked `read_report→validate_report→log_collection` probe returned **`status=0`, `gate=True`, `collection_errors=[]`** for that input. The private marker was **not retained**. This is a fail-closed/provenance rejection regression, **not** a demonstrated privacy leak or claim that raw video entered history.

**Coverage limitation:** Existing unknown-payload tests put raw_video at the top level or landmarks inside a trace. The wider recognized-text census changes recognized fields, not unsupported members inside the device object that binding replaces.

**Fix guidance:** Detect unsupported source keys before reconstruction, preserve a fixed rejection flag/error, and still retain only the independently trusted identity values. Add reader-to-sink coverage for unknown keys inside report.device for FPS/latency/interpreter modes, requiring marker-free retained diagnostics and no gate. Do not restore the untrusted values merely to preserve the rejection indicator.

## Minor supporting finding

### R5 — Non-constructor asset reads still do not close their streams

**Locations:** `VisionEngine.kt:74–85`: lazy `loadGold()` and callable `labelsJson()`; `MainActivity.kt:57` invokes the latter; `VisionEngine.kt:285` reaches the former during feedback.

Both call `assets.open(...).readBytes()` without `use`/finally. Reading the bytes does not close the acquired stream; read/decode/parse failures likewise have no close path, and engine.close only releases detectors/interpreter. Repeated getLabels calls can accumulate streams until finalization; lazy gold loading also leaks its stream. These exact paths are unchanged from HEAD and are **preexisting support**, not evidence that the new constructor rollback failed. The constructor model/label reads at 117/121 now correctly use scoped closure.

Use `use` on both supporting reads and add success/read-failure closure assertions at their actual production seams. The new resource factory is currently used only for constructor assets; its synthetic stream assertions do not cover these runtime methods. Classify as a narrow follow-up, not a blocker for the specific staged native-acquisition rollback. No observed Android descriptor count or real detector release is claimed.

## Substantive fixes supported / scope retained

| Previous concern | Independent current assessment |
|---|---|
| F1/Q1 recognized-text privacy/trust | Exact SHA/revision/chip/UUID/fixed-code retention, producer invalid-setup stripping and host name/package binding are implemented. Independent **24** actual mocked reader/sink cases across all three modes rejected contamination with no marker in saved entries. Trusted names remain present. R4 is a distinct unsafe-indicator regression; syntax-valid opaque IDs are documented as syntax, not human-name provenance. No blanket semantic privacy/attestation claim is accepted. |
| Q2 original delayed start response | Default unconfirmed companion/report and closed/late confirmation rejection repair the original never-received-start case. A scoped companion is atomically replaced/read back; measured immutable reports remain untouched. **R1 leaves the subsequent confirmation-response window open.** |
| F2/Q6 late stop | Six permanent completer/deadline/disposal/late-success/error widget cases cover 29,999/30,000/30,001ms, one coded diagnostic, no raw private error/unhandled future, and replacement status. Honest coverage-only GREEN is appropriate. These are late-stop tests, not R1 confirmation tests. |
| Q3 partial native engine initialization | Actual constructor stages pose/hand/model/interpreter/labels, closes streams, attempts every acquired release, retains original/suppressed exceptions and transfers ownership only after label parsing. Factory defaults preserve detector/Interpreter options. New constructor tests are not Unsafe bypasses; nullable synthetic handles prove orchestration, not real release. R5 is separate unchanged support. |
| Q4 stale view disposal | Default disposal correctly restricts global camera/capture effects to current owner, routes Activity cancellation/outcome coherently, and still attempts stale view's own clear/unbind/shutdown after faults. Repeated disposal is guarded. Provider/analyzer work checks ownership under the final pipeline lock. **R2/R3 prevent claiming all view boundaries/faults are closed.** |
| Q5 failure census | Native fixed vocabulary/generic fallback and host numeric schema agree, including SecurityException/FileNotFoundException. Unknown exception messages/class labels are not retained as arbitrary benchmark text; category/total tests now exist. |
| Earlier committed-target fixes | Exact immutable/latest bytes and run-ID readback precede successful reportPath/state; partial publication is non-gating. Control readback faults also leave report unconfirmed. A successful AtomicFile return alone is not accepted. No power-loss durability proof is inferred. |
| Earlier persistence/window/history work | Pending capture terminal reason, scoped cancellation, posted attempt-generation guards, immutable start-time setup/APK checks, half-open traces and censor denominators, native persistence-failure/retry, assessment form retention and permanent serialization/partial-write/fsync/replace/lock/retry regressions remain in the complete package. Their clocks are analyzer/event/native ACK, not sensor exposure/display. Historical stores/figures and model/reference mathematics were not changed. |

## Acceptance/disposition boundary

For the 16-checklist repair, **5/6** cannot be fully closed because of R1; **4/11** cannot be fully closed because of R2/R3; **15** retains a fail-closed contract blocker R4 despite substantially repaired privacy retention. R5 is the explicitly classified minor supporting ownership follow-up. Parent-owned documentary adjudication (1) must reflect these findings, not the fixer's DONE_WITH_CONCERNS or green suites. The narrow supported persistence/capture accounting/publication/window/clock/plot/setup/blank-form/history portions of **2/3/7/8/9/10/12/13/14/16** remain supported within their recorded evidence limits; this is not wholesale all-16 acceptance.

Obtain focused regressions and fresh independent review of the exact amended snapshot before accepting the software task. Keep real CameraX/provider/resource-release faults, uninterrupted Flutter/native/persistence/export/delete flow, actual device provisioning and USB handoff, physical sustained FPS/latency/thermal/all-sign/signers, model numerical/provenance limits, expert/anatomical/human validation, consent/privacy approval and participant-study authorization separately open. This report changes no source, readiness/gate/progress disposition, study data or artifact and grants no physical/study approval.
