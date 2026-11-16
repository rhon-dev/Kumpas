"""Separate frozen exploratory reused-test evaluation; never select/tune a model."""
import numpy as np
from . import dataset as d

NEGATIVE_STATUS='unmeasured_no_observed_validation_negatives'


def probabilities(p,n):
    if (type(p) is not np.ndarray or p.dtype.kind!='f' or p.shape!=(n,50)
            or not np.isfinite(p).all() or (p<0).any() or (p>1).any()
            or not np.allclose(p.sum(axis=1),1,atol=2e-6,rtol=0)):
        raise ValueError('invalid50 probability mapping/shape/finite/range/sum')
    return p


def metrics(y,p,ids,classes,captures,*,partition):
    probabilities(p,len(ids))
    if type(classes) is not list or len(classes)!=50: raise ValueError('all50 output classes required')
    for i,c in enumerate(classes):
        d.same(c['dense_id'],i,'canonical metric dense order')
        d.integer(c['original_id'],'original class ID')
        if not all(type(c[k]) is str and c[k] for k in ['label','category']): raise ValueError('literal classes required')
        if i and c['original_id']<=classes[i-1]['original_id']: raise ValueError('original class order mismatch')
    if len(set(ids))!=len(ids) or len({r['clip_id'] for r in captures})!=len(captures):
        raise ValueError('duplicate metric IDs')
    if type(y) is not np.ndarray or y.dtype!=np.int64 or y.shape!=(len(ids),) or ((y<0)|(y>=50)).any():
        raise ValueError('invalid metric labels')
    rows=[r for r in captures if r['partition']==partition]
    eligible=[r for r in rows if r['reason']=='eligible']
    d.same(list(ids),[r['clip_id'] for r in eligible],'metric ordered eligible IDs')
    d.same(y.tolist(),[r['dense_id'] for r in eligible],'metric dense mapping')
    prediction=np.argmax(p,axis=1)
    confusion=np.zeros((50,50),np.int64)
    np.add.at(confusion,(y,prediction),1)
    per=[]
    for i,c in enumerate(classes):
        tp=int(confusion[i,i]); support=int(confusion[i].sum()); predicted=int(confusion[:,i].sum())
        precision=tp/predicted if predicted else 0.0
        recall=tp/support if support else 0.0
        f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
        declared=sum(r['dense_id']==i for r in rows)
        per.append(dict(c,precision=precision,recall=recall,f1=f1,support=support,declared=declared,unknown_missing=declared-support))
    excluded=[dict(clip_id=r['clip_id'],dense_id=r['dense_id'],reason=r['reason']) for r in rows if r['reason']!='eligible']
    correct=int(np.trace(confusion))
    return dict(per_class=per,macro_f1=float(np.mean([r['f1'] for r in per])),confusion=confusion.tolist(),
                accuracy=correct/len(y) if len(y) else None,
                all_declared=dict(declared=len(rows),eligible=len(y),ineligible=len(excluded),unknown_missing=len(excluded),correct_eligible=correct),
                exclusions=excluded,zero_denominator='precision/recall/F1=0; empty accuracy=null; macro includes all50',
                false_accept_rate=None,safe_unknown_rate=None,negative_count=None,negative_status=NEGATIVE_STATUS,live_ready=False)


from pathlib import Path
import os


def _publish_json(path,value):
    """Evaluator-owned staged publication; cleanup must not replace readback failure."""
    path=Path(path)
    pending=path.with_name(path.name+'.pending')
    d.write_json(pending,value)
    expected=d.sha256(pending)
    os.link(pending,path)  # Exclusive; a preexisting destination is never ours to clean up.
    try:
        d.same(d.sha256(path),expected,'published manifest digest')
        d.same(d.load_json(path),value,'published manifest readback')
    except BaseException:
        try: path.unlink()  # Only this just-linked attempt; keep pending evidence.
        except OSError: pass  # Outer failure disposition also denies a residual marker.
        raise


