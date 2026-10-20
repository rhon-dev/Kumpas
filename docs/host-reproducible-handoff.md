# Reproducible host handoff

Status: Package D prepared October18,2026; parent independent verification and whole-package review pending. Scope and all16 dispositions are in `host-completion-2026-10-18.md`. Commands here describe host-only reproduction, not authority to install, run a camera, retrain, convert real models, process participant stores or collect data.

## Checkout, runtime and evidence identity

Repository: `/Users/ahronjanl.rafaelahron.0804icloudcom/Documents/Thesis/kumpas`; HEAD `6b8b1b6770e46bea7728a8e9ca4ae6d78e857640` plus the complete dirty/untracked review snapshot. Evidence root `benchmarking/study_evidence/20261015/d`. Read its `taskbrief.md`, append-only `command-ledger.jsonl`, `verification-summary.json`, `artifact-readback.json`, `historical-readback.json`, `protected-after.json` and `review-package.json` before reproducing. Exact source/log hashes are in the ledger and final `source-freeze.json`. Do not use HEAD alone or silently overwrite historical evidence.

Executed host: macOS26.6,8 logical CPUs,8GB physical RAM; Flutter3.41.6/Dart3.11.4; JDK17.0.18; existing Android SDK at `$HOME/Library/Android/sdk`. Existing Python environments are complementary: `/opt/homebrew/bin/python3.11` for broad benchmarking/evaluation, `$HOME/.kumpas-venvs/tf/bin/python` for training tests, `training/.venv/bin/python` for the actual Holistic `solutions` API. Use `-B -E` so bytecode and injected cross-ABI PYTHONPATH do not contaminate execution. Broad discovery explicitly skips two Holistic cases; the compatible21-test parity/campaign run executes them on synthetic inputs. No installation is needed or authorized; stop on a missing dependency.

Use session scratch `~/.hermes/cache/scratch/kumpas-d-20261018` or a new exclusive scratch directory. Do not overwrite its `historical-apks`, `fresh-apks`, `final-apks` or `current-apks` snapshots. The historical directory predates builds; later directories retain unsuccessful and accepted artifact bytes respectively. Generated DATALESS SO/DEX quarantine remains at `app/build/kumpas-d-quarantine/` inside the same provider, with original inode metadata and unavailable digests explicit. The TTF quarantine is in external scratch. None is a participant store or a raw dataset copy. Do not broadly clean/reset or remove these recoverable objects.

## Repeating suites safely

Run one compute/build process at a time. Every D command acquired an exclusive `fcntl.flock` on `~/.hermes/cache/scratch/kumpas-gradle.lock`. Hold it through Gradle execution and XML/binary-result snapshot; otherwise another run can overwrite the counts being cited. Capture a fresh reviewable source manifest immediately before/after every command. Logs/results must use new exclusive names, never old run aliases. D's `run.py` and `postchecks.py` demonstrate the executed runner; its original labels refuse reuse. For parent re-verification, call its `execute` function with a **new** label and an explicit command/cwd/kind, or create an equivalently isolated campaign. Do not run `initialize` again against the same snapshot directory.

Exact suite commands, with current working directory shown:

```sh
# repository/app
/opt/homebrew/bin/flutter analyze --no-pub
/opt/homebrew/bin/flutter test --no-pub --machine

# repository; TMPDIR set to existing session scratch, MPLBACKEND=Agg
/opt/homebrew/bin/python3.11 -B -E -m unittest discover -s benchmarking -p 'test_*.py' -v
/opt/homebrew/bin/python3.11 -B -E -m unittest discover -s evaluation -p 'test_*.py' -v
"$HOME/.kumpas-venvs/tf/bin/python" -B -E -m unittest discover -s training/tests -p 'test_*.py' -v
training/.venv/bin/python -B -E -m unittest benchmarking.test_pipeline_parity benchmarking.test_parity_fixtures -v

# repository/app/android; inside the shared flock
JAVA_HOME=$(/usr/libexec/java_home -v 17)
export JAVA_HOME ANDROID_HOME="$HOME/Library/Android/sdk" ANDROID_SDK_ROOT="$HOME/Library/Android/sdk"
./gradlew --offline --console=plain :app:testDebugUnitTest --rerun :app:compileDebugAndroidTestKotlin --rerun
```

