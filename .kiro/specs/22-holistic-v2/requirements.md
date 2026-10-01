# Phase 22 — Holistic v2: Manual-Channel Recovery & On-Device Parity

## Reconciliation with `docs/hardening-plan.md` (PR #2)

PR #2 defines an eight-stage hardening plan (Stages A–H). This spec does **not** replace it and
does not re-litigate it. Relationship, explicitly:

### Holistic v2 DEPENDS ON the hardening plan

| This spec | Depends on | Why |
|---|---|---|
| All workstreams | **Stage A** (truth-in-docs) | Planning against gates marked PASS on self-invalidating evidence is the failure mode this spec must avoid. A must land first. |
| WS1, WS3 | **Stage B1, B5** (real TF/MediaPipe envs, reproducibility doc) | Re-extraction and an ablation ladder are worthless if the environment cannot be reconstructed. `training/requirements.txt` currently omits TensorFlow entirely. |
| WS2, WS5, WS7 | **Stage B3** (versioned release artifacts) | B3's release mechanism is where version-stamped `feature_spec`, model, and gold standards are published. WS7 extends it; it does not invent a second scheme. |
| WS4 | **Stage B2** (self-contained `fetch_assets.sh` + SHA-256) | WS4 adds `holistic_landmarker.task` to the asset set. It must arrive through B2's checksum-verified path, not a new one. |
| WS4 | **Stage C3** (extract `normalize()` into a testable class) | C3 creates exactly the seam WS4's golden-vector parity test needs. Without it the test requires a camera. |
| WS5 | **Stage C4, C5** (Filipino copy, documented thresholds) | WS5 adds a fifth feedback dimension. Its copy must be Filipino from the first commit and its thresholds documented in C5's format, not retrofitted. |
| WS3 | **Stage G2** (grow test set / cross-validation with CI) | **Promoted from optional to prerequisite.** WS3's primary metric is per-pair accuracy on classes with support 4. A numeral improvement cannot be distinguished from noise at n=4. |
| WS6 | **Stage D (all)** | Especially **D4** (end-to-end latency covering MediaPipe, not interpreter-only) and **D5** (real mid-range device × 3 conditions). D4's number is the only one capable of judging a three-model pipeline. |

### Holistic v2 SUPERSEDES part of the hardening plan

| Hardening task | Status | Resolution |
|---|---|---|
| **G1** — "Diagnose the numerals confusion: data scarcity vs genuine visual ambiguity vs preprocessing artifact" | **ANSWERED — close it, do not execute it** | `docs/holistic-v2-diagnosis.md` §3 answers it: **preprocessing artifact**, two measured causes. (i) `build_sequences.py:47-49` samples 30 frames uniformly across clips that are ~64% rest, leaving 10.3 of 30 timesteps with hand data and only 7–9 for numerals. (ii) Torso-scale normalization compresses the wrist-relative handshape signal to 7.5× below pose amplitude. It is **not** data scarcity and **not** genuine ambiguity — between-class/within-class handshape separation is 3.78 (FIVE vs FOUR) and 9.97 (THREE vs TWO). |
| **G3** — "only if G1 says it's fixable: targeted augmentation or an architecture change" | **Superseded by WS1 + WS2 + WS3** | The intervention is now specific and evidence-led rather than speculative: temporal segmentation and hand canonicalization, ablation-tested. |

### Holistic v2 CHANGES the hardening plan's assumptions

