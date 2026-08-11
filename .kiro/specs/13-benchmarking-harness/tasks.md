# Implementation Plan

## Overview
Build a benchmarking harness that validates accuracy, latency, and FPS against thesis targets. The harness produces structured JSON logs suitable for iteration-over-iteration plotting in the technical validation chapter.

## Tasks

- [x] 1. Create `benchmarking/log_utils.py` with `append_entry`, `load_history`, `validate_entry` helpers and atomic file writes. Create `benchmarking/benchmark_history.json` as an empty JSON array. Schema requires: timestamp, benchmark_type, model_version, device, condition, results.
- [x] 2. Create `benchmarking/accuracy_benchmark.py` that loads a deployed .tflite model, evaluates it on the held-out test set (X_test.npy, y_test.npy), computes per-class accuracy/precision/recall/F1 and aggregate metrics, appends structured results to benchmark_history.json, and prints pass/fail against the ≥90% accuracy gate. Accepts --model-path, --run-id, --notes CLI args.
- [x] 3. Verify accuracy benchmark reproducibility: run twice with same model + data and confirm identical outputs.
- [x] 4. Create `benchmarking/collect_latency.py` host script that runs the Android instrumented latency test via adb, parses JSON output from logcat (tag KumpasBenchmark), gets device info from adb getprop, and appends to benchmark_history.json.
- [x] 5. Create `app/android/app/src/androidTest/.../LatencyBenchmarkTest.kt` instrumented test: load .tflite via TFLiteClassifier, run N=100 inferences on a 30×258 sample, compute mean/median/p50/p95/max timing (cold vs warm), output JSON to logcat with BENCHMARK_RESULT marker.
- [x] 6. Create `benchmarking/collect_fps.py` host script that pulls FPS benchmark JSON from device via adb pull, validates ≥60s duration, checks gate (mean ≥24 FPS), detects degradation flag, and appends to benchmark_history.json.
- [x] 7. Add benchmark mode to the Flutter app (debug menu toggle or --benchmark flag): run full camera→landmarks→inference pipeline for configurable duration (default 60s), track per-frame timestamps, compute sustained FPS (mean, min, p5, stddev), detect degradation (FPS <24 for >2s), write results JSON to /sdcard/Download/kumpas_fps_benchmark.json.
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
- Tasks 5 and 7 require on-device work (Android instrumented test / Flutter benchmark mode). These need a connected device or emulator to verify.
- Tasks 11 and 12 require a Python environment with tensorflow and matplotlib (e.g., Colab or a local venv with those deps).
- The accuracy benchmark reuses the same test data as the Phase 3 eval report — results should match the 95.07% previously reported.
