# Kumpas retraining plan: hands and arms first

**Status: plan only. No phase has started.** Written November 19, 2026 after reading the code, data and evidence named in section 2. No code, model, data or setting was changed. Each phase starts only after the owner approves this plan and that phase.

## 1. Goal and ground rules

**Goal:** retrain the 50-sign classifier and improve how well it recognizes signs. It should recognize mainly from both hands (21 landmarks each) and the arms (shoulders, elbows and wrists). The face stays as an input with lower weight. "Better" means measurably better than the current model, per sign and not only overall. It must be measured on fair data, including the owner's own signing on the MacBook webcam.

Ground rules for every phase:

1. **The current model is the baseline and is never overwritten.**
   - Frozen baseline: `../holistic-migration-data/evidence/phase-4-20261116/full-source-v1/model.keras`, SHA-256 `ea50489a27353cbf4f4e9b53b1a6252fa7c5c6a9f0021660347f7dcc1b1cda47`.
   - It comes with its label file, feature contract (`hm1588-v1`), policy and Holistic detector (`e2dab611…`).
   - Every phase checks these hashes at its start and end.
   - The live viewer keeps using the baseline until the owner approves a switch (Phase 6).
2. **New outputs only.** New data, models and reports go to fresh directories under `../holistic-migration-data/evidence/retraining-v1/`. Existing bundles, campaigns, receipts and reports are read-only. Existing training and recognition code is not edited. New code goes into a new package, `training/holistic_migration/retraining/`.
3. **The official test split stays sealed until Phase 5.** It is then used once, for both models, as an exploratory comparison. It never chooses features, settings or checkpoints. It is already a reused test (weak point 11).
4. **Every change is compared with the baseline per sign**, using the rules in section 5.
5. **Every experiment is logged** with its config, seeds, data identities and results, in an append-only ledger. Nothing is deleted or silently overwritten (PRD §7).
6. **Same scope as today:**
   - the same 50 signs and label order;
   - MediaPipe Holistic and the CNN-LSTM family;
   - the MacBook built-in camera only;
   - landmarks only, never video;
   - no phone, app, export or participant work.

## 2. How the system works today

### 2.1 Landmark detection

- `training/holistic_migration/detector.py` runs the MediaPipe Tasks Holistic Landmarker in VIDEO mode on CPU. The bundle is `holistic_landmarker.task`; blendshapes and segmentation are off. Each clip or live session gets a fresh tracker.
- Each observation returns:
  - 33 pose landmarks (x, y, z, visibility);
  - 21 landmarks per hand (x, y, z), for the SDK "left" and "right" hand;
  - 478 face landmarks (x, y, z, including the iris points).
- Training clips are FSL-105 videos: 640×360, 60 fps, about 4.1 s each.
- The live camera is the built-in 1280×720 camera, resized to 640×360 and not mirrored for the detector.
- Both paths keep 15 observations per second (`sequence.ObservationClock`).

### 2.2 Features

- `features.pack_frame` (hm153-v1) produces 153 values per observation:
  - left hand 63 and right hand 63 values (XY relative to the shoulder midpoint divided by shoulder width; Z relative to the wrist);
  - pose landmarks 11–16, which are both shoulders, elbows and wrists (xyz plus visibility; points with visibility below 0.5 are zeroed): 24 values;
  - 3 masks (left hand, right hand, pose).
  - Unusable shoulders zero the whole row.
- `face_features.pack_frame` (hm1588-v1) is the current model input. It adds all 478 face points to those 153 values: 1,434 values (XY shoulder-relative, Z relative to the face mean) plus a face mask.
- **Share of the current input:**

  | Part | Values | Share |
  |---|---|---|
  | Face | 1,435 | 90% |
  | Both hands | 126 | 8% |
  | Arms | 24 | 1.5% |

### 2.3 From observations to one model input

`face_features.prepare_capture` (built on `sequence.prepare_capture`) does the following:

