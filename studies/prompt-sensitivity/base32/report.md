# Results

| Model | Family | Att. | Scored | Comp. | Score | Fail=0 | TLE mIoU | Prec. | Rec. | Verdict | Meas. err | Evidence | Errors |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gw-gpt-5.6-luna | ALL | 7 | 6 | 0.86 | 0.207 | 0.177 | 0.120 | 0.368 | 0.211 | - | - | - | 1 |
| gw-gpt-5.6-luna | building-footprint | 1 | 1 | 1.00 | 0.544 | 0.544 | 0.544 | 1.000 | 1.000 | - | - | - | 0 |
| gw-gpt-5.6-luna | corridor-net-area | 1 | 1 | 1.00 | 0.253 | 0.253 | 0.000 | 0.000 | 0.000 | - | - | - | 0 |
| gw-gpt-5.6-luna | door-threshold-areas | 1 | 0 | 0.00 | - | 0.000 | - | - | - | - | - | - | 1 |
| gw-gpt-5.6-luna | net-room-areas | 4 | 4 | 1.00 | 0.111 | 0.111 | 0.044 | 0.302 | 0.066 | - | - | - | 0 |
| gw-gpt-5.6-sol | ALL | 7 | 7 | 1.00 | 0.250 | 0.250 | 0.220 | 0.587 | 0.336 | - | - | - | 0 |
| gw-gpt-5.6-sol | building-footprint | 1 | 1 | 1.00 | 0.569 | 0.569 | 0.569 | 1.000 | 1.000 | - | - | - | 0 |
| gw-gpt-5.6-sol | corridor-net-area | 1 | 1 | 1.00 | 0.711 | 0.711 | 0.711 | 1.000 | 1.000 | - | - | - | 0 |
| gw-gpt-5.6-sol | door-threshold-areas | 1 | 1 | 1.00 | 0.026 | 0.026 | 0.000 | 0.000 | 0.000 | - | - | - | 0 |
| gw-gpt-5.6-sol | net-room-areas | 4 | 4 | 1.00 | 0.110 | 0.110 | 0.065 | 0.527 | 0.087 | - | - | - | 0 |
| gw-gpt-6.1-sol | ALL | 7 | 7 | 1.00 | 0.474 | 0.474 | 0.440 | 0.739 | 0.546 | - | - | - | 0 |
| gw-gpt-6.1-sol | building-footprint | 1 | 1 | 1.00 | 0.599 | 0.599 | 0.599 | 1.000 | 1.000 | - | - | - | 0 |
| gw-gpt-6.1-sol | corridor-net-area | 1 | 1 | 1.00 | 0.986 | 0.986 | 0.986 | 1.000 | 1.000 | - | - | - | 0 |
| gw-gpt-6.1-sol | door-threshold-areas | 1 | 1 | 1.00 | 0.319 | 0.319 | 0.224 | 0.347 | 0.327 | - | - | - | 0 |
| gw-gpt-6.1-sol | net-room-areas | 4 | 4 | 1.00 | 0.354 | 0.354 | 0.318 | 0.707 | 0.374 | - | - | - | 0 |
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
| gw-gpt-5.6-luna | t-280-net-room-areas | net-room-areas | 1 | 1 | 4938 | 3460 | 8398 | - | 0.060 |
| gw-gpt-5.6-luna | t-43e-net-room-areas | net-room-areas | 1 | 1 | 5291 | 2566 | 7857 | - | 0.154 |
| gw-gpt-5.6-luna | t-4f1-door-threshold-areas | door-threshold-areas | 1 | 0 | 5294 | 3573 | 8867 | - | - |
| gw-gpt-5.6-luna | t-6bb-building-footprint | building-footprint | 1 | 1 | 5287 | 2835 | 8122 | - | 0.544 |
| gw-gpt-5.6-luna | t-b9c-net-room-areas | net-room-areas | 1 | 1 | 5291 | 3359 | 8650 | - | 0.205 |
| gw-gpt-5.6-luna | t-classroom-net-areas | net-room-areas | 1 | 1 | 4625 | 1770 | 6395 | - | 0.025 |
| gw-gpt-5.6-luna | t-corridor-net-area | corridor-net-area | 1 | 1 | 5248 | 3084 | 8332 | - | 0.253 |
| gw-gpt-5.6-sol | t-280-net-room-areas | net-room-areas | 1 | 1 | 4938 | 6895 | 11833 | - | 0.100 |
| gw-gpt-5.6-sol | t-43e-net-room-areas | net-room-areas | 1 | 1 | 5291 | 3412 | 8703 | - | 0.201 |
| gw-gpt-5.6-sol | t-4f1-door-threshold-areas | door-threshold-areas | 1 | 1 | 5294 | 7076 | 12370 | - | 0.026 |
| gw-gpt-5.6-sol | t-6bb-building-footprint | building-footprint | 1 | 1 | 5287 | 2589 | 7876 | - | 0.569 |
| gw-gpt-5.6-sol | t-b9c-net-room-areas | net-room-areas | 1 | 1 | 5291 | 3871 | 9162 | - | 0.110 |
| gw-gpt-5.6-sol | t-classroom-net-areas | net-room-areas | 1 | 1 | 4625 | 3003 | 7628 | - | 0.031 |
| gw-gpt-5.6-sol | t-corridor-net-area | corridor-net-area | 1 | 1 | 5248 | 3587 | 8835 | - | 0.711 |
| gw-gpt-6.1-sol | t-280-net-room-areas | net-room-areas | 1 | 1 | 4938 | 9191 | 14129 | - | 0.138 |
| gw-gpt-6.1-sol | t-43e-net-room-areas | net-room-areas | 1 | 1 | 5291 | 2642 | 7933 | - | 0.574 |
| gw-gpt-6.1-sol | t-4f1-door-threshold-areas | door-threshold-areas | 1 | 1 | 5294 | 11142 | 16436 | - | 0.319 |
| gw-gpt-6.1-sol | t-6bb-building-footprint | building-footprint | 1 | 1 | 5287 | 1541 | 6828 | - | 0.599 |
| gw-gpt-6.1-sol | t-b9c-net-room-areas | net-room-areas | 1 | 1 | 5291 | 9165 | 14456 | - | 0.670 |
| gw-gpt-6.1-sol | t-classroom-net-areas | net-room-areas | 1 | 1 | 4625 | 1664 | 6289 | - | 0.035 |
| gw-gpt-6.1-sol | t-corridor-net-area | corridor-net-area | 1 | 1 | 5248 | 1151 | 6399 | - | 0.986 |
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
