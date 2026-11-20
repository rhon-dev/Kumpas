"""Frozen-model validation-only rejection calibration; challenge is a separate gate."""
from pathlib import Path
import os
import numpy as np
from . import oov_dataset as o, rejection as r
from . import dataset as d


def known_validation(p):
    """Reuse only hash-bound historical validation probabilities/metadata, never test arrays."""
    files=p['frozen']
    captures=o.json_read(o.check_binding(files['capture_rows.json']))
    declared=[dict(clip_id=c['clip_id'],dense_id=c['dense_id'],status='eligible' if c['reason']=='eligible' else 'ineligible')
              for c in captures if c['partition']=='validation']
    eligible=[c for c in declared if c['status']=='eligible']
    ids=np.load(o.check_binding(files['validation_ids.npy']),allow_pickle=False)
    probs=r.probabilities(np.load(o.check_binding(files['validation_probabilities.npy']),allow_pickle=False))
    if ids.dtype.kind!='U' or ids.shape!=(len(eligible),) or len(probs)!=len(eligible):
        raise ValueError('known validation ID/probability dimensions differ')
    d.same(ids.tolist(),[c['clip_id'] for c in eligible],'frozen validation exact ordered membership')
    y=np.array([c['dense_id'] for c in eligible],np.int64); r.labels(y,len(probs))
    if set(y.tolist())!=set(range(50)) or len(set(ids.tolist()))!=len(ids):
        raise ValueError('all50 known support and unique frozen IDs required')
    if p['evidence_kind']=='public_source':
        d.same([len(probs),len(declared)],[145,150],'approved known eligible/declared denominators')
    return probs,y,ids,declared


def _negative_rows(ledger):
    return [dict(clip_id=l['clip_id'],original_id=l['source']['original_id'],label=l['source']['label'],
                 category=l['source']['category'],status=l['status'],reason=l['reason']) for l in ledger]


def _load_array(root, name, files, shape, dtype):
    d.same(d.sha256(root/name),files[name],'saved score artifact '+name)
    return o.array_read(root/name,shape,dtype)


SCORE_FILES={'known_probabilities.npy','known_labels.npy','known_ids.npy','oov_probabilities.npy','oov_ids.npy'}


def _score_readback(output, protocol, allow_synthetic, operation="calibrate", allow_pending=False):
    """Saved outputs only. No native model/detector execution or source video decode."""
    p=o.read_protocol(protocol,allow_synthetic=allow_synthetic)
    out=d.safe_path(output,must_exist=True)
    if os.path.lexists(out/'scores-failure.json') or (not allow_pending and os.path.lexists(out/'scores-incomplete.json')):
        raise ValueError('failed/incomplete score publication')
    score=o.json_read(out/'score-complete.json')
    keys={'schema_version','status','operation','protocol','negative_bundle','negative_manifest','model','files'}
    if type(score) is not dict or set(score)!=keys: raise ValueError('exact score completion schema required')
    for k,v in dict(schema_version=1,status='scores_saved',protocol=o.binding(protocol),model=p['frozen']['model.keras']).items():
        d.same(score[k],v,'saved scores '+k)
    if score['operation']!=operation or set(score['files'])!=SCORE_FILES:
        raise ValueError('invalid scoring operation/artifact coverage')
    o.check_binding(score['negative_manifest'])
    d.same(score['negative_manifest']['path'],str(Path(score['negative_bundle'])/'complete.json'),'exact negative bundle target')
    mode='calibration' if score['operation']=='calibrate' else 'challenge'
    start=o.json_read(out/'start.json')
    if operation=='calibrate':
        d.same(start,dict(schema_version=1,status='calibration_started',protocol=o.binding(protocol),
            negative_bundle=score['negative_bundle'],model=p['frozen']['model.keras']),'exact calibration start provenance')
    # The caller must validate a freeze before entering this reader for challenge outputs.
    bm,x,ids,ledger=o.read_bundle(score['negative_bundle'],protocol=protocol,mode=mode,allow_synthetic=allow_synthetic)
    expected,y0,id0,kr=known_validation(p) if operation=='calibrate' else known_challenge(p)
    sizes={'known_probabilities.npy':((len(expected),50),'float32'),'known_labels.npy':((len(expected),),'int64'),
        'known_ids.npy':((len(expected),),'U'),'oov_probabilities.npy':((len(ids),50),'float32'),'oov_ids.npy':((len(ids),),'U')}
    values={n:_load_array(out,n,score['files'],*sizes[n]) for n in SCORE_FILES}
    kp=r.probabilities(values['known_probabilities.npy']); op=r.probabilities(values['oov_probabilities.npy'])
    y=r.labels(values['known_labels.npy'],len(kp)); ki=values['known_ids.npy']; oi=values['oov_ids.npy']
    if oi.dtype.kind!='U' or oi.shape!=(len(op),): raise ValueError('saved OOV score IDs invalid')
    d.same(oi.tolist(),ids.tolist(),'scored eligible negative membership')
    if len(op)!=len(ids): raise ValueError('score row count differs from negative bundle')
    if score['operation']=='calibrate':
        if not np.array_equal(kp,expected) or not np.array_equal(y,y0) or not np.array_equal(ki,id0):
            raise ValueError('saved known predictions differ from immutable validation evidence')
    else:
        if not np.array_equal(kp,expected) or not np.array_equal(y,y0) or not np.array_equal(ki,id0):
            raise ValueError('saved historical challenge evidence differs')
    return p,score,kp,y,ki,op,oi,kr,_negative_rows(ledger)


