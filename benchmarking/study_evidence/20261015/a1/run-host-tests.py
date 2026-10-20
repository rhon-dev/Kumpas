import os, sys, subprocess, fcntl, json, datetime
from pathlib import Path
base=Path('/Users/ahronjanl.rafaelahron.0804icloudcom/Documents/Thesis/kumpas')
ev=base/'benchmarking/study_evidence/20261015/a1'
label,kind=sys.argv[1:3]
env=os.environ.copy(); env['TMPDIR']=str(Path.home()/'.hermes/cache/scratch'); env['JAVA_HOME']='/opt/homebrew/Cellar/openjdk@17/17.0.18/libexec/openjdk.jdk/Contents/Home'; env['ANDROID_HOME']=str(Path.home()/'Library/Android/sdk')
cmd=['./gradlew','--offline',':app:testDebugUnitTest','--rerun','--tests','com.kumpas.kumpas_app.DataExporterTest','--tests','com.kumpas.kumpas_app.SessionManagerTest'] if kind=='jvm' else ['/opt/homebrew/bin/flutter','test','--no-pub','test/assessment_save_failure_test.dart','--reporter','expanded']
cwd=base/('app/android' if kind=='jvm' else 'app')
with open(Path(env['TMPDIR'])/'kumpas-gradle.lock','a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 log=ev/(label+'.log')
 with log.open('w') as out: result=subprocess.run(cmd,cwd=cwd,env=env,stdout=out,stderr=subprocess.STDOUT)
 record={'timestamp':datetime.datetime.now().astimezone().isoformat(),'label':label,'command':cmd,'cwd':str(cwd),'exit':result.returncode,'log':str(log.relative_to(base)),'lock':str(Path(env['TMPDIR'])/'kumpas-gradle.lock')}
 with (ev/'command-ledger.jsonl').open('a') as out: out.write(json.dumps(record)+'\n')
 with (ev/'report.md').open('a') as out: out.write(f"- `{label}`: exit {result.returncode}; [{log.name}]({log.name}); command in ledger.\n")
 print(json.dumps(record)); print(log.read_text()[-14000:])
sys.exit(result.returncode)
