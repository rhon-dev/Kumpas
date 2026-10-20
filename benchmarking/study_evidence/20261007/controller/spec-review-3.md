# Independent specification review — owner-approved closure, frozen package 4

Review date: October 9, 2026. Repository: `/Users/ahronjanl.rafaelahron.0804icloudcom/Documents/Thesis/kumpas`.

## Verdicts

- **Specification: COMPLIANT at the requested bounded software-closure boundary under the revised owner policy.** No unresolved Important software defect from the union of `spec-review-2` and `quality-review-2` was identified in this frozen snapshot. Receipt commits ownership; uncertain confirmation is no longer a failed start. True unconfirmed/missing/faulted producer evidence remains non-gating. Structured metadata, diagnostic-preserving trust rejection, final posted view/subscriber checks, actual constructor rollback and runtime stream closure address the remaining union.
- **Task quality: APPROVE WITH CONCERNS / bounded software approval recommendation.** The changes are wired through production seams and have covering executed evidence, not merely detached helpers. The recommendation is not an all-16 blanket acceptance, a parent documentary adjudication, or an integrated/runtime/study approval. Parent retains final acceptance ownership.
- **All-16 overall acceptance: NOT GRANTED by this review.** ID 1 documentary reconciliation remains parent-owned; the runtime/physical/model/expert/human/participant portions identified below remain OPEN. Those are evidence boundaries, not newly demonstrated software failures.
- **Critical/Important remaining code findings:** none identified within this review scope. Non-gating coverage/provenance qualifications are recorded below rather than concealed or promoted into hardware evidence.

The owner explicitly changed the policy at `owner-approved-review-closure-brief-2.md:7–8,20–26`. The old requirement that every lost confirmation reply must demote or revoke an already producer-confirmed run is **superseded**, not an unresolved acceptance item. A valid current receipt creates an owner; confirmation uncertainty concerns producer disposition, not whether ownership exists. Neither green suites nor the fixer's self-verdict supplied this conclusion.

## Snapshot, preservation and evidence identities

Read the complete owner brief, both complete second reviews and the complete `owner_closure_2/fix-report.md`, the original closure plan, repository guidance/requirements, complete frozen diff and coupled live producer/channel/screen/view/Activity/collector contracts and regression definitions. The package includes the previous repairs, not only the latest owner wave. This is a full supplied-change-package/coupled-boundary review, not a claim to have audited every unchanged repository file or every possible hostile input.

Independent read-only verification:

| Identity | Result |
|---|---|
| HEAD | `6b8b1b6770e46bea7728a8e9ca4ae6d78e857640` |
| `review-package-4.diff` | 4,691 lines, 292,502 bytes; SHA-256 `3f931766125990d413fd88d1f24e96c91e3c747dcd9ed73f7a5252904d211a05` |
| Frozen files | 28 current byte hashes match `owner-parent-verification-1.json`; zero mismatches |
| Diff postimages | All 28 reconstructed against HEAD match live files; zero mismatches |
| New source/test files | Eight, included in the frozen package/manifest, not omitted because untracked |
| Protected originals | All 82 match both the parent's current manifest and the **original expected** hashes in `artifact-verification-1.json`; zero mismatches |
| Parent manifest | SHA-256 `35fbf36de63a55741cb888e48781834003fea4aeb76021ce716b552889a93373` |

No task commits are needed to see the repair; an empty BASE..HEAD range is not this working-tree diff. Protected model/reference/history/training/evaluation/figures/handoff bytes remain unchanged.

Actual artifact readback, not just manifest assertions:

| APK | Bytes | SHA-256 |
|---|---:|---|
| Debug | 212207146 | `0707d2f153c713055edaf50171b4c053393480f34940d380512cac0177543dff` |
| Android test | 382400 | `c276116bc3bad24383101f07191f1e71d29fa52c16fc4b3a6b38bec5b024b291` |
| ARM64 release | 66969546 | `da66697f562d56ef34ea22e70c515c537f8cff640e3dda99007e8cf3fd617266` |

