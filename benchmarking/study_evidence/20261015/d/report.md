# Package D host verification report

Status: in progress; no completion or acceptance asserted. Parent independent verification and whole-package spec/quality review required.

## Execution ledger

- `flutter-analyze`: exit 0; `flutter-analyze.log` (exact command/source binding in append-only ledger).
- `flutter-full`: exit 0; `flutter-full.log` (exact command/source binding in append-only ledger).
- `benchmark-full`: exit 0; `benchmark-full.log` (exact command/source binding in append-only ledger).
- `evaluation-full`: exit 0; `evaluation-full.log` (exact command/source binding in append-only ledger).
- `training-full`: exit 0; `training-full.log` (exact command/source binding in append-only ledger).
- `holistic-compatible`: exit 0; `holistic-compatible.log` (exact command/source binding in append-only ledger).
- `jvm-full`: exit 0; `jvm-full.log` (exact command/source binding in append-only ledger).
- `debug-test-build`: exit 0; `debug-test-build.log` (exact command/source binding in append-only ledger).
- `release-build`: exit 1; `release-build.log` (exact command/source binding in append-only ledger).
- `release-build-retry1`: exit 1; `release-build-retry1.log` (exact command/source binding in append-only ledger).
- `release-build-retry2`: exit 1; `release-build-retry2.log` (exact command/source binding in append-only ledger).
- `release-build-retry3`: exit 0; `release-build-retry3.log` (exact command/source binding in append-only ledger).
- `debug-test-build-fresh2`: exit 0; `debug-test-build-fresh2.log` (exact command/source binding in append-only ledger).
- `debug-test-build-fresh3`: exit 0; `debug-test-build-fresh3.log` (exact command/source binding in append-only ledger).
- `release-build-retry4`: exit 0; `release-build-retry4.log` (exact command/source binding in append-only ledger).
- `host-tool-versions`: exit 0; `host-tool-versions.log` (exact command/source binding in append-only ledger).
- `historical-artifact-readback`: exit 0; `historical-artifact-readback.log` (exact command/source binding in append-only ledger).
- `accepted-producer-preflight`: exit 0; `accepted-producer-preflight.log` (exact command/source binding in append-only ledger).


## Final outcome — host evidence prepared, parent acceptance pending

No application/model/benchmark/training/evaluation source or tests were edited by D. Created only the three named new documentation files and new D evidence/review snapshots. All16 dispositions are in `dispositions.json` and the new status document; **all16 complete is false**. Parent independent verification and whole-package spec/quality review remain mandatory. Parent-owned progress/readiness/phase-gates files were untouched.

Actual final counts: Flutter 79 passed with0 failures/skips; JVM 170 tests/17 suites with0 failures/errors/skips; benchmarking 124 discovered, 122 passed and2 explicit Holistic capability skips; compatible parity/campaign 21 passed0 skips (overlapping suite, includes both detector cases); evaluation 18 and training 29 passed0 skips. Flutter analysis exited0 with no issues. JVM and instrumentation Kotlin targets have exact fresh execution lines, and XML/binary results were copied while holding the shared flock. Commands/exits/env/source/log hashes are in the append-only ledger and per-label JSON.

Successful final artifact identities and independent inspection:

- debug: `app/build/app/outputs/apk/debug/app-debug.apk`, 197412392 bytes, SHA256 `f45353b6f7711ab21bb222b5171e678de0f46902e5bf1714cbe2ad55f596ff95`; actual producer `debug-test-build-fresh3-result.json`; external snapshot `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/kumpas-d-20261018/current-apks/debug.apk`.
- android_test: `app/build/app/outputs/apk/androidTest/debug/app-debug-androidTest.apk`, 374427 bytes, SHA256 `f6a80996b8e18188b3cb02fe429e313891d4fc97e4d7e035a4a5ae949c9b506e`; actual producer `debug-test-build-fresh3-result.json`; external snapshot `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/kumpas-d-20261018/current-apks/android_test.apk`.
- release: `app/build/app/outputs/flutter-apk/app-release.apk`, 66969546 bytes, SHA256 `ad59b02daeae01f2fa71e4ca09fbc93985e63aef702025c91f85cc56b462ba27`; actual producer `release-build-retry4-result.json`; external snapshot `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/kumpas-d-20261018/current-apks/release.apk`.

