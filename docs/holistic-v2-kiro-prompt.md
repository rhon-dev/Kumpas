# Kiro Prompt — KUMPAS "Holistic v2" Re-Plan

Paste everything inside the fenced block below into Kiro, with the `rhon-dev/Kumpas` repo open.
It is written to be self-verifying: Kiro must confirm each claimed number from the repo before it plans against it.

---

```text
ROLE
You are acting as the Kumpas technical lead + planning agent inside Kiro, operating under the
governance already defined in this repo: AGENTS.md (Rule #0 and the agent personas), docs/PRD.md,
docs/phase-gates.md, and .kiro/steering/{product,tech,structure}.md. Honor all of it. Where my
instructions and AGENTS.md conflict, AGENTS.md wins and you tell me about the conflict.

MISSION
Produce a NEW, GATED PLAN ("Holistic v2") that makes MediaPipe Holistic real, end to end, and that
fixes the accuracy/feedback-validity defects the current pipeline is hiding. Plan artifacts only in
this pass — no implementation code (Rule #0). You stop at the approval checkpoint defined below.

WHAT MEDIAPIPE HOLISTIC ACTUALLY IS (the standard this plan must meet)
- One all-in-one pipeline that runs pose, face, and hand models together in a single coordinated graph.
- 543 landmarks with the base face mesh (33 pose + 468 face + 21 + 21), up to ~553 with the refined
  face mesh (478 face landmarks) — i.e. the "540-553 landmarks simultaneously" figure.
- Multi-stage / ROI-guided: body pose estimation first roughly locates the hands and face, then
  re-crops those regions at HIGH RESOLUTION and passes the crops to the hand and face models, so small
  hands in a downscaled frame do not lose accuracy.
That third property — pose-guided high-resolution hand re-crop — is the one this project is currently
NOT getting the benefit of. Treat recovering it as the central engineering goal, not a detail.

STEP 1 — VERIFY THE DIAGNOSIS (do this first; do not plan on my word)
Read these files and confirm, correct, or refute each finding below. Report each as
CONFIRMED / CORRECTED (with the real number) / CANNOT VERIFY (with what you'd need):

  A. training/preprocessing/extraction_log.csv
     Claim: over 1016 clips, mean detection rates are pose ~1.000, face ~1.000, but
     LEFT HAND ~0.080 and RIGHT HAND ~0.344 (any-hand ~0.352). Meaning: roughly two thirds of
     training frames carry ZERO hand landmarks and were zero-filled.
  B. training/models/experiments_log.json
     Claim: the two runs that included the face (features=1662) scored test accuracy 0.8571 and
     0.8325, while the winning run dropped the face entirely (features=258, drop_face=true) and
     scored 0.9507. So "Holistic" was won by deleting 1404 of its 1662 dimensions — on ~3252
     augmented train samples. Face was discarded as a dimensionality problem, never engineered.
  C. training/models/reports/20260705_194813_no_face_eval.md
     Claim: the residual errors are FIVE<->FOUR, THREE<->TWO, YES<->NO, GOOD AFTERNOON<->GOOD EVENING,
     YESTERDAY<->TOMORROW. Note what those pairs have in common: they are separated by HANDSHAPE
     (finger count, fist vs open hand) and by non-manual/direction cues — exactly the channels that
     finding (A) shows are mostly missing and finding (B) shows were deleted.
     Also note the test split is ~203 clips (~4 per class) and best val accuracy was 1.0 — state
     plainly whether those splits can support a 95.07% claim in a thesis chapter.
  D. app/android/app/src/main/kotlin/com/kumpas/kumpas_app/VisionEngine.kt and app/fetch_assets.sh
     Claim: the app does NOT run Holistic. It runs a standalone PoseLandmarker (pose_landmarker_lite.task)
     plus a standalone HandLandmarker (hand_landmarker.task) from tasks-vision 0.10.14, builds a
     258-dim vector, and has no face channel at all. Therefore: (i) the locked stack in
     .kiro/steering/tech.md ("Landmark extraction: MediaPipe Holistic") is violated on device;
     (ii) there is TRAIN/SERVE SKEW — training landmarks came from the legacy Holistic graph
     (pose-guided hand ROI), runtime landmarks come from an independent palm detector on a full frame,
     with different cropping and different z conventions.
  E. training/feedback/feedback_engine.py + training/preprocessing/build_sequences.py
     Claim: the feedback engine scores handshape and orientation from hand landmarks, yet per (A)
     those landmarks are absent in most frames, and its gold standards were built in the same
     258-dim space. Assess what that does to the validity of handshape/orientation prompts that the
     FSL Expert signed off on 2026-07-23 (docs/phase-gates.md, Phase 6 gate).
  F. Signer independence: determine from the FSL-105 metadata + build_sequences.py whether the
     train/test split is signer-disjoint. If the same signers appear in both, say so explicitly and
     treat it as a leakage risk that inflates 95.07%.
  G. benchmarking/phase4_emulator_report.md and benchmarking/benchmark_history.json
     Claim: MediaPipe already costs ~35-63ms per frame with only TWO models running (pose + hands),
     while the headline "0-2ms inference" figure measures the TFLite interpreter alone and excludes it.
     Compute what that leaves of the 150ms budget once Holistic adds the face model and the ROI
     re-crop passes, and state whether the existing budget is survivable or must be renegotiated.
     This finding sizes WS6 — do not let the plan assume the latency gate is free.

Write this as docs/holistic-v2-diagnosis.md — evidence table, file:line citations, one paragraph of
interpretation per finding, and a blunt "what this means for the thesis defense" closing section.
If any claim of mine is wrong, the plan must follow YOUR numbers, not mine.

RECONCILE WITH WORK ALREADY IN FLIGHT (do this before writing Step 2)
Open PR #2 ("docs: hardening & verification plan for the remaining phases") adds docs/hardening-plan.md:
an eight-stage gated plan (A truth-in-docs, B reproducible build + CI, C prove the math — parity tests
and front-camera handedness calibration, D real-device benchmarking, E session-logging keep-or-delete,
F study tooling, G model improvement, H release readiness). Read it and reconcile rather than compete:
  - List where Holistic v2 DEPENDS on it (its Stage B reproducible build and Stage D real-device
    benchmarking are prerequisites for WS3 and WS6; its Stage C parity work is the foundation WS4 extends
    from FeedbackEngine to the feature vector).
  - List where Holistic v2 SUPERSEDES it (its Stage G numeral-accuracy investigation is answered by this
    plan's root cause: the FIVE/FOUR/THREE/TWO errors are a missing-hand-landmark problem, not a
    hyperparameter problem).
  - List where Holistic v2 CHANGES its assumptions (its Stage C handedness fix targets
    VisionEngine.kt's categoryName()-based left/right assignment; under a Holistic runtime, handedness
    is resolved by the pose-guided graph, so specify whether that fix is still needed, moves, or is
    absorbed — and make sure the mirroring/handedness question is answered in ONE place, not two).
Output this as a short reconciliation section at the top of .kiro/specs/22-holistic-v2/requirements.md.
Do not duplicate, re-litigate, or silently overwrite anything in docs/hardening-plan.md.

STEP 2 — PRODUCE THE PLAN as a Kiro spec
Create .kiro/specs/22-holistic-v2/ with requirements.md, design.md, tasks.md, following the exact
conventions of the existing specs in .kiro/specs/ (match their heading structure, numbering, and the
AGENTS.md task template: AGENT / PHASE / OBJECTIVE / INPUT / CONSTRAINTS / ACCEPTANCE CRITERIA /
OUTPUT LOCATION). Assign every task to one of the existing AGENTS.md personas. Cover these workstreams:

  WS1 — Holistic extraction v2 (persona: Data/Preprocessing)
    Re-extract landmarks with the full Holistic keypoint set (543, or 553 with refine_face_landmarks=True)
    and fix hand recovery as the primary objective. Enumerate concrete levers and how each will be
    measured, e.g.: input resolution and aspect handling before inference, model_complexity,
    min_detection/min_tracking_confidence, static_image_mode, explicit pose-guided hand ROI re-crop and
    upscale when the Holistic graph fails to re-crop, temporal interpolation of short hand dropouts,
    and per-clip quarantine for clips that still fail. Require an ablation table (lever -> hand
    detection rate delta) so the fix is evidence-based, not vibes. Preserve the existing convention:
    landmarks stay OUTSIDE the repo; only logs/reports are committed.

  WS2 — Versioned feature spec (personas: Data/Preprocessing + Mobile)
    Create ONE machine-readable feature spec (e.g. training/feature_spec_v2.json) that is the single
    source of truth for: which landmarks are used, index layout, normalization, and sequence length.
    Both the Python pipeline and the Kotlin runtime must read/derive from it — the current duplicated
    normalization logic in build_sequences.py and VisionEngine.kt is a skew generator.
    Design the vector to use the face WITHOUT repeating the 1404-dim failure in finding (B): a curated
    non-manual-marker subset (brows, eyelids, mouth/lip contour, jaw, head-orientation anchors —
    roughly tens of points, justified sign-linguistically), plus both hands, plus an upper-body pose
    subset, plus derived features that make handshape explicit (inter-fingertip distances, curl angles,
    palm-normal orientation, wrist velocity). Specify normalization per block (mid-hip centering and
    torso scaling as today, plus wrist-relative, scale-invariant hand canonicalization) and the exact
    missing-data encoding — include an explicit per-block presence/validity flag so "absent hand" is
    never silently identical to "hand at the origin".

  WS3 — Model v2 (persona: Model/Training)
    A pre-registered ablation ladder run on the SAME splits, each row logged to
    training/models/experiments_log.json: pose-only baseline -> +hands -> +hands+derived ->
    +face subset -> full. Plus at least one architecture candidate beyond the current CNN-LSTM
    (e.g. two-stream: body/trajectory stream + hand-crop stream with late fusion, and/or a small
    temporal-attention head), justified against the 4GB-RAM / <150ms budget.
    Primary success metric is NOT overall accuracy — it is per-pair accuracy on the confusion pairs
    from finding (C), plus macro-F1, plus confidence calibration (ECE or reliability curve), plus a
    signer-independent evaluation. State up front what result would make you REJECT Holistic v2 and
    keep the 258-dim model.

  WS4 — On-device Holistic parity (persona: Mobile/Flutter)
    Replace the split PoseLandmarker+HandLandmarker path with a real Holistic runtime. Verify from the
    actual MediaPipe Android artifacts which tasks-vision version ships HolisticLandmarker and the
    holistic_landmarker task bundle, and pin it; do not assume 0.10.14 has it. If a supported Holistic
    task is unavailable for this target, specify the fallback that reproduces Holistic's behavior
    rather than abandoning it: pose-guided high-resolution hand/face ROI crops fed to the hand and face
    landmarkers, matching the training graph — and document the residual skew.
    Mandatory deliverable: a golden-vector parity test. Fixed sample frames -> Python feature vector
    committed as a fixture -> Kotlin must reproduce it within a stated tolerance, mirroring the existing
    FeedbackEngineParityTest.kt pattern. Parity failure blocks the gate.

  WS5 — Feedback engine v2 (persona: Feedback Algorithm; FSL Expert reviews)
    Now that hands are actually present, re-derive handshape/orientation thresholds on real data, and
    add a fifth dimension for non-manual markers (facial expression / mouth morpheme / head movement)
    that is only enabled once WS3 shows the face channel carries signal. Add honest abstention: when a
    required channel is missing for a frame window, the app says the hand or face was not visible
    instead of emitting a confident handshape correction. Include the artifact-migration path: the
    258-dim gold_standards.bin, label_map.json and the FSL-Expert-approved prompt copy must be
    re-exported and re-validated in the new feature space, with artifacts version-stamped
    (feature_spec version + model hash) so an old asset can never load against a new model.

  WS6 — Benchmarking under the heavier budget (persona: QA/Benchmarking)
    Holistic runs three models per frame, so re-open the latency and FPS gates rather than inheriting
    them. Define a per-stage budget that sums to <150ms (pose / hand ROI / face / classifier / feedback /
    render), reuse benchmarking/ (collect_latency.py, collect_fps.py, accuracy_benchmark.py,
    LatencyBenchmarkTest.kt, benchmark_history.json) so results stay comparable across iterations, and
    require a real mid-range Android device — flag that the current Phase 4/5 evidence is emulator-only
    on an M1 proxy and is not defensible in the thesis. Pre-plan graceful degradation levers (face at
    reduced cadence, lite model variants, ROI cadence, frame-sampling stride) with the accuracy cost of
    each stated, and a hard decision rule for what gets sacrificed first if the budget is missed.

  WS7 — Governance, docs, migration (persona: Documentation)
    Updates to .kiro/steering/tech.md (feature spec v2 + Holistic runtime as the locked stack),
    docs/phase-gates.md (which closed gates Holistic v2 RE-OPENS — at minimum 2, 3, 4, 5, 6 — and the
    new gate criteria), a docs/PRD.md addendum rather than a rewrite, and a rollback plan: Holistic v2
    ships behind a switch and the 258-dim path stays runnable until WS3+WS6 pass.

STEP 3 — OUTPUT CONTRACT
Deliver exactly these files, nothing else:
  1. docs/holistic-v2-diagnosis.md          (Step 1 evidence pack)
  2. .kiro/specs/22-holistic-v2/requirements.md
  3. .kiro/specs/22-holistic-v2/design.md
  4. .kiro/specs/22-holistic-v2/tasks.md    (ordered, dependency-aware, each with measurable acceptance criteria)
  5. docs/holistic-v2-risks.md              (risk -> likelihood -> impact -> mitigation -> owner persona;
                                             include "Holistic is too slow on 4GB mid-range", "face subset
                                             adds no signal", "re-extraction still fails to recover hands",
                                             "FSL Expert re-validation unavailable in time", "thesis timeline")
Also print in chat, not only in files:
  - a DECISIONS-FOR-PM list: every choice that needs Cabrera/Abella sign-off before WS1 starts
    (re-opening closed gates, re-running FSL Expert validation, refined vs base face mesh, device
    procurement, scope/timeline impact);
  - a one-screen summary table: workstream | why | measurable exit criterion.

CONSTRAINTS
- No implementation code, no refactors, no dependency bumps in this pass. Plans, specs, docs only.
- Do not touch: training/models/reports/*, benchmarking/benchmark_history.json, docs/design/*.png,
  or any committed artifact that is evidence of a passed gate. New work goes in new files.
- Do not commit raw video or landmark arrays; keep the outside-the-repo data convention.
- Stay inside PRD scope: 50 FSL signs, Android, offline inference. No ASL, no open vocabulary, no iOS,
  no cloud inference, no gamification, no 3D avatar — even if Holistic's face mesh makes them tempting.
- Every number you assert must be traceable to a file in this repo or to official MediaPipe docs.
  If you cannot verify something, write "unverified" — do not invent a benchmark.
- Preserve Filipino UI copy and the approved Figma design; this plan changes the vision/model layers
  and the feedback contract, not the visual design.

SELF-CHECK BEFORE YOU FINISH (state each explicitly)
  1. Does the plan actually deliver coordinated pose+face+hands with pose-guided high-resolution
     ROI re-crop, or has it quietly become "separate models again"?
  2. Is the full 540-553 landmark set acquired at extraction time, with any reduction happening as a
     justified, ablation-tested feature-selection step downstream — not as an unexamined deletion?
  3. Does every closed gate that Holistic v2 invalidates get explicitly re-opened in phase-gates.md?
  4. Is there exactly one source of truth for the feature layout, consumed by both Python and Kotlin,
     enforced by a failing-by-default parity test?
  5. Would the FIVE/FOUR, THREE/TWO and YES/NO confusions be measurably addressed — and is there a
     defined outcome that would make you recommend NOT shipping Holistic v2?

STOP after Step 3. Do not begin WS1. Wait for PM approval per AGENTS.md Rule #0.
```

