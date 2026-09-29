# Leakage-safe Evaluation Protocol Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Separate original-clip validation before fit-only augmentation, select models without reading the test set, and report the reused test split honestly.

**Architecture:** A deterministic manifest maps original training array indices and clip names into fit/validation; a builder produces protocol-specific arrays and augmentation provenance; training records validation-only runs; a freeze record selects a run, after which a standalone exploratory test command scores it. Existing arrays and historic logs remain immutable.

**Tech Stack:** Python, NumPy, TensorFlow/Keras for training, scikit-learn for report metrics; unittest for fast tests.

## Global Constraints

- Existing 813/203 train/test source split is unchanged; no additional clips available.
- Original 95.07% report is historical/exploratory; reused 203-clip test cannot be pristine.
- Seed 20260705, nominal 20% validation per class, minimum two originals per class.
- No app/model deployment, no fabricated signer identity, no edits to existing arrays or historic run records.
- Work on the current branch; leave unrelated changes in README.md and benchmarking/ untouched.

---

### Task 1: Original-clip manifest and fit-only augmented arrays

**Files:** Create `training/models/evaluation_protocol.py`; modify `training/augmentation/augment_landmarks.py` only to expose an importable fit-only augmentation helper without changing its historical CLI; test `training/tests/test_evaluation_protocol.py`.

**Interfaces:** `build_manifest(seq_dir: Path, seed: int=20260705, fraction: float=.2)->dict`; `validate_manifest(manifest: dict, seq_dir: Path)->None`; `build_protocol(seq_dir: Path, out_dir: Path, seed: int=20260705, factor: int=3)->dict`. Manifest entries contain `index`, `clip`, `class_id`, `partition` and source digests. `augment_fit(X, y, names, factor, seed)` returns arrays and provenance.

- [ ] Write a failing unittest that creates class-balanced tiny arrays and checks deterministic partition, no source overlap, all fit/validation labels present, and that only fit originals are augmented.
```python
m = build_manifest(source, seed=20260705)
a = build_protocol(source, output, factor=1)
assert {r['clip'] for r in m['rows'] if r['partition']=='fit'}.isdisjoint({r['clip'] for r in m['rows'] if r['partition']=='validation'})
assert len(a['augmentations']) == a['n_fit_original']
```
- [ ] Run `training/.venv/bin/python -m unittest discover -s training/tests -v` and confirm red from missing API.
- [ ] Implement the splitter/manifest and builder; verify hashes, array/name lengths, duplicate clip names, label integrity, original train/test clip-name overlap, impossible class support. Preserve old arrays; write only new protocol directory and transformation log.
```python
rows = [{'index': i, 'clip': names[i], 'class_id': int(y[i]), 'partition': part[i]} for i in range(len(names))]
X_fit = X[[r['index'] for r in rows if r['partition']=='fit']]
X_val = X[[r['index'] for r in rows if r['partition']=='validation']]
```
- [ ] Run targeted tests green; add red/green tests for changed source digest and inconsistent/duplicate names; run entire training suite.
- [ ] Commit only task files with `git add training/models/evaluation_protocol.py training/augmentation/augment_landmarks.py training/tests/test_evaluation_protocol.py && git commit -m 'feat: create leakage-safe clip partitions'`.

### Task 2: Validation-only training and frozen run selection

**Files:** Modify `training/models/train_cnn_lstm.py`; create `training/models/freeze_selection.py`; test `training/tests/test_training_protocol.py`.

**Interfaces:** training `load_protocol_data(protocol_dir: Path, drop_face: bool)` returns fit, validation, labels and manifest. New run records include `protocol_id`, hashes, validation score and checkpoint; no test score. `freeze_selection(log_path: Path, protocol_dir: Path, output_path: Path)->dict` chooses best validation accuracy (tie-break macro-F1 then run ID) and verifies checkpoint/hash matches.

- [ ] Test that `load_protocol_data` returns explicit unaugmented validation and fails when manifest hash differs, and that selection ignores a historic higher test score.
```python
fit, val, labels, manifest = load_protocol_data(protocol, drop_face=False)
assert len(val[0]) == manifest['n_validation']
record = freeze_selection(log, protocol, frozen)
assert record['run_id'] == 'higher_validation_run'
```
- [ ] Run targeted unittest red; change `model.fit(... validation_data=(X_val,y_val) ...)`; remove all test reads and predictions from training, write new protocol experiment log and checkpoint outside repo.
- [ ] Run targeted tests green and entire training suite; compile Python files; commit only task files.

### Task 3: Explicit exploratory test reporting

**Files:** Modify `training/models/eval_report.py`; create `training/models/evaluate_frozen.py`; test `training/tests/test_evaluate_frozen.py`.

**Interfaces:** `evaluate_frozen(freeze_path: Path, protocol_dir: Path, test_dir: Path, report_dir: Path)->dict` checks checkpoint/manifest/source hashes, runs predictions once, computes accuracy, macro metrics, class support, and clip-level Wilson interval with independence caveat. Legacy `eval_report.py` demands `--run-id` and never chooses by `test_accuracy`.

- [ ] Test missing/contradictory freeze refusal and absence of default max-test-selection; test report is labeled historical test reuse.
```python
assert 'exploratory' in render_report({'correct': 193, 'n': 203}).lower()
with self.assertRaises(ValueError):
    evaluate_frozen(bad_freeze, protocol, source, reports)
```
- [ ] Run targeted unittest red; implement standalone evaluation with explicit frozen run and no auto-best-by-test logic; rerun green and full suite; commit task files.

### Task 4: Signer provenance, docs, real-data smoke test

**Files:** Create `docs/signer-leakage-check.md`; modify `docs/phase-gates.md` and historic `training/models/reports/20260705_194813_no_face_eval.md`. Do not modify README.md with pre-existing edits; report the required README copy separately or amend it only after the user's conflicting edits are reconciled.

- [ ] Document exact CSV columns/index overlap, note unknown identity and accuracy scope; label historic validation as sibling-contaminated and 95.07% as reused exploratory test. Do not claim creator-provided IDs.
- [ ] Run `training/.venv/bin/python -m unittest discover -s training/tests -v` plus `training/.venv/bin/python -m compileall -q training/models training/augmentation`; run protocol builder on real source arrays into `../kumpas-data/sequences/evaluation_v1` and programmatically check counts, disjoint origins, unchanged historic array hashes; no retrain.
- [ ] Review `git diff --check`, inspect exact modified files, commit only docs (excluding README) and tests. Report both verified pipeline behavior and unperformed full retraining/external evaluation.
