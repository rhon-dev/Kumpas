"""Training-only augmentation for hm211 tensors (RETRAINING_PLAN.md Phase 4). Absent parts stay zero; masks only
change where a hand is deliberately dropped. Inputs are never mutated."""
import numpy as np

from .. import augmentation
from . import features_v2


def _present_xy(x):
    """Boolean [..., 211] selecting the XY columns of present points (hands, visible arms, face anchors)."""
    sel = np.zeros(x.shape, dtype=bool)
    xy = lambda start, n, stride: [start + stride * i + c for i in range(n) for c in (0, 1)]
    for start, mask in [(0, 150), (63, 151)]:
        sel[..., xy(start, 21, 3)] = (x[..., mask] == 1)[..., None]
    pose = x[..., 126:150].reshape(x.shape[:-1] + (6, 4))
    visible = (pose[..., 3] >= .5) & (x[..., 152:153] == 1)
    sel[..., xy(126, 6, 4)] = np.repeat(visible, 2, axis=-1)
    sel[..., xy(153, 19, 3)] = (x[..., features_v2.FACE_MASK] == 1)[..., None]
    return sel


SHOULDER_X = [42, 43]  # positions of columns 126 and 130 among the X columns


def spatial(x, rng, rotation=12, scale=(.95, 1.05), shift=.05, jitter=.01):
    """One spatial copy of each [30, 211] sequence: p' = s * R p + shift + N(0, jitter) on present XY only."""
    out = x.astype(np.float64)
    sel = _present_xy(x)
    xcols = np.zeros(x.shape[-1], dtype=bool)
    xcols[[c for c in range(126) if c % 3 == 0] + list(range(126, 150, 4)) + list(range(153, 210, 3))] = True
    for i in range(len(x)):
        theta = np.deg2rad(rng.uniform(-rotation, rotation))
        s, (dx, dy) = rng.uniform(*scale), rng.uniform(-shift, shift, 2)
        c, n = np.cos(theta), np.sin(theta)
        px, py = out[i][:, xcols], out[i][:, np.roll(xcols, 1)]
        nx = s * (c * px - n * py) + dx + rng.normal(0, jitter, px.shape)
        ny = s * (n * px + c * py) + dy + rng.normal(0, jitter, py.shape)
        # shoulders define the normalization (midpoint 0, width 1): rotate them only
        nx[:, SHOULDER_X], ny[:, SHOULDER_X] = (c * px - n * py)[:, SHOULDER_X], (n * px + c * py)[:, SHOULDER_X]
        keep = sel[i][:, xcols]
        out[i][:, xcols] = np.where(keep, nx, px)
        out[i][:, np.roll(xcols, 1)] = np.where(keep, ny, py)
    return out.astype(np.float32)


def rotate5(x, source_ids, seed):
    """The baseline +-5 degree copy (historical angles and hm153 code), with face anchors rotated alike."""
    prefix, receipt = augmentation.rotate_fit(x[..., :153], list(source_ids), partition='fit', seed=seed)
    out = x.copy()
    out[..., :153] = prefix
    for i, angle in enumerate(receipt['angles_degrees']):
        theta = np.deg2rad(angle)
        matrix = np.array([[np.cos(theta), np.sin(theta)], [-np.sin(theta), np.cos(theta)]])
        face = out[i, :, features_v2.FACE].reshape(30, 19, 3)
        present = out[i, :, features_v2.FACE_MASK] == 1
        face[present, :, :2] = face[present, :, :2] @ matrix
        out[i, :, features_v2.FACE] = face.reshape(30, 57)
    receipt['policy'] = 'one_per_original_sequence_coherent_hand_pose_face_anchor_xy_uniform_degrees_[-5,5]'
    return out, receipt


def face_dropout(x, rng, rate):
    """Zero the face block and mask of whole sequences with probability rate."""
    out = x.copy()
    drop = rng.random(len(x)) < rate
    out[drop, :, 153:211] = 0
    return out


def timing(timestamps, rows, rng, trim=2, speed=(.8, 1.25), hand_drop=.2):
    """One [30, 211] sequence from actual observations: trim 0..trim rows per end (at least 8 kept, 4 with a hand, a hand at both ends), a monotone
    time warp u -> u**g with log-uniform g in speed (a uniform speed change is invisible after resampling to 30
    rows), then in hand_drop of sequences one present hand is zeroed for 1-2 consecutive rows."""
    t, rows = np.asarray(timestamps), np.asarray(rows)
    a, b = (int(v) for v in rng.integers(0, trim + 1, 2))
    hand = (rows[:, 150] == 1) | (rows[:, 151] == 1)
    ok = lambda a, b: (len(t) - a - b >= 8 and hand[a] and hand[len(t) - 1 - b]
                       and hand[a:len(t) - b].sum() >= 4)  # trimmed capture stays hm153-eligible in shape
    while not ok(a, b):
        a, b = (a - 1, b) if a >= b else (a, b - 1)
    t, rows = t[a:len(t) - b], rows[a:len(rows) - b]
    g = float(np.exp(rng.uniform(np.log(speed[0]), np.log(speed[1]))))
    if g == 1:
        idx = features_v2.grid_indices(t)
    else:
        target = t[0] + (t[-1] - t[0]) * np.linspace(0, 1, 30) ** g
        idx = np.abs(t[None, :] - target[:, None]).argmin(axis=1)  # first minimum = earlier row on ties
    out = rows[idx].copy()
    if rng.random() < hand_drop:
        slots = [(s, m) for s, m in [(0, 150), (63, 151)] if (out[:, m] == 1).any()]
        start, mask = slots[int(rng.integers(len(slots)))]
        present = np.flatnonzero(out[:, mask] == 1)
        first = int(present[rng.integers(len(present))])
        span = [r for r in (first, first + 1)[:int(rng.integers(1, 3))] if r < 30 and out[r, mask] == 1]
        out[span, start:start + 63], out[span, mask] = 0, 0
    return out
