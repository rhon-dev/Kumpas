"""Read historical generated artifacts only, never original video/NPZ sources."""
from pathlib import Path
import datetime,hashlib,json,sys
D=Path(__file__).resolve().parent
ROOT=D.parents[3]
E=D.parent
DATA=ROOT.parent/'kumpas-data'
def sha(p):
 p=Path(p)
 if p.stat().st_flags & 0x40000000: raise RuntimeError('DATALESS artifact refused: '+str(p))
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def check(p,digest):
 actual=sha(p)
 assert actual==digest,str(p)
 return actual
campaign=DATA/'parity/20261017-validation-v1'
b1_accept=json.loads((E/'controller/b1-acceptance-20261017.json').read_text())
check(campaign/'manifest.json',b1_accept['campaign_manifest_sha256'])
manifest=json.loads((campaign/'manifest.json').read_text())
selection=json.loads((campaign/'selection.json').read_text())
source_bindings=[]
for name,expected in selection['source_sha256'].items():
 current=sha(ROOT/name)
 historical=E/'followups/before'/name if current!=expected else ROOT/name
 check(historical,expected)
 source_bindings.append({'path':name,'historical_sha256':expected,'current_sha256':current,'historical_readback':str(historical)})
frames=0
for fixture in manifest['fixtures']:
 directory=campaign/fixture['directory']
 check(directory/'fixture.json',fixture['fixture_manifest_sha256'])
 for name,expected in fixture['files'].items(): check(directory/name,expected)
 replay=json.loads((directory/'frames/manifest.json').read_text())
 for frame in replay['frames']:
  check(directory/'frames'/frame['filename'],frame['sha256']);frames+=1
assert len(manifest['fixtures'])==6 and frames==180
v=json.loads((E/'b2/verification.json').read_text())
root=Path(v['external_output']);root=root if root.is_absolute() else ROOT/root
outputs={n:check(root/n,h) for n,h in v['outputs_sha256'].items()}
check(root/'campaign.json',v['campaign_sha256'])
check(root/'INCOMPLETE-manifest.json',v['incomplete_manifest_sha256'])
assert not (root/'manifest.json').exists()
config=json.loads((E/'b2/current-inputs-v3.json').read_text())
roles=[]
prior={'source_code_0':E/'b2/review-fix-1-before-validation_campaign.py.txt','source_code_1':E/'b2/review-fix-1-before-test_validation_campaign.py.txt','source_code_11':E/'followups/before/benchmarking/pipeline_parity.py'}
# Check all source-code roles, not source arrays or raw sources. Old helper AND
# tests are execution identities, current repaired versions are distinct.
for role,path in config['paths'].items():
 if not role.startswith('source_code_'):continue
 expected=config['sha256'][role]
 current=sha(path)
 historic=prior.get(role,Path(path))
 check(historic,expected)
 roles.append({'role':role,'path':path,'historical_sha256':expected,'current_sha256':current,'historical_readback':str(historic)})
summary=json.loads((root/'summary.json').read_text())
records=[json.loads(x) for x in (root/'clips.jsonl').read_text().splitlines()]
# Retain only aggregate results; no probabilities, landmarks or media in Git.
counts={name:{'count':summary[name]['n'],'correct':summary[name]['correct']} for name in ('keras','candidate')}
assert len(records)==150 and summary['source_metadata_unavailable']==134
assert all(row=={'count':150,'correct':144} for row in counts.values())
accepted={}
for label in ('a3b-acceptance-20261017.json','b2-bounded-acceptance-20261018.json','followups-acceptance-20261018.json'):
 obj=json.loads((E/'controller'/label).read_text())
 accepted[label]={p:check(ROOT/p,h) for p,h in obj['source_hashes'].items()}
result={'at':datetime.datetime.now().astimezone().isoformat(),'b1':{'fixtures':len(manifest['fixtures']),'pngs':frames,'manifest_sha256':sha(campaign/'manifest.json'),'selection_sha256':sha(campaign/'selection.json'),'source_bindings':source_bindings},'b2':{'outputs':outputs,'config_sha256':sha(E/'b2/current-inputs-v3.json'),'campaign_sha256':sha(root/'campaign.json'),'incomplete_manifest_sha256':sha(root/'INCOMPLETE-manifest.json'),'source_code_roles':roles,'model_counts':counts,'missing_source_records':summary['source_metadata_unavailable'],'successful_manifest_exists':False},'current_acceptance_matches':accepted,'limits':'Generated artifact and historical-source readback only. No old current-source verifier, raw video/NPZ read, inference, regeneration, metadata repair, source rebinding or final-test/generalization claim.'}
if '--check-only' not in sys.argv:
 with (D/'historical-readback.json').open('x') as f:json.dump(result,f,indent=2)
else:
 previous=json.loads((D/'historical-readback.json').read_text())
 assert {k:v for k,v in previous.items() if k!='at'}=={k:v for k,v in result.items() if k!='at'}
print(json.dumps({'b1_fixtures':6,'b1_pngs':frames,'b2_counts':counts,'b2_missing_source_records':134,'b2_source_roles':len(roles),'current_acceptance_matches':True},indent=2))
