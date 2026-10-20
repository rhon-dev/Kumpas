# B1 host parity completion

Status: IN PROGRESS. Host-only task06; parent independent verification/review required.

## Scope and baseline
Read binding task brief, discovery/model-host-audit.md, approved design/plan, existing Python comparator/tests and actual Android PipelineParityTest producer. No app/native/consumer changes authorized. Existing unrelated dirty worktree retained. Historical Python schema is kumpas-feature-reference-v1; native schema is kumpas-android-replay-v1. Neither contains clip identity. New campaign identity must use a versioned companion binding; historical outputs are not retroactively clip-bound. Native prediction payload is attempt_result, not prediction; B1 will not perform classifier inference.

Command ledger and logs are append-only records of actual execution. Raw PNGs/vectors stay external. No Android/anatomical/expert/accuracy/final-test acceptance follows from host fixtures.

- Executed `import-probe`: exit 0; log `import-probe.log`; command in ledger.

Discovery caveats: an overly broad read-only app-tree hash probe hit macOS TimeoutError (60); abandoned, no app writes. A relative Path parent probe failed FileNotFoundError; rerun with resolved repo succeeded. Import probe with -E succeeded; no installs. Will verify native/app preservation using exact accepted binding paths rather than broad generated trees.

- Executed `red-digests`: exit 1; log `red-digests.log`; command in ledger.

- Executed `green-digests`: exit 0; log `green-digests.log`; command in ledger.

- Executed `red-types`: exit 1; log `red-types.log`; command in ledger.

- Executed `green-types`: exit 0; log `green-types.log`; command in ledger.

- Executed `red-binding`: exit 1; log `red-binding.log`; command in ledger.

- Executed `red-binding-assertions`: exit 1; log `red-binding-assertions.log`; command in ledger.

- Executed `green-binding`: exit 0; log `green-binding.log`; command in ledger.

- Executed `red-reference-paths`: exit 1; log `red-reference-paths.log`; command in ledger.

- Executed `red-reference-existing-escape`: exit 1; log `red-reference-existing-escape.log`; command in ledger.

- Executed `red-prepare-memory`: exit 1; log `red-prepare-memory.log`; command in ledger.

- Executed `green-reference-memory`: exit 0; log `green-reference-memory.log`; command in ledger.

- Executed `red-campaign-freeze`: exit 1; log `red-campaign-freeze.log`; command in ledger.

- Executed `green-campaign-freeze`: exit 0; log `green-campaign-freeze.log`; command in ledger.

- Executed `red-campaign-generate`: exit 1; log `red-campaign-generate.log`; command in ledger.

- Executed `red-detector-counts`: exit 1; log `red-detector-counts.log`; command in ledger.

- Executed `green-detector-counts`: exit 0; log `green-detector-counts.log`; command in ledger.

- Executed `green-campaign-generate`: exit 0; log `green-campaign-generate.log`; command in ledger.

- Executed `full-benchmarking`: exit 1; log `full-benchmarking.log`; command in ledger.

- Executed `red-strict-cli`: exit 1; log `red-strict-cli.log`; command in ledger.

- Executed `green-strict-cli`: exit 0; log `green-strict-cli.log`; command in ledger.

- Executed `full-benchmarking-compatible`: exit 0; log `full-benchmarking-compatible.log`; command in ledger.

- Executed `focused-campaign-final`: exit 0; log `focused-campaign-final.log`; command in ledger.

- Executed `generate-six-validation`: exit 0; log `generate-six-validation.log`; command in ledger.

- Executed `verify-six-protected`: exit 0; log `verify-six-protected.log`; command in ledger.

- Executed `python-reference-tests`: exit 0; log `python-reference-tests.log`; command in ledger.

- Executed `diff-check`: exit 0; log `diff-check.log`; command in ledger.

- Executed `coverage-equal-invalid`: exit 0; log `coverage-equal-invalid.log`; command in ledger.

- Executed `full-benchmarking-final`: exit 0; log `full-benchmarking-final.log`; command in ledger.

## Final B1 outcome — DONE_WITH_CONCERNS (parent verification/review pending)

