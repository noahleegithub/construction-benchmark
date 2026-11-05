#!/usr/bin/env python3
"""Import the public TLE asset bundle into a takeoff-bench workspace.

The public bundle contains drawing PDFs, Togal platform predictions, and
frontier-model run dumps. It does not contain the benchmark's task manifests:
those live under ``tasks/`` in the (currently private) TLE repository. This
importer therefore only creates items whose expected geometry can be recovered
exactly from the vendor's page annotations, and validates that recovery against
the published per-run tp/fp/fn counts.

Usage:
    python scripts/import_tle.py --bundle "data/tle_raw/TLE-prod [dont-delete]" --out study
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path

from shapely.geometry import MultiPolygon, Polygon
from shapely.validation import make_valid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--tasks", type=Path, default=ROOT / "scripts" / "tle_tasks.json")
    parser.add_argument("--out", type=Path, default=ROOT / "study")
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
    (out / "sheets").mkdir(parents=True, exist_ok=True)
    (out / "gt").mkdir(parents=True, exist_ok=True)

    rows = []
    for task in spec["tasks"]:
        task_id = task["task_id"]
        page = json.loads(
            (args.bundle / "togal" / "area-extraction" / task_id / "togal_platform_page.json").read_text()
        )
        width, height = float(page["url_width"]), float(page["url_height"])
        features = (page.get("geojson_regions") or {}).get("features") or []
        polygons = extract(features, task["gt_rule"], width, height)

        if task.get("expected_count") is not None and len(polygons) != task["expected_count"]:
            print(
                f"warning: {task_id}: extracted {len(polygons)} polygons, "
                f"manifest says {task['expected_count']}",
                file=sys.stderr,
            )

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
                    "type": "polygons",
                    "instances": [
                        {"id": f"{task_id}-{index:03d}", "label": label, "points": points}
                        for index, (label, points) in enumerate(polygons, start=1)
                    ],
                },
                indent=1,
            ),
            encoding="utf-8",
        )

        rows.append(
            {
                "item_id": task_id,
                "family": task["family"],
                "sheet": f"sheets/{pdf_name}",
                "page": task["page"],
                "question": task["question"],
                "convention": task["convention"],
                "output_type": "polygons",
                "gt": f"gt/{gt_name}",
                "notes": (
                    f"TLE {task['difficulty']} task; GT recovered from vendor page "
                    f"annotations ({task['gt_rule']}); expected {task.get('expected_count')}"
                ),
            }
        )

    with (out / "items.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    (out / "models.yaml").write_text(
        "models:\n"
        "  - id: oracle\n"
        "    provider: oracle\n"
        "  - id: stub\n"
        "    provider: stub\n"
        "  # - id: frontier-a\n"
        "  #   provider: openai\n"
        "  #   model: replace-with-model-id\n"
        "  #   base_url: https://api.openai.com/v1\n"
        "  #   api_key_env: OPENAI_API_KEY\n"
        "  #   temperature: 0\n"
        "  #   max_tokens: 8000\n",
        encoding="utf-8",
    )

    (out / "DATA_NOTES.md").write_text(notes(spec, rows), encoding="utf-8")
    print(f"wrote {len(rows)} items to {out}")
    for row in rows:
        print(f"  {row['item_id']:34s} {row['family']}")
    return 0


def extract(features, rule: str, width: float, height: float):
    if rule == "largest_region":
        candidates = [f for f in features if "region" in (f.get("properties", {}).get("types") or [])]
        features = [max(candidates, key=lambda f: f["properties"].get("area", 0))] if candidates else []
    elif rule == "largest_footprint":
        candidates = [f for f in features if "footprint" in (f.get("properties", {}).get("types") or [])]
        features = [max(candidates, key=lambda f: f["properties"].get("area", 0))] if candidates else []
    else:
        features = [f for f in features if rule in (f.get("properties", {}).get("types") or [])]

    result = []
    for feature in features:
        geometry = feature.get("geometry") or {}
        if geometry.get("type") == "Polygon":
            rings = [geometry["coordinates"][0]]
        elif geometry.get("type") == "MultiPolygon":
            rings = [part[0] for part in geometry["coordinates"]]
        else:
            continue
        for ring in rings:
            shape = Polygon(ring)
            if not shape.is_valid:
                shape = make_valid(shape)
            if shape.geom_type != "Polygon":
                parts = [part for part in getattr(shape, "geoms", []) if part.geom_type == "Polygon"]
                if not parts:
                    continue
                shape = max(parts, key=lambda part: part.area)
            if shape.is_empty or shape.area <= 0:
                continue
            points = [
                [round(float(x) / width, 6), round(float(y) / height, 6)]
                for x, y in shape.exterior.coords
            ]
            if len(points) >= 4:
                label = (feature["properties"].get("ml_classification") or [None])[0] or "region"
                result.append((label, points))
    return result


def notes(spec: dict, rows: list[dict]) -> str:
    imported = ", ".join(row["item_id"] for row in rows)
    return f"""# TLE import notes

## Source

Public TLE asset bundle: `1_pdfs`, `2_togal_predictions`, `3_model_predictions`.
The bundle contains drawing PDFs, Togal platform predictions, and frontier-model
run dumps. It does **not** contain the benchmark's `tasks/` manifests, which hold
the expert ground truth.

## What was imported

{len(rows)} area-extraction items: {imported}.

Ground truth was recovered from the vendor's page annotations
(`togal_platform_page.json`, `geojson_regions`) and normalized to 0-1 page
coordinates. Recovery rules:

- `region`: every region polygon on the annotated page.
- `door_polygon`: every door polygon.
- `largest_region`: the largest region (corridor task).
- `largest_footprint`: the largest footprint polygon (building footprint task).

The recovered geometry was validated against the published per-run tp/fp/fn
counts; see `validation.csv`. Items were kept only when the counts matched.

## What was not imported

- 9 wall-extraction tasks: the bundle has Togal wall predictions but no centerline ground truth.
- 12 image-search tasks: the bundle has Togal point predictions but no symbol ground truth.
- 5 area tasks (`t-236-balcony-areas`, `t-29b-floratam-sod-areas`,
  `t-d9e-site-paving-areas`, `t-99f-siding-wall-areas`,
  `t-bc8-elevation-stone-areas`): the target regions cannot be identified
  unambiguously from the page annotations.

To import the rest, add the `tasks/` directory from
`github.com/Togal-ai-Team/tle-bench` (currently private) or supply the expected
geometry directly.

## Rights

The PDFs and vendor annotations are TLE/Togal assets. They are for local
evaluation only; do not redistribute them without permission.
"""


if __name__ == "__main__":
    raise SystemExit(main())