1. Trims the observations to the interval from the first to the last observation with a hand.
2. Requires:
   - at least 8 observations, at least 4 of them with a hand;
   - 0.4–5 s duration;
   - no gap over 250 ms;
   - usable shoulders throughout;
   - for hm1588 only, a face in every observation.
3. Takes 30 nearest observations on an even time grid, giving Float32 [30, 1588].

In FSL-105 fit and validation clips (794 eligible), the hand interval lasts 1.0–2.0 s (median 1.33 s). In most clips, hands are out of view for about 1.6 s before it and 0.9 s after it. This matches the live hand-in/hand-out capture.

### 2.4 Data and splits

- **Source:** FSL-105 (Mendeley, CC BY 4.0). We use 50 of its 105 signs, 1,016 clips. The dataset card says adult deaf signers recorded it on a blue background.
- **Official split:** 813 train clips (14–17 per sign) and 203 test clips (4–5 per sign). The CSVs carry no signer IDs. The test split is random over clip numbers, so the same signers appear in every split.
- **Validation split:** `candidate-partitions-v1.json` splits the official train clips per sign by a seeded shuffle: 663 fit and 150 validation (exactly 3 per sign).
- **hm1588 bundle** (`hm1588-canonical-bundle-20261116-v1`): 997 eligible clips (649 fit / 145 validation / 203 test).
  - 19 clips are excluded as `invalid_face`: the face is missing somewhere inside the hand interval.
  - Excluded per sign: SON 6, GOOD MORNING 4, BLACK 4, GRANDFATHER 3, SLOW 2.
- **hm153 bundle** (`hm153-canonical-bundle-20261113-accepted-c1`): hands and arms only, same split, all 1,016 clips eligible.
- **Raw observations:** all of them, including every face point, are stored losslessly in `hm153-full-campaign-20261113-accepted-c1`. New feature sets can be rebuilt without running the detector again.
- **Duplicated clips with conflicting labels:** the rejection-calibration audit found identical videos published under two labels: FOUR/SEVEN (twice), GRANDMOTHER/COUSIN and PARENTS/UNCLE. Within our 50 signs this affects:
  - fit clip `clips/23/6.MOV` (FOUR);
  - fit clip `clips/57/9.MOV` (GRANDMOTHER);
  - test clip `clips/23/8.MOV` (FOUR).

### 2.5 Training

- **Model** (`face_train.py`): Conv1D 64 → BatchNorm → Conv1D 128 → BatchNorm → MaxPool 2 → LSTM 128 → Dropout 0.4 → LSTM 64 → Dropout 0.4 → Dense 128 → Dropout 0.4 → Dense 50 softmax.
  - 526,194 parameters; Adam 0.001; seed 20260705.
- **Training data:** each fit clip plus one copy rotated by a seeded angle within ±5° (`face_augmentation.rotate_fit`). There is no other augmentation.
- **Schedule:**
  - batch 32, at most 120 epochs;
  - early stopping on validation accuracy (patience 15);
  - learning rate halved when validation loss stalls (patience 6);
  - the best validation-accuracy epoch is kept (epoch 54 of 69).
- One run took 4.3 minutes on this Mac's CPU.

### 2.6 Evaluation and current results

`face_evaluate.metrics` writes per-sign precision/recall/F1, a 50×50 confusion matrix, macro-F1 and cross-entropy.

| Data | Correct | Note |
|---|---|---|
| Fit | 644/649 | The model cannot fit FIVE on its own training clips (9/13). GOOD EVENING is 13/14. |
| Validation | 142/145 | Misses: FOUR 2/3, BLUE 1/3 |
| Reused test | 193/203 (95.1%, macro-F1 0.949) | SON 2/4 (→ DAUGHTER), GRANDFATHER 2/4 (→ FATHER); HELLO, YOURE WELCOME, YES, FIVE, YESTERDAY and BLACK each 3/4 |

### 2.7 Live recognition

