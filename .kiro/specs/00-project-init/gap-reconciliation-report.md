# Gap Reconciliation Report — SDLC Kickoff vs. Existing Documentation

**Date:** 2026-07-22  
**Author:** Kiro (AI Development Environment)  
**Purpose:** Identify all contradictions, divergences, and alignment points between the SDLC kickoff document and existing repo documentation (docs/PRD.md, docs/phase-gates.md, docs/dataset-notes.md, AGENTS.md).

---

## 1. Documents Reconciled

| Document | Role |
|----------|------|
| SDLC Kickoff (input message) | New authoritative planning framework |
| docs/PRD.md | Original governance document (13 phases) |
| docs/phase-gates.md | Live implementation status tracker |
| docs/dataset-notes.md | FSL-105 findings and implications |
| AGENTS.md | Agent context for AI coding assistants |

---

## 2. Alignments (No Conflict)

These elements are consistent across all documents:

- **Problem statement:** Feedback vacuum for FSL learners; Kumpas provides corrective feedback, not just classification.
- **Novelty claim:** Corrective feedback across four dimensions is the thesis contribution; classification is a prerequisite, not the contribution.
- **Performance targets:** ≥90% accuracy, <150ms latency, 24–30 FPS — identical in all documents.
- **Tech stack:** Flutter/Android, MediaPipe Holistic, CNN-LSTM, TFLite, Colab.
- **Dataset handling:** FSL-105 public dataset, kept outside repo, .gitignore blocks video, RA 10173 applies to evaluation-study participant data.
- **Offline enforcement:** Zero network calls during inference/normal operation.
- **Repo layout:** app/, training/, benchmarking/, evaluation/, docs/ — consistent.

---

## 3. Contradictions Requiring Resolution

### 3.1 Sign Count: 50 vs. 105

| Source | Position |
|--------|----------|
| PRD.md §2 | "50 fixed high-frequency FSL gestures (closed set)" |
| SDLC Kickoff §6.1 | "FSL-105-based landmark extraction pipeline" |
| phase-gates.md | "50-class subset — RESOLVED: everyday-usage pick approved" |
| dataset-notes.md | Notes 105 classes exist, suggests 50-class subset |

**Resolution needed:** The 50-sign subset was already selected and approved per phase-gates.md. The kickoff's "FSL-105-based" language refers to the source dataset, not the MVP sign count. **Recommend: MVP remains 50 signs. Confirm with author.**

### 3.2 Phase Structure: 14 Phases vs. 20 Phases

| Source | Structure |
|--------|-----------|
| PRD.md §6 | Phases 0–13 (14 total, mixed planning + implementation) |
| SDLC Kickoff §10 | Phases 0–20 (21 total, strict planning/implementation separation) |

**Mapping of existing progress:**
| Old Phase | Kickoff Equivalent | Status |
|-----------|-------------------|--------|
| 0 (Repo setup) | 00 (Project init) | ✅ Done |
| 1 (Dataset audit + pipeline) | 03 + 04 (Audit + Data pipeline) | ✅ Done |
| 2 (Model training) | 05 + 06 (Architecture + Training plan) | ✅ Done |
| 3 (Model evaluation) | 07 (Model evaluation) | ✅ Done |
| 4 (TFLite conversion) | 08 (Quantization/export) | ✅ Done (emulator) |
| 5 (Flutter skeleton) | 09 + 12 (Mobile arch + Integration) | ✅ Done |
| 6 (Feedback engine) | 10 (Feedback logic) | ✅ Impl done, expert validation pending |
| 7 (Practice UI) | 11 (UX flow) | ✅ Done |
| 8–13 (Remaining) | 13–20 (Benchmarking through defense) | ⬜ Not started |

**Resolution:** The kickoff structure supersedes the PRD for planning purposes. Existing implementation maps into Phase 17 delivery. Specs 00–16 are written to *formalize* decisions already made AND specify what still needs design work (especially Phases 13–16 which are entirely new in the kickoff).

### 3.3 Backend: Maybe vs. Explicitly No

| Source | Position |
|--------|----------|
| PRD.md §4 | "Firebase — kept intentionally minimal; this is a research tool" |
| PRD.md Phase 8 | "PM decides cloud sync in/out of scope" |
| SDLC Kickoff §6.2 | "No cloud sync, accounts, or any server-side component" — explicitly out |

**Resolution:** Kickoff is authoritative. **Backend is OUT of scope for MVP.** Phase 8 decision is resolved: no backend. Evaluation-study data stays local-only.

### 3.4 Design Tool: Figma vs. No Design Tool

| Source | Position |
|--------|----------|
| PRD.md §4 | "Design: Figma" |
| PRD.md Phase 7 | "built from approved Figma files only" |
| phase-gates.md | "Rebuilt to approved Figma 2026-07-14" |
| SDLC Kickoff §11 | "no visual/design-tool phase — Kiro generates UI directly from spec" |

