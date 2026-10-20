# Independent quality/security/correctness review — frozen package 4

Review date: October 9, 2026. Repository: `/Users/ahronjanl.rafaelahron.0804icloudcom/Documents/Thesis/kumpas`. Base/current HEAD: `6b8b1b6770e46bea7728a8e9ca4ae6d78e857640`.

## Verdict

- **Code quality/security/correctness: APPROVE WITH ONE MINOR FOLLOW-UP at the reviewed software boundary.** No Critical or Important unresolved finding identified in the complete frozen package and examined adjacent paths. R1 below is a narrow malformed-report schema-type acceptance gap; it does not reopen receipt ownership, exact companion validation, privacy retention, constructor rollback or posted view ownership.
- **Owner-approved specification: COMPLIANT for the second-review union closures.** This verdict applies the owner's receipt-commit and strict structured-metadata decisions in `owner-approved-review-closure-brief-2.md`, not the superseded requirement that an uncertain confirmation reply disqualifies ownership. The broader strict schema-v2 report contract has the minor deviation R1; this is not an unqualified assertion of every possible schema/input property.
- **Whole campaign/study acceptance: NOT GRANTED.** Parent documentary adjudication remains open. Installed CameraX/native/Flutter/persistence/export/delete integration, physical setup/performance, actual native release, model/expert/human gates and participant authorization remain separately unverified.
- Findings: **Critical: none. Important: none. Minor: R1.** Evidence limitations below are not presented as observed software failures or silently converted into study approval.

## Scope, integrity and evidence method

Read the complete owner-approved closure brief, both complete second-review reports, the closure ledger `owner_closure_2/fix-report.md`, original closure plan, the complete **4,691-line** frozen `controller/review-package-4.diff`, and the coupled production/test paths. Scope includes the earlier repairs present in that package, not only the newest edits. Traced native producer/control/publication/window/census paths, camera-view construction and final Handler delivery, Dart ownership/watchdogs/completion/disposal, FPS/camera-latency/interpreter readers and sinks, and supporting database/resource/history contracts. A commit-range shortcut would miss these uncommitted changes and was not used.

Independent checks:

- Frozen diff: **292,502 bytes**, SHA-256 `3f931766125990d413fd88d1f24e96c91e3c747dcd9ed73f7a5252904d211a05`.
- Reconstructed all **28** frozen diff postimages against HEAD and compared them to live files: **zero mismatches**.
- Rehashed the parent's **28 reviewed file identities** and **82 protected identities**: zero mismatches, including a final check before report creation. Also compared every original expected protected hash in `controller/artifact-verification-1.json`, not merely a new manifest: **82 checked, zero mismatches**. The original map stores expected/actual objects; its raw JSON shape differs from the parent's hash-only map, but its original expected hashes match the files.
- `git diff --check`: exit 0. HEAD unchanged.
- Independently parsed current JVM XML: **15 suites, 137 tests, 0 failures, 0 errors, 0 skips**. Read the actual parent logs: forced unit-test execution, forced instrumentation-source Kotlin compilation and successful debug/test APK assembly; Flutter analysis **No issues found**, **35 passing Flutter tests**; **42 Python tests, OK**; successful ARM64 release build. The inspected native/Flutter/Python/release logs contain no matched compiler warning/error, failed-test or traceback diagnostics. Prerequisite tasks can be UP-TO-DATE; this is not a clean rebuild or installed instrumentation run.

Actual artifacts independently rehashed and ZIP-tested:

| Artifact | Bytes | SHA-256 | ZIP/ABI/model check |
|---|---:|---|---|
| Debug APK | 212207146 | `0707d2f153c713055edaf50171b4c053393480f34940d380512cac0177543dff` | ZIP integrity passes; Flutter arm64-v8a/armeabi-v7a/x86_64; protected model matches |
| Android test APK | 382400 | `c276116bc3bad24383101f07191f1e71d29fa52c16fc4b3a6b38bec5b024b291` | ZIP integrity passes; no Flutter library/model expected |
| ARM64 release APK | 66969546 | `da66697f562d56ef34ea22e70c515c537f8cff640e3dda99007e8cf3fd617266` | ZIP integrity passes; Flutter arm64-v8a only; protected model matches |

Both application APKs contain `assets/kumpas_50sign.tflite` with SHA-256 `1f4543b8fb159dbe9a662f0b37e64b096f717d7527c45b2d7778f34bc0885aeb`. All artifact hashes match `owner-parent-verification-1.json`. This verifies supplied artifact identities/integrity, not a reproducibility or real-device performance claim. Earlier duplicate-generated-DEX failures/quarantine evidence remain historical records, not erased by successful current output.

