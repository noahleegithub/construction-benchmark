from pathlib import Path

from takeoff_bench import demo, overlay, report, runner


def _only(workspace: Path, provider: str) -> None:
    (workspace / "models.yaml").write_text(
        f"models:\n  - id: {provider}\n    provider: {provider}\n",
        encoding="utf-8",
    )


def test_oracle_scores_one(tmp_path: Path):
    workspace = tmp_path / "oracle"
    demo.create_demo_workspace(workspace)
    _only(workspace, "oracle")
    runner.run(
        workspace,
        workspace / "models.yaml",
        repeats=1,
        force=True,
    )
    summary = report.score_and_report(workspace)
    overall = [row for row in summary if row["family"] == "ALL"][0]
    assert overall["n"] == 3
    assert overall["score"] == 1.0

    run = overlay.find_run(workspace / "runs.jsonl", "demo-rooms", "oracle", 0)
    out = workspace / "overlay.png"
    overlay.draw_overlay(workspace, __item(workspace), run, out)
    assert out.exists() and out.stat().st_size > 5_000


def test_stub_scores_zero(tmp_path: Path):
    workspace = tmp_path / "stub"
    demo.create_demo_workspace(workspace)
    _only(workspace, "stub")
    runner.run(
        workspace,
        workspace / "models.yaml",
        repeats=1,
        force=True,
    )
    summary = report.score_and_report(workspace)
    overall = [row for row in summary if row["family"] == "ALL"][0]
    assert overall["score"] == 0.0
    assert overall["parsed"] == 1.0


def test_runner_is_idempotent(tmp_path: Path):
    workspace = tmp_path / "idem"
    demo.create_demo_workspace(workspace)
    _only(workspace, "oracle")
    first = runner.run(
        workspace,
        workspace / "models.yaml",
        repeats=1,
        force=True,
    )
    second = runner.run(
        workspace,
        workspace / "models.yaml",
        repeats=1,
    )
    assert first == 3
    assert second == 0


def __item(workspace: Path):
    from takeoff_bench.schema import load_items

    return {item.item_id: item for item in load_items(workspace)}["demo-rooms"]
