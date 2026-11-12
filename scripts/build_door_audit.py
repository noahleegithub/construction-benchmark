"""Build a visual audit pack for the derived t-4f1 door-clearance ground truth.

The widths come from the TLE threshold polygons, not from a door schedule. This
script renders every derived failure plus a spatially spread sample of passing
doors so a human can confirm the scale, the jamb convention, and the verdict.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import Polygon

ROOT = Path("study/gateway")
SHEET = Path("study/sheets/t-4f1-door-threshold-areas.pdf")
GT = Path("study/gt/t-4f1-door-threshold-areas.json")
OUT = ROOT / "audit" / "t-4f1"

PAGE_W, PAGE_H = 3024.0, 2160.0
POINTS_PER_FOOT = 9.0  # 1/8 in = 1 ft
INCHES_PER_FOOT = 12.0
MM_PER_INCH = 25.4
CLEAR_WIDTH_MM = 900.0
PASS_CONTROLS = 20
TILE_W, TILE_H = 420, 330
COLS, ROWS = 3, 4
PAD = 90.0  # PDF points of context around a threshold


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def measure(points: list[list[float]]) -> tuple[float, float, list[float]]:
    xy = [(x * PAGE_W, y * PAGE_H) for x, y in points]
    rect = Polygon(xy).minimum_rotated_rectangle
    coords = list(rect.exterior.coords)
    sides = [
        math.dist(coords[i], coords[i + 1])
        for i in range(4)
    ]
    width_in = max(sides) / POINTS_PER_FOOT * INCHES_PER_FOOT
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    bbox = [min(xs), min(ys), max(xs), max(ys)]
    return width_in, width_in * MM_PER_INCH, bbox


def farthest_sample(entries: list[dict], count: int) -> list[dict]:
    if len(entries) <= count:
        return entries
    selected = [entries[0]]
    remaining = entries[1:]
    while len(selected) < count and remaining:
        def distance(entry: dict) -> float:
            x = (entry["bbox"][0] + entry["bbox"][2]) / 2
            y = (entry["bbox"][1] + entry["bbox"][3]) / 2
            return min(
                (x - (other["bbox"][0] + other["bbox"][2]) / 2) ** 2
                + (y - (other["bbox"][1] + other["bbox"][3]) / 2) ** 2
                for other in selected
            )

        best = max(remaining, key=distance)
        selected.append(best)
        remaining.remove(best)
    return selected


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "crops").mkdir(exist_ok=True)
    page = pymupdf.open(SHEET)[0]
    source = json.loads(GT.read_text())["instances"]

    entries = []
    for index, inst in enumerate(source, start=1):
        width_in, width_mm, bbox = measure(inst["points"])
        entries.append(
            {
                "source_index": index,
                "width_in": width_in,
                "width_mm": width_mm,
                "bbox": bbox,
                "kind": "fail" if width_mm < CLEAR_WIDTH_MM else "pass",
            }
        )

    failures = [entry for entry in entries if entry["kind"] == "fail"]
    passes = [entry for entry in entries if entry["kind"] == "pass"]
    selected_passes = farthest_sample(passes, PASS_CONTROLS)
    rows = failures + selected_passes

    # Stable IDs: failures first, then passing controls.
    for index, row in enumerate(rows, start=1):
        row["sample_id"] = f"F{index:02d}" if row["kind"] == "fail" else f"P{index - len(failures):02d}"
        row["crop_file"] = f"crops/{row['sample_id']}.png"
        row["borderline"] = abs(row["width_mm"] - CLEAR_WIDTH_MM) <= 20

    font = load_font(18)
    small = load_font(14)
    tiles = []
    for row in rows:
        x0, y0, x1, y1 = row["bbox"]
        clip = pymupdf.Rect(
            max(0.0, x0 * PAGE_W - PAD),
            max(0.0, y0 * PAGE_H - PAD),
            min(PAGE_W, x1 * PAGE_W + PAD),
            min(PAGE_H, y1 * PAGE_H + PAD),
        )
        pix = page.get_pixmap(matrix=pymupdf.Matrix(4, 4), clip=clip, alpha=False)
        image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

        cx0 = (x0 * PAGE_W - clip.x0) / (clip.x1 - clip.x0) * image.width
        cy0 = (y0 * PAGE_H - clip.y0) / (clip.y1 - clip.y0) * image.height
        cx1 = (x1 * PAGE_W - clip.x0) / (clip.x1 - clip.x0) * image.width
        cy1 = (y1 * PAGE_H - clip.y0) / (clip.y1 - clip.y0) * image.height
        draw = ImageDraw.Draw(image)
        color = "#d62728" if row["kind"] == "fail" else "#2ca02c"
        draw.rectangle([cx0, cy0, cx1, cy1], outline=color, width=4)

        crop_path = OUT / row["crop_file"]
        image.save(crop_path)

        image.thumbnail((TILE_W, TILE_H - 50))
        tile = Image.new("RGB", (TILE_W, TILE_H), "white")
        tile.paste(image, ((TILE_W - image.width) // 2, 4))
        tdraw = ImageDraw.Draw(tile)
        tdraw.rectangle([0, 0, TILE_W - 1, TILE_H - 1], outline="#cccccc", width=1)
        tdraw.text(
            (10, TILE_H - 42),
            f"{row['sample_id']}  {row['kind'].upper()}  "
            f"{row['width_mm']:.1f} mm ({row['width_in']:.2f} in)",
            fill=color,
            font=font,
        )
        tdraw.text(
            (10, TILE_H - 20),
            f"source polygon {row['source_index']}",
            fill="#444444",
            font=small,
        )
        tiles.append(tile)

    sheets = math.ceil(len(tiles) / (COLS * ROWS))
    for sheet_index in range(sheets):
        sheet = Image.new("RGB", (COLS * TILE_W + 20, ROWS * TILE_H + 50), "white")
        draw = ImageDraw.Draw(sheet)
        draw.text(
            (10, 10),
            "t-4f1 door audit — failures (F) and passing controls (P), "
            "scale 1/8 in = 1 ft",
            fill="black",
            font=font,
        )
        for offset in range(COLS * ROWS):
            tile_index = sheet_index * COLS * ROWS + offset
            if tile_index >= len(tiles):
                break
            col, row_index = offset % COLS, offset // COLS
            sheet.paste(tiles[tile_index], (10 + col * TILE_W, 40 + row_index * TILE_H))
        sheet.save(OUT / f"audit_sheet_{sheet_index + 1}.png")

    with (OUT / "audit.csv").open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "sample_id",
            "kind",
            "source_index",
            "width_in",
            "width_mm",
            "verdict",
            "borderline",
            "x0",
            "y0",
            "x1",
            "y1",
            "crop_file",
            "audit_width_mm",
            "audit_verdict",
            "audit_notes",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "sample_id": row["sample_id"],
                    "kind": row["kind"],
                    "source_index": row["source_index"],
                    "width_in": f"{row['width_in']:.2f}",
                    "width_mm": f"{row['width_mm']:.1f}",
                    "verdict": row["kind"],
                    "borderline": "yes" if row["borderline"] else "no",
                    "x0": f"{row['bbox'][0]:.6f}",
                    "y0": f"{row['bbox'][1]:.6f}",
                    "x1": f"{row['bbox'][2]:.6f}",
                    "y1": f"{row['bbox'][3]:.6f}",
                    "crop_file": row["crop_file"],
                    "audit_width_mm": "",
                    "audit_verdict": "",
                    "audit_notes": "",
                }
            )

    pass_controls = [
        {
            "sample_id": row["sample_id"],
            "source_index": row["source_index"],
            "width_mm": round(row["width_mm"], 1),
            "borderline": row["borderline"],
            "bbox": [round(value, 6) for value in row["bbox"]],
        }
        for row in rows
        if row["kind"] == "pass"
    ]
    (OUT / "pass_controls.json").write_text(
        json.dumps(pass_controls, indent=2) + "\n", encoding="utf-8"
    )

    (OUT / "README.md").write_text(
        "# t-4f1 door-clearance audit\n\n"
        "The widths in `audit.csv` are derived from the TLE threshold polygons "
        "and the sheet's `1/8 in = 1 ft` scale. They are provisional until the "
        "boxes are checked against the drawn door openings.\n\n"
        "For each row, open the crop and confirm:\n\n"
        "1. the red/green box sits on the door opening, not the leaf or swing;\n"
        "2. the measured width is the clear opening between jambs;\n"
        "3. the verdict matches the 900 mm rule.\n\n"
        "Rows marked `borderline=yes` are within 20 mm of the threshold; most "
        "failures are 35.00 in (889 mm), so a small scale or jamb-convention "
        "error flips the verdict. Resolve those first.\n\n"
        "Record the checked width in `audit_width_mm`, the checked verdict in "
        "`audit_verdict`, and any discrepancy in `audit_notes`. Do not edit the "
        "derived columns in place; they are the comparison baseline.\n",
        encoding="utf-8",
    )
    print(f"wrote {len(rows)} audit rows ({len(failures)} failures, {len(selected_passes)} pass controls)")
    print(f"wrote {sheets} contact sheets to {OUT}")


if __name__ == "__main__":
    main()
