"""Synthetic-only frozen rejection lifecycle verification."""
import importlib
import importlib.util
from pathlib import Path
import numpy as np
import pytest
from .test_oov_dataset import fixture_protocol, fixture_quarantine, synthetic_media, SyntheticDetector, dump


def module():
    assert importlib.util.find_spec('training.holistic_migration.rejection_run') is not None, 'frozen rejection orchestration missing'
    return importlib.import_module('training.holistic_migration.rejection_run')


class SyntheticBackend:
    def __init__(self,confidence=.6): self.confidence=confidence; self.calls=0; self.loaded=0
    def load(self,path): self.loaded+=1; return object()
    def predict(self,model,x):
        self.calls+=1
        p=np.zeros((len(x),50),np.float32); p[:,0]=self.confidence; p[:,1]=1-np.float32(self.confidence)
        return p


def inputs(tmp_path):
    from training.holistic_migration import oov_dataset as o
    protocol=fixture_protocol(tmp_path,synthetic_media(tmp_path))
    bundle=tmp_path/'negatives'
    o.extract(protocol=protocol,mode='calibration',output=bundle,_detector_factory=SyntheticDetector)
    return protocol,bundle


def test_quarantine_lifecycle_keeps_203_declarations_202_new_known_scores(tmp_path,monkeypatch):
    m=module(); root,view=fixture_quarantine(tmp_path,with_media=True,challenge_count=203)
    m.o.prepare(source_audit=root/'audit.json',authorization=root/'authorization.json',phase4_campaign=root/'phase4',
        quarantine_view=view,output=tmp_path/'approved',_synthetic=True)
    protocol=tmp_path/'approved/protocol.json'; bundle=tmp_path/'negative'
    m.o.extract(protocol=protocol,mode='calibration',output=bundle,_detector_factory=SyntheticDetector)
    backend=SyntheticBackend(); run=tmp_path/'run'; original=np.load
    def no_challenge(path,*args,**kwargs):
        assert 'challenge_' not in Path(path).name, 'known challenge array touched during calibration'
        return original(path,*args,**kwargs)
    with monkeypatch.context() as patcher:
        patcher.setattr(np,'load',no_challenge)
        m.calibrate(protocol=protocol,negative_bundle=bundle,output=run,_backend=backend)
    freeze=m.read_freeze(run,protocol=protocol,allow_synthetic=True)
    assert freeze['baseline_candidate_contract']==m.o.read_protocol(protocol,allow_synthetic=True)['frozen']['candidate-contract.json']
    assert freeze['quarantine_view']==m.o.binding(view), 'companion must explicitly name approved view'
    cb=tmp_path/'challenge-bundle'
    m.o.extract(protocol=protocol,mode='challenge',calibration_run=run,output=cb,_detector_factory=SyntheticDetector)
    assessment=tmp_path/'assessment'
    m.challenge(protocol=protocol,calibration_run=run,negative_bundle=cb,output=assessment,_backend=backend)
    assert np.load(assessment/'known_probabilities.npy').shape==(202,50)
    report=m.o.json_read(assessment/'report.json'); metrics=report['measurements']
    assert metrics['known_only']['declared']==203 and metrics['known_only']['eligible']==202 and metrics['known_only']['quarantined']==1
    assert metrics['extended_known_label']['eligible']==202
    assert metrics['oov']['declared']==2 and metrics['oov']['quarantined']==1 and metrics['oov']['eligible']==1
    assert report['historical_fit_ids_flagged_only']==['clips/23/6.MOV','clips/57/9.MOV']
    assert backend.calls==2
    m.challenge(protocol=protocol,calibration_run=run,negative_bundle=cb,output=assessment,_backend=backend)
    assert backend.calls==2


