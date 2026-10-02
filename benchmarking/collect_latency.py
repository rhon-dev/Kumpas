#!/usr/bin/env python3
"""Collect native final-analyzer-to-event latency from a schema-v2 run.

Requires --serial SERIAL --run-id RUN_ID --condition CONDITION.
--interpreter-only runs the legacy instrumentation as a separate diagnostic;
it never passes the camera/analyzer gate, even with a fast interpreter.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import collect_fps as fps
from collect_fps import validate_report, finite_number
import math

APP_PACKAGE = "com.kumpas.kumpas_app"
TEST_CLASS = f"{APP_PACKAGE}.benchmark.LatencyBenchmarkTest"
LOGCAT_TAG = "KumpasBenchmark"


def summarize(values):
    if not values:
        return {"n": 0, "p50": None, "p95": None}
    ordered = sorted(values)
    return {"n": len(values), "p50": ordered[math.ceil(len(values) * .50) - 1],
            "p95": ordered[math.ceil(len(values) * .95) - 1]}


def assess_report(report: Any, expected_run_id):
    errors = validate_report(report, expected_run_id, require_fps=False)
    event, inference, collection, ack, first_ack, trace_errors = fps.trace_samples(report, expected_run_id, require_traces=True)
    errors.extend(trace_errors)
    errors.extend(fps.validate_attempt_accounting(report, require_latency=True))
    event_summary = summarize(event)
    if event_summary["p95"] is not None and event_summary["p95"] >= 150:
        errors.append("final analyzer to event p95 must be below 150ms")
    return {"gate_pass": not errors, "rejection_reasons": errors,
            "boundary": "final_analyzer_to_event_ms", "event_latency_ms": event_summary,
            "ui_ack_upper_bound_ms": summarize(ack), "first_analyzer_to_ui_ack_upper_bound_ms": summarize(first_ack),
            "ui_ack_endpoint": "native_post_frame_ack_upper_bound_not_physical_display",
            "collection_interval_ms": summarize(collection),
            "interpreter_inference_diagnostic_ms": summarize(inference)}


def assess_interpreter_diagnostic(report: Any):
    valid = isinstance(report, dict) and type(report.get("n_inferences")) is int and report["n_inferences"] > 0
    valid = valid and all(finite_number(report.get(k)) and report[k] >= 0 for k in ("p50_ms", "p95_ms"))
    return {"gate_pass": False, "diagnostic_valid": bool(valid),
            "boundary": "interpreter_only_not_camera_pipeline",
            "rejection_reasons": ["interpreter-only timings cannot close camera/analyzer latency gate"]}


def collect_interpreter(serial):
    if fps.adb(serial, "get-state") != "device":
        raise RuntimeError("selected device is offline")
    for package in (APP_PACKAGE, APP_PACKAGE + ".test"):
        if not fps.adb(serial, "shell", "pm", "path", package).startswith("package:"):
            raise RuntimeError("missing installed package: " + package)
    device = {"serial": serial}
    for key, prop in [("model", "ro.product.model"), ("hardware", "ro.hardware"),
                      ("manufacturer", "ro.product.manufacturer"), ("fingerprint", "ro.build.fingerprint")]:
        device[key] = fps.adb(serial, "shell", "getprop", prop)
    device["is_emulator"] = serial.startswith("emulator-") or fps.is_emulator(device) or fps.adb(serial, "shell", "getprop", "ro.kernel.qemu") == "1"
    fps.adb(serial, "logcat", "-c")
    output = fps.adb(serial, "shell", "am", "instrument", "-w", "-e", "class", TEST_CLASS,
                     APP_PACKAGE + ".test/androidx.test.runner.AndroidJUnitRunner")
    errors = []
    if not re.search(r"OK \(\d+ tests?\)", output) or "FAILURES" in output or "INSTRUMENTATION_FAILED" in output:
        errors.append("interpreter instrumentation did not report a passing test")
    raw = fps.adb(serial, "logcat", "-d", "-s", LOGCAT_TAG + ":I")
    matches = re.findall(r"BENCHMARK_RESULT\s+(\{.*\})", raw)
    report = None
    if len(matches) != 1:
        errors.append("missing/ambiguous diagnostic log result")
    else:
        try:
            report = fps.strict_json_loads(matches[0])
        except ValueError as error:
            errors.append("malformed diagnostic JSON")
    if report is not None:
        report, unsafe = fps.safe_payload(report, fps.REPORT)
        if unsafe:
            errors.append("unsafe or unsupported diagnostic fields rejected")
    return {"report": report, "device": device, "collection_errors": errors}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--serial", required=True)
    ap.add_argument("--run-id", help="Required for camera report, ID returned by benchmark start")
    ap.add_argument("--interpreter-only", action="store_true", help="Legacy diagnostic only, never a camera gate")
    ap.add_argument("--model-version", default="unknown")
    ap.add_argument("--condition", required=True, choices=["optimal", "low_light", "cluttered", "n/a"])
    ap.add_argument("--notes", default="")
    args = ap.parse_args(argv)
    if not args.interpreter_only:
        if not args.run_id or args.condition == "n/a":
            ap.error("camera collection requires --run-id and a camera condition")
        collected = fps.collect(args)
        assessment = assess_report(collected["report"], args.run_id)
        return fps.log_collection(args, collected, "latency", assessment)
    try:
        collected = collect_interpreter(args.serial)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        collected = {"report": None, "raw_report": None, "device": {"serial": args.serial}, "collection_errors": [str(error)]}
    assessment = assess_interpreter_diagnostic(collected["report"])
    return fps.log_collection(args, collected, "interpreter_latency_diagnostic", assessment)


if __name__ == "__main__":
    sys.exit(main())
