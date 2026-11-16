"""Entirely synthetic numeric codec/source/bundle fixtures."""
from dataclasses import replace
import hashlib
import importlib
import json
from pathlib import Path
import numpy as np
import pytest
from training.holistic_migration.features import RawFrame, pack_frame
from .test_sequence import frames


def dataset():
    return importlib.import_module('training.holistic_migration.dataset')


def test_raw_codec_roundtrip_exact_none_and_variable_face(tmp_path):
    observed = frames()
    observed[0] = replace(observed[0], face=np.arange(478*3,dtype=np.float64).reshape(478,3)/13)
    observed[1] = replace(observed[1], face=np.empty((0,3)))
    observed[2] = replace(observed[2], face=np.full((2,3), -.125), left_hand=None)
    observed[3] = replace(observed[3], pose=None)
    observed[4] = replace(observed[4], right_hand=np.full((21,3), .8))
    path = tmp_path/'raw.npz'
    digest = dataset().write_raw(path, observed)
    result = dataset().read_raw(path, digest)
    assert len(result) == len(observed)
    for a,b in zip(observed,result):
        assert a.timestamp_ms == b.timestamp_ms
        for name in ['pose','left_hand','right_hand','face']:
            x,y = getattr(a,name),getattr(b,name)
            if x is None: assert y is None
            else: np.testing.assert_array_equal(x,y)
        np.testing.assert_array_equal(pack_frame(a),pack_frame(b))
    with np.load(path, allow_pickle=False) as z:
        assert all(z[k].dtype.kind != 'O' for k in z.files)



@pytest.mark.parametrize('corruption', ['offset','float_timestamp','bool_presence','absent_block','absent_face',
                                        'nonfinite','object','extra','duplicate_time','digest'])
def test_raw_codec_rejects_corruption_even_rebound_digest(tmp_path, corruption):
    d = dataset()
    path = tmp_path/'raw.npz'
    d.write_raw(path, frames())
    with np.load(path, allow_pickle=False) as z:
        values = {k:z[k] for k in z.files}
    if corruption == 'offset': values['face_offsets'][-1] = 1
    if corruption == 'float_timestamp': values['timestamps'] = values['timestamps'].astype(float)
    if corruption == 'bool_presence': values['pose_present'] = values['pose_present'].astype(bool)
    if corruption == 'absent_block': values['right_hand'][0,0,0] = 1
    if corruption == 'absent_face':
        values['face_values'] = np.ones((1,3))
        values['face_offsets'][1:] = 1
    if corruption == 'nonfinite': values['pose'][0,0,0] = np.inf
    if corruption == 'object': values['pose'] = values['pose'].astype(object)
    if corruption == 'extra': values['unrecognized'] = np.array([1])
    if corruption == 'duplicate_time': values['timestamps'][1] = 0
    with path.open('wb') as stream: np.savez_compressed(stream, **values)
    digest = d.sha256(path) if corruption != 'digest' else '0'*64
    with pytest.raises(ValueError): d.read_raw(path, digest)


@pytest.mark.parametrize('dtype', [np.int64, np.uint64], ids=['signed', 'unsigned'])
def test_raw_integer_maximum_rejected_before_open(tmp_path, monkeypatch, dtype):
    value = int(np.iinfo(dtype).max)
    observed = replace(frames()[0], face=np.array([[value, 0, 0]], dtype=dtype))
    # Face is excluded by normalization: a normalized-output check cannot detect loss.
    np.testing.assert_array_equal(pack_frame(observed), pack_frame(frames()[0]))
    path = tmp_path/'must-not-publish.npz'
    opened = []
    real_open = Path.open
    def track_open(target, *args, **kwargs):
        if target == path:
            opened.append((args, kwargs))
        return real_open(target, *args, **kwargs)
    monkeypatch.setattr(Path, 'open', track_open)
    with pytest.raises(ValueError, match='losslessly'):
        dataset().write_raw(path, [observed])
    assert not opened and not path.exists()


