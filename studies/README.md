# Studies

Each subdirectory is a result set. Shared drawing sheets, ground-truth files,
and item definitions live in `_shared/`, which links to the local-only `study/`
directory. Study directories contain their own items, model outputs, scores, and
figures. The PDFs themselves are not committed; see `../study/DATA_NOTES.md`.

| Directory | Study | Status |
|---|---|---|
| `area-tle-archive/` | Imported TLE area tasks, 19 models, 132 archived runs | reference data |
| `area-tle-8k/` | Gateway area baseline, 3 models, 8k output | early baseline |
| `area-tle-32k/` | Gateway area rerun, 3 models, 32k output | baseline at final cap |
| `area-tle-gpt6/` | GPT-6.0/6.1 area matrix, 4 models, 32k, costs | final area result |
| `centerlines/` | TLE wall/door centerline tasks, 4 models, 7 items | approximate GT |
| `door-threshold/` | `t-4f1` door-threshold detection overlays, 4 models | geometry only |
| `ocg-decisions/` | Valen decision models on single OCG layers, 14 tasks, 898 layers, 3 models | unlabelled model judgments |
| `page-decisions/` | Valen page-relevance decisions on synthetic 8-page packets, 33 tasks, 3 models | synthetic labels |
| `prompt-sensitivity/` | Prompt variants, noise floor, positive control | stopped at failed gate |
| `archive/` | Pilots, smoke tests, and run logs | superseded |

`centerlines/overlays/` and `door-threshold/overlays/` contain full-page sheets:
green is ground truth, red dashed is the model prediction. The header records
the item, model, and score. Overlay PNGs and rendered images are local-only; the
README and numeric results are tracked.

`door-threshold/` is **not** the retired clear-width compliance study. It shows
door-threshold polygon detection. The 900 mm clear-opening task remains retired
because the threshold polygons are not clear-width measurements.

`area-tle-archive/` is the imported TLE bundle; it is kept because it contains
the 19-model, 132-run reference set. The active GPT-6 study is
`area-tle-gpt6/`.

`ocg-decisions/` asks the free Valen decisions API whether each single OCG layer
is useful for its TLE task. See
[`../docs/studies/ocg-layer-decisions.md`](../docs/studies/ocg-layer-decisions.md);
these are model judgments without human labels.

`page-decisions/` asks the same API whether a page is the source sheet for a
task in a synthetic 8-page packet. See
[`../docs/studies/page-relevance-decisions.md`](../docs/studies/page-relevance-decisions.md);
the TLE release has only single-page PDFs, so the packets are constructed, not
real plan sets.

The long-form writeups are indexed in
[`../docs/studies/README.md`](../docs/studies/README.md).
