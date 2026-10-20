#!/usr/bin/env python3
"""Host09 preparation only. No production training backend is provided.

All execution is explicitly synthetic. Trusted callbacks are cooperative in-process
code, NOT an OS sandbox; deadlines cannot preempt a blocking Python callback.
"""
import hashlib
import json
import math
from pathlib import Path
import re
from dataclasses import dataclass
import os
import stat

ISOLATION_BASE = Path.home() / '.hermes/cache/scratch'

SELECTION_METHOD = 'highest validation accuracy; macro-F1 then run ID tie break'
TRAINING_NOT_AUTHORIZED = 'TRAINING_NOT_AUTHORIZED'
REPO_ROOT = Path(__file__).resolve().parents[2]
ROLES = {'source', 'protocol', 'freeze', 'candidate', 'label_map'}


class RunnerError(ValueError):
    """Only fixed safe diagnostic codes cross the CLI/log boundary."""


def require(condition, code='INVALID_CONFIG'):
    if not condition:
        raise RunnerError(code)


def keys(value, expected):
    require(type(value) is dict and set(value) == set(expected))


def number(value, low, high):
    require(type(value) in (int, float) and math.isfinite(value) and low <= value <= high)


def identity(value):
    require(type(value) is str and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', value) is not None)


def absolute(value):
    require(type(value) is str and value and Path(value).is_absolute())
    require('..' not in Path(value).parts and str(Path(value)) == value)
    return Path(value)


def validate_config(config):
    """Validate explicit proposals, never grant training authority."""
    keys(config, {'schema_version','status','training_authorized','synthetic_only',
        'partition','run_id','output_root','bindings','protocol','selection_method',
        'budget','baseline','variants','model_contract'})
    m = config['model_contract']
    keys(m, {'architecture','seq_len','features','drop_face','conv_filters','lstm_units','dense'})
    require(m['architecture'] == 'CNN-LSTM' and m['drop_face'] is True)
    for key, expected in (('seq_len',30),('features',258),('dense',128)):
        require(type(m[key]) is int and m[key] == expected)
    for key, expected in (('conv_filters',[64,128]),('lstm_units',[128,64])):
        require(type(m[key]) is list and all(type(n) is int for n in m[key]) and m[key] == expected)
    require(type(config['schema_version']) is int and config['schema_version'] == 1)
    require(config['training_authorized'] is False, TRAINING_NOT_AUTHORIZED)
    require(config['synthetic_only'] is True and config['status'] == 'proposed')
    require(config['partition'] == 'validation' and config['selection_method'] == SELECTION_METHOD)
    identity(config['run_id'])
    absolute(config['output_root'])
    keys(config['bindings'], ROLES)
    for binding in config['bindings'].values():
        keys(binding, {'path','sha256'})
        absolute(binding['path'])
        require(type(binding['sha256']) is str and re.fullmatch('[0-9a-f]{64}', binding['sha256']) is not None)
    p = config['protocol']
    keys(p, {'version','algorithm','seed','validation_clips','augmentation'})
    require(p['version'] == 'evaluation-v1' and p['algorithm'] == 'stratified-original-clip-v1')
    require(type(p['seed']) is int and p['seed'] == 20260705 and p['augmentation'] == 'fit-only')
    require(type(p['validation_clips']) is list and bool(p['validation_clips']))
    require(all(type(x) is str and x for x in p['validation_clips']))
    require(len(set(p['validation_clips'])) == len(p['validation_clips']))
    b = config['budget']
    keys(b, {'max_experiments','max_total_seconds','max_variant_seconds','max_epochs','batch_size','early_stop_patience'})
    require(all(type(v) is int and v > 0 for v in b.values()))
    require(b['max_experiments'] <= 2 and b['max_variant_seconds'] <= b['max_total_seconds'])
    # Upper bounds are the design's PROPOSED envelope, not training approval.
    require(b['max_epochs'] <= 60 and b['batch_size'] <= 32 and b['early_stop_patience'] <= 15 and b['max_variant_seconds'] <= 900)
    keys(config['baseline'], {'dropout','learning_rate'})
    number(config['baseline']['dropout'], 0, 1)
    number(config['baseline']['learning_rate'], 1e-12, 1)
    variants = config['variants']
    require(type(variants) is list and 1 <= len(variants) <= b['max_experiments'])
    names = []
    for v in variants:
        keys(v, {'run_id','factor','value'})
        identity(v['run_id']); names.append(v['run_id'])
        require(v['factor'] in ('dropout','learning_rate'))
        number(v['value'], 0 if v['factor'] == 'dropout' else 1e-12, 1)
        require(v['value'] != config['baseline'][v['factor']])
    require(len(set(names)) == len(names))
    require(len({v['factor'] for v in variants}) == len(variants))
    return json.loads(json.dumps(config, allow_nan=False))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(path):
    path = absolute(str(path))
    require(not any(p.is_symlink() for p in (path, *path.parents)), 'UNSAFE_PATH')
    return path


def read_bytes(path):
    path = safe_path(path)
    info = path.stat()
    require(stat.S_ISREG(info.st_mode) and not (getattr(info, 'st_flags', 0) & 0x40000000), 'UNREADABLE_INPUT')
    require(info.st_size <= 8 * 1024 * 1024, 'INPUT_TOO_LARGE')
    # No arrays or model deserialization. Candidate bytes are identity only.
    require(path.suffix.lower() not in ('.npy', '.npz'), 'ARRAY_INPUT_FORBIDDEN')
    with path.open('rb') as stream:
        data = stream.read(8 * 1024 * 1024 + 1)
    require(len(data) <= 8 * 1024 * 1024, 'INPUT_TOO_LARGE')
    return data


def parse_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'INVALID_JSON')
            result[key] = value
        return result
    def invalid(_):
        raise RunnerError('INVALID_JSON')
    try:
        return json.loads(data, object_pairs_hook=pairs, parse_constant=invalid)
    except (ValueError, UnicodeError) as exc:
        raise RunnerError('INVALID_JSON') from exc


