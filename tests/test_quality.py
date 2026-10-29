import json

import pytest

from speclens.evidence import claim_atoms, evidence_lines, parse_span_extraction, validate_evidence
from speclens.intent import requested_fields

SOURCE = {
    "id": "board:p2:b0",
    "document_id": "board",
    "page": 2,
    "sha256": "a" * 64,
    "text": "VIN range is 6–24 V.\nGPIO voltage is 3.3 V.\nPart number AFX00002 supports Wi-Fi.",
}


def test_citation_text_is_selected_from_source_not_generated():
    _, spans = evidence_lines([SOURCE])
    response = {
        "findings": [
            {
                "document_id": "board",
                "field": "vin_voltage",
                "status": "stated",
                "value": "6-24 V",
                "evidence_ids": ["e0000"],
            }
        ]
    }
    parsed = parse_span_extraction(json.dumps(response), spans)
    result = validate_evidence(parsed, [SOURCE], {"board"}, ["vin_voltage"], True)
    assert result["findings"][0]["citations"][0]["quote"] == SOURCE["text"].replace("\n", " ")
    response["findings"][0]["value"] = "6–48 V"
    result = validate_evidence(
        parse_span_extraction(json.dumps(response), spans),
        [SOURCE],
        {"board"},
        ["vin_voltage"],
        True,
    )
    assert not result["findings"]
    assert "value_atoms_missing_from_citations" in result["rejected_findings"][0]["reasons"]


def test_nonexistent_span_cannot_be_silently_attached_to_another_source():
    with pytest.raises(ValueError, match="Unknown evidence ID"):
        parse_span_extraction(
            json.dumps(
                {
                    "findings": [
                        {
                            "document_id": "a",
                            "field": "voltage",
                            "status": "stated",
                            "value": "24 V",
                            "evidence_ids": ["invented"],
                        }
                    ]
                }
            ),
            {},
        )


def test_unrequested_fields_are_rejected_even_with_real_quotes():
    _, spans = evidence_lines([SOURCE])
    parsed = parse_span_extraction(
        json.dumps(
            {
                "findings": [
                    {
                        "document_id": "board",
                        "field": "gpio_voltage",
                        "status": "stated",
                        "value": "3.3 V",
                        "evidence_ids": ["e0000"],
                    }
                ]
            }
        ),
        spans,
    )
    result = validate_evidence(parsed, [SOURCE], {"board"}, ["vin_voltage"], True)
    assert result["rejected_findings"][0]["reasons"] == ["field_outside_request"]


def test_numbers_preserve_sign_and_codes_do_not_match_substrings():
    assert claim_atoms("-20–50 °C") == claim_atoms("-20...50 °C")
    assert claim_atoms("3.30 V") == claim_atoms("3.3 V")
    assert claim_atoms("AFX00002") != claim_atoms("AFX00003")
    assert claim_atoms("24 V") != claim_atoms("240 V")
    assert claim_atoms("-40 °C") != claim_atoms("40 °C")


def test_duplicate_fields_with_different_values_reject_both():
    from speclens.evidence import parse_extraction

    findings = [
        {
            "document_id": "board",
            "field": "voltage",
            "status": "stated",
            "value": value,
            "citations": [{"chunk_id": SOURCE["id"], "quote": SOURCE["text"]}],
        }
        for value in ("24 V", "3.3 V")
    ]
    checked = validate_evidence(
        parse_extraction(json.dumps({"findings": findings})), [SOURCE], {"board"}
    )
    assert not checked["findings"]
    assert len(checked["rejected_findings"]) == 2


@pytest.mark.parametrize(
    "question,fields",
    [
        ("Hangi SKU Wi-Fi sunar?", ["wifi_sku"]),
        ("What is the retail price in lira?", ["retail_price"]),
        (
            "Önerilen ortam sıcaklığı ile EUT sıcaklık sınırı?",
            ["ambient_temperature", "eut_temperature"],
        ),
        ("What is the recommended VIN voltage range?", ["vin_voltage"]),
        ("How many digital I/O pins?", ["digital_io_count"]),
        ("How much SRAM and flash memory?", ["sram_capacity", "flash_capacity"]),
        ("What voltage do the digital and analog pins use?", ["gpio_voltage"]),
        ("Dijital ve analog pinlerin gerilimi kaç volt?", ["gpio_voltage"]),
    ],
)
def test_request_fields_do_not_add_related_capabilities(question, fields):
    assert requested_fields(question) == fields
