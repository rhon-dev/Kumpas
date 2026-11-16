"""Task D tests: explicit synthetic fixtures only, never real canonical arrays/weights."""
import importlib
import json
from pathlib import Path
import sys
import numpy as np
import pytest
from .test_augmentation import synthetic_tensor


def train(): return importlib.import_module('training.holistic_migration.train')


def test_lazy_architecture_actual_bounded_optimizer_save_reload(tmp_path):
    t=train()
    import subprocess
    lazy=subprocess.run([sys.executable,'-E','-B','-c',"import sys; import training.holistic_migration.train; assert 'tensorflow' not in sys.modules"],cwd=t.d.REPO,capture_output=True,text=True)
    assert lazy.returncode==0,lazy.stderr
    m=t.build_model()
    import tensorflow as tf
    assert tf.__version__=='2.19.0'
    assert m.input_shape==(None,30,153) and m.output_shape==(None,50)
    assert m.count_params()==250674
    assert [type(l).__name__ for l in m.layers]==['Conv1D','BatchNormalization','Conv1D','BatchNormalization','MaxPooling1D','LSTM','Dropout','LSTM','Dropout','Dense','Dropout','Dense']
    assert [(m.layers[i].filters,m.layers[i].kernel_size,m.layers[i].padding,m.layers[i].activation.__name__) for i in [0,2]]==[(64,(3,),'same','relu'),(128,(3,),'same','relu')]
    assert m.layers[5].units==128 and m.layers[5].return_sequences
    assert m.layers[7].units==64 and not m.layers[7].return_sequences
    assert all(m.layers[i].rate==.4 for i in [6,8,10])
    assert m.layers[9].units==128 and m.layers[-1].activation.__name__=='softmax'
    assert m.loss=='sparse_categorical_crossentropy'
    assert float(m.optimizer.learning_rate.numpy())==pytest.approx(.001)
    x=synthetic_tensor(); y=np.array([0,1],np.int64)
    before=[w.numpy().copy() for w in m.trainable_weights]
    result=m.train_on_batch(x,y,return_dict=True)
    assert np.isfinite(list(result.values())).all()
    assert int(m.optimizer.iterations.numpy())==1
    assert any(not np.array_equal(a,b.numpy()) for a,b in zip(before,m.trainable_weights))
    p=m(x,training=False).numpy()
    assert p.shape==(2,50) and np.isfinite(p).all()
    path=tmp_path/'synthetic.keras'; m.save(path)
    loaded=tf.keras.models.load_model(path)
    np.testing.assert_allclose(loaded(x,training=False).numpy(),p,rtol=1e-6,atol=1e-7)
    assert int(loaded.optimizer.iterations.numpy())==1



def synthetic_bundle(root):
    """Explicit synthetic metadata, never a source_video receipt or real admission."""
    t=train(); d=importlib.import_module('training.holistic_migration.dataset')
    root.mkdir(); campaign=root.parent/(root.name+'-synthetic-campaign'); campaign.mkdir()
    classes=[dict(dense_id=i,original_id=c['id'],label=c['label'],category=c['category']) for i,c in enumerate(d.load_json(d.REPO/'training/preprocessing/selected_classes.json')['selected'])]
    rows=[]; captures=[]
    for p in d.PARTITIONS:
        for c in classes:
            clip=f"clips/{c['original_id']}/synthetic-{p}.mp4"
            rows.append(dict(clip_id=clip,source_token=clip.replace('/',chr(92)),original_id=c['original_id'],dense_id=c['dense_id'],label=c['label'],csv_label=c['label'],official_split='test' if p=='test' else 'train',signer_id=None,partition=p,archive_member=clip,video_bytes=1,video_sha256=d.canonical_hash(clip)))
    rows.sort(key=lambda r:r['clip_id'])
    for r in rows: captures.append(dict(clip_id=r['clip_id'],dense_id=r['dense_id'],partition=r['partition'],reason='eligible',observation_count=30,hand_count=29,start_ms=0,end_ms=1000,source_observation_count=30,source_start_ms=0,source_end_ms=1000))
    membership=campaign/'membership.json'; d.write_json(membership,dict(rows=rows))
    graph=dict(paths=dict(partition_manifest=str(membership),classes=str(d.REPO/'training/preprocessing/selected_classes.json')),bindings=dict(partition_manifest=d.sha256(membership),classes=d.sha256(d.REPO/'training/preprocessing/selected_classes.json')),classes=classes,contract=d.contract_binding(),contract_sha256=d.canonical_hash(d.contract_binding()),runtime=d.runtime_binding(),runtime_sha256=d.canonical_hash(d.runtime_binding()))
    source=dict(schema_version=1,status='complete',evidence_kind='synthetic_in_process',full_campaign_qualification=True,graph=graph)
    d.write_json(campaign/'extraction_manifest.json',source)
    from types import SimpleNamespace
    eligibility=d.eligibility_summary(SimpleNamespace(classes=classes),captures)
    attempt=dict(campaign=str(campaign),campaign_manifest_sha256=d.sha256(campaign/'extraction_manifest.json'),graph=graph)
    artifacts={}
    for name,value in [('class_metadata.json',classes),('capture_rows.json',captures),('eligibility.json',eligibility),('attempt.json',attempt)]:
        d.write_json(root/name,value); artifacts[name]=dict(sha256=d.sha256(root/name))
    for p in d.PARTITIONS:
        selected=[r for r in rows if r['partition']==p]
        arrays={f'X_{p}.npy':synthetic_tensor(50),f'y_{p}.npy':np.array([r['dense_id'] for r in selected],np.int64),f'clip_ids_{p}.npy':np.array([r['clip_id'] for r in selected],dtype=np.str_)}
        for name,a in arrays.items():
            with (root/name).open('xb') as stream: np.save(stream,a,allow_pickle=False)
            artifacts[name]=dict(sha256=d.sha256(root/name),shape=list(a.shape),dtype=str(a.dtype))
    m=dict(schema_version=1,status='complete',evidence_kind='synthetic_in_process',training_qualified=False,classes=classes,eligibility=eligibility,artifacts=artifacts,campaign=str(campaign),campaign_manifest_sha256=d.sha256(campaign/'extraction_manifest.json'),graph=graph,augmentation='none',tensor_contract='Float32[N,30,153] hm153-v1')
    d.write_json(root/'data_manifest.json',m)
    admission=dict(schema_version=1,status='synthetic_fixture_only',purpose='fit_validation_only',bundle=str(root),data_manifest_sha256=d.sha256(root/'data_manifest.json'),campaign_manifest_sha256=m['campaign_manifest_sha256'],source_contract_sha256=graph['contract_sha256'],class_map_sha256=graph['bindings']['classes'],classes=50)
    ap=root.parent/(root.name+'-synthetic-admission.json'); d.write_json(ap,admission)
    return root,ap


