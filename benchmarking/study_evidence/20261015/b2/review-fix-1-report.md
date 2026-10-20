# B2 review repair 1 — incremental evidence

## Scope and status at start

Authorized repairs: B2-R1 selection identity/policy string schema and B2-R2 exact integer protocol counts, exclusively in `training/models/validation_campaign.py` and `training/tests/test_validation_campaign.py`. Read binding task brief, full `controller/b2-review-1.md`, PRD and phase gates; loaded study-readiness, test-driven-development and receiving-code-review.

Work is regression-first, one finding at a time. Fresh synthetic tests and broad training tests will use the existing `~/.kumpas-venvs/tf/bin/python -B -E`, scratch TMPDIR and exclusive logs via existing `b2/run_command.py`. Evidence appended below after execution; no acceptance claim at start. Parent verification and independent re-review required.

Preserve old campaign bytes, v3 config/source identities, all protected/historical sources, native/A3b/B1 bindings, accepted campaigns and prior logs. No real inference, source-media access/hydration, test-row loading, training, real conversion/export, installation, device/default-store operations or Git state changes. Broad tests may execute isolated synthetic conversion. Existing 150+150 predictions remain historical incomplete-source diagnostics; 134 missing source records keep source-provenance acceptance BLOCKED. Newly hardened helper source is not the source identity of the old inference.

## Initial review postimages (to verify before edits)

- helper: `bc7c342a768334c3f0c640451af11b05f2839f23c0ea9ce5736512a2a9998019`
- tests: `4fdae28615d80488ca6d313e1d15f15585e0de45ecc9cb50b9df5247af0381f8`

## Execution record

### Preservation start and R1

`review-fix-1-preservation-before.log` exited 0: initial288, protected82, native42, A3b4, B1source4 and B1 manifest all matched. The original288 baseline contains neither authorized helper/test, so no exclusions are needed. Captured 279 prior B2/B1/diagnostic evidence files plus append-only ledger prefix in `review-fix-1-preservation-before.json`; original helper/test bytes saved in `review-fix-1-before-*.txt`. DATALESS checked before hash reads; no NPZ/video opened.

Inspected actual frozen fields: run ID `20260930_153819_protocol_v1_no_face_baseline`; selection method `highest validation accuracy; macro-F1 then run ID tie break`; test status `exploratory: existing FSL-105 test was consulted by historical runs`. No UUID or new selection/promotion-policy constraint added.

R1 synthetic regression edits each `run_id`, `selection_method`, `test_status` independently to object/list/bool/int/float/null/empty/whitespace, rebinding freeze and candidate provenance hashes and run identity. Positive controls use the ordinary fixture and exact historical strings. Public `validate_inputs` and CLI `main(argv)` boundaries exercised; CLI uses real parser/config digest validation with metadata/predictor spies (not real inference).

- `review-fix-1-r1-red.log`: 1 test, 36 expected failing subtests, exit1 (18 malformed truthy/whitespace controls accepted by public validator; corresponding CLI controls reached metadata and returned INVALID_CLIP_METADATA rather than INVALID_CONFIG). Null/empty controls already rejected: coverage-only, not claimed RED.
- Minimal helper repair: require exact string type and non-whitespace content for all3 fields before inherited selection validation; preserve accepted strings unchanged.
- `review-fix-1-r1-green.log`: 1 test passed, zero failures/errors/skips, exit0. All24 malformed controls rejected by validator and by both normal and explicit incomplete-source CLI modes before metadata/prediction; no output directory created. Historical-string controls passed.

### R2

Inspected protocol builder/validator: count fields are `n_fit_original`, `n_validation`, and `class_counts[class_id][partition]`; seed/fraction are not count fields and remain unchanged. Actual manifest has integer663/150 and integer per-class counts.

The synthetic fixture accepts an optional originals-per-class argument (default4 unchanged). A three-original/class control reconstructs true counts fit1/validation2, top-level2/4: this proves bool `True` is rejected for a genuine count1, rather than merely rejecting its wrong numeric value. Each of6 count locations is independently replaced with equal float, True, False, string, null, object, list, negative integer and wrong positive integer; manifest, selection and provenance digests rebound. Exact integer controls pass before/after.

- `review-fix-1-r2-red.log`: 1 test, 16 expected failing subtests, exit1. Six numerically equal floats and two nested True==1 aliases were accepted by validator and reached CLI metadata (8 public and8 CLI failures). Other malformed/wrong numeric controls already rejected and are coverage-only.
- Minimal helper repair requires exact built-in int for both top-level counts and every nested class-count value, with dictionary container guards, before inherited reconstruction/equality. No coercion or new numeric policy.
- `review-fix-1-r2-green.log`: 1 test passed, zero failures/errors/skips, exit0. All54 malformed controls rejected at public validator and both CLI modes before metadata/prediction, no output directory; integer controls pass.

## Fresh verification and final disposition

**Findings reproduced and repaired in the exercised scope; pending independent parent verification/re-review. Full-source provenance remains BLOCKED.** No claim of study, physical, promotion, anatomy, signer-independent or final-test acceptance.

