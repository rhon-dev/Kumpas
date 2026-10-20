# Host tooling discovery — tasks 7 and 11–16

Date: 2026-10-15. Scope: Research/Evaluation, Documentation, QA planning only. Repository: `/Users/ahronjanl.rafaelahron.0804icloudcom/Documents/Thesis/kumpas`. All paths below are repository-relative unless absolute. This report is the sole authorized write. No source changes, commits, installations, builds, suites, emulator/phone/ADB operations, participant records or default-store operations were performed. Task numbers refer to the owner's host task list, not PRD phase numbers.

## Outcome and evidence boundary

Existing assessment capture, SQLite persistence/export, blank handoff generation and software regression coverage must be reused, not described as absent. Research scoring/analysis is genuinely absent from `evaluation/` (only `.gitkeep`). A study design contains a concrete **proposed** rubric and named statistical tests, but it is pending, not an approved instrument. The current app does not capture its human-rated per-sign dimensions. Do not derive that rubric from classifier confidence, geometric match, mastery or XP.

Read `AGENTS.md`, all of `docs/PRD.md`, current `docs/phase-gates.md`, the final controller acceptance and schema follow-up, implementation/test paths cited below, and the `kumpas-study-readiness` and `research-project-audit` skills. Git status confirms extensive pre-existing authorized tracked/untracked work; none was reverted or edited.

**Actually executed read-only verification:** a Python stdlib JSON/SHA-256/ZIP probe of `benchmarking/study_evidence/20261007/controller/owner-parent-verification-1.json` and its named targets exited 0. Its protected map contains 82 entries; all 82 current hashes matched. All three existing APK hashes and sizes match that manifest. ZIP inspection found:

| Existing artifact | Bytes | SHA-256 | Flutter ABIs |
|---|---:|---|---|
| `app/build/app/outputs/apk/debug/app-debug.apk` | 212207146 | `0707d2f153c713055edaf50171b4c053393480f34940d380512cac0177543dff` | arm64-v8a, armeabi-v7a, x86_64 |
| `app/build/app/outputs/apk/androidTest/debug/app-debug-androidTest.apk` | 382400 | `c276116bc3bad24383101f07191f1e71d29fa52c16fc4b3a6b38bec5b024b291` | none |
| `app/build/app/outputs/flutter-apk/app-release.apk` | 66969546 | `da66697f562d56ef34ea22e70c515c537f8cff640e3dda99007e8cf3fd617266` | arm64-v8a only |

Both app APKs contain `assets/kumpas_50sign.tflite` with SHA-256 `1f4543b8fb159dbe9a662f0b37e64b096f717d7527c45b2d7778f34bc0885aeb`. These are freshly inspected **existing artifacts**, not fresh builds or proof that every current source file produced them. No Android manifest/signature inspection was executed in this audit.

## 7 — Release inspection automation

**Exists:** exact artifact/protected-byte baseline in `controller/owner-parent-verification-1.json`, historical release logs, hash snapshots and layered tests. Search of repository release-named files found evidence logs, not a reusable release-inspection CLI. `benchmarking/verify_session_logging.sh` exists but is a different, device-oriented workflow; do not run it for this task.

**Minimal proposed implementation:** `benchmarking/inspect_release.py` plus `benchmarking/test_inspect_release.py`, standard library only. Require explicit `--repo-root`, `--baseline` and `--apk`/artifact selector; print JSON to stdout by default. Resolve inputs inside the intended repository, load the known manifest schema, validate `protected_count` against the map, hash every required protected entry, stream APK SHA/size, inspect ZIP without extraction, compare the exact Flutter ABI set and exact embedded model entry/hash. Reject missing files, duplicate required ZIP members, malformed baseline, bad ZIP, unexpected ABI, protected mismatch and model mismatch with nonzero exit and fixed diagnostics. Distinguish `baseline_artifact_match` from `current_source_build_provenance`; the latter cannot be inferred from SHA equality or Git HEAD alone in a dirty tree. Optional output must be an explicit new campaign path, never an old manifest overwrite. Do not build, install, invoke ADB, download dependencies or rewrite baselines implicitly.

