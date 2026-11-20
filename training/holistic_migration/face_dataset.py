"""Additive face-inclusive raw-campaign rebuilding; no native inference or fitting."""
from collections import Counter
from pathlib import Path
import json
import os
import sys
import numpy as np
from . import dataset as historical
from .face_features import FEATURE_COUNT, FEATURE_VERSION, prepare_capture

CONTRACT = 'docs/holistic-migration/FEATURES_FACE.md'
TENSOR_CONTRACT = 'Float32[N,30,1588] hm1588-v1'
PARTITIONS = historical.PARTITIONS


def implementation_binding():
    """Bind the new modules/approved contract plus unchanged producer dependencies."""
    names = [CONTRACT, 'training/holistic_migration/face_features.py',
             'training/holistic_migration/face_dataset.py']
    return dict(historical.contract_binding(), **{n:historical.sha256(historical.REPO/n) for n in names})


def eligibility_summary(classes, captures):
    def counts(rows):
        reasons = Counter(r['reason'] for r in rows)
        selected = len(rows) - reasons['not_selected']
        return dict(declared=len(rows), selected=selected, eligible=reasons['eligible'],
                    ineligible=selected-reasons['eligible'], not_selected=reasons['not_selected'],
                    reasons=dict(sorted((k,v) for k,v in reasons.items() if k not in ['eligible','not_selected'])))
    return dict(partitions={p:counts([r for r in captures if r['partition']==p]) for p in PARTITIONS},
                classes=[dict(c,partitions={p:counts([r for r in captures if r['partition']==p and r['dense_id']==c['dense_id']])
                                           for p in PARTITIONS}) for c in classes])


def _capture(row, raw):
    result = prepare_capture(raw)
    summary = dict(presence={n:sum(getattr(f,n) is not None for f in raw)
                             for n in ['pose','left_hand','right_hand','face']},
                   face_cardinality=dict(sorted(Counter(str(len(f.face)) for f in raw if f.face is not None).items())),
                   face_missing=sum(f.face is None for f in raw))
    return result, dict(row, **historical.capture_receipt(result), **summary,
                        status='eligible' if result.tensor is not None else 'ineligible',
                        derived_row_count=30 if result.tensor is not None else 0)


def _write_array(path, array):
    with path.open('xb') as stream:
        np.save(stream, array, allow_pickle=False)
    loaded = np.load(path, allow_pickle=False)
    if loaded.dtype != array.dtype or loaded.shape != array.shape or not np.array_equal(loaded,array):
        raise ValueError('tensor artifact readback mismatch')
    return dict(sha256=historical.sha256(path), shape=list(array.shape), dtype=str(array.dtype))


def build_dataset(*, campaign, output, diagnostic_fit_only=False):
    """Rebuild original, frozen membership only; no augmentation or class reduction."""
    campaign = historical.safe_path(campaign, must_exist=True)
    graph, source, rows = historical.validate_campaign(campaign)
    output = historical.fresh_output(output, dict(graph.paths,campaign=campaign))
    binding = implementation_binding()
    source_hash = historical.sha256(campaign/'extraction_manifest.json')
    output.mkdir()
    try:
        historical.write_json(output/'incomplete.json',dict(status='incomplete',disposition='non_gating'))
        manifest = _build_into(campaign,output,graph,source,rows,binding,source_hash,diagnostic_fit_only)
        (output/'incomplete.json').unlink()  # only our successful attempt's admission barrier
        return manifest
    except BaseException:
        _persist_failure(output)
        raise


