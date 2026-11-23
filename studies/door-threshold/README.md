# Door threshold detection

`t-4f1-door-threshold-areas`: trace every door-threshold polygon. This is a
geometry-detection result, not a clear-width compliance check.

## Results

| Model | Mean IoU | F1 | Precision | Recall | Pred / GT |
|---|---:|---:|---:|---:|---:|
| `gpt-6-astra` | **0.352** | 0.317 | 0.317 | 0.317 | 104 / 104 |
| `gpt-6.1-sol` | 0.281 | **0.320** | 0.344 | 0.298 | 90 / 104 |
| `gpt-6-sol` | 0.060 | 0.000 | 0.000 | 0.000 | 81 / 104 |
| `gpt-6-luna` | 0.007 | 0.000 | 0.000 | 0.000 | 66 / 104 |

The model outputs come from the `area-tle-gpt6` 32k runs. A prediction is
credited by mean best-IoU per ground-truth door; F1 uses one-to-one matching at
IoU 0.5.

## Visual sheets

`overlays/` has one full-page sheet per model:

- `t-4f1__gw-gpt-6-astra.png`
- `t-4f1__gw-gpt-6.1-sol.png`
- `t-4f1__gw-gpt-6-sol.png`
- `t-4f1__gw-gpt-6-luna.png`

It also has a per-door crop grid per model (`door-grid__*.png`). The grid has
one tile per ground-truth door, so missed and displaced thresholds are visible
without zooming the whole sheet.

Green is ground truth; red dashed is the prediction. The sheets show the
detection pattern: astra and 6.1 find many doors but not all, sol and luna
return mostly partial or displaced sets.

## What not to infer

Do not read these polygons as door widths. The audit in
`../area-tle-8k/audit/t-4f1/` found that the threshold polygons include the
door stop; 45 of 46 derived 900 mm failures were false. The clear-width
compliance task remains retired.
