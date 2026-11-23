# t-4f1 door-clearance audit review

## Status: retired

The audit confirmed the TLE threshold polygons are incorrect as a clear-width
ground truth. The user's explicit conclusion: **the door openings should pass**.
Every derived failure in this task is a false positive from the polygon, not a
noncompliant door.

## What was audited

66 rows: 46 derived failures plus 20 passing controls. The audit width and
verdict columns were filled for every row; the notes carry the measurement
reasoning.

## Result

- **45 of 46 derived failures were reclassified as passing at 900 mm.**
- 41 of those are 35.00 in (889 mm) rows. The polygon includes the door stop, so
  its long side is not the clear opening. The clear width is 900 mm.
- **F45**, a 25.99 in closet door, was marked fail but excluded from scope by the
  auditor.
- **F18, F24, F27, F46** had notes about a short polygon or a gap in the opening.
  Those notes are further evidence that the polygons are unreliable, not evidence
  of noncompliance.
- All **20 pass controls** were marked pass. Seven are double closet doors; the
  same door type varies by about 1 in between polygons (P10 71.99 in vs P12
  72.99 in; P05/P08 61.99 in vs P15 60.99 in).

## Consequence

The threshold polygons measure the drawn threshold/stop condition, not the clear
opening between jambs, and they are inconsistent at the 1 in level. The earlier
compliance score of **0.487 is withdrawn**; it measured agreement with a faulty
ground truth.

The `t-4f1-door-clearance` item has been removed from the active workspace.
`derived_gt_invalid.json` preserves the old ground truth for provenance, and
`retired_item.json` records the retirement. The audit pack remains as evidence.

## Next

1. Do not derive code-compliance ground truth from these threshold polygons.
2. Use a drawing with actual noncompliant doors, with the clear opening measured
   manually and adjudicated by a second annotator.
3. Alternatively, use this sheet only as a **zero-failure control**: the correct
   answer is that every in-scope door passes. That tests false positives, not
   failure detection.
4. A different task family (scope-constrained counts, cross-sheet reconciliation)
   does not depend on these polygons and can proceed in parallel.
