"""Synthetic production-schema campaigns; no decoder, detector or model execution."""
from dataclasses import replace
import importlib
import importlib.util
import json
from pathlib import Path
import numpy as np
import pytest
from training.holistic_migration import dataset as old
from training.holistic_migration.face_features import prepare_capture
from .test_dataset import graph_fixture, rebind
from .test_face_features import observed


def builder():
    name = 'training.holistic_migration.face_dataset'
    return importlib.import_module(name) if importlib.util.find_spec(name) else old


@pytest.fixture(scope='module')
def campaign(tmp_path_factory):
    root = tmp_path_factory.mktemp('face-synthetic-campaign')
    graph = old.preflight(**graph_fixture(root/'source'))
    target = root/'campaign'
    (target/'raw').mkdir(parents=True)
    selected = [r['clip_id'] for r in graph.rows]
    old.write_json(target/'selected_ids.json', selected)
    attempt = dict(schema_version=1, evidence_kind='synthetic_in_process', graph=old.graph_receipt(graph),
                   selected_ids_sha256=old.sha256(target/'selected_ids.json'))
    old.write_json(target/'attempt.json', attempt)
    rows = []
    for number, source in enumerate(graph.rows):
        fs = observed()
        # Vary actual geometry by source without any native inference.
        fs = [replace(f, face=f.face + number/1000) for f in fs]
        raw_file = f'raw/{number:06d}.npz'
        digest = old.write_raw(target/raw_file, fs)
        record = graph.records[source['clip_id']]
        rows.append(dict(source, raw_file=raw_file, raw_sha256=digest, status='eligible',
                         decoded_frames=record['decoded_frames'], decoded_bgr_sha256=record['decoded_bgr_sha256'],
                         capture=old.capture_receipt(old.prepare_capture(fs))))
    (target/'rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    manifest = dict(attempt, status='complete', full_campaign_qualification=True,
                    rows_sha256=old.sha256(target/'rows.jsonl'), attempt_sha256=old.sha256(target/'attempt.json'),
                    counts=dict(declared=150, selected=150, processed=150, errors=0))
    old.write_json(target/'extraction_manifest.json', manifest)
    old.validate_campaign(target)  # unchanged production validator, no provenance bypass
    return target


def test_full_build_preserves_all_frozen_identities_and_face_tensors(campaign, tmp_path):
    out = tmp_path/'face-full'
    m = builder().build_dataset(campaign=campaign, output=out)
    assert m['tensor_contract'] == 'Float32[N,30,1588] hm1588-v1', 'historical dataset is not face-inclusive'
    assert m['status'] == 'complete' and m['evidence_kind'] == 'synthetic_in_process'
    assert m['training_qualified'] is m['live_ready'] is m['model_evaluated'] is False
    assert m['mode'] == 'full' and m['feature_version'] == 'hm1588-v1'
    assert len(m['classes']) == 50 and m['classes'][25]['original_id'] == 49
    assert old.load_json(out/'data_manifest.json') == m
    source = [json.loads(s) for s in (campaign/'rows.jsonl').read_text().splitlines()]
    captures = old.load_json(out/'capture_rows.json')
    assert len(captures) == 150
    assert old.load_json(out/'ineligible.json') == []
    assert (out/'FEATURES_FACE.md').read_bytes() == (old.REPO/'docs/holistic-migration/FEATURES_FACE.md').read_bytes()
    assert m['implementation']['training/holistic_migration/face_dataset.py'] == old.sha256(old.REPO/'training/holistic_migration/face_dataset.py')
    assert all(name in m['implementation'] for name in old.contract_binding())
    for part in old.PARTITIONS:
        rows = [r for r in source if r['partition'] == part]
        x = np.load(out/f'X_{part}.npy', allow_pickle=False)
        y = np.load(out/f'y_{part}.npy', allow_pickle=False)
        ids = np.load(out/f'clip_ids_{part}.npy', allow_pickle=False)
        assert x.shape == (50,30,1588) and x.dtype == np.float32 and y.dtype == np.int64
        assert ids.dtype.kind == 'U'
        assert ids.tolist() == [r['clip_id'] for r in rows]
        assert y.tolist() == [r['dense_id'] for r in rows]
        for i, row in enumerate(rows):
            raw = old.read_raw(campaign/row['raw_file'], row['raw_sha256'])
            np.testing.assert_array_equal(x[i], prepare_capture(raw).tensor)
        assert m['eligibility']['partitions'][part] == dict(declared=50,selected=50,eligible=50,ineligible=0,not_selected=0,reasons={})
    for row, capture in zip(source, captures):
        for key in old.BYTE_IDENTITY + ('partition','raw_file','raw_sha256'):
            assert capture[key] == row[key]
        assert capture['presence']['face'] == 8 and capture['face_cardinality'] == {'478':8}
        assert capture['source_observation_count'] == 8 and capture['derived_row_count'] == 30
    for name, record in m['artifacts'].items():
        assert old.sha256(out/name) == record['sha256']
        if name.endswith('.npy'):
            value = np.load(out/name,allow_pickle=False)
            assert list(value.shape) == record['shape'] and str(value.dtype) == record['dtype']
        elif name.endswith('.json'):
            old.load_json(out/name)


