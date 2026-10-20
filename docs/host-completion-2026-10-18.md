# Host completion campaign — October 18, 2026

## Decision boundary

Package D produced final host test/build evidence and this current campaign index. **Parent independent verification and whole-package specification/quality review are pending.** This is not a declaration that all16 owner tasks, PRD gates, or participant-study readiness are complete. The parent owns changes to `docs/phase-gates.md`, `benchmarking/study_readiness.md` and `.superpowers/sdd/progress.md`; this slice did not edit them.

The approved scope is `docs/superpowers/specs/2026-10-15-host-completion-design.md` and its implementation plan. The tested checkout is dirty HEAD `6b8b1b6770e46bea7728a8e9ca4ae6d78e857640`, including accepted tracked edits and new source/tests, not HEAD alone. Evidence below is under `benchmarking/study_evidence/20261015/`; `controller/` contains parent acceptance, `d/` contains this execution. Worker reports with older “in progress” or “review pending” text are historical; the later controller decisions determine accepted scope.

## Complete16-item disposition

| Host task | Implemented/executed and existing review | Current disposition and remaining dependency |
|---|---|---|
|01 Layered study flow|A3a native producer plus A3b exact-artifact Flutter/Python consumers accepted. D reran170 JVM/79 Flutter and the producer preflight.|**Bounded host accepted.** Separate native, Flutter mocked transport and Python replay are not one installed CameraX/channel/store session.|
|02 Lifecycle/races|A2a deterministic timer/cache/shared-observer ordering accepted; current full suites re-executed.|**Bounded host accepted.** Permanent reply loss may stall the shared queue; fresh-screen seeding and arbitrary direct-caller native atomicity remain unproved.|
|03 Persistence/export/purge/reopen|A1 scoped export publication, A2a cache/fault contracts and A3 native isolated SQLite/export/clear/reopen accepted.|**Bounded host accepted.** No default participant store or installed deletion flow exercised; partial filesystem/DB/preferences operations are not an all-or-nothing global transaction or forensic erasure.|
|04 Initialization/resources|A2b host initialization/rollback/subscriber coverage accepted, with retained registry/messenger concerns.|**Bounded host accepted.** Inert registrations across differing messengers, same registry-ID retry, actual FlutterEngine startup/removal and hardware resource release are not proved.|
|05 Producer/collector contracts|A3b exact accepted producer artifacts through actual reader/history paths with mocked transport accepted.|**Bounded host accepted.** Synthetic trust inputs are not independent hardware attestation; interpreter newline adaptation is diagnostic.|
|06 FIVE/THREE parity preparation|B1 six validation fixtures/180 PNGs/real Python Holistic references accepted. D re-read generated artifact hashes only;21 compatible synthetic parity/campaign tests passed.|**Bounded host accepted.** No new Android-produced parity, anatomical labels or classifier acceptance. Sampled-frame and full-video tracking are distinct.|
|07 APK inspector|C1 reusable inspector accepted; its low coverage follow-up closed. D built and independently inspected fresh debug/test/release APKs.|**Tool accepted; fresh evidence pending whole-package review.** ARM64 Flutter release contains dependency libraries in three ABI namespaces; strict ARM64-only probe correctly rejects. No ABI-policy approval, signature, ELF or runtime claim.|
|08 Validation error diagnostics|B2 retained actual150 validation records/model,144 correct each; D hash-checked historical outputs/counts without inference.|**Real diagnostics retained, bounded acceptance only.** Not final-test/generalization evidence or a causal/anatomical explanation;134 source metadata records unavailable.|
|09 Bounded experiments|Existing split/selector retained. No actual retraining; no isolated bounded experiment runner implemented.|**BLOCKED / NOT COMPLETE.** Separate local-versus-Colab approval, frozen experiment parameters/budget and isolated runner implementation/review required. Do not run the existing protected-log-writing trainer.|
|10 Full evaluation/export provenance|B2 additive validation tooling accepted after review fixes. Historical v3 incomplete manifest, config and all13 source-code roles retained and hash-checked.|**Tool accepted; full-source deliverable BLOCKED.**134 NPZ/video pairs were DATALESS in the recorded run; no successful full-source manifest. Historical checkpoint-to-shipped-byte chain and numerical promotion policy remain open.|
|11 Assessment/rubric tooling|A1 form/export contracts and C2 explicit-file legacy export validation accepted;18 evaluation tests passed in D.|**Export validation accepted; human rubric scoring BLOCKED.** Instrument/sign list, rater/blinding/adjudication, missingness, group join, consent and retention approvals absent.|
|12 Analysis utilities|C2 synthetic descriptive pipeline accepted; D reran its current suite. C2 low coverage follow-up closed.|**Synthetic descriptives accepted; human/inferential analysis BLOCKED.** Likert/SUS-labelled responses, classifier confidence, mastery and XP are not human-rated learning scores.|
|13 Current status index|This document reconciles all16 against controller decisions, current hashes and executed D evidence.|**Prepared, parent review pending.** Parent alone may amend governed status files or grant host-completion acceptance.|
|14 Reproducible handoff|`docs/host-reproducible-handoff.md` links exact commands, immutable bindings, historical-safe readback and unchanged blank forms.|**Prepared, parent review pending.** No phone acquired, hardware/trial values filled, or physical execution authorized.|
|15 Architecture decisions|`docs/decisions/2026-10-18-host-scope-deviations.md` records proposed scoped deviations and alternatives.|**Proposed / approval pending.** No invented PM/adviser/expert decision; no stack/model/cloud change authorized.|
|16 Final host verification|D executed current full suites, forced JVM/instrumentation compile, offline fresh APK builds, ZIP/assets/ABI inspection and preservation review package.|**Executed host evidence; parent verification and whole-package review pending.** Not installed startup, physical benchmarks, unseen/signer-independent evaluation or study authorization.|

