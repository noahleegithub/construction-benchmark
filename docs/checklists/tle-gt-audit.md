# TLE threshold polygons are not clear-width ground truth

**Status:** audit finding, 2026-11-12. The `t-4f1` clear-width compliance task is
retired.

## What was tested

The TLE `t-4f1-door-threshold-areas` annotations contain 104 door-threshold
polygons. On a sheet at `1/8 in = 1 ft`, the long side of each polygon was
converted to a real-world width and compared with a 900 mm clear-opening rule.
That produced 46 derived failures.

## Audit result

A visual audit checked all 46 derived failures plus 20 spatially spread passing
controls against the drawn door openings.

- 45 of the 46 derived failures were reclassified as passing at 900 mm.
- The 41 rows at 35.00 in (889 mm) fail because the threshold polygon includes
  the door stop; the polygon's long side is not the clear opening.
- The one remaining fail, a 25.99 in closet door, is outside the auditor's scope.
- Four rows (30–34 in) had notes that the polygon was short or left a gap; those
  are additional evidence of annotation error, not evidence of noncompliance.
- Passing controls were all passing, but the same double-door type varied by
  about 1 in between polygons.

Under the auditor's scope there are **zero noncompliant doors** on this sheet.

## Implication

TLE's threshold polygons describe the drawn threshold/stop condition, not the
clear opening between jambs, and they are not consistent at the 1 in level. They
cannot be used to derive code-compliance ground truth.

This does not invalidate TLE's geometry score: threshold-area IoU remains a valid
measure of agreement with the vendor polygon. It invalidates the compliance task
built on top of those polygons because the semantic object is different.

The earlier 900 mm failure score (0.487 for `gpt-5.6-sol`) is withdrawn. The task
and its derived ground truth were removed from the active workspace; the audit
pack and retired ground truth are preserved under
`study/gateway/audit/t-4f1/`.

## Next

Use a drawing with actual noncompliant doors and measure the clear opening
manually, with a second adjudicator. Alternatively, keep this sheet as a
zero-failure control that tests false positives. Do not reuse the threshold
polygons as a compliance label.
