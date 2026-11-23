# Results

| Model | Family | Att. | Scored | Comp. | Score | Fail=0 | TLE mIoU | Prec. | Rec. | Verdict | Meas. err | Evidence | Errors |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gw-gpt-5.6-luna | ALL | 6 | 6 | 1.00 | 0.135 | 0.135 | 0.048 | 0.160 | 0.078 | - | - | - | 0 |
| gw-gpt-5.6-luna | net-room-areas | 6 | 6 | 1.00 | 0.135 | 0.135 | 0.048 | 0.160 | 0.078 | - | - | - | 0 |
| gw-gpt-5.6-sol | ALL | 6 | 6 | 1.00 | 0.176 | 0.176 | 0.111 | 0.440 | 0.157 | - | - | - | 0 |
| gw-gpt-5.6-sol | net-room-areas | 6 | 6 | 1.00 | 0.176 | 0.176 | 0.111 | 0.440 | 0.157 | - | - | - | 0 |
| gw-gpt-6.1-sol | ALL | 6 | 6 | 1.00 | 0.445 | 0.445 | 0.402 | 0.597 | 0.492 | - | - | - | 0 |
| gw-gpt-6.1-sol | net-room-areas | 6 | 6 | 1.00 | 0.445 | 0.445 | 0.402 | 0.597 | 0.492 | - | - | - | 0 |

# Per-task usage

| Model | Task | Family | Runs | Scored | Input tok | Output tok | Total tok | Cost USD | Score |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| gw-gpt-5.6-luna | t-43e-net-room-areas | net-room-areas | 3 | 3 | 15894 | 8380 | 24274 | - | 0.152 |
| gw-gpt-5.6-luna | t-b9c-net-room-areas | net-room-areas | 3 | 3 | 15896 | 8301 | 24197 | - | 0.117 |
| gw-gpt-5.6-sol | t-43e-net-room-areas | net-room-areas | 3 | 3 | 15897 | 10645 | 26542 | - | 0.222 |
| gw-gpt-5.6-sol | t-b9c-net-room-areas | net-room-areas | 3 | 3 | 15896 | 13487 | 29383 | - | 0.131 |
| gw-gpt-6.1-sol | t-43e-net-room-areas | net-room-areas | 3 | 3 | 15901 | 6328 | 22229 | - | 0.296 |
| gw-gpt-6.1-sol | t-b9c-net-room-areas | net-room-areas | 3 | 3 | 15895 | 29425 | 45320 | - | 0.593 |
