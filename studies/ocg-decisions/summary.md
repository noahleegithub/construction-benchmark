# OCG layer usefulness decisions

Run: `studies/ocg-decisions/answers.jsonl`

- records: 2694
- successful: 2694
- models: valen-0.8b, valen-2b, valen-4b
- tasks: 14
- unique layers: 898

## Overall by model

| Model | n | Yes | Yes rate | Mean | Median | p10 | p90 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `valen-0.8b` | 898 | 105 | 0.117 | 0.200 | 0.113 | 0.023 | 0.556 |
| `valen-2b` | 898 | 279 | 0.311 | 0.308 | 0.097 | 0.001 | 0.892 |
| `valen-4b` | 898 | 141 | 0.157 | 0.250 | 0.200 | 0.010 | 0.583 |

## Yes rate by task

| Task | `valen-0.8b` | `valen-2b` | `valen-4b` |
|---|---:|---:|---:|
| `t-012-tagged-light-fixtures` | 0.01 (150) | 0.79 (150) | 0.07 (150) |
| `t-236-balcony-areas` | 0.03 (58) | 0.05 (58) | 0.22 (58) |
| `t-280-net-room-areas` | 0.18 (79) | 0.18 (79) | 0.14 (79) |
| `t-404-led-light-symbols` | 0.24 (17) | 0.29 (17) | 0.06 (17) |
| `t-43e-net-room-areas` | 0.31 (67) | 0.19 (67) | 0.18 (67) |
| `t-4c4-wall-centerlines` | 0.08 (65) | 0.29 (65) | 0.22 (65) |
| `t-911-chair-symbols` | 0.05 (44) | 0.02 (44) | 0.02 (44) |
| `t-99f-siding-wall-areas` | 0.07 (44) | 0.02 (44) | 0.02 (44) |
| `t-bc8-elevation-stone-areas` | 0.00 (44) | 0.02 (44) | 0.02 (44) |
| `t-corridor-net-area` | 0.19 (63) | 0.29 (63) | 0.16 (63) |
| `t-wall-centerline-3218` | 0.21 (82) | 0.48 (82) | 0.33 (82) |
| `t-wall-centerline-a5-4` | 0.05 (76) | 0.26 (76) | 0.24 (76) |
| `t-wall-centerline-page-10` | 0.18 (44) | 0.07 (44) | 0.11 (44) |
| `t-wall-perimeter-painters` | 0.18 (65) | 0.37 (65) | 0.25 (65) |

## Highest consensus layers

| Task | Layer | Mean p | Models |
|---|---|---:|---:|
| `t-wall-centerline-3218` | `XF2-3218|AR-TILE` | 0.887 | 3 |
| `t-wall-centerline-a5-4` | `XF3-5|AR-PARTITION` | 0.880 | 3 |
| `t-280-net-room-areas` | `X-FLOOR PLANS|DW` | 0.860 | 3 |
| `t-43e-net-room-areas` | `XL MOBILITY 3808 MSA|4-AR-DIM` | 0.859 | 3 |
| `t-4c4-wall-centerlines` | `XL 04 3808|AR-PARTITION` | 0.844 | 3 |
| `t-236-balcony-areas` | `XL 04 3808|3-16-RC-ROOM NAME` | 0.839 | 3 |
| `t-4c4-wall-centerlines` | `XL 04 3808|AR-STAIRS` | 0.838 | 3 |
| `t-corridor-net-area` | `XSTRCT 01 33 3808|S-SW-1-RF` | 0.836 | 3 |
| `t-43e-net-room-areas` | `XL MOBILITY 3808 MSA|AR-PARTITION` | 0.835 | 3 |
| `t-wall-centerline-3218` | `XF2-3218|PARKING-W-STOP` | 0.831 | 3 |
| `t-wall-centerline-3218` | `XF2-3218|AR-BALCONY` | 0.829 | 3 |
| `t-corridor-net-area` | `XSTRCT 01 33 3808|S-SW-2-33` | 0.805 | 3 |
| `t-43e-net-room-areas` | `REVISION 17` | 0.791 | 3 |
| `t-43e-net-room-areas` | `XL MOBILITY 3808 MSA|AR-TILE` | 0.790 | 3 |
| `t-wall-perimeter-painters` | `XSTRCT 01 33 3808|S-COL-4-32` | 0.790 | 3 |

## Lowest consensus layers

| Task | Layer | Mean p | Models |
|---|---|---:|---:|
| `t-4c4-wall-centerlines` | `XSTRCT 01 33 3808|S-8-ANNOTATION` | 0.011 | 3 |
| `t-43e-net-room-areas` | `XL MOBILITY 3808 MSA|AR-DEMISING-WALL` | 0.010 | 3 |
| `t-236-balcony-areas` | `XL LEGEND RCP|REVISION 1` | 0.010 | 3 |
| `t-236-balcony-areas` | `DIM` | 0.010 | 3 |
| `t-wall-perimeter-painters` | `XL MOBILITY 3808 MSA|4-RC-ROOM NAME` | 0.009 | 3 |
| `t-236-balcony-areas` | `XTB 3808|TITLEBLK` | 0.009 | 3 |
| `t-280-net-room-areas` | `X-FLOOR PLANS|A-TUNNEL GRID` | 0.009 | 3 |
| `t-wall-centerline-3218` | `XF2-3218|POOL DRAIN` | 0.009 | 3 |
| `t-4c4-wall-centerlines` | `XSTRCT 01 33 3808|S-COL-RF-SH` | 0.009 | 3 |
| `t-wall-centerline-a5-4` | `1-20-AR-DIM` | 0.009 | 3 |
| `t-wall-centerline-3218` | `XF2-3218|mp-fixture` | 0.009 | 3 |
| `t-4c4-wall-centerlines` | `XSTRCT 01 33 3808|S-COL-33-SH` | 0.008 | 3 |
| `t-43e-net-room-areas` | `XL MOBILITY 3808 MSA|AR-HATCH` | 0.007 | 3 |
| `t-280-net-room-areas` | `X-FLOOR PLANS|ces electric` | 0.007 | 3 |
| `t-wall-centerline-3218` | `XCO-3218|Text Commom` | 0.004 | 3 |

## Caveat

These are model judgments about a single layer, not accuracy against a human label. The layer name is recorded but was not shown to the model. The image is the layer alone, cropped to its ink and rendered on white.
