#!/usr/bin/env python3
"""KUMPAS Phase 6 — corrective feedback engine (Python reference).

Compares a learner's landmark sequence against the class gold standard and
produces structured feedback on four dimensions (PRD §1): TIMING, MOTION,
HANDSHAPE, ORIENTATION. This is the pedagogical core — the Kotlin port in
app/lib/feedback_engine must stay behaviourally identical to this reference.

Input sequences are (30, 258) no_face frames, already normalized by the
preprocessing pipeline (mid-hip centered, torso scaled) — so position
comparisons are signer-size- and camera-distance-invariant.

Pipeline:
  1. DTW-align learner to gold on wrist trajectories (timing-invariant view).
  2. TIMING     — warping-path slope: sustained tempo deviation.
  3. MOTION     — mean aligned wrist-position error + dominant displacement
                  direction of the error.
  4. HANDSHAPE  — per-aligned-frame finger configuration relative to the
                  wrist (translation-invariant), per-finger error.
  5. ORIENTATION— palm-plane normal angle between learner and gold.

Each dimension yields score in [0, 1] (0 = matches gold). Scores above
per-dimension thresholds become FeedbackItem objects with human-readable
prompts, worst first. Thresholds are provisional pending expert calibration.
"""

import json
from dataclasses import dataclass, field, asdict

import numpy as np

# ---- feature layout (no_face, 258) ----
POSE_N = 33
L_WRIST_P, R_WRIST_P = 15, 16          # pose wrist landmark indices
LHAND0, RHAND0 = 132, 132 + 63          # hand blocks, 21*3 each
WRIST_H, INDEX_MCP, PINKY_MCP = 0, 5, 17
FINGERS = {  # hand landmark indices per finger (MCP..TIP)
    "thumb": [1, 2, 3, 4], "index": [5, 6, 7, 8], "middle": [9, 10, 11, 12],
    "ring": [13, 14, 15, 16], "pinky": [17, 18, 19, 20],
}

THRESHOLDS = {"timing": 0.30, "motion": 0.25, "handshape": 0.22, "orientation": 0.25}


@dataclass
class FeedbackItem:
    dimension: str        # timing | motion | handshape | orientation
    severity: float       # score in [0,1]
    hand: str             # "left" | "right" | "both" | "-"
    prompt: str           # human-readable corrective instruction


@dataclass
class FeedbackReport:
    target_label: str
    overall_match: float               # 1 - weighted mean score
    items: list = field(default_factory=list)   # FeedbackItem, worst first

    def to_json(self):
        return json.dumps({"target": self.target_label,
                           "overall_match": round(self.overall_match, 3),
                           "items": [asdict(i) for i in self.items]}, indent=1)


def pose_xyz(seq, lm):
    return seq[:, lm * 4: lm * 4 + 3]


def hand_block(seq, base):
    return seq[:, base: base + 63].reshape(len(seq), 21, 3)


def hand_present(seq, base):
    return np.abs(seq[:, base: base + 63]).sum(axis=1) > 0


def dtw_path(a, b):
    """Plain O(n*m) DTW on frame-feature matrices a (n,d), b (m,d)."""
    n, m = len(a), len(b)
    cost = np.linalg.norm(a[:, None, :] - b[None, :, :], axis=2)
    acc = np.full((n + 1, m + 1), np.inf)
    acc[0, 0] = 0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            acc[i, j] = cost[i - 1, j - 1] + min(acc[i - 1, j], acc[i, j - 1],
                                                 acc[i - 1, j - 1])
    path, (i, j) = [], (n, m)
    while i > 0 and j > 0:
        path.append((i - 1, j - 1))
        k = int(np.argmin([acc[i - 1, j - 1], acc[i - 1, j], acc[i, j - 1]]))
        i, j = (i - 1, j - 1) if k == 0 else (i - 1, j) if k == 1 else (i, j - 1)
    return path[::-1]


def wrist_traj(seq):
    return np.concatenate([pose_xyz(seq, L_WRIST_P), pose_xyz(seq, R_WRIST_P)], axis=1)


def timing_score(path):
    """Sustained tempo deviation from the warping path.

    Tempo is measured only where the GOLD sequence advances — a fast sign
    followed by a static hold otherwise averages back to slope 1 (both
    sequences are fixed 30 frames). ratio < 1 means the learner covered the
    gold's signing phase in fewer frames: too fast.
    Score = |log2(ratio)| clipped to [0,1]; 0.30 ≈ ~25% tempo deviation.
    """
    steps = np.diff(np.array(path), axis=0)
    active = steps[:, 1] > 0
    li, gi = steps[active, 0].sum(), steps[active, 1].sum()
    if li == 0 or gi == 0:
        return 1.0, "faster"
    ratio = li / gi
    return min(abs(float(np.log2(ratio))), 1.0), ("slower" if ratio > 1 else "faster")


