"""Phase4: synthetic-only bounded training and admission regression tests."""
import importlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
import pytest
from .test_face_augmentation import synthetic_tensor


def train():
    name='training.holistic_migration.face_train'
    return importlib.import_module(name if importlib.util.find_spec(name) else 'training.holistic_migration.train')


def test_real_synthetic_optimizer_save_reload_exact_family(tmp_path):
    t=train(); m=t.build_model()
    assert m.input_shape==(None,30,1588), 'historical input is incompatible'
    assert m.output_shape==(None,50)
    assert [type(l).__name__ for l in m.layers]==['Conv1D','BatchNormalization','Conv1D','BatchNormalization','MaxPooling1D','LSTM','Dropout','LSTM','Dropout','Dense','Dropout','Dense']
    assert [(m.layers[i].filters,m.layers[i].kernel_size,m.layers[i].padding,m.layers[i].activation.__name__) for i in [0,2]]==[(64,(3,),'same','relu'),(128,(3,),'same','relu')]
    assert (m.layers[5].units,m.layers[5].return_sequences)==(128,True)
    assert (m.layers[7].units,m.layers[7].return_sequences)==(64,False)
    assert [m.layers[i].rate for i in [6,8,10]]==[.4,.4,.4]
    assert m.layers[9].units==128 and m.layers[9].activation.__name__=='relu'
    assert m.layers[-1].activation.__name__=='softmax' and m.loss=='sparse_categorical_crossentropy'
    assert float(m.optimizer.learning_rate.numpy())==pytest.approx(.001)
    x=synthetic_tensor(); y=np.array([0,1],np.int64)
    before=[v.numpy().copy() for v in m.trainable_weights]
    logs=m.train_on_batch(x,y,return_dict=True)
    assert np.isfinite(list(logs.values())).all()
    assert int(m.optimizer.iterations.numpy())==1
    assert any(not np.array_equal(a,b.numpy()) for a,b in zip(before,m.trainable_weights))
    p=m(x,training=False).numpy(); assert p.shape==(2,50)
    path=tmp_path/'synthetic.keras'; m.save(path)
    import tensorflow as tf
    reloaded=tf.keras.models.load_model(path)
    np.testing.assert_allclose(reloaded(x,training=False).numpy(),p,rtol=1e-6,atol=1e-7)
    assert int(reloaded.optimizer.iterations.numpy())==1


from .test_face_dataset import campaign
from training.holistic_migration import dataset as d, face_dataset as fd
from .test_train import rewrite_json


def synthetic_bundle(root,campaign):
    fd.build_dataset(campaign=campaign,output=root)
    m=d.load_json(root/'data_manifest.json')
    acceptance=root.parent/(root.name+'-acceptance.json')
    d.write_json(acceptance,dict(schema_version=1,status='synthetic_fixture_only',bundle=str(root),
        data_manifest_sha256=d.sha256(root/'data_manifest.json'),classes=50,tensor_contract=fd.TENSOR_CONTRACT,
        partitions=m['eligibility']['partitions'],declared=sum(v['declared'] for v in m['eligibility']['partitions'].values()),
        eligible=sum(v['eligible'] for v in m['eligibility']['partitions'].values()),ineligible=0,
        training_qualified=False,live_ready=False,model_evaluated=False,spec_compliant=True,quality_approved=True,
        code_hashes={n:d.sha256(d.REPO/n) for n in [fd.CONTRACT,'training/holistic_migration/face_dataset.py','training/holistic_migration/face_features.py']}))
    admission=root.parent/(root.name+'-admission.json')
    d.write_json(admission,dict(schema_version=1,status='synthetic_fixture_only',purpose='face_fit_validation_only',
        bundle=str(root),data_manifest_sha256=d.sha256(root/'data_manifest.json'),
        dataset_acceptance=str(acceptance),dataset_acceptance_sha256=d.sha256(acceptance),
        campaign_manifest_sha256=m['campaign_manifest_sha256'],implementation=m['implementation'],
        graph_sha256=d.canonical_hash(m['graph']),classes=m['classes'],tensor_contract=fd.TENSOR_CONTRACT))
    return root,admission


def deny_test_access(monkeypatch):
    real_open=Path.open; load=np.load
    def guard(path,*args,**kwargs):
        assert not Path(path).name.endswith('_test.npy'), 'training opened test tensor'
        assert not (Path(path).suffix=='.npz' and 'raw' in Path(path).parts), 'training opened raw observations'
        return real_open(path,*args,**kwargs)
    def guard_load(path,*args,**kwargs):
        assert not str(path).endswith('_test.npy'); return load(path,*args,**kwargs)
    monkeypatch.setattr(Path,'open',guard); monkeypatch.setattr(np,'load',guard_load)
    monkeypatch.setattr(fd,'validate_bundle',lambda *a:pytest.fail('full consumer reads test/raw'))
    monkeypatch.setattr(d,'validate_campaign',lambda *a:pytest.fail('full campaign reads test/raw'))


