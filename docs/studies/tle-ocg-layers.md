# TLE PDF optional content groups

Checked all 33 TLE release PDFs with PyMuPDF (`Document.get_ocgs()` and
`Document.layer_ui_configs()`). **14 have OCGs; 19 do not.**

## Coverage

| Task | OCGs |
|---|---:|
| `t-236-balcony-areas` | 58 |
| `t-280-net-room-areas` | 79 |
| `t-43e-net-room-areas` | 67 |
| `t-99f-siding-wall-areas` | 44 |
| `t-bc8-elevation-stone-areas` | 44 |
| `t-corridor-net-area` | 63 |
| `t-012-tagged-light-fixtures` | 148 |
| `t-404-led-light-symbols` | 17 |
| `t-911-chair-symbols` | 44 |
| `t-4c4-wall-centerlines` | 65 |
| `t-wall-centerline-3218` | 82 |
| `t-wall-centerline-a5-4` | 76 |
| `t-wall-centerline-page-10` | 44 |
| `t-wall-perimeter-painters` | 65 |

No OCGs: `t-29b`, `t-4f1`, `t-6bb`, `t-b9c`, `t-classroom`, `t-d9e`,
`t-1ce`, `t-2ce`, `t-9c3`, `t-room-lights`, `t-smoke-detectors`, the four
`t-tle-*` page extracts, `t-888`, `t-door-centerline-contractor`,
`t-door-centerlines`, and `t-wall-centerline-ocala`.

`t-9c3`, `t-room-lights`, and `t-smoke-detectors` have an empty
`/OCProperties` dictionary but zero optional content groups; they are not
layered.

## Layer names

Names are CAD/xref-derived, for example:

- Walls: `AR-WALL`, `AR-PARTITION`, `AR-EXTERIOR-WALL`,
  `AR-DEMISING-WALL`, `AR-WALL-CABINETS`
- Openings: `AR-DOOR`, `AR-DOORS`, `AR-EXTERIOR-DOORS`, `AR-SLIDER-MARK`,
  `AR-WINDOW`
- Annotation: `A-DIM`, `4-AR-DIM`, `A-AREA`, `4-AR-ROOM-NAME`,
  `4-AR-NOTES`, `SHT-TEXT`
- Structure: `S-GRID-LINE`, `S-COL-*`, `S-BEAM-*`, `S-SW-*`
- Sheet furniture: `REVISION-*`, `TITLEBLK`, `BORDERTEXT`
- Some sheets use generic CAD names such as `A | WALL | EXTERIOR.3D` and
  `A | DIM | INTERIOR.2D`.

## What it enables

The groups are functional, not just metadata. On `t-wall-centerline-3218`,
toggling groups at a 100 dpi render changed:

| Group | Matching OCGs | Pixels changed |
|---|---:|---:|
| Walls | 5 | 280,734 |
| Dimensions | 2 | 303,447 |
| Grid | 4 | 211,911 |
| Doors | 5 | 55,086 |
| Hatch | 2 | 46,935 |

That makes it possible to render clean wall/door linework with dimensions,
hatch, furniture, notes, grid, and title block removed.

## Layer decisions

A separate experiment asks the Valen decision API whether each single layer is
useful for its task: [`ocg-layer-decisions.md`](ocg-layer-decisions.md).

## Caveats

- OCG presence is not a clean semantic segmentation. Several `AR-WALL*` and
  `AR-DOOR*` groups exist per sheet, and some geometry is split across xrefs
  or remains in other layers.
- The groups are not consistent across tasks. The tasks with no OCGs cannot be
  layer-filtered at all.
- All groups are on by default, so the current renders are the full sheet; layer
  filtering has to be explicit.