- `recognition.PresenceCapture` and `recognition_webcam.py` work like this:
  - a hand entering view starts an attempt;
  - both hands out of view for 5 observations (about 0.33 s) produce one prediction, through the same `prepare_capture` code as training;
  - face or pose loss cancels the attempt;
  - each scored attempt's scores are saved and checked with `verify_recognition`.
- **Tonight's session** (`evidence/presence-live-20261119-234230`): 9 attempts, 9 predictions; the audit check passed.
  - The top-1 predictions covered only four signs: WOMAN 3, YESTERDAY 3, DON'T KNOW 2, GOOD MORNING 1.
  - YESTERDAY was in the top 3 of all nine attempts.
  - We don't know which signs were performed, so the session can't be scored.

## 3. Weak points found

**Data**

1. **Little data.** There are 13–14 training clips and 3 validation clips per sign.
2. **Unknown signers, random splits.** Validation and test contain the same signers, and probably the same recording sessions, as training. Current scores measure "known signers, new clips", not a new person such as the owner.
3. **The face rule removes the hardest examples.**
   - The 19 `invalid_face` exclusions fall on signs where the hand passes in front of the face. SON loses 6 of its 16 train clips.
   - These same signs are among the weakest on test: SON, GRANDFATHER and BLACK.
4. **Label noise.**
   - Identical clips are published under two labels (section 2.4).
   - The model cannot fit FIVE (9/13) and confuses FOUR/FIVE. This may be label noise or genuine overlap between the two signs.
5. **Gap between the dataset and the webcam.** FSL-105 shows deaf adult signers on a blue background. The live input is the owner at home, with a different camera height, angle and framing.

**Features**

6. **The face dominates the input.** It is 90% of the input and includes identity-specific face shape. Because the splits share signers, the model can use face shape or head pose as a shortcut. That would inflate validation and test scores, then fail on a new person.
7. **No direct handshape view.** Handshape is only seen as positions relative to the shoulders. There is no wrist-centred, size-normalised view of finger configuration.

**Training**

8. **Weak augmentation.** There is one ±5° rotation copy; the PRD asks for ±10–15° rotation, scaling and shifting. There is no speed or timing variation and no simulation of short detector dropouts.
9. **Noisy model selection.** Early stopping and checkpoint choice rely on 145 validation clips. With 3 per sign, one clip moves a sign's validation score by 33 points.
10. **One seed per run.** Run-to-run noise is unknown, so small differences between settings cannot be interpreted.

**Evaluation**

11. **The test split is reused.** It was used by four historical notebook variants, by the 2026-09-30 model (181/203) and by Phase 4 (193/203). It is no longer an untouched holdout.
12. **Tiny per-sign samples.** Per-sign numbers rest on 3–5 clips, without uncertainty ranges.
13. **No labeled webcam data.** Nothing measures how well the model recognizes the person who actually uses it.

**Live recognition**

14. **Face loss cancels the attempt** (owner decision D1). Signs that cover the face (SON, GRANDFATHER, BLACK, GOOD MORNING, SLOW) can be cancelled live, as well as being under-represented in training.
15. **Closed set and uncalibrated.** Every attempt returns one of the 50 signs, with a confidence that isn't calibrated. There is no UNKNOWN.
16. **Live predictions cluster.** Tonight's predictions cluster on four signs (section 2.7). This may be a domain or bias problem; labeled attempts are needed to tell.
17. **Handedness isn't verified.** SDK left/right labels are not anatomically checked. A person who signs with the other dominant hand puts one-handed signs into the other hand slot.

## 4. Feature design: hands and arms first, face lighter

This is the proposal to test, not a conclusion.

