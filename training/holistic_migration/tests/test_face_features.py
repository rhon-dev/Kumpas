"""Independent synthetic geometry and policy tests; not anatomical acceptance."""
from dataclasses import replace
import importlib
import importlib.util
import numpy as np
import pytest
from training.holistic_migration import features as historical
from .test_sequence import frames


def face_module():
    # Initial RED exercises the accepted baseline rather than a missing import.
    name = 'training.holistic_migration.face_features'
    return importlib.import_module(name) if importlib.util.find_spec(name) else historical


def observed(n=8, spacing=67):
    face = np.arange(1434, dtype=np.float64).reshape(478, 3) / 1000
    return [replace(f, face=face.copy()) for f in frames(n, spacing)]


@pytest.mark.parametrize('bad', [np.empty((0, 3)), np.zeros((477, 3)), np.zeros((479, 3)),
    np.ma.array(np.zeros((478, 3))), np.zeros((478, 3), dtype=bool), np.zeros((478, 2)),
    np.full((478, 3), np.nan), np.zeros((478, 3), dtype=complex)])
def test_malformed_face_is_error_even_without_shoulders(bad):
    with pytest.raises(ValueError, match='face'):
        face_module().pack_frame(replace(observed()[0], pose=None, face=bad))


def test_resampling_uses_independent_integer_time_grid_and_ties():
    fs = observed(3)
    fs = [replace(f, timestamp_ms=t) for f, t in zip(fs, [0, 100, 200])]
    sampler = getattr(face_module(), 'resample_frames', historical.resample_frames)
    result = sampler(fs, steps=5)
    assert result.shape == (5, 1588), 'time grid must carry full face rows'
    for row, index in zip(result, [0, 0, 1, 1, 2]):
        np.testing.assert_array_equal(row, face_module().pack_frame(fs[index]))
    denominator = 29
    expected = [min(range(3), key=lambda j: abs([0, 100, 200][j]*denominator-i*200)) for i in range(30)]
    np.testing.assert_array_equal(sampler(fs), np.stack([face_module().pack_frame(fs[i]) for i in expected]))


def test_capture_rejects_internal_face_gap_without_deleting_it():
    from training.holistic_migration.sequence import prepare_capture as baseline
    fs = observed()
    fs[4] = replace(fs[4], face=None)
    result = getattr(face_module(), 'prepare_capture', baseline)(fs)
    assert result.reason == 'invalid_face', 'internal absent face cannot enter eligible capture'
    assert result.tensor is None and result.observation_count == result.source_observation_count == 8


def test_float32_face_overflow_is_rejected():
    with pytest.raises(ValueError, match='nonfinite'):
        face_module().pack_frame(replace(observed()[0], face=np.full((478, 3), 1e40)))


def test_exact_layout_geometry_and_historical_prefix_without_mutation():
    f = observed()[0]
    before = [a.copy() if a is not None else None for a in (f.pose, f.left_hand, f.right_hand, f.face)]
    row = face_module().pack_frame(f)
    assert row.shape == (1588,), 'face-inclusive row must have 1588 values, not historical 153'
    assert row.dtype == np.float32 and type(row) is np.ndarray
    np.testing.assert_array_equal(row[:153], historical.pack_frame(f))
    width = np.hypot(.7 - .3, 0)
    expected = np.empty((478, 3), np.float64)
    expected[:, 0] = (f.face[:, 0] - .5) / width
    expected[:, 1] = (f.face[:, 1] - .4) / width
    expected[:, 2] = (f.face[:, 2] - sum(f.face[:, 2]) / 478) / width
    np.testing.assert_allclose(row[153:1587], expected.astype(np.float32).ravel(), rtol=0, atol=2e-7)
    assert row[1587] == 1 and row[151] == 0
    for a, b in zip(before, (f.pose, f.left_hand, f.right_hand, f.face)):
        if a is None: assert b is None
        else: np.testing.assert_array_equal(a, b)


@pytest.mark.parametrize('case,reason', [
    ('empty','no_hands'), ('no_hands','no_hands'), ('few','too_few_observations'),
    ('few_hands','too_few_hand_observations'), ('short','too_short'), ('long','too_long'),
    ('gap','observation_gap'), ('pose','invalid_pose')])
