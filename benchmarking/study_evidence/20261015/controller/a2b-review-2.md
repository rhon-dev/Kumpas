# Independent A2b re-review 2

## Verdicts

- **Specification compliance: PASS at the explicitly bounded host scope, with C1 retained.** F1 is repaired and supported by a preserved behavioral RED/GREEN regression. The original staged acquisition, rollback/resource, asset-stream and asynchronous camera-callback requirements remain supported.
- **Code quality: PASS with the existing framework-boundary concern C1.** The repair is small, placed at the ownership transition, and preserves early-failure and reentrant-newer-owner behavior. No further blocking finding was identified in the reviewed package.

**Disposition: DONE_WITH_CONCERNS; suitable for parent acceptance of A2b's bounded host contract only.** This is not acceptance of runtime Flutter registration/detachment, same-registry retry, host04 as a whole, installed integration, physical performance or participant-study readiness.

## Scope, identity and independent checks

Read the binding `a2b/task-brief.md`, `a2b/review-fix-brief-1.md`, original `controller/a2b-review-1.md`, implementation reports, complete current five-file package and live source/tests. Reviewed the adjacent production factory, cleanup, VisionEngine acquisition/asset paths and CameraPreviewView queued callback/disposal paths. Loaded the study-readiness skill.

Independent read-only tooling established:

- All five current source/test SHA-256 values match `controller/a2b-parent-verification-2.json` (MainActivity `445c32a710890ee664d87d76b3daef86601256e3b7ec1925af704c0010338932`; ActivityInitializationTest `c817fdf081082e2c17666a3df9381a0e7f065afdd7f3737c30aa1ff712a57d7c`). The parent JSON contains the other three full values.
- The tracked MainActivity patch in `controller/a2b-review-package-2.diff`, reconstructed in memory against HEAD with every context/deletion line checked, produces the exact live postimage. All four full untracked package sections equal their live files. Raw diff comparison differed only because of context formatting; postimage identity was verified rather than assuming textual diff identity.
- All **82 protected** baseline hashes match `controller/host-baseline.json`'s `protected[path].expected`; all **8 accepted A2a** hashes match `a2b/source-manifest.json`. Against that original manifest, only MainActivity and ActivityInitializationTest changed; the remaining listed neighbors match.
- `git diff --check` returned exit **0**.

No source/test edits, build/test execution, dependency installation, default-store access, ADB/emulator/device operations or commits were performed by this reviewer. Only this report was written. Results below are independent source review and parsing/readback of retained actual executions, not a newly executed JVM suite.

## F1 — closed at the tested ownership boundary

**Repair:** `MainActivity.kt:171–184` stages all four acquisitions, publishes the new initialization, and clears `eventSink` at line 178 **before registration can reenter**. Early acquisition failures occur before this publication and do not revoke the viable owner's listener. Current-owner rollback clears state; stale rollback does not enter that block (`:195–217`), so it cannot clear the newer subscription or attempt. Existing final posted prediction checks still compare initialization, subscriber identity, attempt/generation and view ownership (`:269–289`).

The benchmark callback is now exposed by the narrow production-used `postBenchmarkReport(owner, report)` seam (`:145–151`), wired directly from the Android factory at `:47–49`. Its previously owner-guarded posted body is preserved; no benchmark producer behavior or channel contract was redesigned.

### Actual regression evidence

Parsed the retained XML rather than relying solely on the fix report:

- `a2b/review-fix-1-inheritance-red-xml`: **1 test, 1 failure, 0 errors, 0 skipped**. Failure is `java.lang.AssertionError: B prediction leaked to displaced A subscriber: [{"state":"prediction"}]`. The associated log identifies `successfulReplacementCannotInheritDisplacedSubscriberBeforeNewListen` as failed and the JVM task/build as failed. This is an assertion failure, not a compiler RED.
- `a2b/review-fix-1-inheritance-green-xml`: **1/0/0/0**; its log shows executed `:app:testDebugUnitTest` and `BUILD SUCCESSFUL`.

The current test at `ActivityInitializationTest.kt:45–72` first proves A can receive a control prediction, publishes B **without assigning B a sink**, emits through the real `handleVisionEvent`, drains the real main Handler shadow, and proves A receives nothing. It then assigns B's collecting sink through an explicitly reflective test seam and proves delivery. This reproduces the previously masked transition without claiming actual EventChannel subscription installation.

Additional coverage is correctly labeled post-fix GREEN, not independent RED cycles:

- **Reentrant no-listen/stale rollback** (`:74–116`): B publishes while older A registration is running; prediction and benchmark callbacks drain inside B registration before B listens, then drain again after A throws. A receives nothing. B remains current, its attempt survives, its handles remain unreleased, and stale detach is not invoked. Attaching B's sink later permits both event types. Existing already-listened reentrant coverage (`:169–196`) additionally proves stale rollback preserves the exact newer sink.
- **Benchmark ownership** (`:118–144`): A control completion is delivered; queued and subsequently posted stale-A completions are suppressed after B publication; B completion before listen cannot reach A; after B listens only B's expected completion payload arrives.
- **Early acquisition preservation** (`:246–278`): all session/exporter/benchmark/vision failures retain A's exact sink and current-owner identity, and real prediction plus posted benchmark delivery still reaches A. Partial acquired-handle release counts and once-only later destruction are checked independently.

