"""Source-bound numeric observation storage and canonical datasets (no native SDK)."""
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import stat
import sys
import numpy as np
from .features import RawFrame, pack_frame
from .sequence import prepare_capture


def sha256(path):
    h = hashlib.sha256()
    with safe_path(path,must_exist=True).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write_raw(path, frames):
    """Exclusive numeric NPZ: Float64 blocks, presence, and ragged face offsets."""
    path=safe_path(path)
    frames = list(frames)
    for frame in frames:
        pack_frame(frame)
        if frame.timestamp_ms>np.iinfo(np.int64).max:
            raise ValueError('raw timestamp exceeds lossless int64 storage range')
        for name in ['pose','left_hand','right_hand','face']:
            value=getattr(frame,name)
            if value is not None:
                with np.errstate(over='ignore',invalid='ignore'):
                    converted=value.astype(np.float64)
                if not np.isfinite(converted).all():
                    raise ValueError('raw values cannot be represented losslessly in Float64')
                if value.dtype.kind in 'iu':
                    # Never cast back to a bounded integer dtype: out-of-range
                    # floats can saturate to its maximum. Python int conversion
                    # and int/int equality compare the actual unbounded values.
                    lossless=all(int(source)==int(encoded)
                                 for source,encoded in zip(value.flat,converted.flat))
                else:
                    with np.errstate(over='ignore',invalid='ignore'):
                        restored=converted.astype(value.dtype)
                    lossless=np.array_equal(restored,value)
                if not lossless:
                    raise ValueError('raw values cannot be represented losslessly in Float64')
    if any(b.timestamp_ms <= a.timestamp_ms for a,b in zip(frames,frames[1:])):
        raise ValueError('raw timestamps must strictly increase')
    arrays: dict[str, np.ndarray] = {'timestamps': np.array([f.timestamp_ms for f in frames], dtype=np.int64)}
    for name, shape in [('pose',(33,4)), ('left_hand',(21,3)), ('right_hand',(21,3))]:
        arrays[name + '_present'] = np.array([getattr(f,name) is not None for f in frames], dtype=np.uint8)
        arrays[name] = np.stack([np.zeros(shape) if getattr(f,name) is None else getattr(f,name)
                                 for f in frames]).astype(np.float64) if frames else np.empty((0,*shape),np.float64)
    faces = [f.face for f in frames if f.face is not None]
    arrays['face_present'] = np.array([f.face is not None for f in frames],dtype=np.uint8)
    arrays['face_offsets'] = np.array([0] + list(np.cumsum([0 if f.face is None else len(f.face) for f in frames])), dtype=np.int64)
    arrays['face_values'] = np.concatenate(faces).astype(np.float64) if faces else np.empty((0,3),np.float64)
    with Path(path).open('xb') as stream:
        np.savez_compressed(stream, **arrays)
    return sha256(path)


def read_raw(path, expected_sha256):
    """Load numeric data only, reconstructing absent SDK components as None."""
    if sha256(path) != expected_sha256:
        raise ValueError('raw digest mismatch')
    with np.load(path, allow_pickle=False) as z:
        if len(z.files) != len(set(z.files)):
            raise ValueError('duplicate raw keys')
        values = {k:z[k] for k in z.files}
    validate_raw_arrays(values)
    result = []
    for i, t in enumerate(values['timestamps']):
        parts = [values[name][i].copy() if values[name+'_present'][i] else None
                 for name in ['pose','left_hand','right_hand']]
        lo,hi = values['face_offsets'][i:i+2]
        face = values['face_values'][lo:hi].copy() if values['face_present'][i] else None
        result.append(RawFrame(int(t), *parts, face))
    return result



