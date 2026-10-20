# Independent final host specification review — A–D

Date: October 18, 2026. Reviewer: independent QA/specification reviewer.

## Verdicts

- **Whole approved host-completion specification: REQUEST CHANGES.** One Important completeness finding, **SPEC-R1**, remains: preparing isolated bounded-experiment tooling was approved separately from executing training, but that tooling has not been implemented. An honest BLOCKED disposition does not by itself waive an approved, independently executable preparation requirement.
- **Package D evidence integrity, preservation and truthfulness: PASS at the explicitly bounded host-evidence scope.** Current files, snapshots, logs, counts and APK bytes support the stated host results. D correctly does not claim all16 complete, integrated runtime, physical performance or study approval. This PASS is not acceptance of missing host09 tooling or source-complete host10 provenance.
- **Research validity / installed / physical / participant readiness: NOT ESTABLISHED; gates remain open.** These are not measured failures created by this review. No PM/adviser/expert approval is supplied by a software review.

This is the final specification review, not a substitute for the separate whole-package quality verdict or the parent's independent verification/acceptance. Existing bounded acceptances remain valid at their recorded limits; they are not silently widened here.

## Scope and reviewed identity

Repository: `/Users/ahronjanl.rafaelahron.0804icloudcom/Documents/Thesis/kumpas`.

HEAD: `6b8b1b6770e46bea7728a8e9ca4ae6d78e857640`, **plus dirty tracked changes and complete new files**. No task commits exist; a BASE..HEAD-only review would miss this work.

Authoritative package: `benchmarking/study_evidence/20261015/d/review-package.json`, with **29 tracked modified postimages + 41 complete new files = 70 review postimages**. The full contents of these changed/new source, test, configuration and documentation files were read, not just patch headers or prior verdicts. The tracked diff was also inspected. Its SHA256 is `3d571a65b6b68d4be012441479453c5b0adc150ef5316f74c032f5ac47e188fd`.

Whole source/document/helper freeze: **279 files**, `d/source-freeze.json` SHA256:

`2d226fe2e3387c1ca16386dd992b0e2d1f8da9e02874eced94c3629cf32b6383`

All279 current hashes match; all70 package postimages and their saved full-file snapshots match. All206 entries of `d/evidence-freeze.json` match. All82 protected originals match their expected baseline digests. The freeze is an integrity inventory, not a claim that every unchanged repository file or every binary was read as source.

Requirements read in full: `AGENTS.md`, `docs/PRD.md`, `docs/phase-gates.md`, approved October15 host design and plan, discovery app/model/tooling audits, `.kiro/specs/21-session-logging/tasks.md` including its unchecked integration task16, and the evaluation-study design/requirements. Read the D report, task brief, verification summary, all16 dispositions, three new handoff/status/decision documents, command/result/source records, relevant failure/quarantine/preservation records and all13 D Python helpers. Read the A1/A2a/A2b/A3a/A3b/B1/B2/C1/C2/follow-up acceptance records and supporting review reports; their limitations were checked against current source rather than blindly adopted.

Source coverage included production native acquisition/ownership/control, export publication, lifecycle/session persistence, VisionEngine/camera/Activity wiring; Dart channel/repository/lifecycle/practice/assessment paths and their regression fixtures; native-to-Dart/Python artifact producers/consumers; collectors/history, parity fixture generation/comparison, validation campaign tooling, APK inspector, and explicit-file evaluation/descriptive utilities with all changed/new tests. `evaluation/__init__.py` and changed status/governance documents were included.

Only this report was written by the reviewer. No build/install, device/emulator/ADB/default-store operation, raw-cloud-source read/hydration, inference/retraining/real conversion, commit/reset/stash/worktree, model/reference/math/XP/layout edit or broad cleanup was performed. Focused tests used existing Python, `-B -E`, and session scratch TMPDIR.

## Blocking finding

### SPEC-R1 — Important: approved host09 preparation is missing, independently of training authorization

**Requirement:** `docs/superpowers/specs/2026-10-15-host-completion-design.md:31–35` explicitly requires preparing isolated campaign execution and validation-only selection tooling **first**, then reserves actual retraining to a separate approval gate. `docs/superpowers/plans/2026-10-15-host-completion.md:81–93`, especially line91, repeats: “Prepare isolated bounded experiment tooling without running retraining.”

**Observed:** `docs/host-completion-2026-10-18.md:21`, `d/dispositions.json` host09, `d/report.md:53`, and decision D-02 explicitly acknowledge that no isolated bounded-experiment runner was implemented. The reviewed package contains no replacement runner. `training/models/validation_campaign.py:1–2` is validation-only diagnostics and explicitly never trains or ranks; it is not the missing execution/isolation tool. The existing default trainer remains unsuitable because of protected historical log/output behavior. Thus this is a directly documented omitted deliverable, not a speculative runtime bug or failed numerical experiment.