def test_calibrate_saved_known_scores_and_feasible_ordinary_readback(tmp_path):
    m=module(); protocol,bundle=inputs(tmp_path); backend=SyntheticBackend(); out=tmp_path/'run'
    result=m.calibrate(protocol=protocol,negative_bundle=bundle,output=out,_backend=backend)
    assert result['status']=='completed_feasible' and result['live_ready'] is False
    assert backend.calls==1 and backend.loaded==1
    assert (out/'oov_probabilities.npy').is_file() and (out/'score-complete.json').is_file()
    freeze=m.read_freeze(out,protocol=protocol,allow_synthetic=True)
    assert freeze['counts']['known_correct_accepted']==50 and freeze['counts']['oov_accepted']==0
    assert freeze['threshold_bits']==int(np.float32(1).view(np.uint32))
    # Ordinary consumer reconstructs the selected cutoff and observed counts, not just file existence.
    from training.holistic_migration.rejection import decide
    assert (decide(np.load(out/'oov_probabilities.npy'),freeze['threshold'])<0).all()
    again=m.calibrate(protocol=protocol,negative_bundle=bundle,output=out,_backend=backend)
    assert again==result and backend.calls==1
    with pytest.raises(ValueError): m.read_freeze(out,protocol=protocol)



def test_infeasible_keeps_full_sweep_no_policy_or_challenge(tmp_path):
    m=module(); protocol,bundle=inputs(tmp_path); backend=SyntheticBackend(1); out=tmp_path/'infeasible'
    result=m.calibrate(protocol=protocol,negative_bundle=bundle,output=out,_backend=backend)
    assert result['status']=='completed_infeasible' and result['freeze'] is None
    assert not (out/'freeze.json').exists() and not (out/'freeze-admission.json').exists()
    assert m.o.json_read(out/'report.json')['sweep']['best_tradeoffs']
    with pytest.raises((ValueError,OSError)): m.read_freeze(out,protocol=protocol,allow_synthetic=True)
    assert hasattr(m,'challenge'), 'separately gated challenge operation missing'
    calls=backend.calls
    with pytest.raises((ValueError,OSError)):
        m.challenge(protocol=protocol,calibration_run=out,negative_bundle=tmp_path/'absent-challenge',output=tmp_path/'denied',_backend=backend)
    assert backend.calls==calls and not (tmp_path/'denied').exists()


def test_challenge_fixed_freeze_once_and_no_rerun(tmp_path):
    m=module(); assert hasattr(m,'challenge'), 'challenge assessment missing'
    protocol,bundle=inputs(tmp_path); backend=SyntheticBackend(); run=tmp_path/'run'
    m.calibrate(protocol=protocol,negative_bundle=bundle,output=run,_backend=backend)
    cb=tmp_path/'challenge-bundle'
    m.o.extract(protocol=protocol,mode='challenge',calibration_run=run,output=cb,_detector_factory=SyntheticDetector)
    assert (run/'challenge-extraction-start.json').is_file()
    before=len(SyntheticDetector.instances)
    with pytest.raises((ValueError,OSError)):
        m.o.extract(protocol=protocol,mode='challenge',calibration_run=run,output=tmp_path/'second-challenge',_detector_factory=SyntheticDetector)
    assert len(SyntheticDetector.instances)==before
    out=tmp_path/'assessment'
    result=m.challenge(protocol=protocol,calibration_run=run,negative_bundle=cb,output=out,_backend=backend)
    assert result['status']=='challenge_assessed' and result['tuning_allowed'] is False
    assert backend.calls==2 and (run/'assessment-start.json').is_file()
    again=m.challenge(protocol=protocol,calibration_run=run,negative_bundle=cb,output=out,_backend=backend)
    assert again==result and backend.calls==2
    with pytest.raises((ValueError,OSError)):
        m.challenge(protocol=protocol,calibration_run=run,negative_bundle=cb,output=tmp_path/'rerun',_backend=backend)
    assert backend.calls==2
    dump(out/'failure.json',{'status':'failed'})
    with pytest.raises(ValueError): m.challenge(protocol=protocol,calibration_run=run,negative_bundle=cb,output=out,_backend=backend)
    assert backend.calls==2



