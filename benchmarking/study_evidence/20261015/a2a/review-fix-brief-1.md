# A2a review fix — R1 screen-instance handoff

## Required reading

Read controller/a2a-review-1.md in full (including exact independent probe and B1 boundary), original a2a/task-brief.md and current production/tests. Review returned specification REQUEST CHANGES and quality REQUEST CHANGES. No A2a acceptance. Parent verified64 targeted JVM/67Flutter/clean analysis and82 protected hashes before review; this is prior evidence, not evidence for new changes.

## Scope and acceptance

Fix the one blocking reachable race R1: old screen dispatches end, only its reply is delayed; replacement observer becomes practice-active/resumed, adopts the old ending cached session; old reply completes and replacement remains sessionless. Both native effects occur in normal issuance order; all replies eventually arrive. Preserve current signatures, clear epoch/reply ordering protections, identity-safe cleanup, duplicate start suppression, original native60-second timeout and safe error/retry behavior. Do not resolve by unscoped extra end that can terminate a replacement. Shared repository/observer state must distinguish ending/not-adoptable state or otherwise reconcile replacement foreground intent after old operation settles. Select minimal mechanism consistent with actual callers.

Write deterministic two-observer regression matching PracticeScreen construct/dispose, native effects-at-dispatch and withheld replies BEFORE production change; execute actual behavioral RED. Include finite delayed success, end failure with retry/new observer usability, replacement departure/reentry while prior end pending, and clear during handoff where relevant. The regression must not deadlock by awaiting an intentionally blocked observer future before releasing its prerequisite; document any synchronization change versus reviewer's exact probe while preserving event order. Preserve the reviewer's original report unchanged. Cover B1 boundary honestly without expanding arbitrary external-caller contracts or asserting cache equality provides native atomicity.

Ownership limited to app/lib/session/session_repository.dart, session_lifecycle.dart and their existing session_clear/session_lifecycle_race/session_repository_race tests. Native files and exporter are frozen for this fix. If broader change is truly required, report need instead of touching it.

## Evidence and constraints

Sole source implementer, no emulator/phone/ADB/default participant stores/install/download/commit/reset/clean/stash/worktree/model/math/XP/layout changes. Existing approved host-only design controls. Load kumpas-study-readiness and test-driven-development skills. Create review-fix-1-report.md before edits under a2a; append actual RED/GREEN commands/exits/logs after each slice; use unique new logs, preserve old failures. Existing a2a/run-host-tests.py provides appropriate scratch/env/shared lock and refuses overwrite. Run focused session tests, Flutter analyze --no-pub and full Flutter test --no-pub --reporter expanded. No new JVM source edits expected; report if no JVM rerun rather than implying full native verification. Compare all82 protected hashes and git diff --check. Return exact changed files, actual tests, concerns and status. Parent will independently verify/review again; do not claim acceptance or completion of broader host tasks.
