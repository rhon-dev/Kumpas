"""Synthetic video/Tasks injections; real OpenCV image transforms, no SDK calls."""
from pathlib import Path
import hashlib
import importlib
import json
import numpy as np
import pytest
from .test_dataset import graph_fixture, dataset, digest, dump
from .test_sequence import frames


def extract():
    return importlib.import_module('training.holistic_migration.extract')


class SyntheticVideo:
    opened=[]
    instances=[]
    def __init__(self,path):
        self.path=Path(path); self.index=-1; self.released=False
        self.opened.append(str(self.path)); self.instances.append(self)
    def isOpened(self): return True
    def read(self):
        self.index+=1
        if self.index==16: return False,None
        image=np.full((8,12,3),[7,19,41],np.uint8)
        original=int(self.path.parent.name); dense=original if original<25 else original-24
        image[0,0]=[dense,int(self.path.stem),self.index]
        return True,image
    def get(self,key): return self.index*1000/30
    def release(self): self.released=True


class SyntheticDetector:
    instances=[]
    def __init__(self,path):
        self.calls=[]; self.closed=False; self.instances.append(self)
    def detect(self,rgb,t):
        from dataclasses import replace
        assert rgb.shape==(360,640,3) and rgb.dtype==np.uint8 and rgb.flags.c_contiguous
        # Full-pixel digest plus geometry/cadence evidence, not a retained RGB
        # copy per call. Dataset helper callers need no local autouse fixture.
        evidence = dict(shape=rgb.shape, dtype=rgb.dtype.str,
                        contiguous=bool(rgb.flags.c_contiguous),
                        sha256=hashlib.sha256(rgb.tobytes()).hexdigest())
        self.calls.append((evidence,t))
        return replace(frames()[len(self.calls)-1],timestamp_ms=t)
    def close(self): self.closed=True


@pytest.fixture(autouse=True)
def clear_synthetic():
    SyntheticVideo.opened=[]; SyntheticVideo.instances=[]; SyntheticDetector.instances=[]
    yield
    SyntheticVideo.opened=[]; SyntheticVideo.instances=[]; SyntheticDetector.instances=[]


def synthetic_campaign(root, **extra):
    kwargs=graph_fixture(root/'source')
    out=root/'campaign'
    code=extract().run_extraction(**kwargs,output=out,video_factory=SyntheticVideo,
                                 detector_factory=SyntheticDetector,**extra)
    return kwargs,out,code


def test_extraction_complete_production_path_synthetic(tmp_path,capsys):
    kwargs,out,code=synthetic_campaign(tmp_path)
    assert code==0
    manifest=json.loads((out/'extraction_manifest.json').read_text())
    assert manifest['status']=='complete' and manifest['evidence_kind']=='synthetic_in_process'
    assert manifest['counts']==dict(declared=150,selected=150,processed=150,errors=0)
    rows=[json.loads(x) for x in (out/'rows.jsonl').read_text().splitlines()]
    assert len(rows)==150 and all(r['status']=='eligible' for r in rows)
    assert len(SyntheticDetector.instances)==150
    assert all(d.closed and len(d.calls)==8 for d in SyntheticDetector.instances)
    assert all(v.released for v in SyntheticVideo.instances)
    assert [t for _,t in SyntheticDetector.instances[0].calls]==[0,67,133,200,267,333,400,467]
    import cv2
    for detector, row in zip(SyntheticDetector.instances, rows):
        assert [t for _, t in detector.calls] == [0,67,133,200,267,333,400,467]
        for (evidence, _), source_index in zip(detector.calls, range(0,16,2)):
            # Independent source pixels/channel reversal and direct resize;
            # full-image hash catches geometry, mirror and channel changes.
            bgr = np.full((8,12,3), [7,19,41], dtype=np.uint8)
            bgr[0,0] = [row['dense_id'], int(Path(row['clip_id']).stem), source_index]
            expected = cv2.resize(bgr[:,:,::-1], (640,360), interpolation=cv2.INTER_AREA)
            assert evidence == dict(shape=(360,640,3), dtype=np.dtype(np.uint8).str,
                                    contiguous=True, sha256=hashlib.sha256(expected.tobytes()).hexdigest())
    for row in rows:
        assert len(dataset().read_raw(out/row['raw_file'],row['raw_sha256']))==8
    assert '150/150' in capsys.readouterr().err



def test_diagnostic_selects_literal_first_fit_only_before_inference(tmp_path):
    root=tmp_path/'source'; kwargs=graph_fixture(root); out=tmp_path/'campaign'
    manifest=json.loads(kwargs['partition_manifest'].read_text())
    expected=sorted(min(r['clip_id'] for r in manifest['rows'] if r['dense_id']==d and r['partition']=='fit') for d in range(50))
    class FitOnlyVideo(SyntheticVideo):
        def __init__(self,path):
            ids=json.loads((out/'selected_ids.json').read_text())
            assert ids==expected and Path(path).stem=='0'
            super().__init__(path)
    code=extract().run_extraction(**kwargs,output=out,diagnostic_fit_only=True,
                                 video_factory=FitOnlyVideo,detector_factory=SyntheticDetector)
    assert code==0
    result=json.loads((out/'extraction_manifest.json').read_text())
    assert result['status']=='diagnostic_fit_only' and result['full_campaign_qualification'] is False
    assert result['counts']==dict(declared=150,selected=50,processed=50,errors=0)
    assert len(SyntheticVideo.opened)==50 and all(Path(p).stem=='0' for p in SyntheticVideo.opened)
    rows=[json.loads(x) for x in (out/'rows.jsonl').read_text().splitlines()]
    assert len(rows)==150 and sum(r['status']=='not_selected' for r in rows)==100



