# Task D incremental implementation evidence

Worker preparation only; no acceptance, real dataset admission, real-source fitting/inference/evaluation, model activation, camera or human approval.

## Preflight (before source work)
- Read task-d-brief.md, immutable C reader/builder schema, and legacy constructor lines65–87 only.
- Verified all36 protected SHA256 bindings and all8 owned destinations absent. Protection receipt SHA256: `037bbff5eaae485560fe24f6f7a16c715d74fe65ca923d480b64811dede0900e`.
- `git diff --exit-code` and `git diff --cached --exit-code`: exit0. Existing migration/root material is untracked; it remains protected by the explicit receipt.
- Runtime shell TMPDIR was the system default: all subsequent execution explicitly sets approved Hermes scratch TMPDIR. No actual-source arrays, videos or weights opened.
- Concern: full-source support/admission remains a parent gate. Synthetic in-process seams cannot prove signed provenance or create real admission. Train must never call C validate_campaign.
- Exclusive evidence directory and incremental commands/results follow. Source is confined to the eight new paths in the brief.

## Evidence allocation
Exclusive evidence: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2`. All child executions use scratch TMPDIR and bounded CPU threads. Initial append helper encountered numbered/deduplicated read_file output; corrected before source edits. No source/product failure.

## 01-augmentation-red
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_augmentation.py -q`
- Exit: 1. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/01-augmentation-red.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/01-augmentation-red.json`.
- Result: F                                                                        [100%]
=================================== FAILURES ===================================
________ test_fit_rotation_preserves_missing_masks_depth_and_one_angle _________

    def test_fit_rotation_preserves_missing_masks_depth_and_one_angle():
>       a=importlib.import_module('training.holistic_migration.augmentation')
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

training/holistic_migration/tests/test_augmentation.py:24: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1204: in _gcd_import
    ???
<frozen importlib._bootstrap>:1176: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'training.holistic_migration.augmentation'
import_ = <function _gcd_import at 0x10087bd80>

>   ???
E   ModuleNotFoundError: No module named 'training.holistic_migration.augmentation'

<frozen importlib._bootstrap>:1140: ModuleNotFoundError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_augmentation.py::test_fit_rotation_preserves_missing_masks_depth_and_one_angle
1 failed in 0.24s

## 02-augmentation-green
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_augmentation.py -q`
- Exit: 0. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/02-augmentation-green.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/02-augmentation-green.json`.
- Result: .                                                                        [100%]
1 passed in 0.20s

## 03-augmentation-boundary-red
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_augmentation.py -q`
- Exit: 1. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/03-augmentation-boundary-red.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/03-augmentation-boundary-red.json`.
- Result: raining/holistic_migration/tests/test_augmentation.py:69: Failed
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_augmentation.py::test_rotation_refuses_non_fit[validation]
FAILED training/holistic_migration/tests/test_augmentation.py::test_rotation_refuses_non_fit[test]
FAILED training/holistic_migration/tests/test_augmentation.py::test_rotation_refuses_non_fit[train]
FAILED training/holistic_migration/tests/test_augmentation.py::test_rotation_refuses_non_fit[None]
FAILED training/holistic_migration/tests/test_augmentation.py::test_invalid_tensor_or_identity_refused[dtype]
FAILED training/holistic_migration/tests/test_augmentation.py::test_invalid_tensor_or_identity_refused[shape]
FAILED training/holistic_migration/tests/test_augmentation.py::test_invalid_tensor_or_identity_refused[nan]
FAILED training/holistic_migration/tests/test_augmentation.py::test_invalid_tensor_or_identity_refused[mask]
FAILED training/holistic_migration/tests/test_augmentation.py::test_invalid_tensor_or_identity_refused[absent]
FAILED training/holistic_migration/tests/test_augmentation.py::test_invalid_tensor_or_identity_refused[invisible]
FAILED training/holistic_migration/tests/test_augmentation.py::test_invalid_tensor_or_identity_refused[pose_mask]
FAILED training/holistic_migration/tests/test_augmentation.py::test_invalid_tensor_or_identity_refused[wrist_depth]
FAILED training/holistic_migration/tests/test_augmentation.py::test_invalid_tensor_or_identity_refused[shoulder]
FAILED training/holistic_migration/tests/test_augmentation.py::test_invalid_tensor_or_identity_refused[ids]
FAILED training/holistic_migration/tests/test_augmentation.py::test_invalid_tensor_or_identity_refused[seed]
15 failed, 1 passed in 0.29s

## 04-augmentation-boundary-green
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_augmentation.py -q`
- Exit: 0. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/04-augmentation-boundary-green.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/04-augmentation-boundary-green.json`.
- Result: ................                                                         [100%]
16 passed in 0.22s

## 05-model-red
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py -q`
- Exit: 1. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/05-model-red.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/05-model-red.json`.
- Result:                                                  [100%]
=================================== FAILURES ===================================
_________ test_lazy_architecture_actual_bounded_optimizer_save_reload __________

tmp_path = PosixPath('/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/pytest-of-ahronjanl.rafaelahron.0804icloudcom/pytest-53/test_lazy_architecture_actual_0')

    def test_lazy_architecture_actual_bounded_optimizer_save_reload(tmp_path):
>       t=train()
          ^^^^^^^

training/holistic_migration/tests/test_train.py:15: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
training/holistic_migration/tests/test_train.py:11: in train
    def train(): return importlib.import_module('training.holistic_migration.train')
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1204: in _gcd_import
    ???
<frozen importlib._bootstrap>:1176: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'training.holistic_migration.train'
import_ = <function _gcd_import at 0x10259bd80>

>   ???
E   ModuleNotFoundError: No module named 'training.holistic_migration.train'

<frozen importlib._bootstrap>:1140: ModuleNotFoundError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_train.py::test_lazy_architecture_actual_bounded_optimizer_save_reload
1 failed in 1.67s

## 06-model-green
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py -q`
- Exit: 0. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/06-model-green.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/06-model-green.json`.
- Result: .                                                                        [100%]
=============================== warnings summary ===============================
training/holistic_migration/tests/test_train.py: 22 warnings
  /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/lib/python3.11/site-packages/keras/src/backend/tensorflow/core.py:172: DeprecationWarning: __array__ implementation doesn't accept a copy keyword, so passing copy=False failed. __array__ must implement 'dtype' and 'copy' keyword arguments.
    return np.array(x)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
1 passed, 22 warnings in 10.59s

## 07-reader-red
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py -q -k admitted_reader`
- Exit: 1. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/07-reader-red.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/07-reader-red.json`.
- Result:                                                  [100%]
=================================== FAILURES ===================================
____ test_admitted_reader_is_fit_validation_only_and_real_rejects_synthetic ____

tmp_path = PosixPath('/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/pytest-of-ahronjanl.rafaelahron.0804icloudcom/pytest-55/test_admitted_reader_is_fit_va0')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x10702cf90>

    def test_admitted_reader_is_fit_validation_only_and_real_rejects_synthetic(tmp_path,monkeypatch):
        t=train(); b,a=synthetic_bundle(tmp_path/'bundle')
        opened=[]; real_open=Path.open; real_load=np.load
        def guard(path,*args,**kwargs):
            assert not any(Path(path).name==f'{prefix}_test.npy' for prefix in ['X','y','clip_ids'])
            opened.append(str(path)); return real_open(path,*args,**kwargs)
        def guard_load(path,*args,**kwargs):
            assert '_test.npy' not in str(path); return real_load(path,*args,**kwargs)
        monkeypatch.setattr(Path,'open',guard); monkeypatch.setattr(np,'load',guard_load)
        monkeypatch.setattr(importlib.import_module('training.holistic_migration.dataset'),'validate_campaign',lambda *a:pytest.fail('all-partition consumer forbidden'))
>       data=t._read_bundle(b,a,evidence_kind='synthetic_in_process')
             ^^^^^^^^^^^^^^
E       AttributeError: module 'training.holistic_migration.train' has no attribute '_read_bundle'

training/holistic_migration/tests/test_train.py:90: AttributeError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_train.py::test_admitted_reader_is_fit_validation_only_and_real_rejects_synthetic
1 failed, 1 deselected in 1.58s

## 08-reader-green
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py -q -k admitted_reader`
- Exit: 0. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/08-reader-green.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/08-reader-green.json`.
- Result: .                                                                        [100%]
1 passed, 1 deselected in 0.28s

## 09-reader-boundary-red
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py -q -k strict_mutations`
- Exit: 1. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/09-reader-boundary-red.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/09-reader-boundary-red.json`.
- Result: ': m['classes']=list(reversed(m['classes']))
        if bad=='dimensions': np.save(b/'X_fit.npy',synthetic_tensor(50)[:,:,:152],allow_pickle=False)
        if bad=='labels': np.save(b/'y_fit.npy',np.zeros(50,np.int64),allow_pickle=False)
        if bad=='ids': np.save(b/'clip_ids_fit.npy',np.array(['duplicate']*50),allow_pickle=False)
        if bad=='object_ids': np.save(b/'clip_ids_fit.npy',np.array(['x']*50,object),allow_pickle=True)
        if bad=='absent':
            x=np.load(b/'X_fit.npy'); x[0,0,1]=1; np.save(b/'X_fit.npy',x,allow_pickle=False)
        if bad=='support':
            for prefix in ['X','y','clip_ids']:
                array=np.load(b/f'{prefix}_fit.npy'); np.save(b/f'{prefix}_fit.npy',array[:-1],allow_pickle=False)
        rewrite_json(b/'data_manifest.json',m); rewrite_json(a,ap)
        if bad not in ['extra_artifact','test_hash','stale','object_ids']: rebind_synthetic(b,a)
        if bad in ['extra_artifact','test_hash']:
            d=importlib.import_module('training.holistic_migration.dataset'); ap['data_manifest_sha256']=d.sha256(b/'data_manifest.json'); rewrite_json(a,ap)
>       with pytest.raises((ValueError,KeyError)): t._read_bundle(b,a,evidence_kind='synthetic_in_process')
E       Failed: DID NOT RAISE any of (ValueError, KeyError)

training/holistic_migration/tests/test_train.py:148: Failed
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_train.py::test_reader_strict_mutations_rejected[capture_float]
FAILED training/holistic_migration/tests/test_train.py::test_reader_strict_mutations_rejected[extra_artifact]
FAILED training/holistic_migration/tests/test_train.py::test_reader_strict_mutations_rejected[test_hash]
3 failed, 13 passed, 2 deselected in 0.90s

## 10-reader-boundary-green
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py -q -k 'not lazy_architecture'`
- Exit: 0. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/10-reader-boundary-green.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/10-reader-boundary-green.json`.
- Result: .................                                                        [100%]
17 passed, 1 deselected in 0.90s

Boundary variants already rejecting malformed admission, copied/stale bundle/class/dimension/label/ID/absent/object/support and unknown_reason were coverage-only GREEN. Behavioral RED existed for capture_float, extra_artifact and test_hash. Masks/wrist-local depth test fixture was corrected to conform to the provided feature contract, not a changed production convention. TF execution raised22 unsuppressed upstream Keras/NumPy copy-keyword deprecation warnings.

## 11-metrics-red
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py -q`
- Exit: 1. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/11-metrics-red.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/11-metrics-red.json`.
- Result: LURES ===================================
_________ test_metrics_all50_sparse_originals_and_unknown_denominators _________

tmp_path = PosixPath('/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/pytest-of-ahronjanl.rafaelahron.0804icloudcom/pytest-59/test_metrics_all50_sparse_orig0')

    def test_metrics_all50_sparse_originals_and_unknown_denominators(tmp_path):
>       e=evaluator(); t=train(); b,a=synthetic_bundle(tmp_path/'bundle')
          ^^^^^^^^^^^

training/holistic_migration/tests/test_evaluate.py:14: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
training/holistic_migration/tests/test_evaluate.py:10: in evaluator
    def evaluator(): return importlib.import_module('training.holistic_migration.evaluate')
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.11/3.11.15/Frameworks/Python.framework/Versions/3.11/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1204: in _gcd_import
    ???
<frozen importlib._bootstrap>:1176: in _find_and_load
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

name = 'training.holistic_migration.evaluate'
import_ = <function _gcd_import at 0x109d1fd80>

>   ???
E   ModuleNotFoundError: No module named 'training.holistic_migration.evaluate'

<frozen importlib._bootstrap>:1140: ModuleNotFoundError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_evaluate.py::test_metrics_all50_sparse_originals_and_unknown_denominators
1 failed in 0.20s

## 12-metrics-green
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py -q`
- Exit: 0. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/12-metrics-green.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/12-metrics-green.json`.
- Result: .                                                                        [100%]
1 passed in 0.30s

## 13-tiny-red
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py -q -k tiny_`
- Exit: 1. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/13-tiny-red.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/13-tiny-red.json`.
- Result: train(); data=encoded_data(tmp_path); backend=SyntheticBackend(wrong=fault=='wrong',fail_reload=fault=='reload'); out=tmp_path/'failed'
>       with pytest.raises(ValueError): t._execute(data,'tiny-fit',out,_backend=backend,_epochs=2)
                                        ^^^^^^^^^^
E       AttributeError: module 'training.holistic_migration.train' has no attribute '_execute'

training/holistic_migration/tests/test_train.py:206: AttributeError
______ test_tiny_failed_learning_or_reload_never_publishes_proof[reload] _______

tmp_path = PosixPath('/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/pytest-of-ahronjanl.rafaelahron.0804icloudcom/pytest-61/test_tiny_failed_learning_or_r1')
fault = 'reload'

    @pytest.mark.parametrize('fault',['wrong','reload'])
    def test_tiny_failed_learning_or_reload_never_publishes_proof(tmp_path,fault):
        t=train(); data=encoded_data(tmp_path); backend=SyntheticBackend(wrong=fault=='wrong',fail_reload=fault=='reload'); out=tmp_path/'failed'
>       with pytest.raises(ValueError): t._execute(data,'tiny-fit',out,_backend=backend,_epochs=2)
                                        ^^^^^^^^^^
E       AttributeError: module 'training.holistic_migration.train' has no attribute '_execute'

training/holistic_migration/tests/test_train.py:206: AttributeError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_train.py::test_tiny_lifecycle_retains_hash_bound_synthetic_proof_only
FAILED training/holistic_migration/tests/test_train.py::test_tiny_failed_learning_or_reload_never_publishes_proof[wrong]
FAILED training/holistic_migration/tests/test_train.py::test_tiny_failed_learning_or_reload_never_publishes_proof[reload]
3 failed, 18 deselected in 0.46s

## 14-tiny-green
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py -q -k tiny_`
- Exit: 0. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/14-tiny-green.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/14-tiny-green.json`.
- Result: ...                                                                      [100%]
3 passed, 18 deselected in 0.40s

## 15-full-red
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py -q -k full_`
- Exit: 1. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/15-full-red.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/15-full-red.json`.
- Result: =32; batches.append(len(x)); return original_step(m,x,y)
        backend.step=track
        deny_test_access(monkeypatch)
        out=tmp_path/'fit'
>       selected=t._execute(data,'fit',out,tiny_proof=tiny/'tiny-proof.json',_backend=backend,_epochs=3)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

training/holistic_migration/tests/test_train.py:221: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

data = AdmittedData(bundle=PosixPath('/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/pytest-of-ahronjanl.ra...c51f0147b8846db8de094bad8daeeeda6a4a188d', 'feature': 'Float32[N,30,153] hm153-v1'}, provenance='synthetic_in_process')
mode = 'fit'
output = PosixPath('/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/pytest-of-ahronjanl.rafaelahron.0804icloudcom/pytest-63/test_full_fresh_model_fit_only0/fit')
tiny_proof = PosixPath('/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/pytest-of-ahronjanl.rafaelahron.0804icloudcom/pytest-63/test_full_fresh_model_fit_only0/tiny/tiny-proof.json')
_backend = <holistic_migration.tests.test_train.SyntheticBackend object at 0x108d5bad0>
_epochs = 3

    def _execute(data,mode,output,*,tiny_proof=None,_backend=None,_epochs=None):
>       if mode!='tiny-fit': raise ValueError('unsupported operation')
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       ValueError: unsupported operation

training/holistic_migration/train.py:311: ValueError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_train.py::test_full_fresh_model_fit_only_augmented_earliest_tie_selection
1 failed, 9 passed, 21 deselected in 0.88s

## 16-full-first-green-attempt
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py -q -k full_`
- Exit: 1. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/16-full-first-green-attempt.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/16-full-first-green-attempt.json`.
- Result: st-64/test_full_proof_rejection_befo8')
bad = 'epochs'

    @pytest.mark.parametrize('bad',['boolean','missing_checkpoint','changed_checkpoint','synthetic_to_real','source','dataset','tensors','family','epochs'])
    def test_full_proof_rejection_before_new_fit(tmp_path,bad):
        from dataclasses import replace
        t=train(); data=encoded_data(tmp_path); backend=SyntheticBackend(); tiny=tmp_path/'tiny'
        t._execute(data,'tiny-fit',tiny,_backend=backend,_epochs=2)
        path=tiny/'tiny-proof.json'; proof=json.loads(path.read_text())
        if bad=='boolean': rewrite_json(path,True)
        if bad=='missing_checkpoint': (tiny/'model.keras').unlink()
        if bad=='changed_checkpoint': (tiny/'model.keras').write_text('changed')
        if bad=='synthetic_to_real': data=replace(data,provenance='source_video')
        if bad=='source': proof['identity']['sources']['train.py']='0'*64
        if bad=='dataset': data=replace(data,identity=dict(data.identity,data_manifest_sha256='0'*64))
        if bad=='tensors': proof['selected_tensors']['X']['sha256']='0'*64
        if bad=='family': proof['identity']['family']['outputs']=8
        if bad=='epochs': proof['actual_epochs']=False
        if bad not in ['boolean','missing_checkpoint','changed_checkpoint']: rewrite_json(path,proof)
        out=tmp_path/'not-created'
>       with pytest.raises((ValueError,TypeError,KeyError,AttributeError)):
E       Failed: DID NOT RAISE any of (ValueError, TypeError, KeyError, AttributeError)

training/holistic_migration/tests/test_train.py:251: Failed
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_train.py::test_full_proof_rejection_before_new_fit[epochs]
1 failed, 9 passed, 21 deselected in 1.12s

## 17-full-green
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py -q -k 'not lazy_architecture'`
- Exit: 0. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/17-full-green.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/17-full-green.json`.
- Result: ..............................                                           [100%]
30 passed, 1 deselected in 1.65s

The initial full-proof mutation run was NOT valid proof of denial: full mode did not yet exist. After full fit was executable, mutations exercised real admission; forged actual_epochs produced behavioral RED in16 and was corrected before17. Full lifecycle successes here use explicitly labeled synthetic oracle/fault seams, not claimed optimizer convergence.

## 18-evaluator-red
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py -q -k 'not metrics'`
- Exit: 1. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/18-evaluator-red.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/18-evaluator-red.json`.
- Result: ts/test_evaluate.py:80: AttributeError
______________ test_existing_incomplete_evaluation_does_not_rerun ______________

tmp_path = PosixPath('/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/pytest-of-ahronjanl.rafaelahron.0804icloudcom/pytest-66/test_existing_incomplete_evalu0')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x10b326f10>

    def test_existing_incomplete_evaluation_does_not_rerun(tmp_path,monkeypatch):
        e=evaluator(); data,backend,run=frozen_synthetic_run(tmp_path); out=tmp_path/'evaluation'; out.mkdir()
>       with pytest.raises(ValueError): e._evaluate(run,data,out,_backend=backend)
                                        ^^^^^^^^^^^
E       AttributeError: module 'training.holistic_migration.evaluate' has no attribute '_evaluate'

training/holistic_migration/tests/test_evaluate.py:86: AttributeError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_evaluate.py::test_separate_evaluator_starts_before_test_and_completed_is_readback_only
FAILED training/holistic_migration/tests/test_evaluate.py::test_frozen_tamper_denied_before_test_or_output[model]
FAILED training/holistic_migration/tests/test_evaluate.py::test_frozen_tamper_denied_before_test_or_output[policy]
FAILED training/holistic_migration/tests/test_evaluate.py::test_frozen_tamper_denied_before_test_or_output[source]
FAILED training/holistic_migration/tests/test_evaluate.py::test_frozen_tamper_denied_before_test_or_output[selection]
FAILED training/holistic_migration/tests/test_evaluate.py::test_frozen_tamper_denied_before_test_or_output[config]
FAILED training/holistic_migration/tests/test_evaluate.py::test_existing_incomplete_evaluation_does_not_rerun
7 failed, 1 deselected in 1.01s

## 19-evaluator-green
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py -q`
- Exit: 0. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/19-evaluator-green.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/19-evaluator-green.json`.
- Result: ........                                                                 [100%]
8 passed in 1.06s

## 20-cli-red
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py training/holistic_migration/tests/test_evaluate.py -q -k 'cli or module_import'`
- Exit: 1. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/20-cli-red.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/20-cli-red.json`.
- Result: in.py:273: AssertionError
__________ test_actual_evaluator_cli_synthetic_refusal_before_output ___________

tmp_path = PosixPath('/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/pytest-of-ahronjanl.rafaelahron.0804icloudcom/pytest-68/test_actual_evaluator_cli_synt0')

    def test_actual_evaluator_cli_synthetic_refusal_before_output(tmp_path):
        import subprocess,sys,os
        t=train(); b,a=synthetic_bundle(tmp_path/'bundle'); out=tmp_path/'not-created'
        p=subprocess.run([sys.executable,'-E','-B','-m','training.holistic_migration.evaluate','--run',str(tmp_path/'absent-run'),'--bundle',str(b),'--admission',str(a),'--output',str(out)],cwd=t.d.REPO,capture_output=True,text=True)
>       assert p.returncode==2 and 'admission status' in p.stderr and not out.exists()
E       AssertionError: assert (0 == 2)
E        +  where 0 = CompletedProcess(args=['/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python',....rafaelahron.0804icloudcom/pytest-68/test_actual_evaluator_cli_synt0/not-created'], returncode=0, stdout='', stderr='').returncode

training/holistic_migration/tests/test_evaluate.py:94: AssertionError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_train.py::test_actual_train_cli_synthetic_refusal_and_no_tensorflow_or_output[tiny-fit]
FAILED training/holistic_migration/tests/test_train.py::test_actual_train_cli_synthetic_refusal_and_no_tensorflow_or_output[fit]
FAILED training/holistic_migration/tests/test_train.py::test_module_import_and_help_lazy_and_no_synthetic_cli_option
FAILED training/holistic_migration/tests/test_evaluate.py::test_actual_evaluator_cli_synthetic_refusal_before_output
4 failed, 39 deselected in 1.15s

## 21-cli-green
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py training/holistic_migration/tests/test_evaluate.py -q -k 'cli or module_import'`
- Exit: 0. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/21-cli-green.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/21-cli-green.json`.
- Result: ....                                                                     [100%]
4 passed, 39 deselected in 1.26s

## 22-path-json-red
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py -q -k 'duplicate_admission or invalid_output'`
- Exit: 1. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/22-path-json-red.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/22-path-json-red.json`.
- Result: hronjanl.rafaelahron.0804icloudcom/pytest-70/test_duplicate_admission_keys_0')

    def test_duplicate_admission_keys_are_not_an_exact_schema(tmp_path):
        t=train(); b,a=synthetic_bundle(tmp_path/'bundle')
        text=a.read_text(); a.write_text(text.replace('{','{"schema_version":0,',1))
>       with pytest.raises(ValueError,match='duplicate'): t._read_bundle(b,a,evidence_kind='synthetic_in_process')
E       Failed: DID NOT RAISE ValueError

training/holistic_migration/tests/test_train.py:282: Failed
_______ test_full_invalid_output_rejected_before_checkpoint_native_load ________

tmp_path = PosixPath('/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/pytest-of-ahronjanl.rafaelahron.0804icloudcom/pytest-70/test_full_invalid_output_rejec0')

    def test_full_invalid_output_rejected_before_checkpoint_native_load(tmp_path):
        t=train(); data=encoded_data(tmp_path); backend=SyntheticBackend(); tiny=tmp_path/'tiny'
        t._execute(data,'tiny-fit',tiny,_backend=backend,_epochs=2)
        loads=backend.loaded
        with pytest.raises(ValueError): t._execute(data,'fit',Path('relative-output'),tiny_proof=tiny/'tiny-proof.json',_backend=backend,_epochs=1)
>       assert backend.loaded==loads and backend.built==1
E       assert (2 == 1)
E        +  where 2 = <holistic_migration.tests.test_train.SyntheticBackend object at 0x1075c3b90>.loaded

training/holistic_migration/tests/test_train.py:290: AssertionError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_train.py::test_duplicate_admission_keys_are_not_an_exact_schema
FAILED training/holistic_migration/tests/test_train.py::test_full_invalid_output_rejected_before_checkpoint_native_load
2 failed, 34 deselected in 0.43s

## 23-path-json-green
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py training/holistic_migration/tests/test_evaluate.py training/holistic_migration/tests/test_augmentation.py -q -k 'not lazy_architecture'`
- Exit: 0. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/23-path-json-green.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/23-path-json-green.json`.
- Result: ............................................................             [100%]
60 passed, 1 deselected in 3.70s

## 24-metric-boundary-red
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py -q -k refuses_invalid`
- Exit: 1. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/24-metric-boundary-red.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/24-metric-boundary-red.json`.
- Result: lueError

training/holistic_migration/tests/test_evaluate.py:111: Failed
_____ test_metrics_refuses_invalid_probability_or_output_mapping[classes] ______

tmp_path = PosixPath('/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/pytest-of-ahronjanl.rafaelahron.0804icloudcom/pytest-72/test_metrics_refuses_invalid_p6')
bad = 'classes'

    @pytest.mark.parametrize('bad',['nan','shape','range','sum','mapping','duplicate_ids','classes'])
    def test_metrics_refuses_invalid_probability_or_output_mapping(tmp_path,bad):
        e=evaluator(); t=train(); b,a=synthetic_bundle(tmp_path/'bundle'); data=t._read_bundle(b,a,evidence_kind='synthetic_in_process')
        classes=data.manifest['classes']; ids=['synthetic/a','synthetic/b']; y=np.array([1,2],np.int64)
        rows=[dict(clip_id=s,dense_id=int(label),partition='test',reason='eligible') for s,label in zip(ids,y)]
        p=np.full((2,50),.02,np.float32)
        if bad=='nan': p[0,0]=np.nan
        if bad=='shape': p=p[:,:49]
        if bad=='range': p[0,0]=-1
        if bad=='sum': p[0]*=.5
        if bad=='mapping': y[:]=0
        if bad=='duplicate_ids': ids[1]=ids[0]; rows[1]['clip_id']=ids[0]
        if bad=='classes': classes=classes[:49]
>       with pytest.raises(ValueError): e.metrics(y,p,ids,classes,rows,partition='test')
E       Failed: DID NOT RAISE ValueError

training/holistic_migration/tests/test_evaluate.py:111: Failed
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_evaluate.py::test_metrics_refuses_invalid_probability_or_output_mapping[duplicate_ids]
FAILED training/holistic_migration/tests/test_evaluate.py::test_metrics_refuses_invalid_probability_or_output_mapping[classes]
2 failed, 5 passed, 9 deselected in 0.54s

## 25-metric-boundary-green
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py -q`
- Exit: 0. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/25-metric-boundary-green.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/25-metric-boundary-green.json`.
- Result: ................                                                         [100%]
16 passed in 1.61s

## 26-real-tf-and-fault-coverage
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py -q -k 'actual_tf or failed_full_report or checkpoint_final'`
- Exit: 0. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/26-real-tf-and-fault-coverage.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/26-real-tf-and-fault-coverage.json`.
- Result: ....                                                                     [100%]
=============================== warnings summary ===============================
training/holistic_migration/tests/test_train.py: 45 warnings
  /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/lib/python3.11/site-packages/keras/src/backend/tensorflow/core.py:172: DeprecationWarning: __array__ implementation doesn't accept a copy keyword, so passing copy=False failed. __array__ must implement 'dtype' and 'copy' keyword arguments.
    return np.array(x)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
4 passed, 36 deselected, 45 warnings in 12.02s

26 is additional execution/fault coverage GREEN (no new production slice). It executed real TF1-step tiny/save/reload and a4-step one-epoch full lifecycle on synthetic fixtures through an explicitly patched synthetic proof gate. That full lifecycle is NOT a tiny-proof acceptance or real-data fit. Existing architecture1-step execution is independent. Fault coverage preserves frozen selection on reporting failure and withholds tiny proof when checkpoint readback fails.

## 27-partial-progress-red
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py -q -k optimizer_failure`
- Exit: 1. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/27-partial-progress-red.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/27-partial-progress-red.json`.
- Result: aining/holistic_migration/tests/test_train.py:360: KeyError
_________ test_optimizer_failure_retains_actual_partial_progress[fit] __________

tmp_path = PosixPath('/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch/pytest-of-ahronjanl.rafaelahron.0804icloudcom/pytest-75/test_optimizer_failure_retains1')
mode = 'fit'

    @pytest.mark.parametrize('mode',['tiny-fit','fit'])
    def test_optimizer_failure_retains_actual_partial_progress(tmp_path,mode):
        t=train(); data=encoded_data(tmp_path); backend=SyntheticBackend(); proof=None
        if mode=='fit':
            tiny=tmp_path/'tiny'; t._execute(data,'tiny-fit',tiny,_backend=backend,_epochs=1); proof=tiny/'tiny-proof.json'
        original=backend.step
        def fail(m,x,y):
            original(m,x,y)
            if m['steps']==2: raise ValueError('synthetic optimizer interruption')
        backend.step=fail
        if mode=='tiny-fit': backend.wrong=True
        out=tmp_path/'interrupted'
        with pytest.raises(ValueError,match='synthetic optimizer interruption'):
            t._execute(data,mode,out,tiny_proof=proof,_backend=backend,_epochs=3)
        failure=json.loads((out/'failure.json').read_text())
>       assert failure['optimizer_steps']==2 and failure['actual_epochs']==(1 if mode=='tiny-fit' else 0)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^
E       KeyError: 'optimizer_steps'

training/holistic_migration/tests/test_train.py:360: KeyError
=========================== short test summary info ============================
FAILED training/holistic_migration/tests/test_train.py::test_optimizer_failure_retains_actual_partial_progress[tiny-fit]
FAILED training/holistic_migration/tests/test_train.py::test_optimizer_failure_retains_actual_partial_progress[fit]
2 failed, 40 deselected in 0.49s

## 28-partial-progress-green
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py -q -k 'not lazy_architecture and not actual_tf'`
- Exit: 0. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/28-partial-progress-green.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/28-partial-progress-green.json`.
- Result: .......................................                                  [100%]
39 passed, 3 deselected in 3.13s

## 29-extra-boundary-coverage
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py training/holistic_migration/tests/test_evaluate.py -q -k 'evaluation_report_failure or tiny_lifecycle or full_fresh'`
- Exit: 0. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/29-extra-boundary-coverage.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/29-extra-boundary-coverage.json`.
- Result: ...                                                                      [100%]
3 passed, 56 deselected in 0.72s

29 is coverage-only GREEN: evaluator reporting failure retains selection/start/partial outputs, no completed receipt and no rerun; test-array guards now encompass canonical reader plus tiny/full execution. Lazy-import assertion now runs in a fresh process so test ordering cannot cause a false failure. No new production behavior was added in this coverage step.

## 30-named-new-suite
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_augmentation.py training/holistic_migration/tests/test_train.py training/holistic_migration/tests/test_evaluate.py -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/named-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/30-named.xml`
- Exit: 0. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/30-named-new-suite.log`; source-bound receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/30-named-new-suite.json`.
- Result:
en_tamper_denied_before_test_or_output[source] PASSED [ 84%]
training/holistic_migration/tests/test_evaluate.py::test_frozen_tamper_denied_before_test_or_output[selection] PASSED [ 85%]
training/holistic_migration/tests/test_evaluate.py::test_frozen_tamper_denied_before_test_or_output[config] PASSED [ 86%]
training/holistic_migration/tests/test_evaluate.py::test_existing_incomplete_evaluation_does_not_rerun PASSED [ 88%]
training/holistic_migration/tests/test_evaluate.py::test_actual_evaluator_cli_synthetic_refusal_before_output PASSED [ 89%]
training/holistic_migration/tests/test_evaluate.py::test_metrics_refuses_invalid_probability_or_output_mapping[nan] PASSED [ 90%]
training/holistic_migration/tests/test_evaluate.py::test_metrics_refuses_invalid_probability_or_output_mapping[shape] PASSED [ 92%]
training/holistic_migration/tests/test_evaluate.py::test_metrics_refuses_invalid_probability_or_output_mapping[range] PASSED [ 93%]
training/holistic_migration/tests/test_evaluate.py::test_metrics_refuses_invalid_probability_or_output_mapping[sum] PASSED [ 94%]
training/holistic_migration/tests/test_evaluate.py::test_metrics_refuses_invalid_probability_or_output_mapping[mapping] PASSED [ 96%]
training/holistic_migration/tests/test_evaluate.py::test_metrics_refuses_invalid_probability_or_output_mapping[duplicate_ids] PASSED [ 97%]
training/holistic_migration/tests/test_evaluate.py::test_metrics_refuses_invalid_probability_or_output_mapping[classes] PASSED [ 98%]
training/holistic_migration/tests/test_evaluate.py::test_evaluation_report_failure_is_retained_and_cannot_rerun PASSED [100%]

