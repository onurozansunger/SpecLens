import json

import pytest
from pydantic import ValidationError

from speclens.evidence import parse_extraction, validate_evidence

SOURCE = {
    "id": "board:p2:b0",
    "document_id": "board",
    "page": 2,
    "sha256": "a" * 64,
    "text": "Recommended VIN input is 6-24 V.\nGPIO voltage is 3.3 V.",
}


def extraction(**changes):
    finding = {
        "document_id": "board",
        "field": "VIN",
        "status": "stated",
        "value": "6-24 V",
        "citations": [{"chunk_id": SOURCE["id"], "quote": "Recommended VIN input is 6-24 V."}],
    }
    finding.update(changes)
    return parse_extraction(json.dumps({"findings": [finding]}))


def test_citation_page_and_hash_come_from_source():
    result = validate_evidence(extraction(), [SOURCE], {"board"})
    citation = result["findings"][0]["citations"][0]
    assert citation["page"] == 2
    assert citation["pdf_sha256"] == SOURCE["sha256"]
    assert result["findings"][0]["semantic_support"] == "not_automatically_verified"


@pytest.mark.parametrize(
    "citation,reason",
    [
        (
            {"chunk_id": SOURCE["id"], "quote": "Recommended VIN input is 6-48 V."},
            "quote_not_in_source",
        ),
        (
            {"chunk_id": "invented:p9:b0", "quote": "Recommended VIN input is 6-24 V."},
            "unknown_chunk",
        ),
    ],
)
def test_fabricated_provenance_is_rejected(citation, reason):
    result = validate_evidence(extraction(citations=[citation]), [SOURCE], {"board"})
    assert result["findings"] == []
    assert reason in result["rejected_findings"][0]["reasons"]


def test_cross_document_citation_is_rejected():
    result = validate_evidence(extraction(document_id="different"), [SOURCE], {"different"})
    assert "cross_document_citation" in result["rejected_findings"][0]["reasons"]


def test_model_cannot_supply_page_or_hash_metadata():
    with pytest.raises(ValidationError):
        extraction(citations=[{"chunk_id": SOURCE["id"], "quote": SOURCE["text"], "page": 99}])


def test_missing_evidence_has_only_context_scope():
    result = validate_evidence(
        extraction(status="not_stated", value=None, citations=[]), [SOURCE], {"board"}
    )
    assert result["findings"][0]["absence_scope"] == "retrieved_context_only"
    assert not result["findings"][0]["provenance_verified"]


def test_missing_evidence_cannot_claim_absence_of_feature():
    result = validate_evidence(
        extraction(status="not_stated", value="not supported", citations=[]), [SOURCE], {"board"}
    )
    assert result["findings"] == []


def test_repeating_same_quote_does_not_establish_conflict():
    citation = {"chunk_id": SOURCE["id"], "quote": "Recommended VIN input is 6-24 V."}
    result = validate_evidence(
        extraction(status="conflicting", citations=[citation, citation]), [SOURCE], {"board"}
    )
    assert "conflict_requires_multiple_citations" in result["rejected_findings"][0]["reasons"]


def test_malformed_output_is_not_repaired_into_a_claim():
    with pytest.raises(ValueError):
        parse_extraction('Here is JSON: {"findings": []}')


def test_quote_existence_does_not_establish_entailment():
    # This is deliberately a semantic error; provenance validation must not claim otherwise.
    result = validate_evidence(extraction(value="6-48 V"), [SOURCE], {"board"})
    assert result["findings"][0]["semantic_support"] == "not_automatically_verified"