def test_admitted_reader_is_fit_validation_only_and_real_rejects_synthetic(tmp_path,monkeypatch):
    t=train(); b,a=synthetic_bundle(tmp_path/'bundle')
    opened=[]; real_open=Path.open; real_load=np.load
    def guard(path,*args,**kwargs):
        assert not any(Path(path).name==f'{prefix}_test.npy' for prefix in ['X','y','clip_ids'])
        opened.append(str(path)); return real_open(path,*args,**kwargs)
    def guard_load(path,*args,**kwargs):
        assert '_test.npy' not in str(path); return real_load(path,*args,**kwargs)
    monkeypatch.setattr(Path,'open',guard); monkeypatch.setattr(np,'load',guard_load)
    monkeypatch.setattr(importlib.import_module('training.holistic_migration.dataset'),'validate_campaign',lambda *a:pytest.fail('all-partition consumer forbidden'))
    data=t._read_bundle(b,a,evidence_kind='synthetic_in_process')
    assert set(data.arrays)=={'fit','validation'}
    assert data.provenance=='synthetic_in_process'
    assert len(data.arrays['fit'][0])==50
    with pytest.raises(ValueError): t.read_admitted(b,a)
    assert not any('_test.npy' in s for s in opened)



def rewrite_json(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,allow_nan=False))


def rebind_synthetic(bundle,admission):
    d=importlib.import_module('training.holistic_migration.dataset')
    m=d.load_json(bundle/'data_manifest.json')
    for name,record in m['artifacts'].items():
        record['sha256']=d.sha256(bundle/name)
        if name.endswith('.npy'):
            array=np.load(bundle/name,allow_pickle=False)
            record.update(shape=list(array.shape),dtype=str(array.dtype))
    rewrite_json(bundle/'data_manifest.json',m)
    a=d.load_json(admission); a['data_manifest_sha256']=d.sha256(bundle/'data_manifest.json'); rewrite_json(admission,a)


@pytest.mark.parametrize('bad',['unknown_reason','capture_float','extra_artifact','test_hash','admission_bool','admission_float','admission_extra','stale','copied','class_order','dimensions','labels','ids','absent','object_ids','support'])
def test_reader_strict_mutations_rejected(tmp_path,bad):
    t=train(); b,a=synthetic_bundle(tmp_path/'bundle')
    ap=json.loads(a.read_text()); m=json.loads((b/'data_manifest.json').read_text())
    if bad in ['unknown_reason','capture_float']:
        r=json.loads((b/'capture_rows.json').read_text())
        if bad=='unknown_reason': r[0]['reason']='invented'
        else: r[0]['observation_count']=30.0
        rewrite_json(b/'capture_rows.json',r)
        if bad=='unknown_reason':
            d=importlib.import_module('training.holistic_migration.dataset'); from types import SimpleNamespace
            e=d.eligibility_summary(SimpleNamespace(classes=m['classes']),r)
            rewrite_json(b/'eligibility.json',e); m['eligibility']=e
    if bad=='extra_artifact': m['artifacts']['unexpected.json']={'sha256':'0'*64}
    if bad=='test_hash': m['artifacts']['X_test.npy']['sha256']='X'*64
    if bad=='admission_bool': ap['schema_version']=True
    if bad=='admission_float': ap['classes']=50.0
    if bad=='admission_extra': ap['allow']=True
    if bad=='copied': ap['bundle']=str(tmp_path/'copy')
    if bad=='class_order': m['classes']=list(reversed(m['classes']))
    if bad=='dimensions': np.save(b/'X_fit.npy',synthetic_tensor(50)[:,:,:152],allow_pickle=False)
    if bad=='labels': np.save(b/'y_fit.npy',np.zeros(50,np.int64),allow_pickle=False)
    if bad=='ids': np.save(b/'clip_ids_fit.npy',np.array(['duplicate']*50),allow_pickle=False)
    if bad=='object_ids': np.save(b/'clip_ids_fit.npy',np.array(['x']*50,object),allow_pickle=True)
    if bad=='absent':
        x=np.load(b/'X_fit.npy'); x[0,0,1]=1; np.save(b/'X_fit.npy',x,allow_pickle=False)
    if bad=='support':
        for prefix in ['X','y','clip_ids']:
            array=np.load(b/f'{prefix}_fit.npy'); np.save(b/f'{prefix}_fit.npy',array[:-1],allow_pickle=False)
    rewrite_json(b/'data_manifest.json',m); rewrite_json(a,ap)
    if bad not in ['extra_artifact','test_hash','stale','object_ids']: rebind_synthetic(b,a)
    if bad in ['extra_artifact','test_hash']:
        d=importlib.import_module('training.holistic_migration.dataset'); ap['data_manifest_sha256']=d.sha256(b/'data_manifest.json'); rewrite_json(a,ap)
    with pytest.raises((ValueError,KeyError)): t._read_bundle(b,a,evidence_kind='synthetic_in_process')


