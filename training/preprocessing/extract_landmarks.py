#!/usr/bin/env python3
"""KUMPAS Phase 1 — MediaPipe Holistic landmark extraction.

Extracts per-frame landmark vectors from the FSL-105 clips of the approved
50-class subset (selected_classes.json). One .npz per clip, written OUTSIDE
the repo (landmark arrays are too large for git; only the extraction log is
committed).

Feature vector per frame (1662 floats):
    pose  33 x (x, y, z, visibility) = 132
    face 468 x (x, y, z)             = 1404
    left hand  21 x (x, y, z)        = 63
    right hand 21 x (x, y, z)        = 63
Missing detections are zero-filled (standard practice; detection rates are
recorded per clip so failures are visible, not hidden).

Optional --brightness F multiplies frames by F before inference (photometric
augmentation happens here in pixel space; geometric augmentation happens later
in landmark space — see augment_landmarks.py). Outputs then go to a
"landmarks_bright_<F>" directory.

Run with the training venv:
    ../.venv/bin/python extract_landmarks.py [--workers 6] [--brightness 0.8]
"""

import argparse
import csv
import json
import multiprocessing as mp
import sys
import time
import zipfile
from pathlib import Path

import cv2
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_DIR = (
    REPO_ROOT.parent / "FSL-105 A dataset for recognizing 105 Filipino sign language videos"
)
DEFAULT_DATA_ROOT = REPO_ROOT.parent / "kumpas-data"
SELECTED_JSON = Path(__file__).resolve().parent / "selected_classes.json"

N_FEATURES = 33 * 4 + 468 * 3 + 21 * 3 + 21 * 3  # 1662

_holistic = None  # per-worker instance


def _init_worker():
    global _holistic
    import mediapipe as mpipe

    _holistic = mpipe.solutions.holistic.Holistic(
        static_image_mode=False,
        model_complexity=1,
        refine_face_landmarks=False,
    )


def frame_vector(results):
    pose = np.zeros(33 * 4, dtype=np.float32)
    face = np.zeros(468 * 3, dtype=np.float32)
    lh = np.zeros(21 * 3, dtype=np.float32)
    rh = np.zeros(21 * 3, dtype=np.float32)
    if results.pose_landmarks:
        pose = np.array(
            [[l.x, l.y, l.z, l.visibility] for l in results.pose_landmarks.landmark],
            dtype=np.float32,
        ).ravel()
    if results.face_landmarks:
        face = np.array(
            [[l.x, l.y, l.z] for l in results.face_landmarks.landmark], dtype=np.float32
        ).ravel()
    if results.left_hand_landmarks:
        lh = np.array(
            [[l.x, l.y, l.z] for l in results.left_hand_landmarks.landmark], dtype=np.float32
        ).ravel()
    if results.right_hand_landmarks:
        rh = np.array(
            [[l.x, l.y, l.z] for l in results.right_hand_landmarks.landmark], dtype=np.float32
        ).ravel()
    detected = (
        results.pose_landmarks is not None,
        results.face_landmarks is not None,
        results.left_hand_landmarks is not None,
        results.right_hand_landmarks is not None,
    )
    return np.concatenate([pose, face, lh, rh]), detected


def extract_clip(job):
    """job: (video_path, out_path, class_id, split, brightness). Returns log row dict."""
    video_path, out_path, class_id, split, brightness = job
    t0 = time.time()
    row = {
        "clip": Path(video_path).parent.name + "/" + Path(video_path).name,
        "class_id": class_id,
        "split": split,
        "status": "ok",
        "frames": 0,
        "fps": 0.0,
        "pose_rate": 0.0,
        "face_rate": 0.0,
        "lh_rate": 0.0,
        "rh_rate": 0.0,
        "any_hand_rate": 0.0,
        "brightness": brightness if brightness else 1.0,
        "seconds": 0.0,
    }
    try:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            row["status"] = "error: cannot open video"
            return row
        row["fps"] = round(cap.get(cv2.CAP_PROP_FPS) or 0.0, 2)
        frames, det_counts = [], np.zeros(4)
        any_hand = 0
        while True:
            ok, bgr = cap.read()
            if not ok:
                break
            if brightness and brightness != 1.0:
                bgr = cv2.convertScaleAbs(bgr, alpha=brightness, beta=0)
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            vec, detected = frame_vector(_holistic.process(rgb))
            frames.append(vec)
            det_counts += np.array(detected, dtype=float)
            any_hand += detected[2] or detected[3]
        cap.release()
        if not frames:
            row["status"] = "error: zero frames decoded"
            return row
        arr = np.stack(frames)  # (T, 1662)
        n = len(frames)
        row.update(
            frames=n,
            pose_rate=round(det_counts[0] / n, 3),
            face_rate=round(det_counts[1] / n, 3),
            lh_rate=round(det_counts[2] / n, 3),
            rh_rate=round(det_counts[3] / n, 3),
            any_hand_rate=round(any_hand / n, 3),
        )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            out_path,
            landmarks=arr,
            class_id=class_id,
            split=split,
            fps=row["fps"],
            brightness=row["brightness"],
            detection_rates=np.array(
                [row["pose_rate"], row["face_rate"], row["lh_rate"], row["rh_rate"]]
            ),
        )
    except Exception as e:  # log, don't kill the pool
        row["status"] = f"error: {e}"
    row["seconds"] = round(time.time() - t0, 1)
    return row


