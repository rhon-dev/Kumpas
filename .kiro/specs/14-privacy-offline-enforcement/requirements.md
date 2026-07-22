# Phase 14 — Privacy & Offline Enforcement Design

## Objective

Formalize "fully offline at inference" as an enforced, testable property — not just an assertion.

## Requirements

WHEN offline enforcement is verified,
the system SHALL enumerate every dependency/library and confirm none perform network calls during normal app operation.

WHEN camera permission is handled,
the system SHALL request permission with a clear purpose explanation and handle denial gracefully (informative message, no crash).

WHEN evaluation-study sessions are recorded (if applicable),
the system SHALL require explicit, separate consent before any session data is stored locally.

WHEN locally-stored session data exists,
the system SHALL document: what is stored, where, for how long, and when it is deleted.

WHEN data separation is enforced,
the system SHALL ensure evaluation-study participant data NEVER merges into the FSL-105 training corpus.

WHEN RA 10173 (Data Privacy Act) applies,
the system SHALL document which data processing activities are covered and what consent is required.

## Acceptance Criteria

1. Dependency audit table lists every library with "makes network calls: yes/no."
2. Offline enforcement is testable: airplane-mode test passes with full functionality.
3. Camera permission flow handles grant/deny/revoke without crash.
4. Consent language exists for evaluation-study participants (if study involves recording).
5. Data-separation rule is enforced at the code/architecture level, not just documented.
6. RA 10173 applicability analysis exists.

## Status

Partially addressed in existing architecture (offline by design). Formal verification pending.