class SyntheticBackend:
    """Trusted lifecycle fault seam, NOT TensorFlow or real learning evidence."""
    def __init__(self,fail_reload=False,wrong=False): self.built=0; self.loaded=0; self.fail_reload=fail_reload; self.wrong=wrong
    def build(self): self.built+=1; return {'steps':0}
    def steps(self,m): return m['steps']
    def step(self,m,x,y): m['steps']+=1
    def predict(self,m,x):
        y=np.rint(x[:,4,0]*100).astype(int)
        if self.wrong: y=(y+1)%50
        p=np.full((len(x),50),.00001,np.float32); p[np.arange(len(x)),y]=1-.00001*49
        return p
    def save(self,m,path): Path(path).write_text(json.dumps(m))
    def load(self,path):
        self.loaded+=1
        if self.fail_reload: raise ValueError('synthetic reload failure')
        return json.loads(Path(path).read_text())
    def callbacks(self,m): return []


def encoded_data(tmp_path):
    t=train(); b,a=synthetic_bundle(tmp_path/'bundle')
    x=np.load(b/'X_fit.npy'); y=np.load(b/'y_fit.npy'); x[:,4:,0]=y[:,None]/100
    np.save(b/'X_fit.npy',x,allow_pickle=False)
    x=np.load(b/'X_validation.npy'); y=np.load(b/'y_validation.npy'); x[:,4:,0]=y[:,None]/100
    np.save(b/'X_validation.npy',x,allow_pickle=False)
    rebind_synthetic(b,a)
    return t._read_bundle(b,a,evidence_kind='synthetic_in_process')


def deny_test_access(monkeypatch):
    original=Path.open; load=np.load
    def guard(path,*args,**kwargs):
        assert not Path(path).name.endswith('_test.npy'),'training touched test array'; return original(path,*args,**kwargs)
    def guard_load(path,*args,**kwargs):
        assert not str(path).endswith('_test.npy'),'training loaded test array'; return load(path,*args,**kwargs)
    monkeypatch.setattr(Path,'open',guard); monkeypatch.setattr(np,'load',guard_load)


def test_tiny_lifecycle_retains_hash_bound_synthetic_proof_only(tmp_path,monkeypatch):
    t=train(); data=encoded_data(tmp_path); backend=SyntheticBackend(); out=tmp_path/'tiny'
    deny_test_access(monkeypatch)
    data=t._read_bundle(data.bundle,data.admission,evidence_kind='synthetic_in_process')
    proof=t._execute(data,'tiny-fit',out,_backend=backend,_epochs=2)
    assert backend.built==1 and backend.loaded==1
    assert proof['provenance']=='synthetic_in_process' and proof['correct']==8 and proof['mean_crossentropy']<=.1
    assert proof['optimizer_steps']==1 and proof['actual_epochs']==1
    assert proof['selected_ids']==[min(s for s,y in zip(data.arrays['fit'][2],data.arrays['fit'][1]) if y==i) for i in range(8)]
    assert (out/'start.json').exists() and (out/'config.json').exists() and (out/'model.keras').exists()
    assert t._verify_tiny(out/'tiny-proof.json',data,_backend=backend)['correct']==8
    with pytest.raises(ValueError): t._execute(data,'tiny-fit',out,_backend=backend,_epochs=2)
    with pytest.raises(ValueError): t.verify_real_tiny(out/'tiny-proof.json',data)


@pytest.mark.parametrize('fault',['wrong','reload'])
def test_tiny_failed_learning_or_reload_never_publishes_proof(tmp_path,fault):
    t=train(); data=encoded_data(tmp_path); backend=SyntheticBackend(wrong=fault=='wrong',fail_reload=fault=='reload'); out=tmp_path/'failed'
    with pytest.raises(ValueError): t._execute(data,'tiny-fit',out,_backend=backend,_epochs=2)
    assert (out/'start.json').exists() and (out/'failure.json').exists()
    assert not (out/'tiny-proof.json').exists()