def test_admission_binds_face_parent_without_test_or_raw_access(campaign,tmp_path,monkeypatch):
    t=train(); b,a=synthetic_bundle(tmp_path/'bundle',campaign)
    reader=getattr(t,'_read_bundle',None)
    assert callable(reader), 'face fit/validation-only reader missing'
    deny_test_access(monkeypatch)
    data=reader(b,a,evidence_kind='synthetic_in_process')
    assert set(data.arrays)=={'fit','validation'}
    assert data.arrays['fit'][0].shape==(50,30,1588)
    assert data.identity['dataset_acceptance_sha256']==d.load_json(a)['dataset_acceptance_sha256']
    assert data.manifest['training_qualified'] is False
    with pytest.raises(ValueError): t.read_admitted(b,a)



def rebind_bundle(bundle,admission):
    m=d.load_json(bundle/'data_manifest.json')
    for name,record in m['artifacts'].items():
        record['sha256']=d.sha256(bundle/name)
        if name.endswith('.npy'):
            arr=np.load(bundle/name,allow_pickle=False)
            record.update(shape=list(arr.shape),dtype=str(arr.dtype))
    rewrite_json(bundle/'data_manifest.json',m)
    a=d.load_json(admission); a['data_manifest_sha256']=d.sha256(bundle/'data_manifest.json')
    accepted=d.load_json(a['dataset_acceptance']); accepted['data_manifest_sha256']=a['data_manifest_sha256']
    rewrite_json(Path(a['dataset_acceptance']),accepted)
    a['dataset_acceptance_sha256']=d.sha256(a['dataset_acceptance']); rewrite_json(admission,a)


@pytest.mark.parametrize('bad',['failed','incomplete','schema_bool','schema_float','duplicate_admission','bad_digest','copied_bundle',
    'extra_admission','wrong_acceptance','acceptance_false','implementation','runtime','class_order','unknown_reason',
    'capture_count_float','extra_capture','shape_float','test_hash','dtype','face_depth','mask','labels','ids','support'])
def test_admission_strict_rebound_mutations(campaign,tmp_path,bad):
    t=train(); b,a=synthetic_bundle(tmp_path/'bundle',campaign)
    m=d.load_json(b/'data_manifest.json'); adm=d.load_json(a)
    if bad in ['failed','incomplete']: (b/('failure.json' if bad=='failed' else 'incomplete.json')).write_text('{}')
    elif bad=='duplicate_admission': a.write_text('{"schema_version":0,'+a.read_text().lstrip()[1:])
    elif bad in ['schema_bool','schema_float','bad_digest','copied_bundle','extra_admission','wrong_acceptance','acceptance_false']:
        if bad=='schema_bool': adm['schema_version']=True
        if bad=='schema_float': adm['schema_version']=1.0
        if bad=='bad_digest': adm['data_manifest_sha256']='X'*64
        if bad=='copied_bundle': adm['bundle']=str(tmp_path/'other')
        if bad=='extra_admission': adm['bypass']=True
        if bad=='wrong_acceptance': adm['dataset_acceptance_sha256']='0'*64
        if bad=='acceptance_false':
            ac=d.load_json(adm['dataset_acceptance']); ac['quality_approved']=False
            rewrite_json(Path(adm['dataset_acceptance']),ac); adm['dataset_acceptance_sha256']=d.sha256(adm['dataset_acceptance'])
        rewrite_json(a,adm)
    else:
        if bad=='implementation': m['implementation']['training/holistic_migration/face_features.py']='0'*64
        if bad=='runtime': m['graph']['runtime']['packages']['numpy']='0'
        if bad=='class_order': m['classes'].reverse()
        if bad in ['unknown_reason','capture_count_float','extra_capture']:
            rows=d.load_json(b/'capture_rows.json')
            if bad=='unknown_reason': rows[0]['reason']='made_up'
            if bad=='capture_count_float': rows[0]['observation_count']=8.0
            if bad=='extra_capture': rows[0]['permission_to_train']=True
            rewrite_json(b/'capture_rows.json',rows)
        if bad=='shape_float': m['artifacts']['X_fit.npy']['shape'][0]=50.0
        if bad=='test_hash': m['artifacts']['X_test.npy']['sha256']='z'*64
        if bad in ['dtype','face_depth','mask']:
            x=np.load(b/'X_fit.npy')
            if bad=='dtype': x=x.astype(np.float64)
            if bad=='face_depth': x[0,0,155]+=1
            if bad=='mask': x[0,0,1587]=0
            np.save(b/'X_fit.npy',x,allow_pickle=False)
        if bad=='labels': np.save(b/'y_fit.npy',np.zeros(50,np.int64),allow_pickle=False)
        if bad=='ids': np.save(b/'clip_ids_fit.npy',np.array(['duplicate']*50),allow_pickle=False)
        if bad=='support':
            for prefix in ['X','y','clip_ids']: np.save(b/f'{prefix}_fit.npy',np.load(b/f'{prefix}_fit.npy')[:-1],allow_pickle=False)
        rewrite_json(b/'data_manifest.json',m)
        if bad not in ['shape_float','test_hash']: rebind_bundle(b,a)
        else:
            adm['data_manifest_sha256']=d.sha256(b/'data_manifest.json'); rewrite_json(a,adm)
            ac=d.load_json(adm['dataset_acceptance']); ac['data_manifest_sha256']=adm['data_manifest_sha256']
            rewrite_json(Path(adm['dataset_acceptance']),ac); adm['dataset_acceptance_sha256']=d.sha256(adm['dataset_acceptance']); rewrite_json(a,adm)
    with pytest.raises((ValueError,OSError,KeyError,TypeError)): t._read_bundle(b,a,evidence_kind='synthetic_in_process')



