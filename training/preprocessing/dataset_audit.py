#!/usr/bin/env python3
"""KUMPAS Phase 1 — FSL-105 dataset audit.

Read-only audit of the FSL-105 dataset (labels.csv, train.csv, test.csv,
clips.zip). Verifies integrity without extracting any video, reports class
balance and category coverage, and proposes a candidate 50-class subset for
PM + FSL Expert approval.

Stdlib only (runs on system Python 3.9, no pip installs).

Usage:
    python3 dataset_audit.py [--dataset-dir PATH] [--out-dir PATH] [--top-n 50]
"""

import argparse
import csv
import json
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_DIR = (
    REPO_ROOT.parent / "FSL-105 A dataset for recognizing 105 Filipino sign language videos"
)
DEFAULT_OUT_DIR = Path(__file__).resolve().parent

# Flag classes whose total sample count deviates from the median by more than
# this fraction (PRD §11 risk #1: class imbalance).
IMBALANCE_TOLERANCE = 0.25


def norm_path(p):
    """Normalize CSV clip paths (Windows backslashes) to zip-style forward slashes."""
    return p.strip().replace("\\", "/")


def read_csv_rows(path):
    # labels.csv ships with a UTF-8 BOM; utf-8-sig handles both cases.
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_split(path, split_name):
    rows = read_csv_rows(path)
    clips = []
    for i, row in enumerate(rows):
        clips.append(
            {
                "path": norm_path(row["vid_path"]),
                "class_id": int(row["id_label"]),
                "label": row["label"].strip(),
                "category": row["category"].strip(),
                "split": split_name,
                "row": i + 2,  # 1-based, +1 for header — for error messages
            }
        )
    return clips


