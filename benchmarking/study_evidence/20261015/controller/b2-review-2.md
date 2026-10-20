# B2 independent re-review 2 — R1/R2 repairs

## Separate verdicts

| Scope | Spec compliance | Code/evidence quality |
|---|---|---|
| Bounded additive tooling, exact postimages below | **PASS** | **PASS** — no new actionable finding in the repair scope |
| Retained historical incomplete-source diagnostics | **PASS for retention as explicitly incomplete diagnostics only** | **PASS for unchanged, consistent retained evidence**, not a fresh independent model computation |
| Full-source B2 completion | **BLOCKED** | 134 missing source-metadata records; no successful manifest |

**B2-R1 (MEDIUM) and B2-R2 (LOW) are closed for the reviewed postimages.** No additional severity-bearing finding identified. These verdicts do not grant model promotion/equivalence, untouched final-test/signer-independent performance, expert/anatomical, physical-device, integrated-runtime or participant-study acceptance.

## Authority and frozen scope

Read PRD, phase gates, B2 task brief, first independent review, repair report, repair snapshots/diff, current helper/tests and parent verification 2. Loaded study-readiness and verification-before-completion. Current host-only restrictions override older generic emulator instructions.

Independently matched live sources against parent hashes, after snapshots and complete added postimages reconstructed from `controller/b2-review-package-2.diff`:

| Source | SHA256 |
|---|---|
| `training/models/validation_campaign.py` | `8e28d5ad110b76881e65d75e1e851ecb71fa2a6e21e232bc2d0a7fe8cea22998` |
| `training/tests/test_validation_campaign.py` | `5d9f2e13f0896b36940fdd81384ee6db9c2708417edcfce5e8064eefe019fe46` |

Before snapshots match old helper/test hashes `bc7c342a768334c3f0c640451af11b05f2839f23c0ea9ce5736512a2a9998019` and `4fdae28615d80488ca6d313e1d15f15585e0de45ecc9cb50b9df5247af0381f8`. Helper repair adds only the two schema guards. Protected historical selector/protocol/exporter behavior is unchanged.

## Finding closure

### B2-R1 — MEDIUM, CLOSED

`validation_campaign.py:89–98` now requires exact string type and non-whitespace content for `run_id`, `selection_method`, `test_status`, before inherited `verified_selection`. `.strip()` tests emptiness without rewriting accepted values. No UUID constraint, policy vocabulary or promotion threshold is invented.

Fresh regression execution covered all three fields independently with object/list/bool/int/float/null/empty/whitespace values: 24 malformed combinations. It rebounded freeze/provenance identities and dependent digests, so rejection is not merely stale-hash failure. Ordinary controls and exact historical non-UUID identity/policy prose pass.

### B2-R2 — LOW, CLOSED

`validation_campaign.py:76–82` now requires exact built-in integers for both top-level counts and every nested class/partition count, guarding dictionary containers before inherited reconstruction/equality. No coercion or replacement numeric policy was introduced; seed/fraction are not incorrectly treated as counts.

Fresh regression execution covered all six count locations with equal floats, True/False, strings, null, object/list containers, negative and wrong positive integers: 54 malformed mutations, with manifest/freeze/provenance hashes rebound. A three-originals/class fixture gives genuine nested count1, exposing True==1 rather than merely a wrong numeric value. Exact integer controls pass before and after restoration.

Both regressions exercise public `validate_inputs` and real `main(argv)` parser/config-digest preflight in normal and explicit incomplete-source modes. Metadata/predictor spies must remain uncalled and output targets absent. These CLI checks are in-process, not standalone backend inference.

## Actual execution

From the repository using the existing interpreter, no installs:

```sh
TMPDIR="$HOME/.hermes/cache/scratch" "$HOME/.kumpas-venvs/tf/bin/python" -B -E -m unittest discover -s training/tests -p test_validation_campaign.py -v
git diff --check
```

