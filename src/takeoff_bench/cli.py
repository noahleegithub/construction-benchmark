"""Command-line interface."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__, config, demo, overlay, report, runner
from .providers import list_models
from .render import render_pdf_page
from .schema import ItemError, load_items

ITEMS_HEADER = "item_id,family,sheet,page,question,convention,output_type,gt,notes\n"

MODELS_TEMPLATE = """models:
  - id: oracle
    provider: oracle          # test-only: returns the ground truth
  - id: stub
    provider: stub            # test-only: returns empty outputs
  # - id: frontier
  #   provider: openai
  #   model: replace-with-model-id
  #   base_url: https://api.openai.com/v1
  #   api_key_env: OPENAI_API_KEY
  #   temperature: 0
  #   max_tokens: 8000
  #   token_param: max_tokens   # use max_completion_tokens if required
  #   detail: high
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="takeoff-bench",
        description="A small, open harness for construction drawing takeoff benchmarks.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "-C",
        "--workspace",
        type=Path,
        default=Path("."),
        help="workspace directory (default: current directory)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="scaffold a new workspace")
    init.add_argument("directory", type=Path)
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=cmd_init)

    demo_parser = sub.add_parser("demo", help="build and score a synthetic workspace")
    demo_parser.add_argument("directory", type=Path, nargs="?", default=Path("demo"))
    demo_parser.set_defaults(func=cmd_demo)

    check = sub.add_parser("check", help="validate items.csv and ground truth")
    check.set_defaults(func=cmd_check)

    models_parser = sub.add_parser("models", help="list models from the configured gateway")
    models_parser.add_argument("--base-url")
    models_parser.set_defaults(func=cmd_models)

    run_parser = sub.add_parser("run", help="run models over selected items")
    run_parser.add_argument("--models", default="models.yaml")
    run_parser.add_argument("--repeats", type=int, default=1)
    run_parser.add_argument("--family")
    run_parser.add_argument("--item")
    run_parser.add_argument("--limit", type=int)
    run_parser.add_argument(
        "--variant",
        default="baseline",
        help="prompt variant: baseline, schema_first, compressed, schema_first_compressed, control_drop_constraints",
    )
    run_parser.add_argument(
        "--cache-bust",
        action="store_true",
        help="append a unique ignored request id to each prompt to bypass gateway replay",
    )
    run_parser.add_argument("--force", action="store_true")
    run_parser.add_argument("--dpi", type=int, default=150)
    run_parser.add_argument("--max-side", type=int, default=2400)
    run_parser.add_argument("--iou-threshold", type=float, default=0.5)
    run_parser.add_argument(
        "--no-report", action="store_true", help="skip scoring after the run"
    )
    run_parser.add_argument(
        "--provider",
        help="override every model's provider (stub or oracle for offline runs)",
    )
    run_parser.add_argument("--runs", default="runs.jsonl")
    run_parser.set_defaults(func=cmd_run)

    score = sub.add_parser("score", help="score runs and write report.md")
    score.add_argument("--runs", default="runs.jsonl")
    score.add_argument("--out", default="report.md")
    score.add_argument("--iou-threshold", type=float, default=0.5)
    score.set_defaults(func=cmd_score)

    usage = sub.add_parser("usage", help="show per-task token usage and cost")
    usage.add_argument("--runs", default="runs.jsonl")
    usage.set_defaults(func=cmd_usage)

    overlay_parser = sub.add_parser("overlay", help="draw ground truth and a prediction")
    overlay_parser.add_argument("--item", required=True)
    overlay_parser.add_argument("--model", required=True)
    overlay_parser.add_argument("--repeat", type=int, default=0)
    overlay_parser.add_argument("--out")
    overlay_parser.add_argument("--runs", default="runs.jsonl")
    overlay_parser.add_argument("--dpi", type=int, default=150)
    overlay_parser.add_argument("--max-side", type=int, default=2400)
    overlay_parser.set_defaults(func=cmd_overlay)

    render = sub.add_parser("render", help="render one item's sheet page to PNG")
    render.add_argument("--item", required=True)
    render.add_argument("--out")
    render.add_argument("--dpi", type=int, default=150)
    render.add_argument("--max-side", type=int, default=2400)
    render.set_defaults(func=cmd_render)

    return parser


