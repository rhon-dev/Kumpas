"""Executed CLI tests use fresh synthetic roots only."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from evaluation import export_cli
from evaluation.test_legacy_export import fixture, encode

class CliTests(unittest.TestCase):
    def setUp(self):
        scratch=Path.home()/'.hermes/cache/scratch'
        self.tmp=tempfile.TemporaryDirectory(prefix='kumpas-c2-SYNTHETIC-',dir=scratch)
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        (self.root/'input.json').write_bytes(encode(fixture()))

    def args(self, **changes):
        args={'mode':'describe','root':str(self.root),'input':'input.json','source':'SYNTHETIC','output-label':'SYNTHETIC-001'}
        args.update(changes)
        return [x for k,v in args.items() for x in ('--'+k,v)]

    def run_cli(self,args):
        cp=subprocess.run([sys.executable,'-B','-E','-m','evaluation.export_cli',*args],capture_output=True)
        self.assertEqual(cp.stderr,b'')
        self.assertNotIn(b'PRIVATE CANARY',cp.stdout)
        self.assertNotIn(str(self.root).encode(),cp.stdout)
        return cp.returncode,json.loads(cp.stdout)

    def test_cli_publishes_readback_and_hash_bound_manifest(self):
        status,result=self.run_cli(self.args())
        self.assertEqual(status,0,result)
        out=self.root/'SYNTHETIC-001'
        manifest=json.loads((out/'manifest.json').read_bytes())
        report=(out/'report.json').read_bytes()
        self.assertEqual(manifest['artifacts']['report.json'],hashlib.sha256(report).hexdigest())
        self.assertEqual(manifest['inputs'][0]['sha256'],hashlib.sha256((self.root/'input.json').read_bytes()).hexdigest())
        self.assertEqual(json.loads(report)['matching']['paired'],1)
        before={p.name:p.read_bytes() for p in out.iterdir()}
        self.assertEqual(self.run_cli(self.args())[0],2)
        self.assertEqual({p.name:p.read_bytes() for p in out.iterdir()},before)

    def test_cli_fails_closed_without_payload_echo(self):
        for change in [{'input':'../PRIVATE CANARY.json'}, {'input':'/PRIVATE CANARY.json'}, {'input':'missing.json'}, {'source':'real'}, {'output-label':'../escape'}, {'mode':'PRIVATE CANARY'}]:
            with self.subTest(change=change):
                status,_=self.run_cli(self.args(**change))
                self.assertEqual(status,2)
                self.assertFalse((self.root/'SYNTHETIC-001'/'manifest.json').exists())
        (self.root/'input.json').write_bytes(b'{"responses":"PRIVATE CANARY","x":NaN}')
        status,result=self.run_cli(self.args())
        self.assertEqual(status,2)
        self.assertEqual(result['diagnostics'][0]['code'],'JSON_INVALID')
        self.assertFalse((self.root/'SYNTHETIC-001').exists())

    def test_symlink_inputs_roots_and_outputs_rejected(self):
        (self.root/'link.json').symlink_to(self.root/'input.json')
        self.assertEqual(self.run_cli(self.args(input='link.json'))[0],2)
        (self.root/'alias').symlink_to(self.root,target_is_directory=True)
        self.assertEqual(self.run_cli(self.args(root=str(self.root/'alias')))[0],2)
        (self.root/'SYNTHETIC-001').symlink_to(self.root,target_is_directory=True)
        self.assertEqual(self.run_cli(self.args())[0],2)
        self.assertFalse((self.root/'manifest.json').exists())

    def test_argument_help_is_json_and_duplicate_input_paths_fail(self):
        status,result=self.run_cli(['--help'])
        self.assertEqual(status,2)
        self.assertEqual(result['diagnostics'][0]['code'],'ARGUMENTS')
        status,result=self.run_cli(self.args(mode='validate')+['--input','input.json'])
        self.assertEqual(status,2)
        self.assertEqual(result['diagnostics'][0]['code'],'DUPLICATE_INPUT')
        self.assertFalse((self.root/'SYNTHETIC-001').exists())

    def test_publication_faults_never_leave_success_manifest(self):
        original=export_cli._write_read
        for index, failing in enumerate(('report.json','manifest.json')):
            label='SYNTHETIC-'+str(100+index)
            def fail_after_write(directory,name,data,**kwargs):
                original(directory,name,data,**kwargs)
                if name==failing:
                    raise export_cli.Rejected('OUTPUT_READBACK')
            output=io.StringIO()
            with patch.object(export_cli,'_write_read',side_effect=fail_after_write), contextlib.redirect_stdout(output):
                status=export_cli.main(self.args(**{'output-label':label}))
            self.assertEqual(status,2)
            self.assertEqual(json.loads(output.getvalue())['diagnostics'][0]['code'],'OUTPUT_READBACK')
            self.assertFalse((self.root/label/'manifest.json').exists())
        with patch.object(export_cli.os,'fsync',side_effect=OSError('PRIVATE CANARY')), contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(export_cli.main(self.args()),2)
        self.assertNotIn('PRIVATE CANARY',output.getvalue())
        self.assertFalse((self.root/'SYNTHETIC-001'/'manifest.json').exists())
        self.assertEqual(self.run_cli(self.args())[0],2)  # partial root cannot be reused

    def test_validate_mode_unattested_is_not_descriptive_authorization(self):
        status,_=self.run_cli(self.args(mode='validate',source='UNATTESTED'))
        self.assertEqual(status,0)
        manifest=json.loads((self.root/'SYNTHETIC-001'/'manifest.json').read_text())
        self.assertEqual(manifest['source'],'UNATTESTED')
        self.assertEqual(manifest['authorization'],'NO_PARTICIPANT_AUTHORIZATION')
        self.assertEqual(self.run_cli(self.args(source='UNATTESTED',**{'output-label':'SYNTHETIC-002'}))[0],2)

    def test_nonregular_input_and_symlink_parent_rejected(self):
        (self.root/'folder').mkdir()
        (self.root/'alias').symlink_to(self.root,target_is_directory=True)
        for path in ('folder','alias/input.json'):
            self.assertEqual(self.run_cli(self.args(input=path))[0],2)
        os.mkfifo(self.root/'pipe')
        self.assertEqual(self.run_cli(self.args(input='pipe'))[0],2)

    def test_input_path_replacement_after_snapshot_hashes_original_report_bytes(self):
        original_bytes = (self.root / 'input.json').read_bytes()
        original_publish = export_cli._publish
        calls = []
        def replace_then_publish(root, label, report, manifest):
            calls.append(label)
            replacement = self.root / 'replacement.json'
            replacement.write_bytes(b'INVALID SYNTHETIC REPLACEMENT')
            os.replace(replacement, self.root / 'input.json')
            return original_publish(root, label, report, manifest)
        with patch.object(export_cli, '_publish', side_effect=replace_then_publish), contextlib.redirect_stdout(io.StringIO()) as output:
            status = export_cli.main(self.args())
        self.assertEqual(status, 0)
        self.assertEqual(calls, ['SYNTHETIC-001'])
        self.assertEqual(json.loads(output.getvalue())['code'], 'PUBLISHED')
        out = self.root / 'SYNTHETIC-001'
        manifest = json.loads((out / 'manifest.json').read_bytes())
        report_bytes = (out / 'report.json').read_bytes()
        self.assertEqual(manifest['inputs'][0]['sha256'], hashlib.sha256(original_bytes).hexdigest())
        self.assertNotEqual(manifest['inputs'][0]['sha256'], hashlib.sha256((self.root / 'input.json').read_bytes()).hexdigest())
        self.assertEqual(manifest['artifacts']['report.json'], hashlib.sha256(report_bytes).hexdigest())
        self.assertEqual(json.loads(report_bytes), export_cli.describe_exports([original_bytes], source='SYNTHETIC'))

    def test_failure_preserves_replacement_of_already_owned_manifest_inode(self):
        original_write = export_cli._write_read
        acquired = []
        sentinel = b'SYNTHETIC UNOWNED SENTINEL'
        def replace_owned_then_fail(directory, name, data, **kwargs):
            original_write(directory, name, data, **kwargs)
            if name == 'manifest.json':
                owned = os.stat(name, dir_fd=directory)
                self.assertEqual(kwargs['owned'][name], (owned.st_dev, owned.st_ino))
                # Retain the displaced inode until the test root is cleaned;
                # unlink/recreate would permit nondeterministic inode reuse.
                os.rename(name, 'displaced-owned-manifest.json', src_dir_fd=directory, dst_dir_fd=directory)
                fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600, dir_fd=directory)
                with os.fdopen(fd, 'wb') as stream:
                    stream.write(sentinel)
                replacement = os.stat(name, dir_fd=directory)
                self.assertNotEqual((owned.st_dev, owned.st_ino), (replacement.st_dev, replacement.st_ino))
                acquired.append((owned.st_dev, owned.st_ino))
                raise export_cli.Rejected('OUTPUT_READBACK')
        with patch.object(export_cli, '_write_read', side_effect=replace_owned_then_fail), contextlib.redirect_stdout(io.StringIO()) as output:
            status = export_cli.main(self.args())
        self.assertEqual(status, 2)
        self.assertEqual(json.loads(output.getvalue()), {'valid': False, 'diagnostics': [{'code': 'OUTPUT_READBACK'}]})
        self.assertEqual(len(acquired), 1)
        out = self.root / 'SYNTHETIC-001'
        self.assertEqual((out / 'manifest.json').read_bytes(), sentinel)
        displaced = out / 'displaced-owned-manifest.json'
        self.assertEqual((displaced.stat().st_dev, displaced.stat().st_ino), acquired[0])
        self.assertEqual(json.loads(displaced.read_bytes())['artifacts']['report.json'], hashlib.sha256((out / 'report.json').read_bytes()).hexdigest())

    def test_publication_collision_preserves_unowned_manifest(self):
        original=export_cli._write_read
        def insert_collision(directory,name,data,**kwargs):
            original(directory,name,data,**kwargs)
            if name=='report.json':
                fd=os.open('manifest.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600,dir_fd=directory)
                with os.fdopen(fd,'wb') as stream: stream.write(b'SYNTHETIC SENTINEL')
        with patch.object(export_cli,'_write_read',side_effect=insert_collision), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(export_cli.main(self.args()),2)
        self.assertEqual((self.root/'SYNTHETIC-001'/'manifest.json').read_bytes(),b'SYNTHETIC SENTINEL')

if __name__ == '__main__': unittest.main()
