# Holistic Migration Plan

## Scope and verified starting point

**Owner update — November 16, 2026:** face features are required for all50 approved gestures. The existing face-free `hm153-v1` software/data checkpoint is historical and does not satisfy that requirement. Define and approve an exact new face-inclusive contract before dependent work. **Phase3 is paused at the owner's explicit request; do not execute it yet.** This checkpoint publication does not authorize new extraction, fitting, evaluation, camera or phone work. See `docs/holistic-migration/OWNER_DECISIONS.md`. Existing source-bound specifications and receipts are preserved, not silently rewritten.

Owner-approved execution: original Kumpas project, all **50 approved gestures**, CNN-LSTM retained, **built-in MacBook webcam only**. No phone implementation/testing, app edits, participant processing, model activation or merge. The November16 owner decision separately authorizes checkpoint publication on the isolated branch only.

Cloud checkout stays unchanged. Execution uses a fresh clone of the supplied original GitHub repository at `~/KumpasBuilds/holistic-migration`, local branch `holistic-migration`, baseline commit `4d901693642af5f572455b2c75ba095b0ec65c7f`. Unpublished/ignored local assets are not assumed recovered. Data and models live separately at `~/KumpasBuilds/holistic-migration-data`.

**Important correction:** published Python extraction already uses Holistic: pose33×4 + face468×3 + two hands21×3 = **1,662** features. The no-face classifier uses pose + both hands = **258**, not hands-only63. Android currently uses separate Pose/Hands detectors. This migration builds one shared Holistic training/Mac path with a newly trained candidate, not a renamed existing model.

## 1. Current state audit

**Status:** source audit complete for the published snapshot. See `docs/holistic-migration/CURRENT_STATE_AUDIT.md` and `PROGRESS.md` for evidence and limits.

**Tasks:**
- [x] Read data import/extraction, sequence construction, model/training/export and native inference contracts.
- [x] Verify sorted original-ID mapping for all50 classes against the application map and official CSVs.
- [x] Verify current sequence default30, full1662/no-face258 input, hip/torso normalization and whole-clip sampling.
- [x] Verify CNN-LSTM: Conv1D64/128 with BatchNorm and MaxPool2; LSTM128/64; Dense128; Dense50 softmax; dropout0.4.
- [x] Run existing training tests:51 passed, with disclosed runtime/deprecation warnings.
- [ ] Verify actual binary signatures if historical ignored assets are later recovered; source signatures are not binary verification.

**Files:** audit documentation only; existing source remains unchanged.

**Output:** verified source contract and complete exact class mapping. Extraction occurs in `training/preprocessing/extract_landmarks.py`; native inference reference is `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/VisionEngine.kt`.

**Risks:** the original cloud copy may contain unpublished work; historical notebook leakage, individual-hand augmentation corruption, tracker reuse, missing-pose disagreement and model/export limitations must not enter the new path silently.

## 2. Holistic design

**Status — November 16, 2026:** historical face-free candidate software complete and freshly reverified. The owner now requires face for all50 gestures, so the required final design is incomplete pending an exact face-inclusive contract and tested implementation. Existing independently accepted A/C implementation is preserved, not relabeled face-inclusive. Physical anatomical confirmation remains open. See `docs/holistic-migration/PHASE_2_STATUS.md`. This section is migration Phase 2, not PRD Phase 2 model training.

**Tasks:**
- [x] Inspect installed Tasks Holistic API and verify a downloaded official bundle with actual blank-frame VIDEO inference. Existing combined environment passes dependency checks.
- [x] Write the candidate contract before code: `docs/holistic-migration/FEATURES.md`.
- [x] Implement/test new `training/holistic_migration/{features,detector}.py`; Task A independently approved for specification and quality, then parent hash-verified and accepted. This is foundation acceptance only, not model/live acceptance.
- [x] Keep both21-point XYZ hands and pose11–16 XYZ/visibility, plus left/right/pose masks: **153** features, candidate Float32 `[batch,30,153]`.
- [x] Use shoulder-midpoint XY origin and 2D shoulder-width scale. Hand Z is wrist-local; pose Z is shoulder-local. Missing blocks stay zero. Bad shoulders invalidate the frame and break captures. No hip visibility requirement.
- [x] Keep raw normalized face observations separately; omit face from this initial candidate, not from Holistic detection. A face-enabled variant requires exact channels, a new contract and retraining. This implementation choice does not establish facial/non-manual sufficiency.
- [x] Provide one shared packer and nearest-observation30-row resampler. Accepted `sequence.py` implements the fit-supported candidate capture/15Hz policy in `CAPTURE_CANDIDATE.md`; tests cover missingness and invalid gaps. Tracking preview shares detector/packer; trained-classifier offline/live replay acceptance remains later work.
- [x] Record the owner requirement that all50 gestures include face; this is a scope decision, not completed expert linguistic validation.
- [ ] Define and approve an exact new face-inclusive contract, then implement/test it before dependent progression. Preserve hm153-v1 as historical evidence, not the required final input.
- [ ] Obtain physical anatomical-left/right and overlay-following confirmation for the completed owner-ready tracking session. Synthetic slot-preservation tests are not physical evidence.

