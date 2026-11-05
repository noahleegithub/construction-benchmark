"""Parse and normalize model output.

Models are asked for one JSON object. In practice they wrap it in fences,
prefix it with prose, or return a bare list. This module is permissive about
the envelope and strict about the payload.
"""

from __future__ import annotations

import json
from typing import Any


def extract_json(text: str | None) -> Any:
    """Return the first JSON value found in ``text``."""
    if not text or not text.strip():
        raise ValueError("empty response")
    raw = text.strip()

    if raw.startswith("```"):
        lines = raw.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        raw = "\n".join(lines).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    for opener, closer in (("{", "}"), ("[", "]")):
        start, end = raw.find(opener), raw.rfind(closer)
        if start >= 0 and end > start:
            try:
                return json.loads(raw[start : end + 1])
            except json.JSONDecodeError:
                continue

    for line in raw.splitlines():
        line = line.strip().rstrip(",")
        if line.startswith(("{", "[")):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue

    raise ValueError("no JSON value found in response")


def coerce_prediction(value: Any, output_type: str) -> dict[str, Any]:
    """Normalize a decoded JSON value to the shape the scorer expects."""
    if output_type == "polygons":
        entries = _entries(value, "instances", "polygons")
        return {"type": "polygons", "instances": [_geometry(e) for e in entries]}

    if output_type == "polylines":
        entries = _entries(value, "lines", "polylines")
        return {"type": "polylines", "lines": [_geometry(e) for e in entries]}

    if output_type == "points":
        entries = _entries(value, "points")
        points = []
        for entry in entries:
            if isinstance(entry, dict) and "points" in entry:
                entry = entry["points"]
            if isinstance(entry, list) and len(entry) == 2 and all(
                isinstance(v, (int, float)) for v in entry
            ):
                points.append([float(entry[0]), float(entry[1])])
            else:
                raise ValueError(f"bad point: {entry!r}")
        return {"type": "points", "points": points}

    if output_type == "count":
        if isinstance(value, (int, float)):
            return {"type": "count", "value": value}
        if isinstance(value, dict):
            for key in ("count", "value", "total"):
                if isinstance(value.get(key), (int, float)):
                    return {"type": "count", "value": value[key]}
        raise ValueError("count response has no numeric count")

    if output_type == "text":
        if isinstance(value, str):
            return {"type": "text", "value": value}
        if isinstance(value, dict):
            for key in ("answer", "value", "text"):
                if isinstance(value.get(key), str):
                    return {"type": "text", "value": value[key]}
        raise ValueError("text response has no string answer")

    if output_type == "quantities":
        entries = _entries(value, "line_items", "items", "quantities")
        items = []
        for entry in entries:
            if not isinstance(entry, dict) or "label" not in entry or "value" not in entry:
                raise ValueError(f"bad line item: {entry!r}")
            items.append(
                {
                    "label": str(entry["label"]),
                    "value": float(entry["value"]),
                    "unit": str(entry.get("unit", "")),
                }
            )
        return {"type": "quantities", "items": items}

    raise ValueError(f"unknown output_type: {output_type}")


def _entries(value: Any, *keys: str) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        for key in keys:
            entries = value.get(key)
            if isinstance(entries, list):
                return entries
    raise ValueError(f"expected a list under one of {keys}")


def _geometry(entry: Any) -> dict[str, Any]:
    if isinstance(entry, list):
        return {"points": entry}
    if isinstance(entry, dict) and isinstance(entry.get("points"), list):
        return entry
    raise ValueError(f"bad geometry entry: {entry!r}")
