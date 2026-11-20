# Automatic MacBook confidence diagnostic

Host-only all50 **uncalibrated model probabilities**, not accuracy, calibrated
rejection, mobile integration, distribution-equivalence evidence or completed
Holistic Phase 5. UNKNOWN/rejection is unavailable. Confident predictions can be
wrong, including for idle/out-of-vocabulary movements.

## Automatic capture (owner decision, November 19, 2026)

The viewer follows the owner-supplied reference video (SHA-256
`6b0c26b8d7fa73866cf0d6238673fe431fc309552c8fdfcac30c422e8a59ea23`): a hand
entering the camera view starts an attempt, and both hands leaving the view ends
and scores it. No click is needed. Visible states: `WAITING_FOR_HAND`,
`CAPTURING`, `RESULT`.

- Hands must be out of view before every attempt, including the first one. Out of
  view means five consecutive valid observations (usable pose and face) with no
  detected hand, about 0.33 s; a one-observation detector dropout does not count. The
  next admitted observation with a detected hand starts `CAPTURING` and clears the
  previous result.
- Every admitted 15 Hz observation of the attempt is buffered. Five consecutive
  hand-free observations (`HAND_OUT_OBSERVATIONS=5`, about 0.33 s) end it; shorter
  dropouts stay inside the attempt. SPACE is an optional manual end and is never
  required.
- Each attempt gets at most one inference. `verify_recognition.prepare_tensor(frames)`
  calls the unchanged `face_features.prepare_capture`, which trims the buffer to its
  first-to-last hand interval and resamples it to Float32 `(30,1588)`. This is the
  same preparation each training clip receives. Ineligible attempts (for example
  fewer than eight observations, under 400 ms or a hand interval over 5 s) are not
  scored, and the screen shows `Not scored: <reason>`.
- Lost pose or face, malformed or nonfinite observations, nonincreasing timestamps,
  observation gaps over 250 ms and hands kept in view for more than 5 s cancel the
  active attempt without inference. After a cancellation, a SPACE end or an R reset,
  hands must leave the view before the next attempt. The same applies after a tracking
  fault while idle, because hands can move unseen during it. After an automatic
  hand-out end, the next attempt can start at once, for the same sign or another one.
- `RESULT` stays visible until the next attempt starts or R resets it. Idle tracking
  loss and stream stalls do not clear it. The reference video returns to the prompt
  after about 2 s; that timeout is not implemented.

`RaisedCapture` (detected wrist above the shoulder midpoint, exactly 30
observations) and `ManualCapture` are kept for history with unchanged behavior; the
viewer no longer uses them. `RaisedCapture` and `PresenceCapture` share the inference
step `RaisedCapture._submit`.

## Run — only after parent checks and renewed camera readiness

Use the existing combined runtime; no installs or asset changes. Five frozen
asset digests are checked before runtime/camera acquisition. Alternate paths must
contain identical frozen bytes. Native capture remains `camera.OwnedCapture` with
strict built-in AVFoundation binding, never OpenCV/default/Continuity capture.

```sh
export TMPDIR="$HOME/.hermes/cache/scratch"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export TF_NUM_INTEROP_THREADS=1 TF_NUM_INTRAOP_THREADS=1
"$HOME/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python" -E -B \
  -m training.holistic_migration.recognition_webcam \
  --diagnostic-uncalibrated --duration 600
```

Optional `--binding /absolute/external/native-build/binding.json` reuses a verified
native receipt. `--audit-dir /absolute/external/new-run` must name a new external
directory; existing targets are refused. Default is a fresh UUID beneath
`../holistic-migration-data/recognition-audits/`. Auditing cannot be silently skipped.
No images, input tensors or landmarks are retained. Raw classifier outputs/order/
display retention is approved locally for this diagnostic, not participant work.

