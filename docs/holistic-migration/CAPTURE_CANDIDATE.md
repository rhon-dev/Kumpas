# Candidate capture contract: hm153-capture-v1

## Status and evidence boundary

This is a candidate recorded-input/streaming contract for the approved 50-class Mac migration. It supplements, and does not rewrite, accepted `FEATURES.md` or historical receipts. The owner explicitly deferred the human webcam check while authorizing continued offline work. No physical, anatomical, linguistic or recognition acceptance is implied.

Parameter choices use fit-only feasibility, not validation/test predictions: the retained 50-class fit pilot had 3,057 observations, usable shoulders/pose on every observation, at least 14 hand-present observations in each selected clip and at least 61 consecutive usable-pose observations. Those clips are diagnostic examples, not an exhaustive per-class quality guarantee. The choices below are not retrospective preregistration or validated gesture boundaries.

## Image and observation clock

- Use unmirrored RGB uint8, explicitly resized to width640/height360 with OpenCV INTER_AREA and made contiguous. File BGR and native BGRA are color adapters only; both eventual classifier paths must call the same shared RGB resize, observation clock and capture preparation.
- Candidate detector cadence is15Hz. Use actual presentation timestamps, not an assumed frame count/FPS clock. OpenCV POS_MSEC was exercised on frozen fit `clips/0/0.MOV`:245 decoded frames, finite strictly increasing presentation times, beginning0ms and ending4066.6666666666665ms. This single check does not establish every video's timestamp behavior.
- Round actual finite nonnegative video presentation milliseconds to built-in integer milliseconds; reject duplicates/backward times instead of inventing a new timestamp. Native camera packets already supply integer milliseconds.
- Every source timestamp must be strictly increasing, including observations not admitted to detection. First frame establishes the clock origin and is admitted. Thereafter admit at most one actual frame for each due15Hz slot, allowing0.5ms for integer timestamp quantization. Skip missed slots without synthesizing frames. One integer implementation computes `due_slot=((2*elapsed_ms+1)*15)//2000`; admit only when it reaches the next slot, then advance beyond all due slots. Reset per unrelated clip/session.
- Create a fresh accepted `HolisticDetector` per clip/session. VIDEO mode, original normalized image landmarks and explicit missing components remain unchanged. No mirroring, world-coordinate substitution or legacy decoder patch.

## One bounded observed capture

1. Validate all supplied RawFrames and strictly increasing timestamps using the accepted feature semantics. Malformed/nonfinite source arrays are errors, not ineligible examples disguised as valid zeros.
2. Find the first and last actual observation with at least one SDK hand present. Remove only leading/trailing handless observations. This is a detector-derived hand-observed interval, not a human annotation of sign start/end. No hand observations means ineligible.
3. Retain every observation inside those bounds, including observations with missing hands. Never delete internal tracking-loss rows or splice separated runs.
4. Require at least8 actual observations and at least4 hand-present observations inside the interval; duration400–5000ms inclusive; maximum consecutive observation gap250ms inclusive; usable shoulders/pose on every retained row. Reject the whole interval when one of these conditions fails. Do not select a convenient valid subwindow from around an internal invalid pose.
5. A missing individual hand is allowed and keeps its63-value zero block/mask. Both hands absent with usable pose remains an actual masked observation, not an idle label or fabricated detection. An invalid pose is different and makes the bounded capture ineligible.
6. Call the accepted `resample_frames(...,steps=30)` once eligibility is established. Output is plain Float32[30,153]. Nearest-observation repetition is derived resampling, not additional camera observations. Never interpolate missing hands into existence.

Return an explicit ineligible reason without a tensor when coverage fails. Keep the source in declared denominators. No placeholder zero sequence, replacement clip, hidden crop or class removal is allowed.

## Provenance and later live use

Raw extraction retains actual timestamps, pose/hands and raw face output losslessly as numeric arrays with explicit presence. Do not truncate a478-point Tasks face to468 or assume one face cardinality. Raw arrays remain outside Git. Raw missing slots may be zero-filled only with explicit presence metadata that reconstructs None exactly.

The extraction/data manifest binds current contract/source files, working runtime, detector bundle, original class map, frozen membership, source-byte and completed-decode audits, every raw output and every final tensor artifact. Historical manifests with pending-at-creation text remain unchanged; the later completed audit is an explicitly linked companion.

Full extraction requires a reviewed pipeline. Full training additionally requires all-class eligible support and retained real-source tiny-overfit proof. Use fit-only augmentation later; none belongs in canonical dataset building. No test-driven policy selection.

A later webcam classifier must use this exact image/clock/capture/feature implementation and an explicitly bounded manual capture before any automatic gate is adopted. A source-video replay can establish preprocessing parity, not live handedness, sign correctness or performance. The current tracking-only preview is not a trained classifier and is not a source of live training samples.