def _save_scores(out, protocol, negative_bundle, p, operation, kp, y, ki, op, oi):
    o.publish(out/'scores-incomplete.json',dict(status='scores_incomplete'))
    for name,array in [('oov_probabilities.npy',r.probabilities(op)),('oov_ids.npy',oi),
                       ('known_probabilities.npy',r.probabilities(kp)),('known_labels.npy',y),('known_ids.npy',ki)]:
        o.save_array(out/name,array)
    score=dict(schema_version=1,status='scores_saved',operation=operation,protocol=o.binding(protocol),
        negative_bundle=str(d.safe_path(negative_bundle,must_exist=True)),negative_manifest=o.binding(Path(negative_bundle)/'complete.json'),
        model=p['frozen']['model.keras'],files={n:d.sha256(out/n) for n in sorted(SCORE_FILES)})
    o.publish(out/'score-complete.json',score)
    return score


def _policy(p, protocol, out, selected):
    return dict(schema_version=1,status='feasible_frozen_rejection_companion',live_ready=False,
        decision='max_softmax_greater_equal_float32',argmax_ties='lowest_index',
        threshold=selected['threshold'],threshold_bits=selected['threshold_bits'],targets=o.TARGETS,counts=selected,
        protocol=o.binding(protocol),quarantine_view=p['quarantine_view'],
        historical_fit_ids_flagged_only=[] if p['quarantine_view'] is None else o.FIT_FLAG_IDS,
        scores=o.binding(out/'score-complete.json'),model=p['frozen']['model.keras'],
        baseline_candidate_contract=p['frozen']['candidate-contract.json'],
        baseline_decision_policy=o.validate_contract(p['frozen'],p['classes'])['policy'],
        labels=p['classes'],feature='hm1588-v1 Float32[30,1588]',implementation=p['implementation'],runtime=p['runtime'],
        historical_policy_unchanged=True,idle_safety_measured=False,expert_validated=False,signer_independent=False,
        device_validated=False,fresh_untouched_holdout=False)


def read_freeze(run, *, protocol, allow_synthetic=False):
    """Affirmative stage-specific admission plus ordinary score decision parity."""
    run=d.safe_path(run,must_exist=True)
    for n in ['freeze-incomplete.json','freeze-failure.json','scores-incomplete.json','scores-failure.json']:
        if os.path.lexists(run/n): raise ValueError('failed policy/score publication')
    # A later reporting failure cannot revoke a valid, affirmatively admitted freeze.
    if os.path.lexists(run/'failure.json'):
        failure=o.json_read(run/'failure.json')
        d.same(failure.get('phase'),'report','failure must be strictly after valid freeze')
    return _freeze_details(run,protocol,allow_synthetic)


