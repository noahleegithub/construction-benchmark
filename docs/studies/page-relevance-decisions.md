# Multi-sheet page relevance decisions

Experiment: for each TLE task, ask a decision model whether a page in a
multi-sheet plan packet is relevant to the task.

## Data limitation

The TLE release contains **only single-page PDFs** (33 PDFs, one page each).
There is no real multi-page project plan in the release. The experiment therefore
builds controlled packets:

- one **target** page: the task's own source sheet;
- seven **distractor** pages sampled from other task families;
- target and distractors shuffled into an 8-page packet.

The target is the positive label and the distractors are negative labels. This
measures source-sheet retrieval, not professional relevance judgments on a real
project plan. A distractor can still contain useful drawing content.

## API and prompt

- `POST https://api.valen-team.workers.dev/v1/decisions`
- Free endpoint; no API key.
- Models: `valen-0.8b`, `valen-2b`, `valen-4b`.
- One image per request; one predicate question.
- The page is rendered as a full sheet at up to 1200 px.
- The prompt states that exactly one page is the source sheet and that most
  pages are distractors; it asks whether this page is the source sheet needed
  for the task.
- Yes means `probability >= 0.5`.

## Metrics

- **Target recall**: target page gets yes.
- **Distractor FPR**: fraction of the seven distractor pages that get yes.
- **Accuracy**: correct page-level labels over all eight pages.
- **Target rank**: rank of the target among the eight probabilities (1 is best).
- **AUC**: probability that the target outranks a randomly chosen distractor.
- **Margin**: target probability minus the highest distractor probability.

## Full run

33 tasks × 8 pages × 3 models = **792/792 successful requests**.

| Model | Target recall | Distractor FPR | Accuracy | Mean rank | Rank-1 | AUC | Target p | Distractor p |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `valen-0.8b` | 1.000 | 0.853 | 0.254 | 3.45 | 10/33 | 0.647 | 0.672 | 0.605 |
| `valen-2b` | 0.970 | 0.918 | 0.193 | 3.36 | 12/33 | 0.660 | 0.879 | 0.803 |
| `valen-4b` | **0.818** | **0.446** | **0.587** | **2.48** | **19/33** | **0.786** | 0.796 | 0.457 |

`valen-4b` is clearly the best of the three: it rejects about half the
distractors, ranks the target first in 19 of 33 packets, and has the highest
AUC. It is still not a reliable yes/no classifier: target recall is 0.818 and
packet accuracy is only 0.587.

`valen-2b` is the worst at the threshold: it finds 32/33 targets but accepts
91.8% of distractors, so its page-level accuracy is 0.193. `valen-0.8b` accepts
85.3% of distractors and gets 25.4% accuracy. Both behave like “is this a
drawing?” classifiers rather than task-specific page selectors.

The target is ranked first in only 10/33 (0.8B), 12/33 (2B), and 19/33 (4B)
packets. The hardest cases are:

| Task | 0.8B rank | 2B rank | 4B rank |
|---|---:|---:|---:|
| `t-2ce-symbol-instances` | 8 | 8 | 8 |
| `t-wall-centerline-a5-4` | 8 | 6 | 7 |
| `t-wall-centerline-ocala` | 8 | 7 | 4 |
| `t-wall-centerline-page-10` | 6 | 4 | 3 |
| `t-wall-perimeter-painters` | 8 | 7 | 4 |
| `t-door-centerline-contractor` | 4 | 6 | 6 |

On `t-012-tagged-light-fixtures`, `t-29b-floratam-sod-areas`,
`t-4f1-door-threshold-areas`, and `t-corridor-net-area`, all three models rank
the target first. That is not enough for page filtering because most distractors
also receive yes.

### Pilot

The first 8-page pilot (`t-012`) showed the same pattern: target rank 1, but
7/8 or 8/8 pages accepted at the 0.5 threshold. The full run confirms it.

## Caveat

The packet labels are synthetic and the distractor set is not a real plan-set
sample. The run tests whether a decision model can use task semantics to rank
pages; it does not measure performance on a real multi-sheet project plan. A
real plan also often has more than one relevant page (floor plan, enlarged
detail, schedule, general notes), which this one-positive packet does not model.
