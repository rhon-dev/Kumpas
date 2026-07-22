# Phase 16 — Evaluation Study Design

## 1. Study Objective

Measure whether using Kumpas's corrective feedback meaningfully improves learners' FSL sign execution accuracy compared to practicing without feedback.

## 2. Study Design: Pre/Post with Control Group

| Group | N (target) | Intervention | Measurement |
|-------|-----------|-------------|-------------|
| Experimental | 20 | Practice with Kumpas (feedback enabled) | Pre-test and post-test sign accuracy |
| Control | 20 | Practice with video reference only (no feedback) | Pre-test and post-test sign accuracy |

**Total participants:** 40 (per original PRD specification)

### Measurement Instrument
- **Pre-test:** Participant attempts 10 selected signs; scored by human evaluator on 4-dimension rubric (handshape, orientation, motion, timing) per sign
- **Post-test:** Same 10 signs, same rubric, different evaluator (or blinded)
- **Practice period:** 30 minutes with assigned tool (Kumpas or video reference)
- **Score:** Total rubric points across 4 dimensions × 10 signs

## 3. Statistical Test Selection

### Primary: Paired Samples t-test (within-group improvement)
- Compare pre vs post scores within each group
- **Assumption check:** Shapiro-Wilk for normality of difference scores
- **If normality violated:** Wilcoxon signed-rank test (non-parametric alternative)

### Secondary: Independent Samples t-test (between-group comparison)
- Compare improvement magnitude (post - pre) between experimental and control
- **If normality violated:** Mann-Whitney U test

### Effect Size: Cohen's d
- Report alongside p-values (statistical significance alone is insufficient for thesis defense)

### Justification for Test Choice
- Paired design controls for individual baseline ability
- t-test is appropriate for continuous rubric scores with N=20 per group
- Non-parametric fallbacks specified in advance (not chosen post-hoc based on results)

## 4. Sample Size Reasoning

**Practical constraint:** 40 participants available within thesis timeline and institutional access.

**Power consideration:** With N=20 per group, α=0.05, a paired t-test can detect a large effect (d≥0.8) with ~80% power, or a medium effect (d≥0.5) with ~50% power. The study is underpowered for detecting small effects.

**Acknowledged limitation:** If the thesis claims a "significant improvement," the power analysis should be reported. If no significant effect is found, the study cannot distinguish "no effect" from "effect too small for this N to detect."

**⚠️ Statistician consultation flag:** If the author is not confident in the power analysis or test selection, consult a statistician BEFORE running the study. Post-hoc statistical corrections are harder to defend.

## 5. Sign Subset for Study

Select 10 signs from the 50-sign MVP for the study (not all 50 — time constraint):
- Cover all 4 feedback dimensions (signs that test different combinations)
- Include signs the model handles well AND signs it struggles with (NUMBER signs)
- Specific selection: to be determined with FSL Expert

## 6. Rubric Design

| Dimension | Score Range | Criteria |
|-----------|------------|----------|
| Handshape | 0–3 | 0: wrong hand config, 1: partially correct, 2: mostly correct, 3: matches reference |
| Orientation | 0–3 | Same scale — palm direction |
| Motion | 0–3 | Same scale — trajectory and path |
| Timing | 0–3 | Same scale — tempo and pacing |

**Total per sign:** 0–12 points
**Total per participant (10 signs):** 0–120 points

### Inter-Rater Reliability
- Two evaluators score a subset independently
- Report Cohen's kappa or ICC
- If agreement is poor, revise rubric before full study

## 7. Data Handling

| Data Type | Storage | Consent Required | Retention |
|-----------|---------|-----------------|-----------|
| Pre/post scores | Local spreadsheet | Yes | Until thesis publication + 2 years |
| Session logs (experimental group) | Exported from device | Yes | Same |
| Participant demographics (age, FSL experience level) | De-identified | Yes | Same |
| Raw video of signing | NOT COLLECTED | — | — |
| Audio | NOT COLLECTED | — | — |

### Separation from Training Data
Study participant data is NEVER used to retrain or modify the model. This is a measurement study, not a data collection exercise.

## 8. Consent Process

1. Written informed consent before participation
2. Consent covers: purpose, procedure, data collected, storage duration, voluntary participation, right to withdraw, researcher contact
3. IRB/ethics review (if required by institution) before any participant interaction
4. Participants receive no compensation beyond participation certificate (or as approved)

## 9. Study Limitations (Pre-Documented)

- **Underpowered for small effects** (N=20 per group)
- **Short practice period** (30 minutes — may not be enough for meaningful improvement)
- **Rubric subjectivity** (human evaluation introduces variability)
- **No long-term follow-up** (immediate post-test only; retention not measured)
- **Selection bias** (convenience sample from available participants)
- **Hawthorne effect** (participants may perform better simply because they're observed)

These limitations should appear in the thesis results chapter, not be discovered by the panel.

## Status

**Pending.** Study not yet conducted. Protocol ready for ethics review once Phase 10 gate closes (FSL Expert validation).
