"""Synthetic frozen evaluator metrics/lifecycle tests; no real test/model data."""
import importlib
from pathlib import Path
from typing import Any
import json
import numpy as np
import pytest
from .test_train import synthetic_bundle, train, rewrite_json


def evaluator(): return importlib.import_module('training.holistic_migration.evaluate')


def test_metrics_all50_sparse_originals_and_unknown_denominators(tmp_path):
    e=evaluator(); t=train(); b,a=synthetic_bundle(tmp_path/'bundle')
    data=t._read_bundle(b,a,evidence_kind='synthetic_in_process'); classes=data.manifest['classes']
    ids=['synthetic/a','synthetic/b','synthetic/c']
    rows=[dict(clip_id=s,dense_id=y,partition='test',reason='eligible') for s,y in zip(ids,[25,25,1])]
    rows.append(dict(clip_id='synthetic/missing',dense_id=49,partition='test',reason='no_hands'))
    probs=np.zeros((3,50),np.float32); probs[np.arange(3),[25,1,1]]=1
    r=e.metrics(np.array([25,25,1],np.int64),probs,ids,classes,rows,partition='test')
    assert len(r['per_class'])==50 and len(r['confusion'])==50
    assert r['per_class'][25]['original_id']==49
    assert r['per_class'][25]['recall']==.5 and r['per_class'][25]['precision']==1
    assert r['per_class'][1]['recall']==1 and r['per_class'][1]['precision']==.5
    assert r['macro_f1']==pytest.approx((2/3+2/3)/50)
    assert r['accuracy']==pytest.approx(2/3)
    assert r['all_declared']==dict(declared=4,eligible=3,ineligible=1,unknown_missing=1,correct_eligible=2)
    assert r['per_class'][49]['declared']==1 and r['per_class'][49]['support']==0 and r['per_class'][49]['unknown_missing']==1
    assert r['exclusions']==[dict(clip_id='synthetic/missing',dense_id=49,reason='no_hands')]
    assert r['false_accept_rate'] is None and r['negative_status']=='unmeasured_no_observed_validation_negatives'
    assert r['live_ready'] is False and r['zero_denominator']=='precision/recall/F1=0; empty accuracy=null; macro includes all50'
    empty=e.metrics(np.empty(0,np.int64),np.empty((0,50),np.float32),[],classes,rows[3:],partition='test')
    assert empty['accuracy'] is None and empty['macro_f1']==0



def frozen_synthetic_run(tmp_path):
    from .test_train import encoded_data,SyntheticBackend
    t=train(); data=encoded_data(tmp_path); backend=SyntheticBackend(); tiny=tmp_path/'tiny'; run=tmp_path/'fit'
    t._execute(data,'tiny-fit',tiny,_backend=backend,_epochs=2)
    t._execute(data,'fit',run,tiny_proof=tiny/'tiny-proof.json',_backend=backend,_epochs=2)
    return data,backend,run


def test_separate_evaluator_starts_before_test_and_completed_is_readback_only(tmp_path,monkeypatch):
    e=evaluator(); data,backend,run=frozen_synthetic_run(tmp_path); out=tmp_path/'evaluation'
    real_open=Path.open; accesses=[]
    def guarded(path,*args,**kwargs):
        if Path(path).name.endswith('_test.npy'):
            assert (out/'evaluation-start.json').exists()
            start=json.loads((out/'evaluation-start.json').read_text())
            assert start['status']=='evaluation_started' and start['evaluation_kind']=='exploratory_reused_test'
            accesses.append(Path(path).name)
        return real_open(path,*args,**kwargs)
    monkeypatch.setattr(Path,'open',guarded)
    r=e._evaluate(run,data,out,_backend=backend)
    assert r['status']=='exploratory_evaluation_complete' and accesses
    report=json.loads((out/'report.json').read_text())
    assert report['evaluation_kind']=='exploratory_reused_test' and report['live_ready'] is False
    assert report['all_declared']['declared']==50 and len(report['per_class'])==50
    count=len(accesses); loaded=backend.loaded
    assert e._evaluate(run,data,out,_backend=backend)==r
    assert len(accesses)==count and backend.loaded==loaded
    assert not (run/'test-report.json').exists()


@pytest.mark.parametrize('fault',['model','policy','source','selection','config'])
def test_frozen_tamper_denied_before_test_or_output(tmp_path,monkeypatch,fault):
    e=evaluator(); data,backend,run=frozen_synthetic_run(tmp_path); out=tmp_path/'evaluation'
    target={'model':'model.keras','policy':'policy.json','source':'selection.json','selection':'selection.json','config':'config.json'}[fault]
    if fault=='source':
        value=json.loads((run/target).read_text()); value['identity']['sources']['evaluate.py']='0'*64; rewrite_json(run/target,value)
    elif fault=='selection':
        value=json.loads((run/target).read_text()); value['best_epoch']=2; rewrite_json(run/target,value)
    else: (run/target).write_text('altered')
    real=Path.open
    def guard(path,*args,**kwargs):
        assert not Path(path).name.endswith('_test.npy'); return real(path,*args,**kwargs)
    monkeypatch.setattr(Path,'open',guard)
    with pytest.raises((ValueError,KeyError)): e._evaluate(run,data,out,_backend=backend)
    assert not out.exists()


def test_existing_incomplete_evaluation_does_not_rerun(tmp_path,monkeypatch):
    e=evaluator(); data,backend,run=frozen_synthetic_run(tmp_path); out=tmp_path/'evaluation'; out.mkdir()
    with pytest.raises(ValueError): e._evaluate(run,data,out,_backend=backend)
    assert not (out/'evaluation-start.json').exists()


