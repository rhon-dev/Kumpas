"""Native synthetic controls; no admitted/real tensors are used here."""
import importlib
import importlib.util
import json
import numpy as np
import pytest


def calibration():
    name='training.holistic_migration.batchnorm_calibration'
    assert importlib.util.find_spec(name), 'native BatchNorm calibration helper missing'
    return importlib.import_module(name)


def small_model():
    import tensorflow as tf
    tf.keras.utils.set_random_seed(20260705)
    m=tf.keras.Sequential([tf.keras.layers.Input((2,2)),
        tf.keras.layers.BatchNormalization(epsilon=.25, name='first'),
        tf.keras.layers.Dropout(.9),
        tf.keras.layers.Conv1D(2,1,use_bias=False, name='mix'),
        tf.keras.layers.BatchNormalization(epsilon=.5, name='second'),
        tf.keras.layers.Flatten(),tf.keras.layers.Dense(2,activation='softmax')])
    m.compile(tf.keras.optimizers.Adam(.001),'sparse_categorical_crossentropy')
    m.get_layer('mix').kernel.assign(np.array([[[2.,1.],[-1.,3.]]],np.float32))
    return m


def inputs():
    return np.array([[[1,2],[3,6]],[[5,4],[7,8]]],np.float32)


def test_exact_population_moments_sequential_dependency_and_frozen_state(tmp_path):
    c=calibration(); m=small_model(); x=inputs()
    m.train_on_batch(x,np.array([0,1]))  # allocate actual Adam slots
    # Restore deterministic gamma/beta/kernel after optimizer; independent scalar oracle.
    for name in ['first','second']:
        m.get_layer(name).gamma.assign([1,1]); m.get_layer(name).beta.assign([0,0])
    m.get_layer('mix').kernel.assign([[[2.,1.],[-1.,3.]]])
    before=[v.numpy().copy() for v in m.variables+m.optimizer.variables]
    compile_config=json.dumps(m.get_compile_config(),sort_keys=True)
    config=json.dumps(m.get_config(),sort_keys=True)
    receipt=c.calibrate(m,x)
    np.testing.assert_array_equal(m.get_layer('first').moving_mean.numpy(),[4,5])
    np.testing.assert_array_equal(m.get_layer('first').moving_variance.numpy(),[5,5])
    # Every scalar computed independently, not using helper/reduction implementation.
    normalized=[[(a-4)/(5.25**.5),(b-5)/(5.25**.5)] for a,b in [(1,2),(3,6),(5,4),(7,8)]]
    channels=[[2*a-b for a,b in normalized],[a+3*b for a,b in normalized]]
    expected_mean=[sum(v)/4 for v in channels]
    expected_var=[sum((z-mu)**2 for z in v)/4 for v,mu in zip(channels,expected_mean)]
    np.testing.assert_allclose(m.get_layer('second').moving_mean.numpy(),expected_mean,atol=1e-6)
    np.testing.assert_allclose(m.get_layer('second').moving_variance.numpy(),expected_var,rtol=1e-6)
    assert json.dumps(m.get_config(),sort_keys=True)==config
    # BN moments alone differ; Dropout RNG state also remains frozen at inference.
    moments={id(v) for name in ['first','second'] for v in [m.get_layer(name).moving_mean,m.get_layer(name).moving_variance]}
    for a,v in zip(before,m.variables+m.optimizer.variables):
        if id(v) not in moments: np.testing.assert_array_equal(a,v.numpy())
    assert json.dumps(m.get_compile_config(),sort_keys=True)==compile_config
    assert receipt['protocol']=='tiny_fit_layerwise_exact_moments_v1'
    assert receipt['finite'] is True
    assert receipt['locked_before']==receipt['locked_after']
    assert len(receipt['layers'])==2
    p=m(x,training=False).numpy()
    path=tmp_path/'native.keras'; m.save(path)
    import tensorflow as tf
    loaded=tf.keras.models.load_model(path)
    np.testing.assert_allclose(loaded(x,training=False).numpy(),p,rtol=1e-6,atol=1e-7)
    np.testing.assert_allclose(np.concatenate([loaded(z[None],training=False).numpy() for z in x]),p,rtol=1e-6,atol=1e-7)


def test_failure_rolls_back_all_moments_and_preserves_primary_exception(monkeypatch):
    c=calibration(); m=small_model(); x=inputs()
    before=[v.numpy().copy() for v in m.weights+m.optimizer.variables]
    failure=RuntimeError('second normalization diagnostic fault')
    real=c._moments; calls=[]
    def fail(value):
        calls.append(1)
        if len(calls)==2: raise failure
        return real(value)
    monkeypatch.setattr(c,'_moments',fail)
    with pytest.raises(RuntimeError) as raised: c.calibrate(m,x)
    assert raised.value is failure
    for a,v in zip(before,m.weights+m.optimizer.variables): np.testing.assert_array_equal(a,v.numpy())


