"""Independent stdlib readback/count/hash check; never loads test rows/models."""
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
OUT=ROOT.parent/'kumpas-data/diagnostics/20261017-validation-v1-3'

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def load(path):
    def reject(_): raise ValueError('NONFINITE_JSON')
    return json.loads(Path(path).read_text(),parse_constant=reject)

if __name__=='__main__':
    config=load(HERE/'current-inputs-v3.json')
    complete=load(OUT/'INCOMPLETE-manifest.json')
    campaign=load(OUT/'campaign.json')
    summary=load(OUT/'summary.json')
    assert not (OUT/'manifest.json').exists()
    assert complete['status']=='INCOMPLETE_SOURCE_METADATA'
    assert complete['n']==150
    assert all(digest(OUT/name)==sha for name,sha in complete['outputs'].items())
    assert all(digest(config['paths'][key])==sha for key,sha in config['sha256'].items())
    assert campaign['inputs']==config
    records=[json.loads(line) for line in (OUT/'clips.jsonl').read_text().splitlines()]
    assert len(records)==150
    assert [r['clip'] for r in records]==config['ordered_clips']
    unavailable=[r['clip'] for r in records if r['metadata_status']=='unavailable']
    assert len(unavailable)==summary['source_metadata_unavailable']==complete['source_metadata_unavailable']==134
    for record in records:
        assert record['partition']=='validation'
        if record['metadata_status']=='unavailable':
            assert record['metadata_error']=='SOURCE_NOT_RESIDENT'
            assert 'npz_sha256' not in record and 'video_sha256' not in record
        else:
            assert digest(record['npz_path'])==record['npz_sha256']
            assert digest(record['video_path'])==record['video_sha256']
            assert len(record['sample_indices'])==len(record['landmark_frame_sha256'])==30
    recomputed={}; errors=[]; abs_errors=[]; confidence_delta=[]; margin_delta=[]
    for model in ['keras','candidate']:
        matrix=[[0]*50 for _ in range(50)]
        for row in records:
            probabilities=row[model]['probabilities']
            assert len(probabilities)==50 and all(type(v) in (float,int) and math.isfinite(v) and 0<=v<=1 for v in probabilities)
            assert abs(sum(probabilities)-1)<1e-5
            order=sorted(range(50),key=lambda k:(-probabilities[k],k))
            assert row[model]['top1']==order[0]
            assert row[model]['confidence']==probabilities[order[0]]
            assert row[model]['margin']==probabilities[order[0]]-probabilities[order[1]]
            matrix[row['dense_label']][order[0]]+=1
        correct=sum(matrix[i][i] for i in range(50))
        assert matrix==summary[model]['confusion']
        assert correct==summary[model]['correct']==144
        assert all(sum(matrix[i])==3 for i in range(50))
        macro=sum(2*matrix[i][i]/(sum(matrix[i])+sum(row[i] for row in matrix)) if sum(matrix[i])+sum(row[i] for row in matrix) else 0 for i in range(50))/50
        assert math.isclose(macro,summary[model]['macro_f1'],rel_tol=0,abs_tol=1e-15)
        recomputed[model]={'n':150,'correct':correct,'accuracy':correct/150,'macro_f1':macro,'classes':50}
    for row in records:
        deltas=[abs(a-b) for a,b in zip(row['keras']['probabilities'],row['candidate']['probabilities'])]
        abs_errors.extend(deltas)
        assert max(deltas)==row['max_absolute_probability_error']
        confidence_delta.append(row['candidate']['confidence']-row['keras']['confidence'])
        margin_delta.append(row['candidate']['margin']-row['keras']['margin'])
        if row['keras']['top1']!=row['dense_label']:
            errors.append({'clip':row['clip'],'truth':row['dense_label'],'prediction':row['keras']['top1'],'metadata_status':row['metadata_status']})
    assert max(abs_errors)==summary['drift']['max_absolute_probability_error']
    assert math.isclose(sum(abs_errors)/len(abs_errors),summary['drift']['mean_absolute_probability_error'],rel_tol=0,abs_tol=1e-16)
    disagreements=sum(r['keras']['top1']!=r['candidate']['top1'] for r in records)
    assert disagreements==summary['drift']['top1_disagreements']==0
    events=[json.loads(line) for line in (OUT/'events.jsonl').read_text().splitlines()]
    for model in ('keras','candidate'):
        assert [e['n'] for e in events if e['event']==model+'_clip_complete']==list(range(1,151))
    assert next(i for i,e in enumerate(events) if e['event']=='keras_released')<next(i for i,e in enumerate(events) if e['event']=='candidate_clip_complete')
    initial=load(HERE/'preservation-before.json')
    mismatches=[p for p,h in initial.items() if digest(p)!=h]
    protected=load(HERE.parent/'b1/protected-hashes.json')['files']
    protected_mismatch=[p for p,h in protected.items() if digest(ROOT/p)!=h['expected']]
    native=load(HERE.parent/'b1/native-binding-before.json')['source_hashes']
    native_mismatch=[p for p,h in native.items() if digest(ROOT/p)!=h]
    a3b=load(HERE.parent/'controller/a3b-acceptance-20261017.json')['source_hashes']
    a3b_mismatch=[p for p,h in a3b.items() if digest(ROOT/p)!=h]
    b1=load(HERE.parent/'controller/b1-acceptance-20261017.json')
    b1_mismatch=[p for p,h in b1['source_hashes'].items() if digest(ROOT/p)!=h]
    assert len(protected)==82 and len(native)==42 and len(a3b)==4
    assert not (mismatches or protected_mismatch or native_mismatch or a3b_mismatch or b1_mismatch)
    assert digest(Path(b1['campaign'])/'manifest.json')==b1['campaign_manifest_sha256']
    # Additional coverage-only checks of strict default and narrow salvage boundary.
    spec=importlib.util.spec_from_file_location('synthetic_b2',ROOT/'training/tests/test_validation_campaign.py')
    tests=importlib.util.module_from_spec(spec); spec.loader.exec_module(tests)
    fixture=tests.InputTests(); fixture.setUp()
    try:
        import validation_campaign as vc
        root=Path(fixture.tmp.name); output_root=root/'extra'; output_root.mkdir()
        for function,error,name in [(vc.run_campaign,'SOURCE_NOT_RESIDENT','strict'),
                                    (vc.run_incomplete_campaign,'INVALID_CLIP_METADATA','bad_metadata')]:
            with patch.object(vc,'clip_metadata',side_effect=ValueError(error)),patch.object(vc,'predict_frozen') as forbidden:
                try: function(fixture.config,str(output_root),str(output_root/name),str(root/'npz'),str(root/'raw'))
                except ValueError as exc: assert str(exc)==error
                else: raise AssertionError('FAIL_CLOSED_REQUIRED')
                forbidden.assert_not_called()
                assert not (output_root/name/'manifest.json').exists()
                assert not (output_root/name/'clips.jsonl').exists()
        boundary='strict nonresident failure; salvage rejects malformed metadata; no predictions called:PASS'
    finally: fixture.doCleanups()
    result={'status':'DONE_WITH_CONCERNS','full_source_provenance':'BLOCKED_SOURCE_NOT_RESIDENT',
        'external_output':str(OUT),'campaign_sha256':digest(OUT/'campaign.json'),
        'incomplete_manifest_sha256':digest(OUT/'INCOMPLETE-manifest.json'),
        'outputs_sha256':complete['outputs'],'config_sha256':digest(HERE/'current-inputs-v3.json'),
        'source_sha256':{str(ROOT/p):digest(ROOT/p) for p in ['training/models/validation_campaign.py','training/tests/test_validation_campaign.py']},
        'recomputed':recomputed,'drift':summary['drift'],'errors':errors,
        'source_metadata_available':150-len(unavailable),'source_metadata_unavailable':len(unavailable),
        'unavailable_clips':unavailable,'preservation':{'initial_count':len(initial),'initial_mismatches':mismatches,
        'protected_count':len(protected),'protected_mismatches':protected_mismatch,'native_count':len(native),'native_mismatches':native_mismatch,
        'a3b_count':len(a3b),'a3b_mismatches':a3b_mismatch,'b1_source_mismatches':b1_mismatch,'b1_manifest_matches':True},
        'additional_boundary_coverage':boundary,'promotion_status':'diagnostic_not_approved_for_promotion'}
    path=HERE/'verification.json'
    with path.open('x') as stream: json.dump(result,stream,indent=2,allow_nan=False); stream.write('\n')
    print(json.dumps({k:result[k] for k in ['status','full_source_provenance','incomplete_manifest_sha256','recomputed','drift','source_metadata_available','source_metadata_unavailable','preservation','additional_boundary_coverage']},indent=2,allow_nan=False))
