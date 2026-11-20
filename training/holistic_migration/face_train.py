"""Isolated hm1588 training. Native TensorFlow is imported only by explicit execution."""


def build_model():
    """Fresh verified legacy CNN-LSTM family, fixed hm1588 input and dense50 output."""
    import tensorflow as tf
    tf.keras.utils.set_random_seed(20260705)
    layers=tf.keras.layers
    model=tf.keras.Sequential(name='hm1588_cnnlstm_c64-128_l128-64')
    model.add(layers.Input((30,1588),dtype='float32'))
    for filters in [64,128]:
        model.add(layers.Conv1D(filters,3,padding='same',activation='relu'))
        model.add(layers.BatchNormalization())
    model.add(layers.MaxPooling1D(2))
    for units,sequences in [(128,True),(64,False)]:
        model.add(layers.LSTM(units,return_sequences=sequences))
        model.add(layers.Dropout(.4))
    model.add(layers.Dense(128,activation='relu'))
    model.add(layers.Dropout(.4))
    model.add(layers.Dense(50,activation='softmax'))
    model.compile(tf.keras.optimizers.Adam(.001),'sparse_categorical_crossentropy',metrics=['accuracy'])
    return model



from pathlib import Path
import os
import numpy as np
from . import dataset as d, face_dataset as fd
from .face_augmentation import validate_tensor, rotate_fit
# These helpers are stateless and feature-agnostic; historical globals stay untouched.
from .train import AdmittedData, _json, _artifact

FEATURE=fd.TENSOR_CONTRACT
SEED=20260705
ACCEPTED_BUNDLE=d.REPO.parent/'holistic-migration-data/hm1588-canonical-bundle-20261116-v1'
ACCEPTED_MANIFEST='71c644b4de78f7031f96f7b25b1d5766f18fa611c33ad12f2a40a353b1c6c19a'
ACCEPTANCE=d.REPO.parent/'holistic-migration-data/evidence/face-data-parent-20261116/dataset-acceptance.json'
ADMISSION_KEYS={'schema_version','status','purpose','bundle','data_manifest_sha256',
    'dataset_acceptance','dataset_acceptance_sha256','campaign_manifest_sha256',
    'implementation','graph_sha256','classes','tensor_contract'}


def _partition(bundle,manifest,captures,partition):
    values=[]
    for prefix in ['X','y','clip_ids']:
        name=f'{prefix}_{partition}.npy'
        a=np.load(_artifact(bundle,manifest,name),allow_pickle=False)
        d.same(dict(shape=list(a.shape),dtype=str(a.dtype)),
            {k:manifest['artifacts'][name][k] for k in ['shape','dtype']},name+' layout')
        values.append(a)
    x,y,ids=values
    validate_tensor(x)
    if y.dtype!=np.int64 or y.shape!=(len(x),) or ((y<0)|(y>=50)).any(): raise ValueError('invalid dense int64 labels')
    if ids.dtype.kind!='U' or ids.shape!=(len(x),): raise ValueError('invalid Unicode IDs')
    expected=[r for r in captures if r['partition']==partition and r['reason']=='eligible']
    d.same(ids.tolist(),[r['clip_id'] for r in expected],partition+' ordered eligible IDs')
    d.same(y.tolist(),[r['dense_id'] for r in expected],partition+' dense labels')
    if len(set(ids.tolist()))!=len(ids): raise ValueError('duplicate IDs')
    if partition in ['fit','validation'] and set(y.tolist())!=set(range(50)): raise ValueError('all50 class support required')
    for a in values: a.flags.writeable=False
    return tuple(values)