def test_actual_evaluator_cli_synthetic_refusal_before_output(tmp_path):
    import subprocess,sys,os
    t=train(); b,a=synthetic_bundle(tmp_path/'bundle'); out=tmp_path/'not-created'
    p=subprocess.run([sys.executable,'-E','-B','-m','training.holistic_migration.evaluate','--run',str(tmp_path/'absent-run'),'--bundle',str(b),'--admission',str(a),'--output',str(out)],cwd=t.d.REPO,capture_output=True,text=True)
    assert p.returncode==2 and 'admission status' in p.stderr and not out.exists()



@pytest.mark.parametrize('bad',['nan','shape','range','sum','mapping','duplicate_ids','classes'])
def test_metrics_refuses_invalid_probability_or_output_mapping(tmp_path,bad):
    e=evaluator(); t=train(); b,a=synthetic_bundle(tmp_path/'bundle'); data=t._read_bundle(b,a,evidence_kind='synthetic_in_process')
    classes=data.manifest['classes']; ids=['synthetic/a','synthetic/b']; y=np.array([1,2],np.int64)
    rows=[dict(clip_id=s,dense_id=int(label),partition='test',reason='eligible') for s,label in zip(ids,y)]
    p=np.full((2,50),.02,np.float32)
    if bad=='nan': p[0,0]=np.nan
    if bad=='shape': p=p[:,:49]
    if bad=='range': p[0,0]=-1
    if bad=='sum': p[0]*=.5
    if bad=='mapping': y[:]=0
    if bad=='duplicate_ids': ids[1]=ids[0]; rows[1]['clip_id']=ids[0]
    if bad=='classes': classes=classes[:49]
    with pytest.raises(ValueError): e.metrics(y,p,ids,classes,rows,partition='test')



def test_evaluation_report_failure_is_retained_and_cannot_rerun(tmp_path,monkeypatch):
    e=evaluator(); t=train(); data,backend,run=frozen_synthetic_run(tmp_path); out=tmp_path/'evaluation'
    selection_hash=t.d.sha256(run/'selection.json')
    real=e.metrics
    def fail(*args,**kwargs): raise ValueError('synthetic evaluation report failure')
    monkeypatch.setattr(e,'metrics',fail)
    with pytest.raises(ValueError,match='synthetic evaluation report failure'):
        e._evaluate(run,data,out,_backend=backend)
    assert (out/'evaluation-start.json').exists() and (out/'failure.json').exists()
    assert not (out/'evaluation-complete.json').exists()
    assert t.d.sha256(run/'selection.json')==selection_hash
    monkeypatch.setattr(e,'metrics',real); calls=backend.loaded
    with pytest.raises(ValueError,match='incomplete'): e._evaluate(run,data,out,_backend=backend)
    assert backend.loaded==calls


def test_new_final_readback_failure_revokes_completion_and_blocks_retry(tmp_path,monkeypatch):
    e=evaluator(); t=train(); data,backend,run=frozen_synthetic_run(tmp_path); out=tmp_path/'evaluation'
    assert data.provenance=='synthetic_in_process'
    frozen={p.name:p.read_bytes() for p in run.iterdir() if p.is_file()}
    original=t.d.sha256; injected=[]; saved={}
    failure=OSError('synthetic post-publication report readback failure')
    def final_readback_fault(path):
        path=Path(path)
        if path==out/'report.json' and (out/'evaluation-complete.json').is_file() and not injected:
            injected.append(path)
            saved.update({p.name:p.read_bytes() for p in out.iterdir()
                          if p.is_file() and p.name!='evaluation-complete.json'})
            raise failure
        return original(path)
    monkeypatch.setattr(t.d,'sha256',final_readback_fault)
    with pytest.raises(OSError) as caught:
        e._evaluate(run,data,out,_backend=backend)
    assert caught.value is failure
    assert injected==[out/'report.json'], 'Must reach artifact verification after completion publication'
    assert {'evaluation-start.json','report.json','report.json.pending','evaluation-complete.json.pending',
            'probabilities.npy','predictions.npy','eligible_ids.npy','eligible_labels.npy'}<=saved.keys()
    assert json.loads((out/'failure.json').read_text())['status']=='failed'
    assert {name:(out/name).read_bytes() for name in saved}==saved
    assert {p.name:p.read_bytes() for p in run.iterdir() if p.is_file()}==frozen
    assert not (out/'evaluation-complete.json').exists(), 'Failed final readback must revoke its success receipt'
    monkeypatch.setattr(t.d,'sha256',original)
    real_open=Path.open; real_load=np.load; loaded=backend.loaded
    def no_test_open(path,*args,**kwargs):
        assert not Path(path).name.endswith('_test.npy'), 'Retry reopened/hashed test content'
        return real_open(path,*args,**kwargs)
    def no_test_load(path,*args,**kwargs):
        assert not str(path).endswith('_test.npy'), 'Retry reloaded test content'
        return real_load(path,*args,**kwargs)
    def no_backend(*args,**kwargs): pytest.fail('Failed target must not load or infer again')
    monkeypatch.setattr(Path,'open',no_test_open); monkeypatch.setattr(np,'load',no_test_load)
    monkeypatch.setattr(backend,'load',no_backend); monkeypatch.setattr(backend,'predict',no_backend)
    retained={p.name:p.read_bytes() for p in out.iterdir() if p.is_file()}
    with pytest.raises(ValueError,match='incomplete'):
        e._evaluate(run,data,out,_backend=backend)
    assert backend.loaded==loaded
    assert {p.name:p.read_bytes() for p in out.iterdir() if p.is_file()}==retained
    assert {p.name:p.read_bytes() for p in run.iterdir() if p.is_file()}==frozen