def validate_raw_arrays(v):
    keys = {'timestamps','face_present','face_offsets','face_values'}
    keys.update(name+suffix for name in ['pose','left_hand','right_hand'] for suffix in ['', '_present'])
    if set(v) != keys:
        raise ValueError('unexpected raw keys')
    t = v['timestamps']
    if t.dtype != np.int64 or t.ndim != 1 or (t < 0).any() or (t[1:] <= t[:-1]).any():
        raise ValueError('invalid raw timestamps')
    n = len(t)
    for name in ['pose','left_hand','right_hand','face']:
        p = v[name+'_present']
        if p.dtype != np.uint8 or p.shape != (n,) or not np.isin(p,[0,1]).all():
            raise ValueError('invalid raw presence')
    for name,shape in [('pose',(33,4)),('left_hand',(21,3)),('right_hand',(21,3))]:
        a = v[name]
        if a.dtype != np.float64 or a.shape != (n,*shape) or not np.isfinite(a).all():
            raise ValueError('invalid raw landmark block')
        if (a[v[name+'_present'] == 0] != 0).any():
            raise ValueError('absent raw block contamination')
    offsets,face = v['face_offsets'],v['face_values']
    if (face.dtype != np.float64 or face.ndim != 2 or face.shape[1] != 3
            or not np.isfinite(face).all() or offsets.dtype != np.int64
            or offsets.shape != (n+1,) or offsets[0] != 0
            or offsets[-1] != len(face) or (offsets[1:] < offsets[:-1]).any()):
        raise ValueError('invalid face values/offsets')
    if ((offsets[1:] - offsets[:-1])[v['face_present']==0] != 0).any():
        raise ValueError('absent face contamination')



REPO = Path(__file__).resolve().parents[2]
PARTITIONS = ('fit', 'validation', 'test')
IDENTITY = ('clip_id','source_token','original_id','dense_id','label','csv_label','official_split','signer_id')
BYTE_IDENTITY = IDENTITY + ('archive_member','video_bytes','video_sha256')


def load_json(path):
    with Path(path).open(encoding='utf-8') as stream:
        return json.load(stream)


def runtime_binding():
    return dict(python=sys.version, executable=str(Path(sys.executable).absolute()),
                platform=platform.platform(), packages={name:importlib.metadata.version(name)
                for name in ['numpy','opencv-contrib-python','mediapipe']})


def contract_binding():
    files = ['docs/holistic-migration/FEATURES.md','docs/holistic-migration/CAPTURE_CANDIDATE.md',
             'docs/holistic-migration/task-c-brief.md']
    files += ['training/holistic_migration/'+name for name in
              ['__init__.py','features.py','detector.py','sequence.py','dataset.py','extract.py','build_dataset.py','requirements.txt']]
    return {name:sha256(REPO/name) for name in files}


@dataclass(frozen=True)
class SourceGraph:
    rows: list
    classes: list
    records: dict
    paths: dict
    bindings: dict
    contract: dict
    runtime: dict


def preflight(*, partition_manifest, source_inventory, decode_summary, raw_root, classes, model, output=None):
    """Validate metadata graph before importing video/Tasks; no source media is opened."""
    paths = {k:Path(v) for k,v in dict(partition_manifest=partition_manifest,source_inventory=source_inventory,
              decode_summary=decode_summary,raw_root=raw_root,classes=classes,model=model).items()}
    paths['decode_records'] = paths['decode_summary'].parent/'records.jsonl'
    paths['upstream_inventory'] = paths['source_inventory'].parent/'selected-source-inventory.json'
    for p in paths.values():
        safe_path(p, must_exist=True)
    if output is not None:
        fresh_output(output, paths)
    bindings = {k:sha256(p) for k,p in paths.items() if k!='raw_root'}
    membership, inventory, summary, upstream, class_map = [load_json(paths[k]) for k in
        ['partition_manifest','source_inventory','decode_summary','upstream_inventory','classes']]
    records = [json.loads(line) for line in paths['decode_records'].read_text().splitlines()]
    validate_graph(membership, inventory, summary, upstream, class_map, records, bindings)
    for row in membership['rows']:
        safe_path(paths['raw_root']/row['clip_id'], must_exist=True)
    selected = class_map['selected']
    ordered = [dict(dense_id=i,original_id=c['id'],label=c['label'],category=c['category']) for i,c in enumerate(selected)]
    return SourceGraph(sorted(membership['rows'], key=lambda r:r['clip_id']), ordered,
                       {r['clip_id']:r for r in records},paths,bindings,contract_binding(),runtime_binding())




def integer(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f'{name} must be a built-in integer >= {minimum}')
    return value


def hash_value(value, name):
    if type(value) is not str or re.fullmatch('[0-9a-f]{64}',value) is None:
        raise ValueError(f'invalid {name} hash')


def same(actual, expected, name):
    # Python equality alone treats bool/int/float as interchangeable schema values.
    if type(actual) is not type(expected):
        raise ValueError(f'{name} type mismatch')
    if isinstance(expected,dict):
        if actual.keys()!=expected.keys(): raise ValueError(f'{name} keys mismatch')
        for key in expected: same(actual[key],expected[key],name)
    elif isinstance(expected,(list,tuple)):
        if len(actual)!=len(expected): raise ValueError(f'{name} length mismatch')
        for a,b in zip(actual,expected): same(a,b,name)
    elif actual != expected:
        raise ValueError(f'{name} mismatch')