**Files:** existing accepted features/detector/sequence modules and tests; candidate specifications. This continuation changed only status documentation. No original extractor or mobile changes.

**Output:** versioned shared preprocessing; fresh237 passing test cases plus194 passing subtests; two actual Tasks VIDEO calls on synthetic blank frames with the byte-verified detector. Runtime warnings are retained. Evidence: `../holistic-migration-data/evidence/phase-2-verification-20261116-1db68d9f852e/verification.json`. These are software/runtime checks, not recognition, linguistic or physical acceptance.

**Risks:** domain/framing differences, shoulder visibility, coordinate depth conventions, SDK anatomical handedness and face-dependent signs.

## 3. Data

**Current status — November16,2026:** paused by explicit owner instruction. Existing hm153-v1 data evidence below is historical. Do not begin new extraction, rebuilding or compatibility migration until the face-inclusive prerequisite and a fresh execution go-ahead are resolved.

**Tasks:**
- [x] Recover official version2 CSVs into the separate data directory and match publisher hashes/sizes. Verify813 selected train and203 selected test rows, all50 labels.
- [x] Finish downloading the original clips.zip and match publisher SHA-256/size before opening it as a complete source. Complete archive recovered, independently rehashed, and all1,016 selected videos fully decoded with zero errors and zero exact byte/pixel duplicate groups. See `docs/holistic-migration/DATA_READINESS.md`.
- [ ] Verify every selected recording, readable/decodable video, duplicate groups, class support and source digests. Keep signer IDs unknown where unavailable; do not claim signer independence.
- [ ] Split originals/groups before transforms. Keep official test sources out of fit/validation; disclose past test exposure. Do not copy augmented siblings across splits.
- [ ] Re-extract every gesture with one new shared detector instance per unrelated clip. Bind outputs to source, detector and contract; filename existence is not a valid cache receipt.
- [ ] Retain raw observations, timestamps and presence; build candidate30-row sequences only after fit-only observability/duration diagnostics. Invalid gaps must not be removed and concatenated away.
- [ ] Re-record only where source quality/coverage fails, after explicit recording/storage approval. Hand-only arrays cannot recover missing pose/face; verified raw videos can be reused.

**Files:** new `training/holistic_migration/{extract,build_dataset}.py` and tests; external manifests, `landmarks/<clip_id>.npz`, `splits/{fit,validation,test}.json`, labels and receipts.

**Output:** complete per-class source/eligible/failure inventory, partition bindings and reproducible tensors. Retain failures in declared denominators.

**Risks:** slow source download, unreadable/cropped clips, duplicates, insufficient signer diversity and absent real idle/unknown examples.

## 4. Model changes and all-gesture retraining

**Tasks:**
- [ ] Reuse the verified CNN-LSTM architecture with the frozen new input shape and the unchanged50-output mapping. Do not reuse old weights as if feature semantics matched.
- [ ] Add new training/evaluation code and behavioral tests; do not reuse the unsafe historical notebook or deferred synthetic experiment runner as a real trainer.
- [ ] Preserve a real-source tiny-overfit checkpoint and reload it to verify the result before full training.
- [ ] Train all50 gestures with fixed configuration/seeds, fit-only masked augmentation, explicit unaugmented validation, early stopping and validation-only selection.
- [ ] Track per-gesture accuracy/precision/recall/F1/support, macro-F1, confusion matrix, loss, exclusions, valid rejection and unknown false acceptance. Match source and eligible denominators.
- [ ] Calibrate rejection with observed validation negatives; mark unmeasured if no usable negatives. Freeze model/policy before a separately invoked exploratory reused-test evaluation.

