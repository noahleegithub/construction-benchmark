# takeoff-bench

A small, open harness for benchmarking models on construction drawing takeoff.

It is built for a narrow question: given one sheet and one question, how close
is the model's geometry, count, text, or quantity to a documented ground truth?
Everything else is deliberately out of scope. There is no database and no web
server; the workspace is a folder of CSV, JSON, and JSONL files that can be
read, diffed, and committed.

## Design

- **Files are the interface.** `items.csv` defines the questions, `gt/*.json`
  holds ground truth, `runs.jsonl` records every request and response, and
  `scores.csv` / `report.md` hold results.
- **Provenance is explicit.** Each run stores the prompt hash, image hash,
  model id, repeat index, usage, and cost, so a score can be traced to the
  exact input that produced it.
- **One scorer, stated once.** Polygon IoU, point F1, text match, and quantity
  error are defined in `scoring.py` and unit-tested. No LLM judges.
- **Failures are not zeros.** Provider errors and parse errors are recorded as
  such and excluded from the score mean, then reported separately.
- **Idempotent batches.** Re-running skips successful runs; provider errors are
  retried on the next invocation.

## Install

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone <repo> takeoff-bench
cd takeoff-bench
uv sync
```

The demo needs no API key and no drawings:

```bash
uv run takeoff-bench demo ./demo
```

It creates a synthetic two-room sheet, runs the `oracle` provider (which returns
the ground truth), scores it, and writes `report.md`, `scores.csv`, and
`runs.jsonl` under `./demo`. The oracle scores 1.000; the `stub` provider scores
0.000. Both exercise the full path.

## Running your own items

```bash
uv run takeoff-bench init ./study
```

This creates:

```
study/
  items.csv          # one row per question
  models.yaml        # model endpoints
  sheets/            # PDFs
  gt/                # ground-truth JSON
```

1. Put PDFs in `study/sheets/`.
2. Add one JSON file per item in `study/gt/` (formats below).
3. Add rows to `study/items.csv`.
4. Validate:

```bash
uv run takeoff-bench -C ./study check
```

5. Run. Start with one family and a small limit:

```bash
export OPENAI_API_KEY=...
uv run takeoff-bench -C ./study run --family room-areas --limit 5 --repeats 3
```

6. Score and inspect:

```bash
uv run takeoff-bench -C ./study score
uv run takeoff-bench -C ./study overlay --item room-101 --model frontier-a
```

The overlay writes a PNG with ground truth in green and the prediction in red.
Use it before trusting any aggregate number.

## items.csv

| column | meaning |
|---|---|
| `item_id` | unique, stable identifier |
| `family` | grouping used in the report, e.g. `room-areas` |
| `sheet` | PDF path relative to the workspace |
| `page` | 1-based page number |
| `question` | the instruction shown to the model |
| `convention` | the measurement convention for this item, in one or two sentences |
| `output_type` | `polygons`, `polylines`, `points`, `count`, `text`, or `quantities` |
| `gt` | ground-truth JSON path relative to the workspace |
| `notes` | optional; not sent to the model |

Write the `convention` field carefully. It is the part of the item that a
drawing cannot answer: net versus gross, centerline versus face, which face for
a perimeter, how a threshold is split. If the convention is ambiguous, the item
is measuring the annotator, not the model.

## Ground truth

All geometry uses normalized page coordinates: `x` and `y` in `[0, 1]`, origin
at the top-left of the page, `x` right, `y` down. This keeps ground truth
independent of render DPI.

Polygons:

```json
{
  "type": "polygons",
  "instances": [
    {"id": "room-101", "label": "101", "points": [[0.11, 0.16], [0.48, 0.16], [0.48, 0.84], [0.11, 0.84]]}
  ]
}
```

Polylines:

```json
{"type": "polylines", "lines": [{"label": "wall-a", "points": [[0.1, 0.2], [0.9, 0.2]]}]}
```

Points:

```json
{"type": "points", "points": [[0.24, 0.31], [0.62, 0.31]]}
```

Count:

```json
{"type": "count", "value": 12}
```

Text:

```json
{"type": "text", "value": "8'-6\""}
```

Quantities:

```json
{
  "type": "quantities",
  "items": [
    {"label": "Gross wall area", "value": 18450, "unit": "sf"},
    {"label": "Net wall area", "value": 16210, "unit": "sf"}
  ]
}
```

## models.yaml

```yaml
models:
  - id: frontier-a
    provider: openai
    model: gpt-5.2
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY
    temperature: 0
    max_tokens: 8000
    token_param: max_tokens        # use max_completion_tokens if required
    detail: high
    input_cost_per_mtok: 2.50      # optional, for cost tracking
    output_cost_per_mtok: 10.00

  - id: frontier-b
    provider: openrouter
    model: anthropic/claude-sonnet-4.5
    base_url: https://openrouter.ai/api/v1
    api_key_env: OPENROUTER_API_KEY
```

Only the OpenAI-compatible chat completions format is implemented. That covers
OpenAI, OpenRouter, vLLM, and most hosted endpoints. To use Anthropic's native
API, point the config at an OpenAI-compatible gateway.

`stub` and `oracle` are offline providers for tests. Do not report results from
either.

## Scoring

- **Polygons.** `score` is the mean over ground-truth instances of each
  instance's best IoU against any prediction, with 0 for a miss. `precision`
  and `recall` use one-to-one greedy matching at IoU >= 0.5. `count_ratio` is
  predicted instances divided by ground-truth instances.
- **Polylines.** Buffered by `line_width / 2` (default 0.0015 of the page) and
  scored as polygons.
- **Points.** Greedy one-to-one matching within `tolerance` (default 0.01 of
  the page); `score` is F1.
- **Count.** `max(0, 1 - relative_error)`.
- **Text.** Normalized exact match; a similarity ratio is reported alongside.
- **Quantities.** Labels are matched after normalization; each ground-truth
  line scores `max(0, 1 - relative_error)`, and a missing line scores 0.

The report includes the mean, standard deviation across repeats, precision,
recall, count ratio, parse rate, and error count per model and family. Provider
errors are excluded from the mean and counted separately; parse errors are
scored as zero but reported in `scores.csv`.

## Files

```
runs.jsonl     one JSON object per request/response
scores.csv     one row per run, with metrics and status
report.md      aggregate table
.cache/        rendered page images (safe to delete)
```

`runs.jsonl` is the record of truth. It contains the raw response, so a prompt
or scorer change can be evaluated against archived outputs without new API
calls.

## Limitations

- One page per item. Tiling for large sheets is not implemented.
- Raster and vector PDFs are both rendered to an image; vector extraction is not
  attempted. For born-digital sheets, a vector pipeline will beat this harness.
- Scanned sheets are not preprocessed (deskew, OCR, threshold).
- Polygon matching is greedy, not optimal assignment. On dense sheets with many
  near-identical instances, prefer reporting recall and cardinality over mean
  IoU.
- Normalized coordinates distort distances on non-square pages; point tolerance
  is therefore approximate.
- No multi-sheet or cross-sheet items yet.

## License

MIT.
