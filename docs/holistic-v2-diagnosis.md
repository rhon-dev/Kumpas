# Holistic v2 — Diagnosis (Step 1 Evidence Pack)

Status: **planning input, not a gate decision.** Produced 2026-09-21 under `AGENTS.md` Rule #0.
No code, no dependency changes, no gate status changes in this document.

Purpose: before planning a "Holistic v2", verify the claimed defects against the repo. Seven
findings were put forward. Each is marked **CONFIRMED**, **CORRECTED**, or **CANNOT VERIFY**.
Two of them are corrected in ways that change what the plan should do, so read §3 before §2.

Every number below is either computed from a file in this repo (or from the landmark arrays in
`../kumpas-data/`, which were present locally when this was written) or cited to official
MediaPipe documentation. Anything I could not establish is marked `unverified` rather than
estimated.

---

## 1. Evidence table

| # | Claim under test | Verdict | What the repo actually says |
|---|---|---|---|
| A | Hand landmarks are missing from ~2/3 of training frames | **CONFIRMED as a number, CORRECTED as a cause** | Rates are exact. But the absence is rest padding, not detection failure — in-span detection is 0.954 |
| B | The face was deleted (1404 of 1662 dims) to win the gate, never engineered | **CONFIRMED** | 1662-dim runs scored 0.8571 / 0.8325; the 258-dim `no_face` run scored 0.9507 |
| C | Residual errors are handshape-separated pairs on a ~203-clip test set | **CONFIRMED, with one omission corrected** | 10 errors total; 6 of 10 are numerals; prompt omitted `YOURE WELCOME→THANK YOU` |
| D | The app does not run Holistic; train/serve skew | **CONFIRMED, and the fix is cheaper than assumed** | Split `PoseLandmarker`+`HandLandmarker`, no face. But `tasks-vision:0.10.14` **already ships** `HolisticLandmarker` |
| E | Feedback engine scores handshape from landmarks that are absent | **CORRECTED — overstated** | The engine does gate on hand presence and abstains. The real defects are different (§2E) |
| F | The train/test split may not be signer-disjoint | **CONFIRMED, already documented** | No signer IDs exist in FSL-105 metadata; clip indices appear in both splits |
| G | Little latency headroom; the headline 0–2 ms excludes MediaPipe | **CONFIRMED** | MediaPipe 35–63 ms/frame vs TFLite 0–2 ms; zero real-device benchmarks exist |

---

## 2. Findings in detail

### A — Hand detection rates: numbers confirmed, causal story corrected

Computed over all 1016 rows of `training/preprocessing/extraction_log.csv` (all `status=ok`,
813 train / 203 test):

| channel | mean rate |
|---|---|
| `pose_rate` | 1.0000 |
| `face_rate` | 0.9999 (min 0.980) |
| `lh_rate` | **0.0803** |
| `rh_rate` | **0.3445** |
| `any_hand_rate` | **0.3516** |

The claimed figures (pose ~1.000, face ~1.000, left 0.080, right 0.344, any-hand 0.352) are
exact. Two facts are stronger than claimed: **733 of 1016 clips (72.1%) have `lh_rate` of
exactly 0.0** for the entire clip, and **no clip anywhere in the dataset exceeds
`any_hand_rate` 0.728**. 95.1% of clips sit at or below 0.5.

**But the interpretation "~2/3 of training frames were zero-filled where hands should be" is
wrong**, and this is the single most consequential correction in this document.

I reconstructed the temporal structure of hand presence from the extracted arrays in
`../kumpas-data/landmarks/` (1016 `.npz`, each `(T, 1662)`), over a stratified sample of 235
clips (3 per class, plus all 100 numeral clips):

| measurement | value |
|---|---|
| mean leading rest, as fraction of clip | 0.396 |
| mean signing span, as fraction of clip | 0.356 (median 0.324) |
| mean trailing rest, as fraction of clip | 0.248 |
| **hand-detection rate *inside* the signing span** | **0.954 (median 0.989)** |
| clips with in-span rate ≥ 0.90 | 217 / 235 (92.3%) |

Per-clip, hand presence is one contiguous block in the middle of the clip. Clips are 242–246
frames (`training/preprocessing/preprocessing_report.md`); hands typically appear around frame
~100 and disappear around frame ~180.

For the numerals specifically, in-span detection is among the *best* in the dataset:
FIVE 0.996, FOUR 0.978, ONE 0.979, THREE 0.961, TWO 0.920.