=============================== warnings summary ===============================
training/holistic_migration/tests/test_train.py: 67 warnings
  /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/lib/python3.11/site-packages/keras/src/backend/tensorflow/core.py:172: DeprecationWarning: __array__ implementation doesn't accept a copy keyword, so passing copy=False failed. __array__ must implement 'dtype' and 'copy' keyword arguments.
    return np.array(x)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
- generated xml file: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/30-named.xml -
======================= 75 passed, 67 warnings in 21.63s =======================

## 31-full-migration-suite
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/migration-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/31-migration.xml`
- Exit: 0. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/31-full-migration-suite.log`; source-bound receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/31-full-migration-suite.json`.
- Result:
ault 
training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_first_report_fault_survives_later_close_fault PASSED [ 97%]
training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_healthy_report_and_primary_without_output_fault_controls 
training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_healthy_report_and_primary_without_output_fault_controls PASSED [ 98%]
training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_prior_cleanup_failure_is_not_replaced_by_diagnostic_stderr PASSED [ 98%]
training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_source_and_detector_retain_both_report_faults_in_order 
training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_source_and_detector_retain_both_report_faults_in_order PASSED [ 98%]
training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_source_primary_survives_diagnostic_stderr_and_closes_report PASSED [ 98%]
training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_source_primary_survives_report_close PASSED [ 99%]
training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_source_primary_survives_report_flush PASSED [ 99%]
training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_source_primary_survives_report_serialization PASSED [ 99%]
training/holistic_migration/tests/test_webcam.py::FinalizationPrecedenceTests::test_source_primary_survives_report_write PASSED [100%]

=============================== warnings summary ===============================
training/holistic_migration/tests/test_train.py: 67 warnings
  /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/lib/python3.11/site-packages/keras/src/backend/tensorflow/core.py:172: DeprecationWarning: __array__ implementation doesn't accept a copy keyword, so passing copy=False failed. __array__ must implement 'dtype' and 'copy' keyword arguments.
    return np.array(x)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
- generated xml file: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/31-migration.xml -
======= 360 passed, 67 warnings, 293 subtests passed in 71.71s (0:01:11) =======

## 32-original-training-suite
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/tests -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/original-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/32-original.xml`
- Exit: 0. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/32-original-training-suite.log`; source-bound receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/32-original-training-suite.json`.
- Result:
und_hashes PASSED [ 90%]
training/tests/test_validation_campaign.py::BackendTests::test_backend_uses_inference_only_then_existing_candidate_and_checks_shapes PASSED [ 92%]
training/tests/test_validation_campaign.py::ResidencyTests::test_dataless_sources_fail_before_a_blocking_content_read PASSED [ 94%]
training/tests/test_validation_campaign.py::CliTests::test_cli_requires_bound_strict_config_and_fixed_safe_errors PASSED [ 96%]
training/tests/test_validation_campaign.py::DiagnosticTests::test_diagnostics_all_classes_counts_and_conversion_drift PASSED [ 98%]
training/tests/test_validation_campaign.py::ProbabilityTests::test_probability_boundary_rejects_shape_type_and_nonfinite 
training/tests/test_validation_campaign.py::ProbabilityTests::test_probability_boundary_rejects_shape_type_and_nonfinite PASSED [100%]