Implemented regression-first fail-closed paired-frame validation, preserving actual Python/native v1 schema names. Missing/equal malformed SHA256 fields no longer pair; exact sequential nonnegative integer indices exclude booleans; finite 258-number features exclude booleans and overflowing integer conversion; malformed schemas/documents/rows/presence values fail with fixed safe errors before array arithmetic. Existing PNG mismatch, missing frame, dimension and presence controls retained. Later equal-invalid-input cases are coverage-only GREEN, not additional claimed repairs.

New `fixture_binding` uses explicit `kumpas-clip-binding-v1` rather than inventing clip fields in historical bytes. `compare_vectors(..., require_clip_binding=True)` is the strict bound boundary. CLI `compare` requires binding by default; `--legacy-frame-only` deliberately enables recorded historical diagnostics tagged `unbound_legacy_frames_only`. Neither mode establishes anatomy. Actual Python references have no class result; native `attempt_result.predictedLabel` is not an equivalent Python prediction. Arbitrary `prediction` object equality was removed; output explicitly says `not_evaluated_feature_only`.

Added external-only `parity_fixtures.py`: verifies six current protocol validation memberships against actual dense/source labels, source/NPZ hashes and NPZ class/split; freezes all selections before extraction. A new exclusive campaign has `INCOMPLETE` until all six named outputs and PNG digests validate. Output escapes/symlink ancestors and reuse are rejected. Per-clip new bindings/fixture manifests capture video/PNG/source indices/FPS/decoded count, label map/protocol/selection, extractor and normalization source hashes, Python/package versions, detection counts, finite summaries and explicit sampling/tracking difference. Two-pass video decoding retains only sampled frames; regression measured old retained-frame peak40 vs allowed5 for3 samples. No normalization mathematics changed.

### Executed suites
- Compatible `training/.venv/bin/python -E`: final parity14/14, campaign4/4 (includes actual Holistic on six synthetic32-frame videos), existing Python-reference2/2. No skips in these focused suites.
- Broad `/opt/homebrew/bin/python3.11 -E`: final discovery90 tests, OK with2 explicit dependency skips. That interpreter's installed MediaPipe lacks `solutions`; the initial broad failure is retained in `full-benchmarking.log`. Do not mistake these two skipped detector tests for executed broad-environment passes; both executed successfully in training/.venv. No installs or synthetic replacement results.
- Real sequential six-validation-original extraction: exit0 in `generate-six-validation.log`; 180 PNGs and six real Holistic references, followed by exact read-back verification in `verify-six-protected.log`.
- `git diff --check`: exit0. All82protected hashes match; all42accepted native source hashes and all4A3b consumer bindings match. Existing native manifest digest remains pinned. No app/native/Dart/consumer/normalization/model/reference source changed.

### RED/GREEN record classification
- `red-digests`→`green-digests`: seven equal missing/malformed digest failures repaired.
- `red-types`→`green-types`: real schema/bool/type validation failures and unsafe exceptions repaired; already-rejected cases are coverage-only.
- `red-binding-assertions`→`green-binding`: missing explicit identity qualification and arbitrary prediction equality repaired. Earlier `red-binding` includes missing-result-key error; corrected assertion run retained.
- `red-reference-existing-escape` and `red-prepare-memory`→`green-reference-memory`: existing traversing PNG accepted and retained-frame peak40 repaired. Earlier missing-path probe error retained, not counted as behavioral RED.
- `red-campaign-freeze`→`green-campaign-freeze`: new public campaign CLI feature; absence was observed through actual subprocess nonzero exit. Invalid-input tests only became meaningful once the valid control passed.
- `red-campaign-generate`→`green-campaign-generate`: explicit unimplemented extraction failure repaired; real synthetic video references generated.
- `red-detector-counts`→`green-detector-counts`: actual detector count output missing, now preserved.
- `red-strict-cli`→`green-strict-cli`: unbound default CLI previously returned success, now rejected unless historical mode explicit.

### Environment / execution caveats
Existing training environment imported NumPy2.4.6/OpenCV5.0.0/MediaPipe0.10.14 successfully with -E. Holistic emitted actual MediaPipe feedback-manager and protobuf deprecation warnings; retained, not treated as recognition failures. Early synthetic tempfile tests used the process default temp root before discovery showed it differed from the declared scratch; runner now sets the session scratch TMPDIR explicitly, and final tests used it. Broad app-tree read-only hash attempt hit an iCloud/macOS timeout; it was abandoned in favor of exact accepted binding checks. No participant stores were accessed.

