# Approved face-inclusive candidate contract: hm1588-v1

## Authorization and boundary

On November 16, 2026 the owner requested continuation of migration Phase 3, then selected **“Approve full-face contract, tests, then data rebuilding”** in response to the explicit proposed 1,588-feature design. This authorizes the prerequisite implementation/tests and reviewed data rebuilding, not real-source model training/evaluation, new detector extraction, camera capture, recording, mobile work, export, activation, publication or research acceptance. The historical hm153-v1 contract and its source-bound artifacts remain unchanged.

This is an engineering candidate, not expert linguistic or anatomical validation. All 50 approved output identities remain unchanged. Do not reduce classes or weaken missingness rules to manufacture support.

## Detector and reusable observations

Retain the exact accepted Tasks Holistic VIDEO/CPU adapter, unmirrored RGB 640x360, real presentation timestamps and 15 Hz observation cadence. Retain the previously bound bundle and runtime. No legacy Solutions, separate detectors, world coordinates or blendshape substitution. A new detector is required per unrelated clip if future extraction is separately authorized.

The existing lossless raw codec stores every observed face point. Reuse is permitted only after the historical complete campaign, source graph, raw digests, decoder evidence, detector/runtime and unchanged producer contracts validate. A valid raw observation has face None or a finite plain numeric ndarray of exact shape (478,3), in observed SDK order. A nonempty different cardinality, present-empty array, semantic ndarray subclass, malformed/nonfinite array or timestamp is an error, not a missing observation or truncation opportunity. Existing raw values and historical receipts are read-only. The cardinality is supported by the retained real-source 478-point observations; compatibility must still be checked across reused recordings.

## Exact layout and normalization

Neural candidate input: Float32 [batch,30,1588]. Let C be the pose 11/12 shoulder midpoint, and W their nonzero 2D image-coordinate shoulder distance. Shoulder visibility and width requirements remain exactly hm153-v1.

- [0:153]: bit-exact hm153-v1 row from the unchanged shared packer, including its masks at indices 150,151,152.
- [153:1587]: all 478 face landmarks, SDK index order 0 through 477, XYZ row-major.
- [1587]: face presence mask, exactly 0 or 1.

For face point i, normalize X=(x_i-C_x)/W and Y=(y_i-C_y)/W. Normalize Z=(z_i-mean(z_0..z_477))/W in Float64 before Float32 conversion. Do not center face XY locally: retain head location relative to the shoulders. Do not rotate the face or remove expression geometry. Face Z has its own mean-relative origin; hand, pose and face depths are not one physical depth space. This mathematical convention does not establish metric depth.

If shoulders are unusable, output 1,588 zeros, including every mask. If shoulders are usable but face is None, retain the 153-value hands/pose row and zero the whole face block plus face mask. Such a row cannot enter an eligible capture. One missing hand remains permitted. Normalize into fresh arrays without mutating raw observations. Reject overflow/nonfinite final Float32 rows.

## Capture and temporal policy

Preserve the exact existing hand-observed interval: trim only before the first and after the last observed hand. Retain internal missing-hand/pose/face rows. Preserve source and bounded denominators. Preserve existing reason precedence: no_hands, too_few_observations, too_few_hand_observations, too_short, too_long, observation_gap, invalid_pose. After those checks, any missing face within the bounded interval yields invalid_face. Malformed face arrays always raise rather than becoming eligibility outcomes, including outside the bounded interval.

Otherwise require at least 8 actual observations, at least 4 hand-present observations, 400–5000 ms duration inclusive, maximum consecutive gap 250 ms, usable shoulders throughout and present exact-cardinality face throughout. Produce 30 nearest actual observations on the existing evenly spaced time grid with earlier-observation tie breaking and no interpolation. Every resampled row must have pose mask152=1 and face mask1587=1. Repeated rows are derived rows, not additional source observations. Missing face cannot be deleted, interpolated or bridged.

## Dataset rebuilding and evidence

Implement an additive preprocessing module and additive raw-campaign rebuilder; preserve accepted historical modules, tests, specifications and data. The existing trainer/evaluator are 153-feature tooling and are not accepted for this new contract.

Freeze the approved contract and implementation identities before actual rebuilding. First run a diagnostic on the literal lexicographically first clip_id of each frozen fit class. Persist all 50 selected IDs before raw feature preparation. No detector, optimizer or classifier runs. If all 50 do not remain eligible, preserve reasons and stop before a full build; obtain a new decision rather than changing selection or criteria.

After diagnostic feasibility and independent software review, rebuild all declared original recordings using the frozen fit/validation/test membership without augmentation, new windowing or label changes. Opening test raw observations solely for deterministic dataset transformation is not classifier evaluation or permission for test-driven design changes. Unknown signer IDs remain unknown. Retain every declared source, eligible/ineligible/error status, exact label/ID, partition, source/raw digest, observation/presence counts and reason. An error leaves an incomplete, non-gating output. A full build with no eligible fit or validation example for any approved class must retain denominator reports and a support-failure artifact without successful data_manifest.json.

Use fresh exclusive external outputs. Retain attempts and failures; never delete/reuse prior attempts. Write X_<partition>.npy Float32[N,30,1588], int64 labels, pickle-free clip IDs, class_metadata.json, capture_rows.json, eligibility.json, the exact contract copy, attempt and source bindings. Include source-level face cardinality and missingness counts, and a re-recording/ineligible list without collecting new data. A diagnostic is not a full bundle. Read back every published array/JSON and bind exact hashes plus current implementation, approved contract, historical campaign and graph identities. Completion publication must preserve the primary exception and revoke a failed new completion if final readback fails; persist a failure disposition when possible. A validator must reject failed/incomplete targets, not rely on filename presence. Do not claim crash/power-loss/hostile-writer atomicity.

Keep training_qualified=false, live_ready=false and model_evaluated=false. Require exact independent parent raw-to-tensor recomputation and per-class partition/support/count reconciliation before bounded data acceptance. Any missing class, failed source, absent negative data, unknown signer independence or physical/linguistic gate remains explicit.

## Required verification

Use the existing verified Python with -E -B and the approved scratch TMPDIR. Exercise strict vertical RED/GREEN slices for exact layout and face geometry; missing/malformed face and shoulders; nearest-time parity and internal invalid-face rejection; complete synthetic 50-class diagnostic/build/readback; provenance/tamper/failed-publication/failed-target and output-overlap denial; zero-support reporting; real subprocess CLI. Record coverage-only GREEN when unchanged helpers already satisfy a control. Preserve exact commands, exits, logs, JUnit and source digests. Run neighboring historical preprocessing and full migration/original training suites with baseline warnings disclosed. Obtain separate independent specification and quality verdicts before real rebuilding.
