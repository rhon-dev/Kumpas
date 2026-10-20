# Explicit-file assessment utilities

These host-only tools validate the **legacy** `DataExporter` / `SessionDatabase` export and generate **SYNTHETIC-only** descriptive questionnaire counts. They are not a human rubric scorer, a validated SUS scorer, an inferential analysis pipeline, or permission to process participant data. No default databases or export directories are searched. No dependencies are installed.

## Audited contract

Source references: `app/lib/ui/assessment_screen.dart:35–76,201–242,284–295,389–393`; `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/SessionDatabase.kt:48–84,136–172,247–265,301–310`; `DataExporter.kt:74–111`; `FeedbackEngine.kt:108–117,120–141,144–178,181–209,253–255`; `app/lib/feedback_engine/models.dart:18–32`.

- Export root has `metadata`, `assessments`, `sessions` and `summary`, with no legacy schema-version field. This adapter rejects unknown fields instead of guessing a newer contract.
- Metadata participant IDs and session IDs are canonical lowercase UUID strings. Assessment and attempt IDs are positive database integers, **not UUIDs**. IDs are unique within each corresponding exported table; attempts across all nested sessions share a single ID namespace. Participant and session foreign-key relationships must match the actual containing export/session.
- `responses` and `feedback_items` are JSON-encoded **strings**, not predecoded objects. Both encoded and outer JSON reject duplicate keys, NaN/Infinity and overflowing floating-point literals. Exact integer fields reject booleans and integral-looking floats. No private values or JSON parser exception messages appear in diagnostics.
- Required pre and post responses: integer `fslConfidence` and `signsKnown`, each 1–5. `signsKnown` is an ordinal self-report, **not an observed number of signs**. Post additionally requires ten integer 1–5 `susScores`. No standardized SUS total is computed: the local SUS-labelled wording/translation has not been approved as an instrument in this scope.
- Optional `ageGroup` domains: `<13`, `13-17`, `18-25`, `26-35`, `36-50`, `>50`. Optional `gender`: `Male`, `Female`, `Non-binary`, `Prefer not to say`. If supplied, these fields must be domain strings; absence differs from null/invalid. Optional post `openFeedback` may be absent or an empty string. Reports count its presence/absence/emptiness, never its content. Current A1 source has resolved the earlier discovery report's feedback-requiredness inconsistency.
- Technical confidence, overall match, session average match and feedback severity are finite numeric values in [0,1], from the existing normalized producer mathematics, **not human scores**. They are not included as outcomes or summarized numerically. Feedback dimension, hand and prompt retain the existing consumer's string types; no linguistic validation is inferred.
- Counts, target class and timestamps are nonnegative exact integers; row IDs are positive. Recognition is SQLite integer 0/1, not a JSON boolean. Duration is finite and nonnegative. Source is `app` or `legacy_migration`. An ended session cannot end before it starts. This adapter does not infer measurement units from arbitrary text, cross-check labels against a selected model, validate wall-clock chronology, or invent a maximum target class.
- Root totals are independently recomputed from scoped nested rows. Closed-session attempt/distinct-target counts must agree. Active-session summaries can lag by design; their zero defaults are not inferred to mean zero observed attempts. No average recomputation, tolerance policy or human outcome policy is invented.

The authoritative accepted A3a producer was separately hash/XML/ledger/source-verified before reading its isolated synthetic exports. Its nonempty transport fixture stores `synthetic`/`stage` response keys rather than the UI questionnaire fields; it is correctly rejected with `REQUIRED`. The empty reopened export validates. These are schema/transport observations, not a new native run or a new app defect. See C2 `native-contract-audit.json` and fresh-run counterparts.

## Explicit event matching and descriptive limits

`describe_exports(inputs, source='SYNTHETIC')` accepts a list of explicit byte snapshots. One export per participant is required; duplicate participant exports reject the batch (`DUPLICATE_EXPORT`). All records must validate before any frequencies are returned. No record is silently dropped.

