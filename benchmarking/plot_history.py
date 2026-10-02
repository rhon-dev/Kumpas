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

    try:
        from collect_fps import strict_json_loads
        history = strict_json_loads(HISTORY_PATH.read_text())
    except (ValueError, OSError):
        print("History unavailable/malformed; no measured performance data.")
        return []
    if not isinstance(history, list): return []
    entries = [e for e in history if isinstance(e, dict) and e.get("benchmark_type") == btype]

    # Exclude retroactive estimates: they are hand-seeded from the Phase 4/5
    # emulator report, not measured runs, and must never appear in a thesis
    # figure. Marked on 2026-09-23 (Day 2, PR #2 Stage A3). See benchmark_history.json.
    excluded = [e for e in entries if e.get("provenance") == "retroactive-estimate"]
    if excluded:
        print(f"  (excluding {len(excluded)} retroactive-estimate entr"
              f"{'y' if len(excluded) == 1 else 'ies'} from plot)")
    entries = [e for e in entries if e.get("provenance") != "retroactive-estimate"]

    if device:
        entries = [e for e in entries if isinstance(e.get("device"), str) and device.lower() in e["device"].lower()]
    if condition:
        entries = [e for e in entries if e.get("condition") == condition]

    # Sort by timestamp
    entries.sort(key=lambda e: e.get("timestamp") if isinstance(e.get("timestamp"), str) else "")
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


def plot_no_measurements(kind: str, output_dir: Path, excluded: int = 0) -> None:
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis("off")
    ax.set_title("Camera pipeline latency" if kind == "latency" else "CameraX analyzer throughput")
    ax.text(.5, .55, "No measured camera-pipeline data available", ha="center", va="center", fontsize=17, transform=ax.transAxes)
    ax.text(.5, .35, "Physical-device acceptance remains BLOCKED\nHistorical estimates and interpreter-only diagnostics are excluded.\nRejected/malformed rows are not converted to zeros.",
            ha="center", va="center", fontsize=11, transform=ax.transAxes)
    fig.tight_layout()
    fig.savefig(output_dir / (kind + "_over_iterations.png"), dpi=150)
    plt.close(fig)


def plot_latency(entries: list[dict], output_dir: Path) -> None:
    """Only the named native analyzer/event summary; rejected values stay labelled."""
    import matplotlib.pyplot as plt
    from collect_fps import finite_number
    measured, excluded, rejected = [], 0, 0
    for e in entries:
        if not isinstance(e, dict): excluded += 1; continue
        if e.get("gate_pass") is not True: rejected += 1
        result, assessment = e.get("results"), e.get("assessment")
        if (e.get("provenance") == "retroactive-estimate" or e.get("measurement_type") != "latency" or
                not isinstance(result, dict) or result.get("schema_version") != 2 or result.get("source") != "camerax_analyzer" or
                not isinstance(assessment, dict) or assessment.get("boundary") != "final_analyzer_to_event_ms"):
            excluded += 1; continue
        summary = assessment.get("event_latency_ms")
        if not isinstance(summary, dict) or type(summary.get("n")) is not int or summary["n"] <= 0 or any(not finite_number(summary.get(k)) or summary[k] < 0 for k in ("p50", "p95")) or summary["p95"] < summary["p50"]:
            excluded += 1; continue
        status = "ACCEPTED" if e.get("gate_pass") is True else "REJECTED/DIAGNOSTIC"
        measured.append((str(e.get("device", "unknown"))[:20] + "\n" + status, summary["p95"], summary["p50"]))
    if not measured:
        plot_no_measurements("latency", output_dir, excluded)
        return
    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(measured))
    ax.bar(x, [row[1] for row in measured], width=.4, align="edge", label="p95", color="#1565C0")
    ax.bar([i - .4 for i in x], [row[2] for row in measured], width=.4, align="edge", label="p50", color="#42A5F5")
    ax.axhline(150, color="#D32F2F", linestyle="--", label="Target p95 <150ms")
    ax.set_xticks(list(x))
    ax.set_xticklabels([row[0] for row in measured], fontsize=8)
    ax.set_ylabel("Native final-analyzer-to-event latency (ms)")
    ax.set_title("Final analyzer to feedback dispatch — successful observed samples only")
    ax.text(.01, 1.02, f"REJECTED/DIAGNOSTIC rows: {rejected}; excluded/missing: {excluded}. No sensor-to-display claim.", transform=ax.transAxes, fontsize=8)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "latency_over_iterations.png", dpi=150)
    plt.close(fig)


def plot_fps(entries: list[dict], output_dir: Path) -> None:
    """Schema-v2 analyzer throughput, never event/processed/sensor/display FPS."""
    import matplotlib.pyplot as plt
    from collect_fps import finite_number
    measured, excluded, rejected = [], 0, 0
    for e in entries:
        if not isinstance(e, dict): excluded += 1; continue
        if e.get("gate_pass") is not True: rejected += 1
        result = e.get("results")
        if (e.get("provenance") == "retroactive-estimate" or e.get("measurement_type") != "fps" or
                not isinstance(result, dict) or result.get("schema_version") != 2 or result.get("source") != "camerax_analyzer"):
            excluded += 1; continue
        rates = result.get("fps")
        rate = rates.get("analyzer") if isinstance(rates, dict) else None
        bins = rate.get("per_second_samples") if isinstance(rate, dict) else None
        if not isinstance(rate, dict) or not finite_number(rate.get("mean_fps")) or rate["mean_fps"] < 0 or not isinstance(bins, list) or not bins or any(not finite_number(x) or x < 0 for x in bins):
            excluded += 1; continue
        status = "ACCEPTED" if e.get("gate_pass") is True else "REJECTED/DIAGNOSTIC"
        measured.append((str(e.get("device", "unknown"))[:20] + "\n" + str(e.get("condition", "unverified")) + "\n" + status,
                         rate["mean_fps"], min(bins)))
    if not measured:
        plot_no_measurements("fps", output_dir, excluded)
        return
    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(measured))
    ax.plot(x, [row[1] for row in measured], "o-", color="#2E7D32", label="Full-window mean analyzer FPS")
    ax.plot(x, [row[2] for row in measured], "s--", color="#FF8F00", label="Minimum one-second analyzer FPS")
    ax.axhline(24, color="#D32F2F", linestyle="--", label="Target sustained >=24 FPS (nominal 24–30)")
    ax.set_xticks(list(x))
    ax.set_xticklabels([row[0] for row in measured], fontsize=8)
    ax.set_ylabel("Analyzer callbacks per second (not detector/display FPS)")
    ax.set_title("CameraX analyzer throughput across measured runs")
    ax.text(.01, 1.02, f"REJECTED/DIAGNOSTIC rows: {rejected}; excluded/missing: {excluded}. Trailing zero bins retained.", transform=ax.transAxes, fontsize=8)
    ax.legend()
    ax.set_ylim(bottom=0)
    fig.tight_layout()
    fig.savefig(output_dir / "fps_over_iterations.png", dpi=150)
    plt.close(fig)


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
