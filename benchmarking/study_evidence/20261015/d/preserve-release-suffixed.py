"""Preserve the exact malformed release ZIP entry's generated source."""
from pathlib import Path
import datetime,fcntl,hashlib,json,os,subprocess
D=Path(__file__).resolve().parent; ROOT=D.parents[3]
source=ROOT/'app/build/app/intermediates/flutter/release/flutter_assets/NativeAssetsManifest 2.json'
peer=source.with_name('NativeAssetsManifest.json')
target=ROOT/'app/build/kumpas-d-quarantine/NativeAssetsManifest 2.json'
def state(p):
 s=p.stat();return {'path':str(p),'bytes':s.st_size,'inode':s.st_ino,'device':s.st_dev,'flags':s.st_flags,'sha256':None if s.st_flags & 0x40000000 else hashlib.sha256(p.read_bytes()).hexdigest()}
with (Path.home()/'.hermes/cache/scratch/kumpas-gradle.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 assert not target.exists()
 row={'event':'release-generated-quarantine','at':datetime.datetime.now().astimezone().isoformat(),'reason':'final-release-inspection.log rejects assets/flutter_assets/NativeAssetsManifest 2.json; exact generated input independently identified','before':state(source),'counterpart':state(peer),'git_ignored':subprocess.run(['git','check-ignore','-v',str(source.relative_to(ROOT)),str(peer.relative_to(ROOT))],cwd=ROOT,capture_output=True,text=True,check=True).stdout}
 with (D/'release-generated-quarantine-before.json').open('x') as f:json.dump(row,f,indent=2)
 os.rename(source,target);row['after']=state(target)
 assert all(row['before'][k]==row['after'][k] for k in ('inode','device','bytes','sha256'))
 with (D/'release-generated-quarantine-after.json').open('x') as f:json.dump(row,f,indent=2)
 with (D/'command-ledger.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
 print(json.dumps(row,indent=2))
