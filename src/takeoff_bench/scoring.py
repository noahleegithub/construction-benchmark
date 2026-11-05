"""Scoring.

Definitions, stated once so results are reproducible:

* ``score`` for geometry is the mean over ground-truth instances of each
  instance's best IoU against any prediction, with 0 for an unmatched
  instance. This penalizes misses and merging.
* ``precision``, ``recall`` and ``f1`` use one-to-one greedy matching at
  ``iou_threshold`` (default 0.5), pairs taken in descending IoU order.
* Polylines are buffered by ``line_width / 2`` and scored as polygons.
* Points are matched within ``tolerance`` in normalized page units.
* Text is normalized (case, whitespace, trailing punctuation) and scored
  exact; a similarity ratio is reported alongside.
* Quantities are matched by label; each line scores ``max(0, 1 - relative
  error)``, and missing lines score 0.
"""

from __future__ import annotations

import difflib
import re
from typing import Any, cast

from shapely.geometry import LineString, Polygon
from shapely.validation import make_valid

DEFAULT_IOU_THRESHOLD = 0.5
DEFAULT_LINE_WIDTH = 0.0015
DEFAULT_POINT_TOLERANCE = 0.01


def score_item(
    prediction: dict[str, Any] | None,
    gt: dict[str, Any],
    *,
    iou_threshold: float = DEFAULT_IOU_THRESHOLD,
    line_width: float = DEFAULT_LINE_WIDTH,
    point_tolerance: float = DEFAULT_POINT_TOLERANCE,
    quantity_tolerance: float = 0.05,
) -> dict[str, Any]:
    kind = gt["type"]
    if prediction is None:
        return _empty_score(kind)

    if kind == "polygons":
        return score_polygons(
            prediction, gt, iou_threshold=iou_threshold
        )
    if kind == "polylines":
        return score_polylines(
            prediction, gt, iou_threshold=iou_threshold, line_width=line_width
        )
    if kind == "points":
        return score_points(prediction, gt, tolerance=point_tolerance)
    if kind == "count":
        return score_count(prediction, gt)
    if kind == "text":
        return score_text(prediction, gt)
    if kind == "quantities":
        return score_quantities(
            prediction, gt, tolerance=quantity_tolerance
        )
    raise ValueError(f"unknown ground-truth type: {kind}")


def score_polygons(
    prediction: dict[str, Any],
    gt: dict[str, Any],
    *,
    iou_threshold: float = DEFAULT_IOU_THRESHOLD,
) -> dict[str, Any]:
    pred = [_polygon(entry) for entry in prediction.get("instances", [])]
    truth = [_polygon(entry) for entry in gt.get("instances", [])]
    return _score_geometry(pred, truth, iou_threshold)


def score_polylines(
    prediction: dict[str, Any],
    gt: dict[str, Any],
    *,
    iou_threshold: float = DEFAULT_IOU_THRESHOLD,
    line_width: float = DEFAULT_LINE_WIDTH,
) -> dict[str, Any]:
    pred = [_buffer_line(entry, line_width) for entry in prediction.get("lines", [])]
    truth = [_buffer_line(entry, line_width) for entry in gt.get("lines", [])]
    result = _score_geometry(pred, truth, iou_threshold)
    result["line_width"] = line_width
    return result


def score_points(
    prediction: dict[str, Any],
    gt: dict[str, Any],
    *,
    tolerance: float = DEFAULT_POINT_TOLERANCE,
) -> dict[str, Any]:
    pred = _points(prediction.get("points", []))
    truth = _points(gt.get("points", []))
    if not pred:
        return _empty_score("points", n_gt=len(truth))

    pairs = []
    for i, (px, py) in enumerate(pred):
        for j, (gx, gy) in enumerate(truth):
            distance = ((px - gx) ** 2 + (py - gy) ** 2) ** 0.5
            if distance <= tolerance:
                pairs.append((distance, i, j))
    pairs.sort()

    used_pred: set[int] = set()
    used_gt: set[int] = set()
    matched: list[float] = []
    for distance, i, j in pairs:
        if i in used_pred or j in used_gt:
            continue
        used_pred.add(i)
        used_gt.add(j)
        matched.append(distance)

    tp = len(matched)
    fp, fn = len(pred) - tp, len(truth) - tp
    precision = tp / len(pred) if pred else 0.0
    recall = tp / len(truth) if truth else 0.0
    return {
        "score": _f1(precision, recall),
        "precision": precision,
        "recall": recall,
        "f1": _f1(precision, recall),
        "n_pred": len(pred),
        "n_gt": len(truth),
        "count_ratio": len(pred) / len(truth) if truth else None,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "mean_distance": sum(matched) / len(matched) if matched else None,
        "tolerance": tolerance,
    }


def score_count(prediction: dict[str, Any], gt: dict[str, Any]) -> dict[str, Any]:
    predicted = float(prediction.get("value", 0))
    truth = float(gt.get("value", 0))
    if truth == 0:
        score = 1.0 if predicted == 0 else 0.0
        relative_error = None
    else:
        relative_error = abs(predicted - truth) / abs(truth)
        score = max(0.0, 1.0 - relative_error)
    return {
        "score": score,
        "predicted": predicted,
        "truth": truth,
        "relative_error": relative_error,
    }


def score_text(prediction: dict[str, Any], gt: dict[str, Any]) -> dict[str, Any]:
    predicted = _normalize_text(str(prediction.get("value", "")))
    truth = _normalize_text(str(gt.get("value", "")))
    exact = bool(truth) and predicted == truth
    similarity = (
        difflib.SequenceMatcher(None, predicted, truth).ratio() if truth else 0.0
    )
    return {
        "score": 1.0 if exact else 0.0,
        "exact": exact,
        "similarity": similarity,
        "predicted": predicted,
        "truth": truth,
    }