@pytest.mark.parametrize('fault',['nan_input','dtype','rank','channels','empty','nonfinite_weight','negative_variance','unsupported_model','unsupported_layer','axis','nonfinite_activation'])
def test_native_input_model_and_finite_guards_are_transactional(fault):
    import tensorflow as tf
    c=calibration(); m=small_model(); x=inputs()
    if fault=='nan_input': x[0,0,0]=np.nan
    if fault=='dtype': x=x.astype(np.float64)
    if fault=='rank': x=x[:,0]
    if fault=='channels': x=np.ones((2,2,3),np.float32)
    if fault=='empty': x=x[:0]
    if fault=='nonfinite_weight': m.get_layer('mix').kernel.assign([[[np.inf,1],[1,1]]])
    if fault=='negative_variance': m.get_layer('first').moving_variance.assign([-1,1])
    if fault=='unsupported_model':
        m=tf.keras.Model(m.inputs,m.outputs)
        m.compile(tf.keras.optimizers.Adam(.001),'mse')
    if fault=='unsupported_layer':
        m=tf.keras.Sequential([tf.keras.layers.Input((2,2)),tf.keras.layers.BatchNormalization(),tf.keras.layers.Lambda(lambda z:z)])
        m.compile(tf.keras.optimizers.Adam(.001),'mse')
    if fault=='axis':
        m=tf.keras.Sequential([tf.keras.layers.Input((2,2)),tf.keras.layers.BatchNormalization(axis=1)])
        m.compile(tf.keras.optimizers.Adam(.001),'mse')
    if fault=='nonfinite_activation': m.get_layer('mix').kernel.assign([[[3e38,3e38],[3e38,3e38]]])
    before=[v.numpy().copy() for v in m.weights+m.optimizer.variables]
    with pytest.raises(ValueError): c.calibrate(m,x)
    for a,v in zip(before,m.weights+m.optimizer.variables): np.testing.assert_array_equal(a,v.numpy())


def test_native_receipt_is_verified_against_reloaded_model_and_inputs(tmp_path):
    c=calibration(); m=small_model(); x=inputs()
    m.train_on_batch(x,np.array([0,1]))
    receipt=c.calibrate(m,x)
    verifier=getattr(c,'verify_receipt',None)
    assert callable(verifier), 'native receipt consumer missing'
    path=tmp_path/'receipt-native.keras'; m.save(path)
    import tensorflow as tf
    loaded=tf.keras.models.load_model(path)
    assert verifier(loaded,x,receipt) is None


@pytest.mark.parametrize('fault',['protocol','source','input','finite','extra','index','pre_nan','pre_negative','pre_shape','post_rebound','locked','layer_count'])
def test_native_receipt_denies_stale_tampered_or_nonmoment_rebound(fault):
    import copy
    c=calibration(); m=small_model(); x=inputs(); receipt=c.calibrate(m,x)
    receipt=copy.deepcopy(receipt)
    if fault=='protocol': receipt['protocol']='batch_mode_diagnostic'
    if fault=='source': receipt['source_sha256']='0'*64
    if fault=='input': x=x.copy(); x[0,0,0]+=1
    if fault=='finite': receipt['finite']=False
    if fault=='extra': receipt['bypass']=True
    if fault=='index': receipt['layers'][0]['index']=7
    if fault=='pre_nan': receipt['layers'][0]['pre_mean'][0]=float('nan')
    if fault=='pre_negative': receipt['layers'][0]['pre_variance'][0]=-1
    if fault=='pre_shape': receipt['layers'][0]['pre_mean'].append(0)
    if fault=='post_rebound':
        m.get_layer('first').moving_mean.assign([99,99])
        receipt['layers'][0]['post_mean']=[99.,99.]
    if fault=='locked': m.get_layer('mix').kernel.assign([[[1,2],[3,4]]])
    if fault=='layer_count': receipt['layers'].pop()
    before=[v.numpy().copy() for v in m.weights+m.optimizer.variables]
    with pytest.raises(ValueError): c.verify_receipt(m,x,receipt)
    for a,v in zip(before,m.weights+m.optimizer.variables): np.testing.assert_array_equal(a,v.numpy())


