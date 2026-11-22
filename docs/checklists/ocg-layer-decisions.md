# OCG layer usefulness decisions

Experiment: does a decision model judge a single PDF optional-content layer as
useful for a TLE task?

## Setup

- API: `POST https://api.valen-team.workers.dev/v1/decisions`
- Free endpoint; no API key.
- Models: `valen-0.8b`, `valen-2b`, `valen-4b`.
- One request per layer. The request contains exactly **one image**, the layer
  rendered with every other OCG hidden.
- The layer name is recorded but **not included in the prompt**.
- The image is cropped to its non-white extent, with an 8% margin, and capped at
  1200 px on the long side.
- Task text comes from the TLE task's `promptBrief`.
- Question type: `predicate`:
  “The visible content of this single OCG layer is useful for completing the
  stated task.”
- Yes means `probability >= 0.5`.

## Scope

14 TLE PDFs have OCGs. The run iterates the PyMuPDF UI layer list, which yields
898 layers (two more than the raw OCG count because some OCGs expose more than
one UI entry). The 19 PDFs without OCGs cannot be tested this way, including
`t-4f1-door-threshold-areas`, `t-888-wall-centerlines`, and
`t-door-centerlines`.

## Pilot: `t-wall-centerline-3218`

82 layers, three models, 246 successful requests:

| Model | Yes | Yes rate | Mean p | Median |
|---|---:|---:|---:|---:|
| `valen-0.8b` | 17 | 0.207 | 0.261 | 0.149 |
| `valen-2b` | 39 | 0.476 | 0.471 | 0.445 |
| `valen-4b` | 27 | 0.329 | 0.351 | 0.330 |

The 2B model ranks `AR-PARTITION` (0.997), `AR-EXTERIOR-WALL` (0.991), and
`AR-WINDOW` (0.982) high, but also gives high scores to `AR-HATCH` (0.928),
`AR-TILE` (0.897), and `AR-BALCONY` (0.932). The 4B model is more
conservative; its top layer is `AR-TILE` (0.849). The 0.8B model is the least
stable: it gives `AR-BALCONY` 0.965 but `AR-WALL-CABINETS` 0.012.

This is a model judgment, not accuracy. There is no human usefulness label yet,
and the visual proxy is the layer alone, not the full sheet.

## Reproduce

```bash
PYTHONPATH= uv run python scripts/run_ocg_decisions.py \
  --out studies/ocg-decisions \
  --models valen-0.8b,valen-2b,valen-4b \
  --save-images --resume
```

Summaries:

```bash
PYTHONPATH= uv run python scripts/summarize_ocg_decisions.py studies/ocg-decisions
```

Outputs: `answers.jsonl`, `per_layer.csv`, `summary_by_model.csv`,
`summary_by_task_model.csv`, `summary.md`, and `images/`.