def test_final_readback_primary_survives_failure_receipt_write_error(tmp_path,monkeypatch):
    e=evaluator(); t=train(); data,backend,run=frozen_synthetic_run(tmp_path); out=tmp_path/'evaluation'
    selection=(run/'selection.json').read_bytes(); injected=[]; diagnostic=[]
    primary=ValueError('synthetic final readback primary'); real_readback=e._evaluation_readback
    real_write=t.d.write_json
    def fail_readback(output,start):
        assert (output/'evaluation-complete.json').is_file()
        injected.append(output)
        raise primary
    def fail_diagnostic(path,value):
        if Path(path)==out/'failure.json':
            diagnostic.append(path)
            raise OSError('synthetic diagnostic write failure')
        return real_write(path,value)
    monkeypatch.setattr(e,'_evaluation_readback',fail_readback)
    monkeypatch.setattr(t.d,'write_json',fail_diagnostic)
    with pytest.raises(ValueError) as caught: e._evaluate(run,data,out,_backend=backend)
    assert caught.value is primary and injected==[out] and diagnostic==[out/'failure.json']
    assert not (out/'evaluation-complete.json').exists()
    assert (out/'evaluation-complete.json.pending').is_file() and (out/'report.json').is_file()
    assert (run/'selection.json').read_bytes()==selection
    monkeypatch.setattr(e,'_evaluation_readback',real_readback)
    calls=backend.loaded
    with pytest.raises(ValueError,match='incomplete'): e._evaluate(run,data,out,_backend=backend)
    assert backend.loaded==calls


def test_failed_final_readback_cannot_promote_when_owned_marker_unlink_fails(tmp_path,monkeypatch):
    e=evaluator(); t=train(); data,backend,run=frozen_synthetic_run(tmp_path); out=tmp_path/'evaluation'
    frozen={p.name:p.read_bytes() for p in run.iterdir() if p.is_file()}
    primary=OSError('synthetic final artifact readback failure'); injected=[]; cleanup=[]
    real_hash=t.d.sha256; real_unlink=Path.unlink
    def fault(path):
        if Path(path)==out/'report.json' and (out/'evaluation-complete.json').is_file() and not injected:
            injected.append(path)
            raise primary
        return real_hash(path)
    def cannot_unlink(path,*args,**kwargs):
        if Path(path)==out/'evaluation-complete.json':
            cleanup.append(path)
            raise PermissionError('synthetic marker cleanup failure')
        return real_unlink(path,*args,**kwargs)
    monkeypatch.setattr(t.d,'sha256',fault); monkeypatch.setattr(Path,'unlink',cannot_unlink)
    with pytest.raises(OSError) as caught: e._evaluate(run,data,out,_backend=backend)
    assert caught.value is primary and injected==[out/'report.json'] and cleanup==[out/'evaluation-complete.json']
    assert (out/'evaluation-complete.json').is_file()  # Failed cleanup is retained, never gating.
    assert json.loads((out/'failure.json').read_text())['status']=='failed'
    monkeypatch.setattr(t.d,'sha256',real_hash); monkeypatch.setattr(Path,'unlink',real_unlink)
    real_open=Path.open
    def no_test(path,*args,**kwargs):
        assert not Path(path).name.endswith('_test.npy')
        return real_open(path,*args,**kwargs)
    def no_backend(*args,**kwargs): pytest.fail('Failed cleanup target must not reload or infer')
    monkeypatch.setattr(Path,'open',no_test)
    monkeypatch.setattr(backend,'load',no_backend); monkeypatch.setattr(backend,'predict',no_backend)
    retained={p.name:p.read_bytes() for p in out.iterdir() if p.is_file()}
    with pytest.raises(ValueError,match='failed|incomplete'): e._evaluate(run,data,out,_backend=backend)
    assert {p.name:p.read_bytes() for p in out.iterdir() if p.is_file()}==retained
    assert {p.name:p.read_bytes() for p in run.iterdir() if p.is_file()}==frozen


@pytest.mark.parametrize('fault_target',['evaluation-complete.json','report.json'])
def test_established_completion_survives_transient_readback_failure(tmp_path,monkeypatch,fault_target):
    e=evaluator(); t=train(); data,backend,run=frozen_synthetic_run(tmp_path); out=tmp_path/'evaluation'
    complete=e._evaluate(run,data,out,_backend=backend)
    retained={p.name:p.read_bytes() for p in out.iterdir() if p.is_file()}
    frozen={p.name:p.read_bytes() for p in run.iterdir() if p.is_file()}
    real_open=Path.open; injected=[]
    failure=OSError('synthetic established-completion read fault')
    def guarded(path,*args,**kwargs):
        assert not Path(path).name.endswith('_test.npy'), 'Completed retry accessed test content'
        if Path(path)==out/fault_target and not injected:
            injected.append(path)
            raise failure
        return real_open(path,*args,**kwargs)
    def no_backend(*args,**kwargs): pytest.fail('Completed retry must be readback-only')
    monkeypatch.setattr(Path,'open',guarded)
    monkeypatch.setattr(backend,'load',no_backend); monkeypatch.setattr(backend,'predict',no_backend)
    with pytest.raises(OSError) as caught: e._evaluate(run,data,out,_backend=backend)
    assert caught.value is failure and injected==[out/fault_target]
    assert {p.name:p.read_bytes() for p in out.iterdir() if p.is_file()}==retained
    assert not (out/'failure.json').exists()
    assert e._evaluate(run,data,out,_backend=backend)==complete
    assert {p.name:p.read_bytes() for p in out.iterdir() if p.is_file()}==retained
    assert {p.name:p.read_bytes() for p in run.iterdir() if p.is_file()}==frozen


