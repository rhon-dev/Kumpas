# Public-data rejection calibration — bounded implementation plan and task brief

> For agentic workers: use subagent-driven-development and strict test-driven-development. Parent owns real-source operations, review, admissions and acceptance. No Git commit is authorized.

AGENT: one Model/Training software implementer with independent QA/specification and quality review afterward.
PHASE: post-Phase4 offline rejection evidence; not live, device, participant or phone work.
OBJECTIVE: prepare an isolated source-bound OOV extraction/calibration/challenge pipeline for the accepted frozen50-output hm1588 model; retain failure if the approved threshold targets cannot both be met.

## Inputs and authority

Repository `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`, branch `holistic-migration`, starting/current HEAD `3b1f1d8efa29d1e717833f3869c77872e4df021c`.
External stage `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/rejection-calibration-public-v1`.
Owner answers and approved targets: stage `owner-authorization.json`; parent protection map and source snapshots: stage `baseline.json`.
Prior accepted classifier: sibling `phase-4-20261116/full-source-v1/model.keras`, SHA-256 `ea50489a27353cbf4f4e9b53b1a6252fa7c5c6a9f0021660347f7dcc1b1cda47`; exact phase4 acceptance/labels/contract/selection and saved validation probabilities under sibling `phase-4-20261116/all50-campaign-v1/` and `full-source-v1/`.
Accepted feature/capture code: `features.py`, `sequence.py`, `detector.py`, `face_features.py`; raw codec/helpers: `dataset.py`. Training/selection bindings are explicit lists; new files must not modify their contracts.
Original public sources outside Git: `~/KumpasBuilds/holistic-migration-data/{clips.zip,labels.csv,train.csv,test.csv,holistic_landmarker.task}`. Archive SHA-256 `c048c0820be1621101dfedeabb76a9fbfca76ed2868eebe23b4cb90d5c748463`.
Readiness inventory and proposal: sibling `acceptance-readiness-20261116T232657Z/{readiness.json,oov-source-candidates.csv,CONTINUATION_GATES.md}`. Original105 labels/2130 clips; approved classifier50 labels; candidates55 other labels/1114 original sources,891 publisher train and223 publisher test. These are publisher-label OOV candidates, not idle annotations, signer identities, expert validation or an established fresh holdout.
Runtime: existing `~/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python`, CPU TensorFlow2.19.0/Keras3.15.1, MediaPipe1.2.0, NumPy2.1.3, existing OpenCV. No installs or environment/provider changes. TMPDIR is `~/.hermes/cache/scratch`.

## Fixed constraints

- Preserve all pre-existing source, test, model, dataset, contract and receipt bytes. Parent alone may update current scope/status documents outside the worker protection receipt.
- No classifier optimization, moment calibration, architecture/feature/output change,51st/idle class, relabeling or serving activation. Existing policy stays unchanged; a new companion is a separate artifact with `live_ready=false` even if offline targets pass.
- No real-source video/array/model execution by implementer. Synthetic tests only. Parent performs actual source audit, pilot, extraction, scoring and acceptance after independent complete review.
- No camera/GUI/phone/SDK/app, recording, participant processing, paid resources, Git write, package or provider changes.
- No synthetic output may qualify as real/public-source evidence. CLI real paths verify immutable owner/public-source/model/label/source identities; injected test backends remain explicit synthetic in-process only.
- Historical positive test stays exposed/exploratory. No threshold ranking, tuning or source selection based on challenge predictions. Expert/new-signer/true idle evidence is unavailable and must remain unmeasured, not zero.
- Approved offline constraints: false acceptance <=1/20 among eligible publisher-labeled OOV calibration sources AND correct accepted known validation >=9/10 among145 eligible known validation sources overall. Exact integer count comparisons, not rounded rates. Report each known/OOV class and declared/eligible/excluded denominators. Existing live per-gesture targets are not replaced.

## Cohesive file ownership

Create ONLY:
1. `training/holistic_migration/oov_dataset.py` — source audit/protocol reader, isolated streamed negative extraction and bounded bundle consumer/CLI.
2. `training/holistic_migration/rejection.py` — pure NumPy Float32 probability admission, deterministic threshold selection, decision/metrics helpers.
3. `training/holistic_migration/rejection_run.py` — frozen model/known-evidence bindings, calibration/freeze, separately gated challenge command and saved-output reporting/readback.
4. `training/holistic_migration/tests/test_oov_dataset.py`.
5. `training/holistic_migration/tests/test_rejection.py`.
6. `training/holistic_migration/tests/test_rejection_run.py`.
7. `training/holistic_migration/REJECTION.md` — exact commands, schema, actual failure/measurement limits and future parent recipe.
8. `docs/holistic-migration/rejection-calibration-report.md` — incremental implementation/TDD/verification report.

