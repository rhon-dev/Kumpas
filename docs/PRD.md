# KUMPAS — Development Governance Document

**Real-Time FSL Gesture Recognition & Corrective Feedback App**

Status: Pre-Development / Architecture Lock Pending
Audience: Interns, junior devs, and AI coding agents (Cursor / Claude Code) working on this repo

> **Rule #0:** No implementation code is written until Section 4 (Architecture) and Section 6 (Phase Gates) are explicitly approved by the PM (Cabrera) and Adviser (Abella). Agents are configured to refuse "just start coding" requests until this doc is checked into the repo as AGENTS.md context.

## 1. Problem Statement (Business/Research Framing)

Filipino Sign Language (FSL) learning resources are one-way broadcasts — videos, PDFs, static images. A hearing learner has no way to know if the sign they just made is correct. This is the "feedback vacuum." Kumpas closes that loop: the phone camera watches the learner sign, a quantized on-device model classifies it against a validated gold-standard, and the app tells the learner what specifically to fix (handshape, orientation, motion, timing) — in real time, on a mid-range Android phone, with no internet dependency at inference time.

This is not a translator app (like Sign-Bridge) and not a lab-accuracy research demo (like SENYAS). It is an instructional tool. Every product decision should be judged against: does this help the learner correct their sign faster?

## 2. Scope

### In scope (MVP / thesis deliverable)

- 50 fixed high-frequency FSL gestures (closed set, not open vocabulary)
- Android only, mid-range hardware (Helio G-series / Snapdragon 6-series, 4GB RAM min)
- On-device inference only (no cloud round-trip for classification — this is the whole point)
- Real-time feedback on: handshape, orientation, motion/trajectory, timing
- Practice mode with immediate corrective prompts (visual/text, not full avatar correction)
- Pre-test / post-test data capture tooling to support the 40-participant evaluation study
- Benchmarking harness: accuracy, precision, recall, F1, latency, FPS across lighting/background/device conditions

### Explicitly out of scope (do not let an agent scope-creep into these)

- ASL or any non-FSL sign language
- Two-way communication / sign-to-speech translation
- Open-vocabulary / continuous sentence recognition
- iOS support
- Cloud-based inference or accounts requiring internet to practice
- Gamification systems, leaderboards, social features
- Full avatar/skeleton overlay correction (feedback is prompt-based text/icon, not 3D pose overlay, unless Phase 11+ explicitly reopens this)

## 3. Current State (as of this doc)

The dataset is already collected — this changes the plan from PRIME v2's generic template. Do not schedule a "data collection" phase. What's actually still needed before training:

- [ ] Dataset audit: confirm 50 gesture classes, ~20 signers, consistent labeling scheme
- [ ] Confirm raw format (raw video vs. pre-extracted MediaPipe landmark sequences — this changes Phase 1 entirely)
- [ ] Confirm gold-standard reference clips are flagged/separated from the general training samples
- [ ] Confirm augmentation has or hasn't been applied yet (brightness ±20%, rotation ±10–15°, scaling, horizontal shift — per methodology)
- [ ] Confirm consent/privacy documentation exists for the 20 signers and covers model training + potential publication of anonymized landmark data (see Section 9)

**First AI-agent task should be a dataset audit script, not model code. This is Phase 1 below.**

> **Amendment (2026-07-05):** The actual dataset on hand is the public FSL-105 dataset (105 classes, raw video), not a team-collected 50-gesture set. See `docs/dataset-notes.md` for the audit findings and implications. The checklist above resolves differently as a result.

## 4. Architecture (locked before any coding phase begins)

```
┌─────────────────────────────┐
│  Training/Research Pipeline │  (Python, offline, Google Colab)
│  - Preprocessing            │
│  - Augmentation             │
│  - CNN-LSTM training        │
│  - TFLite conversion/quant  │
└──────────────┬──────────────┘
               │ exports .tflite model + label map
               ▼
┌─────────────────────────────┐
│  Kumpas Mobile App (Flutter)│
│  - Camera capture           │
│  - MediaPipe Holistic       │
│    landmark extraction      │
│  - TFLite inference         │
│  - Feedback Engine          │
│    (gold-standard compare)  │
│  - Practice UI              │
│  - Local session logging    │
└──────────────┬──────────────┘
               │ (optional, only if backend approved)
               ▼
┌─────────────────────────────┐
│  Lightweight backend        │  Firebase/Firestore or similar
│  - Participant/session sync │
│  - Pre/post assessment data │
│  - Researcher dashboard     │
└─────────────────────────────┘
```

**Tech stack (as specified in the proposal — do not substitute without PM approval):**