def _read_bundle(bundle,admission,*,evidence_kind):
    """Metadata/provenance and fit/validation tensors only, never raw/test contents."""
    if evidence_kind not in ['source_video','synthetic_in_process']: raise ValueError('invalid provenance')
    bundle=d.safe_path(bundle,must_exist=True); admission=d.safe_path(admission,must_exist=True)
    if any(os.path.lexists(bundle/n) for n in ['failure.json','incomplete.json']): raise ValueError('failed/incomplete dataset')
    a=_json(admission)
    if type(a) is not dict or set(a)!=ADMISSION_KEYS: raise ValueError('exact face admission schema required')
    d.same(a['schema_version'],1,'admission schema')
    d.same(a['status'],'accepted_face_dataset_for_training' if evidence_kind=='source_video' else 'synthetic_fixture_only','admission status')
    d.same(a['purpose'],'face_fit_validation_only','admission purpose')
    d.same(a['bundle'],str(bundle),'exact admitted bundle')
    d.same(a['tensor_contract'],FEATURE,'admitted feature')
    for key in ['data_manifest_sha256','dataset_acceptance_sha256','campaign_manifest_sha256','graph_sha256']:
        d.hash_value(a[key],key)
    d.same(d.sha256(bundle/'data_manifest.json'),a['data_manifest_sha256'],'admitted manifest')
    acceptance=d.safe_path(a['dataset_acceptance'],must_exist=True)
    d.same(d.sha256(acceptance),a['dataset_acceptance_sha256'],'parent dataset acceptance digest')
    accepted=_json(acceptance)
    if type(accepted) is not dict: raise ValueError('parent dataset acceptance object required')
    for key,value in dict(schema_version=1,bundle=str(bundle),data_manifest_sha256=a['data_manifest_sha256'],
            status='accepted_bounded_face_inclusive_dataset' if evidence_kind=='source_video' else 'synthetic_fixture_only',
            classes=50,tensor_contract=FEATURE,training_qualified=False,live_ready=False,model_evaluated=False,
            spec_compliant=True,quality_approved=True).items():
        d.same(accepted.get(key),value,'parent acceptance '+key)
    if evidence_kind=='source_video':
        d.same(str(bundle),str(ACCEPTED_BUNDLE),'approved face bundle')
        d.same(a['data_manifest_sha256'],ACCEPTED_MANIFEST,'approved face manifest')
        d.same(str(acceptance),str(ACCEPTANCE),'approved parent acceptance')
    m=_json(bundle/'data_manifest.json')
    attempt_keys={'schema_version','feature_version','mode','campaign','campaign_manifest_sha256','graph','implementation','evidence_kind'}
    if type(m) is not dict or set(m)!=attempt_keys|{'status','tensor_contract','training_qualified','live_ready','model_evaluated','classes','eligibility','artifacts','augmentation'}:
        raise ValueError('exact face manifest schema required')
    for key,value in dict(schema_version=1,feature_version='hm1588-v1',mode='full',status='complete',
            tensor_contract=FEATURE,training_qualified=False,live_ready=False,model_evaluated=False,
            augmentation='none',evidence_kind=evidence_kind).items(): d.same(m.get(key),value,'face manifest '+key)
    d.same(m['implementation'],fd.implementation_binding(),'current face producer implementation')
    d.same(a['implementation'],m['implementation'],'admitted implementation')
    for name in [fd.CONTRACT,'training/holistic_migration/face_dataset.py','training/holistic_migration/face_features.py']:
        d.same(accepted['code_hashes'][name],m['implementation'][name],'accepted producer '+name)
    names={'FEATURES_FACE.md','selected_ids.json','attempt.json','class_metadata.json','capture_rows.json','eligibility.json','ineligible.json'}
    names|={f'{prefix}_{p}.npy' for p in d.PARTITIONS for prefix in ['X','y','clip_ids']}
    if type(m['artifacts']) is not dict or set(m['artifacts'])!=names: raise ValueError('exact face artifact names required')
    for name,record in m['artifacts'].items():
        keys={'sha256','shape','dtype'} if name.endswith('.npy') else {'sha256'}
        if type(record) is not dict or set(record)!=keys: raise ValueError('invalid artifact record')
        d.hash_value(record['sha256'],name)
        if name.endswith('.npy'):
            shape=record['shape']
            if type(shape) is not list or not shape or any(type(v) is not int or v<0 for v in shape): raise ValueError('invalid shape metadata')
            if name.startswith('X_') and (shape[1:]!=[30,1588] or record['dtype']!='float32'): raise ValueError('fixed face dimensions/dtype')
            if name.startswith('y_') and (len(shape)!=1 or record['dtype']!='int64'): raise ValueError('int64 label metadata')
            if name.startswith('clip_ids_') and (len(shape)!=1 or type(record['dtype']) is not str or np.dtype(record['dtype']).kind!='U'): raise ValueError('Unicode metadata')
    metadata={n:_json(_artifact(bundle,m,n)) for n in names if n.endswith('.json')}
    _artifact(bundle,m,'FEATURES_FACE.md')
    d.same(m['artifacts']['FEATURES_FACE.md']['sha256'],m['implementation'][fd.CONTRACT],'copied face contract')
    d.same(metadata['attempt.json'],{k:m[k] for k in attempt_keys},'face builder attempt')
    graph=m['graph']
    d.same(d.canonical_hash(graph),a['graph_sha256'],'admitted source graph')
    d.same(graph['contract'],d.contract_binding(),'current historical producer contract')
    d.same(graph['contract_sha256'],d.canonical_hash(graph['contract']),'producer contract digest')
    d.same(graph['runtime'],d.runtime_binding(),'current producer runtime')
    d.same(graph['runtime_sha256'],d.canonical_hash(graph['runtime']),'producer runtime digest')
    for name,digest in graph['bindings'].items():
        d.hash_value(digest,'graph '+name)
        d.same(d.sha256(d.safe_path(graph['paths'][name],must_exist=True)),digest,'current graph '+name)
    class_path=d.safe_path(graph['paths']['classes'],must_exist=True)
    if evidence_kind=='source_video':
        d.same(graph['bindings']['classes'],'e8089f5c0186bfe6fd9ec63a5150f8094645c1686509f23c1716453b5f9ce0d5','approved literal class map')
    classes=[dict(dense_id=i,original_id=c['id'],label=c['label'],category=c['category']) for i,c in enumerate(_json(class_path)['selected'])]
    for value in [a['classes'],m['classes'],graph['classes'],metadata['class_metadata.json']]: d.same(value,classes,'ordered dense/original/literal50')
    campaign=d.safe_path(m['campaign'],must_exist=True)
    if any(os.path.lexists(campaign/n) for n in ['failure.json','incomplete.json']): raise ValueError('failed/incomplete source campaign')
    campaign_hash=d.sha256(campaign/'extraction_manifest.json')
    d.same(campaign_hash,m['campaign_manifest_sha256'],'current campaign'); d.same(campaign_hash,a['campaign_manifest_sha256'],'admitted campaign')
    source=_json(campaign/'extraction_manifest.json')
    for k,v in dict(schema_version=1,status='complete',evidence_kind=evidence_kind,full_campaign_qualification=True,graph=graph).items(): d.same(source.get(k),v,'campaign '+k)
    for name,key in [('rows.jsonl','rows_sha256'),('attempt.json','attempt_sha256'),('selected_ids.json','selected_ids_sha256')]:
        d.same(d.sha256(campaign/name),source[key],'campaign ledger '+name)
    with (campaign/'rows.jsonl').open(encoding='utf-8') as stream:
        source_rows=[_json_line(line) for line in stream]
    membership=_json(Path(graph['paths']['partition_manifest']))['rows']
    d.index_rows(membership,'membership',True)
    d.same([r['clip_id'] for r in source_rows],sorted(r['clip_id'] for r in membership),'source declared coverage/order')
    d.same(metadata['selected_ids.json'],[r['clip_id'] for r in source_rows],'full ordered selection')
    captures=metadata['capture_rows.json']
    d.same([r['clip_id'] for r in captures],[r['clip_id'] for r in source_rows],'capture declared coverage/order')
    by_id={r['clip_id']:r for r in membership}
    for r,s in zip(captures,source_rows):
        expected_keys=set(s)|{'observation_count','hand_count','start_ms','end_ms','source_observation_count',
            'source_start_ms','source_end_ms','reason','presence','face_cardinality','face_missing','derived_row_count'}
        if type(r) is not dict or set(r)!=expected_keys: raise ValueError('exact capture schema required')
        original=by_id[r['clip_id']]
        for key in d.BYTE_IDENTITY+('partition',):
            d.same(s[key],original[key],'source original '+key); d.same(r[key],s[key],'capture source '+key)
        for key in ['raw_file','raw_sha256','decoded_frames','decoded_bgr_sha256','capture']: d.same(r[key],s[key],'capture provenance '+key)
        dense=d.integer(r['dense_id'],'dense_id')
        if dense>=50 or r['partition'] not in d.PARTITIONS: raise ValueError('invalid capture label/partition')
        d.same(r['label'],classes[dense]['label'],'literal capture label'); d.same(r['original_id'],classes[dense]['original_id'],'original capture label')
        if (r['official_split']=='test')!=(r['partition']=='test'): raise ValueError('test split leakage')
        _capture_metadata(r)
    calculated=fd.eligibility_summary(classes,captures)
    d.same(metadata['eligibility.json'],calculated,'eligibility readback'); d.same(m['eligibility'],calculated,'manifest eligibility')
    d.same(metadata['ineligible.json'],[r for r in captures if r['status']=='ineligible'],'exclusion ledger')
    d.same(accepted['partitions'],calculated['partitions'],'parent accepted denominators')
    for key in ['declared','eligible','ineligible']: d.same(accepted[key],sum(p[key] for p in calculated['partitions'].values()),'accepted '+key)
    arrays={p:_partition(bundle,m,captures,p) for p in ['fit','validation']}
    identity=dict(bundle=str(bundle),admission=str(admission),admission_sha256=d.sha256(admission),
        data_manifest_sha256=a['data_manifest_sha256'],dataset_acceptance=str(acceptance),dataset_acceptance_sha256=a['dataset_acceptance_sha256'],
        campaign_manifest_sha256=campaign_hash,implementation=m['implementation'],graph_sha256=a['graph_sha256'],classes_sha256=d.canonical_hash(classes),feature=FEATURE)
    return AdmittedData(bundle,admission,m,captures,arrays,identity,evidence_kind)


