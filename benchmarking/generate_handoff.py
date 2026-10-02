#!/usr/bin/env python3
"""Generate BLANK/BLOCKED phone-handoff forms; never generate observations."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LABELS = ROOT.parent / 'app/android/app/src/main/assets/label_map.json'
CONDITIONS = ('optimal', 'low_light', 'cluttered')
CANDIDATES = ('redmi_note_11_4gb_candidate', 'additional_device_unverified')


def generate(output: Path):
    raw = LABELS.read_bytes()
    labels = json.loads(raw)
    assert sorted(int(k) for k in labels) == list(range(50))
    assert len({item['label'] for item in labels.values()}) == 50
    assert len({item['id'] for item in labels.values()}) == 50
    output.mkdir(parents=True, exist_ok=True)

    def save(name, fields, rows):
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
        (output / name).write_text(buffer.getvalue())

    candidates = [
        {'candidate_id': CANDIDATES[0], 'model_candidate': 'Redmi Note 11', 'indexed_chip': 'Snapdragon 680',
         'indexed_ram_variants': '4GB/64GB;4GB/128GB;6GB/128GB',
         'provenance': 'Manufacturer search-index excerpt only; direct fetch blocked',
         'source': 'https://www.mi.com/global/product/redmi-note-11/specs', 'availability': 'UNVERIFIED', 'status': 'BLOCKED'},
        {'candidate_id': CANDIDATES[1], 'model_candidate': '', 'indexed_chip': '', 'indexed_ram_variants': '',
         'provenance': 'Additional device slot; all specifications pending local verification',
         'source': '', 'availability': 'UNVERIFIED', 'status': 'BLOCKED'},
    ]
    save('candidate_devices.csv', list(candidates[0]), candidates)
    run_fields = ['candidate_id', 'condition', 'status', 'setup_id', 'run_id', 'device_fingerprint',
                  'actual_chip', 'actual_ram_gb', 'actual_camera_id', 'actual_lens', 'lux', 'distance_cm',
                  'apk_sha256', 'model_sha256', 'revision', 'thermal_state', 'duration_s', 'fps_gate', 'latency_gate',
                  'device_verified', 'setup_verified', 'consent_review', 'expert_review', 'owner_adviser_approval']
    save('condition_runs.csv', run_fields,
         ({'candidate_id': candidate, 'condition': condition, 'status': 'BLOCKED'} for candidate in CANDIDATES for condition in CONDITIONS))
    trial_fields = ['candidate_id', 'condition', 'class_id', 'source_class_id', 'target_label', 'category', 'status',
                    'setup_id', 'run_id', 'attempt_id', 'signer_code', 'consent_verified', 'predicted_class_id',
                    'predicted_label', 'recognized_as_target', 'outcome', 'analyzer_to_feedback_ms', 'ui_ack_upper_bound_ms']
    rows = []
    for candidate in CANDIDATES:
        for condition in CONDITIONS:
            for class_id in range(50):
                item = labels[str(class_id)]
                rows.append({'candidate_id': candidate, 'condition': condition, 'class_id': class_id,
                             'source_class_id': item['id'], 'target_label': item['label'], 'category': item['category'], 'status': 'BLOCKED'})
    save('sign_trials.csv', trial_fields, rows)
    confusion_fields = ['candidate_id', 'condition', 'class_id', 'source_class_id', 'target_label', 'status', 'run_id'] + ['predicted_' + str(i) for i in range(50)]
    save('confusion_matrix.csv', confusion_fields, ({k: v for k, v in row.items() if k in confusion_fields} for row in rows))
    checks = {'label_map_sha256': hashlib.sha256(raw).hexdigest(), 'unique_dense_classes': len(labels),
              'unique_source_ids': len({item['id'] for item in labels.values()}), 'candidates': len(CANDIDATES),
              'condition_cells': len(CANDIDATES) * len(CONDITIONS), 'blank_trial_cells': len(rows),
              'unique_candidate_condition_class_cells': len({(r['candidate_id'], r['condition'], r['class_id']) for r in rows}),
              'blank_confusion_cells': len(rows) * len(labels), 'observed_trials': None,
              'status': 'BLOCKED', 'five_dense_class_id': next(k for k, v in labels.items() if v['label'] == 'FIVE')}
    (output / 'generation_checks.json').write_text(json.dumps(checks, indent=2) + '\n')
    return checks


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', required=True, type=Path, help='Explicit output directory; existing forms must not be overwritten')
    args = parser.parse_args()
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        parser.error('output directory must be empty to preserve any completed forms')
    print(json.dumps(generate(args.output_dir), indent=2))