def check_bindings(config):
    """Metadata-only check. Never open protocol arrays, clips or checkpoint paths.

    The protected validator opens test metadata/arrays, so is deliberately not
    reused here. This verifies declared grouping/counts, not original-row equality
    or regeneration of the stratified split; those remain provenance gates.
    """
    payload = {}
    for role, binding in config['bindings'].items():
        data = read_bytes(Path(binding['path']))
        require(digest(data) == binding['sha256'], 'INPUT_CHANGED')
        if role in ('protocol','freeze','label_map'):
            payload[role] = parse_json(data)
    p = payload['protocol']
    keys(p, {'version','seed','validation_fraction','algorithm','source_sha256',
             'n_fit_original','n_validation','class_counts','rows'})
    require(p['version'] == config['protocol']['version'] and p['algorithm'] == config['protocol']['algorithm'])
    require(type(p['seed']) is int and p['seed'] == config['protocol']['seed'])
    number(p['validation_fraction'], 0.2, 0.2)
    keys(p['source_sha256'], {'X_train.npy','y_train.npy','clips_train.json','clips_test.json'})
    for h in p['source_sha256'].values():
        require(type(h) is str and re.fullmatch('[0-9a-f]{64}', h) is not None)
    require(type(p['rows']) is list and bool(p['rows']))
    names, val, counts = [], [], {}
    nfit = 0
    for index, row in enumerate(p['rows']):
        keys(row, {'index','clip','class_id','partition'})
        require(type(row['index']) is int and row['index'] == index)
        require(type(row['class_id']) is int and row['class_id'] >= 0)
        require(type(row['clip']) is str and row['clip'] and row['partition'] in ('fit','validation'))
        names.append(row['clip'])
        cc = counts.setdefault(str(row['class_id']), {})
        cc[row['partition']] = cc.get(row['partition'], 0) + 1
        if row['partition'] == 'validation': val.append(row['clip'])
        else: nfit += 1
    require(len(set(names)) == len(names) and val == config['protocol']['validation_clips'])
    require(type(p['n_fit_original']) is int and p['n_fit_original'] == nfit and nfit > 0)
    require(type(p['n_validation']) is int and p['n_validation'] == len(val))
    require(type(p['class_counts']) is dict and p['class_counts'] == counts)
    for cc in p['class_counts'].values():
        keys(cc, {'fit','validation'})
        require(all(type(n) is int and n > 0 for n in cc.values()))
        total = cc['fit'] + cc['validation']
        require(total >= 3 and cc['validation'] == min(total - 1, max(2, round(total * p['validation_fraction']))))
    labels = payload['label_map']
    require(type(labels) is dict and set(labels) == set(counts))
    require(set(labels) == {str(i) for i in range(len(labels))})
    label_names = []
    for index, item in labels.items():
        keys(item, {'id','label','category'})
        require(type(item['id']) is int and str(item['id']) == index)
        require(type(item['label']) is str and item['label'] and type(item['category']) is str and item['category'])
        label_names.append(item['label'])
    require(len(set(label_names)) == len(label_names))
    f = payload['freeze']
    keys(f, {'run_id','checkpoint','checkpoint_sha256','protocol_sha256','best_val_accuracy',
             'best_val_macro_f1','selection_method','test_status'})
    identity(f['run_id'])
    require(type(f['checkpoint']) is str and bool(f['checkpoint']))
    require(type(f['checkpoint_sha256']) is str and re.fullmatch('[0-9a-f]{64}', f['checkpoint_sha256']) is not None)
    require(f['protocol_sha256'] == config['bindings']['protocol']['sha256'])
    require(f['selection_method'] == SELECTION_METHOD)
    require(f['test_status'] == 'exploratory: existing FSL-105 test was consulted by historical runs')
    number(f['best_val_accuracy'], 0, 1); number(f['best_val_macro_f1'], 0, 1)
    return {role: binding['sha256'] for role,binding in config['bindings'].items()}