Fixture tests can use tiny synthetic ZIPs and temporary directories: valid ARM64, extra ABI, missing/duplicate model, altered model, truncated ZIP, missing protected entry and declared-count mismatch. Fake ZIP fixtures test the inspector, not Android runtime validity. Signature/package/backup/network-policy inspection requires an explicit installed Android SDK tool path and declared assertions in a separate step; do not invent outputs when that tool is unavailable. A full release acceptance wrapper would compose this inspector with separately authorized build/test evidence, not replace those gates.

## 11 — Assessment rubric and export contract

### What the repository actually specifies

- `docs/PRD.md:148–162`: local pre/post capture; 40-participant experimental/control study tooling; standardized rubric; pre/post and engagement analysis. It does not itself specify scoring anchors.
- `.kiro/specs/16-evaluation-study-design/design.md:9–20,51–73`: proposed groups of 20; ten signs selected with the FSL Expert; 30-minute practice; pre/post human scoring; post evaluator different or blinded. Four dimensions: handshape, orientation, motion, timing; each 0–3. Handshape anchors: wrong, partially correct, mostly correct, reference match. Other dimensions reuse that scale for palm direction, trajectory/path and tempo/pacing. Documented totals: 0–12 per sign, 0–120 across ten signs. Two raters score a subset; kappa or ICC is proposed.
- That same design ends **Pending**, ready for ethics review after expert validation; `requirements.md:33–35` still says design not begun. This is documentary drift, not approval. No completed scoring-rubric file or approval record was located in the audited paths. `docs/phase10-expert-validation-protocol.md` is referenced by current gates as a blank expert-validation template, not study scoring approval.
- `docs/30-day-plan.md:894–978` requests paper instruments, explicit rubric, synthetic perfect/zero/partial/withdrawn fixtures, schema refusal, descriptive/paired/effect-size analysis and dummy-labelled null/strong-effect verification. These are planned deliverables, not completed scripts or approved human decisions.

### Existing implementation and actual serialization

- `app/lib/ui/assessment_screen.dart:26–76,201–213,285–295,390–393`: pre/post `fslConfidence` and `signsKnown`, both integer 1–5 Likert responses. `signsKnown` is **not a measured sign count**. Optional `ageGroup` and `gender`; post adds ten `susScores` items and `openFeedback`. These fields do not include ten observed signs, human raters, four dimension scores, group assignment, instrument version or withdrawal status.
- The UI labels feedback optional (`:333`) but `_postFormComplete` requires nonempty text (`:39–42`): genuine source-level inconsistency, not newly runtime-reproduced here. Capture this as a separate app-owner decision; do not silently redefine requiredness in a host validator. The local ten-item SUS-labelled text needs instrument/translation approval; a ten-item array alone does not establish a validated standardized questionnaire.
- `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/DataExporter.kt:45–80`: top-level `metadata`, `assessments`, `sessions` (nested `attempts`) and `summary`. No export schema-version field. Metadata includes participant UUID, device model, app/Android version and local timestamp without offset.
- `SessionDatabase.kt:77–84,247–265,301–310`: assessment objects contain `id`, `participant_id`, `type`, `timestamp`, and `responses` as a **JSON-encoded string**, not an already-decoded nested object. `feedback_items` is also stored as text. Decode these explicitly with duplicate-key/type/range checks rather than guessing alternate shapes.
- `DataExporter.kt:77` uses global `db.getAttemptCount()`; `SessionDatabase.kt:292–296` counts all attempts, whereas sessions are participant-filtered. Under a multi-participant synthetic database, summary totals may not agree with the scoped payload. Existing `DataExporterTest.export_excludesOtherParticipantsData` creates another session/assessment but no other attempt, so it does not cover this mismatch. Host tooling should reconcile nested rows and flag discrepancies, not trust this summary unconditionally. This is a static finding, not an executed defect test.
- Existing tests: `DataExporterTest.kt` covers structure, completeness, scoped data, fallback storage and helper ownership; `SessionManagerTest.kt`, `MainActivityBoundaryTest.kt`, and `app/test/assessment_save_failure_test.dart` cover checked persistence/failure/retry boundaries. Do not duplicate the exporter or claim integrated installed validation from these tests.

### Minimum safe design and blockers

First implement an explicit-file, read-only export validator with a named legacy exporter adapter. Validate shape, finite numeric values, pre/post types, decoded response shape, UUID relationships, duplicate assessment/session/attempt identities, and computed counts. Return fixed diagnostic codes; avoid echoing free text or device identifiers. Do not auto-select the newest of duplicate pre/post assessments, infer experimental/control groups or infer consent/withdrawal from missing rows.

