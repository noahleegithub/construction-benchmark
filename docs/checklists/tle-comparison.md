# Checklist vs TLE: coverage comparison

This note compares the translated 2025 architectural design-verification
checklist with Togal's *Construction's Last Exam* (TLE) benchmark.

- Checklist: 135 items, 453 checkpoints, 5 areas, 114 items with a cited basis.
- TLE: 60 tasks — 31 geometric, 24 drawing-reasoning, 5 end-to-end.

The comparison is at the level of **evidence and question type**, not wording.
The per-item classification is in `tle-comparison.csv`; it assigns each item a
primary evidence type, which is an analyst judgment rather than a benchmark
label.

## 1. The two corpora ask different kinds of question

| | Design checklist | TLE |
|---|---|---|
| Unit | Review item with checkpoints | Drawing task with ground-truth output |
| Output | Pass/fail or comply/not-comply judgment, deduction points | Polygon, polyline, point set, string, count, or quantity |
| Scoring | Deduction schedule | IoU, F1, string match, quantity error |
| Knowledge | Code clauses, internal standards, performance criteria | None; the prompt states the convention |
| Scope | Architecture design review | Geometry extraction, document QA, takeoff |
| Scale | 135 items over a whole project | 60 tasks over individual sheets and sets |

Every checklist item is normative: "verify adequacy", "comply with", "confirm".
Every TLE task is descriptive: "trace", "locate", "read", "report". That
difference is the first finding: **there are no directly shared items**, only
shared evidence.

## 2. Evidence profile

Each checklist item was assigned the evidence needed to decide it:

| Evidence | Items | Share | TLE family that could supply it |
|---|---:|---:|---|
| Area / region measurement | 14 | 10% | `area-extraction` (10 tasks) |
| Dimension, clearance, level | 50 | 37% | `drawing-qa` (7 tasks) |
| Detail, layer, schedule, material | 34 | 25% | `structured-detail-extraction` (9 tasks) |
| Symbol location / count | 8 | 6% | `image-search` (12 tasks) |
| Code or performance rule only | 21 | 16% | none |
| Coordination / document completeness | 8 | 6% | none |

So 106 of 135 items (79%) need a measurable primitive. TLE has a family for
each of those four primitives. Twenty-nine items (21%) have no measurable
primitive at all.

That is coverage in principle, not in practice. TLE's 60 tasks target a narrow
set of elements:

- Area: rooms, balconies, footprint, door thresholds, siding, stone, sod, and
  paving. It does not target refuge areas, parking bays, ventilation openings,
  or the floor areas of welfare facilities.
- Dimension: one unit width, one window size, one mirror height, one sprinkler
  standard, one CCTV circuit, one trade attribution, one fastener spacing.
  There is no generic "read this dimension" task.
- Detail: wall and ceiling layer build-ups. There is no finish schedule, door
  schedule, or fire-resistance assembly task.
- Symbols: lights, receptacles, toilets, sinks, sprinklers, smoke detectors,
  plants, and photometric points. There is no mailbox, sump, EV charger, or
  accessibility-symbol task.
- Wall centerlines: nine tasks, but the checklist almost never asks for a
  centerline. It asks whether a wall assembly performs.

## 3. Where the two touch

No checklist item is answerable end-to-end by a TLE task. The closest analogues
share an element but not the question:

| Checklist item | TLE task or family | Shared | Still missing |
|---|---|---|---|
| 41. Adequacy of the main apartment floor plan | `t-b9c`, `t-280`, `t-43e` net room areas | Room polygons and areas | Layout adequacy, minimum room dimensions, circulation |
| 46. Adequacy of small window sizes | `t-medium-ocala-w25-window-plan-dimensions` | Window dimensions | Daylight, egress, ventilation, and the adequacy threshold |
| 31, 34, 47, 51, 86, 99. Door performance and clearance | Door centerlines (`t-door-centerlines`), threshold areas (`t-4f1`), e2e door quantities (`t-ddd`) | Door element, position, count | Fire rating, clear width, swing, hardware, threshold detail |
| 23–29, 96, 117–118. Finish criteria | e2e carpet, flooring, and painting takeoffs (`t-fff`, `t-kkk`, `t-nnn`, `t-ooo`) | Finish areas and quantities | Specification compliance, substrate, junction details |
| 28, 32, 36, 57–60, 98, 103–104, 133. Waterproofing, insulation, condensation | Wall-type and ceiling detail extraction (`t-medium-crosby-a607-*`, `t-medium-mwc-a84-*`) | Layer names and order | Performance criteria, continuity, thermal and moisture behavior |
| 39. Minimize masonry walls | Wall centerlines and e2e wall areas (`t-4c4`, `t-eee`) | Wall geometry and area | Material selection rule, structural and acoustic trade-offs |
| 80. Mailbox installation criteria | `image-search` family only | Counting/localization primitive | Mailbox symbols, ratios by tenure, integration with parcel systems |
| 110. Parking layout criteria | None; only generic area extraction | Area primitive | Stall dimensions, aisle width, column clearance, code compliance |

