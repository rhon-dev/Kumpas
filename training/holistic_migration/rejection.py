"""Pure Float32 max-softmax rejection. No fitting, native SDK or data access."""
from numbers import Real
import numpy as np

REJECT_ALL = np.nextafter(np.float32(1),np.float32(np.inf))


def probabilities(p):
    """Only actual plain Float32 N-by-50 probability arrays qualify."""
    if (type(p) is not np.ndarray or p.dtype!=np.float32 or p.ndim!=2 or p.shape[1]!=50
            or not np.isfinite(p).all() or ((p<0)|(p>1)).any()
            or not np.allclose(p.sum(axis=1,dtype=np.float64),1,rtol=0,atol=1e-6)):
        raise ValueError('finite normalized Float32[N,50] probabilities required')
    return p


def threshold(value):
    if (not isinstance(value,Real) or isinstance(value,(bool,np.bool_)) or not np.isfinite(value)
            or value<0 or (value>1 and value!=REJECT_ALL)):
        raise ValueError('finite confidence threshold or exact reject-all control required')
    return np.float32(value)


def decide(p, cutoff):
    p=probabilities(p); t=threshold(cutoff)
    return np.where(p.max(axis=1)>=t,p.argmax(axis=1),-1).astype(np.int64)


def labels(y, n):
    if type(y) is not np.ndarray or y.dtype!=np.int64 or y.shape!=(n,) or ((y<0)|(y>=50)).any():
        raise ValueError('Int64[N] literal dense output labels required')
    return y


def counts(known, y, oov, cutoff):
    known=probabilities(known); oov=probabilities(oov); y=labels(y,len(known))
    kd=decide(known,cutoff); od=decide(oov,cutoff)
    correct=int((kd==y).sum()); accepted=int((od>=0).sum())
    return dict(threshold=float(threshold(cutoff)),threshold_bits=int(threshold(cutoff).view(np.uint32)),
                known_eligible=len(y),known_correct_accepted=correct,known_rejected=int((kd<0).sum()),
                known_incorrect_accepted=int(((kd>=0)&(kd!=y)).sum()),oov_eligible=len(oov),oov_accepted=accepted,
                known_target_met=bool(len(y)>0 and correct*10>=9*len(y)),
                oov_target_met=bool(len(oov)>0 and accepted*20<=len(oov)))


def select(known, y, oov):
    """Enumerate every validation decision regime and retain the complete sweep."""
    known=probabilities(known); oov=probabilities(oov); labels(y,len(known))
    if not len(known) or not len(oov):
        raise ValueError('nonempty known and OOV validation support required')
    confidence=np.unique(np.concatenate([known.max(axis=1),oov.max(axis=1)]))
    boundaries=np.unique(np.concatenate([np.array([0],np.float32),confidence,
        np.nextafter(confidence,np.float32(np.inf)),np.array([REJECT_ALL],np.float32)]))
    sweep=[counts(known,y,oov,t) for t in boundaries]
    feasible=[r for r in sweep if r['known_target_met'] and r['oov_target_met']]
    ranking=lambda r:(r['known_correct_accepted'],-r['oov_accepted'],r['threshold'])
    best=max(feasible,key=ranking) if feasible else None
    # Nondominated count tradeoffs (highest cutoff for equivalent measured counts).
    unique={}
    for r in sweep: unique[(r['known_correct_accepted'],r['oov_accepted'])]=r
    tradeoffs=[r for r in unique.values() if not any(
        s['known_correct_accepted']>=r['known_correct_accepted'] and s['oov_accepted']<=r['oov_accepted']
        and (s['known_correct_accepted'],s['oov_accepted'])!=(r['known_correct_accepted'],r['oov_accepted'])
        for s in unique.values())]
    return dict(status='feasible' if best is not None else 'completed_infeasible',selected=best,
                targets=dict(known_minimum=[9,10],oov_maximum=[1,20]),sweep=sweep,best_tradeoffs=tradeoffs)



def class_declarations(classes):
    if type(classes) is not list or len(classes)!=50:
        raise ValueError('all50 ordered literal classes required')
    for i,c in enumerate(classes):
        if (type(c) is not dict or set(c)!={'dense_id','original_id','label','category'}
                or type(c['dense_id']) is not int or c['dense_id']!=i
                or type(c['original_id']) is not int or c['original_id']<0
                or any(type(c[k]) is not str or not c[k] for k in ['label','category'])):
            raise ValueError('strict ordered literal class schema required')
    if len({c['original_id'] for c in classes})!=50 or len({c['label'] for c in classes})!=50:
        raise ValueError('unique50 original classes required')
    return classes


