"""Exclusive Package D logs and sequential host-only execution. No source edits."""
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

D = Path(__file__).resolve().parent
ROOT = D.parents[3]
SCRATCH = Path.home() / '.hermes/cache/scratch/kumpas-d-20261018'
LOCK = Path.home() / '.hermes/cache/scratch/kumpas-gradle.lock'
SCRATCH.mkdir(parents=True, exist_ok=True)

def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()

def write(p, obj):
    with Path(p).open('x') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')

def append(obj):
    with (D/'command-ledger.jsonl').open('a') as f:
        f.write(json.dumps(obj)+'\n')
        f.flush()
        os.fsync(f.fileno())

def files():
    raw = subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard'], cwd=ROOT)
    paths = sorted(set(raw.decode().strip('\0').split('\0')))
    suffixes = {'.py','.dart','.kt','.kts','.java','.xml','.yaml','.yml','.json','.md','.toml','.gradle','.properties','.txt','.sh','.lock','.ipynb','.csv'}
    return [p for p in paths if (ROOT/p).is_file() and not p.startswith('benchmarking/study_evidence/') and not any(x in Path(p).parts for x in ('.venv','__pycache__','build','.dart_tool','.gradle','node_modules')) and (Path(p).suffix in suffixes or Path(p).name in ('gradlew','.gitignore','.gitkeep'))]

def snapshot():
    return {p:sha(ROOT/p) for p in files()}

def initialize():
    before = snapshot()
    write(D/'source-before.json', before)
    with (D/'git-status-before.txt').open('x') as f:
        subprocess.run(['git','status','--short'], cwd=ROOT, stdout=f, check=True)
    prior = json.loads((ROOT/'benchmarking/study_evidence/20261007/controller/owner-parent-verification-1.json').read_text())
    protected = prior['protected_hashes']
    actual = {p:sha(ROOT/p) for p in protected}
    mismatches = [p for p in protected if protected[p] != actual[p]]
    write(D/'protected-before.json', {'count':len(actual),'hashes':actual,'mismatches':mismatches})
    assert len(actual)==82 and not mismatches
    saved = SCRATCH/'historical-apks'
    saved.mkdir()
    manifest = {}
    # Include both canonical Android and Flutter publication aliases.
    paths = sorted(set(a['path'] for a in prior['artifacts'].values()) | {str(p.relative_to(ROOT)) for p in (ROOT/'app/build/app/outputs').rglob('*.apk')})
    for index, path in enumerate(paths):
        p = ROOT/path
        if not p.exists():
            continue
        target = saved/(str(index)+'-'+p.name)
        shutil.copy2(p, target)
        original_hash = sha(p)
        assert sha(target)==original_hash
        manifest[path]={'snapshot':str(target),'sha256':original_hash,'bytes':p.stat().st_size}
    write(saved/'manifest.json', manifest)
    write(D/'historical-apk-preservation.json', manifest)
    accepted = {}
    for p in sorted((D.parent/'controller').glob('*acceptance*.json')):
        obj=json.loads(p.read_text())
        accepted[p.name]={'sha256':sha(p),'source_matches':{k:sha(ROOT/k)==v for k,v in obj.get('source_hashes',{}).items()}}
    write(D/'acceptance-readback.json', accepted)
    append({'event':'baseline','at':datetime.datetime.now().astimezone().isoformat(),'source_count':len(before),'protected':82,'preserved_apks':len(manifest)})
    print(json.dumps({'source_count':len(before),'protected':len(actual),'apks_preserved':len(manifest),'snapshot':str(saved)}))

