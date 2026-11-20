"""Isolated publisher-label OOV protocol and extraction; no import-time native work."""
from pathlib import Path
import re
import numpy as np
from . import dataset as d

ROW_KEYS = {'clip_id','literal_source_token','original_id','label','category','official_split',
            'partition','video_bytes','video_sha256','decoded_frames','decoded_bgr_sha256',
            'shapes','status','failure'}


def validate_rows(rows, known):
    """Validate literal publisher identities, without repairing malformed tokens."""
    if type(rows) is not list or not rows:
        raise ValueError('nonempty source rows required')
    ids = set(); known_ids = {c['original_id'] for c in known}; known_labels = {c['label'] for c in known}
    for r in rows:
        extra = {'signer_id','annotation_scope','archive_crc32','declared_frames','fps','backend',
                 'first_timestamp_ms','last_timestamp_ms','timestamp_source','error_type','failure_reason'}
        required = {'clip_id','literal_source_token','original_id','label','category','official_split','partition','status'}
        if type(r) is not dict or not required<=set(r) or set(r)-ROW_KEYS-extra:
            raise ValueError('exact OOV row schema required')
        i = d.integer(r['original_id'],'original_id')
        clip = r['clip_id']
        if (type(clip) is not str or re.fullmatch(r'clips/[0-9]+/[A-Za-z0-9_.-]+',clip) is None
                or clip.split('/')[1] != str(i) or clip.split('/')[-1] in ['.','..'] or clip in ids):
            raise ValueError('invalid/duplicate canonical source ID')
        ids.add(clip)
        if r['literal_source_token'] not in [clip.replace('/',chr(92)),clip.replace('/',chr(92)*2)]:
            raise ValueError('literal publisher source token mismatch')
        if any(type(r[k]) is not str or not r[k] for k in ['label','category']):
            raise ValueError('literal publisher label/category required')
        if i in known_ids or r['label'] in known_labels:
            raise ValueError('OOV overlaps known outputs')
        if r['official_split'] not in ['train','test']:
            raise ValueError('invalid publisher split')
        d.same(r['partition'],'calibration' if r['official_split']=='train' else 'challenge','publisher partition')
        if r['status']!='source_error':
            d.integer(r.get('video_bytes'),'video_bytes',1); d.hash_value(r.get('video_sha256'),'source')
        if r['status']=='ok':
            d.integer(r['decoded_frames'],'decoded_frames',1); d.hash_value(r['decoded_bgr_sha256'],'pixels')
            if type(r['shapes']) is not list or not r['shapes']:
                raise ValueError('decoded shapes required')
            for s in r['shapes']:
                if type(s) is not list or len(s)!=3 or s[2]!=3 or any(type(v) is not int or v<1 for v in s):
                    raise ValueError('invalid BGR shape')
            d.same(r.get('failure'),None,'successful source failure')
        elif r['status'] in ['decode_error','source_error']:
            failure=r.get('failure_reason',r.get('failure'))
            if type(failure) is not str or not failure:
                raise ValueError('explicit source/decode failure required')
            for k in ['decoded_frames','decoded_bgr_sha256','shapes']:
                d.same(r.get(k),None,'unavailable '+k)
        else:
            raise ValueError('unrecognized source status')
    return sorted(rows,key=lambda r:r['clip_id'])


def partition_rows(rows, mode, requested_ids=None):
    """Metadata-only selection; never accept challenge IDs through calibration."""
    if mode not in ['pilot','calibration','challenge']:
        raise ValueError('invalid extraction mode')
    selected = sorted([r for r in rows if r['partition']==('challenge' if mode=='challenge' else 'calibration')],key=lambda r:r['clip_id'])
    if mode=='pilot':
        selected=[r for r in selected if r.get('view_disposition')!='quarantined']
        selected = sorted({r['original_id']:next(x for x in selected if x['original_id']==r['original_id']) for r in selected}.values(),key=lambda r:r['clip_id'])
    if requested_ids is not None:
        d.same(requested_ids,[r['clip_id'] for r in selected],'fixed ordered partition membership')
    return selected


def require_real(protocol):
    d.same(protocol.get('evidence_kind'),'public_source','CLI public provenance')


# These are independent, immutable Phase4/owner/public-source anchors, not caller claims.
DATA = d.REPO.parent/'holistic-migration-data'
STAGE = DATA/'evidence/rejection-calibration-public-v1'
PHASE4 = DATA/'evidence/phase-4-20261116'
MODEL_HASH = 'ea50489a27353cbf4f4e9b53b1a6252fa7c5c6a9f0021660347f7dcc1b1cda47'
AUTH_HASH = '192336fdbd0b08bd89f1ab082ee640331c46e5d792689a093f120eaf4a2c01b0'
ARCHIVE_HASH = 'c048c0820be1621101dfedeabb76a9fbfca76ed2868eebe23b4cb90d5c748463'
TARGETS = dict(known_minimum=[9,10],oov_maximum=[1,20])


def json_read(path):
    return json_value(d.safe_path(path,must_exist=True).read_text())


def json_value(text):
    """Reject duplicate keys and JSON NaN/Infinity, including nested values."""
    import json
    def unique(pairs):
        result={}
        for k,v in pairs:
            if k in result: raise ValueError('duplicate JSON key')
            result[k]=v
        return result
    def invalid(v): raise ValueError('nonfinite JSON value')
    def finite_float(value):
        number=float(value)
        if not np.isfinite(number): raise ValueError('nonfinite JSON number')
        return number
    return json.loads(text,object_pairs_hook=unique,parse_constant=invalid,parse_float=finite_float)


def binding(path):
    path=d.safe_path(path,must_exist=True)
    return dict(path=str(path),sha256=d.sha256(path))


def check_binding(record):
    if type(record) is not dict or set(record)!={'path','sha256'}:
        raise ValueError('exact path/hash binding required')
    d.hash_value(record['sha256'],'binding')
    p=d.safe_path(record['path'],must_exist=True)
    d.same(d.sha256(p),record['sha256'],'current bound file')
    return p


def implementation_binding():
    names=['oov_dataset.py','rejection.py','rejection_run.py','features.py','face_features.py',
           'sequence.py','detector.py','dataset.py','extract.py','face_augmentation.py']
    # Absent not-yet-built companion modules cannot produce a usable final protocol.
    return {n:d.sha256(Path(__file__).parent/n) for n in names if (Path(__file__).parent/n).is_file()}


