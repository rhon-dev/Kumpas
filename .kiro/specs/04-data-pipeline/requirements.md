# Phase 4 — Data Pipeline Design

## Objective

Specify the preprocessing and augmentation pipeline before implementation, ensuring reproducibility and methodological soundness.

## Requirements

WHEN landmarks are extracted from raw video,
the system SHALL use MediaPipe Holistic to extract hand + pose landmarks (face landmarks optional per architecture decision).

WHEN landmark sequences are normalized,
the system SHALL apply a documented normalization strategy (e.g., wrist-centered, scale-invariant) with justification.

WHEN augmentation is applied,
the system SHALL document each technique used, its parameter range, and its justification for improving generalization without introducing artifacts.

WHEN the train/val/test split is defined,
the system SHALL document the split methodology and acknowledge that subject-independent splits are not possible with FSL-105 metadata.

WHEN the pipeline runs,
the system SHALL log: dataset version, number of clips processed, any extraction failures, augmentation seed, and output sample counts.

## Acceptance Criteria

1. Landmark extraction spec names exact MediaPipe model version and landmark indices used.
2. Normalization strategy is documented with mathematical definition.
3. Each augmentation technique has a justification (not "because it's common").
4. Split methodology is documented with seed for reproducibility.
5. Pipeline produces logged output traceable to a specific dataset version.

## Status

Implementation exists (`training/preprocessing/`, `training/augmentation/`). Spec formalizes the decisions already made.
