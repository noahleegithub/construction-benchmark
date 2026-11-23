# Results

| Model | Family | Att. | Scored | Comp. | Score | Fail=0 | TLE mIoU | Prec. | Rec. | Verdict | Meas. err | Evidence | Errors |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gw-gpt-6-astra | ALL | 7 | 6 | 0.86 | 0.483 | 0.414 | 0.446 | 0.704 | 0.494 | - | - | - | 1 |
| gw-gpt-6-astra | building-footprint | 1 | 0 | 0.00 | - | 0.000 | - | - | - | - | - | - | 1 |
| gw-gpt-6-astra | corridor-net-area | 1 | 1 | 1.00 | 0.992 | 0.992 | 0.992 | 1.000 | 1.000 | - | - | - | 0 |
| gw-gpt-6-astra | door-threshold-areas | 1 | 1 | 1.00 | 0.352 | 0.352 | 0.235 | 0.317 | 0.317 | - | - | - | 0 |
| gw-gpt-6-astra | net-room-areas | 4 | 4 | 1.00 | 0.389 | 0.389 | 0.362 | 0.726 | 0.412 | - | - | - | 0 |
| gw-gpt-6-luna | ALL | 7 | 7 | 1.00 | 0.243 | 0.243 | 0.141 | 0.331 | 0.184 | - | - | - | 0 |
| gw-gpt-6-luna | building-footprint | 1 | 1 | 1.00 | 0.453 | 0.453 | 0.000 | 0.000 | 0.000 | - | - | - | 0 |
| gw-gpt-6-luna | corridor-net-area | 1 | 1 | 1.00 | 0.797 | 0.797 | 0.797 | 1.000 | 1.000 | - | - | - | 0 |
| gw-gpt-6-luna | door-threshold-areas | 1 | 1 | 1.00 | 0.007 | 0.007 | 0.000 | 0.000 | 0.000 | - | - | - | 0 |
| gw-gpt-6-luna | net-room-areas | 4 | 4 | 1.00 | 0.110 | 0.110 | 0.047 | 0.329 | 0.073 | - | - | - | 0 |
| gw-gpt-6-sol | ALL | 7 | 7 | 1.00 | 0.313 | 0.313 | 0.268 | 0.584 | 0.361 | - | - | - | 0 |
| gw-gpt-6-sol | building-footprint | 1 | 1 | 1.00 | 0.935 | 0.935 | 0.935 | 1.000 | 1.000 | - | - | - | 0 |
| gw-gpt-6-sol | corridor-net-area | 1 | 1 | 1.00 | 0.541 | 0.541 | 0.541 | 1.000 | 1.000 | - | - | - | 0 |
| gw-gpt-6-sol | door-threshold-areas | 1 | 1 | 1.00 | 0.060 | 0.060 | 0.000 | 0.000 | 0.000 | - | - | - | 0 |
| gw-gpt-6-sol | net-room-areas | 4 | 4 | 1.00 | 0.164 | 0.164 | 0.101 | 0.522 | 0.132 | - | - | - | 0 |
| gw-gpt-6.1-sol | ALL | 7 | 7 | 1.00 | 0.455 | 0.455 | 0.422 | 0.706 | 0.541 | - | - | - | 0 |
| gw-gpt-6.1-sol | building-footprint | 1 | 1 | 1.00 | 0.586 | 0.586 | 0.586 | 1.000 | 1.000 | - | - | - | 0 |
| gw-gpt-6.1-sol | corridor-net-area | 1 | 1 | 1.00 | 0.988 | 0.988 | 0.988 | 1.000 | 1.000 | - | - | - | 0 |
| gw-gpt-6.1-sol | door-threshold-areas | 1 | 1 | 1.00 | 0.281 | 0.281 | 0.185 | 0.344 | 0.298 | - | - | - | 0 |
| gw-gpt-6.1-sol | net-room-areas | 4 | 4 | 1.00 | 0.332 | 0.332 | 0.299 | 0.649 | 0.373 | - | - | - | 0 |

# Per-task usage

