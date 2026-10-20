# B2 execution report

IN PROGRESS. Additive validation-only diagnostics. No training, conversion, deployment, test-row loading or promotion authorized. Current campaign hashes are not historical preregistration.

## Additive guards — executed vertical TDD
Metric, probability, exact validation-original equality, identity graph, output guard, and NPZ metadata slices each have preserved behavioral RED then GREEN logs and command exits. Current focused suite: seven tests passing. One initial positive-control absence failure and one invalid augmentation-range implementation attempt are retained, followed by corrected behavioral RED and GREEN respectively. Protected selector/exporter unchanged. Derived fit arrays are current-byte bound, finite/shape/label/log checked, not independently regenerated.

## Before real inference
Focused tests:10 passing. Protected+additive training suite:26 passing,0skips (with upstream Keras/TFLite deprecation warnings). TF import succeeded:TF2.19.0,Keras3.15.1,NumPy2.1.3,Python3.11.15. Current config captured after source changes,150 ordered clips,33 explicitly hashed input/source roles; test arrays hashed by streaming only. One capture failed on nonexistent B1 campaign.json; retried using accepted immutable manifest.json only, without changing B1. Actual inference starts after this entry.

## Interrupted attempt / recovery
First actual CLI tool call timed out after420s; retained original directory with INCOMPLETE.json only, no predictions, no campaign manifest and no successful completion. Follow-up process inspection found no surviving validation process. All150 CSV-resolved raw video paths exist (stat only). Added and RED/GREEN tested durable per-clip metadata progress. Captured new config-v2 matching changed additive source, launched a fresh suffix directory with managed background execution; no old outputs overwritten.

## Real source-availability blocker
Managed retry stopped at metadata clip4=clips_10_1.npz. lsof identified that exact NPZ descriptor; native sample showed read() blocked, no TF model loaded. stat reports size1404854,blocks0,flags1073741920;140/150 NPZs have macOS DATALESS flag,10 resident. No replacement references or metadata synthesized. Sent SIGINT only to owned child to retain fixed failure diagnostics. Real150clip model inference can proceed independently from resident validated original arrays, but full source/metadata completeness must remain blocked; preparing a strictly incomplete prediction-only salvage path rather than a success manifest.

Managed retry disposition: actual-validation-v2 exited2 after explicit SIGINT to child51859; generic CLI code CAMPAIGN_INTERRUPTED_OR_FAILED corresponds to intentional interruption of a blocked read of dataless clips_10_1.npz, NOT a TensorFlow inference exception. Shell zle warnings are wrapper-shell noise, distinct from Python interruption. No classifier predictions were generated in v1/v2. Original log/config/output-v2 preserved. Native sample identifies read() blocking; residency manifest lists140 DATALESS NPZ placeholders. Next additive regression enforces source-residency before content reads; an explicit incomplete-source mode will preserve actual array-based predictions without any successful completion manifest or fabricated metadata.

## Actual150clip inference obtained; full-source campaign remains incomplete
Fresh v3 executed150 Keras+150 existing TFLite predictions sequentially on validated originals. Both144/150; actual CLI exit3 deliberately marks INCOMPLETE_SOURCE_METADATA, not inference failure.140 detector-source NPZs nonresident;10 resident clip metadata records retained. No successful manifest.json published: external INCOMPLETE-manifest.json binds actual outputs. Keras loaded successfully with compile=False in existing TF2.19.0 environment, no dependency/model loading blocker or conversion. Source availability prevents full B2 provenance acceptance; outputs are not synthetic or promotion evidence.

Correction based on actual immutable v3 outputs (supersedes preceding estimate):134/150 source metadata records unavailable,16/150 available. Earlier stat-only snapshot was140/150 DATALESS and10 resident; source residency changed between that snapshot and metadata scan (some placeholders hydrated). Completion count must come from v3 records, not the earlier stat snapshot. No fabricated metadata, missing hashes omitted. Source-metadata incompleteness remains blocking; no further inference retries to chase exit0.

## Final disposition: DONE_WITH_CONCERNS — full-source acceptance BLOCKED

