#!/usr/bin/env python3
"""Summarize Valen OCG-layer decision runs."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path


def quantiles(values: list[float]) -> tuple[float, float]:
    if len(values) < 2:
        return (values[0] if values else 0.0, values[0] if values else 0.0)
    q = statistics.quantiles(values, n=10)
    return q[0], q[-1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path, nargs="?", default=Path("studies/ocg-decisions"))
    args = parser.parse_args()
    records_path = args.run_dir / "answers.jsonl"
    rows = [json.loads(line) for line in records_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    ok = [r for r in rows if r.get("status") == "ok" and r.get("probability") is not None]
    models = sorted({r["model"] for r in rows})
    tasks = sorted({r["task_id"] for r in rows})

    by_model = defaultdict(list)
    by_task_model = defaultdict(list)
    by_layer = defaultdict(lambda: defaultdict(list))
    layer_sample = {}
    for r in ok:
        by_model[r["model"]].append(r)
        by_task_model[(r["task_id"], r["model"])].append(r)
        by_layer[(r["task_id"], r["layer_number"], r["layer_name"])][r["model"]].append(r["probability"])
        layer_sample[(r["task_id"], r["layer_number"], r["layer_name"])] = r

    def stats(rs):
        vals = [r["probability"] for r in rs]
        p10, p90 = quantiles(vals)
        return {
            "n": len(vals),
            "yes": sum(v >= 0.5 for v in vals),
            "yes_rate": sum(v >= 0.5 for v in vals) / len(vals) if vals else 0.0,
            "mean": statistics.mean(vals) if vals else 0.0,
            "median": statistics.median(vals) if vals else 0.0,
            "p10": p10,
            "p90": p90,
        }

    with (args.run_dir / "summary_by_model.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["model", "n", "yes", "yes_rate", "mean", "median", "p10", "p90"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for model in models:
            writer.writerow({"model": model, **stats(by_model[model])})

    with (args.run_dir / "summary_by_task_model.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["task_id", "family", "model", "n", "yes", "yes_rate", "mean", "median", "p10", "p90"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for (task, model), rs in sorted(by_task_model.items()):
            writer.writerow({
                "task_id": task,
                "family": rs[0].get("family"),
                "model": model,
                **stats(rs),
            })

    with (args.run_dir / "per_layer.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["task_id", "family", "layer_number", "layer_name", "layer_depth", "layer_xref"]
        fields += models
        fields += ["mean_probability", "consensus_yes", "n_models", "max_model_yes", "min_model_yes", "ink_fraction", "image_path"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for key, model_values in sorted(by_layer.items()):
            task, number, name = key
            sample = layer_sample[key]
            means = [statistics.mean(v) for v in model_values.values()]
            yes = [statistics.mean(v) >= 0.5 for v in model_values.values()]
            row = {
                "task_id": task,
                "family": sample.get("family"),
                "layer_number": number,
                "layer_name": name,
                "layer_depth": sample.get("layer_depth"),
                "layer_xref": sample.get("layer_xref"),
                "mean_probability": round(statistics.mean(means), 6) if means else "",
                "consensus_yes": sum(yes) >= (len(yes) + 1) // 2,
                "n_models": len(model_values),
                "max_model_yes": max(yes) if yes else None,
                "min_model_yes": min(yes) if yes else None,
                "ink_fraction": sample.get("ink_fraction"),
                "image_path": sample.get("image_path"),
            }
            for model in models:
                vals = model_values.get(model)
                row[model] = round(vals[0], 6) if vals else ""
            writer.writerow(row)

    lines = ["# OCG layer usefulness decisions", ""]
    lines.append(f"Run: `{records_path}`")
    lines.append("")
    lines.append(f"- records: {len(rows)}")
    lines.append(f"- successful: {len(ok)}")
    lines.append(f"- models: {', '.join(models)}")
    lines.append(f"- tasks: {len(tasks)}")
    lines.append(f"- unique layers: {len(by_layer)}")
    lines.append("")
    lines.append("## Overall by model")
    lines.append("")
    lines.append("| Model | n | Yes | Yes rate | Mean | Median | p10 | p90 |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for model in models:
        s = stats(by_model[model])
        lines.append(
            f"| `{model}` | {s['n']} | {s['yes']} | {s['yes_rate']:.3f} | {s['mean']:.3f} | "
            f"{s['median']:.3f} | {s['p10']:.3f} | {s['p90']:.3f} |"
        )
    lines.append("")
    lines.append("## Yes rate by task")
    lines.append("")
    lines.append("| Task | " + " | ".join(f"`{m}`" for m in models) + " |")
    lines.append("|---|" + "|".join("---:" for _ in models) + "|")
    for task in tasks:
        cells = []
        for model in models:
            rs = by_task_model.get((task, model), [])
            cells.append(f"{stats(rs)['yes_rate']:.2f} ({stats(rs)['n']})" if rs else "—")
        lines.append(f"| `{task}` | " + " | ".join(cells) + " |")
    lines.append("")
    lines.append("## Highest consensus layers")
    lines.append("")
    ranked = sorted(
        by_layer.items(),
        key=lambda item: statistics.mean(statistics.mean(v) for v in item[1].values()),
        reverse=True,
    )
    lines.append("| Task | Layer | Mean p | Models |")
    lines.append("|---|---|---:|---:|")
    for (task, _, name), vals in ranked[:15]:
        mean_p = statistics.mean(statistics.mean(v) for v in vals.values())
        lines.append(f"| `{task}` | `{name}` | {mean_p:.3f} | {len(vals)} |")
    lines.append("")
    lines.append("## Lowest consensus layers")
    lines.append("")
    lines.append("| Task | Layer | Mean p | Models |")
    lines.append("|---|---|---:|---:|")
    for (task, _, name), vals in ranked[-15:]:
        mean_p = statistics.mean(statistics.mean(v) for v in vals.values())
        lines.append(f"| `{task}` | `{name}` | {mean_p:.3f} | {len(vals)} |")
    lines.append("")
    lines.append("## Caveat")
    lines.append("")
    lines.append("These are model judgments about a single layer, not accuracy against a human label. "
                 "The layer name is recorded but was not shown to the model. The image is the layer alone, "
                 "cropped to its ink and rendered on white.")
    (args.run_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote summaries for {len(rows)} records, {len(ok)} successful")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
