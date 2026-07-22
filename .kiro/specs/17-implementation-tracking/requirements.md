# Phase 17 — Implementation & Iterative Validation

## Objective

Build every approved spec in dependency order, validating against targets continuously rather than at the end.

## Requirements

WHEN implementation begins for any sub-step,
the system SHALL confirm that sub-step's spec phase is approved before writing code.

WHEN a sub-step is completed,
the system SHALL validate against that sub-step's acceptance criteria before moving to the next.

WHEN numeric targets are touched,
the system SHALL re-run relevant benchmarks and confirm no regression.

WHEN new code introduces dependencies,
the system SHALL verify no network calls are introduced (offline enforcement).

## Implementation Order

1. Data pipeline (spec 04)
2. Model training (spec 05 + 06)
3. Model evaluation against Phase 7 criteria (spec 07)
4. Quantization/export (spec 08)
5. Mobile app foundation (spec 09)
6. On-device integration (spec 12)
7. Feedback logic (spec 10)
8. UX flow implementation (spec 11)
9. Benchmarking harness wired to repeatable script (spec 13)

## Exit Criteria Per Sub-Step

Each sub-step's own approved spec's acceptance criteria are met before moving to the next.

## Status

Phases 1–7 (old numbering) already implemented. Remaining: formal benchmarking harness, real-device validation, evaluation study tooling, release build.
