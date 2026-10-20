"""Execute explicit synthetic CLI and independently verify outputs; no stores."""
import collections
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import re
import xml.etree.ElementTree as ET
from evaluation.test_legacy_export import fixture
from evaluation.legacy_export import validate_bytes

ROOT=Path.cwd()
HERE=ROOT/'benchmarking/study_evidence/20261015/c2'
require_run = sys.argv[1] if len(sys.argv)==2 else ''
if re.fullmatch(r'synthetic-cli-[a-z0-9-]+',require_run) is None: raise SystemExit(2)
OUT=HERE/require_run
SOURCE_PATHS=['evaluation/'+name for name in ('__init__.py','legacy_export.py','synthetic_descriptive.py','export_cli.py','test_legacy_export.py','test_synthetic_descriptive.py','test_export_cli.py')]+['benchmarking/study_evidence/20261015/c2/exercise.py']
SOURCE_HASHES={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in SOURCE_PATHS}

def digest(raw): return hashlib.sha256(raw).hexdigest()
def dump(path,value):
    with path.open('x') as f: json.dump(value,f,indent=2,sort_keys=True,allow_nan=False); f.write('\n')

def cli(label,mode,names,expected):
    args=[sys.executable,'-B','-E','-m','evaluation.export_cli','--mode',mode,'--root',str(OUT),'--source','SYNTHETIC','--output-label',label]
    for name in names: args.extend(['--input',name])
    result=subprocess.run(args,capture_output=True)
    assert result.returncode==expected and result.stderr==b'', (result.returncode,result.stderr)
    assert b'PRIVATE CANARY' not in result.stdout and str(OUT).encode() not in result.stdout
    (OUT/(label+'-'+mode+'.stdout.json')).write_bytes(result.stdout)
    with (HERE/'command-ledger.jsonl').open('a') as f:
        f.write(json.dumps({'label':label+'-'+mode,'argv':args,'exit':result.returncode})+'\n')
    return json.loads(result.stdout)

OUT.mkdir()
names=[]
for i,phases in enumerate([['pre','post'],['pre'],['post'],['pre','pre','post'],[]],1):
    x=fixture()
    participant=f'00000000-0000-4000-8000-{i+100:012d}'
    session=f'00000000-0000-4000-8000-{i+200:012d}'
    x['metadata']['participant_id']=participant
    originals={a['type']:a for a in x['assessments']}
    x['assessments']=[dict(copy.deepcopy(originals[p]),id=j+1,participant_id=participant) for j,p in enumerate(phases)]
    x['sessions'][0].update(id=session,participant_id=participant)
    x['sessions'][0]['attempts'][0]['session_id']=session
    if not phases: x['sessions']=[]
    x['summary']={'total_sessions':len(x['sessions']),'total_attempts':sum(len(s['attempts']) for s in x['sessions']),'total_assessments':len(x['assessments'])}
    name=f'SYNTHETIC-input-{i}.json'; dump(OUT/name,x); names.append(name)

cli('SYNTHETIC-001','describe',names,0)
cli('SYNTHETIC-002','validate',names,0)
(OUT/'SYNTHETIC-invalid.json').write_bytes(b'{"PRIVATE CANARY":NaN}')
for label,mode in [('SYNTHETIC-003','describe'),('SYNTHETIC-004','validate')]:
    result=cli(label,mode,['SYNTHETIC-invalid.json'],2)
    assert result['diagnostics'][0]['code']=='JSON_INVALID'
    assert not (OUT/label).exists()

# Independent recomputation: no validator/descriptive implementation is used here.
roots=[json.loads((OUT/name).read_bytes()) for name in names]
report=json.loads((OUT/'SYNTHETIC-001/report.json').read_bytes())
counts={'exports':len(roots),'participants':len({x['metadata']['participant_id'] for x in roots}),'sessions':sum(len(x['sessions']) for x in roots),'attempts':sum(len(s['attempts']) for x in roots for s in x['sessions']),'assessments':sum(len(x['assessments']) for x in roots)}
assert report['counts']==counts
assert report['matching']=={'paired':1,'unmatched_pre':1,'unmatched_post':1,'ambiguous':1,'no_assessments':1}
for phase in ('pre','post'):
    values=[json.loads(a['responses']) for x in roots for a in x['assessments'] if a['type']==phase]
    for field in ('fslConfidence','signsKnown','ageGroup','gender'):
        freq=collections.Counter(str(v[field]) for v in values if field in v)
        assert all(count==freq.get(key,0) for key,count in report['frequencies'][phase][field].items())
    if phase=='post':
        for index,freq in enumerate(report['frequencies'][phase]['susScores']):
            expected=collections.Counter(str(v['susScores'][index]) for v in values)
            assert all(count==expected.get(key,0) for key,count in freq.items())