def index_rows(rows, name, byte_fields=False):
    if type(rows) is not list:
        raise ValueError(f'{name} rows must be a list')
    indexed = {}
    for row in rows:
        if type(row) is not dict or not all(k in row for k in IDENTITY):
            raise ValueError(f'{name} missing source identity')
        for field in ['dense_id','original_id']:
            integer(row[field],field)
        clip = row['clip_id']
        if (type(clip) is not str or not re.fullmatch(r'clips/[0-9]+/[A-Za-z0-9_.-]+',clip)
                or clip.split('/')[-1] in ['.','..'] or clip.split('/')[1] != str(row['original_id'])):
            raise ValueError('invalid canonical clip_id')
        if clip in indexed:
            raise ValueError(f'duplicate clip_id in {name}')
        same(row['source_token'],clip.replace('/',chr(92)),'source_token')
        if row['official_split'] not in ['train','test']:
            raise ValueError('invalid official split')
        if not all(type(row[k]) is str and row[k] for k in ['label','csv_label']):
            raise ValueError('invalid literal label')
        if row['signer_id'] is not None and type(row['signer_id']) not in [str,int]:
            raise ValueError('invalid signer identity')
        if byte_fields:
            integer(row.get('video_bytes'),'video_bytes',1)
            hash_value(row.get('video_sha256'),'video_sha256')
            same(row.get('archive_member'),clip,'archive_member')
        indexed[clip] = row
    return indexed


def validate_graph(m, inv, s, up, cm, records, b):
    integer(m.get('schema_version'),'schema_version')
    same(m['schema_version'],1,'schema_version')
    same(m.get('source_inventory_sha256'),b['source_inventory'],'membership inventory digest')
    same(inv.get('source_inventory_sha256'),b['upstream_inventory'],'upstream inventory digest')
    same(s.get('source_inventory_sha256'),b['source_inventory'],'decode inventory digest')
    same(s.get('records_sha256'),b['decode_records'],'decode records digest')
    same(m.get('class_map_sha256'),b['classes'],'class map digest')
    same(up.get('class_map_sha256'),b['classes'],'upstream class map digest')
    hash_value(inv.get('archive_sha256'),'archive')
    same(m.get('archive_sha256'),inv['archive_sha256'],'archive')
    selected = cm.get('selected')
    if type(selected) is not list or len(selected)!=50:
        raise ValueError('class map must contain exactly 50 classes')
    previous = -1
    for c in selected:
        integer(c.get('id'),'class id')
        if c['id'] <= previous or type(c.get('label')) is not str or not c['label'] or type(c.get('category')) is not str:
            raise ValueError('invalid ordered class metadata')
        previous = c['id']
    same(up.get('labels'),selected,'upstream classes')
    maps = [index_rows(m.get('rows'),'membership',True),index_rows(inv.get('rows'),'inventory',True),
            index_rows(up.get('rows'),'upstream'),index_rows(records,'decode',True)]
    source_ids = set(maps[0])
    if not source_ids:
        raise ValueError('empty source graph')
    for other in maps[1:]: same(set(other),source_ids,'source identity coverage')
    for clip,row in maps[0].items():
        dense = row['dense_id']
        if dense>=50 or row['original_id']!=selected[dense]['id'] or row['label']!=selected[dense]['label']:
            raise ValueError('class identity mismatch')
        for other,keys in [(maps[1],BYTE_IDENTITY),(maps[2],IDENTITY),(maps[3],BYTE_IDENTITY)]:
            same({k:other[clip][k] for k in keys},{k:row[k] for k in keys},'source identity')
        part = row.get('partition')
        if part not in PARTITIONS: raise ValueError('invalid partition')
        if (row['official_split']=='test') != (part=='test'):
            raise ValueError('official test/train partition contamination')
        rec = maps[3][clip]
        same(rec.get('status'),'ok','completed decode status')
        integer(rec.get('decoded_frames'),'decoded_frames',1)
        for k in ['declared_frames','fps']:
            value=rec.get(k)
            if type(value) not in [int,float] or not np.isfinite(value) or value<=0:
                raise ValueError(f'invalid descriptive {k}')
        if (type(rec.get('shapes')) is not list or not rec['shapes']
                or any(type(shape) is not list or len(shape)!=3
                       or any(type(v) is not int or v<=0 for v in shape) or shape[2]!=3 for shape in rec['shapes'])):
            raise ValueError('invalid decoded shapes')
        hash_value(rec.get('decoded_bgr_sha256'),'decoded pixels')
    n=len(source_ids)
    counts=Counter(r['partition'] for r in maps[0].values())
    if type(m.get('counts')) is not dict or set(m['counts'])!=set(PARTITIONS):
        raise ValueError('invalid partition counts')
    for p in PARTITIONS:
        integer(m['counts'][p],'partition count'); same(m['counts'][p],counts[p],'partition count')
    official=Counter(r['official_split'] for r in maps[0].values())
    if type(up.get('counts')) is not dict or set(up['counts'])!={'train','test'}:
        raise ValueError('invalid/missing upstream counts')
    for p in ['train','test']:
        integer(up['counts'][p],'upstream count'); same(up['counts'][p],official[p],'upstream count')
    for key,expected in [('source_count',n),('ok',n),('errors',0),('decoded_pixel_duplicate_groups',0),
                         ('cross_official_split_pixel_duplicate_groups',0),('cross_label_pixel_duplicate_groups',0)]:
        integer(s.get(key),key); same(s[key],expected,key)
    same(s.get('duplicate_groups'),[],'decoded duplicate groups')
    for key,expected in [('selected_sources',n),('unique_video_byte_hashes',n),('raw_duplicate_groups',0),
                         ('cross_official_split_duplicate_groups',0),('cross_label_duplicate_groups',0)]:
        integer(inv.get('summary',{}).get(key),key); same(inv['summary'][key],expected,key)
    integer(m.get('raw_duplicate_groups'),'raw_duplicate_groups'); same(m['raw_duplicate_groups'],0,'raw duplicates')
    for rows,key in [(maps[0].values(),'video_sha256'),(maps[3].values(),'decoded_bgr_sha256')]:
        hashes=[r[key] for r in rows]
        if len(hashes)!=len(set(hashes)): raise ValueError('duplicate source bytes/pixels')
    for p in PARTITIONS:
        if {r['dense_id'] for r in maps[0].values() if r['partition']==p} != set(range(50)):
            raise ValueError('declared partition class coverage incomplete')