def motion_score(learner, gold, path):
    lw, gw = wrist_traj(learner), wrist_traj(gold)
    diffs = np.array([lw[i] - gw[j] for i, j in path])       # (P, 6)
    err = float(np.linalg.norm(diffs, axis=1).mean())
    mean_diff = diffs.mean(axis=0)                            # per-axis bias
    hand = "right" if np.linalg.norm(mean_diff[3:]) >= np.linalg.norm(mean_diff[:3]) else "left"
    d = mean_diff[3:] if hand == "right" else mean_diff[:3]
    dirs = []
    if abs(d[0]) > 0.05: dirs.append("left" if d[0] > 0 else "right")   # learner x too large -> move left (mirrored to signer)
    if abs(d[1]) > 0.05: dirs.append("higher" if d[1] > 0 else "lower")  # image y grows downward
    direction = " and ".join(dirs) if dirs else "closer to the model path"
    return min(err / 0.8, 1.0), hand, direction


def handshape_score(learner, gold, path, base):
    lp, gp = hand_present(learner, base), hand_present(gold, base)
    pairs = [(i, j) for i, j in path if lp[i] and gp[j]]
    if not pairs:
        # gold uses this hand but learner never shows it
        if gp.any() and not lp.any():
            return 1.0, ["hand not detected"]
        return 0.0, []
    lh, gh = hand_block(learner, base), hand_block(gold, base)
    finger_err = {}
    for name, ids in FINGERS.items():
        e = [np.linalg.norm((lh[i, ids] - lh[i, WRIST_H]) - (gh[j, ids] - gh[j, WRIST_H]),
                            axis=1).mean() for i, j in pairs]
        finger_err[name] = float(np.mean(e))
    worst = sorted(finger_err, key=finger_err.get, reverse=True)
    # score on the worst finger, not the mean — a single-finger error
    # (e.g. FOUR vs FIVE differ only in the thumb) must not be diluted
    score = min(finger_err[worst[0]] / 0.30, 1.0)
    fingers = [f for f in worst if finger_err[f] > 0.6 * finger_err[worst[0]]][:2]
    return score, fingers


def orientation_score(learner, gold, path, base):
    lp, gp = hand_present(learner, base), hand_present(gold, base)
    pairs = [(i, j) for i, j in path if lp[i] and gp[j]]
    if not pairs:
        return 0.0
    lh, gh = hand_block(learner, base), hand_block(gold, base)

    def normal(h, t):
        v1 = h[t, INDEX_MCP] - h[t, WRIST_H]
        v2 = h[t, PINKY_MCP] - h[t, WRIST_H]
        n = np.cross(v1, v2)
        return n / (np.linalg.norm(n) + 1e-8)

    angles = [np.degrees(np.arccos(np.clip(np.dot(normal(lh, i), normal(gh, j)), -1, 1)))
              for i, j in pairs]
    return min(float(np.mean(angles)) / 90.0, 1.0)


def compare(learner, gold, target_label):
    """learner, gold: (T, 258) normalized no_face sequences -> FeedbackReport."""
    path = dtw_path(wrist_traj(learner), wrist_traj(gold))
    items = []

    t_score, tempo = timing_score(path)
    if t_score > THRESHOLDS["timing"]:
        items.append(FeedbackItem("timing", round(t_score, 3), "both",
                     f"Your sign is {tempo} than the model — "
                     f"{'take your time' if tempo == 'faster' else 'keep the movement flowing'}."))

    m_score, m_hand, m_dir = motion_score(learner, gold, path)
    if m_score > THRESHOLDS["motion"]:
        items.append(FeedbackItem("motion", round(m_score, 3), m_hand,
                     f"Move your {m_hand} hand {m_dir}."))

    for hand, base in (("left", LHAND0), ("right", RHAND0)):
        h_score, worst = handshape_score(learner, gold, path, base)
        if h_score > THRESHOLDS["handshape"]:
            if worst == ["hand not detected"]:
                items.append(FeedbackItem("handshape", 1.0, hand,
                             f"This sign uses your {hand} hand — keep it visible to the camera."))
            else:
                items.append(FeedbackItem("handshape", round(h_score, 3), hand,
                             f"Check your {hand}-hand shape — adjust your "
                             f"{' and '.join(worst)} finger{'s' if len(worst) > 1 else ''}."))
        o_score = orientation_score(learner, gold, path, base)
        if o_score > THRESHOLDS["orientation"]:
            items.append(FeedbackItem("orientation", round(o_score, 3), hand,
                         f"Rotate your {hand} palm to match the model orientation."))

    items.sort(key=lambda it: it.severity, reverse=True)
    all_scores = [it.severity for it in items] or [0.0]
    return FeedbackReport(target_label, round(1.0 - float(np.mean(all_scores)), 3), items)
