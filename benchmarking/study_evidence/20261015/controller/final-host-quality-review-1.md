# Independent final host quality/evidence review — A–D

## Verdict

**PASS for the implemented, explicitly bounded host software and D evidence/handoff package, with one LOW nonblocking test-invocation concern (Q1).** No new blocking correctness, privacy, provenance, publication or integration defect was identified. This review incorporates current-source rematching of prior independent scoped reviews, renewed focused execution and independent final-artifact/evidence readback; it does not claim every application path was freshly executed by this reviewer.

**Not an all16 completion or acceptance decision.** Host09's isolated experiment runner remains unimplemented, actual retraining separately unapproved, host10 full-source provenance blocked on134 unavailable source pairs, and human rubric/inferential work approval-blocked. These are substantive remaining deliverables/dependencies, not accepted substitutes. Parent must resolve whole-plan scope/specification disposition separately. The separate specification verdict, parent acceptance and installed/physical/model/expert/study gates are not supplied by this quality report.

Review date: October18,2026. Only this assigned report was written inside the repository. No application/test/build configuration, governed status file, original evidence or protected asset was edited. No Gradle/build, Flutter suite, real inference/training/conversion, installation/download, device/ADB, default participant-store operation, raw video/NPZ read/hydration or Git state mutation was performed.

## Identity and review basis

Repository: `/Users/ahronjanl.rafaelahron.0804icloudcom/Documents/Thesis/kumpas`, dirty HEAD `6b8b1b6770e46bea7728a8e9ca4ae6d78e857640`.

- `d/source-freeze.json` SHA256 **`2d226fe2e3387c1ca16386dd992b0e2d1f8da9e02874eced94c3629cf32b6383`** matches the assignment. All279 recorded files independently rehashed without mismatch, including final recheck.
- `d/review-package.json` SHA256 `793ab603e795e5ef20173b64119a6279139fe4fde31ff88517a9871e0b242346`: **29 tracked postimages +41 complete new files**. All70 checkout/snapshot digests and the nonempty dirty tracked HEAD-diff digest match. HEAD alone was not the source package.
- All206 `d/evidence-freeze.json` entries independently rehashed without mismatch, including final recheck. All82 protected originals match baseline expected values and D's after capture. All69 current accepted source postimages match disk and their recorded acceptance authority; A3a source authority is the specifically selected manifest.
- Read approved October15 design/plan, PRD architecture/gates/privacy requirements, phase-gate/readiness status, D report, runner/readback/inspection helpers, result/source/log/artifact/incident records and all three new documents. Inspected cross-package Activity/control/factory/export/resource/view/subscriber ownership, shared Dart lifecycle/repository queue, benchmark UUID/confirmation/deadline behavior, verified-byte Python/Dart handoff, collector/history and explicit-file evaluation publication seams.
- Prior scoped independent A1/A2/A3/B/C reviews/controller acceptances remain evidence for unchanged code, not new reviewer execution. Latest A2a/A2b/A3b/B2 repair verdicts and follow-up closures were retained instead of superseded initial findings. B1-R1/C1-Q1/C2-L1 are closed. A2a arbitrary-direct-caller/permanent-reply-loss and A2b framework-registration limitations remain.
- Tracked added-line scans found no eval/exec, shell=True, pickle-load or secret-assignment pattern; complete new-file scans found no eval/exec, shell=True or pickle-load pattern. These limited patterns are not a comprehensive security certification. `git diff --check` returned0.

## Finding

### Q1 — LOW / nonblocking: package-qualified replay tests depend on discovery's import path

**Locations:** `benchmarking/test_host_producer_replay.py:26,70,194,342`, bare `import host_fixture_replay` inside tests. Production replay behavior is not implicated.

The initial fresh command from repository root was:

```sh
/opt/homebrew/bin/python3.11 -B -E -m unittest benchmarking.test_host_producer_replay benchmarking.test_inspect_release evaluation.test_export_cli evaluation.test_legacy_export evaluation.test_synthetic_descriptive -v
```

Actual result: exit1, `Ran 76 tests`, `FAILED (errors=52)`. Replay setup/method/subtest errors were `ModuleNotFoundError: No module named 'host_fixture_replay'`. Subtest errors and failed class setup are not separate test methods. Other inspector/evaluation methods passed. Minimal equivalent reproduction: package-qualified `benchmarking.test_host_producer_replay.PreflightNegatives.test_wrong_run` from repository root without adding benchmarking to sys.path.

The documented discovery layout is valid and was independently rerun unchanged:

```sh
/opt/homebrew/bin/python3.11 -B -E -m unittest discover -s benchmarking -p test_host_producer_replay.py -v
```

