"""Synthetic raw-output audit tests; never load a real model or camera."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np


class AuditTests(unittest.TestCase):
    def test_exclusive_persistence_independent_check_and_tamper(self):
        self.assertIsNotNone(importlib.util.find_spec('training.holistic_migration.verify_recognition'),
                             'durable verifier missing')
        from training.holistic_migration import verify_recognition as v
        from training.holistic_migration.recognition import presentation_rows
        labels=[str(i) for i in range(50)]; p=np.full(50,.02)
        with tempfile.TemporaryDirectory(dir=Path.home()/'.hermes/cache/scratch') as d:
            run=Path(d)/'run'
            audit=v.AuditRun(run,labels,{'classifier':'a'*64,'features':'b'*64,'labels':'c'*64})
            rows=presentation_rows(p,labels)
            audit.save(p,rows)
            self.assertEqual(v.check_run(run),1)
            with self.assertRaises(FileExistsError): v.AuditRun(run,labels,{})
            target=run/'attempt-000001.json'
            record=json.loads(target.read_text()); self.assertEqual(record['top3'],rows)
            record['top3'][0]['score']=1.
            target.write_text(json.dumps(record))
            with self.assertRaises(ValueError): v.check_run(run)


class ArchiveFailureTests(unittest.TestCase):
    def test_missing_latest_attempt_is_rejected(self):
        from training.holistic_migration import verify_recognition as v
        from training.holistic_migration.recognition import presentation_rows
        with tempfile.TemporaryDirectory(dir=Path.home()/'.hermes/cache/scratch') as d:
            p=np.full(50,.02); labels=[str(i) for i in range(50)]
            run=Path(d)/'run'; audit=v.AuditRun(run,labels,dict(classifier='a'*64,features='b'*64,labels='c'*64))
            audit.save(p,presentation_rows(p,labels)); audit.save(p,presentation_rows(p,labels))
            (run/'attempt-000002.json').unlink()
            with self.assertRaises(ValueError): v.check_run(run)


class AuditMatrixTests(unittest.TestCase):
    def test_independent_schema_probability_order_and_display_matrix(self):
        import copy
        from training.holistic_migration import verify_recognition as v
        from training.holistic_migration.recognition import presentation_rows
        labels=[str(i) for i in range(50)]; p=np.full(50,.02)
        good=dict(schema=1,attempt=1,raw_output=p.tolist(),top3=presentation_rows(p,labels))
        v.validate_record(good,labels)
        variants=[]
        for key,value in [('schema',1.),('attempt',True),('raw_output',p.tolist()[:-1]),('top3',[])]:
            bad=copy.deepcopy(good); bad[key]=value; variants.append(bad)
        for value in [float('nan'),float('inf'),-.1,1.1]:
            bad=copy.deepcopy(good); bad['raw_output'][0]=value; variants.append(bad)
        for key,value in [('rank',2),('index',4),('label','BAD'),('score',1/3),('display_text','1. 0: 2.00%')]:
            bad=copy.deepcopy(good); bad['top3'][0][key]=value; variants.append(bad)
        bad=copy.deepcopy(good); bad['top3'].reverse(); variants.append(bad)
        for bad in variants:
            with self.subTest(bad=bad),self.assertRaises(ValueError): v.validate_record(bad,labels)

    def test_publication_failure_leaves_unusable_barrier(self):
        from unittest.mock import patch
        from training.holistic_migration import verify_recognition as v
        from training.holistic_migration.recognition import presentation_rows
        with tempfile.TemporaryDirectory(dir=Path.home()/'.hermes/cache/scratch') as d:
            p=np.full(50,.02); labels=[str(i) for i in range(50)]
            run=Path(d)/'run'; audit=v.AuditRun(run,labels,dict(classifier='a'*64,features='b'*64,labels='c'*64))
            with patch.object(v.os,'replace',side_effect=OSError('publication')):
                with self.assertRaises(OSError): audit.save(p,presentation_rows(p,labels))
            self.assertTrue((run/'INCOMPLETE').exists())
            with self.assertRaises(ValueError): v.check_run(run)

    def test_real_cli_help_pass_fail(self):
        import subprocess,sys
        from training.holistic_migration import verify_recognition as v
        from training.holistic_migration.recognition import presentation_rows
        command=[sys.executable,'-E','-B','-m','training.holistic_migration.verify_recognition']
        result=subprocess.run(command+['--help'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0); self.assertIn('--check',result.stdout)
        viewer=subprocess.run([sys.executable,'-E','-B','-m','training.holistic_migration.recognition_webcam','--help'],capture_output=True,text=True)
        self.assertEqual(viewer.returncode,0); self.assertIn('--audit-dir',viewer.stdout)
        with tempfile.TemporaryDirectory(dir=Path.home()/'.hermes/cache/scratch') as d:
            p=np.full(50,.02); labels=[str(i) for i in range(50)]
            run=Path(d)/'run'; audit=v.AuditRun(run,labels,dict(classifier='a'*64,features='b'*64,labels='c'*64))
            audit.save(p,presentation_rows(p,labels))
            result=subprocess.run(command+['--check',str(run)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout); self.assertIn('PASS',result.stdout)
            (run/'labels.json').write_text('[]')
            result=subprocess.run(command+['--check',str(run)],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0); self.assertIn('FAIL',result.stdout)