=============================== warnings summary ===============================
training/tests/test_export_frozen.py::FrozenExportTests::test_frozen_export_preserves_validation_predictions_and_hashes
training/tests/test_export_frozen.py::FrozenExportTests::test_frozen_export_preserves_validation_predictions_and_hashes
  /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/lib/python3.11/site-packages/keras/src/backend/tensorflow/core.py:172: DeprecationWarning: __array__ implementation doesn't accept a copy keyword, so passing copy=False failed. __array__ must implement 'dtype' and 'copy' keyword arguments.
    return np.array(x)

training/tests/test_export_frozen.py::FrozenExportTests::test_frozen_export_preserves_validation_predictions_and_hashes
  /Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/lib/python3.11/site-packages/tensorflow/lite/python/interpreter.py:457: UserWarning:     Warning: tf.lite.Interpreter is deprecated and is scheduled for deletion in
      TF 2.20. Please use the LiteRT interpreter from the ai_edge_litert package.
      See the [migration guide](https://ai.google.dev/edge/litert/migration)
      for details.
      
    warnings.warn(_INTERPRETER_DELETION_WARNING)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
- generated xml file: /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/32-original.xml -
============= 51 passed, 3 warnings, 289 subtests passed in 13.32s =============

## 33-cli-help-0
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m training.holistic_migration.train --help`
- Exit: 0. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/33-cli-help-0.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/33-cli-help-0.json`.
- Result: usage: train.py [-h] {tiny-fit,fit} ...

Isolated admitted hm153 training; no synthetic CLI bypass

positional arguments:
  {tiny-fit,fit}

options:
  -h, --help      show this help message and exit

## 33-cli-help-1
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m training.holistic_migration.train tiny-fit --help`
- Exit: 0. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/33-cli-help-1.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/33-cli-help-1.json`.
- Result: usage: train.py tiny-fit [-h] --bundle BUNDLE --admission ADMISSION --output
                         OUTPUT

options:
  -h, --help            show this help message and exit
  --bundle BUNDLE
  --admission ADMISSION
  --output OUTPUT

## 33-cli-help-2
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m training.holistic_migration.train fit --help`
- Exit: 0. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/33-cli-help-2.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/33-cli-help-2.json`.
- Result: usage: train.py fit [-h] --bundle BUNDLE --admission ADMISSION --output OUTPUT
                    --tiny-proof TINY_PROOF

options:
  -h, --help            show this help message and exit
  --bundle BUNDLE
  --admission ADMISSION
  --output OUTPUT
  --tiny-proof TINY_PROOF

## 33-cli-help-3
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m training.holistic_migration.evaluate --help`
- Exit: 0. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/33-cli-help-3.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/33-cli-help-3.json`.
- Result: usage: evaluate.py [-h] --run RUN --bundle BUNDLE --admission ADMISSION
                   --output OUTPUT

Frozen exploratory reused-test evaluation; never tune/select

options:
  -h, --help            show this help message and exit
  --run RUN
  --bundle BUNDLE
  --admission ADMISSION
  --output OUTPUT

## 34-cli-synthetic-denied-tiny-fit
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m training.holistic_migration.train tiny-fit --bundle /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/named-fixtures/test_actual_train_cli_syntheti0/bundle --admission /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/named-fixtures/test_actual_train_cli_syntheti0/bundle-synthetic-admission.json --output /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/cli-denied-tiny-fit`
- Exit: 2. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/34-cli-synthetic-denied-tiny-fit.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/34-cli-synthetic-denied-tiny-fit.json`.
- Result: usage: train.py [-h] {tiny-fit,fit} ...
train.py: error: admission status mismatch

## 34-cli-synthetic-denied-fit
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m training.holistic_migration.train fit --bundle /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/named-fixtures/test_actual_train_cli_syntheti0/bundle --admission /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/named-fixtures/test_actual_train_cli_syntheti0/bundle-synthetic-admission.json --output /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/cli-denied-fit --tiny-proof /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/absent-real-proof.json`
- Exit: 2. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/34-cli-synthetic-denied-fit.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/34-cli-synthetic-denied-fit.json`.
- Result: usage: train.py [-h] {tiny-fit,fit} ...
train.py: error: admission status mismatch

## 35-cli-synthetic-denied-evaluation
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m training.holistic_migration.evaluate --run /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/absent-frozen-run --bundle /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/named-fixtures/test_actual_train_cli_syntheti0/bundle --admission /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/named-fixtures/test_actual_train_cli_syntheti0/bundle-synthetic-admission.json --output /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/cli-denied-evaluation`
- Exit: 2. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/35-cli-synthetic-denied-evaluation.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/35-cli-synthetic-denied-evaluation.json`.
- Result: usage: evaluate.py [-h] --run RUN --bundle BUNDLE --admission ADMISSION
                   --output OUTPUT
evaluate.py: error: admission status mismatch

## 36-cli-no-synthetic-bypass
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m training.holistic_migration.train tiny-fit --bundle /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/named-fixtures/test_actual_train_cli_syntheti0/bundle --admission /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/named-fixtures/test_actual_train_cli_syntheti0/bundle-synthetic-admission.json --output /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/cli-bypass-never-created --allow-synthetic`
- Exit: 2. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/36-cli-no-synthetic-bypass.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/36-cli-no-synthetic-bypass.json`.
- Result: usage: train.py [-h] {tiny-fit,fit} ...
train.py: error: unrecognized arguments: --allow-synthetic

## 37-runtime-device-readback
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -c 'import tensorflow as tf,json,importlib.metadata,sys; print(json.dumps({'"'"'tensorflow'"'"':tf.__version__,'"'"'keras'"'"':importlib.metadata.version('"'"'keras'"'"'),'"'"'numpy'"'"':importlib.metadata.version('"'"'numpy'"'"'),'"'"'executable'"'"':sys.executable,'"'"'physical_devices'"'"':[(v.name,v.device_type) for v in tf.config.list_physical_devices()],'"'"'gpus'"'"':len(tf.config.list_physical_devices('"'"'GPU'"'"'))},indent=2)); assert not tf.config.list_physical_devices('"'"'GPU'"'"')'`
- Exit: 0. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/37-runtime-device-readback.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/37-runtime-device-readback.json`.
- Result: {
  "tensorflow": "2.19.0",
  "keras": "3.15.1",
  "numpy": "2.1.3",
  "executable": "/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python",
  "physical_devices": [
    [
      "/physical_device:CPU:0",
      "CPU"
    ]
  ],
  "gpus": 0
}

## 38-source-protection-readback
- Command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -c 'from pathlib import Path
import hashlib,json,subprocess,sys
from training.holistic_migration import dataset as d
from training.holistic_migration import train as t
r=d.REPO
p=r.parent/'"'"'holistic-migration-data/evidence/task-d-preflight-20261113/protected.json'"'"'
receipt=json.loads(p.read_text())
protected={k:d.sha256(r/k) for k in receipt['"'"'protected_sha256'"'"']}
assert protected==receipt['"'"'protected_sha256'"'"']
owned={k:d.sha256(r/k) for k in receipt['"'"'owned_additions'"'"']}
assert len(owned)==8
assert d.canonical_hash(d.contract_binding())==receipt['"'"'extraction_contract_sha256'"'"']
cache=[str(p.relative_to(r)) for p in (r/'"'"'training/holistic_migration'"'"').rglob('"'"'*'"'"') if p.name=='"'"'__pycache__'"'"' or p.suffix=='"'"'.pyc'"'"' or p.name=='"'"'.pytest_cache'"'"']
assert not cache,cache
tracked=subprocess.run(['"'"'git'"'"','"'"'diff'"'"','"'"'--exit-code'"'"'],cwd=r,capture_output=True,text=True)
index=subprocess.run(['"'"'git'"'"','"'"'diff'"'"','"'"'--cached'"'"','"'"'--exit-code'"'"'],cwd=r,capture_output=True,text=True)
assert tracked.returncode==index.returncode==0
print(json.dumps(dict(owned_sha256=owned,protected_sha256=protected,protected_count=len(protected),source_contract_sha256=d.canonical_hash(d.contract_binding()),source_sha256=t.source_binding(),runtime=t.training_runtime(),runtime_sha256=d.canonical_hash(t.training_runtime()),tracked_diff_empty=True,index_diff_empty=True,migration_cache_paths=cache,branch=subprocess.check_output(['"'"'git'"'"','"'"'branch'"'"','"'"'--show-current'"'"'],cwd=r,text=True).strip(),head=subprocess.check_output(['"'"'git'"'"','"'"'rev-parse'"'"','"'"'HEAD'"'"'],cwd=r,text=True).strip()),indent=2))
'`
- Exit: 0. Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/38-source-protection-readback.log`; source-bound execution: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/38-source-protection-readback.json`.
- Result: bd",
    "docs/holistic-migration/task-b-report.md": "631e478663154804298944f33475825831de2c46bdd2934edfcf38dc9cf3f319",
    "docs/holistic-migration/task-c-report.md": "2fa276f075f813cec4aadc6526b8473ddf03b6db4b225cf1fbf8a408ca3f0c82",
    "training/models/train_cnn_lstm.py": "a5560e5dec1e8ef68d46a7e1ed739c864b98f68b8575f0c491a7a9f3d02536c1",
    "training/models/evaluation_protocol.py": "9fba8862e7f9aca098f98c485777d9dd9f8ba0a3d502838274461f02c366e116",
    "training/preprocessing/selected_classes.json": "e8089f5c0186bfe6fd9ec63a5150f8094645c1686509f23c1716453b5f9ce0d5",
    "HOLISTIC_MIGRATION_PLAN.md": "2b9a1668588938d20d0b51504206fba71bbc07a5fb0cda307e1b22079673bc1a",
    "docs/holistic-migration/task-d-brief.md": "7610d3c2512e89a3f30a47a584192b9b97f214eaa97d6944a67d6ca5bc6874ee"
  },
  "protected_count": 36,
  "source_contract_sha256": "944e7b7acb495899bd78a937d3a453e2e188812c9a747ce05b9667537ccb15bc",
  "source_sha256": {
    "train.py": "fc110ad83500cb8e58b70658357d717a8dfbf50c2d2e09abaa1b25062c44ec91",
    "augmentation.py": "2920c5c8ce4f215cc39747c7b6151bd825c825dcbfcc5408c3fdb7f025a756ce",
    "evaluate.py": "2a42016419bd81892367fc9379761c98be023ddc99195dedf4587e69724c97cf"
  },
  "runtime": {
    "python": "3.11.15 (main, Mar  3 2026, 00:52:57) [Clang 17.0.0 (clang-1700.6.3.2)]",
    "executable": "/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python",
    "packages": {
      "numpy": "2.1.3",
      "tensorflow": "2.19.0",
      "keras": "3.15.1"
    }
  },
  "runtime_sha256": "bdb65f6de0750899ef9fafbc6def514619aa938d060047c40b3c0c98c9536c8c",
  "tracked_diff_empty": true,
  "index_diff_empty": true,
  "migration_cache_paths": [],
  "branch": "holistic-migration",
  "head": "4d901693642af5f572455b2c75ba095b0ec65c7f"
}

## Verified suite counts and retained synthetic evidence
- Named new tests:75 collected/passed,67 unsuppressed upstream Keras warnings, exit0.
- Full migration:360 collected/passed plus293 passed subtests,67 warnings, exit0.
- Original training:51 collected/passed plus289 passed subtests,3 original warnings, exit0.
- JUnit counts653/340 include main cases plus subtests; they are not new-case totals. All three XMLs have zero failures/errors/skips.
- Source bindings of all7 non-report additions match each final suite execution. The report is intentionally append-only and self-hashed only in external handoff.
- Standalone production CLI help exits0; synthetic admissions for tiny-fit/fit/evaluate exit2 before output. Complete-argument --allow-synthetic invocation exits2 as unrecognized.
- Runtime device readback: TF2.19.0/Keras3.15.1/NumPy2.1.3, CPU only, zero GPUs; subprocess thread limits1. No warnings suppressed.
- A retention glob initially missed pytest’s truncated30-character fixture directory name; corrected only the evidence selector. No product/test/source failure or rerun was hidden.
- Retained actual synthetic history: tiny1 epoch/1 optimizer step (fails memorization, no proof); full1 epoch/4 actual optimizer steps through explicit trusted synthetic proof seam. Architecture forward/optimizer/save-reload1 step also retained. Oracle successful proof/lifecycle evidence stays explicitly synthetic.
- Summary: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2/verification-summary.json`.

## Final preparation delivery and parent gates

Implemented exactly the8 owned additions named in the brief: three production modules, three new test modules, TRAINING.md and this append-only report. No existing/protected source was edited. The production CLI is admitted-real-data-only; internal synthetic seams are not exposed by CLI.

Executable scope: lazy fixed250674-parameter CNN-LSTM50/30x153, strict fit/validation-only canonical admission, masked fit-only rotation, retained tiny proof and fresh full-fit lifecycle, exclusive validation-only selection and separate frozen exploratory reused-test evaluator. Tests include real bounded TF computation and save/reload; oracle and fault seams remain explicitly synthetic. The actual one-step synthetic tiny model did NOT meet memorization and emitted no tiny proof. The bounded actual synthetic full-lifecycle test used an explicitly patched synthetic proof seam, not a successful real tiny proof.

Verification:75 named new cases;360 full migration cases plus293 subtests;51 original cases plus289 subtests, all exit0.67 upstream Keras/NumPy warnings in new/migration suites and3 original warnings are unsuppressed. Original suite synthetic conversion checks are regression execution, not production D export/activation. Standalone CLI refusal/help outputs and source-bound execution receipts are retained externally.

Safety readback: all36 protected hashes match the original parent receipt; C contract remains `944e7b7acb495899bd78a937d3a453e2e188812c9a747ce05b9667537ccb15bc`; git tracked/index diffs empty; migration source has no pyc/__pycache__/.pytest_cache. Branch/head remain holistic-migration/4d901693642af5f572455b2c75ba095b0ec65c7f. No actual-source array/video/weights, camera/GUI/phone/app/participant store, installs/provider changes or commits/pushes were used. Existing camera/webcam regression tests are synthetic/owned-process tests, not camera access.

Remaining external gates (NOT executed or granted): parent independent D review/acceptance; full actual-source support and dataset admission; real-source tiny fitting/checkpoint proof; real all50 full fitting/selection; real separate exploratory test inference; expert/anatomical/linguistic/signer-independent, live owner/physical, research and deployment authorization. Negatives/FAR remain unmeasured/null and live_ready=false. No D software acceptance is granted by this worker. No source implementation slice is being deferred; these are intentionally unopened real-data/human gates.

Trust limitation: in-process callbacks/local hashes cannot establish signed provenance or an OS security sandbox. Failed/incomplete runs remain retained rather than retried or erased. The warnings and explicit synthetic full-proof seam must not be relabeled as actual-source learning evidence.

## Final identities and immutable handoff

The following7 non-report additions are source-frozen and match all final suite receipts. This report's final SHA256 is in the external handoff, avoiding a self-referential digest:

```json
{
  "training/holistic_migration/train.py": "fc110ad83500cb8e58b70658357d717a8dfbf50c2d2e09abaa1b25062c44ec91",
  "training/holistic_migration/evaluate.py": "2a42016419bd81892367fc9379761c98be023ddc99195dedf4587e69724c97cf",
  "training/holistic_migration/augmentation.py": "2920c5c8ce4f215cc39747c7b6151bd825c825dcbfcc5408c3fdb7f025a756ce",
  "training/holistic_migration/tests/test_train.py": "ea4a38b86ae1f9a5887a17a89f3c72178b0215657b5b7c380a1d9b4faeeee2b1",
  "training/holistic_migration/tests/test_evaluate.py": "99060e69827ce7fe4998a2ee5e31556cac1a2e20108ef2a15190606416203e4d",
  "training/holistic_migration/tests/test_augmentation.py": "486ea9ff63427445ab32057e9e5ff334b609b63507d97ab99cc95b8449d131a6",
  "training/holistic_migration/TRAINING.md": "e2e9e0e729b86da8e6301fa680dbf47f87f7699e46b58b77eb7e5c4b9cd1a22f"
}
```

Training runtime SHA256: `bdb65f6de0750899ef9fafbc6def514619aa938d060047c40b3c0c98c9536c8c`. Runtime: Python3.11.15, TensorFlow2.19.0, Keras3.15.1, NumPy2.1.3, approved executable, CPU-only, threads1. Exact runtime/protected36/source8 tables and receipt binding are in the handoff. Parent protection receipt SHA256 remains `037bbff5eaae485560fe24f6f7a16c715d74fe65ca923d480b64811dede0900e`.

Exclusive external handoff directory: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-worker-stfd65f2`.
- Frozen verifiable delivery receipt: `handoff.json` (its exact SHA256 is returned directly to the parent).
- Immutable source/evidence/synthetic-artifact archive: `task-d-handoff.tar.gz`, with archive hash/size/member inventory in handoff.json.
- `handoff-inventory.json`: exact archive member hashes including all8 source additions; final report hash is bound here and in handoff.json.
- Archive includes incremental commands/exits/logs, final suite XMLs/summary, protection readback, this report/docs/tests, and selected explicitly synthetic actual-TF/oracle lifecycle artifacts. Source_video data and historical/real model artifacts are excluded.
- Archive, inventory and delivery receipt are exclusively created, read back and set read-only. Read-only mode/local hashes are accidental-change protection, not OS immutability or a signature. No source/report edits follow this freeze; parent must independently check all hashes and review before real optimization.

