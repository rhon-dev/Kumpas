# Independent consolidated specification re-review — frozen package 3

Review context: October 7 campaign / October 8 (+0800) continuation. Repository: `/Users/ahronjanl.rafaelahron.0804icloudcom/Documents/Thesis/kumpas`. This is a read-only source review, not implementation, device verification or participant authorization.

## Verdicts

- **Specification: NOT FULLY COMPLIANT / CHANGES REQUIRED.** The original lost-start-response case now fails closed, but the new confirmation RPC introduces an acknowledgement-loss/abandonment hole (R1). Recognized-text cleanup fixes the previous malformed-marker examples and binds device/package names, but syntax-valid opaque/private labels remain retainable and can qualify (R2). Package-metadata acquisition failure also discards already-read measured diagnostics, and missing report version text bypasses the unavailable-trust gate (R3).
- **Task quality: REQUEST CHANGES.** Meaningful staged constructor rollback, actual default camera-view disposal ownership, fixed failure vocabulary and permanent hung-stop coverage are present. Passing tests do not cover the decisive new confirmation-response failure cases. Do not accept the software task merely because 132/27/41 tests and APK builds succeeded.
- **Runtime / physical / human / study: OPEN / UNVERIFIED.** No installation, instrumentation execution, real CameraX race/release, continuous camera/channel/UI/persistence/export/delete flow, actual provisioning, phone performance, expert validation or participant acceptance was executed by this review.

**Decisive software blockers:** R1 (IDs 5/6 and retained-control qualification under 8), R2 (ID 15, setup retention under 13), R3 (IDs 13/15 and diagnostic-retention quality). R4 is a smaller new companion-schema defect. R5 is a source-derived early-construction ownership risk/evidence gap, not a claimed observed Android failure. ID 1 remains parent documentary adjudication. These findings are not unavailable-hardware excuses.

## Scope and snapshot verification

Read the complete `controller/final-review-fix-brief-1.md`, original `docs/superpowers/plans/2026-10-07-review-closure.md`, complete `review_fix_1/fix-report.md`, and both complete prior reports `controller/spec-review-1.md` and `controller/quality-review-1.md`. Read **all 3,829 lines** of `controller/review-package-3.diff`, consecutively in five pages, including all tracked changes and all seven new source/test files. The review did not substitute BASE..HEAD for the working diff. HEAD remains `6b8b1b6770e46bea7728a8e9ca4ae6d78e857640`; an empty commit range does not imply no fixes.

Traced the complete current BenchmarkMode, CameraPreviewView, MainActivity, Dart practice control path, FPS collector and latency collector, plus the constructor/ownership helpers and their full new tests in the frozen package. Reviewed all changed regression definitions, setup/protocol documentation, the original all-16 disposition requirements and prior preservation boundaries. Read parent native/Flutter/Python/release logs, manifest and exact generated-DEX quarantine record. This is a complete review of the supplied frozen change package and relevant coupled contracts, not an audit of every unchanged repository file or every possible adversarial input.

Independent read-only hashing against `controller/reviewfix-parent-verification-1.json` returned:

```
HEAD 6b8b1b6770e46bea7728a8e9ca4ae6d78e857640
frozen 27 []
protected 82 []
diffcheck 0
```

Thus all 27 frozen file hashes and all 82 protected original hashes matched at review entry. Independently read back all three APK paths: each SHA-256 and size matched the parent manifest. Protected history/model/reference/training/evaluation/figures/handoff bytes were not regenerated or edited.

No suite or build was rerun. No real ADB, device, installed/default store, participant data, plots or repository history was exercised. The review's Python probes used actual collector/reader/assessment/sink functions, completely mocked ADB and an in-memory replacement only for `append_entry`. They inspected the exact payload handed to persistence; they did not write history. The requested review report is the only write.

## Executed evidence assessed, not newly rerun tests

