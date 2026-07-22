# Phase 10 — Corrective Feedback Logic Design

## Objective

Design the thesis's core contribution — the corrective-feedback algorithm — with real methodological rigor, not placeholder rules.

**This is the highest-scrutiny gate in the entire plan.**

## Requirements

WHEN gold-standard references are defined,
the system SHALL document how a "correct" sign is encoded for comparison (landmark sequence representation, per-dimension features extracted).

WHEN comparison methodology is designed,
the system SHALL specify the diffing algorithm per dimension:
- **Handshape:** how finger joint angles/positions are compared
- **Orientation:** how palm/wrist orientation is measured and compared
- **Motion:** how trajectory is aligned (DTW or similar) and deviation quantified
- **Timing:** how temporal pacing is assessed against the reference

WHEN thresholds are defined,
the system SHALL document "close enough" criteria per dimension with justification (not arbitrary magic numbers).

WHEN feedback messages are generated,
the system SHALL produce actionable, specific guidance (not just "wrong handshape" but what specifically to fix).

WHEN the design is validated,
the system SHALL include worked examples for at least 3 distinct signs showing the full pipeline from raw landmarks to feedback text.

## Acceptance Criteria

1. Gold-standard reference encoding is fully specified and reproducible.
2. Each of the four dimensions has a documented comparison algorithm.
3. Thresholds are justified (empirically derived or literature-based, not arbitrary).
4. Worked examples demonstrate the full pipeline for ≥3 signs.
5. Feedback messages are reviewed by FSL expert for linguistic accuracy.
6. 100% of the 50-sign MVP set has gold-standard coverage (at least one reference per sign).

## Status

Python reference implementation exists (`training/feedback/`). Kotlin port delivered. FSL expert linguistic validation pending. Threshold justification needs formalization.
