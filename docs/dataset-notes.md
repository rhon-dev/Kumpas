# Dataset Notes — FSL-105 vs PRD Assumptions

Date: 2026-07-05. For adviser (Abella) + PM (Cabrera) review. Affects the methodology chapter.

## What the PRD assumed (§3)

- Team-collected dataset, 50 gesture classes, ~20 signers
- Possibly pre-extracted MediaPipe landmarks
- Gold-standard reference clips flagged
- Consent documentation for the 20 signers required

## What is actually on disk

`Thesis/FSL-105 A dataset for recognizing 105 Filipino sign language videos/`

- **FSL-105**: public dataset (Tupal & Villaverde, Mendeley Data, 2023) — not team-collected
- 105 classes across categories (GREETING, SURVIVAL, COLOR, DRINK, FOOD, …)
- 2130 clips: 1704 train / 426 test (per `train.csv` / `test.csv`), ~20 clips per class
- **Raw video** (`.MOV` inside 379MB `clips.zip`) — no landmarks extracted yet
- No gold-standard flags, no signer IDs in the CSVs, no augmentation applied
- Format quirks: CSV clip paths use Windows backslashes (`clips\17\6.MOV`); `labels.csv` starts with a UTF-8 BOM

## Implications

1. **Consent/privacy (PRD §3 checklist, §9):** per-signer consent collection does not apply to FSL-105 — usage is governed by the dataset's published license (verify exact license terms on the Mendeley record and cite it). RA 10173 consent work still fully applies to the future 40-participant evaluation study and to any clips the team records (e.g., fresh gold-standard clips).
2. **Phase 1 pipeline must start from raw video:** MediaPipe Holistic landmark extraction is part of preprocessing, not already done.
3. **105 → 50 subset decision needed:** PRD scope is 50 signs. The audit script proposes a ranked candidate list (`training/preprocessing/audit_report.md`); PM + FSL Expert make the final pick.
4. **Gold-standard clips do not exist yet:** either the FSL Expert designates one validated reference clip per chosen class from FSL-105, or the team records fresh reference clips (which would require consent + provenance logging per PRD §9).
5. **Signer diversity cannot be audited from metadata:** CSVs carry no signer IDs. If per-signer splits matter for the methodology (they do, for leakage claims), this needs the dataset paper / manual review of the clips.
6. **Methodology chapter wording:** any text claiming original data collection for training must be revised to describe FSL-105 with proper citation; original data collection now applies to the evaluation study (and gold-standard clips, if recorded).

## Dataset location rule

The dataset stays **outside** this repo. Scripts reference it via `--dataset-dir` (default: `../FSL-105 A dataset for recognizing 105 Filipino sign language videos`). `.gitignore` also blocks video/zip files as a second line of defense.