Pair availability uses only participant identity plus explicit `type: pre/post`. Assessments do not have session IDs; no session-level pairing is possible. Exactly one pre and one post gives `paired`; repeats give `AMBIGUOUS_PHASE`, a single phase gives `UNMATCHED_PRE`/`UNMATCHED_POST`, and no assessments gives `NO_ASSESSMENTS`. Order and timestamps do not choose a newest record or assign a phase. Fixed diagnostics include input indexes, never participant UUIDs.

Reports contain counts, pair availability, optional-field completeness and per-phase frequencies for known structured questionnaire fields (including ten separate item frequency tables). Frequencies include valid repeated-phase records, while pair availability excludes ambiguous participants. Denominators are records for frequencies/completeness and unique participants for matching; optional feedback completeness uses post records only. No missingness imputation, numeric questionnaire total, improvement score, consent/group/withdrawal inference, rater aggregation, p-value, effect size or effectiveness claim exists.

## Running safely

Use the existing interpreter from the repository root:

```sh
/opt/homebrew/bin/python3.11 -B -E -m unittest discover -s evaluation -t . -p 'test_*.py' -v
```

For a fresh, explicitly supplied synthetic root with read-only input copies, choose a new numeric output label:

```sh
/opt/homebrew/bin/python3.11 -B -E -m evaluation.export_cli \
  --mode describe --root /absolute/explicit/synthetic-root \
  --input SYNTHETIC-input-1.json --input SYNTHETIC-input-2.json \
  --source SYNTHETIC --output-label SYNTHETIC-005
```

Do not run this example against app stores or participant exports. Repeat `--input` for each explicit root-relative file; no globs, absolute input paths, traversal, symlink components or nonregular files are accepted. The root must already exist, be absolute, and have no symlink or dot components. Inputs are opened read-only and bounded to 16 MiB each. The same in-memory bytes are validated, described and hashed; files are not reread between those stages.

`--mode validate --source UNATTESTED` is technical validation capability only, not authorization, a consent assertion or a synthetic-origin assertion. It produces no descriptives. All executions for this task used generated synthetic data, including the UNATTESTED regression. The `SYNTHETIC-N` output-directory name is a restricted campaign namespace, not a substitute for the manifest's explicit source declaration. Real participant processing still requires separate owner/ethics/retention authorization and an approved workflow; none is granted here.

Successful runs exclusively create the named output directory, `report.json` and `manifest.json`; no existing directory/file is reused or overwritten. A manifest binds input indexes/hashes, explicit source/mode/output label and the report digest. Report bytes are read back before the success manifest is written, and the manifest itself is read back before success is printed. Failures have fixed JSON errors and exit 2; success exits 0. `--help` and malformed arguments also return fixed JSON errors; this README is the usage reference. A failed publication may leave its exclusive directory/diagnostic report; choose a new output label, do not reuse it. Cleanup removes only an owned manifest inode, preserving an unowned collision. No directory fsync/power-loss durability or defense against a hostile concurrently relocating directory owner is claimed. Use a trusted, isolated root.

Reproduce the C2 evidence with a **new** campaign suffix; existing evidence is exclusive and must remain unchanged:

```sh
/opt/homebrew/bin/python3.11 -B -E -m benchmarking.study_evidence.20261015.c2.exercise synthetic-cli-newrun
```

This creates only C2 synthetic evidence, executes both modes with valid/invalid inputs, independently recomputes all declared counts/frequencies/completeness and verifies input/output hashes. It also verifies the already accepted synthetic native producer binding before reading its three named export artifacts. It does not execute native code or touch installed stores.

## Remaining gates

Host11 is eligible only for bounded legacy-questionnaire validation. Host12 is eligible only for synthetic descriptive/matching plumbing, pending independent parent/specification/quality review. Human instrument/rubric and selected-sign anchors; wording/translation approval; assessor/blinding/adjudication; group allocation/join procedure; repeated/missing/withdrawn policy; consent/retention; and detailed statistical choices remain owner/adviser/ethics decisions. No participant or inferential acceptance is supplied by green software tests.