def encoded_data(tmp_path,campaign):
    t=train(); b,a=synthetic_bundle(tmp_path/'bundle',campaign)
    for partition in d.PARTITIONS:
        x=np.load(b/f'X_{partition}.npy'); y=np.load(b/f'y_{partition}.npy')
        x[:,:,153]=y[:,None]/100
        np.save(b/f'X_{partition}.npy',x,allow_pickle=False)
    rebind_bundle(b,a)
    return t._read_bundle(b,a,evidence_kind='synthetic_in_process')


class SyntheticBackend:
    """Explicit lifecycle seam, never actual learning evidence or real admission."""
    def __init__(self,wrong=False): self.built=0; self.loaded=0; self.wrong=wrong
    def build(self): self.built+=1; return {'steps':0}
    def steps(self,m): return m['steps']
    def step(self,m,x,y): m['steps']+=1
    def predict(self,m,x):
        y=np.clip(np.rint(x[:,0,153]*100).astype(int),0,49)
        if self.wrong: y=(y+1)%50
        p=np.full((len(x),50),.00001,np.float32); p[np.arange(len(x)),y]=1-.00001*49
        return p
    def save(self,m,path): Path(path).write_text(json.dumps(m))
    def load(self,path): self.loaded+=1; return json.loads(Path(path).read_text())
    def callbacks(self,m): return []


def test_source_bound_tiny_proof_reloaded_on_exact_fit_only(campaign,tmp_path,monkeypatch):
    t=train(); data=encoded_data(tmp_path,campaign); backend=SyntheticBackend(); out=tmp_path/'tiny'
    deny_test_access(monkeypatch)
    execute=getattr(t,'_execute',None)
    assert callable(execute), 'face tiny path missing'
    proof=execute(data,'tiny-fit',out,_backend=backend,_epochs=2)
    assert proof['correct']==8 and proof['mean_crossentropy']<=.1 and proof['provenance']=='synthetic_in_process'
    assert proof['optimizer_steps']==1 and backend.built==1 and backend.loaded==1
    assert proof['selected_ids']==[min(s for s,y in zip(data.arrays['fit'][2],data.arrays['fit'][1]) if y==i) for i in range(8)]
    assert np.load(out/'selected_X.npy').shape==(8,30,1588)
    np.testing.assert_array_equal(np.load(out/'selected_y.npy'),np.arange(8))
    assert t._verify_tiny(out/'tiny-proof.json',data,_backend=backend)==proof
    with pytest.raises(ValueError): t.verify_real_tiny(out/'tiny-proof.json',data)
    with pytest.raises(ValueError): execute(data,'tiny-fit',out,_backend=backend,_epochs=1)


@pytest.mark.parametrize('fault',['wrong','model_tamper','failed_marker','source_tamper','history_tamper','reload','budget','real_seam'])
def test_tiny_denies_failed_or_changed_proofs(campaign,tmp_path,fault):
    from dataclasses import replace
    t=train(); data=encoded_data(tmp_path,campaign); backend=SyntheticBackend(wrong=fault=='wrong'); out=tmp_path/'tiny'
    if fault=='budget':
        with pytest.raises(ValueError): t._execute(data,'tiny-fit',out,_backend=backend,_epochs=301)
        assert not out.exists(); return
    if fault=='real_seam':
        with pytest.raises(ValueError): t._execute(replace(data,provenance='source_video'),'tiny-fit',out,_backend=backend)
        assert not out.exists(); return
    if fault=='reload':
        def fail(path): raise ValueError('explicit synthetic reload failure')
        backend.load=fail
    if fault in ['wrong','reload']:
        with pytest.raises(ValueError): t._execute(data,'tiny-fit',out,_backend=backend,_epochs=2)
        assert (out/'failure.json').exists() and not (out/'tiny-proof.json').exists(); return
    t._execute(data,'tiny-fit',out,_backend=backend,_epochs=1)
    if fault=='failed_marker': (out/'failure.json').write_text('{')
    if fault=='model_tamper': (out/'model.keras').write_text('tamper')
    if fault=='source_tamper':
        proof=d.load_json(out/'tiny-proof.json'); proof['identity']['sources']['face_train.py']='0'*64
        rewrite_json(out/'tiny-proof.json',proof)
    if fault=='history_tamper': (out/'history.json').write_text('[]')
    with pytest.raises((ValueError,OSError)): t._verify_tiny(out/'tiny-proof.json',data,_backend=backend)


