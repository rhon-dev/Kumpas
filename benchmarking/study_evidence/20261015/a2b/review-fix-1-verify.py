"""Read-only source checks and uniquely named A2b review-fix evidence."""
import datetime
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

base = Path(__file__).resolve().parents[4]
ev = Path(__file__).resolve().parent
stamp = datetime.datetime.now().astimezone().isoformat()
def sha(path):
    return hashlib.sha256((base/path).read_bytes()).hexdigest()
def save(name, value):
    with (ev/name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')

baseline = json.loads((ev.parent/'controller/host-baseline.json').read_text())
protected = {path: {'expected': row['expected'], 'actual': sha(path)} for path, row in baseline['protected'].items()}
assert len(protected) == 82
assert all(row['actual'] == row['expected'] for row in protected.values())
accepted = json.loads((ev.parent/'controller/a2a-acceptance-20261016.json').read_text())['source_hashes']
assert len(accepted) == 8
assert all(sha(path) == expected for path, expected in accepted.items())
old = json.loads((ev/'source-manifest.json').read_text())['files']
changed = ['app/android/app/src/main/kotlin/com/kumpas/kumpas_app/MainActivity.kt',
           'app/android/app/src/test/kotlin/com/kumpas/kumpas_app/ActivityInitializationTest.kt']
assert all(sha(path) == expected for path, expected in old.items() if path not in changed)
results = {}
for label in ['review-fix-1-inheritance-red', 'review-fix-1-inheritance-green', 'review-fix-1-focused', 'review-fix-1-full-forced']:
    suites = []
    for path in sorted((ev/(label+'-xml')).glob('TEST-*.xml')):
        root = ET.parse(path).getroot()
        suites.append({'suite': root.attrib['name'], 'timestamp': root.attrib['timestamp'],
                       **{key: int(root.attrib[key]) for key in ['tests','failures','errors','skipped']}})
    assert suites
    totals = {key: sum(row[key] for row in suites) for key in ['tests','failures','errors','skipped']}
    results[label] = {'totals': totals, 'suites': suites}
    if label.endswith('-red'):
        assert totals == {'tests': 1, 'failures': 1, 'errors': 0, 'skipped': 0}
        root = ET.parse(next((ev/(label+'-xml')).glob('TEST-*.xml'))).getroot()
        failure = root.find('testcase/failure')
        assert failure is not None
        assert 'B prediction leaked to displaced A subscriber' in failure.attrib['message']
    else:
        assert totals['failures'] == totals['errors'] == totals['skipped'] == 0
full_log = (ev/'review-fix-1-full-forced.log').read_text()
tasks = {name: f'> Task {name}\n' in full_log for name in [':app:testDebugUnitTest', ':app:compileDebugAndroidTestKotlin']}
assert all(tasks.values())
ledger = [json.loads(line) for line in (ev/'review-fix-1-ledger.jsonl').read_text().splitlines()]
full = next(row for row in ledger if row['label'] == 'review-fix-1-full-forced')
assert full['command'] == ['./gradlew', '--offline', ':app:testDebugUnitTest', '--rerun', ':app:compileDebugAndroidTestKotlin', '--rerun']
assert full['exit'] == 0
check = subprocess.run(['git', 'diff', '--check'], cwd=base, capture_output=True, text=True)
with (ev/'review-fix-1-diff-check.log').open('x') as stream:
    stream.write(check.stdout+check.stderr)
assert check.returncode == 0
summary = {'timestamp': stamp, 'status': 'DONE_WITH_CONCERNS', 'results': results,
           'forced_tasks_executed': tasks, 'instrumentation_runtime_executed': False,
           'protected_count': len(protected), 'protected_mismatches': [],
           'a2a_preserved_count': len(accepted), 'a2a_mismatches': [],
           'other_a2b_manifest_paths_preserved': [path for path in old if path not in changed],
           'source_hashes': {path: sha(path) for path in old}, 'git_diff_check_exit': check.returncode,
           'changed_source_paths': changed,
           'evidence_runner_sha256': sha(str((ev/'run-host-tests.py').relative_to(base)))}
save('review-fix-1-verification.json', summary)
save('review-fix-1-protected-hashes.json', protected)
with (ev/'review-fix-1-ledger.jsonl').open('a') as stream:
    stream.write(json.dumps({'timestamp': stamp, 'label': 'review-fix-1-verification', 'command': ['python3', str(Path(__file__).relative_to(base))], 'cwd': str(base), 'exit': 0, 'outputs': ['review-fix-1-verification.json', 'review-fix-1-protected-hashes.json', 'review-fix-1-diff-check.log']})+'\n')
with (ev/'review-fix-1-report.md').open('a') as stream:
    stream.write('''
## Behavioral result and narrow repair

- Actual pre-production-change RED: one test, one assertion failure, no errors. Exact XML failure: `B prediction leaked to displaced A subscriber: [{"state":"prediction"}]`. A first received a control prediction; B then initialized successfully without assigning its sink, and its prediction reached A after real main Handler draining. RED XML and log were preserved before GREEN.
- Minimal behavioral change: clear `eventSink` immediately upon new initialization publication, before registration/reentrant callbacks. Early acquisition failures occur before this line and retain viable A. Stale rollback still cannot clear a newer subscriber; existing queued initialization/view/subscriber fencing is unchanged.
- Same regression GREEN: one test passed. Additional reentrant/no-listen and benchmark tests are coverage-only GREEN after the demonstrated fix, not claimed independent RED cycles. The reentrant test emits and drains inside B registration and after older A throws; B ownership, active attempt and unreleased resource handles survive, and later B subscription receives vision plus benchmark events. Existing reentrant-already-listened test remains green.
- Benchmark callback body was extracted unchanged to internal `postBenchmarkReport(owner, report)`, called by the real Android factory callback. This narrow production-used host seam permits exact Handler callback tests; no BenchmarkMode production change, fake BinaryMessenger or claim of actual channel installation. Tests prove no inherited subscriber before listen, queued/stale A completion suppression, and B completion payload after listen.
- Early acquisition failure test now observes actual prediction and benchmark delivery to A for all four failed acquisition stages, not only sink identity.

## Runner correction and fresh verification

- Corrected existing runner full mode to `:app:testDebugUnitTest --rerun :app:compileDebugAndroidTestKotlin --rerun`; --rerun is task-specific. Earlier reports/logs were not overwritten. Review-fix labels append to their own ledger/report and preserve unique XML snapshots.
''')
    stream.write(f"- Focused JVM: {results['review-fix-1-focused']['totals']}. Full JVM: {results['review-fix-1-full-forced']['totals']}. Both final targets executed (exact unsuffixed task lines), not UP-TO-DATE. Instrumentation Kotlin source compile exit 0; no runtime instrumentation.\n")
    stream.write(f'- Compared {len(protected)} protected hashes and {len(accepted)} accepted A2a hashes: zero mismatches. Other original A2b manifest source/test paths unchanged. `git diff --check` exit 0. Full source hashes/task/XML details: `review-fix-1-verification.json`.\n')
    stream.write('''
## Handoff — DONE_WITH_CONCERNS

Changed source: MainActivity.kt and ActivityInitializationTest.kt only. Evidence: corrected run-host-tests.py, review-fix-1-report.md, review-fix-1-ledger.jsonl, review-fix-1-verify.py, uniquely named RED/GREEN/focused/full logs/XML, verification/hash JSON and diff-check log. No commits.

Parent independent verification and spec/quality re-review are required; this report does not accept A2b. C1 remains: noncurrent registrations are fenced/inert, not proven detached on a different messenger; successful same-registry-ID retry remains unestablished. Full configureFlutterEngine/permission/BinaryMessenger runtime, real camera/provider/native driver release, installed end-to-end flow, physical measurements and study acceptance were not executed. No implementation blocker encountered; expected behavioral RED is retained as failure evidence.
''')
print(json.dumps(summary, indent=2))
