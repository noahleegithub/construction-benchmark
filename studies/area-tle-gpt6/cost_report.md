# Cost report

Standard short-context rates, USD per 1M tokens. Cached-input discounts are not applied because the runs do not carry a cache-read token count.

Source: https://openai.com/api/pricing/ (Standard, short context ≤272K), retrieved 2026-11-19.

| Model | Total cost (USD) |
|---|---:|
| gw-gpt-6-astra | $2.1680 |
| gw-gpt-6-luna | $0.0151 |
| gw-gpt-6-sol | $0.3453 |
| gw-gpt-6.1-sol | $0.4464 |

| Model | Task | Input tok | Output tok | Input cost | Output cost | Total cost |
|---|---|---:|---:|---:|---:|---:|
| gw-gpt-6-astra | t-280-net-room-areas | 4938 | 9505 | $0.0494 | $0.4753 | $0.5246 |
| gw-gpt-6-astra | t-43e-net-room-areas | 5291 | 2856 | $0.0529 | $0.1428 | $0.1957 |
| gw-gpt-6-astra | t-4f1-door-threshold-areas | 5294 | 11178 | $0.0529 | $0.5589 | $0.6118 |
| gw-gpt-6-astra | t-6bb-building-footprint | 5287 | 1174 | $0.0529 | $0.0587 | $0.1116 |
| gw-gpt-6-astra | t-b9c-net-room-areas | 5291 | 8402 | $0.0529 | $0.4201 | $0.4730 |
| gw-gpt-6-astra | t-classroom-net-areas | 4625 | 1925 | $0.0462 | $0.0963 | $0.1425 |
| gw-gpt-6-astra | t-corridor-net-area | 5248 | 1126 | $0.0525 | $0.0563 | $0.1088 |
| gw-gpt-6-luna | t-280-net-room-areas | 4938 | 4631 | $0.0005 | $0.0023 | $0.0028 |
| gw-gpt-6-luna | t-43e-net-room-areas | 5291 | 2620 | $0.0005 | $0.0013 | $0.0018 |
| gw-gpt-6-luna | t-4f1-door-threshold-areas | 5294 | 5590 | $0.0005 | $0.0028 | $0.0033 |
| gw-gpt-6-luna | t-6bb-building-footprint | 5287 | 2413 | $0.0005 | $0.0012 | $0.0017 |
| gw-gpt-6-luna | t-b9c-net-room-areas | 5291 | 2930 | $0.0005 | $0.0015 | $0.0020 |
| gw-gpt-6-luna | t-classroom-net-areas | 4625 | 2267 | $0.0005 | $0.0011 | $0.0016 |
| gw-gpt-6-luna | t-corridor-net-area | 5248 | 2625 | $0.0005 | $0.0013 | $0.0018 |
| gw-gpt-6-sol | t-280-net-room-areas | 4938 | 5967 | $0.0099 | $0.0597 | $0.0695 |
| gw-gpt-6-sol | t-43e-net-room-areas | 5291 | 2633 | $0.0106 | $0.0263 | $0.0369 |
| gw-gpt-6-sol | t-4f1-door-threshold-areas | 5294 | 5532 | $0.0106 | $0.0553 | $0.0659 |
| gw-gpt-6-sol | t-6bb-building-footprint | 5287 | 2454 | $0.0106 | $0.0245 | $0.0351 |
| gw-gpt-6-sol | t-b9c-net-room-areas | 5291 | 4913 | $0.0106 | $0.0491 | $0.0597 |
| gw-gpt-6-sol | t-classroom-net-areas | 4625 | 1275 | $0.0092 | $0.0127 | $0.0220 |
| gw-gpt-6-sol | t-corridor-net-area | 5248 | 4561 | $0.0105 | $0.0456 | $0.0561 |
| gw-gpt-6.1-sol | t-280-net-room-areas | 4938 | 8265 | $0.0099 | $0.0827 | $0.0925 |
| gw-gpt-6.1-sol | t-43e-net-room-areas | 5291 | 3773 | $0.0106 | $0.0377 | $0.0483 |
| gw-gpt-6.1-sol | t-4f1-door-threshold-areas | 5294 | 8937 | $0.0106 | $0.0894 | $0.1000 |
| gw-gpt-6.1-sol | t-6bb-building-footprint | 5287 | 1601 | $0.0106 | $0.0160 | $0.0266 |
| gw-gpt-6.1-sol | t-b9c-net-room-areas | 5291 | 10954 | $0.0106 | $0.1095 | $0.1201 |
| gw-gpt-6.1-sol | t-classroom-net-areas | 4625 | 2200 | $0.0092 | $0.0220 | $0.0312 |
| gw-gpt-6.1-sol | t-corridor-net-area | 5248 | 1717 | $0.0105 | $0.0172 | $0.0277 |
