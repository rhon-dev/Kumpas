# Phase 7 — Model Evaluation & Selection Criteria

## Objective

Define objectively, in advance, what "the model is done" means — preventing post-hoc rationalization.

## Requirements

WHEN model evaluation is performed,
the system SHALL report: per-class accuracy, aggregate accuracy, precision, recall, F1, and a confusion matrix.

WHEN the ≥90% accuracy target is assessed,
the system SHALL measure on the held-out test set using the quantized model (not just float32).

WHEN model selection criteria are applied,
the system SHALL document: which metric is primary (test accuracy), what secondary metrics inform selection (per-class balance, latency), and what constitutes a "pass."

WHEN leakage is checked,
the system SHALL verify no training samples appear in the test set and document the verification method.

## Acceptance Criteria

1. Evaluation report template exists with all required metrics.
2. ≥90% threshold is measured post-quantization specifically.
3. Model-selection criteria are defined before training results exist.
4. Leakage check is documented and passed.
5. Per-class accuracy identifies problem signs for the feedback engine.

## Status

Complete — 95.07% test accuracy achieved (pre-quantization; post-quantization on emulator showed no degradation). Evaluation report exists at `training/models/reports/`.