Machine-readable equivalent: `d/dispositions.json`. There are exactly16 numbered dispositions; conditional tasks are not counted as complete.

## Controlling acceptance records

Use `controller/a1-acceptance-20261016.json`, `a2a-acceptance-20261016.json`, `a2b-acceptance-20261016.json`, `a3a-acceptance-and-consumer-binding.json`, `a3b-acceptance-20261017.json`, `b1-acceptance-20261017.json`, `b2-bounded-acceptance-20261018.json`, `c1-bounded-acceptance-20261018.json`, `c2-bounded-acceptance-20261018.json` and `followups-acceptance-20261018.json`. The final follow-up closes B1-R1/C1-Q1/C2-L1; they are not still-open repairs. A1 borrowed-handle concern was covered in accepted A2a. A2a/A2b retained limits above are not silently erased.

The authoritative A3a consumer run is `323291af-c067-46dc-bae1-067d62fab10b`, manifest SHA256 `3279cb7d01075a9192f2566ae5573dd6137a23c6710ef1d0a590b78564fe0fed`. D preflight verified42 source bindings,11 artifacts and the accepted producer evidence. Do not substitute another equal-source run.

## Fresh execution, not cached test counts

| Check | Actual result | D evidence |
|---|---|---|
|Flutter analyze --no-pub|Exit0, no issues|`flutter-analyze.log`|
|Flutter full --no-pub --machine|79 nonhidden completed tests,0 failures/skips; final success event|`flutter-full.log`, parsed result JSON|
|JVM forced execution|170 tests in17 XML suites,0 failures/errors/skips|`jvm-full.log`, `jvm-full-xml/`, result JSON|
|Instrumentation Kotlin|Exact `:app:compileDebugAndroidTestKotlin` execution, not UP-TO-DATE|Same JVM command, task-scoped --rerun for each target|
|Broad benchmarking|124 discovered,122 passed and2 explicit Holistic capability skips|`benchmark-full.log`|
|Compatible parity/campaign|21 passed,0 skips, including both skipped detector cases on synthetic media|`holistic-compatible.log`; overlaps broad suite, not21 additional unique tests|
|Evaluation|18 passed,0 skips|`evaluation-full.log`|
|Training|29 passed,0 skips; existing isolated synthetic save/conversion only|`training-full.log`|

All test/build commands captured the same pre-documentation source manifest SHA256 `0223e7b1ef0e85e82afdd891993c5f05c3bfb932141e3c80213d1a0f5cb2b989`, containing261 tracked/untracked reviewable source/config/document files. No application/benchmark/training/evaluation source changed during or after execution. The final freeze adds only the three named documentation files and separately binds D evidence helpers/report; it does not pretend tests ran against later edited production code.

