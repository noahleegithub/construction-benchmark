# Results

| Model | Family | Att. | Scored | Comp. | Score | Fail=0 | TLE mIoU | Prec. | Rec. | Verdict | Meas. err | Evidence | Errors |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gw-gpt-5.6-luna | ALL | 7 | 6 | 0.86 | 0.327 | 0.281 | 0.293 | 0.531 | 0.365 | - | - | - | 1 |
| gw-gpt-5.6-luna | building-footprint | 1 | 1 | 1.00 | 0.723 | 0.723 | 0.723 | 1.000 | 1.000 | - | - | - | 0 |
| gw-gpt-5.6-luna | corridor-net-area | 1 | 1 | 1.00 | 0.918 | 0.918 | 0.918 | 1.000 | 1.000 | - | - | - | 0 |
| gw-gpt-5.6-luna | door-threshold-areas | 1 | 0 | 0.00 | - | 0.000 | - | - | - | - | - | - | 1 |
| gw-gpt-5.6-luna | net-room-areas | 4 | 4 | 1.00 | 0.081 | 0.081 | 0.029 | 0.296 | 0.048 | - | - | - | 0 |
| gw-gpt-5.6-sol | ALL | 7 | 7 | 1.00 | 0.255 | 0.255 | 0.231 | 0.541 | 0.335 | - | - | - | 0 |
| gw-gpt-5.6-sol | building-footprint | 1 | 1 | 1.00 | 0.578 | 0.578 | 0.578 | 1.000 | 1.000 | - | - | - | 0 |
| gw-gpt-5.6-sol | corridor-net-area | 1 | 1 | 1.00 | 0.779 | 0.779 | 0.779 | 1.000 | 1.000 | - | - | - | 0 |
| gw-gpt-5.6-sol | door-threshold-areas | 1 | 1 | 1.00 | 0.024 | 0.024 | 0.000 | 0.000 | 0.000 | - | - | - | 0 |
| gw-gpt-5.6-sol | net-room-areas | 4 | 4 | 1.00 | 0.102 | 0.102 | 0.065 | 0.446 | 0.086 | - | - | - | 0 |
| gw-gpt-6.1-sol | ALL | 7 | 5 | 0.71 | 0.534 | 0.382 | 0.513 | 0.767 | 0.569 | - | - | - | 2 |
| gw-gpt-6.1-sol | building-footprint | 1 | 1 | 1.00 | 0.892 | 0.892 | 0.892 | 1.000 | 1.000 | - | - | - | 0 |
| gw-gpt-6.1-sol | corridor-net-area | 1 | 1 | 1.00 | 0.991 | 0.991 | 0.991 | 1.000 | 1.000 | - | - | - | 0 |
| gw-gpt-6.1-sol | door-threshold-areas | 1 | 0 | 0.00 | - | 0.000 | - | - | - | - | - | - | 1 |
| gw-gpt-6.1-sol | net-room-areas | 4 | 3 | 0.75 | 0.263 | 0.197 | 0.227 | 0.611 | 0.281 | - | - | - | 1 |
| oracle | ALL | 7 | 7 | 1.00 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | - | - | - | 0 |
| oracle | building-footprint | 1 | 1 | 1.00 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | - | - | - | 0 |
| oracle | corridor-net-area | 1 | 1 | 1.00 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | - | - | - | 0 |
| oracle | door-threshold-areas | 1 | 1 | 1.00 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | - | - | - | 0 |
| oracle | net-room-areas | 4 | 4 | 1.00 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | - | - | - | 0 |
| stub | ALL | 7 | 7 | 1.00 | 0.000 | 0.000 | - | 0.000 | 0.000 | - | - | - | 0 |
| stub | building-footprint | 1 | 1 | 1.00 | 0.000 | 0.000 | - | 0.000 | 0.000 | - | - | - | 0 |
| stub | corridor-net-area | 1 | 1 | 1.00 | 0.000 | 0.000 | - | 0.000 | 0.000 | - | - | - | 0 |
| stub | door-threshold-areas | 1 | 1 | 1.00 | 0.000 | 0.000 | - | 0.000 | 0.000 | - | - | - | 0 |
| stub | net-room-areas | 4 | 4 | 1.00 | 0.000 | 0.000 | - | 0.000 | 0.000 | - | - | - | 0 |

# Per-task usage

