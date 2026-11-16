"""Synthetic capture-contract evidence, not linguistic/live acceptance."""
import importlib
import numpy as np
import pytest
from training.holistic_migration.features import RawFrame, resample_frames


def test_clock_first_and_due_slot():
    clock = importlib.import_module('training.holistic_migration.sequence').ObservationClock()
    assert [clock.admit(t) for t in [10, 43, 77, 110, 143, 177]] == [True, False, True, False, True, False]


@pytest.mark.parametrize('fps', [30, 60])
def test_clock_quantization(fps):
    clock = importlib.import_module('training.holistic_migration.sequence').ObservationClock()
    times = [round(i * 1000 / fps) for i in range(fps * 2)]
    assert sum(clock.admit(t) for t in times) == 30


@pytest.mark.parametrize('bad', [True, 2.0, -1, 0, 1])
def test_clock_validates_skipped_inputs_without_mutation(bad):
    clock = importlib.import_module('training.holistic_migration.sequence').ObservationClock()
    assert clock.admit(0)
    assert not clock.admit(1)
    with pytest.raises(ValueError):
        clock.admit(bad)
    assert clock.admit(67)


def test_clock_long_gap_has_no_fabrication():
    clock = importlib.import_module('training.holistic_migration.sequence').ObservationClock()
    assert [clock.admit(t) for t in [0, 10000, 10001, 10067]] == [True, True, False, True]


def frames(n=8, spacing=67):
    pose = np.zeros((33, 4), dtype=np.float64)
    pose[:, 3] = 1
    pose[11, :2] = [.3, .4]
    pose[12, :2] = [.7, .4]
    return [RawFrame(i * spacing, pose.copy(), np.full((21, 3), .2 + i / 100), None)
            for i in range(n)]


def test_capture_positive_exact_accepted_resampling():
    observed = frames()
    result = importlib.import_module('training.holistic_migration.sequence').prepare_capture(observed)
    np.testing.assert_array_equal(result.tensor, resample_frames(observed))
    assert (result.reason, result.observation_count, result.hand_count,
            result.start_ms, result.end_ms) == ('eligible', 8, 8, 0, 469)
    assert type(result.tensor) is np.ndarray and result.tensor.dtype == np.float32


from dataclasses import replace


def capture(observed):
    return importlib.import_module('training.holistic_migration.sequence').prepare_capture(observed)


def test_capture_trims_only_ends_and_keeps_internal_missing_hands():
    observed = frames(12)
    for i in [0, 1, 4, 6, 10, 11]:
        observed[i] = replace(observed[i], left_hand=None)
    result = capture(observed)
    assert (result.observation_count, result.hand_count, result.start_ms, result.end_ms) == (8, 6, 134, 603)
    np.testing.assert_array_equal(result.tensor, resample_frames(observed[2:10]))
    assert (result.tensor[:, 150] == 0).any()
    assert (result.tensor[:, 151] == 0).all()


@pytest.mark.parametrize('case,reason', [
    ('empty','no_hands'), ('handless','no_hands'), ('few','too_few_observations'),
    ('few_hands','too_few_hand_observations'), ('short','too_short'), ('long','too_long'),
    ('gap','observation_gap'), ('pose','invalid_pose')])
def test_capture_fixed_coverage_reasons(case, reason):
    observed = frames()
    if case == 'empty': observed = []
    if case == 'handless': observed = [replace(f, left_hand=None) for f in observed]
    if case == 'few': observed = frames(7)
    if case == 'few_hands':
        observed = [replace(f, left_hand=None) if i not in [0, 3, 7] else f for i, f in enumerate(observed)]
    if case == 'short': observed = frames(8, 50)
    if case == 'long': observed = frames(77)
    if case == 'gap': observed = [replace(f, timestamp_ms=f.timestamp_ms + (200 if i >= 4 else 0)) for i, f in enumerate(observed)]
    if case == 'pose': observed[4] = replace(observed[4], pose=None)
    result = capture(observed)
    assert result.reason == reason and result.tensor is None


@pytest.mark.parametrize('gap,eligible', [(250, True), (251, False)])
def test_capture_gap_boundary(gap, eligible):
    observed = frames()
    observed = [replace(f, timestamp_ms=f.timestamp_ms + (gap - 67 if i >= 4 else 0)) for i, f in enumerate(observed)]
    assert (capture(observed).tensor is not None) is eligible


@pytest.mark.parametrize('duration', [400, 5000])
def test_capture_inclusive_duration(duration):
    n = 8 if duration == 400 else 76
    observed = [replace(f, timestamp_ms=round(i * duration / (n-1))) for i, f in enumerate(frames(n))]
    assert capture(observed).reason == 'eligible'


@pytest.mark.parametrize('kind', ['bool_timestamp','float_timestamp','duplicate','nonfinite','shape','masked','matrix'])
def test_capture_validates_all_even_trimmed_rows(kind):
    observed = frames()
    observed.insert(0, RawFrame(0, None, None, None))
    observed = [replace(f, timestamp_ms=i * 67) for i, f in enumerate(observed)]
    bad = observed[0]
    if kind == 'bool_timestamp': bad = replace(bad, timestamp_ms=False)
    if kind == 'float_timestamp': bad = replace(bad, timestamp_ms=0.0)
    if kind == 'duplicate': bad = replace(bad, timestamp_ms=67)
    if kind == 'nonfinite': bad = replace(bad, face=np.full((478,3), np.nan))
    if kind == 'shape': bad = replace(bad, left_hand=np.zeros((20,3)))
    if kind == 'masked': bad = replace(bad, face=np.ma.array(np.zeros((1,3))))
    if kind == 'matrix': bad = replace(bad, face=np.zeros((1,3)).view(np.matrix))
    observed[0] = bad
    with pytest.raises(ValueError): capture(observed)



def test_plain_rgb_resize_uses_area_and_preserves_rgb():
    import cv2
    image = np.empty((18, 40, 3), dtype=np.uint8)
    image[:] = [17, 43, 91]
    image = image[:, ::-1]
    prepared = importlib.import_module('training.holistic_migration.sequence').prepare_image(image, cv2)
    np.testing.assert_array_equal(prepared, cv2.resize(image, (640,360), interpolation=cv2.INTER_AREA))
    assert prepared.flags.c_contiguous and prepared.shape == (360,640,3)


@pytest.mark.parametrize('image', [np.zeros((2,2,3)), np.zeros((0,2,3),np.uint8),
                                  np.zeros((2,2,4),np.uint8), np.ma.array(np.zeros((2,2,3),np.uint8))])
def test_image_rejects_semantic_or_invalid_arrays(image):
    import cv2
    with pytest.raises(ValueError):
        importlib.import_module('training.holistic_migration.sequence').prepare_image(image, cv2)



def test_capture_reports_source_denominator_even_when_no_bounded_interval():
    observed=[replace(f,left_hand=None) for f in frames()]
    result=capture(observed)
    assert result.reason=='no_hands'
    assert (result.source_observation_count,result.source_start_ms,result.source_end_ms)==(8,0,469)
    assert result.observation_count==0 and result.start_ms is None and result.end_ms is None
