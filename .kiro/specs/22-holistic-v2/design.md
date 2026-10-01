# Phase 22 — Holistic v2: Design

Companion to `requirements.md`. Evidence base: `docs/holistic-v2-diagnosis.md`.
Planning document — no implementation, per `AGENTS.md` Rule #0.

## 1. Design premise

The brief assumed Holistic's pose-guided hand ROI re-crop had never been received. Verification
showed otherwise: in-span hand detection measures **0.954** (median 0.989), and the numeral
classes sit at 0.920–0.996. The design therefore targets the three defects that are actually
measured.

| # | Defect | Evidence | Layer |
|---|---|---|---|
| 1 | Sequence construction spends ~2/3 of every sequence on rest frames | 10.3 of 30 timesteps carry hand data; numerals 7.0–9.0 | Preprocessing (WS1) |
| 2 | Representation buries handshape | wrist-relative handshape amplitude 0.0758 vs pose 0.5713 — 7.5× smaller — while class separation is 3.78 / 9.97 | Feature spec (WS2) |
| 3 | App runs a different landmark graph than training | `VisionEngine.kt:9-10` split detectors, no face, `categoryName()` handedness | Runtime (WS4) |

Defects 1 and 2 are offline, cheap, and add **zero** device latency. Defect 3 costs device
latency and is the only one that needs the Holistic runtime. This ordering drives the whole plan:
**prove the cheap offline wins before spending latency budget.**

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  TRAINING (Python, offline)                                 │
│                                                             │
│  clips ──► Holistic extraction ──► full landmark set        │
│            (mp.solutions.holistic)   543 or 553             │
│                       │                                     │
│                       ▼                                     │
│            ┌──────────────────────┐                         │
│            │ signing-span detect  │  ◄── WS1, NEW           │
│            │ sample WITHIN span   │                         │
│            └──────────┬───────────┘                         │
│                       ▼                                     │
│            ┌──────────────────────┐                         │
│            │ feature_spec_v2.json │  ◄── WS2, single source │
│            │ · block layout       │      of truth           │
│            │ · per-block norm     │                         │
│            │ · derived features   │                         │
│            │ · presence flags     │                         │
│            └──────────┬───────────┘                         │
│                       ▼                                     │
│            ablation ladder ──► model v2 ──► TFLite          │
│                  (WS3)                                      │
└───────────────────────┬─────────────────────────────────────┘
                        │  exports: .tflite + label_map
                        │           + feature_spec_v2.json
                        │           + gold_standards_v2.bin
                        │           + golden-vector fixtures
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  APP (Kotlin/Flutter, on-device, offline)                    │
│                                                             │
│  CameraX ──► HolisticLandmarker ──► FeatureBuilder          │
│              (ONE graph, WS4)        (reads feature_spec)   │
│                    │                        │               │
│            left/right hands            ▲    ▼               │
│            resolved in-graph           │  classifier        │
│            (no categoryName)           │    │               │
│                                        │    ▼               │
│                        golden-vector   │  FeedbackEngine v2 │
│                        parity test ────┘    (WS5)           │
│                        MUST PASS                            │
└─────────────────────────────────────────────────────────────┘
```

The single most important structural change is that `feature_spec_v2.json` sits between the two
halves and both consume it. Today the layout is asserted twice — `build_sequences.py:54` and
`VisionEngine.kt:242` — with nothing proving agreement.

## 3. WS1 — Signing-span detection and sampling

### 3.1 The measured problem

`build_sequences.py:47-49`:

```python
def sample_indices(n_frames, seq_len):
    if n_frames >= seq_len:
        return np.linspace(0, n_frames - 1, seq_len).round().astype(int)