| Model | Task | Family | Runs | Scored | Input tok | Output tok | Total tok | Cost USD | Score |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| gw-gpt-5.6-luna | t-280-net-room-areas | net-room-areas | 1 | 1 | 4938 | 3762 | 8700 | - | 0.043 |
| gw-gpt-5.6-luna | t-43e-net-room-areas | net-room-areas | 1 | 1 | 5291 | 2608 | 7899 | - | 0.139 |
| gw-gpt-5.6-luna | t-4f1-door-threshold-areas | door-threshold-areas | 1 | 0 | 5294 | 3690 | 8984 | - | - |
| gw-gpt-5.6-luna | t-6bb-building-footprint | building-footprint | 1 | 1 | 5287 | 2699 | 7986 | - | 0.723 |
| gw-gpt-5.6-luna | t-b9c-net-room-areas | net-room-areas | 1 | 1 | 5291 | 2486 | 7777 | - | 0.116 |
| gw-gpt-5.6-luna | t-classroom-net-areas | net-room-areas | 1 | 1 | 4625 | 2086 | 6711 | - | 0.026 |
| gw-gpt-5.6-luna | t-corridor-net-area | corridor-net-area | 1 | 1 | 5248 | 2456 | 7704 | - | 0.918 |
| gw-gpt-5.6-sol | t-280-net-room-areas | net-room-areas | 1 | 1 | 4938 | 6667 | 11605 | - | 0.035 |
| gw-gpt-5.6-sol | t-43e-net-room-areas | net-room-areas | 1 | 1 | 5291 | 2274 | 7565 | - | 0.216 |
| gw-gpt-5.6-sol | t-4f1-door-threshold-areas | door-threshold-areas | 1 | 1 | 5294 | 7313 | 12607 | - | 0.024 |
| gw-gpt-5.6-sol | t-6bb-building-footprint | building-footprint | 1 | 1 | 5287 | 3048 | 8335 | - | 0.578 |
| gw-gpt-5.6-sol | t-b9c-net-room-areas | net-room-areas | 1 | 1 | 5291 | 4035 | 9326 | - | 0.130 |
| gw-gpt-5.6-sol | t-classroom-net-areas | net-room-areas | 1 | 1 | 4625 | 3074 | 7699 | - | 0.027 |
| gw-gpt-5.6-sol | t-corridor-net-area | corridor-net-area | 1 | 1 | 5248 | 3399 | 8647 | - | 0.779 |
| gw-gpt-6.1-sol | t-280-net-room-areas | net-room-areas | 1 | 0 | 4938 | 8000 | 12938 | - | - |
| gw-gpt-6.1-sol | t-43e-net-room-areas | net-room-areas | 1 | 1 | 5291 | 2264 | 7555 | - | 0.631 |
| gw-gpt-6.1-sol | t-4f1-door-threshold-areas | door-threshold-areas | 1 | 0 | 5294 | 8000 | 13294 | - | - |
| gw-gpt-6.1-sol | t-6bb-building-footprint | building-footprint | 1 | 1 | 5287 | 1920 | 7207 | - | 0.892 |
| gw-gpt-6.1-sol | t-b9c-net-room-areas | net-room-areas | 1 | 1 | 5291 | 5368 | 10659 | - | 0.124 |
| gw-gpt-6.1-sol | t-classroom-net-areas | net-room-areas | 1 | 1 | 4625 | 1930 | 6555 | - | 0.034 |
| gw-gpt-6.1-sol | t-corridor-net-area | corridor-net-area | 1 | 1 | 5248 | 1404 | 6652 | - | 0.991 |
| oracle | t-280-net-room-areas | net-room-areas | 1 | 1 | - | - | - | - | 1.000 |
| oracle | t-43e-net-room-areas | net-room-areas | 1 | 1 | - | - | - | - | 1.000 |
| oracle | t-4f1-door-threshold-areas | door-threshold-areas | 1 | 1 | - | - | - | - | 1.000 |
| oracle | t-6bb-building-footprint | building-footprint | 1 | 1 | - | - | - | - | 1.000 |
| oracle | t-b9c-net-room-areas | net-room-areas | 1 | 1 | - | - | - | - | 1.000 |
| oracle | t-classroom-net-areas | net-room-areas | 1 | 1 | - | - | - | - | 1.000 |
| oracle | t-corridor-net-area | corridor-net-area | 1 | 1 | - | - | - | - | 1.000 |
| stub | t-280-net-room-areas | net-room-areas | 1 | 1 | - | - | - | - | 0.000 |
| stub | t-43e-net-room-areas | net-room-areas | 1 | 1 | - | - | - | - | 0.000 |
| stub | t-4f1-door-threshold-areas | door-threshold-areas | 1 | 1 | - | - | - | - | 0.000 |
| stub | t-6bb-building-footprint | building-footprint | 1 | 1 | - | - | - | - | 0.000 |
| stub | t-b9c-net-room-areas | net-room-areas | 1 | 1 | - | - | - | - | 0.000 |
| stub | t-classroom-net-areas | net-room-areas | 1 | 1 | - | - | - | - | 0.000 |
| stub | t-corridor-net-area | corridor-net-area | 1 | 1 | - | - | - | - | 0.000 |