def test_completion_publication_failure_retains_evidence_without_success(tmp_path,monkeypatch):
    e=evaluator(); t=train(); data,backend,run=frozen_synthetic_run(tmp_path); out=tmp_path/'evaluation'
    frozen={p.name:p.read_bytes() for p in run.iterdir() if p.is_file()}
    real_hash=t.d.sha256; injected=[]
    failure=OSError('synthetic completion publication readback failure')
    def fail_publication(path):
        if Path(path)==out/'evaluation-complete.json' and not injected:
            assert (out/'evaluation-complete.json.pending').is_file() and Path(path).is_file()
            injected.append(path)
            raise failure
        return real_hash(path)
    monkeypatch.setattr(t.d,'sha256',fail_publication)
    with pytest.raises(OSError) as caught: e._evaluate(run,data,out,_backend=backend)
    assert caught.value is failure and injected==[out/'evaluation-complete.json']
    assert not (out/'evaluation-complete.json').exists()
    assert {'evaluation-start.json','failure.json','report.json','report.json.pending','evaluation-complete.json.pending',
            'probabilities.npy','predictions.npy','eligible_ids.npy','eligible_labels.npy'}=={p.name for p in out.iterdir()}
    monkeypatch.setattr(t.d,'sha256',real_hash)
    loaded=backend.loaded; retained={p.name:p.read_bytes() for p in out.iterdir() if p.is_file()}
    real_open=Path.open
    def no_test(path,*args,**kwargs):
        assert not Path(path).name.endswith('_test.npy')
        return real_open(path,*args,**kwargs)
    def no_backend(*args,**kwargs): pytest.fail('Failed publication must not reload or infer')
    monkeypatch.setattr(Path,'open',no_test)
    monkeypatch.setattr(backend,'load',no_backend); monkeypatch.setattr(backend,'predict',no_backend)
    with pytest.raises(ValueError,match='incomplete'): e._evaluate(run,data,out,_backend=backend)
    assert backend.loaded==loaded
    assert {p.name:p.read_bytes() for p in out.iterdir() if p.is_file()}==retained
    assert {p.name:p.read_bytes() for p in run.iterdir() if p.is_file()}==frozen


@pytest.mark.parametrize('publication',['evaluation-complete.json','report.json'])
def test_completion_publication_primary_survives_actual_cleanup_fault(tmp_path,monkeypatch,publication):
    e=evaluator(); t=train(); data,backend,run=frozen_synthetic_run(tmp_path)
    assert data.provenance=='synthetic_in_process'
    out=tmp_path/'evaluation'
    frozen={p.name:p.read_bytes() for p in run.iterdir() if p.is_file()}
    primary=OSError('synthetic '+publication+' publication readback primary')
    secondary=PermissionError('synthetic '+publication+' publication cleanup secondary')
    real_hash=t.d.sha256; real_unlink=Path.unlink; injected=[]; cleanups=[]; saved={}
    def fail_hash(path):
        if Path(path)==out/publication and not injected:
            assert Path(path).is_file() and (out/(publication+'.pending')).is_file()
            saved.update({p.name:p.read_bytes() for p in out.iterdir() if p.is_file()})
            injected.append(path)
            raise primary
        return real_hash(path)
    def fail_unlink(path,*args,**kwargs):
        if Path(path)==out/publication:
            cleanups.append(path)
            raise secondary
        return real_unlink(path,*args,**kwargs)
    monkeypatch.setattr(t.d,'sha256',fail_hash); monkeypatch.setattr(Path,'unlink',fail_unlink)
    with pytest.raises(OSError) as caught: e._evaluate(run,data,out,_backend=backend)
    assert injected==[out/publication] and cleanups==[out/publication]
    expected={'evaluation-start.json','report.json','report.json.pending',
              'probabilities.npy','predictions.npy','eligible_ids.npy','eligible_labels.npy'}
    if publication=='evaluation-complete.json':
        expected.update(['evaluation-complete.json','evaluation-complete.json.pending'])
    assert expected==saved.keys()
    assert {name:(out/name).read_bytes() for name in saved}==saved
    diagnostic=json.loads((out/'failure.json').read_text())
    monkeypatch.setattr(t.d,'sha256',real_hash); monkeypatch.setattr(Path,'unlink',real_unlink)
    real_open=Path.open; real_load=np.load; loaded=backend.loaded
    def no_test_open(path,*args,**kwargs):
        assert not Path(path).name.endswith('_test.npy'), 'Retry reopened/hashed test content'
        return real_open(path,*args,**kwargs)
    def no_test_load(path,*args,**kwargs):
        assert not str(path).endswith('_test.npy'), 'Retry reloaded test content'
        return real_load(path,*args,**kwargs)
    def no_backend(*args,**kwargs): pytest.fail('Failed publication target must not load or infer again')
    monkeypatch.setattr(Path,'open',no_test_open); monkeypatch.setattr(np,'load',no_test_load)
    monkeypatch.setattr(backend,'load',no_backend); monkeypatch.setattr(backend,'predict',no_backend)
    retained={p.name:p.read_bytes() for p in out.iterdir() if p.is_file()}
    with pytest.raises(ValueError,match='failed|incomplete'): e._evaluate(run,data,out,_backend=backend)
    assert backend.loaded==loaded
    assert {p.name:p.read_bytes() for p in out.iterdir() if p.is_file()}==retained
    assert {p.name:p.read_bytes() for p in run.iterdir() if p.is_file()}==frozen
    (tmp_path/'combined-fault-result.json').write_text(json.dumps(dict(
        provenance=data.provenance,injection_after_link_and_pending=True,cleanup_attempts=len(cleanups),
        exact_primary_preserved=caught.value is primary,raised_type=type(caught.value).__name__,
        raised_message=str(caught.value),failure=diagnostic,retry_denied=True,
        retry_backend_loads=backend.loaded-loaded,frozen_run_preserved=True),indent=2)+'\n')
    assert caught.value is primary, 'Publication cleanup must not replace exact primary readback failure'
    assert diagnostic==dict(status='failed',error='OSError',detail=str(primary))