### Boundary / next owner
This finishes prepared host task06 references, not Android parity. No Android output/runtime was produced; self-comparisons in generation/verifier are structural validation only and no self-comparison report is published as parity evidence. Future authorized Android replay requires an independently verified exact replay/output binding; do not simply copy the Python binding onto unknown native bytes. Historical native documents remain unbound.

The stored full-video normalization/resampling versus sampled-PNG re-detection deltas are different tracking paths, NOT normalization bugs, anatomical judgments or classifier accuracy. No expert labels, current phone performance, signer independence, human outcomes, participant authorization or final-test gate closed. No classifier inference, training/export/deploy, installs, ADB/emulator or commits. B2 provenance/inference/training tooling remains separate. Parent must independently verify artifacts/source/test deltas and obtain spec/quality review before task06 acceptance.

### External outputs and safe aggregate evidence

Campaign: `/Users/ahronjanl.rafaelahron.0804icloudcom/Documents/Thesis/kumpas-data/parity/20261017-validation-v1`; final manifest SHA256 `1cca1526355e9d4ce6c41102a0a6fa474a15dd77bbac2b09daee1ec85e70c452`; selection SHA256 `bc7bb2bd85359cc7242ecfb4bba84e267303c911061a0c1a8fa8ce9c980bf8ad`. All clip directories contain `frames/manifest.json`,30PNGs,`python-detection-v1.json`,`python.json`,`binding.json`,`fixture.json`. Repository `verification.json` contains only aggregate summaries/hashes, not vectors/media.

| Clip | Sampled pose/face/left/right counts | Fixture manifest SHA256 |
|---|---|---|
| `clips_22_14` | 30/30/0/7 | `f8c1fe475e51d8818e6cfe5b7a531bed93029bf7a2172bca6ef10c23c7ca85a0` |
| `clips_22_8` | 30/30/0/8 | `972ce96ffb56a197f130014cf03647c2367547f9e10a1e6d8bc8e3064a1ba535` |
| `clips_22_9` | 30/30/0/8 | `746cf075eb9686ca262d028415b09cb04e6bf38e7789bdb4f816966dfd01defb` |
| `clips_24_10` | 30/30/0/8 | `ec4799fc6e813f6ec6514d6e15fe2942598a51794ae68a6426f6dc96cc03b9d6` |
| `clips_24_11` | 30/30/0/8 | `a115b857ec53355d0709ad825980e427f70d649ce49b9d4d7ddbff70c0e4e3af` |
| `clips_24_18` | 30/30/0/10 | `babb24951ebdf3c05c7cb67313a9ce1eaa9233a6fe048419254758aae0268d24` |

Changed source/test paths: `benchmarking/pipeline_parity.py`, `benchmarking/test_pipeline_parity.py`, new `benchmarking/parity_fixtures.py`, new `benchmarking/test_parity_fixtures.py`. All other task writes are new files under this b1 evidence folder or the new external campaign.

- Executed `final-readback`: exit 0; log `final-readback.log`; command in ledger.

- Executed `final-diff-check`: exit 0; log `final-diff-check.log`; command in ledger.

### Final read-back / handoff
`final-readback.log` reran all six output/PNG/source/82protected/42native/4consumer checks with exit0. `final-diff-check.log`: exit0. Parent can repeat read-only checks with `training/.venv/bin/python -E benchmarking/study_evidence/20261015/b1/verify_evidence.py --check-only`; no existing evidence is overwritten. Exact four source/test hashes are frozen in `handoff.json`. Final broad log is `full-benchmarking-final.log` (90run,2dependency skips); final same-invalid input coverage is `coverage-equal-invalid.log` (14passed). Global current-profile kumpas-study-readiness procedural skill was also updated with reusable actual-Holistic-API probing/external fixture binding/scratch-TMPDIR lessons; no other profile changed.

- Executed `parent-parity-1`: exit 0; log `parent-parity-1.log`; command in ledger.

- Executed `parent-campaign-1`: exit 0; log `parent-campaign-1.log`; command in ledger.

- Executed `parent-readback-1`: exit 0; log `parent-readback-1.log`; command in ledger.