def publish(path, payload, verify=None):
    """Exclusive strict JSON, readback and owned-inode rollback on failure.

    Trusted local filesystem only; not a power-loss or hostile-writer guarantee.
    """
    data = canonical(payload)
    safe_path(path.parent)
    require(ISOLATION_BASE in path.parents and REPO_ROOT not in path.parents, 'UNSAFE_OUTPUT_ROOT')
    fixed = path.name in ('manifest.json','execution.json','completion.json')
    log = path.parent.name == 'logs' and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}\.(started|result)\.json', path.name) is not None
    require(fixed or log, 'UNSUPPORTED_OUTPUT_ARTIFACT')
    require(not path.is_symlink(), 'UNSAFE_PATH')
    owned = None
    try:
        with path.open('xb') as stream:
            info = os.fstat(stream.fileno())
            owned = (info.st_dev, info.st_ino)
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        require(read_bytes(path) == data, 'OUTPUT_CHANGED')
        if verify is not None:
            verify()
        require(read_bytes(path) == data, 'OUTPUT_CHANGED')
    except BaseException as exc:
        if owned is not None:
            try:
                safe_path(path.parent)
                info = path.lstat()
                if stat.S_ISREG(info.st_mode) and (info.st_dev, info.st_ino) == owned:
                    path.unlink()
            except (OSError, RunnerError):
                pass  # Preserve original error; no success is returned.
        if isinstance(exc, OSError):
            raise RunnerError('OUTPUT_PUBLICATION_FAILED') from exc
        raise
    return digest(data)


@dataclass(frozen=True)
class Prepared:
    root: Path
    config_bytes: bytes
    manifest_sha256: str
    root_device: int
    root_inode: int


def prepare(config):
    """Publish a new immutable proposal under the dedicated host scratch base."""
    c = validate_config(config)
    root = safe_path(Path(c['output_root']))
    base = safe_path(ISOLATION_BASE)
    require(base in root.parents and REPO_ROOT not in root.parents, 'UNSAFE_OUTPUT_ROOT')
    require(root.parent.is_dir() and not root.exists(), 'OUTPUT_EXISTS_OR_PARENT_MISSING')
    require(all(root not in Path(b['path']).parents for b in c['bindings'].values()), 'INPUT_OUTPUT_OVERLAP')
    bindings = check_bindings(c)
    manifest = {'schema_version':1, 'kind':'SYNTHETIC_PREPARATION_NOT_TRAINING',
                'config':c,'config_sha256':digest(canonical(c)), 'input_hashes':bindings,
                'runner_sha256':digest(read_bytes(Path(__file__).resolve()))}
    try:
        root.mkdir(mode=0o700)
        (root/'logs').mkdir(mode=0o700)
    except OSError as exc:
        raise RunnerError('OUTPUT_EXISTS_OR_PARENT_MISSING') from exc
    h = publish(root/'manifest.json', manifest)
    require(check_bindings(c) == bindings, 'INPUT_CHANGED')
    info = root.stat()
    return Prepared(root, canonical(c), h, info.st_dev, info.st_ino)