This slice obtained the requested **real150 original validation predictions for each frozen model**, with strict additive provenance/metric/probability guards and durable synthetic RED/GREEN evidence. It does **not** satisfy the full150clip source/metadata provenance deliverable: **134 NPZs and their134 raw videos remain macOS DATALESS placeholders**, verified by post-run stat flags. **16/150** clip metadata records are byte-bound/available, including all six B1 FIVE/THREE targets. Missing data are explicitly omitted, not zero-filled or invented.

The default CLI remains fail-closed: SOURCE_NOT_RESIDENT prevents predictions/publication. The separate explicit `--incomplete-source-diagnostics` option retains actual array-based inference under `INCOMPLETE_SOURCE_METADATA`, exit3, and **INCOMPLETE-manifest.json only**. It cannot publish a successful manifest when source metadata are missing. Additional executed coverage verifies the default nonresident failure and that salvage does not swallow malformed metadata or call inference on malformed inputs. No exit0 retry was attempted after obtaining v3.

### Measured validation results (not final-test claims)

| Model | Correct / validation originals | Accuracy | Macro-F1 /50classes |
|---|---:|---:|---:|
| Frozen Keras baseline |144/150|0.96|0.9592380952380953|
| Already exported candidate |144/150|0.96|0.9592380952380953|

Each class has support3. Confusion/per-class matrices across all50classes are external in `summary.json`; stdlib readback independently recomputed all counts, confusion, top1, margins, metrics, per-class denominators and probabilities. No real test array rows/predictions loaded; existing test arrays were streamed solely for CURRENT byte hashes. Protected synthetic training tests exercise only isolated temporary synthetic fixtures (including their existing save/conversion test).

- Top1 disagreements:0/150, matching historical candidate provenance0/150.
- Probability maxabs:0.18056780099868774 versus historical0.18056738376617432; difference+4.172325134277344e-07. Not assumed byte-identical runtime reproduction.
- Probability mean absolute error:0.0003132479067915363 across150x50 cells.
- Max absolute confidence difference:0.18056780099868774; mean candidate-minus-Keras confidence:+0.0006970469156901041.
- Max absolute margin difference:0.3608846217393875; mean candidate-minus-Keras margin:+0.001708345503096401.
- No numerical promotion threshold exists. Promotion remains **diagnostic_not_approved_for_promotion**; stable top1 does not establish probability equivalence, calibration or confidence-dependent safety.

### Error investigation

| Clip | Source class | Dense truth | Label | Both predicted | Metadata |
|---|---:|---:|---|---|---|
| clips_10_1.npz | 10 | 10 | UNDERSTAND | 9 (SEE YOU TOMORROW) | available |
| clips_14_10.npz | 14 | 14 | NO | 15 (YES) | unavailable |
| clips_21_15.npz | 21 | 21 | TWO | 22 (THREE) | unavailable |
| clips_22_14.npz | 22 | 22 | THREE | 21 (TWO) | available |
| clips_23_19.npz | 23 | 23 | FOUR | 1 (GOOD AFTERNOON) | unavailable |
| clips_53_10.npz | 53 | 29 | MOTHER | 33 (GRANDMOTHER) | unavailable |

FIVE is3/3 for both; THREE is2/3 for both, matching the dated validation summary. For all six targets, stored full-video NPZ sequence length244 and uniformly sampled30; sampled pose and face presence30/30, left-hand block presence0/30. FIVE sampled right-hand counts8,7,10; THREE counts7,8,8. THREE14 misclassifies as TWO with7/30 right-hand presence, while correct THREE8/9 have8/30; this tiny observed contrast is a detector-missingness hypothesis, **not a causal explanation or anatomy finding**. Correct FIVE11 has7/30, so low right-hand count alone does not explain errors. Target torso scales have no <1e-4 fallback frames; FIVE minima0.629635/0.625567/0.585989 and THREE minima0.654965/0.637302/0.622972 (rounded displays only). Sequence sampling may omit discriminative phases; no sparse-frame detector rerun or independent anatomy annotation was performed. Four of six global error clips lack source detector metadata, preventing complete error-versus-detector analysis. All50classes remain visible rather than selecting only favorable signs.

### Runtime and failure provenance

Existing interpreter used with `-B -E`:Python3.11.15,TensorFlow2.19.0,Keras3.15.1,NumPy2.1.3. Actual Keras load succeeded using `load_model(...,compile=False)` and direct batch1 `model(...,training=False)`; model released before candidate interpreter. TFLite uses the already frozen candidate, float32 IO, one thread; no conversion/export/deployment. Trainer comment records Keras3.10; runtime drift is disclosed. Upstream TFLite deprecation and Keras array warnings retained, not hidden.

