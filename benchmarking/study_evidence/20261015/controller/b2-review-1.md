# B2 independent spec and quality review

## Final verdict

- **Spec compliance: REQUESTCHANGES for the reusable strict validator.** B2-R1 allows malformed selection identity/policy metadata through the public input boundary. The actual frozen diagnostic output is internally consistent and may be retained as bounded incomplete-source evidence; this finding does not invalidate its predictions.
- **Code quality: REQUESTCHANGES.** One medium-severity metadata-validation gap (B2-R1); one low-severity protocol numeric-type gap (B2-R2). No critical finding or demonstrated probability, confusion-matrix, validation-original equality, path-containment or incomplete-mode bypass was found in the exercised scope. No repairs made.
- **Full-source B2 acceptance: BLOCKED, independently of code review.** The real run has 134 unavailable source metadata records, an `INCOMPLETE-manifest.json`, and no successful `manifest.json`. Source-provenance completion, promotion, final-test/signer-independent, anatomy/expert, physical-device and participant-study gates remain unmet.

This is a recovery review, not adoption of the interrupted reviewer's verdict. Its transcript was used to recover a possible probe; all findings below were reproduced afresh. Scope is exactly the two additive source/test files, their frozen diff, and bounded readback of the existing diagnostic artifacts. Read PRD and phase gates, binding B2 brief, discovery model audit, B1 review, B2 report/handoff and parent verification. The current host-only restrictions override older generic emulator instructions.

## Frozen postimages and preservation

I parsed both additive file sections of `controller/b2-review-package-1.diff`, reconstructed their complete added postimages, and compared them byte-for-byte with the current files. Both match the parent record:

| File | SHA256 |
|---|---|
| `training/models/validation_campaign.py` | `bc7c342a768334c3f0c640451af11b05f2839f23c0ea9ce5736512a2a9998019` |
| `training/tests/test_validation_campaign.py` | `4fdae28615d80488ca6d313e1d15f15585e0de45ecc9cb50b9df5247af0381f8` |

Independent streaming readback matched **288 initial files, 82 protected files, 42 native-source bindings, 4 A3b source bindings, 4 B1 source bindings and the accepted B1 campaign manifest**, with zero mismatches. These groups overlap; they are not an additive total. All **33 declared current input/source roles** matched their digests. Files were stat-checked for DATALESS before hashing. No NPZ/video was opened by this reviewer; no test-array rows were loaded. Test arrays were only streamed as bytes for declared hash verification. `git diff --check` exited 0.

## Executed verification

Commands ran from the repository using the existing interpreter, no installs:

```sh
TMPDIR="$HOME/.hermes/cache/scratch" "$HOME/.kumpas-venvs/tf/bin/python" -B -E -m unittest discover -s training/tests -p test_validation_campaign.py -v
TMPDIR="$HOME/.hermes/cache/scratch" "$HOME/.kumpas-venvs/tf/bin/python" -B -E "$HOME/.hermes/cache/scratch/b2-independent-review-probe.py"
git diff --check
```

- Fresh focused suite: **11 tests passed, zero skips**, exit 0. Backend test is mocked; it is not a fresh real-model inference run.
- Independent synthetic probe: exit 0, including positive control, strict default nonresident failure, incomplete mode rejecting malformed metadata, incomplete mode rejecting malformed configuration before prediction, omitted unavailable hashes, incomplete-only publication, and CLI exit 3. Mocked predictor was asserted uncalled for rejection cases.
- The scratch probe also performed the postimage/protected/output readback and reproduced R1/R2 below. It contains synthetic fixtures and aggregate checks, not real vectors or probabilities. Scratch is transient; durable reproduction instructions follow below.
- Parent full-suite evidence was separately read at `b2/parent-training-1.log`: **27 training tests, zero skips, OK**, including existing isolated synthetic save/conversion. I did not rerun that conversion or claim the parent's broad suite as my own execution.

### Existing real diagnostic readback

External root: `../kumpas-data/diagnostics/20261017-validation-v1-3/`.

`INCOMPLETE-manifest.json` SHA256 independently matched **`013f3933fe898dadf2fc25fcf7a12cc50689964f7fba39400cba38e0199b497d`**. Every named output digest matched; campaign inputs exactly equal `b2/current-inputs-v3.json`. No success manifest exists.