All three match the current parent sizes/hashes. Both application ZIPs embed `assets/kumpas_50sign.tflite` with SHA-256 `1f4543b8fb159dbe9a662f0b37e64b096f717d7527c45b2d7778f34bc0885aeb`. Actual Flutter libraries are ARM64/ARMv7/x86_64 in debug and ARM64 only in release. Test APK has no Flutter library. These are packaged identities, not installed-device identities or proof of research model provenance.

## Recorded execution independently inspected — no reruns

- Parsed matching current JVM XML: **15 suites, 137 tests, zero failures/errors/skips**. XML includes the real constructor, actual producer emission, Handler delivery, runtime asset and full-window producer-disposition tests.
- `native-owner-parent-1.log` records actual execution of `:app:testDebugUnitTest` and `:app:compileDebugAndroidTestKotlin` under `--rerun`, successful debug/test assembly and exit 0. It records 17 executed/70 up-to-date tasks. It is not a clean rebuild; notably Android test packaging was up-to-date. Instrumentation sources compiled, but installed instrumentation was not executed.
- `flutter-owner-parent-1.log` records clean analysis and **35 passing Flutter tests**.
- `python-owner-parent-1.log` records **42 tests, OK**, including real isolated-history privacy/trust tests and history/plot/handoff regressions.
- `release-owner-parent-1.log` records the ARM64 release command and exit 0.
- The worker's earlier RED and intermediate failed GREEN/analysis runs are retained in its chronological ledger; its final section supersedes pending entries without erasing them. The earlier duplicate-generated-DEX failure/quarantine remains historical evidence; this review does not claim an uninterrupted first-pass campaign or infer an unestablished duplicate origin.

No suite/build, real ADB/device, installed/default store, participant record, plot regeneration or history operation was performed by this reviewer. Independent probes called actual Python readers, binding, assessments and sinks with synthetic objects, fully intercepted ADB and an in-memory replacement for `append_entry`; subprocess execution was prohibited inside the probe. Thus the inspected entry is the exact payload handed to persistence, **not a newly written history file**. Existing parent tests do exercise isolated real history; those are recorded evidence, not this review's reproduction. An initial mock dispatch typo failed on an unexpected synthetic getprop call before sink use; corrected mock dispatch then completed. No real ADB escaped interception.

## Union of second-review findings: independent closure assessment

Native paths below are relative to `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/`; native tests are under the corresponding `src/test/kotlin` directory.

### Spec R1 / quality R1 — receipt ownership and confirmation uncertainty: CLOSED under revised policy

`practice_screen.dart:182–240` preserves the original 30-second start watchdog. A valid current return is checked for mounted/request generation, cancels that watchdog and assigns `_benchmarkStarted` and `_benchmarkRunId` **before** awaiting confirmation (`213–220`). Pending/false/error/timeout states retain the copyable ID; only true confirmation claims running. `250–263` shows owned/complete status and Copy ID, including pending/uncertain confirmation. Completion is run-correlated at `130–134` and not erased by late reply processing. Navigation/disposal increments local generation without revoking the receipt-committed native run (`304–320`). Exceptions are consumed without mutating replacement B. An original start return after timeout/disposal remains unowned and retains scoped bounded late-stop behavior (`198–210`).

`BenchmarkMode.kt:91–99` still accepts only same-run, active, timely confirmation with successful companion publication/readback. `328,344` retains the report-side control status/gate; `collect_fps.py:540–558` independently requires exact matching authoritative companion confirmation. A sent RPC or uncertain UI does not manufacture a pass. Conversely a producer-confirmed run owned at receipt is not rejected merely because the confirmation reply was lost. `environment_protocol.md:175–206` now states this same contract.