v1 tool timeout420s retained its INCOMPLETE start marker only. v2 managed exit2 retained source/config/log/output; explicit SIGINT interrupted a kernel read blocked on a DATALESS NPZ, before model inference. Native sample/lsof/stat root-cause evidence is summarized in `io-blocker.json`; the shell's `zle` warnings are separate wrapper noise, not inference failure. v3 intentional exit3 preserves all150+150 actual predictions with source-metadata incompleteness. Residency changed between earlier stat140missing and v3 scan134missing, so only v3 counts describe the diagnostic output.

### Verified boundaries and limits

-11 new focused tests pass; final complete training suite27tests pass,0skips, including16protected tests. No protected source/tests/logs/selection modified.
-Append-only command ledger preserves every RED/GREEN/execution exit/log plus timeout diagnosis. `git diff --check`:exit0.
-Independent readback:288 initial file hashes unchanged;82protected,42native-producer source,4A3b source,4B1 source, accepted B1 manifest all match their frozen bindings. Current model/checkpoint/protocol/candidate/input hashes match all33declared roles.
-Derived fit arrays are CURRENT byte-bound, finite/shape/label/augmentation-log checked, not independently reaugmented. NPZ-to-original normalization authenticity is not independently reconstructed; exact validation-original array+label equality is verified. Source CSV/label-map semantics and perclip source/dense identities are checked but are not expert linguistic labels or signer verification.
-Trusted local checkout/process/filesystem assumption remains: path/symlink checks, exclusive files, byte readback and post-execution identity checks are not hostile concurrent filesystem attestation or power-loss guarantees. Failure paths retain incomplete markers. No successful full-provenance manifest has been published for the real run.
-No unseen final-test, signer-independent, expert/anatomical, physical-device or participant-study acceptance; no retraining/tuning/promotion, model assets, installations, devices, default stores, commits or reset.

### New files / reproducibility / review handoff

Production additions: `training/models/validation_campaign.py`; `training/tests/test_validation_campaign.py` only. Evidence scripts: `b2/run_command.py`, `b2/capture_current.py`, `b2/verify_evidence.py`. Safe evidence/config/log/report files remain under this b2 directory; probabilities/vectors/media stay external. `current-inputs.json` and `current-inputs-v2.json` are retained superseded configurations; **current-inputs-v3.json** is the exact executed binding, not a mutable latest alias. Every manifest says CURRENT capture, not historical preregistration.

External current diagnostic root: `../kumpas-data/diagnostics/20261017-validation-v1-3/`.
-Preprediction campaign:`campaign.json`,SHA256 `5dead49dd2257df34af9242f623f82345b6108ed9b66e2fda5837c3b9b0c77d0`.
-Incomplete output binding:`INCOMPLETE-manifest.json`,SHA256 `013f3933fe898dadf2fc25fcf7a12cc50689964f7fba39400cba38e0199b497d`.
-Executed config-v3 SHA256 `0df969259b620e64ea0b3ea40484492178dfcb4f719437684af94471c50bb78e`.
-New helper SHA256 `bc7c342a768334c3f0c640451af11b05f2839f23c0ea9ce5736512a2a9998019`.
-New tests SHA256 `4fdae28615d80488ca6d313e1d15f15585e0de45ecc9cb50b9df5247af0381f8`.

Exact actual CLI is in command-ledger.jsonl (`actual-validation-v3`); it used explicit config hash/output root/output/landmark/raw paths and incomplete-source flag. It must not be rerun into an existing output. Independent parent verification and spec/code-quality review remain required before host08/10 acceptance. To close the full-source gap requires actual availability of the134source NPZ/video pairs and a new separately byte-bound complete campaign; this slice did not synthesize or silently hydrate replacement sources to claim completion.

Final untracked-source whitespace readback:both no-index --check calls returned1 for new-file differences with no diagnostics; initial verification wrapper incorrectly assumed0 and its assertion is corrected here without changing source. Direct trailing-whitespace inspection also clean. Standard tracked git diff --check remains exit0. Source/tests unchanged from actual-v3 binding. Default readiness skill updated with source-residency/incomplete-diagnostic lesson.
