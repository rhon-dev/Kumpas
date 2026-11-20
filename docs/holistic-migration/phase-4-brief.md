# Phase 4 — Face-inclusive candidate training and evaluation

## Authority and scope

AGENT: Model/Training, with independent QA/specification and quality review.
PHASE: Holistic Migration Phase 4, **Model changes and all-gesture retraining**; not PRD Phase 4 export/device work.
OBJECTIVE: Implement compatible hm1588-v1 tooling, prove actual-source tiny memorization, fit a fresh all-50 candidate, freeze validation-only selection, then run a separately invoked exploratory reused-test evaluation.

The owner's current instruction is: `phase3 complete \nnow do phase 4\n/caveman`. This is phase-specific authorization for this complete model-phase sequence, superseding earlier withholding of model-phase work. Execute dependent stages only after their prerequisite verification/review; no repeated phase permission request is needed. A failed tiny criterion or blocking review finding must not be bypassed. Model candidate freezing is not adviser, deployment, research, or live acceptance.

INPUT:
- Repository `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`, branch `holistic-migration`, starting HEAD `3b1f1d8efa29d1e717833f3869c77872e4df021c`.
- Accepted data `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/hm1588-canonical-bundle-20261116-v1`.
- Its data_manifest.json SHA-256 `71c644b4de78f7031f96f7b25b1d5766f18fa611c33ad12f2a40a353b1c6c19a`.
- Data acceptance `../holistic-migration-data/evidence/face-data-parent-20261116/dataset-acceptance.json` and `docs/holistic-migration/PHASE_3_STATUS.md`.
- Contract `docs/holistic-migration/FEATURES_FACE.md`: Float32[N,30,1588], existing 153 prefix plus 478 face XYZ and face mask. No feature or capture changes.
- Accepted historical train.py/evaluate.py/augmentation.py are source references for preserved family/protocol, **not compatible entry points**.
- Existing Python `~/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python`, TensorFlow 2.19.0, Keras 3.15.1, NumPy 2.1.3. No installs. Approved TMPDIR `~/.hermes/cache/scratch`.

## Constraints

Preserve every pre-existing source, dataset, contract, report and receipt byte except parent-owned current status documents. All code is additive under training/holistic_migration/. Do not alter original trainer, historical migration trainer/evaluator/augmentation, data producers, shared contracts or mobile assets. No monkeypatching historical module globals as a production adapter. No app edits, detector extraction, camera launch/recording, phone/SDK operations, participant processing, model activation/export, paid services, Git commit/push/merge or environment/provider changes.

Use local CPU bounded resources already available. Record host/runtime/threads. New outputs must be fresh external paths below `../holistic-migration-data/evidence/phase-4-20261116/`; no historical overwrites or repeated run reuse. Keep receipts and logs focused, not full copies of old evidence trees. Parent owns actual-source operations and all status/admission acceptance. Implementer runs synthetic tests only; review precedes actual fitting.

## Requirements and measurable acceptance