## Bounded repair 1 recovery — D-R1-001 (2026-11-14)

The historical handoff above remains unchanged evidence for its original source identity, not the corrected candidate. Authority: `task-d-fix-1-brief.md` and complete rejecting `task-d-review-1.json` (SHA256 `b4d2c103ac392233977c54bcecc191ab33b290b14556f1162b96b2b00b82f1b3`). Exactly three repository paths are editable: this append-only report, `evaluate.py`, and `tests/test_evaluate.py`. The nonblocking rising-validation-then-tie training suggestion is deferred; `test_train.py` is protected.

Before this first append, fresh verification matched all42 repair-protected hashes, all69 review input bindings, all8 owned preimages, all9 preserved snapshots, and the exact77458-byte report prefix (SHA256 `8371cc310cae092a7c8d013f1d4426d29a40624196c3a1aa4fe35075fe1f8963`). HEAD remains `4d901693642af5f572455b2c75ba095b0ec65c7f`; tracked/index diffs were empty. Actual verification command exited0; bounded output and full initial state are in the fresh exclusive external evidence directory `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/initial-verification.json`.

Root cause: the new attempt publishes its completion before final artifact verification, but its failure handler retains the completion; an existing-target readback later promotes that failed attempt. Parent already observed one intended behavioral RED (1 failure,0 errors, exit1), retained under `task-d-before-fix1-20261114`. This repair will first retain a permanent post-publication regression and observe its own RED, then make only the owned new-attempt cleanup fail closed and immediately rerun GREEN. Later already-passing controls are coverage-only GREEN, not manufactured RED. Fresh corrected-source suites will be separately bound; historical75/360/51-case receipts are not relabeled.

Execution is strictly synthetic and trusted in-process; no real canonical arrays, videos, model weights, optimization/inference/evaluation, SDK/camera/GUI/phone/participants, install/provider/config change, commit or push is authorized or performed. Test commands explicitly override the inherited system TMPDIR with approved Hermes scratch and use approved Python `-E -B`, CPU/thread limits and `-p no:cacheprovider`. No acceptance or real-data gate is granted.


### Repair1 executed tracer 01-permanent-red

- Started: `2026-11-14T05:27:29.844132+08:00`; ended: `2026-11-14T05:27:30.562246+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py::test_new_final_readback_failure_revokes_completion_and_blocks_retry -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/01-permanent-red-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/01-permanent-red.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit: 1; XML counts: `{"errors": 0, "failures": 1, "skipped": 0, "tests": 1}`; serialized cases: 1.
- Actual framework summary: `============================== 1 failed in 0.37s ===============================`.
- Receipt/raw log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/01-permanent-red.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/01-permanent-red.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/01-permanent-red.xml`.
- All42 protected hashes and historical report prefix still match; source postimages stable during execution: True. Exact source/runtime/C bindings are in the receipt.

### Repair1 executed tracer 02-permanent-green

- Started: `2026-11-14T05:27:58.005854+08:00`; ended: `2026-11-14T05:27:58.673471+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py::test_new_final_readback_failure_revokes_completion_and_blocks_retry -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/02-permanent-green-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/02-permanent-green.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit: 0; XML counts: `{"errors": 0, "failures": 0, "skipped": 0, "tests": 1}`; serialized cases: 1.
- Actual framework summary: `============================== 1 passed in 0.35s ===============================`.
- Receipt/raw log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/02-permanent-green.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/02-permanent-green.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/02-permanent-green.xml`.
- All42 protected hashes and historical report prefix still match; source postimages stable during execution: True. Exact source/runtime/C bindings are in the receipt.

### Repair1 executed tracer 03-diagnostic-red

- Started: `2026-11-14T05:28:25.368552+08:00`; ended: `2026-11-14T05:28:26.057944+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py::test_final_readback_primary_survives_failure_receipt_write_error -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/03-diagnostic-red-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/03-diagnostic-red.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit: 1; XML counts: `{"errors": 0, "failures": 1, "skipped": 0, "tests": 1}`; serialized cases: 1.
- Actual framework summary: `============================== 1 failed in 0.37s ===============================`.
- Receipt/raw log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/03-diagnostic-red.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/03-diagnostic-red.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/03-diagnostic-red.xml`.
- All42 protected hashes and historical report prefix still match; source postimages stable during execution: True. Exact source/runtime/C bindings are in the receipt.

### Repair1 executed tracer 04-diagnostic-green

- Started: `2026-11-14T05:28:41.921757+08:00`; ended: `2026-11-14T05:28:42.588472+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py::test_final_readback_primary_survives_failure_receipt_write_error -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/04-diagnostic-green-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/04-diagnostic-green.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit: 0; XML counts: `{"errors": 0, "failures": 0, "skipped": 0, "tests": 1}`; serialized cases: 1.
- Actual framework summary: `============================== 1 passed in 0.35s ===============================`.
- Receipt/raw log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/04-diagnostic-green.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/04-diagnostic-green.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/04-diagnostic-green.xml`.
- All42 protected hashes and historical report prefix still match; source postimages stable during execution: True. Exact source/runtime/C bindings are in the receipt.

### Repair1 executed tracer 05-cleanup-red

- Started: `2026-11-14T05:29:17.831380+08:00`; ended: `2026-11-14T05:29:18.504946+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py::test_failed_final_readback_cannot_promote_when_owned_marker_unlink_fails -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/05-cleanup-red-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/05-cleanup-red.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit: 1; XML counts: `{"errors": 0, "failures": 1, "skipped": 0, "tests": 1}`; serialized cases: 1.
- Actual framework summary: `============================== 1 failed in 0.37s ===============================`.
- Receipt/raw log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/05-cleanup-red.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/05-cleanup-red.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/05-cleanup-red.xml`.
- All42 protected hashes and historical report prefix still match; source postimages stable during execution: True. Exact source/runtime/C bindings are in the receipt.

### Repair1 executed tracer 06-cleanup-green

- Started: `2026-11-14T05:29:37.130874+08:00`; ended: `2026-11-14T05:29:37.858271+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py::test_failed_final_readback_cannot_promote_when_owned_marker_unlink_fails -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/06-cleanup-green-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/06-cleanup-green.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit: 0; XML counts: `{"errors": 0, "failures": 0, "skipped": 0, "tests": 1}`; serialized cases: 1.
- Actual framework summary: `============================== 1 passed in 0.42s ===============================`.
- Receipt/raw log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/06-cleanup-green.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/06-cleanup-green.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/06-cleanup-green.xml`.
- All42 protected hashes and historical report prefix still match; source postimages stable during execution: True. Exact source/runtime/C bindings are in the receipt.

### Repair1 executed tracer 07-established-coverage-green

- Started: `2026-11-14T05:30:18.081601+08:00`; ended: `2026-11-14T05:30:18.846950+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py::test_established_completion_survives_transient_readback_failure -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/07-established-coverage-green-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/07-established-coverage-green.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit: 0; XML counts: `{"errors": 0, "failures": 0, "skipped": 0, "tests": 2}`; serialized cases: 2.
- Actual framework summary: `============================== 2 passed in 0.48s ===============================`.
- Receipt/raw log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/07-established-coverage-green.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/07-established-coverage-green.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/07-established-coverage-green.xml`.
- All42 protected hashes and historical report prefix still match; source postimages stable during execution: True. Exact source/runtime/C bindings are in the receipt.

### Repair1 executed tracer 08-publication-coverage-green

- Started: `2026-11-14T05:30:57.136523+08:00`; ended: `2026-11-14T05:30:57.744248+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py::test_completion_publication_failure_retains_evidence_without_success -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/08-publication-coverage-green-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/08-publication-coverage-green.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit: 0; XML counts: `{"errors": 0, "failures": 0, "skipped": 0, "tests": 1}`; serialized cases: 1.
- Actual framework summary: `============================== 1 passed in 0.35s ===============================`.
- Receipt/raw log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/08-publication-coverage-green.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/08-publication-coverage-green.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/08-publication-coverage-green.xml`.
- All42 protected hashes and historical report prefix still match; source postimages stable during execution: True. Exact source/runtime/C bindings are in the receipt.

### Repair1 executed tracer 09-new-owned-regressions

- Started: `2026-11-14T05:31:32.914465+08:00`; ended: `2026-11-14T05:31:34.207029+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py::test_new_final_readback_failure_revokes_completion_and_blocks_retry training/holistic_migration/tests/test_evaluate.py::test_final_readback_primary_survives_failure_receipt_write_error training/holistic_migration/tests/test_evaluate.py::test_failed_final_readback_cannot_promote_when_owned_marker_unlink_fails training/holistic_migration/tests/test_evaluate.py::test_established_completion_survives_transient_readback_failure training/holistic_migration/tests/test_evaluate.py::test_completion_publication_failure_retains_evidence_without_success -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/09-new-owned-regressions-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/09-new-owned-regressions.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit: 0; XML counts: `{"errors": 0, "failures": 0, "skipped": 0, "tests": 6}`; serialized cases: 6.
- Actual framework summary: `============================== 6 passed in 1.01s ===============================`.
- Receipt/raw log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/09-new-owned-regressions.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/09-new-owned-regressions.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/09-new-owned-regressions.xml`.
- All42 protected hashes and historical report prefix still match; source postimages stable during execution: True. Exact source/runtime/C bindings are in the receipt.

### Repair1 executed tracer 10-retained-parent-regression

- Started: `2026-11-14T05:31:34.390058+08:00`; ended: `2026-11-14T05:31:34.973611+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-before-fix1-20261114/test_parent_final_readback.py -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/10-retained-parent-regression-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/10-retained-parent-regression.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit: 0; XML counts: `{"errors": 0, "failures": 0, "skipped": 0, "tests": 1}`; serialized cases: 1.
- Actual framework summary: `============================== 1 passed in 0.33s ===============================`.
- Receipt/raw log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/10-retained-parent-regression.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/10-retained-parent-regression.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/10-retained-parent-regression.xml`.
- All42 protected hashes and historical report prefix still match; source postimages stable during execution: True. Exact source/runtime/C bindings are in the receipt.

### Repair1 executed tracer 11-full-evaluator

- Started: `2026-11-14T05:31:35.153549+08:00`; ended: `2026-11-14T05:31:37.699353+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/11-full-evaluator-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/11-full-evaluator.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit: 0; XML counts: `{"errors": 0, "failures": 0, "skipped": 0, "tests": 23}`; serialized cases: 23.
- Actual framework summary: `============================== 23 passed in 2.28s ==============================`.
- Receipt/raw log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/11-full-evaluator.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/11-full-evaluator.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/11-full-evaluator.xml`.
- All42 protected hashes and historical report prefix still match; source postimages stable during execution: True. Exact source/runtime/C bindings are in the receipt.

### Repair1 executed tracer 12-all-D-modules

- Started: `2026-11-14T05:31:37.882635+08:00`; ended: `2026-11-14T05:31:55.953398+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py training/holistic_migration/tests/test_evaluate.py training/holistic_migration/tests/test_augmentation.py -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/12-all-D-modules-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/12-all-D-modules.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit: 0; XML counts: `{"errors": 0, "failures": 0, "skipped": 0, "tests": 81}`; serialized cases: 81.
- Actual framework summary: `======================= 81 passed, 67 warnings in 17.08s =======================`.
- Receipt/raw log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/12-all-D-modules.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/12-all-D-modules.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/12-all-D-modules.xml`.
- All42 protected hashes and historical report prefix still match; source postimages stable during execution: True. Exact source/runtime/C bindings are in the receipt.

### Repair1 executed tracer 13-full-migration

- Started: `2026-11-14T05:31:56.149626+08:00`; ended: `2026-11-14T05:32:56.513827+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/13-full-migration-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/13-full-migration.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit: 0; XML counts: `{"errors": 0, "failures": 0, "skipped": 0, "tests": 659}`; serialized cases: 366.
- Actual framework summary: `============ 366 passed, 67 warnings, 293 subtests passed in 59.30s ============`.
- Receipt/raw log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/13-full-migration.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/13-full-migration.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/13-full-migration.xml`.
- All42 protected hashes and historical report prefix still match; source postimages stable during execution: True. Exact source/runtime/C bindings are in the receipt.

### Repair1 executed tracer 14-original-training

- Started: `2026-11-14T05:32:56.715287+08:00`; ended: `2026-11-14T05:33:05.438288+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/tests -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/14-original-training-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/14-original-training.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit: 0; XML counts: `{"errors": 0, "failures": 0, "skipped": 0, "tests": 340}`; serialized cases: 51.
- Actual framework summary: `============= 51 passed, 3 warnings, 289 subtests passed in 7.96s ==============`.
- Receipt/raw log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/14-original-training.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/14-original-training.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/14-original-training.xml`.
- All42 protected hashes and historical report prefix still match; source postimages stable during execution: True. Exact source/runtime/C bindings are in the receipt.

## Repair1 source-frozen results and handoff boundary

All three vertical slices observed intended product RED (1 failure,0 errors/skips, exit1 each) before their minimal production change, followed immediately by GREEN (1 pass each). Slice01 reproduces the review fault after publication and verifies exact evidence/frozen-run retention and later denial. Slice03 preserves the primary exception when failure-receipt writing fails. Slice05 preserves the primary through owned-marker unlink failure and uses the retained failure disposition to deny later promotion. These are separate executed stages, not retroactive claims.

Established-completion transient read faults (completion JSON and report hash) and completion-publication failure were coverage-only GREEN:2 cases and1 case respectively, with no extra production change. Existing healthy completed-target retry, incomplete-target denial and pre-publication reporter failure tests remain intact and passed in the full evaluator suite. One ambiguous targeted patch was refused without changing a file; there were no test harness/setup errors or hidden retries.

| Corrected-stage suite | Cases | Subtests | Warnings | Exit |
|---|---:|---:|---:|---:|

| 09-new-owned-regressions | 6 | 0 | 0 | 0 |

| 10-retained-parent-regression | 1 | 0 | 0 | 0 |

| 11-full-evaluator | 23 | 0 | 0 | 0 |

| 12-all-D-modules | 81 | 0 | 67 | 0 |

| 13-full-migration | 366 | 293 | 67 | 0 |

| 14-original-training | 51 | 289 | 3 | 0 |


Each corrected-stage suite has0 failures/errors/skips. XML aggregate tests include subtests (migration659 versus366 serialized cases; original340 versus51 cases); the table separates them. Original parent regression bytes remain SHA256 `f2c3e1f252c02fd5564046bdab3aff38090c9491f5d8f45c0457d7a5cef33539` and were rerun successfully against corrected sources. All commands, exact starts/ends, exits, raw logs/XML and fresh retained synthetic fixtures are bound in `suite-summary.json`/`final-verification.json` and individual command receipts.

Warnings were retained, not hidden: D/migration67 Keras TensorFlow-backend NumPy-copy DeprecationWarnings; original3 warnings comprise two of that DeprecationWarning plus one tf.lite.Interpreter deprecation UserWarning. This matches the historical warning counts. Full suites exercise only explicitly synthetic TF steps/checkpoint lifecycles; the actual synthetic tiny run does not establish memorization or a real proof, and the bounded full lifecycle retains its explicit trusted synthetic proof seam. No actual-source arrays/models, real fitting/evaluation, device/SDK/camera/GUI/phone/participants or installations were used.

