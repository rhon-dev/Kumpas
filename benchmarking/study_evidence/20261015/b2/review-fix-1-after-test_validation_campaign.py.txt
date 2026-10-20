"""Synthetic public-boundary regressions; never opens real test arrays."""
import importlib.util
import sys
from pathlib import Path
import unittest

MODELS = Path(__file__).resolve().parents[1] / 'models'
sys.path.insert(0, str(MODELS))

def api(name):
    # Missing feature is a behaviorally permissive boundary, not an import RED.
    if importlib.util.find_spec('validation_campaign') is None:
        return lambda *a, **kw: None
    import validation_campaign
    return getattr(validation_campaign, name, lambda *a, **kw: None)

class CampaignTests(unittest.TestCase):
    def test_metric_boundary_rejects_non_numeric_and_nonfinite_before_ranking(self):
        for value in [True, '0.96', float('nan'), float('inf'), -0.1, 1.1, None, {}, 10**1000]:
            with self.subTest(value_type=type(value).__name__):
                with self.assertRaisesRegex(ValueError, '^INVALID_METRICS$'):
                    api('validate_metrics')({'accuracy':value,'macro_f1':0.8,'class_count':50},50)
        self.assertIsNone(api('validate_metrics')({'accuracy':0.96,'macro_f1':0.9,'class_count':50},50))
        for count in [True, 50.0, '50', 49]:
            with self.assertRaisesRegex(ValueError, '^INVALID_METRICS$'):
                api('validate_metrics')({'accuracy':0.96,'macro_f1':0.9,'class_count':count},50)