def safe_path(path, *, must_exist=False):
    """Reject symlinks/traversal and macOS cloud placeholders without opening data."""
    path=Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('path must be absolute and traversal-free')
    for part in [*reversed(path.parents),path]:
        if part.is_symlink(): raise ValueError(f'symlink path forbidden: {part}')
    if must_exist:
        try: info=os.stat(path,follow_symlinks=False)
        except OSError as e: raise ValueError(f'missing/unavailable input: {path}') from e
        if getattr(info,'st_flags',0) & getattr(stat,'UF_DATALESS',0x40000000):
            raise ValueError(f'DATALESS input must not be opened: {path}')
        if not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
            raise ValueError(f'non-regular input: {path}')
    return path


def fresh_output(output, inputs):
    output=safe_path(output)
    if output==REPO or REPO in output.parents:
        raise ValueError('output must be outside repository')
    trees=[Path(inputs[k]) for k in ['raw_root'] if k in inputs]
    if 'decode_summary' in inputs: trees.append(Path(inputs['decode_summary']).parent)
    if 'campaign' in inputs: trees.append(Path(inputs['campaign']))
    protected=[Path(p) for p in inputs.values()]+trees+[REPO]
    if any(output==p or output in p.parents for p in protected) or any(p in output.parents for p in trees):
        raise ValueError('output overlaps protected input tree')
    if output.exists(): raise ValueError('output already exists; never reuse an attempt')
    if not output.parent.is_dir(): raise ValueError('output parent must already exist')
    return output




def write_json(path, value):
    with Path(path).open('x',encoding='utf-8') as stream:
        json.dump(value,stream,sort_keys=True,ensure_ascii=False,allow_nan=False,indent=2)
        stream.write('\n')
    same(load_json(path),value,'JSON readback')


def publish_json(path,value):
    """Read back staging bytes before exclusive publication; preserve failed attempts."""
    path=Path(path)
    pending=path.with_name(path.name+'.pending')
    write_json(pending,value)
    expected=sha256(pending)
    os.link(pending,path)  # exclusive: raises if the destination appeared concurrently
    try:
        same(sha256(path),expected,'published manifest digest')
        same(load_json(path),value,'published manifest readback')
    except BaseException:
        path.unlink()  # only our just-linked publication; pending bytes remain for audit
        raise


