# A2b review fix 1 — incremental implementation evidence

Status: in progress; no acceptance claim. Binding brief and independent review read in full; study-readiness and TDD loaded.

## Scope
Only MainActivity.kt and ActivityInitializationTest.kt source/test edits, plus this evidence and runner correction. Existing unrelated work preserved. No default participant stores, device/ADB/emulator, installations, commits, resets or clean operations.

## Initial finding and intended vertical slice
F1 is source-traced but not yet behaviorally reproduced: new initialization publication leaves the displaced subscriber in eventSink. First add a real initializeResources/handleVisionEvent/Handler regression with no B listener, run RED before production changes, then minimally clear the subscriber at publication. Exercise reentrant stale rollback, early acquisition preservation and the production benchmark callback via a narrow production-used seam if needed.

## Evidence ledger
Commands/exits/logs are appended after each execution to review-fix-1-ledger.jsonl and this report. Historical evidence remains untouched.

## Boundaries retained
C1: stale registrations can remain inert rather than physically detached; same-registry retry and cross-messenger detachment are not established. No fabricated BinaryMessenger runtime. Parent independent verification and spec/quality re-review remain required.
- `review-fix-1-inheritance-red`: exit 1; log `review-fix-1-inheritance-red.log`; exact command in ledger.
- `review-fix-1-inheritance-green`: exit 0; log `review-fix-1-inheritance-green.log`; exact command in ledger.
- `review-fix-1-focused`: exit 0; log `review-fix-1-focused.log`; exact command in ledger.
- `review-fix-1-full-forced`: exit 0; log `review-fix-1-full-forced.log`; exact command in ledger.

## Behavioral result and narrow repair

- Actual pre-production-change RED: one test, one assertion failure, no errors. Exact XML failure: `B prediction leaked to displaced A subscriber: [{"state":"prediction"}]`. A first received a control prediction; B then initialized successfully without assigning its sink, and its prediction reached A after real main Handler draining. RED XML and log were preserved before GREEN.
- Minimal behavioral change: clear `eventSink` immediately upon new initialization publication, before registration/reentrant callbacks. Early acquisition failures occur before this line and retain viable A. Stale rollback still cannot clear a newer subscriber; existing queued initialization/view/subscriber fencing is unchanged.
- Same regression GREEN: one test passed. Additional reentrant/no-listen and benchmark tests are coverage-only GREEN after the demonstrated fix, not claimed independent RED cycles. The reentrant test emits and drains inside B registration and after older A throws; B ownership, active attempt and unreleased resource handles survive, and later B subscription receives vision plus benchmark events. Existing reentrant-already-listened test remains green.
- Benchmark callback body was extracted unchanged to internal `postBenchmarkReport(owner, report)`, called by the real Android factory callback. This narrow production-used host seam permits exact Handler callback tests; no BenchmarkMode production change, fake BinaryMessenger or claim of actual channel installation. Tests prove no inherited subscriber before listen, queued/stale A completion suppression, and B completion payload after listen.
- Early acquisition failure test now observes actual prediction and benchmark delivery to A for all four failed acquisition stages, not only sink identity.

## Runner correction and fresh verification

- Corrected existing runner full mode to `:app:testDebugUnitTest --rerun :app:compileDebugAndroidTestKotlin --rerun`; --rerun is task-specific. Earlier reports/logs were not overwritten. Review-fix labels append to their own ledger/report and preserve unique XML snapshots.
- Focused JVM: {'tests': 36, 'failures': 0, 'errors': 0, 'skipped': 0}. Full JVM: {'tests': 165, 'failures': 0, 'errors': 0, 'skipped': 0}. Both final targets executed (exact unsuffixed task lines), not UP-TO-DATE. Instrumentation Kotlin source compile exit 0; no runtime instrumentation.
- Compared 82 protected hashes and 8 accepted A2a hashes: zero mismatches. Other original A2b manifest source/test paths unchanged. `git diff --check` exit 0. Full source hashes/task/XML details: `review-fix-1-verification.json`.

## Handoff — DONE_WITH_CONCERNS

Changed source: MainActivity.kt and ActivityInitializationTest.kt only. Evidence: corrected run-host-tests.py, review-fix-1-report.md, review-fix-1-ledger.jsonl, review-fix-1-verify.py, uniquely named RED/GREEN/focused/full logs/XML, verification/hash JSON and diff-check log. No commits.

Parent independent verification and spec/quality re-review are required; this report does not accept A2b. C1 remains: noncurrent registrations are fenced/inert, not proven detached on a different messenger; successful same-registry-ID retry remains unestablished. Full configureFlutterEngine/permission/BinaryMessenger runtime, real camera/provider/native driver release, installed end-to-end flow, physical measurements and study acceptance were not executed. No implementation blocker encountered; expected behavioral RED is retained as failure evidence.
