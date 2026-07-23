# Design — Phase 8: Session Logging & Local Persistence

## Overview

Replace the append-only JSONL attempt log with a structured SQLite database that groups attempts into sessions, captures pre/post assessments, and supports export + deletion. All data stays local (no network). The native Kotlin layer owns the database; Flutter accesses it via the existing `kumpas/control` MethodChannel.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Flutter UI Layer                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ PracticeScreen│  │ ProfileScreen│  │ AssessmentScreen  │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                  │                    │            │
│  ┌──────▼──────────────────▼────────────────────▼────────┐  │
│  │  SessionRepository (Dart)                             │  │
│  │  - startSession() / endSession()                      │  │
│  │  - recordAttempt() (delegated to native)              │  │
│  │  - saveAssessment() / exportAll() / clearAll()        │  │
│  └──────────────────────────┬────────────────────────────┘  │
│                             │ MethodChannel: kumpas/control  │
└─────────────────────────────┼───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│  Android Native Layer (Kotlin)                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  SessionManager                                      │   │
│  │  - Owns session lifecycle (start/end/auto-timeout)   │   │
│  │  - Links attempts from VisionEngine to active session│   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  SessionDatabase (android.database.sqlite)           │   │
│  │  Tables: participants, sessions, attempts, assessments│  │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  DataExporter                                        │   │
│  │  - Queries all tables → single JSON export file      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Key decision:** SQLite on native side using Android's built-in `android.database.sqlite` — no Flutter plugin needed, data co-located with VisionEngine.

## Components and Interfaces

### New Kotlin Components

| Component | File | Responsibility |
|-----------|------|----------------|
| `SessionDatabase` | `SessionDatabase.kt` | SQLiteOpenHelper — schema, upgrades, raw queries |
| `SessionManager` | `SessionManager.kt` | Session lifecycle (start/end/timeout), participant ID management |
| `DataExporter` | `DataExporter.kt` | Full JSON export, writes to external app storage |

### New Flutter Components

| Component | File | Responsibility |
|-----------|------|----------------|
| `SessionRepository` | `lib/session/session_repository.dart` | Dart-side API wrapping platform channel |
| `SessionLifecycle` | `lib/session/session_lifecycle.dart` | WidgetsBindingObserver — auto start/end on navigation |
| `AssessmentScreen` | `lib/ui/assessment_screen.dart` | Pre/post questionnaire form |
| `ExportDialog` | `lib/ui/export_dialog.dart` | Confirm export, show file path |

### Modified Components

| Component | Change |
|-----------|--------|
| `MainActivity.kt` | Register SessionManager, add new method handlers |
| `SessionLog.kt` | Deprecated (kept only for migration reads) |
| `kumpas_channel.dart` | Add session/assessment/export method calls |
| `profile_screen.dart` | Add Export + Clear buttons in Settings tab |
| `practice_screen.dart` | Hook startSession on enter, endSession on leave |
| `main.dart` | Add WidgetsBindingObserver for app lifecycle |

### Platform Channel API (additions to `kumpas/control`)

| Method | Args | Returns | Notes |
|--------|------|---------|-------|
| `startSession` | — | `String` session UUID | Creates new session |
| `endSession` | — | `null` | Closes active session, computes summaries |
| `getActiveSession` | — | `String?` | Active session ID or null |
| `saveAssessment` | `{type: "pre"\|"post", responses: {...}}` | `null` | Stores assessment |
| `getAssessments` | — | `String` JSON array | All assessments |
| `exportData` | — | `String` file path | Full export |
| `clearAllData` | — | `null` | Wipes DB + resets |
| `getParticipantId` | — | `String` UUID | Device participant ID |

Existing methods (`getHistory`, `startAttempt`, `cancelAttempt`) remain unchanged.

## Data Models

### SQLite Schema

```sql
CREATE TABLE participants (
    id TEXT PRIMARY KEY,          -- UUID v4, generated on first launch
    created_at INTEGER NOT NULL,  -- epoch ms
    device_model TEXT,
    app_version TEXT
);

CREATE TABLE sessions (
    id TEXT PRIMARY KEY,          -- UUID v4
    participant_id TEXT NOT NULL REFERENCES participants(id),
    started_at INTEGER NOT NULL,  -- epoch ms
    ended_at INTEGER,             -- NULL = active
    attempt_count INTEGER DEFAULT 0,
    signs_attempted INTEGER DEFAULT 0,
    avg_match REAL DEFAULT 0,
    duration_s REAL DEFAULT 0,
    source TEXT DEFAULT 'app'     -- 'app' | 'legacy_migration'
);

CREATE TABLE attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id),
    timestamp INTEGER NOT NULL,
    target_class INTEGER NOT NULL,
    target_label TEXT NOT NULL,
    predicted_label TEXT NOT NULL,
    predicted_confidence REAL NOT NULL,
    recognized_as_target INTEGER NOT NULL,  -- 0/1
    overall_match REAL NOT NULL,
    feedback_items TEXT NOT NULL            -- JSON array
);

CREATE TABLE assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    participant_id TEXT NOT NULL REFERENCES participants(id),
    type TEXT NOT NULL,           -- 'pre' | 'post'
    timestamp INTEGER NOT NULL,
    responses TEXT NOT NULL       -- JSON object
);

CREATE INDEX idx_attempts_session ON attempts(session_id);
CREATE INDEX idx_attempts_timestamp ON attempts(timestamp);
CREATE INDEX idx_sessions_participant ON sessions(participant_id);
```

