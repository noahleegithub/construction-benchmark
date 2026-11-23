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
**898 layers** (two more than the raw OCG count because some OCGs expose more
than one UI entry). All **2,694** layer × model requests succeeded.

The 19 PDFs without OCGs cannot be tested this way, including
`t-4f1-door-threshold-areas`, `t-888-wall-centerlines`,
`t-door-centerlines`, and `t-wall-centerline-ocala`.

## Overall

| Model | n | Yes | Yes rate | Mean p | Median | p10 | p90 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `valen-0.8b` | 898 | 105 | 0.117 | 0.200 | 0.113 | 0.023 | 0.556 |
| `valen-2b` | 898 | 279 | 0.311 | 0.308 | 0.097 | 0.001 | 0.892 |
| `valen-4b` | 898 | 141 | 0.157 | 0.250 | 0.200 | 0.010 | 0.583 |

## Yes rate by task

| Task | `valen-0.8b` | `valen-2b` | `valen-4b` |
|---|---:|---:|---:|
| `t-012-tagged-light-fixtures` | 0.01 | **0.79** | 0.07 |
| `t-236-balcony-areas` | 0.03 | 0.05 | 0.22 |
| `t-280-net-room-areas` | 0.18 | 0.18 | 0.14 |
| `t-404-led-light-symbols` | 0.24 | 0.29 | 0.06 |
| `t-43e-net-room-areas` | 0.31 | 0.19 | 0.18 |
| `t-4c4-wall-centerlines` | 0.08 | 0.29 | 0.22 |
| `t-911-chair-symbols` | 0.05 | 0.02 | 0.02 |
| `t-99f-siding-wall-areas` | 0.07 | 0.02 | 0.02 |
| `t-bc8-elevation-stone-areas` | 0.00 | 0.02 | 0.02 |
| `t-corridor-net-area` | 0.19 | 0.29 | 0.16 |
| `t-wall-centerline-3218` | 0.21 | 0.48 | 0.33 |
| `t-wall-centerline-a5-4` | 0.05 | 0.26 | 0.24 |
| `t-wall-centerline-page-10` | 0.18 | 0.07 | 0.11 |
| `t-wall-perimeter-painters` | 0.18 | 0.37 | 0.25 |

## What the models select

Highest mean probability across all three models:

| Task | Layer | Mean p |
|---|---|---:|
| `t-wall-centerline-3218` | `XF2-3218|AR-TILE` | 0.887 |
| `t-wall-centerline-a5-4` | `XF3-5|AR-PARTITION` | 0.880 |
| `t-280-net-room-areas` | `X-FLOOR PLANS|DW` | 0.860 |
| `t-43e-net-room-areas` | `XL MOBILITY 3808 MSA|4-AR-DIM` | 0.859 |
| `t-4c4-wall-centerlines` | `XL 04 3808|AR-PARTITION` | 0.844 |
| `t-236-balcony-areas` | `XL 04 3808|3-16-RC-ROOM NAME` | 0.839 |
| `t-4c4-wall-centerlines` | `XL 04 3808|AR-STAIRS` | 0.838 |
| `t-corridor-net-area` | `XSTRCT 01 33 3808|S-SW-1-RF` | 0.836 |
| `t-43e-net-room-areas` | `XL MOBILITY 3808 MSA|AR-PARTITION` | 0.835 |
| `t-wall-centerline-3218` | `XF2-3218|PARKING-W-STOP` | 0.831 |

Only some of these are genuinely task evidence. `AR-PARTITION` is a strong
wall-centerline layer. `AR-TILE`, `4-AR-DIM`, `DW`, room-name, stair, and parking
layers are not reliable evidence for the stated tasks; they are the kind of
high-confidence false positive the free models produce.

The pilot on `t-wall-centerline-3218` shows the same pattern. `valen-2b` scores
`AR-PARTITION` 0.997, `AR-EXTERIOR-WALL` 0.991, and `AR-WINDOW` 0.982, but also
scores `AR-BALCONY` 0.932, `AR-HATCH` 0.928, and `AR-TILE` 0.897. `valen-4b` is
more conservative but still ranks `AR-TILE` highest at 0.849. `valen-0.8b` is
the least stable: `AR-BALCONY` 0.965, `AR-WALL-CABINETS` 0.012.

`t-012-tagged-light-fixtures` exposes the largest model disagreement: `valen-2b`
says yes for 79% of its 150 layers, while 0.8B and 4B say 1% and 7%. Many of the
2B yes layers are title, revision, notes, and key-map layers, so this is not
credible layer selection.

## Model agreement

Across all 898 layers:

| Pair | Yes/no agreement | Probability correlation |
|---|---:|---:|
| `valen-0.8b` vs `valen-2b` | 0.702 | 0.315 |
| `valen-0.8b` vs `valen-4b` | 0.837 | 0.368 |
| `valen-2b` vs `valen-4b` | 0.777 | 0.614 |

Only **39 layers** are yes for all three models, and **552** are no for all
three. The models uniquely say yes on 36 (0.8B), 150 (2B), and 20 (4B) layers.
The 2B unique-yes count is dominated by the 150-layer `t-012` task.

## Repeat check

Eight layers across tasks, three repeats each with `valen-2b`, returned identical
probabilities to the full run. The API gave no indication whether this is model
determinism or response caching.

## Caveat

These are model judgments, not accuracy against a human usefulness label. There
is no labelled development set yet, and the visual proxy is the layer alone, not
the full sheet. The results should be treated as candidate rankings for a human
audit, not as a solved layer classifier.

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