| Hardening task | Change | Action |
|---|---|---|
| **C1** — handedness/mirroring fix, targeting `VisionEngine.kt:146` `categoryName()`-based left/right assignment | **The mechanism disappears under Holistic.** `HolisticLandmarkerResult` exposes `leftHandLandmarks()` and `rightHandLandmarks()` as separate accessors, so there is no handedness classifier to get wrong. Legacy Python Holistic also assigns in-graph, so training and a Tasks-Holistic runtime already share a convention — the current app is the outlier. | **Do not fix C1 against the split-model code and then re-fix it under Holistic.** Answer the mirroring question **once**, inside **WS4-T3**, against the Holistic runtime. C1's *fixture-test* requirement is not dropped — it is absorbed and strengthened as WS4's golden-vector test. Front-camera mirroring remains a live question: a mirrored input still makes the graph label an anatomical left hand as right. |
| **C2** — normalization parity test | Target changes. Testing the 258-dim `normalize()` is throwaway work **unless** Holistic v2 is rejected. | Build C2's **harness** (fixture exporter + Kotlin test scaffold) now, since it is reusable, but pin fixtures to whichever `feature_spec` version is live. WS4-T4 supplies v2 fixtures. |
| **B2, B3** — asset + release set | Grows. | Add `holistic_landmarker.task`, `feature_spec_v2.json`, and version-stamped `gold_standards_v2.bin` to the same checksum-verified release path. |
| **D5** — real-device benchmarking | Pass/fail thresholds cannot be inherited; Holistic runs three models per frame. | Run D5 **twice**: once on the 258-dim baseline (establishes the comparison point and preserves a fallback measurement) and once on Holistic v2. WS6 re-derives the per-stage budget. |
| **A2, A3, D7** — gate truthfulness | Extended, not duplicated. | WS7 adds a "re-opened by spec 22" annotation to `docs/phase-gates.md`. It must not be a second competing rewrite of the same rows. |
| **G4** — missing per-run eval artifacts | Unchanged and still required. | WS3's ablation ladder must emit the same artifact set (`_eval.md`, `_confusion.png`, `_per_class.csv`) for every run. |

### Owned by the hardening plan alone — out of scope here

Stage E (session-logging keep-or-delete), Stage F (evaluation study tooling), Stage H (release
readiness), A1, A4, B4 (CI), and findings 1.7 (dead code), 1.8 (`BenchmarkMode`), 1.10 (cosmetic
UI), 1.11 (release signing). This spec does not touch them.

---

## Objective

Recover the manual (hand) channel that the current pipeline discards, expose it in a
representation the classifier can use, and eliminate the train/serve skew created by the app
running a different landmark graph than the training pipeline — while keeping the 95.07% /
258-dim path shippable until the replacement is proven better on real hardware.

This is **not** "adopt MediaPipe Holistic". `training/preprocessing/extract_landmarks.py:54`
already uses it and it worked: hand detection inside the signing span measures **0.954**
(median 0.989). The gaps are (1) sequence construction throws most of the manual signal away,
(2) the representation buries handshape, and (3) the Android app never ran Holistic at all.

Full evidence: `docs/holistic-v2-diagnosis.md`. Risks: `docs/holistic-v2-risks.md`.

## Glossary

| Term | Definition |
|------|-----------|
| Signing span | The frame interval of a clip between first and last hand detection. Measures ~35.6% of an FSL-105 clip; the rest is the signer at rest. |
| In-span detection rate | Hand-detection rate computed only within the signing span. 0.954 dataset-wide — the number that shows detection was never the problem. |
| Feature spec | A versioned, machine-readable declaration of landmark selection, index layout, normalization, and sequence length. Single source of truth for Python and Kotlin. |
| Presence flag | An explicit per-block validity bit, so "hand absent" is never numerically identical to "hand at the origin". |
| Golden vector | A committed fixture pairing fixed input frames with the Python-computed feature vector, used to prove the Kotlin runtime reproduces it. |
| NMM | Non-manual marker — facial expression, mouth morpheme, head movement. Grammatically meaningful in sign languages. |
| Blendshape | A named facial-expression coefficient (brow raise, jaw open, mouth pucker) exposed by `HolisticLandmarkerResult.faceBlendshapes()`. A compact alternative to raw face landmarks. |
| Confusion pair | An ordered (true, predicted) pair from the Phase 3 eval report. The seven observed pairs are the primary success metric for WS3. |
| Ablation ladder | A pre-registered sequence of runs on identical splits, each adding one feature block, so every dimension earns its place. |

## Requirements