@pytest.mark.parametrize('publication',['evaluation-complete.json','report.json'])
@pytest.mark.parametrize('readback',['digest','json'])
@pytest.mark.parametrize('cleanup_fault',[False,True])
def test_owned_publication_keeps_primary_with_unrelated_context(tmp_path,monkeypatch,publication,readback,cleanup_fault):
    e=evaluator(); path=tmp_path/publication; pending=tmp_path/(publication+'.pending')
    value=dict(status='explicit_synthetic_fixture'); prior=ValueError('unrelated earlier exception')
    primary=PermissionError('synthetic genuine publication primary with unrelated context')
    try:
        raise prior
    except ValueError:
        try: raise primary
        except PermissionError: pass
    assert primary.__context__ is prior
    real_hash=e.d.sha256; real_json=e.d.load_json; real_unlink=Path.unlink
    injected=[]; cleanups=[]
    def fail(path_arg):
        if Path(path_arg)==path:
            assert path.is_file() and pending.is_file()
            injected.append(path_arg)
            raise primary
        return (real_hash if readback=='digest' else real_json)(path_arg)
    def cleanup(path_arg,*args,**kwargs):
        if Path(path_arg)==path:
            cleanups.append(path_arg)
            if cleanup_fault: raise OSError('synthetic secondary unlink failure')
        return real_unlink(path_arg,*args,**kwargs)
    monkeypatch.setattr(e.d,'sha256' if readback=='digest' else 'load_json',fail)
    monkeypatch.setattr(Path,'unlink',cleanup)
    with pytest.raises(PermissionError) as caught: e._publish_json(path,value)
    assert caught.value is primary and primary.__context__ is prior
    assert injected==[path] and cleanups==[path]
    assert path.exists() is cleanup_fault
    assert json.loads(pending.read_text())==value
    if cleanup_fault: assert path.read_bytes()==pending.read_bytes()


@pytest.mark.parametrize('publication',['evaluation-complete.json','report.json'])
@pytest.mark.parametrize('collision',['pending','preexisting_final','appearing_final'])
def test_owned_publication_never_overwrites_or_cleans_unowned_destination(tmp_path,monkeypatch,publication,collision):
    e=evaluator(); path=tmp_path/publication; pending=tmp_path/(publication+'.pending')
    established=b'{"status":"synthetic_preexisting_established_receipt"}\n'
    value=dict(status='explicit_synthetic_new_attempt'); links=[]; real_link=e.os.link
    if collision=='pending': pending.write_bytes(established)
    if collision=='preexisting_final': path.write_bytes(established)
    def link(source,target):
        assert source==pending and target==path and json.loads(pending.read_text())==value
        links.append(target)
        if collision=='appearing_final': path.write_bytes(established)
        return real_link(source,target)
    def no_cleanup(*args,**kwargs): pytest.fail('A publication not linked by this attempt is not owned')
    monkeypatch.setattr(e.os,'link',link); monkeypatch.setattr(Path,'unlink',no_cleanup)
    with pytest.raises(FileExistsError): e._publish_json(path,value)
    if collision=='pending':
        assert pending.read_bytes()==established and not path.exists() and not links
    else:
        assert path.read_bytes()==established and json.loads(pending.read_text())==value and links==[path]


# Exact preserved parent phase-boundary regression (SHA in owner fix4 brief).
"""Bounded synthetic phase distinction; stop before any evaluation reservation.

This adds the missing healthy report-failure consumer control and checks the
material evaluator admission boundary, not another successful full suite.
"""
import json
from pathlib import Path
import sys
import pytest
from training.holistic_migration import evaluate as e
from training.holistic_migration.tests.test_train import train, encoded_data, SyntheticBackend, deny_test_access


