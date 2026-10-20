"""Capture explicit CURRENT input identities, not historical preregistration."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'training/models'))
from validation_campaign import sha256, validate_inputs, write_json

if __name__=='__main__':
    seq=ROOT.parent/'kumpas-data/sequences'; protocol=seq/'evaluation-v1'
    data=ROOT.parent/'kumpas-data'
    paths={role:str(seq/name) for role,name in [('original_X','X_train.npy'),('original_y','y_train.npy'),
        ('clips_train','clips_train.json'),('clips_test','clips_test.json'),('label_map','label_map.json'),('test_X','X_test.npy'),('test_y','y_test.npy')]}
    paths.update({role:str(protocol/name) for role,name in [('fit_X','X_fit.npy'),('fit_y','y_fit.npy'),
        ('val_X','X_val.npy'),('val_y','y_val.npy'),('manifest','manifest.json'),('augmentations','augmentations.json')]})
    paths.update({'freeze':str(ROOT/'training/models/protocol_selection_evaluation_v1.json'),
        'checkpoint':str(data/'models/20260930_153819_protocol_v1_no_face_baseline.keras'),
        'candidate':str(data/'tflite/evaluation-v1-candidate/kumpas_50sign_20260930_153819_protocol_v1_no_face_baseline_builtins_dynamic.tflite'),
        'provenance':str(data/'tflite/evaluation-v1-candidate/provenance.json')})
    dataset=ROOT.parent/'FSL-105 A dataset for recognizing 105 Filipino sign language videos'
    paths.update({'source_labels':str(dataset/'labels.csv'),'source_train_csv':str(dataset/'train.csv')})
    sources=['training/models/validation_campaign.py','training/tests/test_validation_campaign.py',
        'training/models/evaluation_protocol.py','training/models/train_cnn_lstm.py','training/models/freeze_selection.py',
        'training/models/evaluate_frozen.py','training/tflite_export/export_frozen.py',
        'training/preprocessing/build_sequences.py','training/preprocessing/extract_landmarks.py',
        'training/preprocessing/selected_classes.json','training/augmentation/augment_landmarks.py',
        'benchmarking/pipeline_parity.py','benchmarking/parity_fixtures.py']
    for i,name in enumerate(sources): paths['source_code_'+str(i)]=str(ROOT/name)
    # The B1 accepted completion identity is manifest.json, not a mutable latest alias.
    paths['source_b1_manifest']=str(data/'parity/20261017-validation-v1/manifest.json')
    hashes={k:sha256(Path(v)) for k,v in paths.items()}
    expected={'freeze':'512f9eb32321d1b24b9d40cb5b5cafff8fda99281c9868832a0029a51922be1c',
        'checkpoint':'55ba7bb86dab621ea85112073e805818b7f5f417ed6dd9e116db92fe8d61288d',
        'candidate':'9d8a8035fc0085ca4bd95f3d3fdc9d2f3a9e6439b89789c64305f908536b0468',
        'source_b1_manifest':'1cca1526355e9d4ce6c41102a0a6fa474a15dd77bbac2b09daee1ec85e70c452'}
    assert all(hashes[k]==v for k,v in expected.items()),'FROZEN_IDENTITY_MISMATCH'
    manifest=json.loads((protocol/'manifest.json').read_text())
    clips=[row['clip'] for row in manifest['rows'] if row['partition']=='validation']
    config={'schema':1,'class_count':50,'validation_count':150,'paths':paths,'sha256':hashes,'ordered_clips':clips}
    validate_inputs(config)
    destination=Path(sys.argv[1]); write_json(destination,config)
    print(json.dumps({'config':str(destination),'sha256':sha256(destination),'n':len(clips),'roles':len(paths)}))
