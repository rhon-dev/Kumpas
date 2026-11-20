"""Per-sign and overall metrics, Wilson intervals and exact McNemar (RETRAINING_PLAN.md section 5)."""
import math
from collections import Counter

import numpy as np

Z95 = 1.959963984540054


def wilson(k, n, z=Z95):
    """95% Wilson score interval for k successes in n trials."""
    if n <= 0 or not 0 <= k <= n:
        raise ValueError(f'impossible count {k}/{n}')
    p, den = k / n, 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (0.0 if k == 0 else centre - half, 1.0 if k == n else centre + half)


def mcnemar(b, c):
    """Exact two-sided McNemar p-value; b and c are the two discordant counts."""
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def per_sign(y, p, labels):
    """One row per sign. Prediction is the first maximum, as in evaluate.metrics; 0.0 for zero denominators."""
    y, p = np.asarray(y), np.asarray(p)
    pred = p.argmax(axis=1)
    top3 = np.argsort(-p, axis=1, kind='stable')[:, :3]
    rows = []
    for k, label in enumerate(labels):
        mine = y == k
        n, tp, predicted = int(mine.sum()), int((mine & (pred == k)).sum()), int((pred == k).sum())
        precision = tp / predicted if predicted else 0.0
        recall = tp / n if n else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        wrong = Counter(int(v) for v in pred[mine & (pred != k)]).most_common(1)
        low, high = wilson(tp, n) if n else (None, None)
        rows.append(dict(dense_id=k, label=label, clips=n, correct=tp, recall=recall, wilson_low=low,
                         wilson_high=high, precision=precision, f1=f1,
                         top3_correct=int((top3[mine] == k).any(axis=1).sum()),
                         most_common_wrong=labels[wrong[0][0]] if wrong else '',
                         most_common_wrong_count=wrong[0][1] if wrong else 0))
    return rows


def summary(y, p, labels):
    rows = per_sign(y, p, labels)
    y = np.asarray(y)
    scored = [r for r in rows if r['clips']]
    return dict(clips=len(y), correct=sum(r['correct'] for r in rows),
                accuracy=sum(r['correct'] for r in rows) / len(y),
                macro_f1=sum(r['f1'] for r in rows) / len(rows),
                balanced_accuracy=sum(r['recall'] for r in scored) / len(scored),
                top3_accuracy=sum(r['top3_correct'] for r in rows) / len(y),
                signs_below_90_recall=[r['label'] for r in scored if r['recall'] < .9])