def _json_line(line):
    import json
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result: raise ValueError('duplicate source row key')
            result[key]=value
        return result
    def invalid(value): raise ValueError('nonfinite source row')
    return json.loads(line,object_pairs_hook=unique,parse_constant=invalid)


def _capture_metadata(r):
    reasons=['eligible','no_hands','too_few_observations','too_few_hand_observations','too_short','too_long','observation_gap','invalid_pose','invalid_face']
    if r['reason'] not in reasons: raise ValueError('invalid eligibility reason')
    d.same(r['status'],'eligible' if r['reason']=='eligible' else 'ineligible','capture status')
    d.same(r['derived_row_count'],30 if r['reason']=='eligible' else 0,'derived rows')
    for key in ['observation_count','hand_count','source_observation_count','face_missing','decoded_frames']: d.integer(r[key],key)
    if not 0<=r['hand_count']<=r['observation_count']<=r['source_observation_count']: raise ValueError('inconsistent capture counts')
    for key in ['start_ms','end_ms','source_start_ms','source_end_ms']:
        if r[key] is not None: d.integer(r[key],key)
    for key in ['pose','left_hand','right_hand','face']:
        count=d.integer(r['presence'][key],'presence '+key)
        if count>r['source_observation_count']: raise ValueError('presence exceeds observations')
    if type(r['face_cardinality']) is not dict: raise ValueError('invalid face cardinality ledger')
    if any(k!='478' or type(v) is not int or v<0 for k,v in r['face_cardinality'].items()): raise ValueError('invalid face cardinality')
    d.same(sum(r['face_cardinality'].values()),r['presence']['face'],'face cardinality count')
    d.same(r['face_missing']+r['presence']['face'],r['source_observation_count'],'face presence total')
    d.hash_value(r['raw_sha256'],'raw'); d.hash_value(r['decoded_bgr_sha256'],'decoded')
    raw=Path(r['raw_file'])
    if raw.is_absolute() or raw.parts[:1]!=('raw',) or '..' in raw.parts or raw.suffix!='.npz': raise ValueError('invalid raw path')
    if r['reason']=='eligible' and (r['observation_count']<8 or r['hand_count']<4 or r['start_ms'] is None or r['end_ms'] is None
            or not 400<=r['end_ms']-r['start_ms']<=5000): raise ValueError('eligible capture bounds invalid')


