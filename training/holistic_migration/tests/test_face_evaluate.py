"""Synthetic frozen evaluation and failure-boundary tests only."""
import importlib
import importlib.util
from pathlib import Path
import json
import numpy as np
import pytest
from .test_face_train import campaign,train,encoded_data,SyntheticBackend,deny_test_access,d


def evaluator():
    name='training.holistic_migration.face_evaluate'
    return importlib.import_module(name if importlib.util.find_spec(name) else 'training.holistic_migration.evaluate')


def test_metrics_all50_loss_exclusion_bounds_not_fabricated_accuracy(campaign,tmp_path):
    e=evaluator(); data=encoded_data(tmp_path,campaign)
    ids=['synthetic/a','synthetic/b','synthetic/c']
    rows=[dict(clip_id=s,dense_id=y,partition='validation',reason='eligible') for s,y in zip(ids,[25,25,1])]
    rows.append(dict(clip_id='synthetic/missing',dense_id=49,partition='validation',reason='invalid_face'))
    probs=np.full((3,50),.001,np.float32); probs[np.arange(3),[25,1,1]]=.951
    y=np.array([25,25,1],np.int64)
    report=e.metrics(y,probs,ids,data.manifest['classes'],rows,partition='validation')
    assert 'loss' in report, 'historical report omits crossentropy'
    assert report['loss']==pytest.approx(float(-np.log(probs[np.arange(3),y]).mean()),rel=1e-6)
    assert len(report['confusion'])==50 and len(report['confusion'][0])==50 and len(report['per_class'])==50
    assert report['per_class'][25]['original_id']==49 and report['per_class'][25]['recall']==.5
    assert report['accuracy']==pytest.approx(2/3)
    assert report['all_declared']['declared']==4 and report['all_declared']['eligible']==3
    assert report['all_declared_bounds']==dict(metric='accuracy_bounds_not_measured_all_source_accuracy',lower=.5,upper=.75)
    assert report['policy_rejection_count_scored_positives']==0 and len(report['exclusions'])==1
    assert report['false_accept_rate'] is report['idle_false_accept_rate'] is report['unknown_false_accept_rate'] is report['rejection_threshold'] is None
    assert report['negative_status']=='unmeasured_no_observed_validation_negatives' and report['live_ready'] is False



def frozen_synthetic_run(campaign,tmp_path):
    t=train(); data=encoded_data(tmp_path,campaign); backend=SyntheticBackend()
    tiny=tmp_path/'tiny'; run=tmp_path/'fit'
    t._execute(data,'tiny-fit',tiny,_backend=backend,_epochs=1)
    t._execute(data,'fit',run,tiny_proof=tiny/'tiny-proof.json',_backend=backend,_epochs=2)
    return data,backend,run


def test_separate_frozen_evaluation_starts_before_test_and_repeat_only_reads(campaign,tmp_path,monkeypatch):
    e=evaluator(); data,backend,run=frozen_synthetic_run(campaign,tmp_path); out=tmp_path/'evaluation'
    evaluate=getattr(e,'_evaluate',None)
    assert callable(evaluate), 'face separate evaluator missing'
    real_open=Path.open; accesses=[]
    def guard(path,*args,**kwargs):
        if Path(path).name.endswith('_test.npy'):
            start=d.load_json(out/'evaluation-start.json')
            assert start['evaluation_kind']=='exploratory_reused_test' and start['status']=='evaluation_started'
            assert start['identity']['feature']=='Float32[N,30,1588] hm1588-v1'
            accesses.append(Path(path).name)
        return real_open(path,*args,**kwargs)
    monkeypatch.setattr(Path,'open',guard)
    result=evaluate(run,data,out,_backend=backend)
    assert result['status']=='exploratory_evaluation_complete' and accesses
    report=d.load_json(out/'report.json')
    assert report['fresh_untouched_holdout'] is report['tuning_allowed'] is report['live_ready'] is False
    assert report['evaluation_kind']=='exploratory_reused_test'
    assert np.load(out/'probabilities.npy').shape==(50,50)
    assert np.load(out/'predictions.npy').shape==(50,)
    before=len(accesses); loaded=backend.loaded
    assert evaluate(run,data,out,_backend=backend)==result
    assert len(accesses)==before and backend.loaded==loaded



