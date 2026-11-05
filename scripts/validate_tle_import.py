#!/usr/bin/env python3
"""Check imported TLE ground truth against the published run details.

For each archived model run with per-instance output, this recomputes tp/fp/fn
and mean IoU from the imported ground truth at the TLE threshold (0.3) and
compares them with the published `detail` block. A match is strong evidence
that the recovered geometry is the benchmark's expected geometry.

Usage:
    python scripts/validate_tle_import.py --workspace study \
        --bundle "data/tle_raw/TLE-prod [dont-delete]"
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from pathlib import Path

from shapely.geometry import Polygon
from shapely.validation import make_valid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from takeoff_bench.schema import load_gt, load_items  # noqa: E402
from takeoff_bench.scoring import score_polygons  # noqa: E402

THRESHOLD = 0.3


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=ROOT / "study")
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    items = {item.item_id: item for item in load_items(args.workspace)}
    runs = load_runs(args.bundle / "model_runs" / "runs")
    rows = []

    for item_id, item in items.items():
        gt = load_gt(args.workspace, item)
        for run in runs:
            if not run.get("task", "").endswith(item_id):
                continue
            detail = run.get("detail") or {}
            if detail.get("tp") is None or not run.get("output_lines"):
                continue
            prediction = polygons(run["output_lines"])
            result = score_polygons(
                {
                    "instances": [
                        {"points": [[x, y] for x, y in shape.exterior.coords]}
                        for shape in prediction
                    ]
                },
                gt,
                iou_threshold=THRESHOLD,
            )
            ours_miou = result["matched_iou_sum"] / result["n_gt"] if result["n_gt"] else 0.0
            rows.append(
                {
                    "task": item_id,
                    "model": run.get("model", ""),
                    "published_tp": detail["tp"],
                    "published_fp": detail["fp"],
                    "published_fn": detail["fn"],
                    "published_reward": round(float(run.get("reward") or 0), 4),
                    "ours_tp": result["tp"],
                    "ours_fp": result["fp"],
                    "ours_fn": result["fn"],
                    "ours_miou": round(ours_miou, 4),
                    "counts_match": int(
                        (detail["tp"], detail["fp"], detail["fn"])
                        == (result["tp"], result["fp"], result["fn"])
                    ),
                }
            )

    out = args.out or args.workspace / "validation.csv"
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["task"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"{len(rows)} archived runs checked; wrote {out}\n")
    for item_id in items:
        group = [row for row in rows if row["task"] == item_id]
        if not group:
            print(f"  {item_id:34s} no archived runs")
            continue
        matches = sum(row["counts_match"] for row in group)
        diffs = [abs(row["ours_miou"] - row["published_reward"]) for row in group]
        print(
            f"  {item_id:34s} runs={len(group):3d} tp/fp/fn exact={matches:3d} "
            f"median |mean_iou diff|={statistics.median(diffs):.3f}"
        )
    return 0


def load_runs(directory: Path):
    results = []
    for path in sorted(directory.glob("*.json")):
        try:
            payload = json.loads(path.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if isinstance(payload, dict):
            results.extend(payload.get("results") or [])
    return results


def polygons(output_lines):
    result = []
    for line in output_lines:
        ring = line.get("ring")
        if not ring or len(ring) < 3:
            continue
        shape = Polygon([(float(x) / 1000, float(y) / 1000) for x, y in ring])
        if not shape.is_valid:
            shape = make_valid(shape)
        if shape.geom_type != "Polygon":
            parts = [part for part in getattr(shape, "geoms", []) if part.geom_type == "Polygon"]
            if not parts:
                continue
            shape = max(parts, key=lambda part: part.area)
        if not shape.is_empty and shape.area > 0:
            result.append(shape)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
