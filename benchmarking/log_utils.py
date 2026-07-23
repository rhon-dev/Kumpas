#!/usr/bin/env python3
"""Benchmarking history log utilities.

Provides atomic append, load, and schema validation for
benchmarking/benchmark_history.json.
"""

import json
import tempfile
import time
from pathlib import Path
from typing import Any

HISTORY_PATH = Path(__file__).resolve().parent / "benchmark_history.json"

REQUIRED_FIELDS = {"timestamp", "benchmark_type", "model_version", "device", "condition", "results"}
VALID_TYPES = {"accuracy", "latency", "fps"}
VALID_CONDITIONS = {"optimal", "low_light", "cluttered", "n/a"}


def load_history() -> list[dict]:
    """Load the benchmark history file. Returns empty list if missing."""
    if not HISTORY_PATH.exists():
        return []
    return json.loads(HISTORY_PATH.read_text())


def validate_entry(entry: dict) -> bool:
    """Check that an entry has all required fields and valid values."""
    missing = REQUIRED_FIELDS - set(entry.keys())
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
    if entry["benchmark_type"] not in VALID_TYPES:
        raise ValueError(
            f"Invalid benchmark_type '{entry['benchmark_type']}'; "
            f"must be one of {VALID_TYPES}"
        )
    if entry["condition"] not in VALID_CONDITIONS:
        raise ValueError(
            f"Invalid condition '{entry['condition']}'; "
            f"must be one of {VALID_CONDITIONS}"
        )
    if not isinstance(entry["results"], dict):
        raise ValueError("'results' must be a dict")
    return True


def append_entry(entry: dict) -> None:
    """Validate and atomically append an entry to the history log."""
    validate_entry(entry)
    history = load_history()
    history.append(entry)
    # Atomic write: write to temp file then replace
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", dir=HISTORY_PATH.parent, delete=False
    )
    try:
        json.dump(history, tmp, indent=1)
        tmp.close()
        Path(tmp.name).replace(HISTORY_PATH)
    except Exception:
        Path(tmp.name).unlink(missing_ok=True)
        raise


def make_timestamp() -> str:
    """ISO-format timestamp for log entries."""
    return time.strftime("%Y-%m-%dT%H:%M:%S")
