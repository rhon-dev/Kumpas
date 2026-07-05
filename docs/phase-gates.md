# Phase Gates — Live Status

Source of truth for where the project is. Update this file when a gate opens/closes.
Full phase descriptions: `PRD.md` §6.

| Phase | Deliverable | Status | Gate |
|-------|-------------|--------|------|
| 0 | Repo skeleton, AGENTS.md, Flutter scaffold, Colab template, .gitignore | ✅ Delivered 2026-07-05 | ⏳ Awaiting PM structure confirm |
| 1 | Dataset audit script + report | ✅ Audit delivered 2026-07-05 | ⏳ Awaiting PM sign-off on dataset + 50-class pick |
| 1 | Preprocessing pipeline (video → landmarks → fixed-length sequences) | ⬜ Not started (blocked on gate above) | — |
| 1 | Augmentation pipeline | ⬜ Not started | — |
| 2 | CNN-LSTM baseline + experiment log | ⬜ Blocked on Phase 1 gate | Adviser reviews confusion matrix |
| 3 | Eval report (acc/prec/rec/F1, per-gesture errors) | ⬜ | ≥90% accuracy or plan to reach it |
| 4 | Quantized .tflite + real-device latency/FPS report | ⬜ | <150ms, 24–30 FPS on real hardware |
| 5 | Flutter skeleton: camera → MediaPipe → inference e2e | ⬜ | Runs on real device at target FPS |
| 6 | Corrective feedback engine | ⬜ | FSL Expert reviews 5 sample corrections |
| 7 | Practice UI from approved Figma | ⬜ | Matches Figma, no ad-hoc screens |
| 8 | Session logging / optional backend | ⬜ | PM decides cloud sync in/out of scope |
| 9 | Integration testing (50 gestures × signers) | ⬜ | No open blocking bugs |
| 10 | Field benchmarking (3 conditions × devices) | ⬜ | — |
| 11 | 40-participant study tooling | ⬜ | — |
| 12 | Stats/analysis scripts | ⬜ | — |
| 13 | Final polish, reproducibility notes, defense readiness | ⬜ | — |

## Open decisions

1. **PM confirm repo structure** (Phase 0 gate).
2. **50-class subset**: audit report proposes ranked candidates (`training/preprocessing/audit_report.md`); PM + FSL Expert approve final list.
3. **Dataset provenance**: PRD assumed team-collected data; actual dataset is public FSL-105. See `dataset-notes.md` — needs adviser acknowledgment for methodology chapter.
4. **Gold-standard clips**: FSL-105 has no gold-standard flags. Decide: FSL Expert picks one reference clip per chosen class, or team records fresh gold-standard clips.