- Independently parsed the current matching JVM XML: **15 suites, 132 tests, 0 failures, 0 errors, 0 skips**. The XML contains the new constructor, default-view ownership, confirmation-deadline/fault and full-window unconfirmed regressions.
- Parent `native-reviewfix-parent-2.log:48,95,101–112` shows actual forced unit execution and instrumentation-source Kotlin compilation, debug/test APK packaging and exit 0. Many prerequisite tasks remained UP-TO-DATE; this is not a pristine clean rebuild or installed instrumentation run.
- `flutter-reviewfix-parent-1.log:1–2,19–31`: clean analysis; **27 Flutter tests**, including all six hung-stop completion/disposal cases.
- `python-reviewfix-parent-1.log:1–46`: **41 Python tests, OK**, including recognized-text history probes and permanent history fault tests.
- `release-reviewfix-parent-1.log:1–7`: exit-0 ARM64 release APK build. Manifest identities: debug `4c8ee8cb0fb283ce24d768e358bb05c07d54131a06bad3d7b90ada2970059090`; Android test `c276116bc3bad24383101f07191f1e71d29fa52c16fc4b3a6b38bec5b024b291`; release `ebe520dd92847e85a87de4708692904d673c7f870751a5fe587b0bda8633680e`. Embedded model recorded as `1f4543b8fb159dbe9a662f0b37e64b096f717d7527c45b2d7778f34bc0885aeb`; protected source model matched independently.
- The first parent build failure is preserved in `native-reviewfix-parent-1.log`; `generated-dex-quarantine-1.json` identifies exactly six ignored generated duplicate DEX files, their bytes/hashes and quarantine destinations. The successful rerun followed that narrowly scoped generated-file quarantine without source edits, reset or clean. The duplicate origin is **not established**; do not call this an identified source regression or conceal it as an uninterrupted first-pass build.

The fix ledger honestly distinguishes behavioral RED/GREEN from coverage-only GREEN for existing stop timeout behavior and prior history behavior. The wider privacy census passes because its marker includes spaces, which do not satisfy the remaining opaque-ID/chip contracts; that does not establish semantic/provenance closure for every recognized string.

## R1 — Important: native confirmation can qualify an owner whose confirmation response never succeeds

**Affected finding:** Q2, with new protocol scope under F2/Q6. **Exact locations:** `app/lib/ui/practice_screen.dart:179–225,286–302`; `app/lib/feedback_engine/kumpas_channel.dart:59–61`; native `BenchmarkMode.kt:90–99,325,341`; `MainActivity.kt:114–116`; host `collect_fps.py:35–36,535–537`; protocol `benchmarking/environment_protocol.md` “Start-control ownership and retention”.

Native `confirmStart` atomically writes `status=confirmed` and sets `controlConfirmed=true` **before** MainActivity returns the method response. Dart cancels the original start watchdog at line 209, then awaits a separate bounded confirmation future. A timeout/error at that await only displays a snackbar and releases `_benchmarkStarting`. Disposal invalidates the local generation; a late confirmation success after disposal is simply ignored. There is no persisted abandonment/revocation/lease or terminal disposition for a known run in any of those branches. Identity-scoped stop alone would not cure an already closed report.

**Concrete feasible ordering (source-derived, not a phone observation):** native run A starts at t=0; valid start identity reaches current Flutter owner at t=29; confirmation executes at t=29 and persists confirmed; the confirmation response is lost/delayed. Flutter times out that response at t=59. Camera measurement continues through t=60, producing a complete report and confirmed companion. A delayed confirmation reply at t=65 cannot repair the earlier failed owner state. At t=60 both the native gate and host control checks can accept the confirmed state, subject to their ordinary sample/setup requirements, even though Flutter never acknowledged successful confirmation and offers Retry. No unbounded-future assumption is needed: the Flutter await **is** bounded, but bounding a future does not undo the native effect. The numbers in this example were checked with a Python timeline calculation.

Related cases: native confirmation applied then method error/response loss; disposal or replacement while confirmation is pending; full measurement closing before the confirmation future resolves; and late confirmation success/error after UI timeout. The known ID is not retained as pending ownership for cancellation/disposition in these paths. A replacement must remain protected, but A's prior confirmed companion must not falsely establish the abandoned flow's successful control ownership. A normal successfully acknowledged benchmark remaining measured after later navigation is a different policy; do not conflate it with abandonment during the new confirmation handshake.