def test_full_fresh_model_fit_only_augmented_earliest_tie_selection(tmp_path,monkeypatch):
    t=train(); data=encoded_data(tmp_path); backend=SyntheticBackend(); tiny=tmp_path/'tiny'
    t._execute(data,'tiny-fit',tiny,_backend=backend,_epochs=2)
    before=data.arrays['validation'][0].copy(); batches=[]; original_step=backend.step
    def track(m,x,y):
        assert len(x)<=32; batches.append(len(x)); return original_step(m,x,y)
    backend.step=track
    deny_test_access(monkeypatch)
    data=t._read_bundle(data.bundle,data.admission,evidence_kind='synthetic_in_process')
    out=tmp_path/'fit'
    selected=t._execute(data,'fit',out,tiny_proof=tiny/'tiny-proof.json',_backend=backend,_epochs=3)
    assert backend.built==2  # tiny then a fresh model; no warm start
    assert selected['status']=='frozen_validation_selection' and selected['best_epoch']==1
    assert selected['actual_epochs']==3 and selected['optimizer_steps']==12
    assert sum(batches)==300
    np.testing.assert_array_equal(data.arrays['validation'][0],before)
    assert selected['policy']==t.POLICY and selected['policy']['live_ready'] is False
    assert (out/'complete.json').exists() and (out/'fit-report.json').exists() and (out/'validation-report.json').exists()
    augmentation=json.loads((out/'augmentation.json').read_text())
    assert augmentation['derived_count']==50 and augmentation['real_observations_added']==0
    assert json.loads((out/'model.keras').read_text())['steps']==4  # actual earliest best checkpoint


@pytest.mark.parametrize('bad',['boolean','missing_checkpoint','changed_checkpoint','synthetic_to_real','source','dataset','tensors','family','epochs'])
def test_full_proof_rejection_before_new_fit(tmp_path,bad):
    from dataclasses import replace
    t=train(); data=encoded_data(tmp_path); backend=SyntheticBackend(); tiny=tmp_path/'tiny'
    t._execute(data,'tiny-fit',tiny,_backend=backend,_epochs=2)
    path=tiny/'tiny-proof.json'; proof=json.loads(path.read_text())
    if bad=='boolean': rewrite_json(path,True)
    if bad=='missing_checkpoint': (tiny/'model.keras').unlink()
    if bad=='changed_checkpoint': (tiny/'model.keras').write_text('changed')
    if bad=='synthetic_to_real': data=replace(data,provenance='source_video')
    if bad=='source': proof['identity']['sources']['train.py']='0'*64
    if bad=='dataset': data=replace(data,identity=dict(data.identity,data_manifest_sha256='0'*64))
    if bad=='tensors': proof['selected_tensors']['X']['sha256']='0'*64
    if bad=='family': proof['identity']['family']['outputs']=8
    if bad=='epochs': proof['actual_epochs']=False
    if bad not in ['boolean','missing_checkpoint','changed_checkpoint']: rewrite_json(path,proof)
    out=tmp_path/'not-created'
    with pytest.raises((ValueError,TypeError,KeyError,AttributeError)):
        t._execute(data,'fit',out,tiny_proof=path,_backend=backend,_epochs=3)
    assert backend.built==1 and not out.exists()



@pytest.mark.parametrize('mode',['tiny-fit','fit'])
def test_actual_train_cli_synthetic_refusal_and_no_tensorflow_or_output(tmp_path,mode):
    import subprocess,os
    t=train(); b,a=synthetic_bundle(tmp_path/'bundle'); out=tmp_path/'never-created'
    cmd=[sys.executable,'-E','-B','-m','training.holistic_migration.train',mode,'--bundle',str(b),'--admission',str(a),'--output',str(out)]
    if mode=='fit': cmd+=['--tiny-proof',str(tmp_path/'not-real.json')]
    p=subprocess.run(cmd,cwd=t.d.REPO,capture_output=True,text=True,env=dict(os.environ,TMPDIR=str(Path.home()/'.hermes/cache/scratch')))
    assert p.returncode==2 and 'admission status' in p.stderr and not out.exists()
    assert 'tensorflow' not in p.stderr.lower()


def test_module_import_and_help_lazy_and_no_synthetic_cli_option(tmp_path):
    import subprocess,os
    root=Path(__file__).absolute().parents[3]
    code="import sys,runpy; sys.argv=['train','--help'];\ntry: runpy.run_module('training.holistic_migration.train',run_name='__main__')\nexcept SystemExit as e: assert e.code==0; assert 'tensorflow' not in sys.modules; print('LAZY_HELP_OK')"
    p=subprocess.run([sys.executable,'-E','-B','-c',code],cwd=root,capture_output=True,text=True)
    assert p.returncode==0 and 'LAZY_HELP_OK' in p.stdout
    p=subprocess.run([sys.executable,'-E','-B','-m','training.holistic_migration.train','tiny-fit','--allow-synthetic'],cwd=root,capture_output=True,text=True)
    assert p.returncode==2



def test_duplicate_admission_keys_are_not_an_exact_schema(tmp_path):
    t=train(); b,a=synthetic_bundle(tmp_path/'bundle')
    text=a.read_text(); a.write_text(text.replace('{','{"schema_version":0,',1))
    with pytest.raises(ValueError,match='duplicate'): t._read_bundle(b,a,evidence_kind='synthetic_in_process')


def test_full_invalid_output_rejected_before_checkpoint_native_load(tmp_path):
    t=train(); data=encoded_data(tmp_path); backend=SyntheticBackend(); tiny=tmp_path/'tiny'
    t._execute(data,'tiny-fit',tiny,_backend=backend,_epochs=2)
    loads=backend.loaded
    with pytest.raises(ValueError): t._execute(data,'fit',Path('relative-output'),tiny_proof=tiny/'tiny-proof.json',_backend=backend,_epochs=1)
    assert backend.loaded==loads and backend.built==1



def test_actual_tf_tiny_failure_has_real_step_checkpoint_reload_but_no_proof(tmp_path):
    t=train(); data=encoded_data(tmp_path); out=tmp_path/'actual-synthetic-tiny'
    with pytest.raises(ValueError,match='memorization criterion'):
        t._execute(data,'tiny-fit',out,_epochs=1)
    assert json.loads((out/'history.json').read_text())[0]['optimizer_steps']==1
    assert (out/'model.keras').exists() and not (out/'tiny-proof.json').exists()
    loaded=t.TensorFlowBackend().load(out/'model.keras')
    assert int(loaded.optimizer.iterations.numpy())==1