def audit(dataset_dir, top_n):
    labels = read_csv_rows(dataset_dir / "labels.csv")
    classes = {
        int(r["id"]): {"label": r["label"].strip(), "category": r["category"].strip()}
        for r in labels
    }

    clips = load_split(dataset_dir / "train.csv", "train") + load_split(
        dataset_dir / "test.csv", "test"
    )

    with zipfile.ZipFile(dataset_dir / "clips.zip") as z:
        zip_entries = {norm_path(n) for n in z.namelist() if not n.endswith("/")}

    # --- integrity checks ---
    csv_paths = [c["path"] for c in clips]
    dup_paths = sorted(p for p, n in Counter(csv_paths).items() if n > 1)
    csv_path_set = set(csv_paths)
    missing_in_zip = sorted(csv_path_set - zip_entries)
    orphans_in_zip = sorted(zip_entries - csv_path_set)
    label_mismatches = [
        c for c in clips
        if c["class_id"] not in classes
        or classes[c["class_id"]]["label"] != c["label"]
        or classes[c["class_id"]]["category"] != c["category"]
    ]

    # --- per-class stats ---
    per_class = {}
    for cid, meta in sorted(classes.items()):
        cls_clips = [c for c in clips if c["class_id"] == cid]
        per_class[cid] = {
            "label": meta["label"],
            "category": meta["category"],
            "train": sum(1 for c in cls_clips if c["split"] == "train"),
            "test": sum(1 for c in cls_clips if c["split"] == "test"),
            "total": len(cls_clips),
        }

    totals = sorted(v["total"] for v in per_class.values())
    median_total = totals[len(totals) // 2]
    lo = median_total * (1 - IMBALANCE_TOLERANCE)
    hi = median_total * (1 + IMBALANCE_TOLERANCE)
    imbalanced = {
        cid: v for cid, v in per_class.items() if not (lo <= v["total"] <= hi)
    }
    no_test = {cid: v for cid, v in per_class.items() if v["test"] == 0}

    category_dist = defaultdict(lambda: {"classes": 0, "clips": 0})
    for v in per_class.values():
        category_dist[v["category"]]["classes"] += 1
        category_dist[v["category"]]["clips"] += v["total"]

    # --- candidate subset: rank by sample count, keep category spread ---
    # Round-robin across categories in descending-count order, so the proposal
    # keeps every category represented instead of letting one dominate.
    by_category = defaultdict(list)
    for cid, v in sorted(per_class.items(), key=lambda kv: (-kv[1]["total"], kv[0])):
        by_category[v["category"]].append(cid)
    candidates = []
    while len(candidates) < top_n and any(by_category.values()):
        for cat in sorted(by_category, key=lambda c: -category_dist[c]["clips"]):
            if by_category[cat] and len(candidates) < top_n:
                candidates.append(by_category[cat].pop(0))

    return {
        "audit_date": date.today().isoformat(),
        "dataset_dir": str(dataset_dir),
        "num_classes": len(classes),
        "num_clips": len(clips),
        "num_train": sum(1 for c in clips if c["split"] == "train"),
        "num_test": sum(1 for c in clips if c["split"] == "test"),
        "zip_video_entries": len(zip_entries),
        "duplicate_csv_paths": dup_paths,
        "csv_clips_missing_in_zip": missing_in_zip,
        "zip_clips_not_in_csv": orphans_in_zip,
        "label_metadata_mismatches": [
            {"path": c["path"], "split": c["split"], "row": c["row"]}
            for c in label_mismatches
        ],
        "median_clips_per_class": median_total,
        "imbalance_tolerance": IMBALANCE_TOLERANCE,
        "imbalanced_classes": imbalanced,
        "classes_without_test_samples": no_test,
        "category_distribution": dict(category_dist),
        "per_class": per_class,
        "candidate_subset": candidates,
    }


def write_markdown(r, out_path, top_n):
    ok = not (
        r["duplicate_csv_paths"]
        or r["csv_clips_missing_in_zip"]
        or r["label_metadata_mismatches"]
        or r["classes_without_test_samples"]
    )
    pc = r["per_class"]

    lines = [
        "# FSL-105 Dataset Audit Report",
        "",
        f"Generated {r['audit_date']} by `dataset_audit.py` (read-only; no video extracted).",
        f"Dataset: `{r['dataset_dir']}`",
        "",
        "## Summary",
        "",
        f"- Classes: **{r['num_classes']}**",
        f"- Clips: **{r['num_clips']}** ({r['num_train']} train / {r['num_test']} test, "
        f"{r['num_test'] / r['num_clips']:.0%} test)",
        f"- Video files in `clips.zip`: **{r['zip_video_entries']}**",
        f"- Median clips per class: **{r['median_clips_per_class']}**",
        f"- Integrity: **{'CLEAN' if ok else 'ISSUES FOUND — see below'}**",
        "",
        "## Integrity checks",
        "",
        f"- Duplicate clip paths in CSVs: {len(r['duplicate_csv_paths'])}",
        f"- CSV rows whose clip is missing from zip: {len(r['csv_clips_missing_in_zip'])}",
        f"- Zip videos not referenced by any CSV: {len(r['zip_clips_not_in_csv'])}",
        f"- Rows whose label/category disagree with labels.csv: {len(r['label_metadata_mismatches'])}",
        f"- Classes with zero test samples: {len(r['classes_without_test_samples'])}",
    ]
    for key, title in [
        ("duplicate_csv_paths", "Duplicate paths"),
        ("csv_clips_missing_in_zip", "Missing from zip"),
        ("zip_clips_not_in_csv", "Unreferenced zip videos"),
    ]:
        if r[key]:
            lines += ["", f"### {title}", ""] + [f"- `{p}`" for p in r[key][:20]]
            if len(r[key]) > 20:
                lines.append(f"- … and {len(r[key]) - 20} more (see JSON report)")

    lines += [
        "",
        "## Class balance (PRD §11 risk #1)",
        "",
        f"Classes outside ±{r['imbalance_tolerance']:.0%} of the median "
        f"({r['median_clips_per_class']} clips): **{len(r['imbalanced_classes'])}**",
    ]
    if r["imbalanced_classes"]:
        lines += ["", "| ID | Label | Category | Train | Test | Total |", "|---|---|---|---|---|---|"]
        for cid, v in sorted(r["imbalanced_classes"].items(), key=lambda kv: kv[1]["total"]):
            lines.append(
                f"| {cid} | {v['label']} | {v['category']} | {v['train']} | {v['test']} | {v['total']} |"
            )

    lines += ["", "## Category distribution", "", "| Category | Classes | Clips |", "|---|---|---|"]
    for cat, d in sorted(r["category_distribution"].items(), key=lambda kv: -kv[1]["clips"]):
        lines.append(f"| {cat} | {d['classes']} | {d['clips']} |")

    lines += [
        "",
        f"## Candidate {top_n}-class subset — PENDING PM + FSL EXPERT APPROVAL",
        "",
        "Ranked by sample count with round-robin category coverage. This is a proposal",
        "only; the final 50-sign list is a Phase 1 gate decision (`docs/phase-gates.md`).",
        "",
        "| # | ID | Label | Category | Train | Test |",
        "|---|---|---|---|---|---|",
    ]
    for i, cid in enumerate(r["candidate_subset"], 1):
        v = pc[cid]
        lines.append(
            f"| {i} | {cid} | {v['label']} | {v['category']} | {v['train']} | {v['test']} |"
        )

    lines += [
        "",
        "## Not verified by this audit",
        "",
        "- **Signer identity/diversity** — CSVs carry no signer IDs; per-signer splits and",
        "  leakage analysis need the FSL-105 paper or manual clip review.",
        "- **Gold-standard reference clips** — none flagged in FSL-105; selection/validation",
        "  by the FSL Expert is an open Phase 1 decision.",
        "- **Landmark extraction completeness** — extraction has not run yet; raw video only.",
        "- **Visual quality per clip** (lighting, framing, occlusion) — requires viewing clips.",
        "",
        "Full per-class table: `audit_report.json`.",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET_DIR)
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    ap.add_argument("--top-n", type=int, default=50)
    args = ap.parse_args()

    for name in ("labels.csv", "train.csv", "test.csv", "clips.zip"):
        if not (args.dataset_dir / name).exists():
            sys.exit(f"error: {args.dataset_dir / name} not found")

    r = audit(args.dataset_dir, args.top_n)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.out_dir / "audit_report.json"
    md_path = args.out_dir / "audit_report.md"
    json_path.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(r, md_path, args.top_n)

    print(f"classes={r['num_classes']} clips={r['num_clips']} "
          f"(train={r['num_train']} test={r['num_test']}) zip={r['zip_video_entries']}")
    print(f"missing_in_zip={len(r['csv_clips_missing_in_zip'])} "
          f"orphans={len(r['zip_clips_not_in_csv'])} dups={len(r['duplicate_csv_paths'])} "
          f"imbalanced={len(r['imbalanced_classes'])}")
    print(f"wrote {md_path} and {json_path}")


if __name__ == "__main__":
    main()