def capture_receipt(result):
    return {name:getattr(result,name) for name in
            ['reason','observation_count','hand_count','start_ms','end_ms',
             'source_observation_count','source_start_ms','source_end_ms']}


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def graph_receipt(graph):
    return dict(paths={k:str(p) for k,p in graph.paths.items()},bindings=graph.bindings,
                classes=graph.classes,contract=graph.contract,runtime=graph.runtime,
                contract_sha256=canonical_hash(graph.contract),runtime_sha256=canonical_hash(graph.runtime))


def recheck_graph(graph):
    for key,expected in graph.bindings.items():
        safe_path(graph.paths[key],must_exist=True)
        same(sha256(graph.paths[key]),expected,'input digest readback')
    same(contract_binding(),graph.contract,'current contract')
    same(runtime_binding(),graph.runtime,'current runtime')



def validate_campaign(campaign):
    """Reopen completed artifacts and exact graph; diagnostics can never qualify."""
    campaign=safe_path(campaign,must_exist=True)
    manifest_path=safe_path(campaign/'extraction_manifest.json',must_exist=True)
    manifest=load_json(manifest_path)
    integer(manifest.get('schema_version'),'campaign schema_version')
    same(manifest['schema_version'],1,'campaign schema_version')
    if manifest.get('status')!='complete' or manifest.get('full_campaign_qualification') is not True:
        raise ValueError('only a complete full campaign is a dataset; diagnostic refused')
    if manifest.get('evidence_kind') not in ['synthetic_in_process','source_video']:
        raise ValueError('invalid campaign evidence kind')
    paths=manifest['graph']['paths']
    graph=preflight(**{k:paths[k] for k in ['partition_manifest','source_inventory','decode_summary','raw_root','classes','model']})
    same(graph_receipt(graph),manifest['graph'],'campaign input/current contract/runtime')
    for name,key in [('rows.jsonl','rows_sha256'),('attempt.json','attempt_sha256'),('selected_ids.json','selected_ids_sha256')]:
        safe_path(campaign/name,must_exist=True)
        hash_value(manifest.get(key),key)
        same(sha256(campaign/name),manifest[key],'campaign '+key)
    attempt=load_json(campaign/'attempt.json')
    same(attempt,{k:manifest[k] for k in ['schema_version','evidence_kind','graph','selected_ids_sha256']},'campaign attempt')
    selected=load_json(campaign/'selected_ids.json')
    same(selected,[r['clip_id'] for r in graph.rows],'full declared selection (diagnostics refused)')
    counts=manifest.get('counts')
    if type(counts) is not dict or set(counts)!={'declared','selected','processed','errors'}:
        raise ValueError('invalid campaign counts')
    for key,expected in dict(declared=len(graph.rows),selected=len(graph.rows),processed=len(graph.rows),errors=0).items():
        integer(counts[key],'campaign '+key); same(counts[key],expected,'campaign '+key)
    rows=[json.loads(line) for line in (campaign/'rows.jsonl').read_text().splitlines()]
    indexed=index_rows(rows,'campaign',True)
    same([r['clip_id'] for r in rows],[r['clip_id'] for r in graph.rows],'campaign ordered identity coverage')
    files=set()
    for source in graph.rows:
        row=indexed[source['clip_id']]
        same({k:row.get(k) for k in BYTE_IDENTITY+('partition',)},source,'campaign source identity')
        if row.get('status') not in ['eligible','ineligible']:
            raise ValueError('incomplete campaign row status')
        raw=row.get('raw_file')
        if type(raw) is not str or re.fullmatch(r'raw/[0-9]{6}\.npz',raw) is None or raw in files:
            raise ValueError('invalid/duplicate campaign raw path')
        files.add(raw)
        safe_path(campaign/raw,must_exist=True)
        hash_value(row.get('raw_sha256'),'raw digest')
        integer(row.get('decoded_frames'),'campaign decoded_frames',1)
        same(row['decoded_frames'],graph.records[row['clip_id']]['decoded_frames'],'campaign decoded count')
        same(row.get('decoded_bgr_sha256'),graph.records[row['clip_id']]['decoded_bgr_sha256'],'campaign decoded pixels')
        result=prepare_capture(read_raw(campaign/raw,row['raw_sha256']))
        same(capture_receipt(result),row.get('capture'),'campaign capture readback')
        same(row['status'],'eligible' if result.tensor is not None else 'ineligible','campaign eligibility')
    return graph,manifest,rows


