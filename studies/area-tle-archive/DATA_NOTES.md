# TLE import notes

## Source

Public TLE asset bundle: `1_pdfs`, `2_togal_predictions`, `3_model_predictions`.
The bundle contains drawing PDFs, Togal platform predictions, and frontier-model
run dumps. It does **not** contain the benchmark's `tasks/` manifests, which hold
the expert ground truth.

## What was imported

7 area-extraction items: t-280-net-room-areas, t-43e-net-room-areas, t-4f1-door-threshold-areas, t-6bb-building-footprint, t-b9c-net-room-areas, t-classroom-net-areas, t-corridor-net-area.

Ground truth was recovered from the vendor's page annotations
(`togal_platform_page.json`, `geojson_regions`) and normalized to 0-1 page
coordinates. Recovery rules:

- `region`: every region polygon on the annotated page.
- `door_polygon`: every door polygon.
- `largest_region`: the largest region (corridor task).
- `largest_footprint`: the largest footprint polygon (building footprint task).

The recovered geometry was validated against the published per-run tp/fp/fn
counts; see `validation.csv`. Items were kept only when the counts matched.

## What was not imported

- 9 wall-extraction tasks: the bundle has Togal wall predictions but no centerline ground truth.
- 12 image-search tasks: the bundle has Togal point predictions but no symbol ground truth.
- 5 area tasks (`t-236-balcony-areas`, `t-29b-floratam-sod-areas`,
  `t-d9e-site-paving-areas`, `t-99f-siding-wall-areas`,
  `t-bc8-elevation-stone-areas`): the target regions cannot be identified
  unambiguously from the page annotations.

To import the rest, add the `tasks/` directory from
`github.com/Togal-ai-Team/tle-bench` (currently private) or supply the expected
geometry directly.

## Rights

The PDFs and vendor annotations are TLE/Togal assets. They are for local
evaluation only; do not redistribute them without permission.
