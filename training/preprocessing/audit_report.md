# FSL-105 Dataset Audit Report

Generated 2026-07-05 by `dataset_audit.py` (read-only; no video extracted).
Dataset: `/Users/ahronjanl.rafaelahron.0804icloudcom/Documents/Thesis/FSL-105 A dataset for recognizing 105 Filipino sign language videos`

## Summary

- Classes: **105**
- Clips: **2130** (1704 train / 426 test, 20% test)
- Video files in `clips.zip`: **2130**
- Median clips per class: **20**
- Integrity: **CLEAN**

## Integrity checks

- Duplicate clip paths in CSVs: 0
- CSV rows whose clip is missing from zip: 0
- Zip videos not referenced by any CSV: 0
- Rows whose label/category disagree with labels.csv: 0
- Classes with zero test samples: 0

## Class balance (PRD §11 risk #1)

Classes outside ±25% of the median (20 clips): **0**

## Category distribution

| Category | Classes | Clips |
|---|---|---|
| COLOR | 13 | 261 |
| CALENDAR | 12 | 247 |
| SURVIVAL | 10 | 208 |
| GREETING | 10 | 206 |
| DRINK | 10 | 203 |
| NUMBER | 10 | 202 |
| RELATIONSHIPS | 10 | 202 |
| DAYS | 10 | 201 |
| FAMILY | 10 | 200 |
| FOOD | 10 | 200 |

## Candidate 50-class subset — PENDING PM + FSL EXPERT APPROVAL

Ranked by sample count with round-robin category coverage. This is a proposal
only; the final 50-sign list is a Phase 1 gate decision (`docs/phase-gates.md`).

| # | ID | Label | Category | Train | Test |
|---|---|---|---|---|---|
| 1 | 73 | GREEN | COLOR | 17 | 4 |
| 2 | 37 | AUGUST | CALENDAR | 17 | 5 |
| 3 | 17 | CORRECT | SURVIVAL | 17 | 5 |
| 4 | 2 | GOOD EVENING | GREETING | 17 | 5 |
| 5 | 96 | COLD | DRINK | 17 | 4 |
| 6 | 26 | SEVEN | NUMBER | 17 | 4 |
| 7 | 62 | BOY | RELATIONSHIPS | 17 | 4 |
| 8 | 50 | TOMORROW | DAYS | 17 | 4 |
| 9 | 58 | UNCLE | FAMILY | 17 | 4 |
| 10 | 85 | BREAD | FOOD | 16 | 4 |
| 11 | 72 | BLUE | COLOR | 16 | 4 |
| 12 | 40 | NOVEMBER | CALENDAR | 17 | 5 |
| 13 | 11 | DON’T UNDERSTAND | SURVIVAL | 17 | 4 |
| 14 | 6 | NICE TO MEET YOU | GREETING | 17 | 5 |
| 15 | 97 | JUICE | DRINK | 17 | 4 |
| 16 | 27 | EIGHT | NUMBER | 17 | 4 |
| 17 | 66 | DEAF | RELATIONSHIPS | 17 | 4 |
| 18 | 42 | MONDAY | DAYS | 16 | 4 |
| 19 | 60 | COUSIN | FAMILY | 17 | 4 |
| 20 | 86 | EGG | FOOD | 16 | 4 |
| 21 | 74 | RED | COLOR | 16 | 4 |
| 22 | 41 | DECEMBER | CALENDAR | 17 | 5 |
| 23 | 12 | KNOW | SURVIVAL | 17 | 4 |
| 24 | 1 | GOOD AFTERNOON | GREETING | 17 | 4 |
| 25 | 103 | SUGAR | DRINK | 17 | 4 |
| 26 | 20 | ONE | NUMBER | 16 | 4 |
| 27 | 63 | GIRL | RELATIONSHIPS | 16 | 4 |
| 28 | 43 | TUESDAY | DAYS | 16 | 4 |
| 29 | 52 | FATHER | FAMILY | 16 | 4 |
| 30 | 87 | FISH | FOOD | 16 | 4 |
| 31 | 75 | BROWN | COLOR | 16 | 4 |
| 32 | 34 | MAY | CALENDAR | 17 | 4 |
| 33 | 14 | NO | SURVIVAL | 17 | 4 |
| 34 | 4 | HOW ARE YOU | GREETING | 17 | 4 |
| 35 | 95 | HOT | DRINK | 16 | 4 |
| 36 | 21 | TWO | NUMBER | 16 | 4 |
| 37 | 64 | MAN | RELATIONSHIPS | 16 | 4 |
| 38 | 44 | WEDNESDAY | DAYS | 16 | 4 |
| 39 | 53 | MOTHER | FAMILY | 16 | 4 |
| 40 | 88 | MEAT | FOOD | 16 | 4 |
| 41 | 76 | BLACK | COLOR | 16 | 4 |
| 42 | 36 | JULY | CALENDAR | 17 | 4 |
| 43 | 16 | WRONG | SURVIVAL | 17 | 4 |
| 44 | 0 | GOOD MORNING | GREETING | 16 | 4 |
| 45 | 98 | MILK | DRINK | 16 | 4 |
| 46 | 22 | THREE | NUMBER | 16 | 4 |
| 47 | 65 | WOMAN | RELATIONSHIPS | 16 | 4 |
| 48 | 45 | THURSDAY | DAYS | 16 | 4 |
| 49 | 54 | SON | FAMILY | 16 | 4 |
| 50 | 89 | CHICKEN | FOOD | 16 | 4 |

## Not verified by this audit

- **Signer identity/diversity** — CSVs carry no signer IDs; per-signer splits and
  leakage analysis need the FSL-105 paper or manual clip review.
- **Gold-standard reference clips** — none flagged in FSL-105; selection/validation
  by the FSL Expert is an open Phase 1 decision.
- **Landmark extraction completeness** — extraction has not run yet; raw video only.
- **Visual quality per clip** (lighting, framing, occlusion) — requires viewing clips.

Full per-class table: `audit_report.json`.