Keep questionnaires, practice engagement and **human rubric observations** as separate datasets. A proposed sidecar schema needs instrument/version, pseudonymous join key, phase, selected sign identifier, rater code, four bounded integer scores and explicit missingness/status. That is a schema proposal, not permission to populate real codes or approve the rubric. Do not alter existing app/export schema just to fit a synthetic fixture.

Blocking research decisions: signed instrument/rubric approval; actual ten-sign list and per-sign anchors; assessor/blinding and adjudication rules; group allocation/join procedure including control participants without an app install; handling repeated assessments, partial signs, missing post-tests and withdrawal; consent/retention workflow; questionnaire wording and optional-feedback resolution. Existing 0–3 draft can be faithfully documented but not promoted to approved scoring. A production rubric scorer must remain blocked until those decisions exist.

## 12 — Synthetic validation and analysis

`evaluation/` contains only `.gitkeep`; `training/models/evaluate_frozen.py` and `benchmarking/accuracy_benchmark.py` evaluate recognition models, not participant learning. Reuse neither as a human study outcome scorer.

**Named proposed analysis is already present:** study design `:22–39` specifies paired t-tests within each group, Shapiro–Wilk on difference scores, Wilcoxon fallback, between-group independent t-test of improvements with Mann–Whitney fallback, and Cohen's d. Do not invent ANCOVA or silently substitute a new design. Equally, the proposal leaves important choices unspecified: paired versus independent d denominator, equal-variance versus Welch comparison, alpha/decision details, sidedness, confidence intervals/multiplicity, small/constant/zero-difference handling, missingness and rater aggregation. The power paragraph is a proposal claim, not verified analysis here.

Minimal staged tooling: (1) validate legacy export and separate sidecar; (2) construct explicitly paired records with an exclusion ledger; (3) only after approved scoring rules, compute totals; (4) descriptives and explicitly named statistical methods from an approved analysis specification. Every input/output must state `synthetic`/`dummy` origin; explicit paths only, no directory discovery of exports or default participant stores. Keep raw questionnaire free text out of reports. Require an explicit approved configuration before real-data mode; no implicit n=40 or generated real-looking identities.

Planned fixtures: perfect, zero, partial and withdrawn; duplicate pre/post, malformed nested JSON, missing phase, invalid dimension type/range, cross-participant references, conflicting summary counts, empty sample, singleton, identical paired differences and all-zero differences. After decisions, add analytically specified null/strong-effect cases with independent expected values; never fabricate p-values. Undefined statistics should be null with a reason, not NaN/zero/success. Until decisions are supplied, validation/descriptive plumbing may be built, but full rubric scoring and inferential acceptance must be reported blocked.

## 13 — Current status versus archive

Controlling chronology under `benchmarking/study_evidence/20261007/controller/`:

1. `owner-parent-verification-1.json` records October 9 artifact/suite evidence.
2. `bounded-software-acceptance-1.{md,json}` accepts bounded software with a minor schema follow-up and leaves integrated/physical/study gates open.
3. `schema-minor-acceptance-20261011.json` closes that narrow follow-up after review; this supersedes the pending-review sentence in `schema-minor-parent-20261011.md` and the minor-open statement in October 9 documents.

Historical counts: October 9 records 137 JVM / 35 Flutter / 42 Python and builds; October 11 records 43 Python and renewed 137 JVM, with no new APK build. These suites were **not rerun here**. `docs/phase-gates.md:16–26` gives the superseding status, while older table cells retain changes-required descriptions. `owner-parent-handoff-1.md` still says reviewers active, but it is historical. Do not reopen accepted fixes based on that sentence.

Proposed current campaign index: one timestamped status table linking exact acceptance/snapshot/log paths; columns `implemented`, `last executed`, `reviewed`, `current-hash match`, `remaining gate`, `owner/dependency`. Explicitly label archived reports and keep all original bytes. Phase 11 should say partial app capture/export, research instrument/scoring incomplete; Phase 12 analysis absent. Do not rewrite protected history, old logs or evidence manifests for cosmetic consistency. This audit did not edit any status document.

## 14 — Handoff

