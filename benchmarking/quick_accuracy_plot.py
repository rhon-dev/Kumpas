#!/usr/bin/env python3
"""Quick accuracy test across all model runs on the FSL-105 (50-class) test split.

Reproduces test accuracy from saved predictions (reports/*_y_pred.npy) against
the held-out y_test.npy, with no TensorFlow dependency, and renders a bar chart.

Output: benchmarking/plots/accuracy_all_runs.png
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

THESIS = Path(__file__).resolve().parents[2]
SEQ = THESIS / "kumpas-data" / "sequences"
REPORTS = THESIS / "kumpas" / "training" / "models" / "reports"
OUT = Path(__file__).resolve().parent / "plots" / "accuracy_all_runs.png"

# (run label, y_pred filename) — all experiments logged for the project
RUNS = [
    ("baseline",        "20260705_192720_baseline_y_pred.npy"),
    ("no_face\n(deployed)", "20260705_194813_no_face_y_pred.npy"),
    ("no_face_wider",   "20260705_195312_no_face_wider_y_pred.npy"),
    ("full_dropout05",  "20260705_200027_full_dropout05_y_pred.npy"),
]
GATE = 0.90

y_test = np.load(SEQ / "y_test.npy")
labels, accs = [], []
print(f"Test set: {len(y_test)} samples\n")
for label, fname in RUNS:
    y_pred = np.load(REPORTS / fname)
    acc = float((y_pred == y_test).mean())
    labels.append(label)
    accs.append(acc)
    print(f"  {label.replace(chr(10),' '):24s} {acc:.4f}  ({'PASS' if acc>=GATE else 'below gate'})")

# Plot
colors = ["#2E7D32" if a >= GATE else "#C62828" for a in accs]
fig, ax = plt.subplots(figsize=(9, 5.5))
bars = ax.bar(range(len(accs)), accs, color=colors, width=0.6, edgecolor="black", linewidth=0.5)
ax.axhline(GATE, color="#D32F2F", linestyle="--", linewidth=1.5, label=f"Gate ≥ {GATE:.0%}")

for i, (b, a) in enumerate(zip(bars, accs)):
    ax.text(b.get_x() + b.get_width() / 2, a + 0.012, f"{a:.2%}",
            ha="center", va="bottom", fontsize=11, fontweight="bold")

ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, fontsize=10)
ax.set_ylabel("Test Accuracy", fontsize=11)
ax.set_ylim(0, 1.08)
ax.set_yticks(np.arange(0, 1.01, 0.1))
ax.set_yticklabels([f"{v:.0%}" for v in np.arange(0, 1.01, 0.1)])
ax.set_title("KUMPAS — Model Accuracy on FSL-105 50-Class Test Split\n"
             f"(held-out test set, n={len(y_test)} samples, 50 classes)", fontsize=12)
ax.legend(loc="lower left", fontsize=10)
ax.grid(True, axis="y", alpha=0.3)
plt.tight_layout()

OUT.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUT, dpi=150)
plt.close()
print(f"\nSaved: {OUT}")