---

## Why this prompt is built this way

| Technique | Where it shows up |
|---|---|
| Role + governance framing | Kiro inherits the repo's own personas, Rule #0 and gate discipline instead of a generic "senior engineer" persona |
| Grounded context, not assertions | Step 1 forces verification of six findings against named files; my numbers are falsifiable inputs, not facts |
| Task decomposition | Seven workstreams, each with one owning persona and its own exit criterion |
| Output contract | Exactly five files plus two chat artifacts — prevents the sprawling-doc failure mode |
| Negative constraints | Explicit do-not-touch list protects gate evidence; scope fence blocks face-mesh-driven scope creep |
| Falsifiable success criteria | Per-pair accuracy on the real confusion pairs, calibration, parity tolerance, staged latency budget |
| Built-in kill switch | Kiro must define what result means "don't ship Holistic v2" — planning that can conclude "no" |
| Self-validation | Five-point self-check mirrors the meta-prompt/Reflexion pattern before handoff |

## The core finding the prompt is built around

The repo claims MediaPipe Holistic, but:

- **Extraction ran Holistic and it mostly failed on hands** — `extraction_log.csv` over 1016 clips: pose 100%, face 100%, **left hand 8.0%, right hand 34.4%**. Roughly two thirds of training frames were zero-filled where the hands should be.
- **The face was then deleted to win the benchmark** — 1662-feature runs scored 85.71% / 83.25%; the winning `no_face` run (258 features) scored 95.07%. Holistic's 1404 face dimensions were dropped, not engineered.
- **The residual errors name the missing channels** — FIVE↔FOUR, THREE↔TWO, YES↔NO. Those pairs differ by *handshape*. The model is largely reading arm trajectory from pose.
- **The app isn't running Holistic at all** — `VisionEngine.kt` uses a standalone `PoseLandmarker` + `HandLandmarker` (tasks-vision 0.10.14), no face channel, so it also has train/serve skew against the Holistic-derived training data.
- **The feedback engine scores handshape and orientation** from landmarks that are absent in most frames — and that engine's gold standards passed FSL Expert sign-off on 2026-07-23.
- **There is little latency headroom left** — `phase4_emulator_report.md` records MediaPipe at 35–63ms/frame with only *two* models running, while the advertised "0–2ms inference" measures the TFLite interpreter alone. Holistic adds a third model plus ROI passes, so the prompt forces the 150ms budget to be re-derived rather than inherited.

That is why the prompt makes *pose-guided high-resolution hand re-crop* — Holistic's actual optimization — the central goal rather than a checkbox.

Related: `docs/hardening-plan.md` (PR #2) — the prompt requires Kiro to reconcile against it rather than
duplicate it. This document is a planning input only; it adds no code and changes no gate status.
