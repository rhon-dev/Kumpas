"""Float32-only rejection; synthetic probability vectors throughout."""
import importlib
import importlib.util
import numpy as np
import pytest


def module():
    assert importlib.util.find_spec('training.holistic_migration.rejection') is not None, 'rejection behavior missing'
    return importlib.import_module('training.holistic_migration.rejection')


def probs(confidences, classes=None):
    classes = [0]*len(confidences) if classes is None else classes
    p=np.zeros((len(confidences),50),np.float32)
    for i,(c,k) in enumerate(zip(confidences,classes)):
        p[i,k]=c; p[i,(k+1)%50]=np.float32(1)-np.float32(c)
    return p


def test_exact_float32_boundary_and_lowest_ties():
    m=module(); t=np.float32(.75); below=np.nextafter(t,np.float32(0))
    p=probs([t,below,.5])
    assert m.decide(p,t).tolist()==[0,-1,-1]
    assert m.decide(p,np.float32(.5)).tolist()==[0,0,0]
    for bad in [True,np.bool_(False),float('nan'),float('inf'),-.1,1.1,'0.5']:
        with pytest.raises(ValueError): m.threshold(bad)
    for bad in [p.astype(np.float64),p.astype(bool),np.full((1,50),np.nan,np.float32),
                np.zeros((1,50),np.float32),np.ones((1,51),np.float32),np.full((1,50),-.1,np.float32)]:
        with pytest.raises(ValueError): m.probabilities(bad)
    assert m.probabilities(np.empty((0,50),np.float32)).shape==(0,50)


def test_exact_count_sweep_feasible_infeasible_and_controls():
    m=module(); assert hasattr(m,'select'), 'validation-only threshold selection missing'
    k=probs([.95]*9+[.7]); y=np.zeros(10,np.int64)
    o=probs([.96]+[.8]*19)
    result=m.select(k,y,o)
    assert result['status']=='feasible'
    best=result['selected']
    assert best['known_correct_accepted']==9 and best['oov_accepted']==1
    assert np.float32(best['threshold'])==np.float32(.95)
    assert best['known_target_met'] and best['oov_target_met']
    assert result['sweep'][-1]['known_correct_accepted']==0
    assert result['sweep'][-1]['threshold']==float(m.REJECT_ALL)
    # One additional OOV acceptance or one fewer correct accepted invalidates 1/20 or 9/10.
    impossible=m.select(k,y,probs([.96]*2+[.8]*18))
    assert impossible['status']=='completed_infeasible' and impossible['selected'] is None
    assert impossible['best_tradeoffs']
    impossible=m.select(probs([.95]*8+[.7]*2),y,probs([.96]+[.8]*19))
    assert impossible['selected'] is None
    with pytest.raises(ValueError): m.select(k,y,np.empty((0,50),np.float32))
    with pytest.raises(ValueError): m.select(k,y.astype(bool),o)
    with pytest.raises(ValueError): m.select(np.empty((0,50),np.float32),np.empty(0,np.int64),o)



@pytest.mark.parametrize('fault',['duplicate_declaration','invalid_status','boolean_label','changed_negative_label'])
def test_metric_declarations_cannot_hide_missing_or_ambiguous_sources(fault):
    m=module(); classes=[dict(dense_id=i,original_id=i,label=f'K{i}',category='TEST') for i in range(50)]
    kr=[dict(clip_id='k0',dense_id=0,status='eligible')]
    nr=[dict(clip_id=f'o{i}',original_id=50+i,label=f'OOV{i}',category='TEST',status='eligible') for i in range(55)]
    p=probs([1]); op=probs([.6]*55)
    good=m.metrics(p,np.array([0],np.int64),['k0'],op,[r['clip_id'] for r in nr],classes,kr,nr,.8)
    assert len(good['confusion'])==105 and len(good['oov']['classes'])==55
    if fault=='duplicate_declaration': kr.append(dict(kr[0],status='quarantined'))
    elif fault=='invalid_status': kr.append(dict(clip_id='unmeasured',dense_id=1,status='fabricated_success'))
    elif fault=='boolean_label': kr[0]['dense_id']=False
    else: nr.append(dict(nr[0],clip_id='excluded',status='quarantined',label='CHANGED LABEL'))
    with pytest.raises(ValueError): m.metrics(p,np.array([0],np.int64),['k0'],op,[f'o{i}' for i in range(55)],classes,kr,nr,.8)