def _freeze_details(run, protocol, allow_synthetic):
    admission=o.json_read(run/'freeze-admission.json')
    d.same(admission,dict(schema_version=1,status='feasible_policy_admitted',freeze=o.binding(run/'freeze.json')),'affirmative freeze admission')
    p,score,kp,y,ki,op,oi,kr,nr=_score_readback(run,protocol,allow_synthetic)
    d.same(score['operation'],'calibrate','validation-only policy selection')
    result=r.select(kp,y,op)
    if result['selected'] is None: raise ValueError('infeasible validation cannot qualify policy')
    expected=_policy(p,protocol,run,result['selected'])
    actual=o.json_read(run/'freeze.json'); d.same(actual,expected,'ordinary policy readback')
    d.same(r.counts(kp,y,op,actual['threshold']),actual['counts'],'ordinary decision/count parity')
    if np.float32(actual['threshold']).view(np.uint32)!=actual['threshold_bits']:
        raise ValueError('Float32 threshold identity differs')
    return actual


def _calibration_report(p, kp, y, ki, op, oi, kr, nr, sweep):
    chosen=sweep['selected']
    # Infeasible output has no qualifying threshold; all nondominated measured tradeoffs retain full reports.
    cutoffs=[chosen['threshold']] if chosen is not None else [s['threshold'] for s in sweep['best_tradeoffs']]
    reports=[r.metrics(kp,y,ki.tolist(),op,oi.tolist(),p['classes'],kr,nr,t) for t in cutoffs]
    report=dict(schema_version=1,status='completed_feasible' if chosen is not None else 'completed_infeasible',
        live_ready=False,evidence_kind=p['evidence_kind'],quarantine_view=p['quarantine_view'],
        historical_fit_ids_flagged_only=[] if p['quarantine_view'] is None else o.FIT_FLAG_IDS,
        sweep=sweep,measurements=reports,
        known_evidence='reused_immutable_historical_validation_predictions_not_new_native_inference',
        oov_scope='publisher_label_only_not_idle_or_expert_validated',challenge_used=False,
        all_weak_classes=[c for report in reports for c in report['known']['classes'] if c['support']==0 or c['recall']<.9])
    return report


def _write_report(out, p, kp, y, ki, op, oi, kr, nr, sweep):
    report=_calibration_report(p,kp,y,ki,op,oi,kr,nr,sweep)
    o.publish(out/'report.json',report)
    return report


def _completed_readback(out, protocol, allow_synthetic, _allow_pending=False):
    o.barriers(out,('failure.json',) if _allow_pending else ('failure.json','incomplete.json'))
    complete=o.json_read(out/'complete.json')
    if type(complete) is not dict or set(complete)!={'schema_version','status','live_ready','protocol','scores','report','freeze'}:
        raise ValueError('exact calibration completion schema required')
    d.same(complete['schema_version'],1,'completion schema'); d.same(complete['live_ready'],False,'offline only')
    d.same(complete['protocol'],o.binding(protocol),'completed protocol')
    d.same(complete['scores'],o.binding(out/'score-complete.json'),'exact completed score target')
    d.same(complete['report'],o.binding(out/'report.json'),'exact completed report target')
    report_path=o.check_binding(complete['report'])
    p,s,kp,y,ki,op,oi,kr,nr=_score_readback(out,protocol,allow_synthetic)
    sweep=r.select(kp,y,op)
    expected_status='completed_feasible' if sweep['selected'] is not None else 'completed_infeasible'
    d.same(complete['status'],expected_status,'calibration disposition')
    report=o.json_read(report_path)
    d.same(report,_calibration_report(p,kp,y,ki,op,oi,kr,nr,sweep),'saved report full metric readback')
    d.same(o.json_read(out/'sweep.json'),sweep,'complete measured threshold sweep')
    if sweep['selected'] is not None:
        d.same(complete['freeze'],o.binding(out/'freeze.json'),'exact completed policy target')
        read_freeze(out,protocol=protocol,allow_synthetic=allow_synthetic)
    elif complete['freeze'] is not None or os.path.lexists(out/'freeze-admission.json') or os.path.lexists(out/'freeze.json'):
        raise ValueError('infeasible run cannot publish a qualifying policy')
    return complete


