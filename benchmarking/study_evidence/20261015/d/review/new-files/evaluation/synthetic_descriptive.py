"""SYNTHETIC questionnaire frequencies and event-label pair availability only.

No human scoring, confidence outcome, group assignment, imputation or inference.
"""
from .legacy_export import AGE, GENDER, response, strict_loads, validate_bytes


def describe_exports(inputs, *, source):
    if type(source) is not str or source != 'SYNTHETIC':
        return {'valid': False, 'diagnostics': [{'code': 'SYNTHETIC_REQUIRED'}]}
    if type(inputs) is not list:
        return {'valid': False, 'diagnostics': [{'code': 'TYPE'}]}
    roots, diagnostics, seen = [], [], set()
    counts = {'exports':len(inputs), 'participants':0, 'sessions':0, 'attempts':0, 'assessments':0}
    for index, data in enumerate(inputs):
        result = validate_bytes(data)
        if not result['valid']:
            diagnostics.extend(dict(item, input_index=index) for item in result['diagnostics'])
            continue
        root = strict_loads(data)
        participant = root['metadata']['participant_id']
        if participant in seen:
            diagnostics.append({'code':'DUPLICATE_EXPORT', 'input_index':index})
        seen.add(participant)
        roots.append(root)
        for field in ('sessions', 'attempts', 'assessments'):
            counts[field] += result['counts'][field]
    if diagnostics:
        return {'valid':False, 'synthetic':True, 'diagnostics':diagnostics}
    counts['participants'] = len(seen)
    matching = dict.fromkeys(('paired','unmatched_pre','unmatched_post','ambiguous','no_assessments'), 0)
    completeness = {field:{'present':0,'absent':0} for field in ('ageGroup','gender','openFeedback')}
    completeness['openFeedback']['empty'] = 0
    frequencies = {}
    for phase in ('pre', 'post'):
        frequencies[phase] = {field:{str(i):0 for i in range(1,6)} for field in ('fslConfidence','signsKnown')}
        frequencies[phase]['ageGroup'] = dict.fromkeys(AGE,0)
        frequencies[phase]['gender'] = dict.fromkeys(GENDER,0)
        if phase == 'post':
            frequencies[phase]['susScores'] = [{str(i):0 for i in range(1,6)} for _ in range(10)]
    for index, root in enumerate(roots):
        phases = {'pre':0,'post':0}
        for row in root['assessments']:
            phase = row['type']
            phases[phase] += 1
            values = response(row)
            for field in ('fslConfidence','signsKnown','ageGroup','gender'):
                if field in values:
                    frequencies[phase][field][str(values[field])] += 1
            for field in completeness:
                if field == 'openFeedback' and phase != 'post':
                    continue
                completeness[field]['present' if field in values else 'absent'] += 1
            if phase == 'post':
                completeness['openFeedback']['empty'] += int(values.get('openFeedback') == '')
                for i,value in enumerate(values['susScores']):
                    frequencies[phase]['susScores'][i][str(value)] += 1
        pre, post = phases['pre'], phases['post']
        if pre > 1 or post > 1:
            disposition, code = 'ambiguous', 'AMBIGUOUS_PHASE'
        elif pre == post == 1:
            disposition, code = 'paired', None
        elif pre == 1:
            disposition, code = 'unmatched_pre', 'UNMATCHED_PRE'
        elif post == 1:
            disposition, code = 'unmatched_post', 'UNMATCHED_POST'
        else:
            disposition, code = 'no_assessments', 'NO_ASSESSMENTS'
        matching[disposition] += 1
        if code:
            diagnostics.append({'code':code,'input_index':index})
    return {'valid':True,'synthetic':True,'counts':counts,'matching':matching,
            'completeness':completeness,'frequencies':frequencies,'diagnostics':diagnostics}
