"""Scoring and reporting."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from .schema import load_gt, load_items
from .scoring import score_item

FIELDS = [
    "run_id",
    "item_id",
    "family",
    "model_id",
    "repeat",
    "status",
    "score",
    "tle_miou",
    "precision",
    "recall",
    "f1",
    "count_ratio",
    "tp",
    "fp",
    "fn",
    "n_pred",
    "n_gt",
    "verdict_accuracy",
    "measurement_accuracy",
    "measure_error",
    "evidence_rate",
    "abstained",
    "prompt_tokens",
    "completion_tokens",
    "total_tokens",
    "cost_usd",
    "error",
]

USAGE_FIELDS = [
    "model_id",
    "item_id",
    "family",
    "runs",
    "scored",
    "completion",
    "prompt_tokens",
    "completion_tokens",
    "total_tokens",
    "cost_usd",
    "score",
]


def score_runs(
    workspace: Path,
    runs_path: Path,
    *,
    iou_threshold: float = 0.5,
) -> list[dict[str, Any]]:
    items = {item.item_id: item for item in load_items(workspace)}
    rows: list[dict[str, Any]] = []

    with runs_path.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            item = items.get(record["item_id"])
            if item is None:
                continue
            row = {
                "run_id": record.get("run_id"),
                "item_id": item.item_id,
                "family": item.family,
                "model_id": record["model_id"],
                "repeat": record.get("repeat", 0),
                "status": "scored",
                "error": "",
            }
            usage = record.get("usage") or {}
            prompt_tokens = usage.get("prompt_tokens")
            completion_tokens = usage.get("completion_tokens")
            total_tokens = usage.get("total_tokens")
            if total_tokens is None and isinstance(prompt_tokens, (int, float)) and isinstance(
                completion_tokens, (int, float)
            ):
                total_tokens = prompt_tokens + completion_tokens
            row.update(
                {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "cost_usd": record.get("cost_usd"),
                }
            )
            if record.get("error"):
                row["status"] = "error"
                row["error"] = str(record["error"])[:300]
            elif record.get("parsed") is None:
                row["status"] = "parse_error"
                row["error"] = str(record.get("parse_error") or "no parsed output")[:300]
            else:
                try:
                    result = score_item(
                        record["parsed"],
                        load_gt(workspace, item),
                        iou_threshold=iou_threshold,
                    )
                except Exception as exc:  # noqa: BLE001 - a bad item must not stop the batch
                    row["status"] = "score_error"
                    row["error"] = f"{type(exc).__name__}: {exc}"[:300]
                else:
                    row.update(
                        {
                            "score": result.get("score"),
                            "tle_miou": (
                                result["matched_iou_sum"] / result["n_gt"]
                                if result.get("matched_iou_sum") is not None
                                and result.get("n_gt")
                                else None
                            ),
                            "precision": result.get("precision"),
                            "recall": result.get("recall"),
                            "f1": result.get("f1"),
                            "count_ratio": result.get("count_ratio"),
                            "tp": result.get("tp"),
                            "fp": result.get("fp"),
                            "fn": result.get("fn"),
                            "n_pred": result.get("n_pred"),
                            "n_gt": result.get("n_gt"),
                            "verdict_accuracy": result.get("verdict_accuracy"),
                            "measurement_accuracy": result.get("measurement_accuracy"),
                            "measure_error": result.get("measure_error"),
                            "evidence_rate": result.get("evidence_rate"),
                            "abstained": result.get("abstained"),
                        }
                    )
            rows.append(row)
    return rows


def write_scores(rows: list[dict[str, Any]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in FIELDS})


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(row["model_id"], row["family"])].append(row)
        groups[(row["model_id"], "ALL")].append(row)

    summary = []
    for (model_id, family), group in sorted(groups.items()):
        scored = [row for row in group if row["status"] == "scored"]
        attempted = len(group)
        values = [row["score"] for row in scored if isinstance(row.get("score"), (int, float))]
        score_all = (
            sum(
                row["score"] if row["status"] == "scored" and isinstance(row.get("score"), (int, float)) else 0.0
                for row in group
            )
            / attempted
            if attempted
            else None
        )
        summary.append(
            {
                "model_id": model_id,
                "family": family,
                "n": len(scored),
                "runs": attempted,
                "attempted": attempted,
                "scored": len(scored),
                "completion": len(scored) / attempted if attempted else None,
                "score": mean(values) if values else None,
                "score_all": score_all,
                "tle_miou": _mean(scored, "tle_miou"),
                "sd": pstdev(values) if len(values) > 1 else None,
                "precision": _mean(scored, "precision"),
                "recall": _mean(scored, "recall"),
                "count_ratio": _mean(scored, "count_ratio"),
                "verdict_accuracy": _mean(scored, "verdict_accuracy"),
                "measurement_accuracy": _mean(scored, "measurement_accuracy"),
                "measure_error": _mean(scored, "measure_error"),
                "evidence_rate": _mean(scored, "evidence_rate"),
                "prompt_tokens": _sum(group, "prompt_tokens"),
                "completion_tokens": _sum(group, "completion_tokens"),
                "total_tokens": _sum(group, "total_tokens"),
                "cost_usd": _sum(group, "cost_usd"),
                "parsed": len(scored) / attempted if attempted else None,
                "errors": attempted - len(scored),
            }
        )
    return summary


def task_usage(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate token usage and cost by model and benchmark item."""
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(row["model_id"], row["item_id"], row["family"])].append(row)

    usage = []
    for (model_id, item_id, family), group in sorted(groups.items()):
        scored = [row for row in group if row["status"] == "scored"]
        values = [row["score"] for row in scored if isinstance(row.get("score"), (int, float))]
        runs = len(group)
        usage.append(
            {
                "model_id": model_id,
                "item_id": item_id,
                "family": family,
                "runs": runs,
                "scored": len(scored),
                "completion": len(scored) / runs if runs else None,
                "prompt_tokens": _sum(group, "prompt_tokens"),
                "completion_tokens": _sum(group, "completion_tokens"),
                "total_tokens": _sum(group, "total_tokens"),
                "cost_usd": _sum(group, "cost_usd"),
                "score": mean(values) if values else None,
            }
        )
    return usage


