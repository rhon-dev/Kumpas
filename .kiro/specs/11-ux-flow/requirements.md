# Phase 11 — UX Flow Spec

## Objective

Specify functional screen states for direct implementation — no external design tool step for future changes.

## Requirements

WHEN the main flow is specified,
the system SHALL document the state machine: capture → recognition → feedback display → retry.

WHEN error states are defined,
the system SHALL cover: no landmarks detected, ambiguous sign (low confidence), model load failure, camera permission denied.

WHEN empty states are defined,
the system SHALL cover: no practice history, first-time user, sign not in vocabulary.

WHEN the session flow is designed,
the system SHALL specify: session start/end conditions, attempt counting, and when feedback is displayed vs. hidden.

WHEN the dictionary/learn flow is designed,
the system SHALL specify: how learners browse available signs, select a sign to practice, and view reference demonstrations.

## Acceptance Criteria

1. State-transition diagram (Mermaid or equivalent) covers the full practice flow.
2. Every error state has a defined user-facing behavior (not a crash or blank screen).
3. Empty states have helpful guidance text.
4. Flow matches the 5-tab shell already delivered (Home / Isalin / Diksyunaryo / Mag-aral / Profile).
5. No screen requires network connectivity.

## Status

Implementation delivered (Phase 7 in old numbering — Figma-based UI rebuilt). Spec formalizes for future changes.