**Evidence boundary:** the state transition is explicit in native source, and the absent cleanup/disposition is explicit in Dart. The current widget mock in `app/test/practice_flow_test.dart:67–69` always returns `true` for confirmation. Its hung completers concern original start and late stop, not confirmation. Native `confirmationDeadlineAndPublicationFailureFailClosed` covers request arrival at 29999/30000/30001ms and write fault; it does not cover response delivery/owner abandonment. No live confirmation-loss experiment was executed, and this report does not pretend the separate Flutter and native tests form one live cross-language session.

**What is repaired:** an original start response that never arrives cannot trigger confirmation at all. I independently extracted the current parent XML's actual `NATIVE_CONTROL_FIXTURE` (run `a0bf9b27-ad9b-4e0b-941a-f61d2c7ca7ad`) and replayed its real unconfirmed producer report through both actual host assessments/sinks. Ordinary unconfirmed, missing, empty, mismatched companion and a companion-only forged confirmed upgrade all returned status 1 / gate false while retaining `complete=true` and `analyzer_count=1800`. The worker's saved fixture has a different synthetic UUID from the later parent execution; it was not falsely represented as byte-identical to the parent XML. The final replay used the parent's actual printed object.

**Required closure:** define durable owner disposition covering the confirmation RPC's uncertain result, including a producer-owned fail-closed deadline/lease or equally authoritative scoped mechanism. Do not repair only by adding another optimistic RPC and assuming its response cannot be lost. Keep measurement payloads immutable; an abandonment mechanism must be independently checked by collectors and remain non-gating on missing/unreadable/uncertain disposition. Preserve sample/censor outcomes and B's active state. Add controllable confirmation completers/errors, exact deadline assertions, disposal/replacement and full-window-close scenarios; replay actual producer dispositions into both host gates. Reconcile the docs' explicit claim that confirmation response failure does not establish successful ownership with the implemented state machine.

## R2 — Important: syntax-valid recognized labels still retain private text; semantic trust is not supplied by the regex

**Affected finding:** F1/Q1. **Exact locations:** native `BenchmarkMode.kt:106–121,149,152,177–191,195–198,320–322`; host `collect_fps.py:56–66,426,431–432,465–466,476–518,527–555`; current privacy census `benchmarking/test_collectors.py:159–202` (frozen diff lines 2961–3004); metadata-boundary documentation at the end of `environment_protocol.md`.

Independent actual mocked-reader → assessment → actual sink-to-entry probes used these values, each in an otherwise valid synthetic report:

| Recognized report field | Input | FPS / camera-latency result | Interpreter result |
|---|---|---|---|
| `setup.setup_id` | `PRIVATE_patient_text` | status 0, gate true, marker retained, no errors | status 1, gate false, marker retained |
| `camera.camera_id` | `PRIVATE_patient_text` | status 0, gate true, marker retained, no errors | status 1, gate false, marker retained |
| `setup.chip` | `Snapdragon 680PRIVATE` | status 0, gate true, marker retained, no errors | status 1, gate false, marker retained |

These are in-memory persistence payload results, **not observed participant leakage or writes to repository history**. The unchanged history serializer has no further sanitizer. The original marker `PRIVATE patient text` now disappears because spaces violate these particular contracts; changing the marker to permitted characters exposes the remaining boundary. Rejection is also not protection: interpreter diagnostics retain the same values despite never having a physical pass.

**Important provenance distinction:** real CameraPreviewView supplies `Camera2CameraInfo.cameraId`, not a user name. Native Build/package strings and streaming APK/model digests also have genuine producer provenance. The mocked camera-report probe demonstrates what the host accepts from an untrusted report; it does not demonstrate that Android's actual camera API emitted private text. Conversely, `setup_id` and `chip` are directly loaded from the supplied setup file. The native regex explicitly allows the demonstrated setup values, so arbitrary alias/suffix retention is a real source-side contract, not merely an imagined host exploit. `[A-Za-z]*` is not a closed list of legitimate chip suffixes. Manual verification flags and a warning not to put names in identifiers do not supply a programmatic privacy boundary.

The new docs accurately admit that opaque IDs have syntax checks, not human-name provenance. That admission avoids an attestation overclaim but does not by itself meet the brief's broader requirement: “A permissive label regex alone is not trustworthy provenance or a semantic privacy guarantee.” If parent deliberately narrows privacy to *malformed inputs only plus trusted operator provisioning*, that must be an explicit requirement adjudication, not inferred acceptance from the space-containing marker tests.