def frozen_selection(run,data):
    from . import train as t
    run=d.safe_path(run,must_exist=True)
    if os.path.lexists(run/'failure.json'):
        failure=t._json(run/'failure.json')
        if type(failure) is not dict: raise ValueError('failed selection disposition required')
        d.same(failure.get('status'),'failed','selection failure status')
        d.same(failure.get('selection_disposition'),dict(schema_version=1,phase='fit_reports',
               frozen=True,identity=t._identity(data)),'selection failure disposition')
    disposition=t._json(run/'selection-disposition.json')
    d.same(disposition,dict(schema_version=1,status='selection_frozen',identity=t._identity(data),
                           selection_sha256=d.sha256(run/'selection.json')),'selection disposition')
    selection=t._json(run/'selection.json')
    if type(selection) is not dict: raise ValueError('frozen selection required')
    for key,value in dict(schema_version=1,status='frozen_validation_selection',provenance=data.provenance,identity=t._identity(data),policy=t.POLICY).items():
        d.same(selection.get(key),value,'frozen selection '+key)
    names=['start.json','config.json','policy.json','augmentation.json','history.json','model.keras','validation_probabilities.npy','validation_ids.npy']
    if set(selection['files'])!=set(names): raise ValueError('exact selection artifacts required')
    for name in names: d.same(d.sha256(run/name),selection['files'][name],'frozen '+name)
    config=t._json(run/'config.json')
    d.same(config['schema_version'],1,'frozen config schema')
    d.same(config['operation'],'fit','frozen full-fit operation')
    d.same(config['family'],t.FAMILY,'frozen architecture/configuration family')
    d.same(config['batch_size'],32,'frozen batch')
    d.same(config['selected'],t._selected_identity(data.arrays['fit']),'frozen fit examples')
    d.same(config['validation'],t._selected_identity(data.arrays['validation']),'frozen validation examples')
    d.same(t._json(run/'policy.json'),t.POLICY,'frozen closed-set policy')
    d.same(t._json(run/'augmentation.json'),config['augmentation'],'frozen augmentation')
    d.same(t._json(run/'start.json'),dict(schema_version=1,status='started',identity=t._identity(data),config_sha256=d.canonical_hash(config)),'frozen start')
    history=t._json(run/'history.json')
    if type(history) is not list or not 1<=len(history)<=120: raise ValueError('invalid full history')
    d.integer(config['max_epochs'],'full epoch maximum',1)
    if not len(history)<=config['max_epochs']<=120: raise ValueError('full epoch budget mismatch')
    if data.provenance=='source_video': d.same(config['max_epochs'],120,'real fixed full budget')
    for i,row in enumerate(history):
        d.same(row['epoch'],i+1,'full epoch')
        d.same(row['optimizer_steps'],(i+1)*int(np.ceil(2*len(data.arrays['fit'][0])/32)),'full optimizer steps')
        if type(row['val_accuracy']) is not float or not np.isfinite(row['val_accuracy']) or not 0<=row['val_accuracy']<=1:
            raise ValueError('invalid validation metric')
    best=max(history,key=lambda r:r['val_accuracy'])  # Python max retains earliest exact tie
    d.same(selection['best_epoch'],best['epoch'],'earliest validation best')
    d.same(selection['best_val_accuracy'],best['val_accuracy'],'best validation accuracy')
    d.same(selection['actual_epochs'],len(history),'actual full epochs')
    d.same(selection['optimizer_steps'],history[-1]['optimizer_steps'],'actual full steps')
    d.same(selection['selected_checkpoint_steps'],best['optimizer_steps'],'best checkpoint steps')
    return selection


def _evaluation_readback(output,start):
    from . import train as t
    if (output/'failure.json').exists() or not (output/'evaluation-complete.json').is_file():
        raise ValueError('existing failed/incomplete evaluation cannot rerun')
    complete=t._json(output/'evaluation-complete.json')
    d.same(complete.get('schema_version'),1,'evaluation schema')
    d.same(complete.get('status'),'exploratory_evaluation_complete','evaluation status')
    d.same(t._json(output/'evaluation-start.json'),start,'exact existing evaluation target')
    d.same(complete['start_sha256'],d.sha256(output/'evaluation-start.json'),'evaluation start digest')
    names=['report.json','probabilities.npy','predictions.npy','eligible_ids.npy','eligible_labels.npy']
    if set(complete['files'])!=set(names): raise ValueError('evaluation artifact coverage mismatch')
    for name in names: d.same(d.sha256(output/name),complete['files'][name],'completed evaluation '+name)
    return complete