def read_admitted(bundle,admission):
    return _read_bundle(bundle,admission,evidence_kind='source_video')

from .evaluate import _publish_json
from . import batchnorm_calibration as bc

import hashlib
import importlib.metadata
import os
import sys

FAMILY=dict(seed=SEED,input=[30,1588],outputs=50,conv=[64,128],kernel=3,padding='same',
            batch_norm=True,pool=2,lstm=[128,64],dense=128,dropout=.4,
            optimizer='Adam',learning_rate=.001,loss='sparse_categorical_crossentropy',
            tiny_max_epochs=300,full_max_epochs=120,batch_size=32,
            early_stopping=dict(monitor='val_accuracy',mode='max',patience=15),
            reduce_lr=dict(monitor='val_loss',mode='min',patience=6,factor=.5),
            selection='best_validation_accuracy_earliest_exact_tie',rotation_degrees=5)
POLICY=dict(schema_version=1,decision='closed_set_argmax',outputs=50,
            unknown_rejection='unmeasured_no_observed_validation_negatives',live_ready=False)


def source_binding():
    return {name:d.sha256(Path(__file__).parent/name) for name in ['face_train.py','batchnorm_calibration.py','face_evaluate.py','face_augmentation.py','augmentation.py','face_features.py','face_dataset.py','train.py','evaluate.py','dataset.py']}


def training_runtime():
    import platform
    return dict(python=sys.version,executable=str(Path(sys.executable).absolute()),host=platform.platform(),
                threads={k:os.environ.get(k) for k in ['OMP_NUM_THREADS','TF_NUM_INTRAOP_THREADS','TF_NUM_INTEROP_THREADS','OPENBLAS_NUM_THREADS','VECLIB_MAXIMUM_THREADS']},
                packages={p:importlib.metadata.version(p) for p in ['numpy','tensorflow','keras']})


def _identity(data):
    return dict(dataset=data.identity,provenance=data.provenance,sources=source_binding(),
                runtime=training_runtime(),family=FAMILY,classes=data.manifest['classes'],feature=FEATURE)


def _array_digest(a):
    return dict(shape=list(a.shape),dtype=str(a.dtype),sha256=hashlib.sha256(a.tobytes(order='C')).hexdigest())


def tiny_selection(data):
    x,y,ids=data.arrays['fit']
    indices=[min((j for j in range(len(ids)) if y[j]==i),key=lambda j:str(ids[j])) for i in range(8)]
    return x[indices],y[indices],ids[indices]


def _selected_identity(values):
    x,y,ids=values
    return dict(ids=ids.tolist(),X=_array_digest(x),y=_array_digest(y))


def _output_path(output,data):
    output=d.safe_path(output)
    roots=[d.REPO.parent/'holistic-migration-data/evidence/phase-4-20261116']
    if data.provenance=='synthetic_in_process': roots.append(Path.home()/'.hermes/cache/scratch')
    if not any(root in output.parents for root in roots): raise ValueError('output must be in approved evidence/scratch')
    for source in [data.bundle,Path(data.manifest['campaign']),data.admission,Path(data.identity['dataset_acceptance'])]+[Path(v) for v in data.manifest['graph']['paths'].values()]:
        if output==source or source in output.parents or output in source.parents:
            raise ValueError('output overlaps input')
    if output.exists() or not output.parent.is_dir(): raise ValueError('output must be fresh with existing parent')
    return output


def _reserve(output,data):
    output=_output_path(output,data)
    output.mkdir()
    return output


def _save_array(path,value):
    with Path(path).open('xb') as stream: np.save(stream,value,allow_pickle=False)
    actual=np.load(path,allow_pickle=False)
    if actual.dtype!=value.dtype or not np.array_equal(actual,value): raise ValueError('array publication readback failed')
    return d.sha256(path)


def _predict(backend,model,x):
    from .evaluate import probabilities
    p=backend.predict(model,x)
    return probabilities(p,len(x))


def _loss(y,p):
    if not len(y): return None
    return float(-np.log(np.clip(p[np.arange(len(y)),y].astype(np.float64),1e-300,1)).mean())


class TensorFlowBackend:
    """Bounded NumPy batches avoid implicit tf.data worker pools; no native import at construction."""
    def build(self): return build_model()
    def steps(self,model): return int(model.optimizer.iterations.numpy())
    def step(self,model,x,y):
        result=model.train_on_batch(x,y,return_dict=True)
        if not np.isfinite(list(result.values())).all(): raise ValueError('nonfinite optimizer result')
    def predict(self,model,x):
        return np.concatenate([model(x[i:i+32],training=False).numpy() for i in range(0,len(x),32)]) if len(x) else np.empty((0,50),np.float32)
    def save(self,model,path): model.save(path)
    def load(self,path):
        import tensorflow as tf
        model=tf.keras.models.load_model(path)
        if model.input_shape!=(None,30,1588) or model.output_shape!=(None,50) or model.count_params()!=526194:
            raise ValueError('checkpoint architecture mismatch')
        return model


