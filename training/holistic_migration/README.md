# hm153 offline extraction and canonical data

Task C is an independent recorded-source data path built on immutable Task A
`RawFrame`, `pack_frame`, `resample_frames` and `HolisticDetector`. It does not
import `camera.py` or `webcam.py`. No classifier is fitted, activated or evaluated
by these entry points. Human webcam acceptance remains deferred. The parent has
also reported separate Task B source-terminal/thread-cleanup defects; passing
existing suites is **not** Task B software approval or human acceptance.

## Runtime and exercised commands

From `~/KumpasBuilds/holistic-migration`, use the existing interpreter:

```sh
PY="$HOME/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python"
export TMPDIR="$HOME/.hermes/cache/scratch"
"$PY" -E -B -m training.holistic_migration.extract --help
"$PY" -E -B -m training.holistic_migration.build_dataset --help
"$PY" -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests -v
"$PY" -E -B -m pytest -p no:cacheprovider training/tests -v
```

`requirements.txt` records queried installed **direct** versions, not a complete
transitive lock and not an instruction to install. Runtime identity includes
Python/version/executable, platform and installed NumPy/OpenCV/MediaPipe metadata;
manifests include canonical SHA-256 of that identity and of the current source/
contract hash map. Moving interpreters, changing those identities or changing
bound source contracts intentionally invalidates a campaign.

The synthetic tests exercise production extraction, shared RGB/cadence/capture,
lossless codec, complete 50-class graph, bundle building and both CLI boundaries.
Synthetic outputs are explicitly `synthetic_in_process`; they are not FSL or
live-camera evidence. See `docs/holistic-migration/task-c-report.md` for actual
RED/GREEN commands, exits, final counts and external full verbose logs.

Synthetic detector call records retain shape/dtype/contiguity, timestamp and a
full-pixel SHA-256, not full RGB copies. Tests compare independent expected RGB
resize digests for every admitted frame and keep cadence/closure assertions.
The extraction module's local registry reset also runs at teardown; dataset
helper callers retain only compact evidence, and the bounded repeated-helper
regression checks closed/released fixtures without clearing before assertions.

## Public Python interfaces

- `sequence.ObservationClock().admit(timestamp_ms: int) -> bool`: nonnegative
  strictly increasing built-in ints only, including skipped timestamps; first
  actual frame admits; `((2*elapsed_ms+1)*15)//2000` determines due slots. No
  invented observations after gaps. Reset for each unrelated clip.
- `sequence.prepare_image(rgb, cv) -> ndarray`: plain nonempty RGB uint8,
  unmirrored `INTER_AREA` resize to 640x360, contiguous output; no color swap or
  feature normalization. File BGR is converted to RGB by the extractor first.
- `sequence.prepare_capture(frames) -> CaptureResult`: validates every supplied
  RawFrame with accepted `pack_frame`, then trims only before first/after last
  actual SDK hand. Retains internal missingness. Eligibility is at least 8 real
  observations, at least 4 hand-observed rows, duration 400–5000ms inclusive,
  every consecutive gap at most 250ms and usable pose throughout the interval.
  Eligible output is accepted nearest-observation `resample_frames(...,steps=30)`
  exactly, a plain Float32[30,153]. Invalid shape, semantic arrays, nonfinite values
  or nonincreasing timestamps raise ValueError, not valid zero examples.
- `CaptureResult`: `tensor`, `reason`, bounded `observation_count`, `hand_count`,
  `start_ms`, `end_ms`; additionally `source_observation_count`, `source_start_ms`,
  `source_end_ms` retain the input denominator even for all-handless observations.
  With no hand-observed interval, bounded counts are zero and bounds None. Fixed
  reason priority: `no_hands`, `too_few_observations`,
  `too_few_hand_observations`, `too_short`, `too_long`, `observation_gap`,
  `invalid_pose`, or `eligible`. Coverage failures have tensor None. These bounds
  are detector-derived intervals, **not annotated signs**.
