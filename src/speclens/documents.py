from __future__ import annotations

from pathlib import Path
from threading import Lock

from .common import ROOT, digest, read_json

RENDER_LOCK = Lock()


def document_file(document_id: str, root: Path = ROOT) -> tuple[Path, dict]:
    manifest = read_json(root / "data/raw/manifest.json")
    document = next((d for d in manifest["documents"] if d["id"] == document_id), None)
    if document is None:
        raise ValueError("Unknown document")
    path = root / document["pdf_path"]
    if digest(path) != document["pdf_sha256"]:
        raise ValueError("PDF snapshot changed; citation preview refused")
    return path, document


def render_page(document_id: str, page: int, root: Path = ROOT) -> Path:
    import pypdfium2 as pdfium

    path, document = document_file(document_id, root)
    if not 1 <= page <= document["pages"]:
        raise ValueError("Page is outside this PDF")
    cache = root / "data/processed/previews"
    cache.mkdir(parents=True, exist_ok=True)
    destination = cache / f"{document['pdf_sha256']}-p{page}.png"
    # PDFium is not thread-safe; serialize rendering across FastAPI worker threads.
    with RENDER_LOCK:
        if not destination.exists():
            with pdfium.PdfDocument(path) as pdf:
                image = pdf[page - 1].render(scale=1.4).to_pil()
                image.save(destination)
    return destination
