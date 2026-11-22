# OCG layer decision run

Full run of the Valen decisions API over every OCG layer in the TLE PDFs.

- 14 PDFs with OCGs; **898 layers**
- 3 models: `valen-0.8b`, `valen-2b`, `valen-4b`
- **2,694 successful requests**, no errors
- One image per request; one predicate question per layer
- Layer names withheld from the model
- `summary.md` has the overall and per-task tables
- `per_layer.csv` has one row per task/layer with all model probabilities
- `images/` holds the rendered single-layer images

This is an unlabelled model-judgment study. See
`../../docs/checklists/ocg-layer-decisions.md` for the interpretation and
caveats.
