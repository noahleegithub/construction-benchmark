#!/usr/bin/env python3
"""Build a per-door crop grid comparing TLE door-threshold predictions to GT."""

from __future__ import annotations

import argparse
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from takeoff_bench.render import render_pdf_page
from takeoff_bench.schema import Item, load_gt, load_items
from takeoff_bench.scoring import score_item

COLS = 8
CROP_W = 200
CROP_H = 150
LABEL_H = 24
PAD = 8


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--item", default="t-4f1-door-threshold-areas")
    parser.add_argument("--runs", default="runs.jsonl")
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--max-side", type=int, default=4000)
    args = parser.parse_args()

    items = {item.item_id: item for item in load_items(args.workspace)}
    item = items[args.item]
    gt = load_gt(args.workspace, item)
    png, _ = render_pdf_page(
        item.sheet_path(args.workspace), item.page, dpi=args.dpi, max_side=args.max_side
    )
    page = Image.open(io.BytesIO(png)).convert("RGB")
    out_dir = args.workspace / "overlays"
    out_dir.mkdir(exist_ok=True)

    for model_id in _models(args.workspace / args.runs):
        run = _find_run(args.workspace / args.runs, item.item_id, model_id)
        if run is None or not run.get("parsed"):
            print(f"skip {model_id}: no parsed prediction")
            continue
        prediction = run["parsed"]
        result = score_item(prediction, gt)
        grid = _grid(page, gt, prediction, result)
        out = out_dir / f"door-grid__{model_id}.png"
        grid.save(out)
        print(f"wrote {out} ({result['score']:.3f})")
    return 0


def _models(runs_path: Path) -> list[str]:
    seen = []
    for line in runs_path.open(encoding="utf-8"):
        model = json.loads(line)["model_id"]
        if model.startswith("gw-") and model not in seen:
            seen.append(model)
    return seen


def _find_run(runs_path: Path, item_id: str, model_id: str):
    found = None
    for line in runs_path.open(encoding="utf-8"):
        record = json.loads(line)
        if (
            record.get("item_id") == item_id
            and record.get("model_id") == model_id
            and record.get("error") is None
        ):
            found = record
    return found


def _grid(page: Image.Image, gt, prediction, result) -> Image.Image:
    truths = gt.get("instances", [])
    preds = prediction.get("instances", [])
    rows = (len(truths) + COLS - 1) // COLS
    width = COLS * (CROP_W + PAD) + PAD
    height = 52 + rows * (CROP_H + LABEL_H + PAD) + PAD
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    font = _font(16)
    small = _font(12)
    draw.text((PAD, 14), "t-4f1 door thresholds | green = ground truth, red = prediction", fill="black", font=font)
    draw.text((PAD, 34), f"score {result['score']:.3f} | F1 {result.get('f1', 0):.3f} | pred/gt {len(preds)}/{len(truths)}", fill="black", font=small)

    instances = result.get("instances", [])
    for index, truth in enumerate(truths):
        best = instances[index] if index < len(instances) else {}
        cropped = _crop_around(page, truth.get("points", []))
        if cropped is None:
            continue
        tile, left, top = cropped
        tile_draw = ImageDraw.Draw(tile)
        _draw(tile_draw, truth.get("points", []), page, (left, top), (0, 145, 70), 2)
        for pred in preds:
            if _intersects(pred.get("points", []), truth.get("points", [])):
                _draw(tile_draw, pred.get("points", []), page, (left, top), (200, 35, 35), 1)
        col = index % COLS
        row = index // COLS
        x = PAD + col * (CROP_W + PAD)
        y = 52 + row * (CROP_H + LABEL_H + PAD)
        sheet.paste(tile, (x, y))
        draw.rectangle((x, y, x + CROP_W, y + CROP_H), outline=(180, 180, 180), width=1)
        label = f"GT {index + 1:03d}  IoU {best.get('best_iou', 0):.2f}"
        draw.text((x, y + CROP_H + 3), label, fill="black", font=small)
    return sheet


def _crop_around(page: Image.Image, normalized: list):
    if len(normalized) < 3:
        return None
    xs = [p[0] * page.width for p in normalized]
    ys = [p[1] * page.height for p in normalized]
    cx = (min(xs) + max(xs)) / 2
    cy = (min(ys) + max(ys)) / 2
    left = int(max(0, min(page.width - CROP_W, cx - CROP_W / 2)))
    top = int(max(0, min(page.height - CROP_H, cy - CROP_H / 2)))
    return page.crop((left, top, left + CROP_W, top + CROP_H)).copy(), left, top


def _draw(draw, points, page: Image.Image, offset: tuple[int, int], color, width: int) -> None:
    pts = [
        (p[0] * page.width - offset[0], p[1] * page.height - offset[1])
        for p in points
    ]
    if len(pts) >= 2:
        draw.line(pts + ([pts[0]] if len(pts) >= 3 else []), fill=color, width=width)


def _intersects(a: list, b: list) -> bool:
    if len(a) < 3 or len(b) < 3:
        return False
    ax = [p[0] for p in a]; ay = [p[1] for p in a]
    bx = [p[0] for p in b]; by = [p[1] for p in b]
    return not (max(ax) < min(bx) or max(bx) < min(ax) or max(ay) < min(by) or max(by) < min(ay))


def _font(size: int):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


if __name__ == "__main__":
    raise SystemExit(main())