@pytest.mark.parametrize('phase', ['selection_publication', 'later_report_generation'])
def test_failure_phase_controls_evaluator_admission(tmp_path, monkeypatch, phase):
    t = train()
    data = encoded_data(tmp_path)
    assert data.provenance == 'synthetic_in_process'
    backend = SyntheticBackend()
    tiny = tmp_path / 'tiny'
    run = tmp_path / 'fit'
    deny_test_access(monkeypatch)
    t._execute(data, 'tiny-fit', tiny, _backend=backend, _epochs=1)
    primary = OSError('explicit synthetic ' + phase)
    injections = []
    cleanups = []
    real_hash = t.d.sha256
    real_unlink = Path.unlink
    def digest(path):
        if Path(path) == run / 'selection.json' and not injections:
            assert Path(path).is_file() and (run / 'selection.json.pending').is_file()
            injections.append(str(path))
            raise primary
        return real_hash(path)
    def unlink(path, *args, **kwargs):
        if Path(path) == run / 'selection.json':
            cleanups.append(str(path))
            raise PermissionError('explicit synthetic rollback fault')
        return real_unlink(path, *args, **kwargs)
    def report_fault(*args, **kwargs):
        assert (run / 'selection.json').is_file()
        injections.append('metrics_after_selection_publication_returned')
        raise primary
    with monkeypatch.context() as fault:
        if phase == 'selection_publication':
            fault.setattr(t.d, 'sha256', digest)
            fault.setattr(Path, 'unlink', unlink)
        else:
            fault.setattr(e, 'metrics', report_fault)
        with pytest.raises(OSError) as caught:
            t._execute(data, 'fit', run, tiny_proof=tiny / 'tiny-proof.json', _backend=backend, _epochs=1)
    assert caught.value is primary and injections
    assert (run / 'failure.json').is_file() and (run / 'selection.json').is_file()
    assert not (run / 'complete.json').exists()
    before = {p.name: p.read_bytes() for p in run.iterdir() if p.is_file()}
    selection = None
    consumer_denial = None
    try:
        selection = e.frozen_selection(run, data)
    except (ValueError, OSError) as exc:
        consumer_denial = type(exc).__name__ + ': ' + str(exc)
    reservations = []
    class StopBeforeReservation(Exception):
        pass
    def stop(output, received):
        assert received is data
        reservations.append(str(output))
        raise StopBeforeReservation('synthetic interception before mkdir/start/checkpoint/test')
    def forbidden(*args, **kwargs):
        pytest.fail('No checkpoint read, model inference, or optimization allowed in admission probe')
    for method in ['build', 'load', 'predict', 'step']:
        monkeypatch.setattr(backend, method, forbidden)
    monkeypatch.setattr(t, '_reserve', stop)
    evaluator_denial = None
    try:
        e._evaluate(run, data, tmp_path / 'never-created-evaluation', _backend=backend)
    except StopBeforeReservation:
        pass
    except (ValueError, OSError) as exc:
        evaluator_denial = type(exc).__name__ + ': ' + str(exc)
    result = dict(phase=phase, provenance=data.provenance,
                  primary_preserved=caught.value is primary, injections=injections,
                  cleanup_attempts=cleanups, failure=json.loads((run / 'failure.json').read_text()),
                  selection_accepted=selection is not None, consumer_denial=consumer_denial,
                  evaluator_reservation_boundary_reached=bool(reservations), evaluator_denial=evaluator_denial,
                  frozen_run_unchanged={p.name:p.read_bytes() for p in run.iterdir() if p.is_file()} == before,
                  evaluation_output_absent=not (tmp_path / 'never-created-evaluation').exists(),
                  actual_source_execution=False, tensorflow_loaded='tensorflow' in sys.modules,
                  evaluation_checkpoint_or_test_inference=False)
    (tmp_path / 'phase-boundary-result.json').write_text(json.dumps(result, indent=2) + '\n')
    assert result['frozen_run_unchanged'] and result['evaluation_output_absent']
    assert not result['tensorflow_loaded']
    if phase == 'later_report_generation':
        assert selection is not None and reservations, 'Successfully frozen selection must survive later reporting failure'
    else:
        assert selection is None and not reservations, 'Unsuccessful selection publication must not unlock evaluator admission'


def test_failed_disposition_publication_denies_actual_evaluator(tmp_path,monkeypatch):
    """The affirmative disposition's own failed readback cannot become a success."""
    t=train(); data=encoded_data(tmp_path); backend=SyntheticBackend()
    tiny=tmp_path/'tiny'; run=tmp_path/'fit'
    t._execute(data,'tiny-fit',tiny,_backend=backend,_epochs=1)
    deny_test_access(monkeypatch)
    marker=run/'selection-disposition.json'; primary=OSError('synthetic disposition final readback')
    real_hash=t.d.sha256; real_unlink=Path.unlink; injections=[]; cleanups=[]
    def digest(path):
        if Path(path)==marker and not injections:
            assert marker.is_file() and marker.with_name(marker.name+'.pending').is_file()
            assert (run/'selection.json').is_file()
            injections.append(str(path)); raise primary
        return real_hash(path)
    def unlink(path,*args,**kwargs):
        if Path(path)==marker:
            cleanups.append(str(path)); raise PermissionError('synthetic disposition rollback fault')
        return real_unlink(path,*args,**kwargs)
    with monkeypatch.context() as fault:
        fault.setattr(t.d,'sha256',digest); fault.setattr(Path,'unlink',unlink)
        with pytest.raises(OSError) as caught:
            t._execute(data,'fit',run,tiny_proof=tiny/'tiny-proof.json',_backend=backend,_epochs=1)
    assert caught.value is primary and injections==cleanups==[str(marker)]
    assert marker.is_file() and (run/'failure.json').is_file() and not (run/'complete.json').exists()
    before={p.name:p.read_bytes() for p in run.iterdir() if p.is_file()}
    reservations=[]
    def forbidden(*args,**kwargs): pytest.fail('Failed disposition must deny backend/test work')
    def reserve(*args,**kwargs): reservations.append(True); raise ValueError('reservation improperly reached')
    for name in ['build','load','predict','step']: monkeypatch.setattr(backend,name,forbidden)
    monkeypatch.setattr(t,'_reserve',reserve)
    accepted=None; error=None
    try: accepted=e.frozen_selection(run,data)
    except (ValueError,OSError) as exc: error=str(exc)
    with pytest.raises((ValueError,OSError)):
        e._evaluate(run,data,tmp_path/'never-evaluated',_backend=backend)
    result=dict(primary_preserved=caught.value is primary,injections=injections,cleanups=cleanups,
                consumer_accepted=accepted is not None,denial=error,reservations=reservations,
                failure=json.loads((run/'failure.json').read_text()),actual_source_execution=False)
    (tmp_path/'disposition-publication-result.json').write_text(json.dumps(result,indent=2)+'\n')
    assert {p.name:p.read_bytes() for p in run.iterdir() if p.is_file()}==before
    assert accepted is None and not reservations, 'Failed disposition publication must not admit residual success'


# Execute the byte-identical retained probe in a fresh process: the full suite's
# bounded architecture smoke deliberately imports TensorFlow in the parent.
_exact_phase_boundary_probe=test_failure_phase_controls_evaluator_admission


