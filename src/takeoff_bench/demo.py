"""A synthetic workspace so the harness can be exercised without PDFs.

The demo sheet is a two-room plan with room labels. It is deliberately simple:
the point is to verify the pipeline, not the model.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pymupdf as fitz


def create_demo_workspace(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    (path / "sheets").mkdir(exist_ok=True)
    (path / "gt").mkdir(exist_ok=True)

    width, height = 1000.0, 700.0
    pdf_path = path / "sheets" / "demo-plan.pdf"
    _draw_sheet(pdf_path, width, height)

    rooms = [
        {"id": "room-a", "label": "RM-101", "points": _rect(110, 110, 490, 590, width, height)},
        {"id": "room-b", "label": "RM-102", "points": _rect(510, 110, 890, 590, width, height)},
    ]
    _write_json(path / "gt" / "rooms.json", {"type": "polygons", "instances": rooms})
    _write_json(path / "gt" / "room-count.json", {"type": "count", "value": 2})
    _write_json(path / "gt" / "room-label.json", {"type": "text", "value": "RM-101"})

    rows = [
        {
            "item_id": "demo-rooms",
            "family": "room-areas",
            "sheet": "sheets/demo-plan.pdf",
            "page": 1,
            "question": "Outline the finished floor area of each room as a separate polygon.",
            "convention": "One closed polygon per room, traced on the inner face of the walls; do not merge rooms.",
            "output_type": "polygons",
            "gt": "gt/rooms.json",
            "notes": "Synthetic demo item.",
        },
        {
            "item_id": "demo-count",
            "family": "room-areas",
            "sheet": "sheets/demo-plan.pdf",
            "page": 1,
            "question": "How many rooms are shown on this sheet?",
            "convention": "Count rooms only; do not count doors or windows.",
            "output_type": "count",
            "gt": "gt/room-count.json",
            "notes": "Synthetic demo item.",
        },
        {
            "item_id": "demo-label",
            "family": "room-areas",
            "sheet": "sheets/demo-plan.pdf",
            "page": 1,
            "question": "What is the room number of the left-hand room?",
            "convention": "Return the label exactly as printed.",
            "output_type": "text",
            "gt": "gt/room-label.json",
            "notes": "Synthetic demo item.",
        },
    ]
    with (path / "items.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    (path / "models.yaml").write_text(
        "models:\n"
        "  - id: oracle\n"
        "    provider: oracle\n"
        "  - id: stub\n"
        "    provider: stub\n",
        encoding="utf-8",
    )
    return path


def _draw_sheet(path: Path, width: float, height: float) -> None:
    document = fitz.open()
    page = document.new_page(width=width, height=height)
    page.draw_rect(fitz.Rect(100, 100, 900, 600), color=(0, 0, 0), width=3)
    page.draw_line(fitz.Point(500, 100), fitz.Point(500, 600), color=(0, 0, 0), width=12)
    page.insert_text(fitz.Point(150, 150), "RM-101", fontsize=16)
    page.insert_text(fitz.Point(550, 150), "RM-102", fontsize=16)
    page.insert_text(fitz.Point(150, 640), "DEMO PLAN - NOT TO SCALE", fontsize=9)
    document.save(path)
    document.close()


def _rect(x0, y0, x1, y1, width, height):
    return [
        [x0 / width, y0 / height],
        [x1 / width, y0 / height],
        [x1 / width, y1 / height],
        [x0 / width, y1 / height],
    ]


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
