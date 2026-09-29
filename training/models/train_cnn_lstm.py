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
PROTOCOL_LOG = Path(__file__).resolve().parent / "protocol_experiments_log.json"
from evaluation_protocol import sha256, validate_manifest, manifest_digest

POSE, FACE = 33 * 4, 468 * 3
SEED = 20260705


def load_protocol_data(protocol_dir: Path, drop_face: bool):
    """Load fit and untouched validation only; never open test data."""
    protocol_dir = Path(protocol_dir)
    manifest = json.loads((protocol_dir / "manifest.json").read_text())
    validate_manifest(manifest, protocol_dir.parent)
    X_fit = np.load(protocol_dir / "X_fit.npy", allow_pickle=False)
    y_fit = np.load(protocol_dir / "y_fit.npy", allow_pickle=False)
    X_val = np.load(protocol_dir / "X_val.npy", allow_pickle=False)
    y_val = np.load(protocol_dir / "y_val.npy", allow_pickle=False)
    if X_fit.ndim != 3 or X_val.ndim != 3 or X_fit.shape[1:] != X_val.shape[1:]:
        raise ValueError("fit/validation feature shape mismatch")
    if len(X_fit) != len(y_fit) or len(X_val) != len(y_val) or len(X_val) != manifest["n_validation"]:
        raise ValueError("protocol array length mismatch")
    originals = np.load(protocol_dir.parent / "X_train.npy", mmap_mode="r", allow_pickle=False)
    original_labels = np.load(protocol_dir.parent / "y_train.npy", allow_pickle=False)
    val_indices = [r["index"] for r in manifest["rows"] if r["partition"] == "validation"]
    if not np.array_equal(X_val, originals[val_indices]) or not np.array_equal(y_val, original_labels[val_indices]):
        raise ValueError("validation array differs from original clips")
    if drop_face and X_fit.shape[2] == 1662:
        keep = np.r_[0:POSE, POSE + FACE:1662]
        X_fit, X_val = X_fit[:, :, keep], X_val[:, :, keep]
    label_map = {int(k): v for k, v in json.loads((protocol_dir.parent / "label_map.json").read_text()).items()} if (protocol_dir.parent / "label_map.json").exists() else {int(i): {"label": str(i)} for i in set(original_labels.tolist())}
    return (X_fit, y_fit), (X_val, y_val), label_map, manifest


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
    ap.add_argument("--protocol-dir", type=Path, default=SEQ_DIR / "evaluation-v1")
    ap.add_argument("--drop-face", action="store_true")
    args = ap.parse_args()

    import tensorflow as tf
    from tensorflow.keras import callbacks
    from sklearn.metrics import f1_score

    tf.keras.utils.set_random_seed(SEED)
    conv = tuple(int(x) for x in args.conv.split(","))
    lstm = tuple(int(x) for x in args.lstm.split(","))

    (X_fit, y_fit), (X_val, y_val), label_map, manifest = load_protocol_data(
        args.protocol_dir, args.drop_face)
    t_, f_ = X_fit.shape[1:]
    print(f"fit {X_fit.shape} validation {X_val.shape} (test not opened)")

    model = build_cnn_lstm(t_, f_, len(label_map), conv, lstm,
                           args.dense, args.dropout, args.lr)
    cbs = [
        callbacks.EarlyStopping(patience=15, restore_best_weights=True,
                                monitor="val_accuracy"),
        callbacks.ReduceLROnPlateau(patience=6, factor=0.5, monitor="val_loss"),
    ]
    t0 = time.time()
    hist = model.fit(X_fit, y_fit, validation_data=(X_val, y_val), epochs=args.epochs,
                     batch_size=args.batch, callbacks=cbs, verbose=2)
    train_secs = time.time() - t0
    val_pred = model.predict(X_val, verbose=0).argmax(1)
    val_acc = float((val_pred == y_val).mean())
    val_macro_f1 = float(f1_score(y_val, val_pred, labels=list(range(len(label_map))), average="macro", zero_division=0))
    print(f"RESULT run={args.run_notes} val_acc={val_acc:.4f} val_macro_f1={val_macro_f1:.4f} ({train_secs:.0f}s)")

    run_id = time.strftime("%Y%m%d_%H%M%S") + "_" + args.run_notes.replace(" ", "_")
    MODELS_OUT.mkdir(parents=True, exist_ok=True)
    checkpoint = MODELS_OUT / f"{run_id}.keras"
    if checkpoint.exists():
        raise FileExistsError(checkpoint)
    model.save(checkpoint)
    log = json.loads(PROTOCOL_LOG.read_text()) if PROTOCOL_LOG.exists() else []
    log.append({
        "run_id": run_id, "run_notes": args.run_notes,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "environment": "local tensorflow " + tf.__version__,
        "model_name": model.name, "params": int(model.count_params()),
        "seq_len": int(t_), "features": int(f_),
        "drop_face": args.drop_face,
        "conv_filters": list(conv), "lstm_units": list(lstm),
        "dense": args.dense, "dropout": args.dropout, "lr": args.lr,
        "batch": args.batch, "epochs_run": len(hist.history["loss"]),
        "seed": SEED, "protocol_id": manifest["version"],
        "protocol_sha256": sha256(args.protocol_dir / "manifest.json"),
        "source_sha256": manifest["source_sha256"],
        "checkpoint": str(checkpoint.resolve()), "checkpoint_sha256": sha256(checkpoint),
        "best_val_accuracy": round(val_acc, 4),
        "best_val_macro_f1": round(val_macro_f1, 4),
        "train_seconds": round(train_secs),
    })
    PROTOCOL_LOG.write_text(json.dumps(log, indent=1))
    print(f"logged {run_id} -> {PROTOCOL_LOG.name}; weights -> {checkpoint}")


if __name__ == "__main__":
    main()
