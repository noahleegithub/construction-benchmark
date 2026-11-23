# Prompt-sensitivity gate results

Status: **stopped at the positive-control gate**. No pilot or full sweep was run.

## A. Baseline, 32k, one epoch

21 attempted cells, **20 scored**. `gw-gpt-5.6-luna` on
`t-4f1-door-threshold-areas` returned no JSON (`finish_reason=stop`), so it is a
format failure, not a truncation.

| Model | Scored | F1 | Recall |
|---|---:|---:|---:|
| `gpt-5.6-luna` | 6/7 | 0.227 | 0.211 |
| `gpt-5.6-sol` | 7/7 | 0.363 | 0.336 |
| `gpt-6.1-sol` | 7/7 | 0.558 | 0.546 |

The earlier 8k baseline is not comparable; it had two truncations at exactly
8,000 completion tokens and one format failure.

## B. Noise floor and the replay problem

The first 5-repeat run returned **byte-identical raw output and the same
`response_id`** for every repeat in every cell. The gateway is replaying cached
responses; those repeats are not independent samples.

Adding an ignored request-id nonce with `--cache-bust` fixed it. On the partial
rerun, every cell had distinct raw outputs and distinct response IDs. Pooled
within-cell F1 SD on the completed cells was **0.0076**.

The rerun was stopped after 20/45 calls because the positive-control gate below
failed.

## C. Positive control

Two items, three models, three cache-busted repeats. The control prompt removes
`Include every instance on the sheet` and `Do not merge adjacent instances`.

| Model | Median recall delta | Median F1 delta |
|---|---:|---:|
| `gpt-5.6-luna` | -0.036 | -0.046 |
| `gpt-5.6-sol` | +0.015 | +0.004 |
| `gpt-6.1-sol` | -0.201 | -0.148 |

Only `gpt-6.1-sol` shows the expected substantive drop. The gate required a
median recall drop of at least 0.10 in two of three models. It failed.

## Decision

Do not run the 108-call pilot or the 252-call sweep. The assay cannot show that
a task-relevant prompt change moves two of the three models, so a null
prompt-sensitivity result would be uninterpretable.

This is a methods result, not a claim that prompts do not matter.

## Files

- `../../studies/prompt-sensitivity/base32/` — baseline runs and scores
- `../../studies/prompt-sensitivity/noise/` — cached, invalid repeats
- `../../studies/prompt-sensitivity/noise2/` — cache-busted partial rerun
- `../../studies/prompt-sensitivity/control/` — positive control
- `scripts/prompt_gates.py` — gate tables
- `src/takeoff_bench/prompts.py`, `runner.py`, `providers.py`, `scoring.py` —
  variant registry, cache-bust nonce, prompt/config/response metadata, and
  per-instance IoU output

## Next

A stronger positive control is required before prompt tuning is worth running:
either use a task where the constraint removal demonstrably changes all three
models, or use more items and repeats and pre-register a smaller minimum effect.
Do not lower the gate after seeing this result.