def test_diagnostic_persists_literal_fit_selection_before_feature_preparation(campaign,tmp_path,monkeypatch):
    from training.holistic_migration import face_dataset as module
    out = tmp_path/'diagnostic'
    rows = [json.loads(s) for s in (campaign/'rows.jsonl').read_text().splitlines()]
    selected = [min(r['clip_id'] for r in rows if r['partition']=='fit' and r['dense_id']==i) for i in range(50)]
    real = module.prepare_capture
    calls = []
    def prepare(fs):
        assert old.load_json(out/'selected_ids.json') == selected
        calls.append(len(fs))
        return real(fs)
    monkeypatch.setattr(module,'prepare_capture',prepare)
    m = module.build_dataset(campaign=campaign,output=out,diagnostic_fit_only=True)
    assert m['mode'] == 'diagnostic_fit_only', 'diagnostic must not silently become a full build'
    assert m['status'] == 'diagnostic_complete' and m['diagnostic_eligible'] is True
    assert len(calls)==50 and not (out/'data_manifest.json').exists()
    assert (out/'diagnostic_manifest.json').exists()
    for part in ['validation','test']:
        assert m['eligibility']['partitions'][part] == dict(declared=50,selected=0,eligible=0,ineligible=0,not_selected=50,reasons={})
        assert np.load(out/f'X_{part}.npy',allow_pickle=False).shape == (0,30,1588)
    captures = old.load_json(out/'capture_rows.json')
    assert len(captures) == 150
    assert all(r['reason']=='not_selected' and r['presence'] is None for r in captures if r['partition']!='fit')


from contextlib import contextmanager


@contextmanager
def altered_campaign(campaign, change):
    """Change only targeted synthetic bytes; restore exact shared fixture in finally."""
    saved = {}
    def save(path):
        if path not in saved: saved[path] = path.read_bytes()
    rows_path = campaign/'rows.jsonl'
    manifest_path = campaign/'extraction_manifest.json'
    save(rows_path); save(manifest_path)
    rows = [json.loads(s) for s in rows_path.read_text().splitlines()]
    try:
        for row in rows:
            raw_path = campaign/row['raw_file']
            fs = old.read_raw(raw_path,row['raw_sha256'])
            changed = change(row, fs)
            if changed is not None:
                save(raw_path); raw_path.unlink()
                row['raw_sha256'] = old.write_raw(raw_path,changed)
                capture = old.prepare_capture(changed)
                row['capture'] = old.capture_receipt(capture)
                row['status'] = 'eligible' if capture.tensor is not None else 'ineligible'
        rows_path.write_text(''.join(json.dumps(r)+'\n' for r in rows))
        m = old.load_json(manifest_path); m['rows_sha256'] = old.sha256(rows_path)
        manifest_path.write_text(json.dumps(m))
        yield
    finally:
        for path, data in saved.items(): path.write_bytes(data)