def score_quantities(
    prediction: dict[str, Any],
    gt: dict[str, Any],
    *,
    tolerance: float = 0.05,
) -> dict[str, Any]:
    predicted = prediction.get("items") or prediction.get("line_items") or []
    truth = gt.get("items", [])
    pred_by_label = {_normalize_label(item["label"]): item for item in predicted}

    lines = []
    errors = []
    for target in truth:
        label = _normalize_label(target["label"])
        match = pred_by_label.get(label)
        if match is None:
            match = _nearest_label(label, pred_by_label)
        if match is None:
            lines.append({"label": target["label"], "score": 0.0, "relative_error": None})
            continue
        value = float(target["value"])
        if value == 0:
            relative_error = 0.0 if float(match["value"]) == 0 else 1.0
        else:
            relative_error = abs(float(match["value"]) - value) / abs(value)
        errors.append(relative_error)
        lines.append(
            {
                "label": target["label"],
                "predicted": float(match["value"]),
                "truth": value,
                "relative_error": relative_error,
                "within_tolerance": relative_error <= tolerance,
                "score": max(0.0, 1.0 - relative_error),
            }
        )

    matched = [line for line in lines if line.get("relative_error") is not None]
    return {
        "score": sum(line["score"] for line in lines) / len(lines) if lines else 0.0,
        "lines": lines,
        "matched": len(matched),
        "n_gt": len(lines),
        "n_pred": len(predicted),
        "mape": sum(errors) / len(errors) if errors else None,
        "within_tolerance": (
            sum(1 for line in matched if line["within_tolerance"]) / len(lines)
            if lines
            else 0.0
        ),
        "tolerance": tolerance,
    }


def _score_geometry(pred, truth, iou_threshold: float) -> dict[str, Any]:
    if not pred:
        return _empty_score("polygons" if truth else "polygons", n_gt=len(truth))
    if not truth:
        return _empty_score("polygons")

    ious = [[_iou(p, t) for t in truth] for p in pred]

    # One-to-one greedy matching for precision and recall.
    pairs = [
        (ious[i][j], i, j)
        for i in range(len(pred))
        for j in range(len(truth))
        if ious[i][j] >= iou_threshold
    ]
    pairs.sort(key=lambda item: (-item[0], item[1], item[2]))
    used_pred: set[int] = set()
    used_gt: set[int] = set()
    matched_ious: list[float] = []
    for value, i, j in pairs:
        if i in used_pred or j in used_gt:
            continue
        used_pred.add(i)
        used_gt.add(j)
        matched_ious.append(value)

    tp = len(matched_ious)
    fp, fn = len(pred) - tp, len(truth) - tp
    precision = tp / len(pred) if pred else 0.0
    recall = tp / len(truth) if truth else 0.0

    # Score: each ground-truth instance's best IoU, zero when missed.
    best_per_gt = [max(ious[i][j] for i in range(len(pred))) for j in range(len(truth))]
    score = sum(best_per_gt) / len(best_per_gt)

    return {
        "score": score,
        "precision": precision,
        "recall": recall,
        "f1": _f1(precision, recall),
        "n_pred": len(pred),
        "n_gt": len(truth),
        "count_ratio": len(pred) / len(truth) if truth else None,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "mean_iou_matched": (
            sum(matched_ious) / len(matched_ious) if matched_ious else None
        ),
        "iou_threshold": iou_threshold,
    }


def _empty_score(kind: str, n_gt: int = 0) -> dict[str, Any]:
    return {
        "score": 0.0,
        "precision": 0.0,
        "recall": 0.0,
        "f1": 0.0,
        "n_pred": 0,
        "n_gt": n_gt,
        "count_ratio": 0.0 if n_gt else None,
        "tp": 0,
        "fp": 0,
        "fn": n_gt,
    }


def _polygon(entry: dict[str, Any]) -> Polygon:
    points = entry.get("points", []) if isinstance(entry, dict) else entry
    if not isinstance(points, list) or len(points) < 3:
        return Polygon()
    shape = Polygon(points)
    if not shape.is_valid:
        shape = make_valid(shape)
    if shape.geom_type == "Polygon":
        return cast(Polygon, shape)
    parts = [part for part in getattr(shape, "geoms", []) if part.geom_type == "Polygon"]
    return cast(Polygon, max(parts, key=lambda part: part.area)) if parts else Polygon()


def _buffer_line(entry: dict[str, Any], width: float) -> Polygon:
    points = entry.get("points", []) if isinstance(entry, dict) else entry
    if not isinstance(points, list) or len(points) < 2:
        return Polygon()
    return LineString(points).buffer(
        max(width, 1e-6) / 2, cap_style="flat", join_style="mitre"
    )


def _points(entries: list[Any]) -> list[tuple[float, float]]:
    result = []
    for entry in entries:
        if isinstance(entry, dict):
            entry = entry.get("points")
        if isinstance(entry, list) and len(entry) == 2:
            result.append((float(entry[0]), float(entry[1])))
    return result


def _iou(a: Polygon, b: Polygon) -> float:
    if a.is_empty or b.is_empty:
        return 0.0
    intersection = a.intersection(b).area
    union = a.union(b).area
    return intersection / union if union else 0.0


def _f1(precision: float, recall: float) -> float:
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def _normalize_text(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"\s+", " ", value)
    return value.strip(" .,;:")


def _normalize_label(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _nearest_label(label: str, candidates: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    best, best_ratio = None, 0.0
    for candidate, item in candidates.items():
        ratio = difflib.SequenceMatcher(None, label, candidate).ratio()
        if ratio > best_ratio:
            best, best_ratio = item, ratio
    return best if best_ratio >= 0.85 else None
