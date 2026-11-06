# Turning the checklist into difficult benchmark tasks

The checklist and TLE meet at a useful seam: TLE can extract evidence, the
checklist supplies rules, and neither asks a model to join them. The difficult
benchmark is therefore not "more geometry". It is **measure, apply the rule,
commit to a verdict, and show the evidence**.

TLE's failure profile says which levers make this hard:

- recall collapses as instance count rises (5,793 points → 380 emitted);
- adjacent regions are merged (83 classrooms → 3 polygons);
- derived lines are offset by half a wall thickness;
- near-miss legend entries are chosen instead of the correct one;
- end-to-end scope disagreements produce 5× spreads in wall area and 29× spreads
  in device counts.

Each of those becomes a difficulty control below.

## Design principles

1. **Closed-world rules.** Put the clause, threshold, units and exceptions in
   the prompt. The task should test application, not memorised code.
2. **Compose, don't extract.** One task should require at least two of:
   locate, measure, resolve scope, apply a rule, reconcile, report evidence.
3. **Set-level answers.** Ask for every instance, a per-sheet count and a total.
   Single-instance accuracy is not the hard part.
4. **Evidence-bearing output.** Every verdict carries the sheet, region or
   dimension that supports it. Score the evidence, not just the answer.
5. **Deterministic ground truth.** Prefer rules with numeric thresholds and
   measurable geometry. Avoid aesthetic or jurisdiction-ambiguous judgments.

## Task families

| Family | Example | Why it is hard | Output |
|---|---|---|---|
| Measure-and-rule compliance | "Does every unit-entry door meet the required clear width and fire rating?" | Requires finished-face measurement, schedule lookup, exception handling, verdict | Per-door measured value, rating, verdict, evidence |
| Scope-constrained takeoff | "Count D-3 doors on levels 2–9 of the east tower, excluding unit entries and the podium" | Scope must be inferred from the set; typical floors multiply; exclusions are easy to miss | Per-sheet counts, total, scope ledger |
| Cross-sheet reconciliation | "The fire plan, architectural plan and door schedule disagree; list every inconsistency and the corrected count" | Requires revision awareness, document hierarchy, set-level consistency | Inconsistency list, governing document, corrected values |
| Dense enumeration | "Locate every fire damper on all mechanical sheets" | Recall collapses with N; symbols vary by legend; rotated sheets | Per-sheet point sets and counts |
| Derived geometry with filters | "Trace drywall wall centerlines, excluding shaft and exterior walls, broken at openings" | Medial axis, wall thickness, opening topology, scope filtering | Polylines with wall type and segment IDs |
| Assembly performance | "Does wall type W-12 meet the required U-value and fire rating? Name the layer that fails." | Multi-layer assembly, unit conversion, bridging, threshold lookup | Per-assembly verdict and failing layer |
| Change impact | "If this wall moves 300 mm, what quantities and cost change?" | Measurement plus delta plus rate application | Delta schedule with affected quantities |

## Three worked tasks

### A. Door clear width and fire rating

**Prompt.** Using the level 2–9 unit plans, the door schedule, and the code card
in `/workspace`, report for every unit-entry door: clear width in mm, fire rating
in minutes, and pass/fail against the stated criteria. If a door cannot be
resolved, return `indeterminate` and say what is missing.

**Ground truth.** Per door: measured clear width (finished frame to finished
frame), schedule rating, verdict. Tolerance ±10 mm on width; exact on rating.

**Scoring.** 0.4 verdict accuracy, 0.4 measurement error within tolerance, 0.2
evidence (sheet, door ID, dimension string). An incorrect pass is penalised more
than an explicit indeterminate, but indiscriminate abstention scores zero.

**Difficulty controls.** Corner units with angled frames; double doors; borrowed
lites; a schedule revision that changes one rating; nominal vs finished opening;
doors shown only on the enlarged unit plan.

**Why frontier models fail.** This combines TLE's door-centerline weakness with a
schedule lookup and a rule. A model that traces the door leaf, or reads the
nominal opening, produces a confident wrong verdict.

### B. Scope-constrained door count

**Prompt.** Count type D-3 hollow-metal doors on levels 2–9 of the east tower.
Exclude unit-entry doors, podium doors, and doors shown only on the alternating
floor plan. Report counts per sheet and the total, with the sheets you treated as
in scope.

