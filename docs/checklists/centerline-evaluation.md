# TLE wall-centerline evaluation

Run date: 2026-11-19. Seven recoverable wall-extraction tasks; four gateway
models; one repeat; 32k output cap; rendered at 2400 px longest side.

## What is and is not official

The public TLE bundle does not include the `tasks/` manifests with the exact
`wall_segments.segments` answer key. Ground truth here is recovered from the
vendor page annotations (`geojson_walls`), normalized to the page:

| Task | Published expected | Recovered | Status |
|---|---:|---:|---|
| `t-4c4-wall-centerlines` | 447 | 453 | approximate |
| `t-888-wall-centerlines` | 123 | 121 | approximate |
| `t-door-centerline-contractor` | 16 | 16 | exact |
| `t-wall-centerline-3218` | 281 | 292 | approximate |
| `t-wall-centerline-a5-4` | 343 | 349 | approximate |
| `t-wall-centerline-ocala` | 80 | 77 | approximate |
| `t-wall-centerline-page-10` | 105 | 106 | approximate |

These numbers are valid for comparing models inside this workspace. They are
not an official TLE reproduction. `t-door-centerlines` is excluded because the
bundle has no page geometry for its 848 expected segments;
`t-wall-perimeter-painters` is perimeter linework, not a centerline; and
`t-14b-wall-centerlines` has no page annotation in this bundle.

## Scoring

A predicted segment is credited only when both endpoints are within 0.012 of
the page (12 units on the TLE 1000×1000 grid) of the expert segment's endpoints.
Endpoint order is ignored. Score is segment F1. Oracle ground truth scores 1.000;
the empty stub scores 0.000.

## Results

F1 is over all seven items; `Fail=0` charges parse/provider failures as zero.

| Model | Scored | F1 | Fail=0 | Precision | Recall | Cost |
|---|---:|---:|---:|---:|---:|---:|
| `gpt-6-astra` | 7/7 | **0.547** | 0.547 | 0.588 | 0.535 | $2.718 |
| `gpt-6.1-sol` | 7/7 | 0.494 | 0.494 | 0.555 | 0.464 | $0.479 |
| `gpt-6-sol` | 7/7 | 0.263 | 0.263 | 0.326 | 0.239 | $0.404 |
| `gpt-6-luna` | 4/7 | 0.141 | 0.080 | 0.145 | 0.186 | $0.059 |

Per-task F1:

| Task | GT count | 6.1-sol | 6-astra | 6-sol | 6-luna |
|---|---:|---:|---:|---:|---:|
| `t-4c4` | 453* | 0.535 | **0.554** | 0.184 | 0.044 |
| `t-888` | 121* | 0.690 | **0.844** | 0.439 | fail |
| `t-door-centerline-contractor` | 16 | 0.800 | **0.833** | 0.231 | 0.324 |
| `t-wall-centerline-3218` | 292* | 0.326 | **0.344** | 0.129 | 0.063 |
| `t-wall-centerline-a5-4` | 349* | **0.331** | 0.311 | 0.137 | fail |
| `t-wall-centerline-ocala` | 77* | 0.459 | **0.511** | 0.377 | 0.131 |
| `t-wall-centerline-page-10` | 106* | 0.321 | **0.431** | 0.347 | fail |

`*` recovered count, not the published expected count.

## Findings

- `gpt-6-astra` is the strongest model overall, but its advantage over
  `gpt-6.1-sol` is small relative to its 5.7× cost.
- The bottleneck on dense plans is recall, not line precision. On `t-4c4`,
  astra emits 258 segments against 453 recovered and still reaches precision
  0.764; it returns a clean subset and misses walls rather than flooding the
  answer with false positives.
- The small door task is the only exact-ground-truth item. Both frontier models
  handle it well (0.833 and 0.800); `gpt-6-sol` and `gpt-6-luna` do not.
- `gpt-6-luna` hit the 32k output cap on `t-888` and `t-wall-centerline-page-10`.
  It also returned no JSON on `a5-4` with `finish_reason=stop`. Those are
  format/completion failures, not geometric near-misses.
- Endpoint errors for matched segments are 0.001–0.008 page units, so when a
  model finds a wall it places it accurately. The loss is missed or fragmented
  runs.

## Files

- `report.md`, `scores.csv`, `usage.csv`, `usage_report.md`
- `runs.gateway.jsonl` — 28 model calls
- `cost_report.md`, `costs.csv`
- `validation.csv` — expected vs recovered counts
- `overlays/` — full-page prediction/ground-truth sheets, one per scored
  (task, model) pair