Final production behavior: the owned new completion marker is revoked on final readback failure. If unlink itself fails, a retained failure receipt makes the residual marker non-gating; if diagnostic writing alone fails, successful unlink still leaves an incomplete target. Existing completed-target calls run outside new-attempt cleanup and never rewrite/delete established completion on a transient read fault. Pending files, predictions/IDs/report/start and frozen selection remain retained. Local filesystem inability to perform BOTH revocation and failure-disposition persistence, process death during publication, hostile concurrent writers and permanent media failure are not crash-durability/sandbox guarantees established by these trusted in-process tests. The original primary is preserved through tested ordinary cleanup/diagnostic I/O faults.

Exactly3 changed repository postimages; all42 protected inputs unchanged, all9 old snapshots intact, all69 review bindings verified against unchanged inputs or explicitly historical preimages for the3 repaired paths. Historical report prefix remains exact77458 bytes/SHA256 `8371cc310cae092a7c8d013f1d4426d29a40624196c3a1aa4fe35075fe1f8963`. Corrected evaluator SHA256 `67e42ac9ff6bcbc83488ac70663652e8a9bb847ee4dadfe2942be277a7df0fcf`; corrected evaluator tests SHA256 `2cc0d5ec312084b1037e3337f2d2fd69873974d52b0d0778ef87d9a8765091e1`. Report final hash is external to avoid self-reference.

Training runtime SHA256 `bdb65f6de0750899ef9fafbc6def514619aa938d060047c40b3c0c98c9536c8c`; C contract SHA256 `944e7b7acb495899bd78a937d3a453e2e188812c9a747ce05b9667537ccb15bc` remains unchanged and excludes the three D repair paths. Source/runtime/config/dataset identities from old successful receipts are historical, not rewritten as current. HEAD remains `4d901693642af5f572455b2c75ba095b0ec65c7f`, tracked/index diffs empty and migration cache paths absent. All seven non-report D sources match corrected-stage command receipts; this report is append-only and separately frozen after the executions.

Fresh exclusive external handoff: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix1-worker-_ftezbzp/handoff.json`; exact3 postimages and preimage-to-postimage diff are retained under `postimages/` and `changed.diff`; every fresh evidence artifact is hash-indexed in `evidence-inventory.json`. The handoff binds that inventory, all14 command receipts, raw logs/XML, source/runtime/C/protection/prefix identities and limitations. Parent must independently verify the handoff and obtain complete affected-file spec/quality re-review. The nonblocking rising-validation-then-tie suggestion stays deferred; protected `test_train.py` was not edited. No acceptance, dataset admission, real tiny/full training, reused-test authorization, activation/export, expert/anatomical/linguistic/signer-independent, physical/live/deployment/research or participant approval is granted.


## Recovery / bounded repair2 D-R2-001

Verified at `2026-11-14T07:39:45.141457+08:00` before any append or source edit:49 protected paths,9 snapshots and8 current D postimages exact. Entire114202-byte report prefix SHA256 `487a9a49f58d91c8c9b5f08fa8b7b2eebe5f98e1baf63feb14b5322b7a15c281` retained. Fresh exclusive evidence: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct`; verification `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/recovery-verification.json`. Tracked/index diffs empty; no migration pyc/cache.

Complete review2 SHA256 `5a2deb33961787c6bed3611d2fefeb88f0bae81c2107a322c1aaebeac75fb3be` rejects solely D-R2-001; D-R1-001 remains resolved. This is repair2 of2, not a third repair or acceptance. Exact primary publication/readback object must survive an actual owned cleanup fault. Protected C publisher will not be modified or globally replaced. Permanent exact combined-fault regression will reach behavioral RED before evaluator-only minimal GREEN; already-passing variants remain coverage-only. All execution explicit synthetic, existing venv -E -B, approved scratch and deterministic thread limits. No actual-source arrays/models, native/device SDK operations, real optimization/inference/evaluation, installs/config changes or git writes.

Retain prior evidence and original receipts with their historical source identities. Meaningful new synthetic tracer fixtures/checkpoints stay external; broad-suite duplicates will be inventoried then reduced only inside this fresh evidence directory if needed. Parent verification and complete independent affected-scope re-review remain mandatory; a further blocker requires owner decision. Simultaneous permanent persistence failure, hostile-writer races and crash durability remain explicit limits.

### Repair2 executed tracer 01-combined-fault-red

- Started `2026-11-14T07:41:31.899065+08:00`; ended `2026-11-14T07:41:32.664547+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py::test_completion_publication_primary_survives_actual_cleanup_fault -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/01-combined-fault-red-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/01-combined-fault-red.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit 1; XML counts `{"errors": 0, "failures": 1, "skipped": 0, "tests": 1}`; serialized cases 1; passed subtests 0; warnings 0.
- Actual summary: `============================== 1 failed in 0.42s ===============================`.
- Receipt/log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/01-combined-fault-red.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/01-combined-fault-red.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/01-combined-fault-red.xml`. Fresh synthetic fixtures `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/01-combined-fault-red-fixtures` retained in place, not duplicated into archives.
-49 protected hashes,9 historical snapshots, all unchanged scope files and114202-byte prefix verified; source stable True. Training runtime `bdb65f6de0750899ef9fafbc6def514619aa938d060047c40b3c0c98c9536c8c`, C contract `944e7b7acb495899bd78a937d3a453e2e188812c9a747ce05b9667537ccb15bc`; exact stage source hashes bound in receipt.

### Repair2 executed tracer 02-combined-fault-green

- Started `2026-11-14T07:42:01.937978+08:00`; ended `2026-11-14T07:42:02.651121+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py::test_completion_publication_primary_survives_actual_cleanup_fault -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/02-combined-fault-green-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/02-combined-fault-green.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit 0; XML counts `{"errors": 0, "failures": 0, "skipped": 0, "tests": 1}`; serialized cases 1; passed subtests 0; warnings 0.
- Actual summary: `============================== 1 passed in 0.38s ===============================`.
- Receipt/log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/02-combined-fault-green.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/02-combined-fault-green.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/02-combined-fault-green.xml`. Fresh synthetic fixtures `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/02-combined-fault-green-fixtures` retained in place, not duplicated into archives.
-49 protected hashes,9 historical snapshots, all unchanged scope files and114202-byte prefix verified; source stable True. Training runtime `bdb65f6de0750899ef9fafbc6def514619aa938d060047c40b3c0c98c9536c8c`, C contract `944e7b7acb495899bd78a937d3a453e2e188812c9a747ce05b9667537ccb15bc`; exact stage source hashes bound in receipt.

Repair2 tracer01 reached exact intended behavioral RED (secondary PermissionError instead of original OSError),1 failure/0 errors/exit1; tracer02 immediate GREEN1 case/exit0. Injection after final link/pending, failed cleanup, retained evidence, unchanged frozen selection and blocked retry were reached before the identity assertion. Evaluator-owned exclusive staging preserves the active primary directly, not by inspecting arbitrary exception context. Source snapshots for both stages are separately bound in initial-stage-source-snapshots.json. One no-op identical patch attempt before test addition performed no write; no test harness errors.

Repair2 preflight interruption before tracer03: no pytest process started; not product RED. Extra unchanged-scope check detected external unowned PROGRESS.md change from `7c8c86740665899142b407fc10d1a027d83b1ebf81138785bc50295e7fd3e004` to `c95ae9c10b27c736bf9216588a30fcc63d99c594d28c7a876017546ce50f2d21`. Worker has never written that path and will not revert it;49protected files and9snapshots remain exact. Evidence `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/external-unowned-drift.json`. Preserve and bind the concurrent change separately for parent reconciliation; it is not an authorized worker fourth path. One ambiguous atomic test-parametrization patch was refused without writing and then uniquely reapplied.

### Repair2 executed tracer 03-report-combined-red

- Started `2026-11-14T07:44:37.406123+08:00`; ended `2026-11-14T07:44:38.116832+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider 'training/holistic_migration/tests/test_evaluate.py::test_completion_publication_primary_survives_actual_cleanup_fault[report.json]' -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/03-report-combined-red-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/03-report-combined-red.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit 1; XML counts `{"errors": 0, "failures": 1, "skipped": 0, "tests": 1}`; serialized cases 1; passed subtests 0; warnings 0.
- Actual summary: `============================== 1 failed in 0.39s ===============================`.
- Receipt/log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/03-report-combined-red.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/03-report-combined-red.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/03-report-combined-red.xml`. Fresh synthetic fixtures `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/03-report-combined-red-fixtures` retained in place, not duplicated into archives.
-49 protected hashes,9 historical snapshots, unchanged scope files (except separately bound external PROGRESS.md drift) and114202-byte prefix verified; source stable True. Training runtime `bdb65f6de0750899ef9fafbc6def514619aa938d060047c40b3c0c98c9536c8c`, C contract `944e7b7acb495899bd78a937d3a453e2e188812c9a747ce05b9667537ccb15bc`; exact stage source hashes bound in receipt.

### Repair2 executed tracer 04-report-combined-green

- Started `2026-11-14T07:44:49.054547+08:00`; ended `2026-11-14T07:44:49.724012+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider 'training/holistic_migration/tests/test_evaluate.py::test_completion_publication_primary_survives_actual_cleanup_fault[report.json]' -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/04-report-combined-green-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/04-report-combined-green.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit 0; XML counts `{"errors": 0, "failures": 0, "skipped": 0, "tests": 1}`; serialized cases 1; passed subtests 0; warnings 0.
- Actual summary: `============================== 1 passed in 0.36s ===============================`.
- Receipt/log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/04-report-combined-green.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/04-report-combined-green.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/04-report-combined-green.xml`. Fresh synthetic fixtures `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/04-report-combined-green-fixtures` retained in place, not duplicated into archives.
-49 protected hashes,9 historical snapshots, unchanged scope files (except separately bound external PROGRESS.md drift) and114202-byte prefix verified; source stable True. Training runtime `bdb65f6de0750899ef9fafbc6def514619aa938d060047c40b3c0c98c9536c8c`, C contract `944e7b7acb495899bd78a937d3a453e2e188812c9a747ce05b9667537ccb15bc`; exact stage source hashes bound in receipt.

### Repair2 executed tracer 05-context-ownership-coverage-green

- Started `2026-11-14T07:45:36.000536+08:00`; ended `2026-11-14T07:45:36.480077+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py::test_owned_publication_keeps_primary_with_unrelated_context training/holistic_migration/tests/test_evaluate.py::test_owned_publication_never_overwrites_or_cleans_unowned_destination -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/05-context-ownership-coverage-green-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/05-context-ownership-coverage-green.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit 0; XML counts `{"errors": 0, "failures": 0, "skipped": 0, "tests": 14}`; serialized cases 14; passed subtests 0; warnings 0.
- Actual summary: `============================== 14 passed in 0.21s ==============================`.
- Receipt/log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/05-context-ownership-coverage-green.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/05-context-ownership-coverage-green.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/05-context-ownership-coverage-green.xml`. Fresh synthetic fixtures `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/05-context-ownership-coverage-green-fixtures` retained in place, not duplicated into archives.
-49 protected hashes,9 historical snapshots, unchanged scope files (except separately bound external PROGRESS.md drift) and114202-byte prefix verified; source stable True. Training runtime `bdb65f6de0750899ef9fafbc6def514619aa938d060047c40b3c0c98c9536c8c`, C contract `944e7b7acb495899bd78a937d3a453e2e188812c9a747ce05b9667537ccb15bc`; exact stage source hashes bound in receipt.

Repair2 tracer03 extended the same combined-fault regression to report publication and observed intended RED1 failure/0errors/exit1 before changing the report call. Tracer04 immediate GREEN1/exit0 shares only the already-inspected evaluator-owned primitive; protected C remains untouched. Tracer05 is coverage-only GREEN14 cases, not invented RED: digest and JSON readback with genuine primary PermissionError retaining unrelated prior context, both ordinary and failed cleanup, and pending/preexisting/appearing-destination exclusive collisions for both publications. No further production changes were needed. Established healthy completion and repair1 failure controls remain pending their fresh full-suite execution below. The external PROGRESS.md content records the parent repair2 ledger; it stays separately disclosed, never overwritten.

### Repair2 executed tracer 06-new-owned-regressions

- Started `2026-11-14T07:45:52.718707+08:00`; ended `2026-11-14T07:45:53.547027+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py::test_completion_publication_primary_survives_actual_cleanup_fault training/holistic_migration/tests/test_evaluate.py::test_owned_publication_keeps_primary_with_unrelated_context training/holistic_migration/tests/test_evaluate.py::test_owned_publication_never_overwrites_or_cleans_unowned_destination -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/../holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/06-new-owned-regressions-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/../holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/06-new-owned-regressions.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit 0; XML counts `{"errors": 0, "failures": 0, "skipped": 0, "tests": 16}`; serialized cases 16; passed subtests 0; warnings 0.
- Actual summary: `============================== 16 passed in 0.52s ==============================`.
- Receipt/log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/../holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/06-new-owned-regressions.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/../holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/06-new-owned-regressions.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/../holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/06-new-owned-regressions.xml`. Fresh synthetic fixtures `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/../holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/06-new-owned-regressions-fixtures` retained in place, not duplicated into archives.
-49 protected hashes,9 historical snapshots, unchanged scope files (except separately bound external PROGRESS.md drift) and114202-byte prefix verified; source stable True. Training runtime `bdb65f6de0750899ef9fafbc6def514619aa938d060047c40b3c0c98c9536c8c`, C contract `944e7b7acb495899bd78a937d3a453e2e188812c9a747ce05b9667537ccb15bc`; exact stage source hashes bound in receipt.

### Repair2 executed tracer 07-retained-parent-r2

- Started `2026-11-14T07:45:53.820126+08:00`; ended `2026-11-14T07:45:54.452888+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/../holistic-migration-data/evidence/task-d-before-fix2-20261114/test_retained_publication_cleanup.py -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/../holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/07-retained-parent-r2-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/../holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/07-retained-parent-r2.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit 0; XML counts `{"errors": 0, "failures": 0, "skipped": 0, "tests": 1}`; serialized cases 1; passed subtests 0; warnings 0.
- Actual summary: `============================== 1 passed in 0.37s ===============================`.
- Receipt/log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/../holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/07-retained-parent-r2.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/../holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/07-retained-parent-r2.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/../holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/07-retained-parent-r2.xml`. Fresh synthetic fixtures `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/../holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/07-retained-parent-r2-fixtures` retained in place, not duplicated into archives.
-49 protected hashes,9 historical snapshots, unchanged scope files (except separately bound external PROGRESS.md drift) and114202-byte prefix verified; source stable True. Training runtime `bdb65f6de0750899ef9fafbc6def514619aa938d060047c40b3c0c98c9536c8c`, C contract `944e7b7acb495899bd78a937d3a453e2e188812c9a747ce05b9667537ccb15bc`; exact stage source hashes bound in receipt.

### Repair2 executed tracer 08-retained-parent-r1

- Started `2026-11-14T07:45:54.724624+08:00`; ended `2026-11-14T07:45:55.385652+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/../holistic-migration-data/evidence/task-d-before-fix1-20261114/test_parent_final_readback.py -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/../holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/08-retained-parent-r1-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/../holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/08-retained-parent-r1.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit 0; XML counts `{"errors": 0, "failures": 0, "skipped": 0, "tests": 1}`; serialized cases 1; passed subtests 0; warnings 0.
- Actual summary: `============================== 1 passed in 0.39s ===============================`.
- Receipt/log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/../holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/08-retained-parent-r1.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/../holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/08-retained-parent-r1.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/../holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/08-retained-parent-r1.xml`. Fresh synthetic fixtures `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration/../holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/08-retained-parent-r1-fixtures` retained in place, not duplicated into archives.
-49 protected hashes,9 historical snapshots, unchanged scope files (except separately bound external PROGRESS.md drift) and114202-byte prefix verified; source stable True. Training runtime `bdb65f6de0750899ef9fafbc6def514619aa938d060047c40b3c0c98c9536c8c`, C contract `944e7b7acb495899bd78a937d3a453e2e188812c9a747ce05b9667537ccb15bc`; exact stage source hashes bound in receipt.

### Repair2 executed tracer 09-full-evaluator

- Started `2026-11-14T07:46:06.307847+08:00`; ended `2026-11-14T07:46:09.183457+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/09-full-evaluator-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/09-full-evaluator.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit 0; XML counts `{"errors": 0, "failures": 0, "skipped": 0, "tests": 39}`; serialized cases 39; passed subtests 0; warnings 0.
- Actual summary: `============================== 39 passed in 2.61s ==============================`.
- Receipt/log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/09-full-evaluator.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/09-full-evaluator.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/09-full-evaluator.xml`. Fresh synthetic fixtures `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/09-full-evaluator-fixtures` retained in place, not duplicated into archives.
-49 protected hashes,9 historical snapshots, unchanged scope files (except separately bound external PROGRESS.md drift) and114202-byte prefix verified; source stable True. Training runtime `bdb65f6de0750899ef9fafbc6def514619aa938d060047c40b3c0c98c9536c8c`, C contract `944e7b7acb495899bd78a937d3a453e2e188812c9a747ce05b9667537ccb15bc`; exact stage source hashes bound in receipt.

### Repair2 executed tracer 10-all-d-modules

