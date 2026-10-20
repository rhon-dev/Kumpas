import os, sys, subprocess, fcntl, json, datetime
from pathlib import Path
base = Path(__file__).resolve().parents[4]
ev = Path(__file__).resolve().parent
label, kind, *args = sys.argv[1:]
scratch = Path.home()/'.hermes/cache/scratch/kumpas-a2b'
scratch.mkdir(exist_ok=True)
env = os.environ.copy()
env['TMPDIR'] = str(scratch)
env['JAVA_HOME'] = subprocess.check_output(['/usr/libexec/java_home', '-v', '17'], text=True).strip()
env['ANDROID_HOME'] = str(Path.home()/'Library/Android/sdk')
if kind == 'jvm':
    cmd = ['./gradlew','--offline',':app:testDebugUnitTest','--rerun']
    for suite in (args or ['com.kumpas.kumpas_app.SessionManagerTest','com.kumpas.kumpas_app.DataExporterTest']):
        cmd += ['--tests',suite]
elif kind == 'full':
    cmd = ['./gradlew','--offline',':app:testDebugUnitTest','--rerun',':app:compileDebugAndroidTestKotlin','--rerun']
elif kind == 'analyze':
    cmd = ['/opt/homebrew/bin/flutter','analyze','--no-pub']
else:
    cmd = ['/opt/homebrew/bin/flutter','test','--no-pub',*args,'--reporter','expanded']
cwd = base/('app/android' if kind in ('jvm', 'full') else 'app')
log = ev/(label+'.log')
if log.exists():
    raise SystemExit('Refusing to overwrite evidence '+str(log))
lockpath = Path.home()/'.hermes/cache/scratch/kumpas-gradle.lock'
with lockpath.open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    with log.open('w') as out:
        result = subprocess.run(cmd,cwd=cwd,env=env,stdout=out,stderr=subprocess.STDOUT)
    import xml.etree.ElementTree as ET
    import shutil
    xml_summary = []
    if kind in ('jvm', 'full'):
        snapshot = ev/(label+'-xml')
        snapshot.mkdir()
        for path in sorted((base/'app/build/app/test-results/testDebugUnitTest').glob('TEST-*.xml')):
            shutil.copy2(path, snapshot/path.name)
            root = ET.parse(path).getroot()
            xml_summary.append({'suite': root.attrib['name'], **{key: int(root.attrib.get(key, 0)) for key in ('tests','failures','errors','skipped')}})
record = {'timestamp':datetime.datetime.now().astimezone().isoformat(),'label':label,'command':cmd,'cwd':str(cwd),'exit':result.returncode,'log':str(log.relative_to(base)),'lock':str(lockpath),'TMPDIR':str(scratch), 'xml': xml_summary}
ledger_name = 'review-fix-1-ledger.jsonl' if label.startswith('review-fix-1-') else 'command-ledger.jsonl'
report_name = 'review-fix-1-report.md' if label.startswith('review-fix-1-') else 'report.md'
with (ev/ledger_name).open('a') as out: out.write(json.dumps(record)+'\n')
with (ev/report_name).open('a') as out: out.write(f"- `{label}`: exit {result.returncode}; log `{log.name}`; exact command in ledger.\n")
print(json.dumps(record)); print(log.read_text()[-15000:])
sys.exit(result.returncode)
