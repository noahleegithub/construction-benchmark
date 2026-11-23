# Multi-sheet page relevance

Run: `studies/page-decisions/answers.jsonl`

- records: 792
- successful: 792
- tasks: 33
- models: valen-0.8b, valen-2b, valen-4b

Each packet has one source-sheet target and 7 distractors from other task families. The target is the positive label; distractors are negatives. This is a synthetic packet, not a real multi-page project plan.

## Overall

| Model | Packets | Target recall | Distractor FPR | Accuracy | Mean rank | Rank-1 | Mean AUC | Target p | Distractor p |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `valen-0.8b` | 33 | 1.000 | 0.853 | 0.254 | 3.45 | 10/33 | 0.647 | 0.672 | 0.605 |
| `valen-2b` | 33 | 0.970 | 0.918 | 0.193 | 3.36 | 12/33 | 0.660 | 0.879 | 0.803 |
| `valen-4b` | 33 | 0.818 | 0.446 | 0.587 | 2.48 | 19/33 | 0.786 | 0.796 | 0.457 |

## By task

| Task | `valen-0.8b` | `valen-2b` | `valen-4b` |
|---|---:|---:|---:|
| `t-012-tagged-light-fixtures` | rank 1, p 0.80 | rank 1, p 0.99 | rank 1, p 1.00 |
| `t-1ce-symbol-instances` | rank 3, p 0.59 | rank 6, p 0.94 | rank 6, p 0.83 |
| `t-236-balcony-areas` | rank 3, p 0.70 | rank 1, p 0.98 | rank 1, p 0.96 |
| `t-280-net-room-areas` | rank 2, p 0.79 | rank 1, p 0.98 | rank 1, p 1.00 |
| `t-29b-floratam-sod-areas` | rank 1, p 0.77 | rank 1, p 0.97 | rank 1, p 0.98 |
| `t-2ce-symbol-instances` | rank 8, p 0.50 | rank 8, p 0.49 | rank 8, p 0.03 |
| `t-404-led-light-symbols` | rank 4, p 0.55 | rank 6, p 0.77 | rank 2, p 0.84 |
| `t-43e-net-room-areas` | rank 1, p 0.66 | rank 6, p 0.79 | rank 3, p 0.93 |
| `t-4c4-wall-centerlines` | rank 3, p 0.67 | rank 3, p 0.94 | rank 1, p 0.96 |
| `t-4f1-door-threshold-areas` | rank 1, p 0.76 | rank 1, p 0.96 | rank 1, p 1.00 |
| `t-6bb-building-footprint` | rank 6, p 0.65 | rank 4, p 0.98 | rank 2, p 0.93 |
| `t-888-wall-centerlines` | rank 8, p 0.61 | rank 4, p 0.94 | rank 5, p 0.68 |
| `t-911-chair-symbols` | rank 5, p 0.52 | rank 4, p 0.97 | rank 1, p 0.99 |
| `t-99f-siding-wall-areas` | rank 3, p 0.66 | rank 1, p 0.99 | rank 1, p 1.00 |
| `t-9c3-duplex-receptacles` | rank 1, p 0.69 | rank 5, p 0.92 | rank 4, p 0.27 |
| `t-b9c-net-room-areas` | rank 1, p 0.76 | rank 2, p 0.98 | rank 1, p 1.00 |
| `t-bc8-elevation-stone-areas` | rank 2, p 0.72 | rank 2, p 0.92 | rank 1, p 0.80 |
| `t-classroom-net-areas` | rank 4, p 0.73 | rank 6, p 0.85 | rank 1, p 0.90 |
| `t-corridor-net-area` | rank 1, p 0.79 | rank 1, p 0.99 | rank 1, p 0.97 |
| `t-d9e-site-paving-areas` | rank 6, p 0.69 | rank 3, p 0.98 | rank 1, p 0.97 |
| `t-door-centerline-contractor` | rank 4, p 0.54 | rank 6, p 0.61 | rank 6, p 0.48 |
| `t-door-centerlines` | rank 2, p 0.65 | rank 4, p 0.77 | rank 7, p 0.03 |
| `t-room-lights` | rank 2, p 0.86 | rank 1, p 1.00 | rank 1, p 0.99 |
| `t-smoke-detectors` | rank 3, p 0.75 | rank 1, p 1.00 | rank 1, p 0.99 |
| `t-tle-bxd-duplex-receptacle` | rank 1, p 0.94 | rank 3, p 0.97 | rank 1, p 0.99 |
| `t-tle-pdk-plant-mulch-symbols` | rank 1, p 0.58 | rank 1, p 0.98 | rank 1, p 0.98 |
| `t-tle-rvk-sprinkler-rooms` | rank 1, p 0.71 | rank 1, p 1.00 | rank 1, p 0.99 |
| `t-tle-sgt-toilets` | rank 4, p 0.61 | rank 3, p 0.97 | rank 2, p 0.98 |
| `t-wall-centerline-3218` | rank 2, p 0.74 | rank 1, p 0.85 | rank 1, p 0.84 |
| `t-wall-centerline-a5-4` | rank 8, p 0.50 | rank 6, p 0.55 | rank 7, p 0.02 |
| `t-wall-centerline-ocala` | rank 8, p 0.58 | rank 7, p 0.64 | rank 4, p 0.42 |
| `t-wall-centerline-page-10` | rank 6, p 0.60 | rank 4, p 0.81 | rank 3, p 0.77 |
| `t-wall-perimeter-painters` | rank 8, p 0.51 | rank 7, p 0.53 | rank 4, p 0.78 |