def _recheck(data,identity):
    d.same(_identity(data),identity,'frozen source/runtime/dataset identity')
    for name in ['data_manifest.json']:
        d.same(d.sha256(data.bundle/name),data.identity['data_manifest_sha256'],'data identity readback')
    d.same(d.sha256(data.admission),data.identity['admission_sha256'],'admission readback')
    d.same(d.sha256(data.identity['dataset_acceptance']),data.identity['dataset_acceptance_sha256'],'parent dataset acceptance readback')
    reread=_read_bundle(data.bundle,data.admission,evidence_kind=data.provenance)
    d.same(reread.identity,data.identity,'current dataset provenance')
    d.same(d.sha256(Path(data.manifest['campaign'])/'extraction_manifest.json'),data.identity['campaign_manifest_sha256'],'campaign readback')
    for name in data.manifest['artifacts']:
        if name.endswith('_test.npy'): continue
        _artifact(data.bundle,data.manifest,name)


def _freeze_model(backend,model,output,x,expected):
    candidate=output/'candidate.keras'
    backend.save(model,candidate)
    loaded=backend.load(candidate)
    p=_predict(backend,loaded,x)
    if not np.allclose(p,expected,rtol=1e-6,atol=1e-7): raise ValueError('checkpoint reload predictions differ')
    expected_hash=d.sha256(candidate)
    os.link(candidate,output/'model.keras')
    d.same(d.sha256(output/'model.keras'),expected_hash,'exclusive checkpoint readback')
    return loaded,p


def _batch_independent(backend,model,x,p):
    singles=np.concatenate([_predict(backend,model,row[None]) for row in x])
    if not np.allclose(singles,p,rtol=1e-6,atol=1e-7):
        raise ValueError('tiny inference depends on batch composition')


def _files(output,names):
    return {name:d.sha256(output/name) for name in names}


def _training_failure(output,exc,backend,model,history,*,selection_disposition=None):
    # Preserve completed epochs even when interrupted mid-batch; don't invent unknown steps.
    try: steps=backend.steps(model) if model is not None else 0
    except Exception: steps=None
    try:
        if not (output/'history.json').exists(): d.write_json(output/'history.json',history)
    except Exception:
        pass  # History diagnostics must not replace the primary or prevent failure disposition.
    try:
        if not (output/'failure.json').exists():
            failure=dict(status='failed',error=type(exc).__name__,detail=str(exc),
                         actual_epochs=len(history),optimizer_steps=steps)
            if selection_disposition is not None: failure['selection_disposition']=selection_disposition
            d.write_json(output/'failure.json',failure)
    except Exception:
        pass  # Preserve the original training/publication exception when diagnostics also fail.


def _execute(data,mode,output,*,tiny_proof=None,_backend=None,_epochs=None):
    if mode=='fit': return _full_execute(data,output,tiny_proof=tiny_proof,_backend=_backend,_epochs=_epochs)
    if mode!='tiny-fit': raise ValueError('unsupported operation')
    if data.provenance!='synthetic_in_process' and (_backend is not None or _epochs is not None):
        raise ValueError('trusted seams are synthetic-only')
    epochs=300 if _epochs is None else _epochs
    if type(epochs) is not int or not 1<=epochs<=300: raise ValueError('invalid epoch budget')
    selected=tiny_selection(data)
    identity=_identity(data)
    config=dict(schema_version=1,operation=mode,family=FAMILY,max_epochs=epochs,batch_size=8,
                selected=_selected_identity(selected),augmentation='none',calibration_protocol=bc.PROTOCOL)
    output=_reserve(output,data)
    d.write_json(output/'start.json',dict(schema_version=1,status='started',identity=identity,config_sha256=d.canonical_hash(config)))
    d.write_json(output/'config.json',config)
    backend=TensorFlowBackend() if _backend is None else _backend
    model=None; history=[]
    try:
        model=backend.build(); x,y,ids=selected; history=[]
        for epoch in range(epochs):
            backend.step(model,x,y)
            p=_predict(backend,model,x)
            correct=int((np.argmax(p,axis=1)==y).sum()); loss=_loss(y,p)
            history.append(dict(epoch=epoch+1,optimizer_steps=backend.steps(model),correct=correct,mean_crossentropy=loss))
            if correct==8 and loss<=.1: break
        d.write_json(output/'history.json',history)
        # History is optimizer-only inference. Calibration is one distinct fit-only operation.
        _save_array(output/'pre_calibration_probabilities.npy',p)
        pre=dict(correct=int((p.argmax(axis=1)==y).sum()),mean_crossentropy=_loss(y,p))
        native=isinstance(backend,TensorFlowBackend)
        if not native and data.provenance!='synthetic_in_process':
            raise ValueError('calibration no-op is synthetic-only')
        receipt=dict(schema_version=1,protocol=bc.PROTOCOL,selected=_selected_identity(selected),
                     sources=source_binding(),optimizer_steps=backend.steps(model),pre_calibration=pre,
                     pre_probabilities_sha256=d.sha256(output/'pre_calibration_probabilities.npy'),
                     kind='native_frozen_fit_moments' if native else 'synthetic_lifecycle_only_no_calibration',
                     native=bc.calibrate(model,x) if native else None)
        p=_predict(backend,model,x)
        loaded,p=_freeze_model(backend,model,output,x,p)
        _batch_independent(backend,loaded,x,p)
        receipt['model_sha256']=d.sha256(output/'model.keras')
        if native: bc.verify_precalibration(loaded,x,receipt['native'],np.load(output/'pre_calibration_probabilities.npy',allow_pickle=False))
        d.write_json(output/'batchnorm-calibration.json',receipt)
        _save_array(output/'selected_probabilities.npy',p)
        _save_array(output/'selected_ids.npy',ids)
        _save_array(output/'selected_X.npy',x); _save_array(output/'selected_y.npy',y)
        correct=int((np.argmax(p,axis=1)==y).sum()); loss=_loss(y,p)
        _verify_calibration(output,data,backend,loaded,selected,history)
        _recheck(data,identity)
        if correct!=8 or loss>.1: raise ValueError('tiny memorization criterion not reached')
        proof=dict(schema_version=1,status='tiny_proven',provenance=data.provenance,identity=identity,calibration_protocol=bc.PROTOCOL,
                   selected_ids=ids.tolist(),selected_tensors=_selected_identity(selected),
                   correct=correct,mean_crossentropy=loss,actual_epochs=len(history),optimizer_steps=backend.steps(model),
                   files=_files(output,['start.json','config.json','history.json','model.keras','selected_probabilities.npy','selected_ids.npy','selected_X.npy','selected_y.npy','batchnorm-calibration.json','pre_calibration_probabilities.npy']))
        _publish_json(output/'tiny-proof.json',proof)
        return proof
    except BaseException as exc:
        _training_failure(output,exc,backend,model,history)
        raise