**Required closure:** use a genuinely bounded/generated identity representation or independently trusted provisioning binding for free-form setup aliases; avoid retaining unsupported aliases in either native reports or rejected host history. Tighten chip representation to supported verified vocabulary/suffixes or independently trusted provisioning data; do not try to detect human names heuristically. Preserve legitimate independently verified device/manufacturer/build names and numeric diagnostics. For camera IDs preserve trusted native identity/change checks, while either binding retained host copies to an authoritative source or clearly scoping an explicitly approved trusted-producer boundary; do not claim that regex alone proves provenance. Add syntax-valid adversarial regressions, native setup publication assertions and all three ingestion paths. A universal promise against encoded information in hashes/IDs is not requested; the specific unnecessary cleartext aliases/suffixes above are the demonstrated issue.

## R3 — Important: unavailable package metadata either erases diagnostics or is bypassed by an omitted report field

**Exact locations:** `collect_fps.py:316–341,354–359,509–524,527–555`; `collect_latency.py:77–94,112–117`. Brief slice 1 explicitly requires safe diagnostics and fail-closed qualification when trusted identity is unavailable.

**Executed failure probe:** actual mocked `read_report` had already acquired valid synthetic report/device/APK metadata when `dumpsys package` raised a synthetic RuntimeError. `collect` converted the entire acquisition to `report=None`. Actual sink output was:

```
build_acquisition_failure {
  "collected_report": null,
  "retained_results": {},
  "gate": false,
  "private_in_retained_entry": false
}
```

The gate is safely rejected and private exception text does not reach persisted history, but the measured report, analyzer counts and named trace diagnostics that were already successfully read are lost. The interpreter reader similarly lets the new package-info step escape after its report has been parsed. This is a new failure coupling introduced by the trust-binding extension, not a phone-only limitation.

**Executed missing-field probe:** with an otherwise valid report whose `build.version_name` was omitted and mocked package output yielding no supported `versionName`, actual reader/assessment/sink returned **status 0 / gate true / errors []** for both camera gates. `bind_report_metadata` checks package-name trust only when the untrusted report includes the key. Thus unsupported/unavailable independent package text fails closed when the field is present, but its absence avoids that rejection. No private text is retained in this second case; it is a qualification/evidence-contract issue, not another leak. Numeric build fields are not independently package-bound by the current helper.

**Required closure:** catch package metadata acquisition/parse failure inside the reader, retain the sanitized already-read numeric report and selected safe device metadata, omit unsupported build text, append one fixed unavailable diagnostic and reject qualification independently of the untrusted field's presence. Apply consistently to camera and interpreter paths. Add mocked acquisition-throw, ambiguous/absent package text, missing report version text and valid trusted-name preservation tests. Do not invoke real ADB or erase samples to make the test fail closed.

## R4 — Minor new companion contract defect: boolean/float schema versions qualify

`collect_fps.py:535–537` uses ordinary equality for `schema_version != 1`. Actual sink probes with otherwise valid qualifying report/device/build/control returned:

```
companion_schema True status 0 gate True
companion_schema 1.0 status 0 gate True
companion_schema 1 status 0 gate True
companion_schema 2 status 1 gate False
```

The native producer emits an integer; `true` is not that schema contract. This does not turn an unconfirmed report into confirmed by itself, and is not evidence of compromised app-private storage. It is a malformed-companion fail-closed gap in the new authoritative check. Require `type(version) is int` and version 1, exact scoped identity and fixed status; cover malformed JSON/duplicate keys, boolean/float/null versions and missing/unreadable state for both collectors. Keep raw companion/private extras out of retained diagnostics. No unrelated attestation system is needed.

## R5 — Source-derived additional early-construction ownership risk, not a deployed leak claim

`CameraPreviewView.kt:34–47` publishes an owner token before PreviewView/executor/provider-listener acquisition completes. If PreviewView creation or synchronous provider/listener setup throws, the platform view is never returned and its disposal list is unreachable. The new current token can remain registered without a view; if the executor has been acquired it has no constructor rollback. `CameraViewOwnership.register` has no acquisition transaction/rollback. This is an older supporting camera acquisition weakness with a new token side effect, not proof that the tested normal callbacks leak or that real CameraX threw.

