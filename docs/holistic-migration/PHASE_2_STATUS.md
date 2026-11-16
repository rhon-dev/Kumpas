# Phase 2 — Holistic design status

## Current owner requirement — face-inclusive design pending

After the verification below, the owner required face features for all50 approved gestures and explicitly paused Phase3. The face-free `hm153-v1` implementation remains a verified historical candidate, **not the completed required final design**. A new exact face-inclusive contract, implementation and tests are still required before dependent progression. No new feature count, facial subset or linguistic validation is implied. See `OWNER_DECISIONS.md`; preserve the historical accepted contracts and receipts unchanged. No Phase3 execution is authorized now.

The sections below describe the earlier bounded software verification, not acceptance of the later face-inclusive requirement.

## Bounded result — November 16, 2026

The owner confirmed Phase 1 as approved and verified and requested Phase 2 of `HOLISTIC_MIGRATION_PLAN.md`. This means the migration plan's **Holistic design**, not PRD Phase 2 model training.

The required shared software already exists and has independent bounded acceptance. This continuation verified that implementation rather than replacing or rewriting it. **The candidate software is complete; linguistic sufficiency and physical anatomical confirmation are not accepted.** No new production code was needed.

Execution target remains `~/KumpasBuilds/holistic-migration`, branch `holistic-migration`, HEAD `4d901693642af5f572455b2c75ba095b0ec65c7f`. The original cloud checkout, Recognition V2 worktree, deployed assets and mobile code were not modified.

## Requirement evidence

| Requirement | Current evidence and boundary |
|---|---|
| Exact detector/runtime identity | Python 3.11.15; MediaPipe 1.2.0 Tasks `HolisticLandmarker`, synchronous VIDEO, CPU; NumPy 2.1.3; opencv-contrib-python 5.0.0.93. `requirements.txt` records direct installed versions, not a transitive lock. Fresh dependency check passed. |
| Versioned feature layout | Existing authoritative `FEATURES.md`: `hm153-v1`, Float32 `[batch,30,153]`; left XYZ63, right XYZ63, pose11–16 XYZ/visibility24, three presence/usability masks. No competing `contract.json` was introduced. |
| Shoulder normalization and separate depth origins | Accepted `features.pack_frame` centers image XY on shoulder midpoint, scales by 2D shoulder width, makes each hand Z wrist-local and pose Z shoulder-local. Tests cover invariance and exact block ordering. |
| Missingness and invalid shoulders | Absent hand blocks remain zero; one hand can be absent. Low-visibility pose points are zeroed. Unusable shoulders invalidate the row; resampling/capture rejects internal invalid-pose gaps. Tests cover malformed/nonfinite inputs and semantic ndarray rejection. |
| SDK left/right identity | Adapter and packing tests preserve SDK slots without swapping; RGB remains unmirrored. This is not physical anatomical verification. Owner confirmation remains open for the completed November 15 preview. No camera was reopened. |
| Face preservation and exclusion | Detector retains raw normalized face coordinates separately. Classifier features omit face under the explicit candidate policy. All-class facial/non-manual sufficiency remains unverified; no linguistic review is invented from label names or unit tests. A face-enabled variant needs a new exact contract and retraining. |
| Timestamp/capture policy | Existing accepted `sequence.py` and `CAPTURE_CANDIDATE.md`: actual presentation timestamps, 15 Hz admission, 8 actual bounded observations, 4 hand-present observations, 400–5000 ms duration, maximum 250 ms gap. These are fit-supported candidate rules, not human-annotated gesture boundaries. |
| Shared temporal primitive and parity scope | `resample_frames` uses 30 nearest actual observations, earlier tie breaking, no interpolation. Capture and codec/extraction tests exercise the common implementation and preserve masks. Tracking preview uses the same detector/packer. A trained offline/live classifier path and its replay acceptance are not claimed. |
| Recognition compatibility | All 50 approved outputs remain unchanged in scope. The 153-feature contract is incompatible with historical 258-feature weights. No old model was activated or treated as compatible. |

## Fresh verification

External evidence directory:

`~/KumpasBuilds/holistic-migration-data/evidence/phase-2-verification-20261116-1db68d9f852e/`

- `verification.json`: successful verification; all **15** source bindings from existing A/C acceptances matched; all **71** existing inventoried migration files remained unchanged throughout execution, before the separate documentation reconciliation.
- `preprocessing-tests.stdout.log`, `preprocessing-tests.xml`, `preprocessing-tests.command.json`: **237 test cases passed, 194 subtests passed**, no failures/errors/skips. Five modules: features, detector, sequence, extractor and dataset. The JUnit suite counter is 431 because it includes subtests; it is not 431 collected parent cases. No pytest warnings were reported in this run.
- `dependencies.*`: `uv pip check --python <existing interpreter>` exited 0 and reported 56 compatible packages on stderr.
- `runtime-and-blank-smoke.json`, `blank-smoke.*`: **two actual Tasks VIDEO calls** on synthetic blank RGB640×360 inputs at timestamps 0 and 67 ms; finite Float32153 all-zero rows, no detections, tracker closed. This checks native detector compatibility and invalid/missing output handling, not human tracking or recognition. Native feedback-manager warnings remain in stderr; this was not a warning-free detector run.
- `detector-binding.json`: bundle size **13,683,609 bytes**, SHA-256 `e2dab61191e2dcd0a15f943d8e3ed1dce13c82dfa597b9dd39f562975a50c3f8`, freshly matched to the existing download receipt. This is a recorded byte identity, not a vendor-published checksum.
- `protected-before.json`, `accepted-bindings.json`, before/after Git commands: accepted software unchanged; no tracked/index diff or HEAD change. Prior accepted reports were preserved.

Tests use synthetic fixtures. No real-source extraction, classifier optimization/inference/evaluation, webcam capture/recording, phone operation, export/activation, commit or push occurred.

## Remaining design/physical gates

1. Review all 50 gestures for facial/non-manual distinctions with qualified evidence. Until then, hm153-v1 is only the hands/upper-pose candidate, not a linguistically sufficient final contract.
2. Obtain owner confirmation that the November 15 preview overlay followed movement and SDK left/right matched physical hands. Unit tests establish slot preservation only.
3. Keep trained-classifier offline/live parity and recognition acceptance in their later phases. Existing software tests and a blank-frame detector smoke cannot close those gates.

This report reconciles stale Phase 2 checklist state. It does not reopen accepted A/C software, change their source-bound contracts, waive later gates, authorize real fitting or advance phone work.