def test_full_fresh_fit_only_augmented_earliest_tie_with_complete_history(campaign,tmp_path,monkeypatch):
    t=train(); data=encoded_data(tmp_path,campaign); backend=SyntheticBackend(); tiny=tmp_path/'tiny'
    t._execute(data,'tiny-fit',tiny,_backend=backend,_epochs=1)
    assert callable(getattr(t,'_full_execute',None)), 'face full fitting path missing'
    deny_test_access(monkeypatch)
    vx=data.arrays['validation'][0].copy(); batches=[]; step=backend.step
    def track(m,x,y): batches.append(len(x)); return step(m,x,y)
    backend.step=track
    run=tmp_path/'fit'
    selection=t._execute(data,'fit',run,tiny_proof=tiny/'tiny-proof.json',_backend=backend,_epochs=3)
    assert backend.built==2 and selection['best_epoch']==1
    assert selection['actual_epochs']==3 and selection['optimizer_steps']==12
    assert selection['selected_checkpoint_steps']==4 and sum(batches)==300 and max(batches)<=32
    np.testing.assert_array_equal(vx,data.arrays['validation'][0])
    history=d.load_json(run/'history.json')
    assert all({'epoch','optimizer_steps','loss','accuracy','val_loss','val_accuracy'}<=set(h) for h in history)
    assert (run/'selection-disposition.json').exists() and (run/'complete.json').exists()
    assert selection['policy']['decision']=='closed_set_argmax' and selection['policy']['live_ready'] is False
    assert d.load_json(run/'augmentation.json')['derived_count']==50


@pytest.mark.parametrize('module,arguments',[
    ('face_train',['tiny-fit']),('face_train',['fit','--tiny-proof','/absent/tiny-proof.json']),
    ('face_evaluate',['--run','/absent/frozen'])])
def test_cli_rejects_synthetic_without_native_or_output(campaign,tmp_path,module,arguments):
    b,a=synthetic_bundle(tmp_path/'bundle',campaign); out=tmp_path/'not-created'
    command=[sys.executable,'-E','-B','-m','training.holistic_migration.'+module]+arguments+['--bundle',str(b),'--admission',str(a),'--output',str(out)]
    result=subprocess.run(command,cwd=d.REPO,capture_output=True,text=True)
    assert result.returncode==2, 'CLI must enforce real source admission'
    assert 'admission status' in result.stderr and not out.exists()
    assert 'tensorflow' not in result.stderr.lower()


@pytest.mark.parametrize('module',['face_train','face_evaluate'])
def test_cli_help_is_lazy_with_no_synthetic_or_epoch_bypass(module):
    code="import sys,runpy; sys.argv=['tool','--help'];\ntry: runpy.run_module('training.holistic_migration."+module+"',run_name='__main__')\nexcept SystemExit as e: assert e.code==0; assert 'tensorflow' not in sys.modules; print('LAZY_HELP_OK')"
    result=subprocess.run([sys.executable,'-E','-B','-c',code],cwd=d.REPO,capture_output=True,text=True)
    assert result.returncode==0 and 'LAZY_HELP_OK' in result.stdout
    assert '--allow-synthetic' not in result.stdout and '--epochs' not in result.stdout



def test_actual_tensorflow_tiny_failure_retains_steps_checkpoint_no_proof(campaign,tmp_path):
    t=train(); data=encoded_data(tmp_path,campaign); out=tmp_path/'native-synthetic-tiny'
    with pytest.raises(ValueError,match='memorization criterion'):
        t._execute(data,'tiny-fit',out,_epochs=1)
    assert d.load_json(out/'history.json')[0]['optimizer_steps']==1
    assert (out/'model.keras').exists() and not (out/'tiny-proof.json').exists()
    model=t.TensorFlowBackend().load(out/'model.keras')
    assert model.input_shape==(None,30,1588) and model.count_params()==526194
    assert int(model.optimizer.iterations.numpy())==1