def test_actual_tf_full_bounded_synthetic_with_explicit_trusted_proof_seam(tmp_path,monkeypatch):
    t=train(); data=encoded_data(tmp_path); out=tmp_path/'actual-synthetic-fit'; gate=tmp_path/'synthetic-gate.json'
    rewrite_json(gate,{'synthetic_fixture_gate_only':True})
    # Explicit trusted synthetic lifecycle seam, never production CLI or real proof evidence.
    def synthetic_gate(path,received,**kwargs):
        assert received.provenance=='synthetic_in_process' and path==gate
        return {'provenance':'synthetic_in_process','status':'trusted_fixture_only'}
    monkeypatch.setattr(t,'_verify_tiny',synthetic_gate)
    selected=t._execute(data,'fit',out,tiny_proof=gate,_epochs=1)
    assert selected['actual_epochs']==1 and selected['optimizer_steps']==4
    assert selected['selected_checkpoint_steps']==4 and selected['provenance']=='synthetic_in_process'
    callbacks=t._callbacks(t.TensorFlowBackend(),t.build_model(),data.arrays['validation'][:2])
    assert callbacks[0].monitor=='val_accuracy' and callbacks[0].patience==15 and callbacks[0].mode=='max'
    assert callbacks[1].monitor=='val_loss' and callbacks[1].patience==6 and callbacks[1].factor==.5
    assert callbacks[0].params['validation_data'][0] is data.arrays['validation'][0]


def test_failed_full_report_preserves_selection_but_not_complete(tmp_path,monkeypatch):
    t=train(); data=encoded_data(tmp_path); backend=SyntheticBackend(); tiny=tmp_path/'tiny'; out=tmp_path/'fit'
    t._execute(data,'tiny-fit',tiny,_backend=backend,_epochs=1)
    e=importlib.import_module('training.holistic_migration.evaluate')
    def fail(*args,**kwargs): raise ValueError('synthetic report failure')
    monkeypatch.setattr(e,'metrics',fail)
    with pytest.raises(ValueError,match='synthetic report failure'):
        t._execute(data,'fit',out,tiny_proof=tiny/'tiny-proof.json',_backend=backend,_epochs=1)
    assert (out/'selection.json').exists() and (out/'failure.json').exists()
    assert not (out/'complete.json').exists()


def test_checkpoint_final_readback_failure_does_not_publish_tiny_proof(tmp_path,monkeypatch):
    t=train(); data=encoded_data(tmp_path); backend=SyntheticBackend(); out=tmp_path/'tiny'; sha=t.d.sha256
    def broken(path):
        if Path(path)==out/'model.keras': return '0'*64
        return sha(path)
    monkeypatch.setattr(t.d,'sha256',broken)
    with pytest.raises(ValueError,match='checkpoint readback'):
        t._execute(data,'tiny-fit',out,_backend=backend,_epochs=1)
    assert (out/'failure.json').exists() and not (out/'tiny-proof.json').exists()



@pytest.mark.parametrize('mode',['tiny-fit','fit'])
def test_optimizer_failure_retains_actual_partial_progress(tmp_path,mode):
    t=train(); data=encoded_data(tmp_path); backend=SyntheticBackend(); proof=None
    if mode=='fit':
        tiny=tmp_path/'tiny'; t._execute(data,'tiny-fit',tiny,_backend=backend,_epochs=1); proof=tiny/'tiny-proof.json'
    original=backend.step
    def fail(m,x,y):
        original(m,x,y)
        if m['steps']==2: raise ValueError('synthetic optimizer interruption')
    backend.step=fail
    if mode=='tiny-fit': backend.wrong=True
    out=tmp_path/'interrupted'
    with pytest.raises(ValueError,match='synthetic optimizer interruption'):
        t._execute(data,mode,out,tiny_proof=proof,_backend=backend,_epochs=3)
    failure=json.loads((out/'failure.json').read_text())
    assert failure['optimizer_steps']==2 and failure['actual_epochs']==(1 if mode=='tiny-fit' else 0)
    assert len(json.loads((out/'history.json').read_text()))==failure['actual_epochs']
    assert not (out/'selection.json').exists() and not (out/'tiny-proof.json').exists()


