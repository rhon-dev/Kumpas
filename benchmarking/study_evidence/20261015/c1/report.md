# C1 host07 release inspector execution report

Status: in progress. Host-only tooling, synthetic ZIP tests and read-only existing APK inspection. Existing artifacts are not fresh builds. Checkout hashes captured now do not establish build provenance. Parent review and final fresh build remain separate.

Task brief: taskbrief.md. Commands and actual exit/log evidence: command-ledger.jsonl (append-only). No app/model/build/training source edits authorized.

Execution `initial-snapshot`: exit 0; `initial-snapshot.log`.

Execution `slice1-red`: exit 1; `slice1-red.log`.

Execution `slice1-green`: exit 0; `slice1-green.log`.

Execution `slice2-red`: exit 1; `slice2-red.log`.

Execution `slice2-green`: exit 0; `slice2-green.log`.

Execution `slice3-red`: exit 1; `slice3-red.log`.

Execution `slice3-green`: exit 0; `slice3-green.log`.

Execution `slice4-red`: exit 1; `slice4-red.log`.

Execution `slice4-green`: exit 0; `slice4-green.log`.

Execution `slice5-red`: exit 1; `slice5-red.log`.

Execution `slice5-green`: exit 0; `slice5-green.log`.

Execution `slice6-red`: exit 1; `slice6-red.log`.

Execution `slice6-green`: exit 0; `slice6-green.log`.

Execution `broad-benchmark`: exit 0; `broad-benchmark.log`.

Execution `historical-inventory`: exit 0; `historical-inventory.log`.

Execution `historical-release-strict-arm64`: exit 1; `historical-release-strict-arm64.log`.

Execution `historical-native-policy`: exit 0; `historical-native-policy.log`.

Execution `historical-release-packaging`: exit 1; `historical-release-packaging.log`.

Execution `historical-rejection-diagnosis`: exit 1; `historical-rejection-diagnosis.log`.

Execution `historical-zip-aliases`: exit 0; `historical-zip-aliases.log`.

Execution `slice7-red`: exit 1; `slice7-red.log`.

Execution `slice7-green`: exit 0; `slice7-green.log`.

Execution `historical-release-packaging-2`: exit 0; `historical-release-packaging-2.log`.

Execution `final-focused`: exit 0; `final-focused.log`.

Execution `historical-release-strict-arm64-final`: exit 1; `historical-release-strict-arm64-final.log`.

Execution `final-broad`: exit 0; `final-broad.log`.

Execution `historical-release-packaging-final`: exit 0; `historical-release-packaging-final.log`.

Execution `slice8-red`: exit 1; `slice8-red.log`.

Execution `slice8-green-final-focused`: exit 0; `slice8-green-final-focused.log`.

Execution `historical-release-current-source`: exit 0; `historical-release-current-source.log`.

Execution `current-source-broad`: exit 0; `current-source-broad.log`.

## Final disposition: DONE_WITH_CONCERNS

The additive release inspector and tests are complete for parent review. No existing repository file changed. Fresh builds and independent acceptance remain parent-owned. The concern is historical packaging, not an unreported source edit: the release contains three native ABI namespaces despite ARM64-only Flutter code.

### Implemented contract and scope

The stdlib CLI requires explicit repository, APK and independently supplied version-1 expectation JSON. It binds exact APK digest, all five fixed Android asset hashes, current protected source bytes, exact intended ABI/native-file names and observed native digests. It rejects malformed/duplicate-key/nonfinite JSON, wrong exact types or hash syntax, missing or changed protected assets, corrupt ZIPs, duplicate members, traversal and path aliases, symlinks, missing/extra native files and wrong ABIs. Asset and native case aliases are rejected; Android resources remain case-sensitive because aapt legitimately generated names such as res/9N.9.png and res/9n.9.png. Nothing is extracted.

One open APK descriptor supplies digest and ZIP reads, with a final rehash. Expectations are read once and their exact byte digest is retained. Protected bytes are checked before and after ZIP inspection. Optional output requires an existing explicit directory and a new contained target. POSIX no-follow directory walks, exclusive staging, fsync, exact staged/final byte readback and exclusive hard-link publication preserve existing outputs; fault tests cover fsync/link/readback and staging collisions. All CLI errors are fixed JSON without payload/argument echoes.

### Regression and execution evidence

Eight incremental RED/GREEN slices are retained in command-ledger.jsonl and slice logs. The first RED executed the public CLI and failed its valid-verification assertion against an explicit verification_unavailable result, not import absence. Later REDs demonstrated schema acceptance, unchecked ZIP/native surfaces, symlink/escape output, digest/ZIP path replacement, unsupported compression leakage, Android-resource over-rejection and nonexistent output-root acceptance. Some later tests were already-GREEN characterization (missing/changed assets, existing-output preservation, fault cleanup); they are not claimed as newly repaired defects. The initial schema RED also retained cascaded output failures, then isolated each mutation target for the GREEN run.

- `slice8-green-final-focused.log`: 28 run; 28 passed, 0 skipped, zero failures/errors.