def _verify_calibration(output,data,backend,model,selected,history):
    receipt=_json(output/'batchnorm-calibration.json')
    keys={'schema_version','protocol','selected','sources','optimizer_steps','pre_calibration',
          'pre_probabilities_sha256','kind','native','model_sha256'}
    if type(receipt) is not dict or set(receipt)!=keys: raise ValueError('exact tiny calibration receipt required')
    for key,value in dict(schema_version=1,protocol=bc.PROTOCOL,selected=_selected_identity(selected),
                          sources=source_binding(),optimizer_steps=backend.steps(model),
                          model_sha256=d.sha256(output/'model.keras'),
                          pre_probabilities_sha256=d.sha256(output/'pre_calibration_probabilities.npy')).items():
        d.same(receipt[key],value,'tiny calibration '+key)
    from .evaluate import probabilities
    x,y,_=selected
    pre=probabilities(np.load(output/'pre_calibration_probabilities.npy',allow_pickle=False),len(x))
    metric=dict(correct=int((pre.argmax(axis=1)==y).sum()),mean_crossentropy=_loss(y,pre))
    d.same(receipt['pre_calibration'],metric,'pre-calibration metrics')
    for key in ['correct','mean_crossentropy']:
        d.same(history[-1][key],metric[key],'optimizer-only final history '+key)
    d.same(receipt['optimizer_steps'],history[-1]['optimizer_steps'],'calibration no optimizer step')
    if isinstance(backend,TensorFlowBackend):
        d.same(receipt['kind'],'native_frozen_fit_moments','native calibration required')
        bc.verify_precalibration(model,x,receipt['native'],pre)
    else:
        if data.provenance!='synthetic_in_process': raise ValueError('calibration fixture is synthetic-only')
        d.same(receipt['kind'],'synthetic_lifecycle_only_no_calibration','explicit synthetic receipt')
        d.same(receipt['native'],None,'synthetic fixture has no native calibration')
    return receipt