def test_later_report_failure_preserves_freeze_and_saved_only_recovery(tmp_path,monkeypatch):
    m=module(); protocol,bundle=inputs(tmp_path); backend=SyntheticBackend(); run=tmp_path/'report-fails'
    original=m._write_report
    def fail(*args,**kwargs): raise OSError('report storage failure')
    monkeypatch.setattr(m,'_write_report',fail)
    with pytest.raises(OSError,match='report storage'):
        m.calibrate(protocol=protocol,negative_bundle=bundle,output=run,_backend=backend)
    assert backend.calls==1 and (run/'freeze-admission.json').is_file()
    assert m.read_freeze(run,protocol=protocol,allow_synthetic=True)['live_ready'] is False
    with pytest.raises(ValueError): m.calibrate(protocol=protocol,negative_bundle=bundle,output=run,_backend=backend)
    monkeypatch.setattr(m,'_write_report',original)
    assert hasattr(m,'report_saved'), 'saved-output-only report recovery missing'
    result=m.report_saved(protocol=protocol,run=run,output=tmp_path/'report-recovery',allow_synthetic=True)
    assert result['status']=='saved_output_report' and backend.calls==1
    assert not (run/'complete.json').exists()  # recovery never repairs a failed attempt into completed evidence


@pytest.mark.parametrize('target',['freeze.json','freeze-admission.json'])
def test_unsuccessful_policy_publication_denied_even_with_residual_bytes(tmp_path,monkeypatch,target):
    m=module(); protocol,bundle=inputs(tmp_path); backend=SyntheticBackend(); run=tmp_path/'policy-fails'
    original=m.o.publish
    def fail(path,value):
        original(path,value)
        if path.name==target: raise OSError('postwrite policy readback failure')
    monkeypatch.setattr(m.o,'publish',fail)
    with pytest.raises(OSError): m.calibrate(protocol=protocol,negative_bundle=bundle,output=run,_backend=backend)
    assert (run/target).is_file() and (run/'freeze-failure.json').is_file()
    with pytest.raises(ValueError): m.read_freeze(run,protocol=protocol,allow_synthetic=True)
    assert backend.calls==1



def test_native_synthetic_only_forward_save_reload_and_float32_parity(tmp_path):
    m=module(); assert hasattr(m,'FrozenBackend'), 'native frozen50 adapter missing'
    import tensorflow as tf
    layers=tf.keras.layers
    # Fresh invented model, no compile/fit/optimizer, no accepted checkpoint is opened.
    with tf.device('/CPU:0'):
        model=tf.keras.Sequential([layers.Input((30,1588),dtype='float32'),layers.GlobalAveragePooling1D(),
                                   layers.Dense(50,activation='softmax',kernel_initializer='zeros',bias_initializer='zeros')])
        path=tmp_path/'synthetic.keras'; model.save(path)
    protocol=fixture_protocol(tmp_path,synthetic_media(tmp_path),model_payload=path.read_bytes())
    bundle=tmp_path/'native-bundle'
    m.o.extract(protocol=protocol,mode='calibration',output=bundle,_detector_factory=SyntheticDetector)
    backend=m.FrozenBackend(); native=backend.load(path)
    _,x,ids,_=m.o.read_bundle(bundle,protocol=protocol,mode='calibration',allow_synthetic=True)
    before=[v.numpy().copy() for v in native.weights]
    expected=model(np.asarray(x),training=False).numpy()
    actual=backend.predict(native,x)
    assert actual.dtype==np.float32 and actual.shape==(2,50) and np.array_equal(actual,expected)
    assert all(np.array_equal(v.numpy(),b) for v,b in zip(native.weights,before))
    assert native.optimizer is None if hasattr(native,'optimizer') else True
    cutoff=actual.max()
    assert np.array_equal(m.r.decide(actual,cutoff),m.r.decide(expected,cutoff))
    assert (m.r.decide(actual,np.nextafter(cutoff,np.float32(np.inf)))<0).all()
    run=tmp_path/'native-run'
    result=m.calibrate(protocol=protocol,negative_bundle=bundle,output=run,_backend=backend)
    assert result['status']=='completed_feasible'
    assert np.array_equal(np.load(run/'oov_probabilities.npy'),actual)
    m.read_freeze(run,protocol=protocol,allow_synthetic=True)
    p=m.o.read_protocol(protocol,allow_synthetic=True)
    assert m.o.check_binding(p['frozen']['model.keras']).read_bytes()==path.read_bytes()