def test_actual_tensorflow_full_synthetic_trusted_gate_only(campaign,tmp_path,monkeypatch):
    t=train(); data=encoded_data(tmp_path,campaign); out=tmp_path/'native-synthetic-full'; gate=tmp_path/'synthetic-gate.json'
    gate.write_text('{"synthetic_fixture_only":true}')
    def synthetic_gate(path,received,**kwargs):
        assert received.provenance=='synthetic_in_process' and path==gate
        return {'status':'synthetic_fixture_gate_not_real_proof'}
    monkeypatch.setattr(t,'_verify_tiny',synthetic_gate)
    deny_test_access(monkeypatch)
    result=t._execute(data,'fit',out,tiny_proof=gate,_epochs=1)
    assert result['optimizer_steps']==4 and result['actual_epochs']==1 and result['selected_checkpoint_steps']==4
    history=d.load_json(out/'history.json'); assert len(history)==1 and all(np.isfinite(history[0][k]) for k in ['accuracy','loss','val_accuracy','val_loss'])
    model=t.TensorFlowBackend().load(out/'model.keras')
    callbacks=t._callbacks(t.TensorFlowBackend(),model,data.arrays['validation'][:2])
    early,reduce=callbacks
    assert (early.monitor,early.mode,early.patience)==('val_accuracy','max',15)
    assert (reduce.monitor,reduce.mode,reduce.patience,reduce.factor)==('val_loss','min',6,.5)
    assert early.params['validation_data'][0] is data.arrays['validation'][0]
    # Exercise native callbacks without fitting additional epochs or real data.
    model.stop_training=False
    for cb in callbacks: cb.on_train_begin({})
    for epoch in range(16):
        for cb in callbacks: cb.on_epoch_end(epoch,dict(val_accuracy=.1,val_loss=2.0))
    assert model.stop_training and float(model.optimizer.learning_rate.numpy())<.001


@pytest.mark.parametrize('native',[False,True])
def test_tiny_applies_once_and_retains_bound_calibration_without_rewriting_history(campaign,tmp_path,native):
    t=train(); data=encoded_data(tmp_path,campaign); out=tmp_path/'calibrated'
    backend=None if native else SyntheticBackend()
    if native:
        with pytest.raises(ValueError,match='memorization criterion'):
            t._execute(data,'tiny-fit',out,_epochs=1)
    else:
        t._execute(data,'tiny-fit',out,_backend=backend,_epochs=1)
    assert (out/'batchnorm-calibration.json').is_file(), 'tiny producer omitted calibration receipt'
    receipt=d.load_json(out/'batchnorm-calibration.json')
    assert receipt['protocol']=='tiny_fit_layerwise_exact_moments_v1'
    assert receipt['selected']==t._selected_identity(t.tiny_selection(data))
    assert receipt['sources']==t.source_binding()
    assert receipt['model_sha256']==d.sha256(out/'model.keras')
    assert receipt['optimizer_steps']==1
    before=np.load(out/'pre_calibration_probabilities.npy'); y=t.tiny_selection(data)[1]
    assert receipt['pre_calibration']==dict(correct=int((before.argmax(axis=1)==y).sum()),mean_crossentropy=t._loss(y,before))
    assert d.load_json(out/'history.json')[-1]['mean_crossentropy']==receipt['pre_calibration']['mean_crossentropy']
    assert receipt['pre_probabilities_sha256']==d.sha256(out/'pre_calibration_probabilities.npy')
    assert receipt['kind']==('native_frozen_fit_moments' if native else 'synthetic_lifecycle_only_no_calibration')
    if native:
        from training.holistic_migration import batchnorm_calibration as c
        m=t.TensorFlowBackend().load(out/'model.keras'); x=t.tiny_selection(data)[0]
        assert len(receipt['native']['layers'])==2
        assert receipt['native']['locked_before']==receipt['native']['locked_after']
        assert receipt['native']['input']==t._array_digest(x)
        assert c.verify_receipt(m,x,receipt['native']) is None
        p=t._predict(t.TensorFlowBackend(),m,x)
        singles=np.concatenate([t._predict(t.TensorFlowBackend(),m,z[None]) for z in x])
        np.testing.assert_allclose(singles,p,rtol=1e-6,atol=1e-7)
        assert not (out/'tiny-proof.json').exists()
    else:
        proof=d.load_json(out/'tiny-proof.json')
        assert proof['calibration_protocol']==receipt['protocol']
        assert proof['files']['batchnorm-calibration.json']==d.sha256(out/'batchnorm-calibration.json')
        assert t._verify_tiny(out/'tiny-proof.json',data,_backend=backend)==proof