### WS1 — Sequence construction v2 (🔵 Data/Preprocessing)

- [ ] 1. WHEN a clip is converted into a fixed-length sequence, the system SHALL detect the signing span and sample the `seq_len` frames **within** that span, rather than uniformly across the whole clip, and SHALL record the detected span boundaries per clip.
- [ ] 2. WHEN the signing span cannot be detected for a clip, the system SHALL fall back to whole-clip uniform sampling, mark the clip in the log, and quarantine it from the training set pending review — never silently substitute a degenerate sequence.
- [ ] 3. WHEN sequences are rebuilt, the system SHALL report the resulting per-sequence hand-presence occupancy (timesteps containing hand data, of `seq_len`) for train and test, so the improvement over the measured baseline of 10.3/30 is visible and auditable.
- [ ] 4. WHEN landmarks are re-extracted, the system SHALL acquire the **full** Holistic keypoint set (pose + face + both hands) at extraction time; any dimensionality reduction SHALL occur downstream as an ablation-tested feature-selection step under WS3, never as an unexamined deletion at extraction.
- [ ] 5. WHEN extraction parameters are varied, the system SHALL produce an ablation table mapping each lever to its measured effect on in-span hand-detection rate — candidate levers: `refine_face_landmarks`, `min_detection_confidence`, `min_tracking_confidence`, `model_complexity`, input resolution handling, and temporal interpolation of short hand dropouts.
- [ ] 6. The system SHALL prioritize levers by measured benefit and SHALL NOT assume hand recovery is the objective: in-span detection is already 0.954, so WS1's measurable win is occupancy (requirement 3), not detection rate. Detection-rate work SHALL be scoped to the six classes measured below 0.85 in-span (BLUE 0.570, WHITE 0.627, MOTHER 0.707, RED 0.808, WOMAN 0.840, BLACK 0.840).
- [ ] 7. Landmark arrays SHALL remain outside the repository per the existing convention; only logs, reports, and ablation tables are committed.

### WS2 — Versioned feature specification (🔵 Data/Preprocessing + 🟢 Mobile/Flutter)

- [ ] 8. The system SHALL define exactly one machine-readable feature specification (`training/feature_spec_v2.json`) declaring: landmark selection, index layout, per-block normalization, derived-feature definitions, sequence length, and a version identifier.
- [ ] 9. Both the Python pipeline and the Kotlin runtime SHALL derive their feature layout from that specification. The duplicated normalization logic in `build_sequences.py:54` and `VisionEngine.kt:242` SHALL be reduced to a single declarative source consumed by both.
- [ ] 10. The feature vector SHALL encode handshape explicitly: hand landmarks canonicalized wrist-relative and scale-normalized per hand, plus derived features (inter-fingertip distances, finger curl angles, palm-normal orientation, wrist velocity), so handshape is no longer a 7.5×-smaller-amplitude perturbation of absolute position.
- [ ] 11. The feature vector SHALL carry an explicit per-block presence/validity flag for pose, face, left hand, and right hand, so an absent block is never numerically identical to a block located at the coordinate origin.
- [ ] 12. WHEN a face channel is included, it SHALL be a justified compact representation — blendshape coefficients from `faceBlendshapes()`, or a sign-linguistically motivated landmark subset (brows, eyelids, mouth/lip contour, jaw, head-orientation anchors) — and SHALL NOT reintroduce the 1404-dimension raw face block that scored 0.8571 and 0.8325.
- [ ] 13. The specification SHALL resolve the face-mesh mismatch: training used the base 468-landmark mesh (`extract_landmarks.py:57`, `refine_face_landmarks=False`) while the Tasks `HolisticLandmarker` is documented at 553 total landmarks, implying the refined 478 mesh. One side SHALL move, or the spec SHALL restrict itself to indices stable across both. The decision SHALL be recorded.
- [ ] 14. The specification SHALL state whether pose `visibility` is part of the vector, and this SHALL be contingent on verifying that the Tasks Holistic graph populates it — currently `unverified`.