def runtime_binding():
    import importlib.metadata
    return dict(capture=d.runtime_binding(),packages={n:importlib.metadata.version(n) for n in ['tensorflow','keras']})


def barriers(root, names=('failure.json','incomplete.json')):
    import os
    root=d.safe_path(root,must_exist=True)
    if any(os.path.lexists(root/n) for n in names):
        raise ValueError('failed/incomplete target cannot qualify')


def reserve(output, inputs=()):
    """Fresh, nonoverlapping external-stage directory; reject symlink ancestors."""
    p=d.safe_path(output)
    if STAGE not in p.parents or p==STAGE:
        raise ValueError('output must be below approved external stage')
    for source in inputs:
        s=d.safe_path(source)
        if p==s or s in p.parents or p in s.parents:
            raise ValueError('output overlaps input')
    if p.exists() or not p.parent.is_dir(): raise ValueError('fresh output with existing parent required')
    p.mkdir()
    d.write_json(p/'incomplete.json',dict(status='incomplete'))
    return p


def failure(output, exc, phase):
    try:
        d.write_json(output/'failure.json',dict(status='failed',phase=phase,error_type=type(exc).__name__,detail=str(exc)))
    except Exception:
        pass  # Never replace the primary error with secondary diagnostic I/O.


def publish(path, value):
    """Exclusive JSON publication and exact readback, no overwrite/repair inference."""
    d.write_json(path,value)
    d.same(json_read(path),value,'publication readback')


def _frozen_files(campaign, synthetic):
    campaign=d.safe_path(campaign,must_exist=True)
    if synthetic:
        files={n:binding(campaign/n) for n in ['labels.json','candidate-contract.json','model.keras','capture_rows.json',
            'validation_probabilities.npy','validation_ids.npy','selection.json','phase4-offline-acceptance.json']}
    else:
        d.same(str(campaign),str(PHASE4/'all50-campaign-v1'),'accepted Phase4 campaign')
        fixed={
            'candidate-contract.json':(campaign/'candidate-contract.json','dff68ab114fcfdff93af4cd11ea9976e888e621d0724e60929bb68e680a3234c'),
            'labels.json':(campaign/'labels.json','b634bdeb19b2fbf7482bdd46f791f16725d6510275e5d552f29f3bfc7c628eb6'),
            'phase4-offline-acceptance.json':(campaign/'phase4-offline-acceptance.json','0ced5d32a32b36f2b9deae212fbbdfc976eeb1d1aad80ddb79ddef22552db9cb'),
            'selection.json':(PHASE4/'full-source-v1/selection.json','fbfa41b5f597a701d93df07c09593c4759b0f12604bd1c17d2c565cfbda98089'),
            'model.keras':(PHASE4/'full-source-v1/model.keras',MODEL_HASH),
            'validation_probabilities.npy':(PHASE4/'full-source-v1/validation_probabilities.npy','c6b88003c93802432b0866bd35a18091a219dc20395f6c39fc3900bbd92a160b'),
            'validation_ids.npy':(PHASE4/'full-source-v1/validation_ids.npy','15305b2980c7fd71293500f0e9d9346047edf2f68ebc7de9fafd21ee2d12f70f')}
        files={n:dict(path=str(p),sha256=h) for n,(p,h) in fixed.items()}
        for ref in files.values(): check_binding(ref)
        bundle=DATA/'hm1588-canonical-bundle-20261116-v1'
        manifest=binding(bundle/'data_manifest.json')
        d.same(manifest['sha256'],'71c644b4de78f7031f96f7b25b1d5766f18fa611c33ad12f2a40a353b1c6c19a','accepted known manifest')
        files['data_manifest.json']=manifest
        digest=json_read(bundle/'data_manifest.json')['artifacts']['capture_rows.json']['sha256']
        files['capture_rows.json']=dict(path=str(bundle/'capture_rows.json'),sha256=digest)
        check_binding(files['capture_rows.json'])
        files['detector.task']=dict(path=str(DATA/'holistic_landmarker.task'),sha256='e2dab61191e2dcd0a15f943d8e3ed1dce13c82dfa597b9dd39f562975a50c3f8')
        check_binding(files['detector.task'])
    if synthetic:
        for name in ['challenge_probabilities.npy','challenge_ids.npy','challenge_labels.npy']:
            if (campaign/name).exists(): files[name]=binding(campaign/name)
    return files


def validate_contract(files, classes):
    from .rejection import class_declarations
    class_declarations(classes)
    contract=json_read(check_binding(files['candidate-contract.json']))
    expected=dict(dtype='float32',feature_version='hm1588-v1',input_shape=[None,30,1588],
        output_shape=[None,50],live_ready=False,ordered_classes=classes,
        policy=dict(decision='closed_set_argmax',live_ready=False,outputs=50,schema_version=1,
                    unknown_rejection='unmeasured_no_observed_validation_negatives'))
    if set(contract)!=set(expected)|{'contract_file','contract_sha256','detector_source_graph_sha256'}:
        raise ValueError('exact accepted candidate contract schema required')
    for k,v in expected.items(): d.same(contract[k],v,'baseline candidate contract '+k)
    check_binding(dict(path=contract['contract_file'],sha256=contract['contract_sha256']))
    d.hash_value(contract['detector_source_graph_sha256'],'baseline detector source graph')
    return contract


