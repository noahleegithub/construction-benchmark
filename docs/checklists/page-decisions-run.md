# Page relevance decisions

Synthetic multi-sheet packet experiment using the free Valen decisions API.

- 33 TLE tasks → 33 packets
- 8 pages per packet: one source-sheet target, seven distractors from other task families
- 3 models: `valen-0.8b`, `valen-2b`, `valen-4b`
- **792/792 requests succeeded**
- one image per request; one predicate question per page
- `summary.md` has target recall, distractor false-positive rate, accuracy, target rank, AUC
- `summary_by_task_model.csv` and `per_page.csv` have the details
- `images/` holds the rendered packet pages

The TLE release has only single-page PDFs, so these packets are constructed, not
real multi-page plan sets. See
`../../docs/checklists/page-relevance-decisions.md` for the caveat.
