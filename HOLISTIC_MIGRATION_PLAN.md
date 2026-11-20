# Holistic Migration Plan

**Post-Phase4 continuation — November17,2026 UTC:** the owner approved offline public-data rejection calibration with no new recordings and no available expert/fresh signers. Keep the classifier/features/50 labels and all previous artifacts frozen; prepare additive reviewed tooling, deterministic public-source auditing, calibration-only extraction/pilot, validation-only threshold selection and separate challenge assessment only after a feasible freeze. Approved offline targets are <=1/20 eligible OOV false acceptance and >=9/10 correct accepted known validation overall; retain infeasibility without weaker criteria or test-based tuning. Existing Mac targets are approved for later trials, but no camera readiness, recording or phone permission is granted. Linguistic, signer-independent, true idle and physical acceptance remain open. See `docs/holistic-migration/{rejection-calibration-brief,REJECTION_STATUS}.md` and external `evidence/rejection-calibration-public-v1/owner-authorization.json`.

## Scope and verified starting point

**Phase 4 continuation — November 16, 2026:** the owner confirmed Phase 3 complete and requested Phase 4. The accepted hm1588-v1 dataset is the fixed input. Compatible additive model tooling/tests and independent review precede real tiny memorization, fresh all-50 training with validation-only selection, policy freezing and separately invoked exploratory reused-test scoring. Earlier model-phase withholding below is superseded only for this bounded sequence. No camera, phone, app edit, export/activation, participant work or Git publication. See `phase-4-brief.md`, `OWNER_DECISIONS.md` and `PHASE_4_STATUS.md` under `docs/holistic-migration/`.

**Current continuation — November 16, 2026:** the owner resumed Phase 3 and explicitly approved the full-face contract, tests, then data rebuilding. `FEATURES_FACE.md` defines the additive `hm1588-v1` candidate. Implement and independently review the prerequisite before deterministic raw reuse and fresh bundle creation. Historical hm153-v1 evidence remains preserved. No training, classifier evaluation, new extraction, camera/phone, model activation or Git publication is authorized. See `OWNER_DECISIONS.md`.

**Earlier owner update — November 16, 2026:** face features are required for all50 approved gestures. The existing face-free `hm153-v1` software/data checkpoint is historical and does not satisfy that requirement. Define and approve an exact new face-inclusive contract before dependent work. **Phase3 is paused at the owner's explicit request; do not execute it yet.** This checkpoint publication does not authorize new extraction, fitting, evaluation, camera or phone work. See `docs/holistic-migration/OWNER_DECISIONS.md`. Existing source-bound specifications and receipts are preserved, not silently rewritten.

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

**Status — November 16, 2026:** owner-approved face-inclusive hm1588-v1 prerequisite software accepted after complete independent specification/quality review and parent binding verification. See `FEATURES_FACE.md`, `face-data-review-1.json` and external `evidence/face-data-parent-20261116/software-acceptance.json`. The earlier hm153-v1 implementation and its receipts remain preserved. This is software acceptance, not linguistic/anatomical, model or live acceptance. The protected `PHASE_2_STATUS.md` retains the earlier historical checkpoint; this newer continuation supersedes its pending-contract status without rewriting its evidence. This is migration Phase 2, not PRD Phase 2 model training.