The training suite's existing synthetic save/conversion fixture is permitted; this is not real retraining or a real-model conversion. Do not replace it with default trainer/evaluator/exporter CLI execution. Parse actual Flutter machine `testDone`/final `done`, Python discovered/pass/skip output and all JVM XML. D observed79 Flutter;170 JVM/17 suites;124 broad Python with2 skips;18 evaluation;29 training;21 compatible tests. Do not assume these counts for a changed checkout or add overlapping compatible tests as new unique broad tests.

## Repeating builds and inspection

Before any further build, byte-copy and hash-check **every existing APK being replaced** into a new external snapshot. Existing APK paths may contain historical or other-invocation bytes. Record actual producing command, exit, task execution lines, before/after source manifest, APK size/digest and immutable log digest. Snapshot outputs before a later build can replace them. Fresh build success is not installed startup.

Inside the shared lock, repository/app/android:

```sh
./gradlew --offline --console=plain   :app:compileFlutterBuildDebug --rerun   :app:compileDebugKotlin --rerun   :app:compileDebugAndroidTestKotlin --rerun   :app:packageDebug --rerun :app:packageDebugAndroidTest --rerun   :app:assembleDebug :app:assembleDebugAndroidTest

./gradlew --offline --console=plain   -Ptarget-platform=android-arm64 -Ptarget=lib/main.dart   -Pdart-obfuscation=false -Ptrack-widget-creation=false -Ptree-shake-icons=true   :app:assembleRelease --rerun
```

These are the actual direct-Gradle release arguments used to keep dependency resolution offline, not an invented Flutter `--offline` option. Gradle is incremental: assembly's `--rerun` does not force every prerequisite. D's debug command explicitly forced compilation/packaging; release provenance includes the retained same-source compilation/minification chain and final retry4 packaging. Require task lines for whatever freshness is claimed.

On duplicate/generated-output failures, retain the failed log and inspect only exact implicated paths, canonical counterparts, hashes (if resident), `stat` DATALESS flags and `git check-ignore`. Move only proven implicated generated files with exclusive preservation manifests; never source, protected originals or broad directories. A DATALESS file cannot supply an honest content hash. The observed external move of a DATALESS SO timed out; a same-provider move preserved the original inode/size/flags. Do not invent byte equality or claim its cloud/provider origin is established. D's first metadata-preservation assertion failure and its recovery are intentionally retained. Reinspect rebuilt APKs because a successful build can still package rejected suffixed entries.

The accepted inspector requires explicit independent expectations:

```sh
# repository; read-only stdout, no output overwrite
/opt/homebrew/bin/python3.11 -B -E benchmarking/inspect_release.py   --repo-root "$PWD"   --expectation benchmarking/study_evidence/20261015/d/current-release-expectation.json   --apk app/build/app/outputs/flutter-apk/app-release.apk
```

This exact expectation binds the October18 release digest; it is not a mutable policy for a different future APK. Future expectations must use protected source asset digests, independently captured build-run APK digests and an explicitly declared ABI expectation. Never learn expected model/label hashes from the APK under test. D's current debug expectation uses native path membership from the preserved pre-build APK; release retains C1's historical three-ABI native list. `current-release-strict-arm64-expectation.json` intentionally rejects this release. No ABI configuration policy was newly approved.

`d/inspect-current-artifacts.py` is the actual composition: ZIP CRC, independent five-asset hashing, all native versus Flutter/library ABI inventories, exclusive external artifact snapshots, accepted inspector results and actual build/source/log association. It creates exclusive outputs and is **not** safe to rerun verbatim into its existing targets. Inspector-only `current_source_build_provenance=false` is intentional: the separate actual build records, not an expectation label, establish host build-run provenance. Neither proves signatures, ELF compatibility, installation or runtime behavior. Test APK has no embedded model/native requirement.

## Current accepted native handoff

Read `controller/a3a-acceptance-and-consumer-binding.json`. Use only run `323291af-c067-46dc-bae1-067d62fab10b` and manifest SHA256 `3279cb7d01075a9192f2566ae5573dd6137a23c6710ef1d0a590b78564fe0fed`, with the named successful producer XML/ledger. Equal source hashes from another run do not establish execution identity.

```sh
# repository; verified read-only again in D
/opt/homebrew/bin/python3.11 -B -E benchmarking/host_fixture_replay.py preflight
```

The preflight checks42 source/11 artifact bindings and accepted producer evidence. Flutter consumes verified bytes through a trusted local interpreter/stdout snapshot and explicitly mocked transport. Native SQLite/export/clear/reopen, Flutter rendering/ACK and Python reader/history are separate processes. Do not claim an installed uninterrupted session, hostile-filesystem attestation or independent hardware verification.

