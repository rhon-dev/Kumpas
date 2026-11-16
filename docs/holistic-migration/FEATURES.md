# Candidate shared Holistic contract: hm153-v1

This is an isolated Mac-only candidate implementing the owner's approved migration plan. It is not compatible with historical 258-feature classifiers or references, and has not passed data, linguistic, live, or mobile acceptance. Preserve every approved class and its literal label/ID. The baseline is already Holistic during Python extraction; the change is a new shared training/Mac contract, not a claim that the original extractor was hand-only.

## Detector and source

Use the available MediaPipe Tasks Holistic API, not independent Pose/Hands and not legacy Solutions. The inspected environment is `~/.kumpas-venvs/rv2-holistic-tf-20261101`, Python 3.11.15 / MediaPipe 1.2.0 / NumPy 2.1.3 / opencv-contrib-python 5.0.0.93 / TensorFlow 2.19.0. Verify runtime with an official compatible bundle and actual frames separately. No installed-package patches or old-version private packet adapters.

Feed RGB uint8 H×W×3 unmirrored images. Use VIDEO mode in both file and synchronous webcam paths, with strictly increasing integer millisecond timestamps. Create a new detector per unrelated clip/session. Return normalized image-coordinate arrays for pose (33×4 including visibility), left hand (21×3) and right hand (21×3). Missing components are explicit `None`, not generated landmarks. Retain raw face output separately when available; do not assume the Tasks face count equals the legacy 468. World coordinates never enter this candidate.

## Exact Float32 layout

- `[0:63]`: left hand, 21 points in SDK order, XYZ row-major.
- `[63:126]`: right hand, 21 points in SDK order, XYZ row-major.
- `[126:150]`: pose indices 11,12,13,14,15,16 in that order, XYZ/visibility row-major.
- `[150]`: left hand present (0 or 1).
- `[151]`: right hand present (0 or 1).
- `[152]`: usable pose (0 or 1).

Total: 153 features. Candidate neural input: Float32 `[batch,30,153]`; output: the 50 existing dense class indices ordered by ascending original dataset ID. For example dense 25 maps to original 49, `TODAY`. Never equate dense and original IDs.

Hands and pose are the initial classifier features. Face coordinates are deliberately excluded from this candidate, not proven unnecessary for FSL. Facial/non-manual sufficiency remains an open linguistic/validation question; any face-enabled contract needs exact indices/channels, a new feature version, and retraining. Do not promote this candidate if it fails relevant gestures.

## Normalization and invalid frames

1. Require finite **plain `numpy.ndarray`** arrays and exact component shapes. Semantic ndarray subclasses (including MaskedArray and matrix) are unsupported and must raise a component-specific ValueError before normalization; never coerce away a mask. Ordinary strided/read-only ndarray views remain supported. Reject malformed input rather than truncating or guessing.
2. Require both shoulder visibilities at least 0.5 and finite 2D shoulder width at least 0.0001. A missing/unreliable pose gives an invalid frame: 153 zeros, including masks. Do not preserve raw unnormalized hands as if normalized.
3. Image XY center is the midpoint of shoulders 11/12. Divide XY offsets by 2D shoulder width. No hip points are required.
4. For each hand's Z, subtract that hand's wrist Z before dividing by shoulder width. For pose Z, subtract the shoulder-midpoint Z before scaling. These are distinct depth origins, not a shared physical coordinate system.
5. Pose points below visibility 0.5 are entirely zeroed; otherwise retain visibility unchanged. A missing hand's whole 63-value block remains zero after all transformations; its presence mask is zero. An absent other hand does not invalidate a one-handed gesture.
6. Both hands absent with reliable shoulders is a valid idle observation, not a human-labeled negative gesture. Anatomy must be checked independently; until then the names mean SDK left/right.

## Temporal primitive

Use one shared Float32 nearest-observation time-resampler to 30 rows. Require at least two actual observations, finite vectors, usable pose on every supplied row, and strictly increasing nonnegative integer timestamps. Use evenly spaced target times; choose the nearest original observation with earlier-frame tie breaking. Never interpolate a missing hand into existence. Repeated derived rows are not additional observed camera frames. Capture eligibility/minimum observations, activity segmentation, rate and duration still require fit-only feasibility before any full training run. Invalid observations must break captures; callers may not remove a gap and silently concatenate across it.

## Tests before implementation

Cover exact layout/count/dtype, geometric invariance, wrist-local versus pose depth origins, individual missing hands, no pose, unreliable shoulders, low-visibility pose zeroing, all-idle observations, malformed/nonfinite inputs, timestamp validation, nearest-time tie breaking and preservation of absence through resampling. Detector tests must use supplied SDK-shaped results for conversion and missing-component behavior; a separate real blank-image smoke verifies runtime, not recognition.