def integer_frame(component, dtype, values):
    shape = {'pose': (33, 4), 'left_hand': (21, 3),
             'right_hand': (21, 3), 'face': (5, 3)}[component]
    value = np.resize(np.array(values, dtype=dtype), shape)
    if component == 'pose':
        # Keep usable shoulders; extreme raw values are elsewhere, not an
        # unrelated normalization overflow/invalid-geometry rejection.
        value[11] = [0, 0, 0, 1]
        value[12] = [2, 0, 0, 1]
    return replace(frames()[0], **{component: value})


@pytest.mark.parametrize('component', ['pose', 'left_hand', 'right_hand', 'face'])
@pytest.mark.parametrize('dtype,values', [
    (np.int64, [-(2**63), -(2**63)+1024, -(2**53), -1, 0, 2**53,
                2**53+2, 2**62, 2**63-1024]),
    (np.uint64, [0, 1, 2**53, 2**53+2, 2**63, 2**63+2048, 2**64-2048]),
    *[(dtype, [int(np.iinfo(dtype).min), 0, 1, int(np.iinfo(dtype).max)])
      for dtype in [np.int8, np.uint8, np.int16, np.uint16, np.int32, np.uint32]],
], ids=['int64-large', 'uint64-large', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32'])
def test_raw_exact_representable_integer_controls(tmp_path, component, dtype, values):
    observed = integer_frame(component, dtype, values)
    assert np.isfinite(pack_frame(observed)).all()
    path = tmp_path/'exact.npz'
    checksum = dataset().write_raw(path, [observed])
    back = dataset().read_raw(path, checksum)[0]
    for name in ['pose', 'left_hand', 'right_hand', 'face']:
        source, decoded = getattr(observed, name), getattr(back, name)
        if source is None:
            assert decoded is None
        else:
            assert source.shape == decoded.shape and decoded.dtype == np.float64
            for original, stored in zip(source.flat, decoded.flat):
                if source.dtype.kind in 'iu':
                    # Python ratio/int equality, never mixed NumPy float/int.
                    assert float(stored).as_integer_ratio() == (int(original), 1)
                else:
                    assert float(stored).hex() == float(original).hex()
    np.testing.assert_array_equal(pack_frame(observed), pack_frame(back))


@pytest.mark.parametrize('component', ['pose', 'left_hand', 'right_hand', 'face'])
@pytest.mark.parametrize('dtype,value', [
    (np.int64, 2**63-1), (np.uint64, 2**64-1),
    (np.int64, -(2**63)+1), (np.int64, 2**63-2),
    (np.uint64, 2**64-2), (np.int64, 2**53+1),
    (np.uint64, 2**53+1), (np.int64, -(2**53)-1),
])
def test_raw_nonrepresentable_components_rejected_before_publication(tmp_path, monkeypatch, component, dtype, value):
    bad = replace(integer_frame(component, dtype, [value]), timestamp_ms=67)
    assert np.isfinite(pack_frame(bad)).all()
    path = tmp_path/'never.npz'
    opened = []
    real_open = Path.open
    def track_open(target, *args, **kwargs):
        if target == path:
            opened.append((args, kwargs))
        return real_open(target, *args, **kwargs)
    monkeypatch.setattr(Path, 'open', track_open)
    # A late invalid component must also fail before any partial NPZ is opened.
    with pytest.raises(ValueError, match='losslessly'):
        dataset().write_raw(path, [frames()[0], bad])
    assert not opened and not path.exists()


@pytest.mark.parametrize('dtype', [np.float16, np.float32, np.float64, np.longdouble])
def test_raw_exact_float_width_controls(tmp_path, dtype):
    observed = replace(frames()[0], face=np.array([[0., -0., .125], [-.5, 1., 8.]], dtype=dtype))
    path = tmp_path/'float.npz'
    back = dataset().read_raw(path, dataset().write_raw(path, [observed]))[0]
    for source, stored in zip(observed.face.flat, back.face.flat):
        assert float(source).hex() == float(stored).hex()
    np.testing.assert_array_equal(pack_frame(observed), pack_frame(back))


def test_raw_rejection_preserves_existing_target(tmp_path):
    path = tmp_path/'existing.npz'
    before = b'original target is never opened or overwritten'
    path.write_bytes(before)
    bad = replace(frames()[0], face=np.array([[2**64-1, 0, 0]], dtype=np.uint64))
    with pytest.raises(ValueError, match='losslessly'):
        dataset().write_raw(path, [bad])
    assert path.read_bytes() == before


def test_raw_writer_rejects_masked_and_nonmonotonic(tmp_path):
    d = dataset()
    bad = frames()
    bad[1] = replace(bad[1], timestamp_ms=0)
    with pytest.raises(ValueError): d.write_raw(tmp_path/'bad.npz', bad)
    bad = [replace(frames()[0], face=np.ma.array(np.zeros((4,3))))]
    with pytest.raises(ValueError): d.write_raw(tmp_path/'masked.npz', bad)



def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, sort_keys=True, allow_nan=False))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def graph_fixture(root):
    """Full 50-class graph, three partitions, literal sparse original IDs."""
    root.mkdir(parents=True, exist_ok=True)
    originals = list(range(25)) + list(range(49,74))
    selected = [{'id':oid, 'label':f'SYNTHETIC {oid}', 'category':'SYNTHETIC'} for oid in originals]
    dump(root/'classes.json', {'selected':selected})
    (root/'model.task').write_bytes(b'NOT A REAL MODEL - SYNTHETIC')
    rows,records = [],[]
    bgr = np.full((8,12,3), [7,19,41], dtype=np.uint8)
    pixel = hashlib.sha256()
    for _ in range(16):
        pixel.update(np.asarray(bgr.shape,dtype='<i4').tobytes())
        pixel.update(bgr.tobytes())
    for dense,c in enumerate(selected):
        for number,part in enumerate(['fit','validation','test']):
            clip = f'clips/{c["id"]}/{number}.MOV'
            path = root/'raw'/clip
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(clip.encode())
            row = dict(clip_id=clip,source_token=clip.replace('/',chr(92)), original_id=c['id'],
                       dense_id=dense,label=c['label'],csv_label=c['label'], official_split='test' if part=='test' else 'train',
                       signer_id=None,archive_member=clip,video_bytes=path.stat().st_size,video_sha256=digest(path),partition=part)
            rows.append(row)
            rec={k:v for k,v in row.items() if k!='partition'}
            # Real audit pixels differ by source; fake frames encode source index.
            p = hashlib.sha256()
            for i in range(16):
                image = bgr.copy(); image[0,0,0] = dense; image[0,0,1] = number; image[0,0,2] = i
                p.update(np.asarray(image.shape,dtype='<i4').tobytes()); p.update(image.tobytes())
            records.append(dict(rec,status='ok',decoded_frames=16,declared_frames=16.0,fps=30.0,
                                shapes=[[8,12,3]],backend='SYNTHETIC',decoded_bgr_sha256=p.hexdigest()))
    dump(root/'selected-source-inventory.json', {'counts':{'train':100,'test':50},'labels':selected,'class_map_sha256':digest(root/'classes.json'),
                                               'rows':[{k:v for k,v in r.items() if k not in ['partition','video_bytes','video_sha256','archive_member']} for r in rows]})
    dump(root/'inventory.json',dict(archive_sha256='a'*64, source_inventory_sha256=digest(root/'selected-source-inventory.json'),
                                 summary=dict(selected_sources=150,unique_video_byte_hashes=150,raw_duplicate_groups=0,
                                              cross_official_split_duplicate_groups=0,cross_label_duplicate_groups=0),
                                 rows=[{k:v for k,v in r.items() if k!='partition'} for r in rows]))
    dump(root/'partitions.json',dict(schema_version=1,source_inventory_sha256=digest(root/'inventory.json'),
                                   archive_sha256='a'*64,class_map_sha256=digest(root/'classes.json'),
                                   counts=dict(fit=50,validation=50,test=50),raw_duplicate_groups=0,rows=rows))
    records_path=root/'decode'/'records.jsonl'; records_path.parent.mkdir()
    records_path.write_text(''.join(json.dumps(r)+'\n' for r in records))
    dump(root/'decode'/'summary.json',dict(source_count=150,ok=150,errors=0,decoded_pixel_duplicate_groups=0,
         cross_official_split_pixel_duplicate_groups=0,cross_label_pixel_duplicate_groups=0,duplicate_groups=[],
         source_inventory_sha256=digest(root/'inventory.json'),records_sha256=digest(records_path)))
    return dict(partition_manifest=root/'partitions.json',source_inventory=root/'inventory.json',
                decode_summary=root/'decode'/'summary.json',raw_root=root/'raw',classes=root/'classes.json',model=root/'model.task')


