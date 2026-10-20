"""Quarantine exact generated debug entries rejected by the APK inspector."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,subprocess
D=Path(__file__).resolve().parent
ROOT=D.parents[3]
SCRATCH=Path.home()/'.hermes/cache/scratch/kumpas-d-20261018'
def state(p):
 s=p.stat()
 return {'path':str(p),'bytes':s.st_size,'inode':s.st_ino,'device':s.st_dev,'flags':s.st_flags,'sha256':None if s.st_flags & 0x40000000 else hashlib.sha256(p.read_bytes()).hexdigest()}
with (SCRATCH.parent/'kumpas-gradle.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 records=[]
 for name in ('isolate_snapshot_data','vm_snapshot_data'):
  src=ROOT/'app/build/app/intermediates/flutter/debug/flutter_assets'/(name+' 2')
  counterpart=src.with_name(name)
  dst=ROOT/'app/build/kumpas-d-quarantine'/(name+' 2')
  assert src.exists() and counterpart.exists() and not dst.exists()
  row={'before':state(src),'counterpart':state(counterpart),'target':str(dst),'ignored':subprocess.run(['git','check-ignore','-v',str(src.relative_to(ROOT)),str(counterpart.relative_to(ROOT))],cwd=ROOT,text=True,capture_output=True,check=True).stdout}
  with (D/(name+'-quarantine-before.json')).open('x') as f:json.dump(row,f,indent=2)
  os.rename(src,dst)
  row['after']=state(dst)
  assert all(row['before'][k]==row['after'][k] for k in ('inode','device','bytes'))
  if row['before']['sha256'] is not None:assert row['before']['sha256']==row['after']['sha256']
  records.append(row)
 record={'event':'debug-generated-quarantine','at':datetime.datetime.now().astimezone().isoformat(),'reason':'debug-inspection.log rejects suffixed generated ZIP entries containing spaces; exact two generated inputs independently located. No source change, ABI policy change or broad cleanup. Prior unsuccessful artifact preserved externally.','records':records}
 with (D/'debug-generated-quarantine.json').open('x') as f:json.dump(record,f,indent=2)
 with (D/'command-ledger.jsonl').open('a') as f:f.write(json.dumps(record)+'\n')
 print(json.dumps(record,indent=2))
