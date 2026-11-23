# GPT 6.x sweep

Run date: 2026-11-19. Seven active TLE geometry items, one repeat, 32k output cap.

## Model availability

The gateway exposes:

- GPT 6.0: `gpt-6-astra`, `gpt-6-luna`, `gpt-6-sol`
- GPT 6.1: `gpt-6.1-sol`
- GPT 6.2: **none** — `/models/gpt-6.2`, `-sol`, `-luna`, `-terra`, and
  `-astra` all return 404.

The sweep therefore covers four models, not the requested three families.

## Results

F1 is the primary metric. `gpt-6-astra` failed to return JSON on
`t-6bb-building-footprint`; its mean over scored tasks is 0.504, and its
fail-as-zero mean is 0.432.

| Model | Scored | F1 (scored) | F1 (fail=0) | Recall |
|---|---:|---:|---:|---:|
| `gpt-6.1-sol` | 7/7 | 0.534 | 0.534 | 0.541 |
| `gpt-6-astra` | 6/7 | 0.504 | 0.432 | 0.494 |
| `gpt-6-sol` | 7/7 | 0.390 | 0.390 | 0.361 |
| `gpt-6-luna` | 7/7 | 0.206 | 0.206 | 0.184 |

Tokens and per-task rows are in `usage_report.md`; raw runs are in
`runs.jsonl`. Standard short-context token prices from the official OpenAI
API pricing page (retrieved 2026-11-19) are applied in `costs.csv` and
`cost_report.md`.

| Model | Input $/1M | Output $/1M | Total cost |
|---|---:|---:|---:|
| `gpt-6-astra` | 10.00 | 50.00 | $2.168 |
| `gpt-6-sol` | 2.00 | 10.00 | $0.345 |
| `gpt-6.1-sol` | 2.00 | 10.00 | $0.446 |
| `gpt-6-luna` | 0.10 | 0.50 | $0.015 |

Cached-input discounts are not applied because the runs do not expose a
cache-read token count.