def calibrate(*, protocol, negative_bundle, output, _backend=None):
    synthetic=_backend is not None
    p=o.read_protocol(protocol,allow_synthetic=synthetic)
    if p['evidence_kind']=='public_source' and synthetic: raise ValueError('injected backend is synthetic-only')
    out=d.safe_path(output)
    if out.exists():
        result=_completed_readback(out,protocol,synthetic)
        saved=o.json_read(out/'score-complete.json')
        d.same(saved['negative_bundle'],str(d.safe_path(negative_bundle,must_exist=True)),'exact existing calibration bundle')
        return result
    bm,x,ids,ledger=o.read_bundle(negative_bundle,protocol=protocol,mode='calibration',allow_synthetic=synthetic)
    kp,y,ki,kr=known_validation(p)
    out=o.reserve(out,[protocol,negative_bundle]+[v['path'] for v in p['frozen'].values()])
    phase='scores'
    try:
        o.publish(out/'start.json',dict(schema_version=1,status='calibration_started',protocol=o.binding(protocol),
            negative_bundle=str(Path(negative_bundle)),model=p['frozen']['model.keras']))
        backend=FrozenBackend() if _backend is None else _backend
        model=backend.load(o.check_binding(p['frozen']['model.keras']))
        op=r.probabilities(backend.predict(model,x))
        if len(op)!=len(ids): raise ValueError('model returned wrong number of OOV probabilities')
        _save_scores(out,protocol,negative_bundle,p,'calibrate',kp,y,ki,op,ids)
        p,score,kp,y,ki,op,oi,kr,nr=_score_readback(out,protocol,synthetic,allow_pending=True)
        (out/'scores-incomplete.json').unlink()
        phase='freeze'
        sweep=r.select(kp,y,op)
        o.publish(out/'sweep.json',sweep)
        if sweep['selected'] is not None:
            o.publish(out/'freeze-incomplete.json',dict(status='freeze_incomplete'))
            o.publish(out/'freeze.json',_policy(p,protocol,out,sweep['selected']))
            o.publish(out/'freeze-admission.json',dict(schema_version=1,status='feasible_policy_admitted',freeze=o.binding(out/'freeze.json')))
            _freeze_details(out,protocol,synthetic)
            (out/'freeze-incomplete.json').unlink()
        phase='report'
        if sweep['selected'] is not None:
            read_freeze(out,protocol=protocol,allow_synthetic=synthetic)
        report=_write_report(out,p,kp,y,ki,op,oi,kr,nr,sweep)
        complete=dict(schema_version=1,status=report['status'],live_ready=False,protocol=o.binding(protocol),
            scores=o.binding(out/'score-complete.json'),report=o.binding(out/'report.json'),
            freeze=o.binding(out/'freeze.json') if sweep['selected'] is not None else None)
        o.publish(out/'complete.json',complete)
        completed=_completed_readback(out,protocol,synthetic,_allow_pending=True)
        (out/'incomplete.json').unlink()
        return completed
    except BaseException as exc:
        if phase in ['scores','freeze']:
            try: o.publish(out/('scores-failure.json' if phase=='scores' else 'freeze-failure.json'),dict(status='failed'))
            except Exception: pass
        o.failure(out,exc,phase); raise