- `dataset.preflight(*, partition_manifest, source_inventory, decode_summary,
  raw_root, classes, model, output=None) -> SourceGraph`: all paths absolute.
  Validates full companion graph without opening raw media. Resolves
  `source_inventory.parent/selected-source-inventory.json` and
  `decode_summary.parent/records.jsonl`; never trusts historical `raw_path`.
  Checks literal Windows source_token against canonical clip_id without repairing
  either; source identities/counts, ascending sparse original IDs, 50 classes,
  declared partition support, exact integer schema values (not bool/equal floats),
  source/pixel duplicates and official-test isolation. Descriptive finite positive
  OpenCV `declared_frames` and `fps` floats remain legitimate. Historical pending
  prose remains untouched; completed audit is the availability authority.
- `dataset.write_raw(path, frames) -> sha256` and
  `dataset.read_raw(path, expected_sha256) -> list[RawFrame]`: exclusive numeric NPZ.
- `extract.run_extraction(*, output, diagnostic_fit_only=False,
  video_factory=None, detector_factory=None, cv=None, **preflight_inputs) -> int`:
  default path is actual OpenCV full-stream decode and accepted Tasks VIDEO
  detector. Trusted in-process test injections mark outputs synthetic. They are
  **not a sandbox**. There is no command/module-loader/config injection in CLI.
  Default real extraction additionally enforces the frozen source, class, model
  and decode-record identities from the brief before output creation/native load.
- `dataset.validate_campaign(campaign) -> (graph, manifest, rows)` reopens exact
  full producer coverage/current contracts, raw digests and capture receipts.
- `dataset.build_dataset(*, campaign, output) -> manifest`: no detector execution,
  no new split, augmentation, optimization, test selection or predictions.

## Lossless raw numeric layout

All NPZ reads set `allow_pickle=False`; there are no object arrays:

| Key | Numeric storage |
| --- | --- |
| `timestamps` | int64[N], actual rounded presentation milliseconds |
| `pose`, `left_hand`, `right_hand` | Float64[N,33,4], Float64[N,21,3], Float64[N,21,3] |
| `pose_present`, `left_hand_present`, `right_hand_present`, `face_present` | uint8[N], strictly 0/1 |
| `face_values` | Float64[total_face_points,3], all observed points |
| `face_offsets` | int64[N+1], nondecreasing from 0 to total_face_points |

Absent fixed blocks must contain only zero values and have presence 0. Absent
face blocks must have repeated offsets and presence 0. A present empty face has
presence 1 and repeated offsets: it is distinct from None. Face cardinality is
never assumed/truncated (including 478 points). SDK Float64 values are retained
exactly; the codec rejects values not losslessly representable in Float64 or
nonnegative int64 timestamps rather than silently converting them. Integer
representability uses unbounded Python int/int value comparison after conversion,
never saturating NumPy integer cast-back or mixed float/integer NumPy equality.
Exactly representable large integers (including powers/multiples above 2**53 and
signed int64 minimum) remain supported; signed/unsigned maxima are rejected.
All observations are checked before the raw output is opened/published. Numeric
values, not original ndarray dtypes, are preserved in the Float64 layout.
Round-trip raw values and normalized outputs are checked for exact equality,
not an approximate tolerance; face-excluding normalized equality alone cannot
prove raw preservation.
Raw SDK values remain raw; normalization/resampling is never stored in their place.

## Real CLI: parent-owned, not run as a campaign by Task C

The following is the explicit interface for the parent **after review**. The real
fit-only diagnostic/full inference campaign is deliberately not claimed as run:

```sh
D="$HOME/KumpasBuilds/holistic-migration-data"
"$PY" -E -B -m training.holistic_migration.extract   --partition-manifest "$D/candidate-partitions-v1.json"   --source-inventory "$D/verified-video-byte-inventory.json"   --decode-summary "$D/decoded-source-audit-v1/summary.json"   --raw-root "$D/clips_raw"   --classes "$PWD/training/preprocessing/selected_classes.json"   --model "$D/holistic_landmarker.task"   --output "$D/hm153-fit-diagnostic-NEW"   --diagnostic-fit-only
```

The output must not exist; its parent must exist. No overwrite, reuse/resume by
filename, cloud hydration or automatic replacement clip is supported. Rejects
relative/traversal/symlink paths and macOS DATALESS inputs before opening bytes.
Output must be external to this repository and must not overlap raw-root,
decode-audit or campaign input trees, contain any protected input, or be an
ancestor of the repository. Original source inputs are never written.

