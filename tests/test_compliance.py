import pytest

from takeoff_bench import parsing, report
from takeoff_bench.schema import ItemError, validate_gt
from takeoff_bench.scoring import score_compliance, score_item


def instance(**overrides):
    item = {
        "id": "d-1",
        "measure": 850.0,
        "unit": "mm",
        "verdict": "fail",
        "evidence": {"sheet": "A1-13A", "region": [0.1, 0.2, 0.12, 0.22]},
    }
    item.update(overrides)
    return item


def ground_truth():
    return {
        "type": "compliance",
        "criteria": {"clear_width_mm": 900, "measure_tolerance_mm": 50},
        "instances": [instance()],
    }


def test_perfect_compliance():
    result = score_compliance({"instances": [instance()]}, ground_truth())
    assert result["score"] == 1.0
    assert result["verdict_accuracy"] == 1.0
    assert result["evidence_rate"] == 1.0
    assert result["measure_error"] == 0.0


def test_measurement_outside_tolerance_keeps_verdict():
    result = score_compliance(
        {"instances": [instance(measure=950.0)]}, ground_truth()
    )
    assert result["score"] == pytest.approx(0.6)
    assert result["verdict_accuracy"] == 1.0
    assert result["measurement_accuracy"] == 0.0


def test_wrong_verdict_loses_verdict_component():
    result = score_compliance(
        {"instances": [instance(verdict="pass")]}, ground_truth()
    )
    assert result["score"] == pytest.approx(0.6)
    assert result["verdict_accuracy"] == 0.0
    assert result["measurement_accuracy"] == 1.0


def test_missed_instance_scores_zero():
    result = score_compliance({"instances": []}, ground_truth())
    assert result["score"] == 0.0
    assert result["recall"] == 0.0
    assert result["fn"] == 1


def test_extra_instance_reduces_precision():
    result = score_compliance(
        {
            "instances": [
                instance(),
                instance(
                    id="extra",
                    evidence={"sheet": "A1-13A", "region": [0.8, 0.8, 0.82, 0.82]},
                ),
            ]
        },
        ground_truth(),
    )
    assert result["score"] == 1.0
    assert result["precision"] == 0.5
    assert result["fp"] == 1


def test_dispatches_from_score_item():
    result = score_item({"instances": [instance()]}, ground_truth())
    assert result["score"] == 1.0


def test_parse_compliance():
    parsed = parsing.coerce_prediction(
        {
            "instances": [
                {
                    "measure": 840,
                    "verdict": "fail",
                    "evidence": {"sheet": "A1-13A", "region": [0.1, 0.2, 0.12, 0.22]},
                }
            ]
        },
        "compliance",
    )
    assert parsed["instances"][0]["measure"] == 840.0
    assert parsed["instances"][0]["verdict"] == "fail"


def test_schema_rejects_bad_verdict():
    bad = ground_truth()
    bad["instances"][0]["verdict"] = "maybe"
    with pytest.raises(ItemError, match="invalid verdict"):
        validate_gt("item", bad, "compliance")


def test_report_counts_completion_and_failures_as_zero():
    rows = [
        {"model_id": "m", "family": "f", "status": "scored", "score": 1.0},
        {"model_id": "m", "family": "f", "status": "parse_error", "score": None},
    ]
    summary = report.summarize(rows)
    assert len(summary) == 2
    row = [item for item in summary if item["family"] == "f"][0]
    assert row["attempted"] == 2
    assert row["scored"] == 1
    assert row["completion"] == 0.5
    assert row["score_all"] == 0.5
    assert row["errors"] == 1
