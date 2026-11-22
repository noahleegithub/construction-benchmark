#!/usr/bin/env python3
"""Ask a Valen decision model whether each OCG layer is useful for a TLE task.

The image is a render of exactly one optional-content group, with every other
group hidden. The prompt gives the task but deliberately omits the layer name,
so the answer is based on visible content rather than metadata.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pymupdf
from PIL import Image

API_URL = "https://api.valen-team.workers.dev/v1/decisions"
ORIGIN = "https://valen-team.github.io"
TASK_DATA = Path(".hermes/cache/tle_web/data.js")
RAW_ROOT = Path("data/tle_raw/TLE-prod [dont-delete]/pdfs/release")
DEFAULT_OUT = Path("studies/ocg-decisions")


def load_tasks() -> dict[str, dict]:
    text = TASK_DATA.read_text(encoding="utf-8").split("=", 1)[1].strip().rstrip(";")
    data = json.loads(text)
    return {task["taskId"]: task for task in data["tasks"]}


def safe_name(text: str, limit: int = 80) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("_")
    return text[:limit] or "layer"


def layer_records(pdf: Path) -> list[dict]:
    doc = pymupdf.open(pdf)
    configs = doc.layer_ui_configs()
    ocgs = doc.get_ocgs()
    by_name: dict[str, list[int]] = {}
    for xref, info in ocgs.items():
        by_name.setdefault(info.get("name", ""), []).append(xref)
    records = []
    for entry in configs:
        records.append(
            {
                "number": entry["number"],
                "name": entry["text"],
                "depth": entry.get("depth", 0),
                "xref": (by_name.get(entry["text"]) or [None])[0],
            }
        )
    return records


def render_layer(pdf: Path, number: int, max_side: int) -> tuple[bytes, dict]:
    doc = pymupdf.open(pdf)
    configs = doc.layer_ui_configs()
    if not any(entry["number"] == number for entry in configs):
        raise ValueError(f"layer {number} not present")
    for entry in configs:
        doc.set_layer_ui_config(entry["number"], 0 if entry["number"] == number else 2)
    page = doc[0]
    pix = page.get_pixmap(dpi=150, alpha=False)
    img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")

    # Crop to non-white content, with a small margin. This makes sparse OCG
    # layers legible without changing which layer is shown.
    gray = img.convert("L")
    bbox = gray.point(lambda v: 255 if v < 245 else 0).getbbox()
    crop = None
    if bbox:
        pad_x = max(20, int((bbox[2] - bbox[0]) * 0.08))
        pad_y = max(20, int((bbox[3] - bbox[1]) * 0.08))
        left = max(0, bbox[0] - pad_x)
        top = max(0, bbox[1] - pad_y)
        right = min(img.width, bbox[2] + pad_x)
        bottom = min(img.height, bbox[3] + pad_y)
        crop = [left, top, right, bottom]
        img = img.crop((left, top, right, bottom))
    if max(img.size) > max_side:
        scale = max_side / max(img.size)
        img = img.resize((round(img.width * scale), round(img.height * scale)), Image.Resampling.LANCZOS)

    out = io.BytesIO()
    img.save(out, format="PNG", optimize=True)
    png = out.getvalue()
    # Ink fraction over the rendered layer, before cropping, using a coarse
    # sample to keep this cheap.
    sample = gray.resize((min(800, gray.width), max(1, round(gray.height * min(800, gray.width) / gray.width))))
    try:
        pixels = list(sample.get_flattened_data())
    except AttributeError:
        pixels = list(sample.getdata())
    ink = sum(1 for value in pixels if value < 245) / max(1, len(pixels))
    return png, {
        "crop_bbox": crop,
        "image_width": img.width,
        "image_height": img.height,
        "ink_fraction": round(ink, 6),
        "image_sha256": hashlib.sha256(png).hexdigest(),
    }


def prompt_for(task: dict) -> tuple[str, str]:
    task_text = task.get("promptBrief") or task.get("shortTitle") or task["taskId"]
    text = (
        "You are looking at exactly one optional-content-group (OCG) layer from an "
        "architectural drawing. Every other layer is hidden; the image is the layer's "
        "visible content, cropped to its ink and rendered on white.\n\n"
        f"Task: {task_text}\n\n"
        "Decide whether this layer contains visible drawing content that is useful for "
        "completing the task. Useful means geometry, symbols, text, dimensions, or material "
        "information that directly helps locate, measure, classify, or verify what the task "
        "asks for. Not useful means blank, unrelated annotation, title block, or decorative "
        "content with no bearing on the task."
    )
    question = (
        "The visible content of this single OCG layer is useful for completing the stated task."
    )
    return text, question


def post_decision(model: str, text: str, question: str, png: bytes, temperature: float) -> dict:
    image_url = "data:image/png;base64," + base64.b64encode(png).decode("ascii")
    body = {
        "model": model,
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": text},
                    {"type": "input_image", "image_url": image_url},
                ],
            }
        ],
        "questions": [
            {"name": "layer_useful", "type": "predicate", "instructions": question}
        ],
        "temperature": temperature,
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "Origin": ORIGIN,
            "User-Agent": "Mozilla/5.0",
        },
        method="POST",
    )
    last = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=180) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")
            last = {"status": exc.code, "detail": detail[:1000]}
            if exc.code == 429 or 500 <= exc.code < 600:
                time.sleep(min(60, 5 * (attempt + 1)))
                continue
            raise RuntimeError(f"HTTP {exc.code}: {detail[:1000]}") from exc
        except (TimeoutError, urllib.error.URLError) as exc:
            last = {"status": None, "detail": str(exc)}
            time.sleep(min(60, 5 * (attempt + 1)))
    raise RuntimeError(f"request failed after retries: {last}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--pdf", action="append", default=[], help="Task id or PDF stem; repeatable")
    parser.add_argument("--models", default="valen-0.8b,valen-2b,valen-4b")
    parser.add_argument("--limit", type=int, default=0, help="Max layers per PDF (0 = all)")
    parser.add_argument("--max-side", type=int, default=1200)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--save-images", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    records_path = args.out / "answers.jsonl"
    images_dir = args.out / "images"
    existing = set()
    if args.resume and records_path.exists():
        for line in records_path.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
                existing.add((r["task_id"], r["layer_number"], r["model"]))
            except (KeyError, json.JSONDecodeError):
                pass
    tasks = load_tasks()
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    wanted = set(args.pdf)
    pdfs = sorted(RAW_ROOT.rglob("*.pdf"))
    selected = []
    for pdf in pdfs:
        task_id = pdf.parent.name
        if wanted and task_id not in wanted and pdf.stem not in wanted:
            continue
        records = layer_records(pdf)
        if records:
            selected.append((pdf, task_id, records))
    print(f"{len(selected)} PDFs with layers; {sum(len(r) for _, _, r in selected)} layer renders")
    run_start = datetime.now(timezone.utc).isoformat()
    with records_path.open("a", encoding="utf-8") as out:
        for pdf, task_id, records in selected:
            task = tasks.get(task_id)
            if not task:
                print(f"skip {task_id}: no TLE task text")
                continue
            text, question = prompt_for(task)
            print(f"\n== {task_id} ({len(records)} layers) ==")
            for index, layer in enumerate(records, start=1):
                if args.limit and index > args.limit:
                    break
                try:
                    png, meta = render_layer(pdf, layer["number"], args.max_side)
                except Exception as exc:
                    print(f"  render {index}/{len(records)} {layer['name']}: ERROR {exc}")
                    continue
                image_path = None
                if args.save_images and png:
                    target = images_dir / task_id / f"{index:03d}__{safe_name(layer['name'])}.png"
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(png)
                    image_path = str(target)
                for model in models:
                    key = (task_id, layer["number"], model)
                    if key in existing:
                        print(f"  {index:03d}/{len(records)} {layer['name']} [{model}] exists")
                        continue
                    probability = None
                    try:
                        response = post_decision(model, text, question, png, args.temperature)
                        answer = response.get("answers", [{}])[0]
                        probability = answer.get("probability")
                        record = {
                            "task_id": task_id,
                            "family": task.get("family"),
                            "task_text": text,
                            "pdf": str(pdf),
                            "layer_number": layer["number"],
                            "layer_name": layer["name"],
                            "layer_depth": layer["depth"],
                            "layer_xref": layer["xref"],
                            "model": model,
                            "model_id": response.get("model_id"),
                            "model_name": response.get("model"),
                            "probability": probability,
                            "yes": None if probability is None else probability >= 0.5,
                            "usage": response.get("usage"),
                            "timing": response.get("timing"),
                            "image_path": image_path,
                            **meta,
                            "run_start": run_start,
                            "status": "ok",
                        }
                    except Exception as exc:
                        record = {
                            "task_id": task_id,
                            "family": task.get("family"),
                            "task_text": text,
                            "pdf": str(pdf),
                            "layer_number": layer["number"],
                            "layer_name": layer["name"],
                            "layer_depth": layer["depth"],
                            "layer_xref": layer["xref"],
                            "model": model,
                            "status": "error",
                            "error": str(exc)[:1000],
                            **meta,
                            "run_start": run_start,
                        }
                    out.write(json.dumps(record, ensure_ascii=False) + "\n")
                    out.flush()
                    if record["status"] == "ok":
                        value = record.get("probability")
                        shown = "None" if value is None else f"{value:.3f}"
                        print(f"  {index:03d}/{len(records)} {layer['name']} [{model}] p={shown}")
                    else:
                        print(f"  {index:03d}/{len(records)} {layer['name']} [{model}] ERROR {record['error'][:180]}")
                    time.sleep(0.05)
    print(f"\nwrote {records_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
