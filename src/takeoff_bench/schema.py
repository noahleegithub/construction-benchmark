"""Item metadata and ground-truth loading.

An item is one row in ``items.csv``. A ground-truth file is a small JSON
document holding normalized page coordinates (0..1, origin top-left).
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

OUTPUT_TYPES = (
    "polygons",
    "polylines",
    "segments",
    "points",
    "count",
    "text",
    "quantities",
    "compliance",
)


REQUIRED_COLUMNS = (
    "item_id",
    "family",
    "sheet",
    "page",
    "question",
    "convention",
    "output_type",
    "gt",
)


class ItemError(ValueError):
    """Raised when an item or its ground truth is malformed."""


@dataclass(frozen=True)
class Item:
    item_id: str
    family: str
    sheet: str
    page: int
    question: str
    convention: str
    output_type: str
    gt: str
    notes: str = ""

    def sheet_path(self, workspace: Path) -> Path:
        return _resolve(workspace, self.sheet)

    def gt_path(self, workspace: Path) -> Path:
        return _resolve(workspace, self.gt)


def _resolve(workspace: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (workspace / path)


def load_items(workspace: Path) -> list[Item]:
    """Read and validate ``items.csv`` from a workspace."""
    path = workspace / "items.csv"
    if not path.exists():
        raise ItemError(f"missing {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ItemError(f"items.csv is missing columns: {', '.join(missing)}")
        items = [
            Item(
                item_id=row["item_id"].strip(),
                family=row["family"].strip(),
                sheet=row["sheet"].strip(),
                page=int(row["page"]),
                question=row["question"].strip(),
                convention=row["convention"].strip(),
                output_type=row["output_type"].strip(),
                gt=row["gt"].strip(),
                notes=(row.get("notes") or "").strip(),
            )
            for row in reader
        ]

    seen: set[str] = set()
    for item in items:
        if not item.item_id:
            raise ItemError("empty item_id")
        if item.item_id in seen:
            raise ItemError(f"duplicate item_id: {item.item_id}")
        seen.add(item.item_id)
        if item.output_type not in OUTPUT_TYPES:
            raise ItemError(f"{item.item_id}: unknown output_type {item.output_type!r}")
        if item.page < 1:
            raise ItemError(f"{item.item_id}: page must be >= 1")
        if not item.sheet_path(workspace).exists():
            raise ItemError(f"{item.item_id}: sheet not found: {item.sheet}")
        if not item.gt_path(workspace).exists():
            raise ItemError(f"{item.item_id}: ground truth not found: {item.gt}")
        validate_gt(item.item_id, load_gt(workspace, item), item.output_type)
    return items


def load_gt(workspace: Path, item: Item) -> dict[str, Any]:
    with item.gt_path(workspace).open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_gt(item_id: str, gt: dict[str, Any], output_type: str) -> None:
    """Check the minimal shape required by the scorer."""
    kind = gt.get("type")
    if kind != output_type:
        raise ItemError(f"{item_id}: gt type {kind!r} does not match output_type {output_type!r}")

    if kind in ("polygons", "polylines", "segments"):
        key = {"polygons": "instances", "polylines": "lines", "segments": "segments"}[kind]
        entries = gt.get(key)
        if not isinstance(entries, list) or not entries:
            raise ItemError(f"{item_id}: gt needs a non-empty {key!r} list")
        for entry in entries:
            _check_points(item_id, entry)
    elif kind == "points":
        points = gt.get("points")
        if not isinstance(points, list) or not points:
            raise ItemError(f"{item_id}: gt needs a non-empty 'points' list")
        for point in points:
            if not (isinstance(point, list) and len(point) == 2):
                raise ItemError(f"{item_id}: each point must be [x, y]")
    elif kind == "count":
        if not isinstance(gt.get("value"), (int, float)):
            raise ItemError(f"{item_id}: gt 'value' must be numeric")
    elif kind == "text":
        if not isinstance(gt.get("value"), str):
            raise ItemError(f"{item_id}: gt 'value' must be a string")
    elif kind == "quantities":
        entries = gt.get("items")
        if not isinstance(entries, list) or not entries:
            raise ItemError(f"{item_id}: gt needs a non-empty 'items' list")
        for entry in entries:
            if not isinstance(entry, dict) or "label" not in entry or "value" not in entry:
                raise ItemError(f"{item_id}: each quantity needs 'label' and 'value'")
    elif kind == "compliance":
        criteria = gt.get("criteria")
        if not isinstance(criteria, dict):
            raise ItemError(f"{item_id}: compliance gt needs a 'criteria' object")
        if not isinstance(criteria.get("clear_width_mm"), (int, float)):
            raise ItemError(f"{item_id}: criteria.clear_width_mm must be numeric")
        entries = gt.get("instances")
        if not isinstance(entries, list) or not entries:
            raise ItemError(f"{item_id}: compliance gt needs a non-empty 'instances' list")
        for entry in entries:
            _check_compliance_instance(item_id, entry)


def _check_points(item_id: str, entry: dict[str, Any]) -> None:
    points = entry.get("points") if isinstance(entry, dict) else None
    if not isinstance(points, list) or len(points) < 2:
        raise ItemError(f"{item_id}: each geometry entry needs at least 2 points")
    for point in points:
        if not (isinstance(point, list) and len(point) == 2):
            raise ItemError(f"{item_id}: each point must be [x, y]")


def _check_compliance_instance(item_id: str, entry: Any) -> None:
    if not isinstance(entry, dict):
        raise ItemError(f"{item_id}: each compliance instance must be an object")
    if not isinstance(entry.get("id"), str) or not entry["id"].strip():
        raise ItemError(f"{item_id}: each compliance instance needs a non-empty 'id'")
    if not isinstance(entry.get("measure"), (int, float)):
        raise ItemError(f"{item_id}: compliance instance {entry['id']!r} needs numeric 'measure'")
    if not isinstance(entry.get("unit"), str) or not entry["unit"]:
        raise ItemError(f"{item_id}: compliance instance {entry['id']!r} needs a 'unit'")
    if entry.get("verdict") not in ("pass", "fail", "indeterminate"):
        raise ItemError(
            f"{item_id}: compliance instance {entry['id']!r} has invalid verdict "
            f"{entry.get('verdict')!r}"
        )
    evidence = entry.get("evidence")
    if not isinstance(evidence, dict):
        raise ItemError(f"{item_id}: compliance instance {entry['id']!r} needs 'evidence'")
    if not isinstance(evidence.get("sheet"), str) or not evidence["sheet"]:
        raise ItemError(f"{item_id}: compliance evidence needs a 'sheet'")
    region = evidence.get("region")
    if not (
        isinstance(region, list)
        and len(region) == 4
        and all(isinstance(v, (int, float)) for v in region)
    ):
        raise ItemError(f"{item_id}: compliance evidence needs region [x0,y0,x1,y1]")
