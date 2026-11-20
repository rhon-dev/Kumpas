"""Only invented publisher metadata/media/landmarks; no public data execution."""
import importlib
import importlib.util
import json
from pathlib import Path
import numpy as np
import pytest


def module():
    assert importlib.util.find_spec('training.holistic_migration.oov_dataset') is not None, 'OOV admission module missing'
    return importlib.import_module('training.holistic_migration.oov_dataset')


def row(i=51, split='train'):
    clip = f'clips/{i}/1.MOV'
    return dict(clip_id=clip,literal_source_token=clip.replace('/', '\\'),original_id=i,
                label=f'LITERAL {i}',category='TEST',official_split=split,
                partition='calibration' if split=='train' else 'challenge',video_bytes=3,
                video_sha256='a'*64,decoded_frames=8,decoded_bgr_sha256='b'*64,
                shapes=[[2,3,3]],status='ok',failure=None)


def test_literal_admission_and_partition_firewall():
    m=module(); r=row(); known=[dict(original_id=0,label='KNOWN')]
    assert m.validate_rows([r], known)==[r]
    for key,value in [('clip_id','clips/051/1.MOV'),('literal_source_token','clips/51/1.MOV'),
                      ('label','KNOWN'),('original_id',True),('partition','challenge'),('video_bytes',True)]:
        bad=dict(r,**{key:value})
        with pytest.raises(ValueError): m.validate_rows([bad],known)
    with pytest.raises(ValueError): m.validate_rows([r,r],known)
    with pytest.raises(ValueError): m.partition_rows([r,row(52,'test')],'calibration',requested_ids=['clips/52/1.MOV'])
    assert m.partition_rows([r,row(52,'test')],'pilot')==[r]
    with pytest.raises(ValueError): m.require_real({'evidence_kind':'synthetic_in_process'})


def dump(path,value):
    path.write_text(json.dumps(value,allow_nan=False,sort_keys=True)+'\n')
    return str(path)


def fixture_protocol(tmp_path, source_media=None, model_payload=None):
    m=module(); root=tmp_path/'inputs'; root.mkdir()
    # Metadata-only synthetic archive; no genuine publisher material or checkpoint.
    archive=root/'clips.zip'; archive.write_bytes(b'not-a-real-archive')
    classes=[dict(dense_id=i,original_id=i,label=f'KNOWN {i}',category='TEST') for i in range(50)]
    frozen=root/'phase4'; frozen.mkdir()
    dump(frozen/'labels.json',classes)
    feature=frozen/'FEATURES_FACE.md'; feature.write_text('synthetic feature specification')
    dump(frozen/'candidate-contract.json',dict(contract_file=str(feature),contract_sha256=m.d.sha256(feature),
        detector_source_graph_sha256='c'*64,dtype='float32',feature_version='hm1588-v1',
        input_shape=[None,30,1588],output_shape=[None,50],live_ready=False,ordered_classes=classes,
        policy=dict(decision='closed_set_argmax',live_ready=False,outputs=50,schema_version=1,
                    unknown_rejection='unmeasured_no_observed_validation_negatives')))
    (frozen/'model.keras').write_bytes(b'synthetic-placeholder-not-model' if model_payload is None else model_payload)
    captures=[dict(clip_id=f'clips/{i}/known.MOV',partition='validation',dense_id=i,status='eligible',reason='eligible') for i in range(50)]
    dump(frozen/'capture_rows.json',captures)
    p=np.zeros((50,50),np.float32); p[np.arange(50),np.arange(50)]=1
    np.save(frozen/'validation_probabilities.npy',p); np.save(frozen/'validation_ids.npy',np.array([r['clip_id'] for r in captures]))
    dump(frozen/'selection.json',{'status':'frozen_validation_selection'})
    dump(frozen/'phase4-offline-acceptance.json',{'status':'synthetic_fixture_only'})
    rows=[row(51),row(52),row(51,'test'),row(52,'test')]
    # Distinct canonical test source IDs, hashes, and parent-audit extra metadata.
    for i,r in enumerate(rows):
        if r['official_split']=='test':
            r['clip_id']=r['clip_id'].replace('/1.MOV','/2.MOV'); r['literal_source_token']=r['clip_id'].replace('/','\\')
        r.pop('failure'); r.update(signer_id=None,annotation_scope='publisher_label_only_not_project_expert_or_idle_annotation',
            archive_crc32='12345678',declared_frames=8,fps=15.0,backend='synthetic',first_timestamp_ms=0.0,last_timestamp_ms=469.0,
            video_sha256=f'{i+1:064x}',decoded_bgr_sha256=f'{i+11:064x}')
    rows=sorted(rows,key=lambda r:r['clip_id'])
    if source_media is not None:
        import zipfile
        with zipfile.ZipFile(archive,'w') as z:
            for r,(payload,audit) in zip(rows,source_media):
                z.writestr(r['clip_id'],payload)
                r.update(audit)
    rp=root/'rows.jsonl'; rp.write_text(''.join(json.dumps(r)+'\n' for r in rows))
    dup=root/'duplicates.json'; dump(dup,{'groups':{'raw_bytes':[],'decoded_pixels':[]},'blocking_groups':[]})
    control=root/'control.json'; dump(control,{'status':'matched_prior_selected_source_pixel_audit'})
    ref=lambda path:dict(path=str(path),sha256=m.d.sha256(path))
    audit=dict(schema_version=1,status='complete',evidence_kind='public_source_video_audit',archive=ref(archive),rows=ref(rp),
        duplicates=ref(dup),decoder_control=ref(control),input_bindings={str(archive):m.d.sha256(archive)},
        partitions={p:dict(declared=2,decoded_ok=2,failures=0) for p in ['calibration','challenge']},
        calibration_ids=[r['clip_id'] for r in rows if r['partition']=='calibration'],
        challenge_ids=[r['clip_id'] for r in rows if r['partition']=='challenge'],
        blocking_duplicate_groups=0,protocol_admission_blocked=False,runtime={'synthetic':True},recipe={'neural_inference':False})
    ap=root/'audit.json'; dump(ap,audit)
    auth=root/'authorization.json'; dump(auth,{'approved_offline_targets':{
        'maximum_eligible_publisher_labeled_oov_false_acceptance_fraction':[1,20],
        'minimum_correctly_accepted_eligible_known_validation_fraction':[9,10],
        'per_class_reporting_required':True,'infeasible_result_must_be_preserved':True}})
    out=tmp_path/'protocol'
    m.prepare(source_audit=ap,authorization=auth,phase4_campaign=frozen,output=out,_synthetic=True)
    return out/'protocol.json'