Own focused synthetic evidence only below stage `worker/`. Keep retained evidence <=256MiB; do not copy old evidence trees or actual datasets/models. Use small synthetic fixtures and remove only your own disposable successful scratch fixtures when required, retaining logs/XML/source bindings and focused counterexamples. Escalate if a protected edit or larger resource budget is necessary.

## Module and stage interfaces

This is one cohesive task; implementer owns all three modules and their documented schema together. Finalize exact JSON/dataclass definitions in `REJECTION.md`, retaining the following public CLI contracts so parent can execute without guessing:

```
python -E -B -m training.holistic_migration.oov_dataset prepare --source-audit PATH --authorization PATH --phase4-campaign PATH --output PATH
python -E -B -m training.holistic_migration.oov_dataset pilot --protocol PATH --output PATH
python -E -B -m training.holistic_migration.oov_dataset calibration --protocol PATH --output PATH
python -E -B -m training.holistic_migration.rejection_run calibrate --protocol PATH --negative-bundle PATH --output PATH
python -E -B -m training.holistic_migration.oov_dataset challenge --protocol PATH --calibration-run PATH --output PATH
python -E -B -m training.holistic_migration.rejection_run challenge --protocol PATH --calibration-run PATH --negative-bundle PATH --output PATH
```

Parent source audit is a separate accepted input, not an instruction to reuse selected50-only producers for unselected labels. It will publish `audit.json` plus hash-bound `rows.jsonl`: each of1114 records has `clip_id` (canonical archive member), `literal_source_token`, `original_id`, `label`, `category`, `official_split`, `partition` (`calibration` for publisher train, `challenge` for publisher test), `video_bytes`, `video_sha256`, `decoded_frames`, `decoded_bgr_sha256`, `shapes`, `status` and explicit failure fields where unavailable. Summary binds archive/CSV identities, rows digest, current decoder recipe/runtime, known50 byte/pixel audit references, exact duplicate groups and all891/223 source IDs. A priori deterministic byte/pixel dedup audit may inspect challenge pixels but not neural observations/scores; thereafter calibration readers may consume only calibration payloads. Source audit cannot itself admit classifier inference. Stop for cross-partition/known50 exact content duplicates or source-binding inconsistencies; do not silently re-split/drop groups. Keep decoder failures explicit in declared denominators.

`prepare` writes a fresh immutable protocol binding that audit, owner answers, exact50 labels, frozen model/selection/acceptance, detector bundle, shared/new implementation sources, runtime and fixed target rationals. Require source IDs/labels disjoint from the approved outputs, exact original membership and schema, no arbitrary caller-qualified provenance. No camera or model load. Recheck source/model/protocol bindings at consuming stages. Metadata-only challenge membership is permitted before freezing.

`pilot` uses exactly the lexicographically first publisher-train clip ID per OOV original label,55 original sources with no replacement/cherry-picking. It is explicitly diagnostic, never a complete negative calibration bundle. Parent verifies source/detector/feature/clock behavior and all failures before full calibration extraction.

`calibration` processes all891 declared publisher-train negatives, never challenge payloads. Reuse the actual HolisticDetector, ObservationClock, prepare_image and face_features.prepare_capture, not copied normalization/resampling. One detector per unrelated clip. Stream original BGR frames, compute full decoded audit hash (shape as little-endian int32 then contiguous BGR bytes), use finite actual presentation timestamps and the shared15Hz admission; resize unmirrored RGB640x360. Persist raw observations with the existing exact codec separately from derived Float32[30,1588]. Match audited source bytes/decoded counts/pixels/shapes before qualification; preserve original source IDs, publisher literal label and category, observation/timing/missingness/eligibility/failure details. Never invent hands/face, bridge gaps or assign dense classifier IDs to negative labels. Require all55 negative classes represented by at least one eligible source for complete all-class calibration qualification; retain partial results and clear failure otherwise. No hidden retries or replacement sources.

Bundles have exclusive start/incomplete/complete dispositions, source/implementation/runtime bindings, complete per-source ledgers, raw codec digests, derived tensor/ID arrays and explicit eligible/declared counts. Failed/incomplete artifacts cannot be qualified by residual completion files. No report repair repeats detector/model inference. New source/data outputs are fresh under this external stage; safe paths, symlink/root/traversal checks and strict schema/type/finite checks fail closed. Source decode/absence errors are distinct from classifier rejections.

`calibrate` consumes only the admitted complete calibration bundle and the frozen known-validation probabilities/IDs/labels (145 eligible/150 declared) bound to the accepted checkpoint. Saved known predictions can be reused with complete immutable digest/membership checks, not relabeled as new native inference. Native model inference, if needed, is only `model(X,training=False)` on new eligible OOV tensors, in bounded batches; no optimizer/training API. Verify actual50-output shape, probability dtype/finite/range/sum and masks/contracts first. Save OOV probabilities/IDs BEFORE report/sweep generation, with readback-only recovery. Do not open source challenge tensors/raw or prior positive-test probabilities during calibration.

