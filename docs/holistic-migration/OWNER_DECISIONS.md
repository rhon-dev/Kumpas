# Holistic migration owner decisions

## November 16, 2026 — Face features required; Phase 3 paused

The owner stated: **“all requires face”** and **“we can continue on phase 3 but dont continue it yet.”**

Treat facial information as a required classifier input for all 50 approved gestures. This is an owner scope requirement, not an independently completed linguistic validation.

The existing `hm153-v1` classifier contract deliberately excludes face. Its software acceptance, tests and source-bound historical data receipts remain valid for that historical candidate, but do not satisfy the new face-inclusive requirement. Do not promote its tensors, admission or tooling acceptance as approval for the required final model.

Before dependent data preparation or fitting, define and approve a new exact face-inclusive contract: indices/cardinality, coordinate channels, normalization, presence/missingness rules, feature dimensions and version, detector binding, and shared offline/live behavior. Test that contract. Do not invent a new feature count or silently append an undefined face block.

Raw extraction already retains face observations. Their compatibility and provenance must be verified before any future reuse; this decision does not order re-extraction or authorize changing historical arrays or receipts.

**Phase 3 is paused.** Do not start new extraction, dataset rebuilding, real-source training/evaluation, camera capture, phone work or model activation under this decision. The owner's statement allows a future phase continuation but expressly withholds execution now.

## November 16, 2026 — GitHub checkpoint

The owner requested committing the current migration work to GitHub under their `rhon-dev` identity, without AI co-author attribution. Publish the isolated `holistic-migration` branch only. Do not merge into `main`, rewrite existing history, publish datasets/model binaries or start the paused phase. Preserve historical reports and their provenance rather than rewriting them as newly verified face-inclusive work.