def _publisher_membership(rows, classes):
    """Read original CSV metadata only; no challenge video/array/model access."""
    import csv
    labels=list(csv.DictReader((DATA/'labels.csv').open(encoding='utf-8-sig',newline='')))
    class_map={int(r['id']):(r['label'],r['category']) for r in labels}
    if len(class_map)!=105: raise ValueError('original105 publisher labels required')
    for c in classes:
        d.same([c['label'],c['category']],list(class_map[c['original_id']]),'literal known publisher label')
    known={c['original_id'] for c in classes}
    expected={}
    for split in ['train','test']:
        with (DATA/(split+'.csv')).open(encoding='utf-8-sig',newline='') as stream:
            for r in csv.DictReader(stream):
                i=int(r['id_label'])
                if i in known: continue
                token=r['vid_path']
                match=re.fullmatch(r'clips(\\{1,2})([0-9]+)\1([A-Za-z0-9_.-]+)',token)
                if match is None: raise ValueError('invalid literal publisher token')
                clip='clips/'+match[2]+'/'+match[3]
                if clip in expected: raise ValueError('duplicate original publisher source')
                expected[clip]=dict(literal_source_token=token,original_id=i,label=r['label'],category=r['category'],official_split=split)
    if set(expected)!={r['clip_id'] for r in rows}: raise ValueError('exact original OOV membership required')
    for r in rows:
        for k,v in expected[r['clip_id']].items(): d.same(r[k],v,'original publisher '+k)
        d.same([r['label'],r['category']],list(class_map[r['original_id']]),'publisher label/category')
    d.same([len(rows),len({r['original_id'] for r in rows})],[1114,55],'original OOV coverage')


QUARANTINE_IDS = ['clips/26/7.MOV','clips/26/9.MOV','clips/58/6.MOV','clips/60/9.MOV','clips/61/6.MOV']
KNOWN_QUARANTINE_IDS = ['clips/23/8.MOV']
FIT_FLAG_IDS = ['clips/23/6.MOV','clips/57/9.MOV']
VIEW_HASH = '2c92922faf8eb699b18d5c1b568975f228b3bcb78d469ce04f206db7e928f98c'
QUARANTINE_AUTH_HASH = '46bda9eeb117ca0ac631a1b7460f966475136dca471d2695d9f7a1cb5a9d1944'


def _source_gate(a, quarantine_view=None):
    for k,v in dict(schema_version=1,status='complete',evidence_kind='public_source_video_audit').items():
        d.same(a.get(k),v,'source audit '+k)
    if quarantine_view is None:
        d.same(a.get('blocking_duplicate_groups'),0,'source audit blockers')
        d.same(a.get('protocol_admission_blocked'),False,'source audit original gate')
    else:
        d.same(a.get('blocking_duplicate_groups'),6,'source audit original blockers')
        d.same(a.get('protocol_admission_blocked'),True,'source audit original blocked disposition')


