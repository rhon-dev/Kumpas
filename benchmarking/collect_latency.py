#!/usr/bin/env python3
"""KUMPAS Phase 13 — Collect on-device latency benchmark results.

Runs the Android instrumented latency test via adb, parses the JSON output
from logcat, and appends the result to benchmark_history.json.

Usage:
    python collect_latency.py [--model-version VERSION] [--condition CONDITION] [--notes "..."]

Prerequisites:
    - Device connected via adb
    - App installed with androidTest APK
    - LatencyBenchmarkTest class available
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from log_utils import append_entry, make_timestamp  # noqa: E402

APP_PACKAGE = "com.kumpas.app"
TEST_CLASS = f"{APP_PACKAGE}.benchmark.LatencyBenchmarkTest"
LOGCAT_TAG = "KumpasBenchmark"


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
        # Parse total RAM
        mem_match = re.search(r"MemTotal:\s+(\d+)\s+kB", ram)
        ram_gb = f"{int(mem_match.group(1)) / 1048576:.0f}GB" if mem_match else "?GB"
        return f"{model} / {chip} / {ram_gb}"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown_device"


def clear_logcat():
    """Clear logcat buffer before test."""
    subprocess.run(["adb", "logcat", "-c"], check=False)


def run_instrumented_test() -> bool:
    """Run the latency benchmark instrumented test."""
    print("Running instrumented test...")
    result = subprocess.run(
        ["adb", "shell", "am", "instrument", "-w",
         "-e", "class", TEST_CLASS,
         f"{APP_PACKAGE}.test/androidx.test.runner.AndroidJUnitRunner"],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"Test failed: {result.stderr}")
        return False
    return "OK" in result.stdout or "PASSED" in result.stdout.upper()


def parse_logcat_results() -> dict | None:
    """Parse benchmark results from logcat."""
    result = subprocess.run(
        ["adb", "logcat", "-d", "-s", f"{LOGCAT_TAG}:I"],
        capture_output=True, text=True
    )

    # Look for JSON output tagged with our marker
    for line in result.stdout.splitlines():
        if "BENCHMARK_RESULT" in line:
            # Extract JSON between braces
            match = re.search(r"\{.*\}", line)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    continue
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model-version", default="unknown",
                    help="Model version identifier")
    ap.add_argument("--condition", default="optimal",
                    choices=["optimal", "low_light", "cluttered", "n/a"],
                    help="Environment condition")
    ap.add_argument("--notes", default="", help="Free-text notes")
    args = ap.parse_args()

    print("=" * 60)
    print("KUMPAS Latency Benchmark Collector")
    print("=" * 60)

    # Get device info
    device = get_device_info()
    print(f"Device: {device}")

    # Clear logcat and run test
    clear_logcat()
    success = run_instrumented_test()

    if not success:
        print("ERROR: Instrumented test did not pass.")
        print("Ensure the test APK is installed and the device is connected.")
        return 1

    # Parse results
    results = parse_logcat_results()
    if not results:
        print("ERROR: Could not parse benchmark results from logcat.")
        print(f"Check: adb logcat -s {LOGCAT_TAG}:I")
        return 1

    print(f"\nResults: {json.dumps(results, indent=2)}")

    # Gate check
    p95 = results.get("p95_ms", results.get("p95", 999))
    gate_pass = p95 < 150
    gate_str = "✅ PASS" if gate_pass else "❌ FAIL"
    print(f"\np95 latency: {p95:.1f}ms (gate <150ms → {gate_str})")

    # Build and append entry
    entry = {
        "timestamp": make_timestamp(),
        "benchmark_type": "latency",
        "model_version": args.model_version,
        "device": device,
        "condition": args.condition,
        "results": results,
        "gate_pass": gate_pass,
        "notes": args.notes,
    }
    append_entry(entry)
    print("Logged to benchmark_history.json")
    print("=" * 60)
    return 0 if gate_pass else 1


if __name__ == "__main__":
    sys.exit(main())
