from pathlib import Path

from takeoff_bench import report


def test_task_usage_sums_tokens_and_cost_per_task():
    rows = [
        {
            "model_id": "m",
            "item_id": "task-1",
            "family": "fam",
            "status": "scored",
            "score": 1.0,
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
            "cost_usd": 0.01,
        },
        {
            "model_id": "m",
            "item_id": "task-1",
            "family": "fam",
            "status": "scored",
            "score": 0.0,
            "prompt_tokens": 200,
            "completion_tokens": 100,
            "total_tokens": 300,
            "cost_usd": 0.02,
        },
        {
            "model_id": "m",
            "item_id": "task-1",
            "family": "fam",
            "status": "parse_error",
            "score": None,
            "prompt_tokens": 20,
            "completion_tokens": 0,
            "total_tokens": 20,
            "cost_usd": None,
        },
    ]
    usage = report.task_usage(rows)
    assert len(usage) == 1
    row = usage[0]
    assert row["runs"] == 3
    assert row["scored"] == 2
    assert row["completion"] == 2 / 3
    assert row["prompt_tokens"] == 320
    assert row["completion_tokens"] == 150
    assert row["total_tokens"] == 470
    assert row["cost_usd"] == 0.03
    assert row["score"] == 0.5


def test_write_usage_has_one_row_per_task(tmp_path: Path):
    usage = report.task_usage(
        [
            {
                "model_id": "m",
                "item_id": "task-1",
                "family": "fam",
                "status": "scored",
                "score": 1.0,
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15,
                "cost_usd": None,
            }
        ]
    )
    path = tmp_path / "usage.csv"
    report.write_usage(usage, path)
    text = path.read_text()
    assert "prompt_tokens" in text
    assert "task-1" in text
    assert "15" in text