**Conclusion:** MediaPipe Holistic's pose-guided hand ROI re-crop *worked*. Hands are detected
95–99% of the time while the signer's hands are actually raised. The low aggregate rate measures
how much of each FSL-105 clip is a signer standing still, not how often MediaPipe failed.

The genuinely weak classes by in-span rate are BLUE 0.570, WHITE 0.627, MOTHER 0.707,
RED 0.808, WOMAN 0.840, BLACK 0.840 — plausibly hand-near-face occlusion. That is a real but
secondary issue affecting 6 classes, not a pipeline-wide failure.

### B — The face was dropped, not engineered

`training/models/experiments_log.json` contains exactly 4 runs, all seed `20260705`, `seq_len`
30, `augmented: true`:

| run | features | `drop_face` | params | best val | **test** |
|---|---|---|---|---|---|
| `20260705_192720_baseline` | 1662 | false | 540,402 | 0.9611 | 0.8571 |
| `20260705_194813_no_face` | 258 | true | 270,834 | **1.0** | **0.9507** |
| `20260705_195312_no_face_wider` | 258 | true | 689,394 | **1.0** | 0.9409 |
| `20260705_200027_full_dropout05` | 1662 | false | 540,402 | 0.9221 | 0.8325 |

CONFIRMED. `1662 − 258 = 1404 = 468 × 3`, so the discarded block is the **base** face mesh.
`training/preprocessing/extract_landmarks.py:57` sets `refine_face_landmarks=False`, consistent
with 468 rather than the refined 478.

The face was removed as a dimensionality problem, in a single switch
(`build_sequences.py:119`), and `build_sequences.py:24` describes `no_face` as a *latency*
fallback — a different justification than the accuracy result that actually selected it. No
run attempted a face *subset*, derived facial features, or per-block regularization. The
claim that Holistic "was won by deleting 1404 of its 1662 dimensions" is fair.

**Additional deviation found, not in the original findings:** every run records
`"environment": "local M1 (tensorflow 2.19.0)"`, while `.kiro/steering/tech.md:11` locks the
training environment to Google Colab (GPU). The locked stack was departed from without a
recorded PM approval.

### C — The confusion pairs

`training/models/reports/20260705_194813_no_face_eval.md` — test accuracy 0.9507 on 203 clips,
macro precision 0.9580 / recall 0.9500 / F1 0.9481, best val accuracy 1.0. The full error list
is 10 misclassifications:

| n | true → predicted |
|---|---|
| 3 | FIVE → FOUR |
| 2 | THREE → TWO |
| 1 | FOUR → FIVE |
| 1 | YOURE WELCOME → THANK YOU |
| 1 | YESTERDAY → TOMORROW |
| 1 | YES → NO |
| 1 | GOOD AFTERNOON → GOOD EVENING |

CONFIRMED with two corrections. The original finding **omitted `YOURE WELCOME → THANK YOU`**,
and only FIVE↔FOUR is bidirectional; the rest are one-directional. **6 of 10 errors (60%) fall
in the four numeral classes**, whose F1 scores are FIVE 0.333 (recall 0.250 — 1 of 4 clips
correct), FOUR 0.600, THREE 0.667, TWO 0.800. 40 of 50 classes score F1 1.000.

On whether this supports a 95.07% thesis claim — stated plainly, **no, not as a tight
estimate**:

- Support is 4 clips per class (a few have 5). One extra error moves per-class recall by 25
  percentage points. No confidence interval is reported anywhere.
- Best validation accuracy of 1.0 means the validation set was saturated and provided **no
  model-selection signal**; the choice between the four runs rests on the test split, which
  makes the reported test accuracy partly a selection artifact.
- 40 of 50 classes at exactly F1 1.000 on n=4 is what a small, possibly signer-overlapping
  test set looks like (see F).

The accuracy figure is reproducible and honestly logged. It is the *precision* of the claim
that is unsupportable, not the number.

### D — On-device: confirmed, but the fix is cheaper than the finding assumed

`VisionEngine.kt:9-10` imports `HandLandmarker` and `PoseLandmarker`. There is no
`HolisticLandmarker` import, `N_FEATURES = 258` (`:35`), and no face channel exists anywhere in
the runtime. `app/fetch_assets.sh` fetches only `pose_landmarker_lite.task` and
`hand_landmarker.task`. `app/android/app/build.gradle.kts:59` pins
`com.google.mediapipe:tasks-vision:0.10.14`.

