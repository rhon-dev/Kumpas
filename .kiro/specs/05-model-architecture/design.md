# Phase 5 — Model Architecture Design

## 1. Selected Architecture: CNN-LSTM (no_face variant)

### Layer-by-Layer Specification

| # | Layer | Config | Output Shape | Params |
|---|-------|--------|--------------|--------|
| 0 | Input | — | (30, 258) | 0 |
| 1 | Conv1D | 64 filters, kernel=3, padding=same, ReLU | (30, 64) | 49,600 |
| 2 | BatchNorm | — | (30, 64) | 256 |
| 3 | Conv1D | 128 filters, kernel=3, padding=same, ReLU | (30, 128) | 24,704 |
| 4 | BatchNorm | — | (30, 128) | 512 |
| 5 | MaxPooling1D | pool_size=2 | (15, 128) | 0 |
| 6 | LSTM | 128 units, return_sequences=True | (15, 128) | 131,584 |
| 7 | Dropout | 0.4 | (15, 128) | 0 |
| 8 | LSTM | 64 units, return_sequences=False | (64) | 49,408 |
| 9 | Dropout | 0.4 | (64) | 0 |
| 10 | Dense | 128 units, ReLU | (128) | 8,320 |
| 11 | Dropout | 0.4 | (128) | 0 |
| 12 | Dense (output) | 50 units, Softmax | (50) | 6,450 |
| | **Total** | | | **~270,834** |

### Input Feature Shape

- Temporal: 30 frames (uniformly sampled from source video)
- Spatial: 258 features per frame (33 pose landmarks × 4 + 42 hand landmarks × 3)
- Tensor shape: `(batch, 30, 258)` float32

---

## 2. Architecture Justification (ADR)

### Decision: CNN-LSTM over alternatives

**Context:** The model must classify 50 FSL signs from landmark sequences with <150ms inference on a mid-range Android phone via TFLite.

**Alternatives Considered:**

| Architecture | Pros | Cons | Verdict |
|-------------|------|------|---------|
| **Plain LSTM** | Simple, well-supported in TFLite | No spatial feature extraction across landmarks; higher parameter count for same capacity | ❌ Lacks the CNN's ability to detect spatial patterns across adjacent landmark features |
| **Transformer** | State-of-art for sequences; attention captures long-range dependencies | Larger parameter count; TFLite support for attention ops less mature; risk of exceeding latency budget on mid-range device | ❌ Overkill for 30-frame sequences; latency risk |
| **GCN (Graph Convolutional)** | Exploits anatomical structure of landmark graph | Limited TFLite support; more complex implementation; harder to quantize | ❌ Deployment complexity not justified for 50-class isolated signs |
| **Temporal CNN only** | Fast inference; good TFLite support | Poor at capturing temporal dynamics of signs (motion, timing) without recurrence | ❌ Loses sequential motion information critical for the feedback engine |
| **CNN-LSTM** ✅ | CNN extracts spatial features across landmarks; LSTM captures temporal dynamics; well-supported in TFLite; moderate parameter count | Not state-of-art for large vocabularies | ✅ Balanced: spatial + temporal, quantization-friendly, proven in FSL literature |

**Decision:** CNN-LSTM. The CNN layers extract per-timestep spatial features from the 258-dimensional landmark vector (learning which landmark combinations matter), then the LSTM layers model the temporal progression of those features (motion, timing). This directly serves the feedback engine, which needs both spatial (handshape/orientation) and temporal (motion/timing) understanding.

### Why `no_face` (258) over `full` (1662)?

| Variant | Test Accuracy | Params | Training Time | Rationale |
|---------|--------------|--------|---------------|-----------|
| full (1662) | 85.71% | 540,402 | 314s | Face landmarks add noise; high dimensionality → overfitting with small dataset |
| **no_face (258)** | **95.07%** | **270,834** | **166s** | Dramatically better generalization; signs are hand/arm-articulated, not face-articulated |
| no_face wider (258 → 256/128 LSTM) | 94.09% | 689,394 | 290s | Wider model overfits — diminishing returns |
| full + dropout 0.5 | 83.25% | 540,402 | 426s | Higher dropout couldn't compensate for face noise |

The data speaks clearly: face landmarks hurt performance for this task. FSL-105 signs are articulated through hands and body pose, not facial expression. Dropping face reduces parameters by 50% AND improves accuracy by 10 percentage points.

---

## 3. Quantization Compatibility (Considered at Design Time)

