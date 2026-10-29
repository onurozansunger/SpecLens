from __future__ import annotations

import re
from decimal import Decimal
from typing import Literal

import pint
from pint.errors import PintError
from pydantic import ConfigDict, Field, model_validator

from .common import normalize
from .evidence import StrictModel

UNITS = pint.UnitRegistry(non_int_type=Decimal)


class NumericRange(StrictModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    lower: Decimal
    upper: Decimal
    unit: str = Field(min_length=1, max_length=30)
    scope: Literal[
        "recommended_vin", "gpio_voltage", "operating_temperature", "storage_temperature"
    ]

    @model_validator(mode="after")
    def ordered(self):
        if self.lower > self.upper:
            raise ValueError("Range lower bound exceeds upper bound")
        expected_unit = "kelvin" if self.scope.endswith("temperature") else "volt"
        try:
            UNITS.Quantity(Decimal(0), self.unit).to(expected_unit)
        except (PintError, TypeError) as exc:
            raise ValueError("Unit does not match the specification scope") from exc
        return self


def range_contains(spec: NumericRange, value: Decimal, unit: str, scope: str) -> dict:
    if scope != spec.scope:
        raise ValueError("Cannot compare different specification scopes")
    if not value.is_finite():
        raise ValueError("Target must be finite")
    converted = UNITS.Quantity(value, unit).to(spec.unit).magnitude
    return {
        "within_documented_range": spec.lower <= converted <= spec.upper,
        "target": str(value),
        "target_unit": unit,
        "converted_target": str(converted),
        "range_unit": spec.unit,
        "lower": str(spec.lower),
        "upper": str(spec.upper),
        "bounds": "inclusive",
        "scope": scope,
    }


VIN_RANGE = re.compile(
    r"(?:VIN(?:\s+range)?|(?:recommended\s+)?input\s+voltage\s*\(VIN\))"
    r"\s*(?:is\s+)?(?P<lower>\d+(?:\.\d+)?)\s*[-–]\s*"
    r"(?P<upper>\d+(?:\.\d+)?)\s*V\b",
    re.IGNORECASE,
)
VALUE_RANGE = re.compile(r"(?P<lower>\d+(?:\.\d+)?)\s*[-–]\s*(?P<upper>\d+(?:\.\d+)?)\s*V\b")
HEADER_RANGE = re.compile(
    r"recommended input voltage range is\s*(?P<lower>\d+(?:\.\d+)?)\s*[-–]\s*(?P<upper>\d+(?:\.\d+)?)\s*V\b",
    re.IGNORECASE,
)
VIN_TABLE = re.compile(
    r"Recommended Operating Conditions\s+Symbol Description Min Typ Max Unit\s+"
    r"(?P<row>V\s*IN Input voltage from VIN pad(?: / DC Jack)? "
    r"(?P<lower>\d+(?:\.\d+)?) (?P<typical>\d+(?:\.\d+)?) "
    r"(?P<upper>\d+(?:\.\d+)?) V\b)",
    re.IGNORECASE,
)
VALUE_TRIPLE = re.compile(
    r"(?P<lower>\d+(?:\.\d+)?) (?P<typical>\d+(?:\.\d+)?) "
    r"(?P<upper>\d+(?:\.\d+)?) V",
    re.IGNORECASE,
)


def compare_vin_findings(result: dict, target: Decimal, unit: str = "V") -> list[dict]:
    """Conservative demo: compare only literal VIN ranges copied from verified quotes.

    Accept an ordered Min/Typ/Max VIN row only with its source table header.
    Other table layouts and inferred ranges produce review_required.
    """
    rows = []
    for document in result["documents"]:
        candidates = []
        for finding in result.get("findings", []):
            if finding["document_id"] != document or finding["status"] != "stated":
                continue
            if not finding.get("provenance_verified"):
                continue
            value_matches = list(VALUE_RANGE.finditer(normalize(finding["value"])))
            triple = VALUE_TRIPLE.fullmatch(normalize(finding["value"]))
            if len(value_matches) != 1 and triple is None:
                continue
            value = triple if triple is not None else value_matches[0]
            value_range = (Decimal(value["lower"]), Decimal(value["upper"]))
            for citation in finding["citations"]:
                match = VIN_RANGE.search(normalize(citation["quote"]))
                scope_quote = None
                if match is None:
                    source = next(
                        (
                            c
                            for c in result.get("evidence", [])
                            if c["chunk_id"] == citation.get("chunk_id")
                            and c["document_id"] == document
                        ),
                        None,
                    )
                    if source:
                        text, quote = normalize(source["text"]), normalize(citation["quote"])
                        position = text.find(quote)
                        prefix = text[max(0, position - 60) : position] if position >= 0 else ""
                        if re.search(r"\bVIN Rating\s*$", prefix):
                            match = HEADER_RANGE.search(quote)
                            scope_quote = prefix + quote
                        if match is None:
                            table = VIN_TABLE.search(text)
                            if table and table["row"] in quote:
                                typical_matches = triple is None or (
                                    Decimal(triple["typical"]) == Decimal(table["typical"])
                                )
                                if typical_matches and (
                                    Decimal(table["lower"])
                                    <= Decimal(table["typical"])
                                    <= Decimal(table["upper"])
                                ):
                                    match = table
                                    scope_quote = table.group(0)
                if match and (Decimal(match["lower"]), Decimal(match["upper"])) == value_range:
                    candidates.append((value_range, {**citation, "scope_quote": scope_quote}))
        distinct = {c[0] for c in candidates}
        if len(distinct) != 1:
            rows.append(
                {
                    "document_id": document,
                    "status": "review_required",
                    "reason": "No unique literal VIN range supported by the cited quote",
                }
            )
            continue
        bounds, citation = candidates[0]
        spec = NumericRange(lower=bounds[0], upper=bounds[1], unit="V", scope="recommended_vin")
        rows.append(
            {
                "document_id": document,
                "status": "computed",
                **range_contains(spec, target, unit, "recommended_vin"),
                "citation": citation,
            }
        )
    return rows