Fit diagnostic selects the literal lexicographically first clip_id **within each
already-frozen fit class** and saves `selected_ids.json` before native runtime.
Only those 50 videos are opened/inferred; all sources remain declared in graph and
row ledger, with other rows explicitly `not_selected`. Success can exit 0 but is
`status=diagnostic_fit_only`, `full_campaign_qualification=false`. Declared,
selected, processed and error counts are separate (`processed` means successfully
audited/serialized sources; failed attempts are counted as errors). A builder refuses it, even if
its status/qualification fields alone are altered. No full dataset is emitted.

For the parent's full campaign, omit `--diagnostic-fit-only`, use a different new
output, and retain native stderr externally. The extractor checks each raw source
length/SHA before decoding, validates every actual finite nonnegative POS_MSEC
(including skipped frames), rounds to built-in integer ms, rejects duplicate or
backwards rounded times, and has no FPS/frame-count timestamp fallback. One
accepted tracker is created/closed per unrelated clip; video release runs even
if detector processing/cleanup fails. Full decoded counts, observed shapes and
ordered BGR digest must match the completed audit. Digest framing is exactly
three little-endian int32 height/width/channels followed by contiguous frame bytes
for every frame. One frozen fit clip's existing audit was checked with **zero
inference calls** to establish this byte framing, not capture/recognition quality.

`rows.jsonl` is append-only per attempt: every declared row has eligible,
ineligible, not_selected or fixed error status. Native stderr is not swallowed;
per-clip progress and exceptions go to stderr. Ordinary coverage ineligibility
retains raw data and is not an extraction error. Errors make the attempt
non-gating with exit 2 and `failure.json`; no completion manifest is published.
An interrupted process retains the actual attempt/selection and flushed partial
ledger; it cannot resume or qualify as complete. Disk/process failure cannot
promise a final row for not-yet-processed clips; declared graph remains in attempt.

Completion reopens rows, every raw NPZ, source metadata/model and current contracts.
Manifest JSON is staged/read back, exclusively linked to the final name and read
back again; failed publication removes only that just-linked final name and keeps
its pending artifact. Completed manifests do not imply capture feasibility or
classifier acceptance. File hashes are integrity checks, not signatures against a
malicious process with write access; trusted callbacks/filesystem concurrency are
not a sandbox, and there is no hostile-writer TOCTOU guarantee.

## Canonical bundle CLI and contents

```sh
"$PY" -E -B -m training.holistic_migration.build_dataset   --campaign "$D/hm153-full-campaign-NEW"   --output "$D/hm153-canonical-bundle-NEW"
```

This thin CLI never imports OpenCV/MediaPipe or creates a detector. Both CLIs use
exit 2 for rejected input/failed intended coverage; `--help` exits 0. The complete
synthetic builder CLI success and existing-target/relative-input failures have
been exercised in real subprocesses. Actual commands/logs are in the task report.

Artifacts:
- `X_fit.npy`, `X_validation.npy`, `X_test.npy`: Float32[N,30,153].
- `y_<partition>.npy`: int64 dense labels; `clip_ids_<partition>.npy`: pickle-free
  Unicode arrays, in literal clip_id order within each frozen partition.
- `class_metadata.json`: all 50 dense/original/literal label/category entries.
- `capture_rows.json`, `eligibility.json`: every declared source, bounded/source
  counts and time bounds, eligibility and fixed reasons; declared/eligible/
  ineligible counts by partition and by class, without silently dropping classes.
- `attempt.json`, artifact digests/shapes/dtypes and `data_manifest.json`: exact
  campaign/source/runtime/contract identity and successful readback receipt.

Every class needs at least one eligible fit **and** validation example. Failure
preserves denominator reports and an explicit support-failure artifact, with no
successful data manifest. Test ineligibility is retained/reported; a zero-eligible
partition uses an empty [0,30,153] array, never placeholder zero examples. All
array/JSON artifacts and campaign raw files are reopened/validated before final
publication. `training_qualified=false` explicitly retains later review, real
all-class feasibility, tiny-overfit and physical/linguistic gates. Future training
must load only fit/validation; test is for separate frozen-model evaluation. No
human sign annotation, signer independence, recognition score, anatomical/live
handedness acceptance or performance claim is established here.