def test_missing_tiny_proof_denies_evaluation_before_test_or_reservation(campaign,tmp_path,monkeypatch):
    e=evaluator(); data,backend,run=frozen_synthetic_run(campaign,tmp_path)
    (tmp_path/'tiny/tiny-proof.json').unlink()
    deny_test_access(monkeypatch)
    out=tmp_path/'never-evaluate'
    with pytest.raises((ValueError,OSError)): e._evaluate(run,data,out,_backend=backend)
    assert not out.exists()


@pytest.mark.parametrize('publication',['tiny-proof.json','selection.json','selection-disposition.json','fit-report.json','validation-report.json','complete.json'])
def test_publication_failure_residual_consumers_are_phase_correct(campaign,tmp_path,monkeypatch,publication):
    t=train(); e=evaluator(); data=encoded_data(tmp_path,campaign); backend=SyntheticBackend()
    tiny=tmp_path/'tiny'; run=tiny if publication=='tiny-proof.json' else tmp_path/'fit'
    if publication!='tiny-proof.json': t._execute(data,'tiny-fit',tiny,_backend=backend,_epochs=1)
    deny_test_access(monkeypatch)
    primary=OSError('explicit synthetic final readback'); injections=[]; cleanup=[]
    real_hash=d.sha256; real_unlink=Path.unlink
    def digest(path):
        if Path(path)==run/publication and not injections:
            assert Path(path).is_file() and (run/(publication+'.pending')).is_file()
            injections.append(str(path)); raise primary
        return real_hash(path)
    def unlink(path,*args,**kwargs):
        if Path(path)==run/publication: cleanup.append(str(path)); raise PermissionError('synthetic cleanup secondary')
        return real_unlink(path,*args,**kwargs)
    with monkeypatch.context() as fault:
        fault.setattr(d,'sha256',digest); fault.setattr(Path,'unlink',unlink)
        with pytest.raises(OSError) as caught:
            t._execute(data,'tiny-fit' if publication=='tiny-proof.json' else 'fit',run,
                tiny_proof=tiny/'tiny-proof.json',_backend=backend,_epochs=1)
    assert caught.value is primary and injections==cleanup and injections
    assert (run/'failure.json').exists() and (run/publication).exists()
    if publication=='tiny-proof.json':
        with pytest.raises(ValueError): t._execute(data,'fit',tmp_path/'denied-full',tiny_proof=tiny/'tiny-proof.json',_backend=backend,_epochs=1)
        assert backend.built==1 and not (tmp_path/'denied-full').exists()
    elif publication in ['selection.json','selection-disposition.json']:
        with pytest.raises(ValueError): e.frozen_selection(run,data)
        with pytest.raises(ValueError): e._evaluate(run,data,tmp_path/'denied-eval',_backend=backend)
        assert not (tmp_path/'denied-eval').exists()
    else:
        assert e.frozen_selection(run,data)['status']=='frozen_validation_selection'
        assert d.load_json(run/'failure.json')['selection_disposition']['frozen'] is True


@pytest.mark.parametrize('fault',['model','policy','config','source','failed_disposition','selection_epoch','tiny_model','failed_tiny'])
def test_frozen_tampering_denied_before_test_or_new_output(campaign,tmp_path,monkeypatch,fault):
    e=evaluator(); data,backend,run=frozen_synthetic_run(campaign,tmp_path)
    if fault in ['model','policy','config']: (run/{'model':'model.keras','policy':'policy.json','config':'config.json'}[fault]).write_text('tampered')
    if fault=='source':
        record=d.load_json(run/'selection.json'); record['identity']['sources']['face_evaluate.py']='0'*64
        (run/'selection.json').write_text(json.dumps(record))
    if fault=='failed_disposition': (run/'selection-disposition.json').unlink()
    if fault=='selection_epoch':
        record=d.load_json(run/'selection.json'); record['best_epoch']=2
        (run/'selection.json').write_text(json.dumps(record))
        disposition=d.load_json(run/'selection-disposition.json'); disposition['selection_sha256']=d.sha256(run/'selection.json')
        (run/'selection-disposition.json').write_text(json.dumps(disposition))
    if fault=='tiny_model': (tmp_path/'tiny/model.keras').write_text('tampered')
    if fault=='failed_tiny': (tmp_path/'tiny/failure.json').write_text('{}')
    deny_test_access(monkeypatch)
    out=tmp_path/'not-created'
    with pytest.raises((ValueError,OSError)): e._evaluate(run,data,out,_backend=backend)
    assert not out.exists()