@pytest.mark.parametrize('case,reason', [('nan','timestamp_error'),('negative','timestamp_error'),('duplicate','timestamp_error'),
    ('pixel','decode_error'),('short','decode_error'),('detection','detection_error'),('source','source_error')])
def test_extraction_failure_ledger_all_declared_cleanup_no_completion(tmp_path,case,reason):
    kwargs=graph_fixture(tmp_path/'source'); out=tmp_path/'campaign'
    if case=='source': (kwargs['raw_root']/'clips/0/0.MOV').write_bytes(b'tampered')
    class BrokenVideo(SyntheticVideo):
        def read(self):
            ok,image=super().read()
            if case=='short' and self.index==15: return False,None
            if case=='pixel' and ok: image[1,1,0]=255
            return ok,image
        def get(self,key):
            if case=='nan': return float('nan')
            if case=='negative': return -.01
            if case=='duplicate' and self.index==1: return 0.0
            return super().get(key)
    class BrokenDetector(SyntheticDetector):
        def detect(self,rgb,t):
            if case=='detection': raise RuntimeError('synthetic detector failure')
            return super().detect(rgb,t)
    code=extract().run_extraction(**kwargs,output=out,video_factory=BrokenVideo,detector_factory=BrokenDetector)
    assert code!=0 and not (out/'extraction_manifest.json').exists()
    rows=[json.loads(x) for x in (out/'rows.jsonl').read_text().splitlines()]
    assert len(rows)==150 and any(r['status']=='error' and r['reason']==reason for r in rows)
    assert all(d.closed for d in SyntheticDetector.instances) and all(v.released for v in SyntheticVideo.instances)
    assert json.loads((out/'failure.json').read_text())['status']=='incomplete'


def test_extraction_public_preflight_before_runtime_factories(tmp_path):
    kwargs=graph_fixture(tmp_path/'source'); out=tmp_path/'campaign'; out.mkdir()
    def forbidden(*args): raise AssertionError('runtime must not start')
    with pytest.raises(ValueError,match='exists'):
        extract().run_extraction(**kwargs,output=out,video_factory=forbidden,detector_factory=forbidden)


@pytest.mark.parametrize('value', [True, float('nan'),float('inf'),-.001,'12'])
def test_video_timestamp_rejects_invalid_without_rounding_it_away(value):
    with pytest.raises(ValueError): extract().cv_timestamp(value)



def cli_args(kwargs,out):
    args=[]
    for key,path in dict(kwargs,output=out).items(): args.extend(['--'+key.replace('_','-'),str(path)])
    return args


def test_extraction_cli_help_and_invalid_preflight_in_real_process(tmp_path):
    import subprocess,sys
    cmd=[sys.executable,'-E','-B','-m','training.holistic_migration.extract']
    help_result=subprocess.run(cmd+['--help'],capture_output=True,text=True)
    assert help_result.returncode==0 and '--diagnostic-fit-only' in help_result.stdout
    kwargs=graph_fixture(tmp_path/'source'); out=tmp_path/'campaign'; out.mkdir()
    failure=subprocess.run(cmd+cli_args(kwargs,out),capture_output=True,text=True)
    assert failure.returncode!=0 and 'already exists' in failure.stderr
    assert not (out/'attempt.json').exists()


def test_extraction_main_preflight_failure_never_imports_native(tmp_path,monkeypatch,capsys):
    import builtins
    kwargs=graph_fixture(tmp_path/'source'); out=tmp_path/'campaign'
    data=json.loads(kwargs['partition_manifest'].read_text()); data['schema_version']=True
    dump(kwargs['partition_manifest'],data)
    real=builtins.__import__
    def guarded(name,*args,**kw):
        if name in ['cv2','mediapipe']: raise AssertionError('native import before preflight')
        return real(name,*args,**kw)
    monkeypatch.setattr(builtins,'__import__',guarded)
    assert extract().main(cli_args(kwargs,out))==2
    assert 'schema_version' in capsys.readouterr().err and not out.exists()



def test_real_entry_rejects_nonfrozen_synthetic_inputs_before_native_or_output(tmp_path,monkeypatch):
    import builtins
    kwargs=graph_fixture(tmp_path/'source');out=tmp_path/'never'
    real=builtins.__import__
    def guarded(name,*args,**kw):
        if name in ['cv2','mediapipe']: raise AssertionError('must reject nonfrozen inputs before native runtime')
        return real(name,*args,**kw)
    monkeypatch.setattr(builtins,'__import__',guarded)
    with pytest.raises(ValueError,match='frozen'): extract().run_extraction(**kwargs,output=out)
    assert not out.exists()