def write_usage(usage: list[dict[str, Any]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=USAGE_FIELDS)
        writer.writeheader()
        for row in usage:
            writer.writerow({field: row.get(field, "") for field in USAGE_FIELDS})


def format_usage(usage: list[dict[str, Any]], title: str = "Per-task usage") -> str:
    lines = [
        f"# {title}",
        "",
        "| Model | Task | Family | Runs | Scored | Input tok | Output tok | Total tok | Cost USD | Score |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in usage:
        lines.append(
            "| {model} | {item} | {family} | {runs} | {scored} | {prompt} | {completion} | "
            "{total} | {cost} | {score} |".format(
                model=row["model_id"],
                item=row["item_id"],
                family=row["family"],
                runs=row["runs"],
                scored=row["scored"],
                prompt=_fmt(row["prompt_tokens"], 0),
                completion=_fmt(row["completion_tokens"], 0),
                total=_fmt(row["total_tokens"], 0),
                cost=_fmt(row["cost_usd"], 4),
                score=_fmt(row["score"], 3),
            )
        )
    lines.append("")
    return "\n".join(lines)


def print_usage_dataframe(usage: list[dict[str, Any]]) -> None:
    import pandas as pd

    frame = pd.DataFrame(usage)
    if frame.empty:
        print("No usage records.")
        return
    frame = frame.rename(
        columns={
            "model_id": "Model",
            "item_id": "Task",
            "family": "Family",
            "runs": "Runs",
            "scored": "Scored",
            "completion": "Comp.",
            "prompt_tokens": "Input tok",
            "completion_tokens": "Output tok",
            "total_tokens": "Total tok",
            "cost_usd": "Cost USD",
            "score": "Score",
        }
    )
    for column in ("Input tok", "Output tok", "Total tok"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce").astype("Int64")
    frame["Cost USD"] = pd.to_numeric(frame["Cost USD"], errors="coerce")
    with pd.option_context(
        "display.max_rows", None, "display.width", 220, "display.max_columns", None
    ):
        print(
            frame.to_string(
                index=False,
                float_format=lambda value: f"{value:.3f}",
                na_rep="-",
            )
        )


def format_report(summary: list[dict[str, Any]], title: str = "Results") -> str:
    lines = [
        f"# {title}",
        "",
        "| Model | Family | Att. | Scored | Comp. | Score | Fail=0 | TLE mIoU | Prec. | Rec. | Verdict | Meas. err | Evidence | Errors |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary:
        lines.append(
            "| {model} | {family} | {attempted} | {scored} | {completion} | {score} | "
            "{score_all} | {tle} | {precision} | {recall} | {verdict} | {measure} | "
            "{evidence} | {errors} |".format(
                model=row["model_id"],
                family=row["family"],
                attempted=row["attempted"],
                scored=row["scored"],
                completion=_fmt(row["completion"], 2),
                score=_fmt(row["score"], 3),
                score_all=_fmt(row["score_all"], 3),
                tle=_fmt(row["tle_miou"], 3),
                precision=_fmt(row["precision"], 3),
                recall=_fmt(row["recall"], 3),
                verdict=_fmt(row.get("verdict_accuracy"), 3),
                measure=_fmt(row.get("measure_error"), 1),
                evidence=_fmt(row.get("evidence_rate"), 3),
                errors=row["errors"],
            )
        )
    lines.append("")
    return "\n".join(lines)


def print_dataframe(summary: list[dict[str, Any]]) -> None:
    import pandas as pd

    frame = pd.DataFrame(summary)
    if frame.empty:
        print("No scored runs.")
        return
    frame = frame.rename(
        columns={
            "model_id": "Model",
            "family": "Family",
            "attempted": "Att.",
            "scored": "Scored",
            "completion": "Comp.",
            "score": "Score",
            "score_all": "Fail=0",
            "tle_miou": "TLE mIoU",
            "sd": "SD",
            "precision": "Precision",
            "recall": "Recall",
            "count_ratio": "Count ratio",
            "verdict_accuracy": "Verdict",
            "measurement_accuracy": "Meas. acc",
            "measure_error": "Meas. err",
            "evidence_rate": "Evidence",
            "errors": "Errors",
        }
    )
    frame["_overall"] = frame["Family"].eq("ALL")
    frame = frame.sort_values(
        ["_overall", "Family", "Score"], ascending=[False, True, False]
    ).drop(columns="_overall")
    columns = [
        "Model",
        "Family",
        "Att.",
        "Scored",
        "Comp.",
        "Score",
        "Fail=0",
        "TLE mIoU",
        "Precision",
        "Recall",
        "Verdict",
        "Meas. err",
        "Evidence",
        "Errors",
    ]
    frame = frame[[column for column in columns if column in frame.columns]]
    with pd.option_context(
        "display.max_rows", None, "display.width", 260, "display.max_columns", None
    ):
        print(
            frame.to_string(
                index=False,
                float_format=lambda value: f"{value:.3f}",
                na_rep="-",
            )
        )


def score_and_report(
    workspace: Path,
    runs_path: Path | None = None,
    out_path: Path | None = None,
    *,
    iou_threshold: float = 0.5,
) -> list[dict[str, Any]]:
    runs_path = runs_path or workspace / "runs.jsonl"
    out_path = out_path or workspace / "report.md"
    if not runs_path.exists():
        raise FileNotFoundError(runs_path)
    rows = score_runs(workspace, runs_path, iou_threshold=iou_threshold)
    write_scores(rows, workspace / "scores.csv")
    usage = task_usage(rows)
    write_usage(usage, workspace / "usage.csv")
    (workspace / "usage_report.md").write_text(format_usage(usage), encoding="utf-8")
    summary = summarize(rows)
    text = format_report(summary) + "\n" + format_usage(usage)
    out_path.write_text(text, encoding="utf-8")
    print_dataframe(summary)
    return summary


def _mean(rows: list[dict[str, Any]], key: str) -> float | None:
    values = [row[key] for row in rows if isinstance(row.get(key), (int, float))]
    return mean(values) if values else None


def _sum(rows: list[dict[str, Any]], key: str) -> float | None:
    values = [row[key] for row in rows if isinstance(row.get(key), (int, float))]
    return sum(values) if values else None


def _fmt(value: float | None, digits: int) -> str:
    return f"{value:.{digits}f}" if isinstance(value, (int, float)) else "-"