@pytest.mark.parametrize('fault',['missing','tamper','stale','protocol','selected','checkpoint','steps','pre_metric','pre_hash','kind','native_dummy','extra','config_protocol','proof_protocol','batch_dependent'])
def test_actual_tiny_consumer_denies_rebound_calibration_faults_before_full_reservation(campaign,tmp_path,fault):
    t=train(); data=encoded_data(tmp_path,campaign); out=tmp_path/'tiny'; backend=SyntheticBackend()
    t._execute(data,'tiny-fit',out,_backend=backend,_epochs=1)
    path=out/'batchnorm-calibration.json'; proof=d.load_json(out/'tiny-proof.json')
    receipt=d.load_json(path)
    if fault=='missing': path.unlink()
    elif fault=='tamper': path.write_text('{}')
    elif fault=='config_protocol':
        config=d.load_json(out/'config.json'); config['calibration_protocol']='old'
        rewrite_json(out/'config.json',config)
        start=d.load_json(out/'start.json'); start['config_sha256']=d.canonical_hash(config)
        rewrite_json(out/'start.json',start)
        for name in ['start.json','config.json']: proof['files'][name]=d.sha256(out/name)
    elif fault=='proof_protocol': proof['calibration_protocol']='old'
    elif fault=='batch_dependent':
        predict=backend.predict
        def changed(m,x):
            p=predict(m,x)
            return np.roll(p,1,axis=1) if len(x)==1 else p
        backend.predict=changed
    else:
        if fault=='stale': receipt['sources']['batchnorm_calibration.py']='0'*64
        if fault=='protocol': receipt['protocol']='old'
        if fault=='selected': receipt['selected']['ids'].reverse()
        if fault=='checkpoint': receipt['model_sha256']='0'*64
        if fault=='steps': receipt['optimizer_steps']=2
        if fault=='pre_metric': receipt['pre_calibration']['mean_crossentropy']=.3
        if fault=='pre_hash': receipt['pre_probabilities_sha256']='0'*64
        if fault=='kind': receipt['kind']='native_frozen_fit_moments'
        if fault=='native_dummy': receipt['native']={'status':'success'}
        if fault=='extra': receipt['bypass']=True
        rewrite_json(path,receipt); proof['files'][path.name]=d.sha256(path)
    rewrite_json(out/'tiny-proof.json',proof)
    with pytest.raises((ValueError,OSError,KeyError,TypeError)):
        t._verify_tiny(out/'tiny-proof.json',data,_backend=backend)
    full=tmp_path/'never-full'
    with pytest.raises((ValueError,OSError,KeyError,TypeError)):
        t._execute(data,'fit',full,tiny_proof=out/'tiny-proof.json',_backend=backend,_epochs=1)
    assert not full.exists()


def test_native_positive_synthetic_ordinary_inference_proof_and_consumer(campaign,tmp_path):
    t=train(); b,a=synthetic_bundle(tmp_path/'bundle',campaign)
    # Eight obviously separable synthetic XY patterns; labels and all50 outputs unchanged.
    x=np.load(b/'X_fit.npy'); y=np.load(b/'y_fit.npy')
    patterns=np.random.default_rng(t.SEED).choice(np.array([-1.,1.],np.float32),(50,478,2))
    x[:,:,153:1587].reshape(50,30,478,3)[:,:,:,:2]=patterns[y,None]
    np.save(b/'X_fit.npy',x,allow_pickle=False); rebind_bundle(b,a)
    data=t._read_bundle(b,a,evidence_kind='synthetic_in_process'); out=tmp_path/'native-positive'
    proof=t._execute(data,'tiny-fit',out)
    assert proof['correct']==8 and proof['mean_crossentropy']<=.1
    assert 1<=proof['actual_epochs']<=300 and proof['optimizer_steps']==proof['actual_epochs']
    receipt=d.load_json(out/'batchnorm-calibration.json')
    assert receipt['kind']=='native_frozen_fit_moments'
    assert t._verify_tiny(out/'tiny-proof.json',data)==proof
    import shutil
    shutil.copytree(out,tmp_path/'native-positive-original')
    # The actual native consumer, not just the generic helper, rejects rebound moments.
    receipt['native']['layers'][0]['post_mean'][0]+=1
    rewrite_json(out/'batchnorm-calibration.json',receipt)
    proof['files']['batchnorm-calibration.json']=d.sha256(out/'batchnorm-calibration.json')
    rewrite_json(out/'tiny-proof.json',proof)
    with pytest.raises(ValueError): t._verify_tiny(out/'tiny-proof.json',data)


@pytest.mark.parametrize('fault',['ce','budget','batch','calibration_exception'])
def test_calibration_does_not_relax_gate_or_publish_partial_success(campaign,tmp_path,monkeypatch,fault):
    t=train(); data=encoded_data(tmp_path,campaign); backend=SyntheticBackend(wrong=fault=='budget'); out=tmp_path/'tiny'
    if fault in ['ce','batch']:
        predict=backend.predict
        def changed(m,x):
            p=predict(m,x)
            if fault=='ce':
                y=p.argmax(axis=1); p[:]=.1/49; p[np.arange(len(x)),y]=.9
            elif len(x)==1: p=np.roll(p,1,axis=1)
            return p
        backend.predict=changed
    if fault=='calibration_exception':
        def fail(*args): raise RuntimeError('explicit native calibration fault')
        monkeypatch.setattr(t.bc,'calibrate',fail); backend=t.TensorFlowBackend()
    with pytest.raises((ValueError,RuntimeError)):
        t._execute(data,'tiny-fit',out,_backend=backend,_epochs=None if fault=='budget' else 1)
    assert not (out/'tiny-proof.json').exists() and (out/'failure.json').exists()
    history=d.load_json(out/'history.json')
    assert len(history)==(300 if fault=='budget' else 1)
    assert history[-1]['optimizer_steps']==len(history)
    if fault=='ce': assert history[-1]['correct']==8 and history[-1]['mean_crossentropy']>.1
    if fault in ['batch','calibration_exception']: assert not (out/'batchnorm-calibration.json').exists()