@pytest.mark.parametrize('name',['known_probabilities.npy','oov_probabilities.npy','oov_ids.npy'])
def test_saved_array_cardinality_denied_before_allocation(tmp_path,monkeypatch,name):
    m=module(); protocol,bundle=inputs(tmp_path); backend=SyntheticBackend(); out=tmp_path/'run'
    m.calibrate(protocol=protocol,negative_bundle=bundle,output=out,_backend=backend)
    np.save(out/name,np.zeros((100,50),np.float32) if 'probabilities' in name else np.array(['bad']*100))
    score=m.o.json_read(out/'score-complete.json'); score['files'][name]=m.d.sha256(out/name); dump(out/'score-complete.json',score)
    original=np.load
    def denied(path,*args,**kwargs):
        if Path(path)==out/name: raise AssertionError('saved array allocated before source cardinality admission')
        return original(path,*args,**kwargs)
    monkeypatch.setattr(np,'load',denied)
    with pytest.raises(ValueError): m.report_saved(protocol=protocol,run=out,output=tmp_path/'denied',allow_synthetic=True)
    assert backend.calls==1


def test_completed_reports_reproduce_metrics_not_only_hashes(tmp_path):
    m=module(); protocol,bundle=inputs(tmp_path); backend=SyntheticBackend(); out=tmp_path/'run'
    m.calibrate(protocol=protocol,negative_bundle=bundle,output=out,_backend=backend)
    report=m.o.json_read(out/'report.json'); report['measurements'][0]['known']['correct_accepted']=999
    dump(out/'report.json',report)
    complete=m.o.json_read(out/'complete.json'); complete['report']=m.o.binding(out/'report.json'); dump(out/'complete.json',complete)
    with pytest.raises(ValueError): m.calibrate(protocol=protocol,negative_bundle=bundle,output=out,_backend=backend)
    assert backend.calls==1



def test_public_cli_is_real_only_and_documents_all_commands(tmp_path):
    m=module(); assert hasattr(m,'main') and hasattr(m.o,'main'), 'required public CLIs missing'
    import subprocess
    import sys
    protocol,bundle=inputs(tmp_path)
    for mod in ['oov_dataset','rejection_run']:
        result=subprocess.run([sys.executable,'-E','-B','-m','training.holistic_migration.'+mod,'--help'],capture_output=True,text=True)
        assert result.returncode==0 and 'challenge' in result.stdout
        assert '--synthetic' not in result.stdout and '--backend' not in result.stdout
    assert m.o.main(['pilot','--protocol',str(protocol),'--output',str(tmp_path/'pilot-cli')])==2
    assert not (tmp_path/'pilot-cli').exists()
    assert m.main(['calibrate','--protocol',str(protocol),'--negative-bundle',str(bundle),'--output',str(tmp_path/'run-cli')])==2
    assert not (tmp_path/'run-cli').exists()



def test_failed_policy_stays_denied_when_secondary_failure_receipts_fail(tmp_path,monkeypatch):
    m=module(); protocol,bundle=inputs(tmp_path); backend=SyntheticBackend(); run=tmp_path/'publication-fails'
    original=m.o.publish
    def fail(path,value):
        if path.name=='freeze-failure.json': raise OSError('secondary marker storage unavailable')
        original(path,value)
        if path.name=='freeze-admission.json': raise OSError('admission postwrite readback unavailable')
    monkeypatch.setattr(m.o,'publish',fail)
    monkeypatch.setattr(m.o,'failure',lambda *a:None)
    with pytest.raises(OSError): m.calibrate(protocol=protocol,negative_bundle=bundle,output=run,_backend=backend)
    assert (run/'freeze-admission.json').is_file() and not (run/'freeze-failure.json').exists()
    with pytest.raises(ValueError): m.read_freeze(run,protocol=protocol,allow_synthetic=True)