def _verify_tiny(path,data,*,_backend=None):
    path=d.safe_path(path,must_exist=True)
    if path.name!='tiny-proof.json': raise ValueError('retained tiny-proof.json required')
    if data.provenance!='synthetic_in_process' and _backend is not None: raise ValueError('synthetic backend forbidden')
    output=path.parent
    if any(os.path.lexists(output/n) for n in ['failure.json','incomplete.json']):
        raise ValueError('failed/incomplete tiny attempt cannot qualify a full fit')
    proof=_json(path)
    if type(proof) is not dict: raise ValueError('tiny proof must be an object')
    d.same(proof.get('schema_version'),1,'tiny proof schema')
    d.same(proof.get('status'),'tiny_proven','tiny status')
    d.same(proof.get('calibration_protocol'),bc.PROTOCOL,'tiny proof calibration protocol')
    d.same(proof.get('provenance'),data.provenance,'tiny provenance')
    d.same(proof['identity'],_identity(data),'tiny current identities')
    selected=tiny_selection(data)
    d.same(proof['selected_tensors'],_selected_identity(selected),'exact tiny tensors/IDs')
    d.same(proof['selected_ids'],selected[2].tolist(),'literal first dense0..7')
    names=['start.json','config.json','history.json','model.keras','selected_probabilities.npy','selected_ids.npy','selected_X.npy','selected_y.npy','batchnorm-calibration.json','pre_calibration_probabilities.npy']
    if set(proof['files'])!=set(names): raise ValueError('exact retained tiny artifacts required')
    for name in names: d.same(d.sha256(output/name),proof['files'][name],'tiny '+name)
    config=_json(output/'config.json'); start=_json(output/'start.json')
    history=_json(output/'history.json')
    if type(history) is not list or not 1<=len(history)<=300: raise ValueError('invalid tiny history')
    d.same(proof['actual_epochs'],len(history),'actual tiny epochs')
    d.integer(proof['optimizer_steps'],'actual tiny steps',1)
    for i,row in enumerate(history):
        d.same(row['epoch'],i+1,'history epoch')
        d.same(row['optimizer_steps'],i+1,'history optimizer step')
    d.same(proof['optimizer_steps'],history[-1]['optimizer_steps'],'tiny history steps')
    d.same(config['schema_version'],1,'tiny config schema')
    d.same(config['batch_size'],8,'tiny fixed batch')
    d.integer(config['max_epochs'],'tiny maximum epochs',1)
    if not len(history)<=config['max_epochs']<=300: raise ValueError('tiny budget inconsistent')
    d.same(start,dict(schema_version=1,status='started',identity=_identity(data),config_sha256=d.canonical_hash(config)),'tiny frozen start')
    d.same(config['family'],FAMILY,'tiny config family')
    d.same(config['operation'],'tiny-fit','tiny operation')
    d.same(config['selected'],_selected_identity(selected),'tiny selected config')
    d.same(config['augmentation'],'none','tiny unaugmented')
    d.same(config.get('calibration_protocol'),bc.PROTOCOL,'tiny config calibration protocol')
    if data.provenance=='source_video': d.same(config['max_epochs'],300,'real tiny fixed budget')
    backend=TensorFlowBackend() if _backend is None else _backend
    model=backend.load(output/'model.keras'); x,y,ids=selected
    _verify_calibration(output,data,backend,model,selected,history)
    p=_predict(backend,model,x)
    _batch_independent(backend,model,x,p)
    recorded=np.load(output/'selected_probabilities.npy',allow_pickle=False)
    if not np.allclose(p,recorded,rtol=1e-6,atol=1e-7): raise ValueError('tiny predictions changed')
    if not np.array_equal(np.load(output/'selected_X.npy',allow_pickle=False).view(np.uint32),x.view(np.uint32)): raise ValueError('saved tiny tensors changed')
    d.same(np.load(output/'selected_y.npy',allow_pickle=False).tolist(),y.tolist(),'tiny saved labels')
    d.same(np.load(output/'selected_ids.npy',allow_pickle=False).tolist(),ids.tolist(),'tiny saved IDs')
    correct=int((p.argmax(axis=1)==y).sum()); loss=_loss(y,p)
    if correct!=8 or loss>.1: raise ValueError('retained tiny fails8/8 and CE<=.1')
    d.same(proof['correct'],correct,'tiny correct readback')
    if abs(proof['mean_crossentropy']-loss)>1e-7: raise ValueError('tiny loss readback')
    d.same(proof['optimizer_steps'],backend.steps(model),'tiny actual steps')
    return proof


def verify_real_tiny(path,data):
    if data.provenance!='source_video': raise ValueError('real source tiny proof required')
    return _verify_tiny(path,data)

