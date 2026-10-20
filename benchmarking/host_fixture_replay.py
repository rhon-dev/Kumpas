#!/usr/bin/env python3
"""Pinned A3b synthetic replay. Separate native producer, mocked transport only.

Local trusted checkout boundary, not adversarial concurrent-filesystem security.
All validation diagnostics are fixed codes; never echo untrusted input.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('benchmarking/study_evidence/20261015')
RUN = '323291af-c067-46dc-bae1-067d62fab10b'
DIGEST = '3279cb7d01075a9192f2566ae5573dd6137a23c6710ef1d0a590b78564fe0fed'
MANIFEST = BASE / 'a3a/handoff-parent-1' / RUN / 'manifest.json'
BINDING = BASE / 'controller/a3a-acceptance-and-consumer-binding.json'
ARTIFACTS = {
    'attempt-event.json': ('event', 'study'),
    'study.json': ('study', 'study'),
    'benchmark-index.json': ('benchmark_index', 'study'),
    **{n + '-export.json': ('export', 'study') for n in ('external', 'internal', 'reopened')},
    **{n + '-report.json': ('benchmark_report', n) for n in ('confirmed', 'unconfirmed', 'faulted')},
    **{n + '-control.json': ('benchmark_control', n) for n in ('confirmed', 'unconfirmed')},
}


class Rejected(ValueError):
    """Message is a fixed code only."""


def require(condition, code):
    if not condition:
        raise Rejected(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def loads(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate_json_key')
            result[key] = value
        return result
    try:
        return json.loads(raw, object_pairs_hook=pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(Rejected('nonfinite_json')))
    except (ValueError, UnicodeError, TypeError) as error:
        if isinstance(error, Rejected):
            raise
        raise Rejected('invalid_json') from None


def read_regular(base, relative):
    require(isinstance(relative, str) and bool(relative), 'invalid_path')
    p = PurePosixPath(relative)
    require(not p.is_absolute() and str(p) == relative and all(x not in ('.', '..') for x in p.parts), 'invalid_path')
    base = Path(base)
    # Reject symlinks in every component, not only final target.
    candidate = base / relative
    require(not any(x.is_symlink() for x in (candidate, *candidate.parents)), 'symlink_path')
    require(candidate.resolve().is_relative_to(base.resolve()), 'escaping_path')
    try:
        require(candidate.is_file(), 'missing_regular_file')
        return candidate.read_bytes()
    except OSError:
        raise Rejected('unreadable_file') from None


def validate(manifest=ROOT / MANIFEST, expected_digest=DIGEST, repo=ROOT,
             producer_xml=None, producer_ledger=None):
    """Explicit digest override exists only for isolated negative-fixture tests."""
    repo, manifest = Path(repo), Path(manifest)
    binding = loads(read_regular(ROOT, str(BINDING)))
    require(binding['expected_run_id'] == RUN and binding['manifest_sha256'] == DIGEST
            and binding['manifest'] == str(MANIFEST), 'binding_mismatch')
    raw = read_regular(manifest.parent, manifest.name)
    require(sha(raw) == expected_digest, 'manifest_digest_mismatch')
    m = loads(raw)
    require(isinstance(m, dict), 'manifest_type')
    require(type(m.get('test_schema_version')) is int and m['test_schema_version'] == 1, 'manifest_schema')
    require(m.get('run_id') == RUN and manifest.parent.name == RUN, 'manifest_run')
    require(m.get('synthetic_origin') is True and m.get('producer_outcome') == 'success', 'producer_outcome')
    sources = m.get('source_hashes')
    require(isinstance(sources, dict) and len(sources) == 42, 'source_snapshot')
    # Exact frozen source key set additionally bound to accepted producer ledger.
    for path, digest in sources.items():
        require(isinstance(digest, str) and re.fullmatch('[0-9a-f]{64}', digest), 'source_digest')
        require(sha(read_regular(repo, path)) == digest, 'source_digest_mismatch')
    artifacts = m.get('artifacts')
    require(isinstance(artifacts, list) and len(artifacts) == 11, 'artifact_set')
    verified, payload = {}, {}
    for a in artifacts:
        require(isinstance(a, dict) and set(a) == {'path', 'sha256', 'bytes', 'kind', 'identity'}, 'artifact_fields')
        name = a['path']
        require(isinstance(name, str) and name in ARTIFACTS and name not in verified, 'artifact_identity')
        require((a['kind'], a['identity']) == ARTIFACTS[name], 'artifact_identity')
        require(type(a['bytes']) is int and a['bytes'] >= 0, 'artifact_length')
        data = read_regular(manifest.parent, name)
        require(len(data) == a['bytes'] and sha(data) == a['sha256'], 'artifact_digest_mismatch')
        loads(data)  # Reject ambiguous JSON even in byte-preserved event text.
        verified[name], payload[name] = a, data
    require(set(verified) == set(ARTIFACTS), 'artifact_set')
    study, index = loads(payload['study.json']), loads(payload['benchmark-index.json'])
    require(isinstance(study, dict), 'payload_type')
    require(type(study.get('test_schema_version')) is int and study['test_schema_version'] == 1
            and study.get('run_id') == RUN and study.get('synthetic_origin') is True, 'payload_identity')
    require(study['primary']['delivered_event'].encode() == payload['attempt-event.json']
            and study['delivered_events'] == [study['primary']['delivered_event']], 'event_binding')
    require(study['scenario_id'] == m['scenarios']['study']['scenario_id'], 'scenario_binding')
    require(index == m['scenarios']['benchmark_modes'], 'benchmark_index_binding')
    ids = set()
    for mode in index:
        name, rid = mode['mode'], mode['run_id']
        require(name in ('confirmed', 'unconfirmed', 'faulted') and rid not in ids
                and isinstance(rid, str) and re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', rid), 'benchmark_identity')
        ids.add(rid)
        require(mode['report'] == name + '-report.json', 'benchmark_identity')
        report = loads(payload[mode['report']])
        require(isinstance(report, dict), 'report_type')
        require(report['run_id'] == rid and type(report['schema_version']) is int and report['schema_version'] == 2, 'report_identity')
        if name == 'faulted':
            require(mode['control'] is None and not (manifest.parent / 'faulted-control.json').exists(), 'faulted_companion_present')
        else:
            require(mode['control'] == name + '-control.json', 'benchmark_identity')
            control = loads(payload[mode['control']])
            require(isinstance(control, dict), 'control_type')
            require(set(control) == {'schema_version', 'run_id', 'status'} and type(control['schema_version']) is int
                    and control['schema_version'] == 1 and control['run_id'] == rid and control['status'] == name, 'control_identity')
    require(len(ids) == 3, 'benchmark_identity')
    xml_path = Path(producer_xml) if producer_xml else ROOT / binding['producer_xml']
    try:
        xml = ET.fromstring(read_regular(xml_path.parent, xml_path.name))
        require(xml.tag == 'testsuite' and xml.get('name') == 'com.kumpas.kumpas_app.HostStudyFlowTest'
                and int(xml.get('tests', '-1')) == 5
                and all(int(xml.get(k, '-1')) == 0 for k in ('failures', 'errors', 'skipped')), 'producer_suite_failed')
        cases = xml.findall('testcase')
        require(len(cases) == 5 and all(not any(c.find(k) is not None for k in ('failure', 'error', 'skipped')) for c in cases), 'producer_suite_failed')
        require(sum(c.get('name') == 'executedStudyAndBenchmarkProducer'
                    and c.get('classname') == xml.get('name') for c in cases) == 1, 'producer_target_missing')
    except Rejected:
        raise
    except (ET.ParseError, ValueError):
        raise Rejected('producer_xml_invalid') from None
    stdout = xml.findtext('system-out', '')
    expected_output = 'HOST_STUDY_FIXTURE_MANIFEST ' + str(ROOT / MANIFEST)
    require(expected_output in stdout.splitlines(), 'producer_stdout_mismatch')
    ledger_path = Path(producer_ledger) if producer_ledger else ROOT / binding['producer_ledger']
    rows = [loads(x) for x in read_regular(ledger_path.parent, ledger_path.name).splitlines()]
    rows = [r for r in rows if r.get('label') == binding['producer_label']]
    require(len(rows) == 1, 'producer_ledger_ambiguous')
    row = rows[0]
    require(isinstance(row.get('command'), list)
            and all(isinstance(value, str) for value in row['command']), 'producer_ledger_mismatch')
    require(isinstance(row.get('fixture_outputs'), list)
            and all(isinstance(value, str) for value in row['fixture_outputs']), 'producer_ledger_mismatch')
    require(type(row.get('exit')) is int and row['exit'] == 0 and row.get('source_hashes') == sources
            and expected_output in row.get('fixture_outputs', [])
            and '--tests' in row.get('command', [])
            and 'com.kumpas.kumpas_app.HostStudyFlowTest' in row['command'], 'producer_ledger_mismatch')
    log = read_regular(ROOT, row['log']).decode('utf-8')
    require('BUILD SUCCESSFUL' in log and '> Task :app:testDebugUnitTest' in log.splitlines(), 'producer_log_mismatch')
    return {'receipt_schema_version': 1, 'run_id': RUN, 'manifest_sha256': expected_digest,
            'fixture_root': str(manifest.parent), 'artifacts': verified, 'source_count': len(sources),
            'producer_tests': len(cases), 'producer_xml_sha256': sha(xml_path.read_bytes()),
            'synthetic_origin': True, 'not_physical_measurement': True}, payload


class SyntheticTransport:
    """Only the ADB *function* is mocked; no subprocess/device is allowed.

    Metadata is declared synthetic, copied from the bound producer, never an
    independent physical-device attestation. Report/control responses are exact
    captured bytes decoded as UTF-8, not reserialized reports.
    """
    def __init__(self, report_bytes, control_bytes=None, faults=None):
        self.raw = report_bytes
        self.control = control_bytes
        self.report = loads(report_bytes)
        self.faults = faults or {}
        self.calls = []
        self.read_hashes = []

    def __call__(self, serial, *args):
        require(serial == 'synthetic-a3b', 'unexpected_serial')
        self.calls.append(list(args))
        if args == ('get-state',):
            return 'device'
        if args[:3] == ('shell', 'pm', 'path'):
            if self.faults.get('package'):
                return ''
            return 'package:/data/app/synthetic/base.apk'
        if args[:2] == ('shell', 'sha256sum'):
            return self.report['setup']['apk_sha256'] + '  /data/app/synthetic/base.apk'
        if args[:2] == ('shell', 'getprop'):
            props = {'ro.product.model': 'model', 'ro.hardware': 'hardware',
                     'ro.product.manufacturer': 'manufacturer', 'ro.build.fingerprint': 'fingerprint'}
            if args[2] == 'ro.kernel.qemu':
                return '0'
            if self.faults.get('acquisition'):
                raise RuntimeError('metadata_failed')
            return self.report['device'][props[args[2]]]
        if args[:3] == ('shell', 'dumpsys', 'package'):
            return '' if self.faults.get('build') else 'versionName=' + self.report['build']['version_name']
        if args[:4] == ('shell', 'run-as', 'com.kumpas.kumpas_app', 'cat'):
            if args[4] == 'files/benchmarks/latest.json':
                self.read_hashes.append(sha(self.raw))
                return self.raw.decode('utf-8')
            require(args[4] == 'files/benchmarks/' + self.report['run_id'] + '.control.json', 'unexpected_companion_path')
            if self.control is None:
                raise RuntimeError('control_unavailable')
            return self.control.decode('utf-8')
        if args == ('logcat', '-c'):
            return ''
        if args[:3] == ('shell', 'am', 'instrument'):
            # Transport-only replay; no instrumentation is actually executed.
            return 'OK (1 test)'
        if args[:2] == ('logcat', '-d'):
            # Legacy reader accepts one logcat line. Explicit whitespace-only
            # adapter, not byte-identical transport and not native interpreter
            # instrumentation evidence. No timing/census fields are invented.
            diagnostic = self.raw.decode('utf-8').replace('\n', '')
            self.read_hashes.append(sha(diagnostic.encode('utf-8')))
            return 'BENCHMARK_RESULT ' + diagnostic
        raise Rejected('unexpected_transport_call')


def replay(output):
    import contextlib
    import io
    from types import SimpleNamespace
    from unittest.mock import patch
    import collect_fps as fps
    import collect_latency as latency
    import log_utils
    receipt, payload = validate()
    output = Path(output).absolute()
    require('..' not in output.parts and not any(p.is_symlink() for p in (output, *output.parents)), 'unsafe_output_root')
    output = output.resolve()
    # Only fresh a3b scratch/evidence destinations, never default history.
    permitted = (ROOT / BASE / 'a3b', Path.home() / '.hermes/cache/scratch')
    require(any(output.is_relative_to(p.resolve()) and output != p.resolve() for p in permitted), 'unsafe_output_root')
    output.mkdir(parents=True, exist_ok=False)
    history = output / 'synthetic-history.json'
    observations = []
    for mode in loads(payload['benchmark-index.json']):
        raw = payload[mode['report']]
        companion = payload.get(mode['control'])
        for kind in ('fps', 'latency'):
            transport = SyntheticTransport(raw, companion)
            args = SimpleNamespace(serial='synthetic-a3b', run_id=mode['run_id'], condition='optimal',
                                   model_version='synthetic-native-a3b', notes='')
            stdout = io.StringIO()
            with patch.object(fps, 'adb', transport), patch('subprocess.run', side_effect=AssertionError('real_subprocess_forbidden')), patch.object(log_utils, 'HISTORY_PATH', history), contextlib.redirect_stdout(stdout):
                collected = fps.read_report(args.serial)
                if kind == 'fps':
                    errors = fps.validate_report(collected['report'], args.run_id)
                    assessment = {'gate_pass': not errors, 'rejection_reasons': errors,
                                  'boundary': 'camerax_analyzer_entry_throughput', 'minimum_sustained_fps': 24}
                else:
                    assessment = latency.assess_report(collected['report'], args.run_id)
                exit_code = fps.log_collection(args, collected, kind, assessment)
            require(transport.read_hashes == [sha(raw)], 'transport_bytes_mismatch')
            rows = loads(history.read_bytes())
            retained = rows[-1]
            require(retained['results']['analyzer_count'] == 1800 and not retained['gate_pass'], 'replay_observation')
            traces = retained['results']['traces']
            require(len(traces) == 1 and traces[0]['run_id'] == args.run_id and traces[0]['inference_ms'] == 1
                    and traces[0]['final_analyzer_to_event_ms'] == 50, 'replay_observation')
            (output / (mode['mode'] + '-' + kind + '-stdout.json')).write_text(stdout.getvalue())
            observations.append({'mode': mode['mode'], 'run_id': args.run_id, 'measurement_type': kind,
                                 'collector_exit': exit_code, 'collection_errors': collected['collection_errors'],
                                 'report_transport_sha256': transport.read_hashes[0], 'artifact_sha256': sha(raw),
                                 'transport_calls': transport.calls, 'synthetic_origin': True, 'not_physical_measurement': True})
    validate()  # Frozen producer/source bytes still match after sink execution.
    (output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    ledger = {'synthetic_origin': True, 'not_physical_measurement': True,
              'origin': 'executed-native-artifacts; mocked-adb; real-isolated-history',
              'history': str(history), 'observations': observations}
    (output / 'replay-ledger.json').write_text(json.dumps(ledger, indent=2) + '\n')
    return ledger


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['preflight', 'replay', 'bundle'])
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    try:
        if args.action == 'replay':
            require(args.output is not None, 'output_required')
            result = replay(args.output)
        else:
            receipt, payload = validate()
            if args.action == 'bundle':
                import base64
                result = {'receipt': receipt, 'payload_base64': {k: base64.b64encode(v).decode('ascii') for k, v in payload.items()}}
            else:
                result = receipt
        print(json.dumps(result, sort_keys=True))
        return 0
    except (Rejected, KeyError, TypeError, AttributeError, IndexError, UnicodeError, OSError) as error:
        print(json.dumps({'error_code': str(error) if isinstance(error, Rejected) else 'fixture_invalid'}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
