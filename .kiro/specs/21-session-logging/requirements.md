# Requirements Document

## Introduction

Upgrade the existing append-only attempt history (`attempt_history.jsonl`) into a structured session-based logging system that supports the evaluation study, provides data export for analysis, and complies with RA 10173 data lifecycle requirements. Cloud sync is explicitly out of scope (offline-first, no PM approval for backend).

### Purpose
Enable research-grade data collection from the Kumpas FSL practice app by structuring practice attempts into sessions, capturing pre/post assessment responses, and providing export + deletion capabilities.

### Scope
Local-only session persistence on Android. No cloud backend, no accounts, no network calls.

## Glossary

| Term | Definition |
|------|-----------|
| Session | A bounded practice period (start → end) grouping one or more attempts |
| Attempt | A single gesture recognition + feedback cycle for one sign |
| Participant ID | Device-generated UUID, not linked to any real identity |
| SUS | System Usability Scale — standardized 10-item post-use questionnaire |
| Pre-assessment | Self-rating of FSL confidence + demographics, administered before study |
| Post-assessment | SUS + FSL confidence re-rating, administered after study |

## Requirements

- [ ] 1. WHEN a learner begins a practice session, the system SHALL create a new session record with a unique session ID (UUID), start timestamp, and participant ID (device-generated, persistent across sessions).
- [ ] 2. WHEN a learner ends a practice session (navigates away, app backgrounded >60s, or explicit "end session"), the system SHALL close the session with an end timestamp and compute session summaries (attempt count, distinct signs, avg match, duration seconds).
- [ ] 3. WHEN attempts are recorded during a session, each attempt SHALL be associated with the active session ID.
- [ ] 4. WHEN a pre-assessment is administered, the system SHALL present a structured questionnaire (FSL confidence self-rating 1-5, optional demographics) and store responses linked to the participant ID with a timestamp.
- [ ] 5. WHEN a post-assessment is administered, the system SHALL present the System Usability Scale (10 items, 5-point Likert) plus FSL confidence re-rating, and store responses linked to the participant ID.
- [ ] 6. WHEN assessment responses are stored, the system SHALL validate completeness (all required fields answered) before persisting.
- [ ] 7. WHEN a researcher triggers data export, the system SHALL produce a single JSON file containing all sessions, attempts, and assessment responses for the current participant.
- [ ] 8. WHEN the export file is generated, it SHALL be written to a location accessible via `adb pull` and include a metadata header (export timestamp, app version, device model, participant ID).
- [ ] 9. WHEN a learner requests data deletion from Settings, the system SHALL permanently erase all local session data (attempts, sessions, assessments) and reset all derived statistics to zero.
- [ ] 10. WHEN the app upgrades from the current JSONL format, the system SHALL migrate existing `attempt_history.jsonl` entries into the new session structure (single "legacy" session) without data loss, preserving original timestamps.
- [ ] 11. The session logging system SHALL NOT make any network calls — no telemetry, sync, or analytics.
- [ ] 12. Session logging operations (append, query) SHALL complete in <50ms to avoid impacting the 24-30 FPS pipeline.
- [ ] 13. No personally identifiable information (name, email, phone) SHALL be stored. Participant IDs are device-generated UUIDs only.
- [ ] 14. The system SHALL document the retention policy in-app (Settings screen) and in thesis materials: what is stored, where, how long, deletion mechanism.

## Out of Scope

- Cloud sync / Firebase backend (no PM approval)
- Multi-device sync or user accounts
- Video/image recording of attempts (only landmark-derived metrics stored)
- Real-time analytics or telemetry

## Dependencies

- Existing `SessionLog.kt` (Kotlin, app-private JSONL)
- Existing `KumpasChannel.getHistory()` platform channel
- Existing `LearnerStats` computation (Flutter)
- Phase 14 spec (Privacy & Offline Enforcement) — data lifecycle alignment
- Phase 16 spec (Evaluation Study Design) — assessment instrument definitions
