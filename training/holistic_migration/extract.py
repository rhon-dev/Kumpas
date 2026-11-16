"""Exclusive source-video extraction. Native dependencies load only after preflight."""
from pathlib import Path
import hashlib
import json
import sys
import traceback
from numbers import Real
import numpy as np
from .dataset import (preflight, safe_path, same, sha256, write_raw, read_raw,
                      write_json, publish_json, load_json, capture_receipt, graph_receipt, recheck_graph)
from .sequence import ObservationClock, prepare_image, prepare_capture


FROZEN_BINDINGS = {
    'partition_manifest':'a80620494894701c9f4f2dfde5a3050f4f80b5532b04004c0761c7945300275f',
    'source_inventory':'0ff0c09c7df877c860258049427243aacc03d5f35ef11526715366f28940d41e',
    'upstream_inventory':'23697b80445fe1daedd9dfb1d1127e02e1a474eb13144ff5fcad9e4d589701ca',
    'decode_records':'a1926b7f0d3ecc7788db4126fd435a287c867519e642ff9770aeddcc74f63e3b',
    'classes':'e8089f5c0186bfe6fd9ec63a5150f8094645c1686509f23c1716453b5f9ce0d5',
    'model':'e2dab61191e2dcd0a15f943d8e3ed1dce13c82dfa597b9dd39f562975a50c3f8',
}


class ClipFailure(ValueError):
    def __init__(self,reason,detail):
        super().__init__(detail)
        self.reason=reason


def extract_one(graph,row,output,number,video_factory,detector_factory,cv):
    """Hash, stream full decoded audit, observe admitted frames, persist raw values."""
    stage='source_error'
    video=detector=None
    try:
        path=safe_path(graph.paths['raw_root']/row['clip_id'],must_exist=True)
        same(path.stat().st_size,row['video_bytes'],'source length')
        same(sha256(path),row['video_sha256'],'source byte digest')
        stage='decode_error'
        video=video_factory(str(path))
        if not video.isOpened(): raise ValueError('cannot open video')
        stage='detection_error'
        detector=detector_factory(graph.paths['model'])
        clock=ObservationClock()
        observed=[]
        pixels=hashlib.sha256()
        count=0
        shapes=set()
        while True:
            stage='decode_error'
            ok,bgr=video.read()
            if not ok: break
            if (type(bgr) is not np.ndarray or bgr.dtype!=np.uint8 or bgr.ndim!=3
                    or bgr.shape[2]!=3 or not bgr.shape[0] or not bgr.shape[1]):
                raise ValueError('invalid decoded BGR image')
            count+=1
            shapes.add(tuple(bgr.shape))
            pixels.update(np.asarray(bgr.shape,dtype='<i4').tobytes())
            pixels.update(np.ascontiguousarray(bgr).tobytes())
            stage='timestamp_error'
            timestamp=cv_timestamp(video.get(cv.CAP_PROP_POS_MSEC))
            admitted=clock.admit(timestamp)
            if admitted:
                stage='detection_error'
                rgb=prepare_image(cv.cvtColor(bgr,cv.COLOR_BGR2RGB),cv)
                observation=detector.detect(rgb,timestamp)
                same(observation.timestamp_ms,timestamp,'detector observation timestamp')
                observed.append(observation)
        stage='decode_error'
        audit=graph.records[row['clip_id']]
        same(count,audit['decoded_frames'],'decoded count')
        same(pixels.hexdigest(),audit['decoded_bgr_sha256'],'decoded pixel digest')
        same(sorted(shapes),sorted(tuple(s) for s in audit['shapes']),'decoded shapes')
        stage='capture_error'
        capture=prepare_capture(observed)
        stage='storage_error'
        filename=f'raw/{number:06d}.npz'
        digest=write_raw(output/filename,observed)
        read_raw(output/filename,digest)
        return dict(row,status='eligible' if capture.tensor is not None else 'ineligible',
                    capture=capture_receipt(capture),raw_file=filename,raw_sha256=digest,
                    decoded_frames=count,decoded_bgr_sha256=pixels.hexdigest())
    except Exception as error:
        raise ClipFailure(stage,str(error)) from error
    finally:
        try:
            if detector is not None: detector.close()
        finally:
            if video is not None: video.release()


