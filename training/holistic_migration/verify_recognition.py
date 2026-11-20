"""Small output-only audit archive and independent top-three comparator."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from .face_features import prepare_capture

ROOT = Path(__file__).resolve().parents[2]


def prepare_tensor(frames):
    """Exact live-controller seam: shared preprocessing, no new normalization."""
    result = prepare_capture(frames)
    if result.tensor is None:
        raise ValueError('ineligible capture: '+result.reason)
    return result.tensor


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value,sort_keys=True,allow_nan=False)+'\n').encode()


def write_new(path, value):
    data=encoded(value)
    with path.open('xb') as stream:
        stream.write(data); stream.flush(); os.fsync(stream.fileno())
    if path.read_bytes() != data:
        raise ValueError('audit readback mismatch')


def validate_record(record, labels):
    """Independent oracle: deliberately does not import the presentation ranker."""
    if (set(record) != {'schema','attempt','raw_output','top3'}
            or type(record['schema']) is not int or record['schema'] != 1
            or type(record['attempt']) is not int or record['attempt'] < 1):
        raise ValueError('invalid attempt schema')
    raw=record['raw_output']
    if (type(raw) is not list or len(raw) != 50
            or any(type(x) not in (int,float) or not math.isfinite(x) or not 0 <= x <= 1 for x in raw)
            or not math.isclose(sum(raw),1.,rel_tol=1e-5,abs_tol=1e-5)):
        raise ValueError('invalid raw output shape/probabilities')
    indices=sorted(range(50),key=lambda index:(-raw[index],index))[:3]
    rows=record['top3']
    if type(rows) is not list or len(rows) != 3:
        raise ValueError('exactly three rows required')
    for rank,(row,index) in enumerate(zip(rows,indices),1):
        expected=dict(rank=rank,index=index,label=labels[index],score=raw[index],
                      display_text=f"{rank}. {labels[index]}: {raw[index]:.2f}".replace('’', "'"))
        if (not isinstance(row,dict) or row != expected or type(row['rank']) is not int
                or type(row['index']) is not int or type(row['score']) not in (int,float)):
            raise ValueError('top3 order/index/label/raw-score/display mismatch')


class AuditRun:
    def __init__(self, directory, labels, identities):
        self.path=Path(directory)
        if not self.path.is_absolute() or ROOT == self.path.resolve() or ROOT in self.path.resolve().parents:
            raise ValueError('audit directory must be external absolute path')
        if len(labels) != 50 or len(set(labels)) != 50 or any(type(x) is not str for x in labels):
            raise ValueError('expected 50 unique canonical labels')
        if any(type(x) is not str or len(x) != 64 or any(c not in '0123456789abcdef' for c in x) for x in identities.values()):
            raise ValueError('invalid asset identities')
        self.path.mkdir(parents=True,exist_ok=False)
        self.labels=list(labels); self.count=0; self.receipts={}
        sources={str(p.relative_to(ROOT)):digest_bytes(p.read_bytes()) for p in
                 [Path(__file__),Path(__file__).with_name('recognition.py'),
                  Path(__file__).with_name('recognition_webcam.py'),
                  Path(__file__).with_name('face_features.py'),Path(__file__).with_name('sequence.py'),
                  Path(__file__).with_name('features.py')]}
        write_new(self.path/'labels.json',self.labels)
        write_new(self.path/'run.json',dict(schema=1,identities=identities,sources=sources,
                  labels_sha256=digest_bytes((self.path/'labels.json').read_bytes())))

    def save(self, probabilities, rows):
        # The barrier survives any write/readback failure, denying this run.
        pending=self.path/'INCOMPLETE'
        write_new(pending,dict(attempt=self.count+1))
        record=dict(schema=1,attempt=self.count+1,raw_output=[float(x) for x in probabilities],top3=rows)
        validate_record(record,self.labels)
        target=self.path/f'attempt-{self.count+1:06d}.json'
        write_new(target,record)
        validate_record(json.loads(target.read_text()),self.labels)
        self.receipts[target.name]=digest_bytes(target.read_bytes())
        staged=self.path/'completion.pending.json'
        write_new(staged,self.receipts)
        os.replace(staged,self.path/'completion.json')
        if json.loads((self.path/'completion.json').read_text()) != self.receipts:
            raise ValueError('completion readback mismatch')
        pending.unlink()
        self.count += 1
        return target


def check_run(directory):
    path=Path(directory)
    if (path/'INCOMPLETE').exists():
        raise ValueError('incomplete publication')
    manifest=json.loads((path/'run.json').read_text())
    if (set(manifest) != {'schema','identities','sources','labels_sha256'}
            or type(manifest['schema']) is not int or manifest['schema'] != 1):
        raise ValueError('invalid run schema')
    labels_data=(path/'labels.json').read_bytes()
    if digest_bytes(labels_data) != manifest['labels_sha256']:
        raise ValueError('label order digest mismatch')
    labels=json.loads(labels_data)
    if type(labels) is not list or len(labels) != 50 or any(type(x) is not str for x in labels) or len(set(labels)) != 50:
        raise ValueError('invalid labels')
    if not isinstance(manifest['identities'],dict) or not {'classifier','features','labels'} <= manifest['identities'].keys():
        raise ValueError('missing asset binding')
    for value in manifest['identities'].values():
        if type(value) is not str or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
            raise ValueError('invalid asset binding')
    expected_sources={'training/holistic_migration/'+name for name in
                      ['verify_recognition.py','recognition.py','recognition_webcam.py','face_features.py','sequence.py','features.py']}
    if not isinstance(manifest['sources'],dict) or set(manifest['sources']) != expected_sources:
        raise ValueError('missing source binding')
    for source,expected in manifest['sources'].items():
        if digest_bytes((ROOT/source).read_bytes()) != expected:
            raise ValueError('source identity mismatch')
    attempts=sorted(path.glob('attempt-*.json'))
    if not attempts: raise ValueError('no completed attempts')
    receipts=json.loads((path/'completion.json').read_text())
    if type(receipts) is not dict or set(receipts) != {p.name for p in attempts}:
        raise ValueError('missing/incomplete attempt inventory')
    for target in attempts:
        if digest_bytes(target.read_bytes()) != receipts[target.name]:
            raise ValueError('attempt digest mismatch')
    for number,target in enumerate(attempts,1):
        if target.name != f'attempt-{number:06d}.json': raise ValueError('missing attempt')
        record=json.loads(target.read_text()); validate_record(record,labels)
        if record['attempt'] != number: raise ValueError('attempt identity mismatch')
    return len(attempts)


def main(argv=None):
    parser=argparse.ArgumentParser(description='Verify retained raw50/order/display top3 (no camera/model)')
    parser.add_argument('--check',type=Path,required=True,metavar='RUN_DIR')
    args=parser.parse_args(argv)
    try:
        count=check_run(args.check)
    except (ValueError,OSError,TypeError,KeyError) as error:
        print('FAIL: '+str(error)); return 1
    print(f'PASS: {count} completed attempts; raw50/order/display agree'); return 0


if __name__ == '__main__': sys.exit(main())