def _evaluate(run,data,output,*,_backend=None):
    """Internal synthetic fixture seam. Production CLI supplies only admitted real data."""
    from . import train as t
    if data.provenance!='synthetic_in_process' and _backend is not None: raise ValueError('synthetic seam forbidden')
    run=d.safe_path(run,must_exist=True); output=d.safe_path(output)
    selection=frozen_selection(run,data)
    if run==output or run in output.parents or output in run.parents: raise ValueError('evaluation overlaps frozen run')
    start=dict(schema_version=1,status='evaluation_started',evaluation_kind='exploratory_reused_test',
               run=str(run),selection_sha256=d.sha256(run/'selection.json'),identity=t._identity(data),policy=t.POLICY)
    if output.exists(): return _evaluation_readback(output,start)
    output=t._reserve(output,data)
    d.write_json(output/'evaluation-start.json',start)
    backend=t.TensorFlowBackend() if _backend is None else _backend
    completion_published=False
    try:
        model=backend.load(run/'model.keras')
        vp=t._predict(backend,model,data.arrays['validation'][0])
        frozen=np.load(run/'validation_probabilities.npy',allow_pickle=False)
        probabilities(frozen,len(data.arrays['validation'][0]))
        if not np.allclose(vp,frozen,rtol=1e-6,atol=1e-7): raise ValueError('frozen validation checkpoint readback differs')
        d.same(np.load(run/'validation_ids.npy',allow_pickle=False).tolist(),data.arrays['validation'][2].tolist(),'frozen validation ID mapping')
        # First test array/hash access occurs only after exclusive, bound evaluation-start receipt.
        x,y,ids=t._partition(data.bundle,data.manifest,data.captures,'test')
        p=t._predict(backend,model,x)
        t._save_array(output/'probabilities.npy',p)
        t._save_array(output/'predictions.npy',p.argmax(axis=1).astype(np.int64))
        t._save_array(output/'eligible_ids.npy',ids); t._save_array(output/'eligible_labels.npy',y)
        report=metrics(y,p,ids.tolist(),data.manifest['classes'],data.captures,partition='test')
        report.update(evaluation_kind='exploratory_reused_test',fresh_untouched_holdout=False,
                      tuning_allowed=False,provenance=data.provenance,policy=t.POLICY)
        t._recheck(data,start['identity']); frozen_selection(run,data)
        for prefix in ['X','y','clip_ids']: t._artifact(data.bundle,data.manifest,f'{prefix}_test.npy')
        _publish_json(output/'report.json',report)
        complete=dict(schema_version=1,status='exploratory_evaluation_complete',start_sha256=d.sha256(output/'evaluation-start.json'),
                      files=t._files(output,['report.json','probabilities.npy','predictions.npy','eligible_ids.npy','eligible_labels.npy']))
        _publish_json(output/'evaluation-complete.json',complete)
        completion_published=True
        return _evaluation_readback(output,start)
    except BaseException as exc:
        # Existing completed-target readback is outside this owned new-attempt path.
        if completion_published:
            try: (output/'evaluation-complete.json').unlink(missing_ok=True)
            except OSError: pass  # Retained failure disposition also blocks readback.
        try:
            if not (output/'failure.json').exists():
                d.write_json(output/'failure.json',dict(status='failed',error=type(exc).__name__,detail=str(exc)))
        except Exception:
            pass  # Diagnostic I/O must not replace the primary evaluation failure.
        raise



def main(argv=None):
    import argparse
    from . import train as t
    parser=argparse.ArgumentParser(description='Frozen exploratory reused-test evaluation; never tune/select')
    for key in ['run','bundle','admission','output']: parser.add_argument('--'+key,required=True)
    args=parser.parse_args(argv)
    try:
        d.safe_path(args.output)
        data=t.read_admitted(args.bundle,args.admission)
        result=_evaluate(args.run,data,args.output)
        print(result['status'])
        return 0
    except (ValueError,OSError,KeyError,TypeError) as exc:
        parser.error(str(exc))


if __name__=='__main__':
    raise SystemExit(main())