def _quarantine_read(path, audit_path, authorization, classes, files, rows, synthetic):
    """Explicit metadata exception; original audit remains blocked, not repaired."""
    view=json_read(path)
    if not synthetic:
        d.same(binding(path),dict(path=str(STAGE/'quarantine-view-v1/manifest.json'),sha256=VIEW_HASH),'approved immutable quarantine view')
    expected=dict(schema_version=1,status='frozen_quarantine_view',live_ready=False,targets_changed=False,
        known_validation_membership_changed=False,known_validation_conflict_ids=[],
        original_source_audit_not_requalified_or_rewritten=True,original_splits_labels_weights_and_historical_reports_changed=False,
        actual_classifier_or_detector_extraction=False,annotation_or_signer_truth_inferred=False,
        linguistic_validity_established=False,fresh_untouched_holdout=False,
        qualification_scope='metadata_exclusion_only_pending_consumer_review_and_neural_eligibility',
        selection_basis='source_byte_and_full_decoded_pixel_identity_only_before_any_new_neural_observations_or_scores',
        source_audit_original_disposition='complete_with_protocol_admission_blocked_by_exact_duplicate_groups',
        quarantined_oov_ids=QUARANTINE_IDS,quarantined_known_challenge_ids=KNOWN_QUARANTINE_IDS,
        historical_fit_ids_flagged_only=FIT_FLAG_IDS)
    required=set(expected)|{'files','input_bindings','inherited_fixed_targets','known_validation','known_challenge','negative_partitions'}
    if not required<=set(view) or set(view)-required-{'created_at','limitation'}: raise ValueError('exact quarantine view schema required')
    for k,v in expected.items(): d.same(view.get(k),v,'quarantine '+k)
    audit=json_read(audit_path)
    for target in [binding(audit_path),audit['rows'],audit['duplicates'],authorization,files['labels.json'],files['capture_rows.json']]:
        d.same(view['input_bindings'].get(target['path']),target['sha256'],'quarantine original input binding')
    for target,digest in view['input_bindings'].items(): check_binding(dict(path=target,sha256=digest))
    auth_paths=[Path(p) for p in view['input_bindings'] if Path(p).name=='quarantine-owner-authorization.json']
    if len(auth_paths)!=1: raise ValueError('separate quarantine owner authorization required')
    qauth=binding(auth_paths[0])
    if not synthetic:
        d.same(qauth,dict(path=str(STAGE/'quarantine-owner-authorization.json'),sha256=QUARANTINE_AUTH_HASH),'approved quarantine owner anchor')
    answers=json_read(check_binding(qauth))
    for k,v in dict(schema_version=1,response_status='answered',owner_answer='Approve versioned quarantine and continue',
        known_validation_membership_changed=False,targets_changed=False,relabeling_allowed=False,retraining_allowed=False,
        historical_report_changes_allowed=False,linguistic_validity_established=False).items():
        d.same(answers.get(k),v,'explicit quarantine owner '+k)
    d.same(view['inherited_fixed_targets'],json_read(check_binding(authorization))['approved_offline_targets'],'unchanged approved targets')
    if set(view['files'])!={'negative_rows.jsonl','known_validation_rows.json','known_challenge_rows.json'}:
        raise ValueError('exact quarantine row files required')
    for ref in view['files'].values(): check_binding(ref)
    captures=json_read(check_binding(files['capture_rows.json']))
    by_known={c['clip_id']:c for c in captures}; by_oov={r['clip_id']:r for r in rows}
    if len(by_known)!=len(captures): raise ValueError('unique known source declarations required')
    # Derive source conflicts from BOTH byte and pixel groups, not from the caller mask.
    duplicates=json_read(check_binding(audit['duplicates']))
    conflicts=set(); fit=set(); test=set(); domains={}
    for kind,field in [('raw_bytes','video_sha256'),('decoded_pixels','decoded_bgr_sha256')]:
        for group in duplicates['groups'][kind]:
            members=group['members']; ids=tuple(sorted(m['clip_id'] for m in members))
            if len(set(ids))!=len(ids) or len(ids)<2: raise ValueError('invalid duplicate membership')
            domains.setdefault(ids,set()).add(kind)
            for member in members:
                clip=member['clip_id']; known=member['kind']=='known50'
                source=(by_known if known else by_oov).get(clip)
                if source is None: raise ValueError('unknown duplicate source')
                d.same(member['original_id'],source['original_id'],'duplicate original label identity')
                expected_partition=('known50_test' if source['partition']=='test' else 'known50_train') if known else source['partition']
                d.same(member['partition'],expected_partition,'duplicate original partition')
                d.same(group['sha256'],source[field],'duplicate source content identity')
                if known:
                    if source['partition']=='validation': raise ValueError('known validation conflict is not authorized')
                    (test if source['partition']=='test' else fit).add(clip)
                else: conflicts.add(clip)
    if any(v!={'raw_bytes','decoded_pixels'} for v in domains.values()):
        raise ValueError('quarantine requires paired byte and complete pixel identity')
    d.same(sorted(conflicts),QUARANTINE_IDS,'derived exact OOV conflicts')
    d.same(sorted(fit),FIT_FLAG_IDS,'derived historical fit flags only')
    d.same(sorted(test),KNOWN_QUARANTINE_IDS,'derived known challenge conflict')
    derived=[]
    for row in rows:
        quarantined=row['clip_id'] in conflicts
        derived.append(dict(row,view_disposition='quarantined' if quarantined else 'pending_neural_eligibility',
            view_reason='ambiguous_label_or_exact_duplicate_source' if quarantined else 'source_audit_passed_neural_eligibility_unmeasured',
            quarantine_ground_truth_resolved=False))
    actual=[json_value(line) for line in check_binding(view['files']['negative_rows.jsonl']).read_text().splitlines()]
    d.same(sorted(actual,key=lambda r:r['clip_id']),derived,'exact unchanged negative declarations and quarantine mask')
    for partition,name in [('validation','known_validation_rows.json'),('test','known_challenge_rows.json')]:
        expected_rows=[]
        for c in sorted([c for c in captures if c['partition']==partition],key=lambda c:c['clip_id']):
            cl=classes[c['dense_id']]
            value=dict(clip_id=c['clip_id'],dense_id=c['dense_id'],original_id=cl['original_id'],label=cl['label'],
                       original_feature_reason=c['reason'],view_disposition='unchanged')
            if partition=='test': value.update(view_disposition='quarantined' if c['clip_id'] in test else 'historical_eligible_cached_output_candidate',
                view_reason='ambiguous_label_exact_source_copy' if c['clip_id'] in test else 'historically_exposed_known_challenge')
            expected_rows.append(value)
        d.same(json_read(check_binding(view['files'][name])),expected_rows,'unchanged exact known '+partition+' membership')
        eligible=sum(c['original_feature_reason']=='eligible' for c in expected_rows)
        summary=(dict(declared=len(expected_rows),eligible_unchanged=eligible,quarantined=0) if partition=='validation' else
            dict(declared=len(expected_rows),original_feature_eligible=eligible,quarantined=len(test),
                 remaining_cached_output_candidates=eligible-len(test),historical_test_stays_exploratory=True))
        d.same(view['known_'+('validation' if partition=='validation' else 'challenge')],summary,'known view counts')
    for part in ['calibration','challenge']:
        declared=[r for r in derived if r['partition']==part]; remaining=[r for r in declared if r['view_disposition']!='quarantined']
        support={r['original_id']:sum(x['original_id']==r['original_id'] for x in remaining) for r in declared}
        if not support or min(support.values())<1: raise ValueError('all negative labels must retain source candidates')
        summary=dict(declared=len(declared),quarantined=len(declared)-len(remaining),remaining_source_candidates=len(remaining),
            remaining_publisher_label_count=len(support),minimum_remaining_label_source_count=min(support.values()),
            neural_eligible=None,policy_rejected=None,false_accept_rate=None)
        d.same(view['negative_partitions'][part],summary,'quarantine declared/candidate accounting')
    if not synthetic:
        d.same(view['known_validation'],dict(declared=150,eligible_unchanged=145,quarantined=0),'immutable145 known validation')
        d.same([view['known_challenge'][k] for k in ['declared','quarantined','remaining_cached_output_candidates']],[203,1,202],'known challenge quarantine scope')
    return derived,qauth


def _audit_read(path, classes, synthetic, quarantine_view=None):
    a=json_read(path)
    _source_gate(a,quarantine_view)
    required={'schema_version','status','evidence_kind','archive','rows','duplicates','decoder_control','input_bindings',
        'partitions','calibration_ids','challenge_ids','blocking_duplicate_groups','protocol_admission_blocked','runtime','recipe'}
    extras={'classes','completed_at','declared','decoded_ok','elapsed_monotonic_seconds','errors','expert_validated',
        'fresh_untouched_holdout','idle_annotated','new_neural_observations_or_scores','prior_usage_scope',
        'signer_independence','source_quality_audit_only_not_extraction_or_rejection_evidence','started_at'}
    if not required<=set(a) or set(a)-required-extras: raise ValueError('exact original source audit schema required')
    for k in ['archive','rows','duplicates','decoder_control']: check_binding(a[k])
    for path,digest in a['input_bindings'].items(): check_binding(dict(path=path,sha256=digest))
    rows=[json_value(line) for line in check_binding(a['rows']).read_text().splitlines()]
    rows=validate_rows(rows,classes)
    duplicates=json_read(check_binding(a['duplicates']))
    if quarantine_view is None: d.same(duplicates['blocking_groups'],[],'cross-partition/known50 duplicate blockers')
    control=json_read(check_binding(a['decoder_control']))
    d.same(control['status'],'matched_prior_selected_source_pixel_audit','prior pixel decoder control')
    # Independently reject cross-partition exact content, even a falsified empty duplicate summary.
    for field in ['video_sha256','decoded_bgr_sha256']:
        seen={}
        for r in rows:
            if r.get(field) is None: continue
            prior=seen.setdefault(r[field],r['partition'])
            if prior!=r['partition'] and quarantine_view is None: raise ValueError('cross-partition exact duplicate')
    for part in ['calibration','challenge']:
        selected=[r for r in rows if r['partition']==part]
        d.same(sorted(a[part+'_ids']),[r['clip_id'] for r in selected],'audit declared membership')
        d.same(a['partitions'][part],dict(declared=len(selected),decoded_ok=sum(r['status']=='ok' for r in selected),
               failures=sum(r['status']!='ok' for r in selected)),'audit denominators')
    if not synthetic:
        d.same(a['archive'],dict(path=str(DATA/'clips.zip'),sha256=ARCHIVE_HASH),'approved public archive')
        required=[STAGE/'owner-authorization.json',DATA/'labels.csv',DATA/'train.csv',DATA/'test.csv',
                  DATA/'verified-video-byte-inventory.json',DATA/'decoded-source-audit-v1/records.jsonl']
        if not {str(p) for p in required}<=set(a['input_bindings']): raise ValueError('missing original source audit bindings')
        _publisher_membership(rows,classes)
    return a,rows