Already implemented: `benchmarking/generate_handoff.py`, `benchmarking/test_handoff.py`, `benchmarking/handoff_blank/{candidate_devices.csv,condition_runs.csv,sign_trials.csv,confusion_matrix.csv,generation_checks.json}`. Generator validates dense label IDs and unique source IDs, emits blocked/blank cells, and CLI refuses a nonempty output directory. Existing forms are protected, not missing work or measured observations. Candidate phone labels do not establish hardware availability. `benchmarking/environment_protocol.md:85–200` defines setup provisioning, immutable snapshot, chip vocabulary, actual APK hash, camera representation and scoped control companion.

Minimal addition: a current host handoff index linking existing forms/protocol/acceptance and an explicit pending-device checklist. Never fill lux, signers, trials, hardware verification flags or approvals. Any future generation requires a new empty output directory, not `handoff_blank`. Phone/emulator commands remain a separate authorization gate, even if old PRD language mentions emulator fallback. Current user prohibition controls this campaign.

## 15 — Architecture decisions

No ADR-named file was found by repository filename discovery. Existing evidence includes `docs/phase-gates.md:50`, `docs/30-day-plan.md:81,93,1435–1436`, and `docs/superpowers/specs/2026-09-29-shipped-pipeline-verification-design.md`. They document locked Holistic versus shipped PoseLandmarker + HandLandmarker/258 features, and locked Colab versus local M1 historical training. These are unresolved approval/documentation matters, not authorization to swap models or retrain.

Proposed separate decision records: (a) shipped split-landmarker deviation and parity/anatomy limits, (b) historical local training environment deviation, (c) local-only study export with no implied cloud approval, (d) legacy questionnaire export versus separate human-rated rubric. Each records status **proposed / approval pending**, exact current evidence, alternatives/consequences, affected gates and empty approval fields. Keep already approved receipt-commit/structured-metadata policy linked to `owner-approved-review-closure-brief-2.md`, rather than asking for that same decision again. No invented PM/adviser/expert sign-off.

## 16 — Final host verification plan and runnable commands

Commands below are future authorized checks, **not execution claims**. Run from the exact repository above. `/opt/homebrew/bin/python3.11` existence was verified; dependencies were not imported/installed here. Use a unique campaign command ledger/log per invocation and the established shared Gradle/build lock; rediscover its actual runner path before scheduling builds. Do not run concurrently with another owner's build.

```sh
# Focused existing host collector/history/plot/handoff tests, then broad discovery:
PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg PYTHONPATH=. /opt/homebrew/bin/python3.11 -m unittest benchmarking.test_collectors benchmarking.test_history benchmarking.test_plot_history benchmarking.test_handoff -v
PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg PYTHONPATH=. /opt/homebrew/bin/python3.11 -m unittest discover -s benchmarking -p 'test_*.py' -v
# Existing Flutter analysis and fixtures; requires existing cached dependencies:
(cd app && flutter analyze --no-pub)
(cd app && flutter test --no-pub --reporter expanded)
# Existing JVM export/persistence boundaries, only through the shared lock:
(cd app/android && ./gradlew --offline :app:testDebugUnitTest --rerun-tasks --tests 'com.kumpas.kumpas_app.DataExporterTest' --tests 'com.kumpas.kumpas_app.SessionManagerTest' --tests 'com.kumpas.kumpas_app.MainActivityBoundaryTest')
```

Do not execute device instrumentation/ADB from this host-only plan. New inspector/validator/scorer tests have no runnable module yet; do not report planned filenames as passing tests. Full-suite execution must retain actual exits and parsed JVM XML counts/failures/errors/skips; distinguish missing dependencies from source failures and cached Gradle results from forced execution. If build authorization later arrives, separately force instrumentation-source compilation/debug/test assembly and ARM64 release under the lock; compile/build does not mean installed execution.

Final campaign acceptance requires before/after protected hashes, all tracked dirty postimages plus new files captured (HEAD alone is insufficient), actual new test evidence, independent review, exact artifact inspection and a current status table. Preserve failed logs. Explicit remaining limits: continuous installed CameraX/channel/UI/SQLite/export/delete/reopen; physical FPS/latency/thermal/setup; all-sign/live-signer coverage; expert/anatomical validation; failed selected-model numerical gate and missing signer-independent untouched evaluation; study instrument/statistical decisions, consent and participant authorization. Host success closes none of these automatically.