## Fresh artifacts and packaging boundary

| Artifact | Bytes | SHA256 | Producing successful invocation |
|---|---:|---|---|
|Debug APK|197412392|`f45353b6f7711ab21bb222b5171e678de0f46902e5bf1714cbe2ad55f596ff95`|`debug-test-build-fresh3`|
|Instrumentation/test APK|374427|`f6a80996b8e18188b3cb02fe429e313891d4fc97e4d7e035a4a5ae949c9b506e`|`debug-test-build-fresh3`|
|ARM64-targeted release APK|66969546|`ad59b02daeae01f2fa71e4ca09fbc93985e63aef702025c91f85cc56b462ba27`|`release-build-retry4`; prior same-source release compile/minification chain retained|

The debug/test command actually reran Flutter compilation, application Kotlin, instrumentation Kotlin and both packaging tasks. The release uses direct Gradle `--offline -Ptarget-platform=android-arm64` rather than a Flutter front end that does not forward an offline flag; exact arguments/logs are preserved. Retry4 executed assets/compression/package/assembly; full release compilation/minification occurred in the retained same-source retry2/retry3 chain. Earlier debug/test invocations merely observed release bytes; they are **not** release producers. Earlier release invocations merely observed debug/test bytes; they are **not** their producers.

Independent ZIP CRC and five protected asset digests match in both app APKs. The test APK has no native libraries/models expected. Debug has15 native paths and Flutter libraries in arm64-v8a/armeabi-v7a/x86_64. Release has13 native paths across those three ABI namespaces, but libapp.so and libflutter.so only in arm64-v8a. The accepted inspector passed current debug and historical-three-ABI-consistency release expectations; an explicit strict ARM64-only release expectation returned1 as expected. This is a packaging observation, not an approved ABI requirement or automatic configuration defect. The inspector alone deliberately reports `current_source_build_provenance=false`; `d/artifact-readback.json` independently composes actual build command/result/log/source binding. No signature, ELF compatibility, installation, startup or runtime verifier ran.

## Preservation and execution incidents

Six pre-build APK paths were copied and hash-verified into the external scratch snapshot before any build; exact paths/hashes are in `d/historical-apk-preservation.json`. Fresh and unsuccessful intermediate APK snapshots are also external. All82 protected originals matched before/after. The final review package covers dirty tracked changes **and complete new source/test files**, not an empty BASE..HEAD diff. No commit/reset/clean/stash, dependency install, deliberate raw-dataset hydration or participant-store operation occurred.

Retained failed release logs identify exact generated DATALESS suffix files (`CupertinoIcons 2.ttf`, `app 2.so`, `classes 2.dex`). Only those implicated outputs were moved; no broad clean. The first TTF preservation script asserted unchanged flags after the move and failed; recovery records the observed flag transition and now-readable hash, not a fictional preimage digest. Moving the SO outside its provider timed out; a same-provider, same-volume move preserved inode/device/size/flags. DATALESS SO/DEX hashes remain null with that limitation explicit. These files stay quarantined, not deleted or silently replaced.

The first forced debug build tool call timed out after420s without a completion result; it is not counted successful. Later managed retries produced real exits. Fresh2 debug and the first fresh release packaged suffixed generated asset entries that the accepted inspector correctly rejected. Their APKs/logs remain preserved. Only the exact two duplicate debug snapshots and release NativeAssetsManifest suffix were quarantined after comparing canonical hashes; rebuilt artifacts passed inspection. Filesystem duplication origin is unknown. SDK/Kotlin/Gradle deprecation warnings are retained, not converted into source defects. These recovery details and exact manifests are in `d/report.md` and the append-only command ledger.

## What remains outside host completion

Physical-device acquisition/provisioning and three-condition FPS/latency/thermal/signers/all-sign evidence; uninterrupted installed CameraX/channel/UI/SQLite/export/delete/reopen; anatomical and expert validation; failed selected-model final numeric gate, untouched/signer-independent evaluation and historical shipped-model provenance; retraining approval/runner;134 full-source metadata pairs; approved human instrument/rater/missingness/statistical plan; consent/participant authorization. Missing observations stay missing. Parent whole-package review must precede a host-completion decision; no physical or study gate closes automatically.