for field in ('ageGroup','gender','openFeedback'):
    values=[json.loads(a['responses']) for x in roots for a in x['assessments'] if field!='openFeedback' or a['type']=='post']
    expected={'present':sum(field in v for v in values),'absent':sum(field not in v for v in values)}
    if field=='openFeedback': expected['empty']=sum(v.get(field)=='' for v in values)
    assert report['completeness'][field]==expected
hashes={}
for label in ('SYNTHETIC-001','SYNTHETIC-002'):
    manifest=json.loads((OUT/label/'manifest.json').read_bytes())
    assert manifest['inputs']==[{'index':i,'sha256':digest((OUT/n).read_bytes())} for i,n in enumerate(names)]
    for name,h in manifest['artifacts'].items(): assert digest((OUT/label/name).read_bytes())==h
    for name in ('report.json','manifest.json'): hashes[label+'/'+name]=digest((OUT/label/name).read_bytes())
assert SOURCE_HASHES=={name:digest((ROOT/name).read_bytes()) for name in SOURCE_PATHS}
dump(OUT/'independent-cli-verification.json',{'source_hashes':SOURCE_HASHES,'synthetic':True,'cli_runs':4,'valid_exits':[0,0],'invalid_exits':[2,2],'counts':counts,'output_hashes':hashes,'matching':report['matching'],'all_frequencies_completeness_and_hashes_verified':True})

# Read only the authoritative previously executed isolated synthetic native run.
binding=json.loads((ROOT/'benchmarking/study_evidence/20261015/controller/a3a-acceptance-and-consumer-binding.json').read_bytes())
manifest_path=ROOT/binding['manifest']; raw=manifest_path.read_bytes()
assert digest(raw)==binding['manifest_sha256']
m=json.loads(raw)
assert m['run_id']==binding['expected_run_id'] and m['synthetic_origin'] is True and m['producer_outcome']=='success'
xml=ET.parse(ROOT/binding['producer_xml']).getroot()
assert int(xml.attrib['tests'])==5 and int(xml.attrib['failures'])==int(xml.attrib['errors'])==int(xml.attrib['skipped'])==0
ledger=[json.loads(line) for line in (ROOT/binding['producer_ledger']).read_text().splitlines() if line]
# Explicit accepted parent success evidence, not the producer manifest alone.
assert any(row.get('label')==binding['producer_label'] and row.get('exit')==0 for row in ledger)
assert all(digest((ROOT/path).read_bytes())==h for path,h in m['source_hashes'].items())
observations=[]
for name in ('external-export.json','internal-export.json','reopened-export.json'):
    artifact=next(a for a in m['artifacts'] if a['path']==name)
    raw=(manifest_path.parent/name).read_bytes()
    assert digest(raw)==artifact['sha256'] and len(raw)==artifact['bytes']
    x=json.loads(raw)
    result=validate_bytes(raw)
    expected_valid=name=='reopened-export.json'
    assert result['valid']==expected_valid
    if not expected_valid: assert result['diagnostics'][0]['code']=='REQUIRED'
    observations.append({'artifact':name,'sha256':digest(raw),'counts':{'sessions':len(x['sessions']),'attempts':sum(len(s['attempts']) for s in x['sessions']),'assessments':len(x['assessments'])},'validation':result})
dump(OUT/'native-contract-audit.json',{'synthetic':True,'binding_sha256':digest((ROOT/'benchmarking/study_evidence/20261015/controller/a3a-acceptance-and-consumer-binding.json').read_bytes()),'manifest_sha256':binding['manifest_sha256'],'successful_producer_tests':5,'source_hashes_matched':len(m['source_hashes']),'observations':observations,'limitation':'Transport producer uses synthetic/stage response keys, not UI questionnaire responses; expected REQUIRED rejection is not an app repair or human instrument approval.'})
print(json.dumps({'counts':counts,'output_hashes':hashes,'native_artifacts_verified':len(observations)},sort_keys=True))
