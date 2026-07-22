# Phase 4 — Data Pipeline Design

## 1. Pipeline Overview

```
Raw Video (.MOV)          MediaPipe Holistic         Normalization          Augmentation
  FSL-105 clips     -->   Per-frame landmarks   -->   Root-centered,   -->   Geometric in
  (50 classes)            (1662 floats/frame)        torso-scaled,         landmark space
                                                     fixed-length seq      (train only)
```

**Implementation:** `training/preprocessing/extract_landmarks.py` → `build_sequences.py` → `training/augmentation/augment_landmarks.py`

---

## 2. Landmark Extraction

### MediaPipe Configuration

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Model | MediaPipe Holistic | Provides pose + face + hands in a single pass |
| Version | mediapipe 0.10.14 | Pinned for reproducibility |
| `static_image_mode` | False | Video mode: uses temporal tracking for smoother landmarks |
| `model_complexity` | 1 | Balanced accuracy/speed; complexity 2 is overkill for training data (not real-time) |
| `refine_face_landmarks` | False | Saves computation; face landmarks serve normalization more than classification (dropped in best model) |

### Feature Vector Per Frame (1662 floats)

| Component | Landmarks | Values per landmark | Total |
|-----------|-----------|-------------------|-------|
| Pose | 33 | 4 (x, y, z, visibility) | 132 |
| Face | 468 | 3 (x, y, z) | 1,404 |
| Left hand | 21 | 3 (x, y, z) | 63 |
| Right hand | 21 | 3 (x, y, z) | 63 |
| **Total** | | | **1,662** |

### Missing Detection Handling

- Undetected components (hand, face, or pose) are **zero-filled** per frame
- Detection rates are logged per clip (`extraction_log.csv`) so failures are visible, not hidden
- This is standard practice in landmark-based SLR; the model learns that zeros = absent

### Alternative Feature Set: `no_face` (258 floats)

Drops the 468×3 face landmarks entirely:
- Pose: 132 + Hands: 126 = **258 features**
- **This variant achieved the best accuracy (95.07%)** and became the deployed model
- Justification: Face landmarks are noisy (large feature space with high variance) and sign semantics are carried primarily by hands + pose. Dropping face reduces overfitting risk and cuts feature dimensionality by 84%.

---

## 3. Normalization Strategy

### Mathematical Definition

Per frame `t`, given landmarks in normalized camera coordinates (0–1):

1. **Root translation:** Compute root = midpoint(pose[23], pose[24]) (mid-hip). Subtract root from all landmark (x, y, z) coordinates.

2. **Torso scaling:** Compute scale = ||midpoint(pose[11], pose[12]) − root|| (mid-shoulder to mid-hip distance). Divide all (x, y, z) by scale.

3. **Dead frame handling:** If a frame has no pose detection (sum of absolute values = 0), keep it all-zeros (no spurious normalization applied to zero vectors).

4. **Missing block preservation:** After normalization, restore zeros for face/hand blocks that were originally undetected (prevents the translation/scaling from turning zeros into non-zero artifacts).

### Justification

- **Root-centering** removes dependence on signer's position within the camera frame
- **Torso-scaling** removes dependence on distance from camera (closer = larger raw landmarks)
- Combined: the model sees a canonical, signer-position-invariant representation
- Preserving zeros for missing detections lets the model learn "hand not visible" as a signal, not noise

---

## 4. Temporal Windowing

### Sequence Length: 30 frames

| Parameter | Value | Justification |
|-----------|-------|---------------|
| `seq_len` | 30 | FSL-105 clips are ~242–246 frames at source FPS; 30 temporal samples captures the full sign trajectory at ~8× temporal compression |
| Sampling method | Uniform linear interpolation (`np.linspace(0, n-1, 30)`) | Preserves temporal structure regardless of source video length |
| Short clip handling | Repeat last frame to pad | Clips <30 frames are rare in FSL-105 (min 242); padding is a safety measure |

### Justification for 30 frames

- FSL signs are typically 1–3 seconds; 30 samples provides ~10–30 ms temporal resolution
- Matches common practice in landmark-based SLR literature
- Balances temporal detail against memory/compute for training and on-device inference

---

## 5. Train/Test Split Methodology

### Split Source: FSL-105 Original CSVs

| Split | Samples (50 classes) | Source |
|-------|---------------------|--------|
| Train | 813 | `train.csv` from FSL-105 |
| Test | 203 | `test.csv` from FSL-105 |
| Ratio | ~80/20 | Preserved from dataset authors |

### Critical Decision: No Reshuffling

The split is preserved exactly as published by Tupal & Villaverde. **Never reshuffled** in the pipeline.

**Rationale:**
- Reproducibility: anyone with the same dataset gets the same split
- Comparability: results can be compared to other work using FSL-105
- Avoiding information leakage from post-hoc split optimization

