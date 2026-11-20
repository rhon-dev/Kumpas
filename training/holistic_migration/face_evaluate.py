"""Face-inclusive frozen exploratory evaluation; no selection/tuning from test."""
from pathlib import Path
import os
import numpy as np
from . import dataset as d
from .evaluate import probabilities, metrics as historical_metrics, _publish_json


def metrics(y,p,ids,classes,captures,*,partition):
    report=historical_metrics(y,p,ids,classes,captures,partition=partition)
    from .face_train import _loss
    total=report['all_declared']['declared']; correct=report['all_declared']['correct_eligible']; missing=len(report['exclusions'])
    report.update(loss=_loss(y,p),policy_rejection_count_scored_positives=0,
        policy_rejection_rate_scored_positives=0.0 if len(ids) else None,
        all_declared_bounds=dict(metric='accuracy_bounds_not_measured_all_source_accuracy',
            lower=correct/total if total else None,upper=(correct+missing)/total if total else None),
        idle_false_accept_rate=None,unknown_false_accept_rate=None,rejection_threshold=None,
        rejection_calibration=None)
    return report


def frozen_selection(run,data):
    from . import face_train as t
    run=d.safe_path(run,must_exist=True)
    if os.path.lexists(run/'incomplete.json'): raise ValueError('incomplete selection cannot qualify')
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
    proof_path=d.safe_path(config['tiny_proof'],must_exist=True)
    if proof_path.name!='tiny-proof.json' or any(os.path.lexists(proof_path.parent/n) for n in ['failure.json','incomplete.json']):
        raise ValueError('failed/missing retained tiny proof')
    d.same(d.sha256(proof_path),config['tiny_proof_sha256'],'frozen source-bound tiny proof')
    proof=t._json(proof_path)
    d.same(proof['status'],'tiny_proven','frozen tiny status')
    d.same(proof['identity'],t._identity(data),'frozen tiny identities')
    d.same(proof['selected_tensors'],t._selected_identity(t.tiny_selection(data)),'frozen exact tiny tensors')
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
    from . import face_train as t
    if any(os.path.lexists(output/n) for n in ['failure.json','incomplete.json']) or not (output/'evaluation-complete.json').is_file():
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
    from . import face_train as t
    if data.provenance!='synthetic_in_process' and _backend is not None: raise ValueError('synthetic seam forbidden')
    run=d.safe_path(run,must_exist=True); output=d.safe_path(output)
    selection=frozen_selection(run,data)
    if run==output or run in output.parents or output in run.parents: raise ValueError('evaluation overlaps frozen run')
    start=dict(schema_version=1,status='evaluation_started',evaluation_kind='exploratory_reused_test',
               run=str(run),selection_sha256=d.sha256(run/'selection.json'),identity=t._identity(data),policy=t.POLICY)
    if output.exists(): return _evaluation_readback(output,start)
    t._output_path(output,data)
    t._recheck(data,start['identity'])
    config=t._json(run/'config.json')
    t._verify_tiny(config['tiny_proof'],data,_backend=_backend)
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
    from . import face_train as t
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