**Resolution:** This contradiction is moot for existing work (Figma-based UI was already built and delivered). For future UI modifications, the kickoff's approach applies: Kiro generates changes from the UX flow spec (Phase 11). No new Figma rounds required. **Existing design assets in docs/design/*.png remain as reference.**

### 3.5 Agent Count: 9 vs. 13

| Source | Count | Agents |
|--------|-------|--------|
| PRD.md §7 / AGENTS.md | 9 | Data, Model, Optimization, Mobile, Feedback, QA, Research, Security, Documentation |
| SDLC Kickoff §8 | 13 | Adds: Thesis/PM, Research Grounding, Training & Experimentation, Model Evaluation, Evaluation Study & Release Readiness |

**Resolution:** The kickoff expands and refines the agent model. No existing agent is removed. Four new agents are added for thesis-specific rigor. AGENTS.md should be updated to reflect the 13-agent model once Phase 0 is approved.

### 3.6 "No Coding" Rule vs. Existing Implementation

| Source | Position |
|--------|----------|
| SDLC Kickoff §2, Rule | "No training/app/export code until MVP, data pipeline, model architecture, and mobile architecture are formally approved" |
| phase-gates.md | Phases 0–7 already implemented: model trained (95.07%), app running, feedback engine built |

**Resolution:** This is the most significant tension. The kickoff's gating rule was written for a clean-start project; Kumpas already has substantial validated implementation. **Recommended interpretation:**
- The existing code is *de facto* approved work — it already passed the old phase gates.
- The new spec structure formalizes those decisions retroactively (specs note "Implementation exists. Spec formalizes.").
- The "no coding" rule applies going forward to: (a) any new implementation not yet covered by existing work, and (b) any rework of existing components that touch a spec not yet formally approved under the new structure.
- Specifically: benchmarking harness (Phase 13), privacy enforcement verification (Phase 14), test suite (Phase 15), evaluation study (Phase 16), and release build (Phase 19) are all genuinely new work that must be spec-approved first.

---

## 4. Divergences (Different But Not Contradictory)

### 4.1 Evaluation Study Participant Count

- PRD: "40-participant experimental/control pre-test/post-test"
- Kickoff: Does not name a number (defers to Phase 16 design)

**Status:** Not contradictory. Phase 16 will determine final participant count with reasoning.

### 4.2 Risk Register Format

- PRD §11: 4-item "Risks to Watch" list (informal)
- Kickoff §18: Formal risk register with Impact/Mitigation columns (10 items)

**Status:** Kickoff is more comprehensive. The four PRD risks are all captured in the kickoff's register plus six additional risks.

### 4.3 Approval Authority

- PRD: "PM (Cabrera) and Adviser (Abella)"
- Kickoff: "Thesis author (product owner + primary developer)" as primary approver

**Status:** Aligned — the thesis author is the primary developer and product owner. Adviser approval is referenced where applicable ("and adviser, if applicable").

---

## 5. Information in Existing Docs Not Captured in Kickoff

- **FSL-105 format quirks** (Windows backslashes, UTF-8 BOM in labels.csv) — documented in dataset-notes.md, relevant for Phase 4 pipeline implementation.
- **Selected 50-sign list** — already chosen per phase-gates.md, referenced as `selected-50-signs.md` + `training/preprocessing/selected_classes.json`.
- **Experiment results** — 4 experiments logged, best variant "no_face" at 258 features, 95.07% test accuracy.
- **Emulator benchmark results** — inference 0–2ms, 28.6–29.9 FPS (with M1 proxy caveat).
- **Figma design details** — light green theme, dark mode, 5-tab shell, Filipino UI copy.

These are all valuable implementation details that should be referenced when their respective specs are elaborated into design.md documents.

---

## 6. Recommended Next Steps

1. **Author confirms:** Kickoff document is the authoritative planning framework going forward.
2. **Author resolves §3.1:** MVP remains 50 signs (current consensus) — confirm or change.
3. **Author resolves §3.6:** Existing implementation is accepted as approved work; new specs formalize those decisions retroactively.
4. **Author resolves §3.3:** Backend is OUT (kickoff is authoritative) — confirm.
5. After confirmation, proceed to Phase 1: Project Brief (formalizing the problem statement and thesis contribution as a standalone spec document).
6. Existing `docs/PRD.md`, `docs/phase-gates.md`, and `AGENTS.md` are retained as historical reference and updated to reference the new `.kiro/specs/` structure — not deleted.

---

## 7. Repo Layout Verification

| Expected Directory | Exists? | Notes |
|-------------------|---------|-------|
| app/ | ✅ | Flutter project with full UI |
| training/ | ✅ | Preprocessing, augmentation, models, feedback, export |
| benchmarking/ | ✅ | Emulator report exists |
| evaluation/ | ✅ | Empty (pending Phase 16+) |
| docs/ | ✅ | PRD, phase-gates, dataset-notes, design/ |
| .kiro/steering/ | ✅ | Created this session |
| .kiro/specs/ | ✅ | Created this session (21 phase folders) |
