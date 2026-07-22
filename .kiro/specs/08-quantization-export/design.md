# Phase 8 — Quantization & Export Design

## 1. Quantization Strategy

### Decision: Dynamic Range Quantization (Post-Training)

| Option | Considered | Chosen | Rationale |
|--------|-----------|--------|-----------|
| Dynamic range quantization | ✅ | ✅ | Weights quantized to INT8; activations remain float at runtime. Best size reduction with minimal accuracy impact. No calibration dataset needed. |
| Float16 quantization | ✅ | Export produced but not deployed | Larger file (0.57 MB vs 0.32 MB); marginal latency difference on CPU. GPU delegate could benefit, but mid-range devices may not have reliable GPU delegate support. |
| Full INT8 quantization | Considered | Deferred | Requires representative calibration dataset; more complex pipeline. Reserved as fallback if dynamic range doesn't meet latency targets on real hardware. |
| Quantization-aware training (QAT) | Considered | Not needed | Post-training quantization showed no accuracy degradation (emulator test matched float32 accuracy). QAT adds training complexity without benefit here. |

### Justification for Dynamic Range

1. **Model is small (270K params):** Quantization benefit is primarily size (1.1 MB → 0.32 MB), not compute — the model is already fast.
2. **No accuracy degradation observed:** Emulator testing showed identical predictions to float32.
3. **TFLite Flex delegate required:** LSTM ops use SELECT_TF_OPS fallback. Dynamic range is the most compatible quantization strategy with Flex delegate.
4. **Simple, reproducible pipeline:** One-command export with no calibration tuning.

---

## 2. Export Pipeline

### Script: `training/tflite_export/export_tflite.py`

```
Input: ../kumpas-data/models/<run_id>.keras (trained Keras model)
Output: ../kumpas-data/tflite/kumpas_50sign_<run_id>_<quant>.tflite
        ../kumpas-data/tflite/label_map.json
```

### TFLite Converter Configuration

```python
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS,
    tf.lite.OpsSet.SELECT_TF_OPS  # Required for LSTM operations
]
converter.optimizations = [tf.lite.Optimize.DEFAULT]  # Dynamic range
```

### Export Log
Every export appends to `training/tflite_export/tflite_export_log.json`:
- Timestamp, run_id, input shape
- Per-variant: quantization type, filename, size (MB), local latency

---

## 3. Export Results

| Variant | Size | Local M1 Latency (median) | Local M1 Latency (p95) |
|---------|------|--------------------------|------------------------|
| Dynamic range | 0.32 MB | 0.34 ms | 0.37 ms |
| Float16 | 0.57 MB | 0.50 ms | 0.64 ms |

**Deployed variant:** `kumpas_50sign_20260705_194813_no_face_dynamic.tflite` (0.32 MB)

---

## 4. Accuracy/Latency Tradeoff

| Metric | Float32 (Keras) | Dynamic Range (TFLite) | Delta |
|--------|-----------------|----------------------|-------|
| Test accuracy | 95.07% | 95.07% (emulator) | 0% degradation |
| Model size | ~1.1 MB | 0.32 MB | 71% reduction |
| Inference latency | — | 0–2 ms (emulator) | Well under 150ms budget |

**Key finding:** No measurable accuracy degradation from quantization. The 270K-parameter model with simple operations (Conv1D, LSTM, Dense) quantizes cleanly.

---

## 5. Target Device Specification

### Primary Reference Device (Pending Acquisition)

| Specification | Target |
|--------------|--------|
| Chipset | MediaTek Helio G-series OR Snapdragon 6-series |
| RAM | 4 GB minimum |
| Android API | 28+ (Android 9+) |
| Example candidates | Samsung Galaxy A14, Redmi Note 12, realme C55 |

### Current Measurement (Emulator Fallback)

| Environment | Result | Caveat |
|-------------|--------|--------|
| Android emulator on M1 Mac | Inference: 0–2 ms, FPS: 28.6–29.9 | M1 emulator performance is NOT representative of mid-range ARM hardware |

**Phase 18 requirement:** Real-device measurement on at least one named mid-range device before thesis claims are finalized. The emulator result provides confidence that the model is well within budget, but the actual number will differ on real hardware.

---

## 6. Deployment Artifact

The app bundles the TFLite model as a Flutter asset:
- Path in app: `app/assets/models/kumpas_50sign_no_face_dynamic.tflite`
- Label map: `app/assets/models/label_map.json`
- Total asset size: ~0.35 MB (negligible impact on APK size)

---

## 7. Flex Delegate Note

The model uses `SELECT_TF_OPS` because TFLite's built-in LSTM op doesn't cover all LSTM configurations. This means:
- The app must include the TensorFlow Lite Select TF Ops library (~8 MB added to APK)
- Inference is still fast (sub-ms on M1 emulator) but the Flex delegate has higher cold-start time
- **Alternative if APK size is a concern:** Convert LSTM to equivalent Conv1D stack (sacrifices temporal modeling; not recommended given current results)

---

## Status

**Complete.** All acceptance criteria met:
- ✅ Quantization strategy documented with rationale (dynamic range post-training)
- ✅ Export pipeline produces .tflite with logged provenance
- ✅ Accuracy delta measured (0% degradation)
- ✅ Target devices named (Galaxy A14, Redmi Note 12, realme C55 as candidates)
- ✅ Latency measured on emulator with caveat documented; real-device validation pending (Phase 18)