@pytest.mark.parametrize('publication',['report.json','evaluation-complete.json','final_readback'])
def test_failed_evaluation_publication_no_implicit_rerun(campaign,tmp_path,monkeypatch,publication):
    e=evaluator(); data,backend,run=frozen_synthetic_run(campaign,tmp_path); out=tmp_path/'evaluation'
    original=d.sha256; real_unlink=Path.unlink; injected=[]; cleanup=[]
    primary=OSError('synthetic evaluation readback failure'); frozen=d.sha256(run/'selection.json')
    target=out/('report.json' if publication=='final_readback' else publication)
    def digest(path):
        if Path(path)==target and not injected and (publication!='final_readback' or (out/'evaluation-complete.json').exists()):
            assert target.exists(); injected.append(str(path)); raise primary
        return original(path)
    def unlink(path,*args,**kwargs):
        if Path(path)==(out/'evaluation-complete.json' if publication=='final_readback' else target):
            cleanup.append(str(path)); raise OSError('synthetic rollback denied')
        return real_unlink(path,*args,**kwargs)
    with monkeypatch.context() as fault:
        fault.setattr(d,'sha256',digest); fault.setattr(Path,'unlink',unlink)
        with pytest.raises(OSError) as caught: e._evaluate(run,data,out,_backend=backend)
    assert caught.value is primary and injected and cleanup
    assert (out/'failure.json').exists() and original(run/'selection.json')==frozen
    loaded=backend.loaded; deny_test_access(monkeypatch)
    with pytest.raises(ValueError,match='failed|incomplete'): e._evaluate(run,data,out,_backend=backend)
    assert backend.loaded==loaded



def test_completed_evaluation_with_dangling_failure_marker_is_denied(campaign,tmp_path):
    e=evaluator(); data,backend,run=frozen_synthetic_run(campaign,tmp_path); out=tmp_path/'evaluation'
    e._evaluate(run,data,out,_backend=backend)
    (out/'failure.json').symlink_to('missing-failure-diagnostic')
    with pytest.raises(ValueError,match='failed|incomplete'): e._evaluate(run,data,out,_backend=backend)


@pytest.mark.parametrize('stage',['tiny','selection','evaluation'])
def test_incomplete_marker_denies_residual_success_at_consumer(campaign,tmp_path,stage):
    t=train(); e=evaluator(); data,backend,run=frozen_synthetic_run(campaign,tmp_path)
    if stage=='tiny':
        (tmp_path/'tiny/incomplete.json').write_text('{}')
        with pytest.raises(ValueError): t._verify_tiny(tmp_path/'tiny/tiny-proof.json',data,_backend=backend)
    elif stage=='selection':
        (run/'incomplete.json').write_text('{}')
        with pytest.raises(ValueError): e.frozen_selection(run,data)
    else:
        out=tmp_path/'evaluation'; e._evaluate(run,data,out,_backend=backend)
        (out/'incomplete.json').write_text('{}')
        with pytest.raises(ValueError): e._evaluate(run,data,out,_backend=backend)



def test_changed_current_fit_content_denies_before_evaluation_start(campaign,tmp_path,monkeypatch):
    e=evaluator(); data,backend,run=frozen_synthetic_run(campaign,tmp_path)
    with (data.bundle/'X_fit.npy').open('ab') as stream: stream.write(b'explicit synthetic stale admitted content')
    deny_test_access(monkeypatch)
    out=tmp_path/'not-started'
    with pytest.raises(ValueError): e._evaluate(run,data,out,_backend=backend)
    assert not out.exists()


def test_tiny_incomplete_marker_denies_frozen_selection(campaign,tmp_path):
    e=evaluator(); data,backend,run=frozen_synthetic_run(campaign,tmp_path)
    (tmp_path/'tiny/incomplete.json').write_text('{}')
    with pytest.raises(ValueError): e.frozen_selection(run,data)