So the locked stack at `.kiro/steering/tech.md:8` ("Landmark extraction: MediaPipe Holistic")
is violated on device, and train/serve skew is real: training landmarks came from the legacy
Python Holistic graph, runtime landmarks come from an independent palm detector on a full
frame.

**Three corrections that make WS4 substantially cheaper and safer than planned:**

1. **`tasks-vision:0.10.14` already contains `HolisticLandmarker`.** I downloaded the AAR from
   Google's Maven repository and listed its classes:
   `com/google/mediapipe/tasks/vision/holisticlandmarker/HolisticLandmarker.class`,
   `HolisticLandmarkerResult.class`, `HolisticLandmarkerOptions` and its builder — 10 classes.
   Also present in 0.10.15, 0.10.16 and 1.0.0 (current release on Google Maven).
   **No dependency bump is required.** The plan must not assume one.

2. **Handedness stops being a classifier decision.** `VisionEngine.kt:146` currently assigns
   hand blocks from `hands.handedness()[h][0].categoryName()`. `HolisticLandmarkerResult`
   instead exposes `leftHandLandmarks()` and `rightHandLandmarks()` as separate accessors, so
   that branch disappears. The legacy Python Holistic used for training also assigns left/right
   in-graph, so **training and a Tasks-Holistic runtime share a convention, and the current app
   is the outlier.** Front-camera *mirroring* remains an open question (§3, WS4) — a mirrored
   input still makes the graph label an anatomical left hand as right.

3. **A better face channel exists than raw landmarks.** `HolisticLandmarkerOptions` has
   `setOutputFaceBlendshapes(Boolean)`, and the result exposes `faceBlendshapes()`. Blendshapes
   are a few dozen named, semantically meaningful scalars (brow raise, jaw open, mouth pucker,
   eye blink) rather than 1404 raw coordinates. This is a direct answer to finding B: the
   non-manual-marker channel can be added without re-creating the dimensionality failure.

Full result API, read from the artifact: `faceLandmarks()`, `faceBlendshapes()` (Optional),
`poseLandmarks()`, `poseWorldLandmarks()`, `segmentationMask()` (Optional),
`leftHandLandmarks()`, `leftHandWorldLandmarks()`, `rightHandLandmarks()`,
`rightHandWorldLandmarks()`, `timestampMs()`.
Options: `setMinFaceDetectionConfidence`, `setMinFaceSuppressionThreshold`,
`setMinFacePresenceConfidence`, `setMinPoseDetectionConfidence`,
`setMinPoseSuppressionThreshold`, `setMinPosePresenceConfidence`,
`setMinHandLandmarksConfidence`, `setOutputPoseSegmentationMasks`, `setOutputFaceBlendshapes`,
`setRunningMode`, `setResultListener`, `setErrorListener`. There is no `model_complexity` knob
and no multi-person option.

