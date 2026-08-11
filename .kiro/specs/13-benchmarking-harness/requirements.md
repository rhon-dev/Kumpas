# Phase 13 — Benchmarking Harness Design

## Objective

Specify how benchmarking/ continuously validates accuracy, latency, and FPS against targets across model iterations and device conditions.

## Requirements

WHEN accuracy benchmarks are run,
the system SHALL evaluate on the held-out test set and log: dataset version, model version, quantization state, per-class accuracy, and aggregate accuracy.

WHEN latency benchmarks are run,
the system SHALL measure per-inference timing (mean, p50, p95, max) and distinguish warm vs. cold start, on a named device.

WHEN FPS benchmarks are run,
the system SHALL measure sustained frame rate during live camera pipeline operation over at least 60 seconds.

WHEN environment conditions are tested,
the system SHALL benchmark under: optimal lighting, low lighting, and cluttered background.

WHEN benchmark history is logged,
the system SHALL store results in a comparable, appendable format suitable for plotting progress over iterations in the thesis.

## Acceptance Criteria

1. Accuracy benchmark is reproducible (same inputs → same outputs).
2. Latency benchmark names the exact device and conditions.
3. FPS benchmark runs for sufficient duration to capture sustained (not burst) performance.
4. Environment-condition protocol is documented (what constitutes "low light" and "cluttered background").
5. Historical format allows iteration-over-iteration comparison.

## Status

Partial — emulator benchmarks exist. Real-device and multi-condition benchmarking not yet implemented.