Readback independently recomputed, without real-model reruns:

- 150 ordered clip records; both model probability vectors present in every record; 16 available and 134 unavailable source-metadata dispositions. Unavailable records omit NPZ/video hashes, rather than inventing values.
- Each vector has 50 finite probabilities in [0,1], sum within the representation check; recorded top1, confidence and margin match recomputation.
- Each model: **144/150 correct**, confusion matrix matches the summary, every class support is 3, macro-F1 **0.9592380952380953**.
- Top1 disagreements **0/150**; max absolute probability difference **0.18056780099868774**; recomputed mean absolute error matches the summary.

This establishes consistency of retained outputs with the source-bound execution evidence, not independent proof of model computation. Actual inference is supported by the worker execution artifacts and parent verification; this reviewer deliberately did not rerun it or open cloud-backed sources.

## Findings

### B2-R1 — MEDIUM: malformed frozen selection identity and policy types are accepted

**Location:** `validation_campaign.py:83–88,111–118`; inherited `export_frozen.py:13–27` (read-only dependency).

The additive boundary strictly checks metric fields and several digest relationships but delegates other selection fields to `verified_selection`, which only checks their truthiness. A nonempty object for `run_id`, a list for `selection_method`, and boolean `test_status` are accepted when the provenance object repeats the run identity and dependent current hashes are rebound. Thus byte-consistent, malformed selection metadata passes `validate_inputs` and can be frozen into the campaign. The public CLI also uses this same validator. This contradicts the binding brief's strict selection/malformed-metadata boundary; consistency of two malformed values is not schema validation.

**Fresh reproduction:** start with `test_validation_campaign.InputTests.setUp()` (all inputs synthetic). Change selection JSON to:

```python
freeze.update(run_id={'unexpected': 'object'},
              selection_method=['validation'], test_status=True)
```

Write it, update `config['sha256']['freeze']`, set candidate provenance `run_id` to the same object and `selection_sha256` to the new freeze hash, write/rebind provenance. `validate_inputs(config)` returns a dictionary normally. The actual current selection has strings in all three fields; it was separately inspected and is not malformed.

**Expected:** the new additive validator rejects unsupported types/empty or invalid identities with fixed `INVALID_INPUTS`, before metadata scanning or prediction. Preserve the protected existing selector/exporter; add validation and synthetic regressions in the additive files. Do not infer a new selection/promotion policy or silently rewrite the accepted freeze. This is an input-contract defect, not evidence that the actual model identity or scores changed.

### B2-R2 — LOW: protocol count values need exact integer typing

**Location:** `validation_campaign.py:76–88`, through `evaluation_protocol.py:82–99`.

Rows and config counts exclude bool/float values, but top-level manifest counts and nested class counts are accepted through ordinary Python dictionary equality against the reconstructed manifest. Equality does not distinguish `4.0` from `4`.

**Fresh reproduction:** synthetic fixture manifest `n_validation=4.0`; write/rebind manifest, update freeze `protocol_sha256`, rebind freeze, then update/rebind candidate provenance `protocol_sha256` and `selection_sha256`. `validate_inputs(config)` accepts it. The scratch probe printed `REPRO_B2_R1 manifest n_validation=4.0 ACCEPTED` (that preliminary output label groups probes; the final finding identifier is B2-R2). Actual campaign manifest uses integer `n_validation`.

**Expected follow-up:** require exact integer count types (excluding bool), including nested count values, before inherited equality checks; test rebound-hash malformed controls. Counts remain numerically correct in this reproduced case, so severity is low and it does not invalidate the real diagnostic. No claim is made that an arbitrary wrong numeric count passes reconstruction.

### Durable minimal reproduction recipe

Use the existing TF interpreter with `-B -E` and scratch TMPDIR. From repository root, run the following Python body (no real arrays/models opened):