### Acknowledged Limitation: Signer Independence Unknown

FSL-105 CSVs carry no signer IDs. Whether train/test samples come from different signers cannot be verified from metadata. If the same signer appears in both splits, reported accuracy may be inflated. This is documented as a known limitation in the methodology chapter (see Phase 3 audit, §5).

---

## 6. Augmentation Strategy

### Technique: Geometric Transforms in Landmark Space (Train Only)

| Transform | Range | Justification |
|-----------|-------|---------------|
| In-plane rotation | ±10–15° (sign randomized) | Simulates tilted camera or signer not perfectly upright; range is conservative to avoid anatomically impossible poses |
| Scale | 0.90–1.10 | Simulates slight distance variation beyond what torso-normalization already handles |
| X/Y shift | ±0.10 (normalized units) | Simulates off-center positioning within frame |

### Parameters

| Parameter | Value |
|-----------|-------|
| Factor | 3× (813 original → 3,252 augmented train samples) |
| Seed | 20260705 (date-based, committed) |
| Test split | **Never augmented** |
| Missing block handling | Augmented positions are masked back to zero where original was zero |

### What Is NOT Applied (and Why)

| Technique | Reason for exclusion |
|-----------|---------------------|
| Horizontal flip | FSL signs are NOT left-right symmetric; flipping would create anatomically correct but semantically wrong signs (e.g., right-hand dominant sign executed with left hand) |
| Time warping | Could alter timing dimension that the feedback engine measures; risky for Phase 10 |
| Gaussian noise on landmarks | Risk of moving landmarks outside anatomically plausible range; no clear literature support for improvement |
| Brightness/contrast (pixel-space) | Available via `--brightness` flag but NOT used in final pipeline; landmark extraction already produces normalized coordinates that are largely photometry-invariant |

### Augmentation Applied In Landmark Space (Not Pixel Space)

**Key design choice:** Augmentation operates on already-extracted landmarks, not raw video frames.

- **Advantage:** Orders of magnitude faster (no re-running MediaPipe on augmented video); transforms are exact (no interpolation artifacts); fully reproducible from the log
- **Disadvantage:** Cannot augment MediaPipe's detection behavior (e.g., testing if it handles dark frames). Pixel-space augmentation at extraction time (`--brightness`) exists as a fallback if needed.

---

## 7. Reproducibility Guarantees

| Artifact | Reproducibility mechanism |
|----------|--------------------------|
| Landmark extraction | Pinned mediapipe version, deterministic frame-by-frame processing, logged detection rates |
| Sequence building | Deterministic uniform sampling, no randomness |
| Augmentation | Seeded RNG (20260705), every per-sample transform logged in `augment_log.json` |
| Train/test split | Preserved from source CSVs, never reshuffled |
| Dataset version | Referenced by file path; audit report records clip counts and integrity |

---

## 8. Pipeline Output Summary

| Output | Shape | Location |
|--------|-------|----------|
| `X_train_aug.npy` | (3252, 30, 258) | `../kumpas-data/sequences/` |
| `y_train_aug.npy` | (3252,) | `../kumpas-data/sequences/` |
| `X_test.npy` | (203, 30, 258) | `../kumpas-data/sequences/` |
| `y_test.npy` | (203,) | `../kumpas-data/sequences/` |
| `label_map.json` | 50 entries | `../kumpas-data/sequences/` |
| `augment_log.json` | per-sample transforms | `training/augmentation/` (committed) |
| `extraction_log.csv` | per-clip detection rates | `training/preprocessing/` (committed) |

**Note:** The deployed model uses `no_face` (258 features). Full (1662) features available but performed worse.

---

## 9. Known Issues & Mitigations

| Issue | Impact | Mitigation |
|-------|--------|-----------|
| 2 clips with <10% hand detection (class 5 "IM FINE") | Potential noise in class 5 training data | Retained (model should handle edge cases); flagged for error analysis |
| No signer IDs in metadata | Cannot verify signer-independent split | Documented as limitation; split preserved from authors |
| Face landmarks dropped in best model | Feedback engine cannot use face orientation | Acceptable: FSL-105 signs are primarily hand/arm articulated |

---

## Status

**Complete.** All acceptance criteria from `requirements.md` met:
- ✅ Landmark extraction spec names MediaPipe Holistic 0.10.14 and exact landmark indices (33 pose × 4, 468 face × 3, 42 hands × 3)
- ✅ Normalization strategy documented with mathematical definition (root-center at mid-hip, scale by torso length)
- ✅ Each augmentation technique has explicit justification (not "because it's common")
- ✅ Split methodology documented with seed for reproducibility (preserved from FSL-105 CSVs; augmentation seed 20260705)
- ✅ Pipeline produces logged output traceable to a specific dataset version
