"""A2b final host evidence; read-only source checks, append-only reports."""
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
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()

def save(name, data):
    with (ev/name).open('x') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')

baseline = json.loads((ev.parent/'controller/host-baseline.json').read_text())
protected = {path: {'expected': row['expected'], 'actual': sha(base/path)}
             for path, row in baseline['protected'].items()}
mismatches = [path for path, row in protected.items() if row['expected'] != row['actual']]
assert len(protected) == 82 and not mismatches
save('protected-hashes.json', {'timestamp': stamp, 'count': len(protected), 'mismatches': mismatches, 'files': protected})
accepted = json.loads((ev.parent/'controller/a2a-acceptance-20261016.json').read_text())['source_hashes']
accepted_mismatches = [path for path, expected in accepted.items() if sha(base/path) != expected]
assert not accepted_mismatches

modified = [
    'app/android/app/src/main/kotlin/com/kumpas/kumpas_app/MainActivity.kt',
    'app/android/app/src/main/kotlin/com/kumpas/kumpas_app/ActivityResourceFactory.kt',
    'app/android/app/src/test/kotlin/com/kumpas/kumpas_app/ActivityInitializationTest.kt',
    'app/android/app/src/test/kotlin/com/kumpas/kumpas_app/VisionInitializationTest.kt',
    'app/android/app/src/test/kotlin/com/kumpas/kumpas_app/CameraViewOwnershipTest.kt',
]
preserved = [
    'app/android/app/src/main/kotlin/com/kumpas/kumpas_app/VisionEngine.kt',
    'app/android/app/src/main/kotlin/com/kumpas/kumpas_app/CameraPreviewView.kt',
    'app/android/app/src/main/kotlin/com/kumpas/kumpas_app/CameraViewResourceFactory.kt',
    'app/android/app/src/main/kotlin/com/kumpas/kumpas_app/VisionResourceFactory.kt',
    'app/android/app/src/test/kotlin/com/kumpas/kumpas_app/MainActivityBoundaryTest.kt',
    'app/android/app/src/test/kotlin/com/kumpas/kumpas_app/ResourceCleanupTest.kt',
]
save('source-manifest.json', {'timestamp': stamp, 'modified_by_a2b': modified,
    'files': {path: sha(base/path) for path in modified+preserved},
    'a2a_accepted_files': accepted, 'a2a_mismatches': accepted_mismatches})

results = {}
for label in ['focused-handoff', 'full-handoff']:
    suites = []
    for path in sorted((ev/(label+'-xml')).glob('TEST-*.xml')):
        root = ET.parse(path).getroot()
        suites.append({'suite': root.attrib['name'], 'timestamp': root.attrib['timestamp'],
                       **{key: int(root.attrib[key]) for key in ['tests','failures','errors','skipped']}})
    assert suites
    totals = {key: sum(row[key] for row in suites) for key in ['tests','failures','errors','skipped']}
    assert totals['failures'] == totals['errors'] == totals['skipped'] == 0
    results[label] = {'totals': totals, 'suites': suites}
assert '> Task :app:testDebugUnitTest\n' in (ev/'full-handoff.log').read_text()
assert '> Task :app:compileDebugAndroidTestKotlin\n' in (ev/'full-handoff.log').read_text()
check = subprocess.run(['git','diff','--check'], cwd=base, capture_output=True, text=True)
with (ev/'diff-check.log').open('x') as stream:
    stream.write(check.stdout+check.stderr)
assert check.returncode == 0
summary = {'timestamp': stamp, 'status': 'DONE_WITH_CONCERNS', 'results': results,
    'instrumentation_source_compile_exit': 0, 'instrumentation_executed': False,
    'protected_count': len(protected), 'protected_mismatches': mismatches,
    'a2a_preserved_count': len(accepted), 'a2a_mismatches': accepted_mismatches,
    'git_diff_check_exit': check.returncode, 'modified_source_paths': modified,
    'limits': ['No full configureFlutterEngine/BinaryMessenger startup or successful framework delegate lifecycle executed',
               'Same-engine platform-registry retry and differing-messenger replacement not established',
               'Native wrappers/provider driver calls synthetic; no device or physical/study acceptance']}
save('verification-summary.json', summary)
with (ev/'command-ledger.jsonl').open('a') as stream:
    stream.write(json.dumps({'timestamp':stamp,'label':'final-verification','command':['python3',str(Path(__file__).relative_to(base))],
        'cwd': str(base), 'exit': 0, 'outputs': ['source-manifest.json','protected-hashes.json','verification-summary.json','diff-check.log']})+'\n')
with (ev/'report.md').open('a') as stream:
    stream.write('\n## Final handoff — DONE_WITH_CONCERNS\n\n')
    stream.write(f"- Focused JVM: {results['focused-handoff']['totals']}. Full native JVM (no filters): {results['full-handoff']['totals']}. Fresh XML snapshots in the corresponding `*-xml/` directories.\n")
    stream.write('- Instrumentation Kotlin source compile exit0, task executed (not UP-TO-DATE). No instrumentation/device runtime executed. Final source compile/tests followed formatting and stronger coverage assertions.\n')
    stream.write(f'- Protected assets/contracts: {len(protected)} checked, no mismatches. All {len(accepted)} A2a accepted source hashes unchanged. `git diff --check` exit0.\n')
    stream.write('- Five A2b source paths and preserved neighbors are hashed in source-manifest.json. No Dart/session/export/model/benchmark production changes; no camera or VisionEngine production changes in A2b.\n')
    stream.write('- Exact commands, exits, lock, TMPDIR and log paths in command-ledger.jsonl. Earlier RED run XML was not snapshotted before subsequent runs; behavioral failures and test names/counts remain in original logs. Final focused/full XML is retained. Gradle reported its existing deprecation warning in an early failed run; no install was attempted.\n')
    stream.write('- Parent independent verification and spec/quality review are still required. This is an implementation handoff, not broader acceptance.\n')
    stream.write('\n### A2b source changes\n\n'+'\n'.join('- `'+path+'`' for path in modified)+'\n')
print(json.dumps(summary, indent=2))
