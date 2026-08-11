# Phase 3 — Dataset Audit

## Objective

Formally characterize FSL-105 before any pipeline design decisions are made, documenting class distribution, gaps, licensing, and implications for the training methodology.

## Requirements

WHEN the dataset audit is performed,
the system SHALL document: total clip count, class count, clips per class distribution, train/test split ratio, and format details.

WHEN class imbalance is assessed,
the system SHALL produce a distribution histogram and flag any class with fewer than 15 training samples as at-risk.

WHEN licensing is verified,
the system SHALL document the exact license terms from the Mendeley record and confirm whether derived artifacts (landmark caches) can be redistributed.

WHEN signer diversity is assessed,
the system SHALL note that FSL-105 CSVs carry no signer IDs and document the implication for subject-independent split claims.

WHEN the 50-sign subset is selected,
the system SHALL document selection criteria (frequency, category coverage, pedagogical relevance) and the final list.

## Acceptance Criteria

1. Audit report exists with class distribution data.
2. Imbalance mitigation strategy is chosen and justified (not defaulted silently).
3. License terms are documented with citation.
4. Signer-diversity limitation is acknowledged with its methodological impact.
5. 50-sign subset is listed with selection rationale.

## Status

Largely complete — existing `docs/dataset-notes.md` and `training/preprocessing/` cover most of this. Needs formalization into this spec structure.
