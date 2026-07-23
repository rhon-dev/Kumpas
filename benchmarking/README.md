# Benchmarking Harness

Automated benchmarking for the Kumpas FSL recognition pipeline.
Three benchmark types validate accuracy, latency, and FPS against thesis targets.

## Targets

| Metric | Target | Gate |
|--------|--------|------|
| Test accuracy (post-quantization) | ≥90% | Phase 3 |
| Inference latency p95 | <150ms | Phase 4 |
| Sustained FPS (60s) | 24–30 | Phase 5 |

## Quick Start

### 1. Accuracy Benchmark (Offline, Python)

Evaluates the .tflite model on the held-out test set:

```bash
# From repo root, using an env with tensorflow + sklearn
python benchmarking/accuracy_benchmark.py

# Explicit model path
python benchmarking/accuracy_benchmark.py --model-path ../kumpas-data/tflite/kumpas_50sign_20260705_194813_no_face_dynamic.tflite
```

### 2. Latency Benchmark (On-Device)

Runs the Android instrumented test and collects timing:

```bash
# Build and install test APK first
cd app && flutter build apk --debug
adb install app/build/...

# Collect
python benchmarking/collect_latency.py --model-version 20260705_194813_no_face --condition optimal
```

### 3. FPS Benchmark (On-Device, Live Camera)

Run the app in benchmark mode, then collect:

```bash
# In app: enable benchmark mode via debug menu or --benchmark flag
# Wait for ≥60s of live camera operation
# Then:
python benchmarking/collect_fps.py --model-version 20260705_194813_no_face --condition optimal
```

## Environment Conditions

See `environment_protocol.md` for full definitions:
- `optimal` — well-lit (>300 lux), plain background
- `low_light` — dim (<100 lux), plain background
- `cluttered` — well-lit, complex background

## Plotting

Generate thesis-ready iteration comparison plots:

```bash
python benchmarking/plot_history.py                    # all types
python benchmarking/plot_history.py --type accuracy    # accuracy only
python benchmarking/plot_history.py --device "Galaxy"  # filter by device
```

Outputs to `benchmarking/plots/`.

## File Structure

```
benchmarking/
├── README.md                   # This file
├── accuracy_benchmark.py       # Offline accuracy evaluation
├── collect_latency.py          # Host script: adb → latency results
├── collect_fps.py              # Host script: adb → FPS results
├── log_utils.py                # Shared history log utilities
├── plot_history.py             # Iteration comparison plots
├── benchmark_history.json      # Appendable structured results log
├── environment_protocol.md     # Condition definitions + checklist
├── phase4_emulator_report.md   # Legacy emulator results
└── plots/                      # Generated PNG figures
```

## Log Format

Each benchmark appends a JSON entry to `benchmark_history.json`:

```json
{
  "timestamp": "2026-07-22T14:30:00",
  "benchmark_type": "accuracy|latency|fps",
  "model_version": "20260705_194813_no_face",
  "device": "Samsung Galaxy A14 / Helio G80 / 4GB",
  "condition": "optimal|low_light|cluttered|n/a",
  "results": { ... },
  "gate_pass": true,
  "notes": ""
}
```
