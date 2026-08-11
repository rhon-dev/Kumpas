# Phase 13 — Benchmarking Harness Design

## 1. Three Benchmark Types

### A. Accuracy Benchmark (Offline)
- **Input:** Held-out test set (203 samples) + deployed .tflite model
- **Output:** Per-class accuracy, aggregate accuracy, confusion matrix
- **Frequency:** After every model change or quantization adjustment
- **Script:** `benchmarking/accuracy_benchmark.py`

### B. Latency Benchmark (On-Device)
- **Input:** Sample landmark sequences on target device
- **Measurement:** Per-inference timing (warm vs cold start)
- **Metrics:** Mean, median, p50, p95, max (in ms)
- **Frequency:** On every target device, after model or pipeline changes
- **Script:** Android instrumented test or benchmark app mode

### C. FPS Benchmark (On-Device, Live Camera)
- **Input:** Live camera feed for ≥60 seconds continuous operation
- **Measurement:** Frames completing full pipeline per second (sustained, not burst)
- **Metrics:** Mean FPS, min FPS, FPS over time (detect degradation)
- **Frequency:** On every target device, per environment condition
- **Script:** Built into app (debug overlay or benchmark mode)

## 2. Environment Conditions

| Condition | Definition | How to Reproduce |
|-----------|-----------|------------------|
| Optimal | Well-lit room (>300 lux), plain background, signer centered | Standard indoor lighting, white/gray wall |
| Low light | Dim environment (<100 lux) | Single lamp, no overhead; or evening natural light |
| Cluttered background | Complex visual scene behind signer | Bookshelf, other people, varied objects |

## 3. Logging Format

Each benchmark run produces a JSON entry:

```json
{
  "timestamp": "2026-07-22T14:30:00",
  "benchmark_type": "accuracy|latency|fps",
  "model_version": "20260705_194813_no_face_dynamic",
  "device": "Samsung Galaxy A14 / Helio G80 / 4GB",
  "condition": "optimal|low_light|cluttered",
  "results": { ... },
  "notes": "..."
}
```

History stored in `benchmarking/benchmark_history.json` (appendable, never overwritten).

## 4. Targets (Pass/Fail)

| Metric | Target | Measured (Emulator) | Real Device |
|--------|--------|-------------------|-------------|
| Test accuracy (post-quant) | ≥90% | 95.07% ✅ | Pending |
| Inference latency (p95) | <150ms | 0-2ms ✅ | Pending |
| Sustained FPS (60s) | 24-30 | 28.6-29.9 ✅ | Pending |

## 5. Iteration Comparison

The harness must support plotting metrics across iterations for the thesis technical validation chapter:
- X-axis: model iteration / date
- Y-axis: accuracy / latency / FPS
- Stored as structured data, not screenshots

## Status

**Pending implementation.** Emulator benchmarks exist as ad-hoc reports. Formal harness script with structured logging needs to be built before Phase 18.
