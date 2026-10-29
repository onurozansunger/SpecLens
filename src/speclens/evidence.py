from __future__ import annotations

import json
import re
from collections import Counter
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .common import normalize


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Citation(StrictModel):
    chunk_id: str = Field(min_length=1, max_length=160)
    quote: str = Field(min_length=8, max_length=1000)


class Finding(StrictModel):
    document_id: str = Field(min_length=1, max_length=120)
    field: str = Field(min_length=1, max_length=100)
    status: Literal["stated", "not_stated", "conflicting"]
    value: str | None = Field(default=None, max_length=500)
    citations: list[Citation] = Field(default_factory=list, max_length=8)


class Extraction(StrictModel):
    findings: list[Finding] = Field(max_length=12)


class SpanFinding(StrictModel):
    document_id: str = Field(min_length=1, max_length=120)
    field: str = Field(min_length=1, max_length=100)
    status: Literal["stated", "not_stated", "conflicting"]
    value: str | None = Field(default=None, max_length=500)
    evidence_ids: list[str] = Field(default_factory=list, max_length=8)


class SpanExtraction(StrictModel):
    findings: list[SpanFinding] = Field(max_length=12)


def evidence_lines(chunks: list[dict]) -> tuple[list[dict], dict]:
    """Assign request-local IDs; quotes and page metadata remain server-owned."""
    context, spans = [], {}
    for chunk in chunks:
        parts, current = [], []
        # Keep complete source lines together where possible, especially table rows.
        for source_line in chunk["text"].splitlines():
            line_parts, words = [], []
            for word in normalize(source_line).split():
                if words and len(" ".join(words + [word])) > 450:
                    line_parts.append(" ".join(words))
                    words = []
                words.append(word)
            if words:
                line_parts.append(" ".join(words))
            for line in line_parts:
                if current and len(" ".join(current + [line])) > 450:
                    parts.append(" ".join(current))
                    current = []
                current.append(line)
        if current:
            parts.append(" ".join(current))
        lines = []
        for part in parts:
            span_id = f"e{len(spans):04d}"
            spans[span_id] = {"chunk_id": chunk["id"], "quote": part}
            lines.append(f"{span_id}: {part}")
        context.append({"document_id": chunk["document_id"], "page": chunk["page"], "lines": lines})
    return context, spans


def parse_span_extraction(text: str, spans: dict) -> Extraction:
    parsed = SpanExtraction.model_validate(json.loads(text))
    findings = []
    for finding in parsed.findings:
        citations = []
        for span_id in dict.fromkeys(finding.evidence_ids):
            if span_id not in spans:
                raise ValueError(f"Unknown evidence ID: {span_id[:100]}")
            citations.append(spans[span_id])
        findings.append(
            {
                **finding.model_dump(exclude={"evidence_ids"}),
                "citations": citations,
            }
        )
    return Extraction.model_validate({"findings": findings})


def claim_atoms(text: str) -> set[str]:
    """Necessary lexical support, not a semantic entailment or unit-conversion check."""
    text = normalize(text).replace("−", "-")
    text = re.sub(r"(?<=\d)\s*[-–—]\s*(?=\d)", " ", text)
    text = re.sub(r"\.{2,}", " ", text)
    numbers = {
        "number:" + str(Decimal(n.replace(",", ".")).normalize())
        for n in re.findall(r"(?<![\w.])[-+]?\d+(?:[.,]\d+)?", text)
    }
    codes = {
        "code:" + code.casefold()
        for code in re.findall(r"\b[A-Za-z][A-Za-z_-]*\d[A-Za-z0-9_-]*\b", text)
    }
    return numbers | codes


def parse_extraction(text: str) -> Extraction:
    # Reject prose, partial JSON and code fences rather than silently repairing claims.
    return Extraction.model_validate(json.loads(text))


def validate_evidence(
    extraction: Extraction,
    chunks: list[dict],
    allowed_documents: set[str],
    required_fields: list[str] | None = None,
    check_claim_atoms: bool = False,
) -> dict:
    """Validate provenance and literal quotes; this does not prove claim entailment."""
    sources = {c["id"]: c for c in chunks}
    findings, rejected = [], []
    counts = Counter((f.document_id, f.field.casefold()) for f in extraction.findings)
    for finding in extraction.findings:
        errors, citations = [], []
        key = (finding.document_id, finding.field.casefold())
        if counts[key] > 1:
            errors.append("duplicate_document_field")
        if finding.document_id not in allowed_documents:
            errors.append("document_outside_request")
        if required_fields and finding.field not in required_fields:
            errors.append("field_outside_request")
        if finding.status == "not_stated":
            if finding.value is not None or finding.citations:
                errors.append("not_stated_must_have_null_value_and_no_citations")
        elif not finding.value or not finding.citations:
            errors.append("stated_or_conflicting_requires_value_and_evidence")
        distinct_citations = {(c.chunk_id, normalize(c.quote)) for c in finding.citations}
        if finding.status == "conflicting" and len(distinct_citations) < 2:
            errors.append("conflict_requires_multiple_citations")
        for citation in finding.citations:
            source = sources.get(citation.chunk_id)
            if source is None:
                errors.append("unknown_chunk")
                continue
            if source["document_id"] != finding.document_id:
                errors.append("cross_document_citation")
            if normalize(citation.quote) not in normalize(source["text"]):
                errors.append("quote_not_in_source")
            citations.append(
                {
                    "chunk_id": citation.chunk_id,
                    "quote": citation.quote,
                    "document_id": source["document_id"],
                    "page": source["page"],
                    "pdf_sha256": source["sha256"],
                }
            )
        if check_claim_atoms and finding.value and finding.status != "not_stated":
            quoted = " ".join(c["quote"] for c in citations)
            if claim_atoms(finding.value) - claim_atoms(quoted):
                errors.append("value_atoms_missing_from_citations")
        if errors:
            rejected.append({"finding": finding.model_dump(), "reasons": sorted(set(errors))})
        else:
            findings.append(
                {
                    **finding.model_dump(),
                    "citations": citations,
                    "provenance_verified": finding.status != "not_stated",
                    "semantic_support": "not_automatically_verified",
                    "absence_scope": "retrieved_context_only"
                    if finding.status == "not_stated"
                    else None,
                }
            )
    return {"findings": findings, "rejected_findings": rejected}
