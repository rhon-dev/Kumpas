# Holistic v2 — Risk Register

Companion to `.kiro/specs/22-holistic-v2/` and `docs/holistic-v2-diagnosis.md`.
Planning document. Likelihood and impact are judgements; the evidence columns cite measurements.

Scale — **Likelihood:** Low / Medium / High. **Impact:** Low / Medium / High / Critical
(Critical = invalidates a thesis claim or blocks the defense).

---

## 1. Top risks

### R1 — Handedness or mirroring is silently swapped
| | |
|---|---|
| **Likelihood** | **High** — currently uncalibrated and unverified |
| **Impact** | **Critical** |
| **Evidence** | `VisionEngine.kt:146` assigns hand blocks from `hands.handedness()[h][0].categoryName()`; `CameraPreviewView` feeds the raw front-camera bitmap without mirroring; `benchmarking/phase4_emulator_report.md` lists this as an open issue. PR #2 §1.4 calls it the most dangerous open bug in the repo. |
| **Why it is critical** | The classifier may absorb a consistent swap and still score well. `FeedbackEngine` emits **per-hand** instructions ("your left hand…"), so a swap makes the project's actual pedagogical contribution confidently wrong rather than merely less accurate. A wrong instruction is worse than no instruction for a learner. |
| **Mitigation** | T16 settles it **once**, under the Holistic runtime, with an assertion test rather than reasoning. Holistic's separate `leftHandLandmarks()`/`rightHandLandmarks()` accessors remove the classifier ambiguity but **not** the mirroring question. Do not fix it in the split-model path first — that work is discarded. |
| **Owner** | 🟢 Mobile/Flutter |
| **Residual** | Low after T16, provided the test asserts anatomical correctness on a real signer, not just Python/Kotlin self-consistency. Two mirrored-but-agreeing implementations pass a naive parity test. |

### R2 — No real device, so WS6 cannot close
| | |
|---|---|
| **Likelihood** | **High** — zero real-device measurements exist today |
| **Impact** | **High** |
| **Evidence** | `benchmarking/benchmark_history.json` holds 4 entries: latency and FPS on an `AVD medium_phone` hosted on an Apple M1, both self-labelled retroactive proxies, plus two `offline/python` accuracy runs. No entry has a real device. |
| **Consequence** | The `<150 ms` and `24–30 FPS` gates cannot be honestly closed for either pipeline, and the thesis benchmarking chapter stays the weakest section. This blocks the ship/reject determination (T31), since acceptance criterion 6(b) is a device measurement. |
| **Mitigation** | Escalate as **procurement, not engineering**, at the start of the phase rather than at Wave 6. Interim: proceed through Waves 1–5, which are offline and device-independent, so the plan is not idle while hardware is sourced. Measure the 258-dim baseline on the same device so the comparison is fair. |
| **Owner** | 🔴 QA/Benchmarking + PM |
| **Residual** | Medium. An M1 emulator flatters performance substantially; a mid-range Helio G will be slower by a wide margin, and the direction of that error is known but not its size. |

### R3 — Holistic is too slow on a 4 GB mid-range device
| | |
|---|---|
| **Likelihood** | **Medium** |
| **Impact** | **High** |
| **Evidence** | Two models already cost 35–63 ms per sampled frame on an M1-hosted emulator (`phase4_emulator_report.md`). `.kiro/steering/tech.md:42` puts landmark extraction inside the 150 ms budget, leaving ~85–115 ms — on generous hardware. Holistic adds a face model. |
| **Honest uncertainty** | The **sign** of the change is `unverified`. One Holistic graph may be *cheaper* than two independent detectors because hand and face ROIs are derived from an already-computed pose rather than from independent full-frame detection passes. It may equally be dearer. This is measured in T15/T26, not assumed. |
| **Mitigation** | T24 per-stage budget; T27 pre-measured degradation levers ranked cheapest-accuracy-cost first, with the hard rule that the **face channel is sacrificed before the hand channel**; blendshapes instead of 478 face landmarks; face at reduced cadence. Ultimate fallback: WS1 + WS2 alone are offline and add no device latency, so the accuracy gains survive even if the Holistic runtime is rejected. |
| **Owner** | 🔴 QA/Benchmarking + 🟠 Model Optimization |
| **Residual** | Low-Medium. Rejecting the runtime while keeping the offline fixes is an acceptable landing point, which is why the plan sequences offline work first. |

