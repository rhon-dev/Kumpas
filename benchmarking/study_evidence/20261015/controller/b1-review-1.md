# B1 independent Model/QA review — round 1

## Verdict

- **Spec compliance: PASS for prepared host task06 references.** The named malformed-input boundaries fail closed; actual Python/native schema compatibility and explicit legacy-versus-bound modes are preserved. The six requested validation originals are present with current source/protocol/label provenance and structurally valid external references.
- **Code quality: PASS WITH NONBLOCKING CONCERN.** One low-severity numerical report-hardening issue is reproduced below. No blocking finding for this bounded campaign. This is not an Android parity acceptance or permission to proceed through research gates.
- **Research acceptance: NOT ESTABLISHED / outside B1.** No anatomical, Android-runtime, recognition-accuracy, expert, signer-independent, physical-performance, human-outcome or final-test acceptance.

Reviewed the binding `b1/task-brief.md`, discovery task06 audit, worker report/handoff, controller diff and parent verification; all four current source/test postimages; actual `PipelineParityTest.kt`; and the read-back verifier. No source, native/model/normalization or historical evidence changes were made. Only this report was written.

## Snapshot and independently executed verification

All paths are relative to the repository unless stated otherwise. The following current SHA256 values were recomputed and match both handoff and parent verification:

| Postimage | SHA256 |
|---|---|
| `benchmarking/pipeline_parity.py` | `cc905b5494e1fe78d7c4d3de3bcf05772499946538d42f404f17acad3c43d93d` |
| `benchmarking/test_pipeline_parity.py` | `1a4e3bb35f05f076166f36489de916d592092266649463fdfc3cbbb64b94b2cc` |
| `benchmarking/parity_fixtures.py` | `993703b492a283692ed678a9cb44b62383c52bd7068974c50bf290dd559c036b` |
| `benchmarking/test_parity_fixtures.py` | `2c165cce0db1f0fad3efbec7abe5c7ade83b9dc01c1b6bae2a09bfb0ccf00656` |

Read-only probes ran in `training/.venv/bin/python -B -E`, exit 0:

1. Executed the existing `b1/verify_evidence.py` through `runpy` with `--check-only`, capturing its output in memory rather than rewriting evidence. It re-read all six references, 180 PNGs, replay/output/source digests and protected bindings: **82 protected, 42 native-source and 4 consumer hashes matched**, with no protected mismatches. `INCOMPLETE` is absent.
2. Independently loaded the current protocol manifest, label map and protocol selection; recomputed all three hashes against the frozen selection; checked each selected original's unique row, validation partition, dense class, original index and source-label mapping. **All six matched.** Exact originals: `clips_22_14.npz`, `clips_22_8.npz`, `clips_22_9.npz` (THREE), and `clips_24_10.npz`, `clips_24_11.npz`, `clips_24_18.npz` (FIVE). No global source/dense-ID equivalence was assumed.
3. Exercised four equal-invalid document controls at the public strict comparator: null digest, boolean index, boolean feature and integer presence flag. **All four rejected with ValueError.** Also executed the finite-extreme arithmetic probe described below.
4. `git diff --check --` the four source/test paths exited 0.

External campaign: `../kumpas-data/parity/20261017-validation-v1/`.

- Current completion-manifest SHA256: `1cca1526355e9d4ce6c41102a0a6fa474a15dd77bbac2b09daee1ec85e70c452`.
- Current selection SHA256: `bc7bb2bd85359cc7242ecfb4bba84e267303c911061a0c1a8fa8ce9c980bf8ad`.
- Frozen runtime: Python 3.11.15, NumPy 2.4.6, MediaPipe 0.10.14, opencv-python 5.0.0.93. These are recorded generation versions, not a claim of dependency or model-binary attestation.

I inspected the actual parent logs: `b1/parent-parity-1.log` reports 14 tests, OK; `b1/parent-campaign-1.log` reports 4 tests, OK, including actual detector generation on synthetic videos. The worker's `b1/full-benchmarking-final.log` reports 90 tests, OK with 2 explicit dependency skips. Those broad-environment skips are not detector passes; compatible focused detector executions are separate evidence. **I did not rerun full suites or regenerate the six clips.** This review adds fresh read-back and narrow adversarial probes, not a second full detector campaign.

## Compliance and quality assessment

### Paired-frame boundary

`pipeline_parity.py:161–237` validates supported schema strings, nonempty list/object structure, sequential exact integer indices (excluding booleans), lowercase 64-hex digests, 258 finite numeric values (excluding booleans and overflowing integer conversion), and boolean presence fields before array comparison. Cross-document frame counts/indices and hashes must match. Fixed validation messages do not echo private input values. Tests include both one-sided malformed data and equal-invalid documents, preventing an equality-only bypass.

