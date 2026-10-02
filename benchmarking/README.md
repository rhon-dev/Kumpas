# Benchmarking Harness

Automated benchmarking for the Kumpas FSL recognition pipeline.
Three benchmark types validate accuracy, latency, and FPS against thesis targets.

## Targets

| Metric | Target | Gate |
|--------|--------|------|
| Test accuracy (post-quantization) | ≥90% | Phase 3 |
| Inference latency p95 | <150ms | Phase 4 |
| Sustained CameraX analyzer throughput (≥60s) | 24–30 FPS | Phase 5; physical hardware required |

## Quick Start

### 1. Accuracy Benchmark (Offline, Python)

Evaluates the .tflite model on the held-out test set:

```bash
# From repo root, using an env with tensorflow + sklearn
python benchmarking/accuracy_benchmark.py

# Explicit model path
python benchmarking/accuracy_benchmark.py --model-path ../kumpas-data/tflite/kumpas_50sign_20260705_194813_no_face_dynamic.tflite
```

### 2. Native Latency and FPS (Live Camera)

Start a ≥60s benchmark using the existing settings action / native
`startBenchmark(durationSeconds: 60)` channel entry point. Retain the returned
run ID. Keep the camera active for the whole window and perform practice attempts
for latency traces. An idle/stalled run still finishes and reports honest zeros.
After `benchmark_complete`, collect the **same** run explicitly:

```bash
python3 benchmarking/collect_fps.py --serial "$SERIAL" --run-id "$RUN_ID" --model-version "$MODEL_VERSION" --condition optimal
python3 benchmarking/collect_latency.py --serial "$SERIAL" --run-id "$RUN_ID" --model-version "$MODEL_VERSION" --condition optimal
```

Collectors read `com.kumpas.kumpas_app` internal
`files/benchmarks/latest.json` through `adb -s SERIAL shell run-as`; install a
debuggable build for this readback. Release-build `run-as` denial is a collection
failure, not permission to reuse a Downloads/logcat artifact. Immutable run files
are retained at `files/benchmarks/RUN_ID.json`; collectors never delete them.

Schema v2 separates analyzer, stride-selected, processed and emitted-event counts,
full-window means, and fixed per-second samples including leading/trailing zeros.
The 24–30 FPS target is **analyzer-entry throughput**, not sensor/display FPS or
full detector throughput. The sustained gate requires every one-second analyzer
bin ≥24 and a ≥60s complete run. A sampled detector rate around 7.5/s is not a
substitute target. Short, empty, stalled, stale-ID, malformed, wrong-package,
missing-boundary and emulator reports cannot pass the physical-device gate.

Latency p50/p95 use nearest-rank percentiles of
`final_analyzer_to_event_ms` (analyzer entry before bitmap conversion through
native processing, feedback/persistence and main-thread dispatch). This excludes
sensor/driver acquisition. `collection_ms` is the separate multi-frame interval.
Optional `final_analyzer_to_ui_ack_ms` / `first_analyzer_to_ui_ack_ms` are native
post-frame-ACK **upper bounds**, not physical display latency. Missing ACKs remain
missing, not zeros. No native/Dart clock subtraction is allowed. The named event
boundary p95 must be <150ms; interpreter inference remains a separate diagnostic.

### 3. Legacy Interpreter Diagnostic (Not Camera Latency)

After the existing test APK has been installed by the device owner:

```bash
python3 benchmarking/collect_latency.py --serial "$SERIAL" --interpreter-only --model-version "$MODEL_VERSION" --condition n/a
```

This deliberately returns a nonzero gate status even if the diagnostic succeeds:
`assessment.diagnostic_valid` describes diagnostic validity; `gate_pass` is always
false. Its history `measurement_type` is `interpreter_latency_diagnostic`
(`benchmark_type: latency` is retained for the historical log schema). Do not mix
these rows, legacy retroactive estimates, or schema-v2 `assessment` values into a
camera-latency thesis table using the old plotter's interpreter fields. Previous
history rows are preserved verbatim.

### Collector Regression Tests

```bash
python3 -m unittest discover -s benchmarking -p 'test_collectors.py' -v
```

Tests use synthetic reports, isolated temporary history files and mocked ADB at
the subprocess boundary. They establish software behavior, **not measured phone
performance**. No physical-device gate is closed by these tests.

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