**No suite/build reruns, real ADB, devices, installed/default participant stores, repository histories or plots were exercised.** Independent Python `-B` probes executed actual collector reader/binder/sanitizer/assessment/sink functions with entirely mocked ADB and list-intercepted `append_entry`; no history file was written. Additional producer replay used the parent's actual executed JVM XML output, not worker fixture copies or invented responses. The only repository write by this reviewer is this report.

## Independent actual-function probes

**45 reader-to-sink cases passed their assertions**, covering FPS, camera latency and interpreter diagnostic readers. Each mode covered valid baseline; package acquisition exception, absent package version and ambiguous duplicate package versions; missing report version; unsupported nested `device.raw_video`; syntax-valid setup/camera aliases `PRIVATE_patient_text`; chip suffix `Snapdragon 680PRIVATE`; and companion extra/bool/float/missing/duplicate/unconfirmed variants. Companion variants exercise the camera readers; the interpreter reader has no companion contract and remains diagnostic regardless.

Across these cases, raw returned collection objects and sink entries omitted both private markers; retained `analyzer_count=1800`, the 100ms trace diagnostic and independently selected `model="test phone"`. Only the valid FPS and camera-latency baselines qualified. Package/alias/unknown-field faults retained safe measurements and failed closed. Interpreter rows never passed a camera gate. This is execution of production host functions with synthetic inputs, not execution of instrumentation or physical camera measurements.

Extracted **three `NATIVE_RECEIPT_FIXTURE` objects** from the parent's `TEST-com.kumpas.kumpas_app.BenchmarkModeTest.xml` system-out. Replayed their actual confirmed/unconfirmed/faulted report/companion output through both production host assessments and sinks (**six replay cases**): confirmed returned status 0/gate true; unconfirmed and faulted returned status 1/gate false; all retained 1800 analyzer observations. The producer fixture's full-window result is an executed synthetic producer contract, not a physical observation. Separate Flutter channel mocks establish UI scheduling behavior; the replay does not turn them into one live cross-language session.

The additional schema probe supporting R1 is documented below. These probes supplement, rather than merely repeat, the worker's assertions.

## Second-review union closure adjudication

### Receipt ownership — quality-review-2 R1 / spec-review-2 R1

**Closed under the explicit revised owner policy.** `practice_screen.dart:182–240` cancels the original start watchdog, stores `_benchmarkStarted` and the valid current `_benchmarkRunId`, and shows a copyable pending identity **before** awaiting the separate bounded confirmation. False yields owned/unconfirmed diagnostic status; thrown/timed-out confirmation yields owned/uncertain status, not failed start/Retry. Only a true reply claims confirmed/running. Matching completion remains correlated while confirmation is pending and cannot be erased by a subsequent reply; mounted/generation/ID checks isolate a replacement. Disposal after receipt follows the stated owned-run navigation policy, consumes late errors, and does not issue the unowned late-start stop. An original response arriving after timeout/disposal still takes identity-scoped bounded cleanup.

Native `BenchmarkMode.kt:70–99,328,344` retains default unconfirmed/readback-verified disposition and accepts confirmation only for the same active run before its native deadline. Host `collect_fps.py:35–36,540–558` requires both confirmed report and exact independently read companion. UI ownership and sent RPCs alone do not qualify anything. A native-confirmed run whose confirmation **reply** is lost is not disqualified solely for that loss, exactly as the owner decided. Requiring a third acknowledgement/lease would reintroduce an obsolete policy, not identify a current defect.

Coverage inspected: near-original-deadline receipt (29999ms), pending/error/false/late success/late error/disposal, exact separate timeout/completion/replacement cases in `practice_flow_test.dart`; fresh XML producer confirmed/unconfirmed/publication-faulted full-window fixtures; independent host replay above. No live lost-RPC experiment claimed.

### Strict metadata — spec-review-2 R2

**Closed at the approved structured/trusted-producer boundary.** Native `BenchmarkMode.kt:107–193` validates and strips setup text before retention: exact lowercase UUID setup identity, exact chip vocabulary **Snapdragon 680 / Helio G80**, fixed labels/digests/revision, and actual Build fingerprint comparison. Numeric diagnostics remain. Host `collect_fps.py:427–440,481–528` applies the same structured representations while replacing report device/build names only with independently selected trusted values.

Production `CameraPreviewView.kt:116–124` supplies the actual bound `Camera2CameraInfo.cameraId`; `BenchmarkMode.kt:196–209` retains SHA-256 of its exact UTF-8 bytes as `camera2-sha256:<64 lowercase hex>`, with selector/lens/bound/change tracking. Arbitrary legitimate OEM IDs are represented, not blanket-censored or normalized. Cleartext setup/camera aliases and chip suffixes are rejected, including diagnostic rows. The host verifies structured shape and trusts the approved producer path; it does **not** independently attest Camera2 hardware. Neither UUID shape nor a digest proves an honest/malicious operator's entropy or hardware provenance. Those explicit limits are consistent with the owner's permitted alternative, not hidden exceptions.

