"""Prediction overlays.

Aggregate scores hide the failure modes that matter: half-thickness offsets,
merged rooms, missed instances. This module puts ground truth and prediction
on the same page image: ground truth solid, prediction dashed.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from .render import render_pdf_page
from .schema import Item, load_gt
from .scoring import score_item

GT_COLOR = (0, 145, 70)
PRED_COLOR = (200, 35, 35)
TEXT_COLOR = (20, 20, 20)


def find_run(runs_path: Path, item_id: str, model_id: str, repeat: int) -> dict[str, Any]:
    found = None
    with runs_path.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            if (
                record.get("item_id") == item_id
                and record.get("model_id") == model_id
                and int(record.get("repeat", 0)) == repeat
                and record.get("error") is None
            ):
                found = record
    if found is None:
        raise ValueError(f"no successful run for {item_id} / {model_id} / r{repeat}")
    return found


def draw_overlay(
    workspace: Path,
    item: Item,
    run: dict[str, Any],
    out_path: Path,
    *,
    dpi: int = 150,
    max_side: int = 2400,
) -> dict[str, Any]:
    png, _ = render_pdf_page(
        item.sheet_path(workspace), item.page, dpi=dpi, max_side=max_side
    )
    scratch = out_path.with_suffix(".base.png")
    scratch.write_bytes(png)
    image = Image.open(scratch).convert("RGB")
    scratch.unlink(missing_ok=True)

    draw = ImageDraw.Draw(image)
    width = max(3, round(max(image.size) / 450))
    gt = load_gt(workspace, item)
    prediction = run.get("parsed")
    result = score_item(prediction, gt) if prediction else None

    _draw_geometry(draw, gt, image.size, GT_COLOR, width + 2, dashed=False)
    if prediction:
        _draw_geometry(draw, prediction, image.size, PRED_COLOR, width, dashed=True)

    header_size = max(18, round(image.width / 55))
    legend_size = max(13, round(image.width / 95))
    header_height = round(header_size * 2.3)
    header = f"{item.item_id} | {run['model_id']} | score {_fmt(result)}"
    draw.rectangle((0, 0, image.width, header_height), fill=(255, 255, 255))
    draw.text((12, round(header_size * 0.4)), header, fill=TEXT_COLOR, font=_font(header_size))

    box_y = header_height + 6
    box = header_size * 0.8
    draw.rectangle((12, box_y, 12 + box, box_y + box), outline=GT_COLOR, width=3)
    draw.text((12 + box + 8, box_y), "ground truth", fill=TEXT_COLOR, font=_font(legend_size))
    second_x = 12 + box + 8 + round(legend_size * 8)
    draw.rectangle((second_x, box_y, second_x + box, box_y + box), outline=PRED_COLOR, width=3)
    draw.text((second_x + box + 8, box_y), "prediction (dashed)", fill=TEXT_COLOR, font=_font(legend_size))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path)
    return result or {}


def _draw_geometry(draw, payload: dict[str, Any], size, color, width: int, dashed: bool) -> None:
    width_px, height_px = size
    kind = payload.get("type")

    if kind == "polygons":
        for entry in payload.get("instances", []):
            points = _scaled(entry.get("points", []), width_px, height_px)
            if len(points) >= 3:
                _line(draw, points + [points[0]], color, width, dashed)
    elif kind == "polylines":
        for entry in payload.get("lines", []):
            points = _scaled(entry.get("points", []), width_px, height_px)
            if len(points) >= 2:
                _line(draw, points, color, width, dashed)
    elif kind == "points":
        radius = max(4, width * 2)
        for x, y in _scaled(payload.get("points", []), width_px, height_px):
            draw.ellipse(
                (x - radius, y - radius, x + radius, y + radius),
                outline=color,
                width=width,
            )


def _line(draw, points, color, width: int, dashed: bool) -> None:
    if not dashed:
        draw.line(points, fill=color, width=width, joint="curve")
        return
    dash, gap = max(8, width * 4), max(5, width * 2)
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        length = math.hypot(x2 - x1, y2 - y1)
        if length == 0:
            continue
        steps = int(length // (dash + gap)) + 1
        for step in range(steps):
            start = step * (dash + gap) / length
            end = min(1.0, (step * (dash + gap) + dash) / length)
            if start >= 1.0:
                break
            draw.line(
                [
                    (x1 + (x2 - x1) * start, y1 + (y2 - y1) * start),
                    (x1 + (x2 - x1) * end, y1 + (y2 - y1) * end),
                ],
                fill=color,
                width=width,
            )


def _scaled(points, width_px: int, height_px: int) -> list[tuple[float, float]]:
    return [(float(x) * width_px, float(y) * height_px) for x, y in points]


def _font(size: int):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _fmt(result: dict[str, Any] | None) -> str:
    return f"{result['score']:.3f}" if result else "n/a"
