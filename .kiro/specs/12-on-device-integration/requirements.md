# Phase 12 — On-Device Integration Design

## Objective

Specify how model inference, feedback logic, and the camera pipeline combine at runtime within the latency budget.

## Requirements

WHEN the integration is designed,
the system SHALL specify the exact call sequence: camera frame → landmark extraction → tensor preparation → TFLite inference → confidence check → feedback-logic invocation → UI update.

WHEN the latency budget is allocated,
the system SHALL produce a table showing time allocation per step, totaling ≤150ms, with measured baselines where available.

WHEN confidence thresholds are defined,
the system SHALL specify: minimum confidence for displaying a classification, minimum confidence for triggering feedback, and behavior at ambiguous confidence levels.

WHEN frame dropping is addressed,
the system SHALL document how inference keeps up with the camera pipeline (skip frames, queue, or synchronous gate).

## Acceptance Criteria

1. Call sequence diagram exists with clear data flow between components.
2. Latency budget table sums to ≤150ms with per-step allocations.
3. Confidence thresholds are defined with rationale.
4. Frame-management strategy ensures 24–30 FPS is sustained even if inference occasionally exceeds budget.
5. Integration design is testable end-to-end.

## Status

Implementation exists (end-to-end pipeline running). Spec formalizes latency budget and confidence logic.
