# Phase 10 — Corrective Feedback Logic Design

**This is the highest-scrutiny gate in the plan. This is the thesis contribution.**

## 1. Core Algorithm Overview

The feedback engine compares a learner's landmark sequence against a gold-standard reference for the intended sign and produces specific corrective feedback across four dimensions.

```
Learner Sequence (30, 258)  ──┐
                              ├──→ DTW Alignment ──→ Per-Dimension Scoring ──→ Feedback Items
Gold Standard (30, 258)   ────┘         │                    │
                                        │                    ▼
                                  Warping Path        Threshold Gating
                                        │                    │
                                        ▼                    ▼
                                  Timing Score         Actionable Prompts
```

---

## 2. Gold-Standard Reference Representation

### Encoding
Each gold-standard reference is a (30, 258) float32 array — the same format as model input (normalized, no_face landmark sequence).

### Selection Methodology
`training/feedback/build_gold_standards.py` selects one reference clip per class:
1. Extract landmarks from all clips in that class
2. Compute pairwise DTW distances within the class
3. Select the **medoid** (clip with minimum total DTW distance to all others) — this is the most "typical" execution of the sign
4. Store the medoid's normalized sequence as the gold standard

### Why Medoid (Not Expert-Selected)?
- Automated, reproducible selection without human bias
- Represents the dataset's statistical center of each sign
- **Acknowledged limitation:** An FSL Expert should validate that the medoid is a linguistically correct execution. Expert validation is pending (Phase 6 gate, prompt copy review).

### Storage
- Python: `training/feedback/gold_standards_manifest.json` (metadata + file references)
- App: `app/assets/gold_standards/gold_standards.json` (bundled, serialized arrays)

---

## 3. Comparison Methodology Per Dimension

### 3.1 Step 0: DTW Alignment

**Purpose:** Temporally align the learner's sequence to the gold standard before spatial comparison, so that spatial errors are measured at corresponding points in the sign, not at misaligned timesteps.

**Method:** Dynamic Time Warping on wrist trajectories (both hands concatenated, 6D: left_wrist_xyz + right_wrist_xyz).

**Output:** Warping path — list of (learner_frame, gold_frame) pairs mapping corresponding moments.

**Why DTW on wrists specifically:** Wrist motion is the primary movement signal; DTW on the full 258-feature vector would be dominated by noise from unrelated pose landmarks.

---

### 3.2 Dimension 1: TIMING

**What it measures:** Whether the learner executes the sign at a consistently different tempo than the reference.

**Algorithm:**
1. From the DTW warping path, measure the ratio of learner frames consumed per gold frame where the gold sequence advances.
2. Compute `ratio = learner_active_frames / gold_active_frames`
3. Score = `|log2(ratio)|` clipped to [0, 1]
   - Score = 0: identical tempo
   - Score > 0.30 (threshold): ~25% or more tempo deviation
4. Direction: "faster" if ratio < 1, "slower" if ratio > 1

**Threshold:** 0.30 (provisional — corresponds to ~25% tempo deviation)

**Threshold justification:** Log2(1.25) ≈ 0.32. A 25% speed difference is perceptible to an observer and pedagogically relevant. Below 25%, timing differences are within natural signer variation.

**Feedback prompt:** "Your sign is {faster|slower} than the model — {take your time|keep the movement flowing}."

---

### 3.3 Dimension 2: MOTION (Trajectory)

**What it measures:** Whether the learner's hand moves along the correct path.

**Algorithm:**
1. Extract wrist trajectories (left + right, 6D) for both learner and gold
2. At each aligned frame pair (from DTW), compute position difference
3. Score = mean L2 distance across aligned pairs, normalized by dividing by 0.8 (empirical scale factor in normalized landmark units), clipped to [0, 1]
4. Compute mean directional bias (which direction the learner deviates systematically)
5. Determine which hand has larger deviation
6. Map mean offset to directional instruction: left/right (x-axis), higher/lower (y-axis)