@dataclass(frozen=True)
class SyntheticRequest:
    run_id: str
    factor: str
    value: float
    baseline: tuple
    budget: tuple
    synthetic_only: bool = True


class _Stop(Exception):
    def __init__(self, code):
        self.code = code if code in ('TIMEOUT','CANCELLED','INVALID_CLOCK','INVALID_CANCEL_SIGNAL','INVALID_METRICS') else 'FAILED'


class _Control:
    """Deadline/cancellation checks only; no path, writer or command interface."""
    def __init__(self, clock, cancelled, budget):
        self._clock, self._cancelled, self._budget = clock, cancelled, budget
        self._last = None
        self.start = self._now()
        self.variant_start = self.start

    def _now(self):
        now = self._clock()
        if type(now) not in (int, float) or not math.isfinite(now) or now < 0 or (self._last is not None and now < self._last):
            raise _Stop('INVALID_CLOCK')
        self._last = now
        return now

    def checkpoint(self):
        cancelled = self._cancelled()
        if type(cancelled) is not bool:
            raise _Stop('INVALID_CANCEL_SIGNAL')
        if cancelled:
            raise _Stop('CANCELLED')
        now = self._now()
        if now - self.start >= self._budget['max_total_seconds'] or now - self.variant_start >= self._budget['max_variant_seconds']:
            raise _Stop('TIMEOUT')
        return now


def verify_prepared(prepared, output_hashes=None):
    require(type(prepared) is Prepared, 'INVALID_PREPARATION')
    root = safe_path(prepared.root)
    require(ISOLATION_BASE in root.parents and REPO_ROOT not in root.parents, 'UNSAFE_OUTPUT_ROOT')
    info = root.stat()
    require((info.st_dev, info.st_ino) == (prepared.root_device, prepared.root_inode), 'OUTPUT_CHANGED')
    safe_path(root/'logs')
    data = read_bytes(root/'manifest.json')
    require(digest(data) == prepared.manifest_sha256, 'MANIFEST_CHANGED')
    manifest = parse_json(data)
    config = validate_config(parse_json(prepared.config_bytes))
    require(config['output_root'] == str(root) and manifest['config'] == config, 'MANIFEST_CHANGED')
    require(manifest['config_sha256'] == digest(prepared.config_bytes), 'MANIFEST_CHANGED')
    require(manifest['runner_sha256'] == digest(read_bytes(Path(__file__).resolve())), 'RUNNER_CHANGED')
    require(manifest['input_hashes'] == check_bindings(config), 'INPUT_CHANGED')
    for name, expected in (output_hashes or {}).items():
        require(digest(read_bytes(root/name)) == expected, 'OUTPUT_CHANGED')
    return config


def checked_signals(value):
    try:
        keys(value, {'kind','validation_accuracy_signal','validation_macro_f1_signal'})
        require(value['kind'] == 'SYNTHETIC_SIGNALS_NOT_MODEL_METRICS')
        number(value['validation_accuracy_signal'], 0, 1)
        number(value['validation_macro_f1_signal'], 0, 1)
        return parse_json(canonical(value))
    except (RunnerError, ValueError, TypeError) as exc:
        raise _Stop('INVALID_METRICS') from exc


