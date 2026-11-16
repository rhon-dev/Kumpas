# Task C — source-bound extraction and shared dataset construction

## Goal, authorization and protected boundary

Implement a working offline pipeline for every approved gesture, using accepted Task A and `CAPTURE_CANDIDATE.md`. The owner explicitly chose “Continue offline work; webcam check later.” Only human webcam acceptance is deferred. No camera/GUI/phone/app operations, optimization, classifier fitting, export, activation, commits, pushes, installations or provider changes in this task. Parent owns real campaigns after tests/review. The original cloud checkout and Recognition V2 worktree remain untouched.

Work in `~/KumpasBuilds/holistic-migration`, branch `holistic-migration`. HEAD/base remains4d901693642af5f572455b2c75ba095b0ec65c7f. Preserve all accepted Task A six files and Task B five source/test files exactly. Task B software review may run concurrently; Task C must not import or depend on camera.py/webcam.py or change their supporting reviewed files. Its dependency is accepted features.py/detector.py only.

Create only:
- `training/holistic_migration/sequence.py`: shared image preparation,15Hz clock and bounded capture eligibility/resampling.
- `training/holistic_migration/dataset.py`: source graph validation, lossless numeric raw-observation codec and canonical bundle construction.
- `training/holistic_migration/extract.py`: actual source-video/Tasks streaming extraction CLI, calling those helpers.
- `training/holistic_migration/build_dataset.py`: thin bundle CLI, no detector/model execution.
- `training/holistic_migration/tests/test_sequence.py`
- `training/holistic_migration/tests/test_dataset.py`
- `training/holistic_migration/tests/test_extract.py`
- `training/holistic_migration/README.md`: exact exercised interfaces/commands and limitations.
- `training/holistic_migration/requirements.txt`: actual existing runtime pins queried from installed metadata; no installation.
- `docs/holistic-migration/task-c-report.md`: append actual RED/GREEN commands/exits/results incrementally, beginning before production edits. Save full verbose logs externally and summarize them here rather than duplicating every prior suite log.

If a different file is necessary, stop and report the concrete dependency; do not edit the immutable foundation or invent an alternative feature contract.

## Inputs and actual schema

External data root: `~/KumpasBuilds/holistic-migration-data`.
- `candidate-partitions-v1.json`: schema_version1; counts fit663/validation150/test203; rows with clip_id, source_token, original_id,dense_id,label,csv_label,official_split,signer_id,archive_member,video_bytes,video_sha256,partition. SHA-256 a80620494894701c9f4f2dfde5a3050f4f80b5532b04004c0761c7945300275f.
- `verified-video-byte-inventory.json`: rows before partition assignment; summary and archive_sha256; SHA-256 0ff0c09c7df877c860258049427243aacc03d5f35ef11526715366f28940d41e. Its own source_inventory_sha256 binds `selected-source-inventory.json` (23697b80445fe1daedd9dfb1d1127e02e1a474eb13144ff5fcad9e4d589701ca).
- `decoded-source-audit-v1/summary.json`: source_count1016,ok1016,errors0, all three decoded-pixel duplicate-group counts0, source_inventory_sha256 bound to verified inventory, records_sha256 bound to sibling records.jsonl (a1926b7f0d3ecc7788db4126fd435a287c867519e642ff9770aeddcc74f63e3b).
- Decode JSONL rows have the same source identities plus status ok, decoded_frames integer, declared_frames OpenCV descriptive float, fps float, shapes, backend,decoded_bgr_sha256. These actual descriptive floats are not schema-count errors.
- `clips_raw/<clip_id>`: resident staged raw sources. Verify exact bytes/length against the frozen rows before inference; do not hydrate cloud paths or trust the recorded absolute raw_path as authoritative.
- Source class map: repository `training/preprocessing/selected_classes.json`, object with selected list of id,label,category; SHA-256 e8089f5c0186bfe6fd9ec63a5150f8094645c1686509f23c1716453b5f9ce0d5. Exactly50 classes ordered by ascending original id. Dense25 is original49/TODAY. Preserve literal labels and sparse original IDs; source_token remains literal Windows spelling while clip_id is already canonical POSIX. Do not repair malformed tokens.
- `holistic_landmarker.task`: actual bundle13683609bytes, SHA-256 e2dab61191e2dcd0a15f943d8e3ed1dce13c82dfa597b9dd39f562975a50c3f8. This is an observed official-bundle identity, not a vendor-published checksum.

Frozen membership and verified-byte inventory intentionally retain pending-at-creation text. Validate the completed decode companion and its exact graph rather than rewriting those historical files or treating their old prose as current availability.

## Required interfaces and behavior

Use accepted `RawFrame(timestamp_ms,pose,left_hand,right_hand,face=None)`, `pack_frame`, `resample_frames` and `HolisticDetector(Path).detect(rgb,timestamp_ms)`. Read their small current implementations for exact types; do not copy normalization or resampling.

`sequence.py` exposes:
- `ObservationClock().admit(timestamp_ms:int)->bool` implementing the candidate fixed15Hz clock. Validate every input timestamp before mutation, including skipped frames; reject bool, float, negatives and nonincreasing timestamps. No invented observations on skipped slots.
- `prepare_image(rgb,cv)->ndarray` implementing the candidate shared plain RGB uint8 resize to640×360 INTER_AREA/contiguous form; no mirror or normalization changes.
- `prepare_capture(frames)->CaptureResult`: result has tensor or None, fixed reason, actual observation count/hand count/time bounds. Implement the exact current candidate eligibility and reuse accepted resampling. Shape/semantic-array/finite errors are ValueError; ordinary coverage failure is explicit ineligibility. Preserve internal missingness, reject internal invalid pose/gaps, never concatenate around them.