### R4 — The test set is too small to detect the improvement
| | |
|---|---|
| **Likelihood** | **High** — certain unless hardening G2 lands first |
| **Impact** | **High** |
| **Evidence** | 203 test clips over 50 classes, support 4 per class (`20260705_194813_no_face_eval.md`). FIVE recall 0.250 means 1 of 4 clips correct. Best validation accuracy 1.0 across both 258-dim runs, so validation gave no model-selection signal. |
| **Consequence** | A numeral improvement from 1/4 to 3/4 is two clips. WS3's primary metric — per-pair accuracy on the seven confusion pairs — cannot be distinguished from noise, so the ablation ladder produces rankings that are not statistically meaningful. |
| **Mitigation** | `requirements.md` promotes hardening G2 from optional to **prerequisite**; T10–T14 are explicitly blocked on it. Cross-validate over the combined pool or perform a genuine three-way re-split. Report confidence intervals throughout. Accept that this **changes the reported baseline** from 95.07%. |
| **Owner** | 🟣 Model/Training + PM (the baseline change needs awareness) |
| **Residual** | Medium. Cross-validation raises statistical power but cannot manufacture signer diversity (see R5). |

### R5 — Signer overlap inflates every accuracy number
| | |
|---|---|
| **Likelihood** | **Medium-High** (mechanism plausible, not provable) |
| **Impact** | **High** |
| **Evidence** | FSL-105 `train.csv`/`test.csv` carry only `vid_path, id_label, label, category` — no signer column. Clip indices 0–21 appear in **both** splits, with ~16 train / ~4 test per class assigned differently per class. If the clip index identifies a signer — plausible but `unverified` — then most signers appear in training for some classes and in test for others. |
| **Already on record** | `docs/dataset-notes.md:20,29`, `.kiro/specs/03-dataset-audit/design.md:123,128`, `.kiro/specs/04-data-pipeline/requirements.md:19`. This is a known, documented limitation, not a new discovery. |
| **Mitigation** | Run the cheap empirical probe: per-clip body geometry (torso length, shoulder width, face scale) is already in the extracted arrays; if clips sharing an index cluster across different classes, the index encodes a signer. Then either build a signer-disjoint split or state the limitation explicitly and stop implying signer independence. |
| **Owner** | 🔵 Data/Preprocessing + ⚪ Research/Evaluation |
| **Residual** | Medium. If signers overlap and cannot be separated, the honest outcome is a scoped claim ("signer-dependent accuracy") rather than a fixed number. That is defensible; an unqualified figure is not. |

### R6 — The face subset adds no signal
| | |
|---|---|
| **Likelihood** | **Medium** |
| **Impact** | **Low** |
| **Evidence** | Both 1662-dim runs underperformed the 258-dim run (0.8571 and 0.8325 vs 0.9507). The diagnosis found the numeral confusions are explained by handshape representation, **not** by the missing face — so the face's remaining justification is narrow: GOOD AFTERNOON/GOOD EVENING and YES/NO, which have adequate in-span hand rates (0.450/0.471) and so are not explained by root cause 1. |
| **Why impact is Low** | The plan treats the face as a hypothesis under ablation (T12), not a goal. A null result is a legitimate, publishable finding and costs only T12's runtime. This is a deliberate reframing from the original brief, which treated the face as a headline objective. |
| **Mitigation** | Blendshapes over raw landmarks to keep dimensionality small; strict ablation gating; drop the channel on a null result rather than tuning it into significance; T23 (NMM feedback dimension) is explicitly conditional on T12. |
| **Owner** | 🟣 Model/Training |
| **Residual** | Low |