def test_known_only_and_extended_precision_have_explicit_distinct_semantics():
    m=module()
    classes=[dict(dense_id=i,original_id=i,label=f'K{i}',category='TEST') for i in range(50)]
    known=probs([1,.6,.9],[0,1,0]); y=np.array([0,1,1],np.int64)
    kr=[dict(clip_id=f'k{i}',dense_id=int(k),status='eligible') for i,k in enumerate(y)]
    nr=[dict(clip_id='o',original_id=51,label='OOV',category='TEST',status='eligible'),
        dict(clip_id='q',original_id=51,label='OOV',category='TEST',status='quarantined')]
    measured=m.metrics(known,y,['k0','k1','k2'],probs([1]),['o'],classes,kr,nr,.8)
    clean=m.metrics(known,y,['k0','k1','k2'],probs([.6]),['o'],classes,kr,nr,.8)
    assert measured['known_only']==clean['known_only']
    k=measured['known_only']['classes'][0]; e=measured['extended_known_label']['classes'][0]
    assert k['precision']==.5 and e['precision']==pytest.approx(1/3)
    assert k['f1']>e['f1'] and k['recall']==e['recall']==1 and k['support']==e['support']==1
    assert measured['known_only']['macro_f1']>measured['extended_known_label']['macro_f1']
    assert measured['known_only']['classes'][1]['rejected']==1
    assert measured['known_only']['classes'][1]['incorrect_accepted']==1
    assert measured['oov']['quarantined']==1 and measured['oov']['rejected']==0
    assert measured['oov']['false_accept_rate']==1


def test_extended_confusion_and_all_literal_class_denominators():
    m=module(); assert hasattr(m,'metrics'), 'rejection reporting missing'
    classes=[dict(dense_id=i,original_id=i,label=f'LITERAL {i}',category='TEST') for i in range(50)]
    known=probs([.9,.9,.6],[0,0,1]); y=np.array([0,1,1],np.int64)
    known_rows=[dict(clip_id=f'k{i}',dense_id=k,status='eligible') for i,k in enumerate(y.tolist())]
    known_rows.append(dict(clip_id='missing',dense_id=2,status='source_failure'))
    neg_rows=[dict(clip_id='o0',original_id=51,label='OOV51',category='TEST',status='eligible'),
              dict(clip_id='o1',original_id=51,label='OOV51',category='TEST',status='source_failure'),
              dict(clip_id='o2',original_id=52,label='OOV52',category='TEST',status='eligible')]
    r=m.metrics(known,y,['k0','k1','k2'],probs([.9,.6]),['o0','o2'],classes,known_rows,neg_rows,np.float32(.8))
    assert len(r['known']['classes'])==50 and len(r['confusion'])==52 and len(r['confusion'][0])==51
    assert r['known']['correct_accepted']==1 and r['known']['incorrect_accepted']==1 and r['known']['rejected']==1
    assert r['known']['declared']==4 and r['known']['source_excluded']==1
    assert r['known']['classes'][1]['support']==2 and r['known']['classes'][1]['recall']==0
    assert r['oov']['declared']==3 and r['oov']['eligible']==2 and r['oov']['accepted']==1
    assert r['oov']['classes'][0]['source_failures']==1 and r['oov']['classes'][0]['false_accept_rate']==1
    assert r['idle_false_activations_per_minute'] is None and r['live_ready'] is False
    empty=m.metrics(np.empty((0,50),np.float32),np.empty(0,np.int64),[],np.empty((0,50),np.float32),[],classes,[],[],.8)
    assert empty['known']['correct_accepted_rate'] is None and empty['oov']['false_accept_rate'] is None
    with pytest.raises(ValueError): m.metrics(known,y,['k1','k0','k2'],probs([.9,.6]),['o0','o2'],classes,known_rows,neg_rows,.8)