The actual native producer (`PipelineParityTest.kt:46–53,85–92`) emits `kumpas-android-replay-v1`, the same frame field names and `attempt_result`; it does not emit clip identity. Python's actual schema remains `kumpas-feature-reference-v1`. The new exact-key `kumpas-clip-binding-v1` is therefore appropriate rather than retroactively requiring an unsupported native historical field. CLI comparison requires bindings by default; `--legacy-frame-only` explicitly opts into historical unbound diagnostics. The library retains a legacy default but labels it `unbound_legacy_frames_only`; strict callers must request `require_clip_binding=True`. Arbitrary `prediction` equality is removed and classification is explicitly not evaluated.

### Campaign and provenance

`parity_fixtures.py:49–107` freezes all six selections before detector work, verifies original validation membership and class semantics, checks stored NPZ identity/shape/finite values, hashes source inputs and records preprocessing/extractor/runtime provenance. The stored NPZ's original `split=train` does not conflict with the later evaluation-protocol validation partition. Selection is original-clip based, not an augmented-row selection.

Output containment, traversal and symlink checks precede campaign creation; existing campaign directories are rejected. Per-clip directories and JSON files are exclusive. Two-pass sequential video decoding retains only sampled frames, rather than six videos or all decoded BGR frames. PNG filenames/indices/digests are validated before detector use. Completion follows re-reading every named output and PNG, selection/source hashes and frozen media/landmark inputs; failed work retains an incomplete marker rather than a complete manifest. Tests exercise public CLI controls for overwrite, traversal/symlink, wrong membership/class/hash, failed generation and actual six-video synthetic generation.

The artifact summaries preserve detector presence and finite feature diagnostics. Stored full-video landmarks are sampled then normalized using the actual training helpers; sampled PNGs are independently re-detected with a different tracking history. Their deltas are correctly marked as host-path differences, not normalization bugs, anatomy or accuracy. Structural self-comparison is explicitly not published as Python/Android parity evidence. Raw vectors and media remain external.

## Nonblocking finding

### B1-R1 — LOW: finite inputs can produce nonfinite comparison reports

Location: `pipeline_parity.py:223–228,324`.

The input validator rejects nonfinite values, but finite float64 operands can overflow subtraction or reduction. A read-only strict comparison using matching valid bindings/hashes, 258 synthetic `1e308` values on the Python side and `-1e308` on the native-schema side returned normally with nonfinite block errors and one NumPy warning. `json.dumps(result, allow_nan=False)` then raised ValueError; the CLI's default serializer would permit nonstandard `Infinity` tokens. A self-comparison would not expose this.

This does **not** invalidate the six current finite, ordinary-scale references or their provenance, and no feature-error acceptance threshold/pass bit is asserted. It is a robustness gap for arbitrary comparator inputs, not evidence of a normalization/model defect. Suggested follow-up: explicitly reject nonfinite arithmetic/reductions with a fixed safe error and serialize reports with `allow_nan=False`, adding a public comparator/CLI regression. Do not change normalization or introduce an undocumented feature-range clamp to address it.

## Exact trust and acceptance limits

- Matching binding fields and PNG digests are consistency evidence, not independent origin attestation. The comparator does not itself resolve and authenticate an external replay manifest or verify native execution. A future native result needs independently verified replay/output provenance; copying the Python binding onto unknown bytes is insufficient.
- The campaign CLI's frozen in-memory selection and trusted local filesystem are part of its boundary. Public helper functions are not hostile-input loaders; path checks do not provide race-free protection against an actively mutating filesystem. Protocol/label/selection hashes bind the frozen snapshot; generation is not continuous independent attestation of those metadata files. Current hashes were separately rechecked here.
- Publication is a verified local completion convention, not a power-loss durability guarantee. No concurrent attacker, forced filesystem fault or dependency/model-byte attestation test was performed.
- Real detector execution is supported by generation/focused logs and structurally consistent current outputs. Read-back alone cannot prove detector computation, and this reviewer did not independently rerun it.
- No new classifier inference, training/export/deploy, installs, builds, emulator/ADB/phone operations, default participant-store access or commits occurred. B2 and every human/device/research gate remain separate.

**Recommendation:** accept the scoped prepared-host-reference deliverable with B1-R1 retained as a low-priority follow-up; do not relabel it as completed Android parity or research acceptance.