- **13 tests passed, zero failures/errors/skips**: `Ran 13 tests in 2.040s`, `OK`. Diff check clean; command exit0.
- Existing regressions also passed: metrics/probabilities, exact original validation row/label equality, identity graph, paths/exclusive publication, metadata, residency, incomplete publication and mocked backend sequencing. Temporary metadata/model fixtures are synthetic; this is not fresh real inference.
- Parent broad log independently read: `b2/parent-fix1-training-1.log`, **29 tests, zero failures/errors/skips**, `Ran 29 tests in 6.659s`, `OK`. This is parent execution, not my own broad run. Its isolated synthetic save/conversion emitted existing Keras/TensorFlow/Interpreter warnings; no warning-free claim.
- Saved implementer logs were read and hash-matched: R1 RED one test/36 failing subtests; R2 RED one test/16 failing subtests; each GREEN one test/OK. Saved focused13/OK and full29/OK logs also matched recorded hashes. I did not swap live sources to rerun historical RED.

**Additional probe limitation:** a scratch script was prepared for extra missing-key/whitespace/container and incomplete-mode checks, but its execution was blocked by approval timeout and did not run. No retry or alternate execution was attempted. None of its planned assertions is counted as executed evidence. The successful fresh focused suite, source inspection and preservation/readback are sufficient for the narrow verdicts above.

## Independent preservation checks

DATALESS flags checked before streaming hashes; no real NPZ/video contents opened. Actual independent checks matched **288 initial files,82 protected files,42 native bindings,4 A3b bindings,4 B1 source bindings, accepted B1 manifest**, **279 prior B2/B1/external diagnostic evidence files**, and the exact saved append-only ledger prefix. Sets overlap; these are not an additive total. Zero preservation mismatches found.

The first package parser assumed relative headers and raised IndexError after preservation groups passed. Inspecting actual absolute headers and correcting only the read-only parser completed exact postimage verification. This was a reviewer parser assumption, not a product defect.

Old v3 config/campaign/output bytes remain preserved. `source_code_0` and `source_code_1` independently match historical before snapshots and deliberately do **not** match current hardened helper/tests. New code was not retroactively attached to old inference. Parent/implementer evidence reports the other31 of33 input roles unchanged; I did not reread real arrays simply to duplicate that full role graph check. Config/campaign/output byte preservation was independently checked here.

## Retained diagnostics: distinct acceptance boundary

External root: `../kumpas-data/diagnostics/20261017-validation-v1-3/`.

Independently matched `INCOMPLETE-manifest.json` SHA256 **`013f3933fe898dadf2fc25fcf7a12cc50689964f7fba39400cba38e0199b497d`**, all six named output digests, exact campaign-input equality with `b2/current-inputs-v3.json`, and absence of successful `manifest.json`.

Bounded readback independently checked 150 ordered records; metadata available16/unavailable134; unavailable records omit NPZ/video hashes. Recorded top1 versus dense-label counts recompute to **144/150 correct for each model**, matching summary; incomplete manifest n150/missing134. Previous review established full probability/confusion consistency; this re-review did not repeat all probability arithmetic or real model inference. Identical preserved bytes retain historical diagnostics, not a new execution by hardened source.

**Retain bounded incomplete diagnostics; full-source completion remains BLOCKED.** No source recovery, success manifest, new inference or promotion approval follows from R1/R2 closure. A future complete campaign requires separate authorization and fresh exclusive source provenance; do not rerun merely to chase a success code.

## Files and operations

Only repository file created/modified by this reviewer: this report, first incremental then finalized. Additional scratch file: `$HOME/.hermes/cache/scratch/b2-independent-rereview2.py`, prepared but not executed due to approval timeout. No source/test/model/freeze/protocol/exporter/native/historical evidence edits; no installs, cloud hydration, real inference, test-row loading, training, model conversion/deployment, devices/default stores, commits/reset/stash/worktree operations.
