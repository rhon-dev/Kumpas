# Implementation Plan — Phase 22 Holistic v2

## Overview

Recover the manual channel the pipeline discards, expose handshape in the representation, and close
the train/serve gap where the app runs a different landmark graph than training. Ordered so the
cheap offline wins (T1–T9) are proven before any device latency is spent (T15+), and so the
project can stop at any gate with a shippable app.

**Nothing in this file may start until the PM/Adviser gate on `requirements.md` is approved
(`AGENTS.md` Rule #0), and until hardening-plan Stage A and Gate B are green.**

Every task below follows the `AGENTS.md` task template: AGENT / PHASE / OBJECTIVE / INPUT /
CONSTRAINTS / ACCEPTANCE CRITERIA / OUTPUT LOCATION.

---

## Wave 0 — Unblock (prerequisites owned elsewhere)

- [ ] **T0. Confirm hardening-plan prerequisites are green**
  - **AGENT:** ⚙️ Documentation
  - **PHASE:** 22 / gate entry
  - **OBJECTIVE:** Verify Stage A (truth-in-docs), Gate B (reproducible build), C3 (normalize extracted to a testable class), and G2 (test-set strategy decided) are complete, since WS1–WS6 depend on them.
  - **INPUT:** `docs/hardening-plan.md`, `docs/phase-gates.md`, `.github/workflows/ci.yml`, `training/requirements*.txt`
  - **CONSTRAINTS:** Do not implement the prerequisites here; this is a checkpoint only. Do not edit `docs/hardening-plan.md`.
  - **ACCEPTANCE CRITERIA:** A written checklist in the spec folder marking each prerequisite green or blocked, with the blocking owner named. If G2 is unresolved, T10–T14 are blocked and this must say so.
  - **OUTPUT LOCATION:** `.kiro/specs/22-holistic-v2/prerequisites.md`

---

## Wave 1 — WS1: Sequence construction (offline, no latency cost)

- [ ] **T1. Signing-span detector design + validation on the existing landmark set**
  - **AGENT:** 🔵 Data/Preprocessing
  - **PHASE:** 22 / WS1
  - **OBJECTIVE:** Detect each clip's signing span from two independent signals — hand presence, and pose-wrist motion energy — and validate the detector against the measured baseline before it is wired into the pipeline.
  - **INPUT:** `../kumpas-data/landmarks/*.npz` (1016 clips), `training/preprocessing/extraction_log.csv`
  - **CONSTRAINTS:** Do not modify `extract_landmarks.py` yet. Do not commit landmark arrays. Pose-based estimation must not depend on hand detection, or the detector becomes circular.
  - **ACCEPTANCE CRITERIA:** Reported per-clip span for all 1016 clips; agreement rate between the two signals; the detector reproduces the known distribution (leading rest ≈0.396, span ≈0.356, trailing rest ≈0.248) within a stated tolerance; clips where the signals disagree materially are listed for quarantine.
  - **OUTPUT LOCATION:** `training/preprocessing/span_detection_report.md` + `span_log.csv`

- [ ] **T2. Rebuild sequences sampling within the span**
  - **AGENT:** 🔵 Data/Preprocessing
  - **PHASE:** 22 / WS1
  - **OBJECTIVE:** Sample `seq_len` frames within the detected span instead of uniformly across the clip, and quantify the occupancy gain.
  - **INPUT:** T1 output, `training/preprocessing/build_sequences.py`
  - **CONSTRAINTS:** Hold `seq_len` at 30 and hold pose normalization unchanged — changing more than one variable makes the WS3 ablation uninterpretable. Preserve the FSL-105 CSV split; never reshuffle. Short spans pad by repeating the last frame, as today.
  - **ACCEPTANCE CRITERIA:** Mean hand-present timesteps reported for train and test against the measured baseline of 10.3/30 overall and 7.0/8.8/7.8/7.8/9.0 for ONE/TWO/THREE/FOUR/FIVE, using the same counting method as `docs/holistic-v2-diagnosis.md` §3. Quarantined clips excluded and listed.
  - **OUTPUT LOCATION:** `training/preprocessing/preprocessing_report_v2.md`; arrays outside the repo

- [ ] **T3. Extraction-lever ablation (targeted, not pipeline-wide)**
  - **AGENT:** 🔵 Data/Preprocessing
  - **PHASE:** 22 / WS1
  - **OBJECTIVE:** Measure which extraction levers actually improve in-span detection for the six classes below 0.85, and confirm that pipeline-wide re-extraction is unnecessary.
  - **INPUT:** BLUE (0.570), WHITE (0.627), MOTHER (0.707), RED (0.808), WOMAN (0.840), BLACK (0.840) clips; `training/preprocessing/extract_landmarks.py:54-57`
  - **CONSTRAINTS:** Levers to test: `min_detection_confidence`, `min_tracking_confidence`, `model_complexity`, `refine_face_landmarks`, input resolution handling, short-dropout interpolation. Do not re-extract all 1016 clips to chase a rate that already measures 0.954. Do not overwrite `extraction_log.csv`.
  - **ACCEPTANCE CRITERIA:** An ablation table of lever → in-span detection delta for the six classes; an explicit recommendation on whether full re-extraction is justified; note that `model_complexity` has no Tasks-runtime counterpart and so is a skew source if changed.
  - **OUTPUT LOCATION:** `training/preprocessing/extraction_ablation.md`

- [ ] **T4. Full-landmark-set re-extraction decision**
  - **AGENT:** 🔵 Data/Preprocessing
  - **PHASE:** 22 / WS1
  - **OBJECTIVE:** Decide and record whether to re-extract at the full 543/553 landmark set, driven by the WS2 face decision and the 468-vs-478 mesh question — not by hand recovery.
  - **INPUT:** T3 output, `.kiro/specs/22-holistic-v2/design.md` §4.4
  - **CONSTRAINTS:** Justification must be train/serve parity and keeping the face option open. Re-extraction justified as "fixing hands" must be refused — in-span detection is 0.954.
  - **ACCEPTANCE CRITERIA:** A dated decision record naming the chosen mesh variant, the Python API (legacy vs Tasks), and the cost estimate in compute time.
  - **OUTPUT LOCATION:** `docs/decisions/` (dated file)

---

## Wave 2 — WS2: Feature spec

- [ ] **T5. Author `feature_spec_v2.json`**
  - **AGENT:** 🔵 Data/Preprocessing + 🟢 Mobile/Flutter (joint)
  - **PHASE:** 22 / WS2
  - **OBJECTIVE:** Declare the single authoritative feature layout: block structure, index ranges, per-block normalization, derived-feature definitions, presence flags, `seq_len`, and a version identifier.
  - **INPUT:** `design.md` §4.2, `build_sequences.py:54-62`, `VisionEngine.kt:242-270`
  - **CONSTRAINTS:** Must be consumable by both languages. Must not embed language-specific assumptions. Must state explicitly whether pose `visibility` is included, contingent on T16's finding. Must not reintroduce a 1404-dim raw face block.
  - **ACCEPTANCE CRITERIA:** Every block has a declared index range, normalization rule, and presence flag. Both a Python reader and a Kotlin reader can reconstruct an identical layout from it. No layout constant remains hardcoded in either language.
  - **OUTPUT LOCATION:** `training/feature_spec_v2.json` + `training/feature_spec_v2.md` (rationale)

- [ ] **T6. Verify the canonicalization hypothesis before building on it**
  - **AGENT:** 🟣 Model/Training
  - **PHASE:** 22 / WS2
  - **OBJECTIVE:** Re-confirm on the rebuilt (T2) sequences that wrist-relative canonicalization separates the numeral pairs, before WS3 commits to an architecture.
  - **INPUT:** T2 sequences, `docs/holistic-v2-diagnosis.md` §3
  - **CONSTRAINTS:** Analysis only, no training. This is a falsification check: if separation does not hold on the rebuilt data, WS2's premise is wrong and the plan must stop and re-diagnose.
  - **ACCEPTANCE CRITERIA:** Between-class/within-class handshape separation reported for FIVE-vs-FOUR and THREE-vs-TWO on the rebuilt sequences, against the measured baselines of 3.78 and 9.97; handshape-to-pose amplitude ratio reported against the baseline 7.5×. A clear pass/fail on whether canonicalization is justified.
  - **OUTPUT LOCATION:** `training/preprocessing/canonicalization_check.md`

- [ ] **T7. Implement the Python feature builder from the spec**
  - **AGENT:** 🔵 Data/Preprocessing
  - **PHASE:** 22 / WS2
  - **OBJECTIVE:** Build feature vectors by reading `feature_spec_v2.json`, replacing the hardcoded layout in `build_sequences.py`.
  - **INPUT:** T5, T6
  - **CONSTRAINTS:** Do not delete the 258-dim path — it is the rollback target and the ablation's rung 1. Keep both selectable by spec version.
  - **ACCEPTANCE CRITERIA:** Feature vectors are produced for every spec version including the legacy 258 layout; block offsets come only from the spec file; presence flags are populated and distinguish absent from origin-located blocks.
  - **OUTPUT LOCATION:** `training/preprocessing/` (new module)

- [ ] **T8. Export golden-vector fixtures**
  - **AGENT:** 🔵 Data/Preprocessing
  - **PHASE:** 22 / WS2
  - **OBJECTIVE:** Produce committed fixtures pairing fixed raw landmark input with the Python-computed feature vector, for the Kotlin parity test.
  - **INPUT:** T7, `training/feedback/export_for_app.py` (existing pattern)
  - **CONSTRAINTS:** Commit **raw landmarks, not video frames** — `AGENTS.md` privacy rule forbids raw video and this keeps the test headless. Include cases with each block absent, so presence-flag handling is covered. Minimum 5 fixtures per hardening task C2.
  - **ACCEPTANCE CRITERIA:** Fixtures cover: both hands present, left absent, right absent, both absent, pose-only. Each carries the feature-spec version and expected vector.
  - **OUTPUT LOCATION:** `app/android/app/src/test/resources/` + exporter in `training/`

- [ ] **T9. Feature-spec documentation and versioning rules**
  - **AGENT:** ⚙️ Documentation
  - **PHASE:** 22 / WS2
  - **OBJECTIVE:** Document the spec, its version-stamping rules, and the asset-compatibility contract.
  - **INPUT:** T5, T8
  - **CONSTRAINTS:** Addendum style; do not rewrite `docs/PRD.md`.
  - **ACCEPTANCE CRITERIA:** Rules state how a version bump propagates to model, gold standards, and label map, and what a loader must do on mismatch.
  - **OUTPUT LOCATION:** `training/feature_spec_v2.md`, `docs/PRD.md` addendum section

---

## Wave 3 — WS3: Ablation ladder and model v2

> **Blocked until hardening task G2 is resolved.** At support 4 per class, a numeral improvement of
> two clips cannot be distinguished from noise, and validation accuracy of 1.0 provides no
> model-selection signal.

- [ ] **T10. Pre-register the ablation protocol**
  - **AGENT:** 🟣 Model/Training
  - **PHASE:** 22 / WS3
  - **OBJECTIVE:** Write the ablation protocol *before* running it: six rungs, fixed splits, fixed seed, declared metrics, and the declared rejection criterion.
  - **INPUT:** `design.md` §5, `training/models/experiments_log.json`
  - **CONSTRAINTS:** One variable per rung. Identical splits across rungs. Must state the "do not ship Holistic v2" outcome up front (`requirements.md` acceptance criterion 6) so the result cannot be rationalized after the fact.
  - **ACCEPTANCE CRITERIA:** Protocol names all six rungs, the primary metric (per-pair accuracy on the seven observed pairs), secondary metrics (macro-F1, ECE/reliability, per-class support, CIs), and the rejection rule. Reviewed before any run starts.
  - **OUTPUT LOCATION:** `.kiro/specs/22-holistic-v2/ablation-protocol.md`

- [ ] **T11. Run rungs 0–3 (pose → hands raw → hands canonicalized → derived)**
  - **AGENT:** 🟣 Model/Training
  - **PHASE:** 22 / WS3
  - **OBJECTIVE:** Isolate the contribution of WS1's sampling fix and WS2's canonicalization separately.
  - **INPUT:** T2, T7, T10
  - **CONSTRAINTS:** Append to `experiments_log.json`; never edit existing entries. Record environment honestly — if runs are local rather than Colab, log that (see T21). Emit the full artifact set per run.
  - **ACCEPTANCE CRITERIA:** Four logged runs each with `_eval.md`, `_confusion.png`, `_per_class.csv`. The rung 0 → rung 1 delta quantifies what uniform sampling was discarding. Per-pair accuracy reported with CIs for all seven pairs.
  - **OUTPUT LOCATION:** `training/models/experiments_log.json`, `training/models/reports/`

- [ ] **T12. Run rungs 4–5 (face/NMM channel, full)**
  - **AGENT:** 🟣 Model/Training
  - **PHASE:** 22 / WS3
  - **OBJECTIVE:** Test whether the face channel carries signal, specifically for the pairs *not* explained by handshape.
  - **INPUT:** T11, T4 (face representation decision)
  - **CONSTRAINTS:** The face channel is a hypothesis under test, not a goal. If it does not help, record that and drop it — do not tune it into significance. Must not reintroduce the 1404-dim raw block.
  - **ACCEPTANCE CRITERIA:** Explicit finding on GOOD AFTERNOON/GOOD EVENING (in-span hand rates 0.450/0.471) and YES/NO, which requirement 21 separates from the numeral mechanism. A recommendation to keep or drop the channel, with the ablation row supporting it.
  - **OUTPUT LOCATION:** `training/models/experiments_log.json`, `training/models/reports/`

- [ ] **T13. Architecture candidate beyond CNN-LSTM**
  - **AGENT:** 🟣 Model/Training
  - **PHASE:** 22 / WS3
  - **OBJECTIVE:** Evaluate at least one alternative (two-stream body/hand late fusion, or a temporal-attention head) against the winning rung.
  - **INPUT:** T11, T12
  - **CONSTRAINTS:** Must fit 4 GB RAM and the WS6 budget. Current winner is 270,834 parameters. Justify parameter growth against measured latency, not assumed headroom.
  - **ACCEPTANCE CRITERIA:** At least one candidate logged with the same metric set; a parameter/latency/accuracy trade-off table; a recommendation.
  - **OUTPUT LOCATION:** `training/models/experiments_log.json`, `training/models/reports/`

- [ ] **T14. Backfill eval artifacts for the four original runs**
  - **AGENT:** 🟣 Model/Training
  - **PHASE:** 22 / WS3 (satisfies hardening G4)
  - **OBJECTIVE:** Generate the missing `_eval.md` / `_confusion.png` / `_per_class.csv` for the three 2026-07-05 runs that lack them, so old and new runs are comparable.
  - **INPUT:** `training/models/experiments_log.json`
  - **CONSTRAINTS:** **Do not modify** `training/models/reports/20260705_194813_no_face_eval.md` or any existing gate evidence. New files only.
  - **ACCEPTANCE CRITERIA:** All four original runs have the same artifact set as the new runs.
  - **OUTPUT LOCATION:** `training/models/reports/`

---

## Wave 4 — WS4: On-device Holistic parity

- [ ] **T15. Holistic runtime spike and capability confirmation**
  - **AGENT:** 🟢 Mobile/Flutter
  - **PHASE:** 22 / WS4
  - **OBJECTIVE:** Stand up `HolisticLandmarker` in VIDEO mode and confirm the capabilities the feature spec depends on.
  - **INPUT:** `app/android/app/build.gradle.kts:59` (`tasks-vision:0.10.14` — already contains `HolisticLandmarker`, verified), `holistic_landmarker.task` bundle
  - **CONSTRAINTS:** **No dependency bump** unless a measured reason emerges. Fetch the task bundle through hardening task B2's checksum-verified path. Do not delete the split-detector path yet.
  - **ACCEPTANCE CRITERIA:** Confirmed on device: landmark counts per block; whether `faceBlendshapes()` is populated when enabled; **whether pose `visibility` is populated** (currently `unverified` and the feature spec depends on it); VIDEO-mode stability.
  - **OUTPUT LOCATION:** `benchmarking/holistic_capability_report.md`

- [ ] **T16. Settle front-camera mirroring and handedness — once**
  - **AGENT:** 🟢 Mobile/Flutter
  - **PHASE:** 22 / WS4 (absorbs hardening C1)
  - **OBJECTIVE:** Determine whether the front-camera feed must be mirrored before Holistic, and assert the answer with a test rather than reasoning.
  - **INPUT:** `CameraPreviewView.kt`, T15, Python-side left/right assignment in `extract_landmarks.py`
  - **CONSTRAINTS:** Settle this under the **Holistic** runtime only. Do not fix it in the split-model `categoryName()` path first — that work is discarded, and the "one place, not two" requirement forbids it. Note that `leftHandLandmarks()`/`rightHandLandmarks()` remove the classifier ambiguity but **not** the mirroring question.
  - **ACCEPTANCE CRITERIA:** A test asserts that the anatomical left hand lands in the left block on both the Python and Kotlin paths for the same input. The finding is documented either way. Because `FeedbackEngine` emits per-hand instructions, a swap must be proven absent, not assumed.
  - **OUTPUT LOCATION:** Kotlin test + `docs/decisions/` record

- [ ] **T17. Kotlin feature builder from the spec**
  - **AGENT:** 🟢 Mobile/Flutter
  - **PHASE:** 22 / WS4
  - **OBJECTIVE:** Replace `VisionEngine`'s hardcoded 258-dim construction and `normalize()` with a builder driven by `feature_spec_v2.json`.
  - **INPUT:** T5, T15, T16, hardening C3's extracted class
  - **CONSTRAINTS:** Read the class count from `label_map.json` — remove the `Array(50)` literal at `VisionEngine.kt:65`. Keep the 258-dim path selectable for rollback. Must run headless for tests.
  - **ACCEPTANCE CRITERIA:** Feature construction is spec-driven; no layout literal remains; both spec versions selectable; no camera needed to exercise it.
  - **OUTPUT LOCATION:** `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/`

- [ ] **T18. Golden-vector parity test (gate-blocking)**
  - **AGENT:** 🟢 Mobile/Flutter
  - **PHASE:** 22 / WS4
  - **OBJECTIVE:** Prove the Kotlin feature vector matches Python within tolerance, mirroring `FeedbackEngineParityTest.kt`.
  - **INPUT:** T8 fixtures, T17
  - **CONSTRAINTS:** **Must fail by default** — a missing fixture fails rather than skips. Runs in CI (hardening B4). Tolerance stated explicitly; the existing feedback parity test uses 0.05.
  - **ACCEPTANCE CRITERIA:** All five fixture cases pass; presence flags assert **exact** equality, not tolerance; per-block max absolute deviation reported. Parity failure blocks the WS4 gate.
  - **OUTPUT LOCATION:** `app/android/app/src/test/kotlin/com/kumpas/kumpas_app/FeatureVectorParityTest.kt`

- [ ] **T19. Asset version enforcement and rollback switch**
  - **AGENT:** 🟢 Mobile/Flutter
  - **PHASE:** 22 / WS4 + WS7
  - **OBJECTIVE:** Make asset/model version mismatches fail loudly, and put Holistic v2 behind a runtime switch with the 258-dim path intact.
  - **INPUT:** T17, T19's version stamps from T9
  - **CONSTRAINTS:** `gold_standards.bin` is currently read as a bare `50 × 30 × 258` float blob with no header — a new feature space would silently misread it. The switch state must reach the session log so results are attributable to a pipeline.
  - **ACCEPTANCE CRITERIA:** Loading a mismatched asset fails with a clear error rather than misreading; both pipelines run; the active pipeline is recorded in logs and benchmark entries.
  - **OUTPUT LOCATION:** `app/android/app/src/main/kotlin/com/kumpas/kumpas_app/`

---

## Wave 5 — WS5: Feedback engine v2

- [ ] **T20. Fix `overall_match` and add minimum-support abstention**
  - **AGENT:** 🟡 Feedback Algorithm
  - **PHASE:** 22 / WS5
  - **OBJECTIVE:** Correct the two scoring defects found during verification, independent of any feature-space change.
  - **INPUT:** `training/feedback/feedback_engine.py:131-204`
  - **CONSTRAINTS:** These are **not** Holistic-dependent and can land early. Preserve the existing abstention behaviour at `:137`/`:190`, which is already correct — extend it from binary presence to sufficient support. Keep the Python reference and Kotlin port behaviourally identical.
  - **ACCEPTANCE CRITERIA:** `overall_match` no longer rises when a milder error is added, and no longer returns exactly 1.0 merely because no item crossed a threshold. Handshape/orientation abstain below a stated minimum aligned-pair count. `FeedbackEngineParityTest.kt` updated and passing.
  - **OUTPUT LOCATION:** `training/feedback/feedback_engine.py`, `FeedbackEngine.kt`, fixtures

- [ ] **T21. Re-derive handshape and orientation thresholds**
  - **AGENT:** 🟡 Feedback Algorithm
  - **PHASE:** 22 / WS5
  - **OBJECTIVE:** Recalibrate thresholds on the denser manual channel and document the real basis, replacing the docstring's "provisional pending expert calibration".
  - **INPUT:** T2, T7, current values (timing 0.30, motion 0.25, handshape 0.22, orientation 0.25)
  - **CONSTRAINTS:** Document in hardening task C5's format: value, meaning, derivation, sensitivity. Divisors (0.8, 0.30, 90.0) need the same treatment. Reconcile the docstring against `phase-gates.md`'s claim of completed expert validation.
  - **ACCEPTANCE CRITERIA:** Every constant has a recorded derivation and sensitivity analysis. No undocumented magic number remains in the engine.
  - **OUTPUT LOCATION:** `docs/feedback-thresholds.md` (extends C5)

- [ ] **T22. Re-export and re-validate gold standards**
  - **AGENT:** 🟡 Feedback Algorithm + ⚪ FSL Expert review
  - **PHASE:** 22 / WS5
  - **OBJECTIVE:** Re-export gold standards in the new feature space, version-stamped, and obtain fresh expert sign-off for the affected dimensions only.
  - **INPUT:** `training/feedback/build_gold_standards.py`, `gold_standards_manifest.json`, the 2026-07-23 sign-off
  - **CONSTRAINTS:** Scope the re-validation honestly: DTW aligns on **pose** wrists, so TIMING and MOTION remain valid and retain the existing sign-off. Only HANDSHAPE, ORIENTATION, and any new NMM dimension need fresh review. Do not request a full 50-sign redo of all four dimensions.
  - **ACCEPTANCE CRITERIA:** `gold_standards_v2.bin` carries a feature-spec version and model hash; expert sign-off obtained for the two affected dimensions; the scope justification is recorded so the narrower ask is defensible.
  - **OUTPUT LOCATION:** `training/feedback/`, `docs/phase10-expert-validation-protocol.md` addendum

- [ ] **T23. NMM dimension (conditional)**
  - **AGENT:** 🟡 Feedback Algorithm + ⚪ FSL Expert review
  - **PHASE:** 22 / WS5
  - **OBJECTIVE:** Add a fifth feedback dimension for non-manual markers.
  - **INPUT:** T12 result, T22
  - **CONSTRAINTS:** **Conditional — only if T12 shows the face/NMM channel carries signal.** If it does not, close this task as not-required and record why. New copy must be Filipino at first commit (hardening C4).
  - **ACCEPTANCE CRITERIA:** Either a fifth dimension with expert-approved Filipino copy and documented thresholds, or a recorded decision not to add it, citing T12.
  - **OUTPUT LOCATION:** `training/feedback/`, `FeedbackEngine.kt`, string resources

---

## Wave 6 — WS6: Real-device benchmarking

- [ ] **T24. Define the per-stage latency budget**
  - **AGENT:** 🔴 QA/Benchmarking
  - **PHASE:** 22 / WS6
  - **OBJECTIVE:** Allocate the 150 ms across camera, Holistic, feature construction, classifier, feedback, and render, and state which number the gate governs.
  - **INPUT:** `.kiro/steering/tech.md:42`, `benchmarking/phase4_emulator_report.md`
  - **CONSTRAINTS:** The budget includes landmark extraction per `tech.md:42`. The 0–2 ms interpreter figure must not be presented as the latency result. Per-frame cost and per-recognition latency are different numbers — the pipeline samples every 4th frame and infers every 4th sample — and the existing evidence conflates them.
  - **ACCEPTANCE CRITERIA:** A per-stage budget summing under 150 ms, with the measured two-model baseline of 35–63 ms as the reference point, and explicit definitions of both metrics.
  - **OUTPUT LOCATION:** `benchmarking/latency_budget_v2.md`

- [ ] **T25. End-to-end latency instrumentation**
  - **AGENT:** 🔴 QA/Benchmarking
  - **PHASE:** 22 / WS6 (with hardening D4)
  - **OBJECTIVE:** Instrument camera-frame-in to feedback-ready-out, covering MediaPipe and TFLite together.
  - **INPUT:** `benchmarking/collect_latency.py`, `LatencyBenchmarkTest.kt`, `BenchmarkMode.kt`
  - **CONSTRAINTS:** Reuse the existing harness so history stays comparable. Depends on hardening D1/D2 fixing `BenchmarkMode`'s storage path and frame counting.
  - **ACCEPTANCE CRITERIA:** Reports per-stage and end-to-end p50/p95 with MediaPipe included; results land in `benchmark_history.json` with real device metadata.
  - **OUTPUT LOCATION:** `benchmarking/`

- [ ] **T26. Benchmark baseline and Holistic v2 on real hardware**
  - **AGENT:** 🔴 QA/Benchmarking
  - **PHASE:** 22 / WS6
  - **OBJECTIVE:** Measure both pipelines on a real mid-range device across the three named conditions.
  - **INPUT:** T19 switch, T25, `benchmarking/environment_protocol.md`
  - **CONSTRAINTS:** Helio G / Snapdragon 6 class, 4 GB RAM. Emulator evidence cannot close this gate. **Both** pipelines must be measured on the same device — otherwise "Holistic is slower" cannot be separated from "real hardware is slower than an M1 emulator". Append only; do not edit `benchmark_history.json` history.
  - **ACCEPTANCE CRITERIA:** Entries for 2 pipelines × 3 conditions with `condition` never `"n/a"`, real device metadata, `n_inferences` and `cold_start_ms` populated, FPS runs meeting `collect_fps.py`'s own ≥60 s requirement.
  - **OUTPUT LOCATION:** `benchmarking/benchmark_history.json`, `benchmarking/holistic_v2_device_report.md`

- [ ] **T27. Degradation levers, measured and ranked**
  - **AGENT:** 🔴 QA/Benchmarking + 🟠 Model Optimization
  - **PHASE:** 22 / WS6
  - **OBJECTIVE:** Measure the accuracy cost of each degradation lever and fix the order in which they are applied.
  - **INPUT:** T26, T12
  - **CONSTRAINTS:** Hard rule: the face channel is sacrificed before the hand channel in every case — hands carry the confusion-pair signal. Accuracy costs must be measured, not asserted.
  - **ACCEPTANCE CRITERIA:** A table of lever → latency saved → accuracy cost, and a decision rule naming what is dropped first if the budget is missed.
  - **OUTPUT LOCATION:** `benchmarking/degradation_levers.md`

---

## Wave 7 — WS7: Governance

- [ ] **T28. Update steering and resolve the stack deviations**
  - **AGENT:** ⚙️ Documentation
  - **PHASE:** 22 / WS7
  - **OBJECTIVE:** Bring `.kiro/steering/tech.md` in line with reality and the new locked stack.
  - **INPUT:** `tech.md:8,11,42`, T26 results, `experiments_log.json` environment fields
  - **CONSTRAINTS:** Resolve both recorded deviations: Holistic on device (now fixed by WS4) and Colab-vs-`local M1` training (needs a PM ruling — amend the steering doc or record the deviation).
  - **ACCEPTANCE CRITERIA:** No steering claim contradicts the code or the logs. The feature-spec version and Holistic runtime are named as locked.
  - **OUTPUT LOCATION:** `.kiro/steering/tech.md`

- [ ] **T29. Annotate re-opened gates**
  - **AGENT:** ⚙️ Documentation
  - **PHASE:** 22 / WS7
  - **OBJECTIVE:** Mark gates 2, 3, 4, 5, 6 as re-opened by spec 22, with new criteria.
  - **INPUT:** `docs/phase-gates.md`, T26
  - **CONSTRAINTS:** Annotate; do not rewrite rows that hardening A2/D7 are already editing, to avoid conflicting edits to the same lines.
  - **ACCEPTANCE CRITERIA:** Each re-opened gate names its new criteria and what closes it. No performance claim traces to a retroactive or emulator-only entry.
  - **OUTPUT LOCATION:** `docs/phase-gates.md`

- [ ] **T30. Decision records and PRD addendum**
  - **AGENT:** ⚙️ Documentation
  - **PHASE:** 22 / WS7
  - **OBJECTIVE:** Record every PM-level decision, dated, with reasoning; add a PRD addendum.
  - **INPUT:** DECISIONS-FOR-PM set, T4, T16, T22, T28
  - **CONSTRAINTS:** Addendum, not a rewrite. One file per decision.
  - **ACCEPTANCE CRITERIA:** Every DECISIONS-FOR-PM item has a dated record with the ruling and reasoning.
  - **OUTPUT LOCATION:** `docs/decisions/`, `docs/PRD.md` addendum

- [ ] **T31. Ship-or-reject determination**
  - **AGENT:** ⚙️ Documentation + PM
  - **PHASE:** 22 / WS7 gate
  - **OBJECTIVE:** Apply acceptance criterion 6 and record the outcome.
  - **INPUT:** T11–T13, T26, T18, T22
  - **CONSTRAINTS:** Rejection is a legitimate outcome. If any rejection condition holds, the 258-dim model is retained and the switch defaults to it. The determination must cite measurements, not impressions.
  - **ACCEPTANCE CRITERIA:** A written determination citing per-pair accuracy with CIs, end-to-end p95 latency, parity-test status, and expert-validation status against criterion 6's four conditions.
  - **OUTPUT LOCATION:** `docs/decisions/` + `docs/phase-gates.md`

---

## Task Dependency Graph

```json
{
  "waves": [
    ["T0"],
    ["T1"],
    ["T2", "T3"],
    ["T4", "T5"],
    ["T6"],
    ["T7"],
    ["T8", "T9", "T20"],
    ["T10"],
    ["T11"],
    ["T12", "T13", "T14"],
    ["T15"],
    ["T16"],
    ["T17"],
    ["T18", "T19"],
    ["T21"],
    ["T22", "T23"],
    ["T24"],
    ["T25"],
    ["T26"],
    ["T27"],
    ["T28", "T29", "T30"],
    ["T31"]
  ]
}
```

## Notes

- **T6 is a falsification gate, not a formality.** If wrist-relative separation does not survive
  the rebuilt sequences, WS2's premise is wrong and the plan must stop and re-diagnose rather than
  proceed to WS3.
- **T20 can land early and independently.** The `overall_match` defect and the missing
  minimum-support check are real regardless of Holistic, and fixing them does not touch the feature
  space.
- **T3 deliberately scopes down.** The instinct to re-extract all 1016 clips to "fix hands" is
  wrong: in-span detection is already 0.954. Only six classes fall below 0.85.
- **T11's rung 0 → rung 1 delta is the thesis result.** It quantifies how much accuracy uniform
  sampling was discarding, which is a sharper contribution than "we adopted Holistic".
- **T15 must resolve the pose `visibility` question** before T5 can finalize whether visibility is
  in the vector. T5 may need a second pass; that is expected and cheap.
- **T16 is the highest-risk task in the plan.** PR #2 calls handedness the most dangerous open bug,
  and it is the one defect that makes the project's pedagogical output confidently wrong rather
  than merely inaccurate.
- **T26 needs hardware that the project does not currently have.** Every prior performance number
  is an M1-emulator proxy. This is a procurement dependency, not an engineering one, and it should
  be raised with the PM immediately rather than at Wave 6.
- **Waves are ordered for cheap-first.** T1–T14 are offline and add no device latency. If WS1 and
  WS2 alone fix the numerals, WS4's value becomes train/serve correctness rather than accuracy, and
  the latency risk in WS6 shrinks accordingly.
