"""Scoring.

Definitions, stated once so results are reproducible:

* ``score`` for geometry is the mean over ground-truth instances of each
  instance's best IoU against any prediction, with 0 for an unmatched
  instance. This penalizes misses and merging.
* ``precision``, ``recall`` and ``f1`` use one-to-one greedy matching at
  ``iou_threshold`` (default 0.5), pairs taken in descending IoU order.
* Polylines are buffered by ``line_width / 2`` and scored as polygons.
* Segments are matched one-to-one when both endpoints fall within
  ``endpoint_tolerance`` in normalized page units; score is segment F1.
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

from shapely.geometry import LineString, Polygon, box
from shapely.validation import make_valid

DEFAULT_IOU_THRESHOLD = 0.5
DEFAULT_LINE_WIDTH = 0.0015
DEFAULT_ENDPOINT_TOLERANCE = 0.012
DEFAULT_POINT_TOLERANCE = 0.01


def score_item(
    prediction: dict[str, Any] | None,
    gt: dict[str, Any],
    *,
    iou_threshold: float = DEFAULT_IOU_THRESHOLD,
    line_width: float = DEFAULT_LINE_WIDTH,
    endpoint_tolerance: float = DEFAULT_ENDPOINT_TOLERANCE,
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
    if kind == "segments":
        return score_segments(
            prediction, gt, endpoint_tolerance=endpoint_tolerance
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
    if kind == "compliance":
        return score_compliance(prediction, gt)
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


def score_segments(
    prediction: dict[str, Any],
    gt: dict[str, Any],
    *,
    endpoint_tolerance: float = DEFAULT_ENDPOINT_TOLERANCE,
) -> dict[str, Any]:
    """Match wall/door centerline segments by both endpoints.

    Endpoint order is ignored. A pair is credited only when both of its
    endpoints are within ``endpoint_tolerance`` of the expert segment's
    endpoints, which is the convention stated in the TLE wall tasks.
    """
    pred = [_segment(entry) for entry in prediction.get("segments", [])]
    truth = [_segment(entry) for entry in gt.get("segments", [])]
    pred = [segment for segment in pred if segment is not None]
    truth = [segment for segment in truth if segment is not None]

    if not pred:
        result = _empty_score("segments", n_gt=len(truth))
        result["endpoint_tolerance"] = endpoint_tolerance
        return result
    if not truth:
        result = _empty_score("segments")
        result["endpoint_tolerance"] = endpoint_tolerance
        return result

    pairs: list[tuple[float, int, int]] = []
    for i, candidate in enumerate(pred):
        for j, target in enumerate(truth):
            distance = _segment_distance(candidate, target)
            if distance <= endpoint_tolerance:
                pairs.append((distance, i, j))
    pairs.sort(key=lambda item: (item[0], item[1], item[2]))

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
        "mean_endpoint_distance": sum(matched) / len(matched) if matched else None,
        "endpoint_tolerance": endpoint_tolerance,
    }


def _segment(entry: Any) -> tuple[tuple[float, float], tuple[float, float]] | None:
    if isinstance(entry, dict):
        points = entry.get("points")
        if not isinstance(points, list) and all(
            key in entry for key in ("x1", "y1", "x2", "y2")
        ):
            points = [
                [entry["x1"], entry["y1"]],
                [entry["x2"], entry["y2"]],
            ]
    else:
        points = entry
    if not isinstance(points, list) or len(points) != 2:
        return None
    try:
        first = (float(points[0][0]), float(points[0][1]))
        second = (float(points[1][0]), float(points[1][1]))
    except (TypeError, ValueError, IndexError):
        return None
    return first, second


def _segment_distance(
    a: tuple[tuple[float, float], tuple[float, float]],
    b: tuple[tuple[float, float], tuple[float, float]],
) -> float:
    direct = max(_distance(a[0], b[0]), _distance(a[1], b[1]))
    reverse = max(_distance(a[0], b[1]), _distance(a[1], b[0]))
    return min(direct, reverse)


def _distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


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


def score_compliance(
    prediction: dict[str, Any],
    gt: dict[str, Any],
    *,
    measure_tolerance_mm: float | None = None,
    evidence_iou: float = 0.5,
    region_tolerance: float = 0.02,
) -> dict[str, Any]:
    """Score per-instance measurement, verdict and evidence for a rule check.

    Ground-truth instances are the required findings (for a failure-only task,
    only the noncompliant doors). Predictions are matched by explicit id when
    both sides carry one, otherwise by evidence-region IoU.
    """
    truth = gt.get("instances", [])
    pred = prediction.get("instances", [])
    criteria = gt.get("criteria") or {}
    tolerance = measure_tolerance_mm
    if tolerance is None:
        tolerance = float(criteria.get("measure_tolerance_mm", 50.0))

    pairs: list[tuple[float, int, int]] = []
    for i, candidate in enumerate(pred):
        for j, target in enumerate(truth):
            pid = str(candidate.get("id", "")).strip()
            tid = str(target.get("id", "")).strip()
            if pid and tid and pid == tid:
                pairs.append((2.0, i, j))
                continue
            p_box = _evidence_box(candidate)
            t_box = _evidence_box(target)
            if p_box is None or t_box is None:
                continue
            if _regions_match(p_box, t_box, evidence_iou, region_tolerance):
                pairs.append((_region_affinity(p_box, t_box), i, j))
    pairs.sort(key=lambda item: (-item[0], item[1], item[2]))

    used_pred: set[int] = set()
    used_gt: set[int] = set()
    matches: dict[int, int] = {}
    for _, i, j in pairs:
        if i in used_pred or j in used_gt:
            continue
        used_pred.add(i)
        used_gt.add(j)
        matches[j] = i

    per_instance: list[dict[str, Any]] = []
    verdict_scores: list[float] = []
    measurement_scores: list[float] = []
    evidence_scores: list[float] = []
    errors: list[float] = []
    abstained = sum(1 for item in pred if item.get("verdict") == "indeterminate")

    for j, target in enumerate(truth):
        gt_measure = float(target["measure"])
        gt_verdict = str(target.get("verdict", "fail"))
        i = matches.get(j)
        if i is None:
            verdict_scores.append(0.0)
            measurement_scores.append(0.0)
            evidence_scores.append(0.0)
            per_instance.append({"id": target.get("id"), "matched": False, "score": 0.0})
            continue

        candidate = pred[i]
        measure_delta = abs(float(candidate["measure"]) - gt_measure)
        measure_score = max(0.0, 1.0 - measure_delta / tolerance) if tolerance else 0.0
        verdict_score = 1.0 if candidate.get("verdict") == gt_verdict else 0.0
        ev_score = _evidence_score(candidate, target, evidence_iou, region_tolerance)
        composite = 0.4 * verdict_score + 0.4 * measure_score + 0.2 * ev_score
        verdict_scores.append(verdict_score)
        measurement_scores.append(measure_score)
        evidence_scores.append(ev_score)
        errors.append(measure_delta)
        per_instance.append(
            {
                "id": target.get("id"),
                "matched": True,
                "truth": gt_measure,
                "predicted": float(candidate["measure"]),
                "verdict": candidate.get("verdict"),
                "measure_delta_mm": measure_delta,
                "score": composite,
            }
        )

    n_gt = len(truth)
    tp = len(matches)
    fp = len(pred) - tp
    fn = n_gt - tp
    precision = tp / len(pred) if pred else 0.0
    recall = tp / n_gt if n_gt else 0.0
    score = sum(item["score"] for item in per_instance) / n_gt if n_gt else 0.0

    return {
        "score": score,
        "precision": precision,
        "recall": recall,
        "f1": _f1(precision, recall),
        "n_pred": len(pred),
        "n_gt": n_gt,
        "count_ratio": len(pred) / n_gt if n_gt else None,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "verdict_accuracy": sum(verdict_scores) / n_gt if n_gt else 0.0,
        "measure_error": sum(errors) / len(errors) if errors else None,
        "measurement_accuracy": (
            sum(measurement_scores) / n_gt if n_gt else 0.0
        ),
        "evidence_rate": sum(evidence_scores) / n_gt if n_gt else 0.0,
        "abstained": abstained,
        "instances": per_instance,
    }


def _evidence_box(instance: dict[str, Any]) -> Polygon | None:
    region = (instance.get("evidence") or {}).get("region")
    if not (
        isinstance(region, list)
        and len(region) == 4
        and all(isinstance(value, (int, float)) for value in region)
    ):
        return None
    xs = sorted([float(region[0]), float(region[2])])
    ys = sorted([float(region[1]), float(region[3])])
    return box(xs[0], ys[0], xs[1], ys[1])


def _evidence_score(
    candidate: dict[str, Any],
    target: dict[str, Any],
    evidence_iou: float,
    region_tolerance: float = 0.02,
) -> float:
    candidate_sheet = str((candidate.get("evidence") or {}).get("sheet", ""))
    target_sheet = str((target.get("evidence") or {}).get("sheet", ""))
    if candidate_sheet != target_sheet:
        return 0.0
    p_box = _evidence_box(candidate)
    t_box = _evidence_box(target)
    if p_box is None or t_box is None:
        return 0.5
    if _regions_match(p_box, t_box, evidence_iou, region_tolerance):
        return 1.0
    if _centroid_distance(p_box, t_box) <= 0.03:
        return 0.5
    return 0.0


def _centroid_distance(a: Polygon, b: Polygon) -> float:
    return a.centroid.distance(b.centroid)


def _regions_match(
    a: Polygon, b: Polygon, evidence_iou: float, tolerance: float
) -> bool:
    if _iou(a, b) >= evidence_iou:
        return True
    if a.contains(b.centroid) or b.contains(a.centroid):
        return True
    return _centroid_distance(a, b) <= tolerance


def _region_affinity(a: Polygon, b: Polygon) -> float:
    if _iou(a, b) >= 0.5:
        return 1.0 + _iou(a, b)
    if a.contains(b.centroid) or b.contains(a.centroid):
        return 1.0
    return max(0.0, 1.0 - _centroid_distance(a, b))


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
    best_index = [max(range(len(pred)), key=lambda i: ious[i][j]) for j in range(len(truth))]
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
        "instances": [
            {
                "gt_index": index,
                "best_iou": best_per_gt[index],
                "matched": best_per_gt[index] >= iou_threshold,
                "pred_index": best_index[index],
            }
            for index in range(len(truth))
        ],
        "mean_iou_matched": (
            sum(matched_ious) / len(matched_ious) if matched_ious else None
        ),
        "matched_iou_sum": sum(matched_ious),
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
