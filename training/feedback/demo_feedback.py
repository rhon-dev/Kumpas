#!/usr/bin/env python3
"""KUMPAS Phase 6 gate demo — feedback engine on 5 wrong attempts.

Five "wrong" attempts, built from real test clips + one synthetic error:
  1. attempts THANK YOU  but signs YOURE WELCOME   (confused pair, test clip)
  2. attempts FOUR       but signs FIVE            (handshape pair)
  3. attempts TOMORROW   but signs YESTERDAY       (mirror motion pair)
  4. attempts GOOD EVENING but signs GOOD AFTERNOON
  5. attempts HELLO      at 2x speed               (synthetic timing error)

Plus one control: a correct attempt (another HELLO test clip vs HELLO gold)
to show the engine stays quiet on a good sign.

Output: demo_report.md (committed) — gate artifact for prompt review.

Usage:
    ~/.kumpas-venvs/tf/bin/python demo_feedback.py
"""

import json
from pathlib import Path

import numpy as np

from feedback_engine import compare

REPO_ROOT = Path(__file__).resolve().parents[2]
SEQ_DIR = REPO_ROOT.parent / "kumpas-data" / "sequences"
GOLD_NPZ = REPO_ROOT.parent / "kumpas-data" / "feedback" / "gold_standards.npz"
OUT = Path(__file__).resolve().parent / "demo_report.md"

POSE, FACE = 132, 1404
KEEP = np.r_[0:POSE, POSE + FACE:1662]


def label_ids():
    lm = {int(k): v["label"] for k, v in
          json.loads((SEQ_DIR / "label_map.json").read_text()).items()}
    return lm, {v: k for k, v in lm.items()}


def speed_up(seq, factor=2):
    """Synthetic timing error: play the sign at `factor` speed, then hold."""
    fast = seq[::factor]
    pad = np.repeat(fast[-1:], len(seq) - len(fast), axis=0)
    return np.concatenate([fast, pad])


def main():
    labels, by_name = label_ids()
    gold = np.load(GOLD_NPZ)["gold"]
    X = np.load(SEQ_DIR / "X_test.npy")[:, :, KEEP]
    y = np.load(SEQ_DIR / "y_test.npy")

    def test_clip(name, nth=0):
        return X[np.where(y == by_name[name])[0][nth]]

    cases = [
        ("THANK YOU", test_clip("YOURE WELCOME"), "signed YOURE WELCOME instead"),
        ("FOUR", test_clip("FIVE"), "signed FIVE instead"),
        ("TOMORROW", test_clip("YESTERDAY"), "signed YESTERDAY instead"),
        ("GOOD EVENING", test_clip("GOOD AFTERNOON"), "signed GOOD AFTERNOON instead"),
        ("HELLO", speed_up(test_clip("HELLO")), "signed HELLO at 2x speed"),
        ("HELLO", test_clip("HELLO", nth=1), "CONTROL: correct HELLO attempt"),
    ]

    lines = ["# Phase 6 Gate Demo — Feedback Engine on Wrong Attempts", "",
             "Gold standards: provisional medoids (`gold_standards_manifest.json`).",
             "Thresholds provisional pending expert calibration.", ""]
    for target, attempt, desc in cases:
        rep = compare(attempt, gold[by_name[target]], target)
        lines += [f"## Target: **{target}** — learner {desc}", "",
                  f"Overall match: {rep.overall_match:.0%}", ""]
        if rep.items:
            for it in rep.items:
                lines.append(f"- `{it.dimension}` (severity {it.severity:.2f}, "
                             f"hand: {it.hand}) — **{it.prompt}**")
        else:
            lines.append("- No corrections — attempt matches the gold standard.")
        lines.append("")
        print(f"{target:14s} | {desc:38s} | items={len(rep.items)} "
              f"match={rep.overall_match:.2f}")

    OUT.write_text("\n".join(lines))
    print(f"-> {OUT.name}")


if __name__ == "__main__":
    main()