def run_extraction(*, output, diagnostic_fit_only=False, video_factory=None, detector_factory=None, cv=None, **inputs):
    """Trusted Python injection only for synthetic tests; never a CLI module loader."""
    graph=preflight(**inputs,output=output)
    synthetic=video_factory is not None or detector_factory is not None or cv is not None
    if not synthetic:
        for key,expected in FROZEN_BINDINGS.items():
            same(graph.bindings[key],expected,'frozen '+key+' binding')
    output=Path(output)
    output.mkdir()
    (output/'raw').mkdir()
    selected=(sorted(min(r['clip_id'] for r in graph.rows if r['dense_id']==d and r['partition']=='fit')
                     for d in range(50)) if diagnostic_fit_only else [r['clip_id'] for r in graph.rows])
    selected_set=set(selected)
    write_json(output/'selected_ids.json',selected)
    attempt=dict(schema_version=1,evidence_kind='synthetic_in_process' if synthetic else 'source_video',
                 graph=graph_receipt(graph),selected_ids_sha256=sha256(output/'selected_ids.json'))
    write_json(output/'attempt.json',attempt)
    if cv is None:
        import cv2 as cv
    if video_factory is None: video_factory=cv.VideoCapture
    if detector_factory is None:
        from .detector import HolisticDetector
        detector_factory=HolisticDetector
    rows=[]
    errors=processed=0
    with (output/'rows.jsonl').open('x',encoding='utf-8') as ledger:
        for number,row in enumerate(graph.rows,1):
            if row['clip_id'] not in selected_set:
                record=dict(row,status='not_selected',reason='diagnostic_not_selected')
            else:
                try:
                    record=extract_one(graph,row,output,number,video_factory,detector_factory,cv)
                    processed+=1
                except Exception as error:
                    errors+=1
                    record=dict(row,status='error',reason=getattr(error,'reason','cleanup_error'),
                                detail=str(error),error_type=type(error).__name__)
                    traceback.print_exc(file=sys.stderr)
            ledger.write(json.dumps(record,sort_keys=True,allow_nan=False)+'\n'); ledger.flush()
            rows.append(record)
            print(f'{number}/{len(graph.rows)} {row["clip_id"]} {record["status"]}',file=sys.stderr,flush=True)
    counts=dict(declared=len(graph.rows),selected=len(selected),processed=processed,errors=errors)
    if errors:
        write_json(output/'failure.json',dict(status='incomplete',counts=counts))
        return 2
    try:
        same([json.loads(line) for line in (output/'rows.jsonl').read_text().splitlines()],rows,'ledger readback')
        recheck_graph(graph)
        same(load_json(output/'attempt.json'),attempt,'attempt readback')
        same(load_json(output/'selected_ids.json'),selected,'selection readback')
        for row in rows:
            if 'raw_file' in row: read_raw(output/row['raw_file'],row['raw_sha256'])
    except Exception as error:
        traceback.print_exc(file=sys.stderr)
        write_json(output/'failure.json',dict(status='incomplete',reason='readback_error',detail=str(error),counts=counts))
        return 2
    manifest=dict(attempt,status='diagnostic_fit_only' if diagnostic_fit_only else 'complete',
                  full_campaign_qualification=not diagnostic_fit_only,counts=counts,
                  rows_sha256=sha256(output/'rows.jsonl'),attempt_sha256=sha256(output/'attempt.json'))
    try:
        publish_json(output/'extraction_manifest.json',manifest)
    except Exception as error:
        traceback.print_exc(file=sys.stderr)
        write_json(output/'failure.json',dict(status='incomplete',reason='publication_error',detail=str(error),counts=counts))
        return 2
    return 0


def cv_timestamp(value):
    """Round finite nonnegative actual presentation milliseconds, never an FPS clock."""
    if not isinstance(value,Real) or isinstance(value,(bool,np.bool_)) or not np.isfinite(value) or value<0:
        raise ValueError('presentation timestamp must be real, finite and nonnegative')
    return int(round(value))



def main(argv=None):
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['partition-manifest','source-inventory','decode-summary','raw-root','classes','model','output']:
        parser.add_argument('--'+name,required=True,type=Path)
    parser.add_argument('--diagnostic-fit-only',action='store_true',
                        help='Only literal first frozen fit clip per class; never a full dataset')
    args=vars(parser.parse_args(argv))
    try:
        return run_extraction(**args)
    except (ValueError,OSError,KeyError,TypeError) as error:
        print(f'extraction rejected: {error}',file=sys.stderr)
        return 2


if __name__=='__main__':
    raise SystemExit(main())
