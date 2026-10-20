"""Synthetic reports only; no measured device-performance claims."""
import unittest
import copy
import math
from unittest.mock import patch
import subprocess
import tempfile
from pathlib import Path
from types import SimpleNamespace
import json
import log_utils
import collect_fps as fps
import collect_latency as latency

def valid_report():
    stages = {"analyzer": 30, "selected": 8, "processed": 7, "event": 1}
    report = {
        "schema_version": 2, "run_id": "11111111-1111-4111-8111-111111111111", "package": "com.kumpas.kumpas_app",
        "source": "camerax_analyzer", "clock": "elapsedRealtimeNanos",
        "start_ns": 1_000_000_000, "end_ns": 61_000_000_000,
        "duration_s": 60, "requested_duration_s": 60, "complete": True,
        "failure_count": 0, "failures": {}, "traces": [],
        "attempts": [{"attempt_id": "22222222-2222-4222-8222-222222222222", "attempt_started_ns": 2_000_000_000}], "attempt_count": 1, "censored_count": 0,
        "outcomes": [{"attempt_id": "22222222-2222-4222-8222-222222222222", "code": "success", "at_ns": 3_100_000_000}],
        "origin": "analyzer_entry_not_sensor_exposure",
        "ui_endpoint": "post_frame_native_ack_upper_bound_not_physical_display",
        "model": {"asset": "kumpas_50sign.tflite", "sha256": "a" * 64},
        "build": {"version_code": 1, "version_name": "test", "debuggable": True},
        "device": {"is_emulator": False, "fingerprint": "physical/test/release", "model": "test phone",
                   "manufacturer": "test", "hardware": "test", "sdk_int": 34},
        "control_status": "confirmed", "fps": {}, "storage_state": "latest_published", "measurement_status": "qualified_setup",
        "setup": {"setup_id": "33333333-3333-4333-8333-333333333333", "condition": "optimal", "lux": 400, "distance_cm": 75,
                  "background": "plain", "device_fingerprint": "physical/test/release", "chip": "Snapdragon 680", "ram_gb": 4,
                  "setup_verified": True, "device_verified": True, "front_camera_verified": True,
                  "apk_sha256": "c" * 64, "revision": "b" * 40, "thermal_state": "nominal"},
        "setup_errors": [], "camera": {"selector": "default_front", "lens": "front", "bound": True, "changed": False, "camera_id": "camera2-sha256:" + "e" * 64},
    }
    for stage, rate in stages.items():
        report[stage + "_count"] = rate * 60
        report["fps"][stage] = {"count": rate * 60, "mean_fps": rate,
                                "per_second_samples": [rate] * 60}
    return report


class CollectorTestCase(unittest.TestCase):
    def setUp(self):
        quiet = patch("builtins.print")
        quiet.start()
        self.addCleanup(quiet.stop)


