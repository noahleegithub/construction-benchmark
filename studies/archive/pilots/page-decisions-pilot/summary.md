# Multi-sheet page relevance

Run: `studies/page-decisions-pilot/answers.jsonl`

- records: 24
- successful: 24
- tasks: 1
- models: valen-0.8b, valen-2b, valen-4b

Each packet has one source-sheet target and 7 distractors from other task families. The target is the positive label; distractors are negatives. This is a synthetic packet, not a real multi-page project plan.

## Overall

| Model | Packets | Target recall | Distractor FPR | Accuracy | Mean rank | Rank-1 | Mean AUC | Target p | Distractor p |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `valen-0.8b` | 1 | 1.000 | 1.000 | 0.125 | 1.00 | 1/1 | 1.000 | 0.795 | 0.615 |
| `valen-2b` | 1 | 1.000 | 1.000 | 0.125 | 1.00 | 1/1 | 1.000 | 0.995 | 0.926 |
| `valen-4b` | 1 | 1.000 | 0.857 | 0.250 | 1.00 | 1/1 | 1.000 | 0.996 | 0.762 |

## By task

| Task | `valen-0.8b` | `valen-2b` | `valen-4b` |
|---|---:|---:|---:|
| `t-012-tagged-light-fixtures` | rank 1, p 0.80 | rank 1, p 0.99 | rank 1, p 1.00 |

## Misses

Targets that were not the top-ranked page, or were below 0.5:

| Task | Model | Target p | Rank | Max distractor |
|---|---|---:|---:|---:|

## Caveat

The TLE release has only single-page PDFs. These packets are synthetic: one task source sheet plus distractors from other task families. The labels measure source-sheet retrieval, not professional relevance judgments on a real multi-sheet plan. The target page is the only positive by construction; some distractors may still contain useful drawing content.
