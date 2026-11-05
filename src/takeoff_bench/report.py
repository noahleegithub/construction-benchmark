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
    "error",
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
                                result.get("matched_iou_sum", 0) / result["n_gt"]
                                if result.get("n_gt")
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
        errors = sum(1 for row in group if row["status"] == "error")
        values = [row["score"] for row in scored if isinstance(row.get("score"), (int, float))]
        summary.append(
            {
                "model_id": model_id,
                "family": family,
                "n": len(scored),
                "runs": len(group),
                "score": mean(values) if values else None,
                "tle_miou": _mean(scored, "tle_miou"),
                "sd": pstdev(values) if len(values) > 1 else None,
                "precision": _mean(scored, "precision"),
                "recall": _mean(scored, "recall"),
                "count_ratio": _mean(scored, "count_ratio"),
                "parsed": len(scored) / len(group) if group else None,
                "errors": errors,
            }
        )
    return summary


def format_report(summary: list[dict[str, Any]], title: str = "Results") -> str:
    lines = [
        f"# {title}",
        "",
        "| Model | Family | n | Score | TLE mIoU | SD | Precision | Recall | Count ratio | Parsed | Errors |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary:
        lines.append(
            "| {model} | {family} | {n} | {score} | {tle} | {sd} | {precision} | {recall} | "
            "{ratio} | {parsed} | {errors} |".format(
                model=row["model_id"],
                family=row["family"],
                n=row["n"],
                score=_fmt(row["score"], 3),
                tle=_fmt(row["tle_miou"], 3),
                sd=_fmt(row["sd"], 3),
                precision=_fmt(row["precision"], 3),
                recall=_fmt(row["recall"], 3),
                ratio=_fmt(row["count_ratio"], 2),
                parsed=_fmt(row["parsed"], 2),
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
            "n": "n",
            "runs": "Runs",
            "score": "Score",
            "tle_miou": "TLE mIoU",
            "sd": "SD",
            "precision": "Precision",
            "recall": "Recall",
            "count_ratio": "Count ratio",
            "parsed": "Parsed",
            "errors": "Errors",
        }
    )
    frame["_overall"] = frame["Family"].eq("ALL")
    frame = frame.sort_values(
        ["_overall", "Family", "Score"], ascending=[False, True, False]
    ).drop(columns="_overall")
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
    summary = summarize(rows)
    text = format_report(summary)
    out_path.write_text(text, encoding="utf-8")
    print_dataframe(summary)
    return summary


def _mean(rows: list[dict[str, Any]], key: str) -> float | None:
    values = [row[key] for row in rows if isinstance(row.get(key), (int, float))]
    return mean(values) if values else None


def _fmt(value: float | None, digits: int) -> str:
    return f"{value:.{digits}f}" if isinstance(value, (int, float)) else "-"