class InputTests(unittest.TestCase):
    def setUp(self, originals_per_class=4):
        import tempfile, json, numpy as np
        from evaluation_protocol import build_protocol, sha256
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name); seq = root/'sequences'; seq.mkdir()
        self.seq = seq; self.protocol = seq/'evaluation-v1'
        count = 2*originals_per_class
        np.save(seq/'X_train.npy', np.arange(count*30*1662,dtype=np.float32).reshape(count,30,1662)/100000)
        np.save(seq/'y_train.npy', np.array([0]*originals_per_class+[1]*originals_per_class))
        (seq/'clips_train.json').write_text(json.dumps([f'clips_{i//originals_per_class}_{i%originals_per_class}.npz' for i in range(count)]))
        (seq/'clips_test.json').write_text(json.dumps(['clips_0_99.npz']))
        (seq/'label_map.json').write_text(json.dumps({str(i):{'id':i,'label':str(i),'category':'TEST'} for i in range(2)}))
        (root/'labels.csv').write_text('id,label,category\n0,0,TEST\n1,1,TEST\n')
        (root/'train.csv').write_text('vid_path,id_label,label,category\n'+''.join(f'clips/{i//originals_per_class}/{i%originals_per_class}.MOV,{i//originals_per_class},{i//originals_per_class},TEST\n' for i in range(count)))
        build_protocol(seq,self.protocol,factor=1)
        for name in ['checkpoint.keras','candidate.tflite']: (root/name).write_bytes(b'synthetic-not-a-model')
        manifest = json.loads((self.protocol/'manifest.json').read_text())
        freeze = {'run_id':'frozen','checkpoint':str(root/'checkpoint.keras'),'checkpoint_sha256':sha256(root/'checkpoint.keras'),
                  'protocol_sha256':sha256(self.protocol/'manifest.json'),'selection_method':'validation only','test_status':'exploratory',
                  'best_val_accuracy':0.75,'best_val_macro_f1':0.7}
        (root/'selection.json').write_text(json.dumps(freeze))
        provenance = {'run_id':'frozen','checkpoint_sha256':freeze['checkpoint_sha256'],'selection_sha256':sha256(root/'selection.json'),
                      'protocol_sha256':freeze['protocol_sha256'],'label_map_sha256':sha256(seq/'label_map.json'),
                      'tflite_sha256':sha256(root/'candidate.tflite'),'filename':'candidate.tflite','deployed':False}
        (root/'provenance.json').write_text(json.dumps(provenance))
        paths = {role:str(seq/name) for role,name in [('original_X','X_train.npy'),('original_y','y_train.npy'),('clips_train','clips_train.json'),('clips_test','clips_test.json'),('label_map','label_map.json')]}
        paths.update({role:str(self.protocol/name) for role,name in [('fit_X','X_fit.npy'),('fit_y','y_fit.npy'),('val_X','X_val.npy'),('val_y','y_val.npy'),('manifest','manifest.json'),('augmentations','augmentations.json')]})
        paths.update({role:str(root/name) for role,name in [('checkpoint','checkpoint.keras'),('freeze','selection.json'),('candidate','candidate.tflite'),('provenance','provenance.json'),('source_labels','labels.csv'),('source_train_csv','train.csv')]})
        self.config = {'schema':1,'class_count':2,'validation_count':4,'paths':paths,'sha256':{k:sha256(Path(v)) for k,v in paths.items()},
                       'ordered_clips':[r['clip'] for r in manifest['rows'] if r['partition']=='validation']}

    def _rebound_metadata(self, role, change):
        """Temporarily edit synthetic JSON and rebind the complete digest graph."""
        import copy, json
        from contextlib import contextmanager
        from evaluation_protocol import sha256
        @contextmanager
        def edited():
            saved = {k:Path(self.config['paths'][k]).read_bytes()
                     for k in ('manifest','freeze','provenance')}
            hashes = copy.deepcopy(self.config['sha256'])
            def write(key, value):
                path = Path(self.config['paths'][key])
                path.write_text(json.dumps(value, allow_nan=False))
                self.config['sha256'][key] = sha256(path)
            try:
                value = json.loads(saved[role]); change(value); write(role, value)
                freeze = json.loads(Path(self.config['paths']['freeze']).read_text())
                freeze['protocol_sha256'] = self.config['sha256']['manifest']
                write('freeze', freeze)
                provenance = json.loads(saved['provenance'])
                provenance.update(run_id=freeze['run_id'],
                                  protocol_sha256=self.config['sha256']['manifest'],
                                  selection_sha256=self.config['sha256']['freeze'])
                write('provenance', provenance)
                yield
            finally:
                for key, content in saved.items():
                    Path(self.config['paths'][key]).write_bytes(content)
                self.config['sha256'] = hashes
        return edited()

    def _assert_cli_schema_rejection(self):
        import io, json, uuid
        from contextlib import redirect_stdout
        from unittest.mock import patch
        from evaluation_protocol import sha256
        root = Path(self.tmp.name); path = root/'cli-config.json'
        path.write_text(json.dumps(self.config, allow_nan=False))
        for incomplete in (False, True):
            output = root/('rejected-'+uuid.uuid4().hex)
            args = ['--config',str(path),'--config-sha256',sha256(path),
                    '--output-root',str(root),'--output',str(output),
                    '--landmark-dir',str(root/'unused-npz'),'--raw-dir',str(root/'unused-video')]
            if incomplete:
                args.append('--incomplete-source-diagnostics')
            stream = io.StringIO()
            with patch('validation_campaign.clip_metadata', side_effect=ValueError('INVALID_CLIP_METADATA')) as metadata, \
                    patch('validation_campaign.predict_frozen') as prediction, redirect_stdout(stream):
                code = api('main')(args)
            self.assertEqual(code, 2)
            self.assertEqual(json.loads(stream.getvalue()), {'error':'INVALID_CONFIG','status':'INCOMPLETE'})
            metadata.assert_not_called(); prediction.assert_not_called()
            self.assertFalse(output.exists())

    def test_selection_identity_policy_types_rejected_with_rebound_hashes(self):
        self.assertIsInstance(api('validate_inputs')(self.config), dict)
        for field in ('run_id','selection_method','test_status'):
            for value in ({'unexpected':'object'}, ['validation'], True, 1, 1.0, None, '', '   '):
                with self._rebound_metadata('freeze', lambda j:j.update({field:value})):
                    with self.subTest(boundary='validate_inputs',field=field,value=value):
                        with self.assertRaisesRegex(ValueError, '^INVALID_INPUTS$'):
                            api('validate_inputs')(self.config)
                    with self.subTest(boundary='CLI',field=field,value=value):
                        self._assert_cli_schema_rejection()
        # Existing historical prose and non-UUID run identity remain supported.
        historical = {'run_id':'20260930_153819_protocol_v1_no_face_baseline',
                      'selection_method':'highest validation accuracy; macro-F1 then run ID tie break',
                      'test_status':'exploratory: existing FSL-105 test was consulted by historical runs'}
        with self._rebound_metadata('freeze', lambda j:j.update(historical)):
            self.assertEqual(api('validate_inputs')(self.config)['freeze']['run_id'], historical['run_id'])
        self.assertIsInstance(api('validate_inputs')(self.config), dict)

    def test_protocol_counts_require_exact_integers_with_rebound_hashes(self):
        import json
        # Three originals/class gives a genuine count of1: True==1 must not pass.
        fixture = InputTests(); fixture.setUp(originals_per_class=3)
        self.addCleanup(fixture.doCleanups)
        self.assertIsInstance(api('validate_inputs')(fixture.config), dict)
        manifest = json.loads(Path(fixture.config['paths']['manifest']).read_text())
        paths = [('n_fit_original',), ('n_validation',)]
        paths += [('class_counts',cid,partition) for cid,counts in manifest['class_counts'].items()
                  for partition in counts]
        for keys in paths:
            parent = manifest
            for key in keys[:-1]:
                parent = parent[key]
            original = parent[keys[-1]]
            for value in (float(original), True, False, str(original), None, {}, [], -1, original+1):
                def change(value_json):
                    target = value_json
                    for key in keys[:-1]:
                        target = target[key]
                    target[keys[-1]] = value
                with fixture._rebound_metadata('manifest', change):
                    with self.subTest(boundary='validate_inputs',keys=keys,value=value):
                        with self.assertRaisesRegex(ValueError, '^INVALID_INPUTS$'):
                            api('validate_inputs')(fixture.config)
                    with self.subTest(boundary='CLI',keys=keys,value=value):
                        fixture._assert_cli_schema_rejection()
        # Restored exact integers retain original reconstruction/numeric semantics.
        self.assertIsInstance(api('validate_inputs')(fixture.config), dict)

    def test_reject_shape_compatible_validation_tampering_even_when_current_hash_rebound(self):
        import numpy as np
        from evaluation_protocol import sha256
        for role in ['val_X','val_y']:
            path = Path(self.config['paths'][role]); original = path.read_bytes()
            array = np.load(path); array.flat[0] += 1; np.save(path,array)
            self.config['sha256'][role] = sha256(path)
            with self.assertRaisesRegex(ValueError, '^INVALID_INPUTS$'):
                api('validate_inputs')(self.config)
            path.write_bytes(original); self.config['sha256'][role]=sha256(path)

    def test_identity_graph_rejects_tampering_and_malformed_metadata(self):
        import copy, json, numpy as np
        from evaluation_protocol import sha256
        self.assertIsInstance(api('validate_inputs')(self.config),dict)
        # Unrebound byte changes must fail for every declared input role.
        for role, filename in self.config['paths'].items():
            path=Path(filename); saved=path.read_bytes(); path.write_bytes(saved+b' ')
            with self.subTest(role=role), self.assertRaisesRegex(ValueError,'^INVALID_INPUTS$'):
                api('validate_inputs')(self.config)
            path.write_bytes(saved)
        mutations = [lambda c:c.update(schema=True),lambda c:c.update(schema=1.0),
                     lambda c:c.update(class_count=True),lambda c:c.update(validation_count=3),
                     lambda c:c['ordered_clips'].reverse(),lambda c:c.update(extra='unsafe'),
                     lambda c:c['sha256'].update(val_X='bad')]
        for change in mutations:
            c=copy.deepcopy(self.config); change(c)
            with self.assertRaisesRegex(ValueError,'^INVALID_INPUTS$'): api('validate_inputs')(c)
        edits = [('label_map',lambda j:j['0'].update(id=True)),
                 ('label_map',lambda j:j['0'].update(label='wrong')),
                 ('label_map',lambda j:j.update({'2':j['1']})),
                 ('freeze',lambda j:j.update(checkpoint_sha256='0'*64)),
                 ('freeze',lambda j:j.update(best_val_accuracy=True)),
                 ('manifest',lambda j:j['rows'][0].update(index=True)),
                 ('manifest',lambda j:j['rows'][0].update(partition='validation')),
                 ('provenance',lambda j:j.update(selection_sha256='0'*64)),
                 ('augmentations',lambda j:j[0].update(source_clip='clips_999_0.npz'))]
        for role,change in edits:
            c=copy.deepcopy(self.config); path=Path(c['paths'][role]); saved=path.read_bytes()
            data=json.loads(saved); change(data); path.write_text(json.dumps(data)); c['sha256'][role]=sha256(path)
            with self.subTest(role=role), self.assertRaisesRegex(ValueError,'^INVALID_INPUTS$'):
                api('validate_inputs')(c)
            path.write_bytes(saved)
        for role in ['fit_X','val_X']:
            c=copy.deepcopy(self.config); path=Path(c['paths'][role]); saved=path.read_bytes()
            arr=np.load(path); arr.flat[0]=np.nan; np.save(path,arr); c['sha256'][role]=sha256(path)
            with self.assertRaisesRegex(ValueError,'^INVALID_INPUTS$'): api('validate_inputs')(c)
            path.write_bytes(saved)
        path=Path(self.config['paths']['checkpoint']); link=path.parent/'link.keras'; link.symlink_to(path)
        c=copy.deepcopy(self.config); c['paths']['checkpoint']=str(link)
        with self.assertRaisesRegex(ValueError,'^INVALID_INPUTS$'): api('validate_inputs')(c)

    def test_campaign_refuses_existing_escape_symlink_and_invalid_input_without_success(self):
        root=Path(self.tmp.name); outputs=root/'outputs'; outputs.mkdir()
        existing=outputs/'existing'; existing.mkdir(); (existing/'sentinel').write_text('keep')
        link=outputs/'linked'; link.symlink_to(existing,target_is_directory=True)
        for output in [existing,link,root/'escape',outputs/'..'/'escape']:
            with self.subTest(output=output.name), self.assertRaisesRegex(ValueError,'^INVALID_OUTPUT$'):
                api('run_campaign')(self.config,str(outputs),str(output),str(root/'landmarks'),str(root/'raw'))
        self.assertEqual((existing/'sentinel').read_text(),'keep')
        import copy
        bad=copy.deepcopy(self.config); bad['sha256']['candidate']='0'*64
        with self.assertRaisesRegex(ValueError,'^INVALID_INPUTS$'):
            api('run_campaign')(bad,str(outputs),str(outputs/'failed'),str(root/'landmarks'),str(root/'raw'))
        self.assertFalse((outputs/'failed'/'manifest.json').exists())

    def test_metadata_rejects_nonfinite_and_binds_frames_sampling_and_missingness(self):
        import numpy as np
        root=Path(self.tmp.name); landmarks=root/'landmarks'; landmarks.mkdir(); raw=root/'raw'; (raw/'0').mkdir(parents=True)
        video=raw/'0'/'0.MOV'; video.write_bytes(b'synthetic-video-not-decoded')
        path=landmarks/'clips_0_0.npz'; array=np.zeros((40,1662),dtype=np.float32)
        array[:,11*4:11*4+3]=[0,1,0]; array[:,12*4:12*4+3]=[0,1,0]
        def save(**overrides):
            values=dict(landmarks=array,class_id=np.array(0),split=np.array('train'),fps=np.array(30.),brightness=np.array(1.),detection_rates=np.array([1.,0.,0.,0.]))
            values.update(overrides); np.savez(path,**values)
        row={'clip':path.name,'index':0,'class_id':0,'partition':'validation'}
        save(landmarks=np.full((40,1662),np.nan,dtype=np.float32))
        with self.assertRaisesRegex(ValueError,'^INVALID_CLIP_METADATA$'):
            api('clip_metadata')(row,self.config,str(landmarks),str(raw))
        save(); result=api('clip_metadata')(row,self.config,str(landmarks),str(raw))
        self.assertEqual(result['sequence_frames'],40)
        self.assertEqual(len(result['sample_indices']),30)
        self.assertEqual(result['sampled_presence']['left_hand'],0)
        self.assertEqual(len(result['landmark_frame_sha256']),30)
        for overrides in [dict(class_id=np.array(True)),dict(detection_rates=np.array([1.,0.,0.,np.inf])),dict(split=np.array('test')),
                          dict(fps=np.array(True)),dict(landmarks=np.ones((40,258)))]:
            save(**overrides)
            with self.assertRaisesRegex(ValueError,'^INVALID_CLIP_METADATA$'): api('clip_metadata')(row,self.config,str(landmarks),str(raw))
        # Rebound current CSV must still agree with source class/clip identity.
        csv_path=root/'train.csv'; csv_path.write_text('vid_path,id_label,label,category\nclips\\\\0\\\\0.MOV,1,1,TEST\n')
        self.config['paths']['source_train_csv']=str(csv_path)
        save()
        with self.assertRaisesRegex(ValueError,'^INVALID_CLIP_METADATA$'): api('clip_metadata')(row,self.config,str(landmarks),str(raw))

    def test_campaign_publishes_only_verified_outputs_and_retains_failures(self):
        import json, numpy as np
        from evaluation_protocol import sha256
        root=Path(self.tmp.name); outputs=root/'outputs'; outputs.mkdir(); landmarks=root/'landmarks'; landmarks.mkdir(); raw=root/'raw'; raw.mkdir()
        for clip in self.config['ordered_clips']:
            cid,idx=map(int,clip.removeprefix('clips_').removesuffix('.npz').split('_'))
            (raw/str(cid)).mkdir(exist_ok=True); (raw/str(cid)/(str(idx)+'.MOV')).write_bytes(b'synthetic')
            np.savez(landmarks/clip,landmarks=np.zeros((40,1662),dtype=np.float32),class_id=np.array(cid),split=np.array('train'),
                     fps=np.array(30.),brightness=np.array(1.),detection_rates=np.zeros(4,dtype=float))
        calls=[]
        def predictor(config,inputs,emit):
            self.assertTrue((outputs/'good'/'campaign.json').is_file())
            self.assertFalse((outputs/'good'/'manifest.json').exists())
            calls.append('synthetic')
            a=np.array([[.8,.2] if y==0 else [.2,.8] for y in inputs['y']],dtype=np.float32)
            return a,a.copy(),{'backend':'synthetic-test-only'}
        result=api('run_campaign')(self.config,str(outputs),str(outputs/'good'),str(landmarks),str(raw),predictor=predictor)
        self.assertEqual(calls,['synthetic'])
        events=[json.loads(line) for line in (outputs/'good'/'events.jsonl').read_text().splitlines()]
        self.assertEqual([e['n'] for e in events if e['event']=='metadata_clip_complete'],[1,2,3,4])
        manifest=json.loads((outputs/'good'/'manifest.json').read_text())
        self.assertEqual(manifest['status'],'diagnostic_not_approved_for_promotion')
        self.assertEqual(manifest['n'],4)
        for name,digest in manifest['outputs'].items(): self.assertEqual(sha256(outputs/'good'/name),digest)
        records=[json.loads(line) for line in (outputs/'good'/'clips.jsonl').read_text().splitlines()]
        self.assertEqual([r['clip'] for r in records],self.config['ordered_clips'])
        self.assertEqual(result['keras']['correct'],4)
        def failing(config,inputs,emit): raise RuntimeError('private raw payload must not be echoed')
        with self.assertRaisesRegex(ValueError,'^INFERENCE_FAILED$'):
            api('run_campaign')(self.config,str(outputs),str(outputs/'failed'),str(landmarks),str(raw),predictor=failing)
        self.assertTrue((outputs/'failed'/'INCOMPLETE.json').exists())
        self.assertFalse((outputs/'failed'/'manifest.json').exists())
        self.assertNotIn('private', (outputs/'failed'/'failure.json').read_text())
        def unavailable(*args,**kwargs): raise ValueError('SOURCE_NOT_RESIDENT')
        from unittest.mock import patch
        def partial_predictor(config,inputs,emit):
            return np.full((4,2),.5),np.full((4,2),.5),{'backend':'synthetic-test-only'}
        with patch('validation_campaign.clip_metadata',side_effect=unavailable):
            partial=api('run_incomplete_campaign')(self.config,str(outputs),str(outputs/'partial'),str(landmarks),str(raw),predictor=partial_predictor)
        self.assertIsInstance(partial,dict)
        self.assertEqual(partial['source_metadata_unavailable'],4)
        self.assertEqual(partial['status'],'INCOMPLETE_SOURCE_METADATA')
        self.assertFalse((outputs/'partial'/'manifest.json').exists())
        self.assertTrue((outputs/'partial'/'INCOMPLETE-manifest.json').exists())
        partial_records=[json.loads(line) for line in (outputs/'partial'/'clips.jsonl').read_text().splitlines()]
        self.assertEqual(len(partial_records),4)
        self.assertTrue(all('npz_sha256' not in row for row in partial_records))
        def tamper(config,inputs,emit):
            Path(config['paths']['candidate']).write_bytes(b'changed')
            return np.full((4,2),.5),np.full((4,2),.5),{}
        with self.assertRaisesRegex(ValueError,'^INVALID_INPUTS$'):
            api('run_campaign')(self.config,str(outputs),str(outputs/'tampered'),str(landmarks),str(raw),predictor=tamper)
        self.assertFalse((outputs/'tampered'/'manifest.json').exists())