The 1280×720 preview uses the reference layout and is shown before any classifier
invocation. It displays the full camera frame with face contours and pose and hand
lines (one hand colour, because SDK left/right anatomy is unverified), a top line
`FPS <rate>  mirror ON  q quit  m mirror  r reset  space end`, a small
`UNCALIBRATED - no UNKNOWN` label, and one bottom-left state: white
`Raise your hands to sign` (`Lower your hands; keep face and shoulders in view`
until the hands-out period is complete),
red `REC <seconds> s`, or **exactly three prediction rows** with the first row in
green. FPS is the processed 15 Hz observation rate since the first processed
observation, not the camera rate. Rows sort
by descending original probability, ties by ascending dense index. Scores use
`f'{score:.2f}'` in 0.00–1.00 units, never percentages or top3 renormalization.
Raw scores remain unrounded. Canonical labels are unchanged; curly apostrophes
are transliterated only in display text. The target-sign selector and debug text
are removed. Renderer and audit consume the same presentation rows, for example
`1. GOOD MORNING: 0.97`.

Controls: SPACE optional end; R reset; M display-only mirror; Q/Escape/window close
quit. Detector input stays unmirrored. Session duration
is finite, at most 900 seconds; synchronous SDK/model/GUI calls cannot be forcibly
preempted. Source failures override normal termination; all acquired resources
receive cleanup attempts while preserving the primary error.

Optional `--status /absolute/external/new-status.json` keeps fixed operational
counts (processed observations, started `attempts`, scored `submissions`), state
and asset digests only, no predictions/history. Its parent must exist and
the file must be new. Readers should retry transient parse errors during in-place
updates. Timings/FPS are operational, not physical performance benchmarks.

## Durable output audit and independent comparator

- `run.json`: schema, asset digests, implementation/shared-source identities,
  ordered-label file digest.
- `labels.json`: all50 canonical labels in dense order.
- `attempt-NNNNNN.json`: schema, attempt number, raw50 vector and exactly three
  rank/index/label/full-score/display-text records.
- `completion.json`: complete attempt inventory and exact-byte digests.

Writes are exclusive, flushed/fsynced and read back. A failed save leaves an
`INCOMPLETE` barrier; persistence failure clears the result and terminates
fail-closed. Earlier runs/attempt files are preserved. A zero-attempt run fails
verification rather than implying a prediction happened.

```sh
"$HOME/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python" -E -B \
  -m training.holistic_migration.verify_recognition --check /absolute/external/run
```

The executable prints PASS/FAIL and returns nonzero on failure. It independently
sorts raw50, never calls the presentation ranker, and checks probability shape,
finiteness/range/sum, exact3, tie order, index, label, original score and rounded
display string. It checks label order digest, source identities, complete attempt
inventory and exact-byte hashes. Current source changes intentionally invalidate
an archive checked against this checkout. This proves local consistency, not
independent model-execution attestation, malicious-writer resistance, concurrent
writer safety, or crash/power-loss atomicity. Parent separately binds canonical
labels/frozen assets/actual model output. Synthetic archives are not real inference.

Parent API: `AuditRun(new_external_path, labels, identities)`, then
`save(raw_vector_50, presentation_rows(raw_vector_50, labels))`, and `check_run(path)`.
Identities must contain classifier/features/labels SHA-256 digests (live caller
supplies all five frozen identities). The parent's frozen real-fit sample has zero
raised-hand observations, so it never triggers `RaisedCapture`. Replayed through
`PresenceCapture` with the frozen classifier, the same recorded clip produced one
attempt whose input equals its training `X_fit` row bitwise
(`evidence/presence-capture-20261119/replay_fit_clip.py`). This is recorded-clip
parity, not live webcam accuracy.

## Hardware-free verification

```sh
"$HOME/.kumpas-venvs/rv2-holistic-tf-20261101/bin/python" -E -B \
  -m pytest -p no:cacheprovider \
  training/holistic_migration/tests/test_recognition.py \
  training/holistic_migration/tests/test_recognition_webcam.py \
  training/holistic_migration/tests/test_verify_recognition.py -v
```

External evidence: `holistic-migration-data/evidence/presence-capture-20261119/`
(current hand-presence viewer) and
`holistic-migration-data/evidence/raised-top3-20261118/implementation/` (history).
Vertical RED/GREEN precedes capture, resets/rearming, top3, audit, parity seam,
viewer integration, missing-attempt protection and lowering-boundary changes.
Additional adversarial controls are labelled coverage-only GREEN. Worker execution
is synthetic only: no camera, real model, GUI or device query. Parent independent
review/source protection and real-fit readback/parity remain required before a
new camera session. Human all50 correctness, anatomy, physical performance,
rejection/calibration, research outcomes and full Phase 5 remain unverified.
