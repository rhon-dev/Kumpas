"""Verify bounded F1 postimages, executed logs, preserved inputs and replay."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BASE = OUT.parent

def load(path):
    return json.loads(path.read_bytes())

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def compare(expected):
    return {'count': len(expected), 'mismatches': [p for p, h in expected.items() if digest(ROOT / p) != h]}

allowed = ['benchmarking/host_fixture_replay.py', 'benchmarking/test_host_producer_replay.py']
initial = load(OUT / 'review-fix-1-initial-hashes.json')
changed = [p for p, h in initial.items() if digest(ROOT / p) != h]
assert set(changed) == set(allowed), changed
binding = load(BASE / 'controller/a3a-acceptance-and-consumer-binding.json')
manifest_path = ROOT / binding['manifest']
manifest = load(manifest_path)
assert digest(manifest_path) == binding['manifest_sha256']
native = compare(manifest['source_hashes'])
artifacts = {str((manifest_path.parent / a['path']).relative_to(ROOT)): a['sha256'] for a in manifest['artifacts']}
artifact_check = compare(artifacts)
protected = compare({p: item['expected'] for p, item in load(BASE / 'controller/host-baseline.json')['protected'].items()})
a2a = compare(load(BASE / 'a2b/source-manifest.json')['a2a_accepted_files'])
dart = compare({p: h for p, h in load(BASE / 'controller/a3b-parent-verification-1.json')['source_hashes'].items() if p.endswith('.dart')})
for item in (native, artifact_check, protected, a2a, dart):
    assert not item['mismatches'], item
python = {}
for label, count in [('python-focused', 34), ('python-full', 77), ('green-types', 3)]:
    text = (OUT / f'review-fix-1-{label}.log').read_text()
    match = re.search(r'Ran (\d+) tests?', text)
    assert match is not None, label
    actual = int(match[1])
    assert actual == count and '\nOK\n' in text, label
    python[label] = actual
flutter = {}
for label, expected in [('flutter-focused', 4), ('flutter-full', 79)]:
    events = []
    for line in (OUT / f'review-fix-1-{label}.log').read_text().splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict):
            events.append(event)
    done = [e for e in events if e.get('type') == 'testDone' and not e.get('hidden')]
    assert len(done) == expected and all(e['result'] == 'success' and not e.get('skipped') for e in done)
    assert any(e.get('type') == 'done' and e.get('success') is True for e in events)
    flutter[label] = {'tests': len(done), 'failures': 0, 'skips': 0}
assert 'No issues found!' in (OUT / 'review-fix-1-analyze.log').read_text()
replay = OUT / 'review-fix-1-replay'
history = load(replay / 'synthetic-history.json')
observations = load(replay / 'replay-ledger.json')['observations']
assert len(history) == len(observations) == 6
assert all(row['gate_pass'] is False and row['results']['analyzer_count'] == 1800 for row in history)
assert all(o['collector_exit'] == 1 and o['report_transport_sha256'] == o['artifact_sha256'] for o in observations)
assert 'PRIVATE_LEDGER_TYPE_MARKER' not in json.dumps(history)
assert {(o['mode'], o['measurement_type']) for o in observations} == {(m, k) for m in ('confirmed', 'unconfirmed', 'faulted') for k in ('fps', 'latency')}
diff = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
assert diff.returncode == 0, diff.stdout + diff.stderr
postimages = {p: digest(ROOT / p) for p in allowed}
result = {'status': 'DONE; independent parent review pending', 'changed_preexisting_files': changed,
          'initial_snapshot_count': len(initial), 'unchanged_other_snapshot_files': len(initial) - len(changed),
          'run_id': manifest['run_id'], 'manifest_sha256': digest(manifest_path),
          'native': native, 'artifacts': artifact_check, 'protected': protected, 'A2a': a2a, 'Dart': dart,
          'python': python, 'flutter': flutter, 'analyze': 'No issues found',
          'history_rows': len(history), 'collector_exits': [o['collector_exit'] for o in observations],
          'gate_passes': sum(row['gate_pass'] for row in history), 'git_diff_check_exit': diff.returncode,
          'postimages': postimages}
(OUT / 'review-fix-1-verification.json').open('x').write(json.dumps(result, indent=2) + '\n')
(OUT / 'review-fix-1-source-postimages.txt').open('x').write('\n'.join(f'=== {p} SHA256 {postimages[p]} ===\n' + (ROOT / p).read_text() for p in allowed))
print(json.dumps(result, indent=2))
