"""Replay actual JVM producer output through both host assessments/real sink.
Run after forced native suite; no ADB and no default history access.
"""
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
import collect_fps as fps
import collect_latency as latency
import log_utils

fixture = json.loads(Path(__file__).with_name('native-unconfirmed-fixture.json').read_text())
report = fixture['report']
assert report['complete'] and report['analyzer_count'] == 1800
assert report['control_status'] == fixture['control']['status'] == 'unconfirmed'
assert not report['physical_fps_gate_pass']
args = SimpleNamespace(run_id=report['run_id'], condition='optimal', model_version='synthetic', serial='MOCK')
for kind in ('fps', 'latency'):
    assessment = latency.assess_report(report, args.run_id) if kind == 'latency' else {'gate_pass': not fps.validate_report(report, args.run_id), 'rejection_reasons': fps.validate_report(report, args.run_id)}
    with tempfile.TemporaryDirectory() as directory:
        history = Path(directory) / 'history.json'
        with patch.object(log_utils, 'HISTORY_PATH', history):
            result = fps.log_collection(args, {'report': report, 'control': fixture['control'], 'device': dict(report['device'], apk_sha256=report['setup']['apk_sha256']), 'build': report['build'], 'collection_errors': []}, kind, assessment)
        saved = json.loads(history.read_text())[0]
        assert result == 1 and not saved['gate_pass']
        assert saved['results']['analyzer_count'] == 1800
        assert saved['results']['complete']
        assert 'authoritative benchmark control disposition missing or unconfirmed' in saved['rejection_reasons']
        print(kind, 'actual producer diagnostics retained, independent disposition rejected')
