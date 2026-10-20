"""Explicit-file validation / SYNTHETIC-only descriptive CLI; no store discovery."""
import argparse
import hashlib
import json
import os
import re
import stat
from .legacy_export import Rejected, require, validate_bytes
from .synthetic_descriptive import describe_exports

MAX_BYTES = 16 * 1024 * 1024

class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise Rejected('ARGUMENTS')

def _directory(parent, name):
    return os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)

def _root(path):
    require(type(path) is str and path.startswith('/'), 'PATH_REJECTED')
    parts = path.split('/')[1:]
    require(bool(parts) and all(p and p not in ('.','..') for p in parts), 'PATH_REJECTED')
    current = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in parts:
            nxt = _directory(current, part)
            os.close(current)
            current = nxt
        return current
    except BaseException:
        os.close(current)
        raise

def _read_input(root, path):
    require(type(path) is str and not path.startswith('/'), 'PATH_REJECTED')
    parts = path.split('/')
    require(all(p and p not in ('.','..') for p in parts), 'PATH_REJECTED')
    current = os.dup(root)
    try:
        for part in parts[:-1]:
            nxt = _directory(current, part)
            os.close(current)
            current = nxt
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=current)
        with os.fdopen(fd, 'rb') as stream:
            require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), 'PATH_REJECTED')
            require(os.fstat(stream.fileno()).st_size <= MAX_BYTES, 'INPUT_LIMIT')
            data = stream.read(MAX_BYTES + 1)
            require(len(data) <= MAX_BYTES, 'INPUT_LIMIT')
            return data
    finally:
        os.close(current)

def _json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode('utf-8')

def _write_read(directory, name, data, *, owned):
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=directory)
    with os.fdopen(fd, 'wb') as stream:
        info = os.fstat(stream.fileno())
        owned[name] = (info.st_dev, info.st_ino)
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
    with os.fdopen(fd, 'rb') as stream:
        require(stream.read(len(data) + 1) == data, 'OUTPUT_READBACK')

def _publish(root, label, report, manifest):
    os.mkdir(label, mode=0o700, dir_fd=root)
    directory = _directory(root, label)
    owned = {}
    try:
        report_bytes = _json_bytes(report)
        _write_read(directory, 'report.json', report_bytes, owned=owned)
        # Publish success only after every declared artifact has been read back.
        manifest['artifacts'] = {'report.json':hashlib.sha256(report_bytes).hexdigest()}
        _write_read(directory, 'manifest.json', _json_bytes(manifest), owned=owned)
    except BaseException:
        try:
            info = os.stat('manifest.json', dir_fd=directory, follow_symlinks=False)
            if owned.get('manifest.json') == (info.st_dev, info.st_ino):
                os.unlink('manifest.json', dir_fd=directory)
        except FileNotFoundError:
            pass
        raise
    finally:
        os.close(directory)

def main(argv=None):
    root = None
    try:
        parser = Parser(description=__doc__, allow_abbrev=False, add_help=False)
        parser.add_argument('--mode', required=True, choices=('validate','describe'))
        parser.add_argument('--root', required=True)
        parser.add_argument('--input', required=True, action='append')
        parser.add_argument('--source', required=True, choices=('SYNTHETIC','UNATTESTED'))
        parser.add_argument('--output-label', required=True)
        args = parser.parse_args(argv)
        require(re.fullmatch(r'SYNTHETIC-[0-9]{1,12}', args.output_label) is not None, 'OUTPUT_LABEL')
        require(args.mode != 'describe' or args.source == 'SYNTHETIC', 'SYNTHETIC_REQUIRED')
        require(len(args.input) == len(set(args.input)), 'DUPLICATE_INPUT')
        root = _root(args.root)
        snapshots = [_read_input(root, path) for path in args.input]
        if args.mode == 'describe':
            report = describe_exports(snapshots, source=args.source)
        else:
            results = [validate_bytes(data) for data in snapshots]
            report = {'valid':all(x['valid'] for x in results), 'validation':results}
            report['diagnostics'] = [dict(d,input_index=i) for i,x in enumerate(results) for d in x['diagnostics']]
        if not report['valid']:
            print(json.dumps(report, allow_nan=False, sort_keys=True))
            return 2
        manifest = {'schema_version':1,'output_label':args.output_label,
                    'source':args.source,'mode':args.mode,
                    'authorization':'NO_PARTICIPANT_AUTHORIZATION',
                    'inputs':[{'index':i,'sha256':hashlib.sha256(data).hexdigest()} for i,data in enumerate(snapshots)]}
        _publish(root, args.output_label, report, manifest)
        print(json.dumps({'valid':True,'code':'PUBLISHED','input_count':len(snapshots)},sort_keys=True))
        return 0
    except Rejected as failure:
        code = str(failure)
    except (OSError, ValueError, TypeError, RecursionError, OverflowError):
        code = 'IO_REJECTED'
    finally:
        if root is not None:
            os.close(root)
    print(json.dumps({'valid':False,'diagnostics':[{'code':code}]},sort_keys=True))
    return 2

if __name__ == '__main__':
    raise SystemExit(main())
