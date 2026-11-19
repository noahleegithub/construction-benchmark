"""Compute token costs from a workspace's usage.csv and models.yaml.

Standard short-context token rates only. Cached-input discounts are not applied
because the run records do not expose a cache-read token count.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import yaml


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--models", default="models.yaml")
    args = parser.parse_args()
    workspace = args.workspace

    models = yaml.safe_load((workspace / args.models).read_text())["models"]
    rates = {
        model["id"]: (
            float(model["input_cost_per_mtok"]),
            float(model["output_cost_per_mtok"]),
        )
        for model in models
        if "input_cost_per_mtok" in model and "output_cost_per_mtok" in model
    }

    rows = []
    with (workspace / "usage.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            model_id = row["model_id"]
            if model_id not in rates:
                continue
            prompt = float(row["prompt_tokens"] or 0)
            completion = float(row["completion_tokens"] or 0)
            input_rate, output_rate = rates[model_id]
            input_cost = prompt / 1e6 * input_rate
            output_cost = completion / 1e6 * output_rate
            rows.append(
                {
                    **row,
                    "input_cost_usd": f"{input_cost:.6f}",
                    "output_cost_usd": f"{output_cost:.6f}",
                    "cost_usd": f"{input_cost + output_cost:.6f}",
                }
            )

    fields = list(rows[0].keys()) if rows else []
    with (workspace / "costs.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    by_model: dict[str, float] = {}
    for row in rows:
        by_model[row["model_id"]] = by_model.get(row["model_id"], 0.0) + float(row["cost_usd"])

    lines = [
        "# Cost report",
        "",
        "Standard short-context rates, USD per 1M tokens. Cached-input discounts "
        "are not applied because the runs do not carry a cache-read token count.",
        "",
        "Source: https://openai.com/api/pricing/ (Standard, short context ≤272K), "
        "retrieved 2026-11-19.",
        "",
        "| Model | Total cost (USD) |",
        "|---|---:|",
    ]
    for model_id, cost in sorted(by_model.items()):
        lines.append(f"| {model_id} | ${cost:.4f} |")

    lines += [
        "",
        "| Model | Task | Input tok | Output tok | Input cost | Output cost | Total cost |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in sorted(rows, key=lambda item: (item["model_id"], item["item_id"])):
        lines.append(
            f"| {row['model_id']} | {row['item_id']} | {row['prompt_tokens']} | "
            f"{row['completion_tokens']} | ${float(row['input_cost_usd']):.4f} | "
            f"${float(row['output_cost_usd']):.4f} | ${float(row['cost_usd']):.4f} |"
        )
    (workspace / "cost_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {workspace / 'costs.csv'} and {workspace / 'cost_report.md'}")


if __name__ == "__main__":
    main()
