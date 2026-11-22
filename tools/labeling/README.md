# Drawing Labeler

A local-only browser tool for labeling:

- **sheets** in a multi-page PDF, or
- **OCG layers** in a layered PDF.

Upload a PDF, enter the task prompt, and mark each sheet or layer as
**Relevant**, **Not relevant**, or **Unsure**. The page or layer preview renders
with PDF.js. In layer mode, clicking a layer name isolates that layer for
preview; the label buttons on the row record whether that layer is relevant.
The left/right or up/down arrow keys move through layers while Layers mode is
active; in Sheets mode the left/right arrows move between pages.

Labels are stored in `localStorage` for the current file and can be exported as
JSON or CSV. No file or label leaves the browser.

## Run

### Double-click / one command

The folder includes a stdlib-only launcher:

```bash
python3 start.py
```

On Windows use `start.bat`; on macOS/Linux use `./start.sh`. It chooses a free
port, serves this folder, and opens the browser.

To send it to a colleague, zip the entire `tools/labeling` folder. They need
Python 3, but no packages and no network access. `vendor/` contains PDF.js.

### Manual server

From the repository root:

```bash
python3 -m http.server 8765 --bind 0.0.0.0
```

Open:

```
http://<host>:8765/tools/labeling/
```

For the local server, `http://localhost:8765/tools/labeling/` works. Using
`file://` directly may fail because ES modules and the PDF.js worker need an
HTTP origin.

## Export

The JSON export includes:

- `file` metadata and page count
- `task_prompt`
- every page with `label` and `relevant` (`true`, `false`, or `null`)
- every OCG layer with `id`, `name`, `label`, and `relevant`

The CSV has one row per page or layer and the same fields.

## Notes

- PDF.js is vendored under `vendor/` (`pdfjs-dist 4.10.38`); the tool works
  without a CDN.
- PDFs without OCGs show the Layers tab disabled.
- The layer list is flat; nested OCG groups are displayed by their individual
  group names.
- The current page is still used as the render target in layer mode, so a
  multi-page layered PDF can be labeled page by page.
