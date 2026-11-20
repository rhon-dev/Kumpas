"""Fit-only frozen population moments, never training-mode serving.

Supported native Sequential graphs are deliberately bounded; no custom layers,
nested graphs, shared layers or non-channel-last normalization are interpreted.
TensorFlow stays lazy so CLI admission/help do not initialize the native runtime.
"""
from pathlib import Path
import hashlib
import numpy as np
from . import dataset as d

PROTOCOL = 'tiny_fit_layerwise_exact_moments_v1'


def array_identity(value):
    a = np.asarray(value)
    return dict(shape=list(a.shape), dtype=str(a.dtype),
                sha256=hashlib.sha256(a.tobytes(order='C')).hexdigest())


def _moments(value):
    a = np.asarray(value, dtype=np.float64)
    axes = tuple(range(a.ndim - 1))
    mean = a.mean(axis=axes)
    variance = ((a - mean) ** 2).mean(axis=axes)
    return mean.astype(np.float32), variance.astype(np.float32)


def _locked(model, moments):
    excluded = {id(v) for v in moments}
    return dict(weights=[array_identity(v.numpy()) for v in model.weights if id(v) not in excluded],
                optimizer=[array_identity(v.numpy()) for v in model.optimizer.variables],
                configuration=d.canonical_hash(dict(model=model.get_config(), optimizer=model.optimizer.get_config())))


def _finite(value):
    if not np.isfinite(np.asarray(value)).all():
        raise ValueError('nonfinite calibration state/activation/moment')


def _validate(model, x):
    import tensorflow as tf
    if type(model) is not tf.keras.Sequential or not model.built or getattr(model, 'optimizer', None) is None:
        raise ValueError('built compiled native Sequential model required')
    allowed = (tf.keras.layers.Conv1D, tf.keras.layers.BatchNormalization,
               tf.keras.layers.MaxPooling1D, tf.keras.layers.LSTM, tf.keras.layers.Dropout,
               tf.keras.layers.Dense, tf.keras.layers.Flatten)
    if len({id(layer) for layer in model.layers}) != len(model.layers):
        raise ValueError('shared Sequential layers are unsupported')
    if any(type(layer) not in allowed for layer in model.layers):
        raise ValueError('unsupported native calibration layer')
    if not isinstance(x, np.ndarray) or x.dtype != np.float32 or x.ndim != 3 or not len(x):
        raise ValueError('nonempty Float32 batch/time/channel fit inputs required')
    if tuple(x.shape[1:]) != tuple(model.input_shape[1:]):
        raise ValueError('calibration input/model dimensions differ')
    _finite(x)
    bn = [layer for layer in model.layers if type(layer) is tf.keras.layers.BatchNormalization]
    if not bn or any(layer.axis != -1 or not layer.trainable for layer in bn):
        raise ValueError('trainable channel-last BatchNorm layers required')
    for layer in model.layers:
        if layer.compute_dtype != 'float32' or getattr(layer, 'stateful', False):
            raise ValueError('stateless Float32 calibration family required')
    for v in model.weights + model.optimizer.variables: _finite(v.numpy())
    for layer in bn:
        if (layer.moving_variance.numpy() < 0).any(): raise ValueError('negative moving variance')
    return bn


def calibrate(model, x):
    """Estimate population moments; restore attempt-owned state on any failure."""
    bn = _validate(model, x)
    moments = [v for layer in bn for v in [layer.moving_mean, layer.moving_variance]]
    variables = model.weights + model.optimizer.variables
    snapshot = [(v, v.numpy().copy()) for v in variables]
    before = _locked(model, moments)
    records = []
    activation = x
    try:
        for index, layer in enumerate(model.layers):
            if layer in bn:
                mean, variance = _moments(activation)
                _finite(mean); _finite(variance)
                if (variance < 0).any(): raise ValueError('negative calibrated variance')
                record = dict(index=index, name=layer.name,
                              pre_mean=layer.moving_mean.numpy().tolist(),
                              pre_variance=layer.moving_variance.numpy().tolist(),
                              post_mean=mean.tolist(), post_variance=variance.tolist())
                layer.moving_mean.assign(mean)
                layer.moving_variance.assign(variance)
                records.append(record)
            activation = layer(activation, training=False)
            _finite(activation)
        after = _locked(model, moments)
        d.same(after, before, 'calibration frozen state')
        return dict(schema_version=1, protocol=PROTOCOL, source_sha256=d.sha256(Path(__file__)),
                    input=array_identity(x), finite=True, layers=records,
                    locked_before=before, locked_after=after)
    except BaseException as exc:
        for variable, value in snapshot:
            try: variable.assign(value)
            except BaseException as rollback:
                exc.add_note('calibration rollback failed: ' + repr(rollback))
        raise