class BackendTests(unittest.TestCase):
    def test_backend_uses_inference_only_then_existing_candidate_and_checks_shapes(self):
        import numpy as np, types
        from unittest.mock import patch
        events=[]; calls=[]
        class Model:
            input_shape=(None,30,258); output_shape=(None,2)
            def __call__(self,x,training):
                self.assertion=not training; calls.append(('keras',x.shape,training))
                return np.array([[.8,.2]],dtype=np.float32)
        model=Model()
        class Interpreter:
            def __init__(self,**kwargs): calls.append(('interpreter',kwargs))
            def allocate_tensors(self): pass
            def get_input_details(self): return [{'shape':np.array([1,30,258]),'dtype':np.float32,'index':0}]
            def get_output_details(self): return [{'shape':np.array([1,2]),'dtype':np.float32,'index':1}]
            def set_tensor(self,i,x): calls.append(('tflite',x.shape))
            def invoke(self): pass
            def get_tensor(self,i): return np.array([[.7,.3]],dtype=np.float32)
        def load(path,compile):
            self.assertFalse(compile); calls.append(('load',path)); return model
        tf=types.SimpleNamespace(__version__='synthetic',keras=types.SimpleNamespace(models=types.SimpleNamespace(load_model=load),
                backend=types.SimpleNamespace(clear_session=lambda:calls.append(('clear',)))),
                lite=types.SimpleNamespace(Interpreter=Interpreter),
                config=types.SimpleNamespace(threading=types.SimpleNamespace(set_intra_op_parallelism_threads=lambda n:None,set_inter_op_parallelism_threads=lambda n:None)))
        config={'paths':{'checkpoint':'frozen.keras','candidate':'already.tflite'},'class_count':2}
        inputs={'X':np.zeros((4,30,1662),dtype=np.float32),'y':np.array([0,1,0,1])}
        with patch.dict(sys.modules,{'tensorflow':tf}):
            result=api('predict_frozen')(config,inputs,events.append)
            self.assertIsInstance(result,tuple)
            a,b,runtime=result
            self.assertEqual(a.shape,(4,2)); self.assertEqual(b.shape,(4,2))
            self.assertEqual(sum(c[0]=='keras' for c in calls),4)
            self.assertEqual(sum(c[0]=='tflite' for c in calls),4)
            self.assertLess(calls.index(('clear',)),next(i for i,c in enumerate(calls) if c[0]=='interpreter'))
            model.output_shape=(None,3)
            with self.assertRaisesRegex(ValueError,'^MODEL_SHAPE_MISMATCH$'): api('predict_frozen')(config,inputs,events.append)