### R7 — Re-extraction is undertaken to "recover hands" and finds nothing
| | |
|---|---|
| **Likelihood** | **Medium** — this is what the original brief directed |
| **Impact** | **Medium** (wasted time, not a wrong result) |
| **Evidence** | In-span hand detection is **0.954** (median 0.989); numerals 0.920–0.996. The aggregate 0.352 reflects rest padding: clips are 39.6% leading rest, 35.6% signing, 24.8% trailing rest. |
| **Consequence** | Days spent tuning `min_detection_confidence`, resolution, and ROI re-crop for a rate that is already near ceiling where it matters, while the actual defect (temporal sampling) goes unaddressed. |
| **Mitigation** | `requirements.md` requirement 6 and T3 explicitly scope detection work to the six classes measured below 0.85 in-span (BLUE 0.570, WHITE 0.627, MOTHER 0.707, RED 0.808, WOMAN 0.840, BLACK 0.840). T4 requires re-extraction to be justified by train/serve parity and the face decision, **not** hand recovery. |
| **Owner** | 🔵 Data/Preprocessing |
| **Residual** | Low, provided the diagnosis correction is read before WS1 starts. This is the main reason the diagnosis precedes the spec. |

### R8 — FSL Expert re-validation unavailable in time
| | |
|---|---|
| **Likelihood** | **Medium** |
| **Impact** | **High** |
| **Evidence** | Phase 6 sign-off (2026-07-23) covered all 50 gold standards in the 258-dim space. A feature-space change invalidates the hand-derived dimensions. |
| **Scope is narrower than it first appears** | DTW aligns on **pose** wrists (`feedback_engine.py`, `L_WRIST_P = 15`, `R_WRIST_P = 16`), so **TIMING and MOTION remain valid** and retain the existing sign-off. Only **HANDSHAPE** and **ORIENTATION** need fresh review — two of four dimensions — plus any new NMM dimension. This materially reduces the ask. |
| **Mitigation** | T22 requests the narrow scope with a written justification rather than a full 50-sign redo. Schedule the expert window early. Rejection path: acceptance criterion 6(d) makes unavailable re-validation an explicit reason to retain the 258-dim model, so the thesis is not held hostage to scheduling. |
| **Owner** | 🟡 Feedback Algorithm + PM |
| **Residual** | Low-Medium |

### R9 — Thesis timeline
| | |
|---|---|
| **Likelihood** | **Medium-High** |
| **Impact** | **High** |
| **Evidence** | Spec 22 has 32 tasks across 7 workstreams and depends on PR #2's Stages A, B, C, D and G2. PR #2 alone estimates roughly 7 weeks. Phases 9–13 (integration testing, field benchmarking, 40-participant study, statistics, defense readiness) are all still ⬜ in `docs/phase-gates.md`. |
| **Consequence** | Holistic v2 could consume the remaining schedule and leave the evaluation study — a core PRD deliverable — unrun. An unrun study is a larger defense problem than imperfect numerals. |
| **Mitigation** | The wave ordering is the mitigation: T1–T9 (offline, cheap, no device) deliver most of the expected accuracy gain and can be stopped after Wave 2 with a coherent result. Every wave boundary is a legitimate stopping point with a shippable app. The rollback switch (T19) means abandoning later waves is not a code emergency. PM should treat Waves 3+ as conditional on schedule, not committed. |
| **Owner** | PM (Cabrera) + Adviser (Abella) |
| **Residual** | Medium. Requires an explicit PM decision on scope versus schedule, which is why it appears in DECISIONS-FOR-PM. |

---

## 2. Secondary risks