**Tasks:**
- [x] Inspect installed Tasks Holistic API and verify a downloaded official bundle with actual blank-frame VIDEO inference. Existing combined environment passes dependency checks.
- [x] Write the candidate contract before code: `docs/holistic-migration/FEATURES.md`.
- [x] Implement/test new `training/holistic_migration/{features,detector}.py`; Task A independently approved for specification and quality, then parent hash-verified and accepted. This is foundation acceptance only, not model/live acceptance.
- [x] Keep both21-point XYZ hands and pose11–16 XYZ/visibility, plus left/right/pose masks: **153** features, candidate Float32 `[batch,30,153]`.
- [x] Use shoulder-midpoint XY origin and 2D shoulder-width scale. Hand Z is wrist-local; pose Z is shoulder-local. Missing blocks stay zero. Bad shoulders invalidate the frame and break captures. No hip visibility requirement.
- [x] Keep raw normalized face observations separately; omit face from this initial candidate, not from Holistic detection. A face-enabled variant requires exact channels, a new contract and retraining. This implementation choice does not establish facial/non-manual sufficiency.
- [x] Provide one shared packer and nearest-observation30-row resampler. Accepted `sequence.py` implements the fit-supported candidate capture/15Hz policy in `CAPTURE_CANDIDATE.md`; tests cover missingness and invalid gaps. Tracking preview shares detector/packer; trained-classifier offline/live replay acceptance remains later work.
- [x] Record the owner requirement that all50 gestures include face; this is a scope decision, not completed expert linguistic validation.
- [x] Approve, implement, test and independently review exact face-inclusive hm1588-v1 under `FEATURES_FACE.md`; preserve hm153-v1 as historical evidence. Software acceptance does not establish linguistic/anatomical or model acceptance.
- [ ] Obtain physical anatomical-left/right and overlay-following confirmation for the completed owner-ready tracking session. Synthetic slot-preservation tests are not physical evidence.

**Files:** historical accepted features/detector/sequence modules and tests remain unchanged. This continuation adds reviewed face_features.py, face_dataset.py, their tests, FACE_DATA_README.md and the approved FEATURES_FACE.md contract. No original extractor or mobile changes.

**Output:** versioned shared preprocessing; fresh237 passing test cases plus194 passing subtests; two actual Tasks VIDEO calls on synthetic blank frames with the byte-verified detector. Runtime warnings are retained. Evidence: `../holistic-migration-data/evidence/phase-2-verification-20261116-1db68d9f852e/verification.json`. These are software/runtime checks, not recognition, linguistic or physical acceptance.

**Risks:** domain/framing differences, shoulder visibility, coordinate depth conventions, SDK anatomical handedness and face-dependent signs.

## 3. Data

**Current status — November16,2026:** owner-approved hm1588-v1 prerequisite and deterministic data-rebuild package complete and independently accepted within bounded data-engineering scope. Exact contract: `docs/holistic-migration/FEATURES_FACE.md`; handoff: `PHASE_3_STATUS.md`. All1,016 original sources remain declared;997 eligible tensors (649 fit/145 validation/203 test),19 invalid_face exclusions retained. All50 classes retain support, minimum7/1/4. Historical raw face observations were proven compatible, so no redundant detector extraction occurred. Parent acceptance: external `evidence/face-data-parent-20261116/dataset-acceptance.json`. No model, recording, anatomical/linguistic, physical or research acceptance; no training, classifier evaluation, camera or phone work.

**Tasks:**
- [x] Recover official version2 CSVs into the separate data directory and match publisher hashes/sizes. Verify813 selected train and203 selected test rows, all50 labels.
- [x] Finish downloading the original clips.zip and match publisher SHA-256/size before opening it as a complete source. Complete archive recovered, independently rehashed, and all1,016 selected videos fully decoded with zero errors and zero exact byte/pixel duplicate groups. See `docs/holistic-migration/DATA_READINESS.md`.
- [x] Retain the verified full original-video decode/hash/duplicate audit and freshly verify all1,016 raw-source/producer bindings, face cardinalities and all50-class support. Signer IDs remain unknown; no signer-independent claim.
- [x] Preserve the original pre-transform663/150/203 partition membership and official-test isolation; disclose historical test exposure. No splitting, augmentation or source substitution.
- [x] Reuse compatible complete Holistic raw observations, including face, for every approved gesture after provenance verification. Historical extraction used one detector per unrelated clip; no new detector execution was needed.
- [x] Retain raw observations/timestamps/presence;50/50 frozen-fit diagnostic sources passed before full rebuilding. Produce Float32[N,30,1588] with strict missing-face exclusion and no gap bridging. Preserve all19 failures in declared denominators.
- [ ] Resolve any replacement/re-recording of19 excluded sources under separate recording/storage approval. All50 classes remain supported without them; no collection is authorized or claimed.