class FpsValidationTest(CollectorTestCase):
    def test_main_schema_requires_exact_integer_for_fps_and_latency(self):
        for value in (2, 2.0, True, False, '2', None, 1, 3):
            with self.subTest(value=repr(value)):
                report = valid_report()
                report['traces'] = [trace()]
                report['schema_version'] = value
                expected = type(value) is int and value == 2
                self.assertEqual(expected, not fps.validate_report(report, report['run_id']))
                self.assertEqual(expected, latency.assess_report(report, report['run_id'])['gate_pass'])

    def test_identity_and_elapsed_boundary_fail_closed(self):
        report = valid_report()
        self.assertEqual([], fps.validate_report(report, "11111111-1111-4111-8111-111111111111"))
        for field, value in [("schema_version", 1), ("run_id", "old"),
                             ("package", "com.kumpas.app"), ("source", "interpreter"),
                             ("clock", "dart_wall_clock"), ("complete", False),
                             ("end_ns", 62_000_000_000), ("duration_s", math.nan)]:
            with self.subTest(field=field):
                broken = copy.deepcopy(report)
                broken[field] = value
                self.assertTrue(fps.validate_report(broken, "11111111-1111-4111-8111-111111111111"))
        for malformed in [None, [], {}, {"duration_s": "60"}]:
            self.assertTrue(fps.validate_report(malformed, "11111111-1111-4111-8111-111111111111"))

    def test_empty_samples_trailing_stalls_and_emulators_fail(self):
        for change in ("empty", "missing_bin", "stall", "inflated_mean", "nan", "emulator", "missing_device"):
            with self.subTest(change=change):
                report = valid_report()
                if change == "empty":
                    report["analyzer_count"] = 0
                elif change == "missing_bin":
                    report["fps"]["analyzer"]["per_second_samples"].pop()
                elif change == "stall":
                    report["fps"]["analyzer"]["per_second_samples"][-1] = 0
                    report["fps"]["analyzer"]["mean_fps"] = 29.5
                    report["fps"]["analyzer"]["count"] = report["analyzer_count"] = 1770
                elif change == "inflated_mean":
                    report["fps"]["analyzer"]["mean_fps"] = 999
                elif change == "nan":
                    report["fps"]["analyzer"]["per_second_samples"][0] = math.nan
                elif change == "emulator":
                    report["device"]["is_emulator"] = True
                elif change == "missing_device":
                    report.pop("device")
                self.assertTrue(fps.validate_report(report, "11111111-1111-4111-8111-111111111111"))

    def test_metadata_and_trace_boundary_mismatch_rejected_for_fps(self):
        for missing in ("model", "build", "origin", "traces"):
            report = valid_report()
            del report[missing]
            self.assertTrue(fps.validate_report(report, "11111111-1111-4111-8111-111111111111"), missing)
        report = valid_report()
        report["traces"] = [trace()]
        self.assertEqual([], fps.validate_report(report, "11111111-1111-4111-8111-111111111111"))
        report["storage_error"] = "IOException"
        self.assertTrue(fps.validate_report(report, "11111111-1111-4111-8111-111111111111"))
        report.pop("storage_error")
        del report["traces"][0]["event_delivery_ns"]
        self.assertTrue(fps.validate_report(report, "11111111-1111-4111-8111-111111111111"))

    def test_malformed_field_types_never_raise_or_pass(self):
        fields = ("duration_s", "requested_duration_s", "start_ns", "end_ns", "analyzer_count",
                  "failure_count", "failures", "fps", "device", "traces")
        for field in fields:
            for value in (None, [], {}, "bad", True, -1, 10 ** 500):
                if (field == "failures" and value == {}) or (field == "traces" and value == []):
                    continue  # These are valid empty shapes for an FPS-only run.
                with self.subTest(field=field, shape=type(value).__name__):
                    report = valid_report()
                    report[field] = value
                    self.assertTrue(fps.validate_report(report, "11111111-1111-4111-8111-111111111111"))
                    self.assertFalse(latency.assess_report(report, "11111111-1111-4111-8111-111111111111")["gate_pass"])

    def test_setup_and_publication_qualification_are_required_not_model_name(self):
        changes = [('setup', None), ('storage_state', 'immutable_only_latest_unverified'),
                   ('measurement_status', 'diagnostic'), ('setup_errors', ['setup_missing'])]
        for field, value in changes:
            report = valid_report()
            report[field] = value
            with self.subTest(field=field): self.assertTrue(fps.validate_report(report, '11111111-1111-4111-8111-111111111111'))
        for field, value in [('lux', -1), ('lux', '400'), ('distance_cm', 59), ('ram_gb', 3), ('chip', 'unknown'),
                             ('device_fingerprint', 'other'), ('setup_verified', False), ('device_verified', False),
                             ('front_camera_verified', False), ('condition', 'invented'), ('apk_sha256', 'bad')]:
            report = valid_report()
            report['setup'][field] = value
            with self.subTest(field=field): self.assertTrue(fps.validate_report(report, '11111111-1111-4111-8111-111111111111'))
        for field, value in [('lens', 'back'), ('bound', False), ('changed', True), ('camera_id', 'unknown')]:
            report = valid_report()
            report['camera'][field] = value
            with self.subTest(field=field): self.assertTrue(fps.validate_report(report, '11111111-1111-4111-8111-111111111111'))

    def test_short_run_fails_closed(self):
        validate = getattr(fps, "validate_report", None)
        self.assertTrue(callable(validate), "collector needs fail-closed validation")
        errors = validate({"duration_s": 59, "mean_fps": 30}, "11111111-1111-4111-8111-111111111111")
        self.assertTrue(errors)

