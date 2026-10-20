"""Interprocess append regression; all history files are isolated fixtures."""
import contextlib
import fcntl
import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


from unittest import mock
import log_utils


class HistoryFailureTest(unittest.TestCase):
    def test_failures_preserve_bytes_clean_temp_release_lock_and_retry(self):
        for stage in ('serialization', 'partial_write', 'fsync', 'replace'):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                history = root / 'history.json'
                original = b'[ {"legacy": "unchanged"} ]\n'
                history.write_bytes(original)
                entry = dict(timestamp='synthetic', benchmark_type='fps', model_version='test',
                             device='synthetic', condition='optimal', results={})
                def partial_dump(rows, stream, **kwargs):
                    stream.write('[partial')
                    raise OSError('synthetic partial write')
                if stage == 'serialization':
                    entry['results']['bad'] = object()
                    fault = contextlib.nullcontext()
                elif stage == 'partial_write':
                    fault = mock.patch('log_utils.json.dump', side_effect=partial_dump)
                elif stage == 'fsync':
                    fault = mock.patch('log_utils.os.fsync', side_effect=OSError('synthetic fsync'))
                else:
                    fault = mock.patch.object(Path, 'replace', side_effect=OSError('synthetic replace'))
                with mock.patch.object(log_utils, 'HISTORY_PATH', history):
                    with fault, self.assertRaises((TypeError, OSError)):
                        log_utils.append_entry(entry)
                    self.assertEqual(original, history.read_bytes())
                    self.assertEqual({'history.json', 'history.json.lock'}, {p.name for p in root.iterdir()})
                    with history.with_suffix('.json.lock').open('a') as lock:
                        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        fcntl.flock(lock, fcntl.LOCK_UN)
                    entry['results'] = {}
                    log_utils.append_entry(entry)
                    self.assertEqual([{'legacy': 'unchanged'}, entry], json.loads(history.read_text()))


class HistoryConcurrencyTest(unittest.TestCase):
    def test_append_serializes_read_modify_write_across_processes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            history = root / 'history.json'
            original = {'legacy': 'unchanged'}
            history.write_text(json.dumps([original]))
            code = """
import sys, time
from pathlib import Path
import log_utils
root = Path(sys.argv[1]); name = sys.argv[2]
log_utils.HISTORY_PATH = root / 'history.json'
load = log_utils.load_history
def slow_load():
    rows = load()
    (root / (name + '.read')).touch()
    time.sleep(.4)
    return rows
log_utils.load_history = slow_load
(root / (name + '.ready')).touch()
log_utils.append_entry(dict(timestamp=name, benchmark_type='fps', model_version='test', device='synthetic', condition='optimal', results={}))
"""
            with history.with_suffix('.json.lock').open('a') as lock:
                fcntl.flock(lock, fcntl.LOCK_EX)
                workers = [subprocess.Popen([sys.executable, '-c', code, str(root), name], cwd=Path(__file__).parent,
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE) for name in ('one', 'two')]
                try:
                    deadline = time.monotonic() + 10
                    while not all((root / (n + '.ready')).exists() for n in ('one', 'two')):
                        self.assertLess(time.monotonic(), deadline, 'workers did not reach append')
                        time.sleep(.01)
                    time.sleep(.2)
                    read_under_lock = any((root / (n + '.read')).exists() for n in ('one', 'two'))
                finally:
                    fcntl.flock(lock, fcntl.LOCK_UN)
                    for worker in workers:
                        out, err = worker.communicate(timeout=15)
                        self.assertEqual(0, worker.returncode, err.decode())
            rows = json.loads(history.read_text())
            self.assertFalse(read_under_lock, 'append read history while interprocess lock was held')
            self.assertEqual(3, len(rows))
            self.assertEqual(original, rows[0])
            self.assertEqual({'one', 'two'}, {r['timestamp'] for r in rows[1:]})


if __name__ == '__main__':
    unittest.main()
