"""Prompt construction.

The prompt is deliberately short and schema-first: one JSON object, no prose.
Coordinate convention is normalized page space, origin top-left, x right,
y down, values in [0, 1].
"""

from __future__ import annotations

from .schema import Item

SYSTEM = (
    "You are a senior construction estimator reading a drawing sheet. "
    "Answer from the drawing only. Return one JSON object and nothing else: "
    "no markdown, no comments, no trailing text."
)

SCHEMAS = {
    "polygons": (
        '{"instances": [{"id": "optional-id", "label": "optional-label", '
        '"points": [[x, y], ...]}]}'
    ),
    "polylines": '{"lines": [{"label": "optional-label", "points": [[x, y], ...]}]}',
    "points": '{"points": [[x, y], ...]}',
    "count": '{"count": <integer>}',
    "text": '{"answer": "<verbatim answer>"}',
    "quantities": (
        '{"line_items": [{"label": "<label>", "value": <number>, '
        '"unit": "<unit>"}]}'
    ),
}

NOTES = {
    "polygons": (
        "Emit one closed polygon per real-world instance. Do not merge adjacent "
        "instances and do not substitute a bounding box. Include every instance "
        "on the sheet."
    ),
    "polylines": (
        "Emit one polyline per real-world instance. Give every vertex needed to "
        "follow the line; do not simplify to a bounding box."
    ),
    "points": (
        "Emit one point per real-world instance. Include every instance on the "
        "sheet."
    ),
    "count": "Return the total count, not a list of locations.",
    "text": "Copy the answer exactly as written on the sheet.",
    "quantities": (
        "Emit one line item per distinct label. Use the unit named in the "
        "question; do not convert units."
    ),
}


def build_prompt(item: Item) -> str:
    schema = SCHEMAS[item.output_type]
    note = NOTES[item.output_type]
    convention = item.convention or "No additional convention given."
    return (
        f"Task: {item.question}\n\n"
        f"Convention: {convention}\n\n"
        f"{note}\n\n"
        "Coordinates are normalized to the page: x and y are in [0, 1], the "
        "origin is the top-left corner, x increases right, y increases down.\n\n"
        f"Return exactly this JSON shape:\n{schema}"
    )