@pytest.mark.parametrize('fault',['missing','protocol'])
def test_separate_evaluator_uses_actual_calibration_consumer_before_test_access(campaign,tmp_path,monkeypatch,fault):
    from training.holistic_migration import face_evaluate as e
    t=train(); data=encoded_data(tmp_path,campaign); backend=SyntheticBackend(); tiny=tmp_path/'tiny'; full=tmp_path/'full'
    t._execute(data,'tiny-fit',tiny,_backend=backend,_epochs=1)
    t._execute(data,'fit',full,tiny_proof=tiny/'tiny-proof.json',_backend=backend,_epochs=1)
    if fault=='missing': (tiny/'batchnorm-calibration.json').unlink()
    else:
        receipt=d.load_json(tiny/'batchnorm-calibration.json'); receipt['protocol']='old'
        rewrite_json(tiny/'batchnorm-calibration.json',receipt)
        proof=d.load_json(tiny/'tiny-proof.json'); proof['files']['batchnorm-calibration.json']=d.sha256(tiny/'batchnorm-calibration.json')
        rewrite_json(tiny/'tiny-proof.json',proof)
        config=d.load_json(full/'config.json'); config['tiny_proof_sha256']=d.sha256(tiny/'tiny-proof.json'); rewrite_json(full/'config.json',config)
        start=d.load_json(full/'start.json'); start['config_sha256']=d.canonical_hash(config); rewrite_json(full/'start.json',start)
        selection=d.load_json(full/'selection.json')
        for name in ['start.json','config.json']: selection['files'][name]=d.sha256(full/name)
        rewrite_json(full/'selection.json',selection)
        disposition=d.load_json(full/'selection-disposition.json'); disposition['selection_sha256']=d.sha256(full/'selection.json'); rewrite_json(full/'selection-disposition.json',disposition)
    deny_test_access(monkeypatch); target=tmp_path/'never-evaluation'
    with pytest.raises((ValueError,OSError)): e._evaluate(full,data,target,_backend=backend)
    assert not target.exists()


def native_replay_fixture(tmp_path,campaign):
    """Fresh current-source actual native artifact, not a restamped old proof."""
    t=train(); b,a=synthetic_bundle(tmp_path/'bundle',campaign)
    x=np.load(b/'X_fit.npy'); y=np.load(b/'y_fit.npy')
    patterns=np.random.default_rng(t.SEED).choice(np.array([-1.,1.],np.float32),(50,478,2))
    x[:,:,153:1587].reshape(50,30,478,3)[:,:,:,:2]=patterns[y,None]
    np.save(b/'X_fit.npy',x,allow_pickle=False); rebind_bundle(b,a)
    data=t._read_bundle(b,a,evidence_kind='synthetic_in_process')
    out=tmp_path/'native-replay'; proof=t._execute(data,'tiny-fit',out)
    assert t._verify_tiny(out/'tiny-proof.json',data)==proof
    return data,out,proof


def rebind_lifecycle_selection_tiny(full,tiny):
    """Repoint only a symbolic synthetic full-selection control to native tiny."""
    t=train(); config=d.load_json(full/'config.json')
    config.update(tiny_proof=str(tiny/'tiny-proof.json'),tiny_proof_sha256=d.sha256(tiny/'tiny-proof.json'))
    rewrite_json(full/'config.json',config)
    start=d.load_json(full/'start.json'); start['config_sha256']=d.canonical_hash(config)
    rewrite_json(full/'start.json',start)
    selection=d.load_json(full/'selection.json')
    for name in ['start.json','config.json']: selection['files'][name]=d.sha256(full/name)
    rewrite_json(full/'selection.json',selection)
    disposition=d.load_json(full/'selection-disposition.json'); disposition['selection_sha256']=d.sha256(full/'selection.json')
    rewrite_json(full/'selection-disposition.json',disposition)


