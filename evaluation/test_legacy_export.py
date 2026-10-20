"""All fixtures are explicitly SYNTHETIC; no installed stores are accessed."""
import copy
import json
import unittest
from evaluation.legacy_export import validate_bytes

P = "00000000-0000-4000-8000-000000000001"
S = "00000000-0000-4000-8000-000000000002"

def fixture():
    return {"metadata": {"participant_id": P, "export_timestamp": "2026-10-18T10:00:00", "app_version": "SYNTHETIC", "device_model": "SYNTHETIC", "android_version": "SYNTHETIC"},
        "assessments": [{"id": 1, "participant_id": P, "type": "pre", "timestamp": 1,
            "responses": json.dumps({"fslConfidence": 1, "signsKnown": 2})},
            {"id": 2, "participant_id": P, "type": "post", "timestamp": 3,
            "responses": json.dumps({"fslConfidence": 3, "signsKnown": 4, "susScores": [5]*10, "openFeedback": "SYNTHETIC PRIVATE CANARY"})}],
        "sessions": [{"id": S, "participant_id": P, "started_at": 1, "ended_at": None,
            "attempt_count": 0, "signs_attempted": 0, "avg_match": 0.0, "duration_s": 0.0, "source": "app",
            "attempts": [{"id": 1, "session_id": S, "timestamp": 2, "target_class": 0, "target_label": "SYNTHETIC", "predicted_label": "SYNTHETIC PRIVATE CANARY", "predicted_confidence": 0.5, "recognized_as_target": 0, "overall_match": 0.5, "feedback_items": "[]"}]}],
        "summary": {"total_sessions": 1, "total_attempts": 1, "total_assessments": 2}}

def encode(x):
    return json.dumps(x).encode()