def prepare(*, source_audit, authorization, phase4_campaign, output, quarantine_view=None, _synthetic=False):
    """Freeze immutable metadata, model, literal labels and source identities only."""
    if type(_synthetic) is not bool: raise ValueError('invalid synthetic seam')
    if not _synthetic and quarantine_view is None: raise ValueError('explicit approved quarantine view required for this public source')
    auth=binding(authorization)
    if not _synthetic:
        d.same(auth,dict(path=str(STAGE/'owner-authorization.json'),sha256=AUTH_HASH),'owner authorization')
    answers=json_read(authorization)['approved_offline_targets']
    d.same(answers,dict(maximum_eligible_publisher_labeled_oov_false_acceptance_fraction=[1,20],
        minimum_correctly_accepted_eligible_known_validation_fraction=[9,10],per_class_reporting_required=True,
        infeasible_result_must_be_preserved=True),'approved rational targets')
    _source_gate(json_read(source_audit),quarantine_view)
    files=_frozen_files(phase4_campaign,_synthetic)
    classes=json_read(check_binding(files['labels.json']))
    if type(classes) is not list or len(classes)!=50 or [c['dense_id'] for c in classes]!=list(range(50)):
        raise ValueError('exact ordered50 labels required')
    validate_contract(files,classes)
    a,rows=_audit_read(source_audit,classes,_synthetic,quarantine_view)
    qauth=None
    if quarantine_view is not None:
        rows,qauth=_quarantine_read(quarantine_view,source_audit,auth,classes,files,rows,_synthetic)
    value=dict(schema_version=1,status='protocol_frozen',evidence_kind='synthetic_in_process' if _synthetic else 'public_source',
        live_ready=False,authorization=auth,quarantine_view=None if quarantine_view is None else binding(quarantine_view),
        quarantine_authorization=qauth,audit=binding(source_audit),archive=a['archive'],frozen=files,
        classes=classes,rows=rows,targets=TARGETS,implementation=implementation_binding(),runtime=runtime_binding())
    out=reserve(output,[source_audit,authorization,phase4_campaign])
    try:
        publish(out/'protocol.json',value)
        read_protocol(out/'protocol.json',allow_synthetic=_synthetic,_allow_pending=True)
        (out/'incomplete.json').unlink()
    except BaseException as exc:
        failure(out,exc,'protocol_publication'); raise
    return value


def read_protocol(path, *, allow_synthetic=False, _allow_pending=False):
    path=d.safe_path(path,must_exist=True)
    barriers(path.parent,('failure.json',) if _allow_pending else ('failure.json','incomplete.json'))
    p=json_read(path)
    keys={'schema_version','status','evidence_kind','live_ready','authorization','quarantine_view','quarantine_authorization','audit','archive','frozen',
          'classes','rows','targets','implementation','runtime'}
    if type(p) is not dict or set(p)!=keys: raise ValueError('exact protocol schema required')
    for k,v in dict(schema_version=1,status='protocol_frozen',live_ready=False,targets=TARGETS,
                    implementation=implementation_binding(),runtime=runtime_binding()).items():
        d.same(p[k],v,'current protocol '+k)
    synthetic=p['evidence_kind']=='synthetic_in_process'
    if not (synthetic and allow_synthetic): require_real(p)
    check_binding(p['authorization']); check_binding(p['audit'])
    view=None if p['quarantine_view'] is None else check_binding(p['quarantine_view'])
    _source_gate(json_read(p['audit']['path']),view)
    if not synthetic:
        if view is None: raise ValueError('explicit approved quarantine view required for this public source')
        d.same(p['authorization'],dict(path=str(STAGE/'owner-authorization.json'),sha256=AUTH_HASH),'real owner anchor')
        d.same(p['frozen'],_frozen_files(PHASE4/'all50-campaign-v1',False),'real frozen model bindings')
    for ref in p['frozen'].values(): check_binding(ref)
    d.same(p['classes'],json_read(check_binding(p['frozen']['labels.json'])),'frozen literal labels')
    validate_contract(p['frozen'],p['classes'])
    a,rows=_audit_read(p['audit']['path'],p['classes'],synthetic,view)
    qauth=None
    if view is not None:
        rows,qauth=_quarantine_read(view,p['audit']['path'],p['authorization'],p['classes'],p['frozen'],rows,synthetic)
    d.same(p['quarantine_authorization'],qauth,'explicit bound quarantine authorization')
    d.same(p['archive'],a['archive'],'protocol archive'); d.same(p['rows'],rows,'current audited rows')
    return p



def save_array(path, array):
    with d.safe_path(path).open('xb') as stream:
        np.save(stream,array,allow_pickle=False)
    actual=np.load(path,allow_pickle=False)
    if actual.dtype!=array.dtype or actual.shape!=array.shape or not np.array_equal(actual,array):
        raise ValueError('array publication readback mismatch')
    return d.sha256(path)


