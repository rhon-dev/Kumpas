#!/usr/bin/env python3
"""Freeze a protocol model choice using validation results only."""
import argparse
import json
from pathlib import Path
from evaluation_protocol import sha256, validate_manifest


def freeze_selection(log_path: Path, protocol_dir: Path, output_path: Path) -> dict:
    log_path, protocol_dir, output_path = map(Path, (log_path, protocol_dir, output_path))
    if output_path.exists():
        raise FileExistsError(f"selection is already frozen: {output_path}")
    manifest = json.loads((protocol_dir / "manifest.json").read_text())
    validate_manifest(manifest, protocol_dir.parent)
    digest = sha256(protocol_dir / "manifest.json")
    runs = json.loads(log_path.read_text())
    if not runs:
        raise ValueError("no protocol runs to select")
    valid = []
    for run in runs:
        if run.get("protocol_sha256") != digest:
            continue
        checkpoint = Path(run["checkpoint"])
        if not checkpoint.is_file() or sha256(checkpoint) != run.get("checkpoint_sha256"):
            raise ValueError(f"checkpoint digest mismatch: {run['run_id']}")
        if not all(k in run for k in ("best_val_accuracy", "best_val_macro_f1", "run_id")):
            raise ValueError("validation metric missing")
        valid.append(run)
    if not valid:
        raise ValueError("no runs match this protocol manifest")
    chosen = sorted(valid, key=lambda r: (-r["best_val_accuracy"], -r["best_val_macro_f1"], r["run_id"]))[0]
    record = {k: chosen[k] for k in ("run_id", "checkpoint", "checkpoint_sha256", "protocol_sha256", "best_val_accuracy", "best_val_macro_f1")}
    record["selection_method"] = "highest validation accuracy; macro-F1 then run ID tie break"
    record["test_status"] = "exploratory: existing FSL-105 test was consulted by historical runs"
    output_path.write_text(json.dumps(record, indent=2))
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, default=Path(__file__).resolve().parent / "protocol_experiments_log.json")
    parser.add_argument("--protocol-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(freeze_selection(args.log, args.protocol_dir, args.output), indent=2))