**Files:** additive `training/holistic_migration/{face_features,face_dataset}.py`, their tests and `FACE_DATA_README.md`; `FEATURES_FACE.md` and `PHASE_3_STATUS.md`. Historical extractor/builder/codec/data remain unchanged. New external bundle `hm1588-canonical-bundle-20261116-v1` contains exact source/partition/label bindings, tensors, eligibility/exclusion ledgers and receipts; per-gesture and ineligible-source CSVs are retained in the parent evidence directory.

**Output:** accepted complete per-class source/eligible/failure inventory, frozen partition bindings and997 reproducible eligible tensors. Parent independently verified exact Float32 numerical equality for every tensor; complete independent campaign review passed. Retain19 exclusions in all1,016 declared sources. Phase3 acceptance itself did not authorize training; the separate Phase4 authorization below now governs compatible tooling and model execution. The historical153-feature trainer remains incompatible.

**Risks:** slow source download, unreadable/cropped clips, duplicates, insufficient signer diversity and absent real idle/unknown examples.

## 4. Model changes and all-gesture retraining

**Current status — November 16, 2026:** offline model execution, final independent specification/quality review and bounded parent handoff acceptance are complete. Receipt: external `all50-campaign-v1/phase4-offline-acceptance.json`. Actual rejection calibration and research/live/device acceptance remain open. The unchanged tiny gate passed at 8/8 and mean crossentropy 0.00025213306938494064 within 300 optimizer epochs; the original failed run remains preserved. Fresh all-50 training completed 69 epochs / 2,829 steps, selecting the earliest maximum-validation checkpoint at epoch 54 / 2,214 checkpoint steps. Parent and independent frozen-artifact review verified fit 644/649 and validation 142/145, with all 50 labels, exclusions and weak classes retained. Only after that review and parent acceptance, the separate exploratory reused-test command exited 0: 193/203 correct (95.073892%), macro-F1 0.949039. Parent independently recomputed every class from saved predictions without another test inference. The frozen checkpoint, exact labels/contract, full history, per-class reports, confusion matrices and rejection policy are retained under external `evidence/phase-4-20261116/`. Overall reused-test >=90% is met, but eight classes have recall below90%; SON and GRANDFATHER are each2/4. Rejection calibration and unknown/idle false acceptance remain explicitly unmeasured; no observed validation negatives exist. This is not untouched-holdout, linguistic, signer-independent, live or device acceptance. No test-driven retuning, model activation or Phase5/6 work. See `PHASE_4_STATUS.md` and external `all50-campaign-v1/reports/PHASE4_REPORT.md`.

**Tasks:**
- [x] Reuse the verified CNN-LSTM architecture with the frozen new input shape and the unchanged50-output mapping. Do not reuse old weights as if feature semantics matched.
- [x] Add new training/evaluation code and behavioral tests; do not reuse the unsafe historical notebook or deferred synthetic experiment runner as a real trainer.
- [x] Preserve a real-source tiny-overfit checkpoint and reload it to verify the result before full training. Accepted calibrated run:8/8,CE0.00025213306938494064; earlier failed run preserved.
- [x] Train all50 gestures with fixed configuration/seeds, fit-only masked augmentation, explicit unaugmented validation, early stopping and validation-only selection. Actual69 epochs; selected54.
- [x] Track all50 per-gesture accuracy/precision/recall/F1/support, macro-F1, confusion matrix, loss and exclusions. Match source and eligible denominators. Closed-set positive rejection is0 by policy; unknown false acceptance is unmeasured, not0.
- [x] Account for unavailable validation negatives without fabricated calibration: rejection calibration/FAR are unmeasured/null. Freeze model/policy before the separately invoked exploratory reused-test evaluation;193/203 correct. This does not establish calibrated rejection.
- [ ] Actual rejection calibration remains an unmet safety/acceptance item requiring separately approved annotated negative evidence; no usable negatives exist in this campaign.

