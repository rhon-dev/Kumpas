# Phase 8 — Quantization & Export Design

## Objective

Plan how the selected model becomes a deployable TFLite artifact with documented accuracy/latency tradeoffs.

## Requirements

WHEN quantization strategy is chosen,
the system SHALL document: post-training quantization vs. quantization-aware training, with rationale for the choice.

WHEN the export pipeline runs,
the system SHALL produce a .tflite file and log: source checkpoint, quantization method, output file size, and any operator compatibility warnings.

WHEN accuracy/latency tradeoff is measured,
the system SHALL compare float32 vs. quantized accuracy on the same test set and report the delta.

WHEN the target device is specified,
the system SHALL name actual candidate device(s) by model number, not just "mid-range Android."

## Acceptance Criteria

1. Quantization strategy documented with rationale.
2. Export pipeline produces .tflite with logged provenance.
3. Accuracy delta between float32 and quantized is measured and documented.
4. Target device(s) named specifically.
5. Latency measured on target device (or documented emulator fallback with caveats).

## Status

Implementation exists (`training/tflite_export/`). Emulator benchmark delivered. Real-device validation pending.
