from decimal import Decimal

import pint
import pytest
from pydantic import ValidationError

from speclens.numeric import NumericRange, compare_vin_findings, range_contains


def test_voltage_unit_conversion_and_inclusive_boundary():
    spec = NumericRange(lower="6", upper="24", unit="V", scope="recommended_vin")
    assert range_contains(spec, Decimal(24000), "mV", "recommended_vin")["within_documented_range"]
    assert not range_contains(spec, Decimal("24.001"), "V", "recommended_vin")[
        "within_documented_range"
    ]


def test_incompatible_units_and_scopes_are_rejected():
    spec = NumericRange(lower="6", upper="24", unit="V", scope="recommended_vin")
    with pytest.raises(pint.DimensionalityError):
        range_contains(spec, Decimal(24), "second", "recommended_vin")
    with pytest.raises(ValueError, match="scopes"):
        range_contains(spec, Decimal(24), "V", "gpio_voltage")


@pytest.mark.parametrize("low,high", [("24", "6"), ("NaN", "24"), ("6", "Infinity")])
def test_invalid_ranges_fail(low, high):
    with pytest.raises(ValidationError):
        NumericRange(lower=low, upper=high, unit="V", scope="recommended_vin")


def test_cited_numbers_must_match_claim_before_comparison():
    result = {
        "documents": ["a"],
        "findings": [
            {
                "document_id": "a",
                "status": "stated",
                "provenance_verified": True,
                "value": "6-48 V",
                "citations": [{"quote": "Recommended input voltage (VIN) is 6-24 V"}],
            }
        ],
    }
    assert compare_vin_findings(result, Decimal(24))[0]["status"] == "review_required"
    result["findings"][0]["value"] = "6-24 V"
    assert compare_vin_findings(result, Decimal(24))[0]["within_documented_range"]


def test_gpio_quote_cannot_be_treated_as_vin():
    result = {
        "documents": ["a"],
        "findings": [
            {
                "document_id": "a",
                "status": "stated",
                "provenance_verified": True,
                "value": "0-5 V",
                "citations": [{"quote": "GPIO voltage range is 0-5 V"}],
            }
        ],
    }
    assert compare_vin_findings(result, Decimal(3))[0]["status"] == "review_required"


def test_range_unit_must_match_its_specification_scope():
    with pytest.raises(ValidationError, match="Unit does not match"):
        NumericRange(lower="6", upper="24", unit="second", scope="recommended_vin")


@pytest.mark.parametrize(
    "header,value,status",
    [
        (
            "Recommended Operating Conditions Symbol Description Min Typ Max Unit",
            "6 7.0 24 V",
            "computed",
        ),
        (
            "Recommended Operating Conditions Symbol Description Max Typ Min Unit",
            "6 7.0 24 V",
            "review_required",
        ),
        ("", "6 7.0 24 V", "review_required"),
        (
            "Recommended Operating Conditions Symbol Description Min Typ Max Unit",
            "6 9.0 24 V",
            "review_required",
        ),
        (
            "Recommended Operating Conditions Symbol Description Min Typ Max Unit",
            "6 7.0 48 V",
            "review_required",
        ),
    ],
)
def test_vin_table_requires_ordered_header_and_matching_values(header, value, status):
    quote = "V IN Input voltage from VIN pad / DC Jack 6 7.0 24 V"
    result = {
        "documents": ["a"],
        "evidence": [{"document_id": "a", "chunk_id": "a:p6", "text": f"{header} {quote}"}],
        "findings": [
            {
                "document_id": "a",
                "status": "stated",
                "provenance_verified": True,
                "value": value,
                "citations": [{"chunk_id": "a:p6", "quote": quote}],
            }
        ],
    }
    row = compare_vin_findings(result, Decimal(24))[0]
    assert row["status"] == status
    if status == "computed":
        assert row["lower"] == "6" and row["upper"] == "24"
        assert row["within_documented_range"]
        assert header in row["citation"]["scope_quote"]
