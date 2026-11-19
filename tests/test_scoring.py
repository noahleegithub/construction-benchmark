import math

from takeoff_bench import parsing
from takeoff_bench.scoring import (
    score_count,
    score_item,
    score_points,
    score_polygons,
    score_polylines,
    score_quantities,
    score_segments,
    score_text,
)


def square(x0, y0, x1, y1):
    return {"points": [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]}


def test_perfect_polygons():
    gt = {"type": "polygons", "instances": [square(0, 0, 1, 1)]}
    result = score_polygons(gt, gt)
    assert result["score"] == 1.0
    assert result["precision"] == 1.0
    assert result["recall"] == 1.0
    assert result["count_ratio"] == 1.0


def test_shifted_polygon():
    gt = {"type": "polygons", "instances": [square(0, 0, 1, 1)]}
    pred = {"type": "polygons", "instances": [square(0.2, 0, 1.2, 1)]}
    result = score_polygons(pred, gt)
    assert math.isclose(result["score"], 0.8 / 1.2, rel_tol=1e-6)
    assert result["recall"] == 1.0


def test_merged_polygons_lose_recall():
    gt = {
        "type": "polygons",
        "instances": [square(0, 0, 1, 1), square(1, 0, 2, 1)],
    }
    pred = {"type": "polygons", "instances": [square(0, 0, 2, 1)]}
    result = score_polygons(pred, gt)
    assert math.isclose(result["score"], 0.5, rel_tol=1e-6)
    assert result["recall"] == 0.5
    assert result["count_ratio"] == 0.5


def test_empty_prediction_scores_zero():
    gt = {"type": "polygons", "instances": [square(0, 0, 1, 1)]}
    result = score_item(None, gt)
    assert result["score"] == 0.0
    assert result["recall"] == 0.0


def test_polylines_perfect():
    gt = {"type": "polylines", "lines": [{"points": [[0.1, 0.1], [0.9, 0.1]]}]}
    result = score_polylines(gt, gt)
    assert result["score"] == 1.0


def test_segments_perfect_and_reversed():
    gt = {
        "type": "segments",
        "segments": [
            {"points": [[0.1, 0.1], [0.9, 0.1]]},
            {"points": [[0.1, 0.1], [0.1, 0.9]]},
        ],
    }
    pred = {
        "type": "segments",
        "segments": [
            {"points": [[0.1, 0.9], [0.1, 0.1]]},
            {"points": [[0.9, 0.1], [0.1, 0.1]]},
        ],
    }
    result = score_segments(pred, gt)
    assert result["score"] == 1.0
    assert result["tp"] == 2
    assert result["mean_endpoint_distance"] == 0.0


def test_segments_endpoint_failure_and_extra():
    gt = {"type": "segments", "segments": [{"points": [[0.1, 0.1], [0.9, 0.1]]}]}
    pred = {
        "type": "segments",
        "segments": [
            {"points": [[0.1, 0.1], [0.8, 0.1]]},
            {"points": [[0.1, 0.5], [0.9, 0.5]]},
        ],
    }
    result = score_segments(pred, gt)
    assert result["tp"] == 0
    assert result["fp"] == 2
    assert result["fn"] == 1
    assert result["score"] == 0.0


def test_parse_segments_native_shape():
    parsed = parsing.coerce_prediction(
        {"segments": [{"x1": 0, "y1": 0, "x2": 1, "y2": 1}]}, "segments"
    )
    assert parsed["segments"][0]["points"] == [[0.0, 0.0], [1.0, 1.0]]


def test_points_precision_and_recall():
    gt = {"type": "points", "points": [[0.1, 0.1], [0.5, 0.5]]}
    pred = {"type": "points", "points": [[0.1, 0.1], [0.5, 0.5], [0.9, 0.9]]}
    result = score_points(pred, gt)
    assert math.isclose(result["precision"], 2 / 3)
    assert result["recall"] == 1.0
    assert math.isclose(result["score"], 0.8)


def test_count_score():
    assert score_count({"value": 12}, {"value": 10})["score"] == 0.8
    assert score_count({"value": 0}, {"value": 0})["score"] == 1.0


def test_text_normalization():
    result = score_text({"value": "RM-101."}, {"value": " rm-101 "})
    assert result["score"] == 1.0


def test_quantities():
    gt = {"type": "quantities", "items": [{"label": "Walls", "value": 100}, {"label": "Doors", "value": 50}]}
    pred = {"line_items": [{"label": "walls", "value": 110}, {"label": "Doors", "value": 45}]}
    result = score_quantities(pred, gt)
    assert math.isclose(result["score"], 0.9, rel_tol=1e-6)
    assert result["matched"] == 2


def test_parse_fenced_json():
    text = '```json\n{"instances": [{"points": [[0, 0], [1, 0], [1, 1]]}]}\n```'
    parsed = parsing.coerce_prediction(parsing.extract_json(text), "polygons")
    assert len(parsed["instances"]) == 1


def test_parse_bare_list():
    parsed = parsing.coerce_prediction(
        [[[0, 0], [1, 0], [1, 1]]], "polygons"
    )
    assert parsed["instances"][0]["points"][0] == [0, 0]


def test_parse_prose_prefix():
    text = 'Here is the answer:\n{"count": 7}\nLet me know if you need anything else.'
    parsed = parsing.coerce_prediction(parsing.extract_json(text), "count")
    assert parsed["value"] == 7