Coverage: `practice_flow_test.dart:143–223` covers completion while pending, the separate confirmation deadline, receipt at 29,999ms of the original deadline, error/false/late-success/late-error/disposal, no retry or spurious start/stop, and replacement identity preservation. `293–328` covers copy/report/stop correlation. Native `BenchmarkModeTest.receiptCommittedProducerFullWindowPreservesConfirmedUnconfirmedAndFaultedDisposition` and the actual XML fixtures cover full 60-second measured producer states, timely confirmation, publication fault and immutable A after B. The Flutter tests mock the channel; native fixtures do not execute that Flutter future. These complementary boundaries are **not** a live cross-language confirmation-loss experiment.

### Spec R2 — aliases/chips/camera representation: CLOSED at approved structured-producer boundary

`BenchmarkMode.kt:107–193` parses the setup snapshot, rejects malformed/unknown/duplicate fields and drops invalid retained text. Supplied setup identity must match exact lowercase UUID syntax (`153,179,185–188`); malformed aliases are not normalized or replaced by an apparently legitimate native identity. Chips are exactly `Snapdragon 680` / `Helio G80`, with matching retention validation, not a broad suffix regex. The blank provisioning schema and generation/manual-verification limits are documented at `environment_protocol.md:92–139`.

Actual `CameraPreviewView.kt:116–124` obtains the bound Camera2 API ID. `BenchmarkMode.kt:196–209` represents its exact UTF-8 bytes as `camera2-sha256:<64 lowercase hex>` and checks identity/selector/lens/bind changes. Arbitrary legitimate OEM ID strings therefore do not become cleartext aliases or get silently normalized. Host `collect_fps.py:428–440` requires the same bounded representation, UUID and fixed chips. This is the owner's expressly permitted **trusted-producer structured representation**, not independent host camera enumeration or cryptographic hardware attestation (`environment_protocol.md:159–169`).

Native `invalidSetupTextNeverReachesNativePublishedReports` and host `test_recognized_metadata_privacy_through_real_history` include syntax-valid `PRIVATE_patient_text` and `Snapdragon 680PRIVATE`, not only space-containing malformed examples. Independent reader→assessment→sink probes reject these setup/chip/raw-camera inputs in FPS/camera-latency and remove both markers in all three ingestion modes, including rejected interpreter rows. Numeric diagnostics survive. Fixed chip labels and manually asserted flags still do not establish actual SoC/RAM/lux/distance/thermal qualification; a supplied UUID's syntax does not prove generator entropy. These are declared limits, not an unresolved free-form-alias policy.

### Spec R3 / quality R4 — package trust and unknown fields: CLOSED

`read_package_build` catches acquisition exceptions and rejects absent/ambiguous package name text (`collect_fps.py:531–537`). Camera reader calls it **after** reading the measured report, and appends a fixed unavailable diagnostic without discarding samples (`327–345`). Interpreter does the same (`collect_latency.py:87–95`). Binding rejects unavailable package trust independently of report field presence, requires camera build version evidence, substitutes only trusted names and checks unsupported source device keys **before** reconstructing the device (`collect_fps.py:481–528`). The raw values are omitted; collection errors carry rejection through repeated sink binding (`548–565`).

Independent probes include package throw with private exception text, empty/duplicate package output, omitted version/build and unknown nested `device.raw_video`. All remain non-gating in both camera gates while retaining analyzer count 1800 and a 100ms named trace. All three reader/sink payloads are marker-free. Interpreter remains diagnostic/non-gating and keeps its safe measurements. This is diagnostic retention plus trust rejection, not sanitization-by-dropping-the-entire-report.

### Spec R4 — exact authoritative companion including raw reader: CLOSED

`strict_json_loads:264–274` rejects duplicate/nonfinite JSON. `valid_control:540–545` requires exactly three keys, exact integer version 1 (not bool/float), exact scoped lowercase UUID and fixed status. Reader `336–345` removes invalid companion objects before returning them, using fixed errors; sink validates again. Private extras/type faults do not survive in the raw collected object simply because the eventual sink omits them.