def test_failed_tiny_publication_must_not_unlock_full_fit(tmp_path,monkeypatch):
    """D-R3-001: exact retained parent behavior, at the actual proof consumer."""
    t=train(); data=encoded_data(tmp_path); backend=SyntheticBackend(); out=tmp_path/'tiny'
    assert data.provenance=='synthetic_in_process'
    deny_test_access(monkeypatch)
    primary=OSError('synthetic tiny-proof final publication readback primary')
    cleanup=PermissionError('synthetic tiny-proof cleanup secondary')
    real_hash=t.d.sha256; real_unlink=Path.unlink
    injections=[]; cleanups=[]
    def fail_hash(path):
        if Path(path)==out/'tiny-proof.json' and not injections:
            assert Path(path).is_file() and (out/'tiny-proof.json.pending').is_file()
            injections.append(str(path)); raise primary
        return real_hash(path)
    def fail_unlink(path,*args,**kwargs):
        if Path(path)==out/'tiny-proof.json':
            cleanups.append(str(path)); raise cleanup
        return real_unlink(path,*args,**kwargs)
    monkeypatch.setattr(t.d,'sha256',fail_hash); monkeypatch.setattr(Path,'unlink',fail_unlink)
    with pytest.raises(OSError) as raised:
        t._execute(data,'tiny-fit',out,_backend=backend,_epochs=1)
    assert injections==[str(out/'tiny-proof.json')] and cleanups==[str(out/'tiny-proof.json')]
    assert (out/'failure.json').is_file() and (out/'tiny-proof.json').is_file()
    failure=json.loads((out/'failure.json').read_text())
    monkeypatch.setattr(t.d,'sha256',real_hash); monkeypatch.setattr(Path,'unlink',real_unlink)
    accepted=None; rejection=None
    try: accepted=t._verify_tiny(out/'tiny-proof.json',data,_backend=backend)
    except (ValueError,OSError) as exc: rejection=type(exc).__name__+': '+str(exc)
    result=dict(provenance=data.provenance,actual_source_execution=False,
                injection_after_final_link_and_pending=True,cleanup_attempted=True,
                primary_preserved=raised.value is primary,raised=type(raised.value).__name__,
                failure=failure,residual_proof=True,reloaded_failed_proof_accepted=accepted is not None,
                accepted_status=None if accepted is None else accepted['status'],
                rejection=rejection,backend_models_built=backend.built,synthetic_optimizer_steps=1,
                full_fit_not_executed=True,production_cli_not_used=True)
    (tmp_path/'failed-tiny-consumer-result.json').write_text(json.dumps(result,indent=2)+'\n')
    assert accepted is None, 'Failed publication with retained failure.json must not unlock full-fit proof gate'
    # Exercise the actual caller with this exact failed publication, not only the consumer.
    built=backend.built; loaded=backend.loaded; full=tmp_path/'denied-full'
    def no_work(*args,**kwargs): pytest.fail('Residual failed proof must deny full work before reservation')
    for name in ['build','load','predict','step']: monkeypatch.setattr(backend,name,no_work)
    monkeypatch.setattr(t,'_reserve',no_work); monkeypatch.setattr(t,'rotate_fit',no_work)
    with pytest.raises(ValueError,match='failed tiny'):
        t._execute(data,'fit',full,tiny_proof=out/'tiny-proof.json',_backend=backend,_epochs=1)
    assert backend.built==built and backend.loaded==loaded and not full.exists()


@pytest.mark.parametrize('publication',['tiny-proof.json','selection.json','selection-disposition.json','fit-report.json','validation-report.json','complete.json'])
def test_trainer_publication_preserves_primary_on_actual_cleanup_failure(tmp_path,monkeypatch,publication):
    """Actual link/readback/rollback composition, not a mocked publisher failure."""
    t=train(); data=encoded_data(tmp_path); backend=SyntheticBackend()
    tiny=tmp_path/'tiny'; out=tiny if publication=='tiny-proof.json' else tmp_path/'fit'
    if publication!='tiny-proof.json':
        t._execute(data,'tiny-fit',tiny,_backend=backend,_epochs=1)
    deny_test_access(monkeypatch)
    prior=RuntimeError('unrelated earlier synthetic exception')
    primary=OSError('synthetic '+publication+' final readback primary')
    try: raise prior
    except RuntimeError:
        try: raise primary
        except OSError: pass
    assert primary.__context__ is prior
    real_hash=t.d.sha256; real_unlink=Path.unlink; injections=[]; cleanups=[]; saved={}
    def readback(path):
        if Path(path)==out/publication and not injections:
            assert Path(path).is_file() and (out/(publication+'.pending')).is_file()
            saved.update({p.name:p.read_bytes() for p in out.iterdir() if p.is_file()})
            injections.append(Path(path)); raise primary
        return real_hash(path)
    def cleanup(path,*args,**kwargs):
        if Path(path)==out/publication:
            cleanups.append(Path(path)); raise PermissionError('synthetic secondary cleanup failure')
        return real_unlink(path,*args,**kwargs)
    with monkeypatch.context() as fault:
        fault.setattr(t.d,'sha256',readback); fault.setattr(Path,'unlink',cleanup)
        with pytest.raises(OSError) as caught:
            t._execute(data,'tiny-fit' if publication=='tiny-proof.json' else 'fit',out,
                       tiny_proof=tiny/'tiny-proof.json',_backend=backend,_epochs=1)
    assert injections==[out/publication] and cleanups==[out/publication]
    assert {name:(out/name).read_bytes() for name in saved}==saved
    diagnostic=json.loads((out/'failure.json').read_text())
    (tmp_path/'trainer-publication-result.json').write_text(json.dumps(dict(
        publication=publication,provenance=data.provenance,injected_after_link=True,
        cleanup_attempted=True,primary_preserved=caught.value is primary,
        unrelated_context_preserved=primary.__context__ is prior,failure=diagnostic,
        saved_artifacts=sorted(saved),actual_source_execution=False),indent=2)+'\n')
    assert caught.value is primary, 'Owned cleanup must preserve the exact trainer publication primary'
    assert primary.__context__ is prior
    expected: dict[str,object]=dict(status='failed',error='OSError',detail=str(primary),
                  actual_epochs=1,optimizer_steps=1 if publication=='tiny-proof.json' else 4)
    if publication!='tiny-proof.json':
        frozen=publication in ['fit-report.json','validation-report.json','complete.json']
        expected['selection_disposition']=dict(schema_version=1,phase='fit_reports' if frozen else 'selection',
                                               frozen=frozen,identity=t._identity(data))
    assert diagnostic==expected


