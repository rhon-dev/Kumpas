#!/usr/bin/env python3
"""Collect schema-v2 CameraX analyzer throughput, retaining rejected runs.

Requires --serial SERIAL --run-id RUN_ID --condition CONDITION.
Reads com.kumpas.kumpas_app files/benchmarks/latest.json via run-as.
No images/landmarks are stored. Emulator evidence cannot pass the physical gate.
"""

import argparse
import math
import json
import subprocess
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from log_utils import append_entry, make_timestamp  # noqa: E402

APP_PACKAGE = "com.kumpas.kumpas_app"


def finite_number(value):
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def validate_setup(report, expected_condition=None):
    if not isinstance(report, dict):
        return ["missing run-bound setup"]
    errors = []
    if report.get("storage_state") != "latest_published":
        errors.append("report latest publication unverified")
    if report.get("measurement_status") != "qualified_setup" or report.get("setup_errors") != []:
        errors.append("run setup remains diagnostic or invalid")
    setup, camera = report.get("setup"), report.get("camera")
    if not isinstance(setup, dict):
        return errors + ["missing run-bound setup"]
    condition = setup.get("condition")
    if condition not in ("optimal", "low_light", "cluttered") or (expected_condition is not None and condition != expected_condition):
        errors.append("run condition mismatch or missing")
    lux = setup.get("lux")
    if not finite_number(lux) or lux < 0 or not (lux < 100 if condition == "low_light" else lux > 300):
        errors.append("invalid measured setup lux")
    if setup.get("background") != ("complex" if condition == "cluttered" else "plain"):
        errors.append("invalid setup background")
    if not finite_number(setup.get("distance_cm")) or not 60 <= setup["distance_cm"] <= 90:
        errors.append("invalid setup distance")
    if not finite_number(setup.get("ram_gb")) or not 4 <= setup["ram_gb"] <= 64:
        errors.append("unqualified device RAM")
    if not isinstance(setup.get("chip"), str) or not re.fullmatch(r"(?:Snapdragon 6[0-9]{2}[A-Za-z]*|Helio G[0-9]{2,3})", setup["chip"]):
        errors.append("unqualified device chip")
    if any(setup.get(k) is not True for k in ("setup_verified", "device_verified", "front_camera_verified")):
        errors.append("manual setup/device/front camera verification missing")
    device = report.get("device")
    if not isinstance(device, dict) or not setup.get("device_fingerprint") or setup.get("device_fingerprint") != device.get("fingerprint"):
        errors.append("run setup/device identity mismatch")
    for key, pattern in (("setup_id", r"[A-Za-z0-9_.:-]{1,128}"), ("apk_sha256", r"[0-9a-f]{64}"),
                         ("revision", r"[0-9a-f]{40}|[0-9a-f]{64}")):
        if not isinstance(setup.get(key), str) or not re.fullmatch(pattern, setup[key]):
            errors.append("invalid setup " + key)
    if setup.get("thermal_state") not in ("nominal", "fair", "serious", "critical"):
        errors.append("setup thermal state missing")
    if not isinstance(camera, dict) or camera.get("bound") is not True or camera.get("changed") is not False or camera.get("lens") != "front" or camera.get("selector") != "default_front" or not isinstance(camera.get("camera_id"), str) or camera.get("camera_id") in ("", "unknown"):
        errors.append("actual front camera unbound, changed or unverified")
    return errors