Independent probes cover bool/float/null version, private extras, structured invalid status, missing/unreadable/malformed/duplicate companion and additional wrong-ID/unknown-status cases. All camera faults reject, with safe numeric measurements retained; invalid objects are returned as `control=None`. A synthetic confirmed companion cannot upgrade the **actual executed unconfirmed producer report**: both real host sinks still reject report-side unconfirmed status.

### Quality R2 — final posted view/subscriber boundary: CLOSED at software scheduling boundary

Production `CameraPreviewView.runOwned:35–38` scopes engine emission with the view token; `VisionEngine.kt:38–47` carries it through all `emitResult` paths. Activity removes the internal token before persistence, validates current ownership on arrival (`MainActivity.kt:154–158`), captures the subscribed sink (`188–189`), then rechecks view token and sink identity under the pipeline lock at the **final Handler delivery/event-count boundary** (`190–208`). Ordinary prediction/no-signer/warmup events no longer rely on attempt generation to identify their view. Current terminal persistence and coded failure accounting remain before posting; stale delivery suppression does not rewrite already committed measured outcomes.

`MainActivityBoundaryTest:33–65` queues A while current, publishes B without changing attempt generation after emission, holds subscription constant, drains the real Robolectric Handler and asserts no A UI event or B event count. It separately replaces the subscribed sink. `CameraViewOwnershipTest:30–53` invokes actual engine prediction emission and camera error through an actual view's ownership scope into Activity posting. Other Activity tests retain camera-error generation, persistence failure and safe retry boundaries. These are actual production seams under Robolectric, not real CameraX scheduling or a running Flutter subscriber.

### Spec R5 / quality R3 — acquisition transaction and A/B/C policy: CLOSED at constructor orchestration boundary

`CameraPreviewView.kt:47–54` stages PreviewView/executor/provider before registration. Early acquisition failure leaves viable A current. After publishing B, listener-registration failure marks B disposed and invokes all owned rollback actions (`134–152`); release invalidates only its own current token (`CameraViewOwnership.kt:15–19`). It does not restore stale A or overwrite a newer C. Cleanup failures are suppressed under the original constructor exception and do not prevent later analyzer/unbind/executor attempts. Successful replacement and repeat disposal retain per-view release ownership.

`CameraViewOwnershipTest:56–106` invokes the **actual constructor with bindCamera=true and acquisition factory**, injecting preview/executor/provider/listener faults, cleanup failures and newer-C ownership publication. Early stages assert A remains usable; late stages assert no dead-A restoration, executor shutdown, original exception/suppressed errors and C preservation. The newer C in this particular fault case is a real ownership registration, not a fully bound third physical camera view. Other actual view construction/replacement/disposal tests cover successful views. This suffices for the scoped token transaction; it must not be described as an integrated A/B/C CameraX resource-release experiment. Existing VisionEngine constructor/resource-factory rollback remains wired at `VisionEngine.kt:121–141`.

### Quality R5 — runtime assets: CLOSED

`VisionEngine.kt:86–94` reads actual lazy gold and callable labels assets through the production resource factory and `use`; parse after gold byte acquisition cannot strand its stream. `VisionInitializationTest:38–75` calls actual methods for success/read failure and short-gold parse failure, checking closure; constructor stream/native rollback and repeat-close tests remain. The labels branch labelled `parse` in this matrix does not perform a labels parse: `labelsJson()` returns raw decoded text, so that branch is another successful read, not evidence of a JSON parse fault. This is a non-gating test-label precision concern, not a surviving stream leak. No model/reference/math bytes changed.

## Independent probe results

The 60-case matrix was three modes × 20 cases: valid baseline; setup alias; chip suffix; raw camera alias; unknown device member; missing version; missing build; package throw/empty/duplicate; bool/float/null companion version; companion private extra; unconfirmed; malformed status; unreadable/missing/malformed/duplicate companion. Actual reader/assessment/sink functions were used with fully mocked acquisition and in-memory append interception.

