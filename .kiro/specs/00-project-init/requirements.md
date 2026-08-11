# Phase 0 — Project Re-Initialization

## Objective

Establish the Kiro-native planning structure, reconcile existing documentation against the SDLC kickoff document, and confirm the repo layout before any new implementation work proceeds.

## Requirements

WHEN the project transitions to Kiro-based SDLC management,
the system SHALL have `.kiro/steering/` files covering product context, technical context, and repo structure conventions.

WHEN the project transitions to Kiro-based SDLC management,
the system SHALL have `.kiro/specs/` folders for all 20 development phases (00 through 20).

WHEN existing documentation (docs/PRD.md, docs/phase-gates.md, docs/dataset-notes.md, AGENTS.md) is reconciled against the SDLC kickoff,
the system SHALL produce a gap-reconciliation report identifying all contradictions, divergences, and alignment points.

WHEN contradictions are identified,
the system SHALL flag them explicitly rather than silently overwriting existing documents.

WHEN the repo layout is confirmed,
the system SHALL validate that the directory structure matches the conventions in `.kiro/steering/structure.md`.

## Acceptance Criteria

1. `.kiro/steering/product.md`, `.kiro/steering/tech.md`, `.kiro/steering/structure.md` exist and are populated.
2. `.kiro/specs/` contains folders 00 through 20 with at least a placeholder or requirements.md.
3. Gap-reconciliation report is produced and documents all contradictions found.
4. Repo layout (app/, training/, benchmarking/, evaluation/, docs/) is confirmed to exist.
5. No implementation code is written or modified during this phase.

## Status

In progress — delivering now.
