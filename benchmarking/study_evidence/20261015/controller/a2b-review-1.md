# Independent A2b review 1

## Verdicts

- **Specification compliance: NEEDS_CHANGES** for the replacement-owner subscriber isolation gap F1. The acquisition/rollback, exception preservation, stream faults and queued camera-callback characterization otherwise satisfy the bounded host requirements reviewed here.
- **Code quality: NEEDS_CHANGES** for F1 and its missing replacement-without-new-listen regression. No broader refactor is requested. The existing factory/owned-release seam is appropriately small and is actually called by production configuration.

These are A2b-only verdicts, not runtime, host04, physical-performance or study acceptance. F1 is a source-traced defect in the supported initialization/replacement transaction; I did not execute a new JVM regression for it, and do not claim a demonstrated failure of ordinary one-shot Flutter startup.

## Scope and evidence identity

Read the binding `a2b/task-brief.md`, complete `controller/a2b-review-package-1.diff`, live five-file source/test package, `a2b/report.md`, production cleanup/VisionEngine/camera collaborators, and `controller/a2b-parent-verification-1.json`. The HEAD-relative MainActivity diff includes previously accepted behavior; this review does not relabel those changes as A2b fixes.

Independently computed SHA-256 values for all five A2b paths match the parent verification record. Independently checked all 82 protected files against the baseline's `protected[path].expected` values: no mismatches. All eight A2a accepted hashes in `a2b/source-manifest.json` match current files. `git diff --check` returned exit 0. No source, test, dependency, runtime or participant-store changes were made by this reviewer.

## Findings

### F1 — P2: successful publication inherits the displaced owner's subscriber

**Location:** `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/MainActivity.kt:171–180`, with delivery at `:262–282` and subscription assignment at `:54–58`.

Publishing B updates `initialization` and collaborator fields but leaves `eventSink` unchanged. Releasing displaced A subsequently skips the entire current-owner block (`:188–204`), including clearing that sink. Therefore, if A has listened and B is published without a new B `onListen` yet, B retains A's sink. A new B prediction captures `(deliveryInitialization=B, deliverySink=A's sink)`; both identity checks pass when its Handler runnable drains. B's benchmark completion callback (`:48–51`) also directly uses that inherited sink. Old callbacks being inert does not revoke the old subscription's ability to receive new-owner events.

This is distinct from the documented inability to unregister an old PlatformView factory or detach a different messenger. It is shared Activity state, present in the same production-used transaction exercised by the replacement tests. A new listener need not have arrived synchronously during channel registration. The existing replacement test explicitly writes B's sink (`ActivityInitializationTest.kt:70–72`), masking this transition. The failed-initialization/retry test starts with rollback clearing the sink and consequently does not cover successful replacement.

**Required narrow repair:** sever subscriber ownership when publishing a new initialization, before invoking its registration closure, without clearing a newer reentrant owner's subscriber during stale rollback. Alternatively bind subscriber state explicitly to its initialization and require matching subscriber ownership at both vision and benchmark delivery. Preserve the current early-acquisition-failure behavior that leaves viable A untouched.

**Required regression:** initialize A with a collecting sink; successfully initialize B without setting a new sink; emit a B prediction through the real Activity event handler and drain the main queue. Assert A receives nothing. Then attach B's sink and prove B delivery succeeds. Include the reentrant older-registration-fails/newer-owner-survives variant without assuming B already listened. No actual camera or default stores are needed. This is a requested regression, not a test executed during this review.

### C1 — nonblocking, explicitly bounded: inert is not detached

**Location:** `MainActivity.kt:149–156,188–205`; worker report lines 39–42.

Non-current initialization cleanup deliberately skips its registration-detach actions. That avoids deleting replacement handlers on a shared messenger, but does not establish removal of handlers retained by another messenger. Likewise, registry rejection rolls back and fences retained factories; it does not establish successful retry against the same registry ID. The report accurately retains both limits. I do not infer that cross-engine replacement is an established runtime path or demand an unrelated engine/registry redesign here. Acceptance must retain these limits and must not describe all retained registrations as physically detached. F1 remains actionable independently of these framework boundaries.

## Requirements otherwise supported

1. **Production acquisition seam:** `configureFlutterEngine` calls `initializeResources` after superclass configuration and permission request. The Android factory constructs the existing collaborators with application context, the shared pipeline lock, generation supplier and result callbacks. All closeable acquired handles are enrolled immediately; DataExporter has no acquired closeable handle in this seam. Fields publish only after all acquisitions succeed. Test factories do not fall back to the Android/default-store factory.
2. **Rollback and exception preservation:** current-owner rollback invalidates attempts, clears published fields/sink before detach/release, tries every enrolled cleanup, and suppresses cleanup errors under the original failure. Early acquisition failure preserves an existing viable owner. Published replacement failure releases displaced resources without restoring stale fields. Reentrant stale cleanup does not clear newer fields or invalidate the newer attempt. Normal owned teardown attempts later releases and superclass teardown even after a release error; the bare-Activity superclass exception is evidence of an attempted call, not a functioning Flutter lifecycle.
3. **Posted event fencing:** queued events capture initialization as well as subscriber identity; rollback/retry using the same subscriber cannot deliver the old event. Existing view-token and final Handler checks are preserved. These correctly reject old events; they do not solve F1's new event paired with an inherited old subscriber.
4. **Stream faults:** constructor model/labels close-only and read-plus-close tests verify native release counts, primary exception identity/message and suppressed failure counts. Runtime labels/gold tests verify exact stream close count, primary/suppressed identities, native wrappers remaining open until explicit close, continued attempt usability and idempotent engine close. Existing production `use`/constructor rollback already supports these cases; coverage-only GREEN is the correct description. No VisionEngine production repair is claimed for A2b.
5. **Queued camera callback faults:** the new test registers the actual constructor listener, completes SettableFuture before draining an explicit main Handler queue, distinguishes provider completion failure from shadowed bind failure, and covers replacement/disposal before callback execution. Real Preview/ImageAnalysis objects reach shadowed unbind on disposal after bind failure; the executor shuts down. This establishes orchestration, not CameraX driver release or successful camera binding.

## Verification readback and unexecuted boundaries

- The correct fresh parent evidence is `a2b/parent-full-forced-2.log`: `:app:testDebugUnitTest` and `:app:compileDebugAndroidTestKotlin` are executed, not UP-TO-DATE; the build succeeds. Parent verification records the corrected command applying `--rerun` to each target. The earlier `parent-full-1.log` had cached JVM execution and is not fresh independent JVM evidence.
- Independently parsed current JVM XML: 16 suites, **162 tests, 0 failures, 0 errors, 0 skipped**. The retained full-handoff XML also totals 162/0/0/0, and focused-handoff XML totals 33/0/0/0. These are readbacks of prior executions, not suites rerun by this reviewer. The first-parent XML snapshot alone does not prove freshness.
- Instrumentation Kotlin source compilation is supported by the forced parent log, not instrumentation runtime. No new build or test execution was performed during this review.
- Not executed: full FlutterActivity/FlutterEngine startup, permission delivery, actual BinaryMessenger installation/removal, same-engine registry retry, different-messenger replacement, actual CameraX acquisition/binding/driver release, MediaPipe/TFLite native release, installed end-to-end flow, ADB/emulator/phone, participant/default stores, physical measurements, collection or study acceptance.

**Disposition:** retain the successful bounded rollback/stream/callback evidence, but fix and regression-test F1 before accepting the currently advertised replacement-owner isolation contract. Only this review file was written.