@pytest.mark.parametrize('phase',['selection_publication','later_report_generation'])
def test_failure_phase_controls_evaluator_admission(tmp_path,monkeypatch,phase):
    import subprocess
    code=("from pathlib import Path; import pytest; "
          "from training.holistic_migration.tests.test_evaluate import _exact_phase_boundary_probe; "
          "m=pytest.MonkeyPatch(); "
          "_exact_phase_boundary_probe(Path("+repr(str(tmp_path))+"),m,"+repr(phase)+"); m.undo()")
    result=subprocess.run([sys.executable,'-E','-B','-c',code],cwd=train().d.REPO,capture_output=True,text=True)
    (tmp_path/'exact-probe-process.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0,result.stdout+result.stderr
    record=json.loads((tmp_path/'phase-boundary-result.json').read_text())
    assert not record['tensorflow_loaded'] and not record['evaluation_checkpoint_or_test_inference']


def _snapshot_selection_run(run):
    return {p.name:('symlink',str(p.readlink())) if p.is_symlink() else
            ('file',p.read_bytes()) if p.is_file() else ('directory',None) for p in run.iterdir()}


def _assert_selection_denied_without_work(run,data,backend,tmp_path,monkeypatch):
    t=train(); before=_snapshot_selection_run(run); out=tmp_path/'never-created-evaluation'
    deny_test_access(monkeypatch)
    real_open=Path.open
    def guard(path,*args,**kwargs):
        assert Path(path)!=run/'model.keras','Invalid disposition must precede checkpoint hashing'
        return real_open(path,*args,**kwargs)
    def forbidden(*args,**kwargs): pytest.fail('Invalid selection disposition admitted work/reservation')
    monkeypatch.setattr(Path,'open',guard)
    for name in ['build','load','predict','step']: monkeypatch.setattr(backend,name,forbidden)
    monkeypatch.setattr(t,'_reserve',forbidden); monkeypatch.setattr(t,'_partition',forbidden)
    with pytest.raises((ValueError,OSError)): e.frozen_selection(run,data)
    with pytest.raises((ValueError,OSError)): e._evaluate(run,data,out,_backend=backend)
    monkeypatch.setattr(Path,'open',real_open)
    assert not out.exists() and _snapshot_selection_run(run)==before


@pytest.mark.parametrize('bad',['missing','null','bool','list','schema_bool','schema_float',
    'status','hash','source','provenance','extra','directory','dangling_symlink','duplicate'])
def test_required_selection_disposition_schema_denies_before_work(tmp_path,monkeypatch,bad):
    data,backend,run=frozen_synthetic_run(tmp_path)
    assert e.frozen_selection(run,data)['status']=='frozen_validation_selection'
    path=run/'selection-disposition.json'; value: Any=json.loads(path.read_text())
    if bad in ['missing','directory','dangling_symlink']:
        path.unlink()
        if bad=='directory': path.mkdir()
        if bad=='dangling_symlink': path.symlink_to('unopened-synthetic-target')
    elif bad=='duplicate': path.write_text('{"schema_version":0,'+path.read_text().lstrip()[1:])
    else:
        if bad=='null': value=None
        if bad=='bool': value=True
        if bad=='list': value=[]
        if bad=='schema_bool': value['schema_version']=True
        if bad=='schema_float': value['schema_version']=1.0
        if bad=='status': value['status']='unknown'
        if bad=='hash': value['selection_sha256']='0'*64
        if bad=='source': value['identity']['sources']['train.py']='0'*64
        if bad=='provenance': value['identity']['provenance']='source_video'
        if bad=='extra': value['extra']=True
        rewrite_json(path,value)
    _assert_selection_denied_without_work(run,data,backend,tmp_path,monkeypatch)


def _run_later_report_failure(tmp_path,monkeypatch):
    t=train(); data=encoded_data(tmp_path); backend=SyntheticBackend()
    tiny=tmp_path/'tiny'; run=tmp_path/'fit'; primary=OSError('synthetic later fit report')
    t._execute(data,'tiny-fit',tiny,_backend=backend,_epochs=1)
    def fault(*args,**kwargs):
        assert (run/'selection-disposition.json').is_file(); raise primary
    with monkeypatch.context() as m:
        m.setattr(e,'metrics',fault)
        with pytest.raises(OSError) as caught:
            t._execute(data,'fit',run,tiny_proof=tiny/'tiny-proof.json',_backend=backend,_epochs=1)
    assert caught.value is primary and not (run/'complete.json').exists()
    assert e.frozen_selection(run,data)['status']=='frozen_validation_selection'
    return data,backend,run


@pytest.mark.parametrize('bad',['legacy_missing','null','bool','list','schema_bool','schema_float',
    'phase_selection','phase_unknown','phase_null','frozen_false','frozen_int','frozen_string',
    'source','identity_missing','extra','status_success','malformed','directory','dangling_symlink'])
def test_failure_selection_phase_schema_denies_before_work(tmp_path,monkeypatch,bad):
    data,backend,run=_run_later_report_failure(tmp_path,monkeypatch)
    path=run/'failure.json'; failure=json.loads(path.read_text()); value: Any=failure['selection_disposition']
    if bad=='legacy_missing': del failure['selection_disposition']
    elif bad=='status_success': failure['status']='success'
    elif bad=='malformed': path.write_text('{incomplete')
    elif bad in ['directory','dangling_symlink']:
        path.unlink()
        if bad=='directory': path.mkdir()
        else: path.symlink_to('unopened-synthetic-failure-target')
    else:
        if bad=='null': value=None
        if bad=='bool': value=True
        if bad=='list': value=[]
        if bad=='schema_bool': value['schema_version']=True
        if bad=='schema_float': value['schema_version']=1.0
        if bad=='phase_selection': value['phase']='selection'
        if bad=='phase_unknown': value['phase']='unknown'
        if bad=='phase_null': value['phase']=None
        if bad=='frozen_false': value['frozen']=False
        if bad=='frozen_int': value['frozen']=1
        if bad=='frozen_string': value['frozen']='true'
        if bad=='source': value['identity']['sources']['evaluate.py']='0'*64
        if bad=='identity_missing': del value['identity']
        if bad=='extra': value['extra']=True
        failure['selection_disposition']=value
    if bad not in ['malformed','directory','dangling_symlink']: rewrite_json(path,failure)
    _assert_selection_denied_without_work(run,data,backend,tmp_path,monkeypatch)


@pytest.mark.parametrize('publication',['selection.json','selection-disposition.json'])
@pytest.mark.parametrize('collision',['pending','preexisting_final','appearing_final'])
def test_coordinated_selection_collision_retains_other_owner_and_denies(tmp_path,monkeypatch,publication,collision):
    t=train(); data=encoded_data(tmp_path); backend=SyntheticBackend(); tiny=tmp_path/'tiny'; run=tmp_path/'fit'
    t._execute(data,'tiny-fit',tiny,_backend=backend,_epochs=1)
    established=b'{"synthetic_other_owner":true}\n'; marker=run/publication
    pending=marker.with_name(marker.name+'.pending'); real_publish=t._publish_json; real_link=t.os.link; collisions=[]
    def publish(path,value):
        if Path(path)==marker:
            collisions.append(str(path))
            if collision=='pending': pending.write_bytes(established)
            if collision=='preexisting_final': marker.write_bytes(established)
        return real_publish(path,value)
    def link(source,target):
        if Path(target)==marker and collision=='appearing_final': marker.write_bytes(established)
        return real_link(source,target)
    with monkeypatch.context() as m:
        m.setattr(t,'_publish_json',publish); m.setattr(t.os,'link',link)
        with pytest.raises(FileExistsError):
            t._execute(data,'fit',run,tiny_proof=tiny/'tiny-proof.json',_backend=backend,_epochs=1)
    assert collisions==[str(marker)]
    assert (pending if collision=='pending' else marker).read_bytes()==established
    assert not (run/'complete.json').exists()
    _assert_selection_denied_without_work(run,data,backend,tmp_path,monkeypatch)


@pytest.mark.parametrize('publication',['selection.json','selection-disposition.json','fit-report.json'])
@pytest.mark.parametrize('cleanup_fault',[False,True])
def test_selection_publication_diagnostic_failure_limits_are_phase_specific(tmp_path,monkeypatch,publication,cleanup_fault):
    t=train(); data=encoded_data(tmp_path); backend=SyntheticBackend(); tiny=tmp_path/'tiny'; run=tmp_path/'fit'
    t._execute(data,'tiny-fit',tiny,_backend=backend,_epochs=1); deny_test_access(monkeypatch)
    primary=OSError('synthetic phase publication primary'); marker=run/publication
    real_hash=t.d.sha256; real_unlink=Path.unlink; real_write=t.d.write_json
    injections=[]; cleanups=[]; diagnostics=[]
    def digest(path):
        if Path(path)==marker and not injections:
            assert marker.is_file(); injections.append(str(path)); raise primary
        return real_hash(path)
    def unlink(path,*args,**kwargs):
        if Path(path)==marker:
            cleanups.append(str(path))
            if cleanup_fault: raise PermissionError('synthetic rollback secondary')
        return real_unlink(path,*args,**kwargs)
    def write(path,value):
        if Path(path)==run/'failure.json':
            diagnostics.append(str(path)); raise PermissionError('synthetic diagnostic secondary')
        return real_write(path,value)
    with monkeypatch.context() as m:
        m.setattr(t.d,'sha256',digest); m.setattr(Path,'unlink',unlink); m.setattr(t.d,'write_json',write)
        with pytest.raises(OSError) as caught:
            t._execute(data,'fit',run,tiny_proof=tiny/'tiny-proof.json',_backend=backend,_epochs=1)
    assert caught.value is primary and injections==cleanups==[str(marker)]
    assert diagnostics==[str(run/'failure.json')] and not (run/'failure.json').exists()
    assert (run/'history.json').is_file() and marker.with_name(marker.name+'.pending').is_file()
    assert not (run/'complete.json').exists()
    excluded=publication=='selection-disposition.json' and cleanup_fault
    (tmp_path/'diagnostic-limit-result.json').write_text(json.dumps(dict(publication=publication,
        cleanup_fault=cleanup_fault,primary_preserved=True,diagnostic_attempted=True,
        simultaneous_disposition_rollback_and_failure_persistence_excluded=excluded,
        actual_source_execution=False),indent=2)+'\n')
    if excluded:
        # Residual affirmative disposition plus failed revocation AND failed diagnostic
        # persistence is not claimed crash/permanent-media/hostile-writer durability.
        return
    if publication=='fit-report.json':
        before=_snapshot_selection_run(run)
        assert e.frozen_selection(run,data)['status']=='frozen_validation_selection'
        reservations=[]
        def reserve(*args,**kwargs): reservations.append(True); raise OSError('bounded before reserve')
        def forbidden(*args,**kwargs): pytest.fail('Admission control must stop before backend/test work')
        monkeypatch.setattr(t,'_reserve',reserve)
        for name in ['build','load','predict','step']: monkeypatch.setattr(backend,name,forbidden)
        with pytest.raises(OSError,match='bounded before reserve'):
            e._evaluate(run,data,tmp_path/'never-evaluated',_backend=backend)
        assert reservations==[True] and _snapshot_selection_run(run)==before
    else: _assert_selection_denied_without_work(run,data,backend,tmp_path,monkeypatch)