**One landmark-count mismatch the feature spec must resolve.** Training used legacy Holistic
with `refine_face_landmarks=False` → 468 face landmarks → **543** total. The Tasks
`HolisticLandmarker` is documented at **553** landmarks
([overview](https://developers.google.com/edge/mediapipe/solutions/vision/holistic_landmarker)),
i.e. 33 + 478 + 21 + 21, using the **refined** face mesh. Python and Kotlin must be brought
onto the same face-mesh variant, or restricted to indices that are stable across both.
The Android guide confirms the task bundle name `holistic_landmarker.task` and that image,
video and live-stream modes are supported
([Android guide](https://developers.google.com/edge/mediapipe/solutions/vision/holistic_landmarker/android)).

`unverified`: whether the Tasks Holistic graph populates `NormalizedLandmark.visibility()` for
pose. The current 258-dim vector consumes pose visibility as its 4th component per landmark.
This must be measured on device before the feature spec depends on it.

*(MediaPipe API details above are paraphrased from the linked Google documentation and read
directly from the published Maven artifact. Content was rephrased for compliance with
licensing restrictions.)*

### E — Feedback engine: the finding is overstated

The claim was that the engine "scores handshape and orientation from landmarks missing in most
frames". **That is not what the code does.** `training/feedback/feedback_engine.py:73` defines
`hand_present()`, and both hand-dependent dimensions use it:

- `handshape_score` (`:131`) aligns only frames where *both* learner and gold show the hand. If
  the gold uses a hand the learner never shows, it returns severity 1.0 with the marker
  `"hand not detected"` (`:137`), which surfaces as "This sign uses your {hand} hand — keep it
  visible to the camera" (`:190`) rather than a fabricated finger correction.
- `orientation_score` (`:153`) returns 0.0 — emitting no feedback item — when there are no
  aligned pairs.

So the engine already abstains in the total-absence case. The finding is **CORRECTED**.

The real defects, which the plan should target instead:

1. **No minimum-support threshold.** Presence gating is binary, not quantitative. With roughly
   10 of 30 timesteps carrying hand data (§3), a handshape or orientation severity can be
   computed from a handful of aligned frames and still be reported at full confidence. There is
   no floor on the number of aligned pairs required.
2. **`overall_match` is computed from firing items only** (`:204`:
   `1.0 - mean(severity of items above threshold)`). Two consequences: if nothing fires the
   score is exactly 1.0, and because the mean covers only items that crossed a threshold,
   *adding* a milder error can *raise* `overall_match`. That is a scoring defect independent of
   Holistic.
3. **Documentation/reality mismatch.** The module docstring still reads "Thresholds are
   provisional pending expert calibration", while `docs/phase-gates.md` records FSL Expert
   validation complete on 2026-07-23 with all 50 gold standards approved. Current values:
   timing 0.30, motion 0.25, handshape 0.22, orientation 0.25 (`:42`).
4. **Gold standards are locked to the old feature space.** `VisionEngine.kt:62-65` reads
   `gold_standards.bin` as exactly `50 × 30 × 258` floats, with a hardcoded class count of 50.
   Any feature-space change invalidates this asset.

**Good news that narrows the blast radius:** DTW alignment runs on *pose* wrists
(`L_WRIST_P = 15`, `R_WRIST_P = 16`), not hand landmarks. TIMING and MOTION are therefore valid
regardless of hand detection. Only HANDSHAPE and ORIENTATION depend on the hand channel, so the
2026-07-23 expert sign-off is not wholesale invalidated — it is two of four dimensions that
need re-validation in a new feature space.

### F — Signer independence: confirmed, and already on the record

FSL-105's `train.csv` / `test.csv` carry only `vid_path, id_label, label, category`. **There is
no signer or subject column.** Clip paths are `clips/<class_id>/<index>.MOV`.

Distinct clip indices `0..21` appear in **both** train and test. Per class the dataset holds
~20 clips split ~16 train / ~4–5 test, and the membership differs per class (e.g. class 20
tests on indices 6, 8, 14, 17; class 22 tests on 1, 11, 12, 13). If the clip index identifies a
signer — a plausible reading of ~20 clips per class across 22 indices, but **`unverified`** —
then essentially every signer appears in training for some classes and in test for others, and
95.07% is inflated by signer familiarity.

This cannot be settled from metadata. It is already documented as a limitation at
`docs/dataset-notes.md:20,29`, `.kiro/specs/03-dataset-audit/design.md:123,128`, and
`.kiro/specs/04-data-pipeline/requirements.md:19` — the last of which already *requires*
acknowledging that subject-independent splits are not possible. Holistic v2 does not need to
re-discover this; it needs to stop reporting a single point accuracy as if it were
signer-independent.

A cheap empirical probe is available and worth one task: per-clip body geometry (torso length,
shoulder width, face scale) is already in the extracted arrays. If clips sharing an index
cluster tightly in that space across different classes, the index encodes a signer and the
leakage is real.

### G — Latency headroom

`benchmarking/phase4_emulator_report.md`, dated 2026-07-07, on an `AVD medium_phone` /
Android 35 arm64 / 4 GB emulator hosted on an Apple M1 with `-gpu host` and a synthetic camera:

| metric | measured |
|---|---|
| Camera pipeline FPS | 28.6–29.9 |
| **Landmark extraction (pose+hands), per sampled frame** | **35–63 ms** |
| TFLite inference (30×258 CNN-LSTM, dynamic quant) | 0–2 ms |
| FATAL crashes over 55 s | 0 |

CONFIRMED. The report states in its own header that these are an M1 proxy and must be re-run on
real hardware.

The budget arithmetic matters because `.kiro/steering/tech.md:42` defines the 150 ms budget as
covering **camera frame → landmark extraction → model inference → feedback → UI render**.
Landmark extraction is *inside* the budget. So the current pipeline consumes 35–65 ms of 150 ms,
leaving **~85–115 ms** — and that is on an M1 proxy, for two models, with no face channel.

`benchmarking/benchmark_history.json` holds exactly 4 entries: latency and FPS (both emulator,
both self-labelled retroactive M1 proxies) and two accuracy runs on `offline/python`. **No
real-device measurement exists anywhere in the repo.**

The cost of adding the face model and any ROI re-crop passes under Holistic is **`unverified`**
and cannot be derived from this repo. It must be measured. The existing budget should be
treated as unproven rather than either survivable or blown.

The report's own open issues remain relevant: confident predictions on all-zero input (since
partially mitigated — `VisionEngine.kt:170` now gates on `poseRate < 0.5`), uncalibrated
front-camera handedness, and three models loading synchronously on the calling thread.

---

## 3. The corrected root cause

Findings A and C were framed as one story: hands are missing, so handshape-separated pairs
confuse. The numbers support the conclusion but not the mechanism. Two measured causes explain
the numeral confusions, and neither is a MediaPipe detection failure.

### Root cause 1 — uniform temporal sampling spends two thirds of every sequence on rest

`training/preprocessing/build_sequences.py:47-49`:

```python
def sample_indices(n_frames, seq_len):
    if n_frames >= seq_len:
        return np.linspace(0, n_frames - 1, seq_len).round().astype(int)
```

30 frames are sampled uniformly across the **whole** clip. There is no signing-segment
detection. Since the sign occupies only ~36% of the clip (§2A), most sampled timesteps land in
rest.

Measured directly on the delivered tensor `../kumpas-data/sequences/X_test.npy`, shape
`(203, 30, 1662)`:

| measurement | value |
|---|---|
| timesteps (of 30) containing any hand data | **10.3** |
| timesteps containing right-hand data | 10.1 |
| timesteps containing left-hand data | 2.4 |
| numerals: ONE / TWO / THREE / FOUR / FIVE | 7.0 / 8.8 / 7.8 / 7.8 / 9.0 |

Fraction of test sequences with hand data at each of the 30 timesteps:

```
0.05 0.04 0.03 0.02 0.01 0.01 0.01 0.03 0.05 0.14 0.24 0.32 0.46 0.58 0.75
0.85 0.91 0.95 0.92 0.83 0.74 0.68 0.53 0.42 0.27 0.20 0.13 0.09 0.03 0.02
```

A clean unimodal curve peaking at 0.95 — the signature of raise, sign, lower. The model is
given ~7–9 frames of actual handshape for a numeral, at an arbitrary phase of the hold, and
~20 frames of a person standing still.

`training/preprocessing/preprocessing_report.md` already reported "any-hand 0.352" and flagged
only the 2 clips below 10%. The number was seen; the sampling consequence was not drawn.

### Root cause 2 — the representation buries handshape

`build_sequences.py:54-62` normalizes every block, hands included, by subtracting the mid-hip
root and dividing by torso length. Hand landmarks are therefore expressed in torso units, in
absolute position. Measured on the same tensor, reduced to the 258-dim `no_face` layout:

| quantity | mean absolute value |
|---|---|
| pose block | 0.5713 |
| right-hand block (present frames) | 0.3644 |
| **wrist-relative fingertip configuration — the actual handshape signal** | **0.0758** |

Handshape is a **7.5× smaller-amplitude** component than pose, riding on top of large
positional values. Meanwhile the information itself is perfectly separable:

| pair | between-class handshape distance | within-class spread | ratio |
|---|---|---|---|
| FIVE vs FOUR | 0.1495 | 0.0396 | **3.78** |
| THREE vs TWO | 0.2517 | 0.0252 | **9.97** |

This is the important result: **the discriminative information is present in the data and is
not exposed in the representation.** Making it explicit — wrist-relative, scale-normalized hand
coordinates plus derived features (inter-fingertip distances, curl angles, palm normal) — is a
feature-engineering change, not a new sensor and not a new model family.

### What this means for the plan

- The premise that Holistic's pose-guided high-resolution hand re-crop is "the one benefit this
  pipeline never received" is **false for training**. It was received and it worked (0.954
  in-span). It is genuinely absent **on device**, which is a real train/serve skew problem and
  keeps WS4 fully justified.
- The numerals are fixable by **temporal segmentation plus hand canonicalization**, both cheap,
  both offline, neither requiring new models or added device latency. These should be the first
  interventions, and they should be measured *before* any face channel is added.
- The face is not implicated in the numeral confusions at all. It remains worth testing for
  GOOD AFTERNOON / GOOD EVENING and YES / NO, which have good hand rates (0.450 / 0.471 in-span
  and above) and so are *not* explained by root cause 1. Face work belongs behind an ablation,
  as a hypothesis, not as a headline goal.
- Re-extraction at the full 543/553 landmark set is still worth doing, but its justification is
  **train/serve parity and keeping the face option open**, not hand recovery. Anyone planning
  re-extraction to "fix hands" will spend days and find nothing, because hand detection is
  already at 0.954 where it matters.

---

## 4. What this means for the thesis defense

Blunt version, in the order a panelist will find it.

**The strongest real exposure is the evidence, not the engineering.** The code is in better
shape than the paperwork around it. Three specific items are indefensible as currently written:

1. **The `<150 ms` gate is recorded as PASS using a number that excludes the dominant cost.**
   `phase-gates.md` Phase 4 cites "inference 0–2 ms" while the same report records MediaPipe at
   35–63 ms, and `tech.md:42` defines the budget to include landmark extraction. A panelist who
   opens both files finds this in minutes. This is PR #2's finding 1.2 and it is correct.

2. **95.07% is quoted as a point estimate on 4 clips per class, selected using a validation set
   that scored 1.0, with signer overlap that cannot be ruled out.** Each of those three is
   defensible in isolation if disclosed. Quoting the number without a confidence interval is
   not. The fix is cheap: report a CI, report per-class support, and state the signer limitation
   that `dataset-notes.md` already documents.

3. **The locked stack is departed from in two places without recorded approval** — Holistic on
   device (`tech.md:8` vs `VisionEngine.kt:9-10`) and Colab for training (`tech.md:11` vs
   `"local M1"` in every logged run). Either update the steering doc or record the deviation.

**What is genuinely strong and should be defended confidently:**

- The preprocessing is honest: detection rates were logged per clip, failures were made visible
  rather than hidden, and the weak clips were flagged in the report at the time.
- `FeedbackEngineParityTest.kt` (tolerance 0.05, three real fixtures) is the right pattern for
  proving a hand-ported algorithm matches its reference. It should be pointed at in the
  methodology chapter and extended, not replaced.
- The feedback engine already abstains rather than inventing corrections when a hand is absent
  (§2E). That is a defensible pedagogical design choice, and it was in the code before anyone
  asked.
- The numerals weakness now has a **measured, mechanical explanation** rather than a hand-wave.
  "Our sampling spent two thirds of each sequence on rest frames, and our normalization
  compressed handshape to an eighth of the pose amplitude" is a much better answer than "small
  classes are hard", and it comes with a targeted fix.

**The honest framing for Holistic v2 in the thesis:** this is not "we adopted Holistic". Holistic
was always used for training. It is "we found that our sequence construction discarded most of
the manual signal, we fixed the representation, and we closed a train/serve gap where the app
ran a different landmark graph than the training pipeline". That is a sharper contribution and
it is supported by the numbers in this document.

---

## 5. Open questions requiring a decision before WS1

1. **Is the FSL-105 split signer-disjoint?** Unresolvable from metadata (§2F). Either run the
   body-geometry clustering probe, consult the dataset paper, or state the limitation and stop
   implying signer independence. This is a methodology-chapter decision, not an engineering one.
2. **Is a 203-clip test set (~4 per class, validation saturated at 1.0) defensible?** Current
   position: adequate for a ≥90% gate, inadequate for a tight point estimate. Options are
   cross-validation, a re-split with a real validation set, or reporting with confidence
   intervals. This blocks WS3, because a per-pair improvement on 4 samples per class cannot be
   distinguished from noise.
3. **Base (468) or refined (478) face mesh?** Python trained on 468; the Tasks runtime is
   documented at 553 total, implying 478. One must move.
4. Whether pose `visibility()` is populated by the Tasks Holistic graph (`unverified`, §2D).

---

## 6. Sources

Repo evidence is cited inline by path and line. External references:

- [MediaPipe Holistic landmarker overview](https://developers.google.com/edge/mediapipe/solutions/vision/holistic_landmarker) — 553 landmarks, combined face/hand/pose task.
- [MediaPipe Holistic landmarker guide for Android](https://developers.google.com/edge/mediapipe/solutions/vision/holistic_landmarker/android) — `com.google.mediapipe:tasks-vision` dependency, `holistic_landmarker.task` bundle, supported running modes, options builder.
- `com.google.mediapipe:tasks-vision` artifacts 0.10.14 / 0.10.15 / 0.10.16 / 1.0.0, read from Google's Maven repository to confirm `HolisticLandmarker` class presence and the result/options API surface.

External documentation content was paraphrased rather than quoted. Content was rephrased for
compliance with licensing restrictions.