### WS3 — Model v2 and the ablation ladder (🟣 Model/Training)

- [ ] 15. The system SHALL run a **pre-registered** ablation ladder on identical splits, logging every run to `training/models/experiments_log.json`: pose-only baseline → + hands (raw) → + hands (canonicalized) → + derived handshape features → + face/NMM channel → full.
- [ ] 16. Each ladder run SHALL emit the full artifact set (`_eval.md`, `_confusion.png`, `_per_class.csv`) so runs are comparable, satisfying hardening task G4's requirement for all runs, not just the winner.
- [ ] 17. The primary success metric SHALL be **per-pair accuracy on the seven observed confusion pairs** (FIVE→FOUR, THREE→TWO, FOUR→FIVE, YOURE WELCOME→THANK YOU, YESTERDAY→TOMORROW, YES→NO, GOOD AFTERNOON→GOOD EVENING), not overall accuracy.
- [ ] 18. The system SHALL additionally report macro-F1, confidence calibration (ECE or a reliability curve), and per-class support, and SHALL report accuracy with a confidence interval rather than as a point estimate.
- [ ] 19. WHEN evaluating, the system SHALL NOT claim signer-independence. It SHALL either establish a signer-disjoint split or explicitly report that signer overlap cannot be excluded from FSL-105 metadata, consistent with `.kiro/specs/04-data-pipeline/requirements.md:19`.
- [ ] 20. The system SHALL evaluate at least one architecture candidate beyond the current CNN-LSTM (for example a two-stream body/hand model with late fusion, or a temporal-attention head), justified against the 4 GB RAM and <150 ms constraints.
- [ ] 21. The system SHALL distinguish the two error mechanisms rather than assuming one: the numeral pairs are explained by handshape under-representation, but GOOD AFTERNOON / GOOD EVENING (in-span hand rates 0.450 / 0.471) and YES / NO are **not** explained by it and SHALL be analyzed separately.
- [ ] 22. The system SHALL declare, before running, the outcome that would mean **do not ship Holistic v2** (see Acceptance Criteria 6).

### WS4 — On-device Holistic parity (🟢 Mobile/Flutter)

- [ ] 23. The app SHALL replace the split `PoseLandmarker` + `HandLandmarker` path with `HolisticLandmarker`, pinned to a verified version. **Verified:** `com.google.mediapipe:tasks-vision:0.10.14` — the version already pinned at `app/android/app/build.gradle.kts:59` — already contains `com.google.mediapipe.tasks.vision.holisticlandmarker.HolisticLandmarker`. No dependency bump is required, and the plan SHALL NOT introduce one without a measured reason.
- [ ] 24. WHEN a supported Holistic task cannot meet the latency budget, the fallback SHALL reproduce Holistic's behaviour (pose-guided high-resolution hand/face ROI crops matching the training graph) rather than reverting to independent full-frame detectors, and the residual skew SHALL be documented.
- [ ] 25. The system SHALL deliver a **golden-vector parity test**: fixed sample frames → Python feature vector committed as a fixture → Kotlin must reproduce it within a stated tolerance, mirroring `FeedbackEngineParityTest.kt` (tolerance 0.05). Parity failure SHALL block the gate.
- [ ] 26. The system SHALL settle front-camera mirroring and handedness **once**, in this workstream, with a test that asserts block-level equality between the Python and Kotlin paths on the same input. It SHALL NOT be settled separately in the split-model code first.
- [ ] 27. The hardcoded class count at `VisionEngine.kt:65` (`Array(50)`) SHALL be read from `label_map.json`, and asset loading SHALL reject an asset whose feature-spec version or model hash does not match the loaded model.

### WS5 — Feedback engine v2 (🟡 Feedback Algorithm; FSL Expert reviews)

