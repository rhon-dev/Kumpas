"""Independent APK ZIP/assets/ABI readback plus accepted inspector composition."""
import copy,datetime,fcntl,hashlib,json,os,shutil,subprocess,zipfile
from pathlib import Path
D=Path(__file__).resolve().parent
ROOT=D.parents[3]
SCRATCH=Path.home()/'.hermes/cache/scratch/kumpas-d-20261018'
E=D.parent

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,obj):
 with p.open('x') as f:json.dump(obj,f,indent=2)
def stream_sha(f):
 h=hashlib.sha256()
 for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
with (SCRATCH.parent/'kumpas-gradle.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 protected=json.loads((D/'protected-before.json').read_text())['hashes']
 historical=json.loads((E/'c1/historical-release-packaging-expectation.json').read_text())
 before=json.loads((D/'historical-apk-preservation.json').read_text())
 build_debug=json.loads((D/'debug-test-build-fresh3-result.json').read_text())
 build_release=json.loads((D/'release-build-retry3-result.json').read_text())
 assert build_debug['exit']==build_release['exit']==0
 assert not build_debug['source_changes'] and not build_release['source_changes']
 paths={'debug':'app/build/app/outputs/apk/debug/app-debug.apk','android_test':'app/build/app/outputs/apk/androidTest/debug/app-debug-androidTest.apk','release':'app/build/app/outputs/flutter-apk/app-release.apk'}
 snapshots=SCRATCH/'final-apks';snapshots.mkdir()
 records={}
 for kind,name in paths.items():
  p=ROOT/name
  build=build_release if kind=='release' else build_debug
  expected=build['artifacts'][name]
  assert sha(p)==expected['sha256'] and p.stat().st_size==expected['bytes']
  target=snapshots/(kind+'.apk');shutil.copy2(p,target)
  assert sha(target)==expected['sha256']
  with zipfile.ZipFile(p) as z:
   names=z.namelist()
   assert len(names)==len(set(names))
   corrupt=z.testzip();assert corrupt is None
   native=sorted(n for n in names if n.startswith('lib/') and not n.endswith('/'))
   abis=sorted({n.split('/')[1] for n in native})
   flutter=sorted({n.split('/')[1] for n in native if n.endswith('/libflutter.so')})
   app_abis=sorted({n.split('/')[1] for n in native if n.endswith('/libapp.so')})
   assets={}
   missing=[]
   if kind!='android_test':
    for asset,binding in historical['assets'].items():
     assert protected[binding['source']]==binding['sha256']==sha(ROOT/binding['source'])
     if asset not in names:missing.append(asset);continue
     with z.open(asset) as f:assets[asset]=stream_sha(f)
     assert assets[asset]==binding['sha256']
    assert not missing and len(assets)==5
  records[kind]={'path':name,'snapshot':str(target),'sha256':sha(p),'bytes':p.stat().st_size,'native_files':native,'all_native_abis':abis,'flutter_abis':flutter,'app_abis':app_abis,'assets':assets,'missing_required_assets':missing,'zip_crc_error':corrupt,'build_result':build['label']+'-result.json','build_log_sha256':build['log_sha256'],'source_manifest':build['source_manifest'],'source_manifest_sha256':build['source_manifest_sha256'],'independent_build_run_provenance':True,'signature_verified':False,'elf_verified':False,'installed_or_runtime_verified':False}
  if kind=='android_test':continue
  expectation=copy.deepcopy(historical)
  expectation.update(artifact_kind='fresh_build',apk_sha256=expected['sha256'])
  if kind=='debug':
   # Native path expectation is from preserved pre-build APK, not learned
   # from the artifact under test. Protected assets remain independent.
   with zipfile.ZipFile(before[name]['snapshot']) as old:
    expectation['native_files']=sorted(n for n in old.namelist() if n.startswith('lib/') and not n.endswith('/'))
    expectation['abis']=sorted({n.split('/')[1] for n in expectation['native_files']})
  expectation['protected']=protected
  exp=D/('final-'+kind+'-expectation.json');save(exp,expectation)
  def inspect(label,expected_path,expected_exit):
   cmd=['/opt/homebrew/bin/python3.11','-B','-E','benchmarking/inspect_release.py','--repo-root',str(ROOT),'--expectation',str(expected_path),'--apk',str(p),'--output-root',str(D),'--output',str(D/(label+'-inspection.json'))]
   log=D/(label+'-inspection.log')
   with log.open('x') as f:result=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
   record={'event':'inspector','label':label,'command':cmd,'at':datetime.datetime.now().astimezone().isoformat(),'exit':result.returncode,'expected_exit':expected_exit,'log':log.name,'log_sha256':sha(log),'expectation_sha256':sha(expected_path)}
   with (D/'command-ledger.jsonl').open('a') as f:f.write(json.dumps(record)+'\n')
   assert result.returncode==expected_exit,(label,log.read_text())
   if expected_exit==0:
    assert json.loads((D/(label+'-inspection.json')).read_text())==json.loads(log.read_text())
   return record
  records[kind]['accepted_inspector']=inspect('final-'+kind,exp,0)
  if kind=='release':
   strict=copy.deepcopy(expectation)
   strict['abis']=['arm64-v8a'];strict['native_files']=[n for n in strict['native_files'] if n.startswith('lib/arm64-v8a/')]
   strictpath=D/'final-release-strict-arm64-expectation.json';save(strictpath,strict)
   records[kind]['strict_arm64_probe']=inspect('final-release-strict-arm64',strictpath,1)
   records[kind]['strict_arm64_accepted']=False
 save(D/'artifact-readback.json',{'at':datetime.datetime.now().astimezone().isoformat(),'artifacts':records,'limits':'Actual host build-run/source/log binding is composed here; inspector alone deliberately reports current_source_build_provenance=false. Release native expectations retained C1 three-ABI historical packaging, not a newly approved ABI policy. Debug native paths independently from preserved baseline. Test APK has no model/native requirement. CRC and hashes are not signatures/ELF/runtime claims.'})
 print(json.dumps({k:{n:v for n,v in row.items() if n in ('path','sha256','bytes','all_native_abis','flutter_abis','strict_arm64_accepted','build_result')} for k,row in records.items()},indent=2))
