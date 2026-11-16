# Task A — shared Holistic feature/detector foundation

AGENT: Data/Preprocessing and host QA implementer.
PHASE: Holistic migration foundation only.
OBJECTIVE: Implement and exercise the exact candidate contract in `docs/holistic-migration/FEATURES.md` through a new additive Python package.
INPUT: Read that contract first, then `AGENTS.md`, `docs/PRD.md`, `training/preprocessing/{extract_landmarks.py,build_sequences.py,selected_classes.json}`. The owner explicitly approved a new isolated Mac-only migration, including new code; historical PRD phase approvals are not newly closed. Preserve the old pipeline.

## File ownership

Create only:
- `training/holistic_migration/__init__.py`
- `training/holistic_migration/features.py`
- `training/holistic_migration/detector.py`
- `training/holistic_migration/tests/__init__.py`
- `training/holistic_migration/tests/test_features.py`
- `training/holistic_migration/tests/test_detector.py`
- Your report `docs/holistic-migration/task-a-report.md` (create early and append real RED/GREEN commands/results per slice).

No other source, plan, requirements, environment, existing test, or instruction-file writes. No commits/pushes. No camera, dataset extraction, training, phone/app operations, downloads, dependency installs, old history changes, or recognition-v2 worktree access.

## Interfaces

Use a frozen dataclass `RawFrame(timestamp_ms: int, pose: np.ndarray | None, left_hand: np.ndarray | None, right_hand: np.ndarray | None, face: np.ndarray | None = None)`.
- `pack_frame(frame: RawFrame) -> np.ndarray`: exact 153-vector and rules from FEATURES.md. Invalid shoulder/pose observations return a zero vector; malformed shape/types/nonfinite arrays raise ValueError. Raw timestamp must be a nonnegative built-in int, excluding bool. Return Float32; do not mutate input arrays.
- `resample_frames(frames: Sequence[RawFrame], steps: int = 30) -> np.ndarray`: pack through that same function; require >=2 observations and all usable-pose masks, monotonic timestamps, steps>=2 exact int. Nearest time sampling with earlier-frame ties. Return `(steps,153)` Float32. Do not remove invalid observations or bridge gaps. No imports of MediaPipe/TensorFlow in features.py.
- `HolisticDetector(model_path: Path)`: lazy import MediaPipe only at construction, explicit Tasks Holistic VIDEO/CPU options with optional face blendshapes/segmentation disabled, context manager/close ownership, `detect(rgb: np.ndarray, timestamp_ms: int) -> RawFrame`. Validate RGB shape/uint8 and timestamp before native calls. Validate strictly increasing timestamps per instance. Reset by creating new instances, never share across unrelated clips.
- A side-effect-free conversion helper `frame_from_result(result, timestamp_ms) -> RawFrame` reads normalized image landmarks from actual SDK-shaped objects. Require pose 33, hands21 if present; face count is variable but Nx3. Preserve observed XYZ and pose visibility, do not confuse world outputs. Empty lists become None. Optional visibility missing/None must fail closed for pose confidence (zero), not fabricate visibility1.

## Verification and report

Follow strict TDD vertical slices: write one behavior test, run RED, implement minimal code, run GREEN, then next behavior. Use existing Python:
`~/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m unittest discover -s training/holistic_migration/tests -v`
Set TMPDIR to `/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch`; disable bytecode/cache writes. Do not install dependencies.

Test every behavior enumerated in FEATURES.md, including missing left while right present and converse, depth-origin separation, no mutation, nonfinite results after normalization, all-idle, exact malformed counts, and temporal preservation of missing hands. Test conversion with SDK-shaped result fixtures, detector preflight without constructing native runtime on invalid CLI/API inputs, and exception-safe context cleanup. Do not claim fixtures establish SDK runtime or anatomical correctness.

The available MediaPipe version is 1.2.0; its decoder is ctypes-based, not the old `_build_landmarker_result` packet function. Inspect installed signatures if needed. Do not patch installed packages or add old-version private adapters.

Return only status, modified-file paths, real RED/GREEN/final test summary, report path and concerns. All other details belong in your report.