- [ ] 28. WHEN the manual channel is denser after WS1, the system SHALL re-derive the handshape and orientation thresholds on real data and SHALL replace the docstring claim "provisional pending expert calibration" with the actual calibration basis.
- [ ] 29. The system SHALL enforce a **minimum aligned-frame support** before emitting a handshape or orientation judgement, and SHALL abstain with an explicit "channel not visible" message when support is insufficient — rather than scoring from however few frames happen to contain a hand.
- [ ] 30. The system SHALL fix `overall_match` (`feedback_engine.py:204`), which currently averages only items above threshold, so that adding a milder error cannot raise the score and an empty item list does not automatically yield 1.0.
- [ ] 31. The system SHALL add a fifth feedback dimension for non-manual markers, enabled **only if** WS3 demonstrates the face/NMM channel carries signal for the affected classes.
- [ ] 32. WHEN the feature space changes, `gold_standards.bin`, `label_map.json`, and the FSL-Expert-approved prompt copy SHALL be re-exported and re-validated, version-stamped with the feature-spec version and model hash so an old asset cannot load against a new model.
- [ ] 33. Re-validation scope SHALL be justified, not assumed total: DTW alignment runs on pose wrists (`feedback_engine.py`, `L_WRIST_P = 15`, `R_WRIST_P = 16`), so TIMING and MOTION remain valid regardless of the hand channel. Only HANDSHAPE, ORIENTATION, and any new NMM dimension require fresh expert sign-off.
- [ ] 34. New user-facing copy SHALL be Filipino at first commit, consistent with hardening task C4.

### WS6 — Latency and FPS under a three-model pipeline (🔴 QA/Benchmarking)

- [ ] 35. The system SHALL re-open the latency and FPS gates rather than inheriting them, and SHALL define a per-stage budget summing to <150 ms across: camera acquisition, Holistic inference (pose/hand/face), feature construction, classifier, feedback, and render — consistent with `.kiro/steering/tech.md:42`, which defines the budget to include landmark extraction.
- [ ] 36. The system SHALL measure **end-to-end** latency including MediaPipe. The existing 0–2 ms figure measures the TFLite interpreter alone while the same report records MediaPipe at 35–63 ms; that figure SHALL NOT be presented as the latency result.
- [ ] 37. Benchmarks SHALL run on a real mid-range Android device (Helio G / Snapdragon 6 class, 4 GB RAM) across the three `environment_protocol.md` conditions, reusing the existing `benchmarking/` harness so results stay comparable. Emulator-only evidence SHALL NOT close this gate.
- [ ] 38. The system SHALL benchmark the 258-dim baseline and Holistic v2 under identical conditions, so the comparison is measured rather than inferred and a fallback measurement exists.
- [ ] 39. The system SHALL pre-plan graceful-degradation levers with the accuracy cost of each stated (face at reduced cadence, lite model variants, ROI cadence, frame-sampling stride) and a hard decision rule for what is sacrificed first if the budget is missed.
- [ ] 40. Cold-start cost SHALL be measured before and after, given that Holistic replaces two model loads with one bundle.

### WS7 — Governance, documentation, rollback (⚙️ Documentation)

- [ ] 41. `.kiro/steering/tech.md` SHALL be updated to name the feature-spec version and the Holistic runtime as the locked stack, and SHALL resolve the two recorded deviations: Holistic on device (`tech.md:8` vs `VisionEngine.kt:9-10`) and Colab for training (`tech.md:11` vs `"local M1"` in all four logged runs).
- [ ] 42. `docs/phase-gates.md` SHALL annotate which closed gates Holistic v2 re-opens — at minimum 2, 3, 4, 5, and 6 — with new gate criteria, as an annotation layered on hardening tasks A2/D7 rather than a competing rewrite.
- [ ] 43. `docs/PRD.md` SHALL receive an addendum, not a rewrite.
- [ ] 44. The system SHALL define a rollback plan: Holistic v2 ships behind a switch, and the 258-dim path stays runnable until WS3 and WS6 both pass.
- [ ] 45. All artifacts SHALL be version-stamped (feature-spec version + model hash), published through hardening task B3's release mechanism.
- [ ] 46. A decision record SHALL be written for each PM-level choice listed in the DECISIONS-FOR-PM set, dated, with reasoning.

