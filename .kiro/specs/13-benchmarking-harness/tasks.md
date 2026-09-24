# Implementation Plan

## Overview
Build a benchmarking harness that validates accuracy, latency, and FPS against thesis targets. The harness produces structured JSON logs suitable for iteration-over-iteration plotting in the technical validation chapter.

## Tasks

- [x] 1. Create `benchmarking/log_utils.py` with `append_entry`, `load_history`, `validate_entry` helpers and atomic file writes. Create `benchmarking/benchmark_history.json` as an empty JSON array. Schema requires: timestamp, benchmark_type, model_version, device, condition, results.
- [x] 2. Create `benchmarking/accuracy_benchmark.py` that loads a deployed .tflite model, evaluates it on the held-out test set (X_test.npy, y_test.npy), computes per-class accuracy/precision/recall/F1 and aggregate metrics, appends structured results to benchmark_history.json, and prints pass/fail against the ≥90% accuracy gate. Accepts --model-path, --run-id, --notes CLI args.
- [x] 3. Verify accuracy benchmark reproducibility: run twice with same model + data and confirm identical outputs.
- [x] 4. Create `benchmarking/collect_latency.py` host script that runs the Android instrumented latency test via adb, parses JSON output from logcat (tag KumpasBenchmark), gets device info from adb getprop, and appends to benchmark_history.json.
- [x] 5. Create `app/android/app/src/androidTest/.../LatencyBenchmarkTest.kt` instrumented test: load .tflite via TFLiteClassifier, run N=100 inferences on a 30×258 sample, compute mean/median/p50/p95/max timing (cold vs warm), output JSON to logcat with BENCHMARK_RESULT marker.
  - **NEVER EXECUTED** (noted 2026-09-23, Day 1 of `docs/30-day-plan.md`). The file exists at `app/android/app/src/androidTest/kotlin/com/kumpas/kumpas_app/benchmark/LatencyBenchmarkTest.kt`, so the create task is genuinely done and the box stays `[x]`. It has never been run: an Android instrumented test needs a connected device or a running emulator, and no device is in hand. Per `docs/hardening-plan.md` §1.1 it also cannot run from a clean clone, because the `.tflite` it opens is gitignored. **No latency number in this repo comes from this test.** Clear this note only when a run happens, recording the date and device (see `docs/30-day-plan.md` §9 item 3).
- [x] 6. Create `benchmarking/collect_fps.py` host script that pulls FPS benchmark JSON from device via adb pull, validates ≥60s duration, checks gate (mean ≥24 FPS), detects degradation flag, and appends to benchmark_history.json.
- [x] 7. Add benchmark mode to the Flutter app (debug menu toggle or --benchmark flag): run full camera→landmarks→inference pipeline for configurable duration (default 60s), track per-frame timestamps, compute sustained FPS (mean, min, p5, stddev), detect degradation (FPS <24 for >2s), write results JSON to /sdcard/Download/kumpas_fps_benchmark.json.
  - **NEVER EXECUTED** (noted 2026-09-23, Day 1 of `docs/30-day-plan.md`). The code exists: `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/BenchmarkMode.kt`, constructed at `MainActivity.kt:56` with the frame hook live in the `VisionEngine` callback. So the create task is done and the box stays `[x]`. It has never produced a result, for three separate reasons, all from `docs/hardening-plan.md` §1.8:
    1. **No device.** Sustained-FPS measurement needs real hardware; none is in hand.
    2. **The write path fails on API 29+.** `BenchmarkMode.kt:72` writes to `Environment.getExternalStoragePublicDirectory(DIRECTORY_DOWNLOADS)`, but `AndroidManifest.xml` grants `WRITE_EXTERNAL_STORAGE` only with `maxSdkVersion="28"`. On anything newer the write fails, so `collect_fps.py` has nothing to `adb pull`. Fix is PR #2 Stage D1 (`context.getExternalFilesDir(null)`).
    3. **No UI can trigger it.** There is no entry point calling `startBenchmark`/`stopBenchmark` (PR #2 Stage D3).
  - Also note for whoever runs it: it currently counts *emitted events* (post-stride, roughly 7.5/s) rather than camera frames, which contradicts the FPS gate's semantics (PR #2 Stage D2). Fix D1 to D3 before trusting any number it produces. **No FPS number in this repo comes from this code.**
- [x] 8. Create `benchmarking/environment_protocol.md` documenting three conditions (optimal >300lux plain background, low_light <100lux plain background, cluttered >300lux complex background) with reproducible setup instructions, labeling conventions, and a pre-run checklist.
- [x] 9. Create `benchmarking/plot_history.py` that reads benchmark_history.json and generates publication-ready PNG plots (accuracy/latency/FPS over iterations) with target threshold lines. Supports --type, --device, --condition filters. Outputs to benchmarking/plots/.
- [x] 10. Seed benchmark_history.json with retroactive entries from the Phase 4 emulator report (latency: 0-2ms p95; FPS: 28.6-29.9 mean over 55s).
- [x] 11. Run accuracy benchmark against current best model (20260705_194813_no_face_dynamic.tflite) and verify ≥90% PASS.
- [x] 12. Validate that plot_history.py produces correct plots from seeded history data.
- [x] 13. Update docs/phase-gates.md with benchmarking harness delivery status.
- [x] 14. Create `benchmarking/README.md` explaining how to run each benchmark type, targets, file structure, and log format.

## Task Dependency Graph
```json
{
  "waves": [
    [1, 8, 14],
    [2, 4, 6, 9, 10],
    [3, 5, 7, 11],
    [12],
    [13]
  ]
}
```

## Notes

**What a checked box means in this file (added 2026-09-23, Day 1 of `docs/30-day-plan.md`).** Every task here is worded as a *create* task, so `[x]` means **the artifact was written**, not that it was ever run and not that its output is trustworthy. Tasks 5 and 7 are checked and carry `NEVER EXECUTED` notes; read those notes before citing any latency or FPS figure. Task 10 seeded *retroactive estimates* by hand, which is what it says it does, so a green task 10 is not a measurement either. Tasks 2, 3, and 11 did genuinely execute, on 2026-07-23, host-side.

This convention was chosen over un-checking tasks 5 and 7, which `docs/hardening-plan.md` Stage A1 proposes. Un-checking would assert that `LatencyBenchmarkTest.kt` and `BenchmarkMode.kt` do not exist, and both do. The defect is execution, not authorship, and the checkbox tracks authorship. Reasoning is recorded in `docs/30-day-plan.md` §1b Conflict 5. `grep -c '\[x\]'` on this file therefore still returns 14, deliberately.

- Tasks 5 and 7 require on-device work (Android instrumented test / benchmark mode). These need a connected device or emulator to verify, and as of 2026-09-23 neither has been run. See the per-task notes above.
- Tasks 11 and 12 require a Python environment with tensorflow and matplotlib. As of 2026-09-23 that environment is `benchmarking/.venv` (TensorFlow 2.21.0, scikit-learn 1.9.0) and it is **not declared by any requirements file in the repo**; `benchmarking/requirements.txt` does not exist. Day 5 of the 30-day plan creates it.
- The accuracy benchmark reuses the same test data as the Phase 3 eval report — results should match the 95.07% previously reported. Caveat recorded 2026-09-23: the logged runs used TensorFlow 2.19.0 while `benchmarking/.venv` now has 2.21.0, so an exact match is not guaranteed. Day 15 re-runs it and records any difference rather than reconciling it.
