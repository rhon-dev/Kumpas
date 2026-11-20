# Feature contracts for the hands-and-arms round (hm211-v1, hm337-v1)

Status: frozen for RETRAINING_PLAN.md Phases 3-5 (owner request "do phase 3-4-5", 2026-11-20). Changes need a new version; v1 is never edited. `hm153-v1` (`features.py`) and `hm1588-v1` (`face_features.py`) are unchanged.

Implementation: `training/holistic_migration/retraining/features_v2.py`. Bundles: `holistic-migration-data/evidence/retraining-v1/bundles/v1/` (fit and validation), test built only in Phase 5.

## Width correction

The plan's section 4 lists 19 face anchor points but calls the result 214 values (20 points). The listed points are used exactly, so the widths are 211 (not 214) and 337 (not 340). No point was added.

## hm211-v1 (one observation)

| Columns | Content |
|---|---|
| 0-152 | hm153-v1 exactly (`features.pack_frame`): left hand 63, right hand 63, arms 24, masks left/right/pose |
| 153-209 | 19 face anchors x 3, in this order: 10, 1, 152, 234, 454, 33, 133, 362, 263, 70, 105, 107, 336, 334, 300, 61, 291, 13, 14 |
| 210 | face mask |

- Anchor XY: `(face_xy - shoulder_midpoint_xy) / shoulder_width_2d`. Anchor Z: `(face_z - mean z of all 478 face points) / shoulder_width_2d`. These are the same Float64 expressions as hm1588-v1, so each anchor value is bit-identical to the matching hm1588 column whenever both exist.
- Face mask is 1 when the pose is usable (column 152 is 1) and the observation has a 478-point face. Otherwise columns 153-210 are 0.
- A face with another point count is rejected (error), as in hm1588.
- Unusable shoulders zero the whole row, as in hm153.

## Capture (sequence of 30)

- Eligibility, reasons, reason order and the hand interval are exactly `sequence.prepare_capture` (hm153). **The face is optional**: a missing face is never a reason to exclude a clip.
- The 30 rows are the actual observations chosen by the same nearest-observation integer-grid rule (ties pick the earlier observation). No interpolation.

## hm337-v1

| Columns | Content |
|---|---|
| 0-210 | hm211-v1 |
| 211-273 | left hand, hand-local |
| 274-336 | right hand, hand-local |

- Computed from the Float32 hm211 row of each of the 30 rows (Float64 arithmetic, Float32 result). Because hm153 coordinates are a uniform scale and shift of image coordinates, this equals computing from image coordinates, up to Float32 rounding.
- For a present hand `h` (21 x 3, hm153 values): `d = hypot(h[9].x - h[0].x, h[9].y - h[0].y)` (wrist to middle-finger knuckle). Local XY `= (h.xy - h[0].xy) / d`; local Z `= h.z / d` (hm153 hand Z is already wrist-relative).
- Absent hand (mask 0), or `d < 1e-6`: the 63 local values are 0. The mask is not changed.
- Because it is a function of the tensor, training computes it after augmentation.

## Not part of the contract

Augmentation (`retraining/augment_v2.py`) and the face-reliance views are training and evaluation tools, not features.
