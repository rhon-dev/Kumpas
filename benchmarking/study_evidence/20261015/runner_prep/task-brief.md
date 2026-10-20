# Task brief — SPEC-R1

AGENT: Model/QA. PHASE: host09 preparation, not training approval.
OBJECTIVE: additive isolated bounded-runner preparation with fake-only execution contracts.
INPUT: PRD, phase-gates, approved design §C and plan Package B, controller/final-host-{spec,quality}-review-1.md; historical evaluation_protocol.py/freeze_selection.py read-only.
CONSTRAINTS: only new training/models/experiment_runner.py, training/tests/test_experiment_runner.py and runner_prep evidence; no protected source/output, default stores, raw arrays, actual training/conversion/inference, deployment, network/install/device or Git mutations.
ACCEPTANCE: behavioral RED→GREEN slices; strict explicit proposed config/bindings; external exclusive roots; sequential bounded fake execution, safe failure/cancel/timeout states; immutable snapshots and final hash readback; CLI prepare/dry-run synthetic only and real execution rejection; focused/full training suites with existing ~/.kumpas-venvs/tf/bin/python -B -E; preservation readback. Parent review required.
OUTPUT: this evidence directory and the two new additive Python files.
