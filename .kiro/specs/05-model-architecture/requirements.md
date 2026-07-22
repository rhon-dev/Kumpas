# Phase 5 — Model Architecture Design

## Objective

Design and justify the CNN-LSTM architecture against the accuracy/latency/on-device constraints, with quantizability considered at design time.

## Requirements

WHEN the architecture is designed,
the system SHALL specify: input feature shape (from landmarks), CNN layer configuration, LSTM layer configuration, output layer, and total parameter count.

WHEN the architecture is justified,
the system SHALL document why CNN-LSTM was chosen over alternatives (transformer, plain LSTM, GCN, temporal CNN) given the <150ms on-device constraint.

WHEN the architecture is designed,
the system SHALL consider quantization impact at design time — avoiding operations known to degrade under INT8 quantization.

WHEN feature engineering is specified,
the system SHALL document which landmark indices are used, how temporal sequences are windowed, and any derived features (angles, velocities).

## Acceptance Criteria

1. Architecture spec includes a layer-by-layer table with shapes and parameter counts.
2. ADR documents the CNN-LSTM choice with at least one alternative considered.
3. Quantization compatibility is addressed (not deferred to Phase 8 as an afterthought).
4. Feature engineering is reproducible from the spec alone.
5. Total parameter count is within a budget compatible with <150ms TFLite inference.

## Status

Implementation exists (`training/models/`). Best variant: "no_face" with 258 features, 95.07% test accuracy. Spec formalizes.