def _build_into(campaign,output,graph,source,rows,binding,source_hash,diagnostic_fit_only):
    selected = ([min(r['clip_id'] for r in rows if r['partition']=='fit' and r['dense_id']==c['dense_id'])
                 for c in graph.classes] if diagnostic_fit_only else [r['clip_id'] for r in rows])
    selected_set = set(selected)
    mode = 'diagnostic_fit_only' if diagnostic_fit_only else 'full'
    historical.write_json(output/'selected_ids.json', selected)
    attempt = dict(schema_version=1, feature_version=FEATURE_VERSION, mode=mode,
                   campaign=str(campaign), campaign_manifest_sha256=source_hash,
                   graph=historical.graph_receipt(graph), implementation=binding,
                   evidence_kind=source['evidence_kind'])
    historical.write_json(output/'attempt.json', attempt)
    with (output/'FEATURES_FACE.md').open('xb') as stream:
        stream.write((historical.REPO/CONTRACT).read_bytes())
    tensors = {p:[] for p in PARTITIONS}
    labels = {p:[] for p in PARTITIONS}
    ids = {p:[] for p in PARTITIONS}
    captures = []
    for number,row in enumerate(rows):
        if row['clip_id'] not in selected_set:
            captures.append(dict(row, status='not_selected',reason='not_selected',
                                 presence=None,face_cardinality=None,face_missing=None,derived_row_count=0,
                                 source_observation_count=row['capture']['source_observation_count']))
            continue
        try:
            result, capture = _capture(row, historical.read_raw(campaign/row['raw_file'], row['raw_sha256']))
        except BaseException as error:
            failed_rows = captures + [dict(row,status='error',reason='error',error_type=type(error).__name__)]
            failed_rows += [dict(r,status='not_processed',reason='not_processed') for r in rows[number+1:]]
            try:
                historical.write_json(output/'error_rows.json',dict(declared=len(rows),processed=len(captures),errors=1,rows=failed_rows))
            except BaseException:
                pass
            raise
        captures.append(capture)
        if result.tensor is not None:
            p = row['partition']
            tensors[p].append(result.tensor)
            labels[p].append(row['dense_id'])
            ids[p].append(row['clip_id'])
    eligibility = eligibility_summary(graph.classes,captures)
    documents = {'selected_ids.json':selected, 'attempt.json':attempt, 'class_metadata.json':graph.classes,
                 'capture_rows.json':captures, 'eligibility.json':eligibility,
                 'ineligible.json':[r for r in captures if r['status']=='ineligible']}
    for name,value in documents.items():
        if name not in ['selected_ids.json','attempt.json']:
            historical.write_json(output/name,value)
    unsupported = [[c['dense_id'],p] for c in eligibility['classes'] for p in ['fit','validation']
                   if c['partitions'][p]['eligible']==0]
    if not diagnostic_fit_only and unsupported:
        historical.write_json(output/'support_failure.json',dict(unsupported=unsupported))
        raise ValueError(f'missing eligible support in fit/validation classes: {unsupported}')
    artifacts = {}
    for p in PARTITIONS:
        partition_tensors = tensors.pop(p)
        x = np.stack(partition_tensors) if partition_tensors else np.empty((0,30,FEATURE_COUNT),np.float32)
        for name,array in [(f'X_{p}.npy',x), (f'y_{p}.npy',np.array(labels[p],np.int64)),
                           (f'clip_ids_{p}.npy',np.array(ids[p],dtype=np.str_))]:
            artifacts[name] = _write_array(output/name,array)
    for name,value in documents.items():
        historical.same(historical.load_json(output/name),value,'final JSON readback')
        artifacts[name] = dict(sha256=historical.sha256(output/name))
    historical.same(historical.sha256(output/'FEATURES_FACE.md'),binding[CONTRACT],'copied face contract')
    artifacts['FEATURES_FACE.md'] = dict(sha256=binding[CONTRACT])
    for name,record in artifacts.items():
        historical.same(historical.sha256(output/name),record['sha256'],'final artifact digest')
    for row in rows:
        historical.same(historical.sha256(campaign/row['raw_file']),row['raw_sha256'],'final raw digest')
    for name,key in [('rows.jsonl','rows_sha256'),('attempt.json','attempt_sha256'),('selected_ids.json','selected_ids_sha256')]:
        historical.same(historical.sha256(campaign/name),source[key],'final campaign ledger digest')
    historical.recheck_graph(graph)
    historical.same(implementation_binding(),binding,'current face implementation')
    historical.same(historical.sha256(campaign/'extraction_manifest.json'),source_hash,'current campaign')
    manifest = dict(attempt, status='diagnostic_complete' if diagnostic_fit_only else 'complete', tensor_contract=TENSOR_CONTRACT,
                    training_qualified=False, live_ready=False, model_evaluated=False,
                    classes=graph.classes, eligibility=eligibility, artifacts=artifacts, augmentation='none')
    if diagnostic_fit_only:
        manifest['diagnostic_eligible'] = all(r['reason']=='eligible' for r in captures if r['clip_id'] in selected_set)
    _publish_completion(output/('diagnostic_manifest.json' if diagnostic_fit_only else 'data_manifest.json'),manifest)
    return manifest