def test_public_preflight_validates_complete_synthetic_graph(tmp_path):
    kwargs=graph_fixture(tmp_path/'source')
    graph=dataset().preflight(**kwargs,output=tmp_path/'campaign')
    assert len(graph.rows)==150 and len(graph.classes)==50
    assert graph.classes[25]['original_id']==49
    assert graph.paths['decode_records']==kwargs['decode_summary'].parent/'records.jsonl'
    assert graph.bindings['partition_manifest']==digest(kwargs['partition_manifest'])
    assert not (tmp_path/'campaign').exists()



def rebind(root, membership=None, inventory=None, upstream=None, records=None, summary=None):
    """Rebind all hashes so schema tests cannot stop at stale digest checks."""
    membership = membership if membership is not None else json.loads((root/'partitions.json').read_text())
    inventory = inventory if inventory is not None else json.loads((root/'inventory.json').read_text())
    upstream = upstream if upstream is not None else json.loads((root/'selected-source-inventory.json').read_text())
    summary = summary if summary is not None else json.loads((root/'decode/summary.json').read_text())
    if records is not None: (root/'decode/records.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in records))
    dump(root/'selected-source-inventory.json',upstream)
    inventory['source_inventory_sha256']=digest(root/'selected-source-inventory.json'); dump(root/'inventory.json',inventory)
    membership['source_inventory_sha256']=digest(root/'inventory.json'); dump(root/'partitions.json',membership)
    summary['source_inventory_sha256']=digest(root/'inventory.json')
    summary['records_sha256']=digest(root/'decode/records.jsonl'); dump(root/'decode/summary.json',summary)


@pytest.mark.parametrize('case,match', [('schema_bool','schema_version'),('dense_float','dense_id'),('bytes_bool','video_bytes'),
    ('count_float','count'),('decode_float','decoded_frames'),('duplicate','duplicate'),('traversal','clip_id'),
    ('bad_token','source_token'),('test_to_fit','official'),('identity','identity'),('archive','archive'),
    ('decode_count','source_count'),('pixel_duplicate','duplicate'),('upstream_count','count'),
    ('class_order','class'),('class_bool','class'),('partition','partition')])
def test_public_preflight_rebound_tampering(tmp_path,case,match):
    root=tmp_path/'source'; kwargs=graph_fixture(root)
    m=json.loads((root/'partitions.json').read_text()); inv=json.loads((root/'inventory.json').read_text())
    u=json.loads((root/'selected-source-inventory.json').read_text()); s=json.loads((root/'decode/summary.json').read_text())
    rec=[json.loads(x) for x in (root/'decode/records.jsonl').read_text().splitlines()]
    if case=='schema_bool': m['schema_version']=True
    if case=='dense_float':
        for rows in [m['rows'],inv['rows'],u['rows'],rec]: rows[0]['dense_id']=0.0
    if case=='bytes_bool':
        for rows in [m['rows'],inv['rows'],rec]: rows[0]['video_bytes']=True
    if case=='count_float': m['counts']['fit']=50.0
    if case=='decode_float': rec[0]['decoded_frames']=16.0
    if case=='duplicate':
        for rows in [m['rows'],inv['rows'],u['rows'],rec]: rows.append(rows[0].copy())
    if case=='traversal':
        for rows in [m['rows'],inv['rows'],u['rows'],rec]: rows[0]['clip_id']='clips/../escape.MOV'
    if case=='bad_token':
        for rows in [m['rows'],inv['rows'],u['rows'],rec]: rows[0]['source_token']='clips/0/0.MOV'
    if case=='test_to_fit': m['rows'][2]['partition']='fit'; m['counts'].update(fit=51,test=49)
    if case=='identity': rec[0]['signer_id']='changed'
    if case=='archive': m['archive_sha256']='b'*64
    if case=='decode_count': s['source_count']=149
    if case=='pixel_duplicate': rec[1]['decoded_bgr_sha256']=rec[0]['decoded_bgr_sha256']
    if case=='upstream_count': u['counts']={'train':99,'test':50}
    if case=='class_order':
        c=json.loads((root/'classes.json').read_text()); c['selected'].reverse(); dump(root/'classes.json',c)
        m['class_map_sha256']=digest(root/'classes.json'); u['class_map_sha256']=digest(root/'classes.json')
    if case=='class_bool':
        c=json.loads((root/'classes.json').read_text()); c['selected'][0]['id']=False; dump(root/'classes.json',c)
        m['class_map_sha256']=digest(root/'classes.json'); u['class_map_sha256']=digest(root/'classes.json')
    if case=='partition': m['rows'][0]['partition']='train'
    rebind(root,m,inv,u,rec,s)
    with pytest.raises(ValueError,match=match): dataset().preflight(**kwargs,output=tmp_path/'campaign')



@pytest.mark.parametrize('case,match', [('existing','exists'),('inside_raw','overlap'),('inside_repo','repository'),
    ('ancestor','overlap'),('symlink','symlink'),('raw_symlink','symlink'),('relative','absolute'),
    ('dataless','DATALESS'),('stale','digest')])
def test_public_preflight_path_and_byte_boundaries(tmp_path,monkeypatch,case,match):
    kwargs=graph_fixture(tmp_path/'source'); out=tmp_path/'campaign'
    if case=='existing': out.mkdir()
    if case=='inside_raw': out=kwargs['raw_root']/'output'
    if case=='inside_repo': out=Path(__file__).resolve().parents[3]/'NEVER_CREATE'
    if case=='ancestor': out=tmp_path
    if case=='symlink':
        (tmp_path/'link').symlink_to(tmp_path/'source',target_is_directory=True); out=tmp_path/'link'/'output'
    if case=='raw_symlink':
        raw=kwargs['raw_root']/'clips/0/0.MOV'; raw.unlink(); raw.symlink_to(kwargs['model'])
    if case=='relative': kwargs['model']=Path('relative.task')
    if case=='dataless':
        import os
        real=os.stat
        def stat(path,*args,**kw):
            result=real(path,*args,**kw)
            if str(path).endswith('clips/0/0.MOV'):
                from types import SimpleNamespace
                return SimpleNamespace(st_flags=0x40000000, st_mode=result.st_mode)
            return result
        monkeypatch.setattr(os,'stat',stat)
    if case=='stale': kwargs['source_inventory'].write_text(kwargs['source_inventory'].read_text()+' ')
    with pytest.raises(ValueError,match=match): dataset().preflight(**kwargs,output=out)



def test_repeated_extract_helpers_keep_compact_closed_evidence(tmp_path):
    # This module is a helper caller: test_extract's autouse reset does not run.
    from .test_extract import extract, SyntheticVideo, SyntheticDetector
    import cv2
    graph = dataset().preflight(**graph_fixture(tmp_path/'source'))
    out = tmp_path/'bounded'
    (out/'raw').mkdir(parents=True)
    previous = (SyntheticVideo.opened, SyntheticVideo.instances, SyntheticDetector.instances)
    SyntheticVideo.opened, SyntheticVideo.instances, SyntheticDetector.instances = [], [], []
    def image_bytes(value):
        if isinstance(value, np.ndarray):
            return value.nbytes
        if isinstance(value, dict):
            return sum(image_bytes(v) for v in value.values())
        if isinstance(value, (tuple, list)):
            return sum(image_bytes(v) for v in value)
        return 0
    retained_bytes = []
    try:
        for number, row in enumerate(graph.rows[:2], 1):
            result = extract().extract_one(graph, row, out, number,
                                           SyntheticVideo, SyntheticDetector, cv2)
            assert result['status'] == 'eligible'
            assert len(dataset().read_raw(out/result['raw_file'], result['raw_sha256'])) == 8
            assert len(SyntheticDetector.instances) == number
            assert all(d.closed and len(d.calls) == 8 for d in SyntheticDetector.instances)
            assert all(v.released for v in SyntheticVideo.instances)
            for detector in SyntheticDetector.instances:
                assert [t for _, t in detector.calls] == [0, 67, 133, 200, 267, 333, 400, 467]
            retained_bytes.append(image_bytes([d.calls for d in SyntheticDetector.instances]))
        # Retain both clips' call evidence through assertions, not full RGB arrays.
        assert retained_bytes == [0, 0]
    finally:
        SyntheticVideo.opened, SyntheticVideo.instances, SyntheticDetector.instances = previous


def test_canonical_bundle_production_flow_exact_ids_and_tensors(tmp_path):
    from .test_extract import synthetic_campaign
    from training.holistic_migration.sequence import prepare_capture
    kwargs,campaign,code=synthetic_campaign(tmp_path)
    assert code==0
    out=tmp_path/'bundle'
    manifest=dataset().build_dataset(campaign=campaign,output=out)
    assert manifest['status']=='complete' and manifest['evidence_kind']=='synthetic_in_process'
    assert manifest['classes'][25]['original_id']==49
    assert json.loads((out/'data_manifest.json').read_text())==manifest
    rows=[json.loads(x) for x in (campaign/'rows.jsonl').read_text().splitlines()]
    for part in ['fit','validation','test']:
        expected=[r for r in rows if r['partition']==part]
        x=np.load(out/f'X_{part}.npy',allow_pickle=False)
        y=np.load(out/f'y_{part}.npy',allow_pickle=False)
        ids=np.load(out/f'clip_ids_{part}.npy',allow_pickle=False)
        assert x.shape==(50,30,153) and x.dtype==np.float32 and y.dtype==np.int64
        assert ids.tolist()==[r['clip_id'] for r in expected]
        assert y.tolist()==[r['dense_id'] for r in expected]
        for index,row in enumerate(expected):
            raw=dataset().read_raw(campaign/row['raw_file'],row['raw_sha256'])
            np.testing.assert_array_equal(x[index],prepare_capture(raw).tensor)
        assert manifest['eligibility']['partitions'][part]==dict(declared=50,eligible=50,ineligible=0,reasons={})
    assert len(manifest['eligibility']['classes'])==50



def rebind_campaign(campaign, rows):
    (campaign/'rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    m=json.loads((campaign/'extraction_manifest.json').read_text())
    m['rows_sha256']=digest(campaign/'rows.jsonl'); dump(campaign/'extraction_manifest.json',m)


@pytest.mark.parametrize('case', ['diagnostic','disguised_diagnostic','raw_byte','ledger_byte','row_missing',
    'row_duplicate','row_identity','raw_traversal','raw_symlink','count_float','raw_digest','capture','existing','current_contract'])
def test_bundle_rejects_incomplete_tampered_campaign_public_path(tmp_path,case,monkeypatch):
    from .test_extract import synthetic_campaign
    kwargs,campaign,code=synthetic_campaign(tmp_path,diagnostic_fit_only=case in ['diagnostic','disguised_diagnostic'])
    out=tmp_path/'bundle'
    m=json.loads((campaign/'extraction_manifest.json').read_text())
    rows=[json.loads(x) for x in (campaign/'rows.jsonl').read_text().splitlines()]
    if case=='disguised_diagnostic':
        m['status']='complete'; m['full_campaign_qualification']=True; dump(campaign/'extraction_manifest.json',m)
    if case=='raw_byte': (campaign/rows[0]['raw_file']).write_bytes(b'tamper')
    if case=='ledger_byte': (campaign/'rows.jsonl').write_text((campaign/'rows.jsonl').read_text()+' ')
    if case=='row_missing': rows.pop(); rebind_campaign(campaign,rows)
    if case=='row_duplicate': rows[-1]=rows[0].copy(); rebind_campaign(campaign,rows)
    if case=='row_identity': rows[0]['original_id']=999; rebind_campaign(campaign,rows)
    if case=='raw_traversal': rows[0]['raw_file']='../outside.npz'; rebind_campaign(campaign,rows)
    if case=='raw_symlink':
        path=campaign/rows[0]['raw_file']; real=tmp_path/'moved.npz'; path.rename(real); path.symlink_to(real)
    if case=='count_float': m['counts']['declared']=150.0; dump(campaign/'extraction_manifest.json',m)
    if case=='raw_digest': rows[0]['raw_sha256']='0'*64; rebind_campaign(campaign,rows)
    if case=='capture': rows[0]['capture']['hand_count']=1; rebind_campaign(campaign,rows)
    if case=='existing': out.mkdir()
    if case=='current_contract': monkeypatch.setattr(dataset(),'contract_binding',lambda: {'changed':'0'*64})
    with pytest.raises(ValueError): dataset().build_dataset(campaign=campaign,output=out)
    assert not (out/'data_manifest.json').exists()



def weak_campaign(root,weak_partition,all_classes=False):
    from .test_extract import extract,SyntheticVideo,SyntheticDetector
    from dataclasses import replace
    kwargs=graph_fixture(root/'source'); campaign=root/'campaign'
    class WeakDetector(SyntheticDetector):
        def detect(self,rgb,t):
            result=super().detect(rgb,t)
            path=SyntheticVideo.instances[-1].path
            target={'fit':'0','validation':'1','test':'2'}[weak_partition]
            if path.stem==target and (all_classes or path.parent.name=='0'):
                return replace(result,left_hand=None,right_hand=None)
            return result
    code=extract().run_extraction(**kwargs,output=campaign,video_factory=SyntheticVideo,detector_factory=WeakDetector)
    assert code==0
    return campaign


@pytest.mark.parametrize('partition',['fit','validation'])
def test_bundle_requires_all_class_support_retains_failed_denominators(tmp_path,partition):
    campaign=weak_campaign(tmp_path,partition); out=tmp_path/'bundle'
    with pytest.raises(ValueError,match='eligible support'): dataset().build_dataset(campaign=campaign,output=out)
    assert not (out/'data_manifest.json').exists()
    eligibility=json.loads((out/'eligibility.json').read_text())
    assert eligibility['partitions'][partition]==dict(declared=50,eligible=49,ineligible=1,reasons={'no_hands':1})
    assert eligibility['classes'][0]['partitions'][partition]['declared']==1


def test_bundle_reports_all_test_ineligibility_without_zero_examples(tmp_path):
    campaign=weak_campaign(tmp_path,'test',all_classes=True)
    out=tmp_path/'bundle'; m=dataset().build_dataset(campaign=campaign,output=out)
    assert m['eligibility']['partitions']['test']==dict(declared=50,eligible=0,ineligible=50,reasons={'no_hands':50})
    assert np.load(out/'X_test.npy',allow_pickle=False).shape==(0,30,153)
    assert np.load(out/'y_test.npy',allow_pickle=False).shape==(0,)
    assert len(json.loads((out/'capture_rows.json').read_text()))==150



@pytest.mark.parametrize('artifact',['X_fit.npy','X_validation.npy','eligibility.json','campaign_raw'])
def test_bundle_final_readback_rejects_midbuild_tamper(tmp_path,monkeypatch,artifact):
    from .test_extract import synthetic_campaign
    kwargs,campaign,code=synthetic_campaign(tmp_path); out=tmp_path/'bundle'
    real=dataset().write_json
    rows=[json.loads(x) for x in (campaign/'rows.jsonl').read_text().splitlines()]
    def write(path,value):
        result=real(path,value)
        if Path(path).name=='class_metadata.json':
            target=(campaign/rows[0]['raw_file']) if artifact=='campaign_raw' else out/artifact
            target.write_bytes(b'tampered after earlier readback')
        return result
    monkeypatch.setattr(dataset(),'write_json',write)
    with pytest.raises(ValueError): dataset().build_dataset(campaign=campaign,output=out)
    assert not (out/'data_manifest.json').exists()



def test_bundle_cli_help_success_failure_and_no_native_imports(tmp_path,monkeypatch):
    from .test_extract import synthetic_campaign
    import subprocess,sys,builtins
    builder=importlib.import_module('training.holistic_migration.build_dataset')
    kwargs,campaign,code=synthetic_campaign(tmp_path)
    real=builtins.__import__
    def guarded(name,*args,**kw):
        if name in ['cv2','mediapipe']: raise AssertionError('builder must not import native inference')
        return real(name,*args,**kw)
    monkeypatch.setattr(builtins,'__import__',guarded)
    assert builder.main(['--campaign',str(campaign),'--output',str(tmp_path/'bundle')])==0
    cmd=[sys.executable,'-E','-B','-m','training.holistic_migration.build_dataset']
    help_result=subprocess.run(cmd+['--help'],capture_output=True,text=True)
    assert help_result.returncode==0 and '--campaign' in help_result.stdout
    success=subprocess.run(cmd+['--campaign',str(campaign),'--output',str(tmp_path/'cli_bundle')],capture_output=True,text=True)
    assert success.returncode==0,success.stderr
    failure=subprocess.run(cmd+['--campaign',str(campaign),'--output',str(tmp_path/'cli_bundle')],capture_output=True,text=True)
    assert failure.returncode==2 and 'already exists' in failure.stderr
    relative=subprocess.run(cmd+['--campaign','relative','--output',str(tmp_path/'never')],capture_output=True,text=True)
    assert relative.returncode==2 and 'absolute' in relative.stderr



@pytest.mark.parametrize('case',['unrepresentable_face','timestamp_range','symlink_read'])
def test_codec_rejects_loss_or_unsafe_read(tmp_path,case):
    d=dataset(); observed=frames(); path=tmp_path/'raw.npz'
    if case=='unrepresentable_face': observed[0]=replace(observed[0],face=np.array([[2**53+1,0,0]],np.int64))
    if case=='timestamp_range': observed=[replace(observed[0],timestamp_ms=2**63)]
    if case=='symlink_read':
        checksum=d.write_raw(path,observed); link=tmp_path/'link.npz';link.symlink_to(path)
        with pytest.raises(ValueError,match='symlink'): d.read_raw(link,checksum)
    else:
        with pytest.raises(ValueError): d.write_raw(path,observed)
        assert not path.exists()


def test_rebound_capture_equal_float_count_is_not_integer(tmp_path):
    from .test_extract import synthetic_campaign
    kwargs,campaign,code=synthetic_campaign(tmp_path)
    rows=[json.loads(x) for x in (campaign/'rows.jsonl').read_text().splitlines()]
    rows[0]['capture']['hand_count']=8.0
    rebind_campaign(campaign,rows)
    with pytest.raises(ValueError): dataset().build_dataset(campaign=campaign,output=tmp_path/'bundle')



@pytest.mark.parametrize('name',['data_manifest.json','extraction_manifest.json'])
def test_failed_manifest_readback_never_leaves_completed_publication(tmp_path,monkeypatch,name):
    from .test_extract import synthetic_campaign
    d=dataset(); real=d.load_json
    def corrupt(path):
        value=real(path)
        if Path(path).name==name: return dict(value,status='CORRUPTED READBACK')
        return value
    if name=='extraction_manifest.json':
        monkeypatch.setattr(d,'load_json',corrupt)
        # Producer must preserve attempt but withhold the successful manifest.
        try: kwargs,campaign,code=synthetic_campaign(tmp_path)
        except ValueError: campaign=tmp_path/'campaign';code=2
        assert code!=0
        assert not (campaign/name).exists()
    else:
        kwargs,campaign,code=synthetic_campaign(tmp_path)
        monkeypatch.setattr(d,'load_json',corrupt)
        with pytest.raises(ValueError): d.build_dataset(campaign=campaign,output=tmp_path/'bundle')
        assert not (tmp_path/'bundle'/name).exists()



def test_contract_cannot_silently_drop_missing_source_inputs(tmp_path,monkeypatch):
    monkeypatch.setattr(dataset(),'REPO',tmp_path)
    with pytest.raises(ValueError,match='missing'): dataset().contract_binding()


def test_graph_receipt_hashes_runtime_and_contract_canonically(tmp_path):
    g=dataset().preflight(**graph_fixture(tmp_path/'source'))
    receipt=dataset().graph_receipt(g)
    for name in ['runtime','contract']:
        expected=hashlib.sha256(json.dumps(receipt[name],sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()).hexdigest()
        assert receipt[name+'_sha256']==expected



def test_public_preflight_requires_upstream_official_counts(tmp_path):
    root=tmp_path/'source';kwargs=graph_fixture(root)
    upstream=json.loads((root/'selected-source-inventory.json').read_text());upstream.pop('counts')
    rebind(root,upstream=upstream)
    with pytest.raises(ValueError,match='counts'): dataset().preflight(**kwargs)