- Mobile: Flutter (Dart), targeting Android only for MVP
- CV/landmarks: MediaPipe Holistic (hand + face + pose)
- Model training: TensorFlow / Keras, CNN-LSTM architecture
- Deployment: TensorFlow Lite (quantized, target inference <150ms)
- Training environment: Google Colab (GPU)
- Design: Figma
- IDE: VS Code
- Backend (if/when approved): Firebase (Auth + Firestore) — kept intentionally minimal; this is a research tool, not a SaaS product

**Non-negotiable performance targets (from methodology — hold agents to these, not vibes):**

- Recognition accuracy ≥ 90% on held-out test set
- Inference latency < 150ms per gesture window
- Sustained 24–30 FPS video pipeline on target hardware
- Explicit benchmarking under: optimal light / low light / cluttered background

## 5. User Roles

| Role | Description | Access |
|------|-------------|--------|
| Learner (hearing participant) | Uses practice mode, receives feedback | App only, no admin panel |
| FSL Expert/Validator | Validates gold-standard clips are linguistically correct | Read/flag access to gesture library, not app code |
| Researcher/Analyst | Pulls pre/post assessment data, engagement metrics | Dashboard/export access, read-only on production data |
| Content Admin | Manages the 50-gesture library, gold-standard assets | Admin panel (if backend built) or config files (if not) |
| Adviser/PM | Approves phase gates | Repo owner, merge rights |

## 6. Development Phases (gated — agents stop at each ▶ checkpoint)

**Phase 0 — Repo & environment setup**
Deliverable: repo skeleton, AGENTS.md, Flutter project scaffold, Colab notebook template, .gitignore for model artifacts/datasets.
▶ Gate: PM confirms structure before any real code.

**Phase 1 — Dataset audit & preprocessing pipeline** (replaces "data collection" since dataset exists)
Deliverable: audit script/report on the existing dataset (class balance, signer diversity, landmark extraction completeness), preprocessing pipeline that turns raw video/landmarks into fixed-length sequences ready for training, augmentation pipeline (brightness 80–120%, rotation ±10–15°, scale, shift) applied and logged.
▶ Gate: Data Agent presents class distribution + sample counts. No training starts until PM signs off dataset is clean.

**Phase 2 — Model architecture & training**
Deliverable: CNN-LSTM baseline trained in Colab, experiment log (architecture variants tried, hyperparameters, val accuracy per variant).
▶ Gate: Adviser reviews confusion matrix per gesture class before model is "selected."

**Phase 3 — Model evaluation**
Deliverable: accuracy/precision/recall/F1 report, per-gesture error analysis (which of the 50 signs get confused with which).
▶ Gate: Must hit or have a plan to hit ≥90% accuracy before moving to quantization.

**Phase 4 — TFLite conversion & on-device benchmarking**
Deliverable: quantized .tflite model, latency benchmark report on an actual mid-range device when available; if no real Android device is available, use an emulator and install/download one if needed, then test FPS.
▶ Gate: <150ms latency and 24–30 FPS confirmed on real hardware when available, or via an emulator fallback if no physical device is present, before mobile integration starts.

**Phase 5 — Mobile app skeleton**
Deliverable: Flutter app with working camera feed + MediaPipe landmark extraction + model inference running end-to-end (no feedback logic yet, just "predicted: gesture X").
▶ Gate: Runs on a real device without crashing at target FPS; if no physical device is available, use an emulator and install/download one if needed.

**Phase 6 — Corrective feedback engine**
Deliverable: algorithm comparing learner's landmark sequence against gold-standard (e.g., per-joint angle/position deltas or DTW-based alignment), producing structured feedback objects (which dimension is wrong: handshape / orientation / motion / timing).
▶ Gate: Feedback Agent demonstrates output on 5 sample "wrong" attempts with human-readable corrective prompts, reviewed by FSL Expert for linguistic sense.

**Phase 7 — Practice UI (Figma → Flutter)**
Deliverable: practice screen, feedback display, gesture library browser, session history — built from approved Figma files only.
▶ Gate: UI matches approved Figma; no new screens invented ad hoc.

**Phase 8 — Session logging / optional backend**
Deliverable: local (or Firebase, if approved) storage of attempt logs, pre/post assessment capture forms for the researcher.
▶ Gate: PM confirms whether cloud sync is in-scope before any backend agent starts.

**Phase 9 — Integration testing**
Deliverable: full end-to-end test matrix (all 50 gestures, multiple signers, both group types).
▶ Gate: No open blocking bugs before benchmarking phase.

**Phase 10 — Field benchmarking**
Deliverable: results across the 3 environment conditions (optimal/low-light/cluttered) × device matrix, formatted for the thesis technical validation chapter.

**Phase 11 — Pilot evaluation study support**
Deliverable: tooling/scripts to support the 40-participant experimental/control pre-test/post-test data collection and scoring against the standardized rubric.

