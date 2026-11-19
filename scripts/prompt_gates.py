"""Read prompt-study runs and print the gate tables.

Usage:
    python scripts/prompt_gates.py \
      --baseline studies/prompt-sensitivity/base32 \
      --noise studies/prompt-sensitivity/noise \
      --control studies/prompt-sensitivity/control
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

from takeoff_bench import report


def stats(values: list[float]) -> tuple[float | None, float | None, int]:
    if not values:
        return None, None, 0
    return (
        statistics.mean(values),
        statistics.pstdev(values) if len(values) > 1 else None,
        len(values),
    )


def rows_for(workspace: Path, runs: Path | None = None) -> list[dict]:
    return report.score_runs(workspace, runs or workspace / "runs.jsonl")


def raw_for(workspace: Path, runs: Path | None = None) -> dict[tuple[str, str, str], list[str]]:
    cells: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    path = runs or workspace / "runs.jsonl"
    for line in path.open(encoding="utf-8"):
        record = json.loads(line)
        if not str(record.get("model_id", "")).startswith("gw-"):
            continue
        key = (
            record.get("prompt_variant", "baseline"),
            record["item_id"],
            record["model_id"],
        )
        cells[key].append(str(record.get("raw") or ""))
    return cells


def by_cell(rows: list[dict]) -> dict[tuple[str, str, str], list[dict]]:
    cells: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        if str(row.get("model_id", "")).startswith("gw-"):
            cells[(row["prompt_variant"], row["item_id"], row["model_id"])].append(row)
    return cells


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--noise", type=Path)
    parser.add_argument("--control", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    baseline_rows = rows_for(args.baseline)
    baseline = by_cell(baseline_rows)
    out: dict[str, object] = {}

    print("# Prompt sensitivity gates\n")
    print("## A. Baseline, 32k, single epoch\n")
    print("| Variant | Item | Model | Runs | Scored | Completion | F1 | Recall | Precision |")
    print("|---|---|---|---:|---:|---:|---:|---:|---:|")
    for (variant, item, model), group in sorted(baseline.items()):
        scored = [row for row in group if row["status"] == "scored"]
        f1 = [row["f1"] for row in scored if isinstance(row.get("f1"), (int, float))]
        rec = [row["recall"] for row in scored if isinstance(row.get("recall"), (int, float))]
        pre = [row["precision"] for row in scored if isinstance(row.get("precision"), (int, float))]
        print(
            f"| {variant} | {item} | {model} | {len(group)} | {len(scored)} | "
            f"{len(scored) / len(group):.2f} | "
            f"{statistics.mean(f1) if f1 else float('nan'):.3f} | "
            f"{statistics.mean(rec) if rec else float('nan'):.3f} | "
            f"{statistics.mean(pre) if pre else float('nan'):.3f} |"
        )
    out["baseline_cells"] = len(baseline)
    out["baseline_scored"] = sum(
        1 for group in baseline.values() for row in group if row["status"] == "scored"
    )
    out["baseline_runs"] = sum(len(group) for group in baseline.values())

    if args.noise:
        noise_rows = rows_for(args.noise)
        noise = by_cell(noise_rows)
        raw_cells = raw_for(args.noise)
        print("\n## B. Noise floor, 5 repeats\n")
        print("| Item | Model | Repeats | Distinct raw | F1 mean | F1 SD |")
        print("|---|---|---:|---:|---:|---:|")
        variances = []
        for (variant, item, model), group in sorted(noise.items()):
            scored = [row for row in group if row["status"] == "scored"]
            values = [row["f1"] for row in scored if isinstance(row.get("f1"), (int, float))]
            mean, sd, n = stats(values)
            if sd is not None:
                variances.append((n, sd))
            distinct = len(set(raw_cells.get((variant, item, model), [])))
            print(
                f"| {item} | {model} | {len(group)} | {distinct} | "
                f"{mean if mean is not None else float('nan'):.3f} | "
                f"{sd if sd is not None else float('nan'):.3f} |"
            )
        if variances:
            denominator = sum(n - 1 for n, _ in variances)
            pooled = math.sqrt(sum((n - 1) * sd**2 for n, sd in variances) / denominator)
            print(f"\nPooled within-cell F1 SD: **{pooled:.4f}**")
            out["pooled_f1_sd"] = pooled
        out["noise_cells"] = len(noise)
        out["noise_scored"] = sum(
            1 for group in noise.values() for row in group if row["status"] == "scored"
        )

    if args.control:
        control_rows = rows_for(args.control)
        control = by_cell(control_rows)
        print("\n## C. Positive control, constraints removed\n")
        print("| Item | Model | Baseline F1 | Control F1 | Delta F1 | Baseline recall | Control recall | Delta recall |")
        print("|---|---|---:|---:|---:|---:|---:|---:|")
        deltas = defaultdict(list)
        for (variant, item, model), group in sorted(control.items()):
            base_group = baseline.get(("baseline", item, model), [])
            base_scored = [row for row in base_group if row["status"] == "scored"]
            ctrl_scored = [row for row in group if row["status"] == "scored"]
            if not base_scored or not ctrl_scored:
                continue
            base_f1 = statistics.mean(
                row["f1"] for row in base_scored if isinstance(row.get("f1"), (int, float))
            )
            ctrl_f1 = statistics.mean(
                row["f1"] for row in ctrl_scored if isinstance(row.get("f1"), (int, float))
            )
            base_rec = statistics.mean(
                row["recall"] for row in base_scored if isinstance(row.get("recall"), (int, float))
            )
            ctrl_rec = statistics.mean(
                row["recall"] for row in ctrl_scored if isinstance(row.get("recall"), (int, float))
            )
            deltas[model].append(ctrl_rec - base_rec)
            print(
                f"| {item} | {model} | {base_f1:.3f} | {ctrl_f1:.3f} | "
                f"{ctrl_f1 - base_f1:+.3f} | {base_rec:.3f} | {ctrl_rec:.3f} | "
                f"{ctrl_rec - base_rec:+.3f} |"
            )
        for model, values in sorted(deltas.items()):
            print(f"\n{model}: median recall delta {statistics.median(values):+.3f} over {len(values)} items")
        out["control_median_recall_delta"] = {
            model: statistics.median(values) for model, values in deltas.items()
        }

    if args.out:
        args.out.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