@pytest.mark.parametrize('partition',['fit','validation'])
def test_full_missing_face_support_fails_with_denominators_and_no_completion(campaign,tmp_path,partition):
    out = tmp_path/'unsupported'
    def change(row,fs):
        if row['partition']==partition and row['dense_id']==0:
            return [replace(f,face=None) if i==3 else f for i,f in enumerate(fs)]
    with altered_campaign(campaign,change):
        with pytest.raises(ValueError,match='eligible support'):
            builder().build_dataset(campaign=campaign,output=out)
        assert not (out/'data_manifest.json').exists()
        eligibility = old.load_json(out/'eligibility.json')
        assert eligibility['partitions'][partition] == dict(declared=50,selected=50,eligible=49,ineligible=1,not_selected=0,reasons={'invalid_face':1})
        assert old.load_json(out/'support_failure.json')['unsupported'] == [[0,partition]]
        assert old.load_json(out/'failure.json')['status']=='failed'
        rows = old.load_json(out/'capture_rows.json')
        target = next(r for r in rows if r['dense_id']==0 and r['partition']==partition)
        assert target['face_missing']==1 and target['face_cardinality']=={'478':7}
        assert target['derived_row_count']==0 and target['source_observation_count']==8
        assert len(old.load_json(out/'ineligible.json'))==1


def validate(out):
    return getattr(builder(),'validate_bundle',lambda path:old.load_json(path/'data_manifest.json'))(out)


def test_consumer_rejects_persisted_failure_even_with_success_manifest(campaign,tmp_path):
    out = tmp_path/'failed-target'
    m = builder().build_dataset(campaign=campaign,output=out)
    assert validate(out)==m
    (out/'failure.json').write_text('{}')
    with pytest.raises(ValueError,match='failed'):
        validate(out)
    assert (out/'data_manifest.json').exists(), 'consumer may not revoke an established completion'


@pytest.fixture(scope='module')
def full_bundle(campaign,tmp_path_factory):
    out = tmp_path_factory.mktemp('face-bundles')/'full'
    builder().build_dataset(campaign=campaign,output=out)
    return out


@contextmanager
def edited_json(path, transform):
    before = path.read_bytes()
    value = json.loads(before)
    transform(value)
    path.write_text(json.dumps(value))
    try: yield
    finally: path.write_bytes(before)


@pytest.mark.parametrize('key,value', [('schema_version',True),('schema_version',1.0),('mode','diagnostic_fit_only'),
    ('training_qualified',0),('live_ready',True),('model_evaluated',True),('feature_version','hm153-v1'),
    ('status','diagnostic_complete'),('tensor_contract','Float32[N,30,153] hm153-v1'),('evidence_kind','source_video')])
def test_consumer_rejects_inexact_or_inconsistent_manifest_schema(full_bundle,key,value):
    path = full_bundle/'data_manifest.json'
    with edited_json(path, lambda m:m.update({key:value})):
        with pytest.raises(ValueError): validate(full_bundle)
    assert validate(full_bundle)['schema_version']==1


@pytest.mark.parametrize('artifact',['X_fit.npy','y_validation.npy','clip_ids_test.npy','capture_rows.json',
    'eligibility.json','class_metadata.json','ineligible.json','selected_ids.json','FEATURES_FACE.md'])
def test_consumer_rejects_artifact_tampering_without_deleting_completion(full_bundle,artifact):
    path = full_bundle/artifact
    before = path.read_bytes()
    try:
        path.write_bytes(before+b' corrupt')
        with pytest.raises(ValueError): validate(full_bundle)
        assert (full_bundle/'data_manifest.json').exists()
    finally: path.write_bytes(before)


@pytest.mark.parametrize('case',['raw','campaign','implementation','graph'])
def test_consumer_rejects_changed_current_provenance(full_bundle,campaign,monkeypatch,case):
    module = builder()
    if case == 'implementation':
        real = module.implementation_binding
        monkeypatch.setattr(module,'implementation_binding',lambda:dict(real(),CHANGED='0'*64))
        with pytest.raises(ValueError): validate(full_bundle)
    else:
        row = json.loads((campaign/'rows.jsonl').read_text().splitlines()[0])
        path = {'raw':campaign/row['raw_file'],'campaign':campaign/'extraction_manifest.json',
                'graph':Path(old.load_json(campaign/'attempt.json')['graph']['paths']['classes'])}[case]
        before = path.read_bytes()
        try:
            path.write_bytes(before+b' ')
            with pytest.raises(ValueError): validate(full_bundle)
        finally: path.write_bytes(before)
    assert (full_bundle/'data_manifest.json').exists()


