#!/usr/bin/env python3
"""KUMPAS Phase 3 — evaluation report for a trained run.

Takes a run_id from experiments_log.json (default: highest test accuracy),
loads its saved test predictions, and writes the thesis-facing evaluation
artifacts:

    reports/<run_id>_eval.md          accuracy/precision/recall/F1 + confused pairs
    reports/<run_id>_confusion.png    per-class confusion matrix
    reports/<run_id>_per_class.csv    per-class metrics table

Usage:
    ~/.kumpas-venvs/tf/bin/python eval_report.py [--run-id RUN_ID]
"""

import argparse
import csv
import json
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
SEQ_DIR = REPO_ROOT.parent / "kumpas-data" / "sequences"
LOG_PATH = Path(__file__).resolve().parent / "experiments_log.json"
REPORTS_DIR = Path(__file__).resolve().parent / "reports"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-id", default=None)
    args = ap.parse_args()

    from sklearn.metrics import (classification_report, confusion_matrix,
                                 precision_recall_fscore_support)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    log = json.loads(LOG_PATH.read_text())
    run = (next(r for r in log if r["run_id"] == args.run_id) if args.run_id
           else max(log, key=lambda r: r["test_accuracy"]))
    run_id = run["run_id"]

    y_test = np.load(SEQ_DIR / "y_test.npy")
    y_pred = np.load(REPORTS_DIR / f"{run_id}_y_pred.npy")
    label_map = {int(k): v for k, v in
                 json.loads((SEQ_DIR / "label_map.json").read_text()).items()}
    names = [label_map[i]["label"] for i in range(len(label_map))]

    acc = float((y_pred == y_test).mean())
    prec, rec, f1, support = precision_recall_fscore_support(
        y_test, y_pred, labels=range(len(names)), zero_division=0)
    macro = precision_recall_fscore_support(y_test, y_pred, average="macro",
                                            zero_division=0)
    cm = confusion_matrix(y_test, y_pred, labels=range(len(names)))

    # confusion matrix figure
    fig, ax = plt.subplots(figsize=(16, 14))
    ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(names)), names, rotation=90, fontsize=7)
    ax.set_yticks(range(len(names)), names, fontsize=7)
    ax.set_xlabel("predicted"); ax.set_ylabel("true")
    ax.set_title(f"{run_id} — test accuracy {acc:.3f}")
    for i in range(len(names)):
        for j in range(len(names)):
            if cm[i, j] and i != j:
                ax.text(j, i, cm[i, j], ha="center", va="center",
                        color="red", fontsize=6)
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / f"{run_id}_confusion.png", dpi=150)

    with open(REPORTS_DIR / f"{run_id}_per_class.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["class_id", "label", "precision", "recall", "f1", "support"])
        for i, n in enumerate(names):
            w.writerow([i, n, round(prec[i], 3), round(rec[i], 3),
                        round(f1[i], 3), int(support[i])])

    pairs = sorted(((int(cm[i, j]), names[i], names[j])
                    for i in range(len(names)) for j in range(len(names))
                    if i != j and cm[i, j]), reverse=True)
    weak = sorted(range(len(names)), key=lambda i: f1[i])[:10]

    md = [
        f"# Phase 3 Evaluation — `{run_id}`",
        "",
        f"Environment: {run['environment']} | params {run['params']:,} | "
        f"features {run['features']} | seq_len {run['seq_len']} | seed {run['seed']}",
        "",
        "## Headline metrics (held-out FSL-105 test split, 203 clips)",
        "",
        f"- **Test accuracy: {acc:.4f}** (gate: ≥ 0.90 → {'PASS' if acc >= 0.9 else 'FAIL'})",
        f"- Macro precision {macro[0]:.4f} / recall {macro[1]:.4f} / F1 {macro[2]:.4f}",
        f"- Best val accuracy during training: {run['best_val_accuracy']}",
        "",
        "## Most-confused pairs (per-gesture error analysis)",
        "",
        "| n | true | predicted |", "|---|---|---|",
    ] + [f"| {n} | {a} | {b} |" for n, a, b in pairs[:15]] + [
        "",
        "## Weakest classes by F1",
        "",
        "| class | label | precision | recall | F1 | support |", "|---|---|---|---|---|---|",
    ] + [f"| {i} | {names[i]} | {prec[i]:.3f} | {rec[i]:.3f} | {f1[i]:.3f} | {int(support[i])} |"
         for i in weak] + [
        "",
        "Full table: `" + f"{run_id}_per_class.csv" + "`. "
        "Confusion matrix: `" + f"{run_id}_confusion.png" + "`.",
        "",
        "## Full classification report",
        "",
        "```",
        classification_report(y_test, y_pred, target_names=names, digits=3,
                              zero_division=0),
        "```", "",
    ]
    (REPORTS_DIR / f"{run_id}_eval.md").write_text("\n".join(md))
    print(f"acc={acc:.4f} macro_f1={macro[2]:.4f} -> reports/{run_id}_eval.md")


if __name__ == "__main__":
    main()