**Files:** additive `training/holistic_migration/{face_train,face_evaluate,face_augmentation,batchnorm_calibration}.py`, corresponding tests and `FACE_TRAINING.md`; external checkpoints/configuration/reports. Historical migration trainer/evaluator and original model/export/reference assets remain untouched.

**Output:** an actually fitted all-gesture candidate, complete reports, provenance and a frozen policy—not synthetic optimizer evidence alone.

**Risks:** overfitting, weak classes hidden by aggregate accuracy, confident unknown acceptance and inadequate negative data.

## 5. MacBook webcam testing

**Tasks:**
- [ ] Create `training/holistic_migration/webcam.py` with the shared detector/features and a verified built-in-camera binding. No default-index or iPhone/Continuity fallback.
- [ ] Open a visible, bounded tracking-only check before expensive extraction/training. Mirror display only; save no webcam video by default.
- [ ] After a trained candidate exists, use self-paced explicit start/finish controls initially and emit one result per completed attempt. Reset invalid tracking; log prompted versus owner-confirmed performed signs separately.
- [ ] Test every gesture:10 confirmed attempts in normal conditions and10 under a separately defined changed condition. Include one-handed signs, occlusion, handedness, restart, idle and unknown signs.
- [ ] Measure processed FPS, final-observation-to-decision latency and collection time separately.

**Mac targets approved November17,2026 UTC; trials not executed:** per-gesture correct acceptance at least9/10 in each condition; no idle false acceptance in5minutes; at most1/20 unknown accepts; at least15 processed FPS and p95 decision latency at most300ms during10minutes, no crash. Offline/live replay features must agree within a declared Float32 tolerance. Manual-only capture cannot establish autonomous idle/unknown behavior; identify which path is actually exercised.

**Failure action:** record the failed gesture/condition, distinguish tracking/capture/features/rejection/classification, repair using fit/validation data, then repeat all-gesture regression. Do not tune on frozen final-test failures.

**Files:** new webcam/capture code and streaming tests; external operational/trial reports only with approved storage scope.

**Output:** runnable Mac-only preview/recognizer and owner-performed per-gesture acceptance evidence. Open camera or passing mocks alone are insufficient.

**Risks:** camera permission/identity, slow processing, domain shift, small single-user sample and unresolved linguistic/anatomical validity.

## 6. Phone readiness — planning only

**November 17, 2026 — planning delivered; phone entry remains blocked.** Owner requested `start phase 6`. `docs/holistic-migration/PHONE_READINESS.md` binds the actual frozen hm1588-v1 candidate, exact50-label order, historical uncalibrated policy and Holistic bundle; defines fixed-batch Float32 export/parity requirements, source-level built-in/Flex and SDK risks, proposed separate cost budgets and the blocked phone-entry checklist. Read-only artifact/scope evidence: external `evidence/phase-6-planning-20261117/`. No classifier conversion/inference, SDK build/device query, app edit, camera or activation. Phase5 and rejection acceptance are not waived; exact conversion/SDK compatibility and physical performance remain unverified.

**Tasks:**
- [x] Document fixed input/label/feature/policy identities, source-level TFLite compatibility investigation, proposed size/memory budgets, future probability/top1/rejection parity and quantization risks in `PHONE_READINESS.md`. Numerical budgets/tolerances require agreement; exact artifact conversion remains separately approval-gated.
- [x] Separate classifier cost from Holistic detector cost. Mac results do not establish sustained phone speed or thermal behavior.
- [x] Publish the prerequisite checklist for source/data provenance, all-gesture offline/Mac gates, frozen model/contract/labels/policy, rollback, exact target SDK support and explicit phone-phase approval. Checklist publication is not satisfaction of its open gates.

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
- Mac acceptance targets are approved; real owner-confirmed attempts, current camera readiness and any recording/storage permission remain required before trials.
- Any unpublished local modifications that must be reconciled once cloud access is restored?
- Training duration and extraction budget will be estimated from real-source pilot timing before a long run.