Native immutable/latest invalid-setup assertions and executed producer fixture definitions were inspected; host adversarial actual-function probes independently retained legitimate trusted names/numerics while omitting the private values. README and environment protocol agree on schema, provisioning, fixed chip provenance/manual checks and the camera trust limit.

### Acquisition, unknown-device rejection and exact companion — spec-review-2 R3/R4 / quality-review-2 R4

**Closed.** `collect_fps.py:327–345,481–545` and `collect_latency.py:87–95` catch package acquisition/parse failure inside the reader, preserve already-read sanitized measurements and safe selected identity, and append fixed unavailable diagnostics. Absent/ambiguous package text cannot bypass qualification by omitting report version text; repeated sink binding also rejects unavailable/mismatched trust. Unsupported source device keys are detected **before** rebuilding trusted names. The raw values disappear while the reader's fixed error survives to sink rejection.

`valid_control` requires exactly three keys, integer schema 1 excluding bool/float, exact scoped lowercase UUID and finite status. Reader invalidation happens before returning the collection object, and sink validation repeats it; private extra/duplicate/malformed objects cannot be raw-reader leaks or qualifying companions. Independent probes exercised both layers. This closure does not imply every report numeric field has equally strict typing; R1 names the separate main-report gap.

### Final posted delivery — quality-review-2 R2

**Closed for the production software boundaries examined.** `CameraPreviewView.kt:36–38` scopes production provider/analyzer/error work with the view owner; `VisionEngine.kt:38–47` tags every corresponding emission and restores nested scope in finally. `MainActivity.kt:154–209` removes the internal tag before persistence/retention, checks current view at arrival and again under `pipelineLock` at final Handler delivery, captures the intended sink and verifies sink identity immediately before event counting/delivery. Replacement view identity is independent of attempt generation.

Persistence and fixed terminal failure accounting still happen before posting; stale UI suppression does not erase previously committed SQLite records. Success dispatch timing remains tied to actual permitted delivery; undelivered unfinished work remains censorable rather than fabricated successful latency. Existing cancellation/persistence-failure ledgers and pending trace guards remain.

Coverage inspected in fresh XML and definitions: actual VisionEngine emission/reportCameraError through actual view `runOwned` into Activity Handler; prediction/no-signer/warmup/error queued while A owns, B registered before drain with unchanged attempt generation and unchanged sink, no A delivery/no event count; separate subscriber replacement; persistence-failure/retry accounting. Real analyzer/provider scheduling and uninterrupted app integration remain unexecuted.

### Construction/cleanup — quality-review-2 R3/R5 / spec-review-2 R5

**Closed for staged acquisition and ownership orchestration.** `CameraPreviewView.kt:47–56,134–156` stages PreviewView/executor/provider acquisition before publishing B. Early failure leaves viable A untouched and releases acquired executor. Later listener-registration failure marks B disposed and attempts current-token release, own clear/unbind and executor shutdown; original exception is rethrown with cleanup failures suppressed. Token release never restores stale A or overwrites newer C. Disposal is repeat guarded and stale views still release their own resources without cancelling the replacement.

`CameraViewOwnershipTest.actualViewConstructionRollsBackAcquisitionsAndOnlyItsPublishedOwner` invokes the actual constructor with `bindCamera=true` and preview/executor/provider/listener/newer-C fault factories; it asserts A/B/C behavior, original/suppressed exceptions and executor shutdown. Own clear/unbind fault hooks exercise cleanup continuation, but are not real bound CameraX use-case release measurements. Provider acquisition/listener tests must not be represented as physical provider execution.

Earlier `VisionEngine.kt:121–141` staged pose/hand/model/interpreter/label construction still rolls back every acquired resource; `SessionManager.kt:52–61,237–246` closes owned database helpers on initialization/terminal-close failure; Activity `onDestroy` attempts later owners and superclass teardown despite earlier faults. Runtime `VisionEngine.kt:86–94` now closes actual gold/labels streams through the resource factory using `use` before parsing. Runtime success/read/short-gold parse faults cover the production methods, not only constructor-bypassed close helpers. Real MediaPipe/Interpreter release remains unverified.

## Minor finding R1 — main report schema accepts floating-point 2.0

**Locations:** `benchmarking/collect_fps.py:121–125` (ordinary equality in schema validation), `381–383` (schema_version shares NUMBER retention), `548–578` (actual sink); `collect_latency.py:36–38` shares validation. This is a retained supporting schema gap, not the repaired authoritative-companion bug.

**Exact scenario:** An otherwise valid schema-v2 report contains JSON `"schema_version":2.0`, with valid run/setup/device/build/measurements and exact integer-schema confirmed companion. Python equality treats `2.0 == 2`; NUMBER sanitizer preserves the float. An independently executed actual validator→sink probe returned **status 0, retained schema 2.0, gate true**. Native produces integer 2. The malformed report is therefore accepted despite an integer version contract. No confirmed/unconfirmed bypass, measurement change, private-value retention or device compromise was demonstrated.