**Why blocking:** The approved scope already separated preparation from execution. Unresolved local-versus-Colab authorization and an unapproved concrete training budget justify not running experiments; they do not automatically defer all runner preparation. Current documentation is honest, but treating both as one approval block would reduce the approved host scope without a recorded scope amendment.

**Reproduction / audit steps (read-only):** compare design §C and plan Package B's tooling bullet with host09's disposition; inspect the complete new-file/postimage inventory and the validation campaign module's public purpose. No training or raw-data probe is required to reproduce the omission.

**Required resolution:** either (a) implement and independently test/review the isolated preparation layer, with training execution still disabled absent explicit authorization, or (b) obtain an explicit owner-approved scope deferral distinguishing missing tooling from prohibited execution. Do not silently amend the frozen design or call the runner complete. A proposed D-02 record with blank approvals is not such a waiver.

For option (a), use synthetic/fake execution only to verify exclusive output/log isolation, protected-output refusal, explicit configuration/selection binding, sequential bounded execution and timeout/failure handling. Keep concrete variant/budget values proposed until separately approved; do not use this finding as authorization for training, conversion, numerical promotion or new test-set consultation. Re-freeze changed files and rerun affected reviews after an authorized repair.

## Requirements matrix — all16 dispositions

“PASS bounded” below means compliance with the stated host deliverable and its evidence boundary, not PRD phase closure.

| Host | Requirement / inspected implementation | Independent specification disposition |
|---|---|---|
|01|Layered native event/control/SQLite/export/purge/reopen producer; exact verified artifact consumers in Flutter and Python.|**PASS bounded.** Production dispatch/fixture seams and pinned A3a-to-A3b binding support separate host processes, not one installed continuous camera/channel/store flow.|
|02|Lifecycle timers, cache invalidation and replacement-screen ordering.|**PASS bounded.** Shared observer reconciliation, non-adoptable ending identity and deterministic tests cover accepted finite-response cases. Permanent reply loss, fresh-screen lifecycle seeding and arbitrary direct callers remain outside proof.|
|03|Scoped export counts, safe publication, borrowed handles, partial-clear invalidation, persistence/purge/reopen.|**PASS bounded.** Read production helpers and failure/retry tests, including strengthened original borrowed-handle checks. No global cross-filesystem/DB/preferences transaction or forensic-erasure claim. Default participant stores were not exercised.|
|04|Staged resource acquisition, exception-preserving cleanup, camera/event subscription replacement.|**PASS bounded.** Rollback and final delivery ownership checks match accepted repairs. Inert versus detached registration, registry-ID retry/differing-messenger behavior and actual hardware/FlutterEngine teardown remain expressly limited.|
|05|Native benchmark/control artifacts through actual collectors/history with transport mocked.|**PASS bounded.** Pinned manifest, successful producer XML/ledger, strict list types and verified-byte handoff inspected; preflight independently rerun. Synthetic trust metadata and diagnostic interpreter adaptation do not establish hardware attestation.|
|06|Six FIVE/THREE validation fixture preparations and strict parity schema/identity/finite arithmetic.|**PASS bounded.** Six external fixtures/180 PNGs hash-checked by safe readback. B1-R1 overflow follow-up is closed in the later accepted comparator; old source-bound references remain historical. No new Android/anatomical/classifier parity asserted.|
|07|Reusable APK inspector and final artifact inspection.|**PASS bounded tooling/evidence.** Current artifact bytes, ZIP CRC, protected assets and native inventories independently checked. ARM64 Flutter and three-ABI dependency packaging are accurately distinguished; strict ARM64-only rejection is retained, not redefined as a policy approval.|
|08|Validation-only Keras/candidate clip/class diagnostics.|**PASS retained diagnostics only.** Historical150 records/model,144 correct/model retained; safe readback independently rerun. No new inference and no final-test, anatomical, causal or signer-independent claim.|
|09|Prepare isolated bounded campaign tooling; train only after separate authorization.|**REQUEST CHANGES — SPEC-R1.** Both actual training and runner are absent, but only training execution is clearly separately approval-gated by the approved preparation requirement.|
|10|Additive strict validation/provenance helper; full source-bound evaluation/export deliverable.|**PASS helper; full-source deliverable BLOCKED.** All13 historical code roles checked against their correct historical snapshots;134 source metadata pairs remain unavailable. No successful full-source manifest or cryptographic historical checkpoint-to-shipped-model chain is supplied.|
|11|Optional-feedback/required-questionnaire contracts; explicit legacy export validation; human rubric boundary.|**PASS technical export/form scope; human scoring BLOCKED.** App self-reports, SUS-labelled items and transport dummy payloads are not approved rubric observations. Instrument/sign list/rater/join/missingness/consent decisions remain absent.|
|12|Synthetic descriptive tools with safe diagnostics, exact types, relational counts and absent/ambiguous observations.|**PASS synthetic plumbing; human/inferential acceptance BLOCKED.** No guessed group/consent/withdrawal, zero imputation, human score or approved inferential plan is claimed. C2-L1 publication coverage follow-up is closed.|
|13|Current campaign index with implementation/execution/review/dependency distinctions.|**PASS prepared documentation.** Exactly16 unique dispositions, `all16_complete=false`; frozen older parent-owned ledgers are not silently upgraded. Parent reconciliation/acceptance still required. SPEC-R1 prevents full host-completion declaration.|
|14|Reproducible handoff and blank physical-study forms.|**PASS prepared handoff.** Exact environments/commands, pinned consumer selection, historical-safe readback and command reuse hazards documented. Blank hardware/trial forms stay planning artifacts; no acquired phone or trial claimed.|
|15|Architecture decisions/deviations.|**PASS proposed decision records only.** Holistic versus split landmarkers, historical local training versus Colab, local storage and separate rubric questions remain proposed/approval-pending. No fabricated PM/adviser/expert/cloud/ABI policy approval.|
|16|Complete host verification/build/source freeze and independent final reviews.|**PASS executed D evidence; acceptance still pending.** Counts/task lines/APKs verified below. This specification review supplies one required review, not separate quality review or parent re-execution. Spec21 integration task16 remains unchecked and is not satisfied by host16.|

