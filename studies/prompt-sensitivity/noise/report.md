# Results

| Model | Family | Att. | Scored | Comp. | Score | Fail=0 | TLE mIoU | Prec. | Rec. | Verdict | Meas. err | Evidence | Errors |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gw-gpt-5.6-luna | ALL | 15 | 15 | 1.00 | 0.261 | 0.261 | 0.209 | 0.411 | 0.343 | - | - | - | 0 |
| gw-gpt-5.6-luna | building-footprint | 5 | 5 | 1.00 | 0.607 | 0.607 | 0.607 | 1.000 | 1.000 | - | - | - | 0 |
| gw-gpt-5.6-luna | net-room-areas | 10 | 10 | 1.00 | 0.089 | 0.089 | 0.010 | 0.117 | 0.015 | - | - | - | 0 |
| gw-gpt-5.6-sol | ALL | 15 | 15 | 1.00 | 0.266 | 0.266 | 0.217 | 0.509 | 0.363 | - | - | - | 0 |
| gw-gpt-5.6-sol | building-footprint | 5 | 5 | 1.00 | 0.598 | 0.598 | 0.598 | 1.000 | 1.000 | - | - | - | 0 |
| gw-gpt-5.6-sol | net-room-areas | 10 | 10 | 1.00 | 0.100 | 0.100 | 0.027 | 0.264 | 0.044 | - | - | - | 0 |
| gw-gpt-6.1-sol | ALL | 15 | 15 | 1.00 | 0.489 | 0.489 | 0.455 | 0.778 | 0.654 | - | - | - | 0 |
| gw-gpt-6.1-sol | building-footprint | 5 | 5 | 1.00 | 0.586 | 0.586 | 0.586 | 1.000 | 1.000 | - | - | - | 0 |
| gw-gpt-6.1-sol | net-room-areas | 10 | 10 | 1.00 | 0.440 | 0.440 | 0.390 | 0.668 | 0.480 | - | - | - | 0 |

# Per-task usage

| Model | Task | Family | Runs | Scored | Input tok | Output tok | Total tok | Cost USD | Score |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| gw-gpt-5.6-luna | t-280-net-room-areas | net-room-areas | 5 | 5 | 24690 | 21205 | 45895 | - | 0.081 |
| gw-gpt-5.6-luna | t-6bb-building-footprint | building-footprint | 5 | 5 | 26435 | 14540 | 40975 | - | 0.607 |
| gw-gpt-5.6-luna | t-b9c-net-room-areas | net-room-areas | 5 | 5 | 26455 | 15590 | 42045 | - | 0.096 |
| gw-gpt-5.6-sol | t-280-net-room-areas | net-room-areas | 5 | 5 | 24690 | 21455 | 46145 | - | 0.071 |
| gw-gpt-5.6-sol | t-6bb-building-footprint | building-footprint | 5 | 5 | 26435 | 16645 | 43080 | - | 0.598 |
| gw-gpt-5.6-sol | t-b9c-net-room-areas | net-room-areas | 5 | 5 | 26455 | 21245 | 47700 | - | 0.129 |
| gw-gpt-6.1-sol | t-280-net-room-areas | net-room-areas | 5 | 5 | 24690 | 42405 | 67095 | - | 0.137 |
| gw-gpt-6.1-sol | t-6bb-building-footprint | building-footprint | 5 | 5 | 26435 | 9110 | 35545 | - | 0.586 |
| gw-gpt-6.1-sol | t-b9c-net-room-areas | net-room-areas | 5 | 5 | 26455 | 52535 | 78990 | - | 0.742 |