class AdbCollectionTest(CollectorTestCase):
    def test_second_review_acquisition_unknown_device_and_companion_contract(self):
        for kind in ('fps', 'latency', 'interpreter_latency_diagnostic'):
            for fault in ('package_throw', 'package_missing', 'package_duplicate', 'version_missing', 'device_extra', 'report_schema_float', 'schema_bool', 'schema_float', 'schema_null', 'control_extra', 'control_missing', 'control_unreadable', 'control_duplicate', 'control_malformed', 'control_status'):
                with self.subTest(kind=kind, fault=fault), tempfile.TemporaryDirectory() as directory:
                    report = valid_report()
                    report['traces'] = [trace()]
                    report.update(n_inferences=100, p50_ms=1, p95_ms=2)
                    if fault == 'report_schema_float': report['schema_version'] = 2.0
                    if fault == 'version_missing': report['build'].pop('version_name')
                    if fault == 'device_extra': report['device']['raw_video'] = 'PRIVATE_patient_text'
                    control = {'schema_version': 1, 'run_id': report['run_id'], 'status': 'confirmed'}
                    if fault == 'schema_bool': control['schema_version'] = True
                    if fault == 'schema_float': control['schema_version'] = 1.0
                    if fault == 'schema_null': control['schema_version'] = None
                    if fault == 'control_status': control['status'] = {'private': 'PRIVATE_patient_text'}
                    if fault == 'control_extra': control['private'] = 'PRIVATE_patient_text'
                    def adb(serial, *args):
                        if args == ('get-state',): return 'device'
                        if args[:3] == ('shell', 'pm', 'path'): return 'package:/data/app/base.apk'
                        if args[:2] == ('shell', 'sha256sum'): return 'c' * 64 + '  /data/app/base.apk'
                        if args[:3] == ('shell', 'dumpsys', 'package'):
                            if fault == 'package_throw': raise RuntimeError('PRIVATE_patient_text')
                            if fault == 'package_missing': return ''
                            if fault == 'package_duplicate': return 'versionName=test\nversionName=test'
                            return 'versionName=test'
                        if args[:3] == ('shell', 'run-as', fps.APP_PACKAGE):
                            if args[-1].endswith('.control.json'):
                                if fault == 'control_unreadable': raise OSError('PRIVATE_patient_text')
                                if fault == 'control_duplicate': return '{"schema_version":1,"schema_version":1,"private":"PRIVATE_patient_text"}'
                                if fault == 'control_malformed': return '{PRIVATE_patient_text'
                                if fault == 'control_missing': return '{}'
                                return json.dumps(control)
                            return json.dumps(report)
                        if args[:2] == ('logcat', '-d'): return 'BENCHMARK_RESULT ' + json.dumps(report)
                        if args[:3] == ('shell', 'am', 'instrument'): return 'OK (1 test)'
                        return {'ro.product.model': 'test phone', 'ro.product.manufacturer': 'test', 'ro.hardware': 'test', 'ro.build.fingerprint': 'physical/test/release'}.get(args[-1], '0')
                    history = Path(directory) / 'history.json'
                    args = SimpleNamespace(serial='SERIAL', run_id=report['run_id'], condition='optimal', model_version='test', notes='')
                    with patch.object(fps, 'adb', side_effect=adb), patch.object(log_utils, 'HISTORY_PATH', history):
                        collected = latency.collect_interpreter('SERIAL') if kind == 'interpreter_latency_diagnostic' else fps.collect(args)
                        self.assertNotIn('PRIVATE_patient_text', json.dumps(collected))
                        assessment = {'gate_pass': kind != 'interpreter_latency_diagnostic', 'rejection_reasons': []}
                        status = fps.log_collection(args, collected, kind, assessment)
                    self.assertEqual(1, status)
                    rows = json.loads(history.read_text())
                    self.assertNotIn('PRIVATE_patient_text', history.read_text())
                    self.assertEqual(1800, rows[0]['results']['analyzer_count'])
                    self.assertEqual(100, rows[0]['results']['traces'][0]['final_analyzer_to_event_ms'])
                    self.assertEqual('test phone', rows[0]['results']['device']['model'])
                    if kind != 'interpreter_latency_diagnostic' or not fault.startswith(('schema_', 'control_')):
                        self.assertTrue(rows[0]['rejection_reasons'])

    def test_shared_failure_codes_retain_category_and_total(self):
        report = valid_report()
        report.update(failure_count=3, failures={'SecurityException': 1, 'FileNotFoundException': 1, 'failure': 1})
        clean, unsafe = fps.safe_payload(report, fps.REPORT)
        self.assertFalse(unsafe)
        self.assertEqual(report['failures'], clean['failures'])
        self.assertEqual(sum(clean['failures'].values()), clean['failure_count'])

    def test_control_disposition_is_independent_required_scoped_evidence(self):
        report = valid_report()
        args = SimpleNamespace(serial='SERIAL', run_id=report['run_id'], condition='optimal', model_version='test')
        for control in (None, {}, {'run_id': report['run_id'], 'status': 'unconfirmed'},
                        {'run_id': 'wrong', 'status': 'confirmed'}):
            with self.subTest(control=control), patch.object(fps, 'append_entry') as saved:
                collected = {'report': report, 'device': dict(report['device'], apk_sha256='c' * 64),
                             'build': {'version_name': 'test'}, 'control': control, 'collection_errors': []}
                self.assertEqual(1, fps.log_collection(args, collected, 'fps', {'gate_pass': True, 'rejection_reasons': []}))
                self.assertEqual(1800, saved.call_args.args[0]['results']['analyzer_count'])

    def test_recognized_metadata_privacy_through_real_history(self):
        marker = 'PRIVATE_patient_text'
        fields = [('model', 'sha256'), ('setup', 'apk_sha256'), ('setup', 'revision'),
                  ('setup', 'chip'), ('device', 'model'), ('device', 'manufacturer'),
                  ('build', 'version_name'), ('camera', 'camera_id'),
                  ('device', 'hardware'), ('device', 'fingerprint'),
                  ('setup', 'setup_id'), ('setup', 'condition'), ('setup', 'background'),
                  ('setup', 'device_fingerprint'), ('setup', 'thermal_state'),
                  ('model', 'asset'), ('model', 'metadata_error'),
                  ('camera', 'lens'), ('camera', 'selector')]
        fields += [(None, key) for key in ('run_id', 'package', 'source', 'clock', 'origin',
                   'ui_endpoint', 'storage_state', 'storage_error', 'measurement_status', 'control_status')]
        for kind in ('fps', 'latency', 'interpreter_latency_diagnostic'):
            for section, field in fields:
                with self.subTest(kind=kind, section=section, field=field), tempfile.TemporaryDirectory() as directory:
                    report = valid_report()
                    report['traces'] = [trace()]
                    report.update(n_inferences=100, p50_ms=1, p95_ms=2)
                    if section is None: report[field] = marker
                    else: report[section][field] = 'Snapdragon 680PRIVATE' if field == 'chip' else marker
                    def adb(serial, *args):
                        if args == ('get-state',): return 'device'
                        if args[:3] == ('shell', 'pm', 'path'): return 'package:/data/app/base.apk'
                        if args[:2] == ('shell', 'sha256sum'): return 'c' * 64 + '  /data/app/base.apk'
                        if args[:3] == ('shell', 'dumpsys', 'package'): return 'versionName=test'
                        if args[:3] == ('shell', 'run-as', fps.APP_PACKAGE):
                            if args[-1].endswith('.control.json'): return json.dumps({'schema_version': 1, 'run_id': report['run_id'], 'status': 'confirmed'})
                            return json.dumps(report)
                        if args[:2] == ('logcat', '-d'): return 'BENCHMARK_RESULT ' + json.dumps(report)
                        if args[:3] == ('shell', 'am', 'instrument'): return 'OK (1 test)'
                        return {'ro.product.model': 'test phone', 'ro.product.manufacturer': 'test',
                                'ro.hardware': 'test', 'ro.build.fingerprint': 'physical/test/release'}.get(args[-1], '0')
                    history = Path(directory) / 'history.json'
                    args = SimpleNamespace(serial='SERIAL', run_id='11111111-1111-4111-8111-111111111111', condition='optimal', model_version='test', notes='')
                    with patch.object(fps, 'adb', side_effect=adb), patch.object(log_utils, 'HISTORY_PATH', history):
                        collected = latency.collect_interpreter('SERIAL') if kind == 'interpreter_latency_diagnostic' else fps.read_report('SERIAL')
                        assessment = latency.assess_interpreter_diagnostic(collected['report']) if kind == 'interpreter_latency_diagnostic' else latency.assess_report(collected['report'], args.run_id) if kind == 'latency' else {'gate_pass': not fps.validate_report(collected['report'], args.run_id), 'rejection_reasons': fps.validate_report(collected['report'], args.run_id)}
                        status = fps.log_collection(args, collected, kind, assessment)
                    self.assertEqual(1, status)
                    self.assertNotIn(marker, history.read_text())
                    self.assertNotIn('Snapdragon 680PRIVATE', history.read_text())
                    saved = json.loads(history.read_text())[0]['results']
                    self.assertEqual(100, saved['traces'][0]['final_analyzer_to_event_ms'])
                    self.assertEqual('test phone', saved['device']['model'])
                    self.assertEqual('physical/test/release', saved['device']['fingerprint'])

    def test_allowed_error_fields_never_persist_private_text_via_reader_and_history(self):
        marker = 'PRIVATE_SYNTHETIC_MARKER'
        for kind in ('fps', 'latency', 'interpreter_latency_diagnostic'):
            for field in ('storage_error', 'metadata_error', 'setup_errors', 'reason'):
                with self.subTest(kind=kind, field=field), tempfile.TemporaryDirectory() as directory:
                    report = valid_report()
                    report['traces'] = [trace()]
                    report.update(n_inferences=100, p50_ms=1, p95_ms=2)
                    if field == 'metadata_error': report['model'][field] = marker
                    elif field == 'setup_errors': report[field] = ['setup_missing', marker]
                    elif field == 'reason': report['excluded_samples'] = [{'attempt_id': '22222222-2222-4222-8222-222222222222', 'reason': marker, 'at_ns': 4}]
                    else: report[field] = marker
                    def adb(serial, *args):
                        if args == ('get-state',): return 'device'
                        if args[:3] == ('shell', 'pm', 'path'): return 'package:/data/app/base.apk'
                        if args[:2] == ('shell', 'sha256sum'): return 'c' * 64 + '  /data/app/base.apk'
                        if args[:3] == ('shell', 'dumpsys', 'package'): return 'versionName=test'
                        if args[:3] == ('shell', 'run-as', fps.APP_PACKAGE):
                            if args[-1].endswith('.control.json'): return json.dumps({'schema_version': 1, 'run_id': report['run_id'], 'status': 'confirmed'})
                            return json.dumps(report)
                        if args[:2] == ('logcat', '-d'): return 'BENCHMARK_RESULT ' + json.dumps(report)
                        if args[:3] == ('shell', 'am', 'instrument'): return 'OK (1 test)'
                        return 'physical/test/release'
                    history = Path(directory) / 'history.json'
                    args = SimpleNamespace(serial='SERIAL', run_id='11111111-1111-4111-8111-111111111111', condition='optimal', model_version='test', notes='')
                    with patch.object(fps, 'adb', side_effect=adb), patch.object(log_utils, 'HISTORY_PATH', history):
                        collected = latency.collect_interpreter('SERIAL') if kind == 'interpreter_latency_diagnostic' else fps.read_report('SERIAL')
                        assessment = latency.assess_interpreter_diagnostic(collected['report']) if kind == 'interpreter_latency_diagnostic' else latency.assess_report(collected['report'], args.run_id) if kind == 'latency' else {'gate_pass': not fps.validate_report(collected['report'], args.run_id), 'rejection_reasons': fps.validate_report(collected['report'], args.run_id)}
                        status = fps.log_collection(args, collected, kind, assessment)
                    self.assertEqual(1, status)
                    self.assertNotIn(marker, history.read_text())
                    self.assertNotIn('Snapdragon 680PRIVATE', history.read_text())
                    saved = json.loads(history.read_text())[0]['results']
                    self.assertEqual(100, saved['traces'][0]['final_analyzer_to_event_ms'])
                    if field == 'setup_errors': self.assertIn('setup_missing', saved['setup_errors'])

    def test_host_sink_drops_unsafe_nested_payload_and_raw_text_for_both_collectors(self):
        for kind in ('fps', 'latency', 'interpreter_latency_diagnostic'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                report = valid_report() if kind != 'interpreter_latency_diagnostic' else {'n_inferences': 100, 'p95_ms': 2, 'p50_ms': 1}
                report['raw_video'] = 'IDENTIFIABLE_MARKER'
                if kind != 'interpreter_latency_diagnostic':
                    report['traces'] = [trace()]
                    report['traces'][0]['landmarks'] = ['IDENTIFIABLE_MARKER']
                history = Path(directory) / 'history.json'
                args = SimpleNamespace(serial='SERIAL', run_id='11111111-1111-4111-8111-111111111111', model_version='test', condition='optimal', notes='')
                collected = {'report': report, 'raw_report': 'IDENTIFIABLE_MARKER', 'device': {'serial': 'SERIAL'}, 'collection_errors': []}
                with patch.object(log_utils, 'HISTORY_PATH', history):
                    status = fps.log_collection(args, collected, kind, {'gate_pass': True, 'rejection_reasons': []})
                raw = history.read_text()
                self.assertEqual(1, status)
                self.assertNotIn('IDENTIFIABLE_MARKER', raw)
                saved = json.loads(raw)[0]
                self.assertNotIn('raw_report', saved)
                self.assertNotIn('raw_video', saved['results'])
                self.assertTrue(saved['rejection_reasons'])
                if kind != 'interpreter_latency_diagnostic':
                    self.assertEqual(100, saved['results']['traces'][0]['final_analyzer_to_event_ms'])
                else:
                    self.assertEqual(2, saved['results']['p95_ms'])

    def test_real_history_append_retains_failed_and_diagnostic_rows(self):
        args = SimpleNamespace(serial="SERIAL", run_id="11111111-1111-4111-8111-111111111111", model_version="test", condition="optimal", notes="")
        for kind in ("fps", "interpreter_latency_diagnostic"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                history = Path(directory) / "history.json"
                original = {"historical_row": "must remain unchanged"}
                history.write_text(json.dumps([original]))
                with patch.object(log_utils, "HISTORY_PATH", history):
                    status = fps.log_collection(args, {"report": None, "raw_report": "malformed", "device": {"serial": "SERIAL"}, "collection_errors": ["rejected"]},
                                                kind, {"gate_pass": False, "rejection_reasons": ["no evidence"]})
                rows = json.loads(history.read_text())
                self.assertEqual(1, status)
                self.assertEqual(2, len(rows))
                self.assertEqual(original, rows[0])
                self.assertFalse(rows[1]["gate_pass"])
                self.assertEqual({}, rows[1]["results"])
                self.assertEqual(kind, rows[1]["measurement_type"])


    def test_collection_compares_condition_selected_device_and_apk_without_relabelling(self):
        for kind in ('fps', 'latency'):
            for mismatch in ('condition', 'fingerprint', 'apk', 'missing_apk', 'none'):
                report = valid_report()
                collected = {'report': report, 'device': dict(report['device'], serial='SERIAL', apk_sha256='c' * 64), 'build': {'version_name': 'test'}, 'control': {'schema_version': 1, 'run_id': report['run_id'], 'status': 'confirmed'}, 'collection_errors': []}
                condition = 'low_light' if mismatch == 'condition' else 'optimal'
                if mismatch == 'fingerprint': collected['device']['fingerprint'] = 'other'
                if mismatch == 'apk': collected['device']['apk_sha256'] = 'd' * 64
                if mismatch == 'missing_apk': collected['device'].pop('apk_sha256')
                args = SimpleNamespace(serial='SERIAL', run_id='11111111-1111-4111-8111-111111111111', condition=condition, model_version='test', notes='')
                with self.subTest(kind=kind, mismatch=mismatch), patch.object(fps, 'append_entry') as append:
                    status = fps.log_collection(args, collected, kind, {'gate_pass': True, 'rejection_reasons': []})
                    self.assertEqual(0 if mismatch == 'none' else 1, status)
                    self.assertEqual('optimal', append.call_args.args[0]['results']['setup']['condition'])

    def test_reader_parse_errors_and_interpreter_output_never_echo_raw_payload(self):
        for raw in ('{"IDENTIFIABLE_MARKER":1,"IDENTIFIABLE_MARKER":2}', '{IDENTIFIABLE_MARKER', '{"raw_video":"IDENTIFIABLE_MARKER"}'):
            def adb(serial, *args):
                if args == ('get-state',): return 'device'
                if args[:3] == ('shell', 'pm', 'path'): return 'package:/data/app/base.apk'
                if args[:3] == ('shell', 'run-as', fps.APP_PACKAGE): return raw
                if args[:2] == ('logcat', '-d'): return 'IDENTIFIABLE_MARKER unrelated log\nBENCHMARK_RESULT ' + raw
                if args[:3] == ('shell', 'am', 'instrument'): return 'OK (1 test)'
                return 'physical/test/release'
            with self.subTest(raw=raw), patch.object(fps, 'adb', side_effect=adb):
                for result in (fps.read_report('SERIAL'), latency.collect_interpreter('SERIAL')):
                    self.assertNotIn('IDENTIFIABLE_MARKER', json.dumps(result))
                    self.assertTrue(result['collection_errors'])
                    self.assertNotIn('raw_report', result)

    def test_json_rejects_duplicate_keys_and_nonfinite_values(self):
        parse = getattr(fps, "strict_json_loads", None)
        self.assertTrue(callable(parse), "JSON must not silently normalize duplicate keys/NaN")
        for raw in ('{"run_id":"old","run_id":"11111111-1111-4111-8111-111111111111"}', '{"duration_s":NaN}', '{"mean_fps":Infinity}'):
            self.assertRaises(ValueError, parse, raw)


    def test_failed_report_is_logged_and_never_deleted(self):
        main = getattr(fps, "main", None)
        self.assertTrue(callable(main), "collector CLI must log rejected runs")
        result = {"report": {"run_id": "old", "duration_s": 59}, "raw_report": "retained",
                  "device": {"serial": "SERIAL"}, "collection_errors": []}
        with patch.object(fps, "read_report", return_value=result), patch.object(fps, "append_entry") as append, patch.object(fps.subprocess, "run") as adb:
            status = main(["--serial", "SERIAL", "--run-id", "11111111-1111-4111-8111-111111111111", "--condition", "optimal"])
        self.assertEqual(1, status)
        entry = append.call_args.args[0]
        self.assertFalse(entry["gate_pass"])
        self.assertIsInstance(entry["device"], str)
        self.assertEqual("SERIAL", entry["device_metadata"]["serial"])
        self.assertNotIn("run_id", entry["results"])
        self.assertNotIn("raw_report", entry)
        self.assertTrue(entry["rejection_reasons"])
        adb.assert_not_called()


    def test_serial_and_package_are_explicit_for_every_read(self):
        read = getattr(fps, "read_report", None)
        self.assertTrue(callable(read), "read must select a serial and verify package")
        def run(command, **kwargs):
            self.assertEqual(["adb", "-s", "SERIAL"], command[:3])
            args = command[3:]
            if args == ["get-state"]:
                output = "device"
            elif args == ["shell", "pm", "path", fps.APP_PACKAGE]:
                output = "package:/data/app/base.apk"
            elif args[:2] == ["shell", "sha256sum"]:
                output = "c" * 64 + "  /data/app/base.apk"
            elif args[:3] == ["shell", "run-as", fps.APP_PACKAGE]:
                output = __import__("json").dumps(valid_report())
            else:
                output = "physical/test/release" if args[-1] == "ro.build.fingerprint" else "test"
            return subprocess.CompletedProcess(command, 0, stdout=output, stderr="")
        with patch.object(fps.subprocess, "run", side_effect=run) as calls:
            result = read("SERIAL")
        self.assertEqual("c" * 64, result["device"].get("apk_sha256"))
        self.assertEqual("11111111-1111-4111-8111-111111111111", result["report"]["run_id"])
        self.assertGreater(calls.call_count, 2)
        with patch.object(fps.subprocess, "run") as calls:
            self.assertRaises(ValueError, read, "")
            self.assertRaises(ValueError, read, "SERIAL", package="com.kumpas.app")
            calls.assert_not_called()


def trace():
    return {"attempt_id": "22222222-2222-4222-8222-222222222222", "run_id": "11111111-1111-4111-8111-111111111111", "clock": "elapsedRealtimeNanos", "attempt_started_ns": 2_000_000_000,
            "first_analyzer_ns": 2_000_000_000, "final_analyzer_ns": 3_000_000_000,
            "native_result_ns": 3_050_000_000, "event_delivery_ns": 3_100_000_000,
            "final_analyzer_to_event_ms": 100, "inference_ms": 10, "collection_ms": 1000}


class LatencyValidationTest(CollectorTestCase):
    def test_censored_and_unaccounted_slow_attempts_cannot_pass_success_only_percentiles(self):
        for change in ('censored', 'missing_census', 'missing_terminal', 'missing_start_time'):
            report = valid_report()
            report['traces'] = [trace()]
            if change == 'censored':
                report['attempts'].append({'attempt_id': 'slow', 'attempt_started_ns': 60_000_000_000})
                report['attempt_count'] = 2
                report['censored_count'] = 1
                report['outcomes'].append({'attempt_id': 'slow', 'code': 'censored_at_close', 'at_ns': report['end_ns']})
            elif change == 'missing_census': report.pop('attempts')
            elif change == 'missing_terminal': report['outcomes'] = []
            else: report['traces'][0].pop('attempt_started_ns')
            with self.subTest(change=change):
                assessed = latency.assess_report(report, '11111111-1111-4111-8111-111111111111')
                self.assertFalse(assessed['gate_pass'])
                self.assertEqual(100, assessed['event_latency_ms']['p95']) # retained conditional successful sample, not invented censor latency

    def test_half_open_deadline_and_pre_run_attempt_start_fail_closed(self):
        for change in ('event_at_end', 'ack_at_end', 'pre_run_start'):
            report = valid_report()
            t = trace()
            report['traces'] = [t]
            if change == 'event_at_end':
                t['event_delivery_ns'] = report['end_ns']
                t['final_analyzer_to_event_ms'] = (t['event_delivery_ns'] - t['final_analyzer_ns']) / 1e6
            elif change == 'ack_at_end':
                t.update(ui_ack_ns=report['end_ns'], final_analyzer_to_ui_ack_ms=58000, first_analyzer_to_ui_ack_ms=59000)
            else:
                t['attempt_started_ns'] = report['start_ns'] - 1
            with self.subTest(change=change):
                self.assertTrue(fps.trace_samples(report, '11111111-1111-4111-8111-111111111111')[5])
                self.assertFalse(latency.assess_report(report, '11111111-1111-4111-8111-111111111111')['gate_pass'])

    def test_legacy_runner_selects_serial_and_never_uses_camera_gate(self):
        runner = getattr(latency, "collect_interpreter", None)
        self.assertTrue(callable(runner), "legacy diagnostic runner must remain usable")
        commands = []
        def adb(serial, *args):
            self.assertEqual("SERIAL", serial)
            commands.append(args)
            if args[:3] == ("shell", "pm", "path"):
                return "package:/data/app/base.apk"
            if args[:3] == ("shell", "am", "instrument"):
                self.assertIn(latency.TEST_CLASS, args)
                self.assertIn("com.kumpas.kumpas_app.test/androidx.test.runner.AndroidJUnitRunner", args)
                return "OK (1 test)"
            if args[:2] == ("logcat", "-d"):
                return 'KumpasBenchmark: BENCHMARK_RESULT {"n_inferences":100,"p50_ms":1,"p95_ms":2}'
            if args == ("get-state",):
                return "device"
            return "test"
        with patch.object(fps, "adb", side_effect=adb):
            result = runner("SERIAL")
        self.assertEqual(100, result["report"]["n_inferences"])
        self.assertIn(("logcat", "-c"), commands)
        self.assertFalse(latency.assess_interpreter_diagnostic(result["report"])["gate_pass"])


    def test_camera_collector_never_runs_interpreter_test(self):
        report = valid_report()
        report["traces"] = [trace()]
        collected = {"report": report, "raw_report": "synthetic", "device": dict(report["device"], serial="SERIAL", apk_sha256="c" * 64), "build": {"version_name": "test"}, "control": {"schema_version": 1, "run_id": report["run_id"], "status": "confirmed"}, "collection_errors": []}
        with patch.object(fps, "read_report", return_value=collected), patch.object(fps, "append_entry") as log, patch.object(latency.subprocess, "run") as adb:
            try:
                status = latency.main(["--serial", "SERIAL", "--run-id", "11111111-1111-4111-8111-111111111111", "--condition", "optimal"])
            except TypeError:
                self.fail("camera collector must accept explicit serial and run ID")
        self.assertEqual(0, status)
        self.assertEqual("final_analyzer_to_event_ms", log.call_args.args[0]["assessment"]["boundary"])
        adb.assert_not_called()

    def test_interpreter_only_result_cannot_close_camera_gate(self):
        assess = getattr(latency, "assess_interpreter_diagnostic", None)
        self.assertTrue(callable(assess), "legacy measurements require diagnostic labeling")
        result = assess({"n_inferences": 100, "p50_ms": 1, "p95_ms": 2})
        self.assertFalse(result["gate_pass"])
        self.assertTrue(result["diagnostic_valid"])
        self.assertEqual("interpreter_only_not_camera_pipeline", result["boundary"])
        self.assertFalse(assess({"p95_ms": 1})["diagnostic_valid"])


    def test_oversize_ack_with_malformed_end_fails_without_overflow(self):
        report = valid_report()
        report["end_ns"] = 10 ** 500
        report["traces"] = [trace()]
        report["traces"][0]["ui_ack_ns"] = 10 ** 500
        self.assertFalse(latency.assess_report(report, "11111111-1111-4111-8111-111111111111")["gate_pass"])

    def test_trace_identity_derived_values_and_ack_validation(self):
        report = valid_report()
        report["traces"] = [trace()]
        for field, value in [("run_id", "stale"), ("attempt_id", ""),
                             ("first_analyzer_ns", 0), ("native_result_ns", 2_000_000_000),
                             ("final_analyzer_to_event_ms", 1), ("collection_ms", 1),
                             ("inference_ms", -1), ("event_delivery_ns", 65_000_000_000),
                             ("ui_ack_ns", 3_090_000_000)]:
            with self.subTest(field=field):
                broken = copy.deepcopy(report)
                broken["traces"][0][field] = value
                self.assertFalse(latency.assess_report(broken, "11111111-1111-4111-8111-111111111111")["gate_pass"])
        acknowledged = report["traces"][0]
        acknowledged.update(ui_ack_ns=3_120_000_000, final_analyzer_to_ui_ack_ms=120,
                            first_analyzer_to_ui_ack_ms=1120)
        summary = latency.assess_report(report, "11111111-1111-4111-8111-111111111111")
        self.assertTrue(summary["gate_pass"])
        self.assertEqual(120, summary["ui_ack_upper_bound_ms"]["p95"])
        acknowledged["final_analyzer_to_ui_ack_ms"] = 5
        self.assertFalse(latency.assess_report(report, "11111111-1111-4111-8111-111111111111")["gate_pass"])

    def test_missing_or_wrong_clock_boundaries_never_pass(self):
        assess = getattr(latency, "assess_report", None)
        self.assertTrue(callable(assess), "camera traces need separate latency assessment")
        report = valid_report()
        report["traces"] = [trace()]
        valid = assess(report, "11111111-1111-4111-8111-111111111111")
        self.assertTrue(valid["gate_pass"])
        self.assertEqual(100, valid["event_latency_ms"]["p95"])
        self.assertEqual(10, valid["interpreter_inference_diagnostic_ms"]["p95"])
        for field in ("first_analyzer_ns", "final_analyzer_ns", "native_result_ns", "event_delivery_ns", "clock"):
            broken = copy.deepcopy(report)
            del broken["traces"][0][field]
            self.assertFalse(assess(broken, "11111111-1111-4111-8111-111111111111")["gate_pass"], field)
        report["traces"] = []
        self.assertFalse(assess(report, "11111111-1111-4111-8111-111111111111")["gate_pass"])
        self.assertFalse(assess({"p95_ms": 1}, "11111111-1111-4111-8111-111111111111")["gate_pass"])

if __name__ == "__main__":
    unittest.main()