def test_historical_precedence_with_missing_face(case, reason):
    fs = [replace(f, face=None) for f in observed()]
    if case == 'empty': fs = []
    if case == 'no_hands': fs = [replace(f, left_hand=None) for f in fs]
    if case == 'few': fs = fs[:7]
    if case == 'few_hands': fs = [replace(f, left_hand=None) if i not in [0,3,7] else f for i,f in enumerate(fs)]
    if case == 'short': fs = [replace(f, timestamp_ms=i*50) for i,f in enumerate(fs)]
    if case == 'long': fs = [replace(f, timestamp_ms=i*1000) for i,f in enumerate(fs)]
    if case == 'gap': fs = [replace(f, timestamp_ms=f.timestamp_ms+(200 if i>=4 else 0)) for i,f in enumerate(fs)]
    if case == 'pose': fs[4] = replace(fs[4], pose=None)
    result = face_module().prepare_capture(fs)
    assert result.reason == reason and result.tensor is None


def test_trimmed_face_missingness_permitted_internal_hand_missingness_retained():
    fs = observed(12)
    for i in [0,1,4,6,10,11]: fs[i] = replace(fs[i], left_hand=None)
    for i in [0,1,10,11]: fs[i] = replace(fs[i], face=None)
    result = face_module().prepare_capture(fs)
    assert (result.reason, result.observation_count, result.hand_count, result.source_observation_count) == ('eligible',8,6,12)
    assert result.tensor.shape == (30,1588)
    np.testing.assert_array_equal(result.tensor, face_module().resample_frames(fs[2:10]))
    assert (result.tensor[:,150] == 0).any()
    assert (result.tensor[:,151] == 0).all()
    assert (result.tensor[:,[152,1587]] == 1).all()
    fs[0] = replace(fs[0], face=np.empty((0,3)))
    with pytest.raises(ValueError, match='face'): face_module().prepare_capture(fs)


@pytest.mark.parametrize('case', ['none','visibility','width'])
def test_unusable_shoulders_zero_every_mask(case):
    f = observed()[0]
    if case == 'none': f = replace(f, pose=None)
    else:
        pose = f.pose.copy()
        if case == 'visibility': pose[11,3] = .499
        if case == 'width': pose[12,:2] = pose[11,:2]
        f = replace(f, pose=pose)
    np.testing.assert_array_equal(face_module().pack_frame(f), np.zeros(1588,np.float32))


def test_missing_face_preserves_historical_row():
    f = replace(observed()[0], face=None)
    result = face_module().pack_frame(f)
    np.testing.assert_array_equal(result[:153],historical.pack_frame(f))
    assert not result[153:].any()


@pytest.mark.parametrize('bad', [True,1,1.0,0,-1])
def test_resample_rejects_invalid_steps(bad):
    with pytest.raises(ValueError): face_module().resample_frames(observed(),steps=bad)


@pytest.mark.parametrize('case', ['one','duplicate','descending','missing_face','missing_pose','timestamp_bool','timestamp_float'])
def test_resampling_never_bridges_invalid_observations(case):
    fs = observed()
    if case == 'one': fs = fs[:1]
    if case == 'duplicate': fs[1] = replace(fs[1],timestamp_ms=0)
    if case == 'descending': fs.reverse()
    if case == 'missing_face': fs[3] = replace(fs[3],face=None)
    if case == 'missing_pose': fs[3] = replace(fs[3],pose=None)
    if case == 'timestamp_bool': fs[0] = replace(fs[0],timestamp_ms=False)
    if case == 'timestamp_float': fs[0] = replace(fs[0],timestamp_ms=0.0)
    with pytest.raises(ValueError): face_module().resample_frames(fs)


def test_face_float64_intermediate_overflow_rejected_without_warning():
    f = replace(observed()[0], face=np.full((478,3),1e308))
    with np.errstate(all='raise'), pytest.raises(ValueError,match='nonfinite'):
        face_module().pack_frame(f)


@pytest.mark.parametrize('gap,reason', [(250,'eligible'),(251,'observation_gap')])
def test_gap_inclusive_boundary(gap,reason):
    fs = observed()
    delta = gap - 67
    fs = [replace(f,timestamp_ms=f.timestamp_ms+(delta if i>=4 else 0)) for i,f in enumerate(fs)]
    assert face_module().prepare_capture(fs).reason == reason


@pytest.mark.parametrize('duration,reason',[(399,'too_short'),(400,'eligible'),(5000,'eligible'),(5001,'too_long')])
def test_duration_inclusive_boundary(duration,reason):
    count = 26
    fs = observed(count)
    fs = [replace(f,timestamp_ms=i*duration//(count-1)) for i,f in enumerate(fs)]
    assert face_module().prepare_capture(fs).reason == reason