## Independently checked execution evidence

### Saved D executions — parsed/read back, not rerun by this reviewer

| Check | Actual evidence readback |
|---|---|
|Flutter full|79 nonhidden `testDone` successes,0 failures/errors/skips; final `done.success=true`.|
|Flutter analysis|Exit0 record; log contains `No issues found!`.|
|JVM full|17 saved XML suites,170 actual testcase nodes;0 failures/errors/skips. `:app:testDebugUnitTest` executed, not UP-TO-DATE.|
|Instrumentation source compile|Exact executed `:app:compileDebugAndroidTestKotlin` line in successful forced JVM invocation. Compilation is not instrumentation execution.|
|Benchmarking|`Ran 124 tests`; `OK (skipped=2)` —122 passing,2 explicit MediaPipe Holistic capability skips.|
|Compatible parity/campaign|21 tests, `OK`, no skips in the existing compatible environment. Overlaps broad discovery; not21 extra unique tests.|
|Evaluation|18 tests, `OK`, no skips.|
|Training|29 tests, `OK`, no skips. Existing synthetic fixtures do not imply actual training or real-model conversion.|

Command/result log hashes and source-manifest digests were compared, not inferred from successful tool starts. The initial261-file source manifest still matches the checkout, with no altered initial source entries. Successful test/build records bind to manifest SHA256 `0223e7b1ef0e85e82afdd891993c5f05c3bfb932141e3c80213d1a0f5cb2b989`. Later additions are the documented handoff/status/decision files and separately frozen D material, not untested production modifications.

### Fresh reviewer execution

1. Existing `/opt/homebrew/bin/python3.11 -B -E -m unittest benchmarking.test_inspect_release evaluation.test_export_cli evaluation.test_legacy_export evaluation.test_synthetic_descriptive -v`, with scratch TMPDIR: **49 tests, all passed,0 skips**, exit0. This is an overlapping focused check, not a rerun of all D suites.
2. `d/readback-history.py --check-only`: exit0; six B1 fixtures/180 PNGs; B2 actual150 records and144 correct per model,134 missing source records,13 historical source-code roles; current acceptance bindings match. No raw video/NPZ opened or inference run.
3. `benchmarking/host_fixture_replay.py preflight`: exit0; authoritative run `323291af-c067-46dc-bae1-067d62fab10b`, manifest SHA256 `3279cb7d01075a9192f2566ae5573dd6137a23c6710ef1d0a590b78564fe0fed`;11 artifact/42 source bindings and5 successful producer tests checked. This verifies the retained accepted producer run, not a fresh JVM producer execution.
4. Independent Python hashing/parsing:70 postimages/snapshots,279 freeze entries,206 evidence entries,82 protected originals and261 original execution-source entries matched. Independent APK ZIP/digest/asset checks and six historical APK snapshot hashes matched. `git diff --check` exit0.