def known_challenge(p):
    """Historical exposed203 known positives, only after affirmative freeze/start."""
    synthetic=p['evidence_kind']=='synthetic_in_process'
    if synthetic:
        if 'challenge_probabilities.npy' not in p['frozen']:
            return np.empty((0,50),np.float32),np.empty(0,np.int64),np.array([],dtype=np.str_),[]
        refs={n:p['frozen'][source] for n,source in [('probabilities.npy','challenge_probabilities.npy'),
            ('eligible_ids.npy','challenge_ids.npy'),('eligible_labels.npy','challenge_labels.npy')]}
    else:
        root=o.PHASE4/'exploratory-reused-test-v1'
        refs={n:dict(path=str(root/n),sha256=h) for n,h in {
            'probabilities.npy':'5ec40aa560789ffbea2ddf7062fc50d0e9b06157bdb32302d85f5a9daf5792ec',
            'eligible_ids.npy':'6b4453f3d3a427e51ee9d1014397e447236e6d6da35a58878ea1de3519183c86',
            'eligible_labels.npy':'4dbcea84ebeddbcab8d2c580d8da6a9b02ad47e39bc43e0028bde0a40701b246'}.items()}
    arrays={n:np.load(o.check_binding(ref),allow_pickle=False) for n,ref in refs.items()}
    probs=r.probabilities(arrays['probabilities.npy']); y=r.labels(arrays['eligible_labels.npy'],len(probs)); ids=arrays['eligible_ids.npy']
    captures=o.json_read(o.check_binding(p['frozen']['capture_rows.json']))
    rows=[dict(clip_id=c['clip_id'],dense_id=c['dense_id'],status='eligible' if c['reason']=='eligible' else 'ineligible',reason=c['reason'])
          for c in captures if c['partition']=='test']
    eligible=[c for c in rows if c['status']=='eligible']
    if ids.dtype.kind!='U' or ids.shape!=(len(eligible),) or len(probs)!=len(eligible):
        raise ValueError('historical challenge dimensions differ from declared metadata')
    if not synthetic: d.same([len(probs),len(rows)],[203,203],'historical203 challenge evidence')
    d.same(ids.tolist(),[c['clip_id'] for c in eligible],'historical exact known challenge membership')
    d.same(y.tolist(),[c['dense_id'] for c in eligible],'historical known challenge labels')
    if p['quarantine_view'] is not None:
        # The original cached arrays remain203; mask only the new assessment after freeze/start.
        excluded=set(o.KNOWN_QUARANTINE_IDS)
        if not excluded<={c['clip_id'] for c in eligible}: raise ValueError('missing approved known challenge quarantine')
        keep=np.array([clip not in excluded for clip in ids.tolist()],dtype=bool)
        probs,y,ids=probs[keep],y[keep],ids[keep]
        for c in rows:
            if c['clip_id'] in excluded: c.update(status='quarantined',reason='ambiguous_label_exact_source_copy')
        if not synthetic: d.same(len(probs),202,'new202 known challenge candidate scope')
    return probs,y,ids,rows


def _assessment_start(protocol, calibration_run, negative_bundle, output):
    return dict(schema_version=1,status='assessment_started',protocol=o.binding(protocol),
        freeze=o.binding(Path(calibration_run)/'freeze.json'),negative_bundle=str(d.safe_path(negative_bundle,must_exist=True)),
        negative_manifest=o.binding(Path(negative_bundle)/'complete.json'),output=str(d.safe_path(output)),
        tuning_allowed=False)


def _challenge_readback(out, protocol, calibration_run, negative_bundle, allow_synthetic, _allow_pending=False):
    policy=read_freeze(calibration_run,protocol=protocol,allow_synthetic=allow_synthetic)
    o.barriers(out,('failure.json',) if _allow_pending else ('failure.json','incomplete.json'))
    start=_assessment_start(protocol,calibration_run,negative_bundle,out)
    d.same(o.json_read(Path(calibration_run)/'assessment-start.json'),start,'exclusive bound assessment start')
    d.same(o.json_read(out/'start.json'),start,'assessment local start')
    p,score,kp,y,ki,op,oi,kr,nr=_score_readback(out,protocol,allow_synthetic,operation='challenge')
    complete=o.json_read(out/'complete.json')
    expected=dict(schema_version=1,status='challenge_assessed',live_ready=False,tuning_allowed=False,
        protocol=o.binding(protocol),freeze=o.binding(Path(calibration_run)/'freeze.json'),
        scores=o.binding(out/'score-complete.json'),report=o.binding(out/'report.json'))
    d.same(complete,expected,'challenge completion')
    report=o.json_read(o.check_binding(complete['report']))
    d.same(report,_challenge_report(p,kp,y,ki,op,oi,kr,nr,policy),'fixed challenge metric readback')
    return complete


