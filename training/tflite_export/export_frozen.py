#!/usr/bin/env python3
"""Export a validation-frozen checkpoint without replacing the deployed model."""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "models"))
from evaluation_protocol import sha256, validate_manifest


def verified_selection(freeze_path: Path, protocol_dir: Path) -> dict:
    freeze_path, protocol_dir = Path(freeze_path), Path(protocol_dir)
    freeze = json.loads(freeze_path.read_text())
    manifest_path = protocol_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    validate_manifest(manifest, protocol_dir.parent)
    if freeze.get("protocol_sha256") != sha256(manifest_path):
        raise ValueError("protocol manifest digest mismatch")
    if not all(freeze.get(k) for k in ("run_id", "checkpoint", "checkpoint_sha256",
                                         "selection_method", "test_status")):
        raise ValueError("incomplete frozen selection")
    checkpoint = Path(freeze["checkpoint"])
    if not checkpoint.is_file() or sha256(checkpoint) != freeze["checkpoint_sha256"]:
        raise ValueError("checkpoint digest mismatch")
    return freeze


def export_candidate(freeze_path: Path, protocol_dir: Path, output_dir: Path,
                     label_map_path: Path) -> dict:
    """Produce a builtins-only candidate with source and validation provenance.

    Deliberately does not install the candidate into Android; deployment needs
    an explicit decision after evaluation and device compatibility checks.
    """
    import numpy as np
    import tensorflow as tf
    from tensorflow.python.framework.convert_to_constants import convert_variables_to_constants_v2

    protocol_dir, output_dir, label_map_path = map(Path, (protocol_dir, output_dir, label_map_path))
    freeze = verified_selection(freeze_path, protocol_dir)
    if not re.fullmatch(r"[A-Za-z0-9_-]+", freeze["run_id"]):
        raise ValueError("invalid frozen run ID")
    source_labels = protocol_dir.parent / "label_map.json"
    if sha256(label_map_path) != sha256(source_labels):
        raise ValueError("label map digest mismatch")
    if output_dir.exists():
        raise FileExistsError(output_dir)
    label_map = json.loads(source_labels.read_text())
    checkpoint = Path(freeze["checkpoint"])
    model = tf.keras.models.load_model(checkpoint)
    if model.input_shape[1:] != (30, 258) or model.output_shape[-1] != len(label_map):
        raise ValueError("model shape does not match the 30x258 feature spec/label map")

    # Freeze the checkpoint's actual variables with a fixed batch dimension.
    # The direct Keras builtins-only converter cannot lower the LSTM TensorList.
    fn = tf.function(lambda x: model(x, training=False))
    concrete = fn.get_concrete_function(tf.TensorSpec([1, 30, 258], tf.float32))
    frozen = convert_variables_to_constants_v2(concrete)
    converter = tf.lite.TFLiteConverter.from_concrete_functions([frozen])
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS]
    blob = converter.convert()
    interpreter = tf.lite.Interpreter(model_content=blob)
    interpreter.allocate_tensors()
    input_detail, output_detail = interpreter.get_input_details()[0], interpreter.get_output_details()[0]
    if tuple(input_detail["shape"]) != (1, 30, 258) or tuple(output_detail["shape"]) != (1, len(label_map)):
        raise ValueError("TFLite export shape mismatch")
    X_val = np.load(protocol_dir / "X_val.npy", allow_pickle=False)
    if X_val.shape[2] == 1662:
        X_val = X_val[:, :, np.r_[0:132, 1536:1662]]
    if X_val.ndim != 3 or X_val.shape[1:] != (30, 258) or len(X_val) == 0:
        raise ValueError("validation array shape mismatch")
    expected = model.predict(X_val, verbose=0)
    actual = []
    for sample in X_val:
        interpreter.set_tensor(input_detail["index"], sample[None].astype(np.float32))
        interpreter.invoke()
        actual.append(interpreter.get_tensor(output_detail["index"])[0])
    actual = np.asarray(actual)
    disagreements = int(np.count_nonzero(expected.argmax(axis=1) != actual.argmax(axis=1)))
    max_abs = float(np.max(np.abs(expected - actual)))

    filename = f"kumpas_50sign_{freeze['run_id']}_builtins_dynamic.tflite"
    output_dir.mkdir(parents=True, exist_ok=False)
    artifact = output_dir / filename
    artifact.write_bytes(blob)
    result = {
        "run_id": freeze["run_id"],
        "checkpoint_sha256": freeze["checkpoint_sha256"],
        "selection_sha256": sha256(Path(freeze_path)),
        "protocol_sha256": freeze["protocol_sha256"],
        "label_map_sha256": sha256(label_map_path),
        "tflite_sha256": sha256(artifact),
        "filename": filename,
        "converter": "frozen concrete function, fixed batch=1, TFLITE_BUILTINS, dynamic range",
        "tensorflow_version": tf.__version__,
        "validation_samples": len(X_val),
        "validation_prediction_disagreements": disagreements,
        "validation_probability_max_abs": max_abs,
        "deployed": False,
        "test_status": freeze["test_status"],
    }
    (output_dir / "provenance.json").write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--protocol-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--label-map", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(export_candidate(args.freeze, args.protocol_dir,
                                      args.output_dir, args.label_map), indent=2))
