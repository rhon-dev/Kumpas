"""Bound executed-native host fixtures; never invoke real ADB/devices."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / 'benchmarking/host_fixture_replay.py'

# Match discovery's sibling-import layout for package-qualified unittest runs.
if str(TOOL.parent) not in sys.path:
    sys.path.insert(0, str(TOOL.parent))


class HostProducerReplayTest(unittest.TestCase):
    def test_bundle_transfers_verified_bytes_not_stale_boolean(self):
        import base64
        result = subprocess.run([sys.executable, str(TOOL), 'bundle'], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        bundle = json.loads(result.stdout)
        self.assertEqual(set(bundle['payload_base64']), set(bundle['receipt']['artifacts']))
        for name, encoded in bundle['payload_base64'].items():
            raw = base64.b64decode(encoded, validate=True)
            self.assertEqual(hashlib.sha256(raw).hexdigest(), bundle['receipt']['artifacts'][name]['sha256'])

    def test_replay_refuses_lexical_escape_before_creating_any_directory(self):
        from unittest.mock import patch
        import host_fixture_replay as replay
        escaped = ROOT / replay.BASE / 'a3b/../not-a3b'
        with patch.object(Path, 'mkdir', side_effect=AssertionError('unexpected_write')):
            with self.assertRaisesRegex(replay.Rejected, 'unsafe_output_root'):
                replay.replay(escaped)

    def test_replay_exact_readers_to_real_isolated_history(self):
        import tempfile
        with tempfile.TemporaryDirectory(prefix='a3b-reader-') as folder:
            output = Path(folder) / 'replay'
            result = subprocess.run([sys.executable, str(TOOL), 'replay', '--output', str(output)],
                                    cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            ledger = json.loads((output / 'replay-ledger.json').read_bytes())
            rows = json.loads((output / 'synthetic-history.json').read_bytes())
            self.assertEqual(len(rows), 6)
            self.assertEqual(len(ledger['observations']), 6)
            for row in rows:
                self.assertEqual(row['results']['analyzer_count'], 1800)
                self.assertEqual(len(row['results']['traces']), 1)
                self.assertEqual(row['results']['traces'][0]['inference_ms'], 1)
                self.assertIn(row['expected_run_id'], {x['run_id'] for x in ledger['observations']})
                self.assertFalse(row['gate_pass'], 'synthetic fixture is not physical evidence')
            self.assertTrue(ledger['synthetic_origin'])
            self.assertTrue(all(x['report_transport_sha256'] == x['artifact_sha256'] for x in ledger['observations']))

    def test_pinned_preflight_emits_verified_payload_hashes(self):
        result = subprocess.run([sys.executable, str(TOOL), 'preflight'],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt['run_id'], '323291af-c067-46dc-bae1-067d62fab10b')
        self.assertEqual(len(receipt['artifacts']), 11)
        self.assertEqual(receipt['source_count'], 42)
        self.assertEqual(receipt['producer_tests'], 5)
        for name, artifact in receipt['artifacts'].items():
            raw = (Path(receipt['fixture_root']) / name).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), artifact['sha256'])


class CollectorFaultCoverage(unittest.TestCase):
    """Coverage-only existing collector behavior; mutations never touch originals."""
    @classmethod
    def setUpClass(cls):
        import host_fixture_replay as replay
        cls.replay = replay
        cls.receipt, cls.payload = replay.validate()

    def exercise(self, raw=None, control: str | bytes | None = 'original', fault=None, direct=False, interpreter=False):
        import contextlib
        import io
        import tempfile
        from types import SimpleNamespace
        from unittest.mock import patch
        import collect_fps as fps
        import collect_latency as latency
        import log_utils
        raw = raw if raw is not None else self.payload['confirmed-report.json']
        companion = self.payload['confirmed-control.json'] if control == 'original' else control
        transport = self.replay.SyntheticTransport(raw, companion, fault)
        args = SimpleNamespace(serial='synthetic-a3b', run_id=json.loads(raw)['run_id'],
                               condition='optimal', model_version='synthetic-native-a3b', notes='')
        with tempfile.TemporaryDirectory(prefix='a3b-fault-') as folder:
            history = Path(folder) / 'history.json'
            with patch.object(fps, 'adb', transport), patch('subprocess.run', side_effect=AssertionError('real_subprocess_forbidden')), patch.object(log_utils, 'HISTORY_PATH', history), contextlib.redirect_stdout(io.StringIO()):
                if interpreter:
                    collected = latency.collect_interpreter(args.serial)
                elif direct:
                    report = json.loads(raw)
                    collected = {'report': report, 'control': json.loads(companion) if companion else None,
                                 'device': dict(report['device'], serial=args.serial, apk_sha256=report['setup']['apk_sha256']),
                                 'build': report['build'], 'collection_errors': []}
                else:
                    collected = fps.collect(args)
                assessment = latency.assess_interpreter_diagnostic(collected['report']) if interpreter else latency.assess_report(collected['report'], args.run_id)
                result = fps.log_collection(args, collected, 'interpreter_latency_diagnostic' if interpreter else 'latency', assessment)
            rows = json.loads(history.read_bytes())
            self.assertEqual(len(rows), 1)
            self.assertEqual(result, 1)
            self.assertFalse(rows[0]['gate_pass'])
            self.assertNotIn('PRIVATE', json.dumps(rows))
            return collected, rows[0], assessment, transport

    def test_exact_native_report_and_control_values_retained(self):
        collected, row, assessment, transport = self.exercise()
        self.assertEqual(collected['control']['status'], 'confirmed')
        self.assertEqual(row['results']['analyzer_count'], 1800)
        self.assertEqual(row['results']['device']['model'], 'robolectric')
        self.assertEqual(assessment['event_latency_ms'], {'n': 1, 'p50': 50, 'p95': 50})
        self.assertEqual(assessment['interpreter_inference_diagnostic_ms']['p95'], 1)
        self.assertIn('report latest publication unverified', row['rejection_reasons'])
        self.assertEqual(transport.read_hashes, [self.replay.sha(self.payload['confirmed-report.json'])])

    def test_control_schema_identity_and_missing_reader_and_direct_sink(self):
        original = json.loads(self.payload['confirmed-control.json'])
        controls: list[bytes | None] = [None]
        for changes in ({'schema_version': 1.0}, {'schema_version': True}, {'run_id': '00000000-0000-0000-0000-000000000000'}, {'status': 'PRIVATE'}, {'extra': 'PRIVATE'}):
            controls.append(json.dumps(dict(original, **changes)).encode())
        for direct in (False, True):
            for control in controls:
                with self.subTest(direct=direct, control=control):
                    collected, row, _, _ = self.exercise(control=control, direct=direct)
                    if not direct:
                        self.assertIsNone(collected['control'])
                        self.assertTrue(collected['collection_errors'])
                    self.assertEqual(row['results']['analyzer_count'], 1800)
                    self.assertIn('authoritative benchmark control disposition missing or unconfirmed', row['rejection_reasons'])

    def test_report_schema_and_private_text_rejected_at_reader_and_sink(self):
        for direct in (False, True):
            for value in (2.0, True, '2', None, [], 1):
                raw = json.loads(self.payload['confirmed-report.json'])
                raw['schema_version'] = value
                raw['storage_error'] = 'PRIVATE'
                raw['model']['metadata_error'] = 'PRIVATE'
                raw['setup_errors'] = ['PRIVATE']
                with self.subTest(direct=direct, schema=value):
                    collected, row, assessment, _ = self.exercise(raw=json.dumps(raw).encode(), direct=direct)
                    self.assertTrue(assessment['rejection_reasons'])
                    self.assertEqual(row['results']['analyzer_count'], 1800)
                    self.assertIn('unsafe or unsupported report fields rejected' if direct else 'collection read rejected', row['rejection_reasons'])
                    if not direct:
                        self.assertIn('unsafe or unsupported report fields rejected', collected['collection_errors'])
                    self.assertNotIn('storage_error', row['results'])
                    if not direct:
                        self.assertNotIn('PRIVATE', json.dumps(collected))

    def test_package_and_metadata_acquisition_failures_no_report_fabricated(self):
        for fault in ('package', 'acquisition'):
            collected, row, _, _ = self.exercise(fault={fault: True})
            self.assertIsNone(collected['report'])
            self.assertNotIn('analyzer_count', row['results'])
            self.assertTrue(row['rejection_reasons'])

    def test_fixed_diagnostics_preserve_native_counts_and_traces(self):
        for direct in (False, True):
            report = json.loads(self.payload['confirmed-report.json'])
            report['storage_error'] = 'IOException'
            report['model']['metadata_error'] = 'metadata_failed'
            collected, row, _, _ = self.exercise(raw=json.dumps(report).encode(), direct=direct)
            self.assertEqual(row['results']['storage_error'], 'IOException')
            self.assertEqual(row['results']['model']['metadata_error'], 'metadata_failed')
            self.assertEqual(row['results']['analyzer_count'], 1800)
            self.assertEqual(row['results']['traces'][0]['final_analyzer_to_event_ms'], 50)
            self.assertIn('benchmark report could not be persisted', row['rejection_reasons'])

    def test_build_failure_preserves_safe_counts_and_rejects_trust(self):
        collected, row, _, _ = self.exercise(fault={'build': True})
        self.assertEqual(row['results']['analyzer_count'], 1800)
        self.assertIn('installed package metadata unavailable', collected['collection_errors'])
        self.assertNotIn('version_name', row['results']['build'])

    def test_interpreter_reader_native_report_is_diagnostic_not_fabricated_timing(self):
        collected, row, assessment, transport = self.exercise(interpreter=True)
        self.assertEqual(row['results']['analyzer_count'], 1800)
        self.assertEqual(row['results']['traces'][0]['inference_ms'], 1)
        self.assertFalse(assessment['diagnostic_valid'], 'camera report has no interpreter-only census')
        self.assertEqual(row['measurement_type'], 'interpreter_latency_diagnostic')
        self.assertIn('interpreter-only timings cannot close camera/analyzer latency gate', row['rejection_reasons'])
        normalized = self.payload['confirmed-report.json'].replace(b'\n', b'')
        self.assertEqual(transport.read_hashes, [self.replay.sha(normalized)])
        self.assertEqual(json.loads(normalized), json.loads(self.payload['confirmed-report.json']))


class PreflightNegatives(unittest.TestCase):
    def setUp(self):
        import tempfile
        import shutil
        import host_fixture_replay as replay
        self.replay = replay
        self.temp = tempfile.TemporaryDirectory(prefix='a3b-negative-')
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name) / replay.RUN
        shutil.copytree(ROOT / replay.MANIFEST.parent, self.folder)
        self.manifest = self.folder / 'manifest.json'

    def check(self, mutate=None, code=None, **kwargs):
        if mutate:
            data = json.loads(self.manifest.read_bytes())
            mutate(data)
            self.manifest.write_text(json.dumps(data))
        digest = hashlib.sha256(self.manifest.read_bytes()).hexdigest()
        with self.assertRaises(self.replay.Rejected) as error:
            self.replay.validate(self.manifest, expected_digest=digest, **kwargs)
        self.assertRegex(str(error.exception), '^[a-z_]+$')
        if code:
            self.assertEqual(str(error.exception), code)

    def test_manifest_schema_rejects_float_and_boolean(self):
        for value in (1.0, True, '1', None, 2):
            with self.subTest(value=value):
                self.check(lambda d: d.update(test_schema_version=value), 'manifest_schema')

    def test_pinned_digest_cannot_bless_changed_real_manifest(self):
        self.manifest.write_bytes(self.manifest.read_bytes() + b' ')
        with self.assertRaisesRegex(self.replay.Rejected, 'manifest_digest_mismatch'):
            self.replay.validate(self.manifest)

    def test_duplicate_json_key(self):
        self.manifest.write_bytes(self.manifest.read_bytes().replace(b'"test_schema_version": 1', b'"test_schema_version":1,"test_schema_version":1'))
        self.check(code='duplicate_json_key')

    def test_wrong_run(self):
        self.check(lambda d: d.update(run_id='00000000-0000-0000-0000-000000000000'), 'manifest_run')

    def test_failed_and_nonsynthetic_producer(self):
        for field, value in [('producer_outcome', 'failure'), ('synthetic_origin', 1)]:
            original = self.manifest.read_bytes()
            self.check(lambda d: d.update({field: value}), 'producer_outcome')
            self.manifest.write_bytes(original)

    def test_duplicate_and_wrong_artifact_identities(self):
        self.check(lambda d: d['artifacts'].__setitem__(1, d['artifacts'][0]), 'artifact_identity')

    def test_wrong_artifact_kind(self):
        self.check(lambda d: d['artifacts'][0].update(kind='export'), 'artifact_identity')

    def test_escaping_artifact(self):
        self.check(lambda d: d['artifacts'][0].update(path='../private.json'), 'artifact_identity')

    def test_missing_artifact(self):
        (self.folder / 'attempt-event.json').unlink()
        self.check(code='missing_regular_file')

    def test_tampered_artifact(self):
        with (self.folder / 'attempt-event.json').open('ab') as f:
            f.write(b' ')
        self.check(code='artifact_digest_mismatch')

    def test_symlink_artifact(self):
        target = self.folder / 'attempt-event.json'
        target.unlink()
        target.symlink_to(ROOT / self.replay.MANIFEST.parent / 'attempt-event.json')
        self.check(code='symlink_path')

    def test_float_artifact_size(self):
        self.check(lambda d: d['artifacts'][0].update(bytes=759.0), 'artifact_length')

    def test_source_escape_and_digest_mismatch(self):
        self.check(lambda d: d['source_hashes'].__setitem__('../escape', d['source_hashes'].pop(next(iter(d['source_hashes'])))), 'invalid_path')

    def test_source_snapshot_tampered(self):
        self.check(lambda d: d['source_hashes'].__setitem__(next(iter(d['source_hashes'])), '0' * 64), 'source_digest_mismatch')

    def test_failed_skipped_and_wrong_stdout_producer(self):
        binding = json.loads((ROOT / self.replay.BINDING).read_bytes())
        original = (ROOT / binding['producer_xml']).read_bytes()
        for before, after in [(b'failures="0"', b'failures="1"'), (b'skipped="0"', b'skipped="1"'), (self.replay.RUN.encode(), b'00000000-0000-0000-0000-000000000000')]:
            xml = Path(self.temp.name) / 'producer.xml'
            xml.write_bytes(original.replace(before, after))
            self.check(producer_xml=xml)

    def test_producer_target_must_have_executed(self):
        binding = json.loads((ROOT / self.replay.BINDING).read_bytes())
        original = (ROOT / binding['producer_xml']).read_bytes()
        xml = Path(self.temp.name) / 'producer.xml'
        xml.write_bytes(original.replace(b'executedStudyAndBenchmarkProducer', b'unrelatedSuccessfulTest'))
        self.check(producer_xml=xml, code='producer_target_missing')

    def test_source_symlink_component_refused(self):
        repo = Path(self.temp.name) / 'repo'
        repo.mkdir()
        (repo / 'app').symlink_to(ROOT / 'app', target_is_directory=True)
        self.check(repo=repo, code='symlink_path')

    def test_deeper_payload_identity_and_schema(self):
        for name, field, value in [('study.json', 'run_id', 'stale'),
                                   ('study.json', 'test_schema_version', 1.0),
                                   ('confirmed-control.json', 'schema_version', True),
                                   ('confirmed-control.json', 'run_id', 'stale'),
                                   ('confirmed-report.json', 'schema_version', 2.0),
                                   ('confirmed-report.json', 'run_id', 'stale')]:
            original_manifest = self.manifest.read_bytes()
            target = self.folder / name
            original_payload = target.read_bytes()
            obj = json.loads(original_payload)
            obj[field] = value
            data = json.dumps(obj).encode()
            target.write_bytes(data)
            def update(m):
                next(a for a in m['artifacts'] if a['path'] == name).update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
            self.check(update)
            target.write_bytes(original_payload)
            self.manifest.write_bytes(original_manifest)

    def test_nonobject_payload_has_fixed_rejection(self):
        for name, code in [('study.json', 'payload_type'), ('confirmed-report.json', 'report_type'), ('confirmed-control.json', 'control_type')]:
            original_manifest = self.manifest.read_bytes()
            target = self.folder / name
            original_payload = target.read_bytes()
            target.write_bytes(b'[]')
            def update(m):
                next(a for a in m['artifacts'] if a['path'] == name).update(bytes=2, sha256=hashlib.sha256(b'[]').hexdigest())
            self.check(update, code=code)
            target.write_bytes(original_payload)
            self.manifest.write_bytes(original_manifest)

    def test_ledger_nonzero_bool_and_wrong_sources(self):
        binding = json.loads((ROOT / self.replay.BINDING).read_bytes())
        original = [json.loads(x) for x in (ROOT / binding['producer_ledger']).read_bytes().splitlines()]
        for field, value in [('exit', 1), ('exit', False), ('source_hashes', {}) , ('fixture_outputs', [])]:
            import copy
            rows = copy.deepcopy(original)
            row = next(x for x in rows if x.get('label') == binding['producer_label'])
            row[field] = value
            ledger = Path(self.temp.name) / 'ledger.jsonl'
            ledger.write_text('\n'.join(json.dumps(x) for x in rows))
            self.check(producer_ledger=ledger, code='producer_ledger_mismatch')


class ProducerLedgerCliTypes(unittest.TestCase):
    """F1: malformed JSON substitutions in memory; original evidence untouched."""
    def invoke(self, action, field=None, value=None):
        import contextlib
        import io
        from unittest.mock import patch
        import host_fixture_replay as replay
        binding = json.loads((ROOT / replay.BINDING).read_bytes())
        ledger_path = ROOT / binding['producer_ledger']
        rows = [json.loads(line) for line in ledger_path.read_bytes().splitlines()]
        if field is not None:
            row = next(row for row in rows if row.get('label') == binding['producer_label'])
            row[field] = value
        replacement = '\n'.join(json.dumps(row) for row in rows).encode()
        original_read = replay.read_regular

        def read(base, relative):
            if Path(base) / relative == ledger_path:
                return replacement
            return original_read(base, relative)

        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(replay, 'read_regular', side_effect=read), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = replay.main([action])
        return code, stdout.getvalue(), stderr.getvalue()

    def assert_bad_field(self, field, required):
        marker = 'PRIVATE_LEDGER_TYPE_MARKER'
        # Strings/objects retain membership targets to reproduce the bug, as do
        # mixed lists: rejection must validate the entire container first.
        values = [' '.join(required + [marker]),
                  dict.fromkeys(required + [marker], marker),
                  7, 1.5, True, False, None, [],
                  *[required + [value] for value in (7, True, False, None, {marker: marker}, [marker])]]
        for action in ('preflight', 'bundle'):
            for index, value in enumerate(values):
                with self.subTest(action=action, field=field, case=index):
                    code, stdout, stderr = self.invoke(action, field, value)
                    self.assertEqual(code, 2, 'malformed ledger must not succeed')
                    self.assertEqual(stdout, '', 'no receipt or bundle may escape')
                    self.assertEqual(json.loads(stderr), {'error_code': 'producer_ledger_mismatch'})
                    self.assertNotIn(marker, stdout + stderr)

    def test_command_requires_string_array_at_public_cli(self):
        self.assert_bad_field('command', ['--tests', 'com.kumpas.kumpas_app.HostStudyFlowTest'])

    def test_fixture_outputs_requires_string_array_at_public_cli(self):
        import host_fixture_replay as replay
        self.assert_bad_field('fixture_outputs', ['HOST_STUDY_FIXTURE_MANIFEST ' + str(ROOT / replay.MANIFEST)])

    def test_unchanged_valid_ledger_and_string_arrays_still_succeed(self):
        import host_fixture_replay as replay
        for action in ('preflight', 'bundle'):
            for field, value in [(None, None),
                                 ('command', ['--tests', 'com.kumpas.kumpas_app.HostStudyFlowTest', 'extra-safe-argument']),
                                 ('fixture_outputs', ['extra-safe-line', 'HOST_STUDY_FIXTURE_MANIFEST ' + str(ROOT / replay.MANIFEST)])]:
                with self.subTest(action=action, field=field):
                    code, stdout, stderr = self.invoke(action, field, value)
                    self.assertEqual(code, 0, stderr)
                    self.assertEqual(stderr, '')
                    result = json.loads(stdout)
                    receipt = result['receipt'] if action == 'bundle' else result
                    self.assertEqual(receipt['run_id'], replay.RUN)
                    self.assertEqual(receipt['manifest_sha256'], replay.DIGEST)
                    if action == 'bundle':
                        self.assertEqual(set(result['payload_base64']), set(replay.ARTIFACTS))


if __name__ == '__main__':
    unittest.main()