The shared vocabulary is therefore real but shallow: rooms, walls, doors,
windows, finishes, details, and symbols appear in both. The questions do not.

## 4. What each covers that the other does not

**Checklist-only**

- Code and standard compliance: district plans, housing-vulnerable unit ratios,
  fire doors, refuge areas, direct stairs, evacuation stairs, accessibility,
  daycare and welfare-facility criteria.
- Performance: inter-floor noise grades, zero-energy insulation grades,
  condensation risk, waterproofing continuity, ventilation, smoke control.
- Coordination: architectural–structural–civil–MEP drawing consistency, area
  table reconciliation, drawing completeness.
- Systems the benchmark does not model: vertical transport, parking layout,
  ramps, drainage networks, MEP/structural interfaces, barrier-free design.
- Judgment: "adequate", "appropriate", "comply" — no ground-truth geometry.

**TLE-only**

- Dense instance enumeration: 5,793 photometric points, 848 door centerlines,
  447 wall segments.
- Verbatim legend lookup and sheet-wide text search.
- Detail-layer extraction from wall and ceiling assemblies.
- Scope-constrained, multi-sheet quantity takeoff: doors by class, gross and net
  wall area, carpet by finish tag, electrical devices, drywall by assembly.
- A scoring apparatus: instance matching, IoU, precision/recall, cardinality.

## 5. The gap neither covers

The central gap is **measurement plus rule**: neither corpus asks a model to
obtain a measurement and then decide whether it satisfies a criterion.

- The checklist supplies the rule and the tolerance, but assumes a human reads
  the dimension or area.
- TLE supplies the measurement primitive, but never applies a rule to it.

Examples that fall between them:

1. **Clear width.** "Is the corridor clear width at least 1.2 m?" requires
   measuring the clear distance between finished faces and applying a code
   threshold. TLE has no corridor-width task; the checklist states the rule but
   not the measurement.
2. **Parking geometry.** "Does each stall meet 2.5 × 5.0 m with a 6 m aisle?"
   TLE has no parking task; the checklist has a layout item but no measurement
   protocol.
3. **Refuge area.** "Is the refuge area at least 2 ㎡?" TLE can trace a region;
   the checklist states the threshold; neither joins the two.
4. **Door clear width and fire rating.** TLE can locate a door and measure a
   threshold; the checklist checks performance and fire resistance; neither asks
   for both.
5. **Daylight or ventilation ratio.** "Is the window area at least one-eighth of
   the floor area?" TLE can trace windows only as dimensions in one QA item; the
   checklist requires the ratio but does not measure it.

Four further gaps are outside both:

- **Cross-sheet and cross-discipline consistency.** Checklist items 13, 19, 21,
  73 and 94 ask for it; TLE's end-to-end tasks span sheets but only sum
  quantities, with no consistency check between architectural, structural and
  MEP drawings.
- **System-level performance.** Energy grades, acoustic grades, fire-resistance
  ratings and condensation risk need simulation or multi-layer reasoning; the
  checklist cites the criteria, TLE extracts none of the inputs.
- **Constructability and sequencing.** Neither corpus asks how the design would
  be built, inspected or staged.
- **Cost and design-change impact.** The checklist assigns deduction points and
  TLE produces quantities, but neither asks for the cost or programme
  consequence of a design decision.

## 6. What a combined benchmark would add

A checklist-derived extension to TLE would have four fields per task:

1. **Measurement** — the quantity to extract (clear width, area, count, layer
   thickness).
2. **Rule** — the code or internal criterion, with the clause and tolerance.
3. **Verdict** — pass, fail, or indeterminate, with the measured value.
4. **Evidence** — the geometry or sheet reference supporting the verdict.

That schema would cover the 106 measurable checklist items and make the 29
rule-only items explicit: they are not drawing-measurement tasks unless a
measurable proxy is defined.

The practical conclusion is that the checklist and TLE are complementary rather
than overlapping. TLE is an extraction benchmark with almost no design-rule
content; the checklist is a rule base with almost no formal measurement. The
uncovered middle — measure, apply the rule, show the evidence — is the most
valuable place to extend either one.
