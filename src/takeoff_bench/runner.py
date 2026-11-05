"""Batch runner.

The run record is the unit of provenance. One line per (item, model, repeat)
holds the exact prompt hash, image hash, raw response, parsed output, usage
and error. Re-running is idempotent unless ``force`` is set; provider errors
are retried on the next invocation, parse errors are kept.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from . import parsing, prompts
from .providers import build_provider
from .render import render_pdf_page
from .schema import Item, load_gt, load_items


def load_models(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    models = data.get("models") or []
    if not isinstance(models, list) or not models:
        raise ValueError(f"{path} needs a non-empty 'models' list")
    for model in models:
        if "id" not in model or "provider" not in model:
            raise ValueError("each model needs 'id' and 'provider'")
    return models


def run(
    workspace: Path,
    models_path: Path,
    *,
    repeats: int = 1,
    family: str | None = None,
    item_id: str | None = None,
    limit: int | None = None,
    force: bool = False,
    dpi: int = 150,
    max_side: int = 2400,
    provider_override: str | None = None,
    runs_path: Path | None = None,
) -> int:
    items = load_items(workspace)
    if family:
        items = [item for item in items if item.family == family]
    if item_id:
        items = [item for item in items if item.item_id == item_id]
    if limit:
        items = items[:limit]
    if not items:
        raise ValueError("no items selected")

    models = load_models(models_path)
    runs_path = runs_path or workspace / "runs.jsonl"
    done = _existing_keys(runs_path) if not force else set()
    cache_dir = workspace / ".cache" / "renders"
    cache_dir.mkdir(parents=True, exist_ok=True)

    total = len(items) * len(models) * repeats
    index = 0
    written = 0

    for item in items:
        system = prompts.SYSTEM
        user = prompts.build_prompt(item)
        image_png, image_size = _render(item, workspace, cache_dir, dpi, max_side)
        image_sha = hashlib.sha256(image_png).hexdigest()
        gt = load_gt(workspace, item)

        for model in models:
            provider_name = provider_override or model["provider"]
            try:
                provider = build_provider(provider_name, model)
            except ValueError as exc:
                print(f"skip {model['id']}: {exc}")
                index += repeats
                continue

            model_key = model["id"]
            model_config_hash = hashlib.sha256(
                json.dumps(model, sort_keys=True).encode("utf-8")
            ).hexdigest()[:16]
            prompt_hash = hashlib.sha256(
                "\n".join(
                    [
                        system,
                        user,
                        str(model.get("model", model_key)),
                        provider_name,
                        model_config_hash,
                        str(dpi),
                        str(max_side),
                    ]
                ).encode("utf-8")
            ).hexdigest()

            for repeat in range(repeats):
                index += 1
                key = (item.item_id, model_key, repeat, prompt_hash)
                if key in done:
                    print(f"[{index}/{total}] skip {item.item_id} {model_key} r{repeat}")
                    continue

                print(f"[{index}/{total}] {item.item_id} {model_key} r{repeat}")
                result = provider.complete(
                    system=system,
                    user=user,
                    image_png=image_png,
                    item=item,
                    gt=gt,
                )

                parsed = None
                parse_error = None
                if result.error is None:
                    try:
                        parsed = parsing.coerce_prediction(
                            parsing.extract_json(result.text), item.output_type
                        )
                    except ValueError as exc:
                        parse_error = str(exc)

                record = {
                    "run_id": uuid.uuid4().hex[:12],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "item_id": item.item_id,
                    "family": item.family,
                    "model_id": model_key,
                    "provider": provider_name,
                    "model": model.get("model", model_key),
                    "repeat": repeat,
                    "prompt_hash": prompt_hash,
                    "model_config_hash": model_config_hash,
                    "image_sha256": image_sha,
                    "image_size": list(image_size),
                    "dpi": dpi,
                    "max_side": max_side,
                    "raw": result.text,
                    "parsed": parsed,
                    "parse_error": parse_error,
                    "error": result.error,
                    "latency_ms": result.latency_ms,
                    "usage": result.usage,
                    "cost_usd": result.cost_usd,
                }
                with runs_path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                written += 1
                if result.error is None:
                    done.add(key)

    print(f"wrote {written} runs to {runs_path}")
    return written


def _existing_keys(path: Path) -> set[tuple[str, str, int, str]]:
    keys: set[tuple[str, str, int, str]] = set()
    if not path.exists():
        return keys
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("error") is None:
                keys.add(
                    (
                        record["item_id"],
                        record["model_id"],
                        int(record.get("repeat", 0)),
                        record["prompt_hash"],
                    )
                )
    return keys


def _render(
    item: Item,
    workspace: Path,
    cache_dir: Path,
    dpi: int,
    max_side: int,
) -> tuple[bytes, tuple[int, int]]:
    key = f"{item.item_id}-{dpi}-{max_side}.png"
    cached = cache_dir / key
    if cached.exists():
        from PIL import Image

        with Image.open(cached) as image:
            return cached.read_bytes(), image.size
    image_png, size = render_pdf_page(
        item.sheet_path(workspace), item.page, dpi=dpi, max_side=max_side
    )
    cached.write_bytes(image_png)
    return image_png, size