def validate_attempt_accounting(report, require_latency=False):
    if not isinstance(report, dict): return ["missing attempt census"]
    starts, outcomes = report.get("attempts"), report.get("outcomes")
    count, censored = report.get("attempt_count"), report.get("censored_count")
    if not isinstance(starts, list) or not isinstance(outcomes, list) or type(count) is not int or type(censored) is not int or count < 0 or censored < 0:
        return ["missing/malformed attempt census"]
    errors, by_id, terminals = [], {}, {}
    start, end = report.get("start_ns"), report.get("end_ns")
    for item in starts:
        if not isinstance(item, dict): errors.append("malformed attempt start"); continue
        identity, at = item.get("attempt_id"), item.get("attempt_started_ns")
        if not isinstance(identity, str) or not identity or identity in by_id or type(at) is not int or type(start) is not int or type(end) is not int or not start <= at < end:
            errors.append("invalid attempt start census")
        else: by_id[identity] = at
    codes = {'success', 'no_signer', 'cancelled', 'timeout', 'camera_error', 'persistence_failed', 'failure', 'censored_at_close'}
    for item in outcomes:
        if not isinstance(item, dict): errors.append("malformed attempt outcome"); continue
        identity, code, at = item.get("attempt_id"), item.get("code"), item.get("at_ns")
        if not isinstance(identity, str) or identity not in by_id or identity in terminals or not isinstance(code, str) or code not in codes:
            errors.append("invalid or unaccounted outcome identity/code"); continue
        if type(at) is not int or type(end) is not int or not by_id[identity] <= at <= end or (at == end and code != 'censored_at_close'):
            errors.append("outcome outside half-open window")
        terminals[identity] = code
    if count != len(by_id) or set(by_id) != set(terminals) or len(outcomes) != len(terminals) or censored != sum(code == 'censored_at_close' for code in terminals.values()):
        errors.append("attempt/outcome/censor denominator mismatch")
    if require_latency:
        if censored:
            errors.append("censored unfinished work prevents successful-only latency gate")
        traces = report.get("traces")
        trace_ids = set()
        if isinstance(traces, list):
            for trace in traces:
                if not isinstance(trace, dict): continue
                identity, at = trace.get('attempt_id'), trace.get('attempt_started_ns')
                if not isinstance(identity, str) or identity not in by_id or terminals.get(identity) != 'success' or type(at) is not int or at < by_id.get(identity, 0):
                    errors.append("trace missing started/successful attempt census")
                if isinstance(identity, str): trace_ids.add(identity)
        if {i for i, code in terminals.items() if code == 'success'} != trace_ids:
            errors.append("successful attempts missing retained latency traces")
    return errors