- **The main block stays exactly hm153:** both hands' 21 landmarks, the shoulders, elbows and wrists, the masks and the current normalization. No change to how these are computed.
- **Reduce the face to about 20 anchor points.** These are enough to locate the hand relative to the face and to show coarse expression (eyebrows, mouth), but not enough for identity. Proposed points (MediaPipe face mesh indices):

  | Region | Indices |
  |---|---|
  | Forehead | 10 |
  | Nose tip | 1 |
  | Chin | 152 |
  | Face sides | 234, 454 |
  | Eye corners | 33, 133, 362, 263 |
  | Eyebrows | 70, 105, 107, 336, 334, 300 |
  | Mouth corners | 61, 291 |
  | Lip centres | 13, 14 |

  - That is 60 values plus a face mask, so the input becomes 214 values (**hm214-v1**).
  - The face drops from 90% to about 28% of the input.
  - The exact list is frozen in the Phase 3 contract.
- **Make the face optional.** A missing face zeroes the face block and mask instead of excluding the clip. This brings back the 19 excluded clips. Shoulders stay mandatory, because every coordinate is normalized by them.
- **Face dropout in training.** For 50% of training sequences, zero the whole face block and mask. The model then has to recognize every sign from hands and arms alone and uses the face only as extra evidence.
- **Measure how much the model relies on the face:**
  - *face reliance*: how much macro-F1 drops when the face block is zeroed at evaluation;
  - *face-only accuracy*: accuracy with hands and arms zeroed (it should stay near chance).
- **Separate candidate:** hand-local shape channels. Each hand is placed relative to its own wrist and scaled by the wrist-to-middle-knuckle distance, adding 126 values (**hm340-v1**).
- **Fallback, only if face reliance stays high:** a two-branch CNN-LSTM in which the face passes through a 16-unit bottleneck before joining the hands/arms branch. This changes the model layout and needs separate approval.

## 5. Measurement rules

### Two baselines

- **B0, the frozen baseline:** the current model, unchanged. It is used in the test comparison (Phase 5) and the webcam comparison (Phase 6).
- **B0-CV, the baseline recipe:**
  - the same features, model and training settings, retrained on the cross-validation folds from Phase 2;
  - candidates are compared with B0-CV on identical folds and seeds;
  - this is the fair offline comparison, because the frozen model was chosen using its own validation clips.

### Reported for every run

- **Per sign:**
  - clips, correct and recall;
  - a 95% Wilson interval for recall (a range that is honest about small counts);
  - precision, F1 and top-3 recall;
  - the most common wrong prediction.
- **Overall:** accuracy, macro-F1, balanced accuracy, top-3 accuracy and the number of signs below 90% recall.
- **Face checks:** face reliance and face-only accuracy (section 4).
- **Comparison with the baseline**, on the same clips or attempts:
  - the per-sign change in correct counts;
  - an exact McNemar test, a paired test of whether the two models' errors really differ.
- **Common clips only.** Comparisons use clips that both inputs can score. Clips that only the new input can score (the 19 recovered face-missing clips) are reported separately.

### Decision rule, fixed before any candidate run

A change is kept only if all of the following hold:

1. Mean macro-F1 over seeds improves by at least max(1.0 point, 2 × the seed-to-seed standard deviation of B0-CV).
2. No sign loses more than 1 correct clip on average over seeds compared with B0-CV, unless the owner accepts a written explanation.
3. The number of signs below 90% recall does not increase.
4. Zeroing the face costs at most 5 points of macro-F1.
   - Signs that lose more than 20 points are listed for owner or expert review as possibly face-dependent.
   - If face-only accuracy is above 15%, the shortcut must be investigated before the recipe can be selected.

If two settings are within the noise threshold, the simpler one wins.

### Leakage checklist

Check these in Phases 1–2 and again before every final run:

- Exact and near-duplicate clips always sit in the same fold. Duplicates with conflicting labels are quarantined.
- Folds are fixed and hashed before any training.
- Augmented copies stay in their source clip's fold.
- Augmentation parameters and any statistics come from training folds only.
- Early stopping uses an inner split of the training fold, never the fold being scored.
- The official test split is not opened before Phase 5.
- The owner's webcam holdout is never used for training or tuning.
- Signer grouping is used if Phase 1 finds a reliable one. Otherwise every report says "signer-unknown".