**34 passed, zero failures/errors/skips, exit0.** Thus this is focused-invocation maintainability friction, not a failing documented campaign or invalidation of D's successful discovery. Optional follow-up: package-safe imports or an explicit supported focused command. No repair is required for this bounded PASS and none was made.

Initial failure output remains tool-retained at `~/.hermes/cache/terminal-output/out-1792305081-77034-1350.log`; it is not counted as a successful suite.

## Fresh reviewer execution

Existing Python3.11, `-B -E`, explicit Hermes scratch TMPDIR, `MPLBACKEND=Agg`; shared exclusive `kumpas-gradle.lock` acquired nonblocking. No competing build was started. Synthetic tests own their temporary fixtures.

| Fresh operation | Actual result |
|---|---|
|Replay discovery above|34 passed,0 skips,exit0;1.297s|
|`-m unittest benchmarking.test_inspect_release evaluation.test_export_cli evaluation.test_legacy_export evaluation.test_synthetic_descriptive -v`|49 passed,0 skips,exit0;3.306s;31 inspector +18 evaluation|
|`benchmarking/host_fixture_replay.py preflight`|Exit0; exact selected run/manifest,42 sources,11 artifacts,5 successful producer tests|
|`d/readback-history.py --check-only`|Exit0;6 fixtures/180 PNGs; B2 150 records/model,144 correct each,134 missing source records; all13 historical code roles/current accepted bindings|
|Real `inspect_release.py`, current debug expectation, stdout-only|Exit0,empty stderr; stdout digest `9f40bad4d210dea42862b6051e5c7b704deb2e1ce8b8882e8424c966b43a4af6` equals saved D log|
|Same CLI,current release expectation|Exit0,empty stderr; stdout digest `e15496d4995382de17ad20feb0dd976dbb66f40862582467e61146f90e5f41fe` equals saved D log|
|Same CLI,strict ARM64-only release expectation|Expected exit1,empty stderr; rejection digest `34389503cfb90a28456a124d8087eb1015b10f20e38e9f0656bdb453d7b5d847` equals saved D log|

**83 distinct canonical methods passed in final correctly scoped runs.** Repeated methods from the initial failed combined invocation are not added. Inspector commands supplied repository root, `d/current-<kind>-expectation.json` and the actual corresponding APK, with no output target. No fresh broad benchmarking/training/Holistic/Flutter/JVM execution is claimed.

Reviewer diagnostic recovery: an artifact helper initially used unavailable hashlib.file_digest in the older default python3 and stopped before APK reads; streaming hashlib completed the retry. An acceptance-map helper initially assumed every authority directly carried source_hashes; following A3a's selected manifest completed all69 comparisons. Neither error changed source/evidence or supplied a fictional pass. Final report overwrite first met the tool's stale-write guard; rereading the incremental report permitted this replacement.

## Independently parsed saved D execution — not reviewer reruns

| Check | Actual saved readback |
|---|---|
|Flutter analysis|Exit0,`No issues found!`|
|Flutter machine|79 visible successful testDone events; final done success=true;0 failures/skips|
|JVM preserved XML|17 suites,170 tests;0 failures/errors/skips|
|Broad benchmarking|124 discovered;122 explicit ok lines,2 actual Holistic capability skips;`OK (skipped=2)`|
|Compatible parity/campaign|21 tests,OK,0 skips; overlaps broad discovery, not21 additional unique tests|
|Evaluation|18 tests,OK,0 skips|
|Training|29 tests,OK,0 skips; synthetic fixture warnings retained|

All11 named final summary log digests match actual logs. JVM/debug/release result objects exactly occur as end records in the append-only ledger. Relevant source manifests hash to `0223e7b1ef0e85e82afdd891993c5f05c3bfb932141e3c80213d1a0f5cb2b989`, with no recorded source changes. Later addition of three documentation files is not hidden later production-code drift.

## Exact artifact/producer binding

Independent streaming hashes under the shared lock matched current APKs and external snapshots to producing result artifact maps, source manifests and log digests:

| Artifact | Bytes / actual producer | SHA256 |
|---|---|---|
|Debug|197412392 / `debug-test-build-fresh3`|`f45353b6f7711ab21bb222b5171e678de0f46902e5bf1714cbe2ad55f596ff95`|
|Instrumentation/test|374427 / `debug-test-build-fresh3`|`f6a80996b8e18188b3cb02fe429e313891d4fc97e4d7e035a4a5ae949c9b506e`|
|Release|66969546 / `release-build-retry4`|`ad59b02daeae01f2fa71e4ca09fbc93985e63aef702025c91f85cc56b462ba27`|