Threshold is a single max-softmax confidence cutoff with `accept = max(p) >= Float32(threshold)`, lowest-index argmax exact ties. Preserve Float32 boundaries. Enumerate all validation-data decision boundaries plus a representable reject-all control; reject-all cannot pass the known-correct requirement. Among feasible candidates maximize known correct-accepted count, then minimize OOV accepted count, then choose the highest cutoff. Reject boolean/nonfinite/invalid probability and threshold values; prove exact boundary, ties, empty/missing support and infeasible behavior. No zero-denominator pass, arbitrary fallback threshold or undeclared extra margin/stability rule. Keep all measured candidate counts and the complete sweep.

If no feasible threshold exists, publish an explicit completed-infeasible report with saved scores, sweep, best trade-offs and all weak classes; publish NO qualifying policy/admission. Do not score/extract neural challenge observations, retrain or weaken criteria. Parent may independently verify infeasibility from saved validation outputs and close only the bounded failed experiment.

A feasible freeze binds Float32 threshold identity, target rational/counts, exact known/OOV validation membership/saved scores, classifier/labels/feature/detector/protocol/source/runtime and coverage to a new rejection companion. Strict ordinary decision readback must reproduce the counts before success. `live_ready=false`, idle safety/linguistic/signer/device/untouched-holdout claims remain false/unmeasured. Historical closed_set_argmax policy is never edited.

Both `challenge` commands must validate an affirmative feasible freeze BEFORE any neural challenge raw/tensor/model scoring work. Extraction handles exactly223 declared publisher-test negatives. Scoring exclusively reserves an assessment start before challenge inference, saves scores/IDs, then reports once. It may apply the fixed threshold to hash-bound historical203 known-positive saved outputs, explicitly exploratory reused evidence and never selection input. No reranking/tuning or automatic failed-target rerun. Completed targets offer validated saved-output readback only; failed/incomplete targets stay denied. Preserve a valid frozen policy if a later report fails, while denying an unsuccessful policy publication; use stage-specific affirmative qualification and explicit failure barriers rather than permissive existence checks.

Reports: known per-class precision/recall/F1/correct-accepted/rejected/incorrect-accepted/support, all-known macro-F1 and denominators; OOV per-publisher-class eligible/declared/accepted/rejected/source failures and false-accept rate; source versus classifier exclusion accounting; extended confusion including a rejection column without inventing a neural output; target disposition, provenance and all limits. Genuine idle/continuous false activations per minute are null without annotated exposure. No physical/device/live readiness claim from offline max-softmax evaluation. Full source/video error outcomes stay in ledgers; absence is not a fabricated prediction.

## Vertical TDD and verification steps

- [ ] First behavior slice: literal OOV/protocol admission, real/synthetic distinction and protected challenge access. Write/execute a meaningful failing assertion, implement only that slice, verify GREEN.
- [ ] Streamed extraction/capture/codec source parity, missingness, failure/cleanup and pilot-versus-full qualification: repeat separate RED/GREEN slices on compact synthetic videos/RawFrame outputs.
- [ ] Probability/Float32 threshold boundary and exact-count feasibility/tie/infeasible selection: separate RED/GREEN slices. Include e.g. known correct counts on10 positives and unknown accepts on20 negatives so one extra accept crosses1/20 and one fewer correct crosses9/10.
- [ ] Frozen model/source/membership guards, score publication/readback, feasible/infeasible consumers and challenge-before-start denial: separate RED/GREEN through the real public functions/CLI seams. Include residual failed-policy/failed-completion markers and healthy later-report-failure controls.
- [ ] Native synthetic-only50-output forward/save/reload/ordinary-inference decision parity if the orchestration introduces a backend adapter; never actual-source inference or optimizer steps. Keep API injection labeled synthetic and unavailable to real CLI provenance.
- [ ] Run affected suite, full migration pytest and original training pytest with exact existing interpreter, fresh owned basetemp/XML/logs and current source digests. Mixed unittest/function/subtest collection must be counted correctly; retain warnings, REDs and harness errors separately. Keep fixtures within retention budget. No broad source formatting or original-test edits.

Example commands (fresh output paths under stage worker):
```
~/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests/test_oov_dataset.py training/holistic_migration/tests/test_rejection.py training/holistic_migration/tests/test_rejection_run.py -q --junitxml=PATH
~/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/holistic_migration/tests -q --junitxml=PATH
~/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest training/tests -q --junitxml=PATH
```

OUTPUT: eight owned files, incremental report, exact delivered path/hash operations, commands/exits/collected cases/subtests/warnings, behavioral stage records and retained evidence inventory. Read-only independent complete specification AND quality review precedes any parent real extraction/calibration. Parent retains all final gates and no automatic third repair is authorized. Return DONE/DONE_WITH_CONCERNS/BLOCKED, report path, concise test summary and concerns. Do not start real data work or close the task yourself.
