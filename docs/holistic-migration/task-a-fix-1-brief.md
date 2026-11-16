# Task A fix 1 — semantic NumPy subclasses

AGENT: bounded regression-first fixer.
OBJECTIVE: Fix only independent review L01/REQ-A-INPUT-INTEGRITY. Parent independently reproduced all three defects. No new feature work or preview/data/training work.

Read requirements `docs/holistic-migration/task-a-brief.md`, the current `FEATURES.md`, review `task-a-review-1.json`, and the two actual production modules. Do not re-audit the repository or reconstruct previous TDD history.

## Required behavior

`pack_frame` accepts only exact plain `np.ndarray` component arrays (or explicit None), not semantic subclasses. Reject MaskedArray, matrix and other ndarray subclasses with a component-specific ValueError before any validation/normalization that could hide missingness or return the subclass. Do not coerce masked arrays to plain arrays, discard a mask, fabricate coordinates, or loosen finite checks. Plain noncontiguous/read-only ndarray views, ordinary numeric dtypes and current valid SDK conversion remain supported.

Three demonstrated failures: a partially masked hand becomes unnormalized but marked present; a masked NaN at an unselected pose point bypasses finiteness; matrix pose raises incidental IndexError. Add a single cohesive type-boundary regression slice covering these cases and component positions, run real RED before the minimal guard change, then GREEN. Include a subclass with overridden array semantics to ensure the guard runs first; plain arrays/views remain positive controls.

## File ownership

Modify only `training/holistic_migration/features.py`, `tests/test_features.py`, and optionally remove the unused `importlib` from `tests/test_detector.py`. Append actual commands, exits and results to `docs/holistic-migration/task-a-report.md`. Do not change the detector, other code, docs, requirements or old tests. Parent owns FEATURES.md and reviews.

Previous source/report/spec/review bytes were preserved and read-back hash-verified BEFORE mutation at:
`/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-a-before-fix-3ecdfe36991c4588bf3ce732470c4ea2/snapshot-index.json`.
Reference this mapping in the report; preserve earlier evidence as historical, never claim the old hash covers repaired code.

## Verification

Use `TMPDIR=/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch ~/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest discover -s training/holistic_migration/tests -v` for RED/GREEN and final package discovery. Do not install anything, open model/camera/data files, commit, or change the original cloud checkout/recognition-v2 worktree. Keep this a small bounded fix, not a new development phase.

Return short status, changed paths, actual regression/final counts and report path. Parent will freeze a fresh review package and obtain re-review before Task B.