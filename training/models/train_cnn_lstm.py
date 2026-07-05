#!/usr/bin/env python3
"""KUMPAS Phase 2 — CNN-LSTM training (local run).

Same architecture and data as notebooks/kumpas_cnn_lstm_training.ipynb; run
locally on the M1 because the team opted for local baseline iteration
(documented deviation from the PRD's Colab default — the notebook reproduces
any experiment on Colab GPU from the same seed and data).

Every run appends to training/models/experiments_log.json (PRD §7: no silent
overwriting). Model weights go OUTSIDE the repo (../kumpas-data/models/);
metrics, reports, and the confusion matrix are committed.

The TF venv lives OUTSIDE the repo and outside iCloud-synced paths (iCloud
stalls on site-packages' thousands of files): ~/.kumpas-venvs/tf
(tensorflow==2.19.0 / keras 3.10 / numpy 2.1).

Usage:
    ~/.kumpas-venvs/tf/bin/python train_cnn_lstm.py --run-notes baseline
    ~/.kumpas-venvs/tf/bin/python train_cnn_lstm.py --drop-face --run-notes no_face
    ~/.kumpas-venvs/tf/bin/python train_cnn_lstm.py --conv 64,128 --lstm 256,128 --run-notes wider
"""

import argparse
import json
import time
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
SEQ_DIR = REPO_ROOT.parent / "kumpas-data" / "sequences"
MODELS_OUT = REPO_ROOT.parent / "kumpas-data" / "models"
LOG_PATH = Path(__file__).resolve().parent / "experiments_log.json"
REPORTS_DIR = Path(__file__).resolve().parent / "reports"

POSE, FACE = 33 * 4, 468 * 3
SEED = 20260705


def load_data(use_augmented, drop_face):
    X_train = np.load(SEQ_DIR / ("X_train_aug.npy" if use_augmented else "X_train.npy"))
    y_train = np.load(SEQ_DIR / ("y_train_aug.npy" if use_augmented else "y_train.npy"))
    X_test = np.load(SEQ_DIR / "X_test.npy")
    y_test = np.load(SEQ_DIR / "y_test.npy")
    label_map = {int(k): v for k, v in
                 json.loads((SEQ_DIR / "label_map.json").read_text()).items()}
    if drop_face and X_train.shape[2] == 1662:
        keep = np.r_[0:POSE, POSE + FACE:1662]
        X_train, X_test = X_train[:, :, keep], X_test[:, :, keep]
    return X_train, y_train, X_test, y_test, label_map


def build_cnn_lstm(t, f, n_classes, conv_filters, lstm_units, dense=128,
                   dropout=0.4, lr=1e-3):
    import tensorflow as tf
    from tensorflow.keras import layers, models

    m = models.Sequential(
        name=f"cnnlstm_c{'-'.join(map(str, conv_filters))}_l{'-'.join(map(str, lstm_units))}")
    m.add(layers.Input((t, f)))
    for i, filt in enumerate(conv_filters):
        m.add(layers.Conv1D(filt, 3, padding="same", activation="relu"))
        m.add(layers.BatchNormalization())
        if i == len(conv_filters) - 1:
            m.add(layers.MaxPooling1D(2))
    for i, units in enumerate(lstm_units):
        m.add(layers.LSTM(units, return_sequences=(i < len(lstm_units) - 1)))
        m.add(layers.Dropout(dropout))
    m.add(layers.Dense(dense, activation="relu"))
    m.add(layers.Dropout(dropout))
    m.add(layers.Dense(n_classes, activation="softmax"))
    # metrics= must be keyword: Keras 3's third positional arg is loss_weights
    m.compile(tf.keras.optimizers.Adam(lr), "sparse_categorical_crossentropy",
              metrics=["accuracy"])
    return m


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-notes", required=True,
                    help="what changed vs previous experiment (goes in the log)")
    ap.add_argument("--conv", default="64,128")
    ap.add_argument("--lstm", default="128,64")
    ap.add_argument("--dense", type=int, default=128)
    ap.add_argument("--dropout", type=float, default=0.4)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--epochs", type=int, default=120)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--no-augmented", action="store_true")
    ap.add_argument("--drop-face", action="store_true")
    args = ap.parse_args()

    import tensorflow as tf
    from tensorflow.keras import callbacks

    tf.keras.utils.set_random_seed(SEED)
    conv = tuple(int(x) for x in args.conv.split(","))
    lstm = tuple(int(x) for x in args.lstm.split(","))

    X_train, y_train, X_test, y_test, label_map = load_data(
        not args.no_augmented, args.drop_face)
    class_names = [label_map[i]["label"] for i in range(len(label_map))]
    t_, f_ = X_train.shape[1], X_train.shape[2]
    print(f"train {X_train.shape} test {X_test.shape}")

    model = build_cnn_lstm(t_, f_, len(class_names), conv, lstm,
                           args.dense, args.dropout, args.lr)
    cbs = [
        callbacks.EarlyStopping(patience=15, restore_best_weights=True,
                                monitor="val_accuracy"),
        callbacks.ReduceLROnPlateau(patience=6, factor=0.5, monitor="val_loss"),
    ]
    t0 = time.time()
    hist = model.fit(X_train, y_train, validation_split=0.15, epochs=args.epochs,
                     batch_size=args.batch, callbacks=cbs, verbose=2)
    train_secs = time.time() - t0
    val_acc = float(max(hist.history["val_accuracy"]))

    y_pred = model.predict(X_test, verbose=0).argmax(1)
    test_acc = float((y_pred == y_test).mean())
    print(f"RESULT run={args.run_notes} val_acc={val_acc:.4f} "
          f"test_acc={test_acc:.4f} ({train_secs:.0f}s)")

    run_id = time.strftime("%Y%m%d_%H%M%S") + "_" + args.run_notes.replace(" ", "_")
    MODELS_OUT.mkdir(parents=True, exist_ok=True)
    model.save(MODELS_OUT / f"{run_id}.keras")
    REPORTS_DIR.mkdir(exist_ok=True)
    np.save(REPORTS_DIR / f"{run_id}_y_pred.npy", y_pred)

    log = json.loads(LOG_PATH.read_text()) if LOG_PATH.exists() else []
    log.append({
        "run_id": run_id, "run_notes": args.run_notes,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "environment": "local M1 (tensorflow " + tf.__version__ + ")",
        "model_name": model.name, "params": int(model.count_params()),
        "seq_len": int(t_), "features": int(f_),
        "augmented": not args.no_augmented, "drop_face": args.drop_face,
        "conv_filters": list(conv), "lstm_units": list(lstm),
        "dense": args.dense, "dropout": args.dropout, "lr": args.lr,
        "batch": args.batch, "epochs_run": len(hist.history["loss"]),
        "seed": SEED,
        "best_val_accuracy": round(val_acc, 4),
        "test_accuracy": round(test_acc, 4),
        "train_seconds": round(train_secs),
    })
    LOG_PATH.write_text(json.dumps(log, indent=1))
    print(f"logged {run_id} -> {LOG_PATH.name}; weights -> kumpas-data/models/")


if __name__ == "__main__":
    main()