- Started `2026-11-14T07:46:09.495338+08:00`; ended `2026-11-14T07:46:28.534222+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py training/holistic_migration/tests/test_evaluate.py training/holistic_migration/tests/test_augmentation.py -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/10-all-d-modules-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/10-all-d-modules.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit 0; XML counts `{"errors": 0, "failures": 0, "skipped": 0, "tests": 97}`; serialized cases 97; passed subtests 0; warnings 67.
- Actual summary: `======================= 97 passed, 67 warnings in 17.96s =======================`.
- Receipt/log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/10-all-d-modules.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/10-all-d-modules.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/10-all-d-modules.xml`. Fresh synthetic fixtures `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/10-all-d-modules-fixtures` retained in place, not duplicated into archives.
-49 protected hashes,9 historical snapshots, unchanged scope files (except separately bound external PROGRESS.md drift) and114202-byte prefix verified; source stable True. Training runtime `bdb65f6de0750899ef9fafbc6def514619aa938d060047c40b3c0c98c9536c8c`, C contract `944e7b7acb495899bd78a937d3a453e2e188812c9a747ce05b9667537ccb15bc`; exact stage source hashes bound in receipt.

### Repair2 executed tracer 11-full-migration

- Started `2026-11-14T07:46:28.867683+08:00`; ended `2026-11-14T07:47:33.156499+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/11-full-migration-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/11-full-migration.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit 0; XML counts `{"errors": 0, "failures": 0, "skipped": 0, "tests": 675}`; serialized cases 382; passed subtests 293; warnings 67.
- Actual summary: `======= 382 passed, 67 warnings, 293 subtests passed in 63.12s (0:01:03) =======`.
- Receipt/log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/11-full-migration.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/11-full-migration.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/11-full-migration.xml`. Fresh synthetic fixtures `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/11-full-migration-fixtures` retained in place, not duplicated into archives.
-49 protected hashes,9 historical snapshots, unchanged scope files (except separately bound external PROGRESS.md drift) and114202-byte prefix verified; source stable True. Training runtime `bdb65f6de0750899ef9fafbc6def514619aa938d060047c40b3c0c98c9536c8c`, C contract `944e7b7acb495899bd78a937d3a453e2e188812c9a747ce05b9667537ccb15bc`; exact stage source hashes bound in receipt.

### Repair2 executed tracer 12-original-training

- Started `2026-11-14T07:47:33.571207+08:00`; ended `2026-11-14T07:47:43.081410+08:00`.
- Actual command: `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/tests -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/12-original-training-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/12-original-training.xml` from `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration`.
- Environment: `{"CUDA_VISIBLE_DEVICES": "-1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "TF_DETERMINISTIC_OPS": "1", "TF_NUM_INTEROP_THREADS": "1", "TF_NUM_INTRAOP_THREADS": "1", "TMPDIR": "/Users/ahronjanl.rafaelahron.0804icloudcom/.hermes/cache/scratch", "VECLIB_MAXIMUM_THREADS": "1"}`.
- Exit 0; XML counts `{"errors": 0, "failures": 0, "skipped": 0, "tests": 340}`; serialized cases 51; passed subtests 289; warnings 3.
- Actual summary: `============= 51 passed, 3 warnings, 289 subtests passed in 8.69s ==============`.
- Receipt/log/XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/12-original-training.command.json`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/12-original-training.log`, `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/12-original-training.xml`. Fresh synthetic fixtures `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/12-original-training-fixtures` retained in place, not duplicated into archives.
-49 protected hashes,9 historical snapshots, unchanged scope files (except separately bound external PROGRESS.md drift) and114202-byte prefix verified; source stable True. Training runtime `bdb65f6de0750899ef9fafbc6def514619aa938d060047c40b3c0c98c9536c8c`, C contract `944e7b7acb495899bd78a937d3a453e2e188812c9a747ce05b9667537ccb15bc`; exact stage source hashes bound in receipt.

## Repair2 source-frozen results and bounded handoff

Two vertical production slices each reached intended assertion RED1 failure/0errors/exit1 followed immediately by GREEN1/exit0: exact completion publication/readback+cleanup fault, then the same shared report-publication fault. Tracer05 added14 coverage-only GREEN controls without production changes; new permanent combined cases plus controls execute16 cases. All existing repair1 controls remain unchanged and passed. Retained original D-R2 and D-R1 parent regressions each passed1 case against current repaired source, not relabeled old proofs.

| Executed corrected-stage suite | Cases | Subtests | Warnings | Exit |
|---|---:|---:|---:|---:|
| 06-new-owned-regressions | 16 | 0 | 0 | 0 |
| 07-retained-parent-r2 | 1 | 0 | 0 | 0 |
| 08-retained-parent-r1 | 1 | 0 | 0 | 0 |
| 09-full-evaluator | 39 | 0 | 0 | 0 |
| 10-all-d-modules | 97 | 0 | 67 | 0 |
| 11-full-migration | 382 | 293 | 67 | 0 |
| 12-original-training | 51 | 289 | 3 | 0 |

All corrected-stage suites have0failures/errors/skips. XML totals differ from cases by passed subtests: migration675 total versus382 cases; original340 versus51 cases. Raw logs/XML, exact commands, exits and stage-specific source snapshots remain in fresh external evidence and suite-summary.json; no fixture archive duplicates were made. Upstream67 Keras NumPy-copy warnings in D/migration and3 original warnings (two same deprecations, one tf.lite.Interpreter UserWarning) were neither installed around nor suppressed.

The minimal evaluator-owned primitive stages with exclusive pending creation, verifies bytes, uses exclusive hard-link publication, and verifies digest/JSON. Only after its own link does it attempt cleanup; ordinary cleanup OSError cannot replace the active original object. Both report and completion use it. It does not inspect exception.__context__, modify protected C, globally patch dependencies, rewrite a preexisting pending/final receipt or delete an established completed evaluation. Permanent controls cover genuine primary PermissionError with unrelated prior context, digest and JSON faults, ordinary/failed cleanup, pending/preexisting/appearing-final collisions, all retained diagnostics/predictions/start, frozen selection and failed-target retry denial without backend/test access.

Exactly3 worker-changed paths: evaluate.py, tests/test_evaluate.py and this append-only report. All49 protected hashes,9 repair2 snapshots,9 older repair1 snapshots and143 review2 bindings verified (140current unchanged +3 explicit historical preimages). Entire114202-byte prefix SHA256 `487a9a49f58d91c8c9b5f08fa8b7b2eebe5f98e1baf63feb14b5322b7a15c281` and older77458-byte prefix survive. Unowned PROGRESS.md changed externally during the worker: `7c8c86740665899142b407fc10d1a027d83b1ebf81138785bc50295e7fd3e004` → `c95ae9c10b27c736bf9216588a30fcc63d99c594d28c7a876017546ce50f2d21`; worker never wrote/reverted it. Preflight stopped before pytest, not product RED; original observed traceback/command and separate drift receipt are retained. Parent must reconcile this concurrent ledger edit. No protected identity drift occurred.

Current evaluator SHA256 `66e0cc943104c127eddc0aebf00405e622411eaa90f580487a4ed19223db3fbf`; current evaluator tests SHA256 `c24f05b71de9d51764dbf1713d02f117bd2ed2c5eaf761f41404092b89694450`. Training runtime SHA256 `bdb65f6de0750899ef9fafbc6def514619aa938d060047c40b3c0c98c9536c8c`; C contract SHA256 `944e7b7acb495899bd78a937d3a453e2e188812c9a747ce05b9667537ccb15bc`. HEAD/tracked/index stay unchanged and migration source has no pyc/cache. Full task8candidate hashes, exactly3postimages, repair/complete diffs, all unchanged/protected hashes, stage/final identities and evidence inventory are frozen by external `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-fix2-worker-8hz1gtct/handoff.json`; report final SHA256 is external to avoid self-reference.

- Second and final automatic repair cycle. Parent verification and complete affected-scope independent specification/quality re-review remain mandatory. Any further blocker requires owner decision, not a third automatic repair.
- No D acceptance or real-data fitting/evaluation/tiny-proof/model activation/export/live/physical/research/participant authority is granted.
- All test arrays/checkpoints are explicitly synthetic. Bounded existing TF synthetic forward/optimizer/save-reload/lifecycle tests establish executability only; no real-source arrays, model weights, fitting or inference were accessed.
- Actual synthetic tiny learning failure is expected by its test and creates no real tiny proof. Synthetic full lifecycle uses its unchanged explicit trusted proof seam. No real fitted FSL candidate is produced.
- D sources are hash-coupled. All old proof/selection receipts retain their historical evaluator identity and cannot qualify repaired sources silently.
- Evaluator owns only its just-linked publications. Existing-target readback remains outside new-attempt cleanup. Retained failure disposition blocks a residual completion after unlink failure.
- Simultaneous inability to revoke completion and persist failure, permanent media failure, process death/crash durability, hostile replacement writers/TOCTOU and OS/signed-provenance guarantees remain unestablished.
- C publisher remains byte-identical including its unsafe combined-cleanup behavior for its own consumers; this repair composes an evaluator-owned primitive and does not globally replace the dependency or unwrap arbitrary exception context.
- External unowned PROGRESS.md changed during execution. Worker never wrote or reverted it; exact baseline/current hashes and interruption are separately retained for parent reconciliation, not hidden in the3worker postimages.
- Historical review143 compact bindings and both generations of9snapshots were checked. Prior bulk fixture inventory/archive was not re-walked or duplicated; previous published inventory remains source-bound retained evidence.
- Original67 Keras warnings in D/migration and3 original warnings remain visible and unsuppressed. Rising-validation-then-tie suggestion remains deferred; protected trainer/tests unchanged.
- Unknown/FAR/safe-unknown remain null/unmeasured, reused test remains exploratory. Expert/anatomical/linguistic/signer-independent/target-device/camera/phone/human gates are not established.

## Owner-authorized bounded repair3 recovery — 2026-11-15T17:51:01.414900+08:00

Owner explicitly authorized one additional trainer/tests/append-only-report repair and re-review after two exhausted automatic cycles; this is not a reset or further-repair authority. Read original and owner repair3 briefs and complete rejected review3 (D-R3-001). Verified all51 protected hashes,9 exact snapshots,8 current D preimages, and the entire155298-byte report prefix SHA-256 21691b0db9da9723800814f835b9ebde1e9e334ed79db318606a50546dcd9cc0 before this append.

