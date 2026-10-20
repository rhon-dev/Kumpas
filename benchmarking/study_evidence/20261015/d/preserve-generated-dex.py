"""Preserve the exact generated DEX named by the retained build failure."""
import datetime,fcntl,hashlib,json,os,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent
ROOT=D.parents[3]
source=ROOT/'app/build/app/intermediates/dex/release/minifyReleaseWithR8/classes 2.dex'
peer=source.with_name('classes.dex')
target=ROOT/'app/build/kumpas-d-quarantine/classes 2.dex'
def state(p):
 s=p.stat()
 return {'path':str(p),'bytes':s.st_size,'inode':s.st_ino,'device':s.st_dev,'flags':s.st_flags,'sha256':None if s.st_flags & 0x40000000 else hashlib.sha256(p.read_bytes()).hexdigest()}
with (Path.home()/'.hermes/cache/scratch/kumpas-gradle.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 assert source.exists() and peer.exists() and not target.exists()
 record={'event':'dex-quarantine','at':datetime.datetime.now().astimezone().isoformat(),'failure_log':'release-build-retry2.log','before':state(source),'counterpart':state(peer),'git_ignored':subprocess.run(['git','check-ignore','-v',str(source.relative_to(ROOT)),str(peer.relative_to(ROOT)),str(target.relative_to(ROOT))],cwd=ROOT,capture_output=True,text=True,check=True).stdout,'method':'same-provider same-volume rename of only implicated generated DEX; preserve inode, do not delete','limits':'DATALESS byte digest unavailable before rename; no claim of content equality, filesystem origin or broad cleanup. No source or protected asset moved.'}
 with (D/'dex-quarantine-before.json').open('x') as f: json.dump(record,f,indent=2)
 try:
  os.rename(source,target)
  after=state(target)
  assert all(record['before'][k]==after[k] for k in ('bytes','inode','device'))
  record.update(exit=0,after=after)
 except Exception as e:
  record.update(exit=1,error=repr(e),source_exists=source.exists(),target_exists=target.exists())
 with (D/'dex-quarantine-after.json').open('x') as f: json.dump(record,f,indent=2)
 with (D/'command-ledger.jsonl').open('a') as f: f.write(json.dumps(record)+'\n')
 print(json.dumps(record,indent=2))
 raise SystemExit(record['exit'])
