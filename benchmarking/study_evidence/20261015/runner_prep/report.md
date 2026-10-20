# SPEC-R1 isolated experiment runner preparation

Status: implemented and self-verified for synthetic preparation only; independent parent verification/specification/quality review and any D2 acceptance remain pending.

Scope: approved host09 preparation only. Actual training, conversion, inference, test-row consultation, promotion and deployment are not authorized. All executed runner scenarios must be synthetic. No historical source or frozen D evidence is to change.

Design constraints: strict versioned proposed configuration, validation-only original-clip grouping and historical validation accuracy/macro-F1/run-ID ordering. Explicit supplied variant and budget values are proposals, not approved training parameters. Production backend is deliberately absent and rejects with TRAINING_NOT_AUTHORIZED. Trusted programmatic callbacks are not an OS sandbox and cannot be forcibly preempted; deterministic synthetic clock/deadline contract only. CLI never accepts arbitrary executables or real execution.

Evidence is appended below after actual execution. Parent owns independent verification, review and any subsequent D2 re-freeze/status reconciliation.

## Executed incremental evidence

- Initial preservation readback: 82 protected originals, 69 accepted source files, 279 D source files and 206 D evidence files all matched. `preservation-before.json`.
- Schema slice: `red-schema.log`, exit1, 1 method with13 expected behavioral failures (permissive scaffold accepted forbidden values); `green-schema.log`, exit0, 1 method. This is not an import-absence RED.
- Preparation slice: `red-prepare.log`, exit1, 3 methods/13 behavioral failures; `green-prepare.log`, exit0, all4 current methods passed. Exclusive scratch roots, immutable detached snapshot and metadata-bound original-clip validation covered.
- Synthetic execution slice: `red-execution.log`, exit1, 8 methods/14 behavioral failures; `green-execution.log`, exit0, 8 methods passed. Deterministic fake clock/backend: sequential ordering/ties, timeout/total-budget/failure/interrupt/cancel, invalid finite/range/type/extra metrics, forbidden writer-interface attempt, changed inputs and tampered output.
- CLI slice: `red-cli.log`, exit1, 2 behavioral failures; `green-cli.log`, exit0, 10 methods passed. `prepare`/`dry-run` publish real synthetic artifacts; `execute`/`train` and arbitrary command requests fail without invoking a backend. These tests exercise CLI main; separate actual process evidence follows.

The nonfunctional API scaffolds returned no result/permissively accepted input before each slice; actual assertions failed, not missing imports. No real executor or shell facility was implemented. Values in synthetic fixtures (including tiny budgets and variant values) are explicitly supplied proposals used only to test contracts, not approved training settings.

## Additional regression-first hardening

- `red-final-integrity.log`:2 actual failures demonstrated a success receipt remaining after final readback failure and arbitrary internal stop text being persisted. The final-readback test was moved to the actual verification seam and rerun: `red-final-readback-rebound.log`,1 actual failure. `green-final-integrity.log`:12 methods passed. Publication now rolls back only its exclusively created inode on failure and retains the execution marker/earlier logs. Stop reasons use a fixed vocabulary.
- `red-protocol-grouping.log`:2 actual subtest failures demonstrated acceptance of too few original clips and a changed validation fraction with the full protocol→freeze hash graph rebound. `green-protocol-grouping.log`:13 methods passed. Enforce evaluation-v1 seed20260705, fraction0.2, minimum3 originals/class and the protected algorithm's per-class validation-count formula; require ordered original validation clip IDs and no duplicate original across partitions. The synthetic fixture now has1 fit +2 validation originals. Existing malformed-protocol tests were strengthened to rebind the freeze graph too; their original GREEN alone did not independently prove the metadata schema.
- `red-model-contract.log`:1 behavioral failure for rejection of the explicit model/structured-label preparation. `green-model-contract.log`:1 passed. Require the unchanged declared no-face CNN-LSTM contract (30×258, conv64/128, LSTM128/64, dense128) from the historical selected baseline; exact integer types, structured label IDs/labels/categories. These are declarations bound to inputs, not loaded-model or architecture attestations.
- `red-output-interface.log`:2 behavioral failures showed the generic publication helper reaching a writer for forbidden paths. The writer was intercepted: **no repository/forbidden write occurred**. Production publication now refuses out-of-scratch targets and any filenames other than fixed manifests/receipts or sanitized per-variant JSON logs. The final focused run passed this regression.
- Seven subsequent test methods were coverage-only GREEN, not newly repaired defects: all budget-field exact-type matrix; every binding role plus symlink/array refusal; accuracy then F1 selection precedence; pre-start cancellation and invalid clock/cancel signal; manifest/log-symlink tampering; existing-output and fsync failure; duplicate/nonfinite JSON.