def _challenge_report(p, kp, y, ki, op, oi, kr, nr, policy):
    return dict(schema_version=1,status='challenge_assessed',live_ready=False,tuning_allowed=False,
        evidence_kind=p['evidence_kind'],quarantine_view=p['quarantine_view'],
        historical_fit_ids_flagged_only=[] if p['quarantine_view'] is None else o.FIT_FLAG_IDS,
        evaluation_kind='historical_exposed_known_and_publisher_test_oov_not_fresh_holdout',
        threshold=policy['threshold'],threshold_bits=policy['threshold_bits'],
        measurements=r.metrics(kp,y,ki.tolist(),op,oi.tolist(),p['classes'],kr,nr,policy['threshold']),
        fixed_threshold_counts=r.counts(kp,y,op,policy['threshold']),selection_allowed=False)


def challenge(*, protocol, calibration_run, negative_bundle, output, _backend=None):
    """One fixed-threshold assessment; every completed readback is inference-free."""
    synthetic=_backend is not None
    # No negative bundle, raw/tensor or historical test access before this affirmative gate.
    policy=read_freeze(calibration_run,protocol=protocol,allow_synthetic=synthetic)
    p=o.read_protocol(protocol,allow_synthetic=synthetic)
    if p['evidence_kind']=='public_source' and synthetic: raise ValueError('synthetic backend forbidden')
    out=d.safe_path(output)
    if out.exists(): return _challenge_readback(out,protocol,calibration_run,negative_bundle,synthetic)
    start=_assessment_start(protocol,calibration_run,negative_bundle,out)
    # An attempt binds the entire frozen experiment, not merely an arbitrary fresh target directory.
    o.publish(Path(calibration_run)/'assessment-start.json',start)
    out=o.reserve(out,[protocol,calibration_run,negative_bundle])
    try:
        o.publish(out/'start.json',start)
        bm,x,ids,ledger=o.read_bundle(negative_bundle,protocol=protocol,mode='challenge',allow_synthetic=synthetic)
        d.same(bm['calibration_freeze'],start['freeze'],'challenge extraction same frozen companion')
        kp,y,ki,kr=known_challenge(p)
        backend=FrozenBackend() if _backend is None else _backend
        model=backend.load(o.check_binding(p['frozen']['model.keras']))
        op=r.probabilities(backend.predict(model,x))
        if len(op)!=len(ids): raise ValueError('challenge model returned wrong row count')
        _save_scores(out,protocol,negative_bundle,p,'challenge',kp,y,ki,op,ids)
        p,score,kp,y,ki,op,oi,kr,nr=_score_readback(out,protocol,synthetic,operation='challenge',allow_pending=True)
        (out/'scores-incomplete.json').unlink()
        report=_challenge_report(p,kp,y,ki,op,oi,kr,nr,policy)
        o.publish(out/'report.json',report)
        o.publish(out/'complete.json',dict(schema_version=1,status='challenge_assessed',live_ready=False,tuning_allowed=False,
            protocol=o.binding(protocol),freeze=start['freeze'],scores=o.binding(out/'score-complete.json'),report=o.binding(out/'report.json')))
        completed=_challenge_readback(out,protocol,calibration_run,negative_bundle,synthetic,_allow_pending=True)
        (out/'incomplete.json').unlink()
        return completed
    except BaseException as exc:
        o.failure(out,exc,'challenge_assessment'); raise