def _observe(path, row, detector_path, detector_factory, cv):
    """Full pixel audit with actual timestamps; exactly the accepted shared capture."""
    import hashlib
    from .sequence import ObservationClock, prepare_image
    from .extract import cv_timestamp
    from .face_features import prepare_capture
    video=detector=None
    try:
        video=cv.VideoCapture(str(path))
        if not video.isOpened(): raise ValueError('cannot open source video')
        detector=detector_factory(detector_path)
        clock=ObservationClock(); raw=[]; pixels=hashlib.sha256(); count=0; shapes=set()
        while True:
            ok,bgr=video.read()
            if not ok: break
            if (type(bgr) is not np.ndarray or bgr.dtype!=np.uint8 or bgr.ndim!=3
                    or bgr.shape[2]!=3 or min(bgr.shape)<1):
                raise ValueError('invalid decoded BGR frame')
            count+=1; shapes.add(tuple(bgr.shape))
            pixels.update(np.asarray(bgr.shape,dtype='<i4').tobytes())
            pixels.update(np.ascontiguousarray(bgr).tobytes())
            t=cv_timestamp(video.get(cv.CAP_PROP_POS_MSEC))
            if clock.admit(t):
                image=prepare_image(cv.cvtColor(bgr,cv.COLOR_BGR2RGB),cv)
                f=detector.detect(image,t)
                d.same(f.timestamp_ms,t,'actual detector timestamp'); raw.append(f)
        d.same(count,row['decoded_frames'],'audited decoded frame count')
        d.same(pixels.hexdigest(),row['decoded_bgr_sha256'],'audited full decoded pixels')
        d.same([list(s) for s in sorted(shapes)],row['shapes'],'audited BGR shapes')
        return raw,prepare_capture(raw)
    finally:
        try:
            if detector is not None: detector.close()
        finally:
            if video is not None: video.release()


def _npy_header(stream, file_size):
    """Read at most a small literal NPY header before any array allocation."""
    import ast
    import math
    import struct
    magic=stream.read(8)
    if magic not in [b'\x93NUMPY\x01\x00',b'\x93NUMPY\x02\x00']:
        raise ValueError('raw/array NPY version denied')
    size=2 if magic[-2]==1 else 4
    encoded=stream.read(size)
    if len(encoded)!=size: raise ValueError('raw/array truncated header')
    length=struct.unpack('<H' if size==2 else '<I',encoded)[0]
    if length>4096: raise ValueError('raw/array header exceeds bound')
    payload=stream.read(length)
    try: header=ast.literal_eval(payload.decode('latin1'))
    except (ValueError,SyntaxError,UnicodeError) as exc: raise ValueError('raw/array invalid header') from exc
    if type(header) is not dict or set(header)!={'descr','fortran_order','shape'} or header['fortran_order'] is not False:
        raise ValueError('raw/array exact C-order header required')
    shape=header['shape']
    if type(shape) is not tuple or any(type(n) is not int or n<0 for n in shape):
        raise ValueError('raw/array invalid cardinality')
    try: dtype=np.dtype(header['descr'])
    except (ValueError,TypeError) as exc: raise ValueError('raw/array invalid dtype') from exc
    if dtype.hasobject or dtype.fields is not None or dtype.subdtype is not None:
        raise ValueError('raw/array plain numeric or Unicode dtype required')
    if 8+size+length+math.prod(shape)*dtype.itemsize!=file_size:
        raise ValueError('raw/array header cardinality differs from stored bytes')
    return shape,dtype


def array_read(path, shape, dtype, *, mmap_mode=None):
    """Exact audited shape/dtype checked from bounded header before np.load."""
    path=d.safe_path(path,must_exist=True)
    with path.open('rb') as stream: actual,kind=_npy_header(stream,path.stat().st_size)
    if actual!=shape or (dtype=='U' and (kind.kind!='U' or not 0<kind.itemsize<=1024)) or (dtype!='U' and kind!=np.dtype(dtype)):
        raise ValueError('source-bound array shape/dtype required')
    return np.load(path,allow_pickle=False,mmap_mode=mmap_mode)


def read_raw_bounded(path, digest, source):
    """Admit unchanged numeric codec only after source-bounded ZIP/NPY inspection."""
    import zipfile
    path=d.safe_path(path,must_exist=True)
    d.same(d.sha256(path),digest,'raw digest')
    maximum=d.integer(source['decoded_frames'],'raw audited frame limit',1)
    shapes={'timestamps':(np.dtype('int64'),None),'face_offsets':(np.dtype('int64'),None),
        'face_values':(np.dtype('float64'),None)}
    for name,shape in [('pose',(33,4)),('left_hand',(21,3)),('right_hand',(21,3))]:
        shapes[name]=(np.dtype('float64'),shape)
    for name in ['pose','left_hand','right_hand','face']: shapes[name+'_present']=(np.dtype('uint8'),())
    with zipfile.ZipFile(path) as archive:
        infos=archive.infolist()
        if len(infos)!=len(shapes) or {i.filename for i in infos}!={k+'.npy' for k in shapes}:
            raise ValueError('raw exact unique member coverage required')
        # Each possible observation has <=478 face points, 33 pose and21 points per hand.
        if sum(i.file_size for i in infos)>maximum*(8+4+8+(33*4+42*3+478*3)*8)+8+len(shapes)*4108:
            raise ValueError('raw uncompressed bytes exceed audited capture bound')
        headers={}
        for info in infos:
            if info.flag_bits&1 or info.is_dir(): raise ValueError('raw encrypted/directory member denied')
            with archive.open(info) as stream: headers[info.filename[:-4]]=_npy_header(stream,info.file_size)
        shape,kind=headers['timestamps']
        if len(shape)!=1 or shape[0]>maximum: raise ValueError('raw observations exceed audited decoded frames')
        n=shape[0]
        for name,(dtype,tail) in shapes.items():
            shape,kind=headers[name]
            if kind!=dtype: raise ValueError('raw exact dtype required')
            if name=='face_values':
                if len(shape)!=2 or shape[1]!=3 or shape[0]>n*478: raise ValueError('raw face cardinality exceeds capture bound')
            else:
                expected=(n,) if name=='timestamps' else (n+1,) if name=='face_offsets' else (n,*tail)
                if shape!=expected: raise ValueError('raw source-bounded shape required')
    raw=d.read_raw(path,digest)
    if any(f.face is not None and len(f.face)>478 for f in raw): raise ValueError('raw per-observation face cardinality exceeds bound')
    return raw


def _counts(ledger):
    return dict(declared=len(ledger),eligible=sum(r['status']=='eligible' for r in ledger),
        quarantined=sum(r['status']=='quarantined' for r in ledger),
        source_candidates=sum(r['status']!='quarantined' for r in ledger),
        source_failures=sum(r['status']=='source_failure' for r in ledger),
        capture_exclusions=sum(r['status']=='ineligible' for r in ledger),errors=sum(r['status']=='error' for r in ledger))


