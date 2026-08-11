#!/usr/bin/env python3
"""KUMPAS Phase 13 — Plot benchmark history for thesis figures.

Reads benchmark_history.json and generates iteration-over-iteration plots
for accuracy, latency, and FPS metrics.

Usage:
    python plot_history.py [--type accuracy|latency|fps|all]
                           [--device DEVICE] [--condition CONDITION]
                           [--output-dir DIR]

Outputs PNGs to benchmarking/plots/ by default.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

BENCHMARKING_DIR = Path(__file__).resolve().parent
HISTORY_PATH = BENCHMARKING_DIR / "benchmark_history.json"
DEFAULT_OUTPUT = BENCHMARKING_DIR / "plots"

# Targets from spec
TARGETS = {
    "accuracy": 0.90,
    "latency_p95_ms": 150.0,
    "fps_min": 24.0,
}


def load_and_filter(btype: str, device: str | None, condition: str | None) -> list[dict]:
    """Load history and filter by type, device, condition."""
    if not HISTORY_PATH.exists():
        print(f"Error: {HISTORY_PATH} not found. Run a benchmark first.")
        sys.exit(1)

    history = json.loads(HISTORY_PATH.read_text())
    entries = [e for e in history if e["benchmark_type"] == btype]

    if device:
        entries = [e for e in entries if device.lower() in e.get("device", "").lower()]
    if condition:
        entries = [e for e in entries if e.get("condition") == condition]

    # Sort by timestamp
    entries.sort(key=lambda e: e.get("timestamp", ""))
    return entries


def plot_accuracy(entries: list[dict], output_dir: Path) -> None:
    """Plot accuracy over iterations."""
    import matplotlib.pyplot as plt

    if not entries:
        print("No accuracy entries found. Skipping.")
        return

    labels = [e.get("model_version", e["timestamp"][:10]) for e in entries]
    values = [e["results"]["accuracy"] for e in entries]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(range(len(values)), values, "o-", color="#2E7D32", linewidth=2, markersize=8)
    ax.axhline(y=TARGETS["accuracy"], color="#D32F2F", linestyle="--", linewidth=1.5,
               label=f"Target ≥{TARGETS['accuracy']:.0%}")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Test Accuracy")
    ax.set_xlabel("Model Version")
    ax.set_title("Accuracy Across Model Iterations")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    out = output_dir / "accuracy_over_iterations.png"
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  → {out}")


def plot_latency(entries: list[dict], output_dir: Path) -> None:
    """Plot latency p95 over iterations."""
    import matplotlib.pyplot as plt

    if not entries:
        print("No latency entries found. Skipping.")
        return

    labels = []
    p95_values = []
    median_values = []

    for e in entries:
        r = e["results"]
        labels.append(f"{e.get('device', '?')[:20]}\n{e['timestamp'][:10]}")
        p95_values.append(r.get("p95_ms", r.get("p95", 0)))
        median_values.append(r.get("median_ms", r.get("p50_ms", r.get("median", 0))))

    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(labels))
    ax.bar(x, p95_values, width=0.4, align="edge", color="#1565C0", alpha=0.8, label="p95")
    ax.bar([i - 0.4 for i in x], median_values, width=0.4, align="edge",
           color="#42A5F5", alpha=0.8, label="Median")
    ax.axhline(y=TARGETS["latency_p95_ms"], color="#D32F2F", linestyle="--",
               linewidth=1.5, label=f"Target p95 <{TARGETS['latency_p95_ms']:.0f}ms")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("Latency (ms)")
    ax.set_xlabel("Device / Date")
    ax.set_title("Inference Latency Across Runs")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()

    out = output_dir / "latency_over_iterations.png"
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  → {out}")


def plot_fps(entries: list[dict], output_dir: Path) -> None:
    """Plot sustained FPS over iterations."""
    import matplotlib.pyplot as plt

    if not entries:
        print("No FPS entries found. Skipping.")
        return

    labels = []
    mean_fps = []
    min_fps = []

    for e in entries:
        r = e["results"]
        labels.append(f"{e.get('device', '?')[:20]}\n{e.get('condition', 'n/a')}")
        mean_fps.append(r.get("mean_fps", 0))
        min_fps.append(r.get("min_fps", 0))

    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(labels))
    ax.plot(x, mean_fps, "o-", color="#2E7D32", linewidth=2, markersize=8, label="Mean FPS")
    ax.plot(x, min_fps, "s--", color="#FF8F00", linewidth=1.5, markersize=6, label="Min FPS")
    ax.axhline(y=TARGETS["fps_min"], color="#D32F2F", linestyle="--",
               linewidth=1.5, label=f"Target ≥{TARGETS['fps_min']:.0f} FPS")
    ax.axhline(y=30, color="#388E3C", linestyle=":", linewidth=1, alpha=0.5, label="30 FPS cap")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("Frames Per Second")
    ax.set_xlabel("Device / Condition")
    ax.set_title("Sustained FPS Across Runs")
    ax.set_ylim(0, max(max(mean_fps, default=30) * 1.1, 35))
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    out = output_dir / "fps_over_iterations.png"
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"  → {out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--type", choices=["accuracy", "latency", "fps", "all"],
                    default="all", help="Which benchmark type to plot")
    ap.add_argument("--device", default=None, help="Filter by device name (substring)")
    ap.add_argument("--condition", default=None, help="Filter by condition")
    ap.add_argument("--output-dir", default=None, help="Output directory for PNGs")
    args = ap.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT
    output_dir.mkdir(parents=True, exist_ok=True)

    print("KUMPAS Benchmark History Plots")
    print(f"Output: {output_dir}")
    print()

    types = ["accuracy", "latency", "fps"] if args.type == "all" else [args.type]

    for btype in types:
        entries = load_and_filter(btype, args.device, args.condition)
        print(f"[{btype}] {len(entries)} entries")
        if btype == "accuracy":
            plot_accuracy(entries, output_dir)
        elif btype == "latency":
            plot_latency(entries, output_dir)
        elif btype == "fps":
            plot_fps(entries, output_dir)

    print("\nDone.")


if __name__ == "__main__":
    main()
