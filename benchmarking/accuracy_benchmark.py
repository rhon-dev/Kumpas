#!/usr/bin/env python3
"""KUMPAS Phase 13 — Accuracy benchmark for deployed .tflite model.

Evaluates the quantized TFLite model on the held-out test set and logs
structured results to benchmark_history.json.

Usage:
    python accuracy_benchmark.py [--model-path PATH] [--run-id ID] [--notes "..."]

Defaults to the latest dynamic-quant export from tflite_export_log.json.
"""

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = REPO_ROOT.parent / "kumpas-data"
SEQ_DIR = DATA_ROOT / "sequences"
TFLITE_DIR = DATA_ROOT / "tflite"
EXPORT_LOG = REPO_ROOT / "training" / "tflite_export" / "tflite_export_log.json"

# Append benchmarking dir so log_utils is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))
from log_utils import append_entry, make_timestamp  # noqa: E402


def resolve_model(model_path: str | None, run_id: str | None) -> tuple[Path, str]:
    """Resolve the .tflite model path and run_id."""
    if model_path:
        p = Path(model_path)
        if not p.exists():
            raise FileNotFoundError(f"Model not found: {p}")
        # Derive run_id from filename if not given
        rid = run_id or p.stem.replace("kumpas_50sign_", "").replace("_dynamic", "").replace("_float16", "").replace("_builtins", "")
        return p, rid

    # Default: prefer builtins variant (deployed to device), fall back to dynamic
    builtins = TFLITE_DIR / "kumpas_50sign_builtins_dynamic.tflite"
    if builtins.exists():
        rid = run_id or "20260705_194813_no_face_builtins"
        return builtins, rid

    # Fallback: latest dynamic export from log
    log = json.loads(EXPORT_LOG.read_text())
    latest = log[-1]
    rid = run_id or latest["run_id"]
    dynamic = next(e for e in latest["exports"] if e["quant"] == "dynamic")
    p = TFLITE_DIR / dynamic["file"]
    if not p.exists():
        raise FileNotFoundError(
            f"Expected model at {p} (from tflite_export_log.json). "
            "Run export_tflite.py first or pass --model-path explicitly."
        )
    return p, rid


def load_test_data() -> tuple[np.ndarray, np.ndarray, dict]:
    """Load X_test, y_test, and label_map."""
    x_test = np.load(SEQ_DIR / "X_test.npy")
    y_test = np.load(SEQ_DIR / "y_test.npy")
    label_map = json.loads((SEQ_DIR / "label_map.json").read_text())
    # Normalize keys to int
    label_map = {int(k): v for k, v in label_map.items()}
    return x_test, y_test, label_map


def run_tflite_inference(model_path: Path, x_test: np.ndarray) -> np.ndarray:
    """Run batch inference through TFLite interpreter."""
    import tensorflow as tf

    interp = tf.lite.Interpreter(model_path=str(model_path))
    interp.allocate_tensors()
    inp_detail = interp.get_input_details()[0]
    out_detail = interp.get_output_details()[0]

    # Check if feature slicing is needed (no_face: 258 vs full: 1662)
    expected_features = inp_detail["shape"][2]
    if x_test.shape[2] != expected_features:
        print(f"  Feature mismatch: test data has {x_test.shape[2]}, model expects {expected_features}")
        if x_test.shape[2] == 1662 and expected_features == 258:
            # no_face variant: drop face landmarks (indices 132:1536)
            POSE, FACE = 132, 1404
            keep = np.r_[0:POSE, POSE + FACE:1662]
            x_test = x_test[:, :, keep]
            print(f"  Sliced to no_face features: {x_test.shape}")
        else:
            raise ValueError(
                f"Cannot reconcile test data features ({x_test.shape[2]}) "
                f"with model input ({expected_features})"
            )

    predictions = []
    for i in range(len(x_test)):
        sample = x_test[i:i+1].astype(np.float32)
        interp.set_tensor(inp_detail["index"], sample)
        interp.invoke()
        output = interp.get_tensor(out_detail["index"])
        predictions.append(int(np.argmax(output, axis=-1)[0]))

    return np.array(predictions)


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, label_map: dict) -> dict:
    """Compute accuracy, per-class metrics, and confused pairs."""
    from sklearn.metrics import precision_recall_fscore_support

    n_classes = len(label_map)
    names = [label_map[i]["label"] if isinstance(label_map[i], dict) else label_map[i]
             for i in range(n_classes)]

    accuracy = float((y_pred == y_true).mean())
    prec, rec, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=range(n_classes), zero_division=0
    )
    macro_prec, macro_rec, macro_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0
    )

    # Per-class breakdown
    per_class = []
    for i in range(n_classes):
        per_class.append({
            "class_id": i,
            "label": names[i],
            "precision": round(float(prec[i]), 4),
            "recall": round(float(rec[i]), 4),
            "f1": round(float(f1[i]), 4),
            "support": int(support[i]),
        })

    return {
        "accuracy": round(accuracy, 4),
        "macro_precision": round(float(macro_prec), 4),
        "macro_recall": round(float(macro_rec), 4),
        "macro_f1": round(float(macro_f1), 4),
        "n_samples": int(len(y_true)),
        "n_classes": n_classes,
        "per_class": per_class,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model-path", default=None, help="Path to .tflite model")
    ap.add_argument("--run-id", default=None, help="Model run identifier")
    ap.add_argument("--notes", default="", help="Free-text notes for the log entry")
    args = ap.parse_args()

    print("=" * 60)
    print("KUMPAS Accuracy Benchmark")
    print("=" * 60)

    # Resolve model
    model_path, run_id = resolve_model(args.model_path, args.run_id)
    print(f"Model: {model_path.name}")
    print(f"Run ID: {run_id}")

    # Load test data
    x_test, y_test, label_map = load_test_data()
    print(f"Test set: {len(x_test)} samples, {len(label_map)} classes")

    # Run inference
    print("Running inference...")
    t0 = time.perf_counter()
    y_pred = run_tflite_inference(model_path, x_test)
    elapsed = time.perf_counter() - t0
    print(f"Inference complete: {elapsed:.2f}s ({elapsed/len(x_test)*1000:.1f} ms/sample)")

    # Compute metrics
    metrics = compute_metrics(y_test, y_pred, label_map)

    # Gate check
    gate_pass = metrics["accuracy"] >= 0.90
    gate_str = "✅ PASS" if gate_pass else "❌ FAIL"
    print(f"\nAccuracy: {metrics['accuracy']:.4f} (gate ≥0.90 → {gate_str})")
    print(f"Macro F1: {metrics['macro_f1']:.4f}")

    # Build log entry
    entry = {
        "timestamp": make_timestamp(),
        "benchmark_type": "accuracy",
        "model_version": run_id,
        "model_file": model_path.name,
        "device": "offline/python",
        "condition": "n/a",
        "results": metrics,
        "gate_pass": gate_pass,
        "notes": args.notes,
    }

    # Append to history
    append_entry(entry)
    print(f"\nLogged to benchmark_history.json")
    print("=" * 60)

    return 0 if gate_pass else 1


if __name__ == "__main__":
    sys.exit(main())