Fresh exclusive evidence: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph`; preflight: `preflight.json`. Editable paths remain train.py, tests/test_train.py and this append-only report only. Protected C/evaluator are unchanged. All execution is isolated synthetic with existing -E -B interpreter, approved scratch, deterministic CPU/thread bounds; no actual-source arrays/models/media/real fitting/evaluation, devices, installs, Git writes or historical receipt changes. Parent mutable PROGRESS/todos are excluded from frozen source checks.

Vertical tracers will first retain the precise residual-proof consumer RED, then minimal disposition correction/GREEN, then applicable exact-primary publication/diagnostic faults and coverage-only controls. Existing evaluator publication primitive has been inspected; no blanket context unwrapping/global dependency replacement/framework is permitted. Parent verification and complete independent re-review remain mandatory; no D acceptance or real-data authority is conferred.

### 01-residual-proof-red — behavioral_RED

Executed 2026-11-15T17:51:33.371292+08:00; exit 1.

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py::test_failed_tiny_publication_must_not_unlock_full_fit -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/01-residual-proof-red-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/01-residual-proof-red.xml
```

Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/01-residual-proof-red.log` (SHA-256 a20c0cfbe1bd12f9f4d5cc73a3b8d7453d9e284429893c5b10c6e5b5fdc04b7e); XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/01-residual-proof-red.xml`; receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/01-residual-proof-red.command.json`. Actual parsed result: {"summary_lines": ["============================== 1 failed in 0.28s ==============================="], "xml_counts": {"tests": 1, "failures": 1, "errors": 0, "skipped": 0}, "cases": 0, "subtests": 0, "warnings": 0}. Source-stage snapshots and current runtime/C/source identities are bound in the receipt; all51 protected hashes,9 snapshots and fixed report prefix reverified. No actual-source execution. This label distinguishes expected behavioral RED from coverage-only GREEN; a wrapper completion is not product success.

### 02-residual-proof-green — executed_GREEN

Executed 2026-11-15T17:51:50.631673+08:00; exit 0.

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py::test_failed_tiny_publication_must_not_unlock_full_fit -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/02-residual-proof-green-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/02-residual-proof-green.xml
```

Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/02-residual-proof-green.log` (SHA-256 39a0e911224fb750df071452aa8b3ab9ef629b13bed6161ca9a33f491dccc3f3); XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/02-residual-proof-green.xml`; receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/02-residual-proof-green.command.json`. Actual parsed result: {"summary_lines": ["============================== 1 passed in 0.23s ==============================="], "xml_counts": {"tests": 1, "failures": 0, "errors": 0, "skipped": 0}, "cases": 1, "subtests": 0, "warnings": 0}. Source-stage snapshots and current runtime/C/source identities are bound in the receipt; all51 protected hashes,9 snapshots and fixed report prefix reverified. No actual-source execution. This label distinguishes expected behavioral RED from coverage-only GREEN; a wrapper completion is not product success.

### 03-tiny-primary-red — behavioral_RED

Executed 2026-11-15T17:52:27.480252+08:00; exit 1.

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py::test_trainer_publication_preserves_primary_on_actual_cleanup_failure -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/03-tiny-primary-red-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/03-tiny-primary-red.xml
```

Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/03-tiny-primary-red.log` (SHA-256 0c957c3b06e1e14bcdf0349e006ef0658a1ee9fbc0252919a0d91e8eb0db1900); XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/03-tiny-primary-red.xml`; receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/03-tiny-primary-red.command.json`. Actual parsed result: {"summary_lines": ["============================== 1 failed in 0.27s ==============================="], "xml_counts": {"tests": 1, "failures": 1, "errors": 0, "skipped": 0}, "cases": 0, "subtests": 0, "warnings": 0}. Source-stage snapshots and current runtime/C/source identities are bound in the receipt; all51 protected hashes,9 snapshots and fixed report prefix reverified. No actual-source execution. This label distinguishes expected behavioral RED from coverage-only GREEN; a wrapper completion is not product success.

### 04-tiny-primary-green — executed_GREEN

Executed 2026-11-15T17:52:49.769592+08:00; exit 0.

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py::test_trainer_publication_preserves_primary_on_actual_cleanup_failure -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/04-tiny-primary-green-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/04-tiny-primary-green.xml
```

Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/04-tiny-primary-green.log` (SHA-256 65ba48968367ea49cd2ab6d640c87eaa29b7791158d8d6d99c96d22756a4fd9b); XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/04-tiny-primary-green.xml`; receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/04-tiny-primary-green.command.json`. Actual parsed result: {"summary_lines": ["============================== 1 passed in 0.24s ==============================="], "xml_counts": {"tests": 1, "failures": 0, "errors": 0, "skipped": 0}, "cases": 1, "subtests": 0, "warnings": 0}. Source-stage snapshots and current runtime/C/source identities are bound in the receipt; all51 protected hashes,9 snapshots and fixed report prefix reverified. No actual-source execution. This label distinguishes expected behavioral RED from coverage-only GREEN; a wrapper completion is not product success.

### 05-selection-primary-red — behavioral_RED

Executed 2026-11-15T17:53:23.203716+08:00; exit 1.

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider 'training/holistic_migration/tests/test_train.py::test_trainer_publication_preserves_primary_on_actual_cleanup_failure[selection.json]' -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/05-selection-primary-red-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/05-selection-primary-red.xml
```

Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/05-selection-primary-red.log` (SHA-256 21cac4065d71cdbb1fb0fdba430b412846dd1dea73e14aa4dcc389724bc15e2c); XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/05-selection-primary-red.xml`; receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/05-selection-primary-red.command.json`. Actual parsed result: {"summary_lines": ["============================== 1 failed in 0.39s ==============================="], "xml_counts": {"tests": 1, "failures": 1, "errors": 0, "skipped": 0}, "cases": 0, "subtests": 0, "warnings": 0}. Source-stage snapshots and current runtime/C/source identities are bound in the receipt; all51 protected hashes,9 snapshots and fixed report prefix reverified. No actual-source execution. This label distinguishes expected behavioral RED from coverage-only GREEN; a wrapper completion is not product success.

### 06-selection-primary-green — executed_GREEN

Executed 2026-11-15T17:53:46.430743+08:00; exit 0.

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider 'training/holistic_migration/tests/test_train.py::test_trainer_publication_preserves_primary_on_actual_cleanup_failure[selection.json]' -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/06-selection-primary-green-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/06-selection-primary-green.xml
```

Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/06-selection-primary-green.log` (SHA-256 13c211d9d6577d4a4487ab96a52a4a189644dd9175e9ddf4d0ee76eb4dacab69); XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/06-selection-primary-green.xml`; receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/06-selection-primary-green.command.json`. Actual parsed result: {"summary_lines": ["============================== 1 passed in 0.32s ==============================="], "xml_counts": {"tests": 1, "failures": 0, "errors": 0, "skipped": 0}, "cases": 1, "subtests": 0, "warnings": 0}. Source-stage snapshots and current runtime/C/source identities are bound in the receipt; all51 protected hashes,9 snapshots and fixed report prefix reverified. No actual-source execution. This label distinguishes expected behavioral RED from coverage-only GREEN; a wrapper completion is not product success.

### 07-report-primary-red — behavioral_RED

Executed 2026-11-15T17:54:03.114020+08:00; exit 1.

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider 'training/holistic_migration/tests/test_train.py::test_trainer_publication_preserves_primary_on_actual_cleanup_failure[fit-report.json]' -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/07-report-primary-red-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/07-report-primary-red.xml
```

Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/07-report-primary-red.log` (SHA-256 233ab1274c1968dafc41232370c14c74cd6f84843dae7069b8a291db1398fb98); XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/07-report-primary-red.xml`; receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/07-report-primary-red.command.json`. Actual parsed result: {"summary_lines": ["============================== 1 failed in 0.36s ==============================="], "xml_counts": {"tests": 1, "failures": 1, "errors": 0, "skipped": 0}, "cases": 0, "subtests": 0, "warnings": 0}. Source-stage snapshots and current runtime/C/source identities are bound in the receipt; all51 protected hashes,9 snapshots and fixed report prefix reverified. No actual-source execution. This label distinguishes expected behavioral RED from coverage-only GREEN; a wrapper completion is not product success.

### 08-report-primary-green — executed_GREEN

Executed 2026-11-15T17:54:24.447066+08:00; exit 0.

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider 'training/holistic_migration/tests/test_train.py::test_trainer_publication_preserves_primary_on_actual_cleanup_failure[fit-report.json]' -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/08-report-primary-green-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/08-report-primary-green.xml
```

Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/08-report-primary-green.log` (SHA-256 f20431bef6c82783e343013d5d43e2d9d190fbba3ba3acaba0a2d85f6e16e684); XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/08-report-primary-green.xml`; receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/08-report-primary-green.command.json`. Actual parsed result: {"summary_lines": ["============================== 1 passed in 0.29s ==============================="], "xml_counts": {"tests": 1, "failures": 0, "errors": 0, "skipped": 0}, "cases": 1, "subtests": 0, "warnings": 0}. Source-stage snapshots and current runtime/C/source identities are bound in the receipt; all51 protected hashes,9 snapshots and fixed report prefix reverified. No actual-source execution. This label distinguishes expected behavioral RED from coverage-only GREEN; a wrapper completion is not product success.

### 09-validation-report-coverage — coverage_only_GREEN

Executed 2026-11-15T17:54:25.279897+08:00; exit 0.

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider 'training/holistic_migration/tests/test_train.py::test_trainer_publication_preserves_primary_on_actual_cleanup_failure[validation-report.json]' -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/09-validation-report-coverage-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/09-validation-report-coverage.xml
```

Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/09-validation-report-coverage.log` (SHA-256 fcc5df2c1a01c891e3f6289aeff9104c81e08c2c3f4f233593f60dce9e5eb993); XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/09-validation-report-coverage.xml`; receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/09-validation-report-coverage.command.json`. Actual parsed result: {"summary_lines": ["============================== 1 passed in 0.28s ==============================="], "xml_counts": {"tests": 1, "failures": 0, "errors": 0, "skipped": 0}, "cases": 1, "subtests": 0, "warnings": 0}. Source-stage snapshots and current runtime/C/source identities are bound in the receipt; all51 protected hashes,9 snapshots and fixed report prefix reverified. No actual-source execution. This label distinguishes expected behavioral RED from coverage-only GREEN; a wrapper completion is not product success.

### 10-complete-primary-red — behavioral_RED

Executed 2026-11-15T17:54:42.625816+08:00; exit 1.

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider 'training/holistic_migration/tests/test_train.py::test_trainer_publication_preserves_primary_on_actual_cleanup_failure[complete.json]' -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/10-complete-primary-red-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/10-complete-primary-red.xml
```

Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/10-complete-primary-red.log` (SHA-256 450eb1313097a0a1a4d57fc20d9bd34a379de10e105245d519811740c0c5c454); XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/10-complete-primary-red.xml`; receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/10-complete-primary-red.command.json`. Actual parsed result: {"summary_lines": ["============================== 1 failed in 0.32s ==============================="], "xml_counts": {"tests": 1, "failures": 1, "errors": 0, "skipped": 0}, "cases": 0, "subtests": 0, "warnings": 0}. Source-stage snapshots and current runtime/C/source identities are bound in the receipt; all51 protected hashes,9 snapshots and fixed report prefix reverified. No actual-source execution. This label distinguishes expected behavioral RED from coverage-only GREEN; a wrapper completion is not product success.

### 11-complete-primary-green — executed_GREEN

Executed 2026-11-15T17:55:03.968391+08:00; exit 0.

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider 'training/holistic_migration/tests/test_train.py::test_trainer_publication_preserves_primary_on_actual_cleanup_failure[complete.json]' -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/11-complete-primary-green-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/11-complete-primary-green.xml
```

Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/11-complete-primary-green.log` (SHA-256 5d4a01c0b93fc433e73cfbf3ff450fec89cf013b077002110b79a65432358b34); XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/11-complete-primary-green.xml`; receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/11-complete-primary-green.command.json`. Actual parsed result: {"summary_lines": ["============================== 1 passed in 0.31s ==============================="], "xml_counts": {"tests": 1, "failures": 0, "errors": 0, "skipped": 0}, "cases": 1, "subtests": 0, "warnings": 0}. Source-stage snapshots and current runtime/C/source identities are bound in the receipt; all51 protected hashes,9 snapshots and fixed report prefix reverified. No actual-source execution. This label distinguishes expected behavioral RED from coverage-only GREEN; a wrapper completion is not product success.

### 12-diagnostic-primary-red — behavioral_RED

Executed 2026-11-15T17:55:33.111620+08:00; exit 1.

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py::test_training_diagnostic_io_never_replaces_primary -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/12-diagnostic-primary-red-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/12-diagnostic-primary-red.xml
```

Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/12-diagnostic-primary-red.log` (SHA-256 e8655c266eb833547c1abf9fd223519bdcbd02f5cb57a025b24875dfb7c77bb8); XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/12-diagnostic-primary-red.xml`; receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/12-diagnostic-primary-red.command.json`. Actual parsed result: {"summary_lines": ["============================== 2 failed in 0.31s ==============================="], "xml_counts": {"tests": 2, "failures": 2, "errors": 0, "skipped": 0}, "cases": 0, "subtests": 0, "warnings": 0}. Source-stage snapshots and current runtime/C/source identities are bound in the receipt; all51 protected hashes,9 snapshots and fixed report prefix reverified. No actual-source execution. This label distinguishes expected behavioral RED from coverage-only GREEN; a wrapper completion is not product success.

### 13-diagnostic-primary-green — executed_GREEN

Executed 2026-11-15T17:55:56.662305+08:00; exit 0.

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py::test_training_diagnostic_io_never_replaces_primary -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/13-diagnostic-primary-green-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/13-diagnostic-primary-green.xml
```

Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/13-diagnostic-primary-green.log` (SHA-256 502df153c932ff00fe90b3092951671deef6624cbc65f7d0ec7d0307bfb07175); XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/13-diagnostic-primary-green.xml`; receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/13-diagnostic-primary-green.command.json`. Actual parsed result: {"summary_lines": ["============================== 2 passed in 0.28s ==============================="], "xml_counts": {"tests": 2, "failures": 0, "errors": 0, "skipped": 0}, "cases": 2, "subtests": 0, "warnings": 0}. Source-stage snapshots and current runtime/C/source identities are bound in the receipt; all51 protected hashes,9 snapshots and fixed report prefix reverified. No actual-source execution. This label distinguishes expected behavioral RED from coverage-only GREEN; a wrapper completion is not product success.

### 14-boundary-controls — coverage_only_GREEN

Executed 2026-11-15T17:57:00.922575+08:00; exit 0.

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py::test_failed_tiny_disposition_denies_full_caller_before_work training/holistic_migration/tests/test_train.py::test_trainer_bound_publisher_readback_and_cleanup_controls training/holistic_migration/tests/test_train.py::test_trainer_bound_publisher_preserves_unowned_targets training/holistic_migration/tests/test_train.py::test_tiny_publication_primary_survives_failure_diagnostic_fault -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/14-boundary-controls-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/14-boundary-controls.xml
```

Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/14-boundary-controls.log` (SHA-256 2905e1904f43d9e3aadfcef4ce1ddc6c9cb785ebfb34a86d037654a7cfe72dd6); XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/14-boundary-controls.xml`; receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/14-boundary-controls.command.json`. Actual parsed result: {"summary_lines": ["============================== 42 passed in 0.65s =============================="], "xml_counts": {"tests": 42, "failures": 0, "errors": 0, "skipped": 0}, "cases": 42, "subtests": 0, "warnings": 0}. Source-stage snapshots and current runtime/C/source identities are bound in the receipt; all51 protected hashes,9 snapshots and fixed report prefix reverified. No actual-source execution. This label distinguishes expected behavioral RED from coverage-only GREEN; a wrapper completion is not product success.

### 15-protected-selection-diagnostic — out_of_scope_consumer_diagnostic_not_repaired

Executed 2026-11-15T17:58:07.852601+08:00; exit 1.

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/test_protected_selection_disposition.py -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/15-protected-selection-diagnostic-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/15-protected-selection-diagnostic.xml
```

Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/15-protected-selection-diagnostic.log` (SHA-256 df0b4cdefa8fb35262e23bdfb627c584449818cac0a8c16e1e4c20921b5d5551); XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/15-protected-selection-diagnostic.xml`; receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/15-protected-selection-diagnostic.command.json`. Actual parsed result: {"summary_lines": ["============================== 1 failed in 0.34s ==============================="], "xml_counts": {"tests": 1, "failures": 1, "errors": 0, "skipped": 0}, "cases": 0, "subtests": 0, "warnings": 0}. Source-stage snapshots and current runtime/C/source identities are bound in the receipt; all51 protected hashes,9 snapshots and fixed report prefix reverified. No actual-source execution. This label distinguishes expected behavioral RED from coverage-only GREEN; a wrapper completion is not product success.

### Concrete protected-consumer blocker — no scope expansion

Stage15 is an actual explicitly synthetic diagnostic, not a repair GREEN: 1 behavioral failure/0 errors/0 skips/exit1. After selection.json final-link/readback failure plus rollback PermissionError, the original OSError is now preserved and failure.json persists with actual_epochs=1/optimizer_steps=4. Nevertheless protected evaluate.frozen_selection() accepts that residual selection as frozen_validation_selection after faults clear. No evaluator invocation, test inference, real fit, TensorFlow import or actual-source data was used: the trusted synthetic backend supplied two oracle models/five recorded synthetic steps only.

This is distinct from the repaired failed-tiny consumer, and from the intentionally usable successfully frozen selection after a later report failure. A blanket failure.json check at the evaluator would break that established reporting policy. Concrete evidence is in 15-protected-selection-diagnostic.command.json and its retained selection-consumer-diagnostic.json. The evaluator consumer is frozen by this brief; it was not edited, globally replaced or context-unwrapped. Report this protected-consumer disposition blocker to parent for an owner decision rather than expand this one-repair exception. No further production changes are planned or authorized. Required verification/handoff proceeds for the bounded trainer repair; no D acceptance is claimed.

### 16-all-new-regressions — executed_GREEN

Executed 2026-11-15T17:58:59.902214+08:00; exit 0.

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py::test_failed_tiny_publication_must_not_unlock_full_fit training/holistic_migration/tests/test_train.py::test_trainer_publication_preserves_primary_on_actual_cleanup_failure training/holistic_migration/tests/test_train.py::test_training_diagnostic_io_never_replaces_primary training/holistic_migration/tests/test_train.py::test_failed_tiny_disposition_denies_full_caller_before_work training/holistic_migration/tests/test_train.py::test_trainer_bound_publisher_readback_and_cleanup_controls training/holistic_migration/tests/test_train.py::test_trainer_bound_publisher_preserves_unowned_targets training/holistic_migration/tests/test_train.py::test_tiny_publication_primary_survives_failure_diagnostic_fault -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/16-all-new-regressions-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/16-all-new-regressions.xml
```

Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/16-all-new-regressions.log` (SHA-256 a2e5d6dfe654da44c32a794da0051c9e76d183d6185859bca28d8adb9bb6f186); XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/16-all-new-regressions.xml`; receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/16-all-new-regressions.command.json`. Actual parsed result: {"summary_lines": ["============================== 50 passed in 1.20s =============================="], "xml_counts": {"tests": 50, "failures": 0, "errors": 0, "skipped": 0}, "cases": 50, "subtests": 0, "warnings": 0}. Source-stage snapshots and current runtime/C/source identities are bound in the receipt; all51 protected hashes,9 snapshots and fixed report prefix reverified. No actual-source execution. This label distinguishes expected behavioral RED from coverage-only GREEN; a wrapper completion is not product success.

### 17-retained-parent-regressions — executed_GREEN

Executed 2026-11-15T17:59:01.004199+08:00; exit 0.

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-review3-parent-20261115/test_parent_failed_tiny_publication.py /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-before-fix1-20261114/test_parent_final_readback.py /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-review2-finalization-20261114/test_parent_publication_cleanup.py -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/17-retained-parent-regressions-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/17-retained-parent-regressions.xml
```

Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/17-retained-parent-regressions.log` (SHA-256 004a1f98a1a43c46bfc346b7bcb056790865b763c11978140df6c5b5e002dc69); XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/17-retained-parent-regressions.xml`; receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/17-retained-parent-regressions.command.json`. Actual parsed result: {"summary_lines": ["============================== 3 passed in 0.56s ==============================="], "xml_counts": {"tests": 3, "failures": 0, "errors": 0, "skipped": 0}, "cases": 3, "subtests": 0, "warnings": 0}. Source-stage snapshots and current runtime/C/source identities are bound in the receipt; all51 protected hashes,9 snapshots and fixed report prefix reverified. No actual-source execution. This label distinguishes expected behavioral RED from coverage-only GREEN; a wrapper completion is not product success.

### 18-all-D — executed_GREEN

Executed 2026-11-15T17:59:22.593324+08:00; exit 0.

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py training/holistic_migration/tests/test_evaluate.py training/holistic_migration/tests/test_augmentation.py -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/18-all-D-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/18-all-D.xml
```

Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/18-all-D.log` (SHA-256 3ead566e2000b65e3f3de98c56d24ebf2a1df6b50fae4a623f3b1644e3fc8739); XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/18-all-D.xml`; receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/18-all-D.command.json`. Actual parsed result: {"summary_lines": ["====================== 147 passed, 67 warnings in 20.27s ======================="], "xml_counts": {"tests": 147, "failures": 0, "errors": 0, "skipped": 0}, "cases": 147, "subtests": 0, "warnings": 67}. Source-stage snapshots and current runtime/C/source identities are bound in the receipt; all51 protected hashes,9 snapshots and fixed report prefix reverified. No actual-source execution. This label distinguishes expected behavioral RED from coverage-only GREEN; a wrapper completion is not product success.

### 19-full-migration — executed_GREEN

Executed 2026-11-15T18:00:48.876194+08:00; exit 0.

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/19-full-migration-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/19-full-migration.xml
```

Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/19-full-migration.log` (SHA-256 6a7702d7abb9100e69d0016490012355e82b3be07681fa7c99040a3b5d07fcf7); XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/19-full-migration.xml`; receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/19-full-migration.command.json`. Actual parsed result: {"summary_lines": ["======= 432 passed, 67 warnings, 293 subtests passed in 75.37s (0:01:15) ======="], "xml_counts": {"tests": 725, "failures": 0, "errors": 0, "skipped": 0}, "cases": 432, "subtests": 293, "warnings": 67}. Source-stage snapshots and current runtime/C/source identities are bound in the receipt; all51 protected hashes,9 snapshots and fixed report prefix reverified. No actual-source execution. This label distinguishes expected behavioral RED from coverage-only GREEN; a wrapper completion is not product success.

### 20-original-training — executed_GREEN

Executed 2026-11-15T18:00:58.634214+08:00; exit 0.

```sh
/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/tests -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/20-original-training-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/20-original-training.xml
```

Log: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/20-original-training.log` (SHA-256 c1b9255ad97af5a6c9eb5d78e7475e0a20091dcefda00a06fef973e2ed585b80); XML: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/20-original-training.xml`; receipt: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/20-original-training.command.json`. Actual parsed result: {"summary_lines": ["============= 51 passed, 3 warnings, 289 subtests passed in 8.47s =============="], "xml_counts": {"tests": 340, "failures": 0, "errors": 0, "skipped": 0}, "cases": 51, "subtests": 289, "warnings": 3}. Source-stage snapshots and current runtime/C/source identities are bound in the receipt; all51 protected hashes,9 snapshots and fixed report prefix reverified. No actual-source execution. This label distinguishes expected behavioral RED from coverage-only GREEN; a wrapper completion is not product success.

## Bounded repair3 result and verification — 2026-11-15T18:04:57.315945+08:00

D-R3-001 is corrected at the actual trainer proof consumer: any retained failure.json entry denies the proof before its success bytes, checkpoint load or full-fit work/reservation. Permanent exact fault regression plus full-caller poison guards exercise the residual proof and persisted failure. All trainer success-publication call sites now compose the unchanged inspected evaluator-owned primitive; exact primary object and unrelated prior context survive ordinary cleanup faults. History and failure diagnostics are attempted separately without replacing the original error. No protected dependency/framework/global publisher replacement/context unwrapping was introduced. Successfully frozen selections remain preserved on later report failure.