1. Add `face_train.py`, `face_evaluate.py`, `face_augmentation.py`, corresponding tests and `FACE_TRAINING.md`. Preserve historical code unchanged. Reuse stateless safe helpers where suitable; no source identity laundering or dynamic module injection.
2. Face admission must bind parent dataset acceptance, exact bundle/manifest, face implementation/current producer bindings, runtime, ordered dense/original/literal 50 labels and immutable partition/source identities. Training opens/hashes only fit and validation tensor contents. Never call full face_dataset.validate_bundle from the training path because it accesses test tensors/raw. Parent provenance verification may check accepted metadata bindings and fit/validation contents separately. Test metadata is allowed before freeze; classifier scores/test contents are not.
3. Require source_video provenance for CLI, completed/full unaugmented hm1588-v1, failed/incomplete denial, strict schema/type/digest/path checks, finite Float32 shape, all50 fit/validation support, mask and missing-block invariants, usable shoulders/face, face-mean Z tolerance, unique/disjoint clip IDs, original partition/labels, declared/eligible/exclusion reconciliation. Synthetic fixtures remain labeled synthetic and cannot pass real admission. Keep builder training_qualified=false untouched; use separate parent admission.
4. Retain exact family topology: Conv1D64/128 kernel3 same ReLU with BatchNorm, MaxPool2, LSTM128(return_sequences)/64, dropout0.4 after each, Dense128 ReLU/dropout0.4, Dense50 softmax. Fresh weights, input30x1588; Adam0.001 and sparse CE, seed20260705. Verify real forward/optimizer/save/reload on explicit synthetic inputs. No architecture search.
5. Full-fit augmentation: one source-ID-seeded whole-sequence XY rotation within +/-5 degrees per fit original. Apply SAME angle to hands, visible pose and all present face XY. Preserve Z, visibility, masks and absent/low-visibility blocks exactly. Do not augment validation/test/tiny; no mirroring, swapping or invented observations. Record angles/IDs/policy.
6. Tiny: first literal eligible fit ID for dense0..7, exactly8 real sources, unchanged50 outputs, no augmentation, max300 full-batch epochs. Publish proof only if saved/reloaded checkpoint gives8/8 correct and mean CE<=0.1. Retain IDs, tensors/digests, model, history, optimizer steps and source/runtime/config/dataset bindings. Full entry rechecks/reloads this proof on exact fit-only examples before a fresh full fit; failed/incomplete proof cannot qualify. No synthetic backend/epoch bypass for real data.
7. Full: fixed max120 epochs/batch32/shuffle seed, explicit unaugmented validation, EarlyStopping val_accuracy max patience15, ReduceLROnPlateau val_loss min patience6 factor0.5. Earliest max validation accuracy checkpoint wins exact ties. Train all50. No test read or scoring before independently reserved evaluation. Save reproducible configuration, augmentation, actual epochs/steps, train/validation loss/accuracy history and validation probabilities/IDs. Save/reload selected candidate and freeze source-bound model/labels/policy before reports/evaluation.
8. Report all50 precision/recall/F1/support/per-class accuracy or recall, confusion50x50, macro-F1, loss/overall accuracy, exclusions and eligible vs all-declared denominators; do not turn missing sources into fabricated predictions. Explicit bounds/all-source accounting are acceptable, not mislabeling correct/declared as measured accuracy. No observed annotated validation negatives exist: rejection calibration/FAR/idle/unknown safety are **unmeasured** (null), no invented zero rates or thresholds. Freeze explicit closed_set_argmax policy, live_ready=false. Distinguish zero policy rejection among scored positives from19 data exclusions.
9. Separate evaluation command must verify frozen selection/proof/config/model/current-source identities, exclusively publish evaluation-start before any test hash/load/inference, then write predictions/probabilities/IDs/labels and complete reports. Always label test exploratory_reused_test, fresh_untouched_holdout=false, tuning_allowed=false. No candidate ranking/retuning from test. Existing complete target readback only; incomplete/failed target no implicit rerun. Source-bound failure/publication semantics must deny residual failed proofs/selections while preserving a valid selection after later reporting failure. No hostile-writer/power-loss guarantee claims.
10. Strict vertical TDD: retain behavioral RED then GREEN for each behavior slice; distinguish already-passing coverage. Run full affected, full migration and original training suites. Preserve runtime/deprecation warnings. Independent review returns separate specification/quality verdicts and exact consumed-input bindings. Parent checks source hashes and runs current relevant tests before actual fitting.

## Ownership and handoff

IMPLEMENTER WRITE SET ONLY:
- training/holistic_migration/face_train.py
- training/holistic_migration/face_evaluate.py
- training/holistic_migration/face_augmentation.py
- training/holistic_migration/tests/test_face_train.py
- training/holistic_migration/tests/test_face_evaluate.py
- training/holistic_migration/tests/test_face_augmentation.py
- training/holistic_migration/FACE_TRAINING.md
- docs/holistic-migration/phase-4-report.md
- its own focused evidence directory below external phase-4 root.

Parent owns this brief, OWNER_DECISIONS.md, HOLISTIC_MIGRATION_PLAN.md, PROGRESS.md, new PHASE_4_STATUS.md, admissions, actual tiny/full/evaluation commands and final adjudication. All other inputs protected. If a requirement needs a protected edit, report blocker rather than widen scope.

OUTPUT LOCATION: code/docs above; external command/log/XML/source snapshot records under phase-4 root. Implementer report includes exact path/hash manifest, commands/exits/test counts, observed RED/GREEN, source and output ownership, concerns and actual CLI commands parent should run. Return concise DONE/DONE_WITH_CONCERNS/BLOCKED, report path and test summary. No commits. No phase acceptance by implementer.