- Independently checked all archives' ZIP CRC and exact duplicate names; native membership equals D inventory. Both app APKs' five assets match independent protected checkout bytes. Test APK has no invented model/native requirement. All6 historical APK snapshots independently rehashed successfully.
- JVM log has exact executed `:app:testDebugUnitTest` and `:app:compileDebugAndroidTestKotlin` lines, not UP-TO-DATE. Debug fresh3 executes Flutter/application/instrumentation compilation and both packaging tasks. Instrumentation source compilation/build is not instrumentation runtime.
- Release retry2 actually compiles Flutter/Kotlin then fails R8 on generated DEX; retry3 actually executes successful R8/package/assembly. Retry4 executes refreshed assets/compression/package/assembly while reusing unchanged-source compilation/minification. This is a documented retained producer chain, not all-prerequisites freshness in retry4 or a cached APK presented as a new full compilation. Merely observing another artifact in an earlier invocation does not establish its producer.
- Debug native libraries span3 ABI namespaces. Release libapp/libflutter are ARM64 only; dependencies give13 native paths across3 namespaces. Historical consistency passes; strict ARM64-only rejects. No new ABI policy or automatic configuration-defect finding follows. Inspector `current_source_build_provenance=false` is correct: separate actual command/result/source/log composition supplies bounded host-build provenance.
- ZIP/hash readback does not verify signatures, ELF compatibility, installed startup/runtime, physical performance or reproducible-build byte determinism.

## Integrated contract/handoff assessment

| Boundary | Quality/evidence assessment |
|---|---|
|Persistence/export/clear/resource ownership|Production control uses the tested callable and explicitly injected export-database factory, without default-store fallback. Scoped counts derive from exported rows; unique staging/publication/readback preserves prior exports and borrowed helper ownership. Acquired-resource rollback and final view/subscriber/event fencing remain intact. No native-driver release, arbitrary-caller session atomicity, differing-messenger handler removal or same-registry retry guarantee is inferred.|
|Provenance/types/privacy|Pinned A3a run `323291af-c067-46dc-bae1-067d62fab10b`, manifest `3279cb7d01075a9192f2566ae5573dd6137a23c6710ef1d0a590b78564fe0fed`, remains authoritative. Fresh replay negatives exercise XML/ledger/artifact/schema rejection. Command/output fields are string arrays before membership. Dart receives verified in-memory bytes, not an unchecked pathname reread. Collector/history fixed diagnostics, report/control schemas and synthetic trust preserve diagnostic/nonphysical disposition.|
|Historical model/parity identity|Safe readback passed without opening original raw sources. B1 keeps its before-follow-up comparator. B2 keeps old helper **and test** plus comparator role; repaired current code is separately bound. No retroactive rebinding, regeneration or successful full-source manifest.|
|Publication/research tooling|Fresh inspector/evaluation regressions cover aliases/symlinks/duplicates, snapshots, second-fsync/partial-write/final-open faults, owned-inode cleanup and input-byte binding. Evaluation permits explicit synthetic descriptors, not human scores or consent/real-data authorization. Trusted local filesystem limits remain, not hostile-filesystem/power-loss promises.|
|New documentation reproducibility|All three docs distinguish direct offline Gradle/task-scoped rerun from prerequisite freshness, current artifacts from preserved history, and safe readback from source-opening old verifiers. Commands, pinned handoff, ABI limitations, blank forms and proposed approvals match actual evidence. Parent-owned status amendments remain pending rather than falsely attributed to D.|

## Incidents and remaining gates

D's420s timeout without observed completion, generated-output failures, rejected intermediate APKs and quarantine assertion/move failures remain retained, not successes. Independently stat-checked quarantined SO/DEX inode/device/size/flags against manifests: match. **No content read/hash was attempted for those DATALESS objects; null digests remain honest.** Metadata-preserving rename is not byte-hash proof. Duplication/provider origin remains unknown. TTF recovery records an observed flags transition rather than fabricating unchanged flags or an unavailable preimage digest. No blanket byte-preserved claim is accepted for unhashed objects.

Still unresolved: host09 runner plus separate training approval;134 source pairs/full historical model chain; human instrument/sign/rater/missingness/statistical/consent approvals; uninterrupted installed CameraX/channel/UI/SQLite/export/delete/reopen; actual hardware/setup/FPS/latency/thermal/all-sign/signers; numerical/untouched/signer-independent/expert/anatomical gates. Missing observations remain missing, not zeros. Host software/artifact PASS closes none of these.

**Final quality disposition: PASS, bounded as above; Q1 LOW is advisory. Parent whole-plan specification/scope adjudication and acceptance remain outstanding.**