```python
import sys, json
from pathlib import Path
sys.path[:0] = ['training/models', 'training/tests']
import test_validation_campaign as tests
import validation_campaign as vc
from evaluation_protocol import sha256
f = tests.InputTests(); f.setUp()
try:
    def edit(role, change):
        p = Path(f.config['paths'][role])
        value = json.loads(p.read_text()); change(value)
        p.write_text(json.dumps(value))
        f.config['sha256'][role] = sha256(p)
    assert isinstance(vc.validate_inputs(f.config), dict)  # positive control
    edit('freeze', lambda j: j.update(
        run_id={'unexpected': 'object'},
        selection_method=['validation'], test_status=True))
    edit('provenance', lambda j: j.update(
        run_id={'unexpected': 'object'},
        selection_sha256=f.config['sha256']['freeze']))
    assert isinstance(vc.validate_inputs(f.config), dict)  # R1: unexpected acceptance
    edit('manifest', lambda j: j.update(n_validation=4.0))
    edit('freeze', lambda j: j.update(protocol_sha256=f.config['sha256']['manifest']))
    edit('provenance', lambda j: j.update(
        protocol_sha256=f.config['sha256']['manifest'],
        selection_sha256=f.config['sha256']['freeze']))
    assert isinstance(vc.validate_inputs(f.config), dict)  # R2: unexpected acceptance
finally:
    f.doCleanups()
```

The executed scratch probe independently checked R2 before introducing R1, so the second acceptance is not dependent on malformed selection types.

## Other assessed boundaries

- **Selection/protocol/hash graph:** declared paths/digests are strictly checked; no mutable latest checkpoint selection. `verified_selection` reconstructs original-clip partition membership and binds the checkpoint. Validation feature rows and labels are exactly compared with originals after shape/type/range/finiteness checks. Source/dense label semantics and ordered clip identities are checked rather than assuming global equality. R1/R2 are the identified schema exceptions.
- **Metrics/probabilities/arithmetic:** exact builtin numeric metric typing excludes bool/string/NaN/infinity/out-of-range values; class counts and model output dimensions are checked. Float probabilities require finite [0,1] values and normalized sums. Drift arithmetic is done after bounded probability checks, with float64 reductions; it does not inherit B1's unrestricted finite-extreme subtraction issue. Metadata torso arithmetic uses float64 with overflow/invalid traps and strict finite JSON; this reviewer made no normalization changes.
- **Publication/paths:** explicit config hash, absolute paths, symlink/traversal refusal, direct-child output containment, exclusive directory/files and exact-byte write readback are present. Inputs and available source hashes are rechecked after prediction; generated records are reparsed and correctness counts recomputed before publishing a manifest. The CLI excludes repository output roots. This remains a trusted local filesystem boundary, not hostile concurrent filesystem attestation or power-loss proof.
- **DATALESS/incomplete mode:** NPZ and video residency are checked before NPZ content or source hashing in metadata acquisition. Default source unavailability fails closed. Explicit incomplete mode catches only fixed `SOURCE_NOT_RESIDENT`, not malformed metadata; it does not turn invalid config/metadata into predictions. Missing sources yield nonzero exit 3 and an incomplete manifest, never a success manifest. No attempt was made to inspect inaccessible NPZ internals or pretend malformed unavailable bytes were validated.
- **Source lineage:** actual config binds preprocessing/normalization/augmentation/helper source roles and runtime information. Hashes are CURRENT capture, not preregistration. Fit arrays are byte/shape/finiteness/label/log checked, not independently reaugmented. NPZ-to-original normalization authenticity is not independently reconstructed. Available NPZ metadata is not anatomy truth; 134 missing source pairs prevent complete detector/error provenance. No invented data, promotion threshold or new final-test claim is warranted.

## Disposition and files written

Retain the real run as **verified bounded incomplete-source diagnostics**, not full B2 completion. Request additive schema hardening/review for R1; retain R2 as a low-priority companion regression. Even after those code findings are addressed, source-provenance acceptance remains blocked until a separately authorized, fresh, complete campaign can bind actual resident sources; do not rerun inference solely to chase a success code.

Only repository file written by this reviewer: this report. One synthetic/readback probe was created under the session scratch directory. No source/test/model/native/consumer/historical evidence edits; no installs, training, real inference, conversion, devices, default stores, retraining, deployment, commits, reset, stash or worktree operations.