These reviewer executions are not parent execution counts. No expensive build or whole-suite duplication was undertaken.

## APK provenance and recovery adjudication

| Artifact | Bytes | SHA256 | Supported producing invocation |
|---|---:|---|---|
|Debug|197412392|`f45353b6f7711ab21bb222b5171e678de0f46902e5bf1714cbe2ad55f596ff95`|`debug-test-build-fresh3`|
|Android test|374427|`f6a80996b8e18188b3cb02fe429e313891d4fc97e4d7e035a4a5ae949c9b506e`|`debug-test-build-fresh3`|
|Release|66969546|`ad59b02daeae01f2fa71e4ca09fbc93985e63aef702025c91f85cc56b462ba27`|`release-build-retry4`, with retained same-source retry2/retry3 compilation/minification chain|

Current APK paths and external current snapshots match these sizes/hashes. Independent ZIP CRC and duplicate-name checks passed. Both application APKs contain the five expected protected assets with matching independent protected-source hashes; test APK has no corresponding native/model requirement. Debug has15 native paths and three Flutter ABI namespaces. Release has13 native paths in arm64-v8a/armeabi-v7a/x86_64, with libapp/libflutter only ARM64.

**Fresh host-build claim is warranted only with its documented incremental composition.** Debug fresh3 explicitly executed Flutter/application/instrumentation compilation and both packaging tasks. Release retry2 executed Flutter/Kotlin compilation and attempted R8 but failed; retry3 executed R8 and successful assembly; retry4 repackaged after the exact generated-manifest quarantine, retaining the same261-file source identity. Retry4's compiler/minifier tasks are UP-TO-DATE, so it must not be described as a fresh clean full rebuild by itself. The documentation explains this correctly. An earlier invocation merely observing another variant's APK is not that variant's producer. No clean-build, hermetic reproducibility, signature, ELF compatibility, installation, startup or runtime acceptance is inferred.

The inspector's own `current_source_build_provenance=false` is appropriate: expectations alone cannot establish provenance. The separate actual source/command/result/log/artifact composition supplies bounded host build-run evidence. The strict ARM64-only probe correctly rejects three-ABI dependency namespaces. Historical packaging consistency passing is neither approval of that policy nor proof of a Gradle defect; do not silently narrow or approve it during review.

Read the failed logs and exact quarantine/recovery records. The first420s debug tool timeout has no observed successful completion and is excluded. Initial/retried release failures and suffix-containing APK inspector rejections are retained. Six historical pre-build APK path snapshots rehash correctly. Resident suffixed debug snapshots/NativeAssetsManifest have recorded canonical digest comparisons; DATALESS SO/DEX preimage digests remain **unknown/null**, not “verified bytes.” TTF flags changed on rename and its preimage digest was unavailable; recovery states this instead of asserting unchanged flags. The failed external SO move and successful same-provider metadata-preserving rename do not establish provider origin or content equality. Narrow generated-object preservation is supported; no broad-clean/source-reset rationale is supplied or needed.

## Limited nonblocking observations and acceptance boundaries

- The parent-owned `.superpowers/sdd/progress.md`, `docs/phase-gates.md` and `benchmarking/study_readiness.md` retain dated older counts/active-work language. D's current index explicitly supersedes historical descriptions and correctly leaves those files to the parent. After adjudication, add an authorized current parent decision; do not rewrite historical evidence or present stale counts as current.
- D's report opens with an older “in progress” line but has an explicit final-outcome section and pending-parent boundary. This is not a hidden acceptance claim. Future parent status should be separate from this frozen evidence package.
- Do not reopen closed A1 borrowed-handle, A2a finite handoff, A2b subscriber leak, A3b ledger-type, B1 arithmetic-overflow, C1 publication-coverage or C2 CLI-coverage findings merely because earlier reports called them open. Later source/test/acceptance records resolve them. Conversely, retained messenger/registration, permanent-reply-loss, direct-caller, installed-flow and research limits remain limitations, not fixes supplied by this review.

## Required next decision

Resolve **SPEC-R1** by authorized tooling implementation/review or an explicit scope-deferral decision. Parent must independently complete its readback/verification, obtain the separate whole-package quality verdict and record only the supported bounded outcome. No need to rerun training/inference or hydrate unavailable data merely to obtain a green status.

Continue to leave full-source provenance, historical model chain/numerical promotion, untouched/signer-independent evaluation, approved human instrument/rater/missingness/statistics, consent/participant authorization, actual installed continuous flow, physical hardware/provisioning/three-condition FPS/latency/thermal/all-sign/signer and expert/anatomical gates open. Host software evidence cannot close these gates.
