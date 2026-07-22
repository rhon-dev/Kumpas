# Phase 3 — Dataset Audit: Design Document

## 1. Dataset Identity

| Property | Value |
|----------|-------|
| Name | FSL-105: A dataset for recognizing 105 Filipino sign language videos |
| Authors | Isaiah Jassen Lizaso Tupal, Cabatuan K. Melvin |
| Publisher | Mendeley Data (Elsevier) |
| Year | 2023 |
| Source | Public repository (Mendeley Data) |
| License | CC BY 4.0 (Mendeley Data default for open datasets; depositors select from CC-0/CC-BY/CC-BY-NC) |
| Citation | Tupal, I.J.L. & Villaverde, J. (2023). "The Video Filipino Sign Language Sign Database of Introductory 105 FSL Signs." SSRN 4476867 / Mendeley Data. |
| Local path | `../FSL-105 A dataset for recognizing 105 Filipino sign language videos/` (OUTSIDE repo) |

**License implication:** Under CC BY 4.0, derived artifacts (extracted landmark sequences, augmented data) can be used and redistributed with attribution. The landmark cache is a derived work and can be shared. Proper citation in the thesis and any distributed artifact is required.

---

## 2. Dataset Composition

| Metric | Value |
|--------|-------|
| Total classes | 105 |
| Total clips | 2,130 |
| Train split | 1,704 (80%) |
| Test split | 426 (20%) |
| Clips per class (median) | 20 |
| Clips per class (range) | 18–22 |
| Categories | 10 (GREETING, SURVIVAL, NUMBER, CALENDAR, DAYS, FAMILY, RELATIONSHIPS, COLOR, FOOD, DRINK) |
| Format | Raw .MOV video in `clips.zip` (379 MB) |
| Metadata files | `labels.csv`, `train.csv`, `test.csv` |
| Format quirks | Windows backslashes in CSV paths; UTF-8 BOM in labels.csv |

### Category Distribution

| Category | Classes | Clips |
|----------|---------|-------|
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

---

## 3. Class Balance Assessment

**Finding: The dataset is remarkably well-balanced.**

- Median clips per class: 20
- No class deviates more than ±25% from the median
- Classes flagged as imbalanced: **0**
- Classes with zero test samples: **0**

### Imbalance Mitigation Strategy (Applied)

Despite the natural balance, the small absolute sample count (16–17 train samples per class) motivated augmentation to improve generalization:

- **Augmentation factor:** 3× (813 → 3,252 train samples)
- **Technique:** Geometric transforms in landmark space (rotation ±10–15°, scale 0.90–1.10, shift ±0.10)
- **Rationale:** Small per-class sample count (~16 train) risks overfitting despite balanced distribution. Landmark-space augmentation avoids pixel-domain artifacts while expanding the effective training set.
- **Class weighting:** Not applied (unnecessary given balanced distribution). Would be reconsidered if per-class accuracy post-training showed systematic failures.

---

## 4. 50-Sign Subset Selection

### Selection Criteria

1. **Pedagogical frequency:** Signs that appear in multiple beginner FSL curricula were prioritized.
2. **Category coverage:** All 10 categories represented (no category dropped entirely).
3. **Discriminability:** Signs with high mutual confusability excluded (e.g., SIX–TEN share similar handshapes; month/weekday names are initialized signs that are mutually hard to distinguish).
4. **Practical value:** Signs useful for everyday communication prioritized over specialized vocabulary.

### Referenced Curricula

- Benilde SDEAS — FSL Learning Program (essential vocabulary)
- Kakamay Movement — Basic Sign Language
- Deaf Association of Quezon Province — FSL
- Inquirer — Basic phrases for learning FSL (2019)
- PageOne — 10 Basic FSL signs for everyday use

### Final 50-Sign List (Approved 2026-07-05)

| Category | Signs Kept | Count |
|----------|-----------|-------|
| GREETING | GOOD MORNING, GOOD AFTERNOON, GOOD EVENING, HELLO, HOW ARE YOU, IM FINE, NICE TO MEET YOU, THANK YOU, YOURE WELCOME, SEE YOU TOMORROW | 10/10 |
| SURVIVAL | UNDERSTAND, DON'T UNDERSTAND, KNOW, DON'T KNOW, NO, YES, WRONG, CORRECT, SLOW, FAST | 10/10 |
| NUMBER | ONE, TWO, THREE, FOUR, FIVE | 5/10 |
| DAYS | TODAY, TOMORROW, YESTERDAY | 3/10 |
| FAMILY | FATHER, MOTHER, SON, DAUGHTER, GRANDFATHER, GRANDMOTHER | 6/10 |
| RELATIONSHIPS | BOY, GIRL, MAN, WOMAN, DEAF, HARD OF HEARING | 6/10 |
| COLOR | BLUE, RED, BLACK, WHITE | 4/13 |
| FOOD | BREAD, EGG, CHICKEN, RICE | 4/10 |
| DRINK | HOT, COLD | 2/10 |

