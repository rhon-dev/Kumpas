"""Replay current executed JVM receipt fixtures; no ADB/default history.
Flutter response-loss tests remain separately mocked, not a live session.
"""
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / 'benchmarking'))
import collect_fps as fps
import collect_latency as latency
import log_utils

xml = REPO / 'app/build/app/test-results/testDebugUnitTest/TEST-com.kumpas.kumpas_app.BenchmarkModeTest.xml'
root = ET.parse(xml).getroot()
fixtures = [json.loads(line.split('NATIVE_RECEIPT_FIXTURE ', 1)[1])
            for output in root.findall('system-out') for line in (output.text or '').splitlines()
            if line.startswith('NATIVE_RECEIPT_FIXTURE ')]
assert len(fixtures) == 3
(HERE / 'executed-producer-fixtures.json').write_text(json.dumps(fixtures, indent=2) + '\n')
for fixture in fixtures:
    report = fixture['report']
    assert report['complete'] and report['analyzer_count'] == 1800
    args = SimpleNamespace(run_id=report['run_id'], condition='optimal', model_version='synthetic-replay', serial='MOCK')
    variants = [('actual', fixture.get('control'))]
    if fixture['mode'] == 'confirmed':
        variants.extend((name, control) for name, control in [
            ('missing', None), ('unconfirmed', dict(fixture['control'], status='unconfirmed')),
            ('float', dict(fixture['control'], schema_version=1.0)),
            ('extra', dict(fixture['control'], private='PRIVATE_patient_text'))])
    for variant, control in variants:
        for kind in ('fps', 'latency'):
            assessment = latency.assess_report(report, args.run_id) if kind == 'latency' else {
                'gate_pass': not fps.validate_report(report, args.run_id),
                'rejection_reasons': fps.validate_report(report, args.run_id)}
            with tempfile.TemporaryDirectory() as directory:
                history = Path(directory) / 'history.json'
                with patch.object(log_utils, 'HISTORY_PATH', history):
                    status = fps.log_collection(args, {
                        'report': report, 'control': control,
                        'device': dict(report['device'], apk_sha256=report['setup']['apk_sha256']),
                        'build': report['build'], 'collection_errors': []}, kind, assessment)
                saved = json.loads(history.read_text())[0]
                expected_gate = fixture['mode'] == 'confirmed' and variant == 'actual'
                assert saved['gate_pass'] == expected_gate, saved['rejection_reasons']
                assert status == (0 if expected_gate else 1)
                assert saved['results']['analyzer_count'] == 1800
                assert saved['results']['complete']
                assert saved['results']['traces'][0]['final_analyzer_to_event_ms'] == 50
                assert 'PRIVATE_patient_text' not in history.read_text()
                print(f"REPLAY {fixture['mode']}/{variant}/{kind}: gate={expected_gate}, retained=1800/50ms")
print('Replay completed: actual JVM output, both actual host assessments/sinks, isolated real histories.')