def eligibility_summary(graph, captures):
    def counts(rows):
        eligible=sum(r['reason']=='eligible' for r in rows)
        return dict(declared=len(rows),eligible=eligible,ineligible=len(rows)-eligible,
                    reasons=dict(sorted(Counter(r['reason'] for r in rows if r['reason']!='eligible').items())))
    return dict(partitions={p:counts([r for r in captures if r['partition']==p]) for p in PARTITIONS},
                classes=[dict(c,partitions={p:counts([r for r in captures if r['partition']==p and r['dense_id']==c['dense_id']])
                                           for p in PARTITIONS}) for c in graph.classes])


def build_dataset(*,campaign,output):
    """Canonical, unaugmented arrays; source ineligibility is never an example."""
    campaign=Path(campaign)
    graph,source,rows=validate_campaign(campaign)
    output=fresh_output(output,dict(graph.paths,campaign=campaign))
    output.mkdir()
    write_json(output/'attempt.json',dict(campaign=str(campaign),campaign_manifest_sha256=sha256(campaign/'extraction_manifest.json'),
                                        graph=graph_receipt(graph)))
    tensors={p:[] for p in PARTITIONS}
    labels={p:[] for p in PARTITIONS}
    ids={p:[] for p in PARTITIONS}
    captures=[]
    for row in rows:
        raw=read_raw(campaign/row['raw_file'],row['raw_sha256'])
        result=prepare_capture(raw)
        same(capture_receipt(result),row['capture'],'capture readback')
        capture=dict(clip_id=row['clip_id'],dense_id=row['dense_id'],partition=row['partition'],**capture_receipt(result))
        captures.append(capture)
        if result.tensor is not None:
            p=row['partition']
            tensors[p].append(result.tensor); labels[p].append(row['dense_id']); ids[p].append(row['clip_id'])
    eligibility=eligibility_summary(graph,captures)
    write_json(output/'eligibility.json',eligibility)
    write_json(output/'capture_rows.json',captures)
    unsupported=[[c['dense_id'],p] for c in eligibility['classes'] for p in ['fit','validation']
                 if c['partitions'][p]['eligible']==0]
    if unsupported:
        write_json(output/'failure.json',dict(status='ineligible_support',unsupported=unsupported))
        raise ValueError(f'missing eligible support in fit/validation classes: {unsupported}')
    artifacts={}
    for p in PARTITIONS:
        arrays={f'X_{p}.npy':np.stack(tensors[p]) if tensors[p] else np.empty((0,30,153),np.float32),
                f'y_{p}.npy':np.array(labels[p],dtype=np.int64),f'clip_ids_{p}.npy':np.array(ids[p],dtype=np.str_)}
        for name,array in arrays.items():
            with (output/name).open('xb') as stream: np.save(stream,array,allow_pickle=False)
            loaded=np.load(output/name,allow_pickle=False)
            if loaded.dtype!=array.dtype or loaded.shape!=array.shape or not np.array_equal(loaded,array):
                raise ValueError('tensor artifact readback mismatch')
            artifacts[name]=dict(sha256=sha256(output/name),shape=list(array.shape),dtype=str(array.dtype))
    write_json(output/'class_metadata.json',graph.classes)
    expected_json={'eligibility.json':eligibility,'capture_rows.json':captures,'class_metadata.json':graph.classes,
                   'attempt.json':dict(campaign=str(campaign),campaign_manifest_sha256=sha256(campaign/'extraction_manifest.json'),
                                       graph=graph_receipt(graph))}
    for name,expected in expected_json.items():
        same(load_json(output/name),expected,'final JSON readback')
        artifacts[name]=dict(sha256=sha256(output/name))
    for name,record in artifacts.items():
        safe_path(output/name,must_exist=True)
        same(sha256(output/name),record['sha256'],'final artifact digest')
    final_graph,final_source,final_rows=validate_campaign(campaign)
    same(final_source,source,'campaign final readback')
    same(final_rows,rows,'campaign rows final readback')
    recheck_graph(graph)
    manifest=dict(schema_version=1,status='complete',evidence_kind=source['evidence_kind'],
                  training_qualified=False,classes=graph.classes,eligibility=eligibility,artifacts=artifacts,
                  campaign=str(campaign),campaign_manifest_sha256=sha256(campaign/'extraction_manifest.json'),
                  graph=graph_receipt(graph),augmentation='none',tensor_contract='Float32[N,30,153] hm153-v1')
    publish_json(output/'data_manifest.json',manifest)
    return manifest