@pytest.mark.parametrize('case',['count_float','capture_count_bool','selection_order','label','dtype','face_value','missing_artifact','shape_float'])
def test_consumer_rejects_rebound_semantic_artifact_corruption(full_bundle,case):
    names = {'count_float':'eligibility.json','capture_count_bool':'capture_rows.json',
             'selection_order':'selected_ids.json','label':'y_fit.npy','dtype':'X_fit.npy',
             'face_value':'X_fit.npy','missing_artifact':None,'shape_float':None}
    name = names[case]
    manifest_path = full_bundle/'data_manifest.json'
    saved_manifest = manifest_path.read_bytes()
    path = full_bundle/name if name else None
    saved_artifact = path.read_bytes() if path else None
    try:
        m = old.load_json(manifest_path)
        if case == 'missing_artifact': del m['artifacts']['X_fit.npy']
        elif case == 'shape_float': m['artifacts']['X_fit.npy']['shape'][0] = 50.0
        elif name.endswith('.json'):
            v = old.load_json(path)
            if case == 'count_float':
                v['partitions']['fit']['eligible'] = 50.0
                m['eligibility'] = v
            if case == 'capture_count_bool': v[0]['hand_count'] = True
            if case == 'selection_order': v.reverse()
            path.write_text(json.dumps(v))
        else:
            v = np.load(path,allow_pickle=False)
            if case == 'label': v[0] = 1
            if case == 'dtype': v = v.astype(np.float64)
            if case == 'face_value': v[0,0,153] += .25
            with path.open('wb') as stream: np.save(stream,v,allow_pickle=False)
            m['artifacts'][name].update(shape=list(v.shape),dtype=str(v.dtype))
        if name: m['artifacts'][name]['sha256'] = old.sha256(path)
        manifest_path.write_text(json.dumps(m))
        with pytest.raises(ValueError): validate(full_bundle)
    finally:
        manifest_path.write_bytes(saved_manifest)
        if path: path.write_bytes(saved_artifact)


@pytest.mark.parametrize('rollback_fails',[False,True])
def test_publication_readback_preserves_primary_and_denies_failed_target(campaign,tmp_path,monkeypatch,rollback_fails):
    out = tmp_path/'publication-fault'
    target = out/'data_manifest.json'
    primary = ValueError('PRIMARY publication readback fault')
    real_open, real_unlink = Path.open, Path.unlink
    def opened(path,*args,**kwargs):
        if path==target and args and args[0]=='rb': raise primary
        return real_open(path,*args,**kwargs)
    def unlinked(path,*args,**kwargs):
        if path==target and rollback_fails: raise OSError('SECONDARY rollback fault')
        return real_unlink(path,*args,**kwargs)
    with monkeypatch.context() as faults:
        faults.setattr(Path,'open',opened); faults.setattr(Path,'unlink',unlinked)
        with pytest.raises(ValueError) as caught:
            builder().build_dataset(campaign=campaign,output=out)
        assert caught.value is primary
    assert (out/'data_manifest.json.pending').exists()
    assert target.exists() is rollback_fails
    assert old.load_json(out/'failure.json') == dict(status='failed',disposition='incomplete_non_gating')
    with pytest.raises(ValueError,match='failed'): validate(out)
    before = {p.name:p.read_bytes() for p in out.iterdir() if p.is_file()}
    with pytest.raises(ValueError,match='already exists'):
        builder().build_dataset(campaign=campaign,output=out)
    assert before=={p.name:p.read_bytes() for p in out.iterdir() if p.is_file()}


def test_malformed_face_retains_error_identity_and_failed_disposition(campaign,tmp_path):
    out = tmp_path/'cardinality-error'
    def change(row,fs):
        if row['dense_id']==0 and row['partition']=='fit':
            return [replace(f,face=np.zeros((477,3))) if i==0 else f for i,f in enumerate(fs)]
    with altered_campaign(campaign,change):
        # Old full campaign validator intentionally accepts ragged cardinality.
        old.validate_campaign(campaign)
        with pytest.raises(ValueError,match='face'):
            builder().build_dataset(campaign=campaign,output=out)
        assert (out/'failure.json').exists(), 'source error must persist failed attempt disposition'
        failures = old.load_json(out/'error_rows.json')
        assert failures['declared']==150 and failures['errors']==1
        assert len(failures['rows'])==150
        bad = next(r for r in failures['rows'] if r['status']=='error')
        assert bad['clip_id']=='clips/0/0.MOV' and bad['raw_sha256']
        assert not (out/'data_manifest.json').exists()
        with pytest.raises(ValueError,match='failed'): validate(out)


