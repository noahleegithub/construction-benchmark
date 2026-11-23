# TLE area archive

Imported TLE area-extraction tasks used as the reference set for the gateway
experiments.

- 7 tasks: 4 net-room-area, 1 building footprint, 1 corridor, 1 door threshold.
- 19 archived models, 132 runs.
- Ground truth: `study/gt/`, copied from recoverable vendor page annotations.
- 124/132 archived runs reproduce published `tp/fp/fn`; see
  `validation.csv` and `DATA_NOTES.md`.

`report.md` and `scores.csv` use the importer's legacy table layout. Do not
compare its `Score` directly with the newer 32k GPT-6 tables without checking
the metric column: the archive reports `mean_iou` and `TLE mIoU`, not F1.