def cmd_init(args) -> int:
    path: Path = args.directory
    if (path / "items.csv").exists() and not args.force:
        raise SystemExit(f"{path / 'items.csv'} already exists; use --force to overwrite")
    (path / "sheets").mkdir(parents=True, exist_ok=True)
    (path / "gt").mkdir(parents=True, exist_ok=True)
    (path / "items.csv").write_text(ITEMS_HEADER, encoding="utf-8")
    (path / "models.yaml").write_text(MODELS_TEMPLATE, encoding="utf-8")
    (path / "sheets" / ".gitkeep").touch()
    (path / "gt" / ".gitkeep").touch()
    print(f"created workspace at {path.resolve()}")
    print("next: add PDFs to sheets/, ground truth to gt/, and rows to items.csv")
    return 0


def cmd_demo(args) -> int:
    path: Path = args.directory
    demo.create_demo_workspace(path)
    runner.run(
        path,
        path / "models.yaml",
        repeats=1,
        force=True,
    )
    report.score_and_report(path)
    print(f"demo workspace: {path.resolve()}")
    return 0


def cmd_check(args) -> int:
    items = load_items(args.workspace)
    families: dict[str, int] = {}
    for item in items:
        families[item.family] = families.get(item.family, 0) + 1
    print(f"{len(items)} items, {len(families)} families")
    for family, count in sorted(families.items()):
        print(f"  {family}: {count}")
    return 0


def cmd_models(args) -> int:
    import pandas as pd

    base_url, api_key, headers = config.gateway_settings()
    if args.base_url:
        base_url = args.base_url.rstrip("/")
    if not api_key:
        raise SystemExit("TAMU_API_KEY is not set; add it to .env or export it")
    entries = list_models(base_url, api_key, headers)
    frame = pd.DataFrame(
        [{"id": entry["id"], "owned_by": entry.get("owned_by", "")} for entry in entries]
    )
    print(frame.to_string(index=False))
    return 0


def cmd_run(args) -> int:
    workspace: Path = args.workspace
    runner.run(
        workspace,
        workspace / args.models,
        repeats=args.repeats,
        family=args.family,
        item_id=args.item,
        limit=args.limit,
        force=args.force,
        dpi=args.dpi,
        max_side=args.max_side,
        provider_override=args.provider,
        runs_path=workspace / args.runs,
        variant=args.variant,
        cache_bust=args.cache_bust,
    )
    if not args.no_report:
        report.score_and_report(
            workspace,
            runs_path=workspace / args.runs,
            iou_threshold=args.iou_threshold,
        )
    return 0


def cmd_score(args) -> int:
    workspace: Path = args.workspace
    report.score_and_report(
        workspace,
        runs_path=workspace / args.runs,
        out_path=workspace / args.out,
        iou_threshold=args.iou_threshold,
    )
    return 0


def cmd_usage(args) -> int:
    workspace: Path = args.workspace
    rows = report.score_runs(workspace, workspace / args.runs)
    usage = report.task_usage(rows)
    report.write_usage(usage, workspace / "usage.csv")
    (workspace / "usage_report.md").write_text(
        report.format_usage(usage), encoding="utf-8"
    )
    report.print_usage_dataframe(usage)
    return 0


def cmd_overlay(args) -> int:
    workspace: Path = args.workspace
    items = {item.item_id: item for item in load_items(workspace)}
    item = items.get(args.item)
    if item is None:
        raise SystemExit(f"unknown item: {args.item}")
    run = overlay.find_run(
        workspace / args.runs, args.item, args.model, args.repeat
    )
    out_path = Path(args.out) if args.out else workspace / f"overlay-{args.item}-{args.model}.png"
    result = overlay.draw_overlay(
        workspace,
        item,
        run,
        out_path,
        dpi=args.dpi,
        max_side=args.max_side,
    )
    print(f"wrote {out_path} (score {result.get('score', 0):.3f})")
    return 0


def cmd_render(args) -> int:
    workspace: Path = args.workspace
    items = {item.item_id: item for item in load_items(workspace)}
    item = items.get(args.item)
    if item is None:
        raise SystemExit(f"unknown item: {args.item}")
    png, size = render_pdf_page(
        item.sheet_path(workspace), item.page, dpi=args.dpi, max_side=args.max_side
    )
    out_path = Path(args.out) if args.out else workspace / f"{args.item}.png"
    out_path.write_bytes(png)
    print(f"wrote {out_path} ({size[0]}x{size[1]})")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config.load_env(config.REPO_ROOT / ".env", Path(args.workspace) / ".env")
    try:
        return args.func(args)
    except (ItemError, FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
