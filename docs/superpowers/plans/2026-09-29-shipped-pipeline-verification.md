# Shipped Pipeline Verification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Build an offline paired-frame parity harness and a live camera-to-feedback latency trace whose real-device measurements can be run later; make anatomical handedness an explicit unverified gate.

**Architecture:** Python prepares deterministic, hashed PNG replay sets and reference Holistic vectors; Android instrumented code replays the PNGs through the live extractor and writes features/predictions. A host script compares paired data. Native timing is stamped along the existing analyzer→VisionEngine→event-sink path and collected only from a real device.

**Tech Stack:** Python 3.11/NumPy/OpenCV/MediaPipe; Kotlin, MediaPipe Tasks, CameraX, TFLite, Android instrumented tests, unittest/JUnit.

## Global Constraints

- Do not alter app model, features or hand mapping merely to make tests pass.
- Store media and frame-level biometric vectors outside git, under `../kumpas-data/parity/` or app-specific storage.
- No physical phone or Android SDK now. Never invent on-device results; leave anatomical left/right unverified.
- Work on current branch, preserve unrelated worktree edits including README/benchmark_history and the prior evaluation task.

---

### Task 1: Deterministic paired-frame manifest and comparator

**Files:** Create `benchmarking/pipeline_parity.py`, `benchmarking/test_pipeline_parity.py`.

**Interfaces:** `extract_frames(video, output, indices)->manifest`, `compare_vectors(python_json, android_json)->report` with frame SHA and signed block mismatch metrics. A CLI offers `prepare` and `compare` without touching the repository's existing benchmark history.

- [ ] Write failing tests for deterministic frame naming/digests, dimension checks, frame/hash alignment, block MAE and detection mismatch.
```python
report = compare_vectors(py, android)
assert report['matched_frames'] == 2
assert report['anatomical_left_right'] == 'unverified'
```
- [ ] Run `training/.venv/bin/python -m unittest benchmarking/test_pipeline_parity.py -v` and observe missing import/API.
- [ ] Implement frame export and comparator; test green. Run a real FSL-105 clip through frame preparation and verify output hashes. Commit files only after green.

### Task 2: Python Holistic reference and pure normalization parity

**Files:** Extend `benchmarking/pipeline_parity.py`, add `benchmarking/test_python_reference.py`; create `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/FeatureNormalizer.kt`, `app/android/app/src/test/kotlin/com/kumpas/kumpas_app/FeatureNormalizerTest.kt`; modify `VisionEngine.kt` to call the extracted pure normalizer.

**Interfaces:** Reference takes manifest and generates 258D normalized vectors from the exact exported PNGs, with per-frame presence and checksum; Kotlin `FeatureNormalizer.normalize(f: FloatArray, poseSeen: Boolean)` returns same layout and missing-block behavior.

- [ ] Write red Python and JUnit synthetic-vector tests with zero-pose, one missing hand, and nonzero torso; run available tests red (if Android SDK unavailable, record JVM test as blocked, not green).
```python
assert vectors.shape[1] == 258
assert np.all(normalized[:, 132:195] == 0)  # missing left-hand block
```
- [ ] Implement minimal extraction and pure normalizer; change VisionEngine to call it. Run Python tests and any available Kotlin compile/tests; report Android toolchain blocker explicitly.

### Task 3: Android replay and trace capture

**Files:** Modify `VisionEngine.kt`, `CameraPreviewView.kt`, `MainActivity.kt`; create `app/android/app/src/androidTest/kotlin/com/kumpas/kumpas_app/benchmark/PipelineParityTest.kt`, `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/PipelineTrace.kt`, `benchmarking/collect_pipeline_trace.py`; add JVM trace arithmetic test.

**Interfaces:** `VisionEngine.extractFrame(bitmap,timestampMs)` is shared by onFrame and replay; Android test reads app-specific PNG files and writes replay JSON without logging biometric vectors. Analyzer stamps `elapsedRealtimeNanos` before bitmap work, and the main-thread sink records terminal delivery. Collector requires physical device and sufficient valid attempt samples and writes a separate report.

- [ ] Add red trace arithmetic/JVM tests and Python collector parser tests (no false pass on empty/emulator traces). Run tests red.
```kotlin
assertEquals(42.0, trace.lastFrameToFeedbackMs, 0.001)
```
- [ ] Implement minimal shared extractor/replay/trace. Run all runnable tests and compile source where Android SDK exists; never claim instrumented pass without hardware.

### Task 4: Reproduction and status report

**Files:** Create `benchmarking/pipeline_verification.md` with exact offline commands and physical-device checklist; annotate `docs/phase-gates.md` only in an isolated addition, not rewrite unrelated rows.

- [ ] Run Python unit suite, real-clip preparation and reference extraction on one local FSL-105 clip, comparator using a synthetic same-vector Android fixture clearly labeled **software self-test**, and static compilation checks. Record frame counts/digests and state that a real Android comparison, anatomical correctness, and camera-to-feedback numbers remain pending.
- [ ] Inspect `git diff --check` and targeted diff; preserve all pre-existing edits. Commit only this task's files if verified.