| Model | Task | Family | Runs | Scored | Input tok | Output tok | Total tok | Cost USD | Score |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| gw-gpt-6-astra | t-280-net-room-areas | net-room-areas | 1 | 1 | 4938 | 9505 | 14443 | - | 0.139 |
| gw-gpt-6-astra | t-43e-net-room-areas | net-room-areas | 1 | 1 | 5291 | 2856 | 8147 | - | 0.578 |
| gw-gpt-6-astra | t-4f1-door-threshold-areas | door-threshold-areas | 1 | 1 | 5294 | 11178 | 16472 | - | 0.352 |
| gw-gpt-6-astra | t-6bb-building-footprint | building-footprint | 1 | 0 | 5287 | 1174 | 6461 | - | - |
| gw-gpt-6-astra | t-b9c-net-room-areas | net-room-areas | 1 | 1 | 5291 | 8402 | 13693 | - | 0.804 |
| gw-gpt-6-astra | t-classroom-net-areas | net-room-areas | 1 | 1 | 4625 | 1925 | 6550 | - | 0.035 |
| gw-gpt-6-astra | t-corridor-net-area | corridor-net-area | 1 | 1 | 5248 | 1126 | 6374 | - | 0.992 |
| gw-gpt-6-luna | t-280-net-room-areas | net-room-areas | 1 | 1 | 4938 | 4631 | 9569 | - | 0.098 |
| gw-gpt-6-luna | t-43e-net-room-areas | net-room-areas | 1 | 1 | 5291 | 2620 | 7911 | - | 0.145 |
| gw-gpt-6-luna | t-4f1-door-threshold-areas | door-threshold-areas | 1 | 1 | 5294 | 5590 | 10884 | - | 0.007 |
| gw-gpt-6-luna | t-6bb-building-footprint | building-footprint | 1 | 1 | 5287 | 2413 | 7700 | - | 0.453 |
| gw-gpt-6-luna | t-b9c-net-room-areas | net-room-areas | 1 | 1 | 5291 | 2930 | 8221 | - | 0.179 |
| gw-gpt-6-luna | t-classroom-net-areas | net-room-areas | 1 | 1 | 4625 | 2267 | 6892 | - | 0.020 |
| gw-gpt-6-luna | t-corridor-net-area | corridor-net-area | 1 | 1 | 5248 | 2625 | 7873 | - | 0.797 |
| gw-gpt-6-sol | t-280-net-room-areas | net-room-areas | 1 | 1 | 4938 | 5967 | 10905 | - | 0.102 |
| gw-gpt-6-sol | t-43e-net-room-areas | net-room-areas | 1 | 1 | 5291 | 2633 | 7924 | - | 0.196 |
| gw-gpt-6-sol | t-4f1-door-threshold-areas | door-threshold-areas | 1 | 1 | 5294 | 5532 | 10826 | - | 0.060 |
| gw-gpt-6-sol | t-6bb-building-footprint | building-footprint | 1 | 1 | 5287 | 2454 | 7741 | - | 0.935 |
| gw-gpt-6-sol | t-b9c-net-room-areas | net-room-areas | 1 | 1 | 5291 | 4913 | 10204 | - | 0.328 |
| gw-gpt-6-sol | t-classroom-net-areas | net-room-areas | 1 | 1 | 4625 | 1275 | 5900 | - | 0.031 |
| gw-gpt-6-sol | t-corridor-net-area | corridor-net-area | 1 | 1 | 5248 | 4561 | 9809 | - | 0.541 |
| gw-gpt-6.1-sol | t-280-net-room-areas | net-room-areas | 1 | 1 | 4938 | 8265 | 13203 | - | 0.130 |
| gw-gpt-6.1-sol | t-43e-net-room-areas | net-room-areas | 1 | 1 | 5291 | 3773 | 9064 | - | 0.625 |
| gw-gpt-6.1-sol | t-4f1-door-threshold-areas | door-threshold-areas | 1 | 1 | 5294 | 8937 | 14231 | - | 0.281 |
| gw-gpt-6.1-sol | t-6bb-building-footprint | building-footprint | 1 | 1 | 5287 | 1601 | 6888 | - | 0.586 |
| gw-gpt-6.1-sol | t-b9c-net-room-areas | net-room-areas | 1 | 1 | 5291 | 10954 | 16245 | - | 0.540 |
| gw-gpt-6.1-sol | t-classroom-net-areas | net-room-areas | 1 | 1 | 4625 | 2200 | 6825 | - | 0.034 |
| gw-gpt-6.1-sol | t-corridor-net-area | corridor-net-area | 1 | 1 | 5248 | 1717 | 6965 | - | 0.988 |
