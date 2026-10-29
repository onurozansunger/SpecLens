"""Conservative literal capacity recovery when an LLM incorrectly abstains."""

import re
from decimal import Decimal

from .evidence import claim_atoms
from .intent import fold

VERSION = "literal-capacity-v1"


def recover_capacity(question: str, field: str, document: str, spans: dict, chunks: list[dict]):
    if field not in {"flash_capacity", "sram_capacity"}:
        return None
    q = fold(question)
    if not re.search(r"how much|capacity|kapasite|ne kadar", q):
        return None
    label = "flash" if field == "flash_capacity" else "(?:sram|ram)"
    pattern = re.compile(
        r"(?P<amount>\d+(?:\.\d+)?)\s*(?P<unit>[kKmMgG]B)\s+(?:on-chip\s+|internal\s+)?"
        + label
        + r"\b",
        re.IGNORECASE,
    )
    named_codes = {a for a in claim_atoms(question) if a.startswith("code:")}
    sources = {c["id"]: c for c in chunks}
    candidates = []
    for span in spans.values():
        if sources[span["chunk_id"]]["document_id"] != document:
            continue
        text = span["quote"]
        if named_codes - claim_atoms(text):
            continue
        lower = fold(text)
        if any(word in q for word in ("external", "harici")) and "external" not in lower:
            continue
        if any(word in q for word in ("internal", "dahili", "on-chip")) and not re.search(
            r"internal|on-chip", lower
        ):
            continue
        if re.search(r"\bmain\b|\bana\b", q) and "main" not in lower:
            continue
        for match in pattern.finditer(text):
            # Preserve byte-unit case; do not turn Mb (megabits) into MB (megabytes).
            if not match["unit"].endswith("B"):
                continue
            key = (Decimal(match["amount"]), match["unit"].casefold())
            candidates.append((key, f"{match['amount']} {match['unit']}", span))
    if len({c[0] for c in candidates}) != 1:
        return None
    _, value, citation = candidates[0]
    return {
        "document_id": document,
        "field": field,
        "status": "stated",
        "value": value,
        "citations": [citation],
    }