def execute(label, cmd, cwd, kind='plain'):
    env = dict(os.environ, TMPDIR=str(SCRATCH), PYTHONDONTWRITEBYTECODE='1', MPLBACKEND='Agg', ANDROID_HOME=str(Path.home()/'Library/Android/sdk'), ANDROID_SDK_ROOT=str(Path.home()/'Library/Android/sdk'))
    env['JAVA_HOME']=subprocess.check_output(['/usr/libexec/java_home','-v','17'],text=True).strip()
    log = D/(label+'.log')
    with LOCK.open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        before = snapshot()
        write(D/(label+'-sources.json'), before)
        record={'event':'start','label':label,'command':cmd,'cwd':str(cwd),'at':datetime.datetime.now().astimezone().isoformat(),'source_manifest':label+'-sources.json','source_manifest_sha256':sha(D/(label+'-sources.json')),'lock':str(LOCK),'environment':{k:env[k] for k in ('TMPDIR','JAVA_HOME','ANDROID_HOME','ANDROID_SDK_ROOT','MPLBACKEND','PYTHONDONTWRITEBYTECODE')}}
        append(record)
        with log.open('x') as output:
            result = subprocess.run(cmd, cwd=cwd, env=env, stdout=output, stderr=subprocess.STDOUT)
        text = log.read_text(errors='replace')
        record.update(event='end',exit=result.returncode,ended_at=datetime.datetime.now().astimezone().isoformat(),log=log.name,log_sha256=sha(log))
        after = snapshot()
        record['source_changes']=[p for p in set(before)|set(after) if before.get(p)!=after.get(p)]
        if kind=='python':
            match=re.search(r'Ran (\d+) tests? in',text)
            record['tests']=int(match.group(1)) if match else None
            record['summary']=re.findall(r'^OK[^\n]*|^FAILED[^\n]*',text,re.M)
            record['skip_lines']=[x for x in text.splitlines() if ' ... skipped ' in x]
        elif kind=='flutter':
            events=[]
            for line in text.splitlines():
                try:
                    value=json.loads(line)
                    if isinstance(value,dict): events.append(value)
                except ValueError: pass
            done=[e for e in events if e.get('type')=='testDone' and not e.get('hidden',False)]
            record.update(tests=len(done),failures=sum(e.get('result')!='success' and not e.get('skipped',False) for e in done),skipped=sum(e.get('skipped',False) for e in done),done_events=[e for e in events if e.get('type')=='done'])
        elif kind=='jvm':
            out=D/(label+'-xml'); out.mkdir()
            suites=[]
            for p in sorted((ROOT/'app/build/app/test-results/testDebugUnitTest').glob('TEST-*.xml')):
                shutil.copy2(p,out/p.name)
                xml=ET.parse(p).getroot()
                suites.append({'suite':xml.attrib['name'],**{k:int(xml.attrib.get(k,0)) for k in ('tests','failures','errors','skipped')}})
            record['xml']=suites
            record['totals']={k:sum(s[k] for s in suites) for k in ('tests','failures','errors','skipped')}
            results=ROOT/'app/build/app/test-results/testDebugUnitTest/binary'
            if results.exists(): shutil.copytree(results,D/(label+'-binary'))
            record['required_executed_tasks']={t:('> Task '+t) in text.splitlines() for t in (':app:testDebugUnitTest',':app:compileDebugAndroidTestKotlin')}
        if kind=='build':
            artifacts={}
            for p in sorted((ROOT/'app/build/app/outputs').rglob('*.apk')):
                artifacts[str(p.relative_to(ROOT))]={'sha256':sha(p),'bytes':p.stat().st_size}
            record['artifacts']=artifacts
        append(record)
        with (D/'report.md').open('a') as f:
            f.write(f"- `{label}`: exit {result.returncode}; `{log.name}` (exact command/source binding in append-only ledger).\n")
        write(D/(label+'-result.json'), record)
        print(json.dumps({k:v for k,v in record.items() if k not in ('xml','environment','command')}))
        if result.returncode: print(text[-9000:])
        if record['source_changes']: raise SystemExit('Reviewable sources changed during command')
        return result.returncode

if __name__=='__main__':
    label=sys.argv[1]
    if label=='initialize': initialize()
    else:
        commands={
            'flutter-analyze':(['/opt/homebrew/bin/flutter','analyze','--no-pub'],ROOT/'app','plain'),
            'flutter-full':(['/opt/homebrew/bin/flutter','test','--no-pub','--machine'],ROOT/'app','flutter'),
            'benchmark-full':(['/opt/homebrew/bin/python3.11','-B','-E','-m','unittest','discover','-s','benchmarking','-p','test_*.py','-v'],ROOT,'python'),
            'evaluation-full':(['/opt/homebrew/bin/python3.11','-B','-E','-m','unittest','discover','-s','evaluation','-p','test_*.py','-v'],ROOT,'python'),
            'training-full':([str(Path.home()/'.kumpas-venvs/tf/bin/python'),'-B','-E','-m','unittest','discover','-s','training/tests','-p','test_*.py','-v'],ROOT,'python'),
            'holistic-compatible':([str(ROOT/'training/.venv/bin/python'),'-B','-E','-m','unittest','benchmarking.test_pipeline_parity','benchmarking.test_parity_fixtures','-v'],ROOT,'python'),
            'jvm-full':(['./gradlew','--offline','--console=plain',':app:testDebugUnitTest','--rerun',':app:compileDebugAndroidTestKotlin','--rerun'],ROOT/'app/android','jvm'),
            'debug-test-build':(['./gradlew','--offline','--console=plain',':app:assembleDebug','--rerun',':app:assembleDebugAndroidTest','--rerun'],ROOT/'app/android','build'),
            'debug-test-build-fresh':(['./gradlew','--offline','--console=plain',':app:compileFlutterBuildDebug','--rerun',':app:compileDebugKotlin','--rerun',':app:compileDebugAndroidTestKotlin','--rerun',':app:packageDebug','--rerun',':app:packageDebugAndroidTest','--rerun',':app:assembleDebug',':app:assembleDebugAndroidTest'],ROOT/'app/android','build'),
            'release-build':(['./gradlew','--offline','--console=plain','-Ptarget-platform=android-arm64','-Ptarget=lib/main.dart','-Pdart-obfuscation=false','-Ptrack-widget-creation=false','-Ptree-shake-icons=true',':app:assembleRelease','--rerun'],ROOT/'app/android','build'),
        }
        key='release-build' if label.startswith('release-build-retry') else ('debug-test-build-fresh' if label.startswith('debug-test-build-fresh') else label)
        cmd,cwd,kind=commands[key]
        sys.exit(execute(label,cmd,cwd,kind))
