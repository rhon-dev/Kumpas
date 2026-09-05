# Implementation Plan

## Overview
Replace the append-only JSONL attempt log with a structured SQLite database that groups attempts into sessions, captures pre/post assessments for the evaluation study, and provides export + deletion capabilities. All local-only, no network calls.

## Tasks

- [x] 1. Create `SessionDatabase.kt` — SQLiteOpenHelper with schema creation (participants, sessions, attempts, assessments tables + indexes). Include DB version 1 creation and helper methods for raw insert/query/delete.
- [x] 2. Create `SessionManager.kt` — manages session lifecycle (start/end/auto-timeout). Generates participant UUID on first launch (persisted in SharedPreferences). Exposes `startSession()`, `endSession()`, `getActiveSessionId()`, `recordAttempt(json)`. Implements 60s auto-close via Handler timer on `onPause`/`onResume`.
- [x] 3. Create `DataExporter.kt` — queries all tables, builds the export JSON structure (metadata + assessments + sessions with nested attempts), writes to app-specific external files directory. Returns the file path string.
- [x] 4. Wire `SessionManager` and `SessionDatabase` into `MainActivity.kt` — initialize on `configureFlutterEngine`, register new MethodChannel handlers: `startSession`, `endSession`, `getActiveSession`, `saveAssessment`, `getAssessments`, `exportData`, `clearAllData`, `getParticipantId`.
- [x] 5. Modify `VisionEngine` callback in `MainActivity.kt` to route attempt results through `SessionManager.recordAttempt()` instead of (or in addition to) the old `SessionLog.append()`.
- [x] 6. Implement JSONL migration logic in `SessionManager` — on first init, check if `attempt_history.jsonl` exists, parse all lines into a legacy session in the new DB, rename file to `.jsonl.migrated`.
- [x] 7. Update `KumpasChannel.dart` — add Dart methods: `startSession()`, `endSession()`, `getActiveSession()`, `saveAssessment(type, responses)`, `getAssessments()`, `exportData()`, `clearAllData()`, `getParticipantId()`.
- [x] 8. Create `lib/session/session_repository.dart` — Dart-side wrapper that coordinates session channel calls and caches active session state.
- [x] 9. Create `lib/session/session_lifecycle.dart` — `WidgetsBindingObserver` that calls `startSession` when app enters practice screen and `endSession` when backgrounded or navigating away.
- [x] 10. Hook session lifecycle into `practice_screen.dart` — call `SessionRepository.startSession()` on screen init, `endSession()` on dispose/navigation away.
- [x] 11. Create `lib/ui/assessment_screen.dart` — pre-assessment form (FSL confidence 1-5, signs known 1-5, optional demographics) and post-assessment form (same + SUS 10-item Likert + optional open feedback). Validates completeness before save.
- [x] 12. Add "Export Data" and "Clear All Data" buttons to the Settings tab in `profile_screen.dart`. Export shows a confirmation dialog with the resulting file path. Clear shows a destructive-action confirmation, then calls `clearAllData` and refreshes stats.
- [x] 13. Add "Tungkol sa Data" (retention policy) card to Settings tab in `profile_screen.dart` with the Filipino privacy copy from the design doc.
- [x] 14. Write Android unit tests for `SessionDatabase` — verify schema creation, CRUD operations, and migration from JSONL.
- [x] 15. Write Android unit tests for `SessionManager` — verify session start/end state machine, auto-timeout, attempt linkage.
- [ ] 16. Verify on emulator: full practice flow creates session + attempts in DB, export produces valid JSON, clear wipes everything, migration handles existing JSONL.

## Task Dependency Graph
```json
{
  "waves": [
    [1],
    [2, 3],
    [4, 6],
    [5, 7],
    [8],
    [9, 10, 11],
    [12, 13],
    [14, 15],
    [16]
  ]
}
```

## Notes
- Task 1 is the foundation — all other native tasks depend on the DB being defined.
- Tasks 2 and 3 can be built in parallel once the DB exists.
- Task 6 (migration) depends on SessionManager being wired up.
- Tasks 14-15 (unit tests) use Robolectric or Android JUnit — no device needed.
- Task 16 (emulator verification) is the integration gate — validates the full flow.
- The existing `getHistory` method channel call should continue working (backed by SQLite query instead of JSONL reads) — ensure backward compatibility in Task 5.
