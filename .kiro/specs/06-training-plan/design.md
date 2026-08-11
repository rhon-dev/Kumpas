# Phase 6 — Training & Experimentation Plan: Design

## 1. Training Methodology

### Environment
- **Primary:** Local M1 Mac (TensorFlow 2.19.0, Keras 3.10)
- **Alternative:** Google Colab GPU (notebook reproduces any experiment from same seed/data)
- **Deviation from PRD:** Training ran locally instead of Colab default — documented; notebook exists for reproduction

### Stopping Criteria
- EarlyStopping: patience=15, monitor=val_accuracy, restore_best_weights=True
- ReduceLROnPlateau: patience=6, factor=0.5, monitor=val_loss
- Max epochs: 120 (never reached; early stopping triggers at 63–106 epochs)

### Compute Budget
- Per-experiment: 2–7 minutes locally (166–426 seconds)
- Total experiments: 4 (deliberate — small search space with clear signal)
- No GPU cluster required for this dataset scale

---

## 2. Experiment Tracking

### Format: `training/models/experiments_log.json`

Every run appends a JSON entry with:
```json
{
  "run_id": "<timestamp>_<notes>",
  "run_notes": "<what changed>",
  "timestamp": "...",
  "environment": "...",
  "model_name": "...",
  "params": 270834,
  "seq_len": 30,
  "features": 258,
  "augmented": true,
  "drop_face": true,
  "conv_filters": [64, 128],
  "lstm_units": [128, 64],
  "dense": 128,
  "dropout": 0.4,
  "lr": 0.001,
  "batch": 32,
  "epochs_run": 63,
  "seed": 20260705,
  "best_val_accuracy": 1.0,
  "test_accuracy": 0.9507,
  "train_seconds": 166
}
```

**Rule:** Never silently overwrite — always append.

---

## 3. Hyperparameter Search Scope

| Hyperparameter | Searched Values | Best |
|---------------|----------------|------|
| Features | 1662 (full), 258 (no_face) | 258 |
| LSTM units | [128, 64], [256, 128] | [128, 64] |
| Dropout | 0.4, 0.5 | 0.4 |
| Conv filters | [64, 128] (fixed) | [64, 128] |
| Learning rate | 0.001 (fixed) | 0.001 |
| Batch size | 32 (fixed) | 32 |

**Search strategy:** Manual/factorial on the two dimensions with highest expected impact (feature set, model width). Not grid/random search — justified by small dataset where overfitting is the primary risk, not underfitting.

---

## 4. Reproducibility Checklist

| Requirement | Mechanism |
|-------------|-----------|
| Random seed | 20260705 (TF global seed set before model build) |
| Dataset version | FSL-105 (2130 clips), 50-sign subset |
| Split | Preserved from FSL-105 train.csv/test.csv |
| Augmentation seed | 20260705, factor=3 |
| Environment | TensorFlow 2.19.0, numpy 2.1, mediapipe 0.10.14 |
| Config snapshot | Logged per-run in experiments_log.json |
| Weights | Saved to ../kumpas-data/models/<run_id>.keras |

---

## Status

**Complete.** Formalizes methodology already executed. 4 experiments logged, best model selected.
