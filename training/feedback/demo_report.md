# Phase 6 Gate Demo — Feedback Engine on Wrong Attempts

Gold standards: provisional medoids (`gold_standards_manifest.json`).
Thresholds provisional pending expert calibration.

## Target: **THANK YOU** — learner signed YOURE WELCOME instead

Overall match: 31%

- `timing` (severity 1.00, hand: both) — **Your sign is faster than the model — take your time.**
- `orientation` (severity 1.00, hand: right) — **Rotate your right palm to match the model orientation.**
- `handshape` (severity 0.72, hand: right) — **Check your right-hand shape — adjust your pinky and ring fingers.**
- `motion` (severity 0.69, hand: left) — **Move your left hand right and lower.**
- `handshape` (severity 0.43, hand: left) — **Check your left-hand shape — adjust your middle and ring fingers.**
- `orientation` (severity 0.27, hand: left) — **Rotate your left palm to match the model orientation.**

## Target: **FOUR** — learner signed FIVE instead

Overall match: 74%

- `handshape` (severity 0.26, hand: right) — **Check your right-hand shape — adjust your thumb and index fingers.**

## Target: **TOMORROW** — learner signed YESTERDAY instead

Overall match: 59%

- `orientation` (severity 0.57, hand: right) — **Rotate your right palm to match the model orientation.**
- `handshape` (severity 0.24, hand: right) — **Check your right-hand shape — adjust your thumb and pinky fingers.**

## Target: **GOOD EVENING** — learner signed GOOD AFTERNOON instead

Overall match: 51%

- `orientation` (severity 0.66, hand: right) — **Rotate your right palm to match the model orientation.**
- `handshape` (severity 0.32, hand: right) — **Check your right-hand shape — adjust your pinky and ring fingers.**

## Target: **HELLO** — learner signed HELLO at 2x speed

Overall match: 67%

- `timing` (severity 0.47, hand: both) — **Your sign is faster than the model — take your time.**
- `motion` (severity 0.28, hand: right) — **Move your right hand right.**
- `handshape` (severity 0.24, hand: right) — **Check your right-hand shape — adjust your thumb and middle fingers.**

## Target: **HELLO** — learner CONTROL: correct HELLO attempt

Overall match: 100%

- No corrections — attempt matches the gold standard.

---

## Prompt copy review (2026-07-13) — expert linguistic validation PENDING

Full template inventory (feedback_engine.py, mirrored in Kotlin port — any copy
change must land in both + rerun parity test):

1. timing: "Your sign is {faster|slower} than the model — {take your time|keep the movement flowing}."
2. motion: "Move your {left|right} hand {left|right|higher|lower|closer to the model path}."
3. handshape: "Check your {left|right}-hand shape — adjust your {fingers}."
4. hand missing: "This sign uses your {hand} hand — keep it visible to the camera."
5. orientation: "Rotate your {hand} palm to match the model orientation."

Items for the FSL expert / adviser to validate:

- **"the model" wording** — learners may read this as the ML model. Candidate:
  "the example". Affects templates 1, 2 (fallback), 5.
- **Orientation prompt is not actionable** — no direction given ("rotate which
  way?"). Engine currently computes only an angle magnitude, not an axis.
  Is a generic rotate prompt acceptable pedagogically, or does this need
  per-axis direction (engine change)?
- **Motion grammar** — "right and lower" mixes an adverb with a comparative.
  Candidate: "to the right and down" (also swap higher/lower → up/down).
- **Mirror convention** — code maps learner x-offset to signer-frame
  left/right (front camera preview is mirrored). Expert should confirm on
  device that "move left" matches the learner's intuition.
- **Severity gradation** — identical text at severity 1.00 and 0.27. Graded
  copy ("slightly rotate…") optional.
- **Prompt volume** — worst case shows 6 prompts (THANK YOU demo). Consider
  top-3 cap or "focus on this first" emphasis in UI.
- **Calibration flag** — TOMORROW vs YESTERDAY (opposite motion) triggered no
  motion prompt; motion threshold may be too loose for direction-critical
  sign pairs.
- Untested-in-demo variants: timing "slower", hand-not-visible. Add demo cases
  before the expert session.
