# Face-inclusive data implementation plan and bounded task brief

> For agentic workers: use subagent-driven-development and strict vertical test-driven-development. Parent owns acceptance, real rebuilding and progress/decision updates. No Git commits or pushes.

**AGENT:** Data/Preprocessing, one cohesive implementer.
**PHASE:** Holistic migration prerequisite and Phase 3 Data, not PRD Phase 3 model evaluation.
**OBJECTIVE:** Deliver an additive, tested hm1588-v1 preprocessing and lossless-raw reuse builder, without real data execution.
**INPUT:** Approved `docs/holistic-migration/FEATURES_FACE.md`; unchanged `FEATURES.md`, `CAPTURE_CANDIDATE.md`; accepted `training/holistic_migration/{features,sequence,dataset,detector}.py` and existing tests; source ownership manifest at `../holistic-migration-data/evidence/face-data-resume-20261116/protected.json`.
**OUTPUT:** New files only: `training/holistic_migration/face_features.py`, `face_dataset.py`, `tests/test_face_features.py`, `tests/test_face_dataset.py`, `FACE_DATA_README.md`; append-only `docs/holistic-migration/face-data-report.md`. External synthetic evidence only under a fresh child of `../holistic-migration-data/evidence/face-data-worker-*`.

## Binding constraints

Read AGENTS.md, PRD and current owner requirement; the parent's newly recorded owner approval authorizes this bounded work. All existing historical production/test/spec/report paths are protected; do not edit them or relax graph/runtime bindings. Do not mutate the new parent-owned FEATURES_FACE.md. Only the six declared new paths may be created/changed. No real raw/video/model/array reads, detector/camera/GUI, training/classifier/model/evaluator, app/mobile/device, installs or Git writes. Synthetic existing fixture helpers are allowed; explicitly mark synthetic bundles as synthetic_in_process. Existing accepted trainer remains 153-specific and must not be advertised as compatible.

## Task 1: shared face features and capture

Create `face_features.py`. Consume unchanged `RawFrame`, `pack_frame`, `CaptureResult` and existing capture policy. Export `FEATURE_VERSION='hm1588-v1'`, `FEATURE_COUNT=1588`, `pack_frame(frame)`, `resample_frames(frames,steps=30)`, `prepare_capture(frames)`. Aliased imports avoid accidentally calling the new function recursively. Follow every exact numerical/missingness/priority rule in FEATURES_FACE.md. Reuse existing primitive behavior, but never change or monkeypatch historical modules. Build independent expected geometry and time indices in tests, not self-comparison alone. Guard present-empty/wrong cardinality, semantic arrays, finite-conversion overflow, input mutation, missing shoulders and missing single hand. Assert the first 153 columns equal the accepted packer bit-for-bit for valid shoulders. Test unchanged temporal ties/masks and internal face gaps.

- Write the first behavioral test reaching the missing behavior, record actual failing assertion (missing import/typo is not behavioral RED), then add minimum implementation and rerun it GREEN.
- Add one behavior slice at a time. Preserve RED/GREEN logs/commands/source snapshots or hashes. Existing-control passes are coverage-only GREEN, never fabricated RED.

## Task 2: raw reuse diagnostic, bundle builder and consumer validation

Create additive `face_dataset.py` with `build_dataset(*,campaign,output,diagnostic_fit_only=False)` and `validate_bundle(output)` plus `python -m training.holistic_migration.face_dataset --campaign ABS --output FRESH_ABS [--diagnostic-fit-only]`. Use the actual accepted `dataset.validate_campaign` and `read_raw` to prove full producer graph/provenance/raw compatibility. It is acceptable that this validator reads the existing full campaign even for a diagnostic; distinguish provenance validation of all raw files from selected 50 new-feature preparation. Do not open media or instantiate detectors. Preserve source/current contract/runtime bindings; use new explicit bindings for all new module/contract bytes and transitive unchanged source dependencies. A source_video output must never be called synthetic or vice versa.

The existing validator has costly full raw readback. Keep run time/memory bounded, process one source at a time, avoid extra bulk fixture copies and retain raw/derived counts separately. Full tensors total approximately 193608960 bytes if all1016 sources are eligible; this is storage planning, not measured execution.

Diagnostic: first lexicographic clip_id per already-frozen fit class, selected_ids saved before face preparation, all declared partition/class denominators retained; other rows not_selected, not presumed eligible. Never claim full dataset completion or full qualification for a diagnostic. Parent decides feasibility from diagnostic results before invoking full build.

Full build: apply new capture to all old raw rows; no splitting/augmentation, keep all50 labels. Store exact ordered partitions/IDs, all source/raw identities and presence/cardinality summary, eligibility per class/partition, ineligible/re-record list, contract copy, graph and current implementation/campaign bindings. Reject missing fit/validation class support with failure evidence and no successful full manifest. Test zero-eligible test partition as [0,30,1588]. Include all new artifacts and required JSON/NPY dtype/shape/digest readback. training_qualified=false, live_ready=false, model_evaluated=false always. A success manifest must not imply training or linguistic/physical acceptance.

Implement primary-preserving exclusive completion publication within owned module, not protected dataset.publish_json. Stage/readback/link/readback and retain pending bytes. On readback failure revoke only own just-published completion; retain original exception if rollback/failure diagnostics also fail; best-effort persist fixed failure disposition. validate_bundle must reject persisted failure, malformed schema, diagnostic-as-full, tampered artifacts/current sources and failed-target retry; do not simply trust marker presence or schema equality accepting bool/float. Preserve established completions on later transient validation failure. No sandbox/hostile-writer/crash guarantees.

Test with actual synthetic production campaign fixture, complete50 classes and all partitions, malformed/provenance/cardinality faults, changed raw digest, output collision/overlap, copied contract tamper, publication+rollback faults, failed-target consumer denial and healthy controls. Exercise real subprocess CLI --help, one synthetic full success and rejection paths. Avoid requiring a real detector for tests.

## Task 3: final verification and handoff

Write FACE_DATA_README.md with exact exercised commands and boundaries. Report incremental source hash and command/log/exit/JUnit evidence, synthetic labels and all concerns in face-data-report.md. Use the current verified interpreter `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B` with TMPDIR `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch`. Run new tests, full migration suite and original training tests. Baseline full migration489 cases+293subtests and original51 cases+289subtests; 67/3 warnings respectively are prior evidence, not guaranteed new totals. Record actual new counts. No need to exercise real native blank detector or camera.

Before return, verify all protected hashes and owned path hashes, save an external `handoff.json` binding delivered files, protected receipt and every retained log/XML/command/stage record. Do not recursively duplicate old evidence archives. Return only DONE/DONE_WITH_CONCERNS/BLOCKED, absolute handoff/report paths, short test summary and concerns. Parent must independently read/verify source, execute tests and obtain complete independent spec/quality approval before real source rebuilding. This worker has no authority to close acceptance or start actual data processing.

## Parent continuation after reviewed delivery

Freeze complete six-file delta plus approved contract/brief, review both spec and quality, and accept only bounded software. Use fresh exclusive external diagnostic/full outputs. Record available disk, separate UTC wall and monotonic intervals, timeouts, exact commands and source hashes before execution. Parent separately recomputes all tensors against unchanged raw observations, reconciles manifest/eligibility/partitions/source hashes and preserves historic data. Record current-source data acceptance and limits. Stop after Phase 3 data handoff; actual training requires a new decision.