The new tests disable provider binding and invoke `runOwned` synthetically; they cover disposal failures and queued ownership boundaries, not constructor exceptions from the actual setup path. Stage acquisition/registration or add narrow production fault seams and rollback, preserve the original failure and attempt all acquired releases. Decide explicitly whether failed replacement registration should leave no owner or restore a previous viable owner; never silently restore stale capture state. This is a focused follow-up risk/evidence gap, not the basis for claiming Q3's repaired VisionEngine constructor still leaks.

## Complete prior-finding disposition

| Finding | Independent current assessment |
|---|---|
| F1 / Q1 | **Partially repaired, not closed.** Hash/revision/UUID/fixed-code malformed values are dropped; names are host-bound. R2 and R3 remain. The broader requirement cannot be replaced by only the previously reproduced eight examples. |
| F2 / Q6 | **Original missing late-stop coverage closed at the mocked software boundary.** Permanent pending/success/error × disposal tests advance 29999/30000/30001ms, assert one coded diagnostic, no raw private print/unhandled error and unchanged replacement. `debugPrint` is restored in finally. The new confirmation await needs its own cases under R1; it is not covered by these stop tests. |
| Q2 | **Original lost-start/full-window scenario repaired; new confirmation-response scenario remains R1.** Pending native disposition, scoped companion, closed/late confirmation rejection and independent host requirement are wired. No blanket durable-owner acceptance. |
| Q3 | **Requested VisionEngine construction orchestration supported.** `VisionEngine.kt:109–137` stages pose/hand/interpreter, closes model/label streams via use, transfers only after parsing and attempts acquired releases while preserving the original/suppressed failures. `VisionInitializationTest` invokes the actual constructor with resource factory, covering acquisition/open/read/parse faults plus normal/repeat close. Default factory preserves MediaPipe options and Interpreter thread count. Synthetic nullable handles are orchestration, not real detector release/inference proof. |
| Q4 | **Requested stale-view default-disposal/callback ownership support present.** Activity passes its pipeline-lock owner object into every production view; default release routes to `cancelCapture` and ledger accounting. Stale A cannot clear/cancel B; A's own analyzer/unbind/executor cleanup is independent. `runOwned` gates provider bind/error and frame/count/error actions at the final shared boundary, not just before queuing. New tests invoke actual default teardown, actual Activity current-owner boundary and cleanup fault hooks. Camera/provider runtime remains unexecuted; R5 identifies a different acquisition risk. |
| Q5 | **Fixed producer/consumer vocabulary repaired.** Unknown native classes map to `failure`; SecurityException/FileNotFoundException and other finite codes survive shared sanitizer with consistent totals. Raw exception messages remain outside retained benchmark counters. Existing UI/logcat error prose is not equivalent to the safe benchmark/history sink and is not newly claimed sanitized. |

## Recognized-text and trust census

This review inspected the whole REPORT/TRACE/DEVICE/SETUP and assessment schemas, not only the marker examples:

| Category | Current boundary and limits |
|---|---|
| package/source/clock/origin/UI endpoint, measurement/storage/control status | Fixed native labels and host finite vocabularies; unknown values omitted/rejected. |
| storage/model error, setup errors, exclusion reasons, outcome codes, failure-counter keys | Finite shared codes; arbitrary messages/unknown class names are dropped or mapped to generic failure. Safe numbers remain. |
| run/trace/attempt-start/outcome/exclusion IDs | Exact lowercase UUID retention; no normalization into acceptance. Actual native IDs are generated; trace/window/census comparisons remain. Host syntax alone is not cryptographic producer attestation. |
| model asset and SHA | Fixed asset label; native streaming digest; host exact 64-hex format. Host does not independently attest every report model digest to installed assets; artifact hash evidence is separate. |
| setup APK, revision | Exact lowercase digest/revision formats; installed APK independently checked natively and on selected host. Revision format is not independent Git provenance. |
| setup condition/background/thermal | Fixed sets; numeric lux/distance/RAM and manual verification are retained as declared setup, not measured/attested hardware by code. |
| setup chip and setup ID | R2: broad suffix / arbitrary opaque alias; human/operator handoff does not establish semantic sanitization. |
| camera selector/lens/id | Native actual Camera2 API provenance and final view ownership are substantive; selector/lens enums, opaque ID format. Host camera ID copy remains syntax-only (R2 boundary); no actual lens/device qualification executed. |
| device model/manufacturer/hardware/fingerprint; setup fingerprint | Native Build values; reader independently selected getprop; mismatched report copies replaced with trusted values and rejection carried to sink. Legitimate names are retained, not blanket stripped. Report-side sdk/emulator numeric/bool provenance differs from the independently acquired host emulator checks. |
| build version name/code/debug flag | Native package/application info. Host name compared/replaced with dumpsys only on key presence; numeric fields remain report diagnostics. R3 covers absent/unavailable independent text. No comprehensive package attestation is claimed. |
| assessment boundary/endpoint text | Built internally by actual assessment functions, not copied from report; generic TEXT sanitizer relies on that trusted caller. Rejection reasons are internally coded and sink strips raw reader exceptions to fixed collection-read rejection. |
| selected serial / CLI model version / expected ID / condition / notes | Operator inputs are a different trust source from report payloads; notes are deliberately blanked. CLI model-version/expected-ID labels are not themselves a universal private-text sanitizer. No proof against intentional misuse of all operator inputs is inferred. |