@pytest.mark.parametrize('diagnostic',['history.json','failure.json'])
def test_training_diagnostic_io_never_replaces_primary(tmp_path,monkeypatch,diagnostic):
    t=train(); data=encoded_data(tmp_path); backend=SyntheticBackend(); out=tmp_path/'tiny'
    deny_test_access(monkeypatch)
    primary=OSError('synthetic optimizer primary after one step')
    secondary=PermissionError('synthetic diagnostic secondary')
    real_step=backend.step; real_write=t.d.write_json; calls=[]
    def step(model,x,y):
        real_step(model,x,y); raise primary
    def write(path,value):
        if Path(path).name in ['history.json','failure.json']:
            calls.append(Path(path).name)
            if Path(path).name==diagnostic: raise secondary
        return real_write(path,value)
    monkeypatch.setattr(backend,'step',step); monkeypatch.setattr(t.d,'write_json',write)
    with pytest.raises(OSError) as caught:
        t._execute(data,'tiny-fit',out,_backend=backend,_epochs=1)
    assert diagnostic in calls and backend.built==1
    assert caught.value is primary, 'Diagnostic I/O must preserve the original training exception'
    assert calls==['history.json','failure.json'], 'Try failure disposition even if history persistence failed'
    assert (out/'start.json').is_file() and (out/'config.json').is_file()
    assert not (out/'tiny-proof.json').exists()
    if diagnostic=='history.json':
        assert json.loads((out/'failure.json').read_text())==dict(
            status='failed',error='OSError',detail=str(primary),actual_epochs=0,optimizer_steps=1)
    else:
        assert json.loads((out/'history.json').read_text())==[]


@pytest.mark.parametrize('disposition',['failed','success_claim','malformed','directory','dangling_symlink'])
def test_failed_tiny_disposition_denies_full_caller_before_work(tmp_path,monkeypatch,disposition):
    t=train(); data=encoded_data(tmp_path); backend=SyntheticBackend(); tiny=tmp_path/'tiny'
    t._execute(data,'tiny-fit',tiny,_backend=backend,_epochs=1)
    proof=tiny/'tiny-proof.json'
    assert t._verify_tiny(proof,data,_backend=backend)['status']=='tiny_proven'  # healthy control
    marker=tiny/'failure.json'
    if disposition=='directory': marker.mkdir()
    elif disposition=='dangling_symlink': marker.symlink_to('synthetic-missing-diagnostic')
    elif disposition=='malformed': marker.write_bytes(b'{incomplete diagnostic')
    else: rewrite_json(marker,dict(status=disposition))
    built=backend.built; loaded=backend.loaded; out=tmp_path/'must-not-exist'
    retained={p.name:p.read_bytes() for p in tiny.iterdir() if p.is_file() and not p.is_symlink()}
    deny_test_access(monkeypatch)
    real_open=Path.open
    def no_proof_read(path,*args,**kwargs):
        assert Path(path)!=proof, 'Failed disposition must precede success artifact consumption'
        return real_open(path,*args,**kwargs)
    def no_work(*args,**kwargs): pytest.fail('Failed tiny gate must precede new work/reservation/backend')
    monkeypatch.setattr(Path,'open',no_proof_read)
    for name in ['build','load','predict','step']: monkeypatch.setattr(backend,name,no_work)
    monkeypatch.setattr(t,'rotate_fit',no_work); monkeypatch.setattr(t,'_reserve',no_work)
    with pytest.raises(ValueError,match='failed tiny'):
        t._execute(data,'fit',out,tiny_proof=proof,_backend=backend,_epochs=1)
    assert backend.built==built and backend.loaded==loaded and not out.exists()
    monkeypatch.setattr(Path,'open',real_open)
    assert {p.name:p.read_bytes() for p in tiny.iterdir() if p.is_file() and not p.is_symlink()}==retained


@pytest.mark.parametrize('publication',['tiny-proof.json','selection.json','selection-disposition.json','fit-report.json','validation-report.json','complete.json'])
@pytest.mark.parametrize('readback',['digest','json'])
@pytest.mark.parametrize('cleanup_fault',[False,True])
def test_trainer_bound_publisher_readback_and_cleanup_controls(tmp_path,monkeypatch,publication,readback,cleanup_fault):
    t=train(); e=importlib.import_module('training.holistic_migration.evaluate')
    assert t._publish_json is e._publish_json  # existing inspected primitive, no dependency replacement
    path=tmp_path/publication; pending=tmp_path/(publication+'.pending'); value=dict(status='explicit_synthetic_only')
    primary=PermissionError('synthetic final readback'); injections=[]; cleanups=[]
    real_hash=t.d.sha256; real_json=t.d.load_json; real_unlink=Path.unlink
    def read(path_arg):
        if Path(path_arg)==path:
            assert path.is_file() and pending.is_file(); injections.append(path_arg); raise primary
        return (real_hash if readback=='digest' else real_json)(path_arg)
    def cleanup(path_arg,*args,**kwargs):
        if Path(path_arg)==path:
            cleanups.append(path_arg)
            if cleanup_fault: raise OSError('synthetic unlink secondary')
        return real_unlink(path_arg,*args,**kwargs)
    monkeypatch.setattr(t.d,'sha256' if readback=='digest' else 'load_json',read)
    monkeypatch.setattr(Path,'unlink',cleanup)
    with pytest.raises(PermissionError) as caught: t._publish_json(path,value)
    assert caught.value is primary and injections==[path] and cleanups==[path]
    assert path.exists() is cleanup_fault and json.loads(pending.read_text())==value
    if cleanup_fault: assert path.read_bytes()==pending.read_bytes()


