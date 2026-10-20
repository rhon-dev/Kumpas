# A1 independent QA review

## Verdicts

- **Specification: APPROVE for A1 host scope only.** The scoped-summary, unique/failure-safe export publication, borrowed-helper ownership and optional-feedback requirements are supported by the reviewed implementation and parent execution evidence.
- **Code quality: APPROVE with one non-blocking test-strengthening observation below.** No blocking correctness or scope regression identified in the five reviewed files.
- This is not acceptance of other host packages, installed runtime integration, physical performance, research scoring, training or participant-study readiness.

## Review basis and verification

Read the A1 brief/report, full approved host design, controller/a1-review-package.diff, all five current source/test files and controller/a1-parent-verification.json. Read the relevant unchanged MainActivity pipelineLock/caller ownership and StudyDataFiles purge implementation, plus SessionManager identity/purge wiring. The existing dirty repository and historical test are not attributed wholesale to A1.

Independently recomputed SHA-256 for each of the five reviewed files: all match the frozen parent manifest. Inspected parent-jvm-1.log: the test task actually executed and the build succeeded. Inspected parent-flutter-1.log: both named widget tests passed. Parent manifest records 61 JVM tests (22 exporter, 39 SessionManager), zero failures/errors/skips, two Flutter tests, and 82 protected hashes with no mismatches. These executions and the protected-file verification belong to the parent; this reviewer did not rerun suites or independently recompute the protected map. No build, install, ADB, emulator, training or default-store operation was performed.

## Requirement assessment

| Requirement | Reviewed evidence | Assessment |
| --- | --- | --- |
| Participant-scoped attempts | DataExporter.kt:88–108 retains participant filtering and counts actual nested arrays. DataExporterTest.kt:211–225 includes an attempt belonging to another participant and independently sums exported rows. | Supported; no global count or schema widening. |
| Same-time prior export preservation | DataExporter.kt:45–52,116–122 uses UUID suffixes and exclusive creation. Tests:56,229–237 fix time and verify different paths plus unchanged original bytes. | Supported; a collision fails rather than overwriting an existing destination. |
| Staging, close, publication and exact readback | DataExporter.kt:53–61 closes the stream before verifying staged bytes, publishing and verifying destination bytes and staging disappearance. ExportPublication.kt:7–12 is a small real-I/O seam using same-directory rename. | Supported; no success path is returned on the tested faults. |
| Owned cleanup and retry | DataExporter.kt:62–68 removes only the newly reserved destination and an actually acquired staging file; failed deletion adds a suppressed diagnostic. Tests:241–308,337–367 cover partial write, close, publication, corrupt destination, committed read failure, error after rename and silent short write; check prior bytes, sentinel, exact directory membership and successful retry. | Supported for ordinary handled I/O failures; cleanup refusal and process death are limits, not guaranteed erasure. |
| Borrowed database | No exporter close call; MainActivity.kt:54,99–105 serializes the operation and closes the caller-owned helper in finally. Tests:381–415 retain existing success/failure coverage; test:409–414 checks the original database handle on success. | Supported by source; failure-path ownership assertion could be stronger (Q1). |
| Purge compatibility | StudyDataFiles.kt:9,16–34 accepts alphanumeric/hyphen identity segments. Both generated destination and stage names fit for the production UUID identities. Tests:312–333 exercise actual purge using observed staging/final names in both external and fallback roots, preserving sentinels. | Supported without matcher changes. Purge still deliberately fails when external storage is unavailable. |
| Optional versus required answers | assessment_screen.dart:35–41 removes only the optional-feedback condition. Required confidence/signs and all SUS responses remain checked; payload/layout unchanged. assessment_save_failure_test.dart:10–57 checks incomplete required responses, no save while incomplete, all required responses with blank feedback, exact post payload and navigation. | Supported. The mock proves channel payload, not native persistence. |
| Existing save failure/retry | assessment_save_failure_test.dart:58–90 retains the historical pre-form failure/retry test. | Preserved; not represented as newly authored A1 behavior or post-specific persistence evidence. |

## Findings

### Q1 — Low / non-blocking: failure tests can reopen a closed helper

- **Location:** app/android/app/src/test/kotlin/com/kumpas/kumpas_app/DataExporterTest.kt:363–366 (also existing checks at 390–405).
- `db.readableDatabase.isOpen` after the failed operation obtains a database from the helper again. It therefore verifies continued usability but is weaker than checking that the original borrowed handle was never closed. A future accidental failure-path `db.close()` could escape this assertion if subsequent access reopens it.
- **Suggested follow-up:** capture `val originalDatabase = db.writableDatabase` before the failing export, then assert `originalDatabase.isOpen` before accessing any helper getter. The existing success test at 409–414 already uses this stronger pattern.
- **Disposition:** not a current production defect: reviewed exporter code never closes the borrowed helper. It does not block A1 approval.

## Exact acceptance limits

- Publication relies on the documented caller serialization; the exporter does not independently lock out arbitrary external filesystem writers or unsynchronized database callers.
- A reserved empty destination or staging file may remain after process interruption. Deletion refusal can retain an artifact and surface a failure/suppressed diagnostic; the new names remain managed-purge compatible. Cleanup-refusal, process-death and power-loss behavior were not newly probed here.
- No fsync/power-loss durability, forensic deletion, hostile-filesystem race resistance, arbitrary malformed participant-ID support or unlimited-volume export guarantee is established. Current production identities are generated UUIDs; no new input contract is inferred.
- Robolectric filesystem/database tests and mocked Flutter transport do not establish uninterrupted installed Android/Flutter integration, actual external-storage behavior on every device, or a real questionnaire database write from this widget test.
- Reviewer changes are limited to this report. No source, test, dependency, baseline, protected file, status/index or commit was modified. One read-only search wrapper initially assumed the wrong output key; it was retried successfully and did not affect the verdict.