## 6. Phases

### Phase 0: freeze the baseline and set up the ledger

**What will be done**
- Write `retraining-v1/baseline-manifest.json` with the hashes of:
  - the frozen model, labels, feature contract, policy and detector;
  - both bundles and the raw campaign manifest;
  - the partition file;
  - the current recognition source files.
- Recompute the baseline's per-sign fit and validation tables from the saved `fit_probabilities.npy` and `validation_probabilities.npy`, without new inference.
- Create the append-only ledger `retraining-v1/LEDGER.md` and `experiments.jsonl`.

**Touches:** read-only access to everything listed; new files only under `evidence/retraining-v1/`.

**Exit criteria**
- The manifest is written and read back, and every hash matches the recorded Phase 4 identity.
- The recomputed tables reproduce fit 644/649 and validation 142/145 exactly, sign by sign.

**Risks and rollback:** no existing file is touched. Deleting `retraining-v1/` undoes the phase.

### Phase 1: data and leakage audit (read-only, no candidate models)

**What will be done**
1. **Near-duplicates.** Compare each validation and test clip's hands-and-arms sequence (hm153) with every fit clip. Flag pairs closer than the closest 1% of fit-to-fit pairs. Review flagged pairs with the owner, using still frames.
2. **Labels.** Confirm the three duplicate-labeled clips. Review the 4 FIVE training clips the model cannot fit, and the FOUR/FIVE confusions, using still frames.
3. **Signers.** Compute scale-free body proportions per clip (forearm/upper-arm ratio, shoulder width / arm length). Check:
   - whether the clips form a few clear person-clusters;
   - whether the clip number in `clips/<sign>/<n>.MOV` predicts the cluster across signs.
   Use the clusters as fold groups only if they are clear; otherwise record "signer-unknown".
4. **Handedness.** For each sign, record which SDK hand carries the movement, and compare with the owner's dominant hand.
5. **Face visibility.** For each sign, record how often the face disappears inside the hand interval.
6. **Shortcut probes.** Train small logistic-regression probes on the fit split and score them on validation:
   - (a) face features only;
   - (b) only the first observation of the hand interval.
   High accuracy from (b), or from (a) on signs that don't use the face, is a warning that the scores rely on signer or session cues.

**Touches**
- New `training/holistic_migration/retraining/audit.py` and `training/holistic_migration/tests/test_retraining_audit.py`.
- Reads the bundles, raw campaign and partition file.
- Still frames of flagged clips go to scratch only, never to Git.
- Output: `retraining-v1/phase1-audit/`.

**Exit criteria**
- An audit report with all counts and every flagged clip.
- An owner decision (keep or quarantine) for each flagged clip, saved as a new view `quarantine-view-v2.json`; the original data is unchanged.
- The grouping decision is recorded: signer groups, or "signer-unknown".
- The probe results are recorded, with their interpretation.

**Risks and rollback**
- The near-duplicate check reads test-clip features: distances only, no model predictions on test. It needs owner approval (question 8); the alternative is to check fit and validation only.
- Body-proportion clusters may be unreliable. If so, they are not used.
- Everything is read-only, and quarantine lives in a separate view file. Deleting the view undoes it.

### Phase 2: fair validation and the baseline recipe under cross-validation

**What will be done**
- **Build 5 folds** over the 813 official train clips (fit plus validation):
  - stratified by sign, about 3 clips per sign per fold;
  - duplicate groups and any signer groups kept together;
  - quarantined clips left out.
  Freeze `folds-v1.json` with its hash before any training.
- **Inner stopping set:** inside each training fold, hold out 1 clip per sign for early stopping. The fold being scored never influences stopping or selection.
- **New runner:** it reproduces the Phase 4 model and training settings exactly. Only the input width and the data source are parameters.
- **Run B0-CV:** hm1588, current recipe, 5 folds × 3 seeds (20260705, 20260706, 20260707). That is 15 runs, about 1 CPU hour.