def test_builder_final_raw_digest_recheck_rejects_midbuild_change(campaign,tmp_path,monkeypatch):
    module = builder(); out = tmp_path/'midbuild'
    row = json.loads((campaign/'rows.jsonl').read_text().splitlines()[0])
    target = campaign/row['raw_file']; before = target.read_bytes()
    real = module._write_array
    def write(path,array):
        result = real(path,array)
        if path.name=='X_fit.npy': target.write_bytes(before+b'tampered after preparation')
        return result
    monkeypatch.setattr(module,'_write_array',write)
    try:
        with pytest.raises(ValueError,match='raw'):
            module.build_dataset(campaign=campaign,output=out)
        assert not (out/'data_manifest.json').exists()
        assert (out/'failure.json').exists()
    finally: target.write_bytes(before)


def test_real_subprocess_cli_help_full_diagnostic_and_rejections(campaign,tmp_path):
    import subprocess,sys
    command = [sys.executable,'-E','-B','-m','training.holistic_migration.face_dataset']
    results = []
    def execute(arguments):
        result = subprocess.run(command+arguments,cwd=old.REPO,capture_output=True,text=True)
        results.append(dict(command=command+arguments,exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr))
        (tmp_path/'cli-results.json').write_text(json.dumps(results,indent=2))
        return result
    help_result = execute(['--help'])
    assert help_result.returncode==0 and '--campaign' in help_result.stdout and '--diagnostic-fit-only' in help_result.stdout
    out = tmp_path/'cli-full'
    success = execute(['--campaign',str(campaign),'--output',str(out)])
    assert success.returncode==0,success.stderr
    assert validate(out)['evidence_kind']=='synthetic_in_process'
    again = execute(['--campaign',str(campaign),'--output',str(out)])
    assert again.returncode==2 and 'already exists' in again.stderr
    bad = execute(['--campaign','relative','--output',str(tmp_path/'never')])
    assert bad.returncode==2 and 'absolute' in bad.stderr
    overlap = execute(['--campaign',str(campaign),'--output',str(campaign/'nested')])
    assert overlap.returncode==2 and 'overlap' in overlap.stderr
    diagnostic = tmp_path/'cli-diagnostic'
    result = execute(['--campaign',str(campaign),'--output',str(diagnostic),'--diagnostic-fit-only'])
    assert result.returncode==0,result.stderr
    assert not (diagnostic/'data_manifest.json').exists()
    assert old.load_json(diagnostic/'diagnostic_manifest.json')['mode']=='diagnostic_fit_only'


