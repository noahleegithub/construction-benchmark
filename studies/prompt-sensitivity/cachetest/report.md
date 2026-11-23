# Results

| Model | Family | Att. | Scored | Comp. | Score | Fail=0 | TLE mIoU | Prec. | Rec. | Verdict | Meas. err | Evidence | Errors |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cachetest | ALL | 6 | 5 | 0.83 | 0.588 | 0.490 | 0.588 | 1.000 | 1.000 | - | - | - | 1 |
| cachetest | building-footprint | 6 | 5 | 0.83 | 0.588 | 0.490 | 0.588 | 1.000 | 1.000 | - | - | - | 1 |
| cachetest-a | ALL | 1 | 1 | 1.00 | 0.589 | 0.589 | 0.589 | 1.000 | 1.000 | - | - | - | 0 |
| cachetest-a | building-footprint | 1 | 1 | 1.00 | 0.589 | 0.589 | 0.589 | 1.000 | 1.000 | - | - | - | 0 |
| cachetest-b | ALL | 1 | 1 | 1.00 | 0.589 | 0.589 | 0.589 | 1.000 | 1.000 | - | - | - | 0 |
| cachetest-b | building-footprint | 1 | 1 | 1.00 | 0.589 | 0.589 | 0.589 | 1.000 | 1.000 | - | - | - | 0 |
| cachetest-c | ALL | 1 | 1 | 1.00 | 0.589 | 0.589 | 0.589 | 1.000 | 1.000 | - | - | - | 0 |
| cachetest-c | building-footprint | 1 | 1 | 1.00 | 0.589 | 0.589 | 0.589 | 1.000 | 1.000 | - | - | - | 0 |

# Per-task usage

| Model | Task | Family | Runs | Scored | Input tok | Output tok | Total tok | Cost USD | Score |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| cachetest | t-6bb-building-footprint | building-footprint | 6 | 5 | 31799 | 7923 | 39722 | - | 0.588 |
| cachetest-a | t-6bb-building-footprint | building-footprint | 1 | 1 | 5287 | 1284 | 6571 | - | 0.589 |
| cachetest-b | t-6bb-building-footprint | building-footprint | 1 | 1 | 5287 | 1284 | 6571 | - | 0.589 |
| cachetest-c | t-6bb-building-footprint | building-footprint | 1 | 1 | 5287 | 1284 | 6571 | - | 0.589 |