**Severity:** Minor / non-blocking follow-up. Scope is type strictness for an otherwise identical supported version; all qualification and scoped companion requirements still apply. Do not claim that this result makes an unconfirmed run qualify or that it demonstrates forged physical evidence.

**Coverage gap:** Existing malformed-field and exact-companion tests do not reject floating-point main report version 2.0. Fresh suites pass despite this independent counterexample.

**Fix guidance:** Check `type(report.get('schema_version')) is int` and exact value 2 before qualification, separately from general NUMBER fields. Add actual reader→assessment→sink regressions for float 2.0 and null/string/bool/wrong integer, covering FPS and camera latency while retaining safe numeric diagnostics and valid integer baselines. Interpreter diagnostic input has its own schema history and must remain non-gating; do not force it into a fabricated camera schema. No source fix was made by this reviewer.

## All-16 disposition and adjacent invariants

“Supported” means reviewed source plus the stated synthetic/artifact evidence, not a continuous installed or participant flow.

| ID | Independent disposition |
|---|---|
| 1 | Parent documentary reconciliation remains OPEN. Frozen progress/readiness/gate records still include earlier review verdicts and dated evidence; parent must append current adjudication, not erase history. |
| 2 | Persistence/retry, checked writes and assessment form retention supported by actual production-boundary tests; continuous camera→Flutter→SQLite→export→delete/reopen remains OPEN. |
| 3 | Pending attempt timeout/cancel/dispose terminal reason and generation-specific late identity handling supported; no physical capture timing claim. |
| 4 | Final view token plus subscriber identity enforced through posted delivery/counting; installed provider/analyzer race acceptance OPEN. |
| 5 | Warmup, original start watchdog, hung late-stop and separate bounded confirmation supported under receipt commit; full installed lifecycle OPEN. |
| 6 | Valid copyable receipt UUID and correlated completion retained during uncertainty; original unowned late-start cleanup remains scoped; USB handoff OPEN. |
| 7 | Started-ID ledger, malformed/duplicate/unknown handling, failure/cancel/timeout/censor denominator preserved; no successful-only latency substitution. |
| 8 | Exact immutable/latest target byte/ID readback and control disposition publication faults remain conservative; power-loss/crash durability OPEN. |
| 9 | Half-open windows, full-window rates/trailing stalls, old starts, censoring and late ACK exclusions preserved; no new physical deadline observations. |
| 10 | Analyzer entry/native result/event dispatch/native post-frame ACK meanings preserved; not sensor exposure or physical display timing. |
| 11 | Actual engine/view constructor orchestration, current-owner rollback, own-resource cleanup, SQLite ownership and runtime streams supported; real native release OPEN. |
| 12 | Protected history/figures/provenance hashes preserved and parent plot tests pass; no reviewer regeneration or new visual/measurement certification. |
| 13 | Immutable start-time setup, installed-APK binding, structured metadata and front-camera/change checks supported; actual lux/distance/SoC/RAM/thermal/provisioning OPEN. |
| 14 | Dense blank handoff/software generator coverage and protected bytes preserved; forms are not trials, acquired phones or signer outcomes. |
| 15 | Native/host recognized-text privacy, unknown-source rejection, package trust and raw companion/sink contracts repaired; no universal privacy/producer/operator attestation claim. Minor R1 is separately scoped. |
| 16 | Interprocess history serialization and serialization/partial-write/fsync/replace/lock/retry regressions preserved in fresh parent Python evidence; repository history untouched. |

Finite failure-code vocabulary and totals remain aligned across producer/consumer, including SecurityException/FileNotFoundException with generic fallback. Publication failure never gains a successful reportPath/gate from AtomicFile's return alone. Scoped cancellation/clear/pause prevent old attempt deliveries; a view replacement does not rely on those generations to suppress stale ordinary events. Model/reference normalization and feedback mathematics, XP/layout and protected training/evaluation/history/handoff artifacts were not altered by this review.

## Final boundary

The previous Important second-review union is resolved under the owner's actual revised contracts; R1 is the only residual code finding identified here and is an explicit minor follow-up. Parent may use this as bounded software-quality approval with that finding visible, alongside the separate specification review and its documentary reconciliation. Do not infer installed runtime, CameraX release, physical FPS/latency/thermal, hardware acquisition, expert/anatomical validation, model selection/provenance, learning outcomes, consent/privacy approval or participant-study authorization from green suites, replay or APK identities.

This report grants no commit, deployment, source modification or device/store operation authorization. Report path: `benchmarking/study_evidence/20261007/controller/quality-review-3.md`.
