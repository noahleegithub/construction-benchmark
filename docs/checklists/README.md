# Design verification checklists

Korean architectural design-verification checklists, translated into English and
consolidated into one review document.

## Sources

| File | Role | Date |
|---|---|---|
| `source/design-verification-architecture-250701-policy.xlsx` | Policy draft (`방침용`) | 2025-07-01 |
| `source/design-verification-architecture-250709-release.xlsx` | Distribution release (`배포용`) | 2025-07-09 |

Both workbooks cover the same 135 checklist items. The 2025-07-09 release is
used as the base because it consolidates line-wrapped checkpoint text into one
row per check point.

## Outputs

| File | Contents |
|---|---|
| `architecture-design-verification-checklist.md` | Readable checklist, one section per item, with checkboxes |
| `architecture-design-verification-checklist.csv` | Bilingual table (English + Korean) for review and analysis |
| `architecture-design-verification-checklist.json` | Machine-readable bilingual records |

## Consolidation

- **Items:** 135 in both workbooks; 135/135 item texts are identical after
  whitespace and punctuation normalization. No item exists in only one file.
- **Checkpoints:** the 2025-07-09 release has 453 consolidated checkpoints; the
  2025-07-01 draft has 490 fragments because wrapped lines were stored as
  separate entries. All 490 draft fragments are substrings of the release text
  after whitespace normalization (490/490), so the 37-entry difference is line
  wrapping, not lost content.
- **Duplicates:** the release contains no duplicate item text and no duplicate
  checkpoint string, within or across items. The version merge therefore did
  not need to drop content; it removed the draft's line-wrap artifacts.
- **Fields retained:** original ID, priority code, discipline, area, drawing,
  checklist item, checkpoints, additional comment, other note, basis,
  verification stage, subcategory, category, and deduction.

## Translation

Technical English, with a fixed glossary for Korean construction terms
(design verification, check point, net area, fire compartment, direct stair,
refuge area, piloti, and so on). Numbers, dimensions, drawing codes, article
numbers and references are preserved verbatim. The Korean text is kept in the
CSV and JSON alongside the translation.

The Korean source is authoritative. This translation has not been certified by
the issuing organization; verify critical clauses against the workbook before
using them in a contract or approval submission.

## Deduction basis

The `감점분류표` (deduction classification) sheet is reproduced as Appendix A of
the Markdown document, with the existing and proposed rates.

## Use in this repository

The checklist is a domain reference for the takeoff benchmark. It is not
benchmark ground truth: it describes what a reviewer checks, not the geometry
or quantity expected on a particular sheet. It is useful for deriving review
questions, failure taxonomies and task families.

## Rights

The source workbooks were supplied by the user. They are kept locally under
`source/` and are gitignored; check the issuing organization's redistribution
terms before publishing them or a derived translation outside this project.