@pytest.mark.parametrize('fault',['pre_mean','pre_variance'])
def test_native_replay_denies_finite_rebound_pre_moments_at_all_consumers(campaign,tmp_path,monkeypatch,fault):
    import copy
    import tensorflow as tf
    from training.holistic_migration import face_evaluate as e
    t=train(); data,out,proof=native_replay_fixture(tmp_path,campaign)
    backend=t.TensorFlowBackend(); model=backend.load(out/'model.keras'); x=t.tiny_selection(data)[0]
    receipt=d.load_json(out/'batchnorm-calibration.json')
    pre=np.load(out/'pre_calibration_probabilities.npy',allow_pickle=False)
    def independent_replay(native):
        clone=tf.keras.models.clone_model(model); clone.set_weights(model.get_weights())
        for record in native['layers']:
            layer=clone.layers[record['index']]
            layer.moving_mean.assign(record['pre_mean']); layer.moving_variance.assign(record['pre_variance'])
        return t._predict(backend,clone,x)
    np.testing.assert_allclose(independent_replay(receipt['native']),pre,rtol=1e-6,atol=1e-7)
    # Symbolic full lifecycle only; no native full fitting/evaluation/test access.
    symbolic=tmp_path/'symbolic-tiny'; full=tmp_path/'symbolic-full'; fixture_backend=SyntheticBackend()
    fixture_backend.predict=lambda m,x:t._predict(backend,model,x)  # frozen synthetic fixture inference only
    t._execute(data,'tiny-fit',symbolic,_backend=fixture_backend,_epochs=1)
    t._execute(data,'fit',full,tiny_proof=symbolic/'tiny-proof.json',_backend=fixture_backend,_epochs=1)
    rebind_lifecycle_selection_tiny(full,out)
    assert e.frozen_selection(full,data)['status']=='frozen_validation_selection'
    original=copy.deepcopy(receipt)
    receipt['native']['layers'][0][fault][0]+=10000. if fault=='pre_mean' else 100000000.
    changed=independent_replay(receipt['native'])
    assert np.isfinite(changed).all() and not np.allclose(changed,pre,rtol=1e-6,atol=1e-7)
    # The sole inconsistency is finite native pre-state vs unchanged saved probabilities/history.
    assert receipt['sources']==t.source_binding() and receipt['native']['source_sha256']==d.sha256(Path(t.bc.__file__))
    assert receipt['native']['locked_after']==original['native']['locked_after']
    import shutil
    shutil.copytree(out,tmp_path/'native-replay-original')
    unchanged={name:d.sha256(out/name) for name in proof['files'] if name!='batchnorm-calibration.json'}
    rewrite_json(out/'batchnorm-calibration.json',receipt)
    proof['files']['batchnorm-calibration.json']=d.sha256(out/'batchnorm-calibration.json')
    rewrite_json(out/'tiny-proof.json',proof); rebind_lifecycle_selection_tiny(full,out)
    assert e.frozen_selection(full,data)['status']=='frozen_validation_selection'
    deny_test_access(monkeypatch)
    with pytest.raises(ValueError,match='pre-calibration replay'):
        t._verify_tiny(out/'tiny-proof.json',data)
    never_full=tmp_path/'never-native-full'
    with pytest.raises(ValueError,match='pre-calibration replay'):
        t._execute(data,'fit',never_full,tiny_proof=out/'tiny-proof.json')
    target=tmp_path/'never-native-evaluation'
    with pytest.raises(ValueError,match='pre-calibration replay'):
        e._evaluate(full,data,target)
    assert not never_full.exists() and not target.exists()
    assert unchanged=={name:d.sha256(out/name) for name in unchanged}
    d.write_json(tmp_path/'native-replay-control.json',dict(fault=fault,healthy_current_source_consumer=True,
        healthy_replay=True,rebound_replay_max_abs=float(np.max(np.abs(changed-pre))),
        tolerance=dict(rtol=1e-6,atol=1e-7),rebound_receipt_sha256=d.sha256(out/'batchnorm-calibration.json'),
        rebound_tiny_sha256=d.sha256(out/'tiny-proof.json'),unchanged_artifact_hashes=unchanged,
        denied_at=['tiny_consumer','before_full_reservation','before_new_evaluation'],
        sources=t.source_binding(),native_helper_source=receipt['native']['source_sha256']))


def test_native_producer_denies_inconsistent_pre_moments_before_receipt_publication(campaign,tmp_path,monkeypatch):
    t=train(); data=encoded_data(tmp_path,campaign); out=tmp_path/'producer-replay-failure'
    calibrate=t.bc.calibrate; captured=[]
    def corrupted(model,x):
        receipt=calibrate(model,x)
        captured.append((model,[v.numpy().copy() for v in model.variables+model.optimizer.variables],
                         json.dumps(model.get_config(),sort_keys=True),json.dumps(model.get_compile_config(),sort_keys=True)))
        receipt['layers'][0]['pre_mean'][0]+=10000.
        return receipt
    monkeypatch.setattr(t.bc,'calibrate',corrupted)
    with pytest.raises(ValueError,match='pre-calibration replay'):
        t._execute(data,'tiny-fit',out,_epochs=1)
    assert (out/'model.keras').exists() and not (out/'tiny-proof.json').exists()
    assert not (out/'batchnorm-calibration.json').exists()
    assert 'pre-calibration replay' in d.load_json(out/'failure.json')['detail']
    assert d.load_json(out/'history.json')[-1]['optimizer_steps']==1
    model,state,config,compile_config=captured[0]
    for expected,v in zip(state,model.variables+model.optimizer.variables): np.testing.assert_array_equal(v.numpy(),expected)
    assert json.dumps(model.get_config(),sort_keys=True)==config
    assert json.dumps(model.get_compile_config(),sort_keys=True)==compile_config