@pytest.mark.parametrize('fault',['shared','no_bn','no_optimizer','stateful','frozen_bn'])
def test_native_model_family_guards(fault):
    import tensorflow as tf
    c=calibration(); m=small_model(); x=inputs()
    if fault=='shared':
        bn=tf.keras.layers.BatchNormalization()
        m=tf.keras.Sequential([tf.keras.layers.Input((2,2)),bn,bn])
        m.compile(tf.keras.optimizers.Adam(.001),'mse')
    if fault=='no_bn':
        m=tf.keras.Sequential([tf.keras.layers.Input((2,2)),tf.keras.layers.Dense(2)])
        m.compile(tf.keras.optimizers.Adam(.001),'mse')
    if fault=='no_optimizer':
        m=tf.keras.Sequential([tf.keras.layers.Input((2,2)),tf.keras.layers.BatchNormalization()])
    if fault=='stateful':
        m=tf.keras.Sequential([tf.keras.layers.Input(batch_shape=(2,2,2)),tf.keras.layers.BatchNormalization(),tf.keras.layers.LSTM(2,stateful=True)])
        m.compile(tf.keras.optimizers.Adam(.001),'mse')
    if fault=='frozen_bn': m.get_layer('first').trainable=False
    with pytest.raises(ValueError): c.calibrate(m,x)


@pytest.mark.parametrize('fault',['healthy','pre_mean','pre_variance','shape','nan','clone','assignment','inference'])
def test_isolated_precalibration_replay_preserves_every_candidate_state_on_success_and_failure(tmp_path,monkeypatch,fault):
    import copy
    import tensorflow as tf
    c=calibration(); m=small_model(); x=inputs()
    m.train_on_batch(x,np.array([0,1]))
    pre=m(x,training=False).numpy(); receipt=c.calibrate(m,x)
    path=tmp_path/'replay-native.keras'; m.save(path); m=tf.keras.models.load_model(path)
    receipt=copy.deepcopy(receipt)
    calibrated=m(x,training=False).numpy()
    state=[v.numpy().copy() for v in m.variables+m.optimizer.variables]
    configuration=json.dumps(dict(model=m.get_config(),compile=m.get_compile_config(),optimizer=m.optimizer.get_config()),sort_keys=True)
    if fault in ['pre_mean','pre_variance']: receipt['layers'][0][fault][0]+=10000.
    if fault=='shape': pre=pre[:1]
    if fault=='nan': pre=pre.copy(); pre[0,0]=np.nan
    sentinel=RuntimeError('isolated replay '+fault)
    if fault in ['clone','assignment','inference']:
        clone_model=tf.keras.models.clone_model
        def fail(*args,**kwargs): raise sentinel
        def clone(source):
            if fault=='clone': raise sentinel
            result=clone_model(source)
            if fault=='assignment': monkeypatch.setattr(result.get_layer('first').moving_mean,'assign',fail)
            if fault=='inference': monkeypatch.setattr(result,'call',fail)
            return result
        monkeypatch.setattr(tf.keras.models,'clone_model',clone)
    if fault=='healthy': assert c.verify_precalibration(m,x,receipt,pre) is None
    elif fault in ['clone','assignment','inference']:
        with pytest.raises(RuntimeError) as raised: c.verify_precalibration(m,x,receipt,pre)
        # Native Keras __call__ wraps an inference exception; our verifier adds no wrapper.
        if fault=='inference': assert 'isolated replay inference' in str(raised.value)
        else: assert raised.value is sentinel
    else:
        with pytest.raises(ValueError): c.verify_precalibration(m,x,receipt,pre)
    assert configuration==json.dumps(dict(model=m.get_config(),compile=m.get_compile_config(),optimizer=m.optimizer.get_config()),sort_keys=True)
    for expected,v in zip(state,m.variables+m.optimizer.variables): np.testing.assert_array_equal(v.numpy(),expected)
    np.testing.assert_array_equal(m(x,training=False).numpy(),calibrated)


def test_secondary_rollback_failure_retains_primary_and_attempts_later_restorations(monkeypatch):
    c=calibration(); m=small_model(); x=inputs(); variables=m.weights+m.optimizer.variables
    snapshots=[v.numpy().copy() for v in variables]; attempted=[]
    primary=RuntimeError('primary second-moment failure'); secondary=RuntimeError('secondary rollback failure')
    real=c._moments; calls=[]
    def moments(value):
        calls.append(1)
        if len(calls)==2: raise primary
        return real(value)
    monkeypatch.setattr(c,'_moments',moments)
    for index,variable in enumerate(variables):
        assign=variable.assign
        def tracked(value,index=index,assign=assign):
            if len(calls)==2:
                attempted.append(index)
                if index==0: raise secondary
            return assign(value)
        monkeypatch.setattr(variable,'assign',tracked)
    with pytest.raises(RuntimeError) as raised: c.calibrate(m,x)
    assert raised.value is primary
    assert attempted==list(range(len(variables)))
    assert any('secondary rollback failure' in note for note in raised.value.__notes__)
    for expected,v in zip(snapshots[1:],variables[1:]): np.testing.assert_array_equal(v.numpy(),expected)
