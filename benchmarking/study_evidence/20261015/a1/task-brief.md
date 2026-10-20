# A1 requirements

## Authorization and global constraints

The owner replied `continue` after reviewing the written design and approval question. This authorizes the recommended host-only implementation in docs/superpowers/specs/2026-10-15-host-completion-design.md. Actual retraining and unapproved research scoring remain separate gates, exactly as presented.

- Work in the verified existing dirty repository; no worktree/reset/clean/stash/commit/push.
- No emulator, phone, ADB or default participant-store operations.
- Preserve all82 protected original hashes, model/reference assets, historical evidence, feedback mathematics, XP, approved layout and unrelated work.
- Record actual RED/GREEN output incrementally; already-green characterization is not a repair.
- Use session scratch TMPDIR; existing environments only. Serialize Gradle/build and compute-heavy execution.
- Parent owns status/index/final acceptance. Implementers write only their assigned source/tests and evidence folders.
- Every task requires source/test review and parent verification, not worker self-report alone.


### Package A1: export and questionnaire contracts (host tasks3 and11, partial)

Files: app/android/app/src/main/kotlin/com/kumpas/kumpas_app/DataExporter.kt; corresponding src/test/kotlin/.../DataExporterTest.kt; app/lib/ui/assessment_screen.dart; app/test/assessment_save_failure_test.dart. A small adjacent export-publication helper and its tests are allowed if needed for injected faults.

Interfaces remain `DataExporter(context).export(participantId, db): String` and AssessmentScreen(isPost: true). Database helper is borrowed; callers retain ownership. Existing export JSON structure and purge-recognized filename prefix remain compatible.

- [ ] Inspect existing tests, SessionManager managed-export matcher and caller serialization before editing.
- [ ] RED: create two participants with attempts; export one and independently sum its nested attempts. Assert summary total equals that scoped payload, not global DB count.
- [ ] GREEN: derive total_attempts from the exported session arrays. Do not widen data inclusion or change DB schema.
- [ ] RED: partial/close/publication failures cannot corrupt prior completed export; repeated same-time exports cannot overwrite prior data. Verify no success path is returned on failure and borrowed DB remains usable.
- [ ] GREEN: introduce minimal injected publication seam, unique destinations and safe staging/publication/readback with cleanup. Preserve unrelated sentinels and recognize every temporary artifact in owned cleanup. Never claim forensic/power-loss guarantees.
- [ ] RED: post form with required answers but empty optional feedback can submit; missing required response cannot submit. Existing save-failure/retry remains.
- [ ] GREEN: remove only `_openFeedback.isNotEmpty` from completion requirement; keep required response checks and layout.
- [ ] Run focused JVM exporter/SessionManager tests and Flutter assessment tests; append commands/exits/log paths after each slice.
- [ ] Parent independently verifies and reviews A1 before remaining coupled app changes.

Illustrative summary assertion, adapted to existing fixture API rather than inventing one:
```kotlin
val payload = JSONObject(File(exporter.export(participantA, database)).readText())
val sessions = payload.getJSONArray("sessions")
val actualCount = (0 until sessions.length()).sumOf {
    sessions.getJSONObject(it).getJSONArray("attempts").length()
}
assertEquals(actualCount, payload.getJSONObject("summary").getInt("total_attempts"))
```

Target command from app/android under shared lock:
```sh
./gradlew --offline :app:testDebugUnitTest --rerun --tests 'com.kumpas.kumpas_app.DataExporterTest' --tests 'com.kumpas.kumpas_app.SessionManagerTest'
```
From app:
```sh
flutter test --no-pub test/assessment_save_failure_test.dart --reporter expanded
```


## Report contract
Create report.md and append command-ledger.jsonl here before edits. Record each actual RED/GREEN command, exit and log immediately. Report changed paths, fresh tests, protected hash check, concerns and remaining boundaries. Do not commit. Parent accepts only after independent verification/review.