### Assessment Response Schemas

**Pre-assessment:**
```json
{
  "fsl_confidence": 3,
  "fsl_signs_known": 1,
  "age_range": "18-24",
  "gender": "prefer_not_to_say",
  "hearing_status": "hearing"
}
```

**Post-assessment (includes SUS):**
```json
{
  "fsl_confidence": 4,
  "fsl_signs_known": 3,
  "sus_responses": [3, 2, 4, 1, 5, 2, 4, 1, 5, 3],
  "sus_score": 72.5,
  "open_feedback": "..."
}
```

### Export Format

```json
{
  "metadata": {
    "export_timestamp": "2026-08-01T14:30:00",
    "app_version": "1.0.0",
    "device_model": "Samsung Galaxy A14",
    "participant_id": "uuid..."
  },
  "assessments": [...],
  "sessions": [
    {
      "id": "...", "started_at": ..., "ended_at": ...,
      "attempt_count": 15, "avg_match": 0.73,
      "attempts": [...]
    }
  ]
}
```

Export path: `/sdcard/Android/data/com.kumpas.kumpas_app/files/kumpas_export_<id>.json`

### Session Lifecycle State Machine

```
[No Session] --navigate to practice--> [Session Active (new UUID)]
[Session Active] --attempt recorded--> [Session Active (N attempts)]
[Session Active] --leave / bg >60s / explicit end--> [Session Closed]
[Session Closed] --navigate to practice--> [New Session Active]
```

Auto-close: `onPause` starts 60s timer. `onResume` before timeout cancels it. Timeout fires → session closed with `ended_at = last_attempt + 60000`.

### Migration (JSONL → SQLite)

1. Check if `attempt_history.jsonl` exists
2. Create participant + one legacy session (`source = "legacy_migration"`)
3. Parse each line → insert `attempts` row
4. Compute session summaries
5. Rename file to `.jsonl.migrated` (backup)

## Correctness Properties

### Property 1: Session Uniqueness
Each session has a unique UUID; no two sessions can be active simultaneously.
**Validates: Requirements 1, 2**

### Property 2: Attempt Linkage
Every attempt belongs to exactly one session (foreign key enforced).
**Validates: Requirements 3**

### Property 3: No Data Loss on Migration
Line count of JSONL = row count in attempts after migration.
**Validates: Requirements 10**

### Property 4: Export Completeness
Export contains ALL sessions, attempts, and assessments for the participant.
**Validates: Requirements 7, 8**

### Property 5: Clear is Total
After `clearAllData`, all tables are empty and participant ID is regenerated.
**Validates: Requirements 9**

### Property 6: No Network
Zero network permissions requested; airplane-mode test passes.
**Validates: Requirements 11**

### Property 7: Timestamp Monotonicity
Attempts within a session have non-decreasing timestamps.
**Validates: Requirements 1, 3**

## Error Handling

| Scenario | Handling |
|----------|----------|
| DB creation fails | App falls back to in-memory logging; surfaces error in Settings |
| Migration parse error on a line | Skip line, log error, continue; report skipped count |
| Export write fails (no storage space) | Return error string via channel; UI shows toast |
| Session end called with no active session | No-op, return null |
| Assessment saved with incomplete fields | Return validation error; UI highlights missing fields |
| App killed mid-session | On next launch, detect unclosed session (ended_at = NULL), close it with `started_at + duration estimate` |

## Testing Strategy

| Layer | Approach |
|-------|----------|
| SessionDatabase | Android unit tests (Robolectric): schema creation, CRUD, migration |
| SessionManager | Unit tests: lifecycle state transitions, timeout logic |
| DataExporter | Unit test: mock DB data → verify JSON output matches schema |
| Migration | Unit test: sample JSONL → verify correct row count + data integrity |
| Platform channel | Flutter integration test: call methods, verify responses |
| UI forms | Widget tests: assessment form validation, button states |
| End-to-end | Emulator: practice flow → check DB state → export → verify JSON |

## Retention Policy (In-App Copy)

Settings → "Tungkol sa Data":

> **Ano ang naka-imbak:** Mga resulta ng pagsasanay (score, feedback, timestamp), pre/post na assessment.
> **Saan:** Lokal lamang sa device — walang data na naipapadala online.
> **Gaano katagal:** Hanggang i-delete mo o i-uninstall ang app.
> **Paano mag-delete:** Settings → "I-clear ang lahat ng data."
> **Para sa pananaliksik:** Maaaring i-export gamit ang USB (may pahintulot lamang).

## Performance Notes

- SQLite writes on background handler thread — no UI/pipeline blocking
- `recordAttempt()` is fire-and-forget from VisionEngine callback
- Index on `attempts.timestamp` for fast ordered queries
- `getHistory(limit=200)` uses SQL LIMIT — same perf as current JSONL tail
- Storage estimate: 1000 attempts × ~500 bytes ≈ 500KB (well under 10MB)
