# TLE wall-centerline import notes

## Source

Public TLE asset bundle, `togal/wall-extraction/<task>/togal_platform_page.json`, `geojson_walls` features. PDFs are copied from `pdfs/index.json`.

## Ground truth status

- 7 items imported.
- 1 item(s) match the published expected count exactly: t-door-centerline-contractor
- 6 item(s) are approximate and are marked in `items.csv`: t-4c4-wall-centerlines, t-888-wall-centerlines, t-wall-centerline-3218, t-wall-centerline-a5-4, t-wall-centerline-ocala, t-wall-centerline-page-10

The public bundle does not contain the TLE `tasks/` manifests that hold the exact `wall_segments.segments` answer key. The recovered page annotations are usable for model comparison within this workspace, but they are not an official TLE reproduction. Do not report these counts as official TLE scores.

## Scoring

Segments are matched one-to-one when both endpoints fall within 0.012 of the page (12 units on the TLE 1000x1000 grid). Score is segment F1.

## Excluded

- `t-door-centerlines`: no page geometry in the bundle (expected 848).
- `t-wall-perimeter-painters`: perimeter linework, not a wall centerline task.
- `t-14b-wall-centerlines`: no page annotation in this bundle.
