#!/usr/bin/env python3
"""Import recoverable TLE wall-extraction tasks as segment items.

The public bundle does not contain the benchmark task manifests. This importer
uses the vendor page annotations (``geojson_walls``) as a recoverable, but
approximate, ground truth. It records the expected count from the published
task page and the recovered count so the count gap is never hidden.

Usage:
    python scripts/import_tle_walls.py \
        --bundle "data/tle_raw/TLE-prod [dont-delete]" \
        --out study/walls
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--tasks", type=Path, default=ROOT / "scripts" / "tle_wall_tasks.json")
    parser.add_argument("--out", type=Path, default=ROOT / "study" / "walls")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    spec = json.loads(args.tasks.read_text(encoding="utf-8"))
    index = json.loads((args.bundle / "pdfs" / "index.json").read_text(encoding="utf-8"))
    pdf_by_task = {
        asset["task_id"]: args.bundle / "pdfs" / asset["path"]
        for asset in index.get("assets", [])
    }

    out = args.out
    if (out / "items.csv").exists() and not args.force:
        raise SystemExit(f"{out}/items.csv exists; pass --force to rebuild")
    for directory in ("sheets", "gt"):
        (out / directory).mkdir(parents=True, exist_ok=True)

    rows = []
    validation = []
    for task in spec["tasks"]:
        task_id = task["task_id"]
        page_path = (
            args.bundle
            / "togal"
            / "wall-extraction"
            / task_id
            / "togal_platform_page.json"
        )
        if not page_path.exists():
            print(f"skip {task_id}: page annotation not found", file=sys.stderr)
            continue
        page = json.loads(page_path.read_text(encoding="utf-8"))
        width, height = float(page["url_width"]), float(page["url_height"])
        features = (page.get("geojson_walls") or {}).get("features") or []
        segments = extract_segments(features, task["predicate"], width, height)

        pdf_source = pdf_by_task.get(task_id)
        if pdf_source is None or not pdf_source.exists():
            print(f"skip {task_id}: PDF not found", file=sys.stderr)
            continue
        pdf_name = f"{task_id}.pdf"
        shutil.copy2(pdf_source, out / "sheets" / pdf_name)

        gt_name = f"{task_id}.json"
        (out / "gt" / gt_name).write_text(
            json.dumps(
                {
                    "type": "segments",
                    "segments": [
                        {
                            "id": f"{task_id}-{index:04d}",
                            "label": label,
                            "points": points,
                        }
                        for index, (label, points) in enumerate(segments, start=1)
                    ],
                },
                indent=1,
            ),
            encoding="utf-8",
        )

        expected = task.get("expected_count")
        status = "exact" if expected == len(segments) else "approximate"
        rows.append(
            {
                "item_id": task_id,
                "family": "wall-extraction",
                "sheet": f"sheets/{pdf_name}",
                "page": 1,
                "question": task["question"],
                "convention": task["convention"],
                "output_type": "segments",
                "gt": f"gt/{gt_name}",
                "notes": (
                    f"TLE {task.get('difficulty', '')} task; recovered from vendor "
                    f"page annotations (geojson_walls/{task['predicate']}); "
                    f"expected {expected}, recovered {len(segments)} ({status})"
                ),
            }
        )
        validation.append(
            {
                "item_id": task_id,
                "expected_count": expected,
                "recovered_count": len(segments),
                "status": status,
            }
        )

    if not rows:
        raise SystemExit("no wall tasks imported")

    with (out / "items.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with (out / "validation.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(validation[0]))
        writer.writeheader()
        writer.writerows(validation)

    (out / "models.yaml").write_text(
        "models:\n"
        "  - id: oracle\n"
        "    provider: oracle\n"
        "  - id: stub\n"
        "    provider: stub\n",
        encoding="utf-8",
    )
    (out / "DATA_NOTES.md").write_text(notes(rows, validation), encoding="utf-8")
    print(f"wrote {len(rows)} wall items to {out}")
    for row in rows:
        print(f"  {row['item_id']:32s} {row['notes']}")
    return 0


def extract_segments(features, predicate: str, width: float, height: float):
    result = []
    for feature in features:
        properties = feature.get("properties") or {}
        if predicate not in (properties.get("types") or []):
            continue
        geometry = feature.get("geometry") or {}
        if geometry.get("type") != "LineString":
            continue
        coordinates = geometry.get("coordinates") or []
        if len(coordinates) < 2:
            continue
        label = (properties.get("ml_classification") or ["wall"])[0] or "wall"
        for first, second in zip(coordinates, coordinates[1:]):
            points = [
                [round(float(first[0]) / width, 6), round(float(first[1]) / height, 6)],
                [round(float(second[0]) / width, 6), round(float(second[1]) / height, 6)],
            ]
            if points[0] != points[1]:
                result.append((label, points))
    return result


def notes(rows, validation) -> str:
    approximate = [row for row in validation if row["status"] != "exact"]
    exact = [row for row in validation if row["status"] == "exact"]
    lines = [
        "# TLE wall-centerline import notes",
        "",
        "## Source",
        "",
        "Public TLE asset bundle, `togal/wall-extraction/<task>/togal_platform_page.json`, "
        "`geojson_walls` features. PDFs are copied from `pdfs/index.json`.",
        "",
        "## Ground truth status",
        "",
        f"- {len(rows)} items imported.",
        f"- {len(exact)} item(s) match the published expected count exactly: "
        + (", ".join(row["item_id"] for row in exact) or "none"),
        f"- {len(approximate)} item(s) are approximate and are marked in `items.csv`: "
        + (", ".join(row["item_id"] for row in approximate) or "none"),
        "",
        "The public bundle does not contain the TLE `tasks/` manifests that hold the "
        "exact `wall_segments.segments` answer key. The recovered page annotations "
        "are usable for model comparison within this workspace, but they are not an "
        "official TLE reproduction. Do not report these counts as official TLE scores.",
        "",
        "## Scoring",
        "",
        "Segments are matched one-to-one when both endpoints fall within 0.012 of "
        "the page (12 units on the TLE 1000x1000 grid). Score is segment F1.",
        "",
        "## Excluded",
        "",
        "- `t-door-centerlines`: no page geometry in the bundle (expected 848).",
        "- `t-wall-perimeter-painters`: perimeter linework, not a wall centerline task.",
        "- `t-14b-wall-centerlines`: no page annotation in this bundle.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
