# t-4f1 door-clearance audit

The widths in `audit.csv` are derived from the TLE threshold polygons and the sheet's `1/8 in = 1 ft` scale. They are provisional until the boxes are checked against the drawn door openings.

For each row, open the crop and confirm:

1. the red/green box sits on the door opening, not the leaf or swing;
2. the measured width is the clear opening between jambs;
3. the verdict matches the 900 mm rule.

Rows marked `borderline=yes` are within 20 mm of the threshold; most failures are 35.00 in (889 mm), so a small scale or jamb-convention error flips the verdict. Resolve those first.

Record the checked width in `audit_width_mm`, the checked verdict in `audit_verdict`, and any discrepancy in `audit_notes`. Do not edit the derived columns in place; they are the comparison baseline.