**Ground truth.** Counts by sheet and total, plus the in-scope sheet list.

**Scoring.** 0.4 count F1, 0.3 scope-sheet precision/recall, 0.2 total
reconciliation, 0.1 evidence. A correct total with the wrong scope is capped.

**Difficulty controls.** A sheet index with decoy levels; typical-floor notation;
one addendum sheet; a door type that appears in two schedules; a mirrored tower.

**Why frontier models fail.** This is the end-to-end failure mode: models do not
hold a scope ledger, multiply typical floors inconsistently, and reconcile to a
total that is internally inconsistent.

### C. Cross-sheet inconsistency

**Prompt.** Compare the fire-compartment plan, the architectural plan and the
door schedule. List every inconsistency: element ID, the two conflicting values,
which document governs under the stated hierarchy, and the corrected value.

**Ground truth.** A set of inconsistency tuples, each with element, values,
governing document and corrected value.

**Scoring.** Precision/recall over tuples; governing-document accuracy; corrected
value accuracy. Partial credit per tuple.

**Difficulty controls.** Three sheets, two revisions, one superseded note; a
schedule that is correct but keyed to an old plan; a compartment boundary that
moves by one grid line.

**Why frontier models fail.** TLE's e2e tasks already show that models do not
maintain a consistent measurement basis across sheets. This task makes that
failure the answer.

## Difficulty ladder

1. **Single-sheet, one rule.** Measure a clear width and apply a threshold.
2. **Single-sheet, set-level.** Every door or stall on the sheet, per-sheet count.
3. **Multi-sheet scope.** Infer the in-scope sheets and multiply typical floors.
4. **Revision reconciliation.** Two revisions, one governing hierarchy.
5. **Full-set audit.** Several rules, dense sheets, explicit abstention.

Do not jump to level 5. Levels 1–2 produce clean ground truth and expose whether
the model can measure at all; levels 3–4 are where the interesting failures are.

## Ground-truth production

- Write a **rule card** per item: clause text, threshold, units, exceptions,
  decision logic and acceptable evidence.
- Annotate each instance with measured value, evidence coordinates or sheet
  reference, and verdict. Two annotators, adjudicated disagreements.
- Where the PDF has vector geometry, compute the measurement directly and store
  the computation; do not eyeball it.
- Keep an `indeterminate` class for genuinely unreadable or missing evidence.
- Store the drawing revision and the rule-card version with every item.

## Harness integration

Add three task types to `takeoff-bench`:

- `compliance` — measurement + rule + verdict;
- `scope_quantity` — counts with an explicit scope ledger;
- `consistency` — tuples of conflicting values and the governing document.

A compliance ground truth can be as small as:

```json
{
  "type": "compliance",
  "criteria": {"clear_width_mm": 850, "fire_rating_min": 20},
  "instances": [
    {"id": "D-101", "measure": 900, "unit": "mm", "rating": 20,
     "verdict": "pass", "evidence": {"sheet": "A-201", "region": [0.31, 0.44, 0.36, 0.47]}}
  ]
}
```

Score verdict, measurement error, evidence overlap and abstention separately.
Report each family on its own; a single mean will hide the difference between
"cannot measure" and "cannot apply the rule".

## What to avoid

- **Code-recall tasks.** If the answer is in the prompt's rule card, the task is
  reading comprehension. The difficulty must be in locating and measuring.
- **Ambiguous aesthetics.** "Is the layout good?" has no reproducible ground
  truth. Use numeric criteria or expert adjudication with a rubric.
- **Single-instance items.** They reward local perception and hide the recall
  collapse that matters at set scale.
- **Text-only answers.** Require a measured value and an evidence reference, or
  the model can bluff.

## A two-week starting point

Pick three rules with hard numbers and existing checklist backing: accessible
door clear width (item 86), parking-stall geometry (item 110), and refuge-area
minimum (item 55). Annotate five sheets, 15–20 instances, two annotators. Run
five models at three repeats. If the models cannot beat a trivial baseline on
level 1, the task is calibrated; then add scope and revision controls.

That gives a benchmark that is hard for the right reason: the model must hold a
measurement model, resolve the scope, apply a rule, and defend the answer with
evidence.