```

Uniform across a clip that is 39.6% leading rest + 35.6% signing + 24.8% trailing rest. Resulting
hand-presence profile across the 30 timesteps of `X_test.npy`:

```
0.05 0.04 0.03 0.02 0.01 0.01 0.01 0.03 0.05 0.14 0.24 0.32 0.46 0.58 0.75
0.85 0.91 0.95 0.92 0.83 0.74 0.68 0.53 0.42 0.27 0.20 0.13 0.09 0.03 0.02
```

### 3.2 Approach

Span detection should not depend on the hand channel alone, or it becomes circular (a clip with
poor detection gets a short span, which then hides the poor detection). Two independent signals,
combined:

- **Hand presence** — first-to-last frame with any hand landmark. Direct but circular-prone.
- **Wrist motion energy from pose** — pose is detected at 1.000 across all 1016 clips, so
  pose-wrist displacement gives a span estimate that is available even when hands are missed.

Design rule: take the union of the two estimates, pad by a small margin, and log both so
disagreement is visible. Where they disagree materially, quarantine per requirement 2 rather than
silently picking one.

### 3.3 Sampling inside the span

Uniform sampling within the padded span, keeping `seq_len` at 30 for comparability with the
existing four logged runs. Changing both the sampling window and the sequence length at once
would make the ablation uninterpretable — `seq_len` is a separate lever for a later run.

Short spans (fewer than `seq_len` frames) repeat the last frame, matching existing behaviour.

### 3.4 What WS1 does not do

It does not chase detection rate pipeline-wide. In-span detection is 0.954. Only BLUE (0.570),
WHITE (0.627), MOTHER (0.707), RED (0.808), WOMAN (0.840), and BLACK (0.840) fall below 0.85, and
the plausible mechanism there is hand-near-face occlusion, which is a different fix (ROI or
confidence tuning) applied to six classes rather than 50.

## 4. WS2 — Feature spec v2

### 4.1 Why a spec file rather than shared code

Python and Kotlin cannot share an implementation, so the only thing that can be shared is a
declaration. The spec declares layout and normalization; each side implements it; the
golden-vector test proves the implementations agree. That is the same contract
`FeedbackEngineParityTest.kt` already establishes for the feedback math, which is the strongest
pattern in the repo.

### 4.2 Block structure

| Block | Content | Normalization | Rationale |
|---|---|---|---|
| Pose (upper body subset) | Shoulders, elbows, wrists, hips, head anchors | Mid-hip centered, torso-scaled (unchanged) | Carries trajectory; already works |
| Hand, canonicalized ×2 | 21 landmarks per hand | **Wrist-relative, per-hand scale-normalized** | Fixes the 7.5× amplitude problem |
| Derived handshape ×2 | Inter-fingertip distances, curl angles, palm normal, wrist velocity | Unit-scaled | Makes finger count directly readable |
| Face / NMM | Blendshape coefficients, or a justified landmark subset | Per-coefficient | Compact; avoids the 1404-dim failure |
| Presence flags | One per block | Binary | Removes the absent/at-origin ambiguity |

Pose normalization is deliberately unchanged. It is not implicated in any measured defect, and
holding it constant keeps the ablation ladder interpretable.

### 4.3 Why canonicalization is expected to work

The information is already separable in the existing data; it is simply not exposed:

| Pair | Between-class distance | Within-class spread | Ratio |
|---|---|---|---|
| FIVE vs FOUR | 0.1495 | 0.0396 | 3.78 |
| THREE vs TWO | 0.2517 | 0.0252 | 9.97 |

A ratio near 10 for THREE vs TWO means a linear separator exists in the wrist-relative space. The
classifier fails to find it because the signal sits 7.5× below the pose amplitude in an absolute
coordinate frame. This is the load-bearing argument for WS2 and it should be re-verified on the
rebuilt sequences before WS3 commits to an architecture change.

### 4.4 Face channel: blendshapes preferred

`HolisticLandmarkerResult.faceBlendshapes()` (enabled via
`HolisticLandmarkerOptions.setOutputFaceBlendshapes`) returns named expression coefficients rather
than raw coordinates. Advantages over a hand-picked landmark subset: far lower dimensionality,
semantically interpretable in a thesis, and directly aligned to non-manual markers (brow, jaw,
mouth, eye).

Two open issues the spec must resolve:

1. **Python-side availability.** The training extraction uses legacy `mp.solutions.holistic`,
   which does not expose blendshapes. Either Python moves to the Tasks `HolisticLandmarker`
   (which also fixes the 468/478 mismatch), or the face channel uses a landmark subset on both
   sides. **This is a genuine fork in the design and belongs in DECISIONS-FOR-PM.**
2. **Mesh variant.** Training used the base 468 mesh; the Tasks runtime is documented at 553 total
   landmarks, implying the refined 478 mesh. Landmark indices are not interchangeable between
   variants for the refined region.

### 4.5 Presence flags

Today an absent hand is all-zero (`build_sequences.py` restores zeros after normalization;
`VisionEngine.kt:242` skips normalization for zero blocks). After wrist-relative
canonicalization, a *present* hand also has a zero wrist, so absent and present become harder to
distinguish, not easier. Explicit flags are therefore a correctness requirement of
canonicalization, not a nice-to-have.

## 5. WS3 — Ablation ladder

### 5.1 Pre-registered rungs

Identical splits, one variable per rung, every run logged:

| Rung | Features | Question it answers |
|---|---|---|
| 0 | Pose only | How much is pure trajectory worth? Establishes the floor the current model may be near. |
| 1 | + hands, raw (current encoding) | Reproduces the 258-dim baseline under new sampling — isolates WS1's contribution alone. |
| 2 | + hands, canonicalized | Isolates WS2's canonicalization contribution. |
| 3 | + derived handshape features | Isolates explicit handshape features. |
| 4 | + face/NMM channel | Does the face carry signal for the non-numeral pairs? |
| 5 | Full | Interaction effects. |

Rungs 0 and 1 matter most for the thesis narrative: the difference between them quantifies how
much accuracy the old uniform sampling was discarding, which is the paper's actual finding.

### 5.2 Metrics

Primary is per-pair accuracy on the seven observed pairs. Overall accuracy is a **reporting**
metric only — it is already 0.9507 and can rise while the numerals stay broken, which is exactly
how the current state arose.

Also required: macro-F1, calibration (ECE or reliability curve), per-class support, and
confidence intervals. `VisionEngine.kt:170` gates on `poseRate < 0.5` to avoid classifying an
empty frame, but nothing calibrates confidence when a signer *is* present, and the feedback
contract depends on that confidence being meaningful.

### 5.3 The statistical blocker

Test support is 4 per class. A numeral improvement from 1/4 to 3/4 correct is two clips. That
cannot be distinguished from noise, and best validation accuracy of 1.0 means there was no
model-selection signal either. **Hardening task G2 must complete before rung comparisons are
meaningful** — this is why requirement 19 promotes it from optional to prerequisite. Options are
cross-validation over the combined pool, or a genuine three-way re-split. Either changes the
reported baseline, which needs PM awareness.

### 5.4 Architecture candidate

A two-stream model (body/trajectory stream + hand-crop stream, late fusion) matches the causal
story: the streams have different amplitude scales and different temporal bandwidths, which is
precisely the problem a single concatenated vector created. It must be justified against 4 GB RAM
and the WS6 budget; the current winner is 270,834 parameters, so there is architectural room if
latency allows.

## 6. WS4 — On-device Holistic

### 6.1 Verified starting point

`com.google.mediapipe:tasks-vision:0.10.14`, already pinned at
`app/android/app/build.gradle.kts:59`, ships
`com.google.mediapipe.tasks.vision.holisticlandmarker.HolisticLandmarker`. Confirmed by reading
the published artifact. No dependency bump.

Result surface: `faceLandmarks()`, `faceBlendshapes()` (Optional), `poseLandmarks()`,
`poseWorldLandmarks()`, `segmentationMask()` (Optional), `leftHandLandmarks()`,
`leftHandWorldLandmarks()`, `rightHandLandmarks()`, `rightHandWorldLandmarks()`, `timestampMs()`.

Options: confidence and suppression thresholds for face/pose/hand, `setOutputFaceBlendshapes`,
`setOutputPoseSegmentationMasks`, `setRunningMode`, result and error listeners. Notably **no**
`model_complexity` equivalent and no multi-person setting, so the Python-side `model_complexity=1`
lever (`extract_landmarks.py:56`) has no runtime counterpart — a skew source WS1's ablation should
quantify.

*(API details read from the published Maven artifact and paraphrased from the
[Android guide](https://developers.google.com/edge/mediapipe/solutions/vision/holistic_landmarker/android)
and [overview](https://developers.google.com/edge/mediapipe/solutions/vision/holistic_landmarker).
Content was rephrased for compliance with licensing restrictions.)*

### 6.2 Handedness: simplified, not solved

`VisionEngine.kt:146` currently reads
`hands.handedness()[h][0].categoryName()` and branches to offset 132 or 195. Under Holistic that
branch disappears — hands arrive pre-assigned. Both the legacy Python Holistic used for training
and the Tasks Holistic runtime assign in-graph, so **the app is the only component using a
different convention.**

What does **not** disappear: front-camera mirroring. `CameraPreviewView` feeds the raw front-camera
bitmap to MediaPipe. A mirrored image makes the graph label an anatomical left hand as the right
hand, consistently and silently. Because `FeedbackEngine` emits per-hand instructions ("your left
hand…"), a swap makes the project's actual pedagogical contribution confidently wrong.

**Design decision:** settle mirroring exactly once, here, under the Holistic runtime, with an
assertion test rather than reasoning. Do not fix it in the split-model code first — that work
would be discarded. This satisfies the "answered in one place, not two" requirement and absorbs
hardening task C1.

### 6.3 Golden-vector parity test

The pattern already exists and works. `FeedbackEngineParityTest.kt` loads JSON fixtures plus a
binary gold file from the test classpath, runs the Kotlin implementation, and asserts agreement
with Python-computed expectations within 0.05.

Extension for WS4:

| Aspect | Design |
|---|---|
| Input | Fixed frames committed as fixtures (images or pre-extracted raw landmarks — raw landmarks avoid committing likenesses, which suits the privacy constraint) |
| Expected | Python-computed `feature_spec_v2` vector, committed |
| Assertion | Per-block max absolute deviation within a stated tolerance, **plus** presence-flag exact equality |
| Default | Failing. A missing fixture must fail, not skip. |
| Gate | Parity failure blocks the WS4 gate |

Committing raw landmarks rather than frames keeps `AGENTS.md`'s no-raw-video rule intact and makes
the test runnable headless, which is what hardening task C3 enables.

### 6.4 Asset version enforcement

`VisionEngine.kt:62-65` reads `gold_standards.bin` as exactly `50 × 30 × 258` floats with a
hardcoded class count. In a new feature space this silently misreads rather than failing. Design:
every asset carries the feature-spec version and model hash; loading rejects a mismatch loudly.
This is what makes the rollback switch (WS7) safe.

## 7. WS5 — Feedback engine v2

### 7.1 Corrected scope

The engine already abstains when a hand is entirely absent (`feedback_engine.py:137, 190`). The
real defects are narrower and more specific:

| Defect | Location | Fix |
|---|---|---|
| No minimum support — a severity can rest on a handful of aligned frames | `handshape_score` / `orientation_score` | Require a minimum aligned-pair count; abstain below it |
| `overall_match` averages only firing items, so a milder extra error can raise it, and an empty list yields exactly 1.0 | `:204` | Score over all dimensions, not just those above threshold |
| Docstring says thresholds are provisional; `phase-gates.md` says expert-validated | module docstring vs `phase-gates.md` | Reconcile; record the real calibration basis |
| Gold standards pinned to 258 dims | `VisionEngine.kt:62-65` | Re-export version-stamped |

### 7.2 Re-validation scope is partial, and that matters for the timeline

DTW alignment uses **pose** wrists, not hand landmarks. Consequences:

- **TIMING and MOTION** derive from pose and remain valid. The 2026-07-23 expert sign-off holds
  for them.
- **HANDSHAPE and ORIENTATION** derive from hand landmarks in the changed feature space and need
  fresh sign-off.
- A new **NMM** dimension would need sign-off from scratch, and only if WS3 rung 4 shows signal.

So expert re-validation is two of four dimensions, not a full redo. This materially reduces the
risk that FSL Expert availability blocks the thesis timeline — the single largest schedule risk in
`docs/holistic-v2-risks.md`.

### 7.3 Abstention as a pedagogical position

A tutor that says "I could not see your hand" is more useful and more honest than one that guesses
a finger correction from three frames. The engine already does the strong version of this; WS5
extends it from binary presence to sufficient support. This is worth stating explicitly in the
thesis as a design choice rather than a limitation.

## 8. WS6 — Latency budget, re-derived

### 8.1 Why it cannot be inherited

`.kiro/steering/tech.md:42` defines the 150 ms budget as covering camera → landmark extraction →
inference → feedback → render. The only measurement available splits as: MediaPipe 35–63 ms for
**two** models, TFLite 0–2 ms. The headline "0–2 ms" excludes the dominant cost. Holistic adds a
face model.

### 8.2 Budget structure

Per-stage allocation summing to <150 ms, measured end-to-end on real hardware:

| Stage | Notes |
|---|---|
| Camera acquisition + conversion | Existing bitmap conversion is already a known GC pressure point (`VisionEngine.tick()` exists to avoid per-frame allocation) |
| Holistic inference | Pose + hand + face in one graph; replaces the measured 35–63 ms two-model cost. Sign of the delta is **unverified** — one graph may be cheaper than two through shared ROI work, or more expensive through the added face model. Must be measured, not assumed. |
| Feature construction | New derived features add cost; small but non-zero |
| Classifier | 0–2 ms measured; larger if a two-stream architecture is chosen |
| Feedback (DTW) | Currently O(n·m) DTW on 30×30 — cheap, but scales with any `seq_len` change |
| Render | Flutter overlay via EventChannel |

Note the pipeline samples every 4th frame and infers every 4th sample, so per-frame cost and
per-recognition latency are different numbers. WS6 must report both and be explicit about which
the 150 ms gate governs — the current evidence conflates them.

### 8.3 Degradation levers, pre-ranked

Ranked by expected accuracy cost, cheapest first, with the accuracy cost to be **measured** rather
than asserted:

1. Face channel at reduced cadence (face expression changes slowly relative to handshape)
2. Blendshapes instead of face landmarks, if not already chosen
3. Lite model variants
4. Wider frame-sampling stride
5. Drop the face channel entirely — returns to a hands+pose model, still better than today's if
   WS1 and WS2 landed

Hard rule: the face channel is sacrificed before the hand channel, in every case. Hands carry the
confusion-pair signal; the face is a hypothesis under test.

### 8.4 Baseline symmetry

Both the 258-dim baseline and Holistic v2 must be benchmarked on the same device under the same
three conditions. Without the baseline measured on real hardware, "Holistic v2 is slower" cannot
be distinguished from "real hardware is slower than an M1 emulator" — and the latter is likely
true by a wide margin.

## 9. WS7 — Governance and rollback

### 9.1 Gate re-opening

Gates 2, 3, 4, 5, and 6 rest on the 258-dim feature space and are re-opened by a feature-space
change. Gate 1 (preprocessing) is re-opened only if re-extraction happens. Design: annotate the
existing table with a re-opened marker and new criteria rather than rewriting rows that hardening
tasks A2 and D7 are already editing, to avoid a merge conflict over the same lines.

### 9.2 Rollback switch

Holistic v2 ships behind a runtime switch with the 258-dim path intact until WS3 and WS6 pass.
Requirements: both asset sets installable; version stamps enforced at load (§6.4); the switch
recorded in session logs so a benchmark or study result can be attributed to the correct pipeline.

The switch is what makes acceptance criterion 6 — the defined "no" — real rather than rhetorical.
Without it, rejecting Holistic v2 late means reverting code under deadline pressure.

### 9.3 Stack deviations to resolve

| Locked | Actual | Resolution |
|---|---|---|
| `tech.md:8` MediaPipe Holistic for landmark extraction | `VisionEngine.kt:9-10` split Pose + Hand landmarkers | WS4 brings the app into compliance |
| `tech.md:11` Google Colab (GPU) for training | `"local M1 (tensorflow 2.19.0)"` in all four logged runs | Either amend steering or record the deviation — PM decision |

## 10. Correctness properties

Properties that must hold regardless of implementation choices:

1. **Single layout authority.** No feature layout constant exists outside `feature_spec_v2.json`
   in either language.
2. **Absence is distinguishable.** No absent block is numerically identical to a present block.
3. **Parity is enforced, not asserted.** The golden-vector test fails by default and runs in CI.
4. **Ablation completeness.** Every shipped feature block has a run showing its contribution; every
   dropped block has one too.
5. **No inherited measurements.** No performance claim survives the feature-space change without
   re-measurement on real hardware.
6. **Asset/model agreement.** A version mismatch fails loudly at load.
7. **Abstention over fabrication.** Insufficient channel support yields abstention, never a
   confident correction.
8. **Reversibility.** The 258-dim path stays runnable until its replacement is proven better.

## 11. Open questions

1. **Python-side face representation** — move Python to Tasks `HolisticLandmarker` for blendshape
   parity, or use a landmark subset on both sides? (§4.4; PM decision)
2. **Face mesh variant** — base 468 or refined 478? (§4.4; forced by the runtime's 553)
3. **Does the Tasks graph populate pose `visibility`?** `unverified`; the current vector consumes
   it as the 4th component per pose landmark.
4. **Is one Holistic graph cheaper or dearer than two separate detectors?** `unverified`; sign of
   the change is unknown and the whole WS6 budget depends on it.
5. **Signer-disjointness** — resolve via the body-geometry clustering probe, the dataset paper, or
   an explicit limitation statement. Blocks any signer-independence claim.
6. **Test-set strategy** — cross-validation or re-split. Blocks WS3 rung comparison.