def validate_report(report: Any, expected_run_id, require_fps=True):
    """Return explicit rejection reasons; malformed input must never raise/pass."""
    if not isinstance(report, dict):
        return ["report must be an object"]
    errors = []
    for field, expected in [("schema_version", 2), ("run_id", expected_run_id),
                            ("package", APP_PACKAGE), ("source", "camerax_analyzer"),
                            ("clock", "elapsedRealtimeNanos")]:
        if not expected or report.get(field) != expected:
            errors.append("invalid " + field)
    errors.extend(validate_setup(report))
    errors.extend(validate_attempt_accounting(report))
    if "storage_error" in report:
        errors.append("benchmark report could not be persisted")
    if report.get("complete") is not True:
        errors.append("incomplete run")
    duration = report.get("duration_s")
    requested = report.get("requested_duration_s")
    if not finite_number(duration) or duration < 60:
        errors.append("duration below 60 seconds or malformed")
    if type(requested) is not int or requested < 60:
        errors.append("invalid requested duration")
    if finite_number(duration) and type(requested) is int and duration != requested:
        errors.append("duration does not match complete requested window")
    start, end = report.get("start_ns"), report.get("end_ns")
    if type(start) is not int or type(end) is not int or not 0 <= start < end <= 2 ** 63 - 1:
        errors.append("missing monotonic run boundaries")
    elif not finite_number(duration) or not math.isclose((end - start) / 1e9, duration, abs_tol=1e-6):
        errors.append("run boundary duration mismatch")
    device = report.get("device")
    if not isinstance(device, dict) or type(device.get("is_emulator")) is not bool:
        errors.append("missing device/emulator metadata")
    elif device["is_emulator"] or is_emulator(device):
        errors.append("emulator cannot pass physical-device gate")
    elif any(not isinstance(device.get(k), str) or not device[k].strip()
             for k in ("model", "fingerprint", "hardware", "manufacturer")):
        errors.append("incomplete device metadata")
    fps = report.get("fps")
    if not isinstance(fps, dict):
        errors.append("missing separate FPS rates")
        return errors
    for stage in ("analyzer", "selected", "processed", "event"):
        rate = fps.get(stage)
        count = report.get(stage + "_count")
        if type(count) is not int or not 0 <= count <= 2 ** 31 - 1 or not isinstance(rate, dict):
            errors.append("invalid " + stage + " count/rate")
            continue
        samples, mean = rate.get("per_second_samples"), rate.get("mean_fps")
        if rate.get("count") != count or not finite_number(mean) or mean < 0:
            errors.append("invalid " + stage + " mean/count")
        if not isinstance(samples, list) or not finite_number(duration) or duration <= 0:
            errors.append("missing " + stage + " per-second samples")
            continue
        if len(samples) != math.ceil(duration) or any(not finite_number(x) or x < 0 for x in samples):
            errors.append("invalid " + stage + " bins (including trailing zeros)")
            continue
        total = sum(x * min(1.0, duration - i) for i, x in enumerate(samples))
        if not math.isclose(total, count, abs_tol=1e-6) or not finite_number(mean) or not math.isclose(mean, count / duration, abs_tol=1e-6):
            errors.append("inconsistent " + stage + " counts/full-window denominator")
        if stage == "analyzer":
            if count == 0:
                errors.append("empty analyzer run")
            if require_fps and (any(x < 24 for x in samples) or count / duration < 24):
                errors.append("sustained analyzer throughput below 24 FPS")
    failure_count = report.get("failure_count")
    failures = report.get("failures")
    if type(failure_count) is not int or failure_count < 0 or not isinstance(failures, dict) or any(type(n) is not int or n < 0 for n in failures.values()):
        errors.append("invalid failure counters")
    elif sum(failures.values()) != failure_count:
        errors.append("failure counter mismatch")
    model, build = report.get("model"), report.get("build")
    if not isinstance(model, dict) or model.get("asset") != "kumpas_50sign.tflite" or not isinstance(model.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", model["sha256"]):
        errors.append("missing/malformed model identity")
    if not isinstance(build, dict) or type(build.get("version_code")) is not int or type(build.get("debuggable")) is not bool:
        errors.append("missing/malformed build identity")
    if report.get("origin") != "analyzer_entry_not_sensor_exposure" or report.get("ui_endpoint") != "post_frame_native_ack_upper_bound_not_physical_display":
        errors.append("missing analyzer/ACK boundary labels")
    if require_fps:
        errors.extend(trace_samples(report, expected_run_id)[5])
    return errors


def trace_samples(report: Any, expected_run_id, require_traces=False):
    errors = []
    traces = report.get("traces") if isinstance(report, dict) else None
    event, inference, collection, ack, first_ack = [], [], [], [], []
    seen = set()
    if not isinstance(traces, list):
        errors.append("missing/malformed trace array")
    elif not traces and require_traces:
        errors.append("missing camera/analyzer traces")
    else:
        for i, trace in enumerate(traces):
            if not isinstance(trace, dict) or trace.get("clock") != "elapsedRealtimeNanos":
                errors.append(f"trace {i}: missing native clock")
                continue
            names = ("first_analyzer_ns", "final_analyzer_ns", "native_result_ns", "event_delivery_ns")
            times = [trace.get(name) for name in names]
            if any(type(t) is not int or not 0 <= t <= 2 ** 63 - 1 for t in times):
                errors.append(f"trace {i}: missing monotonic boundaries")
                continue
            if times != sorted(times):
                errors.append(f"trace {i}: boundary order mismatch")
                continue
            attempt = trace.get("attempt_id")
            if not isinstance(attempt, str) or not attempt or attempt in seen or trace.get("run_id") != expected_run_id:
                errors.append(f"trace {i}: invalid/stale/duplicate identity")
            if isinstance(attempt, str):
                seen.add(attempt)
            start, end = report.get("start_ns"), report.get("end_ns")
            if type(start) is not int or type(end) is not int or times[0] < start or times[3] >= end:
                errors.append(f"trace {i}: outside run boundaries")
            started = trace.get("attempt_started_ns", times[0])
            if type(started) is not int or type(start) is not int or not start <= started <= times[0]:
                errors.append(f"trace {i}: invalid/pre-run attempt start")
            event_ms = (times[3] - times[1]) / 1e6
            collection_ms = (times[1] - times[0]) / 1e6
            def matches(field, value):
                return finite_number(trace.get(field)) and math.isclose(trace[field], value, abs_tol=1e-6)
            if not matches("final_analyzer_to_event_ms", event_ms) or not matches("collection_ms", collection_ms):
                errors.append(f"trace {i}: derived boundary mismatch")
            event.append(event_ms)
            collection.append(collection_ms)
            if not finite_number(trace.get("inference_ms")) or trace["inference_ms"] < 0 or trace["inference_ms"] > (times[2] - times[1]) / 1e6:
                errors.append(f"trace {i}: invalid interpreter diagnostic")
            else:
                inference.append(trace["inference_ms"])
            if "ui_ack_ns" in trace:
                at = trace["ui_ack_ns"]
                if type(at) is not int or not 0 <= at <= 2 ** 63 - 1 or at < times[3] or type(end) is not int or at >= end:
                    errors.append(f"trace {i}: invalid native UI ACK boundary")
                else:
                    ack_ms, first_ack_ms = (at - times[1]) / 1e6, (at - times[0]) / 1e6
                    if not matches("final_analyzer_to_ui_ack_ms", ack_ms) or not matches("first_analyzer_to_ui_ack_ms", first_ack_ms):
                        errors.append(f"trace {i}: UI ACK derived mismatch")
                    ack.append(ack_ms)
                    first_ack.append(first_ack_ms)
            elif "final_analyzer_to_ui_ack_ms" in trace or "first_analyzer_to_ui_ack_ms" in trace:
                errors.append(f"trace {i}: missing native ACK timestamp")
    return event, inference, collection, ack, first_ack, errors


def is_emulator(device):
    fingerprint = str(device.get("fingerprint", "")).lower()
    model = str(device.get("model", "")).lower()
    return fingerprint.startswith("generic") or "emulator" in fingerprint or "sdk" in model or "emulator" in model or device.get("hardware") in ("ranchu", "goldfish")


def strict_json_loads(raw):
    def reject_constant(value):
        raise ValueError("nonfinite JSON constant: " + value)
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result
    return json.loads(raw, parse_constant=reject_constant, object_pairs_hook=unique_keys)


def adb(serial, *args):
    if not isinstance(serial, str) or not re.fullmatch(r"[A-Za-z0-9_.:-]+", serial):
        raise ValueError("explicit nonempty ADB serial required")
    result = subprocess.run(["adb", "-s", serial, *args], capture_output=True, text=True, timeout=120)
    if result.returncode:
        raise RuntimeError(f"ADB {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def read_report(serial, package=APP_PACKAGE):
    """Read internal app-owned report; never remove files or use unselected ADB."""
    if package != APP_PACKAGE:
        raise ValueError("wrong package; expected " + APP_PACKAGE)
    if not serial:
        raise ValueError("explicit ADB serial required")
    if adb(serial, "get-state") != "device":
        raise RuntimeError("selected serial is not an online device")
    package_paths = adb(serial, "shell", "pm", "path", package)
    if not package_paths.startswith("package:"):
        raise RuntimeError("Kumpas package not installed on selected serial")
    device = {"serial": serial}
    errors = []
    paths = package_paths.splitlines()
    if len(paths) != 1 or not re.fullmatch(r"package:/data/app/[A-Za-z0-9_/=+~.:-]+\.apk", paths[0]):
        errors.append("installed single APK identity unavailable")
    else:
        digest_output = adb(serial, "shell", "sha256sum", paths[0][len("package:"):])
        digest = digest_output.split()[0] if digest_output.split() else ""
        if re.fullmatch(r"[0-9a-f]{64}", digest):
            device["apk_sha256"] = digest
        else:
            errors.append("installed APK digest unavailable")
    for key, prop in [("model", "ro.product.model"), ("hardware", "ro.hardware"),
                      ("manufacturer", "ro.product.manufacturer"), ("fingerprint", "ro.build.fingerprint")]:
        device[key] = adb(serial, "shell", "getprop", prop)
        if not device[key]:
            raise RuntimeError("missing device metadata: " + key)
    qemu = adb(serial, "shell", "getprop", "ro.kernel.qemu")
    device["is_emulator"] = qemu == "1" or serial.startswith("emulator-") or is_emulator(device)
    raw = adb(serial, "shell", "run-as", package, "cat", "files/benchmarks/latest.json")
    try:
        report = strict_json_loads(raw)
    except (ValueError, TypeError) as error:
        report = None
        errors.append("malformed report JSON")
    if isinstance(report, dict) and isinstance(report.get("device"), dict):
        if report["device"].get("fingerprint") != device["fingerprint"]:
            errors.append("report device does not match selected serial fingerprint")
    if device["is_emulator"]:
        errors.append("selected serial is an emulator, not physical hardware")
    if report is not None:
        report, unsafe = safe_payload(report, REPORT)
        if unsafe:
            errors.append("unsafe or unsupported report fields rejected")
    return {"report": report, "device": device, "collection_errors": errors}


def parser(description=__doc__):
    ap = argparse.ArgumentParser(description=description)
    ap.add_argument("--serial", required=True, help="Explicit ADB serial; no default device")
    ap.add_argument("--run-id", required=True, help="ID returned by this benchmark start")
    ap.add_argument("--model-version", default="unknown")
    ap.add_argument("--condition", required=True, choices=["optimal", "low_light", "cluttered"])
    ap.add_argument("--notes", default="")
    return ap


def collect(args):
    try:
        return read_report(args.serial)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        return {"report": None, "raw_report": None, "device": {"serial": args.serial},
                "collection_errors": [str(error)]}


# Only these primitive fields can cross the untrusted-report/history boundary.
NUMBER = 'number'
TEXT = 'text'
RATE = {'count': NUMBER, 'mean_fps': NUMBER, 'per_second_samples': [NUMBER]}
TRACE: dict[str, Any] = {k: NUMBER for k in ('attempt_started_ns', 'first_analyzer_ns', 'final_analyzer_ns',
    'native_result_ns', 'event_delivery_ns', 'ui_ack_ns', 'inference_ms', 'collection_ms',
    'final_analyzer_to_event_ms', 'analyzer_to_feedback_ms', 'final_analyzer_to_ui_ack_ms',
    'first_analyzer_to_ui_ack_ms')}
TRACE.update({k: TEXT for k in ('attempt_id', 'run_id', 'clock')})
DEVICE: dict[str, Any] = {k: TEXT for k in ('serial', 'model', 'manufacturer', 'hardware', 'fingerprint', 'apk_sha256')}
DEVICE.update(sdk_int=NUMBER, is_emulator=bool)
SETUP: dict[str, Any] = {k: TEXT for k in ('setup_id', 'condition', 'background', 'device_fingerprint',
    'chip', 'apk_sha256', 'revision', 'thermal_state')}
SETUP.update({k: NUMBER for k in ('lux', 'distance_cm', 'ram_gb')})
SETUP.update({k: bool for k in ('setup_verified', 'device_verified', 'front_camera_verified')})
REPORT: dict[str, Any] = {k: NUMBER for k in ('schema_version', 'start_ns', 'end_ns', 'duration_s',
    'requested_duration_s', 'analyzer_count', 'selected_count', 'processed_count',
    'event_count', 'failure_count', 'attempt_count', 'censored_count', 'n_inferences', 'mean_ms', 'median_ms', 'p50_ms', 'p95_ms', 'min_ms', 'max_ms')}
REPORT.update({k: TEXT for k in ('run_id', 'package', 'source', 'clock', 'origin',
    'ui_endpoint', 'storage_state', 'storage_error', 'measurement_status')})
REPORT.update(complete=bool, physical_fps_gate_pass=bool, device=DEVICE,
    model={'asset': TEXT, 'sha256': TEXT, 'metadata_error': TEXT},
    build={'version_code': NUMBER, 'version_name': TEXT, 'debuggable': bool},
    fps={k: RATE for k in ('analyzer', 'selected', 'processed', 'event')}, traces=[TRACE],
    failures={k: NUMBER for k in ('no_signer', 'persistence_failed', 'failure',
        'IOException', 'IllegalStateException', 'IllegalArgumentException', 'RuntimeException')},
    attempts=[{'attempt_id': TEXT, 'attempt_started_ns': NUMBER}],
    outcomes=[{'attempt_id': TEXT, 'code': TEXT, 'at_ns': NUMBER, 'attempt_started_ns': NUMBER}],
    excluded_samples=[{'attempt_id': TEXT, 'reason': TEXT, 'at_ns': NUMBER}],
    setup=SETUP, setup_errors=[TEXT], camera={'lens': TEXT, 'selector': TEXT, 'bound': bool, 'changed': bool, 'camera_id': TEXT})
SUMMARY = {'n': NUMBER, 'p50': NUMBER, 'p95': NUMBER}
ASSESSMENT: dict[str, Any] = {k: SUMMARY for k in ('event_latency_ms', 'ui_ack_upper_bound_ms',
    'first_analyzer_to_ui_ack_upper_bound_ms', 'collection_interval_ms', 'interpreter_inference_diagnostic_ms')}
ASSESSMENT.update(gate_pass=bool, diagnostic_valid=bool, boundary=TEXT,
    ui_ack_endpoint=TEXT, minimum_sustained_fps=NUMBER)


def safe_payload(value, schema) -> tuple[Any, bool]:
    """Deep-copy allowlisted primitives; never retain unknown keys or containers."""
    if isinstance(schema, dict):
        if not isinstance(value, dict):
            return {}, True
        result, unsafe = {}, bool(set(value) - set(schema))
        for key in value.keys() & schema.keys():
            copied, bad = safe_payload(value[key], schema[key])
            unsafe |= bad
            if not bad or isinstance(schema[key], (dict, list)):
                result[key] = copied
        return result, unsafe
    if isinstance(schema, list):
        if not isinstance(value, list) or len(value) > 10000:
            return [], True
        result, unsafe = [], False
        for item in value:
            copied, bad = safe_payload(item, schema[0])
            unsafe |= bad
            if not bad or isinstance(schema[0], dict):
                result.append(copied)
        return result, unsafe
    valid = (value is None or
             (schema == NUMBER and finite_number(value)) or
             (schema == TEXT and isinstance(value, str) and len(value) <= 256 and '\n' not in value) or
             (schema is bool and type(value) is bool))
    return (value, False) if valid else (None, True)


def log_collection(args, collected, benchmark_type, assessment):
    report, unsafe = safe_payload(collected.get("report") or {}, REPORT)
    device, device_unsafe = safe_payload(collected.get("device") or {}, DEVICE)
    clean_assessment, assessment_unsafe = safe_payload({k: v for k, v in assessment.items() if k != "rejection_reasons"}, ASSESSMENT)
    errors = (["collection read rejected"] if collected.get("collection_errors") else []) + assessment["rejection_reasons"]
    if benchmark_type != "interpreter_latency_diagnostic":
        errors.extend(validate_setup(report, args.condition))
        if not isinstance(report.get("device"), dict) or report["device"].get("fingerprint") != device.get("fingerprint"):
            errors.append("selected device/report fingerprint mismatch")
        if not isinstance(report.get("setup"), dict) or not device.get("apk_sha256") or report["setup"].get("apk_sha256") != device["apk_sha256"]:
            errors.append("selected installed APK/setup identity mismatch")
    if unsafe or device_unsafe or assessment_unsafe:
        errors.append("unsafe or unsupported report fields rejected")
    gate = assessment["gate_pass"] and not errors
    clean_assessment["gate_pass"] = gate
    entry = {"timestamp": make_timestamp(), "benchmark_type": "latency" if benchmark_type == "interpreter_latency_diagnostic" else benchmark_type,
             "measurement_type": benchmark_type,
             "model_version": args.model_version,
             "device": " / ".join(str(device[k]) for k in ("model", "hardware", "serial") if k in device),
             "device_metadata": device,
             "condition": args.condition, "expected_run_id": args.run_id,
             "results": report,
             "assessment": clean_assessment, "gate_pass": gate, "rejection_reasons": errors,
             "notes": ""}
    append_entry(entry)
    print(json.dumps({"gate_pass": gate, "rejection_reasons": errors, "assessment": assessment}, indent=2))
    return 0 if gate else 1


def main(argv=None):
    args = parser().parse_args(argv)
    collected = collect(args)
    errors = validate_report(collected["report"], args.run_id)
    return log_collection(args, collected, "fps", {"gate_pass": not errors, "rejection_reasons": errors,
                            "boundary": "camerax_analyzer_entry_throughput", "minimum_sustained_fps": 24})


if __name__ == "__main__":
    sys.exit(main())