class ResidencyTests(unittest.TestCase):
    def test_dataless_sources_fail_before_a_blocking_content_read(self):
        from types import SimpleNamespace
        class CloudPlaceholder:
            def stat(self): return SimpleNamespace(st_flags=0x40000000)
        with self.assertRaisesRegex(ValueError,'^SOURCE_NOT_RESIDENT$'):
            api('assert_resident')(CloudPlaceholder())
        class Resident:
            def stat(self): return SimpleNamespace(st_flags=0)
        self.assertIsNone(api('assert_resident')(Resident()))

class CliTests(unittest.TestCase):
    def test_cli_requires_bound_strict_config_and_fixed_safe_errors(self):
        import tempfile,json,subprocess,hashlib
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); config=root/'config.json'
            base=[sys.executable,'-B','-E',str(MODELS/'validation_campaign.py'),'--config',str(config),'--config-sha256']
            tail=['--output-root',str(root),'--output',str(root/'new'),'--landmark-dir',str(root/'npz'),'--raw-dir',str(root/'raw')]
            for payload,digest in [('{"schema":1,"schema":1}',None),('{"private":"secret"}', '0'*64),('{"value":1e999}',None)]:
                config.write_text(payload)
                actual=digest or hashlib.sha256(config.read_bytes()).hexdigest()
                result=subprocess.run(base+[actual]+tail,capture_output=True,text=True)
                self.assertEqual(result.returncode,2)
                self.assertEqual(json.loads(result.stdout),{'error':'INVALID_CONFIG','status':'INCOMPLETE'})
                self.assertNotIn('secret',result.stdout+result.stderr)

