# Phase 12 — On-Device Integration Design

## 1. Inference Call Sequence

```
┌─ Camera Thread ─────────────────────────────────────────────────────┐
│ CameraX frame callback (30 FPS)                                     │
│   └─ Check: pipeline busy? ──→ YES: drop frame                     │
│                              └─ NO: post to inference executor      │
└─────────────────────────────────────────────────────────────────────┘
                                    │
┌─ Inference Thread ────────────────▼─────────────────────────────────┐
│ 1. MediaPipe Holistic process(rgb_frame)                            │
│    └─ Extract 33 pose + 42 hand landmarks → 258 features per frame  │
│ 2. Append to sliding window buffer (30 frames)                      │
│ 3. When buffer full:                                                │
│    a. Normalize sequence (root-center, torso-scale)                 │
│    b. Set TFLite input tensor (1, 30, 258) float32                  │
│    c. Invoke TFLite interpreter                                     │
│    d. Read output: softmax probabilities (50 classes)               │
│    e. If confidence > threshold:                                    │
│       - Classification result ready                                 │
│       - If practice mode: invoke feedback engine                    │
│ 4. Post result to main thread via Handler                           │
└─────────────────────────────────────────────────────────────────────┘
                                    │
┌─ Main Thread ─────────────────────▼─────────────────────────────────┐
│ Update UI: prediction label, confidence, feedback items, FPS        │
└─────────────────────────────────────────────────────────────────────┘
```

## 2. Latency Budget Table

| Step | Target (ms) | Measured (Emulator) | Risk |
|------|------------|-------------------|------|
| Frame capture + format conversion | 5 | ~3 | Low |
| MediaPipe Holistic inference | 80 | TBD real device | **HIGH** — dominant cost |
| Buffer management + normalization | 2 | <1 | Low |
| TFLite model inference | 10 | 0-2 | Low (tiny model) |
| Feedback engine (DTW + scoring) | 15 | TBD | Medium (DTW is O(n²) on 30 frames) |
| Channel transfer + UI render | 5 | <5 | Low |
| **TOTAL** | **<150** | **~30 (emulator, not representative)** | |

**Critical path:** MediaPipe Holistic. If it exceeds 100ms on real hardware, the total budget is blown. Mitigation: reduce model_complexity, or skip every other frame for landmark extraction while interpolating.

## 3. Confidence Thresholds

| Threshold | Value | Behavior |
|-----------|-------|----------|
| Display threshold | 40% | Below this, show "Processing..." (no prediction displayed) |
| Classification threshold | 60% | Below this, show prediction but flag as uncertain |
| Feedback trigger | 70% | Below this, don't run feedback engine (unreliable classification) |
| High confidence | 85% | Green indicator; feedback results are trustworthy |

**Rationale:** The model achieves 95% accuracy on clean test data, but real-world conditions (lighting, angle, partial occlusion) will reduce effective confidence. Setting the feedback trigger at 70% ensures the engine only produces feedback when the classification is reasonably certain.

## 4. Sliding Window Buffer

- **Size:** 30 frames (matching model input)
- **Fill strategy:** Accumulate frames sequentially; trigger inference when full
- **Reset:** Clear buffer when practice mode starts or sign selection changes
- **Overlap:** No sliding overlap for MVP (capture → infer → reset → next attempt)

## Status

**Complete.** Integration running end-to-end on emulator. Real-device latency profiling pending (Phase 18).
