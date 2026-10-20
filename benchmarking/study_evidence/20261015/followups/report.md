# Host follow-up execution report

This is the authorized narrow implementer record for B1-R1, C1-Q1 and C2-L1. Parent owns review and acceptance. Scope is four named files only: the parity comparator and its tests, release-inspector tests, and export-CLI tests. No generator, model, native, training, normalization or accepted record changes are authorized.

## Before editing B1-R1

Read the PRD, phase gates, approved host completion design/plan and all three complete reviewer reports. The B1 issue requires a behavioral failing regression for finite subtraction/reduction overflow before production changes. The repair must reject arithmetic nonfiniteness with a fixed safe message and strict JSON, without clamping or changing normalization. Preserve the accepted comparator bytes and historical fixture source identities. C1 and C2 are coverage-only GREEN additions, not defect repairs.

Before edits, capture source snapshots, protected/native/consumer bindings and pre-existing inventory with resident-file checks. Original six fixtures and 180 PNGs are read-only; no regeneration or rebinding. Historical C1/C2 source-bound evidence remains historical when tests change. Tests use existing Python 3.11 with -B -E and scratch TMPDIR; compatible Holistic tests use the existing training environment if needed. No real participant stores, devices, installs, training, inference, conversion or deployments are exercised.

## B1-R1 executed repair and C1-Q1 next slice

`b1-red.log` records genuine behavioral RED: three methods ran; the ordinary/large-finite control passed while six library subcases returned normally instead of rejecting, and six actual CLI subcases exited zero with overflowing reports (12 failed subtests). Finite subtraction, single-frame block mean reduction, and cross-frame block mean aggregation were each exposed in strict and explicit legacy modes. `b1-green.log` records the focused suite after local NumPy overflow/invalid trapping, finite-result checks, and strict compare-CLI serialization/fixed JSON failure. No numerical clamping or normalization change was made.

The initial capture attempt safely stopped before reading a DATALESS executable inside benchmarking/.venv. It made no source edits or hydration. The corrected capture excludes environment/cache trees, includes the prior C2 file allowlist, and succeeded in `before-capture.log`; accepted comparator bytes are retained under `before/benchmarking/pipeline_parity.py`.

C1-Q1 now begins as coverage-only GREEN. Persist three separate deterministic faults at the production publish seam: second fsync after final link; one-byte partial write followed by an exception; final-target open failure. Assert owned final/stage cleanup and preservation of pre-existing sibling/final sentinels. No C1 production edits are authorized or needed.

## C1-Q1 result and C2-L1 next slice

`c1-coverage-green.log` is the first execution of the three new persistent methods against unchanged inspector production code. All passed; this is durable coverage of existing correct behavior, not RED or a repaired C1 defect. The probes confirm exact fault reachability, cleanup of only acquired output/stage, and preservation of pre-existing stage/completed-output sentinels.

C2-L1 now begins as two coverage-only GREEN methods. Change the input pathname only after snapshot/validation and confirm the published manifest hashes the original bytes used in the report. For cleanup, complete owned manifest acquisition, rename and retain that inode, create a different-inode unowned sentinel at the canonical manifest pathname, then fail and verify the sentinel remains. No C2 production edit is needed or authorized.

## C2-L1 result and final verification

`c2-coverage-green.log` ran 10 CLI methods with no skips or failures. Both new methods passed on their first execution against unchanged production code: the report/digest uses original input snapshot bytes after pathname replacement, and cleanup preserves the different-inode replacement manifest while the displaced owned inode remains retained. These are coverage-only GREEN, not manufactured regressions or defect repairs.

The actual compare subprocess matrix rejects finite subtraction overflow, single-frame reduction overflow and cross-frame aggregate reduction overflow in both strict bound and explicit legacy modes, with fixed JSON `{"ok": false, "error": "comparison_failed"}`, nonzero exit, empty stderr and no nonfinite JSON tokens. Rejections leave absent output absent and retain existing sentinel output. Ordinary and representable large-finite controls succeed, including identical 1e308 operands and the single-frame 1e306 control whose four-frame aggregate overflows. Native replay schema and clip-binding/legacy semantics are unchanged. The comparator traps NumPy overflow/invalid locally and checks result finiteness; successful compare output is serialized with `allow_nan=False` before the output file is opened. This is numeric-input/report rejection, not an atomic-I/O or hostile-filesystem publication guarantee.

Executed suite results (overlapping executions are not summed):