- `current-source-broad.log`: 118 run; 116 passed, 2 skipped, zero failures/errors.


The two broad skips explicitly report unavailable MediaPipe Holistic `solutions`; they are not passes. Their inherited skip text mentions another environment, but this worker did not run that environment. Existing Python 3.11 was used with -B -E and scratch TMPDIR; no installation or training occurred.

### Real historical APK observations

All existing APK paths below were read-only inventoried. Five main-app artifacts contain all five assets with hashes matching the independently protected checkout. The instrumentation APK lacks those app assets, as recorded rather than treated as an application release. The extra `app-release 2.apk` is a distinct artifact, not silently selected.

| Existing APK | Bytes | SHA-256 | Native ABIs | Flutter ABIs |

|---|---:|---|---|---|

| `app/build/app/outputs/apk/androidTest/debug/app-debug-androidTest.apk` | 382400 | `c276116bc3bad24383101f07191f1e71d29fa52c16fc4b3a6b38bec5b024b291` | none | none |

| `app/build/app/outputs/apk/debug/app-debug.apk` | 212207146 | `0707d2f153c713055edaf50171b4c053393480f34940d380512cac0177543dff` | arm64-v8a, armeabi-v7a, x86_64 | arm64-v8a, armeabi-v7a, x86_64 |

| `app/build/app/outputs/apk/release/app-release 2.apk` | 66969546 | `ebe520dd92847e85a87de4708692904d673c7f870751a5fe587b0bda8633680e` | arm64-v8a, armeabi-v7a, x86_64 | arm64-v8a |

| `app/build/app/outputs/apk/release/app-release.apk` | 66969546 | `da66697f562d56ef34ea22e70c515c537f8cff640e3dda99007e8cf3fd617266` | arm64-v8a, armeabi-v7a, x86_64 | arm64-v8a |

| `app/build/app/outputs/flutter-apk/app-debug.apk` | 212207146 | `0707d2f153c713055edaf50171b4c053393480f34940d380512cac0177543dff` | arm64-v8a, armeabi-v7a, x86_64 | arm64-v8a, armeabi-v7a, x86_64 |

| `app/build/app/outputs/flutter-apk/app-release.apk` | 66969546 | `da66697f562d56ef34ea22e70c515c537f8cff640e3dda99007e8cf3fd617266` | arm64-v8a, armeabi-v7a, x86_64 | arm64-v8a |


`historical-release-current-source-result.json` is the final successful CLI output and supersedes earlier successful captures for current inspector-source identity only. Its APK digest came from the historical owner-parent-verification-1.json record, not from the APK under verification; asset/protected expectations came from host-baseline.json. Its explicit three-ABI/native-file packaging policy was frozen after current observation, not preregistered. That bounded consistency success is not strict ARM64-only acceptance. The separate strict ARM64 expectation was rejected (exit 1); no strict-acceptance result exists. Earlier real-APK failures due to over-broad resource case folding remain preserved, followed by the behavioral regression and repair.

Final real-result SHA-256: `ea6af87cb75419d631e099955aa74dcb18c3e12e1606f3f7b7858e5ebe149a83`. Inventory SHA-256: `8f65742711c97073ae94b69bc406ed44f4167d9ebbe74615bc9e12ee005ed0a0`.

### Preservation and handoff

All 1193 pre-existing tracked/untracked non-C1 files in preservation-before.json are unchanged, including accepted native/A3/B1/B2 sources, manifests and source-bound fixtures. All 82 original protected hashes match. Only two source files were added:

- `benchmarking/inspect_release.py`: `ecf9f2f33f2fc1f28bf9d6efc47a2f6f661e1e9fef929180cafe920c42eb5bb3`.

- `benchmarking/test_inspect_release.py`: `03450c2a0035116910d78d514a9d90e446f0679c8eb1626ea0870090ee98eae9`.


Supporting additions are confined to this c1 directory: task brief, incremental report, append-only command ledger, evidence runners, preservation snapshot, versioned explicit expectations, actual logs, historical inventory/diagnostic records, immutable CLI results and verification-summary.json. No app/build/Gradle/model/label/training/normalization/math/XP/privacy source changed. B2 remains accepted bounded tooling with full provenance blocked by 134 missing metadata records.

### Remaining limitations

This inspected historical bytes, not a fresh build. Current source capture is not build-source provenance; neither artifact_kind=fresh_build nor a matching APK hash changes that. Native names and archive hashes do not establish ELF ABI correctness, APK signatures, Android manifest policy, runtime behavior, physical performance or study authorization. Trust in the expectation issuer, host and checkout remains required. Descriptor checks and publication readback are not adversarial concurrent-filesystem or power-loss guarantees. A strict ARM64-only requirement needs parent adjudication; this slice did not change release configuration. Parent independently reruns/reviews, constructs expectations for its fresh artifact and retains all installed/physical/human gates.

Execution `final-verification`: exit 0; `final-verification.log`.

Execution `parent-focused-1`: exit 0; `parent-focused-1.log`.

Execution `parent-historical-1`: exit 0; `parent-historical-1.log`.