**Touches**
- New `retraining/folds.py`.
- New `retraining/model.py`: the same layers as `face_train.build_model`, with an input-width parameter.
- New `retraining/train_cv.py`.
- New `retraining/report.py`: per-sign tables, Wilson intervals, McNemar.
- Tests for all of these.
- Phase 4 code and data are untouched.

**Exit criteria**
- The tests pass, including:
  - width 1588 gives exactly 526,194 parameters and the same layers as `face_train.build_model`;
  - no clip in two folds and no group split across folds;
  - every sign in every fold;
  - no augmented copy crossing folds.
- An independent code review approves the runner before the real runs.
- B0-CV is finished. The ledger holds:
  - its out-of-fold per-sign table (about 16 clips per sign);
  - the seed standard deviation;
  - the resulting decision threshold.
  All of these are written before any candidate run.

**Risks and rollback**
- The CV score may come out below the frozen model's 97.9% validation. That would mean the old validation was lucky or leaky; it is information, not a failure.
- If grouping leaves a sign missing from some fold, fall back to 4 folds and record it.
- Only new code and files are added, so there is nothing to roll back.

### Phase 3: new feature sets

**What will be done**
- Write the contract `docs/holistic-migration/FEATURES_ARMS_V2.md` with exact indices and rules for:
  - hm153: exists, used as it is;
  - hm214-v1: hm153 plus about 20 face anchors plus a face mask, with the face optional;
  - hm340-v1: hm214 plus hand-local shape channels.
- Build bundles for all 1,016 clips from the raw campaign, without running the detector, using the same split membership. Report eligible counts per sign; the 19 face-excluded clips should come back.
- Check every tensor bit-for-bit against an independent second implementation, as was done for hm1588.

**Touches**
- New `retraining/features_v2.py` and `retraining/build_v2.py`, with tests.
- The contract document.
- New bundles under `retraining-v1/bundles/`.
- `features.py`, `face_features.py` and all existing bundles stay untouched.

**Exit criteria**
- The owner approves the contract before anything is built.
- The tests and an independent review pass.
- The independent recomputation matches every tensor.
- Per-sign counts are reported, and the old bundles' hashes are unchanged.
- In hm214 a clip is excluded only for hm153's reasons; the face is no longer a reason.

**Risks and rollback**
- Poorly chosen anchors show up in Phase 4's face checks and per-sign results. Fix them in a new contract version, never by editing v1.
- Recovered face-missing clips may carry other problems. They are listed separately, so their effect can be measured with and without them.
- The bundles are new files; deleting them undoes the phase.

### Phase 4: training-recipe experiments, fixed list

**What will be done:** run each experiment on the Phase 2 folds, with 3 seeds, and compare it with B0-CV under section 5. The list is fixed before the first run. Anything added later is labeled exploratory.

| ID | Input | Change from the row above |
|---|---|---|
| E1 | hm153 | Current recipe without the face |
| E2 | hm214 | Face anchors, face optional |
| E3 | hm214 | + face dropout 50% |
| E4 | hm214 | + stronger spatial augmentation: rotation ±12°, scale 0.95–1.05, shift ±0.05 shoulder widths, landmark jitter σ 0.01; 3 copies per clip |
| E5 | hm214 | + timing augmentation from raw observations: speed 0.8–1.25×, trim up to 2 observations at each end, drop one hand for 1–2 rows in 20% of sequences |
| E6 | hm214 | + label smoothing 0.1 and L2 1e-4 |
| E7 | hm340 | Best of E3–E6, plus hand-local shape channels |
| E8 (only if needed) | hm214 | Two-branch face bottleneck (needs approval) |
| E9 (only if Phase 1 supports it and the owner approves) | Best so far | Mirror plus swap hands, for left-handed signing |