def run_synthetic(prepared, executor, clock, cancelled=lambda: False):
    """Run a trusted cooperative fake executor once, sequentially, without retries.

    No shell, subprocess, checkpoint discovery, real backend or model loading.
    The callback can execute arbitrary Python because it is trusted, so neither
    filesystem sandboxing nor hard preemption is claimed. CLI never loads one.
    """
    c = verify_prepared(prepared)
    root = prepared.root
    outputs = {'manifest.json':prepared.manifest_sha256}
    outputs['execution.json'] = publish(root/'execution.json', {
        'kind':'SYNTHETIC_INCOMPLETE_UNTIL_COMPLETION', 'run_id':c['run_id'],
        'manifest_sha256':prepared.manifest_sha256})
    states = {v['run_id']:'NOT_STARTED' for v in c['variants']}
    records = []
    status = 'SYNTHETIC_COMPLETE'
    try:
        control = _Control(clock, cancelled, c['budget'])
        for v in c['variants']:
            verify_prepared(prepared, outputs)
            control.checkpoint()
            control.variant_start = control._last
            rid = v['run_id']
            started = 'logs/' + rid + '.started.json'
            outputs[started] = publish(root/started, {'kind':'SYNTHETIC_STARTED', 'run_id':rid})
            states[rid] = 'INCOMPLETE'
            request = SyntheticRequest(rid, v['factor'], v['value'],
                tuple(sorted(c['baseline'].items())), tuple(sorted(c['budget'].items())))
            try:
                value = executor(request, control)
                control.checkpoint()
                value = checked_signals(value)
                states[rid] = 'SYNTHETIC_COMPLETE'
                records.append(dict(value, run_id=rid))
            except _Stop as stop:
                states[rid] = stop.code
                status = stop.code
            except KeyboardInterrupt:
                states[rid] = status = 'INTERRUPTED'
            except Exception:
                states[rid] = status = 'FAILED'
            result = 'logs/' + rid + '.result.json'
            payload = {'kind':'SYNTHETIC_RESULT_NOT_MODEL_METRICS','run_id':rid,'status':states[rid]}
            if status == 'SYNTHETIC_COMPLETE':payload['signals'] = value
            outputs[result] = publish(root/result, payload)
            verify_prepared(prepared, outputs)
            if status != 'SYNTHETIC_COMPLETE':break
    except _Stop as stop:
        status = stop.code
    except KeyboardInterrupt:
        status = 'INTERRUPTED'
    # Any integrity/publication error propagates with no completion receipt;
    # execution.json and any started logs remain visibly incomplete.
    verify_prepared(prepared, outputs)
    success = status == 'SYNTHETIC_COMPLETE' and len(records) == len(c['variants'])
    selected = None
    if success:
        selected = sorted(records, key=lambda r:(-r['validation_accuracy_signal'],
            -r['validation_macro_f1_signal'],r['run_id']))[0]['run_id']
    receipt = {'schema_version':1,'kind':'SYNTHETIC_ONLY_NOT_TRAINING_OR_MODEL_METRICS',
        'run_id':c['run_id'],'status':status,'success':success,
        'training_authorized':False,'selected_synthetic_run_id':selected,
        'selection_method':SELECTION_METHOD,'variant_states':states,
        'manifest_sha256':prepared.manifest_sha256,'output_hashes':outputs}
    publish(root/'completion.json', receipt, verify=lambda: verify_prepared(prepared, outputs))
    return receipt


def execute_training(*args, **kwargs):
    """Deliberately disabled regardless of caller/config flags."""
    raise RunnerError(TRAINING_NOT_AUTHORIZED)


class _DemoClock:
    def __init__(self):
        self.value = 0

    def __call__(self):
        return self.value


def main(argv=None):
    """Only prepare/dry-run are supported; stdout is fixed safe JSON.

    Usage: experiment_runner.py {prepare|dry-run} --config /absolute/config.json
    Output must be a fresh directory beneath ~/.hermes/cache/scratch. Dry-run
    uses ONLY built-in deterministic synthetic signals and virtual time.
    """
    import sys
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        if args and args[0] in ('execute', 'train'):
            execute_training()
        require(len(args) == 3 and args[0] in ('prepare','dry-run') and args[1] == '--config', 'INVALID_REQUEST')
        config = parse_json(read_bytes(absolute(args[2])))
        prepared = prepare(config)
        status = 'PREPARED'
        if args[0] == 'dry-run':
            clock = _DemoClock()
            def demo(request, control):
                clock.value += 1
                control.checkpoint()
                return {'kind':'SYNTHETIC_SIGNALS_NOT_MODEL_METRICS',
                        'validation_accuracy_signal':0.5,'validation_macro_f1_signal':0.5}
            receipt = run_synthetic(prepared, demo, clock)
            status = receipt['status']
        print(canonical({'kind':'SYNTHETIC_PREPARATION_ONLY','status':status,
            'training_authorized':False,'manifest_sha256':prepared.manifest_sha256}).decode())
        return 0 if status in ('PREPARED','SYNTHETIC_COMPLETE') else 1
    except (Exception, KeyboardInterrupt) as exc:
        # Never echo malformed config, arbitrary exception text, paths or argv.
        unauthorized = type(exc) is RunnerError and str(exc) == TRAINING_NOT_AUTHORIZED
        print(canonical({'code':TRAINING_NOT_AUTHORIZED if unauthorized else 'INVALID_REQUEST',
                         'training_authorized':False}).decode())
        return 3 if unauthorized else 2


if __name__ == '__main__':
    raise SystemExit(main())
