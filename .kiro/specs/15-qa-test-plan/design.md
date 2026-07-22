# Phase 15 — QA & Test Plan Design

## 1. Test Layers

### Unit Tests (Python — Training Pipeline)
| Test | Covers | Priority |
|------|--------|----------|
| Normalization correctness | Root-centering, torso-scaling produce expected values on synthetic input | High |
| Augmentation invertibility | Transform + inverse returns near-original | Medium |
| Feedback timing score | Known warping paths produce expected tempo scores | High |
| Feedback handshape score | Synthetic finger differences produce expected finger identification | High |
| Feedback orientation score | Known palm normals produce expected angle scores | High |
| Threshold gating | Scores below threshold produce no feedback items | High |
| Gold-standard medoid selection | Medoid is closest to all other clips in class | Medium |

### Unit Tests (Kotlin — On-Device Pipeline)
| Test | Covers | Priority |
|------|--------|----------|
| Feedback engine parity | Kotlin output matches Python reference on same inputs | Critical |
| Normalization parity | Kotlin landmark normalization matches Python | High |
| Label map loading | 50 classes load correctly from bundled JSON | Medium |
| Confidence threshold gating | Below-threshold predictions don't trigger feedback | High |

### Integration Tests
| Test | Covers | Priority |
|------|--------|----------|
| Model load + inference | TFLite model loads and produces valid softmax output | Critical |
| End-to-end pipeline | Synthetic landmarks → model prediction → feedback report | High |
| Gold standard loading | All 50 gold standards load and have correct shapes | High |
| Camera → prediction | Live camera frame reaches prediction callback | High |

### Device-Matrix Tests
| Test | Devices | Priority |
|------|---------|----------|
| FPS sustained ≥24 for 60s | All target devices | Critical |
| Latency <150ms (p95) | All target devices | Critical |
| No crash on deny permission | All target devices | High |
| No crash on rotation | All target devices | Medium |

## 2. Device Matrix

| # | Device | Chipset | RAM | Android | Rationale |
|---|--------|---------|-----|---------|-----------|
| 1 | Samsung Galaxy A14 | Helio G80 | 4 GB | Android 13 | Lower-bound mid-range |
| 2 | Redmi Note 12 | Snapdragon 685 | 4 GB | Android 13 | Popular mid-range |
| 3 | (TBD by author) | — | ≥4 GB | ≥Android 9 | Third device for diversity |

## 3. Regression Testing

**Mechanism:** Benchmark comparison across commits.

After any model, pipeline, or integration change:
1. Re-run accuracy benchmark → compare to last known value
2. Re-run latency benchmark on reference device → compare to last known value
3. Flag if accuracy drops >1% or latency increases >20%

**Enforcement:** Manual for MVP (run before merge). Automated CI is out of scope for a single-developer thesis project.

## 4. Manual Test Protocol (Non-Automatable)

| Test | Protocol | Pass Criteria |
|------|----------|---------------|
| Live signing accuracy | Researcher performs each of 50 signs 3 times | ≥80% correct predictions |
| Feedback usefulness | Researcher intentionally makes errors on 10 signs | Feedback identifies correct dimension |
| Low-light performance | Perform in dim room | FPS ≥20, predictions still work |
| Cluttered background | Perform with complex background | No crash, predictions work |

## Status

**Pending implementation.** No automated test suite exists yet. Test plan documented for Phase 17 implementation.