| Evidence | Run | Passed | Skipped | Result |
|---|---:|---:|---:|---|
| B1 behavioral RED | 3 methods | ordinary control passed | 0 | expected failure: 12 failed subtests across library/CLI rejection methods |
| B1 focused GREEN, general Python | 17 | 16 | 1 | exit 0 |
| C1 focused coverage GREEN | 31 | 31 | 0 | exit 0 |
| C2 focused coverage GREEN | 10 | 10 | 0 | exit 0 |
| Final broad benchmarking, general Python | 124 | 122 | 2 | exit 0 |
| Broad evaluation | 18 | 18 | 0 | exit 0 |
| Final compatible parity plus synthetic campaign | 21 | 21 | 0 | exit 0 |

General Python is `/opt/homebrew/bin/python3.11 -B -E`. The two broad skips explicitly report that its MediaPipe lacks Holistic `solutions`; they are not detector passes. The separate final `training/.venv/bin/python -B -E` execution passed all 21 parity/campaign methods, including the real detector on newly created synthetic inputs only. It did not regenerate the accepted six real validation fixtures. Every execution inherited the explicit Hermes scratch TMPDIR. The initial broad command with `-t .` failed discovery before running tests because benchmarking has no importable package initializer; the corrected established `-s benchmarking` invocation and final repeat both passed. The failed log is retained. No dependency installations occurred.

## Preservation and immutable historical identities

`before.json`, `after.json`, `historical-identities.json`, `summary.json` and their actual logs are the machine-readable evidence. There are 2,730 captured inventory entries representing 1,598 distinct pre-existing paths (relative/absolute aliases are retained from the prior allowlist). Comparing all entries except the four authorized source paths yielded zero mismatches. All 82 protected originals, 42 native producer sources and 4 A3b consumers match their accepted hashes. All pre-existing tests/logs/configs/reports under the inventoried scopes remain unchanged except the expressly authorized three test files. Current accepted B2 source hashes match; six historical B2 output digests plus its campaign and incomplete manifest match, without rerunning inference. All three historical debug/test/release APK hashes match the prior parent artifact record. APK/B2 checks are readback against historical expectations, not new build/inference provenance.

The original B1 completion manifest remains `1cca1526355e9d4ce6c41102a0a6fa474a15dd77bbac2b09daee1ec85e70c452`, selection remains `bc7bb2bd85359cc7242ecfb4bba84e267303c911061a0c1a8fa8ce9c980bf8ad`. All six fixture manifests/references, 180 PNGs and declared outputs match their historical hashes. The saved accepted comparator is `before/benchmarking/pipeline_parity.py`, SHA256 `cc905b5494e1fe78d7c4d3de3bcf05772499946538d42f404f17acad3c43d93d`. Its exact bytes, not the repaired runtime, remain the original generation identity. Readback with the repaired comparator is a structural self-check only, not new generation or native parity.

The expected old verifier binding drift is exactly `benchmarking/pipeline_parity.py`: historical `cc905b5494e1fe78d7c4d3de3bcf05772499946538d42f404f17acad3c43d93d`, current `d9d1e4ba4a938b080cd408936f978a166dc19bf7eab1ee4a56c18e875a6342b4`. `b1/verify_evidence.py:56` would reject that current-checkout source comparison after this authorized change. It was not invoked because it also reads original NPZ/video sources; the safe audit verified fixture bytes and source roles without those reads. No historical manifest/config was retrofitted. C1/C2 parent source-role hashes independently match the saved before snapshots for their changed tests and current unchanged bytes for every other role; `summary.json` retains both historical and new identities.

## Final source postimages and handoff

Only these four repository source/test files were modified; all new working evidence is under this followups directory. Complete exact before/after source snapshots and `source.diff` are included. `git diff --check` exited 0; all four postimages parse and have no trailing whitespace.

| Source | SHA256 |
|---|---|
| `benchmarking/pipeline_parity.py` | `d9d1e4ba4a938b080cd408936f978a166dc19bf7eab1ee4a56c18e875a6342b4` |
| `benchmarking/test_pipeline_parity.py` | `73d9c465ade5ca177619371a8cc6b62a9639e34ffee63faca30aa1d20ce24c25` |
| `benchmarking/test_inspect_release.py` | `75ae48ac36ccc1a753260aafd660998ea5b5fab53f8512cc16d046fd448d1498` |
| `evaluation/test_export_cli.py` | `66640847482f3421ffdc90e2912e7bdcd0963127a14bc66c8aba7dae0eb3fa43` |

Disposition: implemented and host-verified, pending parent independent testing and complete four-file review. No unresolved implementation blocker was found. The historical current-source verifier drift is intentional and disclosed, not repaired by altering accepted evidence. No accepted record or parent progress file was updated. No real participant store, devices/ADB, downloads/installations, cloud hydration, real inference/conversion, training, deployment, commits/reset/stash/worktrees or model/app/native changes occurred. Physical, anatomical/linguistic, full-source B2, human/research and participant-authorization gates remain unchanged.
