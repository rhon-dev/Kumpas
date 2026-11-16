# Task C fix1 — exact raw numeric preservation and synthetic fixture retention

## Ordering and scope

Queue this repair until the active Task B recovery implementer delivers its immutable-baseline handoff. B currently hash-checks the20 protected C/A/Swift/contract files; do not change C under that worker or start another implementer concurrently. Parent must snapshot delivered B postimages and supply a fresh protection receipt first.

Work in `~/KumpasBuilds/holistic-migration`, branch `holistic-migration`. This is the first bounded C repair after complete independent review. No camera/GUI/phone/app operations, real source inference, fitting, optimization, model export/activation, installs, commits/pushes or provider changes. User explicitly deferred the human webcam check; this is offline software work only.

Own only:
- `training/holistic_migration/dataset.py`
- `training/holistic_migration/tests/test_dataset.py`
- `training/holistic_migration/tests/test_extract.py` (bounded S-C01 test-fixture repair only)
- `training/holistic_migration/README.md` (only exact codec/test-resource clarification if needed)
- Append-only `docs/holistic-migration/task-c-report.md`.

Preserve accepted A, sequence policy/helper/tests, extractor and builder production code, runtime pins, B source/tests/native Swift, original data/membership/class maps and all historical receipts. No new conftest/module or unrelated refactoring without a concrete parent-approved dependency. Read task-c-brief.md and the complete task-c-review-recovery-1.json. Do not weaken the lossless contract or reinterpret an earlier failed report as approval.

## Parent-adjudicated findings

### Blocking L-C01 / MR-C01

The Float64 codec casts input to Float64, casts back to the input integer dtype and compares arrays. In the exercised macOS arm64 NumPy2.1.3 runtime, the cast back can saturate to the original integer maximum, falsely passing this check.

Parent independently reproduced the actual public writer/reader on synthetic face arrays in exclusive scratch files:
- int64 maximum was accepted and read back as input+1.
- uint64 maximum was accepted and read back as input+1.
- Both files were published, and normalized hm153 outputs still matched because face is excluded. Normalized equality is not raw equality.
- Actual RED:2tests,2failures,0errors,exit1. This demonstrates the codec's public numeric defect, not corruption of real SDK Float64/FSL observations.

Required: genuinely exact representability/value comparison that cannot be satisfied by saturating integer cast-back or mixed float/integer NumPy comparison. Keep exactly representable signed/unsigned integers and valid Float64 SDK-shaped controls; reject nonrepresentable values before opening/publishing the raw output. Do not simply ban all integers or all values beyond2**53, because some larger powers/multiples are exactly representable. Preserve existing float-width, finiteness, semantic-array, missingness and timestamp checks.

### Nonblocking S-C01 — included as a bounded test-only improvement

SyntheticDetector.instances retains closed fake detectors whose call records keep full RGB copies. The local autouse reset in test_extract.py does not apply to dataset-module callers. Two bounded clips retained5,529,600 and11,059,200 ndarray bytes; this is test-fixture retention, not a native detector leak, measured RSS or observed OOM. Existing suites passed.

Fix within the two owned test modules: either use compact sufficient image/cadence/geometry evidence instead of every full RGB copy, or ensure explicit registry lifetime/cleanup covers helper callers. Preserve meaningful geometry/channel/cadence/closure assertions. Do not delete assertions, suppress warnings or clear records before their assertions merely to claim lower memory. Avoid circular fixture imports and do not add test machinery to production. Exercise at least a bounded repeated-helper/closed-fixture case; no large intentional OOM test.

## Immutable evidence

All9 reviewed C postimages and exact coverage matched the complete review. Pre-fix source/report/review snapshot:
`~/KumpasBuilds/holistic-migration-data/evidence/task-c-before-fix-570ad20c8af34710b1cba83dc83c55c2/snapshot-index.json`.

Parent reproduction source: `parent_codec_red.py` in that directory. Exact results: `parent_codec_red.result.json`; complete log: `parent-codec-red.log`. The script writes its result exclusively, so rerun a copied script in a fresh exclusive external run directory; do not overwrite the old result.

Complete current C package/manifest:
`~/KumpasBuilds/holistic-migration-data/evidence/task-c-review-17292f00faaf47d2b96d74d43b8d3a7b/{task-c.diff,manifest.json}`.

Prior synthetic producer/bundle receipts bind the old dataset.py contract. Preserve them; never rewrite their source hashes to make them look current after this repair. Regenerate corrected synthetic artifacts in a new exclusive run when needed. No real inference is needed or authorized in this worker.

## Vertical TDD and verification

1. Append recovery/status to original task-c-report.md before edits; link the already verified exact pre-report snapshot. Add signed/unsigned maxima regressions first, run actual RED and retain commands/exits. Assert rejection before output creation. Cover affected raw component paths without substituting a normalization overflow failure for this defect.
2. Implement the narrow exact guard. Exercise positive representable boundaries (including signed minimum and large representable unsigned values), nearby nonrepresentable integers, ordinary integer dtypes and actual-shaped Float64/None/empty/478/variable-face values. Use exact Python scalar integer/value semantics for comparisons; do not repeat the defect in test assertions. Verify raw value preservation as well as normalized equality.
3. Address the included S-C01 test-only resource finding with its own actual behavioral RED/GREEN or honestly labelled coverage-only GREEN. Keep production extraction unchanged and retain current functional assertions.
4. Run the parent's two-case codec harness in a fresh run, affected dataset/extract/sequence tests, and full migration plus original training pytest suites in the existing interpreter. Use `-E -B`, TMPDIR `~/.hermes/cache/scratch`, pytest `-p no:cacheprovider`; unittest discovery omits the C function cases. Record actual test/subtest/warning counts separately, commands/exits/full external logs.
5. Regenerate/read back a complete synthetic campaign/bundle and diagnostic refusal under corrected current contract in a fresh external path. Keep it explicitly synthetic and not training-qualified. Recheck all parent-supplied protected B/A/unaffected-C bytes and original tracked/staged diff.
6. Append exact changed files/postimages, regenerated synthetic provenance, actual results and remaining boundaries. No commit. Parent packages the full corrected C candidate and requests affected data-group re-review; unchanged sequence-group verified findings may carry forward only through explicit byte/interface mapping. C acceptance remains pending until that re-review is actually read and matched.
