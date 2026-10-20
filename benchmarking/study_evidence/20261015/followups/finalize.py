"""Final evidence summary; does not update parent acceptance records."""
import ast
import difflib
import json
import re
import subprocess
from capture import HERE, ROOT, ALLOWED, sha, save

before = json.loads((HERE / 'before.json').read_text())
after = json.loads((HERE / 'after.json').read_text())
assert not after['inventory_mismatches']
assert all(not group['mismatches'] for group in after['checks'].values())
source_delta = []
for name in ALLOWED:
    original = (HERE / 'before' / name).read_text()
    current = (ROOT / name).read_text()
    ast.parse(current)
    assert all(line == line.rstrip() for line in current.splitlines())
    assert sha(HERE / 'after' / name) == after['sources'][name] == sha(ROOT / name)
    source_delta.extend(difflib.unified_diff(original.splitlines(True), current.splitlines(True), fromfile='before/'+name, tofile='after/'+name))
with (HERE / 'source.diff').open('x') as stream:
    stream.write(''.join(source_delta))
result = subprocess.run(['git', 'diff', '--check', '--', *ALLOWED], cwd=ROOT, capture_output=True, text=True)
assert result.returncode == 0, result.stdout + result.stderr

historical = {}
for package in ('c1', 'c2'):
    record = json.loads((HERE.parent / ('controller/'+package+'-parent-verification-1.json')).read_text())
    rows = []
    for name, expected in record['source_hashes'].items():
        old = sha(HERE / 'before' / name) if name in ALLOWED else sha(ROOT / name)
        assert old == expected, (name, old, expected)
        current = sha(ROOT / name)
        rows.append({'path': name, 'historical_sha256': expected, 'current_sha256': current, 'historical_snapshot_matches': True})
    historical[package] = rows
logs = {}
for name in ('b1-red', 'b1-green', 'c1-coverage-green', 'c2-coverage-green', 'broad-benchmark-discover', 'broad-evaluation', 'compatible-parity-campaign', 'final-benchmark', 'final-compatible-parity'):
    text = (HERE / (name+'.log')).read_text()
    count = int(re.search(r'Ran (\d+) tests?', text).group(1))
    skipped = re.search(r'OK \(skipped=(\d+)\)', text)
    skips = int(skipped.group(1)) if skipped else 0
    ok = '\nOK' in text
    assert ok == (name != 'b1-red')
    logs[name] = {'run': count, 'skipped': skips, 'passed_methods': count-skips if ok else None, 'ok': ok, 'sha256': sha(HERE / (name+'.log'))}
assert 'FAILED (failures=12)' in (HERE / 'b1-red.log').read_text()
unique = {str((ROOT / name).resolve()) if not name.startswith('/') else name for name in before['inventory']}
save('summary.json', {'status': 'IMPLEMENTED_VERIFIED_PENDING_PARENT_REVIEW', 'source_postimages': after['sources'],
    'historical_source_preimages': before['sources'], 'tests': logs, 'git_diff_check_exit': result.returncode,
    'preservation': after['checks'], 'preexisting_inventory_entries': len(before['inventory']),
    'preexisting_inventory_unique_paths': len(unique), 'inventory_mismatches': after['inventory_mismatches'],
    'historical_c1_c2_source_roles': historical,
    'distinction': 'B1-R1 has actual behavioral RED then GREEN. C1-Q1 three and C2-L1 two are first-run GREEN coverage-only; production unchanged.',
    'environment_issues': ['Initial capture stopped on DATALESS environment executable before content read; corrected exclusion succeeded without hydration.', 'Initial benchmarking discovery -t . failed because benchmarking is not an importable package; existing -s benchmarking discovery succeeded.'],
    'limits': 'Historical fixtures/configs/outputs retained unchanged; no retroactive rebinding. Parent review/verification outstanding; physical/research/participant gates unchanged.'})
print(json.dumps({'tests': logs, 'preservation': after['checks'], 'inventory_entries': len(before['inventory']), 'inventory_unique': len(unique), 'source_hashes': after['sources']}, indent=2))