**Total: 50 signs across 9 categories**

### Exclusion Rationale

- **CALENDAR (all 12 months):** Low everyday frequency for beginner practice; initialized/abbreviated signs that are mutually confusable.
- **DAYS (weekday names):** Same reasoning as months.
- **NUMBER (SIX–TEN):** Similar handshape articulation → high confusion risk, lower pedagogical priority than ONE–FIVE.
- **PARENTS:** Compound of FATHER + MOTHER — overlaps both individual classes.
- **Remaining FAMILY/RELATIONSHIPS/COLOR/FOOD/DRINK:** Lower frequency in beginner curricula or less distinct signing.

Machine-readable list: `training/preprocessing/selected_classes.json`

---

## 5. Signer Diversity Assessment

**Finding: Cannot be audited from available metadata.**

- CSVs contain no signer ID field
- The dataset paper describes multiple signers but does not publish per-clip signer attribution
- Implication for methodology: **Subject-independent train/test splits cannot be verified** from metadata alone

### Methodological Response

1. The train/test split from FSL-105's original CSVs is preserved as-is (never reshuffled).
2. The thesis methodology chapter must acknowledge that signer-independent evaluation is not verifiable and frame accuracy claims accordingly.
3. If a reviewer challenges this, manual review of clips (visual identification) could partially address it, but this is not feasible for the automated pipeline.
4. The 95.07% test accuracy may be inflated if the same signers appear in both splits — this is a known limitation, not a hidden one.

---

## 6. Data Integrity Verification

All integrity checks passed:

| Check | Result |
|-------|--------|
| Duplicate clip paths in CSVs | 0 |
| CSV rows missing from zip | 0 |
| Zip videos not referenced by CSVs | 0 |
| Label/category metadata mismatches | 0 |
| Classes with zero test samples | 0 |

### Known Quality Issues

- **2 clips with weak hand visibility (<10% any-hand detection rate):**
  - `5/3.MOV` (class 5 "IM FINE") — 9.9% hand detection
  - `5/4.MOV` (class 5 "IM FINE") — 9.1% hand detection
- These clips are included in training (not dropped) as the model should handle edge cases. Flagged for error analysis if class 5 shows poor performance.

---

## 7. Gold-Standard References

**Finding: FSL-105 contains no gold-standard flagged clips.**

### Resolution (Implemented)

The feedback engine's gold-standard builder (`training/feedback/build_gold_standards.py`) selects reference clips by:
1. Extracting landmarks from all clips per class
2. Computing per-clip quality metrics (hand detection rate, landmark stability)
3. Selecting the highest-quality clip as the gold-standard reference

This is an automated heuristic, not FSL Expert validation. **FSL Expert linguistic validation of gold-standard references remains pending** (Phase 6/10 gate in phase-gates.md).

---

## 8. Privacy & Licensing Summary

| Concern | Status |
|---------|--------|
| Dataset license | CC BY 4.0 (Mendeley Data) — use with attribution permitted |
| Per-signer consent for FSL-105 | Not applicable (public dataset, governed by published license) |
| RA 10173 applicability to FSL-105 | Not applicable (no PII in distributed dataset) |
| RA 10173 for evaluation study | FULLY APPLIES — separate consent required for any participant data |
| Derived artifacts (landmarks) redistributable? | Yes, under CC BY with citation |
| Raw video committed to repo? | NO — .gitignore enforces; outside repo by convention |

---

## 9. Audit Tooling

| Script | Purpose | Output |
|--------|---------|--------|
| `training/preprocessing/dataset_audit.py` | Read-only integrity + balance audit | `audit_report.json`, `audit_report.md` |
| `training/preprocessing/extract_landmarks.py` | MediaPipe Holistic landmark extraction | Landmark arrays (outside repo) |
| `training/preprocessing/build_sequences.py` | Fixed-length sequence builder | Sequence arrays |
| `training/augmentation/augment_landmarks.py` | Seeded geometric augmentation | Augmented arrays + `augment_log.json` |

All scripts are stdlib-only for the audit; MediaPipe required only for extraction.

---

## 10. Open Items for Later Phases

1. **FSL Expert validation of gold-standard clips** — required before Phase 10 (Feedback Logic) gate can close.
2. **Real-device accuracy validation** — emulator results (95.07%) must be confirmed on actual hardware (Phase 18).
3. **Signer diversity study** — if a reviewer challenges the train/test split independence, manual clip review may be needed. Document as a known limitation.

---

## Status

**Complete.** All acceptance criteria from `requirements.md` met:
- ✅ Audit report exists with class distribution data
- ✅ Imbalance mitigation strategy chosen and justified (augmentation, not class weighting — justified by balanced distribution + small sample count)
- ✅ License terms documented with citation (CC BY 4.0, Mendeley Data)
- ✅ Signer-diversity limitation acknowledged with methodological impact
- ✅ 50-sign subset listed with selection rationale and referenced curricula
