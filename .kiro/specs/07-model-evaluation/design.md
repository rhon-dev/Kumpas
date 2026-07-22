# Phase 7 — Model Evaluation & Selection Criteria: Design

## 1. Evaluation Methodology

### Primary Metric: Test Accuracy (Aggregate)
- Measured on the held-out test split (203 samples, 50 classes)
- Threshold: ≥90%
- **Result: 95.07% — PASS**

### Secondary Metrics
- Macro precision: 0.958
- Macro recall: 0.950
- Macro F1: 0.948
- Per-class accuracy (full classification report)
- Confusion matrix (visual + CSV)

### Measurement Point
- Evaluated on the saved checkpoint restored by EarlyStopping (best val_accuracy weights)
- Test set never seen during training or validation
- Post-quantization accuracy verified separately (Phase 8/18)

---

## 2. Model Selection Criteria (Defined Before Training)

| Criterion | Threshold | Priority |
|-----------|-----------|----------|
| Test accuracy | ≥90% | Primary (pass/fail gate) |
| Per-class F1 balance | No class below 0.30 F1 | Secondary (flags problem signs) |
| Parameter count | <1M (quantization-friendly) | Constraint |
| Inference latency (TFLite) | <150ms on target device | Constraint (Phase 8/18) |

### Selection Decision
The `no_face` variant (95.07%) was selected because:
1. Highest test accuracy across all 4 experiments
2. Smallest parameter count (270K) — best quantization candidate
3. Fastest training (166s) — simplest model that works best

---

## 3. Leakage Verification

| Check | Method | Result |
|-------|--------|--------|
| Train/test overlap | Split preserved from FSL-105 CSVs; never reshuffled | ✅ No overlap possible |
| Augmentation applied to test | Code review confirms augmentation is train-only | ✅ Clean |
| Validation leak into model selection | Val split is from training data; test is separate | ✅ Test never influences training |

**Acknowledged limitation:** Signer-independence cannot be verified (no signer IDs in metadata). If same signers appear in both splits, accuracy may be inflated.

---

## 4. Per-Class Analysis

### Problem Signs (F1 < 0.90)

| Sign | F1 | Confusion Pattern | Implication for Feedback Engine |
|------|-----|-------------------|--------------------------------|
| FIVE | 0.333 | Confused with FOUR (3/4 errors) | Handshape distinction (5 fingers vs 4) is critical |
| FOUR | 0.600 | Confused with FIVE | Same pair — finger extension ambiguity |
| THREE | 0.667 | Confused with TWO | Adjacent number signs share similar base handshape |
| TWO | 0.800 | Gets THREE's errors | Less severe — high recall (1.0) |

### Strong Categories (F1 = 1.0 for all members)
- FAMILY (all 6 signs)
- RELATIONSHIPS (all 6 signs)
- COLOR (all 4 signs)
- FOOD (all 4 signs)
- DRINK (both signs)

### Pattern
Number signs (especially FOUR/FIVE, TWO/THREE) are the weakest — they differ only in finger count, which is the hardest landmark feature to distinguish from 258-dimensional sequences. This is expected and consistent with literature (adjacent numbers confuse landmark-based models).

**Implication for feedback engine:** The feedback logic must be especially rigorous on handshape thresholds for number signs. If the classifier is uncertain between FOUR and FIVE, the feedback should guide the learner specifically on finger extension.

---

## 5. Confusion Matrix Review Process

1. Generate confusion matrix for every model run (saved as PNG + raw predictions)
2. Identify most-confused pairs (>1 error between two specific classes)
3. Check if confused pairs share linguistic features (handshape, motion) — confirms the model is making "reasonable" errors, not random ones
4. Flag any confusion that suggests data quality issues (e.g., mislabeled clips)
5. Use confusion patterns to inform feedback-engine threshold sensitivity

---

## Status

**Complete.** Model accepted at 95.07% test accuracy on 2026-07-06. Confusion analysis documented. Per-class weaknesses (number signs) acknowledged with mitigation plan for feedback engine.