def _persist_failure(output):
    """Best effort fixed disposition; secondary failures never replace primary."""
    try:
        with (output/'failure.json').open('x',encoding='utf-8') as stream:
            json.dump(dict(status='failed',disposition='incomplete_non_gating'),stream,sort_keys=True)
            stream.write('\n')
    except BaseException:
        pass


def _publish_completion(path,value):
    """Exclusive stage/readback/link/readback; retain pending audit bytes.

    Bounded local publication only: no crash, power-loss or hostile-writer guarantee.
    """
    pending = path.with_name(path.name+'.pending')
    linked = False
    try:
        historical.write_json(pending,value)
        expected = historical.sha256(pending)
        os.link(pending,path)
        linked = True
        historical.same(historical.sha256(path),expected,'published manifest digest')
        historical.same(historical.load_json(path),value,'published manifest readback')
    except BaseException:
        if linked:
            try:
                if path.samefile(pending): path.unlink()
            except BaseException:
                pass
        _persist_failure(path.parent)
        raise


def validate_bundle(output):
    """Read-only consumer; never revokes previously established publications."""
    output = historical.safe_path(output, must_exist=True)
    if any((output/name).exists() or (output/name).is_symlink()
           for name in ['failure.json','incomplete.json']):
        raise ValueError('failed/incomplete target cannot be consumed')
    path = historical.safe_path(output/'data_manifest.json', must_exist=True)
    manifest = historical.load_json(path)
    if type(manifest) is not dict:
        raise ValueError('manifest must be an object')
    attempt_keys = {'schema_version','feature_version','mode','campaign','campaign_manifest_sha256','graph','implementation','evidence_kind'}
    manifest_keys = attempt_keys | {'status','tensor_contract','training_qualified','live_ready','model_evaluated',
                                    'classes','eligibility','artifacts','augmentation'}
    if set(manifest)!=manifest_keys:
        raise ValueError('invalid manifest schema keys')
    expected = dict(schema_version=1, feature_version=FEATURE_VERSION,mode='full',status='complete',
                    tensor_contract=TENSOR_CONTRACT,training_qualified=False,live_ready=False,
                    model_evaluated=False,augmentation='none')
    for name,value in expected.items():
        historical.same(manifest.get(name),value,'face manifest '+name)
    attempt = historical.load_json(historical.safe_path(output/'attempt.json', must_exist=True))
    if type(attempt) is not dict or set(attempt)!=attempt_keys:
        raise ValueError('invalid attempt schema keys')
    for name,value in attempt.items():
        historical.same(manifest.get(name),value,'attempt '+name)
    if manifest.get('evidence_kind') not in ['source_video','synthetic_in_process']:
        raise ValueError('invalid evidence kind')
    historical.same(manifest.get('implementation'),implementation_binding(),'current face implementation')
    campaign = historical.safe_path(manifest.get('campaign'),must_exist=True)
    historical.same(historical.sha256(campaign/'extraction_manifest.json'),
                    manifest.get('campaign_manifest_sha256'),'current campaign digest')
    graph,source,rows = historical.validate_campaign(campaign)
    historical.same(manifest.get('graph'),historical.graph_receipt(graph),'current campaign graph')
    historical.same(manifest['evidence_kind'],source['evidence_kind'],'evidence kind provenance')
    names = {'FEATURES_FACE.md','selected_ids.json','attempt.json','class_metadata.json',
             'capture_rows.json','eligibility.json','ineligible.json'}
    names.update(f'{prefix}_{p}.npy' for prefix in ['X','y','clip_ids'] for p in PARTITIONS)
    artifacts = manifest.get('artifacts')
    if type(artifacts) is not dict or set(artifacts)!=names:
        raise ValueError('invalid required artifact coverage')
    for name,record in artifacts.items():
        target = historical.safe_path(output/name,must_exist=True)
        digest = historical.sha256(target)
        if name.endswith('.npy'):
            array = np.load(target,allow_pickle=False,mmap_mode='r')
            expected_record = dict(sha256=digest,shape=list(array.shape),dtype=str(array.dtype))
        else:
            expected_record = dict(sha256=digest)
            if name.endswith('.json'): historical.load_json(target)
        historical.same(record,expected_record,'artifact readback '+name)
    historical.same(historical.sha256(output/'FEATURES_FACE.md'),implementation_binding()[CONTRACT],'copied face contract')
    historical.same(historical.load_json(output/'selected_ids.json'),[r['clip_id'] for r in rows],'full ordered selection')
    historical.same(historical.load_json(output/'class_metadata.json'),graph.classes,'frozen classes')
    historical.same(manifest.get('classes'),graph.classes,'manifest classes')
    captures = historical.load_json(output/'capture_rows.json')
    if type(captures) is not list or len(captures)!=len(rows):
        raise ValueError('capture rows must cover every declared source')
    arrays = {p:{key:np.load(output/f'{key}_{p}.npy',allow_pickle=False,mmap_mode='r')
                 for key in ['X','y','clip_ids']} for p in PARTITIONS}
    for p,blocks in arrays.items():
        count = sum(r.get('status')=='eligible' for r in captures if type(r) is dict and r.get('partition')==p)
        if (blocks['X'].shape!=(count,30,FEATURE_COUNT) or blocks['X'].dtype!=np.float32
                or blocks['y'].shape!=(count,) or blocks['y'].dtype!=np.int64
                or blocks['clip_ids'].shape!=(count,) or blocks['clip_ids'].dtype.kind!='U'):
            raise ValueError('invalid tensor/label/ID dtype or shape')
    indices = {p:0 for p in PARTITIONS}
    for row,actual in zip(rows,captures):
        result,expected_capture = _capture(row,historical.read_raw(campaign/row['raw_file'],row['raw_sha256']))
        historical.same(actual,expected_capture,'capture provenance and presence readback')
        if result.tensor is not None:
            p = row['partition']; i = indices[p]; blocks = arrays[p]
            if not np.array_equal(blocks['X'][i],result.tensor):
                raise ValueError('raw-to-tensor readback mismatch')
            historical.same(int(blocks['y'][i]),row['dense_id'],'ordered label')
            historical.same(str(blocks['clip_ids'][i]),row['clip_id'],'ordered clip ID')
            indices[p] += 1
    eligibility = eligibility_summary(graph.classes,captures)
    historical.same(historical.load_json(output/'eligibility.json'),eligibility,'eligibility readback')
    historical.same(manifest.get('eligibility'),eligibility,'manifest eligibility')
    historical.same(historical.load_json(output/'ineligible.json'),[r for r in captures if r['status']=='ineligible'],'ineligible list')
    if any(c['partitions'][p]['eligible']==0 for c in eligibility['classes'] for p in ['fit','validation']):
        raise ValueError('missing eligible support')
    return manifest


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campaign',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--diagnostic-fit-only',action='store_true',default=False)
    args = parser.parse_args(argv)
    try:
        manifest = build_dataset(campaign=args.campaign,output=args.output,diagnostic_fit_only=args.diagnostic_fit_only)
    except (ValueError,OSError,KeyError,TypeError) as error:
        print(f'face dataset rejected: {error}',file=sys.stderr)
        return 2
    name = 'diagnostic_manifest.json' if args.diagnostic_fit_only else 'data_manifest.json'
    print(f"completed {args.output/name}; mode={manifest['mode']}; training_qualified=false")
    if args.diagnostic_fit_only and not manifest['diagnostic_eligible']:
        print('diagnostic infeasible: stop before full build; owner decision required',file=sys.stderr)
        return 2
    return 0


if __name__=='__main__':
    raise SystemExit(main())