def _callbacks(backend,model,validation):
    if not isinstance(backend,TensorFlowBackend): return backend.callbacks(model)
    import tensorflow as tf
    callbacks=[tf.keras.callbacks.EarlyStopping(monitor='val_accuracy',mode='max',patience=15),
               tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss',mode='min',patience=6,factor=.5)]
    for cb in callbacks:
        cb.set_model(model)
        cb.set_params(dict(epochs=120,steps=None,verbose=0,validation_data=validation))
    return callbacks


def _full_execute(data,output,*,tiny_proof,_backend=None,_epochs=None):
    if data.provenance!='synthetic_in_process' and (_backend is not None or _epochs is not None):
        raise ValueError('trusted seams are synthetic-only')
    if tiny_proof is None: raise ValueError('retained real tiny proof is mandatory')
    # Proof readback (including reloaded inference on fit-only tiny inputs) precedes a new fit/run.
    _output_path(output,data)
    proof=_verify_tiny(tiny_proof,data,_backend=_backend)
    epochs=120 if _epochs is None else _epochs
    if type(epochs) is not int or not 1<=epochs<=120: raise ValueError('invalid full budget')
    identity=_identity(data); x,y,ids=data.arrays['fit']; vx,vy,vids=data.arrays['validation']
    rotated,augmentation=rotate_fit(x,ids.tolist(),partition='fit',seed=SEED)
    config=dict(schema_version=1,operation='fit',family=FAMILY,max_epochs=epochs,batch_size=32,
                selected=_selected_identity(data.arrays['fit']),validation=_selected_identity(data.arrays['validation']),
                augmentation=augmentation,tiny_proof=str(Path(tiny_proof)),tiny_proof_sha256=d.sha256(tiny_proof))
    output=_reserve(output,data)
    d.write_json(output/'start.json',dict(schema_version=1,status='started',identity=identity,config_sha256=d.canonical_hash(config)))
    d.write_json(output/'config.json',config); d.write_json(output/'policy.json',POLICY)
    d.write_json(output/'augmentation.json',augmentation)
    backend=TensorFlowBackend() if _backend is None else _backend
    model=None; history=[]
    selection_disposition=dict(schema_version=1,phase='selection',frozen=False,identity=identity)
    try:
        model=backend.build()  # deliberately fresh; the tiny checkpoint is never reused as initialization
        tx=np.concatenate([x,rotated]); ty=np.concatenate([y,y])
        callbacks=_callbacks(backend,model,(vx,vy))
        for cb in callbacks: cb.on_train_begin({})
        rng=np.random.default_rng(SEED); best=-1; best_epoch=None; best_p=None; history=[]
        for epoch in range(epochs):
            for cb in callbacks: cb.on_epoch_begin(epoch,{})
            order=rng.permutation(len(tx))
            for offset in range(0,len(order),32):
                batch=order[offset:offset+32]; backend.step(model,tx[batch],ty[batch])
            vp=_predict(backend,model,vx)
            tp=_predict(backend,model,tx)
            logs=dict(loss=_loss(ty,tp),accuracy=float((tp.argmax(axis=1)==ty).mean()),val_accuracy=float((vp.argmax(axis=1)==vy).mean()),val_loss=_loss(vy,vp))
            history.append(dict(epoch=epoch+1,optimizer_steps=backend.steps(model),**logs))
            if logs['val_accuracy']>best:
                best=logs['val_accuracy']; best_epoch=epoch+1; best_p=vp.copy()
                backend.save(model,output/'candidate.keras')
            for cb in callbacks: cb.on_epoch_end(epoch,logs)
            if getattr(model,'stop_training',False): break
        for cb in callbacks: cb.on_train_end(history[-1])
        d.write_json(output/'history.json',history)
        selected_model=backend.load(output/'candidate.keras')
        vp=_predict(backend,selected_model,vx)
        if not np.allclose(vp,best_p,rtol=1e-6,atol=1e-7): raise ValueError('best checkpoint reload mismatch')
        digest=d.sha256(output/'candidate.keras'); os.link(output/'candidate.keras',output/'model.keras')
        d.same(d.sha256(output/'model.keras'),digest,'frozen full checkpoint')
        _save_array(output/'validation_probabilities.npy',vp); _save_array(output/'validation_ids.npy',vids)
        _recheck(data,identity)
        selection=dict(schema_version=1,status='frozen_validation_selection',provenance=data.provenance,identity=identity,
                       policy=POLICY,best_epoch=best_epoch,best_val_accuracy=best,actual_epochs=len(history),
                       optimizer_steps=backend.steps(model),selected_checkpoint_steps=backend.steps(selected_model),
                       files=_files(output,['start.json','config.json','policy.json','augmentation.json','history.json','model.keras','validation_probabilities.npy','validation_ids.npy']))
        _publish_json(output/'selection.json',selection)
        # An affirmative disposition is emitted only after selection publication returned.
        _publish_json(output/'selection-disposition.json',dict(schema_version=1,status='selection_frozen',
                      identity=identity,selection_sha256=d.sha256(output/'selection.json')))
        selection_disposition=dict(schema_version=1,phase='fit_reports',frozen=True,identity=identity)
        # Selection is already frozen. Reporting failure must not erase it or claim complete reports.
        from .face_evaluate import metrics
        for partition,values,p in [('fit',data.arrays['fit'],None),('validation',data.arrays['validation'],vp)]:
            rx,ry,rids=values
            if p is None: p=_predict(backend,selected_model,rx)
            if partition=='fit':
                _save_array(output/'fit_probabilities.npy',p); _save_array(output/'fit_ids.npy',rids)
            report=metrics(ry,p,rids.tolist(),data.manifest['classes'],data.captures,partition=partition)
            _publish_json(output/f'{partition}-report.json',report)
        _publish_json(output/'complete.json',dict(schema_version=1,status='fit_reports_complete',selection_sha256=d.sha256(output/'selection.json'),
                       files=_files(output,['fit_probabilities.npy','fit_ids.npy','fit-report.json','validation-report.json'])))
        return selection
    except BaseException as exc:
        _training_failure(output,exc,backend,model,history,selection_disposition=selection_disposition)
        raise



def main(argv=None):
    import argparse
    parser=argparse.ArgumentParser(description='Isolated admitted hm1588 training; no synthetic CLI bypass')
    commands=parser.add_subparsers(dest='operation',required=True)
    for mode in ['tiny-fit','fit']:
        command=commands.add_parser(mode)
        command.add_argument('--bundle',required=True)
        command.add_argument('--admission',required=True)
        command.add_argument('--output',required=True)
        if mode=='fit': command.add_argument('--tiny-proof',required=True)
    args=parser.parse_args(argv)
    try:
        d.safe_path(args.output)
        data=read_admitted(args.bundle,args.admission)
        result=_execute(data,args.operation,args.output,tiny_proof=getattr(args,'tiny_proof',None))
        print(result['status'])
        return 0
    except (ValueError,OSError,KeyError,TypeError) as exc:
        parser.error(str(exc))


if __name__=='__main__':
    raise SystemExit(main())