def extract(*, protocol, mode, output, calibration_run=None, _detector_factory=None):
    """Stream only fixed partition members; test injection is synthetic-only Python."""
    import hashlib
    import json
    import shutil
    import tempfile
    import zipfile
    synthetic=_detector_factory is not None
    p=read_protocol(protocol,allow_synthetic=synthetic)
    if p['evidence_kind']=='public_source' and synthetic: raise ValueError('real protocol forbids injected detector')
    if mode=='challenge':
        if calibration_run is None: raise ValueError('affirmative feasible freeze required before challenge extraction')
        from .rejection_run import read_freeze
        read_freeze(calibration_run,protocol=protocol,allow_synthetic=synthetic)
    selected=partition_rows(p['rows'],mode)
    ledger_sources=selected if mode!='pilot' else sorted(selected+[r for r in p['rows']
        if r['partition']=='calibration' and r.get('view_disposition')=='quarantined'],key=lambda r:r['clip_id'])
    if mode=='challenge':
        publish(Path(calibration_run)/'challenge-extraction-start.json',dict(schema_version=1,status='challenge_extraction_started',
            protocol=binding(protocol),freeze=binding(Path(calibration_run)/'freeze.json'),output=str(d.safe_path(output))))
    out=reserve(output,[protocol,p['archive']['path']]+[v['path'] for v in p['frozen'].values()])
    (out/'raw').mkdir()
    import cv2 as cv
    from .detector import HolisticDetector
    detector_factory=HolisticDetector if _detector_factory is None else _detector_factory
    detector_path=Path(p['frozen'].get('detector.task',p['frozen']['model.keras'])['path'])
    start=dict(schema_version=1,status='extraction_started',mode=mode,protocol=binding(protocol),
        evidence_kind=p['evidence_kind'],implementation=p['implementation'],runtime=p['runtime'],
        selected_ids=[r['clip_id'] for r in selected],calibration_freeze=None if mode!='challenge' else binding(Path(calibration_run)/'freeze.json'))
    ledger=[]; tensors=[]; ids=[]
    try:
        publish(out/'start.json',start)
        with zipfile.ZipFile(check_binding(p['archive'])) as archive, tempfile.TemporaryDirectory(dir=out,prefix='source-') as temp, (out/'rows.jsonl').open('x') as stream:
            for i,row in enumerate(ledger_sources):
                record=dict(source=row,clip_id=row['clip_id'],status='source_failure' if row['status']!='ok' else 'error',
                    reason=row.get('failure_reason',row.get('failure')),raw_file=None,raw_sha256=None,capture=None,presence=None,
                    face_cardinality=None)
                try:
                    if row.get('view_disposition')=='quarantined':
                        record.update(status='quarantined',reason=row['view_reason'])
                    elif row['status']=='ok':
                        path=Path(temp)/'source.MOV'
                        info=archive.getinfo(row['clip_id'])
                        d.same(info.file_size,row['video_bytes'],'archive declared bytes')
                        if info.file_size>=20*1024*1024: raise ValueError('source exceeds approved single-clip bound')
                        with archive.open(info) as src,path.open('xb') as dst: shutil.copyfileobj(src,dst,1024*1024)
                        d.same(d.sha256(path),row['video_sha256'],'audited source bytes')
                        raw,capture=_observe(path,row,detector_path,detector_factory,cv)
                        filename=f'raw/{i:06d}.npz'
                        digest=d.write_raw(out/filename,raw); read_raw_bounded(out/filename,digest,row)
                        from collections import Counter
                        record.update(status='eligible' if capture.tensor is not None else 'ineligible',reason=capture.reason,
                            raw_file=filename,raw_sha256=digest,capture=d.capture_receipt(capture),
                            presence={n:sum(getattr(f,n) is not None for f in raw) for n in ['pose','left_hand','right_hand','face']},
                            face_cardinality=dict(Counter(str(len(f.face)) for f in raw if f.face is not None)))
                        if capture.tensor is not None: tensors.append(capture.tensor); ids.append(row['clip_id'])
                except Exception as exc:
                    record.update(status='error',reason=str(exc),error_type=type(exc).__name__)
                finally:
                    path=Path(temp)/'source.MOV'
                    path.unlink(missing_ok=True)
                stream.write(json.dumps(record,sort_keys=True,allow_nan=False)+'\n'); stream.flush(); ledger.append(record)
        x=np.stack(tensors) if tensors else np.empty((0,30,1588),np.float32)
        save_array(out/'X.npy',x); save_array(out/'ids.npy',np.array(ids,dtype=np.str_))
        support={r['original_id'] for r in selected if any(l['clip_id']==r['clip_id'] and l['status']=='eligible' for l in ledger)}
        missing=sorted({r['original_id'] for r in selected}-support)
        counts=_counts(ledger)
        qualified=mode!='pilot' and counts['errors']==0 and (mode!='calibration' or not missing)
        manifest=dict(schema_version=1,status='complete' if counts['errors']==0 else 'incomplete',qualified=qualified,
            mode=mode,protocol=binding(protocol),evidence_kind=p['evidence_kind'],live_ready=False,counts=counts,
            missing_eligible_classes=missing,files={n:d.sha256(out/n) for n in ['start.json','rows.jsonl','X.npy','ids.npy']},
            calibration_freeze=start['calibration_freeze'])
        read_protocol(protocol,allow_synthetic=synthetic)
        publish(out/'complete.json',manifest)
        if counts['errors']: raise ValueError('extraction errors retained in full source ledger')
        (out/'incomplete.json').unlink()
        return manifest
    except BaseException as exc:
        failure(out,exc,'extraction'); raise