**Files:** new `training/holistic_migration/{train,evaluate}.py` and tests; external checkpoints/configuration/reports. Original model/export/reference assets remain untouched.

**Output:** an actually fitted all-gesture candidate, complete reports, provenance and a frozen policy—not synthetic optimizer evidence alone.

**Risks:** overfitting, weak classes hidden by aggregate accuracy, confident unknown acceptance and inadequate negative data.

## 5. MacBook webcam testing

**Tasks:**
- [ ] Create `training/holistic_migration/webcam.py` with the shared detector/features and a verified built-in-camera binding. No default-index or iPhone/Continuity fallback.
- [ ] Open a visible, bounded tracking-only check before expensive extraction/training. Mirror display only; save no webcam video by default.
- [ ] After a trained candidate exists, use self-paced explicit start/finish controls initially and emit one result per completed attempt. Reset invalid tracking; log prompted versus owner-confirmed performed signs separately.
- [ ] Test every gesture:10 confirmed attempts in normal conditions and10 under a separately defined changed condition. Include one-handed signs, occlusion, handedness, restart, idle and unknown signs.
- [ ] Measure processed FPS, final-observation-to-decision latency and collection time separately.

**Proposed targets, pending owner approval before evaluation:** per-gesture correct acceptance at least9/10 in each condition; no idle false acceptance in5minutes; at most1/20 unknown accepts; at least15 processed FPS and p95 decision latency at most300ms during10minutes, no crash. Offline/live replay features must agree within a declared Float32 tolerance. Manual-only capture cannot establish autonomous idle/unknown behavior; identify which path is actually exercised.

**Failure action:** record the failed gesture/condition, distinguish tracking/capture/features/rejection/classification, repair using fit/validation data, then repeat all-gesture regression. Do not tune on frozen final-test failures.

**Files:** new webcam/capture code and streaming tests; external operational/trial reports only with approved storage scope.

**Output:** runnable Mac-only preview/recognizer and owner-performed per-gesture acceptance evidence. Open camera or passing mocks alone are insufficient.

**Risks:** camera permission/identity, slow processing, domain shift, small single-user sample and unresolved linguistic/anatomical validity.

## 6. Phone readiness — planning only

**Tasks:**
- [ ] Document fixed input/label/feature/policy identities, TFLite operator compatibility, size/memory budgets, conversion probability/top1/rejection parity and quantization risks.
- [ ] Separate classifier cost from Holistic detector cost. Mac results do not establish sustained phone speed or thermal behavior.
- [ ] Require source/data provenance, all-gesture offline/Mac gates, frozen model/contract/labels/policy, rollback, exact target SDK support and explicit phone-phase approval.

**Files:** planning documentation only. Existing TFLite exporters, `app/` and reference assets remain unchanged.

**Output:** phone-entry checklist. No device query, build, installation, phone camera or model activation.

**Risks:** unsupported native Holistic runtime, expensive face processing, delegate/operator incompatibility, mirror/rotation differences and thermal throttling.

## Execution order

1. Use the verified published-source audit; preserve original local work.
2. Test the candidate shared foundation and complete source recovery.
3. Verify built-in-camera tracking and fit-only feature/capture feasibility.
4. Freeze partitions/contracts, re-extract all gestures and validate outputs.
5. Prove real tiny-overfit, train/select/calibrate using fit/validation, then freeze and evaluate.
6. Complete owner-performed Mac trials; retain failures and open gates honestly.
7. Review phone planning only; do not begin phone work.

## Open questions and gates

- Does future scope expand beyond the approved50 signs? Current execution does not assume105 classes.
- Which classes need facial/non-manual features? The initial153 candidate cannot establish linguistic sufficiency.
- May new live recordings or landmark sequences be retained, and under what storage/consent rules?
- Are proposed Mac acceptance targets approved? Real owner-confirmed attempts still require participation.
- Any unpublished local modifications that must be reconciled once cloud access is restored?
- Training duration and extraction budget will be estimated from real-source pilot timing before a long run.
