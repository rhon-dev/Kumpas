# Phase 15 — QA & Test Plan Design

## Objective

Specify the full test strategy before implementation — unit, integration, device-matrix, and regression tests.

## Requirements

WHEN unit tests are designed,
the system SHALL cover: landmark normalization, feature extraction, feedback-logic thresholds per dimension, confidence gating.

WHEN integration tests are designed,
the system SHALL cover: model load + inference on sample landmark sequences, TFLite runtime behavior on target Android API levels.

WHEN device-matrix tests are designed,
the system SHALL name at least 2-3 representative mid-range Android devices and test FPS/latency targets on each.

WHEN regression tests are designed,
the system SHALL verify: accuracy/latency/FPS do not silently regress across commits.

WHEN test coverage is assessed,
the system SHALL identify which critical paths have automated tests vs. which require manual verification.

## Acceptance Criteria

1. Unit test list covers the feedback-logic boundary (the highest-risk component).
2. Integration test covers model load + inference reproducibility.
3. Device matrix names specific devices with expected performance.
4. Regression mechanism exists (benchmark comparison across runs).
5. Manual-test protocol exists for paths that cannot be automated (live camera, real signing).

## Status

Pending — no automated test suite exists yet.
