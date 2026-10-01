#!/usr/bin/env python3
"""Score a frozen validation-selected run on the *reused*, exploratory test set.

This command cannot create an untouched holdout retroactively. It is a
separate evaluation step after selection; never use its score to rank runs.
"""
import argparse
import json
import math
from pathlib import Path

import numpy as np
from evaluation_protocol import sha256, validate_manifest


def wilson_interval(correct: int, n: int, z: float = 1.959963984540054) -> tuple:
    if n <= 0:
        raise ValueError("empty test set")
    p = correct / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    radius = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (centre - radius, centre + radius)


def render_report(result: dict) -> str:
    lo, hi = result["wilson_95"]
    rows = [f"| {r['label']} | {r['support']} | {r['precision']:.3f} | {r['recall']:.3f} | {r['f1']:.3f} |"
            for r in result["per_class"]]
    return "\n".join([
        f"# Exploratory evaluation — {result['run_id']}", "",
        "**Status: exploratory, NOT a pristine final test.** The existing FSL-105 test split was consulted in historical model experiments. This run was selected using validation only, but the test clips are not newly unseen to the project.", "",
        "**Scope:** Accuracy on the specified FSL-105 clip split; signer-independent generalization not established (no verified signer IDs).", "",
        f"- Correct: {result['correct']}/{result['n']}",
        f"- Accuracy: {result['accuracy']:.4f}",
        f"- Macro F1: {result['macro_f1']:.4f}",
        f"- Clip-level Wilson 95% interval: [{lo:.4f}, {hi:.4f}]; assumes independent clips, which is not verified without signer identities.", "",
        "| Class | Support | Precision | Recall | F1 |", "|---|---:|---:|---:|---:|", *rows, "",
    ])


def evaluate_frozen(freeze_path: Path, protocol_dir: Path, test_dir: Path, report_dir: Path) -> dict:
    freeze_path, protocol_dir, test_dir, report_dir = map(Path, (freeze_path, protocol_dir, test_dir, report_dir))
    if not freeze_path.is_file():
        raise FileNotFoundError(f"missing frozen validation selection: {freeze_path}")
    freeze = json.loads(freeze_path.read_text())
    manifest_path = protocol_dir / "manifest.json"
    if freeze.get("protocol_sha256") != sha256(manifest_path):
        raise ValueError("frozen selection/manifest digest mismatch")
    manifest = json.loads(manifest_path.read_text())
    validate_manifest(manifest, protocol_dir.parent)
    required = ("run_id", "checkpoint", "checkpoint_sha256", "selection_method", "best_val_accuracy")
    if not all(k in freeze for k in required):
        raise ValueError("incomplete frozen validation selection")
    checkpoint = Path(freeze["checkpoint"])
    if not checkpoint.is_file() or sha256(checkpoint) != freeze["checkpoint_sha256"]:
        raise ValueError("frozen checkpoint digest mismatch")
    if sha256(test_dir / "clips_test.json") != manifest["source_sha256"]["clips_test.json"]:
        raise ValueError("test clip list digest mismatch")
    X_test = np.load(test_dir / "X_test.npy", allow_pickle=False)
    y_test = np.load(test_dir / "y_test.npy", allow_pickle=False)
    if len(X_test) != len(y_test) or len(y_test) != len(json.loads((test_dir / "clips_test.json").read_text())):
        raise ValueError("test arrays/clip list length mismatch")
    from tensorflow.keras.models import load_model
    from sklearn.metrics import precision_recall_fscore_support, f1_score
    model = load_model(checkpoint)
    if X_test.shape[1] != model.input_shape[1]:
        raise ValueError("model/test sequence length mismatch")
    if model.input_shape[2] == 258 and X_test.shape[2] == 1662:
        X_test = X_test[:, :, np.r_[0:132, 1536:1662]]
    if X_test.shape[2] != model.input_shape[2]:
        raise ValueError("model/test feature mismatch")
    pred = model.predict(X_test, verbose=0).argmax(axis=1)
    label_map = json.loads((test_dir / "label_map.json").read_text())
    ids = list(range(len(label_map)))
    precision, recall, f1, support = precision_recall_fscore_support(
        y_test, pred, labels=ids, zero_division=0)
    correct, n = int(np.sum(pred == y_test)), len(y_test)
    result = {"run_id": freeze["run_id"], "correct": correct, "n": n,
              "accuracy": correct / n, "macro_f1": float(f1_score(y_test, pred, labels=ids, average="macro", zero_division=0)),
              "wilson_95": wilson_interval(correct, n),
              "per_class": [{"label": label_map[str(i)]["label"], "support": int(support[i]),
                             "precision": float(precision[i]), "recall": float(recall[i]), "f1": float(f1[i])}
                            for i in ids],
              "selection_sha256": sha256(freeze_path), "manifest_sha256": sha256(manifest_path),
              "test_arrays_sha256": {name: sha256(test_dir / name) for name in ("X_test.npy", "y_test.npy")},
              "status": "exploratory-reused-test"}
    report_dir.mkdir(parents=True, exist_ok=False)
    (report_dir / "evaluation.json").write_text(json.dumps(result, indent=2))
    (report_dir / "evaluation.md").write_text(render_report(result))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--protocol-dir", type=Path, required=True)
    parser.add_argument("--test-dir", type=Path, required=True)
    parser.add_argument("--report-dir", type=Path, required=True)
    args = parser.parse_args()
    result = evaluate_frozen(args.freeze, args.protocol_dir, args.test_dir, args.report_dir)
    print(f"EXPLORATORY reused test: {result['correct']}/{result['n']} = {result['accuracy']:.4f}")
