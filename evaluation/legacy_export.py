"""Strict read-only adapter for SessionDatabase v1 / DataExporter legacy JSON.

This technical contract does not authorize participant processing or supply a
human outcome instrument. Diagnostics intentionally never contain input values.
"""
import datetime
import json
import math
import uuid

AGE = ('<13', '13-17', '18-25', '26-35', '36-50', '>50')
GENDER = ('Male', 'Female', 'Non-binary', 'Prefer not to say')


class Rejected(ValueError):
    """A fixed, privacy-safe failure code; never attach an input value."""


def require(condition, code):
    if not condition:
        raise Rejected(code)


def strict_loads(data):
    def pairs(items):
        obj = {}
        for key, value in items:
            require(key not in obj, 'JSON_INVALID')
            obj[key] = value
        return obj

    def bad_constant(_):
        raise Rejected('JSON_INVALID')

    def number(text):
        value = float(text)
        require(math.isfinite(value), 'JSON_INVALID')
        return value

    try:
        return json.loads(data, object_pairs_hook=pairs,
                          parse_constant=bad_constant, parse_float=number)
    except (ValueError, TypeError, UnicodeError, RecursionError):
        raise Rejected('JSON_INVALID') from None


def shape(obj, required, optional=()):
    require(type(obj) is dict, 'SHAPE')
    require(set(required) <= obj.keys(), 'REQUIRED')
    require(obj.keys() <= set(required) | set(optional), 'UNKNOWN_FIELD')


def integer(value, minimum=0):
    require(type(value) is int, 'TYPE')
    require(value >= minimum, 'RANGE')


def numeric(value, minimum=None, maximum=None):
    require(type(value) in (int, float), 'TYPE')
    try:
        finite = math.isfinite(value)
    except OverflowError:
        finite = False
    require(finite, 'NONFINITE')
    require(minimum is None or value >= minimum, 'RANGE')
    require(maximum is None or value <= maximum, 'RANGE')


def text(value):
    require(type(value) is str, 'TYPE')


def identity(value):
    text(value)
    try:
        require(str(uuid.UUID(value)) == value, 'UUID')
    except (ValueError, AttributeError):
        raise Rejected('UUID') from None


def unique(value, seen):
    require(value not in seen, 'DUPLICATE_ID')
    seen.add(value)


def response(row):
    text(row['responses'])
    values = strict_loads(row['responses'])
    required = ['fslConfidence', 'signsKnown']
    if row['type'] == 'post':
        required.append('susScores')
    shape(values, required, ['ageGroup', 'gender', 'openFeedback'] if row['type'] == 'post' else ['ageGroup', 'gender'])
    for field in ('fslConfidence', 'signsKnown'):
        integer(values[field], 1)
        require(values[field] <= 5, 'RANGE')
    for field, allowed in (('ageGroup', AGE), ('gender', GENDER)):
        if field in values:
            text(values[field])
            require(values[field] in allowed, 'ENUM')
    if 'openFeedback' in values:
        text(values['openFeedback'])
    if 'susScores' in values:
        require(type(values['susScores']) is list, 'TYPE')
        require(len(values['susScores']) == 10, 'RANGE')
        for value in values['susScores']:
            integer(value, 1)
            require(value <= 5, 'RANGE')
    return values


def _validate(root):
    shape(root, ('metadata', 'sessions', 'assessments', 'summary'))
    metadata = root['metadata']
    shape(metadata, ('participant_id', 'export_timestamp', 'app_version', 'device_model', 'android_version'))
    identity(metadata['participant_id'])
    for key in ('export_timestamp', 'app_version', 'device_model', 'android_version'):
        text(metadata[key])
    try:
        stamp = metadata['export_timestamp']
        require(datetime.datetime.strptime(stamp, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S') == stamp, 'TIMESTAMP')
    except ValueError:
        raise Rejected('TIMESTAMP') from None
    for key in ('sessions', 'assessments'):
        require(type(root[key]) is list, 'TYPE')
    counts = {'sessions': len(root['sessions']), 'attempts': 0, 'assessments': len(root['assessments'])}
    aids, sids, tids = set(), set(), set()
    for row in root['assessments']:
        shape(row, ('id', 'participant_id', 'type', 'timestamp', 'responses'))
        integer(row['id'], 1)
        unique(row['id'], aids)
        identity(row['participant_id'])
        require(row['participant_id'] == metadata['participant_id'], 'RELATION')
        integer(row['timestamp'])
        text(row['type'])
        require(row['type'] in ('pre', 'post'), 'PHASE')
        response(row)
    for row in root['sessions']:
        shape(row, ('id', 'participant_id', 'started_at', 'ended_at', 'attempt_count', 'signs_attempted', 'avg_match', 'duration_s', 'source', 'attempts'))
        identity(row['id'])
        unique(row['id'], sids)
        identity(row['participant_id'])
        require(row['participant_id'] == metadata['participant_id'], 'RELATION')
        integer(row['started_at'])
        if row['ended_at'] is not None:
            integer(row['ended_at'])
            require(row['ended_at'] >= row['started_at'], 'TIMESTAMP')
        for field in ('attempt_count', 'signs_attempted'):
            integer(row[field])
        numeric(row['avg_match'], 0, 1)
        numeric(row['duration_s'], 0)
        text(row['source'])
        require(row['source'] in ('app', 'legacy_migration'), 'ENUM')
        require(type(row['attempts']) is list, 'TYPE')
        counts['attempts'] += len(row['attempts'])
        for attempt in row['attempts']:
            shape(attempt, ('id', 'session_id', 'timestamp', 'target_class', 'target_label', 'predicted_label', 'predicted_confidence', 'recognized_as_target', 'overall_match', 'feedback_items'))
            integer(attempt['id'], 1)
            unique(attempt['id'], tids)
            identity(attempt['session_id'])
            require(attempt['session_id'] == row['id'], 'RELATION')
            for field in ('timestamp', 'target_class'):
                integer(attempt[field])
            for field in ('target_label', 'predicted_label', 'feedback_items'):
                text(attempt[field])
            numeric(attempt['predicted_confidence'], 0, 1)
            numeric(attempt['overall_match'], 0, 1)
            integer(attempt['recognized_as_target'])
            require(attempt['recognized_as_target'] in (0, 1), 'RANGE')
            items = strict_loads(attempt['feedback_items'])
            require(type(items) is list, 'TYPE')
            for item in items:
                shape(item, ('dimension', 'severity', 'hand', 'prompt'))
                for field in ('dimension', 'hand', 'prompt'):
                    text(item[field])
                numeric(item['severity'], 0, 1)
        if row['ended_at'] is not None:
            require(row['attempt_count'] == len(row['attempts']), 'SESSION_COUNT_MISMATCH')
            require(row['signs_attempted'] == len({a['target_class'] for a in row['attempts']}), 'SESSION_COUNT_MISMATCH')
    shape(root['summary'], ('total_sessions', 'total_attempts', 'total_assessments'))
    for key, count in counts.items():
        integer(root['summary']['total_' + key])
        require(root['summary']['total_' + key] == count, 'COUNT_MISMATCH')
    return counts


def validate_bytes(data):
    """Return aggregate counts or a fixed rejection, never raw records."""
    try:
        counts = _validate(strict_loads(data))
        return {'valid': True, 'diagnostics': [], 'counts': counts}
    except Rejected as failure:
        return {'valid': False, 'diagnostics': [{'code': str(failure)}]}
    except (RecursionError, OverflowError):
        return {'valid': False, 'diagnostics': [{'code': 'INPUT_LIMIT'}]}