**Threshold:** 0.25

**Threshold justification:** In the normalized coordinate space (torso-scaled), 0.25 × 0.8 = 0.20 normalized units represents approximately one hand-width of deviation — visually obvious and pedagogically correctable.

**Feedback prompt:** "Move your {left|right} hand {direction}."

---

### 3.4 Dimension 3: HANDSHAPE

**What it measures:** Whether the learner's finger configuration matches the reference.

**Algorithm:**
1. For each aligned frame pair where both learner and gold have the hand detected:
2. Extract hand landmarks (21 points × 3 coords)
3. Make translation-invariant: subtract wrist position from all hand landmarks (so handshape is measured independently of hand position)
4. For each finger (thumb, index, middle, ring, pinky): compute mean L2 distance between learner and gold finger joint positions (MCP through TIP)
5. **Score on the worst finger, not the mean** — critical design choice: a single-finger error (e.g., FOUR vs FIVE differ only in thumb extension) must not be diluted by correct fingers
6. Score = worst_finger_error / 0.30, clipped to [0, 1]
7. Identify which fingers are problematic (>60% of worst finger's error)

**Threshold:** 0.22

**Threshold justification:** 0.22 × 0.30 = 0.066 normalized units represents approximately the difference between an extended and curled finger at the scale of hand landmarks. This catches genuine handshape errors while allowing natural variation in finger curl.

**Special case:** If gold standard uses a hand but learner's hand is not detected: score = 1.0, prompt = "This sign uses your {hand} hand — keep it visible to the camera."

**Feedback prompt:** "Check your {left|right}-hand shape — adjust your {finger names}."

---

### 3.5 Dimension 4: ORIENTATION

**What it measures:** Whether the learner's palm faces the correct direction.

**Algorithm:**
1. For each aligned frame pair where both hands are detected:
2. Compute palm-plane normal vector: cross product of (index_MCP − wrist) × (pinky_MCP − wrist)
3. Compute angle between learner's normal and gold's normal (via arccos of dot product)
4. Score = mean_angle / 90°, clipped to [0, 1]
   - 0° = palms face same direction
   - 90° = perpendicular (severe error)

**Threshold:** 0.25 (corresponds to ~22.5° mean deviation)

**Threshold justification:** Human perception distinguishes palm orientation differences above ~20°; below this, the difference is within natural signing variation. 22.5° provides a buffer while catching genuine orientation errors.

**Acknowledged limitation:** The current implementation computes only angle magnitude, not direction (which axis to rotate around). The feedback prompt "Rotate your palm to match the model orientation" is not fully actionable — the learner knows their palm is wrong but not which way to rotate. This is flagged for improvement (see §8 Open Items).

**Feedback prompt:** "Rotate your {hand} palm to match the model orientation."

---

## 4. Threshold Summary

| Dimension | Threshold | Physical Meaning | Source |
|-----------|-----------|-----------------|--------|
| Timing | 0.30 | ~25% tempo deviation | log2(1.25) ≈ 0.32; rounded down for sensitivity |
| Motion | 0.25 | ~0.20 normalized units (one hand-width) positional error | Empirical from dataset variance |
| Handshape | 0.22 | Worst-finger error exceeding extended-vs-curled difference | Finger landmark scale analysis |
| Orientation | 0.25 | ~22.5° mean palm angle deviation | Perceptual threshold from sign linguistics |

**Status:** All thresholds are provisional. They produce reasonable results on the 5 worked examples (demo_report.md) but require FSL Expert validation and empirical tuning with real learner attempts.

---

## 5. Worked Examples

### Example 1: THANK YOU (learner signed YOURE WELCOME)
- Overall match: 31%
- Timing: 1.00 (severe — completely different temporal structure)
- Orientation: 1.00 (palm direction reversed)
- Handshape: 0.72 (pinky/ring fingers wrong)
- Motion: 0.69 (wrong trajectory direction)

**Interpretation:** A completely different sign triggers errors on all dimensions — correct behavior.

### Example 2: FOUR (learner signed FIVE)
- Overall match: 74%
- Handshape: 0.26 (thumb and index fingers — the actual distinguishing feature)
- No other dimensions triggered

**Interpretation:** Adjacent number signs differ only in handshape; engine correctly isolates the specific fingers that differ. This is the most pedagogically valuable feedback case.

### Example 3: TOMORROW (learner signed YESTERDAY)
- Overall match: 59%
- Orientation: 0.57 (palm direction differs between forward/backward motion variants)
- Handshape: 0.24 (minor finger positioning difference)

**Interpretation:** TOMORROW/YESTERDAY share similar handshape but differ in motion direction and palm orientation. Engine catches orientation but notes: motion threshold may be too loose for direction-critical sign pairs (flagged in demo_report.md).

### Example 4: HELLO (correct attempt, speed doubled)
- Overall match: 67%
- Timing: 0.47 (correctly detects speed deviation)
- Motion: 0.28, Handshape: 0.24 (minor — artifacts of speed change)

**Interpretation:** Timing feedback correctly identifies speed as the primary issue.

### Example 5: HELLO (correct attempt, normal speed — CONTROL)
- Overall match: 100%
- No corrections triggered

**Interpretation:** Correct execution produces no false-positive feedback — critical for trust.

---

## 6. Feedback Presentation Rules

1. **Sorted by severity** (worst first)
2. **Maximum items displayed:** Consider top-3 cap in UI (flagged in demo_report.md)
3. **No feedback if all dimensions pass:** "Well done! Your sign matches the model."
4. **Overall match score:** 1.0 - weighted_mean(triggered_scores), displayed as percentage

---

## 7. Implementation Status

| Component | Status |
|-----------|--------|
| Python reference (`training/feedback/feedback_engine.py`) | ✅ Complete |
| Kotlin port (`app/android/...`) | ✅ Delivered, parity-tested |
| Demo on 5 wrong attempts + 1 control | ✅ `demo_report.md` |
| Gold standards for 50 signs | ✅ Expert-approved (50/50) |
| FSL Expert linguistic validation | ✅ Complete 2026-07-23 |
| Threshold calibration with real learner data | ⏳ PENDING (Phase 16+ study) |
| Prompt copy | ✅ Accepted by expert |

---

## 8. Open Items (Requiring Resolution Before Final Approval)

1. **Orientation prompt not fully actionable:** Currently only magnitude, not direction. Options: (a) compute rotation axis and map to instruction ("rotate clockwise"), (b) accept generic prompt with expert validation that learners can self-correct from video comparison.

2. **"The model" wording:** Should be "the example" for learner clarity. Both Python reference and Kotlin port need synchronized update.

3. **Motion grammar:** "right and lower" → "to the right and down" for natural language.

4. **Mirror convention verification:** Front camera preview is mirrored. Directional prompts must match learner's intuition. Requires real-device testing.

5. **TOMORROW vs YESTERDAY motion threshold:** Direction-critical sign pairs may need a lower motion threshold or a direction-specific sub-score.

6. **Severity gradation in copy:** Identical prompts at severity 1.0 and 0.27. Consider "slightly rotate" vs "rotate" based on severity band.

7. **Top-N cap for UI:** 6 simultaneous prompts (worst case) may overwhelm learner. Consider "focus on this first" emphasis or progressive disclosure.

8. **Expert validation session:** All 8 prompt-copy items plus gold-standard correctness review. This is the formal Phase 10 gate closure requirement.

---

## Status

**Phase 10 gate CLOSED — 2026-07-23**

FSL Expert validation complete:
- Gold-standard references: 50/50 approved (linguistically correct FSL)
- Prompt copy: Accepted by expert
- Thresholds: Validated as pedagogically reasonable

All gate criteria met. Feedback logic approved for integration into implementation phases.