Observed results:

- **Zero private markers** in collected reader objects or append payloads.
- **Zero safe-count/trace retention failures**: each retained analyzer_count 1800 and final_analyzer_to_event_ms 100.
- Only the valid FPS and camera-latency baselines qualified; every other camera case returned status 1/gate false. Interpreter never qualified, including its valid numeric baseline.
- Invalid companion objects did not remain exposed by the camera reader.

Separately replayed the **actual parent XML's** three `NATIVE_RECEIPT_FIXTURE` objects, rather than fabricating producer responses:

| Executed producer mode / run UUID | FPS | Camera latency | Safe diagnostics |
|---|---|---|---|
| confirmed / `e0d18310-8651-4090-8f52-e0c84092033a` | status 0, gate true | status 0, gate true | 1800 analyzers, 50ms trace |
| unconfirmed / `62fafecc-dc2a-4647-a214-cfa29749a9ed` | status 1, gate false | status 1, gate false | 1800 analyzers, 50ms trace |
| faulted / parent XML fixture | status 1, gate false | status 1, gate false | 1800 analyzers, 50ms trace; control unavailable diagnostic |

Additional missing/wrong-ID/unknown-status companion probes reject in both camera modes. The forged companion-only confirmed upgrade of the executed unconfirmed report also rejects in both modes. These results establish host consumption of executed synthetic producer output, not a continuous installed device/channel session or real camera performance.

## All 16 bounded acceptance dispositions

“Supported” means precisely the software/artifact boundary stated, not global acceptance. Parent documentary reconciliation is distinct from missing runtime evidence and from code defects.

