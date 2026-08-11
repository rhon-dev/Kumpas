#!/usr/bin/env python3
"""Extract the 50 gold-standard source clips from clips.zip for expert review.

Copies only the specific video clips used as gold standards into a flat folder
for easy sequential playback during the FSL Expert validation session.

Output: ../kumpas-data/gold_clips_for_review/
  00_GOOD_MORNING_clips_0_13.MOV
  01_GOOD_AFTERNOON_clips_1_4.MOV
  ...

Usage:
    python3 extract_gold_clips_for_review.py
"""

import json
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = REPO_ROOT.parent / "FSL-105 A dataset for recognizing 105 Filipino sign language videos"
DATA_ROOT = REPO_ROOT.parent / "kumpas-data"
MANIFEST = Path(__file__).resolve().parent / "gold_standards_manifest.json"
OUT_DIR = DATA_ROOT / "gold_clips_for_review"


def main():
    manifest = json.loads(MANIFEST.read_text())
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Parse source clip names to get the original video paths
    # clips_0_13.npz -> clips/0/13.MOV
    clip_map = {}
    for idx, entry in sorted(manifest.items(), key=lambda x: int(x[0])):
        src = entry["source_clip"]  # e.g. "clips_0_13.npz"
        parts = src.replace(".npz", "").split("_")  # ["clips", "0", "13"]
        folder_id = parts[1]
        clip_id = parts[2]
        zip_path = f"clips/{folder_id}/{clip_id}.MOV"
        safe_label = entry["label"].replace("'", "").replace(" ", "_")
        out_name = f"{int(idx):02d}_{safe_label}_{src.replace('.npz', '.MOV')}"
        clip_map[zip_path] = OUT_DIR / out_name

    print(f"Extracting {len(clip_map)} gold-standard clips...")

    zip_path_file = DATASET_DIR / "clips.zip"
    if not zip_path_file.exists():
        raise SystemExit(f"clips.zip not found at {zip_path_file}")

    with zipfile.ZipFile(zip_path_file) as z:
        # Normalize zip entries (handle backslashes)
        names = {n.replace("\\", "/"): n for n in z.namelist()}
        extracted = 0
        for rel_path, out_path in clip_map.items():
            if out_path.exists():
                extracted += 1
                continue
            if rel_path in names:
                with z.open(names[rel_path]) as src:
                    out_path.write_bytes(src.read())
                extracted += 1
            else:
                print(f"  WARNING: {rel_path} not found in zip")

    print(f"Done: {extracted}/{len(clip_map)} clips -> {OUT_DIR}")
    print(f"\nPlay all in order:")
    print(f"  open {OUT_DIR}")
    print(f"  (select all, right-click -> Open With -> QuickTime/VLC)")


if __name__ == "__main__":
    main()