def fixture_quarantine(tmp_path, with_media=False, challenge_count=1):
    """Invented metadata with actual exclusion IDs, no public arrays/media/checkpoint."""
    m=module(); base=fixture_protocol(tmp_path); p=m.read_protocol(base,allow_synthetic=True)
    root=Path(p['audit']['path']).parent; frozen=root/'phase4'
    classes=p['classes']
    originals=list(range(25))+list(range(49,58))+list(range(62,68))+[72,74,76,77,85,86,89,91,95,96]
    for c,i in zip(classes,originals): c['original_id']=i
    dump(frozen/'labels.json',classes)
    contract=m.json_read(frozen/'candidate-contract.json'); contract['ordered_classes']=classes; dump(frozen/'candidate-contract.json',contract)
    captures=m.json_read(frozen/'capture_rows.json')
    for c in captures:
        cl=classes[c['dense_id']]; c.update(original_id=cl['original_id'],label=cl['label'])
    captures += [dict(clip_id=clip,partition=part,dense_id=dense,original_id=classes[dense]['original_id'],
                     label=classes[dense]['label'],reason='eligible')
                 for clip,part,dense in [('clips/23/6.MOV','fit',23),('clips/57/9.MOV','fit',33),('clips/23/8.MOV','test',23)]]
    captures += [dict(clip_id=f'clips/{classes[i%50]["original_id"]}/synthetic-test-{i}.MOV',partition='test',
        dense_id=i%50,original_id=classes[i%50]['original_id'],label=classes[i%50]['label'],reason='eligible')
        for i in range(challenge_count-1)]
    tests=[c for c in captures if c['partition']=='test']
    if challenge_count>1:
        probs=np.zeros((len(tests),50),np.float32); probs[np.arange(len(tests)),[c['dense_id'] for c in tests]]=1
        np.save(frozen/'challenge_probabilities.npy',probs); np.save(frozen/'challenge_ids.npy',np.array([c['clip_id'] for c in tests]))
        np.save(frozen/'challenge_labels.npy',np.array([c['dense_id'] for c in tests],np.int64))
    dump(frozen/'capture_rows.json',captures)
    rows=[row(i) for i in [26,58,60,61]]+[row(26,'test')]
    rows[-1]['clip_id']='clips/26/2.MOV'; rows[-1]['literal_source_token']='clips\\26\\2.MOV'
    quarantines=['clips/26/7.MOV','clips/26/9.MOV','clips/58/6.MOV','clips/60/9.MOV','clips/61/6.MOV']
    for clip in quarantines:
        source=row(int(clip.split('/')[1]),'test' if clip=='clips/26/7.MOV' else 'train')
        source.update(clip_id=clip,literal_source_token=clip.replace('/','\\')); rows.append(source)
    for source in rows[:4]:
        source['clip_id']=source['clip_id'].replace('/1.MOV','/z.MOV'); source['literal_source_token']=source['clip_id'].replace('/','\\')
    if with_media:
        import zipfile
        media=synthetic_media(tmp_path,5)
        with zipfile.ZipFile(root/'clips.zip','w') as z:
            for source,(payload,audit) in zip(rows[:5],media):
                source.update(audit); z.writestr(source['clip_id'],payload)
    for i,source in enumerate(rows):
        if not with_media or i>=5: source.update(video_sha256=f'{i+1:064x}',decoded_bgr_sha256=f'{i+100:064x}')
    pairs=[['clips/23/6.MOV','clips/26/7.MOV'],['clips/57/9.MOV','clips/60/9.MOV'],
           ['clips/23/8.MOV','clips/26/9.MOV'],['clips/58/6.MOV','clips/61/6.MOV']]
    groups={kind:[] for kind in ['raw_bytes','decoded_pixels']}
    for pair in pairs:
        for kind,field in [('raw_bytes','video_sha256'),('decoded_pixels','decoded_bgr_sha256')]:
            digest=next(r[field] for r in rows if r['clip_id']==pair[-1]); members=[]
            for clip in pair:
                source=next((r for r in rows if r['clip_id']==clip),None)
                if source is not None:
                    source[field]=digest; members.append(dict(clip_id=clip,original_id=source['original_id'],kind='oov',partition=source['partition']))
                else:
                    known=next(c for c in captures if c['clip_id']==clip); known[field]=digest
                    members.append(dict(clip_id=clip,original_id=known['original_id'],kind='known50',partition='known50_test' if known['partition']=='test' else 'known50_train'))
            groups[kind].append(dict(members=members,sha256=digest))
    dump(frozen/'capture_rows.json',captures)
    (root/'rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    blocking=[dict(g,kind=kind) for kind,gs in groups.items() for g in gs if any(x['kind']=='known50' for x in g['members'])]
    dump(root/'duplicates.json',dict(groups=groups,blocking_groups=blocking))
    audit=m.json_read(root/'audit.json'); audit.update(rows=m.binding(root/'rows.jsonl'),duplicates=m.binding(root/'duplicates.json'),
        protocol_admission_blocked=True,blocking_duplicate_groups=6,
        partitions={part:dict(declared=sum(r['partition']==part for r in rows),decoded_ok=sum(r['partition']==part for r in rows),failures=0) for part in ['calibration','challenge']},
        calibration_ids=[r['clip_id'] for r in rows if r['partition']=='calibration'],challenge_ids=[r['clip_id'] for r in rows if r['partition']=='challenge'])
    audit['archive']=m.binding(root/'clips.zip'); audit['input_bindings'][str(root/'clips.zip')]=m.d.sha256(root/'clips.zip')
    dump(root/'audit.json',audit)
    viewroot=tmp_path/'view'; viewroot.mkdir()
    qauth=root/'quarantine-owner-authorization.json'
    dump(qauth,dict(schema_version=1,response_status='answered',owner_answer='Approve versioned quarantine and continue',
        known_validation_membership_changed=False,targets_changed=False,relabeling_allowed=False,retraining_allowed=False,
        historical_report_changes_allowed=False,linguistic_validity_established=False))
    viewrows=[dict(r,view_disposition='quarantined' if r['clip_id'] in quarantines else 'pending_neural_eligibility',
        view_reason='ambiguous_label_or_exact_duplicate_source' if r['clip_id'] in quarantines else 'source_audit_passed_neural_eligibility_unmeasured',quarantine_ground_truth_resolved=False) for r in rows]
    (viewroot/'negative_rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in viewrows))
    for partition,name in [('validation','known_validation_rows.json'),('test','known_challenge_rows.json')]:
        knownrows=[]
        for c in sorted([c for c in captures if c['partition']==partition],key=lambda c:c['clip_id']):
            v=dict(clip_id=c['clip_id'],dense_id=c['dense_id'],original_id=c['original_id'],label=c['label'],original_feature_reason=c['reason'],view_disposition='unchanged')
            if partition=='test': v.update(view_disposition='quarantined' if c['clip_id']=='clips/23/8.MOV' else 'historical_eligible_cached_output_candidate',
                view_reason='ambiguous_label_exact_source_copy' if c['clip_id']=='clips/23/8.MOV' else 'historically_exposed_known_challenge')
            knownrows.append(v)
        dump(viewroot/name,knownrows)
    # Match the supplied schema; only synthetic cardinalities differ.
    view=dict(schema_version=1,status='frozen_quarantine_view',live_ready=False,targets_changed=False,
        known_validation_membership_changed=False,known_validation_conflict_ids=[],
        original_source_audit_not_requalified_or_rewritten=True,original_splits_labels_weights_and_historical_reports_changed=False,
        actual_classifier_or_detector_extraction=False,annotation_or_signer_truth_inferred=False,
        linguistic_validity_established=False,fresh_untouched_holdout=False,
        qualification_scope='metadata_exclusion_only_pending_consumer_review_and_neural_eligibility',
        selection_basis='source_byte_and_full_decoded_pixel_identity_only_before_any_new_neural_observations_or_scores',
        source_audit_original_disposition='complete_with_protocol_admission_blocked_by_exact_duplicate_groups',
        quarantined_oov_ids=quarantines,quarantined_known_challenge_ids=['clips/23/8.MOV'],historical_fit_ids_flagged_only=['clips/23/6.MOV','clips/57/9.MOV'],
        files={n:m.binding(viewroot/n) for n in ['negative_rows.jsonl','known_validation_rows.json','known_challenge_rows.json']},
        input_bindings={str(path):m.d.sha256(path) for path in [root/'audit.json',root/'rows.jsonl',root/'duplicates.json',root/'authorization.json',qauth,frozen/'labels.json',frozen/'capture_rows.json']},
        inherited_fixed_targets=m.json_read(root/'authorization.json')['approved_offline_targets'],
        known_validation=dict(declared=50,eligible_unchanged=50,quarantined=0),
        known_challenge=dict(declared=challenge_count,original_feature_eligible=challenge_count,quarantined=1,remaining_cached_output_candidates=challenge_count-1,historical_test_stays_exploratory=True),
        negative_partitions={part:dict(declared=sum(r['partition']==part for r in rows),quarantined=sum(r['partition']==part and r['clip_id'] in quarantines for r in rows),
            remaining_source_candidates=sum(r['partition']==part and r['clip_id'] not in quarantines for r in rows),remaining_publisher_label_count=len({r['original_id'] for r in rows if r['partition']==part and r['clip_id'] not in quarantines}),
            minimum_remaining_label_source_count=1,neural_eligible=None,policy_rejected=None,false_accept_rate=None) for part in ['calibration','challenge']})
    dump(viewroot/'manifest.json',view)
    return root,viewroot/'manifest.json'


def test_quarantine_skips_payloads_and_pilot_selects_before_observation(tmp_path):
    m=module(); root,view=fixture_quarantine(tmp_path,with_media=True)
    m.prepare(source_audit=root/'audit.json',authorization=root/'authorization.json',phase4_campaign=root/'phase4',
        quarantine_view=view,output=tmp_path/'approved',_synthetic=True)
    protocol=tmp_path/'approved/protocol.json'; p=m.read_protocol(protocol,allow_synthetic=True)
    pilot=m.partition_rows(p['rows'],'pilot')
    assert len(pilot)==4 and all(r['view_disposition']!='quarantined' for r in pilot), 'pilot selected quarantined source'
    assert all(r['clip_id'].endswith('/z.MOV') for r in pilot)
    SyntheticDetector.instances=[]; out=tmp_path/'negatives'
    result=m.extract(protocol=protocol,mode='calibration',output=out,_detector_factory=SyntheticDetector)
    assert result['qualified'] and result['counts']['declared']==8
    assert result['counts']['quarantined']==4 and result['counts']['source_candidates']==4 and result['counts']['eligible']==4
    assert len(SyntheticDetector.instances)==4
    _,_,ids,ledger=m.read_bundle(out,protocol=protocol,mode='calibration',allow_synthetic=True)
    assert len(ids)==4
    excluded=[r for r in ledger if r['status']=='quarantined']; assert len(excluded)==4
    assert all(r['raw_file'] is None and r['capture'] is None and r['reason']=='ambiguous_label_or_exact_duplicate_source' for r in excluded)
    # Quarantined members do not even exist in the synthetic ZIP; touching one would fail the whole extraction.
    pilot_out=tmp_path/'pilot'
    pm=m.extract(protocol=protocol,mode='pilot',output=pilot_out,_detector_factory=SyntheticDetector)
    assert pm['qualified'] is False and pm['counts']['quarantined']==4 and len(SyntheticDetector.instances)==8
    assert len([json.loads(line) for line in (pilot_out/'rows.jsonl').read_text().splitlines() if json.loads(line)['status']=='quarantined'])==4


def test_explicit_owner_view_admits_blocked_audit_without_rewriting_it(tmp_path):
    m=module(); root,view=fixture_quarantine(tmp_path); before=(root/'audit.json').read_bytes()
    assert 'quarantine_view' in __import__('inspect').signature(m.prepare).parameters, 'explicit quarantine interface missing'
    out=tmp_path/'approved'
    m.prepare(source_audit=root/'audit.json',authorization=root/'authorization.json',phase4_campaign=root/'phase4',
              quarantine_view=view,output=out,_synthetic=True)
    p=m.read_protocol(out/'protocol.json',allow_synthetic=True)
    assert p['quarantine_view']==m.binding(view)
    assert sum(r['view_disposition']=='quarantined' for r in p['rows'])==5
    assert (root/'audit.json').read_bytes()==before
    with pytest.raises(ValueError): m.prepare(source_audit=root/'audit.json',authorization=root/'authorization.json',
        phase4_campaign=root/'phase4',output=tmp_path/'no-view',_synthetic=True)


@pytest.mark.parametrize('mutation',['extra','omitted','validation','partition','label','substitution','fit_flag','duplicate'])
def test_quarantine_rebound_digest_mutations_use_healthy_current_source(tmp_path,mutation):
    m=module(); root,view=fixture_quarantine(tmp_path)
    m.prepare(source_audit=root/'audit.json',authorization=root/'authorization.json',phase4_campaign=root/'phase4',
        quarantine_view=view,output=tmp_path/'approved',_synthetic=True)
    protocol=tmp_path/'approved/protocol.json'; healthy=m.read_protocol(protocol,allow_synthetic=True)
    manifest=m.json_read(view)
    if mutation in ['extra','omitted','partition','label','substitution']:
        path=Path(manifest['files']['negative_rows.jsonl']['path'])
        rows=[json.loads(l) for l in path.read_text().splitlines()]
        target=next(r for r in rows if r['view_disposition']==('quarantined' if mutation=='omitted' else 'pending_neural_eligibility'))
        if mutation=='extra': target['view_disposition']='quarantined'
        elif mutation=='omitted': target['view_disposition']='pending_neural_eligibility'
        elif mutation=='partition': target['partition']='challenge'
        elif mutation=='label': target['label']='NOT THE PUBLISHER LABEL'
        else: target['clip_id']='clips/26/substituted.MOV'
        path.write_text(''.join(json.dumps(r)+'\n' for r in rows)); manifest['files']['negative_rows.jsonl']=m.binding(path)
    elif mutation=='validation':
        path=Path(manifest['files']['known_validation_rows.json']['path']); rows=m.json_read(path)
        rows[0]['view_disposition']='quarantined'; dump(path,rows); manifest['files'][path.name]=m.binding(path)
    elif mutation=='fit_flag': manifest['historical_fit_ids_flagged_only']=[]
    else:
        path=root/'duplicates.json'; dup=m.json_read(path); dup['groups']['raw_bytes'].pop(); dump(path,dup)
        audit=m.json_read(root/'audit.json'); audit['duplicates']=m.binding(path); dump(root/'audit.json',audit)
        manifest['input_bindings'][str(path)]=m.d.sha256(path)
        manifest['input_bindings'][str(root/'audit.json')]=m.d.sha256(root/'audit.json')
        healthy['audit']=m.binding(root/'audit.json')
    dump(view,manifest); healthy['quarantine_view']=m.binding(view); dump(protocol,healthy)
    with pytest.raises(ValueError): m.read_protocol(protocol,allow_synthetic=True)


@pytest.mark.parametrize('token',[r'clips\26\1.MOV',r'clips\\26\\1.MOV'])
def test_literal_publisher_separator_spellings_are_preserved_not_repaired(token):
    m=module(); source=row(26); source['literal_source_token']=token
    assert m.validate_rows([source],[])==[source]
    for bad in [token.replace('26','026'),token.replace('clips','other'),r'clips\\26\1.MOV']:
        with pytest.raises(ValueError): m.validate_rows([dict(source,literal_source_token=bad)],[])


def test_separate_candidate_contract_is_bound_and_semantically_checked(tmp_path):
    m=module(); protocol=fixture_protocol(tmp_path); p=m.read_protocol(protocol,allow_synthetic=True)
    assert 'candidate-contract.json' in p['frozen'], 'separate accepted contract omitted'
    contract=Path(p['frozen']['candidate-contract.json']['path']); original=m.json_read(contract)
    for key,value in [('dtype','float64'),('input_shape',[None,30,1589]),('ordered_classes',list(reversed(p['classes']))),
                      ('policy',dict(original['policy'],decision='rejection_already_calibrated'))]:
        dump(contract,dict(original,**{key:value}))
        changed=dict(p); changed['frozen']=dict(p['frozen'],**{'candidate-contract.json':m.binding(contract)})
        dump(protocol,changed)
        with pytest.raises(ValueError): m.read_protocol(protocol,allow_synthetic=True)
    dump(contract,original); dump(protocol,p)
    assert m.read_protocol(protocol,allow_synthetic=True)==p


def test_protocol_bindings_synthetic_not_cli_admitted_and_tamper(tmp_path):
    m=module(); assert hasattr(m,'prepare'), 'source-bound protocol preparation missing'
    protocol=fixture_protocol(tmp_path)
    p=m.read_protocol(protocol,allow_synthetic=True)
    assert p['evidence_kind']=='synthetic_in_process' and p['live_ready'] is False
    assert len(p['classes'])==50 and len(p['rows'])==4
    with pytest.raises(ValueError): m.read_protocol(protocol)
    bound=Path(p['audit']['path']); original=bound.read_bytes(); bound.write_bytes(original+b' ')
    with pytest.raises(ValueError): m.read_protocol(protocol,allow_synthetic=True)
    bound.write_bytes(original)
    # A residual failure blocks an otherwise healthy protocol.
    dump(protocol.parent/'failure.json',{'status':'failed'})
    with pytest.raises(ValueError): m.read_protocol(protocol,allow_synthetic=True)


def synthetic_media(root,count=4):
    import cv2 as cv
    import hashlib
    result=[]
    for k in range(count):
        path=root/f'invented-{k}.avi'
        writer=cv.VideoWriter(str(path),cv.VideoWriter_fourcc(*'MJPG'),15,(32,24))
        assert writer.isOpened()
        for j in range(10): writer.write(np.full((24,32,3),(k*40+j),np.uint8))
        writer.release(); cap=cv.VideoCapture(str(path)); h=hashlib.sha256(); n=0; shapes=set()
        try:
            while True:
                ok,bgr=cap.read()
                if not ok: break
                n+=1; shapes.add(tuple(bgr.shape))
                h.update(np.array(bgr.shape,dtype='<i4').tobytes()); h.update(np.ascontiguousarray(bgr).tobytes())
        finally: cap.release()
        payload=path.read_bytes()
        result.append((payload,dict(video_bytes=len(payload),video_sha256=hashlib.sha256(payload).hexdigest(),
            decoded_frames=n,decoded_bgr_sha256=h.hexdigest(),shapes=[list(s) for s in sorted(shapes)])))
    return result


class SyntheticDetector:
    instances=[]
    missing_face=False
    throw=False
    def __init__(self,path):
        self.closed=False; self.seen=[]; self.instances.append(self)
    def detect(self,rgb,timestamp):
        from training.holistic_migration.features import RawFrame
        assert rgb.shape==(360,640,3) and rgb.dtype==np.uint8
        self.seen.append(timestamp)
        if self.throw: raise RuntimeError('injected detector failure')
        pose=np.zeros((33,4),np.float64); pose[:,3]=1; pose[11,0]=.2; pose[12,0]=.8
        hand=np.zeros((21,3),np.float64); face=None if self.missing_face else np.zeros((478,3),np.float64)
        return RawFrame(timestamp,pose,hand,None,face)
    def close(self): self.closed=True


def test_streamed_video_raw_tensor_parity_and_pilot_firewall(tmp_path):
    m=module(); assert hasattr(m,'extract'), 'streamed extraction missing'
    media=synthetic_media(tmp_path); protocol=fixture_protocol(tmp_path,media)
    SyntheticDetector.instances=[]
    out=tmp_path/'calibration'
    result=m.extract(protocol=protocol,mode='calibration',output=out,_detector_factory=SyntheticDetector)
    assert result['status']=='complete' and result['qualified'] is True
    assert result['counts']==dict(declared=2,eligible=2,quarantined=0,source_candidates=2,source_failures=0,capture_exclusions=0,errors=0)
    assert len(SyntheticDetector.instances)==2 and all(d.closed for d in SyntheticDetector.instances)
    admitted=m.read_bundle(out,protocol=protocol,mode='calibration',allow_synthetic=True)
    assert admitted[1].shape==(2,30,1588) and admitted[1].dtype==np.float32
    assert admitted[2].tolist()==['clips/51/1.MOV','clips/52/1.MOV']
    for r in admitted[3]:
        raw=m.d.read_raw(out/r['raw_file'],r['raw_sha256'])
        from training.holistic_migration.face_features import prepare_capture
        assert np.array_equal(prepare_capture(raw).tensor,admitted[1][admitted[2].tolist().index(r['clip_id'])])
        assert r['presence']['face']==10 and r['capture']['source_observation_count']==10
    pilot=tmp_path/'pilot'
    assert m.extract(protocol=protocol,mode='pilot',output=pilot,_detector_factory=SyntheticDetector)['qualified'] is False
    with pytest.raises(ValueError): m.read_bundle(pilot,protocol=protocol,mode='calibration',allow_synthetic=True)
    before=len(SyntheticDetector.instances)
    with pytest.raises(ValueError): m.extract(protocol=protocol,mode='challenge',output=tmp_path/'challenge',_detector_factory=SyntheticDetector)
    assert len(SyntheticDetector.instances)==before and not (tmp_path/'challenge').exists()



def test_public_prepare_requires_explicit_approved_view_before_evidence_binding(tmp_path,monkeypatch):
    m=module(); called=[]
    def forbidden(*args,**kwargs): called.append(True); raise AssertionError('no-view public path attempted binding')
    monkeypatch.setattr(m,'binding',forbidden)
    with pytest.raises(ValueError,match='approved quarantine view'): m.prepare(source_audit=tmp_path/'audit',
        authorization=tmp_path/'authorization',phase4_campaign=tmp_path/'campaign',output=tmp_path/'denied')
    assert not called and not (tmp_path/'denied').exists()


def test_blocked_audit_denied_before_any_frozen_model_admission(tmp_path,monkeypatch):
    m=module(); protocol=fixture_protocol(tmp_path); p=m.read_protocol(protocol,allow_synthetic=True)
    ap=Path(p['audit']['path']); audit=m.json_read(ap)
    audit.update(protocol_admission_blocked=True,blocking_duplicate_groups=6); dump(ap,audit)
    called=[]
    def forbidden(*args,**kwargs): called.append(True); raise AssertionError('frozen model admission reached blocked source gate')
    monkeypatch.setattr(m,'_frozen_files',forbidden)
    with pytest.raises(ValueError,match='source audit'):
        m.prepare(source_audit=ap,authorization=p['authorization']['path'],phase4_campaign=ap.parent/'absent',output=tmp_path/'denied',_synthetic=True)
    assert called==[] and not (tmp_path/'denied').exists()


def test_protocol_readback_failure_retains_barrier_without_secondary_markers(tmp_path,monkeypatch):
    m=module(); base=fixture_protocol(tmp_path); p=m.read_protocol(base,allow_synthetic=True)
    root=Path(p['audit']['path']).parent; original=m.read_protocol; target=tmp_path/'publication'
    def fail(path,**kwargs):
        result=original(path,**kwargs)
        if Path(path).parent==target: raise OSError('protocol qualification readback unavailable')
        return result
    monkeypatch.setattr(m,'read_protocol',fail); monkeypatch.setattr(m,'failure',lambda *a:None)
    with pytest.raises(OSError): m.prepare(source_audit=root/'audit.json',authorization=root/'authorization.json',
        phase4_campaign=root/'phase4',output=target,_synthetic=True)
    monkeypatch.setattr(m,'read_protocol',original)
    with pytest.raises(ValueError): m.read_protocol(target/'protocol.json',allow_synthetic=True)


def test_parent_audit_row_timestamp_schema_and_nonfinite_json(tmp_path):
    m=module(); r=row(); r['timestamp_source']='actual_CAP_PROP_POS_MSEC'
    assert m.validate_rows([r],[dict(original_id=0,label='KNOWN')])==[r]
    path=tmp_path/'nonfinite.json'; path.write_text('{"value":1e999}')
    with pytest.raises(ValueError): m.json_read(path)


@pytest.mark.parametrize('fault',['extra_key','face_count','source_failure','reason','nan','duplicate_key'])
def test_bundle_rebound_ledger_schema_and_finite_coverage(tmp_path,fault):
    m=module(); protocol=fixture_protocol(tmp_path,synthetic_media(tmp_path)); out=tmp_path/'negative'
    m.extract(protocol=protocol,mode='calibration',output=out,_detector_factory=SyntheticDetector)
    _,_,_,ledger=m.read_bundle(out,protocol=protocol,mode='calibration',allow_synthetic=True)
    if fault=='extra_key': ledger[0]['unapproved']=True
    elif fault=='face_count': ledger[0]['face_cardinality']={'478':999}
    elif fault=='source_failure': ledger[0]['status']='source_failure'
    elif fault=='reason': ledger[0]['source']['fps']=float('nan')
    elif fault=='nan': ledger[0]['face_cardinality']={'478':float('nan')}
    text=''.join(json.dumps(r)+'\n' for r in ledger)
    if fault=='duplicate_key': text=text.replace('"face_cardinality":', '"face_cardinality":{},"face_cardinality":',1)
    (out/'rows.jsonl').write_text(text)
    complete=m.json_read(out/'complete.json'); complete['files']['rows.jsonl']=m.d.sha256(out/'rows.jsonl'); dump(out/'complete.json',complete)
    with pytest.raises(ValueError): m.read_bundle(out,protocol=protocol,mode='calibration',allow_synthetic=True)


@pytest.mark.parametrize('fault',['nan','duplicate_key','nonfinite_timestamp','label_change','view_extra','audit_extra'])
def test_original_audit_and_approved_view_strict_schema_with_rebound_inputs(tmp_path,fault):
    m=module(); root,view=fixture_quarantine(tmp_path)
    if fault in ['view_extra','audit_extra']:
        path=view if fault=='view_extra' else root/'audit.json'; obj=m.json_read(path); obj['unapproved']=True; dump(path,obj)
    else:
        path=root/'rows.jsonl'; rows=[json.loads(l) for l in path.read_text().splitlines()]
        if fault=='nan': rows[0]['fps']=float('nan')
        elif fault=='nonfinite_timestamp': rows[0]['first_timestamp_ms']=float('inf')
        elif fault=='label_change': rows[0]['label']='CHANGED LABEL SAME ORIGINAL ID'
        text=''.join(json.dumps(r)+'\n' for r in rows)
        if fault=='duplicate_key': text=text.replace('"status":','"status":"error","status":',1)
        path.write_text(text)
        audit=m.json_read(root/'audit.json'); audit['rows']=m.binding(path); dump(root/'audit.json',audit)
    if fault!='view_extra':
        manifest=m.json_read(view); manifest['input_bindings'][str(root/'audit.json')]=m.d.sha256(root/'audit.json')
        manifest['input_bindings'][str(root/'rows.jsonl')]=m.d.sha256(root/'rows.jsonl'); dump(view,manifest)
    with pytest.raises(ValueError): m.prepare(source_audit=root/'audit.json',authorization=root/'authorization.json',
        phase4_campaign=root/'phase4',quarantine_view=view,output=tmp_path/'denied',_synthetic=True)


@pytest.mark.parametrize('value',[False,0.0])
def test_ordered_label_integer_schema_not_python_equality(tmp_path,value):
    m=module(); protocol=fixture_protocol(tmp_path); p=m.read_protocol(protocol,allow_synthetic=True)
    classes=p['classes']; classes[0]['dense_id']=value
    labels=Path(p['frozen']['labels.json']['path']); dump(labels,classes); p['frozen']['labels.json']=m.binding(labels)
    contract=Path(p['frozen']['candidate-contract.json']['path']); c=m.json_read(contract); c['ordered_classes']=classes
    dump(contract,c); p['frozen']['candidate-contract.json']=m.binding(contract); dump(protocol,p)
    with pytest.raises(ValueError): m.read_protocol(protocol,allow_synthetic=True)


@pytest.mark.parametrize('fault',['extra_frames','face_cardinality','unknown_member','oversized_header'])
def test_raw_bounds_are_checked_before_codec_allocation(tmp_path,monkeypatch,fault):
    m=module(); protocol=fixture_protocol(tmp_path,synthetic_media(tmp_path)); out=tmp_path/'negative'
    m.extract(protocol=protocol,mode='calibration',output=out,_detector_factory=SyntheticDetector)
    _,_,_,ledger=m.read_bundle(out,protocol=protocol,mode='calibration',allow_synthetic=True)
    path=out/ledger[0]['raw_file']
    with np.load(path,allow_pickle=False) as z: values={k:z[k] for k in z.files}
    if fault=='extra_frames': values['timestamps']=np.arange(100,dtype=np.int64)
    elif fault=='face_cardinality': values['face_values']=np.zeros((478*10+1,3),np.float64)
    elif fault=='unknown_member': values['unexpected']=np.zeros(1,np.uint8)
    if fault=='oversized_header':
        import zipfile,struct
        with zipfile.ZipFile(path,'w') as z:
            for name,a in values.items():
                import io
                stream=io.BytesIO(); np.save(stream,a,allow_pickle=False); payload=stream.getvalue()
                if name=='timestamps': payload=b'\x93NUMPY\x01\x00'+struct.pack('<H',65535)+b' '*65535
                z.writestr(name+'.npy',payload)
    else:
        with path.open('wb') as stream: np.savez_compressed(stream,**values)
    ledger[0]['raw_sha256']=m.d.sha256(path)
    (out/'rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in ledger))
    complete=m.json_read(out/'complete.json'); complete['files']['rows.jsonl']=m.d.sha256(out/'rows.jsonl'); dump(out/'complete.json',complete)
    def forbidden(*a,**kw): raise AssertionError('unbounded codec allocation reached before raw admission')
    monkeypatch.setattr(m.d,'read_raw',forbidden)
    with pytest.raises(ValueError,match='raw'): m.read_bundle(out,protocol=protocol,mode='calibration',allow_synthetic=True)


@pytest.mark.parametrize('missing,throws',[(True,False),(False,True)])
def test_missingness_and_cleanup_keep_failures_out_of_predictions(tmp_path,monkeypatch,missing,throws):
    m=module(); protocol=fixture_protocol(tmp_path,synthetic_media(tmp_path))
    monkeypatch.setattr(SyntheticDetector,'missing_face',missing); monkeypatch.setattr(SyntheticDetector,'throw',throws)
    SyntheticDetector.instances=[]; out=tmp_path/'negative'
    if throws:
        with pytest.raises(ValueError,match='extraction errors'): m.extract(protocol=protocol,mode='calibration',output=out,_detector_factory=SyntheticDetector)
        assert (out/'failure.json').is_file() and (out/'incomplete.json').is_file()
    else:
        result=m.extract(protocol=protocol,mode='calibration',output=out,_detector_factory=SyntheticDetector)
        assert result['qualified'] is False and result['missing_eligible_classes']==[51,52]
        assert result['counts']['eligible']==0 and result['counts']['capture_exclusions']==2
    assert all(d.closed for d in SyntheticDetector.instances) and len(SyntheticDetector.instances)==2
    assert not list(out.glob('source-*'))
    with pytest.raises(ValueError): m.read_bundle(out,protocol=protocol,mode='calibration',allow_synthetic=True)
