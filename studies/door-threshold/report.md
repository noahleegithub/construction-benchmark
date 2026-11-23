# Results

| Model | Family | Att. | Scored | Comp. | Score | Fail=0 | TLE mIoU | Prec. | Rec. | Verdict | Meas. err | Evidence | Errors |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gw-gpt-6-astra | ALL | 1 | 1 | 1.00 | 0.352 | 0.352 | 0.235 | 0.317 | 0.317 | - | - | - | 0 |
| gw-gpt-6-astra | door-threshold-areas | 1 | 1 | 1.00 | 0.352 | 0.352 | 0.235 | 0.317 | 0.317 | - | - | - | 0 |
| gw-gpt-6-luna | ALL | 1 | 1 | 1.00 | 0.007 | 0.007 | 0.000 | 0.000 | 0.000 | - | - | - | 0 |
| gw-gpt-6-luna | door-threshold-areas | 1 | 1 | 1.00 | 0.007 | 0.007 | 0.000 | 0.000 | 0.000 | - | - | - | 0 |
| gw-gpt-6-sol | ALL | 1 | 1 | 1.00 | 0.060 | 0.060 | 0.000 | 0.000 | 0.000 | - | - | - | 0 |
| gw-gpt-6-sol | door-threshold-areas | 1 | 1 | 1.00 | 0.060 | 0.060 | 0.000 | 0.000 | 0.000 | - | - | - | 0 |
| gw-gpt-6.1-sol | ALL | 1 | 1 | 1.00 | 0.281 | 0.281 | 0.185 | 0.344 | 0.298 | - | - | - | 0 |
| gw-gpt-6.1-sol | door-threshold-areas | 1 | 1 | 1.00 | 0.281 | 0.281 | 0.185 | 0.344 | 0.298 | - | - | - | 0 |

# Per-task usage

| Model | Task | Family | Runs | Scored | Input tok | Output tok | Total tok | Cost USD | Score |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| gw-gpt-6-astra | t-4f1-door-threshold-areas | door-threshold-areas | 1 | 1 | 5294 | 11178 | 16472 | - | 0.352 |
| gw-gpt-6-luna | t-4f1-door-threshold-areas | door-threshold-areas | 1 | 1 | 5294 | 5590 | 10884 | - | 0.007 |
| gw-gpt-6-sol | t-4f1-door-threshold-areas | door-threshold-areas | 1 | 1 | 5294 | 5532 | 10826 | - | 0.060 |
| gw-gpt-6.1-sol | t-4f1-door-threshold-areas | door-threshold-areas | 1 | 1 | 5294 | 8937 | 14231 | - | 0.281 |