Actual executed final suites: new regressions50 passed; exact retained parent D-R1/R2/R3 regressions3 passed; complete D147 passed/67warnings; full migration432 cases+293subtests passed/67warnings; original training51 cases+289subtests passed/3warnings. Every suite has0failures/errors/skips. Source-bound receipts/log/XML retain the actual commands. Earlier stage RED commands intentionally failed their named primary/disposition assertions before minimal source edits; already-passing boundary variants are coverage-only GREEN. Warning blocks are byte-equivalent to historical baseline text (67 Keras NumPy-copy deprecations; original2 Keras deprecations+1 TFLite interpreter deprecation), unsuppressed, with no new warning differences. All23 original trainer test/fixture definitions are AST-identical; no old assertions were weakened. Receipt cases means passed cases; the suite summary separately parses actual collected cases and XML/subtests, including the intended RED failures.

**D acceptance remains blocked:** the separate stage15 protected selection-consumer diagnostic has1behavioral failure/0errors/0skips/exit1. A failed selection publication with persisted failure is still accepted by protected evaluate.frozen_selection(). Exact evidence and scope boundary are in protected-consumer-blocker.json. No protected consumer change was made; parent/owner decision is required, not another repair inferred from this exception. Existing original evaluator D-R1/D-R2 regressions remain GREEN.

Final source/postimage/prefix/protected/historical/stage/inventory bindings are finalized externally in handoff.json, final-verification.json, evidence-inventory.json, complete8-path diff and repair-only3-path delta. Parent must independently verify this handoff and obtain complete affected-scope specification/quality re-review before accepting D. No acceptance or real-data gate is granted by worker tests.

Limits: simultaneous inability to revoke a tiny success artifact AND persist failure, process death/crash/power-loss durability, hostile writers/TOCTOU, OS sandbox/signatures and permanent media loss remain unproved. Synthetic artifacts regenerate current identities; historical proof/selection receipts remain historical. All new execution uses synthetic fixtures/oracle seams or the existing bounded TF synthetic forward/optimizer/save-reload tests, not actual-source fitting/inference/evaluation. No actual-source arrays/weights/media, real tiny proof, devices/camera/phone/SDK/GUI/participants, installs/provider/model/config/Git writes or historical rewrites occurred. Unknown/FAR/safe-unknown and live/physical/expert/research gates remain unmeasured/open. Parent mutable PROGRESS/todos were neither written nor reverted. This is the one explicit additional repair after the exhausted two-cycle automatic budget, not a reset or further-repair authorization.

## Owner-authorized coordinated repair4 recovery — 2026-11-15T22:15:00.326077+08:00

Existing owner approval resumed, no permission renewal or budget reset. Fresh readback matched {'protected': 51, 'review_inputs': 394, 'snapshots': 9}, all8 current source paths, exact9 original source/review snapshots and the complete199487-byte report prefix `189bd9ef96eea0021b524320ef0c16f10cf27ed4e619e42042af33affa30ae83`. HEAD/index/tracked differences remain empty. Evidence: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/preflight.json`. Only train/evaluate/their2tests and this append-only report are editable. Synthetic-only execution; parent verification and complete independent review still required. No real-data or live authority granted.

### 01-exact-phase-pair-red — behavioral_RED

Executed `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py::test_failure_phase_controls_evaluator_admission -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/01-exact-phase-pair-red-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/01-exact-phase-pair-red.xml`; exit `1`. XML units: `{"tests": 2, "failures": 1, "errors": 0, "skipped": 0}`. Actual summary: ['========================= 1 failed, 1 passed in 0.72s ==========================']. Source-stage bytes and hashes: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/01-exact-phase-pair-red.command.json`; log/XML `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/01-exact-phase-pair-red.log` / `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/01-exact-phase-pair-red.xml`. Earlier-stage snapshots are not claimed to equal later expanded tests.

### 02-exact-phase-pair-green — immediate_GREEN

Executed `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py::test_failure_phase_controls_evaluator_admission -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/02-exact-phase-pair-green-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/02-exact-phase-pair-green.xml`; exit `0`. XML units: `{"tests": 2, "failures": 0, "errors": 0, "skipped": 0}`. Actual summary: ['============================== 2 passed in 0.60s ===============================']. Source-stage bytes and hashes: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/02-exact-phase-pair-green.command.json`; log/XML `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/02-exact-phase-pair-green.log` / `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/02-exact-phase-pair-green.xml`. Earlier-stage snapshots are not claimed to equal later expanded tests.

### 03-disposition-publication-red — behavioral_RED

Executed `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py::test_failed_disposition_publication_denies_actual_evaluator -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/03-disposition-publication-red-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/03-disposition-publication-red.xml`; exit `1`. XML units: `{"tests": 1, "failures": 1, "errors": 0, "skipped": 0}`. Actual summary: ['============================== 1 failed in 0.56s ===============================']. Source-stage bytes and hashes: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/03-disposition-publication-red.command.json`; log/XML `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/03-disposition-publication-red.log` / `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/03-disposition-publication-red.xml`. Earlier-stage snapshots are not claimed to equal later expanded tests.

### 04-disposition-publication-green — immediate_GREEN

Executed `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py::test_failed_disposition_publication_denies_actual_evaluator training/holistic_migration/tests/test_evaluate.py::test_failure_phase_controls_evaluator_admission -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/04-disposition-publication-green-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/04-disposition-publication-green.xml`; exit `0`. XML units: `{"tests": 3, "failures": 0, "errors": 0, "skipped": 0}`. Actual summary: ['============================== 3 passed in 0.73s ===============================']. Source-stage bytes and hashes: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/04-disposition-publication-green.command.json`; log/XML `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/04-disposition-publication-green.log` / `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/04-disposition-publication-green.xml`. Earlier-stage snapshots are not claimed to equal later expanded tests.

### 05-grounded-boundary-controls — coverage_only_GREEN

Executed `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py::test_failure_phase_controls_evaluator_admission training/holistic_migration/tests/test_evaluate.py::test_failed_disposition_publication_denies_actual_evaluator training/holistic_migration/tests/test_evaluate.py::test_required_selection_disposition_schema_denies_before_work training/holistic_migration/tests/test_evaluate.py::test_failure_selection_phase_schema_denies_before_work training/holistic_migration/tests/test_evaluate.py::test_coordinated_selection_collision_retains_other_owner_and_denies training/holistic_migration/tests/test_evaluate.py::test_selection_publication_diagnostic_failure_limits_are_phase_specific training/holistic_migration/tests/test_train.py::test_full_failure_phase_survives_history_diagnostic_failure training/holistic_migration/tests/test_train.py::test_trainer_publication_preserves_primary_on_actual_cleanup_failure training/holistic_migration/tests/test_train.py::test_trainer_bound_publisher_readback_and_cleanup_controls training/holistic_migration/tests/test_train.py::test_trainer_bound_publisher_preserves_unowned_targets -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/05-grounded-boundary-controls-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/05-grounded-boundary-controls.xml`; exit `0`. XML units: `{"tests": 97, "failures": 0, "errors": 0, "skipped": 0}`. Actual summary: ['============================== 97 passed in 7.29s ==============================']. Source-stage bytes and hashes: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/05-grounded-boundary-controls.command.json`; log/XML `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/05-grounded-boundary-controls.log` / `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/05-grounded-boundary-controls.xml`. Earlier-stage snapshots are not claimed to equal later expanded tests.

### Coordinated selection publication protocol (repair4)

The producer exclusively publishes selection-disposition.json only after selection.json publication returns successfully. Its exact schema1/status selection_frozen binds the current complete training identity and selected receipt digest. This affirmative publication does not infer success from residual selection bytes or optimizer completion. Full-fit failure.json now carries exact selection_disposition {schema_version:1, phase:selection|fit_reports, frozen:false|true, identity:current_identity}; selection includes fitting and all freeze publications, fit_reports begins only after both publishers return. Consumer validates this phase-sensitive failure state when present AND always requires the affirmative disposition before checkpoint hash/test/output reservation. Unknown/legacy missing, malformed, bool/float substitutes, stale identities and contradictions deny; successful selection followed by later reporting failure remains usable. Tiny failure receipts and failed-tiny denial are unchanged. Current source identity changes invalidate older tiny proofs; no historical proof rebinding.

The sole changed old exact expectation is test_trainer_publication_preserves_primary_on_actual_cleanup_failure: all original five diagnostic fields remain required exactly, full-fit variants now additionally require the exact current source-bound phase object. Added selection-disposition publication variants strengthen its publisher/control matrix. Original test bytes and every executed expanded stage are retained separately. The exact96-line parent pair remains a byte-identical embedded block; its collection wrapper executes that original callable in an isolated -E -B process, preserving its no-TensorFlow assertion during whole-suite runs that intentionally include bounded synthetic TF smoke.

Limits: exclusive ordinary local files, caught synchronous failures and successful denial evidence only; no OS sandbox, signed provenance, hostile concurrent writer/TOCTOU or crash/fsync/permanent-media durability claim. Simultaneous failed rollback of the affirmative disposition and failed failure.json persistence is explicitly excluded and exercised only as a non-guarantee control. Original selection readback failure stays denied even if both its rollback and diagnostics fail, because no affirmative disposition was attempted. A later report diagnostic failure does not invalidate earlier successful selection. No further source repair or real-data/live authority is granted.

### 06-retained-diagnostics — executed_GREEN

Executed `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-review3-parent-20261115/test_parent_failed_tiny_publication.py /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-before-fix1-20261114/test_parent_final_readback.py /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-review2-finalization-20261114/test_parent_publication_cleanup.py /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix3-worker-0mtlkmph/test_protected_selection_disposition.py /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-review4-parent-20261115/test_parent_selection_phase_boundary.py -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/06-retained-diagnostics-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/06-retained-diagnostics.xml`; exit `0`. XML units: `{"tests": 6, "failures": 0, "errors": 0, "skipped": 0}`. Actual summary: ['============================== 6 passed in 1.12s ===============================']. Source-stage bytes and hashes: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/06-retained-diagnostics.command.json`; log/XML `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/06-retained-diagnostics.log` / `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/06-retained-diagnostics.xml`. Earlier-stage snapshots are not claimed to equal later expanded tests.

### 07-complete-D — executed_GREEN

Executed `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_train.py training/holistic_migration/tests/test_evaluate.py training/holistic_migration/tests/test_augmentation.py -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/07-complete-D-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/07-complete-D.xml`; exit `0`. XML units: `{"tests": 204, "failures": 0, "errors": 0, "skipped": 0}`. Actual summary: ['====================== 204 passed, 67 warnings in 28.99s =======================']. Source-stage bytes and hashes: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/07-complete-D.command.json`; log/XML `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/07-complete-D.log` / `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/07-complete-D.xml`. Earlier-stage snapshots are not claimed to equal later expanded tests.

### 08-full-migration — executed_GREEN

Executed `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/08-full-migration-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/08-full-migration.xml`; exit `1`. XML units: `{"tests": 782, "failures": 1, "errors": 0, "skipped": 0}`. Actual summary: ['== 1 failed, 489 passed, 67 warnings, 292 subtests passed in 76.62s (0:01:16) ==']. Source-stage bytes and hashes: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/08-full-migration.command.json`; log/XML `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/08-full-migration.log` / `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/08-full-migration.xml`. Earlier-stage snapshots are not claimed to equal later expanded tests.

### 09-original-training — executed_GREEN

Executed `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/tests -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/09-original-training-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/09-original-training.xml`; exit `0`. XML units: `{"tests": 340, "failures": 0, "errors": 0, "skipped": 0}`. Actual summary: ['============= 51 passed, 3 warnings, 289 subtests passed in 9.00s ==============']. Source-stage bytes and hashes: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/09-original-training.command.json`; log/XML `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/09-original-training.log` / `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/09-original-training.xml`. Earlier-stage snapshots are not claimed to equal later expanded tests.

### 10-protected-startup-diagnostic — diagnostic_no_source_changes

Executed `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_camera.py::CaptureTests::test_startup_eof_timeout_and_stderr_are_preserved -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/10-protected-startup-diagnostic-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/10-protected-startup-diagnostic.xml`; exit `0`. XML units: `{"tests": 3, "failures": 0, "errors": 0, "skipped": 0}`. Actual summary: ['===================== 1 passed, 2 subtests passed in 0.14s =====================']. Source-stage bytes and hashes: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/10-protected-startup-diagnostic.command.json`; log/XML `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/10-protected-startup-diagnostic.log` / `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/10-protected-startup-diagnostic.xml`. Earlier-stage snapshots are not claimed to equal later expanded tests.

### 11-full-migration-serial-rerun — executed_GREEN_after_protected_startup_timing_failure

Executed `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/11-full-migration-serial-rerun-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/11-full-migration-serial-rerun.xml`; exit `0`. XML units: `{"tests": 782, "failures": 0, "errors": 0, "skipped": 0}`. Actual summary: ['======= 489 passed, 67 warnings, 293 subtests passed in 75.67s (0:01:15) =======']. Source-stage bytes and hashes: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/11-full-migration-serial-rerun.command.json`; log/XML `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/11-full-migration-serial-rerun.log` / `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/11-full-migration-serial-rerun.xml`. Earlier-stage snapshots are not claimed to equal later expanded tests.

### 12-new-covering-final — executed_GREEN

Executed `/Users/ahronjanl.rafaelahron.0804icloudcom/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python -E -B -m pytest -p no:cacheprovider training/holistic_migration/tests/test_evaluate.py::test_failure_phase_controls_evaluator_admission training/holistic_migration/tests/test_evaluate.py::test_failed_disposition_publication_denies_actual_evaluator training/holistic_migration/tests/test_evaluate.py::test_required_selection_disposition_schema_denies_before_work training/holistic_migration/tests/test_evaluate.py::test_failure_selection_phase_schema_denies_before_work training/holistic_migration/tests/test_evaluate.py::test_coordinated_selection_collision_retains_other_owner_and_denies training/holistic_migration/tests/test_evaluate.py::test_selection_publication_diagnostic_failure_limits_are_phase_specific training/holistic_migration/tests/test_train.py::test_full_failure_phase_survives_history_diagnostic_failure training/holistic_migration/tests/test_train.py::test_trainer_publication_preserves_primary_on_actual_cleanup_failure training/holistic_migration/tests/test_train.py::test_trainer_bound_publisher_readback_and_cleanup_controls training/holistic_migration/tests/test_train.py::test_trainer_bound_publisher_preserves_unowned_targets -v --basetemp=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/12-new-covering-final-fixtures --junitxml=/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/12-new-covering-final.xml`; exit `0`. XML units: `{"tests": 97, "failures": 0, "errors": 0, "skipped": 0}`. Actual summary: ['============================== 97 passed in 6.45s ==============================']. Source-stage bytes and hashes: `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/12-new-covering-final.command.json`; log/XML `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/12-new-covering-final.log` / `/Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115/12-new-covering-final.xml`. Earlier-stage snapshots are not claimed to equal later expanded tests.

## Owner-authorized coordinated repair4 bounded result — 2026-11-15T22:31:10.998690+08:00

D-R4-001 phase distinction now passes at frozen_selection and actual evaluator reservation boundary. The byte-identical parent pair had genuine RED (1 behavior failure/1 healthy pass), then immediate GREEN (2 pass); failed affirmative-disposition publication had its own RED1 then GREEN, with exact primary preserved. Grounded final covering matrix97 pass; retained D-R1/R2/R3 and both selection diagnostics6 pass. Complete D204 pass/67warnings. Final full migration489 collected cases plus293 subtests pass/67warnings. Original training51 cases plus289 subtests pass/3warnings. All final named suites have0failures/errors/skips; warning blocks match baseline exactly without suppression. See suite-summary.json, material-probe-results.json and source-stage snapshots under /Users/ahronjanl.rafaelahron.0804icloudcom/KumpasBuilds/holistic-migration-data/evidence/task-d-owner-fix4-worker-20261115.

One earlier full-migration run retained a protected synthetic child-startup subtest failure: its50ms startup deadline expired before the expected specific stderr/exit7 arrived;489 parent cases and292 other subtests passed. The exact protected test then passed1case+2subtests and a serial whole-suite rerun passed489+293, without any source changes. Cause beyond the observed timing boundary is not established; no protected test or timeout was weakened or repaired. RED and this failed full receipt/log/XML remain immutable.

Exactly5 authorized repository paths changed; all51 protections,9 original snapshots, complete199487-byte report prefix, inherited394 source/review inputs (explicit preimage mappings for the5 changed paths), textual source scope, current source/runtime/C identity and caches/Git readbacks verified. The original17 evaluator definitions are AST-identical; all30 original trainer definitions remain, with only the3 explicitly documented publication expectation/decorator extensions. Full lexical definition inventory is separate from parameterized case/subtest counts. Current8-path package, repair delta, before/after images and full evidence inventory union are frozen externally. No real-source arrays/model weights/videos, real optimization/evaluation, SDK/camera/phone/GUI/participants or install/config/provider/Git writes occurred. Original training synthetic converter tests are not actual model export/activation.

This is a repair handoff, NOT D acceptance: independent parent verification and complete spec/quality re-review are mandatory. No budget reset, next repair or real-data/live authority. Unknown/FAR/physical/expert/signer-independent/research/study gates remain unchanged. Simultaneous failed affirmative-disposition rollback plus failed failure persistence and crash/permanent-media/hostile-writer/TOCTOU durability remain explicitly excluded, not promoted from passing synthetic controls.
