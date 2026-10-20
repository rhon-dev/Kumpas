"""Synthetic event-label matching, missingness and safe frequencies."""
import copy
import json
import unittest
from evaluation.test_legacy_export import fixture, encode, P
from evaluation.synthetic_descriptive import describe_exports

class DescriptiveTests(unittest.TestCase):
    def describe(self, *rows):
        return describe_exports([encode(x) for x in rows], source='SYNTHETIC')

    def test_explicit_labels_pair_and_optional_absence(self):
        x=fixture()
        x['assessments'].reverse()  # order/time never assigns phase
        result=self.describe(x)
        self.assertTrue(result['valid'], result)
        self.assertEqual(result['matching'], {'paired':1,'unmatched_pre':0,'unmatched_post':0,'ambiguous':0,'no_assessments':0})
        self.assertEqual(result['completeness']['ageGroup'], {'present':0,'absent':2})
        self.assertEqual(result['completeness']['openFeedback'], {'present':1,'absent':0,'empty':0})
        self.assertEqual(result['frequencies']['pre']['signsKnown']['2'], 1)
        self.assertNotIn(P,json.dumps(result))
        self.assertNotIn('PRIVATE CANARY',json.dumps(result))

    def test_ambiguity_unmatched_empty_and_invalid_are_not_imputed(self):
        for phases, expected in [([], 'no_assessments'), (['pre'],'unmatched_pre'), (['post'],'unmatched_post'), (['pre','pre','post'],'ambiguous')]:
            x=fixture(); originals={a['type']:a for a in x['assessments']}
            x['assessments']=[dict(copy.deepcopy(originals[p]), id=i+1) for i,p in enumerate(phases)]
            x['summary']['total_assessments']=len(phases)
            result=self.describe(x)
            self.assertTrue(result['valid'], result)
            self.assertEqual(result['matching'][expected],1)
            if expected!='no_assessments': self.assertEqual(result['matching']['paired'],0)
            if expected=='ambiguous': self.assertEqual(result['diagnostics'][0]['code'],'AMBIGUOUS_PHASE')
        self.assertEqual(self.describe()['matching']['paired'],0)
        x=fixture(); x['assessments'][0]['responses']='{}'
        invalid=self.describe(x)
        self.assertFalse(invalid['valid'])
        self.assertEqual(invalid['diagnostics'][0], {'code':'REQUIRED','input_index':0})
        self.assertNotIn('frequencies',invalid)
        self.assertEqual(self.describe(fixture(),fixture())['diagnostics'][0]['code'],'DUPLICATE_EXPORT')
        for source in ['real',None,True]:
            self.assertFalse(describe_exports([encode(fixture())],source=source)['valid'])

if __name__ == '__main__': unittest.main()