## Final executed verification

Existing interpreter: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/tf/bin/python -B -E`; scratch TMPDIR; no installs.

| Actual command scope | Result | Evidence |
|---|---|---|
|`-m unittest training.tests.test_experiment_runner -v`|22 passed;0 failures/errors/skips;exit0|`focused-final.log`,0.235s|
|`-m unittest discover -s training/tests -p 'test_*.py' -v`|51 passed;0 failures/errors/skips;exit0|`full.log`,8.560s|
|Initial and final preservation|82 protected +69 accepted +279 D sources +206 D evidence;zero mismatches|`preservation-{before,after}.json`|
|`git diff --check`|exit0|Actual terminal execution; no tracked edits made by this task|

The51 full-suite methods include the22 new methods; do not add them as73 distinct tests. Existing full-suite tests performed isolated synthetic model construction/conversion/interpreter checks, with retained TensorFlow/Keras deprecation/startup warnings. No real checkpoint conversion, candidate inference, training or test-row consultation was performed.

### Actual process CLI evidence

`capture-cli.py` executed9 separate real CLI processes using retained synthetic input files, not mocked subprocess output. Exact commands/exits/output hashes are in `command-ledger.jsonl` and `cli-evidence.json`; stdout/stderr are retained separately. All stderr files are empty. External root:

`/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/kumpas-runner-prep-cli-o_abp3g8`

| Process label | Exit | Checked result |
|---|---:|---|
|cli-prepare|0|PREPARED;new manifest/log directory|
|cli-demo|0|SYNTHETIC_COMPLETE;2 sequential fake variants;virtual time;synthetic selection only|
|cli-timeout|1|TIMEOUT;no selected run;success=false;remaining variant NOT_STARTED|
|cli-invalid|2|INVALID_REQUEST;test-partition selection rejected;no output root|
|cli-authflag|3|TRAINING_NOT_AUTHORIZED;true flag rejected;no output root|
|cli-execute|3|TRAINING_NOT_AUTHORIZED;no backend invocation|
|cli-train|3|TRAINING_NOT_AUTHORIZED;no backend invocation|
|cli-command-refusal|3|TRAINING_NOT_AUTHORIZED;arbitrary command token not executed or echoed|
|cli-no-overwrite|2|INVALID_REQUEST;prior preparation manifest hash unchanged|

All18 external synthetic files (5 input identities + retained preparation/demo/timeout manifests/logs/receipts) are hash-bound and read back. The five `cli-*-config.json` files are versioned explicit fixture proposals; `cli-invalid-config.json` and `cli-authflag-config.json` are intentional rejection fixtures, not usable training configurations. Output targets already exist after capture: replaying the same prepare/dry-run configuration must reject, not overwrite. To reproduce successful publication, generate a new exclusive synthetic root/config via the reviewed fixture recipe; do not edit the captured configuration.

## Interface and limitations

- Public preparation: `prepare(config) -> Prepared` with frozen dataclass, immutable configuration bytes, manifest digest and root inode identity. No caller-owned mutable dict remains authoritative. Public fake execution: `run_synthetic(prepared, trusted_executor, clock, cancelled)`; request fields are immutable, expose no output paths/writers/commands, and callbacks return only strict synthetic validation signals. Historical selection method text is preserved exactly. Test scores, probabilities as human scores, unknown config/metric keys and nonfinite/bool metric values are rejected.
- CLI syntax: `experiment_runner.py {prepare|dry-run} --config /absolute/config.json`. It never imports an executor or accepts a shell/command/module hook. `execute_training(...)`, `execute` and `train` always reject with fixed TRAINING_NOT_AUTHORIZED. Configuration preparation cannot grant training approval. No latest-checkpoint search, silent retry, automatic promotion, deployment or test ranking exists.
- Output roots are intentionally narrower than general external paths: fresh descendants of `~/.hermes/cache/scratch`, with an existing parent. Existing targets, lexical traversal, symlink ancestors/inputs/log roots, repository/application/model/history/default-store destinations and unsupported artifact names are refused. This directory is temporary host evidence, not permanent storage; scratch retention/pruning remains a parent handoff concern.
- Bounded execution is **cooperative synthetic contract execution**, not a production wall-clock process supervisor. A trusted callback can access Python globals/filesystem directly or block forever; the helper does not sandbox arbitrary Python or forcibly kill callbacks. Deadlines/cancel are checked before/after and at callback checkpoints, sequentially, with no concurrent variants/retries. Do not enable real training by plugging an arbitrary executor into this seam; a separately approved production design/backend would need its own resource/process controls and review.
- Metadata-only protocol validation deliberately does not call protected validators that open original arrays/test metadata. It verifies exact declared schemas, grouping/count semantics, label ordering, freeze/protocol digests and input bytes; it does **not** regenerate the seeded stratified allocation, prove original-row array equality, inspect test rows, deserialize a model, attest historical checkpoint→candidate lineage or independently verify label/expert provenance. It never follows the freeze checkpoint pathname or protocol source-array hash paths. The source/candidate fixture identities are synthetic placeholders; the actual runner source is independently bound in each manifest.
- JSON uses fixed safe errors and strict serialization. Input reads reject arrays, symlinks and macOS DATALESS flags before content reads; bounded metadata/identity inputs are capped at8MiB, a tooling guard rather than an approved training resource budget. Filesystem integrity is local/trusted and readback-based, not hostile concurrent-writer or power-loss durability. On publication fault, owned-inode cleanup is attempted; an unremovable or concurrently replaced artifact is not certified as success. Input/output/source changes detected during checks fail closed; no guarantee covers undetectable change-and-restore or post-return modification.

## Handoff identity and disposition

- New production helper: `training/models/experiment_runner.py`, SHA256 `a2d7df7d8616976358eb5a9cafd11e9de3b434a0213878e7659c805945598dbd`.
- New tests: `training/tests/test_experiment_runner.py`, SHA256 `f3755d35eebf885561751cbeea05d2accf31800a7cc2a107ef3bcb1396792ee3`.
- Focused log SHA256 `480609c892a6a4e4c41e9c4bc4f6f149ab336729aab6572279f0be001586178d`; full-suite log SHA256 `32ad938c4b31bf2e5871deac4b951526d2f72355f686051480f048e9c794405e`.
- `source-freeze.json`, `evidence-freeze.json` and `verification.json` provide the final machine-readable new-file inventory/readback. No protected or accepted source, frozen D source/document/evidence, application/native/benchmark/evaluation implementation, historical training protocol/log/model/source or governed status document was edited. No Git mutations, downloads, devices, default stores, cloud hydration or actual experiments occurred.

**Host09 preparation is eligible for independent review only. Actual training remains BLOCKED.** This worker does not close SPEC-R1 by self-acceptance, refresh the whole package, rewrite historical D reports, claim all16 complete or close scientific/physical/participant gates. Parent must independently verify this additive slice, obtain specification/quality review and then prepare a separate D2 re-freeze/status decision if warranted. Q1 is unrelated and unchanged; supported replay discovery was already documented.
