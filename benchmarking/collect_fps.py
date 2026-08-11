#!/usr/bin/env python3
"""KUMPAS Phase 13 — Collect on-device FPS benchmark results.

Pulls the FPS benchmark JSON output from the device (written by the app's
benchmark mode) and appends it to benchmark_history.json.

Usage:
    python collect_fps.py [--model-version VERSION] [--condition CONDITION]
                          [--device-path PATH] [--notes "..."]

Prerequisites:
    - Device connected via adb
    - App has been run in benchmark mode (≥60s)
    - Results file exists at device-path
"""

import argparse
import json
import subprocess
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from log_utils import append_entry, make_timestamp  # noqa: E402

DEFAULT_DEVICE_PATH = "/sdcard/Download/kumpas_fps_benchmark.json"


def get_device_info() -> str:
    """Get device model and chip info from adb."""
    try:
        model = subprocess.check_output(
            ["adb", "shell", "getprop", "ro.product.model"],
            text=True
        ).strip()
        chip = subprocess.check_output(
            ["adb", "shell", "getprop", "ro.hardware.chipname"],
            text=True
        ).strip()
        ram = subprocess.check_output(
            ["adb", "shell", "cat", "/proc/meminfo"],
            text=True
        )
        mem_match = re.search(r"MemTotal:\s+(\d+)\s+kB", ram)
        ram_gb = f"{int(mem_match.group(1)) / 1048576:.0f}GB" if mem_match else "?GB"
        return f"{model} / {chip} / {ram_gb}"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown_device"


def pull_results(device_path: str) -> dict | None:
    """Pull FPS results JSON from device via adb."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_path = tmp.name

    result = subprocess.run(
        ["adb", "pull", device_path, tmp_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"ERROR: adb pull failed: {result.stderr}")
        print(f"Ensure the app was run in benchmark mode and the file exists at:")
        print(f"  {device_path}")
        Path(tmp_path).unlink(missing_ok=True)
        return None

    try:
        data = json.loads(Path(tmp_path).read_text())
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"ERROR: Failed to parse results: {e}")
        data = None
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return data


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model-version", default="unknown",
                    help="Model version identifier")
    ap.add_argument("--condition", default="optimal",
                    choices=["optimal", "low_light", "cluttered"],
                    help="Environment condition during benchmark")
    ap.add_argument("--device-path", default=DEFAULT_DEVICE_PATH,
                    help="Path on device to the FPS results JSON")
    ap.add_argument("--notes", default="", help="Free-text notes")
    args = ap.parse_args()

    print("=" * 60)
    print("KUMPAS FPS Benchmark Collector")
    print("=" * 60)

    # Get device info
    device = get_device_info()
    print(f"Device: {device}")
    print(f"Pulling from: {args.device_path}")

    # Pull results
    results = pull_results(args.device_path)
    if not results:
        return 1

    print(f"\nResults: {json.dumps(results, indent=2)}")

    # Validate duration
    duration = results.get("duration_s", 0)
    if duration < 60:
        print(f"WARNING: Benchmark duration {duration}s < 60s minimum. "
              "Results may not reflect sustained performance.")

    # Gate check
    mean_fps = results.get("mean_fps", 0)
    min_fps = results.get("min_fps", 0)
    gate_pass = mean_fps >= 24
    gate_str = "✅ PASS" if gate_pass else "❌ FAIL"
    print(f"\nMean FPS: {mean_fps:.1f}, Min FPS: {min_fps:.1f}")
    print(f"Gate (mean ≥24 FPS) → {gate_str}")

    # Check for degradation
    degraded = results.get("degradation_detected", False)
    if degraded:
        print("⚠️  Degradation detected: FPS dropped below 24 for >2s during the run")

    # Build and append entry
    entry = {
        "timestamp": make_timestamp(),
        "benchmark_type": "fps",
        "model_version": args.model_version,
        "device": device,
        "condition": args.condition,
        "results": results,
        "gate_pass": gate_pass,
        "notes": args.notes,
    }
    append_entry(entry)
    print("Logged to benchmark_history.json")

    # Cleanup device file
    subprocess.run(["adb", "shell", "rm", args.device_path], check=False)
    print(f"Cleaned up {args.device_path} on device")
    print("=" * 60)
    return 0 if gate_pass else 1


if __name__ == "__main__":
    sys.exit(main())