| ID | Independent disposition, evidence and remaining boundary |
|---|---|
| 1 | **OPEN — parent documentary adjudication.** Progress/readiness/phase-gates and earlier review/adjudication records must be reconciled to the revised policy, current 137/35/42 evidence and this verdict. Historical fail/pending records are not silently deleted. Reviewer does not edit or grant this gate. |
| 2 | **Bounded persistence/retry support retained.** `MainActivity.kt:172–186`, checked SessionManager writes, production persistence-failure EventSink/accounting/retry and assessment-save-failure widget cover failure handling. Real uninterrupted camera→Flutter→SQLite→export→delete/reopen remains OPEN. |
| 3 | **Bounded pending-capture timeout/reason support retained.** Request-specific terminal map, widget timeout/cancel/dispose and native recognized-old-timeout accounting preserve replacement identity. This is mocked timing, not observed capture deadlines. |
| 4 | **Final posted view/subscriber software boundary supported.** Production token emission→Activity Handler recheck and unchanged-generation/same-sink regression close quality R2; stale default disposal remains protected. Actual provider/analyzer scheduling and real stream replacement remain OPEN. |
| 5 | **Revised control/lifecycle software contract supported.** Three-second warmup, original start watchdog, scoped bounded late stop and separate bounded confirmation remain; receipt ownership/uncertainty/completion/disposal/replacement are covered. Not an installed lifecycle acceptance; real flow OPEN. |
| 6 | **Identity/recovery software contract supported.** Valid current UUID is retained/copyable before confirmation, completion stays correlated, scoped report/stop preserved. Executed producer→actual host replay distinguishes confirmed/unconfirmed/faulted. Physical USB handoff OPEN; no lost-confirmation-demotion requirement is imposed. |
| 7 | **Ledger/censor support retained.** Started IDs, duplicate/unknown/old timeout handling, persistence-failure codes and immutable terminal/censor boundaries are supported by native/host tests. Failed/censored samples are not fabricated successful latency observations. |
| 8 | **Publication/disposition software support retained.** `BenchmarkMode.kt:347–379` verifies exact immutable/latest target bytes and run identity; partial publication stays pessimistic/non-gating. Strict companion and readback/publication faults covered. Crash/power-loss durability OPEN. |
| 9 | **Half-open windows/full denominator supported.** PipelineMetrics, native trace/outcome boundaries and host census/derived validation preserve exact-end exclusion, old starts, trailing zero/stall bins, late ACK and censors. Physical deadline observations OPEN. |
| 10 | **Named same-clock timing boundary supported.** Analyzer entry precedes conversion; native result/event/native post-frame ACK fields and host derivations remain. Not sensor exposure, first-frame end-to-end latency or physical display paint. |
| 11 | **Resource orchestration supported.** Actual engine/view acquisition rollback, default ownership cleanup, Activity superclass attempts, SessionManager owned initialization and runtime asset streams are wired/tested. Throwable cleanup still cannot prove actual resource release; detector/interpreter/CameraX runtime failures OPEN. |
| 12 | **Plot/provenance preservation supported.** Parent Python plot tests executed; original protected figure/provenance hashes match. Reviewer did not regenerate or visually recertify PNGs; diagnostic/empty/rejected rows are not new physical observations. |
| 13 | **Software setup/provisioning contract supported.** Native installed-APK digest before timing, immutable setup snapshot, front selector/lens/bind/change checks, exact UUID/fixed chips and structured Camera2 provenance agree with host/docs/blank schema. Actual lux/distance/SoC/RAM/thermal/fingerprint/APK/camera physical preparation remains OPEN. |
| 14 | **Blank dense handoff artifact supported.** Dense label/all-sign/condition form tests recorded and original forms unchanged. Templates remain blank/planned, not acquired phones, trials, signer outcomes or observations. |
| 15 | **Requested diagnostic privacy/trust closure supported.** Native published rejection strips aliases; all three host readers/sinks enforce fixed/structured metadata, preserve trusted names/safe numbers, retain fixed trust errors and reject unknown device/companion content. Not universal sanitization of arbitrary CLI/operator inputs, malicious-producer attestation or a comprehensive privacy approval. |
| 16 | **History concurrency/four-fault software coverage retained.** Existing stable sibling lock and serialization/partial-write/fsync/replace tests protect original bytes/temp cleanup/lock release/retry; recorded parent Python evidence covers these. Original repository history remains byte-identical. Not forensic or power-loss durability. |

## Open runtime/research gates and final ownership

1. **Integrated runtime (IDs 2/4/5/6/11):** a separately authorized study-free installation must exercise real CameraX/platform-view/native channel/Flutter/persistence/export/delete/reopen, old/new attempt/view/run identities and lifecycle/error races. Compiled instrumentation sources and separate mocks are not this acceptance flow. No default-store operations are authorized by this report.
2. **Physical provisioning/performance (ID 13 and performance promises):** actual target-class hardware availability, sustained ≥60-second analyzer FPS, named latency, thermal behavior, three conditions/all signs/multiple signers and contemporaneous environment/hardware verification remain unmeasured here. An unavailable phone is not a demonstrated physical failure; passing synthetic samples are not hardware results.
3. **Model/expert/human/study:** deployed model numerical/provenance gates, reused-test/signer-independent limits, anatomical/linguistic expert approval, pedagogical/learning outcomes, consent/privacy/adviser approval and participant-study authorization remain separate. Protected hashes establish preservation, not resolution of those research questions.

**Recommendation:** accept the repaired frozen snapshot at the bounded software-review boundary after parent reconciliation; do not replay the obsolete confirmation-abandonment policy or treat prior report numbering as interchangeable. Preserve the recorded intermediate failures and unchanged protected artifacts. Parent should append current evidence/policy/verdict to its documentary gates and keep all runtime/physical/human/model/study gates explicitly open.

This reviewer created only `benchmarking/study_evidence/20261007/controller/spec-review-3.md`. No source/test/protocol/readiness/progress/gate files were edited, no suite/build was rerun, and no devices/default stores/history/plots were operated on.