**Phase 12 — Analysis & write-up tooling**
Deliverable: stats scripts for the Research/Analyst role (pre/post comparison, engagement metrics), not production app code.

**Phase 13 — Final polish & defense readiness**
Deliverable: cleaned repo, README, reproducibility notes for training pipeline, final benchmarking tables.

## 7. AI Agent Personas (paste the relevant one into Cursor/Claude before assigning a task)

- 🔵 **Data/Preprocessing Agent** — Python only. Owns dataset audit, cleaning, augmentation. Never touches Flutter code. Must log every transform applied to the dataset (reproducibility matters for the thesis methodology chapter).
- 🟣 **Model/Training Agent** — TensorFlow/Keras, Colab notebooks. Owns CNN-LSTM architecture experiments. Must log every experiment (architecture, hyperparams, resulting val accuracy) — no silent overwriting of previous results.
- 🟠 **Model Optimization Agent** — TFLite conversion, quantization, on-device benchmarking. Owns the latency/FPS numbers. Reports must specify actual device model tested, not "should work."
- 🟢 **Mobile/Flutter Agent** — Owns camera pipeline, MediaPipe integration, state management, UI screens. Does not modify the trained model or feedback-comparison math, only calls into it.
- 🟡 **Feedback Algorithm Agent** — Owns the gold-standard comparison logic (this is the pedagogical core of the app — treat changes here as high-risk, always reviewed by the FSL Expert, not just the PM).
- 🔴 **QA/Benchmarking Agent** — Owns the lighting/background/device test matrix and the accuracy/latency/FPS reporting. Independent from the Model Agent — should not "grade its own homework."
- ⚪ **Research/Evaluation Agent** — Owns pre/post assessment scripts and stats. Read-only relationship to the app codebase.
- ⚫ **Security/Privacy Agent** — Owns consent handling, anonymization of participant video/landmark data, and Data Privacy Act (RA 10173) compliance review before any dataset or clip leaves the local environment.
- ⚙️ **Documentation Agent** — Keeps AGENTS.md, this PRD, and phase-gate status in sync with actual repo state. Flags drift between "what the doc says" and "what the code does."

## 8. Standard AI Task Prompt Template

Interns must fill this before assigning any agent a task:

```
AGENT: [which persona from Section 7]
PHASE: [which numbered phase from Section 6]
OBJECTIVE: [one sentence — what should exist after this task]
INPUT: [exact file/dataset paths the agent should use]
CONSTRAINTS: [what it must NOT touch — e.g. "do not modify the feedback comparison logic"]
ACCEPTANCE CRITERIA: [measurable — e.g. "val accuracy ≥ 90% on held-out set" or "latency < 150ms on Snapdragon 680 device"]
OUTPUT LOCATION: [where the deliverable should be saved]
```

No task gets assigned to an agent without this filled in. If an intern can't fill in "acceptance criteria," they don't understand the task well enough to delegate it yet.

## 9. Privacy & Compliance Notes

- Participant video/landmark data falls under the Data Privacy Act of 2012 (RA 10173) — biometric-adjacent data (body/hand/face landmarks) requires informed consent covering training use and any publication of anonymized derivatives.
- Gold-standard signer clips should be stored separately from general training data with clear provenance (who validated them, when).
- No raw participant video should be committed to the repo — only extracted landmark sequences, and only with consent on file.

## 10. Repo Structure

```
kumpas/
├── AGENTS.md                 # agent personas, pasted from Section 7
├── docs/
│   ├── PRD.md                # this document
│   └── phase-gates.md        # live checklist of Section 6
├── training/                 # Python, Colab notebooks, Data/Model agents live here
│   ├── preprocessing/
│   ├── augmentation/
│   ├── models/
│   └── tflite_export/
├── app/                      # Flutter project, Mobile Agent lives here
│   ├── lib/
│   │   ├── camera/
│   │   ├── inference/
│   │   ├── feedback_engine/
│   │   └── ui/
├── benchmarking/             # QA Agent test harnesses + results
└── evaluation/               # Research Agent — pre/post stats scripts
```

## 11. Risks to Watch

- **Class imbalance** across the 50 gestures if some signers contributed more samples than others — audit this in Phase 1, don't discover it in Phase 3.
- **Hardware fragmentation** — "mid-range Android" spans a wide performance range; benchmark on at least 2-3 distinct real devices when possible, and use an emulator fallback if real devices are unavailable.
- **Timeline pressure** — 11 months total, and if dataset work is already done you've effectively skipped 2 months of the original work plan; don't let that slack get silently absorbed by scope creep instead of an earlier defense-readiness date.
- **Feedback quality vs. model accuracy** — a model can hit 90% classification accuracy while still giving unhelpful feedback if the gold-standard comparison logic is weak. Treat Phase 6 as equally important as Phase 2-3, not an afterthought.