**Touches**
- New `retraining/augment_v2.py`, with tests.
- Configs under `retraining-v1/configs/`; results under `retraining-v1/runs/`.
- One run takes about 4–10 minutes. E1–E7 is 105 runs, roughly 8–14 CPU hours, run in the background with receipts.

**Exit criteria**
- Each listed experiment is either finished, or abandoned with a reason written in the ledger.
- One recipe is selected by the section 5 rule, or the result is "nothing beats B0-CV". In that case retraining stops and the baseline stays.
- For the selected recipe:
  - zeroing the face costs at most 5 points of macro-F1;
  - face-only accuracy is at most 15%, or the shortcut investigation is closed;
  - the per-sign comparison table against B0-CV is written.

**Risks and rollback**
- **Overfitting the folds.** Trying many settings on the same folds can overfit them. The fixed list and fixed threshold limit this, and Phase 6 confirms on new data.
- **Augmentation bugs.** For example, moving points of an absent hand. Every transform has tests showing that absent hands or faces stay zero and masks stay unchanged.
- Only configs are added; the frozen recipe and model are untouched.

### Phase 5: train, freeze and compare the candidate offline

**What will be done**
- **Train once:** the selected recipe on all non-quarantined official train clips, with seed 20260705. Use a fixed number of epochs, the median best epoch from the Phase 4 cross-validation. The test split plays no part in stopping.
- **Freeze** the result as `retraining-v1/candidate-v1/model.keras`, with a manifest of its data, config, code and runtime hashes.
- **Optional:** fit one temperature value on the cross-validation out-of-fold predictions, so confidences become meaningful. This never changes which sign wins.
- **Test comparison:** evaluate the frozen baseline and the candidate once on the official test split with the same script. Write a per-sign table plus McNemar, labeled "exploratory, reused test".

**Touches:** `retraining/train_cv.py` (final mode) and `retraining/report.py`. Outputs go to `retraining-v1/candidate-v1/` and `retraining-v1/test-comparison/`.

**Exit criteria**
- The candidate is frozen, and the baseline hashes are unchanged.
- The test comparison report is written.
  - The reused test does not select anything.
  - If the candidate is clearly worse on it (3 or more extra errors overall, or any sign worse by 2 or more clips), stop and review with the owner before Phase 6.
  - Nothing is retuned on test results.

**Risks and rollback**
- If the candidate is worse than the baseline, the baseline stays and the result is logged.
- The candidate is a new file, and the viewer still uses the baseline.

### Phase 6: webcam holdout, both models on the owner's signing

**What will be done**
- **Collection mode.** Add a separate labeled collection mode to the viewer; the current test mode stays exactly as it is. It:
  - shows which sign to perform;
  - records each finished attempt's landmark observations, never video;
  - lets the owner keep or discard each attempt.
  Recordings are stored outside the repository.
- **Holdout recording:** 5 attempts per sign × 50 signs, in random order, over two sessions on different days, with the same framing as tonight. This data is never used for training or tuning.
- **Scoring:** replay every recorded attempt through the frozen baseline and the candidate, so both get identical inputs. Report:
  - per-sign accuracy for both models;
  - paired differences and McNemar;
  - capture outcomes per sign, such as attempts cancelled because the face was hidden.
- **Switch decision:** decide with the owner whether the live viewer switches to the candidate. The switch is a flag or default change with its own approval, and the baseline stays available.

**Touches**
- `recognition_webcam.py`: collection mode and a model-selection flag.
- `verify_recognition.py`: candidate identities.
- Tests for both.
- `recognition.py` only if the owner also changes the face-loss rule (question 6).
- Outputs go to `retraining-v1/webcam-holdout/`.

