# Phase Gates — Live Status

Source of truth for where the project is. Update this file when a gate opens/closes.
Full phase descriptions: `PRD.md` §6.

| Phase | Deliverable | Status | Gate |
|-------|-------------|--------|------|
| 0 | Repo skeleton, AGENTS.md, Flutter scaffold, Colab template, .gitignore | ✅ Delivered 2026-07-05 | ⏳ Awaiting PM structure confirm |
| 1 | Dataset audit script + report | ✅ Audit delivered 2026-07-05 | ⏳ Awaiting PM sign-off on dataset + 50-class pick |
| 1 | Preprocessing pipeline (video → landmarks → fixed-length sequences) | ✅ Delivered 2026-07-05 (1016 clips, 0 errors — `training/preprocessing/preprocessing_report.md`) | — |
| 1 | Augmentation pipeline | ✅ Delivered 2026-07-05 (813 → 3252 train samples, seeded + logged) | — |
| 2 | CNN-LSTM baseline + experiment log | ✅ 4 experiments logged 2026-07-05 (`training/models/experiments_log.json`); best: `no_face`, 258 features | ⏳ Adviser reviews confusion matrix |
| 3 | Eval report (acc/prec/rec/F1, per-gesture errors) | ✅ **Test accuracy 95.07% — gate PASS** (`training/models/reports/20260705_194813_no_face_eval.md`) | ✅ ≥90% met |
| 4 | Quantized .tflite + real-device latency/FPS report | 🔄 Exports ready (dynamic 0.32MB / f16 0.57MB, M1 <1ms informational) — needs real Android device measurement | <150ms, 24–30 FPS on real hardware |
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
2. ~~**50-class subset**~~ — RESOLVED 2026-07-05: everyday-usage pick approved by team, see `selected-50-signs.md` + `training/preprocessing/selected_classes.json`. FSL Expert may still swap individual signs before training.
3. **Dataset provenance**: PRD assumed team-collected data; actual dataset is public FSL-105. See `dataset-notes.md` — needs adviser acknowledgment for methodology chapter.
4. **Gold-standard clips**: FSL-105 has no gold-standard flags. Decide: FSL Expert picks one reference clip per chosen class, or team records fresh gold-standard clips.