## All 16 acceptance dispositions

“Supported” below means the named software/artifact boundary, not broad integrated acceptance. Native filenames refer to `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/`; corresponding tests are under `src/test/kotlin` unless otherwise noted.

| ID | Disposition and exact acceptance boundary |
|---|---|
| 1 | **Parent documentary adjudication open.** Frozen progress/readiness/phase-gates still describe the latest fix worker as active and 121/21/38 as pre-wave evidence. Preserve dated records; append/reconcile current 132/27/41, build recovery and this changes-required verdict. Reviewer does not edit those documents or mark acceptance. |
| 2 | **Persistence/retry layered support retained; integrated runtime open.** `MainActivity.kt:169–200`, SessionManager checked writes, `MainActivityBoundaryTest.persistenceFailureReachesEventSinkAccountsFailureAndAllowsSafeRetry`, assessment save-failure widget. No continuous real camera→UI→SQLite→export→delete/reopen execution. |
| 3 | **Pending capture timeout/reason support retained.** `practice_screen.dart:147–176,248–266` generation-specific terminal map; widget timeout/cancel/dispose and native recognized-old-timeout accounting preserve replacement. Mocked scheduling is not physical capture timing. |
| 4 | **Stale posted-event and view-owned callback software guards supported.** `MainActivity.kt:154–203`, `CameraPreviewView.kt:49–123`, Activity owner wiring and CameraViewOwnershipTest; actual provider/analyzer scheduling unexecuted; R5 early-construction gap separately disclosed. |
| 5 | **Partial / software blocker R1.** Three-second warmup, original start watchdog and permanent hung late-stop deadlines supported. New confirmation response loss/error/disposal/replacement lacks durable disposition and regressions. Full runtime lifecycle acceptance remains open. |
| 6 | **Partial / software blocker R1; minor R4.** Valid returned UUID, scoped stop/report/copy/correlated completion preserved; pending/confirmed companion added and original lost-start replay rejects. Confirmation-response uncertainty is not resolved by the companion's optimistic confirmed flag. No USB handoff executed. |
| 7 | **Ledger/censor software support retained.** Native valid started IDs, duplicate/unknown timeout handling, posted persistence failure and half-open outcomes/censoring remain. Malformed IDs cannot echo into retained traces/exclusions. Missing/failed/censored latency is not fabricated. |
| 8 | **Measured publication readback support retained; new disposition partial.** `BenchmarkMode.kt:344–376` exact immutable/latest target bytes/ID checks and final-target faults preserved. Control writes reuse readback; normal/native publication fault tests exist. R1 optimistic disposition and R4 schema gap prevent blanket control-evidence closure. Crash/power-loss durability not proven. |
| 9 | **Half-open windows/full-denominator support retained.** PipelineMetrics and native/host trace/window/census tests; exact-end exclusion, old starts, trailing zeros and late ACK/censor preservation remain. No real deadline crossing measured here. |
| 10 | **Named same-clock timing contract supported.** Analyzer entry supplied at `CameraPreviewView.kt:65`; PipelineTrace event/collection/native ACK fields and host derived checks preserved. It excludes sensor exposure and does not measure physical display paint. |
| 11 | **Requested cleanup/constructor/default owner orchestration supported; real release open.** Actual VisionEngine constructor factory tests, default stale-view/current Activity disposal and fault cleanup, SessionManager owned initialization rollback, Activity superclass attempts. No native detector release or real CameraX failure acceptance; R5 additional acquisition risk remains explicitly scoped. |
| 12 | **Plot/provenance software/artifact preservation supported.** Parent actual Python plot tests, unchanged protected figure/provenance hashes. Reviewer did not visually re-certify PNGs or regenerate plots. Diagnostic/empty/rejected data are not new measured observations. |
| 13 | **Partial / R2–R3; physical provisioning open.** Native installed-APK streaming hash before timing, wrong/missing/split identity, immutable setup snapshot/front camera change checks and documented blank provisioning workflow retained. Syntax-valid supplied labels, missing trusted metadata and dropped diagnostics require fixes/adjudication. Actual lux/distance/RAM/SoC/camera/thermal qualification not executed. |
| 14 | **Blank dense handoff artifact supported, not acquired hardware or trials.** Actual label-map/handoff tests and protected forms preserved; all-sign/condition/signer outcomes remain blank/planned. Phone availability and participant evidence cannot be inferred. |
| 15 | **NOT CLOSED — R2/R3.** Original four diagnostic leaks and malformed hash/revision/UUID/text examples repaired; trusted selected-device/package names retained. Syntax-valid opaque/private values still reach sink, and missing/unavailable package trust is inconsistent. No blanket privacy/provenance guarantee from the expanded census. |
| 16 | **History concurrency/four-fault permanent support retained.** Stable sibling lock plus serialization/partial-write/fsync/replace fault regressions preserve original bytes/temp cleanup/lock release/retry. Prior behavior is honestly coverage-only GREEN. Protected repository history remained byte-identical; no forensic durability claim. |