| Exclusive log (all under this `b2/` directory) | Result |
|---|---|
| `review-fix-1-focused.log` | 13 tests, zero failures/errors/skips, exit0 |
| `review-fix-1-training-full.log` | 29 tests, zero failures/errors/skips, exit0 |
| `review-fix-1-diff-check.log` | `git diff --check`, exit0 |
| `review-fix-1-preservation-after.log` | verifier assumption failure, exit1: v3 also binds the test source, not only helper; no campaign/source changes |
| `review-fix-1-preservation-after-retry.log` | corrected verifier requires exactly both authorized postimages; all preservation assertions pass, exit0 |
| `review-fix-1-historical-identities.log` | old v3/campaign/manifest identities and150/134 counts read back, exit0 |

Full training discovery executed the protected isolated **synthetic** model save/conversion test. Its retained log contains existing Keras numpy-copy deprecation, TensorFlow converter/deprecated Interpreter and backend informational warnings; tests passed, but output is not warning-free. No real checkpoint inference/conversion or test-array rows loaded. Targeted CLI regressions call public `main(argv)` in-process with real argparse/config digest validation and patched metadata/predictor; they are not standalone subprocess runs or physical/backend evidence. Existing subprocess malformed-JSON CLI tests also ran in both fresh suites.

Reproduction commands from repository root (use a fresh unique runner tag on repetition; never overwrite logs):

```sh
P="$HOME/.kumpas-venvs/tf/bin/python"
R=benchmarking/study_evidence/20261015/b2/run_command.py
"$P" -B -E "$R" NEW-UNIQUE-TAG "$P" -B -E -m unittest discover -s training/tests -p test_validation_campaign.py -v
"$P" -B -E "$R" ANOTHER-NEW-UNIQUE-TAG "$P" -B -E -m unittest discover -s training/tests -v
```

The runner sets `TMPDIR=$HOME/.hermes/cache/scratch` and `PYTHONDONTWRITEBYTECODE=1`; every invocation used the existing TF interpreter with `-B -E`. RED reproduction source is preserved as before postimages; source diff and new test names describe the executable regression. Do not replace live sources just to reproduce RED during review; use isolated temporary copies if needed.

### Preservation and new review identities

Fresh streaming readback: **288 initial,82 protected,42 native,4 A3b,4 B1 source bindings, accepted B1 manifest, and279 prior B2/B1/external diagnostic artifacts** all match their pre-edit baselines (overlapping sets, not additive). Ledger prefix unchanged, only appended. DATALESS checked before preservation/input hash reads. No real source NPZ/video content read/hydrated. Real test arrays were streamed only for declared digest verification, never loaded as rows.

The current v3 input graph has33 roles:31 still match current files; `source_code_0` and `source_code_1` intentionally bind **historical helper/test postimages**, not this hardening. The initial preservation attempt incorrectly expected only the helper role to differ; the retained failure and corrected exact-two-path assertion document this verification correction. No input config, manifest, source hash or campaign was rebound to retrofit this repair to historical inference. The original288 baseline includes neither authorized additive file; there were no excluded baseline mismatches.

| New source/postimage | SHA256 |
|---|---|
| `training/models/validation_campaign.py` | `8e28d5ad110b76881e65d75e1e851ecb71fa2a6e21e232bc2d0a7fe8cea22998` |
| `training/tests/test_validation_campaign.py` | `5d9f2e13f0896b36940fdd81384ee6db9c2708417edcfce5e8064eefe019fe46` |
| `review-fix-1-source.diff` | `2f54b74c1a8ea58ae167f3be0f39f790faf5684c56189750a5e926b0df21cc07` |
| `review-fix-1-preservation-after.json` | `9a93367d34115acbf374e690eb84a538f58dec5c6f9836410661bed3968695bb` |

`review-fix-1-preservation-after.json` also contains exact test-log SHA256s and parsed counts. Before/after snapshots are `review-fix-1-{before,after}-{validation_campaign.py,test_validation_campaign.py}.txt`; baselines and all prior artifact hashes are in `review-fix-1-preservation-before.json`. New evidence consists of this report, these4 snapshots,2 preservation JSON files, source diff and the exclusive `review-fix-1-*.log` files; existing `command-ledger.jsonl` appended only. Only the2 authorized source/test files were changed. Scratch verifier exists at `$HOME/.hermes/cache/scratch/b2-review-fix-1-preservation.py` (transient; durable assertions/results are in the JSON/log evidence). Generic regression/provenance lesson added to the active-profile study-readiness skill, outside this repository.

### Historical campaign retained, not reexecuted

External root: `../kumpas-data/diagnostics/20261017-validation-v1-3/`.

- v3 config SHA256: `0df969259b620e64ea0b3ea40484492178dfcb4f719437684af94471c50bb78e`.
- Historical campaign SHA256: `5dead49dd2257df34af9242f623f82345b6108ed9b66e2fda5837c3b9b0c77d0`.
- `INCOMPLETE-manifest.json` SHA256: `013f3933fe898dadf2fc25fcf7a12cc50689964f7fba39400cba38e0199b497d`.
- No successful `manifest.json`; retained150+150 historical predictions are incomplete-source diagnostic evidence only,134 source metadata records missing. These repairs did **not** generate new inference/campaign outputs or independently recompute model predictions. Original historical helper/test hashes remain those listed at report start. Future inference needs separate authorization, new postimages and a fresh exclusive campaign, not rebinding the old execution.

No installs, device/default-store access, training, real model conversion/export/deployment, commits/reset/stash/worktree operations occurred. Parent must independently match these postimages and re-review R1/R2 before accepting the narrow repairs; source-provenance BLOCKED remains independent of that review.
