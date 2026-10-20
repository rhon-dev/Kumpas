"""Synthetic-only contract tests: never train or load arrays/models."""
import copy
import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
import io

from training.models import experiment_runner as runner


def dump(path, value):
    path.write_text(json.dumps(value, allow_nan=False, sort_keys=True))
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


class FakeClock:
    def __init__(self):self.value=0
    def __call__(self):return self.value
    def advance(self, seconds):self.value+=seconds


def signals(accuracy, f1):
    return {'kind':'SYNTHETIC_SIGNALS_NOT_MODEL_METRICS',
            'validation_accuracy_signal':accuracy,'validation_macro_f1_signal':f1}


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        protocol = {'version':'evaluation-v1','seed':20260705,'validation_fraction':0.2,
                    'algorithm':'stratified-original-clip-v1',
                    'source_sha256':{n:'a'*64 for n in ('X_train.npy','y_train.npy','clips_train.json','clips_test.json')},
                    'n_fit_original':1,'n_validation':2,
                    'class_counts':{'0':{'fit':1,'validation':2}},
                    'rows':[{'index':0,'clip':'0/fit','class_id':0,'partition':'fit'},
                            {'index':1,'clip':'0/val','class_id':0,'partition':'validation'},
                            {'index':2,'clip':'0/val2','class_id':0,'partition':'validation'}]}
        bindings = {'protocol': dump(self.root/'protocol.json',protocol),
                    'source': dump(self.root/'source.json',{'fixture':'synthetic code identity'}),
                    'candidate': dump(self.root/'candidate.json',{'fixture':'not a model'}),
                    'label_map':dump(self.root/'labels.json',{'0':{'id':0,'label':'SYNTHETIC','category':'SYNTHETIC'}})}
        bindings['freeze'] = dump(self.root/'freeze.json',{
            'run_id':'SYNTHETIC-baseline','checkpoint':'SYNTHETIC-NOT-OPENED',
            'checkpoint_sha256':'b'*64,'protocol_sha256':bindings['protocol']['sha256'],
            'best_val_accuracy':0.5,'best_val_macro_f1':0.5,
            'selection_method':runner.SELECTION_METHOD if hasattr(runner,'SELECTION_METHOD') else 'highest validation accuracy; macro-F1 then run ID tie break',
            'test_status':'exploratory: existing FSL-105 test was consulted by historical runs'})
        self.config = {'schema_version':1,'status':'proposed','training_authorized':False,
            'synthetic_only':True,'partition':'validation','run_id':'SYNTHETIC-campaign',
            'output_root':str(self.root/'campaign'), 'bindings':bindings,
            'protocol':{'version':'evaluation-v1','algorithm':'stratified-original-clip-v1',
                'seed':20260705,'validation_clips':['0/val','0/val2'],'augmentation':'fit-only'},
            'selection_method':'highest validation accuracy; macro-F1 then run ID tie break',
            'budget':{'max_experiments':2,'max_total_seconds':20,'max_variant_seconds':10,
                      'max_epochs':2,'batch_size':2,'early_stop_patience':1},
            'baseline':{'dropout':0.3,'learning_rate':0.001},
            'model_contract':{'architecture':'CNN-LSTM','seq_len':30,'features':258,
                'drop_face':True,'conv_filters':[64,128],'lstm_units':[128,64],'dense':128},
            'variants':[{'run_id':'SYNTHETIC-B','factor':'dropout','value':0.4},
                        {'run_id':'SYNTHETIC-A','factor':'learning_rate','value':0.002}]}

    def test_budget_exact_integer_matrix_and_variant_order_schema(self):
        for field in self.config['budget']:
            for value in (True,1.0,0,-1,float('nan')):
                c=copy.deepcopy(self.config);c['budget'][field]=value
                with self.subTest(field=field,value=value),self.assertRaises(runner.RunnerError):runner.validate_config(c)
        for variants in ([], self.config['variants']*2, list(reversed(self.config['variants']))):
            c=copy.deepcopy(self.config);c['variants']=copy.deepcopy(variants)
            if len(variants)==2:self.assertEqual(runner.validate_config(c)['variants'],variants)
            else:
                with self.assertRaises(runner.RunnerError):runner.validate_config(c)

    def test_binding_every_role_hash_symlink_and_array_refusal(self):
        for role in self.config['bindings']:
            c=copy.deepcopy(self.config);c['bindings'][role]['sha256']='0'*64
            with self.subTest(role=role),self.assertRaises(runner.RunnerError):runner.prepare(c)
        alias=self.root/'input-alias.json';alias.symlink_to(self.root/'source.json')
        c=copy.deepcopy(self.config);c['bindings']['source']['path']=str(alias)
        with self.assertRaises(runner.RunnerError):runner.prepare(c)
        array=self.root/'X_test.npy';array.write_bytes(b'not an array, never deserialize')
        c=copy.deepcopy(self.config);c['bindings']['source']={'path':str(array),'sha256':hashlib.sha256(array.read_bytes()).hexdigest()}
        with self.assertRaises(runner.RunnerError):runner.prepare(c)
        self.assertFalse(Path(c['output_root']).exists())

    def test_selection_accuracy_then_macro_f1(self):
        for mode,pairs,winner in [('accuracy',[(0.8,0.1),(0.7,0.9)],'SYNTHETIC-B'),
                                  ('f1',[(0.7,0.9),(0.7,0.8)],'SYNTHETIC-B')]:
            c=copy.deepcopy(self.config);c['output_root']=str(self.root/mode)
            iterator=iter(pairs)
            result=runner.run_synthetic(runner.prepare(c),lambda *args:signals(*next(iterator)),FakeClock())
            self.assertEqual(result['selected_synthetic_run_id'],winner)

    def test_cancel_before_start_and_invalid_clock_or_cancel_signal(self):
        for mode,clock,cancel,expected in [('cancel',FakeClock(),lambda:True,'CANCELLED'),
                ('clock',lambda:float('inf'),lambda:False,'INVALID_CLOCK'),
                ('signal',FakeClock(),lambda:1,'INVALID_CANCEL_SIGNAL')]:
            c=copy.deepcopy(self.config);c['output_root']=str(self.root/mode);calls=[]
            result=runner.run_synthetic(runner.prepare(c),lambda *args:calls.append(1),clock,cancel)
            self.assertEqual(result['status'],expected);self.assertEqual(calls,[])
            self.assertEqual(set(result['variant_states'].values()),{'NOT_STARTED'})

    def test_manifest_tamper_and_log_symlink_refused(self):
        for mode in ('manifest','logs'):
            c=copy.deepcopy(self.config);c['output_root']=str(self.root/mode)
            prepared=runner.prepare(c);calls=[]
            if mode=='manifest':(prepared.root/'manifest.json').write_text('{}')
            else:
                (prepared.root/'logs').rmdir()
                (prepared.root/'logs').symlink_to(self.root,target_is_directory=True)
            with self.assertRaises(runner.RunnerError):runner.run_synthetic(prepared,lambda *args:calls.append(1),FakeClock())
            self.assertEqual(calls,[])
            self.assertFalse((prepared.root/'completion.json').exists())

    def test_publication_collision_and_fsync_failure_preserve_old_bytes(self):
        path=self.root/'completion.json';path.write_bytes(b'old')
        with self.assertRaises(runner.RunnerError):runner.publish(path,{'new':True})
        self.assertEqual(path.read_bytes(),b'old')
        fresh=self.root/'manifest.json'
        with patch.object(runner.os,'fsync',side_effect=OSError('PRIVATE')):
            with self.assertRaises(runner.RunnerError):runner.publish(fresh,{'new':True})
        self.assertFalse(fresh.exists());self.assertEqual(path.read_bytes(),b'old')

    def test_strict_json_duplicate_and_nonfinite_rejected(self):
        for raw in (b'{"schema_version":1,"schema_version":1}',b'{"x":NaN}',b'{"x":Infinity}',b'{PRIVATE'):
            with self.subTest(raw=raw),self.assertRaises(runner.RunnerError):runner.parse_json(raw)

    def test_publication_interface_refuses_arbitrary_artifact_paths(self):
        for path in (self.root/'checkpoint.keras',runner.REPO_ROOT/'training/models/NEW-FORBIDDEN.json'):
            with self.subTest(path=path),patch.object(Path,'open',side_effect=AssertionError('writer must not be reached')):
                with self.assertRaises(runner.RunnerError):runner.publish(path,{'synthetic':True})

    def test_explicit_unchanged_no_face_model_and_structured_labels(self):
        c=copy.deepcopy(self.config)
        c['model_contract']={'architecture':'CNN-LSTM','seq_len':30,'features':258,
            'drop_face':True,'conv_filters':[64,128],'lstm_units':[128,64],'dense':128}
        c['bindings']['label_map']=dump(self.root/'structured-labels.json',
                                      {'0':{'id':0,'label':'SYNTHETIC','category':'SYNTHETIC'}})
        try:prepared=runner.prepare(c)
        except runner.RunnerError:prepared=None
        self.assertIsNotNone(prepared,'explicit unchanged model/structured label contract must prepare')
        for key,value in [('features',1662),('drop_face',False),('seq_len',30.0),
                          ('conv_filters',[64,True]),('lstm_units',[256,128]),('dense',True)]:
            invalid=copy.deepcopy(c);invalid['model_contract'][key]=value
            with self.subTest(key=key),self.assertRaises(runner.RunnerError):runner.validate_config(invalid)

    def test_protocol_original_clip_count_and_fraction_contract_rebound(self):
        ppath=Path(self.config['bindings']['protocol']['path'])
        fpath=Path(self.config['bindings']['freeze']['path'])
        protocol=json.loads(ppath.read_bytes());freeze=json.loads(fpath.read_bytes())
        for mode in ('too_few_originals','changed_fraction'):
            with self.subTest(mode=mode):
                p=copy.deepcopy(protocol);c=copy.deepcopy(self.config)
                c['output_root']=str(self.root/mode)
                if mode=='too_few_originals':
                    p['rows'].pop();p['n_validation']=1;p['class_counts']['0']['validation']=1
                    c['protocol']['validation_clips']=['0/val']
                else:p['validation_fraction']=0.3
                c['bindings']['protocol']=dump(ppath,p)
                f=copy.deepcopy(freeze);f['protocol_sha256']=c['bindings']['protocol']['sha256']
                c['bindings']['freeze']=dump(fpath,f)
                with self.assertRaises(runner.RunnerError):runner.prepare(c)

    def test_final_readback_fault_never_leaves_a_success_receipt(self):
        prepared=runner.prepare(self.config)
        real_verify=runner.verify_prepared
        def corrupt_during_final_readback(value,hashes=None):
            if (prepared.root/'completion.json').exists():
                (prepared.root/'logs/SYNTHETIC-B.result.json').write_text('tampered at final readback')
            return real_verify(value,hashes)
        with patch.object(runner,'verify_prepared',side_effect=corrupt_during_final_readback):
            with self.assertRaises(runner.RunnerError):
                runner.run_synthetic(prepared,lambda *args:signals(0.5,0.5),FakeClock())
        self.assertFalse((prepared.root/'completion.json').exists(), 'failed final readback must not leave success')
        self.assertTrue((prepared.root/'execution.json').exists())

    def test_synthetic_stop_exception_text_never_echoed(self):
        prepared=runner.prepare(self.config)
        def execute(*args):raise runner._Stop('PRIVATE_UNTRUSTED_REASON')
        result=runner.run_synthetic(prepared,execute,FakeClock())
        self.assertEqual(result['status'],'FAILED')
        self.assertNotIn('PRIVATE', ''.join(p.read_text() for p in prepared.root.rglob('*.json')))

    def test_cli_prepares_and_synthetic_demo_only(self):
        for mode in ('prepare','dry-run'):
            c=copy.deepcopy(self.config);c['output_root']=str(self.root/mode)
            path=self.root/(mode+'.json');dump(path,c)
            out=io.StringIO()
            with redirect_stdout(out):code=runner.main([mode,'--config',str(path)])
            self.assertTrue((Path(c['output_root'])/'manifest.json').is_file(), 'CLI must really prepare')
            self.assertEqual(code,0)
            result=json.loads(out.getvalue())
            self.assertEqual(result['status'],'PREPARED' if mode=='prepare' else 'SYNTHETIC_COMPLETE')
            self.assertFalse(result['training_authorized'])
            self.assertNotIn(str(path),out.getvalue())

    def test_cli_training_arbitrary_command_invalid_and_safe_errors(self):
        for args in (['execute'],['train','PRIVATE'],['execute','--command','PRIVATE'],
                     ['PRIVATE'],['prepare','--command','PRIVATE']):
            out=io.StringIO()
            with redirect_stdout(out):code=runner.main(args)
            self.assertEqual(code,3 if args[0] in ('train','execute') else 2)
            payload=json.loads(out.getvalue())
            self.assertEqual(payload['code'],'TRAINING_NOT_AUTHORIZED' if code==3 else 'INVALID_REQUEST')
            self.assertNotIn('PRIVATE',out.getvalue())
        with self.assertRaisesRegex(runner.RunnerError,'^TRAINING_NOT_AUTHORIZED$'):
            runner.execute_training(executor=lambda:self.fail('must not execute'))
        path=self.root/'invalid.json';path.write_text('{PRIVATE')
        out=io.StringIO()
        with redirect_stdout(out):code=runner.main(['prepare','--config',str(path)])
        self.assertEqual(code,2)
        self.assertNotIn('PRIVATE',out.getvalue())
        self.assertFalse(Path(self.config['output_root']).exists())

    def test_synthetic_order_ties_immutable_request_and_no_retry(self):
        prepared=runner.prepare(self.config)
        clock=FakeClock(); seen=[]; active=[]
        def execute(request, control):
            self.assertFalse(active);active.append(request.run_id)
            self.assertTrue(request.synthetic_only)
            with self.assertRaises((AttributeError, TypeError)):request.run_id='mutated'
            self.assertFalse(hasattr(request,'output_root'))
            seen.append(request.run_id);clock.advance(1);control.checkpoint()
            active.pop()
            return signals(0.7,0.6)
        result=runner.run_synthetic(prepared, execute, clock)
        self.assertIsNotNone(result, 'synthetic execution must publish checked completion')
        self.assertEqual(result['status'],'SYNTHETIC_COMPLETE')
        self.assertEqual(result['selected_synthetic_run_id'],'SYNTHETIC-A')
        self.assertEqual(seen,['SYNTHETIC-B','SYNTHETIC-A'])
        self.assertFalse(active)
        root=Path(self.config['output_root'])
        self.assertEqual(json.loads((root/'completion.json').read_text()),result)
        for path,h in result['output_hashes'].items():
            self.assertEqual(hashlib.sha256((root/path).read_bytes()).hexdigest(),h)
        with self.assertRaises(runner.RunnerError):runner.run_synthetic(prepared,execute,clock)
        self.assertEqual(len(seen),2)

    def test_synthetic_stop_conditions_and_safe_incomplete_logs(self):
        scenarios=['timeout','total','failure','interrupt','cancel','badmetric','boolmetric','nanmetric','extra','backward','forbidden']
        for mode in scenarios:
            with self.subTest(mode=mode):
                c=copy.deepcopy(self.config);c['output_root']=str(self.root/mode)
                if mode=='total':c['budget']['max_total_seconds']=10
                prepared=runner.prepare(c);clock=FakeClock();seen=[];cancel=[False]
                sentinel=self.root/'protected-sentinel';sentinel.write_bytes(b'UNCHANGED')
                def execute(request,control):
                    seen.append(request.run_id)
                    if mode=='timeout':clock.advance(10)
                    if mode=='total':clock.advance(6)
                    if mode=='failure':raise RuntimeError('PRIVATE DO NOT ECHO')
                    if mode=='interrupt':raise KeyboardInterrupt('PRIVATE DO NOT ECHO')
                    if mode=='cancel':cancel[0]=True
                    if mode=='backward':clock.value=-1
                    if mode=='forbidden':control.write_file('../protected-sentinel','PRIVATE')
                    if mode=='badmetric':return signals(1.1,0.5)
                    if mode=='boolmetric':return signals(True,0.5)
                    if mode=='nanmetric':return signals(float('nan'),0.5)
                    if mode=='extra':return dict(signals(0.5,0.5),test_score=0.9)
                    return signals(0.7,0.6)
                result=runner.run_synthetic(prepared,execute,clock,lambda:cancel[0])
                self.assertIsNotNone(result,'stop must be recorded, not silently ignored')
                expected={'timeout':'TIMEOUT','total':'TIMEOUT','failure':'FAILED','interrupt':'INTERRUPTED',
                          'cancel':'CANCELLED','badmetric':'INVALID_METRICS','boolmetric':'INVALID_METRICS',
                          'nanmetric':'INVALID_METRICS','extra':'INVALID_METRICS','backward':'INVALID_CLOCK','forbidden':'FAILED'}[mode]
                self.assertEqual(result['status'],expected)
                self.assertIsNone(result['selected_synthetic_run_id'])
                self.assertFalse(result['success'])
                self.assertEqual(len(seen),2 if mode=='total' else 1)
                self.assertEqual(sentinel.read_bytes(),b'UNCHANGED')
                self.assertNotIn('PRIVATE', ''.join(p.read_text() for p in Path(c['output_root']).rglob('*.json')))

    def test_synthetic_input_and_manifest_change_fail_before_executor(self):
        prepared=runner.prepare(self.config);called=[]
        Path(self.config['bindings']['source']['path']).write_text('changed')
        with self.assertRaises(runner.RunnerError):runner.run_synthetic(prepared,lambda *args:called.append(1),FakeClock())
        self.assertEqual(called,[])
        self.assertFalse((prepared.root/'completion.json').exists())

    def test_synthetic_output_tamper_has_no_success_receipt(self):
        prepared=runner.prepare(self.config);clock=FakeClock();seen=[]
        def execute(request,control):
            seen.append(request.run_id)
            if len(seen)==2:
                (prepared.root/'logs/SYNTHETIC-B.result.json').write_text('tampered')
            return signals(0.7,0.6)
        with self.assertRaises(runner.RunnerError):runner.run_synthetic(prepared,execute,clock)
        self.assertFalse((prepared.root/'completion.json').exists())

    def test_prepare_exclusive_binding_and_immutable_snapshot(self):
        prepared = runner.prepare(self.config)
        self.assertIsNotNone(prepared, 'preparation must publish an immutable manifest')
        root = Path(self.config['output_root'])
        manifest = json.loads((root/'manifest.json').read_text())
        self.assertEqual(manifest['config'], self.config)
        self.assertEqual(manifest['config_sha256'], hashlib.sha256(runner.canonical(self.config)).hexdigest())
        self.assertTrue((root/'logs').is_dir())
        self.config['variants'][0]['value'] = 0.9
        self.assertEqual(json.loads(prepared.config_bytes)['variants'][0]['value'], 0.4)
        before = {p.name:p.read_bytes() for p in root.iterdir() if p.is_file()}
        with self.assertRaises(runner.RunnerError): runner.prepare(self.config)
        self.assertEqual(before, {p.name:p.read_bytes() for p in root.iterdir() if p.is_file()})

    def test_prepare_refuses_unsafe_roots_and_changed_bindings(self):
        bad_roots = [str(runner.REPO_ROOT/'training/models/forbidden'),
                     str(self.root/'..'/'escape'), str(Path.home()/'Library/Application Support/kumpas/forbidden')]
        target=self.root/'target'; target.mkdir()
        link=self.root/'alias';link.symlink_to(target, target_is_directory=True)
        bad_roots += [str(link/'campaign'), str(self.root)]
        for path in bad_roots:
            c=copy.deepcopy(self.config);c['output_root']=path
            with self.subTest(path=path), self.assertRaises(runner.RunnerError): runner.prepare(c)
        Path(self.config['bindings']['source']['path']).write_text('changed')
        with self.assertRaises(runner.RunnerError): runner.prepare(self.config)
        self.assertFalse(Path(self.config['output_root']).exists())

    def test_prepare_protocol_semantics_rebound_hashes(self):
        for role,mutate in [('protocol', lambda p:p['rows'][1].update(clip='0/fit')),
                            ('protocol', lambda p:p['rows'][1].update(partition='fit')),
                            ('protocol', lambda p:p.update(n_fit_original=True)),
                            ('protocol', lambda p:p.update(n_validation=True)),
                            ('freeze',lambda p:p.update(protocol_sha256='e'*64)),
                            ('freeze',lambda p:p.update(best_val_accuracy=True)),
                            ('label_map',lambda p:p.update(human_score=0.9))]:
            with self.subTest(role=role):
                path=Path(self.config['bindings'][role]['path']); old=path.read_bytes()
                payload=json.loads(old);mutate(payload)
                c=copy.deepcopy(self.config);c['bindings'][role]=dump(path,payload)
                freeze_path=Path(c['bindings']['freeze']['path']);freeze_old=freeze_path.read_bytes()
                if role=='protocol':
                    freeze=json.loads(freeze_old);freeze['protocol_sha256']=c['bindings']['protocol']['sha256']
                    c['bindings']['freeze']=dump(freeze_path,freeze)
                with self.assertRaises(runner.RunnerError):runner.prepare(c)
                path.write_bytes(old)
                if role=='protocol':freeze_path.write_bytes(freeze_old)
        self.assertFalse(Path(self.config['output_root']).exists())

    def test_config_schema_authorization_numeric_and_selection(self):
        self.assertIsNotNone(runner.validate_config(self.config))
        mutations = [lambda c:c.update(training_authorized=True),
                     lambda c:c.update(partition='test'),
                     lambda c:c.update(human_score='probability'),
                     lambda c:c.update(selection_method='highest test accuracy'),
                     lambda c:c.update(schema_version=1.0),
                     lambda c:c['budget'].update(max_epochs=True),
                     lambda c:c['budget'].update(max_total_seconds=float('nan')),
                     lambda c:c['budget'].update(max_experiments=1),
                     lambda c:c['variants'][0].update(value=True),
                     lambda c:c['variants'][0].update(value=float('inf')),
                     lambda c:c['variants'][0].update(factor='test_score'),
                     lambda c:c['variants'][0].update(value=0.3),
                     lambda c:c['bindings']['source'].update(sha256='A'*64)]
        for mutate in mutations:
            c=copy.deepcopy(self.config);mutate(c)
            with self.subTest(config=c), self.assertRaises(runner.RunnerError):
                runner.validate_config(c)