def test_diagnostic_never_replaces_first_frozen_fit_id_with_eligible_alternative(campaign,tmp_path):
    paths = {k:Path(v) for k,v in old.load_json(campaign/'attempt.json')['graph']['paths'].items()}
    root = paths['classes'].parent
    relative = 'clips/0/-first.MOV'
    source_file = paths['raw_root']/relative
    raw_file = campaign/'raw/999999.npz'
    originals = [paths[k] for k in ['partition_manifest','source_inventory','upstream_inventory','decode_summary','decode_records']]
    originals += [campaign/n for n in ['selected_ids.json','attempt.json','rows.jsonl','extraction_manifest.json']]
    saved = {path:path.read_bytes() for path in originals}
    try:
        source_file.write_bytes(b'SYNTHETIC extra fit source')
        membership = old.load_json(paths['partition_manifest'])
        inventory = old.load_json(paths['source_inventory'])
        upstream = old.load_json(paths['upstream_inventory'])
        summary = old.load_json(paths['decode_summary'])
        records = [json.loads(s) for s in paths['decode_records'].read_text().splitlines()]
        source = dict(next(r for r in membership['rows'] if r['dense_id']==0 and r['partition']=='fit'),
                      clip_id=relative,source_token=relative.replace('/',chr(92)),archive_member=relative,
                      video_bytes=source_file.stat().st_size,video_sha256=old.sha256(source_file))
        membership['rows'].append(source); membership['counts']['fit']+=1
        inventory['rows'].append({k:v for k,v in source.items() if k!='partition'})
        inventory['summary']['selected_sources']+=1; inventory['summary']['unique_video_byte_hashes']+=1
        upstream['rows'].append({k:source[k] for k in old.IDENTITY}); upstream['counts']['train']+=1
        decoded = dict(next(r for r in records if r['dense_id']==0),**{k:source[k] for k in old.BYTE_IDENTITY})
        decoded['decoded_bgr_sha256']=old.canonical_hash(relative)
        records.append(decoded); summary['source_count']+=1; summary['ok']+=1
        rebind(root,membership,inventory,upstream,records,summary)
        graph = old.preflight(**{k:paths[k] for k in ['partition_manifest','source_inventory','decode_summary','raw_root','classes','model']})
        fs=observed(); fs[3]=replace(fs[3],face=None)
        digest=old.write_raw(raw_file,fs)
        rows=[json.loads(s) for s in (campaign/'rows.jsonl').read_text().splitlines()]
        rows.append(dict(source,raw_file='raw/999999.npz',raw_sha256=digest,status='eligible',decoded_frames=16,
                         decoded_bgr_sha256=decoded['decoded_bgr_sha256'],capture=old.capture_receipt(old.prepare_capture(fs))))
        rows.sort(key=lambda r:r['clip_id'])
        (campaign/'rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
        (campaign/'selected_ids.json').write_text(json.dumps([r['clip_id'] for r in rows]))
        attempt=old.load_json(campaign/'attempt.json'); attempt['graph']=old.graph_receipt(graph)
        attempt['selected_ids_sha256']=old.sha256(campaign/'selected_ids.json')
        (campaign/'attempt.json').write_text(json.dumps(attempt))
        manifest=dict(old.load_json(campaign/'extraction_manifest.json'),**attempt)
        manifest.update(rows_sha256=old.sha256(campaign/'rows.jsonl'),attempt_sha256=old.sha256(campaign/'attempt.json'),
                        counts=dict(declared=151,selected=151,processed=151,errors=0))
        (campaign/'extraction_manifest.json').write_text(json.dumps(manifest))
        old.validate_campaign(campaign)
        out=tmp_path/'literal-first'
        result=builder().build_dataset(campaign=campaign,output=out,diagnostic_fit_only=True)
        assert old.load_json(out/'selected_ids.json')[0]==relative
        assert result['diagnostic_eligible'] is False
        captures=old.load_json(out/'capture_rows.json')
        assert next(r for r in captures if r['clip_id']=='clips/0/0.MOV')['reason']=='not_selected'
        assert result['eligibility']['partitions']['fit']['declared']==51
        assert result['eligibility']['partitions']['fit']['selected']==50
    finally:
        for path,data in saved.items(): path.write_bytes(data)
        source_file.unlink(missing_ok=True);raw_file.unlink(missing_ok=True)


def test_zero_eligible_test_partition_has_exact_empty_shape(campaign,tmp_path):
    out = tmp_path/'empty-test'
    def change(row,fs):
        if row['partition']=='test': return [replace(f,face=None) for f in fs]
    with altered_campaign(campaign,change):
        m = builder().build_dataset(campaign=campaign,output=out)
        assert np.load(out/'X_test.npy',allow_pickle=False).shape==(0,30,1588)
        assert np.load(out/'y_test.npy',allow_pickle=False).dtype==np.int64
        assert np.load(out/'clip_ids_test.npy',allow_pickle=False).dtype.kind=='U'
        assert m['eligibility']['partitions']['test']==dict(declared=50,selected=50,eligible=0,ineligible=50,not_selected=0,reasons={'invalid_face':50})
        assert len(old.load_json(out/'ineligible.json'))==50
        assert validate(out)==m


@pytest.mark.parametrize('case',['campaign_child','campaign_ancestor','raw_child','decode_child','repo','relative','collision','symlink'])
def test_builder_denies_output_collisions_and_protected_overlap(campaign,tmp_path,case):
    graph = old.load_json(campaign/'attempt.json')['graph']['paths']
    out = tmp_path/'out'
    if case=='campaign_child': out=campaign/'never'
    if case=='campaign_ancestor': out=campaign.parent
    if case=='raw_child': out=Path(graph['raw_root'])/'never'
    if case=='decode_child': out=Path(graph['decode_summary']).parent/'never'
    if case=='repo': out=old.REPO/'never'
    if case=='relative': out=Path('relative')
    if case=='collision': out.mkdir(); (out/'sentinel').write_bytes(b'preserve existing bytes')
    if case=='symlink':
        link=tmp_path/'linked'; link.symlink_to(campaign,target_is_directory=True); out=link/'never'
    before=old.sha256(campaign/'extraction_manifest.json')
    with pytest.raises(ValueError): builder().build_dataset(campaign=campaign,output=out)
    assert old.sha256(campaign/'extraction_manifest.json')==before
    if case=='collision': assert (out/'sentinel').read_bytes()==b'preserve existing bytes'


@pytest.mark.parametrize('case',['count_float','diagnostic','raw_digest','identity','decoder'])
def test_builder_uses_unchanged_campaign_provenance_validation(campaign,tmp_path,case):
    out=tmp_path/'invalid-provenance'
    rows_path=campaign/'rows.jsonl'; manifest_path=campaign/'extraction_manifest.json'
    saved_rows=rows_path.read_bytes(); saved_manifest=manifest_path.read_bytes()
    rows=[json.loads(s) for s in rows_path.read_text().splitlines()]
    m=old.load_json(manifest_path)
    try:
        if case=='count_float': m['counts']['declared']=150.0
        if case=='diagnostic': m['full_campaign_qualification']=False
        if case=='raw_digest': rows[0]['raw_sha256']='0'*64
        if case=='identity': rows[0]['signer_id']='unbound'
        if case=='decoder': rows[0]['decoded_frames']=999
        rows_path.write_text(''.join(json.dumps(r)+'\n' for r in rows))
        m['rows_sha256']=old.sha256(rows_path); manifest_path.write_text(json.dumps(m))
        with pytest.raises(ValueError): builder().build_dataset(campaign=campaign,output=out)
        assert not out.exists(), 'invalid producer graph cannot create a new-feature attempt'
    finally:
        rows_path.write_bytes(saved_rows); manifest_path.write_bytes(saved_manifest)


def test_builder_imports_no_native_inference(campaign,tmp_path,monkeypatch):
    import builtins
    real=builtins.__import__
    def guarded(name,*args,**kwargs):
        if name.split('.')[0] in ['cv2','mediapipe','tensorflow']:
            raise AssertionError('new builder must not import inference or training')
        return real(name,*args,**kwargs)
    monkeypatch.setattr(builtins,'__import__',guarded)
    m=builder().build_dataset(campaign=campaign,output=tmp_path/'no-inference',diagnostic_fit_only=True)
    assert m['evidence_kind']=='synthetic_in_process'


@pytest.mark.parametrize('stage',['pending_readback','link','json_readback'])
def test_publication_fault_stages_retain_pending_and_primary(tmp_path,monkeypatch,stage):
    module=builder(); out=tmp_path/'publish'; out.mkdir()
    target=out/'data_manifest.json'; pending=out/'data_manifest.json.pending'
    primary=ValueError('PRIMARY '+stage)
    real_open,real_link=Path.open,module.os.link
    def opened(path,*args,**kwargs):
        if stage=='pending_readback' and path==pending and not args: raise primary
        if stage=='json_readback' and path==target and not args: raise primary
        return real_open(path,*args,**kwargs)
    def linked(source,destination,*args,**kwargs):
        if stage=='link': raise primary
        return real_link(source,destination,*args,**kwargs)
    with monkeypatch.context() as faults:
        faults.setattr(Path,'open',opened); faults.setattr(module.os,'link',linked)
        with pytest.raises(ValueError) as caught: module._publish_completion(target,{'synthetic':True})
        assert caught.value is primary
    assert pending.exists() and not target.exists()
    assert old.load_json(out/'failure.json')['status']=='failed'


def test_failure_diagnostics_and_rollback_failure_never_mask_primary(campaign,tmp_path,monkeypatch):
    module=builder(); out=tmp_path/'all-secondary-fail'
    target=out/'data_manifest.json'
    primary=RuntimeError('PRIMARY')
    real_open=Path.open
    def opened(path,*args,**kwargs):
        if path==target and args and args[0]=='rb': raise primary
        if path==out/'failure.json': raise OSError('SECONDARY diagnostic write')
        return real_open(path,*args,**kwargs)
    def unlinked(path,*args,**kwargs): raise OSError('SECONDARY rollback')
    with monkeypatch.context() as faults:
        faults.setattr(Path,'open',opened);faults.setattr(Path,'unlink',unlinked)
        with pytest.raises(RuntimeError) as caught: module.build_dataset(campaign=campaign,output=out)
        assert caught.value is primary
    assert target.exists() and not (out/'failure.json').exists()
    # A valid-looking unverified completion must not pass consumer admission.
    with pytest.raises(ValueError): validate(out)


def test_exclusive_publication_never_overwrites_or_revokes_foreign_completion(tmp_path):
    module=builder(); out=tmp_path/'exclusive'; out.mkdir(); target=out/'data_manifest.json'
    target.write_bytes(b'FOREIGN established completion')
    with pytest.raises(FileExistsError): module._publish_completion(target,{'new':True})
    assert target.read_bytes()==b'FOREIGN established completion'
    assert (out/'data_manifest.json.pending').exists()


def test_consumer_transient_read_failure_preserves_established_manifest(full_bundle,monkeypatch):
    target=full_bundle/'data_manifest.json'; before=target.read_bytes();real_open=Path.open
    def opened(path,*args,**kwargs):
        if path==target: raise OSError('transient read failure')
        return real_open(path,*args,**kwargs)
    with monkeypatch.context() as faults:
        faults.setattr(Path,'open',opened)
        with pytest.raises(OSError): validate(full_bundle)
    assert target.read_bytes()==before and not (full_bundle/'failure.json').exists()
    assert validate(full_bundle)['status']=='complete'



@pytest.mark.parametrize('case',['empty_attempt','extra_manifest','missing_campaign','invalid_path','nonobject_manifest'])
def test_consumer_rejects_malformed_schema_even_with_rebound_attempt(full_bundle,case):
    target = full_bundle/'data_manifest.json'; attempt_path = full_bundle/'attempt.json'
    before = target.read_bytes(); original_attempt = attempt_path.read_bytes()
    try:
        m = old.load_json(target)
        if case == 'empty_attempt':
            attempt_path.write_text('{}')
            m['artifacts']['attempt.json']['sha256'] = old.sha256(attempt_path)
        if case == 'extra_manifest': m['unrecognized_acceptance']=True
        if case == 'missing_campaign': del m['campaign']
        if case == 'invalid_path': m['campaign']=None
        if case == 'nonobject_manifest': m=[]
        target.write_text(json.dumps(m))
        with pytest.raises(ValueError): validate(full_bundle)
    finally:
        target.write_bytes(before); attempt_path.write_bytes(original_attempt)


def test_infeasible_diagnostic_cli_stops_without_claiming_full_qualification(campaign,tmp_path):
    import subprocess,sys
    out = tmp_path/'infeasible-diagnostic'
    def change(row,fs):
        if row['dense_id']==0 and row['partition']=='fit':
            return [replace(f,face=None) if i==3 else f for i,f in enumerate(fs)]
    with altered_campaign(campaign,change):
        command = [sys.executable,'-E','-B','-m','training.holistic_migration.face_dataset',
                   '--campaign',str(campaign),'--output',str(out),'--diagnostic-fit-only']
        result = subprocess.run(command,cwd=old.REPO,capture_output=True,text=True)
        (tmp_path/'diagnostic-cli.json').write_text(json.dumps(dict(command=command,exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr),indent=2))
        assert result.returncode==2, 'infeasible diagnostic must stop and request a new parent decision'
        m = old.load_json(out/'diagnostic_manifest.json')
        assert m['diagnostic_eligible'] is False and m['status']=='diagnostic_complete'
        assert not (out/'data_manifest.json').exists()
        assert m['eligibility']['partitions']['fit']['eligible']==49
        assert m['training_qualified'] is False
        # Even renaming the diagnostic marker cannot pass full consumer admission.
        (out/'data_manifest.json').write_bytes((out/'diagnostic_manifest.json').read_bytes())
        with pytest.raises(ValueError): validate(out)
