"""Snapshot actual A2a host checks without modifying protected evidence."""
import datetime
import hashlib
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

base = Path(__file__).resolve().parents[4]
ev = Path(__file__).resolve().parent
stamp = datetime.datetime.now().astimezone().isoformat()

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def save(name, value):
    with (ev/name).open('x') as out:
        json.dump(value, out, indent=2)
        out.write('\n')

baseline = json.loads((ev.parent/'controller/host-baseline.json').read_text())
protected = {}
for path, expected in baseline['protected'].items():
    actual = sha(base/path) if (base/path).is_file() else None
    protected[path] = {'expected':expected['expected'], 'actual':actual, 'matches':actual == expected['expected']}
mismatches = [path for path, row in protected.items() if not row['matches']]
save('protected-hashes.json', {'timestamp':stamp, 'count':len(protected), 'mismatches':mismatches, 'files':protected})
assert len(protected) == 82 and not mismatches

paths = [
 'app/android/app/src/main/kotlin/com/kumpas/kumpas_app/SessionManager.kt',
 'app/android/app/src/test/kotlin/com/kumpas/kumpas_app/SessionManagerTest.kt',
 'app/android/app/src/test/kotlin/com/kumpas/kumpas_app/DataExporterTest.kt',
 'app/lib/session/session_repository.dart',
 'app/lib/session/session_lifecycle.dart',
 'app/test/session_clear_test.dart',
 'app/test/session_lifecycle_race_test.dart',
 'app/test/session_repository_race_test.dart',
]
save('source-manifest.json', {'timestamp':stamp, 'scope':'A2a current source including preserved prior accepted native edits; not a BASE..HEAD acceptance diff', 'files':{p:sha(base/p) for p in paths}})

suites = {}
xmlroot = base/'app/build/app/test-results/testDebugUnitTest'
(ev/'final-jvm-xml').mkdir(exist_ok=False)
for suite in ['SessionManagerTest', 'DataExporterTest']:
    path = xmlroot/f'TEST-com.kumpas.kumpas_app.{suite}.xml'
    root = ET.parse(path).getroot()
    counts = {k:int(root.attrib[k]) for k in ['tests','failures','errors','skipped']}
    assert counts['failures'] == counts['errors'] == counts['skipped'] == 0
    assert root.attrib['timestamp'].startswith('2026-10-15T19:37:')
    suites[suite] = counts
    shutil.copyfile(path, ev/'final-jvm-xml'/path.name)

flutter = {}
for label in ['final-focused-dart', 'full-flutter-tests-final']:
    text = (ev/(label+'.log')).read_text()
    match = re.search(r'\+(\d+): All tests passed!', text)
    assert match, label
    flutter[label] = int(match.group(1))
assert 'No issues found!' in (ev/'full-flutter-analyze-green.log').read_text()
result = subprocess.run(['git','diff','--check'], cwd=base, text=True, capture_output=True)
(ev/'diff-check.log').write_text(result.stdout+result.stderr)
assert result.returncode == 0
summary = {'timestamp':stamp, 'targeted_jvm':suites, 'targeted_jvm_total':sum(v['tests'] for v in suites.values()), 'full_native_suite_executed':False, 'flutter':flutter, 'flutter_analyze_exit':0, 'protected_count':len(protected), 'protected_mismatches':mismatches, 'git_diff_check_exit':result.returncode, 'source_paths':paths}
save('verification-summary.json',summary)
with (ev/'command-ledger.jsonl').open('a') as out:
    out.write(json.dumps({'timestamp':stamp,'label':'final-snapshot','command':['/opt/homebrew/bin/python3.11',str(Path(__file__).relative_to(base))],'cwd':str(base),'exit':0,'outputs':['verification-summary.json','protected-hashes.json','source-manifest.json','final-jvm-xml/','diff-check.log']})+'\n')
with (ev/'report.md').open('a') as out:
    out.write('\n## Final host verification snapshot\n\n')
    out.write(f"- Targeted JVM: {summary['targeted_jvm_total']} passed ({suites['SessionManagerTest']['tests']} SessionManager, {suites['DataExporterTest']['tests']} DataExporter), no failures/errors/skips. This is NOT the full native suite. XML copied into `final-jvm-xml/`.\n")
    out.write(f"- Focused Dart: {flutter['final-focused-dart']} passed; full Flutter: {flutter['full-flutter-tests-final']} passed; full analyze exit0, no issues. Initial analyze found one new test braces lint, fixed and rerun; failure log preserved.\n")
    out.write(f"- Protected hashes: {len(protected)} compared, {len(mismatches)} mismatches; `git diff --check` exit0. Source hashes in `source-manifest.json`.\n")
    out.write('- Formatting command: `/opt/homebrew/bin/dart format app/lib/session/session_repository.dart app/lib/session/session_lifecycle.dart app/test/session_clear_test.dart app/test/session_lifecycle_race_test.dart app/test/session_repository_race_test.dart`, exit0; subsequent diff check exit0.\n')
    out.write('\n### A2a source paths\n\n'+'\n'.join('- `'+p+'`' for p in paths)+'\n')
print(json.dumps(summary, indent=2))
