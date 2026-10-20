# A3a — executed native host study/benchmark artifact producer

## Authority and dependencies

Owner approved host-only completion design/plan. A1 export/questionnaire, A2a lifecycle/cache and A2b initialization/resource scopes accepted with documented limits. Read controller/a2b-acceptance-20261016.json and discovery/app-host-audit.md sections1/5. No emulator/phone/ADB/default participant stores/install/download/commit/reset/clean/worktree/model/training/math/XP/layout changes. This is host contracts, NOT installed E2E.

## Goal

Produce a reproducible fresh host artifact set using real production MainActivity event AND control dispatch plus isolated real SessionManager/SQLite/DataExporter/purge/reopen. A later A3b task will consume exact artifacts in Dart/Python. Do not hand-author a fake persistence model or duplicate native business logic in tests. Separate constructed synthetic terminal input from actual recognition; no camera or inference result claim.

## Owned files

- MainActivity.kt: minimal extract internal callable control dispatcher used by real MethodChannel registration and tests; preserve synchronization/error/permission/ownership contracts.
- ActivityResourceFactory.kt or adjacent narrow factory only for explicitly isolated export SessionDatabase acquisition. Never let injected manager/exporter silently fall back to applicationContext/default stores. Production path still uses applicationContext and closes owned temporary export helper on success/failure.
- New src/test/kotlin/com/kumpas/kumpas_app/HostStudyFixture.kt and HostStudyFlowTest.kt; optional narrow test fixture producer helper.
- Existing MainActivityBoundaryTest.kt/ActivityInitializationTest.kt only to adapt or cover extraction; keep accepted resource/subscriber guarantees.
- app/android/app/build.gradle.kts minimal fixture-path forwarding if necessary (discover actual file before editing).
- Evidence under benchmarking/study_evidence/20261015/a3a/.
No Dart/collector/training implementation in this slice. Final package must include any accepted factory interface/test adaptations.

## Study scenario acceptance

1. Fresh fixture root, distinct internal/external exports/database/preferences, canonical containment assertions. Unique prefs namespace and both openDatabase overloads correctly isolated; applicationContext returns fixture where needed. No default-store fallback. Track/close every helper, preserve unrelated sentinels.
2. Initialize actual Activity collaborators through A2b production-used seam with real isolated SessionManager/DataExporter/BenchmarkMode and a safe synthetic resource-engine seam; real control dispatcher callable is SAME function registered by MethodChannel. Fake transport explicitly labelled. Never call full configureFlutterEngine/default Android factory.
3. Use actual controls to start session, get participant, save synthetic pre/post assessments/history/export/clear. Start attempt via safe permission seam if feasible; otherwise explicitly label direct AttemptBoundary setup and retain actual terminal event handler. Deliver one synthetic terminal result with valid timing, drain actual Handler/EventSink, query real DB independently. Exactly one row/result; duplicate/stale invalidated terminal must not add rows or deliver.
4. Capture exact delivered event JSON; feedback payload/timing and control IDs/state must derive from production outputs. Attempt UUID is not in existing history schema: correlate via declared unique synthetic field combinations/counts, do not invent a durable attempt UUID column or migrate DB for tests.
5. Actual external+fallback internal exports must agree with independent row counts and participant scoping; capture summaries and selected synthetic rows in envelope. Include failed attempt/assessment save or failed export/clear where reproducibly available with fixed error codes; no success on failed operation. Keep original exceptions/ownership behavior.
6. Clear actual managed SQLite/preferences/files, assert both export roots and legacy residue gone, sentinels survive, exactly one new participant. Close/reopen helpers; reopened participant ID stable, history/assessments empty, new export empty. Account for files already removed on partial purge failure; no fictional filesystem transaction.
7. Preserve committed persistence independently of stale UI suppression when clear/replacement occurs before Handler drain. One narrow scenario is enough if coverage elsewhere is linked explicitly.

## Benchmark fixture producer

Use executed existing BenchmarkModeTest NATIVE_RECEIPT_FIXTURE outputs or extract production-used helper into new producer test. Emit actual native confirmed/unconfirmed/publication-fault report and control companion bytes without reconstructing payloads. Preserve mode/run identity and exact hashes. Existing historical replay script under20261007 must NOT write old campaign. Later A3b reads these exact bytes through mocked transport.

## Versioned handoff interface

Choose and document a versioned TEST schema (not production benchmark schema). Envelope fields must include synthetic_origin, scenario/run UUID, exact event strings, control call responses/error codes, independent row/history/assessment/export/delete/reopen observations and stage boundaries. No manufactured execution logs or placeholder metrics. Explicitly distinguish actual native control/event execution from later mock delivery.

Emit a manifest with exact schema integer, fresh run UUID, source hashes for relevant production/test inputs, artifact relative paths+SHA256, scenario/mode identities and actual producer outcome. Design path/identity/type validation before output; refuse pre-existing destination, escaping/symlink paths and duplicate artifacts. Never reuse an old run implicitly. Source hashes must match actual files used; document whether calculated before test compile and verify afterward. Test missing/stale/duplicate/tampered output behavior in producer helper as applicable; consumer exhaustive negative matrix belongs A3b.

Input path proposal: Gradle -Pkumpas.hostFixtureDir=<new explicit directory> forwarded to test system property of same name; tests create fresh run subdirectory with exclusive writes. Ordinary full JVM tests must stay runnable without external preconditions (safe scratch default or test-only temp generation), but explicit handoff command prints exact real output root. Do not mark skipped producers as success; manifest successful flag only after assertions pass. Preserve failure logs even if no success manifest is published. Emit no participant/raw video data; fixture is wholly synthetic.

## Regression workflow and checks

Read current code and existing tests before edits. Create report/command-ledger early and append each actual RED/GREEN command/log/exit immediately. Start with fixture isolation, actual control reuse and native flow vertical slices; extraction itself can be behavior-preserving but behavior changes require real failing regression. Preserve accepted A2b source/ownership behavior; callbacks cannot route to old subscribers.

Existing cached JDK17/SDK/Gradle only; shared fcntl lock ~/.hermes/cache/scratch/kumpas-gradle.lock, TMPDIR session scratch. Run focused new producer/boundary/initialization tests, execute explicit fresh handoff command, inspect generated exact files; then full JVM and instrumentation source compilation with --rerun on EACH task. No device execution. Parse counts, snapshot XML, record output hashes. Compare all82protected and accepted A2a source hashes. A2b MainActivity/factory/test may intentionally change for this authorized extraction; freeze new postimages and map exact delta, do not claim unchanged A2b if changed.

Return DONE/DONE_WITH_CONCERNS/BLOCKED, exact fixture root/manifest path, source changes, actual tests and execution boundaries. Parent independently runs producer/verifies artifacts and reviews spec/quality before consumers proceed. No task01/03/05 whole-completion claim yet.