| # | Risk | L | I | Mitigation | Owner |
|---|---|---|---|---|---|
| R10 | Python and Kotlin diverge again after the spec lands | Medium | High | Golden-vector parity test (T18) fails by default and runs in CI; no layout literal permitted outside `feature_spec_v2.json` | 🟢 Mobile |
| R11 | Parity test passes while both sides are wrong in the same way | Low | Critical | T16 asserts **anatomical** correctness on a real signer, not just cross-language agreement. Parity proves consistency, not correctness — these are separate properties | 🟢 Mobile |
| R12 | Old asset loads against a new model and silently misreads | Medium | High | `gold_standards.bin` is currently a bare `50 × 30 × 258` float blob with no header (`VisionEngine.kt:62-65`). T19 adds version stamps and loud rejection | 🟢 Mobile |
| R13 | Face-mesh variant mismatch (468 trained vs 478 runtime) corrupts face indices | Medium | Medium | T4/T5 resolve the variant before any face channel ships; refined-region indices are not interchangeable | 🔵 Data |
| R14 | Pose `visibility` absent from the Tasks Holistic graph, breaking the 4-per-landmark layout | Medium | Medium | `unverified` today. T15 checks it before T5 finalizes the spec; T5 may need a second pass | 🟢 Mobile |
| R15 | `model_complexity` has no Tasks-runtime counterpart, creating new skew | Medium | Medium | T3 quantifies the effect; if material, Python must match the runtime rather than optimizing independently | 🔵 Data |
| R16 | Span detection is circular — poor detection yields a short span, hiding the poor detection | Medium | Medium | T1 requires two independent signals, one of them pose-based (pose is 1.000 across all 1016 clips); disagreements are quarantined, not resolved silently | 🔵 Data |
| R17 | Canonicalization makes present and absent hands harder to distinguish (both have a zero wrist) | High | Medium | Presence flags are a correctness requirement of canonicalization, not an optional extra (requirement 11); T18 asserts flags with exact equality | 🔵 Data |
| R18 | The 258-dim rollback path rots while unused | Medium | Medium | T19 keeps both selectable and logs which is active; T26 benchmarks both, which exercises the fallback | 🟢 Mobile |
| R19 | Two-stream architecture blows the parameter or memory budget | Low | Medium | T13 requires a parameter/latency/accuracy table against the 4 GB and 150 ms constraints; current winner is 270,834 params | 🟣 Model |
| R20 | Gate annotations conflict with PR #2's concurrent edits to the same rows | Medium | Low | T29 annotates rather than rewrites rows that hardening A2/D7 are editing | ⚙️ Documentation |
| R21 | Colab-vs-`local M1` deviation stays unresolved and surfaces at defense | Medium | Medium | T28 forces a ruling: amend steering or record the deviation. All four logged runs say `"local M1 (tensorflow 2.19.0)"` while `tech.md:11` locks Colab | ⚙️ Documentation |
| R22 | Scope creep from Holistic's extra outputs (segmentation mask, full face mesh) | Medium | Medium | PRD scope fence is explicit: no 3D avatar, no gamification. `segmentationMask()` and blendshapes make both tempting; `requirements.md` Out of Scope names them | PM |

---

## 3. Risks the diagnosis retired

Recorded so they are not re-raised.

| Risk as originally framed | Why it is retired |
|---|---|
| "MediaPipe fails to detect hands in ~2/3 of frames" | In-span detection is 0.954 (median 0.989). The aggregate reflects rest padding, not failure. |
| "Holistic's pose-guided hand ROI re-crop was never received" | It was received and it worked, in training. It is genuinely absent **on device**, which is R1/WS4's concern, not a data problem. |
| "The feedback engine fabricates handshape corrections from absent landmarks" | It already gates on presence and abstains (`feedback_engine.py:137,190`). The real defects are the missing minimum-support threshold and the `overall_match` computation — both narrower, both addressed in T20. |
| "A newer `tasks-vision` is needed for `HolisticLandmarker`" | 0.10.14, already pinned at `app/android/app/build.gradle.kts:59`, contains it. Verified from the published artifact. No dependency bump. |
| "The numerals problem may be data scarcity or genuine visual ambiguity" (PR #2 task G1) | Neither. Between-class/within-class handshape separation is 3.78 (FIVE vs FOUR) and 9.97 (THREE vs TWO) — the information is present and separable. It is a representation and sampling artifact. |

---

## 4. Risk-driven stopping points

Each wave boundary is a legitimate stop with a coherent result and a shippable app. This is the
primary mitigation for R9.

| Stop after | You have | You lack |
|---|---|---|
| Wave 2 (T9) | Measured occupancy gain, a versioned feature spec, verified canonicalization hypothesis | Any accuracy claim — no model trained yet |
| Wave 3 (T14) | Ablation ladder quantifying what uniform sampling discarded — the sharpest thesis result | On-device parity; the app still runs the old graph |
| Wave 4 (T19) | Train/serve skew closed, parity enforced, handedness settled, rollback switch | Real-device performance numbers |
| Wave 5 (T23) | Corrected feedback scoring, re-validated gold standards | Real-device performance numbers |
| Wave 6 (T27) | Honest performance evidence for both pipelines on real hardware | Only governance paperwork remains |

Stopping after Wave 3 is the highest value-per-week option if the schedule tightens: it delivers
the accuracy result and the thesis narrative without depending on hardware procurement (R2) or
expert availability (R8).