## Runtime and research gates — separate from the software defects

1. **IDs 2/4/5:** execute only after separate authorization, on a study-free isolated installation, the real CameraX/platform-view/native-channel/Flutter/persistence/export/delete/reopen flow including faults, old/new attempt/view/run identities and cancelled/purged delivery races. Preserve installed/default-store sentinels and bind APK/model identity. Current source/compiled instrumentation and unit/widget mocks are not that flow.
2. **ID 11:** real detector/interpreter/camera release and lifecycle failure behavior need actual isolated runtime evidence. Constructor resource factories and cleanup closures prove orchestration only; a throwing close is not proof of resource release, and repeat-close guards intentionally do not retry potentially unsafe native closes.
3. **ID 13:** actual prepared manifest readback, installed APK/fingerprint, bound front camera, measured lux/distance, verified region/SoC/RAM and contemporaneous thermal/setup evidence remain unexecuted. Correctly shaped setup and manual true flags do not establish physical qualification.
4. **Physical performance:** target-class phone availability, sustained ≥60-second analyzer FPS, named latency, thermal effects, three conditions, all signs and multiple signers remain blocked/unmeasured, not demonstrated physical failures. Emulator or host proxy results are not substitutes.
5. **Human/research:** expert linguistic/anatomical validation, model numerical gate, reused-test/signer-independent/provenance limits, learning outcomes, consent/privacy/adviser approval and participant-study authorization remain separate/open. No model reselection/retraining/deployment or historical accuracy reinterpretation occurred in this repair.

## Decision and next ownership

Preserve the substantial repaired boundaries: original lost-start disposition, immutable measurement/readback/censor contracts, constructor rollback, default per-view ownership, fixed failure vocabulary, bounded stop behavior, trusted names and numeric diagnostics. Resolve R1–R3 with genuine behavioral regressions or explicit parent specification adjudication (particularly R2's trusted-operator versus semantic-sanitization scope), fix the narrow R4 contract, and address/explicitly scope R5. Obtain fresh covering/full evidence and independent re-review of that exact changed snapshot; do not replay prior completed A–G or fabricate runtime evidence.

This reviewer changed only `benchmarking/study_evidence/20261007/controller/spec-review-2.md`. Source/docs/tests/builds were left read-only. **Software task acceptance remains changes required; no runtime, physical, human or participant acceptance is granted.**