def read_bundle(output, *, protocol, mode, allow_synthetic=False):
    """Read only this partition and saved raw/tensors; no detector/video/inference."""
    from .face_features import prepare_capture
    from .face_augmentation import validate_tensor
    import json
    p=read_protocol(protocol,allow_synthetic=allow_synthetic)
    out=d.safe_path(output,must_exist=True); barriers(out)
    m=json_read(out/'complete.json')
    keys={'schema_version','status','qualified','mode','protocol','evidence_kind','live_ready','counts',
          'missing_eligible_classes','files','calibration_freeze'}
    if type(m) is not dict or set(m)!=keys: raise ValueError('exact bundle schema required')
    for k,v in dict(schema_version=1,status='complete',qualified=True,mode=mode,protocol=binding(protocol),
                    evidence_kind=p['evidence_kind'],live_ready=False).items(): d.same(m[k],v,'bundle '+k)
    if mode not in ['calibration','challenge']: raise ValueError('pilot is never a qualified negative bundle')
    if set(m['files'])!={'start.json','rows.jsonl','X.npy','ids.npy'}: raise ValueError('exact bundle artifact coverage required')
    for name,digest in m['files'].items(): d.same(d.sha256(out/name),digest,'saved bundle '+name)
    start=json_read(out/'start.json')
    for k,v in dict(schema_version=1,status='extraction_started',mode=mode,protocol=binding(protocol),
        evidence_kind=p['evidence_kind'],implementation=p['implementation'],runtime=p['runtime'],
        selected_ids=[r['clip_id'] for r in partition_rows(p['rows'],mode)],calibration_freeze=m['calibration_freeze']).items():
        d.same(start.get(k),v,'extraction start '+k)
    if mode=='challenge':
        if m['calibration_freeze'] is None: raise ValueError('challenge freeze required')
        freeze_path=check_binding(m['calibration_freeze'])
        from .rejection_run import read_freeze
        read_freeze(freeze_path.parent,protocol=protocol,allow_synthetic=allow_synthetic)
        d.same(json_read(freeze_path.parent/'challenge-extraction-start.json'),dict(schema_version=1,
            status='challenge_extraction_started',protocol=binding(protocol),freeze=m['calibration_freeze'],
            output=str(out)),'exclusive challenge extraction reservation')
    ledger=[json_value(line) for line in (out/'rows.jsonl').read_text().splitlines()]
    selected=partition_rows(p['rows'],mode)
    if len(ledger)!=len(selected): raise ValueError('complete declared ledger required')
    x=np.load(out/'X.npy',allow_pickle=False,mmap_mode='r'); ids=np.load(out/'ids.npy',allow_pickle=False)
    if x.dtype!=np.float32 or x.shape!=(sum(r['status']=='eligible' for r in ledger),30,1588): raise ValueError('invalid OOV tensor shape/dtype')
    if ids.dtype.kind!='U' or ids.shape!=(len(x),): raise ValueError('invalid OOV IDs')
    expected=[]; support=set()
    for source,r in zip(selected,ledger):
        expected_keys={'source','clip_id','status','reason','raw_file','raw_sha256','capture','presence','face_cardinality'}
        if type(r) is not dict or set(r)!=expected_keys: raise ValueError('exact complete ledger schema required')
        d.same(r['source'],source,'literal audited source'); d.same(r['clip_id'],source['clip_id'],'ledger source ID')
        if source.get('view_disposition')=='quarantined' and r['status']!='quarantined':
            raise ValueError('quarantine cannot become a neural observation or rejection')
        if r['status'] in ['eligible','ineligible']:
            raw_name=r['raw_file']
            if type(raw_name) is not str or re.fullmatch(r'raw/[0-9]{6}\.npz',raw_name) is None: raise ValueError('unsafe raw path')
            raw=read_raw_bounded(out/raw_name,r['raw_sha256'],source); capture=prepare_capture(raw)
            d.same(r['capture'],d.capture_receipt(capture),'raw capture readback'); d.same(r['reason'],capture.reason,'eligibility reason')
            d.same(r['presence'],{n:sum(getattr(f,n) is not None for f in raw) for n in ['pose','left_hand','right_hand','face']},'presence readback')
            from collections import Counter
            d.same(r['face_cardinality'],dict(Counter(str(len(f.face)) for f in raw if f.face is not None)),'face cardinality readback')
            d.same(r['status'],'eligible' if capture.tensor is not None else 'ineligible','capture status')
            if capture.tensor is not None:
                index=len(expected); expected.append(source['clip_id']); support.add(source['original_id'])
                validate_tensor(np.asarray(x[index:index+1]))
                if not np.array_equal(x[index],capture.tensor): raise ValueError('derived tensor differs from raw codec')
        elif r['status']=='quarantined':
            if source.get('view_disposition')!='quarantined': raise ValueError('unauthorized quarantine ledger row')
            d.same(r['reason'],source['view_reason'],'quarantine reason')
            for key in ['raw_file','raw_sha256','capture','presence','face_cardinality']:
                d.same(r[key],None,'quarantined source must have no observations')
        elif r['status']=='source_failure':
            if source['status']=='ok' or r['raw_file'] is not None or r['capture'] is not None:
                raise ValueError('unavailable source cannot have neural prediction')
        else: raise ValueError('failed source cannot qualify complete bundle')
    d.same(ids.tolist(),expected,'exact ordered eligible OOV membership')
    d.same(m['counts'],_counts(ledger),'declared/eligible source accounting')
    missing=sorted({r['original_id'] for r in selected}-support)
    d.same(m['missing_eligible_classes'],missing,'class support')
    if mode=='calibration' and missing: raise ValueError('every declared OOV class needs eligible support')
    return m,x,ids,ledger



def main(argv=None):
    import argparse
    import sys
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    prepare_parser=sub.add_parser('prepare',help='Freeze admitted public-source metadata only')
    for name in ['source-audit','authorization','phase4-campaign','quarantine-view','output']:
        prepare_parser.add_argument('--'+name,required=True,type=Path)
    for name in ['pilot','calibration','challenge']:
        command=sub.add_parser(name)
        command.add_argument('--protocol',required=True,type=Path)
        command.add_argument('--output',required=True,type=Path)
        if name=='challenge': command.add_argument('--calibration-run',required=True,type=Path)
    args=vars(parser.parse_args(argv)); command=args.pop('command')
    try:
        if command=='prepare': value=prepare(**args)
        else: value=extract(mode=command,**args)
        print(value['status'])
        return 0 if command=='prepare' or command=='pilot' or value['qualified'] else 2
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print('OOV admission/extraction denied: '+str(exc),file=sys.stderr)
        return 2


if __name__=='__main__':
    raise SystemExit(main())
