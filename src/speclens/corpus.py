from __future__ import annotations

import concurrent.futures
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pdfplumber

from .common import ROOT, digest, normalize, read_json, write_json, write_jsonl


def _download(url: str, destination: Path, *, pdf: bool = False) -> None:
    temporary = destination.with_suffix(destination.suffix + ".download")
    size = 0
    try:
        with httpx.stream("GET", url, follow_redirects=True, timeout=60) as response:
            response.raise_for_status()
            with temporary.open("wb") as f:
                for part in response.iter_bytes():
                    size += len(part)
                    if size > 50 * 1024 * 1024:
                        raise ValueError("Pilot document exceeds the 50 MB download limit")
                    f.write(part)
        if pdf and not temporary.read_bytes()[:5] == b"%PDF-":
            raise ValueError(f"Source did not return PDF bytes: {url}")
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)


def fetch_corpus(root: Path = ROOT) -> dict:
    config = read_json(root / "configs/corpus.json")
    raw = root / "data/raw"
    raw.mkdir(parents=True, exist_ok=True)
    manifest_path = raw / "manifest.json"
    existing = read_json(manifest_path).get("documents", []) if manifest_path.exists() else []
    previous = {row["id"]: row for row in existing if row.get("status") == "downloaded"}

    def fetch(document):
        directory = raw / document["id"]
        directory.mkdir(exist_ok=True)
        pdf, source = directory / "document.pdf", directory / "source.md"
        old = previous.get(document["id"])
        if old:
            if old["source_revision"] != document["source_revision"]:
                raise ValueError("Source revision changed: create a new corpus snapshot")
            if digest(pdf) != old["pdf_sha256"] or digest(source) != old["source_sha256"]:
                raise ValueError(f"Cached source integrity failure: {document['id']}")
            if old["pdf_sha256"] != document.get("expected_pdf_sha256", old["pdf_sha256"]):
                raise ValueError(
                    f"Cached PDF differs from the configured snapshot: {document['id']}"
                )
            if old["source_sha256"] != document.get("expected_source_sha256", old["source_sha256"]):
                raise ValueError(
                    f"Cached Markdown differs from configured snapshot: {document['id']}"
                )
            return old
        try:
            _download(document["source_url"], source)
            _download(document["pdf_url"], pdf, pdf=True)
            with pdfplumber.open(pdf) as parsed:
                pages = len(parsed.pages)
            if (
                document.get("expected_pdf_sha256")
                and digest(pdf) != document["expected_pdf_sha256"]
            ):
                raise ValueError(
                    "Producer PDF changed; preserve this run and create a new reviewed corpus snapshot"
                )
            if (
                document.get("expected_source_sha256")
                and digest(source) != document["expected_source_sha256"]
            ):
                raise ValueError("Pinned Markdown does not match the expected source hash")
            return {
                **document,
                "status": "downloaded",
                "pdf_path": str(pdf.relative_to(root)),
                "source_path_local": str(source.relative_to(root)),
                "pdf_sha256": digest(pdf),
                "source_sha256": digest(source),
                "pages": pages,
                "pdf_bytes": pdf.stat().st_size,
                "fetched_at": datetime.now(UTC).isoformat(),
                "source_pdf_revision_equivalence": "not_assumed",
            }
        except (httpx.HTTPError, ValueError) as exc:
            return {**document, "status": "failed", "error": str(exc)}

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        documents = list(pool.map(fetch, config["documents"]))
    result = {"purpose": config["purpose"], "documents": documents}
    write_json(manifest_path, result)
    failures = [d["id"] for d in documents if d["status"] != "downloaded"]
    if failures:
        raise RuntimeError(f"PDF download failed for {failures}; see {manifest_path}")
    return {"documents": len(documents), "pages": sum(d["pages"] for d in documents)}


def split_lines(text: str, max_chars: int = 1400) -> list[str]:
    """Keep reading order and overlap only complete source lines where possible."""
    lines = [normalize(line) for line in text.splitlines() if normalize(line)]
    blocks, current = [], []
    for line in lines:
        # Very long PDF lines are split on whitespace, never discarded.
        words = line.split()
        parts, part = [], []
        for word in words:
            if part and len(" ".join(part + [word])) > max_chars:
                parts.append(" ".join(part))
                part = []
            part.append(word)
        if part:
            parts.append(" ".join(part))
        for part in parts:
            if current and len("\n".join(current + [part])) > max_chars:
                blocks.append("\n".join(current))
                tail = current[-1]
                current = [tail] if len(tail) + len(part) + 1 <= max_chars else []
            current.append(part)
    if current:
        blocks.append("\n".join(current))
    return blocks


def extract_corpus(root: Path = ROOT) -> dict:
    manifest = read_json(root / "data/raw/manifest.json")
    pages, chunks = [], []
    for document in manifest["documents"]:
        if document["status"] != "downloaded":
            raise ValueError(f"Incomplete corpus: {document['id']}")
        path = root / document["pdf_path"]
        if digest(path) != document["pdf_sha256"]:
            raise ValueError(f"PDF changed: {document['id']}")
        with pdfplumber.open(path) as pdf:
            for number, page in enumerate(pdf.pages, start=1):
                text = page.extract_text(x_tolerance=2, y_tolerance=3) or ""
                tables = []
                for table in page.find_tables():
                    rows = table.extract()
                    tables.append({"bbox": list(table.bbox), "rows": rows})
                pages.append(
                    {
                        "document_id": document["id"],
                        "page": number,
                        "sha256": document["pdf_sha256"],
                        "text": text,
                        "width": page.width,
                        "height": page.height,
                        "tables": tables,
                        "text_layer_present": bool(text.strip()),
                    }
                )
                for idx, block in enumerate(split_lines(text)):
                    chunks.append(
                        {
                            "id": f"{document['id']}:p{number}:b{idx}",
                            "document_id": document["id"],
                            "page": number,
                            "family": document["family"],
                            "sha256": document["pdf_sha256"],
                            "kind": "page_text",
                            "text": block,
                        }
                    )
    processed = root / "data/processed"
    write_jsonl(processed / "pages.jsonl", pages)
    write_jsonl(processed / "chunks.jsonl", chunks)
    result = {
        "documents": len(manifest["documents"]),
        "pages": len(pages),
        "chunks": len(chunks),
        "tables_detected": sum(len(p["tables"]) for p in pages),
        "pages_without_text": sum(not p["text_layer_present"] for p in pages),
        "parser": "pdfplumber",
        "backend": "cpu",
        "accuracy_evaluated": False,
        "source_manifest_sha256": digest(root / "data/raw/manifest.json"),
    }
    write_json(processed / "extraction.json", result)
    return result