## Historical artifacts versus current-source verifiers

B1 external generated campaign: `../kumpas-data/parity/20261017-validation-v1`, manifest SHA256 `1cca1526355e9d4ce6c41102a0a6fa474a15dd77bbac2b09daee1ec85e70c452`. Six fixtures/180 PNGs remain historical outputs. Their comparator hash is intentionally the **before-follow-up** source `cc905b5494e1fe78d7c4d3de3bcf05772499946538d42f404f17acad3c43d93d`; its exact snapshot is `followups/before/benchmarking/pipeline_parity.py`. Current arithmetic hardening is a different accepted postimage. Do not rebind the old selection or regenerate outputs to hide drift.

B2 retained run: `../kumpas-data/diagnostics/20261017-validation-v1-3`; `campaign.json` SHA256 `5dead49dd2257df34af9242f623f82345b6108ed9b66e2fda5837c3b9b0c77d0`; `INCOMPLETE-manifest.json` SHA256 `013f3933fe898dadf2fc25fcf7a12cc50689964f7fba39400cba38e0199b497d`. The executed `b2/current-inputs-v3.json` binds the old helper **and old test file**, before review hardening. Exact snapshots are `b2/review-fix-1-before-validation_campaign.py.txt` and `b2/review-fix-1-before-test_validation_campaign.py.txt`; comparator role uses the B1 before snapshot. Check every source role, not just the helper, against the appropriate historical bytes. Current helper/test hashes come from B2 bounded acceptance; current comparator/tests from October18 follow-up acceptance. Leave historical config, run identity and missing134 source records unchanged.

Safe, read-only repeat of the checks actually executed by D:

```sh
/opt/homebrew/bin/python3.11 -B -E benchmarking/study_evidence/20261015/d/readback-history.py --check-only
```

This checks generated PNG/reference/fixture digests, B2 recorded outputs/config/incomplete binding, all13 historical source-code roles and current accepted repaired sources. It refuses DATALESS generated artifacts before opening them and never opens original raw videos or NPZs. It does not perform inference, rebuild source metadata, retroactively preregister a capture, or create a successful full-source manifest. Stored144/150 validation results per model are retained diagnostics, not untouched final-test or signer/generalization evidence.

**Do not run** B1's old `verify_evidence.py --check-only` here: despite its old handoff recommendation, it expects current hashes to equal historical tool hashes and also opens original video/NPZ sources. B2's old whole-input verifier similarly cannot be substituted for safe readback when source-bound helper/tests have intentionally changed. The old follow-up `audit.py` also expects historical APK paths to retain old bytes; after fresh builds those bytes belong to the external historical snapshot. A current-source mismatch is not permission to rewrite historical execution identity. No raw-dataset hydration/download is authorized.

## Blank physical-study handoff and remaining gates

Reuse, do not fill or overwrite: `benchmarking/handoff_blank/candidate_devices.csv`, `condition_runs.csv`, `sign_trials.csv`, `confusion_matrix.csv`, `generation_checks.json`. `benchmarking/generate_handoff.py` already exists and refuses nonempty output directories; any newly authorized generation needs a new empty directory. Candidate device labels do not establish ownership, hardware verification or measurements.

Read `benchmarking/environment_protocol.md` for the app-private `files/benchmarks/next_setup.json` schema, immutable start-time snapshot, actual APK identity, structured camera representation and control-companion qualification. Do not provision it or run device transport in this host-only scope. Hardware identity, chip verification, lighting/lux, camera/configuration, dates, signers/trials and sign-offs remain unmeasured/blank. Before physical work obtain explicit device/install/store authorization, actual hardware and setup evidence, and the approved all-sign/three-condition protocol. Interpreter timing cannot substitute for physical camera-to-display latency.

Human rubric, ten-sign selection, rater/blinding/adjudication, missingness, group joins/control participants, consent/withdrawal/retention, questionnaire wording and statistical decisions remain separately approval-blocked. The drafted four0–3 dimensions and proposed t/Wilcoxon/Mann–Whitney/Cohen's-d methods are not approved scoring/analysis. No real-data mode, inferred consent, fabricated participant record or automatic promotion is supplied by this handoff.

Parent next action: verify final source/protected/APK/log hashes and exact suite counts, review complete dirty tracked changes plus every new source/test/document in `d/review/`, obtain whole-package spec and quality verdicts, resolve findings, then record only the bounded host decision actually supported. Keep this frozen package stable while reviewing; place subsequent status decisions in separate evidence.