## Misses

Targets that were not the top-ranked page, or were below 0.5:

| Task | Model | Target p | Rank | Max distractor |
|---|---|---:|---:|---:|
| `t-tle-sgt-toilets` | `valen-4b` | 0.976 | 2 | 0.991 |
| `t-b9c-net-room-areas` | `valen-2b` | 0.975 | 2 | 0.985 |
| `t-6bb-building-footprint` | `valen-4b` | 0.932 | 2 | 0.996 |
| `t-bc8-elevation-stone-areas` | `valen-2b` | 0.925 | 2 | 0.971 |
| `t-room-lights` | `valen-0.8b` | 0.860 | 2 | 0.909 |
| `t-404-led-light-symbols` | `valen-4b` | 0.837 | 2 | 0.875 |
| `t-280-net-room-areas` | `valen-0.8b` | 0.786 | 2 | 0.792 |
| `t-wall-centerline-3218` | `valen-0.8b` | 0.737 | 2 | 0.793 |
| `t-bc8-elevation-stone-areas` | `valen-0.8b` | 0.721 | 2 | 0.751 |
| `t-door-centerlines` | `valen-0.8b` | 0.653 | 2 | 0.694 |
| `t-d9e-site-paving-areas` | `valen-2b` | 0.977 | 3 | 0.984 |
| `t-tle-sgt-toilets` | `valen-2b` | 0.973 | 3 | 0.991 |
| `t-tle-bxd-duplex-receptacle` | `valen-2b` | 0.971 | 3 | 0.993 |
| `t-4c4-wall-centerlines` | `valen-2b` | 0.941 | 3 | 0.985 |
| `t-43e-net-room-areas` | `valen-4b` | 0.927 | 3 | 0.996 |
| `t-wall-centerline-page-10` | `valen-4b` | 0.772 | 3 | 0.896 |
| `t-smoke-detectors` | `valen-0.8b` | 0.750 | 3 | 0.909 |
| `t-236-balcony-areas` | `valen-0.8b` | 0.697 | 3 | 0.807 |
| `t-4c4-wall-centerlines` | `valen-0.8b` | 0.674 | 3 | 0.834 |
| `t-99f-siding-wall-areas` | `valen-0.8b` | 0.657 | 3 | 0.695 |

## Caveat

The TLE release has only single-page PDFs. These packets are synthetic: one task source sheet plus distractors from other task families. The labels measure source-sheet retrieval, not professional relevance judgments on a real multi-sheet plan. The target page is the only positive by construction; some distractors may still contain useful drawing content.
