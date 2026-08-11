# Phase 19 — Release Readiness & Thesis Defense Preparation

## Objective

Confirm the system is genuinely ready for real-device distribution and defense demonstration.

## Requirements

WHEN a release build is produced,
the system SHALL be a signed APK/AAB installable on a clean device without developer tools.

WHEN release artifacts are verified,
the system SHALL confirm: debug logging removed, dev-only bypass flags removed, no test data in assets.

WHEN crash handling is verified,
the system SHALL handle gracefully: no camera permission, no landmarks detected, model load failure, unexpected input.

WHEN offline enforcement is re-verified,
the system SHALL run the airplane-mode test on the release build specifically (not just dev build).

WHEN a demo script is prepared,
the system SHALL document: what to show a thesis panel, in what order, with fallback if live camera demo has issues.

WHEN known limitations are documented,
the system SHALL list honestly: isolated-sign only, FSL-105 vocabulary only (50-sign subset), single reference device family tested, any accuracy gaps on specific signs.

## Acceptance Criteria

1. Signed release build installs on a clean device.
2. No debug artifacts in release.
3. Crash-free on common failure modes.
4. Offline enforcement confirmed on release build.
5. Demo script exists with fallback plan.
6. Known-limitations document is honest and complete.
7. docs/PRD.md and docs/phase-gates.md updated to reflect final state.

## Status

Pending — not yet begun.