Debug/test freshness uses `debug-test-build-fresh3`: Flutter/application/instrumentation compile and both package tasks executed. Release freshness uses `release-build-retry4`: actual ARM64-targeted offline assets/package/assembly, bound to the unchanged-source full compile/minification chain in retry2/retry3. Earlier debug/test commands only observed release bytes and are not release producers; earlier release commands only observed debug/test bytes and are not their producers. Latest independent `artifact-readback.json` and current inspector outputs are authoritative; intermediate manifests retain unsuccessful or historical artifacts.

Independent ZIP CRC/duplicate-member checks and all five protected asset digests passed for each app APK. Test APK has no native/models requirement. Debug has Flutter libraries in3 ABI namespaces; release libapp/libflutter only ARM64 but13 total native paths in3 dependency namespaces. Current debug and retained historical-three-ABI release expectations passed; strict ARM64-only release probe exited1 as expected, not an approved policy failure or automatic Gradle configuration defect. Inspector-only build provenance remains false by design; the separate real command/source/log/producer composition establishes host build-run provenance. No signature/ELF/install/startup/runtime claim.

### Incidents retained, not concealed

Release initial/retry1/retry2 exited1 on generated DATALESS suffix files TTF/SO/DEX. Narrow quarantine manifests preserve exact objects; no broad deletion/clean/reset or source fix. The TTF script exited1 on a flags-equality assertion after rename: the flag changed, so recovery records actual postimage/hash rather than inventing a preimage hash. External SO rename timed out Errno60; same-provider relocation preserved inode/device/size/flags. SO/DEX DATALESS digests remain null; this is not byte-hash verification. Resident debug snapshot and release JSON duplicates were hash-compared to canonical files before exact-file quarantine. Duplication origin is unknown.

The first stronger debug tool call timed out420s with no observed completion exit and is not counted successful. Managed fresh2 completed, but the accepted inspector rejected two suffixed generated ZIP snapshot entries. After preservation/rebuild, fresh3 debug passed. The first fresh release inspector rejected the suffixed NativeAssetsManifest entry; after preservation and retry4, current release passed. Both unsuccessful APKs are preserved in external `fresh-apks`/`final-apks` snapshots. The attempted SIGINT found no such process after managed completion: no signal was delivered or daemon killed. Exact observed incidents are in `execution-incidents.json`; source-script assertion failures are not fake build or source-test failures. Retained Kotlin/SDK/Gradle/upstream dependency warnings are nonfatal in the successful commands.

### Historical-safe readback and remaining blockers

`historical-readback.json` verifies six historical B1 fixtures/180 PNGs and original comparator-before identity without opening raw video/NPZ. B2 retained150 historical validation records/model,144 correct each,134 missing metadata records, incomplete binding and all13 source-code roles checked against the correct historical helper/test/comparator snapshots. Current repaired sources match the latest accepted records separately. No old source-complete verifier, inference/retraining or hydration of raw data was run; no manifests were rebound. Follow-ups B1-R1/C1-Q1/C2-L1 are accepted closed.

Host09 actual retraining remains unapproved and its isolated runner unimplemented. Host10 full-source provenance remains blocked134 DATALESS source pairs. Host11/12 human rubric/scoring/inference remains blocked on instruments, raters, missingness and analysis/consent approvals; synthetic descriptors do not satisfy it. Host13–16 artifacts are prepared/executed but review pending. Installed continuous camera/channel/SQLite/export/delete/reopen, physical FPS/latency/thermal/all signs/signers, expert/anatomical, untouched/signer-independent evaluation and participant authorization remain open.

Preservation: all82 protected originals unchanged; 261 initial reviewable source/config/docs files unchanged except the three new authorized docs (264 final inventory); 69 latest accepted source postimages matched. Six pre-build APK path snapshots rehashed successfully. `review-package.json` supplies 29 changed tracked postimages plus complete contents of 41 new files and the nonempty dirty HEAD diff. `git diff --check` exit0; separate new-file whitespace scan clean. External media/vectors/APK bytes remain outside Git; no participant stores were copied.

Deliverables: `docs/host-completion-2026-10-18.md`, `docs/host-reproducible-handoff.md`, `docs/decisions/2026-10-18-host-scope-deviations.md` (proposed/approval pending). Exact final source/document/helper/report hashes follow in `source-freeze.json`; freeze this package for parent whole-change review. No commits/push/deployment/installations/device transport/real-model conversion or model/reference/math/XP/layout edits. Blank hardware/trial/approval forms remain unchanged.
