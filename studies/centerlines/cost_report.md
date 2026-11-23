# Cost report

Standard short-context rates, USD per 1M tokens. Cached-input discounts are not applied because the runs do not carry a cache-read token count.

Source: https://openai.com/api/pricing/ (Standard, short context ≤272K), retrieved 2026-11-19.

| Model | Total cost (USD) |
|---|---:|
| gw-gpt-6-astra | $2.7176 |
| gw-gpt-6-luna | $0.0593 |
| gw-gpt-6-sol | $0.4041 |
| gw-gpt-6.1-sol | $0.4785 |

| Model | Task | Input tok | Output tok | Input cost | Output cost | Total cost |
|---|---|---:|---:|---:|---:|---:|
| gw-gpt-6-astra | t-4c4-wall-centerlines | 5181 | 9736 | $0.0518 | $0.4868 | $0.5386 |
| gw-gpt-6-astra | t-888-wall-centerlines | 5180 | 5360 | $0.0518 | $0.2680 | $0.3198 |
| gw-gpt-6-astra | t-door-centerline-contractor | 5103 | 3111 | $0.0510 | $0.1555 | $0.2066 |
| gw-gpt-6-astra | t-wall-centerline-3218 | 5179 | 9855 | $0.0518 | $0.4928 | $0.5445 |
| gw-gpt-6-astra | t-wall-centerline-a5-4 | 5177 | 8315 | $0.0518 | $0.4158 | $0.4675 |
| gw-gpt-6-astra | t-wall-centerline-ocala | 5179 | 5827 | $0.0518 | $0.2913 | $0.3431 |
| gw-gpt-6-astra | t-wall-centerline-page-10 | 4817 | 4985 | $0.0482 | $0.2492 | $0.2974 |
| gw-gpt-6-luna | t-4c4-wall-centerlines | 5183 | 5872 | $0.0005 | $0.0029 | $0.0035 |
| gw-gpt-6-luna | t-888-wall-centerlines | 5183 | 32000 | $0.0005 | $0.0160 | $0.0165 |
| gw-gpt-6-luna | t-door-centerline-contractor | 5102 | 3714 | $0.0005 | $0.0019 | $0.0024 |
| gw-gpt-6-luna | t-wall-centerline-3218 | 5179 | 3423 | $0.0005 | $0.0017 | $0.0022 |
| gw-gpt-6-luna | t-wall-centerline-a5-4 | 5178 | 25385 | $0.0005 | $0.0127 | $0.0132 |
| gw-gpt-6-luna | t-wall-centerline-ocala | 5179 | 8981 | $0.0005 | $0.0045 | $0.0050 |
| gw-gpt-6-luna | t-wall-centerline-page-10 | 4821 | 32000 | $0.0005 | $0.0160 | $0.0165 |
| gw-gpt-6-sol | t-4c4-wall-centerlines | 5180 | 6110 | $0.0104 | $0.0611 | $0.0715 |
| gw-gpt-6-sol | t-888-wall-centerlines | 5181 | 4372 | $0.0104 | $0.0437 | $0.0541 |
| gw-gpt-6-sol | t-door-centerline-contractor | 5103 | 2399 | $0.0102 | $0.0240 | $0.0342 |
| gw-gpt-6-sol | t-wall-centerline-3218 | 5179 | 4914 | $0.0104 | $0.0491 | $0.0595 |
| gw-gpt-6-sol | t-wall-centerline-a5-4 | 5177 | 6031 | $0.0104 | $0.0603 | $0.0707 |
| gw-gpt-6-sol | t-wall-centerline-ocala | 5174 | 4746 | $0.0103 | $0.0475 | $0.0578 |
| gw-gpt-6-sol | t-wall-centerline-page-10 | 4819 | 4678 | $0.0096 | $0.0468 | $0.0564 |
| gw-gpt-6.1-sol | t-4c4-wall-centerlines | 5184 | 9558 | $0.0104 | $0.0956 | $0.1059 |
| gw-gpt-6.1-sol | t-888-wall-centerlines | 5179 | 3991 | $0.0104 | $0.0399 | $0.0503 |
| gw-gpt-6.1-sol | t-door-centerline-contractor | 5107 | 2416 | $0.0102 | $0.0242 | $0.0344 |
| gw-gpt-6.1-sol | t-wall-centerline-3218 | 5178 | 9198 | $0.0104 | $0.0920 | $0.1023 |
| gw-gpt-6.1-sol | t-wall-centerline-a5-4 | 5180 | 6049 | $0.0104 | $0.0605 | $0.0708 |
| gw-gpt-6.1-sol | t-wall-centerline-ocala | 5179 | 4825 | $0.0104 | $0.0483 | $0.0586 |
| gw-gpt-6.1-sol | t-wall-centerline-page-10 | 4819 | 4650 | $0.0096 | $0.0465 | $0.0561 |
