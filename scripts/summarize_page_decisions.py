#!/usr/bin/env python3
"""Summarize synthetic multi-sheet page-relevance decisions."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path, nargs="?", default=Path("studies/page-decisions"))
    args = parser.parse_args()
    rows = [json.loads(line) for line in (args.run_dir / "answers.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    ok = [r for r in rows if r.get("status") == "ok" and r.get("probability") is not None]
    models = sorted({r["model"] for r in rows})
    groups = defaultdict(list)
    for row in ok:
        groups[(row["task_id"], row["model"])].append(row)

    def metrics(rs):
        targets = [r for r in rs if r["role"] == "target"]
        distractors = [r for r in rs if r["role"] == "distractor"]
        if not targets or not distractors:
            return None
        target = targets[0]
        tp = target["probability"]
        dp = [r["probability"] for r in distractors]
        max_d = max(dp)
        rank = 1 + sum(1 for p in dp if p > tp)
        auc = sum(1.0 if tp > p else 0.5 if tp == p else 0.0 for p in dp) / len(dp)
        return {
            "task_id": target["task_id"],
            "family": target.get("family"),
            "model": target["model"],
            "target_probability": tp,
            "target_yes": tp >= 0.5,
            "target_rank": rank,
            "target_margin": tp - max_d,
            "target_auc": auc,
            "distractor_mean": statistics.mean(dp),
            "distractor_max": max_d,
            "distractor_fpr": sum(p >= 0.5 for p in dp) / len(dp),
            "distractor_yes": sum(p >= 0.5 for p in dp),
            "packet_size": len(rs),
            "packet_accuracy": (int(tp >= 0.5) + sum(p < 0.5 for p in dp)) / len(rs),
            "source_task_id": target.get("source_task_id"),
        }

    by_model = defaultdict(list)
    by_task_model = {}
    for (task, model), rs in sorted(groups.items()):
        m = metrics(rs)
        if m:
            by_model[model].append(m)
            by_task_model[(task, model)] = m

    with (args.run_dir / "summary_by_model.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["model", "n_packets", "packet_size", "target_recall", "mean_fpr", "accuracy", "mean_target_rank", "perfect_rank1", "mean_auc", "mean_target_p", "mean_distractor_p", "mean_margin"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for model in models:
            ms = by_model[model]
            if not ms:
                continue
            w.writerow({
                "model": model,
                "n_packets": len(ms),
                "packet_size": ms[0]["packet_size"],
                "target_recall": statistics.mean(int(m["target_yes"]) for m in ms),
                "mean_fpr": statistics.mean(m["distractor_fpr"] for m in ms),
                "accuracy": statistics.mean(m["packet_accuracy"] for m in ms),
                "mean_target_rank": statistics.mean(m["target_rank"] for m in ms),
                "perfect_rank1": sum(m["target_rank"] == 1 for m in ms) / len(ms),
                "mean_auc": statistics.mean(m["target_auc"] for m in ms),
                "mean_target_p": statistics.mean(m["target_probability"] for m in ms),
                "mean_distractor_p": statistics.mean(m["distractor_mean"] for m in ms),
                "mean_margin": statistics.mean(m["target_margin"] for m in ms),
            })

    with (args.run_dir / "summary_by_task_model.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["task_id", "family", "model", "target_probability", "target_yes", "target_rank", "target_margin", "target_auc", "distractor_mean", "distractor_max", "distractor_fpr", "distractor_yes", "packet_size", "packet_accuracy", "source_task_id"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for key in sorted(by_task_model):
            w.writerow(by_task_model[key])

    with (args.run_dir / "per_page.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["task_id", "family", "model", "packet_position", "role", "source_task_id", "source_family", "probability", "yes", "image_path", "ink_fraction", "image_width", "image_height"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in ok:
            w.writerow({k: row.get(k) for k in fields})

    lines = ["# Multi-sheet page relevance", ""]
    lines.append(f"Run: `{args.run_dir / 'answers.jsonl'}`")
    lines.append("")
    lines.append(f"- records: {len(rows)}")
    lines.append(f"- successful: {len(ok)}")
    lines.append(f"- tasks: {len({r['task_id'] for r in ok})}")
    lines.append(f"- models: {', '.join(models)}")
    lines.append("")
    lines.append("Each packet has one source-sheet target and 7 distractors from other task families. "
                 "The target is the positive label; distractors are negatives. This is a synthetic "
                 "packet, not a real multi-page project plan.")
    lines.append("")
    lines.append("## Overall")
    lines.append("")
    lines.append("| Model | Packets | Target recall | Distractor FPR | Accuracy | Mean rank | Rank-1 | Mean AUC | Target p | Distractor p |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for model in models:
        ms = by_model[model]
        if not ms:
            continue
        lines.append(
            f"| `{model}` | {len(ms)} | {statistics.mean(int(m['target_yes']) for m in ms):.3f} | "
            f"{statistics.mean(m['distractor_fpr'] for m in ms):.3f} | {statistics.mean(m['packet_accuracy'] for m in ms):.3f} | "
            f"{statistics.mean(m['target_rank'] for m in ms):.2f} | {sum(m['target_rank'] == 1 for m in ms)}/{len(ms)} | "
            f"{statistics.mean(m['target_auc'] for m in ms):.3f} | {statistics.mean(m['target_probability'] for m in ms):.3f} | "
            f"{statistics.mean(m['distractor_mean'] for m in ms):.3f} |"
        )
    lines.append("")
    lines.append("## By task")
    lines.append("")
    lines.append("| Task | " + " | ".join(f"`{m}`" for m in models) + " |")
    lines.append("|---|" + "|".join("---:" for _ in models) + "|")
    tasks = sorted({k[0] for k in by_task_model})
    for task in tasks:
        cells = []
        for model in models:
            m = by_task_model.get((task, model))
            cells.append(f"rank {m['target_rank']}, p {m['target_probability']:.2f}" if m else "—")
        lines.append(f"| `{task}` | " + " | ".join(cells) + " |")
    lines.append("")
    lines.append("## Misses")
    lines.append("")
    lines.append("Targets that were not the top-ranked page, or were below 0.5:")
    lines.append("")
    lines.append("| Task | Model | Target p | Rank | Max distractor |")
    lines.append("|---|---|---:|---:|---:|")
    misses = [m for ms in by_model.values() for m in ms if m["target_rank"] != 1 or not m["target_yes"]]
    for m in sorted(misses, key=lambda x: (x["target_rank"], -x["target_probability"]))[:20]:
        lines.append(f"| `{m['task_id']}` | `{m['model']}` | {m['target_probability']:.3f} | {m['target_rank']} | {m['distractor_max']:.3f} |")
    lines.append("")
    lines.append("## Caveat")
    lines.append("")
    lines.append("The TLE release has only single-page PDFs. These packets are synthetic: one task source sheet plus distractors from other task families. "
                 "The labels measure source-sheet retrieval, not professional relevance judgments on a real multi-sheet plan. "
                 "The target page is the only positive by construction; some distractors may still contain useful drawing content.")
    (args.run_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote summaries for {len(ok)} records, {len(by_task_model)} task/model packets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