**Exit criteria**
- At least 4 kept attempts for every sign, each confirmed by the owner as performed as intended.
- Both models are scored on the same attempts, and the report is written.
- **Proposed switch rule:** switch only if all of these hold:
  - the candidate gets at least as many attempts right as the baseline;
  - McNemar does not show the candidate significantly worse;
  - no sign is worse by 2 or more of its 5 attempts.
  Otherwise the baseline stays.
- If the viewer switches:
  - the existing tests pass;
  - a short live session like tonight's works;
  - switching back takes one flag.

**Risks and rollback**
- One person's signing does not represent all learners; it is reported as single-signer evidence.
- Wrongly performed signs are guarded by the keep/discard step and the owner's confirmation.
- Stored landmarks are personal data. They stay local, outside Git, and are deleted on request.
- The viewer default stays on the baseline until the owner approves a switch, and collection mode is an addition, not a replacement.

### Later, not part of this plan

- Calibrated UNKNOWN/rejection: continues the existing public-data rejection track and needs a frozen candidate first.
- Personalization with the owner's recordings, using sessions separate from the holdout.
- Phone export and testing.
- Formal Mac acceptance trials: 10 confirmed attempts per sign per condition, against the approved targets.

## 7. Compute and effort

- **CPU:** one training run takes about 4–10 minutes (Phase 4 measured 4.3 minutes).
  - Phase 2: about 1 hour.
  - Phase 4: about 8–14 hours.
  - Phase 5: under 30 minutes.
  - Everything runs locally; no paid services.
- **Owner time:**
  - Phase 1 review of flagged clips: about 30 minutes.
  - Phase 3 contract approval.
  - Phase 6 recording: about 2 × 40 minutes.
  - A decision at each phase exit.

## 8. Questions and things I need from you

1. **Approvals.** `AGENTS.md` (Rule #0) asks for PM (Cabrera) and Adviser (Abella) approval before training code and architecture work. Is your approval enough, or do they need to sign off first? The PRD also locks training to Colab. Is local CPU training acceptable as a recorded deviation, as in Phase 4?
2. **Webcam data.** May I save landmark sequences (never video) of your attempts for the Phase 6 holdout? Please also say:
   - where they should be stored;
   - how long to keep them;
   - whether separate sessions may ever be used for training.
3. **Recording time.** Can you record 5 attempts per sign, 250 in total, in about two 40-minute sessions? Should it be tonight's room and lighting only, or a second condition as well?
4. **Dominant hand.** Which hand do you sign with? Should left-handed signing be supported (E9)?
5. **Face-dependent signs.** Which of the 50 signs use a facial expression or mouth shape, or touch or point to the face? Is an FSL expert available now to answer this? Earlier, none was available.
6. **Face-loss rule.** If the new model copes with a hidden face, may the live viewer keep attempts where the hand briefly covers the face, instead of cancelling them? This changes your D1 decision and matters for SON, GRANDFATHER, BLACK, GOOD MORNING and SLOW.
7. **Label conflicts.** Should the duplicate-labeled clips be quarantined from all new runs? They are `clips/23/6.MOV` (FOUR), `clips/57/9.MOV` (GRANDMOTHER) and test clip `clips/23/8.MOV` (FOUR). The original files stay as they are.
8. **Test clips in Phase 1.** May the near-duplicate check compare test clips with training clips (distances only, no model predictions)? Or should it stay on fit and validation only?
9. **Signers.** Do you know how many signers recorded FSL-105, or whether the clip numbers map to signers? Could you ask the dataset authors (Tupal and Cabatuan, De La Salle University) for signer IDs?
10. **Tonight's session.** Which signs did you perform in the 9 attempts, in order? The predictions were DON'T KNOW, YESTERDAY, WOMAN, WOMAN, WOMAN, GOOD MORNING, YESTERDAY, YESTERDAY, DON'T KNOW. Your answer tells us whether the clustering is a real bias.
11. **Priorities.** Which signs matter most to you, and which have already failed for you live?
12. **Switch rule.** Is the proposed Phase 6 switch rule acceptable, or do you want a stricter one?
