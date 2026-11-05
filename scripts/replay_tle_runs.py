#!/usr/bin/env python3
"""Replay the archived TLE model answers through this harness.

The public bundle includes per-model output lines for every task, so a
populated workspace can be scored without new API calls. This writes
`runs.jsonl` in the harness schema; `takeoff-bench score` then produces the
same report as a live run.

Usage:
    python scripts/replay_tle_runs.py --workspace study \
        --bundle "data/tle_raw/TLE-prod [dont-delete]"
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from takeoff_bench.schema import load_items  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=ROOT / "study")
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    items = {item.item_id: item for item in load_items(args.workspace)}
    runs_path = args.workspace / "runs.jsonl"
    if runs_path.exists() and args.force:
        runs_path.unlink()

    counters: dict[tuple[str, str], int] = defaultdict(int)
    written = 0
    for path, result in archived(args.bundle / "model_runs" / "runs"):
        task = result.get("task", "").split("/")[-1]
        if task not in items or not result.get("output_lines"):
            continue
        model_id = slug(result.get("model") or path.stem)
        if result.get("error"):
            continue
        instances = []
        for line in result["output_lines"]:
            ring = line.get("ring")
            if not ring or len(ring) < 3:
                continue
            instances.append(
                {"label": line.get("label", ""), "points": [[x / 1000, y / 1000] for x, y in ring]}
            )
        if not instances:
            continue

        key = (task, model_id)
        repeat = counters[key]
        counters[key] += 1
        record = {
            "run_id": uuid.uuid4().hex[:12],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "item_id": task,
            "family": items[task].family,
            "model_id": model_id,
            "provider": "tle-archive",
            "model": result.get("model"),
            "repeat": repeat,
            "prompt_hash": "tle-archive",
            "model_config_hash": "tle-archive",
            "image_sha256": "",
            "image_size": None,
            "dpi": None,
            "max_side": None,
            "raw": None,
            "parsed": {"type": "polygons", "instances": instances},
            "parse_error": None,
            "error": None,
            "latency_ms": None,
            "usage": (result.get("detail") or {}).get("usage") or {},
            "cost_usd": (result.get("detail") or {}).get("cost_usd"),
            "archive_file": path.name,
        }
        with runs_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        written += 1

    print(f"wrote {written} archived runs to {runs_path}")
    return 0


def archived(directory: Path):
    for path in sorted(directory.glob("*.json")):
        try:
            payload = json.loads(path.read_text())
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if isinstance(payload, dict):
            for result in payload.get("results") or []:
                yield path, result


def slug(value: str) -> str:
    value = value.replace(":", "-").replace("/", "-")
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value)
    return value.strip("-") or "model"


if __name__ == "__main__":
    raise SystemExit(main())