@pytest.mark.parametrize('target',['scores','report','freeze','start'])
def test_exact_calibration_publication_targets_not_interchangeable(tmp_path,target):
    m=module(); protocol,bundle=inputs(tmp_path); backend=SyntheticBackend(); run=tmp_path/'run'
    m.calibrate(protocol=protocol,negative_bundle=bundle,output=run,_backend=backend)
    if target=='start':
        start=m.o.json_read(run/'start.json'); start['model']=dict(start['model'],sha256='a'*64); dump(run/'start.json',start)
    else:
        complete=m.o.json_read(run/'complete.json'); source=Path(complete[target]['path'])
        copy=run/('copy-'+source.name); copy.write_bytes(source.read_bytes()); complete[target]=m.o.binding(copy); dump(run/'complete.json',complete)
    with pytest.raises(ValueError): m.calibrate(protocol=protocol,negative_bundle=bundle,output=run,_backend=backend)
    assert backend.calls==1


def test_assessment_readback_failure_retains_barrier_without_secondary_markers(tmp_path,monkeypatch):
    m=module(); protocol,bundle=inputs(tmp_path); backend=SyntheticBackend(); run=tmp_path/'run'
    m.calibrate(protocol=protocol,negative_bundle=bundle,output=run,_backend=backend)
    cb=tmp_path/'challenge-bundle'; m.o.extract(protocol=protocol,mode='challenge',calibration_run=run,output=cb,_detector_factory=SyntheticDetector)
    original=m._challenge_readback; assessment=tmp_path/'assessment'
    def fail(*args,**kwargs): original(*args,**kwargs); raise OSError('assessment qualification unavailable')
    monkeypatch.setattr(m,'_challenge_readback',fail); monkeypatch.setattr(m.o,'failure',lambda *a:None)
    with pytest.raises(OSError): m.challenge(protocol=protocol,calibration_run=run,negative_bundle=cb,output=assessment,_backend=backend)
    monkeypatch.setattr(m,'_challenge_readback',original)
    with pytest.raises(ValueError): m.challenge(protocol=protocol,calibration_run=run,negative_bundle=cb,output=assessment,_backend=backend)
    assert backend.calls==2
    m.read_freeze(run,protocol=protocol,allow_synthetic=True)


def test_completed_calibration_readback_failure_cannot_drop_publication_barrier(tmp_path,monkeypatch):
    m=module(); protocol,bundle=inputs(tmp_path); backend=SyntheticBackend(); run=tmp_path/'run'
    original=m._completed_readback
    def fail(*args,**kwargs):
        original(*args,**kwargs)
        raise OSError('completion qualification readback unavailable')
    monkeypatch.setattr(m,'_completed_readback',fail); monkeypatch.setattr(m.o,'failure',lambda *a:None)
    with pytest.raises(OSError): m.calibrate(protocol=protocol,negative_bundle=bundle,output=run,_backend=backend)
    monkeypatch.setattr(m,'_completed_readback',original)
    with pytest.raises(ValueError): m.calibrate(protocol=protocol,negative_bundle=bundle,output=run,_backend=backend)
    assert backend.calls==1
    assert m.read_freeze(run,protocol=protocol,allow_synthetic=True)['live_ready'] is False


def test_unsuccessful_score_publication_cannot_be_recovered_as_admitted_scores(tmp_path,monkeypatch):
    m=module(); protocol,bundle=inputs(tmp_path); backend=SyntheticBackend(); run=tmp_path/'scores-fail'
    original=m.o.publish
    def fail(path,value):
        if path.name=='scores-failure.json': raise OSError('secondary marker failure')
        original(path,value)
        if path.name=='score-complete.json': raise OSError('score postwrite readback failure')
    monkeypatch.setattr(m.o,'publish',fail); monkeypatch.setattr(m.o,'failure',lambda *a:None)
    with pytest.raises(OSError): m.calibrate(protocol=protocol,negative_bundle=bundle,output=run,_backend=backend)
    assert (run/'score-complete.json').is_file()
    with pytest.raises(ValueError): m.report_saved(protocol=protocol,run=run,output=tmp_path/'denied-report',allow_synthetic=True)
    assert backend.calls==1