class LegacyTests(unittest.TestCase):
    def test_actual_encoded_shape_counts_and_privacy(self):
        result = validate_bytes(encode(fixture()))
        self.assertTrue(result["valid"], result)
        self.assertEqual(result["counts"], {"sessions": 1, "attempts": 1, "assessments": 2})
        for private in (P, S, "PRIVATE CANARY", "device_model", "responses"):
            self.assertNotIn(private, json.dumps(result))

    def test_strict_encoded_and_relational_rejections(self):
        cases = []
        def case(code, change):
            x=fixture(); change(x); cases.append((code, encode(x)))
        case('RELATION', lambda x: x['assessments'][0].update(participant_id=S))
        case('RELATION', lambda x: x['sessions'][0]['attempts'][0].update(session_id=P))
        case('DUPLICATE_ID', lambda x: x['assessments'].append(copy.deepcopy(x['assessments'][0])))
        case('DUPLICATE_ID', lambda x: x['sessions'].append(copy.deepcopy(x['sessions'][0])))
        case('DUPLICATE_ID', lambda x: x['sessions'][0]['attempts'].append(copy.deepcopy(x['sessions'][0]['attempts'][0])))
        case('COUNT_MISMATCH', lambda x: x['summary'].update(total_attempts=9))
        case('TYPE', lambda x: x['summary'].update(total_attempts=True))
        case('TYPE', lambda x: x['assessments'][0].update(id=1.0))
        case('UUID', lambda x: x['metadata'].update(participant_id='SYNTHETIC PRIVATE CANARY'))
        case('PHASE', lambda x: x['assessments'][0].update(type='SYNTHETIC PRIVATE CANARY'))
        case('TYPE', lambda x: x['assessments'][0].update(responses={'fslConfidence':1}))
        case('JSON_INVALID', lambda x: x['assessments'][0].update(responses='{"fslConfidence":1,"fslConfidence":2}'))
        case('JSON_INVALID', lambda x: x['assessments'][0].update(responses='{"fslConfidence":NaN}'))
        case('RANGE', lambda x: x['assessments'][0].update(responses='{"fslConfidence":0,"signsKnown":1}'))
        case('TYPE', lambda x: x['assessments'][0].update(responses='{"fslConfidence":true,"signsKnown":1}'))
        case('REQUIRED', lambda x: x['assessments'][0].update(responses='{"signsKnown":1}'))
        case('REQUIRED', lambda x: x['assessments'][1].update(responses='{"fslConfidence":1,"signsKnown":1}'))
        case('RANGE', lambda x: x['assessments'][1].update(responses=json.dumps({'fslConfidence':1,'signsKnown':1,'susScores':[1]*9})))
        case('ENUM', lambda x: x['assessments'][0].update(responses=json.dumps({'fslConfidence':1,'signsKnown':1,'gender':'SYNTHETIC PRIVATE CANARY'})))
        case('JSON_INVALID', lambda x: x['sessions'][0]['attempts'][0].update(feedback_items='[NaN]'))
        case('RANGE', lambda x: x['sessions'][0]['attempts'][0].update(predicted_confidence=2))
        case('TYPE', lambda x: x['sessions'][0]['attempts'][0].update(recognized_as_target=True))
        cases += [('JSON_INVALID', b'{"x":1,"x":2}'), ('JSON_INVALID', b'NaN'), ('JSON_INVALID', b'{"x":1e999}'), ('SHAPE', b'[]')]
        for code, data in cases:
            with self.subTest(code=code):
                result=validate_bytes(data)
                self.assertFalse(result['valid'])
                self.assertIn(code, [d['code'] for d in result['diagnostics']])
                self.assertNotIn('PRIVATE CANARY', json.dumps(result))
                self.assertNotIn(P, json.dumps(result))

    def test_closed_session_counts_are_reconciled_but_active_counts_may_lag(self):
        x=fixture()
        self.assertTrue(validate_bytes(encode(x))['valid'])
        x['sessions'][0]['ended_at']=4
        result=validate_bytes(encode(x))
        self.assertFalse(result['valid'])
        self.assertEqual(result['diagnostics'][0]['code'],'SESSION_COUNT_MISMATCH')
        x['sessions'][0].update(attempt_count=1,signs_attempted=1)
        self.assertTrue(validate_bytes(encode(x))['valid'])

    def test_exact_types_requiredness_and_optional_domains_matrix(self):
        invalid_values=[None,True,False,1.0,'1',[],{}]
        paths=[('assessments',0,'id'),('assessments',0,'timestamp'),('sessions',0,'attempt_count'),('sessions',0,'signs_attempted'),('sessions',0,'started_at'),('sessions',0,'attempts',0,'id'),('sessions',0,'attempts',0,'target_class'),('sessions',0,'attempts',0,'timestamp'),('sessions',0,'attempts',0,'recognized_as_target'),('summary','total_sessions')]
        for path in paths:
            for bad in invalid_values:
                x=fixture(); owner=x
                for part in path[:-1]: owner=owner[part]
                owner[path[-1]]=bad
                with self.subTest(path=path,bad=bad): self.assertFalse(validate_bytes(encode(x))['valid'])
        for field in ('fslConfidence','signsKnown'):
            for bad in [None,True,1.0,'1',0,6,[],{}]:
                x=fixture(); values={'fslConfidence':1,'signsKnown':1}; values[field]=bad
                x['assessments'][0]['responses']=json.dumps(values)
                self.assertFalse(validate_bytes(encode(x))['valid'])
        for field,good in [('ageGroup','18-25'),('gender','Prefer not to say')]:
            x=fixture(); values={'fslConfidence':1,'signsKnown':1,field:good}
            x['assessments'][0]['responses']=json.dumps(values)
            self.assertTrue(validate_bytes(encode(x))['valid'])
            values[field]=None; x['assessments'][0]['responses']=json.dumps(values)
            self.assertFalse(validate_bytes(encode(x))['valid'])
        x=fixture(); values=json.loads(x['assessments'][1]['responses']); values.pop('openFeedback')
        x['assessments'][1]['responses']=json.dumps(values)
        self.assertTrue(validate_bytes(encode(x))['valid'])
        values['openFeedback']=''; x['assessments'][1]['responses']=json.dumps(values)
        self.assertTrue(validate_bytes(encode(x))['valid'])

    def test_feedback_types_nonfinite_unknown_keys_and_empty_export(self):
        x=fixture(); item={'dimension':'handshape','severity':0.5,'hand':'right','prompt':'PRIVATE CANARY'}
        x['sessions'][0]['attempts'][0]['feedback_items']=json.dumps([item])
        self.assertTrue(validate_bytes(encode(x))['valid'])
        for key in item:
            bad=copy.deepcopy(x); values=copy.deepcopy(item); values[key]=None
            bad['sessions'][0]['attempts'][0]['feedback_items']=json.dumps([values])
            self.assertFalse(validate_bytes(encode(bad))['valid'])
        for path in [('sessions',0,'avg_match'),('sessions',0,'duration_s'),('sessions',0,'attempts',0,'overall_match'),('sessions',0,'attempts',0,'predicted_confidence')]:
            for bad in [float('nan'),float('inf'),float('-inf'),True,'0.5']:
                y=fixture(); owner=y
                for part in path[:-1]: owner=owner[part]
                owner[path[-1]]=bad
                result=validate_bytes(encode(y))
                self.assertFalse(result['valid'])
                self.assertNotIn('PRIVATE CANARY',json.dumps(result))
        for value in [b'', b'null', b'"PRIVATE CANARY"', b'{}', b'\\xff']:
            self.assertFalse(validate_bytes(value)['valid'])
        x=fixture(); x['metadata']['PRIVATE CANARY']='PRIVATE CANARY'
        self.assertEqual(validate_bytes(encode(x))['diagnostics'][0]['code'],'UNKNOWN_FIELD')
        x=fixture(); x['sessions']=[]; x['assessments']=[]
        x['summary']={'total_sessions':0,'total_attempts':0,'total_assessments':0}
        self.assertEqual(validate_bytes(encode(x))['counts'],{'sessions':0,'attempts':0,'assessments':0})

    def test_existing_engine_normalized_ranges_not_human_scores(self):
        for field in ('avg_match','overall_match','severity'):
            for value in (-0.1,1.1):
                x=fixture()
                if field=='avg_match': x['sessions'][0][field]=value
                elif field=='overall_match': x['sessions'][0]['attempts'][0][field]=value
                else: x['sessions'][0]['attempts'][0]['feedback_items']=json.dumps([{'dimension':'handshape','severity':value,'hand':'right','prompt':'PRIVATE CANARY'}])
                result=validate_bytes(encode(x))
                self.assertFalse(result['valid'])
                self.assertEqual(result['diagnostics'][0]['code'],'RANGE')

if __name__ == '__main__':
    unittest.main()