def verify_receipt(model, x, receipt):
    """Read-only binding of persisted native moments and frozen nonmoment state."""
    bn = _validate(model, x)
    moments = [v for layer in bn for v in [layer.moving_mean, layer.moving_variance]]
    if type(receipt) is not dict or set(receipt) != {'schema_version','protocol','source_sha256','input','finite','layers','locked_before','locked_after'}:
        raise ValueError('exact native calibration receipt required')
    d.same(receipt['schema_version'], 1, 'calibration receipt schema')
    d.same(receipt['protocol'], PROTOCOL, 'calibration receipt protocol')
    d.same(receipt['source_sha256'], d.sha256(Path(__file__)), 'calibration helper source')
    d.same(receipt['input'], array_identity(x), 'calibration exact fit input')
    d.same(receipt['finite'], True, 'calibration finite checks')
    d.same(receipt['locked_before'], receipt['locked_after'], 'calibration unchanged frozen state')
    d.same(receipt['locked_after'], _locked(model, moments), 'calibration checkpoint frozen state')
    d.same(len(receipt['layers']), len(bn), 'calibration normalization count')
    activation = x
    records = iter(receipt['layers'])
    for index, layer in enumerate(model.layers):
        if layer in bn:
            record = next(records)
            if type(record) is not dict or set(record) != {'index','name','pre_mean','pre_variance','post_mean','post_variance'}:
                raise ValueError('exact normalization receipt required')
            d.same(record['index'], index, 'calibration graph order')
            d.same(record['name'], layer.name, 'calibration normalization name')
            for key in ['pre_mean','pre_variance','post_mean','post_variance']:
                value = np.asarray(record[key])
                if value.shape != tuple(layer.moving_mean.shape) or value.dtype.kind not in 'fi':
                    raise ValueError('invalid calibration moment layout')
                _finite(value)
                if 'variance' in key and (value < 0).any(): raise ValueError('negative receipt variance')
            mean, variance = _moments(activation)
            d.same(record['post_mean'], mean.tolist(), 'recomputed fit population mean')
            d.same(record['post_variance'], variance.tolist(), 'recomputed fit population variance')
            d.same(record['post_mean'], layer.moving_mean.numpy().tolist(), 'checkpoint calibrated mean')
            d.same(record['post_variance'], layer.moving_variance.numpy().tolist(), 'checkpoint calibrated variance')
        activation = layer(activation, training=False)
        _finite(activation)
    d.same(receipt['locked_after'], _locked(model, moments), 'receipt readback unchanged state')


def verify_precalibration(model, x, receipt, pre_probabilities):
    """Bind recorded pre-moments to optimizer-only inference on an isolated clone.

    The calibrated candidate is never assigned pre-state, compiled, or optimized.
    Check its complete variable/configuration identity even when replay fails.
    """
    import tensorflow as tf
    _validate(model, x)
    def state():
        return d.canonical_hash(dict(variables=[array_identity(v.numpy()) for v in model.variables + model.optimizer.variables],
                                     model=model.get_config(), compile=model.get_compile_config(),
                                     optimizer=model.optimizer.get_config()))
    before = state()
    try:
        verify_receipt(model, x, receipt)
        replay_model = tf.keras.models.clone_model(model)
        replay_model.set_weights(model.get_weights())
        for record in receipt['layers']:
            layer = replay_model.layers[record['index']]
            layer.moving_mean.assign(record['pre_mean'])
            layer.moving_variance.assign(record['pre_variance'])
        replay = np.asarray(replay_model(x, training=False))
        expected = np.asarray(pre_probabilities)
        _finite(replay); _finite(expected)
        if replay.shape != expected.shape or not np.allclose(replay, expected, rtol=1e-6, atol=1e-7):
            raise ValueError('pre-calibration replay probabilities differ')
    finally:
        d.same(state(), before, 'pre-calibration replay unchanged candidate state')
