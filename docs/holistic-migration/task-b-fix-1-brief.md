# Task B fix1 — terminal reconciliation and partial thread rollback

## Execution ordering and scope

This is a queued bounded repair, not current Task B acceptance. Dispatch only after the sole Task C implementer has delivered its immutable-baseline handoff; do not run two source implementers concurrently or change Task C's11 protected baseline files mid-task. Task C is independent accepted-Task-A offline work explicitly authorized while the owner defers the human webcam check. Its captured delivery/protection receipts must remain historical after this later authorized repair.

Work in `~/KumpasBuilds/holistic-migration` on `holistic-migration`. No commits, pushes, installs, provider changes, model fitting, camera/GUI launch, phone/app work or participant processing. No live camera retry: owner explicitly said webcam check later.

Own only:
- `training/holistic_migration/camera.py`
- `training/holistic_migration/webcam.py`
- `training/holistic_migration/tests/test_camera.py`
- `training/holistic_migration/tests/test_webcam.py`
- Append-only `docs/holistic-migration/task-b-report.md`.

Preserve camera.swift, all six accepted Task A files, all Task C files, original source/data/class maps and historical evidence. Read the original task-b-preview-brief.md and complete task-b-review-1.json; no unrelated refactoring or features.

## Reviewed defect map

Both specification and quality verdicts are false; no security findings or optional suggestions were listed. Parent matched all five reviewed Task B postimages before reproducing.

- **L01/MR01:** reader fatal framing/EOF/timeout failure can occur while detector/packing/display handles the current frame. q/Escape, window close or the loop deadline can then terminate before another next_frame call, leaving a normal terminal and successful return despite the already-recorded source failure. Existing native_exit/stderr retention does not fix final disposition.
- **L02:** Thread objects are assigned before start succeeds. Constructor rollback calls close, which joins a never-started thread; its RuntimeError interrupts both pipe closes and replaces the acquisition error. The owned child was reaped in reproductions; do not invent a surviving-child claim.

## Immutable preimages and independently executed RED

Snapshot mapping (original path, retained exact bytes and digest):
`~/KumpasBuilds/holistic-migration-data/evidence/task-b-before-fix-8830ecffa4174cd98b6ecc4c7b1c3ea0/snapshot-index.json`.

It preserves the five source/test files plus the original report, brief, review and parent live note. The report's old reviewed hash must remain recoverable before appending repair evidence.

Parent's corrected synthetic behavioral harness:
`~/KumpasBuilds/holistic-migration-data/evidence/task-b-before-fix-8830ecffa4174cd98b6ecc4c7b1c3ea0/parent_fault_regressions.py`.

Execute from repository root with verified Python `-E -B`, TMPDIR `~/.hermes/cache/scratch`. Actual corrected RED:6tests,5failures,0errors,exit1,0.296seconds. Receipt:
`parent-regression-runs/35a12c77d90743e9b72d645e8517294e/observations.json`; full log `parent-red-corrected.log` in the same snapshot root.

The actual production OwnedCapture reader/queue/next_frame/close and run_preview were exercised with a synthetic Python binary-pipe child, inert GUI methods, synthetic detector and true owned resource cleanup. No real camera, model or GUI was opened. All three source-failure cases emitted one frame, then child exit7 and captured EOFError; quit/window_closed/deadline still returned normally. Both thread-start cases reaped the child but left stdout/stderr open and masked the primary with `cannot join thread before it is started`. Healthy quit processed one frame, had no reader error, used deliberate SIGTERM(-15) and closed all resources normally.

An initial parent harness had a scheduling race: q could occur before the injected detector failure. Its original script, log and receipt are preserved in initial-probe-preservation.json; that quit case is explicitly not counted as a product reproduction. The corrected harness synchronizes pending-frame admission and asserts one processed frame plus exit7/EOF before evaluating the terminal outcome. Do not rewrite this history.

## Required repair behavior

### Slice1 — terminal/source failure

Add behavioral regressions to the owned test files before production edits and execute their actual RED against the current code. Use the production pipe path and deterministic synchronization for source failure during processing followed by q/Escape, window close and deadline, plus a healthy-quit control. Do not manufacture clock or scheduling failures in place of the source defect.

Reconcile an observed capture failure or unexpected native exit that happened before owned shutdown with the final outcome. A normal terminal/CLI return cannot mask a fatal source failure. Preserve the original source diagnostic and stderr/exit, and still close capture/detector/window. Distinguish deliberate termination/kill of a healthy owned child from unexpected source failure; do not mark healthy quit/deadline as failed solely because cleanup signals the child. Preserve earlier primary exceptions instead of overwriting them with a secondary failure. Add a focused unexpected-child-exit case even when the reader has not yet published its error. Keep operational report error fields fixed/structured, not arbitrary recognized strings.

### Slice2 — constructor/teardown acquisition

Execute separate thread-start faults for owned-camera-stderr and owned-camera-frames through the production constructor. Preserve the original acquisition error directly or as the explicit cause; never replace it with an unstarted join error. Track/recognize successful thread acquisition, attempt every owned pipe close even if a join or earlier teardown step fails, and retain bounded cleanup of only the owned child.

A partially failed close must not become permanently unrepairable merely because _closed was set before cleanup. Cover retry of incomplete teardown and a join/pipe fault where later owned cleanup is still attempted. Keep idempotent successful close and ownership boundaries. Do not suppress errors merely to make tests pass.

## Verification and handoff

For each vertical slice append actual RED/GREEN commands, exits and results immediately to the original report, linking the immutable pre-report snapshot. Label coverage-only GREEN honestly when later variants already pass after a common fix. Do not rewrite earlier evidence as if it tested new source.

Run named camera/webcam tests, the parent's corrected six-case harness in a fresh run directory, and the full migration/original suites after the fix. Task C now includes pytest function tests; unittest discovery alone omits them. Required full commands from repository root:

```sh
export TMPDIR="$HOME/.hermes/cache/scratch"
PY="$HOME/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python"
"$PY" -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests -v
"$PY" -E -B -m pytest -p no:cacheprovider training/tests -v
```

Current protection receipt after parent-verified C delivery:
`~/KumpasBuilds/holistic-migration-data/evidence/task-c-review-17292f00faaf47d2b96d74d43b8d3a7b/task-b-fix-protection.json`.
It binds20 preserved C/Task A/native Swift/contract paths. Parent independently verified the C delivery at186 migration tests and51 original tests, before this later B repair; retain that historical boundary rather than rewriting C's11-file handoff guard to match new B bytes.

Retain actual failures, logs and source hashes; do not weaken tests or skip current Task C tests. Recheck the current protected bytes before/after. No real camera/GUI exercise is needed for this repair and no human acceptance is authorized.

Return exact changed files, actual executed assertions/counts, report path and remaining concerns. Parent will package the complete corrected Task B scope and obtain independent affected-scope re-review before acceptance. The earlier empty-detection camera session remains bounded historical evidence under its original source identity, not a physical acceptance of repaired code.