@pytest.mark.parametrize('publication',['tiny-proof.json','selection.json','selection-disposition.json','fit-report.json','validation-report.json','complete.json'])
@pytest.mark.parametrize('collision',['pending','preexisting_final','appearing_final'])
def test_trainer_bound_publisher_preserves_unowned_targets(tmp_path,monkeypatch,publication,collision):
    t=train(); path=tmp_path/publication; pending=tmp_path/(publication+'.pending')
    value=dict(status='explicit_synthetic_only'); established=b'{"status":"synthetic_established_other_owner"}\n'
    links=[]; real_link=t.os.link
    if collision=='pending': pending.write_bytes(established)
    if collision=='preexisting_final': path.write_bytes(established)
    def link(source,target):
        assert source==pending and target==path; links.append(target)
        if collision=='appearing_final': path.write_bytes(established)
        return real_link(source,target)
    def no_cleanup(*args,**kwargs): pytest.fail('Unowned successful target must not be revoked')
    monkeypatch.setattr(t.os,'link',link); monkeypatch.setattr(Path,'unlink',no_cleanup)
    with pytest.raises(FileExistsError): t._publish_json(path,value)
    if collision=='pending':
        assert pending.read_bytes()==established and not path.exists() and not links
    else:
        assert path.read_bytes()==established and json.loads(pending.read_text())==value and links==[path]


@pytest.mark.parametrize('cleanup_fault',[False,True])
def test_tiny_publication_primary_survives_failure_diagnostic_fault(tmp_path,monkeypatch,cleanup_fault):
    t=train(); data=encoded_data(tmp_path); backend=SyntheticBackend(); out=tmp_path/'tiny'
    deny_test_access(monkeypatch)
    primary=OSError('synthetic tiny publication primary'); injected=[]; cleanups=[]; diagnostics=[]
    real_hash=t.d.sha256; real_unlink=Path.unlink; real_write=t.d.write_json
    def digest(path):
        if Path(path)==out/'tiny-proof.json' and not injected:
            assert Path(path).is_file(); injected.append(Path(path)); raise primary
        return real_hash(path)
    def cleanup(path,*args,**kwargs):
        if Path(path)==out/'tiny-proof.json':
            cleanups.append(Path(path))
            if cleanup_fault: raise PermissionError('synthetic unlink secondary')
        return real_unlink(path,*args,**kwargs)
    def write(path,value):
        if Path(path)==out/'failure.json':
            diagnostics.append(Path(path)); raise OSError('synthetic diagnostic writer failure')
        return real_write(path,value)
    with monkeypatch.context() as fault:
        fault.setattr(t.d,'sha256',digest); fault.setattr(Path,'unlink',cleanup); fault.setattr(t.d,'write_json',write)
        with pytest.raises(OSError) as caught: t._execute(data,'tiny-fit',out,_backend=backend,_epochs=1)
    assert injected==cleanups==[out/'tiny-proof.json'] and diagnostics==[out/'failure.json']
    assert caught.value is primary and not (out/'failure.json').exists()
    assert (out/'tiny-proof.json').exists() is cleanup_fault
    assert (out/'history.json').is_file() and (out/'tiny-proof.json.pending').is_file()
    if not cleanup_fault:
        with pytest.raises(ValueError): t._verify_tiny(out/'tiny-proof.json',data,_backend=backend)
    # When BOTH unlink and failure persistence fail, no durable denial is established.
    # Deliberately do not promote this excluded case as a universal fail-closed guarantee.


def test_full_failure_phase_survives_history_diagnostic_failure(tmp_path,monkeypatch):
    t=train(); data=encoded_data(tmp_path); backend=SyntheticBackend(); tiny=tmp_path/'tiny'; run=tmp_path/'fit'
    t._execute(data,'tiny-fit',tiny,_backend=backend,_epochs=1); deny_test_access(monkeypatch)
    primary=OSError('synthetic full optimizer primary'); real_step=backend.step; real_write=t.d.write_json
    diagnostics=[]
    def step(model,x,y):
        real_step(model,x,y); raise primary
    def write(path,value):
        if Path(path)==run/'history.json':
            diagnostics.append('history'); raise PermissionError('synthetic history diagnostic')
        if Path(path)==run/'failure.json': diagnostics.append('failure')
        return real_write(path,value)
    with monkeypatch.context() as m:
        m.setattr(backend,'step',step); m.setattr(t.d,'write_json',write)
        with pytest.raises(OSError) as caught:
            t._execute(data,'fit',run,tiny_proof=tiny/'tiny-proof.json',_backend=backend,_epochs=1)
    assert caught.value is primary and diagnostics==['history','failure']
    assert json.loads((run/'failure.json').read_text())==dict(
        status='failed',error='OSError',detail=str(primary),actual_epochs=0,optimizer_steps=1,
        selection_disposition=dict(schema_version=1,phase='selection',frozen=False,identity=t._identity(data)))
    assert not (run/'selection-disposition.json').exists() and not (run/'selection.json').exists()
    retained={p.name:p.read_bytes() for p in run.iterdir() if p.is_file()}
    with pytest.raises(ValueError):
        t._execute(data,'fit',run,tiny_proof=tiny/'tiny-proof.json',_backend=backend,_epochs=1)
    assert {p.name:p.read_bytes() for p in run.iterdir() if p.is_file()}==retained







