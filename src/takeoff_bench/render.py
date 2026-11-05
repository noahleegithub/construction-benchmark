"""PDF page rendering."""

from __future__ import annotations

import io
from pathlib import Path

import pymupdf as fitz
from PIL import Image


def render_pdf_page(
    path: Path,
    page_number: int,
    dpi: int = 150,
    max_side: int = 2400,
) -> tuple[bytes, tuple[int, int]]:
    """Render a 1-based PDF page to PNG bytes.

    Raises ``FileNotFoundError`` for a missing file and ``ValueError`` for a
    page outside the document.
    """
    if not path.exists():
        raise FileNotFoundError(path)
    with fitz.open(path) as document:
        if not 1 <= page_number <= document.page_count:
            raise ValueError(
                f"page {page_number} outside 1..{document.page_count} for {path.name}"
            )
        pixmap = document[page_number - 1].get_pixmap(dpi=dpi, alpha=False)
        image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)

    if max(image.size) > max_side:
        scale = max_side / max(image.size)
        image = image.resize(
            (max(1, round(image.width * scale)), max(1, round(image.height * scale))),
            Image.Resampling.LANCZOS,
        )

    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue(), image.size
