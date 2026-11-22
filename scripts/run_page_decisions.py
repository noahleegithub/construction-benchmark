#!/usr/bin/env python3
"""Page-relevance decisions for synthetic multi-sheet TLE packets.

The TLE release contains only single-page PDFs, so this creates a controlled
packet for each task: one page from the task's own sheet plus distractor pages
from other task families. The model sees one page at a time and answers whether
that page is relevant to the task. The source-sheet page is the positive label;
all distractors are negative labels.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pymupdf
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_ocg_decisions import load_tasks, post_decision  # noqa: E402

ROOT = Path("data/tle_raw/TLE-prod [dont-delete]/pdfs")
INDEX = ROOT / "index.json"
DEFAULT_OUT = Path("studies/page-decisions")


def load_pages() -> list[dict]:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    pages = []
    for asset in index["assets"]:
        path = ROOT / asset["path"]
        pages.append(
            {
                "task_id": asset["task_id"],
                "family": asset["family"],
                "pdf": path,
                "page": 0,
            }
        )
    return pages


def render_page(path: Path, max_side: int) -> tuple[bytes, dict]:
    doc = pymupdf.open(path)
    page = doc[0]
    pix = page.get_pixmap(dpi=150, alpha=False)
    img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    if max(img.size) > max_side:
        scale = max_side / max(img.size)
        img = img.resize((round(img.width * scale), round(img.height * scale)), Image.Resampling.LANCZOS)
    out = io.BytesIO()
    img.save(out, format="PNG", optimize=True)
    png = out.getvalue()
    gray = img.convert("L")
    sample = gray.resize((min(800, gray.width), max(1, round(gray.height * min(800, gray.width) / gray.width))))
    try:
        pixels = list(sample.get_flattened_data())
    except AttributeError:
        pixels = list(sample.getdata())
    ink = sum(1 for value in pixels if value < 245) / max(1, len(pixels))
    return png, {
        "image_width": img.width,
        "image_height": img.height,
        "ink_fraction": round(ink, 6),
        "image_sha256": hashlib.sha256(png).hexdigest(),
    }


def build_packet(target: dict, pages: list[dict], size: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    other_family = [p for p in pages if p["task_id"] != target["task_id"] and p["family"] != target["family"]]
    same_family = [p for p in pages if p["task_id"] != target["task_id"] and p["family"] == target["family"]]
    rng.shuffle(other_family)
    rng.shuffle(same_family)
    distractors = other_family[: max(0, size - 1)]
    if len(distractors) < size - 1:
        distractors += same_family[: size - 1 - len(distractors)]
    packet = [{"source": target, "role": "target"}] + [{"source": p, "role": "distractor"} for p in distractors]
    rng.shuffle(packet)
    for position, item in enumerate(packet, start=1):
        item["position"] = position
    return packet


def prompt_for(task: dict, packet_size: int) -> tuple[str, str]:
    task_text = task.get("promptBrief") or task.get("shortTitle") or task["taskId"]
    text = (
        f"You are reviewing one page of a {packet_size}-page multi-sheet plan packet. "
        f"Exactly one page in this packet is the source sheet for the task; the other pages are distractors. "
        f"The task is: {task_text}\n\n"
        "Decide whether this page is the source sheet needed to complete the task. "
        "Answer yes only if the page contains the specific discipline, floor/elevation, symbols, "
        "or dimensions required by the task. Do not answer yes merely because the page is a drawing: "
        "a different discipline, a different floor, a different project, or a page with only "
        "title-block/revision/annotation content is not relevant. Most pages in the packet are "
        "distractors."
    )
    question = "This page is the source sheet relevant to completing the stated task."
    return text, question


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--models", default="valen-0.8b,valen-2b,valen-4b")
    parser.add_argument("--packet-size", type=int, default=8)
    parser.add_argument("--tasks", default="", help="Comma-separated task ids; default all")
    parser.add_argument("--max-side", type=int, default=1200)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--save-images", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    answers_path = args.out / "answers.jsonl"
    images_dir = args.out / "images"
    existing = set()
    if args.resume and answers_path.exists():
        for line in answers_path.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(line)
                existing.add((row["task_id"], row["packet_position"], row["model"]))
            except (KeyError, json.JSONDecodeError):
                pass

    tasks = load_tasks()
    all_pages = load_pages()
    pages = all_pages
    wanted = {x.strip() for x in args.tasks.split(",") if x.strip()}
    if wanted:
        pages = [p for p in all_pages if p["task_id"] in wanted]
    pages_by_task = {p["task_id"]: p for p in all_pages}
    target_tasks = [t for t in tasks.values() if t["taskId"] in pages_by_task]
    if wanted:
        target_tasks = [t for t in target_tasks if t["taskId"] in wanted]
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    page_cache: dict[str, tuple[bytes, dict]] = {}
    print(f"{len(target_tasks)} tasks x {args.packet_size} pages x {len(models)} models")
    run_start = datetime.now(timezone.utc).isoformat()
    with answers_path.open("a", encoding="utf-8") as out:
        for task in target_tasks:
            target = pages_by_task[task["taskId"]]
            seed = int(hashlib.sha256(task["taskId"].encode()).hexdigest()[:8], 16)
            packet = build_packet(target, all_pages, args.packet_size, seed)
            text, question = prompt_for(task, args.packet_size)
            print(f"\n== {task['taskId']} ==")
            for item in packet:
                source = item["source"]
                position = item["position"]
                role = item["role"]
                try:
                    cache_key = source["task_id"]
                    if cache_key in page_cache:
                        png, meta = page_cache[cache_key]
                    else:
                        png, meta = render_page(source["pdf"], args.max_side)
                        page_cache[cache_key] = (png, meta)
                except Exception as exc:
                    print(f"  page {position} {source['task_id']}: render ERROR {exc}")
                    continue
                image_path = None
                if args.save_images:
                    image_path = images_dir / task["taskId"] / f"{position:02d}__{source['task_id']}.png"
                    image_path.parent.mkdir(parents=True, exist_ok=True)
                    image_path.write_bytes(png)
                    image_path = str(image_path)
                for model in models:
                    key = (task["taskId"], position, model)
                    if key in existing:
                        print(f"  page {position:02d} {role:10} [{model}] exists")
                        continue
                    try:
                        response = post_decision(model, text, question, png, args.temperature)
                        answer = response.get("answers", [{}])[0]
                        probability = answer.get("probability")
                        record = {
                            "task_id": task["taskId"],
                            "family": task.get("family"),
                            "task_text": text,
                            "packet_position": position,
                            "packet_size": len(packet),
                            "source_task_id": source["task_id"],
                            "source_family": source["family"],
                            "role": role,
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
                            "task_id": task["taskId"],
                            "family": task.get("family"),
                            "task_text": text,
                            "packet_position": position,
                            "packet_size": len(packet),
                            "source_task_id": source["task_id"],
                            "source_family": source["family"],
                            "role": role,
                            "model": model,
                            "status": "error",
                            "error": str(exc)[:1000],
                            **meta,
                            "run_start": run_start,
                        }
                    out.write(json.dumps(record, ensure_ascii=False) + "\n")
                    out.flush()
                    if record["status"] == "ok":
                        print(f"  page {position:02d} {role:10} {source['task_id']:30} [{model}] p={record['probability']:.3f}")
                    else:
                        print(f"  page {position:02d} {role:10} [{model}] ERROR {record['error'][:160]}")
                    time.sleep(0.05)
    print(f"\nwrote {answers_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