## Acceptance Criteria

1. **Occupancy.** Rebuilt sequences raise mean hand-present timesteps materially above the measured baseline of 10.3/30 overall and 7.0–9.0/30 for numerals, reported for train and test with the same method used in `docs/holistic-v2-diagnosis.md` §3.
2. **One source of truth.** `feature_spec_v2.json` exists, both Python and Kotlin derive their layout from it, and a golden-vector parity test failing-by-default proves agreement within a stated tolerance in CI.
3. **Confusion pairs.** Per-pair accuracy on all seven observed pairs is reported before and after, with confidence intervals, on a split adequate to detect the change (hardening G2 satisfied). FIVE recall improves from the current 0.250 or the plan states why not.
4. **Every dimension earns its place.** No feature block ships without an ablation row showing its contribution; no block is deleted without one either. The 1404-dim raw face block is not reintroduced.
5. **Real measurement.** Per-stage latency and FPS come from a real mid-range device across three named conditions, end-to-end including MediaPipe, for both the baseline and Holistic v2, logged in `benchmark_history.json` with `condition` never `"n/a"`.
6. **A defined "no".** Holistic v2 is **rejected**, and the 258-dim model retained, if any of the following holds after WS3 and WS6: (a) per-pair accuracy on the numeral pairs does not improve beyond the confidence interval; (b) end-to-end p95 latency exceeds 150 ms on the target device after the WS6 degradation levers are applied; (c) the golden-vector parity test cannot be made to pass, leaving unquantified train/serve skew; (d) FSL Expert re-validation of HANDSHAPE/ORIENTATION cannot be obtained within the thesis timeline. Rejection is a legitimate outcome and leaves a shippable app.
7. **Gate honesty.** Every gate this spec re-opens is marked re-opened in `docs/phase-gates.md` with its new criteria, and no performance claim in the repo traces to a retroactive or emulator-only entry.
8. **Rollback proven.** The 258-dim path remains runnable behind a switch until criteria 3 and 5 both pass.

## Out of Scope

- Any implementation work. This spec is a plan; Rule #0 applies (see Status).
- Dependency bumps. `tasks-vision:0.10.14` already provides `HolisticLandmarker`.
- Re-running detection-rate recovery pipeline-wide. In-span detection is 0.954; only the six classes below 0.85 warrant it.
- Anything outside PRD scope: 50 FSL signs, Android, offline inference. No ASL, open vocabulary, iOS, cloud inference, gamification, or 3D avatar — the face mesh and segmentation mask make the last two tempting and they remain out.
- Changes to the approved Figma design or Filipino UI copy. This spec changes the vision, model, and feedback-contract layers only.
- Stages E, F, H of the hardening plan.

## Dependencies

- `docs/holistic-v2-diagnosis.md` — the evidence this spec is planned against.
- `docs/hardening-plan.md` (PR #2) — Stages A, B, C3/C4/C5, D, and G2 are prerequisites as tabled above.
- `.kiro/specs/04-data-pipeline/` — the pipeline this supersedes; its signer-independence caveat carries forward.
- `.kiro/specs/10-feedback-logic/` — the feedback contract WS5 revises.
- `.kiro/specs/13-benchmarking-harness/` — reused by WS6; its task checkboxes need hardening A1 first.
- `training/feedback/gold_standards_manifest.json` and the 2026-07-23 FSL Expert sign-off — partially invalidated by a feature-space change (WS5 requirement 33).
- A real mid-range Android device. WS6 cannot close without one.

## Status

**Planning only — awaiting PM (Cabrera) and Adviser (Abella) approval per `AGENTS.md` Rule #0.**
No implementation may begin, including WS1. Findings A and E in the original brief were corrected
during verification, so the plan follows the measured numbers rather than the briefed ones; the
PM should review that correction before approving scope. See the DECISIONS-FOR-PM set for choices
that must be settled before WS1 starts.