class DiagnosticTests(unittest.TestCase):
    def test_diagnostics_all_classes_counts_and_conversion_drift(self):
        import numpy as np
        a=np.array([[.8,.1,.1],[.1,.8,.1],[.1,.8,.1]])
        b=np.array([[.7,.2,.1],[.1,.8,.1],[.8,.1,.1]])
        result=api('summarize')(a,b,np.array([0,1,2]),3)
        self.assertIsInstance(result,dict)
        self.assertEqual(result['keras']['correct'],2)
        self.assertEqual(result['candidate']['correct'],2)
        self.assertEqual(result['keras']['n'],3)
        self.assertEqual(len(result['keras']['per_class']),3)
        self.assertEqual(result['drift']['top1_disagreements'],1)
        self.assertAlmostEqual(result['drift']['max_absolute_probability_error'],.7)
        self.assertEqual(result['status'],'diagnostic_not_approved_for_promotion')
        with self.assertRaisesRegex(ValueError,'^INVALID_PROBABILITIES$'):
            api('summarize')(a,b[:2],np.array([0,1,2]),3)
        for y in [np.array([True,False,True]),np.array([0,1,3]),np.array([0.,1.,2.])]:
            with self.assertRaisesRegex(ValueError,'^INVALID_LABELS$'): api('summarize')(a,b,y,3)

class ProbabilityTests(unittest.TestCase):
    def test_probability_boundary_rejects_shape_type_and_nonfinite(self):
        import numpy as np
        valid = np.array([[0.2, 0.8]], dtype=np.float32)
        for bad in [np.array([[True, False]]), np.array([['0.2','0.8']]),
                    np.array([[float('nan'),0.8]]), np.array([[float('inf'),0.8]]),
                    np.array([[-0.2,1.2]]), np.array([[0.1,0.1]]),
                    np.array([0.2,0.8]), np.ones((1,3)), np.ones((2,2))]:
            with self.subTest(shape=bad.shape, dtype=str(bad.dtype)):
                with self.assertRaisesRegex(ValueError, '^INVALID_PROBABILITIES$'):
                    api('validate_probabilities')(bad,1,2)
        self.assertIsNone(api('validate_probabilities')(valid,1,2))

if __name__ == '__main__':
    unittest.main()
