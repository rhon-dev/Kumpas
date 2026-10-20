# Host-only completion design

Status: owner approved host-only implementation by replying `continue` after the design and approval question. Retraining and unapproved research scoring remain separate gates. This design covers the 16 requested host tasks without an emulator, physical phone, ADB, participant records, model deployment, commits, dependency installation or paid services. Existing accepted repairs and protected historical files remain intact.

## Approach and alternatives

Recommended: extend existing production seams and deterministic tests, execute real host producers, replay their versioned artifacts into Flutter/Python, and preserve explicit boundaries between these processes. This gives reproducible layered contract evidence without pretending to run installed integration.

Alternative: only add standalone mocks and documentation. Lower implementation cost, but it leaves the producer/consumer and persistence handoff untested.

Alternative: broadly refactor the app and research pipeline before testing. Rejected: unnecessary risk to accepted work, feedback mathematics, XP, layout and historical assets.

## A. App contracts and fixtures (tasks 1–5)

Use unique synthetic roots for SQLite, preferences and exports. Refuse default stores and pre-existing campaign output. A native host test executes production event/control behavior, persists records, exports, clears and reopens. It emits exact event payloads and independently observed state snapshots in a versioned test envelope. Flutter consumes these exact artifacts through explicitly mocked transport and verifies feedback, ACK and cache invalidation. Python consumes native benchmark artifacts through actual reader/assessment/history code with transport mocked and real device subprocesses forbidden.

Add only narrowly necessary native control, initialization and exporter seams; production registration must use the same dispatch tested by the harness. Never duplicate business logic in tests. Preserve current UUID-receipt ownership and structured-metadata contracts. Bind artifacts to a fresh run manifest and source hashes; refuse missing, failed, skipped, stale or duplicate producers.

Characterize suspected lifecycle races, late session responses, partial-clear cache invalidation and activity acquisition rollback with failing regressions before fixes. Existing passing coverage is coverage-only GREEN, not a new repaired defect.

Proposed export contract: a failed write must not destroy a previous completed export or publish a partial successful export. Use unique publication identities and verified, failure-safe publication in owned export roots. Test participant-scoped summary counts against payload rows. Preserve borrowed database ownership and existing export compatibility.

Resolve the form contradiction in favor of its existing label: optional feedback remains optional, while required questionnaire answers remain required. Confirm this with widget regressions.

## B. Parity and provenance (tasks 6, 8, 10)

Generate external fixtures for all six existing FIVE/THREE validation clips: THREE 22/14,22/8,22/9; FIVE 24/10,24/11,24/18. Keep video, PNGs and landmark vectors outside Git. Compare sampled-frame and original full-video preprocessing as distinct paths. Tighten fixture/schema/digest/type/identity validation without changing normalization mathematics. No Android replay or anatomical agreement is claimed.

Run validation-only frozen Keras/candidate inference, producing immutable clip-level predictions, class summaries and numerical drift diagnostics. Do not reopen reused test data for tuning. Bind arrays, label semantics, ordered clips, selection, checkpoint, runtime and outputs in a new campaign manifest. Do not retrofit historical manifests as preregistration. Conversion execution and numerical acceptance remain separate; no candidate promotion occurs.

## C. Model experiments (task 9)

Prepare isolated campaign execution and validation-only selection tooling first. Actual retraining remains a separate approval gate because the local-versus-Colab deviation is unresolved and existing CLI writes protected historical logs.

Proposed bounded experiment policy, if subsequently approved: at most two sequential single-factor variants, unchanged split/seed/no-face CNN-LSTM shape, maximum60 epochs/batch32/early-stop patience15 and15-minute enforced wall-clock limit per run. One dropout variant and one learning-rate variant; exact baseline-relative parameters must be frozen before training. No new test evaluation, sweep expansion, automatic deployment or overwriting existing logs. Resource use is sequential on the discovered8GB host.

## D. Release and research tools (tasks 7, 11–12)

Implement a standard-library APK inspector with explicit inputs, streaming hashes, ZIP member/ABI/model/label/asset assertions, protected-map checks and immutable JSON output. Reject malformed baselines, missing/duplicate required members, mismatches and corrupt archives. State whether an artifact merely matches a historical baseline or is tied to a newly executed build.

Implement an explicit-file legacy export validator and synthetic-only descriptive pipeline. Validate nested JSON, participant relationships, duplicate identities, pre/post types, finite values, ranges and independently computed counts. Keep questionnaires, engagement and human rubric observations separate. Never echo free-text responses in diagnostics or infer consent, group, withdrawal or missing-score values.

The located four-dimension0–3 human rubric and proposed inferential methods are pending approval. Implement validation/descriptive plumbing and faithful draft schemas, but no authoritative rubric scoring or real-data/inferential acceptance until instrument, sign list, rater, missingness and analysis decisions are approved. These conditional tasks must remain explicitly blocked, not falsely marked complete.

## E. Documentation and final verification (tasks 13–16)

Create one current campaign index with implementation, actual execution, review, source/hash identity and remaining dependency columns. Clearly separate historical reports without modifying protected original evidence. Draft architecture deviations as proposed, not approved. Link existing blank handoff forms rather than regenerating or filling them.

Run focused RED/GREEN cycles, full Flutter analysis/tests, forced JVM tests, Python benchmarking/training/evaluation tests, instrumentation-source compilation and debug/test/ARM64 release assembly as applicable using existing environments. Serialize Gradle/build and compute-heavy jobs. Capture exits, parsed counts, logs, artifact identities and protected hashes. Independent specification and quality review must cover the complete changed source plus new files before acceptance.

## Preservation and success criteria

All82 original protected hashes must remain equal unless the owner explicitly authorizes a named exception. No existing training log, installed model, participant store, original benchmark history, scoring mathematics, XP or approved UI layout is changed. Preserve unrelated work and failed execution logs.

Each requested task receives one explicit disposition: completed with evidence, already supported with evidence, or blocked by a named input/approval. A prepared harness is not an installed end-to-end pass. Host work does not close physical performance, real camera/resource behavior, live-signer, linguistic, anatomical, human-study or participant-authorization gates.

## Source of requirements

Read-only discoveries: benchmarking/study_evidence/20261015/discovery/app-host-audit.md, model-host-audit.md and tooling-host-audit.md. Baseline: benchmarking/study_evidence/20261015/controller/host-baseline.json. The discovered defects remain hypotheses until executable regression evidence establishes them.
