#!/usr/bin/env python3
"""KUMPAS Phase 4 prep — TFLite conversion + quantization of a trained run.

Converts a saved .keras model (kumpas-data/models/<run_id>.keras) to TFLite
with dynamic-range and float16 quantization, copies the label map alongside,
and runs a LOCAL latency micro-benchmark.

The local latency number is informational only: the Phase 4 gate (<150ms)
must be measured on a real mid-range Android device (PRD §4/§6).

Artifacts go OUTSIDE the repo (../kumpas-data/tflite/) — .tflite is
gitignored; this conversion log (tflite_export_log.json) is committed.

Usage:
    ~/.kumpas-venvs/tf/bin/python export_tflite.py --run-id <run_id>
"""

import argparse
import json
import time
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = REPO_ROOT.parent / "kumpas-data"
LOG_PATH = Path(__file__).resolve().parent / "tflite_export_log.json"


def convert(model, quant):
    import tensorflow as tf

    conv = tf.lite.TFLiteConverter.from_keras_model(model)
    # Keras LSTM usually lowers to fused TFLite ops; SELECT_TF_OPS is the fallback
    conv.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS,
                                      tf.lite.OpsSet.SELECT_TF_OPS]
    conv.optimizations = [tf.lite.Optimize.DEFAULT]
    if quant == "float16":
        import tensorflow as tf2
        conv.target_spec.supported_types = [tf2.float16]
    return conv.convert()


def bench(blob, sample, n=50):
    import tensorflow as tf

    interp = tf.lite.Interpreter(model_content=blob)
    interp.allocate_tensors()
    inp = interp.get_input_details()[0]
    interp.set_tensor(inp["index"], sample)
    interp.invoke()  # warmup
    times = []
    for _ in range(n):
        t0 = time.perf_counter()
        interp.set_tensor(inp["index"], sample)
        interp.invoke()
        times.append((time.perf_counter() - t0) * 1000)
    return round(float(np.median(times)), 2), round(float(np.percentile(times, 95)), 2)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args()

    import tensorflow as tf

    model = tf.keras.models.load_model(DATA_ROOT / "models" / f"{args.run_id}.keras")
    t, f = model.input_shape[1], model.input_shape[2]
    sample = np.random.rand(1, t, f).astype(np.float32)

    out_dir = DATA_ROOT / "tflite"
    out_dir.mkdir(parents=True, exist_ok=True)
    entries = []
    for quant in ("dynamic", "float16"):
        blob = convert(model, quant)
        p = out_dir / f"kumpas_50sign_{args.run_id}_{quant}.tflite"
        p.write_bytes(blob)
        med, p95 = bench(blob, sample)
        entries.append({"quant": quant, "file": p.name,
                        "size_mb": round(len(blob) / 1e6, 2),
                        "local_m1_latency_ms_median": med,
                        "local_m1_latency_ms_p95": p95})
        print(f"{quant}: {len(blob)/1e6:.2f} MB, local M1 median {med} ms (p95 {p95})")

    # label map next to the models for the app
    seq_label_map = DATA_ROOT / "sequences" / "label_map.json"
    (out_dir / "label_map.json").write_text(seq_label_map.read_text())

    log = json.loads(LOG_PATH.read_text()) if LOG_PATH.exists() else []
    log.append({"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "run_id": args.run_id,
                "input_shape": [int(t), int(f)],
                "note": "local M1 latency is informational; Phase 4 gate "
                        "requires real mid-range Android measurement",
                "exports": entries})
    LOG_PATH.write_text(json.dumps(log, indent=1))
    print(f"artifacts -> {out_dir}; log -> {LOG_PATH.name}")


if __name__ == "__main__":
    main()