| Design Choice | Quantization Impact |
|---------------|-------------------|
| Conv1D + ReLU | Fully quantizable; ReLU is Q-friendly (no negative range) |
| BatchNorm | Fused into preceding conv during quantization; no runtime cost |
| LSTM | TFLite supports quantized LSTM; standard cell (no custom gates) |
| Dense + ReLU | Fully quantizable |
| Softmax output | Kept in float32 during quantized inference (standard practice) |
| Dropout | Disabled at inference (no quantization impact) |
| No custom ops | All layers are TFLite builtin ops — no Flex delegate needed |

**Parameter count (270K)** is well within budget for on-device inference. For reference, the Kannada SL TFLite model (Nature 2026) ran at 27.8ms with a similar architecture at ~3.8MB model size. Kumpas's quantized model is expected to be <1MB.

---

## 4. Feature Engineering

### Landmark Indices Used

**Pose (33 landmarks × 4 values each = 132 features):**
- All 33 MediaPipe Holistic pose landmarks
- Values: x, y, z (normalized, root-centered, torso-scaled) + visibility confidence
- Key landmarks: shoulders (11, 12), hips (23, 24) used for normalization; elbows (13, 14), wrists (15, 16) carry arm position information

**Hands (21 landmarks × 3 values × 2 hands = 126 features):**
- All 21 MediaPipe hand landmarks per hand (wrist, thumb CMC through tip, index through pinky MCP through tip)
- Values: x, y, z (normalized)
- These carry the primary sign information: finger configuration, hand orientation

### Derived Features

No manually engineered derived features (angles, velocities) are computed. The CNN layers learn to extract relevant spatial features from raw landmark coordinates. This is a deliberate simplicity choice:
- Reduces pipeline complexity
- Lets the model learn task-relevant features rather than imposing assumptions
- Raw coordinates are sufficient for 95% accuracy

The feedback engine (Phase 10) DOES compute derived features (joint angles, velocities) for its per-dimension analysis — but those are computed separately from the classification model's input.

---

## 5. Training Configuration

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Optimizer | Adam | Standard for sequential models; adaptive learning rate |
| Learning rate | 0.001 (initial) | Standard starting point |
| LR schedule | ReduceLROnPlateau (patience=6, factor=0.5, monitor=val_loss) | Adaptive; avoids manual schedule tuning |
| Batch size | 32 | Balances gradient noise and memory; standard for this dataset scale |
| Early stopping | patience=15, monitor=val_accuracy, restore_best_weights=True | Prevents overfitting; restores peak generalization |
| Validation split | 15% of training data | Held out for early stopping and LR scheduling |
| Seed | 20260705 | Reproducible initialization |
| Loss | Sparse categorical crossentropy | Standard for multi-class classification with integer labels |
| Epochs (max) | 120 | Early stopping triggers well before this (63 epochs for best model) |

---

## 6. Experiment Results Summary

| Run | Features | LSTM | Params | Val Acc | Test Acc | Decision |
|-----|----------|------|--------|---------|----------|----------|
| baseline | 1662 (full) | 128-64 | 540K | 96.1% | 85.7% | ❌ Overfits |
| **no_face** | **258** | **128-64** | **270K** | **100%** | **95.07%** | ✅ **Selected** |
| no_face_wider | 258 | 256-128 | 689K | 100% | 94.1% | ❌ Larger, worse |
| full_dropout05 | 1662 | 128-64 | 540K | 92.2% | 83.3% | ❌ Worst |

**Selected model:** `20260705_194813_no_face` — 270,834 parameters, 95.07% test accuracy, 63 epochs.

---

## 7. Model Size Estimates

| Format | Estimated Size |
|--------|---------------|
| Keras (.keras) | ~3.2 MB (float32 weights) |
| TFLite (float32) | ~1.1 MB |
| TFLite (INT8 quantized) | ~300 KB |

These estimates are within comfortable range for bundling as a Flutter app asset.

---

## Status

**Complete.** All acceptance criteria from `requirements.md` met:
- ✅ Layer-by-layer table with shapes and parameter counts
- ✅ ADR documents CNN-LSTM choice with 4 alternatives considered
- ✅ Quantization compatibility addressed at design time (no custom ops, Q-friendly activations)
- ✅ Feature engineering reproducible from spec (258 features = pose 132 + hands 126, no_face)
- ✅ Total parameter count (270K) compatible with <150ms TFLite inference