def report_saved(*, protocol, run, output, allow_synthetic=False, calibration_run=None):
    """Fresh diagnostic report from admitted saved scores; never mutate/retry inference."""
    run=d.safe_path(run,must_exist=True)
    score=o.json_read(run/'score-complete.json')
    operation=score.get('operation')
    if operation=='challenge':
        if calibration_run is None: raise ValueError('challenge report needs affirmative frozen calibration')
        policy=read_freeze(calibration_run,protocol=protocol,allow_synthetic=allow_synthetic)
        start=o.json_read(Path(calibration_run)/'assessment-start.json')
        d.same(start['output'],str(run),'original single assessment target')
    elif operation!='calibrate': raise ValueError('unsupported saved report operation')
    p,score,kp,y,ki,op,oi,kr,nr=_score_readback(run,protocol,allow_synthetic,operation=operation)
    out=o.reserve(output,[protocol,run])
    try:
        if operation=='calibrate':
            report=_write_report(out,p,kp,y,ki,op,oi,kr,nr,r.select(kp,y,op))
        else:
            report=_challenge_report(p,kp,y,ki,op,oi,kr,nr,policy)
            o.publish(out/'report.json',report)
        complete=dict(schema_version=1,status='saved_output_report',operation=operation,
            source_scores=o.binding(run/'score-complete.json'),report=o.binding(out/'report.json'),
            repairs_original_disposition=False,neural_inference_repeated=False,live_ready=False)
        o.publish(out/'complete.json',complete)
        (out/'incomplete.json').unlink()
        d.same(o.json_read(out/'complete.json'),complete,'saved report readback')
        o.check_binding(complete['report']); o.check_binding(complete['source_scores'])
        return complete
    except BaseException as exc:
        o.failure(out,exc,'saved_report'); raise



class FrozenBackend:
    """CPU-only bounded ordinary inference. No optimizer, fitting or moment updates."""
    def load(self,path):
        import tensorflow as tf
        with tf.device('/CPU:0'):
            model=tf.keras.models.load_model(d.safe_path(path,must_exist=True),compile=False,safe_mode=True)
        if (model.input_shape!=(None,30,1588) or model.output_shape!=(None,50)
                or len(model.inputs)!=1 or len(model.outputs)!=1
                or str(model.inputs[0].dtype)!='float32' or str(model.outputs[0].dtype)!='float32'):
            raise ValueError('frozen model must consume Float32[30,1588] and emit Float32[50]')
        return model

    def predict(self,model,x):
        import tensorflow as tf
        from .face_augmentation import validate_tensor
        if x.dtype!=np.float32 or x.ndim!=3 or x.shape[1:]!=(30,1588):
            raise ValueError('fixed Float32 tensor contract required')
        outputs=[]
        for i in range(0,len(x),32):
            block=np.asarray(x[i:i+32]); validate_tensor(block)
            with tf.device('/CPU:0'):
                p=model(block,training=False).numpy()
            r.probabilities(p)
            if p.shape!=(len(block),50): raise ValueError('frozen model returned wrong output shape')
            outputs.append(p)
        return np.concatenate(outputs) if outputs else np.empty((0,50),np.float32)



def main(argv=None):
    import argparse
    import sys
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    for name in ['calibrate','challenge','report']:
        command=sub.add_parser(name)
        command.add_argument('--protocol',required=True,type=Path)
        command.add_argument('--output',required=True,type=Path)
        if name!='report': command.add_argument('--negative-bundle',required=True,type=Path)
        else: command.add_argument('--run',required=True,type=Path)
        if name=='challenge': command.add_argument('--calibration-run',required=True,type=Path)
        if name=='report': command.add_argument('--calibration-run',type=Path)
    args=vars(parser.parse_args(argv)); command=args.pop('command')
    try:
        operation={'calibrate':calibrate,'challenge':challenge,'report':report_saved}[command]
        value=operation(**args)
        print(value['status'])
        return 0 if value['status']!='completed_infeasible' else 3
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print('Frozen rejection operation denied: '+str(exc),file=sys.stderr)
        return 2


if __name__=='__main__':
    raise SystemExit(main())