**Exact delivery limit:** prediction delivery captures subscriber identity at enqueue time; benchmark completion checks initialization and uses the current sink when its posted runnable executes. The tests establish initialization replacement isolation, not a new subscriber-epoch/queue-drop contract for benchmark events within one still-current initialization. Neither test path installs a real BinaryMessenger.

## Original A2b requirements rechecked

| Requirement | Current evidence and bounded conclusion |
| --- | --- |
| Production-used staged acquisition | `configureFlutterEngine` invokes `initializeResources` after superclass configuration and permission request. `AndroidActivityResourceFactory` constructs existing SessionManager, DataExporter, BenchmarkMode and VisionEngine using application context and the existing lock/generation/result wiring. Each returned closeable handle is immediately enrolled; DataExporter has no closeable acquired handle here. Synthetic factories never fall back to production/default stores. |
| Later acquisition/registration failure, retry and publication | Activity tests cover all acquisition stages; registration failure with failing detach and all releases; concrete synthetic-native VisionEngine publication/close/retry; registry rejection with retained factory refusal; and failed replacement releasing displaced A without restoring stale fields. Fields publish only after acquisition completes. Fresh transaction retry is established; registry-ID retry is not. |
| Original failure and all cleanup attempts | Rollback sets released/current state before detach/release, tries every enrolled action, suppresses distinct cleanup errors under the original exception, and avoids repeated release. Tests check exception identity, ordered close counts, suppressed counts, cleared fields and surviving newer ownership/attempts. Normal destruction attempts registration cleanup, every resource and superclass cleanup even when earlier actions fail. The bare Activity's missing-delegate failure proves an attempted superclass call, not successful framework teardown. |
| Constructor/runtime stream faults | `VisionInitializationTest.kt:77–156` covers staged constructor failures, model/labels close-only and read-plus-close faults with native rollback failures, and runtime labels/gold close-only and read-plus-close faults. Assertions include original/suppressed identity for runtime faults, close counts, acquired wrapper release counts, usable engine after runtime fault, and idempotent engine close. Existing production `use` and constructor rollback support these cases; these are coverage-only GREEN, not a VisionEngine production fix. |
| Queued provider completion/bind failure | `CameraViewOwnershipTest.kt:39–86` uses the actual constructor-registered listener, a SettableFuture completed before an explicit main Handler drain, separate provider failure and shadowed bind failure, and stale/disposed-before-drain cases. Real Preview/ImageAnalysis objects reach shadowed unbind after bind failure; executor shutdown and repeated dispose are checked. Existing constructor ownership/rollback and final Activity view-owner fencing tests remain in the package. This proves callback/disposal orchestration, not actual driver release. |
| Existing persistence/subscriber/view regressions and scope | The full parent execution includes the existing boundary/resource/persistence/view suites. MainActivity event persistence and final delivery guards remain intact. Source-hash checks preserve A2a and protected files; no VisionEngine/camera/benchmark production changes were introduced by this F1 repair. No unrelated control/export harness was introduced. |

## Retained execution readback

Independently parsed snapshot totals (tests/failures/errors/skipped):

| Snapshot | Suites | Totals |
| --- | ---: | --- |
| `a2b/review-fix-1-focused-xml` | 5 | **36/0/0/0** |
| `a2b/review-fix-1-full-forced-xml` | 16 | **165/0/0/0** |
| `a2b/parent-fix1-full-xml` | 16 | **165/0/0/0** |

The parent's ActivityInitializationTest XML contains all **12** current test cases, including the three new replacement/benchmark tests and strengthened early-acquisition test. `a2b/parent-fix1-full.log` contains exact executed lines `> Task :app:testDebugUnitTest` and `> Task :app:compileDebugAndroidTestKotlin`, followed by `BUILD SUCCESSFUL in 11s`; these are not UP-TO-DATE lines. The runner/report correction applies `--rerun` to each task separately. Instrumentation evidence is **Kotlin source compilation only**, not instrumentation runtime. Historical pre-fix 162-test evidence is not substituted for the repaired package's 165-test execution.

## C1 and other explicit limits — retained, not silently solved

1. **Inert is not detached.** Noncurrent initialization cleanup skips registration-detach actions to avoid deleting replacement handlers. Owner guards prevent retained stale callbacks/factories from acting, but do not prove removal of handlers on a different messenger or release of all references retained by framework registrations. F1's shared-sink repair does not change this boundary.
2. **Same-registry retry is not guaranteed.** False registration results throw and roll back; retained factories are fenced. The synthetic transaction retry does not establish that a registry already holding `kumpas/camera_preview` will accept the same ID again. Cross-engine/different-messenger replacement is likewise not executed.
3. **Framework boundary precedes the seam.** Full FlutterActivity/FlutterEngine startup, superclass configuration failure, permission request/delivery, actual channel install/remove and a functioning Flutter delegate were not exercised. Enrolled synthetic detach actions prove transaction cleanup behavior, not real messenger detachment.
4. **Native/hardware limits.** Synthetic owned wrappers, shadowed provider operations and Robolectric streams do not prove MediaPipe/TFLite/CameraX native or driver release, successful physical camera binding, physical FPS/latency/thermal/recognition outcomes, or power-loss behavior.
5. **No broader acceptance.** No installed end-to-end camera/Flutter/persistence/export/delete flow, participant/default stores, physical collection, model/training changes or study acceptance was exercised or authorized here.

No new blocker was encountered. These are acceptance boundaries and the previously disclosed nonblocking C1, not claims that the unexecuted runtime guarantees are true.