def load_jobs(dataset_dir, clips_dir, out_dir, brightness):
    with open(SELECTED_JSON, encoding="utf-8") as f:
        selected = {c["id"] for c in json.load(f)["selected"]}

    def rows(csv_name, split):
        with open(dataset_dir / csv_name, newline="", encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                cid = int(r["id_label"])
                if cid in selected:
                    rel = r["vid_path"].strip().replace("\\", "/")
                    yield rel, cid, split

    all_rows = list(rows("train.csv", "train")) + list(rows("test.csv", "test"))

    # ensure raw clips are extracted from the zip (once; reused on re-runs)
    needed = [rel for rel, _, _ in all_rows]
    missing = [rel for rel in needed if not (clips_dir / rel).exists()]
    if missing:
        print(f"extracting {len(missing)} clips from clips.zip ...", flush=True)
        with zipfile.ZipFile(dataset_dir / "clips.zip") as z:
            names = {n.replace("\\", "/"): n for n in z.namelist()}
            for rel in missing:
                with z.open(names[rel]) as src:
                    dst = clips_dir / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_bytes(src.read())

    jobs, skipped = [], 0
    for rel, cid, split in all_rows:
        out_path = out_dir / rel.replace("/", "_").replace(".MOV", ".npz")
        if out_path.exists():
            skipped += 1
            continue
        jobs.append((clips_dir / rel, out_path, cid, split, brightness))
    return jobs, skipped, len(all_rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET_DIR)
    ap.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT,
                    help="output root OUTSIDE the repo")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--brightness", type=float, default=None,
                    help="photometric augment: multiply frames by this factor (e.g. 0.8, 1.2)")
    ap.add_argument("--train-only", action="store_true",
                    help="only process train-split clips (used for augmentation passes)")
    args = ap.parse_args()

    sub = "landmarks" if not args.brightness else f"landmarks_bright_{args.brightness}"
    out_dir = args.data_root / sub
    clips_dir = args.data_root / "clips_raw"
    out_dir.mkdir(parents=True, exist_ok=True)

    jobs, skipped, total = load_jobs(args.dataset_dir, clips_dir, out_dir, args.brightness)
    if args.train_only:
        jobs = [j for j in jobs if j[3] == "train"]
    print(f"clips total={total} done_already={skipped} to_process={len(jobs)} -> {out_dir}",
          flush=True)

    log_path = Path(__file__).resolve().parent / (
        "extraction_log.csv" if not args.brightness else f"extraction_log_bright_{args.brightness}.csv"
    )
    fieldnames = ["clip", "class_id", "split", "status", "frames", "fps", "pose_rate",
                  "face_rate", "lh_rate", "rh_rate", "any_hand_rate", "brightness", "seconds"]
    new_log = not log_path.exists()

    t0 = time.time()
    n_err = 0
    with open(log_path, "a", newline="", encoding="utf-8") as logf:
        writer = csv.DictWriter(logf, fieldnames=fieldnames)
        if new_log:
            writer.writeheader()
        if jobs:
            ctx = mp.get_context("spawn")
            with ctx.Pool(args.workers, initializer=_init_worker) as pool:
                for i, row in enumerate(pool.imap_unordered(extract_clip, jobs), 1):
                    writer.writerow(row)
                    logf.flush()
                    if row["status"] != "ok":
                        n_err += 1
                    if i % 50 == 0 or i == len(jobs):
                        rate = i / (time.time() - t0)
                        print(f"[{i}/{len(jobs)}] {rate:.1f} clips/s, errors={n_err}", flush=True)

    print(f"done: processed={len(jobs)} errors={n_err} elapsed={time.time()-t0:.0f}s "
          f"log={log_path.name}", flush=True)
    sys.exit(1 if n_err else 0)


if __name__ == "__main__":
    main()
