"""Read-only source/protected checks; writes evidence only beside this script."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASELINE = HERE.parent / 'controller/host-baseline.json'
base = json.loads(BASELINE.read_text())
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
protected = {p: {'expected': h['expected'], 'actual': sha(ROOT / p)}
             for p, h in base['protected'].items()}
mismatches = [p for p, h in protected.items() if h['actual'] != h['expected']]
changed = [p for p, h in base['file_hashes'].items() if sha(ROOT / p) != h]
sources = [
    'app/android/app/src/main/kotlin/com/kumpas/kumpas_app/DataExporter.kt',
    'app/android/app/src/main/kotlin/com/kumpas/kumpas_app/ExportPublication.kt',
    'app/android/app/src/test/kotlin/com/kumpas/kumpas_app/DataExporterTest.kt',
    'app/lib/ui/assessment_screen.dart',
    'app/test/assessment_save_failure_test.dart',
]
suites = []
for name in ('DataExporterTest', 'SessionManagerTest'):
    path = ROOT / f'app/build/app/test-results/testDebugUnitTest/TEST-com.kumpas.kumpas_app.{name}.xml'
    content = path.read_text()
    suite = ET.fromstring(content)
    suites.append(dict(suite.attrib))
    (HERE / path.name).write_text(content)
diff = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, text=True, capture_output=True)
(HERE / 'diff-check.log').write_text(diff.stdout + diff.stderr)
result = {
    'observed_at': datetime.datetime.now().astimezone().isoformat(),
    'protected_count': len(protected), 'protected_mismatches': mismatches,
    'protected': protected, 'changed_since_parent_baseline': changed,
    'source_sha256': {p: sha(ROOT / p) for p in sources},
    'jvm_suites': suites, 'jvm_total': sum(int(s['tests']) for s in suites),
    'diff_check_exit': diff.returncode,
}
(HERE / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
code = int(bool(mismatches or diff.returncode or any(int(s[k]) for s in suites for k in ('failures', 'errors', 'skipped'))))
with (HERE / 'command-ledger.jsonl').open('a') as out:
    out.write(json.dumps({'timestamp': result['observed_at'], 'command': '/opt/homebrew/bin/python3.11 benchmarking/study_evidence/20261015/a1/verify.py', 'exit': code, 'log': 'benchmarking/study_evidence/20261015/a1/verification.json'}) + '\n')
print(json.dumps({k: v for k, v in result.items() if k not in ('protected', 'source_sha256')}, indent=2))
raise SystemExit(code)
