"""Keep the DATALESS generated file within its provider, outside output tree."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,subprocess
D=Path(__file__).resolve().parent
ROOT=D.parents[3]
source=ROOT/'app/build/app/intermediates/flutter/release/arm64-v8a/app 2.so'
target=ROOT/'app/build/kumpas-d-quarantine/app 2.so'
lockpath=Path.home()/'.hermes/cache/scratch/kumpas-gradle.lock'
def state(p):
 s=p.stat()
 return {'path':str(p),'bytes':s.st_size,'inode':s.st_ino,'device':s.st_dev,'flags':s.st_flags,'sha256':None if s.st_flags & 0x40000000 else hashlib.sha256(p.read_bytes()).hexdigest()}
with lockpath.open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 target.parent.mkdir(exist_ok=False)
 before=state(source)
 record={'event':'same-provider-quarantine','at':datetime.datetime.now().astimezone().isoformat(),'earlier_attempt':'quarantine-recovery.py exited1: os.rename to external scratch timed out Errno60; source inode27582004 size5309360 flags1073741920 still existed, external target absent','before':before,'target':str(target),'git_ignored':subprocess.run(['git','check-ignore','-v',str(source.relative_to(ROOT)),str(target.relative_to(ROOT))],cwd=ROOT,capture_output=True,text=True,check=True).stdout,'limits':'No assertion about cloud/provider origin; no attempt to read DATALESS bytes; metadata-preserving move is not a pre/post content hash comparison.'}
 with (D/'generated-quarantine-so-provider-before.json').open('x') as f: json.dump(record,f,indent=2)
 try:
  os.rename(source,target)
  after=state(target)
  assert all(before[k]==after[k] for k in ('bytes','inode','device'))
  record.update(after=after,exit=0)
 except Exception as e:
  record.update(exit=1,error=repr(e),source_exists=source.exists(),target_exists=target.exists())
 with (D/'generated-quarantine-so-provider-after.json').open('x') as f: json.dump(record,f,indent=2)
 with (D/'command-ledger.jsonl').open('a') as f: f.write(json.dumps(record)+'\n')
 print(json.dumps(record,indent=2))
 raise SystemExit(record['exit'])
