# Phase 6 — Training & Experimentation Plan

## Objective

Define how training is run, tracked, and reproduced — ensuring every reported number is traceable.

## Requirements

WHEN an experiment is run,
the system SHALL log: architecture variant, hyperparameters, dataset version, augmentation config, split seed, training duration, and resulting val/test accuracy.

WHEN hyperparameter search is performed,
the system SHALL document the search scope (which hyperparameters varied, what ranges) and compute budget.

WHEN a training run completes,
the system SHALL save the model checkpoint alongside a config snapshot that allows exact reproduction.

WHEN stopping criteria are defined,
the system SHALL specify: early stopping patience, minimum delta, and the metric monitored.

## Acceptance Criteria

1. Experiment log format is defined and consistently used across all runs.
2. Every reported accuracy number is traceable to a specific checkpoint + config.
3. Hyperparameter search scope is bounded and documented.
4. Reproducibility checklist exists: seed, dataset version, config, environment.

## Status

Implementation exists (`training/models/experiments_log.json`, 4 experiments logged). Spec formalizes.