`dataset.py` supplies shared producer/consumer validation and numeric raw codec. Bind exact source/class/partition/decode/runtime/model/contract hashes; compare all source identities and counts across companions; reject duplicate/path-traversal/cross-partition/original-test-to-fit contamination. Require exact built-in integers for schema IDs/counts, excluding bool/equal floats; preserve legitimate descriptive OpenCV floats. Check DATALESS flags before opening raw media. Reject symlink/traversal/overlapping output paths; never modify original inputs.

Raw storage is lossless numeric NPZ (`allow_pickle=False` on load): timestamps, explicit pose/left/right/face presence, pose33×4 and hands21×3 at Float64, plus variable-cardinality face values/offsets or another documented numeric-only lossless layout. Reconstruct None exactly. Preserve raw SDK values before normalization and all observed face points; no object arrays, truncation, semantic masks hidden by coercion, fabricated detections or silent absent-block contamination. Test round-trip exact normalized output equality.

`extract.py` CLI accepts explicit absolute `--partition-manifest`, `--source-inventory`, `--decode-summary`, `--raw-root`, `--classes`, `--model`, `--output`. Resolve the sibling decode records and inventory's upstream companion from those verified files; document the exact interface. Preflight metadata/paths/source graph and reject existing output before loading SDK/creating trackers. Output must be a fresh exclusive external directory, not inside the repo, source root or another protected input tree. Preserve incomplete attempts; never reuse by filename or overwrite.

For every selected source: hash-check raw bytes, decode its full frame stream, use actual finite monotonic POS_MSEC rounded to integer milliseconds, apply shared clock/image helper before actual accepted Tasks VIDEO detection, create/close one detector per unrelated clip, and save raw observations. Verify decoded count and ordered decoded BGR digest against the completed audit while decoding (the audit hashes little-endian height,width,channels then contiguous bytes for each frame). No guessed timestamp fallback when presentation timestamps fail. Keep every declared source in an append-only row ledger, including fixed error/ineligible status. Preserve stderr; use actual per-clip progress. Publish a completed extraction manifest only after all output bytes/digests and input identities are read back. Errors/incomplete intended coverage must remain non-gating with nonzero CLI exit, never success plus invented arrays.

Add explicit `--diagnostic-fit-only`: choose the first clip by literal clip_id within each dense class of the already frozen fit partition (exactly one/class), save the selected IDs before inference, and open/infer only those selected source videos. The full metadata graph stays bound and unchanged. A successful bounded diagnostic has status `diagnostic_fit_only`, full-campaign qualification false and its declared/selected/processed counts separate; builder must refuse it as a training dataset even with exit0. Record per-clip capture eligibility using the same shared helper, without publishing a full dataset or claiming those detector-derived intervals are annotated signs. This lets the parent exercise real fit-only production extraction/codec before admitting the full campaign. Test that the diagnostic never decodes validation/test sources and cannot bypass dataset completion guards.

`build_dataset.py --campaign ABSOLUTE_DIRECTORY --output NEW_EXTERNAL_DIRECTORY` validates the completed campaign/rows/raw digests/current contract, calls the same prepare_capture and writes unaugmented Float32 X_fit/X_validation/X_test arrays with shape[N,30,153], integer y arrays, ordered clip IDs, ordered dense/original/literal class metadata and data_manifest.json. Keep declared, eligible and ineligible counts/reasons per partition/class; no placeholder zero examples or silent class removal. Require eligible support for all50 classes in fit/validation; retain/report test ineligibility explicitly. No new split, test selection/predictions, augmentation or optimization. Fail readback/tampering rather than publishing a successful manifest. Future training will load only fit/validation, with explicit separate frozen-model test evaluation.

Runtime: existing `~/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B`, TMPDIR `~/.hermes/cache/scratch`. Tests use injected in-process synthetic detector/video fixtures only where native inference is not the subject. No arbitrary command/module loader exposed through CLI/config. Trusted callbacks are not a sandbox; report that boundary. Do not represent synthetic fixtures as FSL evidence or run the real bulk campaign.

## Vertical test-first slices

1. Create report. Add one clock test, run RED, implement minimal GREEN. Extend to30/60fps quantization, nonmonotonic skipped timestamps and long-gap/no-fabrication boundaries one behavior at a time.
2. Add positive bounded-capture test with8 synthetic valid RawFrames at increasing67ms spacing; tensor must equal accepted resample_frames on those exact frames. Then test missing single/both hands, first/last trimming only, all-handless, too-short/long, too-few hand observations, internal invalid pose and250ms boundary, malformed/nonfinite input and plain-array controls.
3. Raw codec round-trip including None and differing face cardinality; corrupt offsets/types/absence blocks/object arrays/digests reject. Source graph positive fixture then fully rebound schema/path/duplicate/original-split tamper cases through the public preflight, not merely an earlier stale-digest rejection.
4. Actual extraction flow on explicitly synthetic decoded-video fixtures with injected detector: cadence/geometry/new tracker per clip/decoded count+pixel digest/cleanup/output ledger. Fail-before-runtime invalid input and incomplete-publication cases. Synthetic output remains labelled synthetic.
5. Actual bundle flow on complete synthetic graph: exact tensor/ID/partition mapping, ineligibility denominators and unsupported class; byte tamper/readback/existing-target failures. Exercise both CLI entry points and --help; document actual commands.
6. Run full migration suite and original training suite, preserve actual logs/exits/counts, verify Task A and Task B hashes unchanged and original tracked diff empty. Self-review, append exact handoff interfaces/limitations and stop for parent review. No commit.

Do not implement all source before running RED, skip failure paths, synthesize missing receipts, restart completed Task A/B, or dispatch another worker. Return only concise completion status, actual tests, report path and remaining concerns.
