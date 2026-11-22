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

## Results

Run: `studies/page-decisions/summary.md`.

### Pilot

`t-012-tagged-light-fixtures`, 8-page packet, three models:

| Model | Target p | Target rank | Max distractor | Yes rate |
|---|---:|---:|---:|---:|
| `valen-0.8b` | 0.795 | 1 | 0.750 | 8/8 |
| `valen-2b` | 0.995 | 1 | 0.983 | 8/8 |
| `valen-4b` | 0.996 | 1 | 0.991 | 7/8 |

The target ranks first for all three models, but almost every distractor also
gets yes. At a 0.5 threshold, this packet has accuracy 0.125 for 0.8B and 2B and
0.250 for 4B. The models are ranking pages, not producing usable page-level
yes/no decisions.

## Caveat

The packet labels are synthetic and the distractor set is not a real plan-set
sample. The run is useful for testing whether a decision model can use task
semantics to rank pages, not for claiming field accuracy.
