# OCG layer usefulness decisions

Run: `studies/ocg-decisions-pilot/answers.jsonl`

- records: 246
- successful: 246
- models: valen-0.8b, valen-2b, valen-4b
- tasks: 1
- unique layers: 82

## Overall by model

| Model | n | Yes | Yes rate | Mean | Median | p10 | p90 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `valen-0.8b` | 82 | 17 | 0.207 | 0.261 | 0.149 | 0.020 | 0.800 |
| `valen-2b` | 82 | 39 | 0.476 | 0.471 | 0.445 | 0.002 | 0.973 |
| `valen-4b` | 82 | 27 | 0.329 | 0.351 | 0.330 | 0.017 | 0.725 |

## Yes rate by task

| Task | `valen-0.8b` | `valen-2b` | `valen-4b` |
|---|---:|---:|---:|
| `t-wall-centerline-3218` | 0.21 (82) | 0.48 (82) | 0.33 (82) |

## Highest consensus layers

| Task | Layer | Mean p | Models |
|---|---|---:|---:|
| `t-wall-centerline-3218` | `XF2-3218|AR-TILE` | 0.887 | 3 |
| `t-wall-centerline-3218` | `XF2-3218|PARKING-W-STOP` | 0.831 | 3 |
| `t-wall-centerline-3218` | `XF2-3218|AR-BALCONY` | 0.829 | 3 |
| `t-wall-centerline-3218` | `XF2-3218|8-AR-DIM` | 0.787 | 3 |
| `t-wall-centerline-3218` | `XF2-3218|AR-PARTITION` | 0.781 | 3 |
| `t-wall-centerline-3218` | `XF2-3218|AR-STOREFRONT` | 0.749 | 3 |
| `t-wall-centerline-3218` | `XF2-3218|AR-EXTERIOR-DOORS` | 0.729 | 3 |
| `t-wall-centerline-3218` | `XF2-3218|XCORE-12-36-3218$0$AR-STAIRS` | 0.719 | 3 |
| `t-wall-centerline-3218` | `XCO-3218|S-EXP-JOINT` | 0.715 | 3 |
| `t-wall-centerline-3218` | `XCO-3218|S-COL 2` | 0.711 | 3 |
| `t-wall-centerline-3218` | `XF2-3218|XF1-3218$0$AR-DOORS` | 0.661 | 3 |
| `t-wall-centerline-3218` | `XF2-3218|2 HR FR WALL` | 0.650 | 3 |
| `t-wall-centerline-3218` | `XF2-3218|dtl-134-80%screen` | 0.643 | 3 |
| `t-wall-centerline-3218` | `XF2-3218|AR-STAIRS` | 0.633 | 3 |
| `t-wall-centerline-3218` | `XF2-3218|AR-WINDOW` | 0.619 | 3 |

## Lowest consensus layers

| Task | Layer | Mean p | Models |
|---|---|---:|---:|
| `t-wall-centerline-3218` | `BORDERTEXT` | 0.075 | 3 |
| `t-wall-centerline-3218` | `XF2-3218|8-AR-DR-NUMBER` | 0.071 | 3 |
| `t-wall-centerline-3218` | `XF2-3218|AR-ABOVE` | 0.067 | 3 |
| `t-wall-centerline-3218` | `XT-3218|BORDERTEXT` | 0.066 | 3 |
| `t-wall-centerline-3218` | `XCO-3218|SITE-PROPERTY-LINE` | 0.047 | 3 |
| `t-wall-centerline-3218` | `XF2-3218|AR-APPLIANCES` | 0.044 | 3 |
| `t-wall-centerline-3218` | `XF2-3218|AR-PARKING-PAINT` | 0.040 | 3 |
| `t-wall-centerline-3218` | `REVISION` | 0.037 | 3 |
| `t-wall-centerline-3218` | `XF2-3218|POOL-DRAINSLOPE` | 0.033 | 3 |
| `t-wall-centerline-3218` | `XCO-3218|S-TOWER-16-ANNOTATION` | 0.018 | 3 |
| `t-wall-centerline-3218` | `XT-3218|TITLEBLK` | 0.018 | 3 |
| `t-wall-centerline-3218` | `TXT` | 0.012 | 3 |
| `t-wall-centerline-3218` | `XF2-3218|POOL DRAIN` | 0.009 | 3 |
| `t-wall-centerline-3218` | `XF2-3218|mp-fixture` | 0.009 | 3 |
| `t-wall-centerline-3218` | `XCO-3218|Text Commom` | 0.004 | 3 |

## Caveat

These are model judgments about a single layer, not accuracy against a human label. The layer name is recorded but was not shown to the model. The image is the layer alone, cropped to its ink and rendered on white.
