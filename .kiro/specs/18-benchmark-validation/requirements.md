# Phase 18 — Benchmark Validation Against Targets

## Objective

Formally confirm the three numeric targets are met on real hardware, not simulated.

## Requirements

WHEN accuracy is validated,
the system SHALL confirm ≥90% test accuracy holds post-quantization (not just pre-quantization) on the actual deployed .tflite model.

WHEN latency is validated,
the system SHALL confirm <150ms end-to-end inference on the defined device matrix (not just emulator).

WHEN FPS is validated,
the system SHALL confirm 24–30 FPS sustained camera pipeline on the defined device matrix.

WHEN a target is missed,
the system SHALL document: which target, by how much, root cause analysis, and remediation plan or explicit tradeoff decision.

WHEN tradeoffs are accepted,
the system SHALL record the rationale — never silently relax a target.

## Acceptance Criteria

1. All three targets validated on at least one named real device.
2. Post-quantization accuracy confirmed (not assumed from float32 results).
3. Benchmark report is reproducible and names exact conditions.
4. Any target miss has a documented, approved tradeoff decision.
5. Results are suitable for inclusion in the thesis technical validation chapter.

## Status

Emulator validation complete. Real-device validation pending.
