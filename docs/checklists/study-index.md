# Studies

Each subdirectory is a self-contained result set. Shared drawing sheets and
ground-truth files live in `_shared/`; study directories contain their own
items, model outputs, scores, and figures.

| Directory | Study | Status |
|---|---|---|
| `area-tle-archive/` | Imported TLE area tasks, 19 models, 132 archived runs | reference data |
| `area-tle-8k/` | Gateway area baseline, 3 models, 8k output | early baseline |
| `area-tle-32k/` | Gateway area rerun, 3 models, 32k output | baseline at final cap |
| `area-tle-gpt6/` | GPT-6.0/6.1 area matrix, 4 models, 32k, costs | final area result |
| `centerlines/` | TLE wall/door centerline tasks, 4 models, 7 items | approximate GT |
| `door-threshold/` | `t-4f1` door-threshold detection overlays, 4 models | geometry only |
| `prompt-sensitivity/` | Prompt variants, noise floor, positive control | stopped at failed gate |

`centerlines/overlays/` and `door-threshold/overlays/` contain full-page sheets:
green is ground truth, red dashed is the model prediction. The header records
the item, model, and score.

`door-threshold/` is **not** the retired clear-width compliance study. It shows
door-threshold polygon detection. The 900 mm clear-opening task remains retired
because the threshold polygons are not clear-width measurements.

`area-tle-archive/` is the imported TLE bundle; it is kept because it contains
the 19-model, 132-run reference set. The active GPT-6 study is
`area-tle-gpt6/`.