def metrics(known, y, known_ids, oov, oov_ids, classes, known_rows, oov_rows, cutoff):
    """All declared denominators and extended confusion; rejection is not output51."""
    known=probabilities(known); oov=probabilities(oov); labels(y,len(known))
    class_declarations(classes)
    if type(known_rows) is not list or type(oov_rows) is not list:
        raise ValueError('explicit metric source declarations required')
    seen=set(); negative={}
    for known_kind,rows in [(True,known_rows),(False,oov_rows)]:
        required={'clip_id','status','dense_id'} if known_kind else {'clip_id','status','original_id','label','category'}
        for row in rows:
            if type(row) is not dict or not required<=set(row) or set(row)-required-{'reason'}:
                raise ValueError('exact metric source schema required')
            clip=row['clip_id']
            if type(clip) is not str or not clip or clip in seen: raise ValueError('unique metric source declarations required')
            seen.add(clip)
            if row['status'] not in ['eligible','ineligible','source_failure','quarantined']:
                raise ValueError('unmeasured source is not a fabricated prediction')
            key='dense_id' if known_kind else 'original_id'; identity=row[key]
            if type(identity) is not int or identity<0 or (known_kind and identity>=50):
                raise ValueError('metric label must be literal integer')
            if not known_kind:
                if any(type(row[k]) is not str or not row[k] for k in ['label','category']):
                    raise ValueError('literal negative label/category required')
                literal=(row['label'],row['category'])
                if negative.setdefault(identity,literal)!=literal: raise ValueError('inconsistent publisher negative class')
    eligible_known=[r for r in known_rows if r['status']=='eligible']
    eligible_oov=[r for r in oov_rows if r['status']=='eligible']
    if (known_ids!=[r['clip_id'] for r in eligible_known] or oov_ids!=[r['clip_id'] for r in eligible_oov]
            or y.tolist()!=[r['dense_id'] for r in eligible_known]
            or len(known_ids)!=len(known) or len(oov_ids)!=len(oov)
            or len(set(known_ids))!=len(known_ids) or len(set(oov_ids))!=len(oov_ids)):
        raise ValueError('exact ordered scored/declared membership required')
    kd=decide(known,cutoff); od=decide(oov,cutoff)
    negative_classes=sorted({r['original_id'] for r in oov_rows})
    confusion=np.zeros((50+len(negative_classes),51),np.int64)
    for truth,pred in zip(y,kd): confusion[truth,50 if pred<0 else pred]+=1
    index={c:50+i for i,c in enumerate(negative_classes)}
    for r,pred in zip(eligible_oov,od): confusion[index[r['original_id']],50 if pred<0 else pred]+=1
    rate=lambda n,d: n/d if d else None
    per_known=[]; known_only=[]
    for c in classes:
        i=c['dense_id']; mask=y==i; support=int(mask.sum()); tp=int(((kd==i)&mask).sum())
        predicted=int((kd==i).sum())
        only_precision=tp/predicted if predicted else 0.0
        # Include OOV false positives only in the explicitly extended metric.
        predicted+=int((od==i).sum())
        precision=tp/predicted if predicted else 0.0
        recall=tp/support if support else 0.0
        f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
        declared=sum(r['dense_id']==i for r in known_rows)
        per_known.append(dict(c,declared=declared,support=support,source_excluded=declared-support,
            correct_accepted=tp,rejected=int((mask&(kd<0)).sum()),incorrect_accepted=int((mask&(kd>=0)&(kd!=y)).sum()),
            precision=precision,recall=recall,f1=f1))
        only_f1=2*only_precision*recall/(only_precision+recall) if only_precision+recall else 0.0
        known_only.append(dict(per_known[-1],precision=only_precision,f1=only_f1,
            quarantined=sum(r['dense_id']==i and r['status']=='quarantined' for r in known_rows)))
        per_known[-1]['quarantined']=known_only[-1]['quarantined']
    per_oov=[]
    for i in negative_classes:
        declared=[r for r in oov_rows if r['original_id']==i]
        selected=np.array([r['original_id']==i for r in eligible_oov],dtype=bool)
        eligible=int(selected.sum()); accepted=int((selected&(od>=0)).sum())
        per_oov.append(dict(original_id=i,label=declared[0]['label'],category=declared[0]['category'],
            declared=len(declared),eligible=eligible,excluded=len(declared)-eligible,
            quarantined=sum(r['status']=='quarantined' for r in declared),
            source_failures=sum(r['status']=='source_failure' for r in declared),
            capture_exclusions=sum(r['status']=='ineligible' for r in declared),
            accepted=accepted,rejected=eligible-accepted,false_accept_rate=rate(accepted,eligible)))
    correct=int((kd==y).sum()); rejected=int((kd<0).sum()); accepted=int((od>=0).sum())
    known_summary=dict(declared=len(known_rows),eligible=len(known),source_excluded=len(known_rows)-len(known),
        quarantined=sum(r['status']=='quarantined' for r in known_rows),correct_accepted=correct,
        rejected=rejected,incorrect_accepted=len(known)-correct-rejected,correct_accepted_rate=rate(correct,len(known)))
    return dict(schema_version=1,threshold=float(threshold(cutoff)),live_ready=False,
        known_only=dict(known_summary,precision_scope='known_sources_only',
            macro_f1=sum(c['f1'] for c in known_only)/50,classes=known_only),
        extended_known_label=dict(known_summary,precision_scope='known_plus_accepted_publisher_oov_false_positives',
            macro_f1=sum(c['f1'] for c in per_known)/50,classes=per_known),
        known_compatibility_alias='known is extended_known_label; use explicit metrics above',
        known=dict(declared=len(known_rows),eligible=len(known),source_excluded=len(known_rows)-len(known),
            correct_accepted=correct,rejected=rejected,incorrect_accepted=len(known)-correct-rejected,
            correct_accepted_rate=rate(correct,len(known)),macro_f1=sum(c['f1'] for c in per_known)/50,classes=per_known),
        oov=dict(declared=len(oov_rows),eligible=len(oov),excluded=len(oov_rows)-len(oov),
            quarantined=sum(c['quarantined'] for c in per_oov),source_candidates=sum(r['status']!='quarantined' for r in oov_rows),
            source_failures=sum(c['source_failures'] for c in per_oov),capture_exclusions=sum(c['capture_exclusions'] for c in per_oov),
            accepted=accepted,rejected=len(oov)-accepted,false_accept_rate=rate(accepted,len(oov)),classes=per_oov),
        confusion=confusion.tolist(),confusion_rows=[c['label'] for c in classes]+[c['label'] for c in per_oov],
        confusion_columns=[c['label'] for c in classes]+['REJECTED_NOT_NEURAL_OUTPUT'],
        idle_false_activations_per_minute=None,genuine_idle_annotated=False,expert_validated=False,
        signer_independent=False,device_validated=False,fresh_untouched_holdout=False)
