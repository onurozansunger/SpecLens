from copy import deepcopy

from speclens.benchmark import score_result


def fixture():
    ref = {"document_id": "a", "page": 2, "pdf_sha256": "hash", "quote": "SRAM: 32 kB"}
    task = {
        "expected_findings": [
            {
                "document_id": "a",
                "field": "sram_capacity",
                "status": "stated",
                "value_patterns": [r"\b32\s*kB\b"],
                "evidence_groups": [[ref]],
            }
        ]
    }
    result = {
        "status": "provenance_checked",
        "findings": [
            {
                "document_id": "a",
                "field": "sram_capacity",
                "status": "stated",
                "value": "32 kB",
                "citations": [deepcopy(ref)],
            }
        ],
    }
    return task, result


def test_field_checks_do_not_find_expected_values_in_other_documents():
    task, result = fixture()
    assert score_result(task, result)["all_checks_passed"]
    result["findings"][0]["document_id"] = "b"
    checks = score_result(task, result)
    assert not checks["all_checks_passed"] and checks["extra_fields"] == 1


def test_value_without_matching_unit_or_source_is_not_a_task_pass():
    task, result = fixture()
    result["findings"][0]["value"] = "132 MB"
    assert not score_result(task, result)["all_checks_passed"]
    result["findings"][0]["value"] = "32 kB"
    result["findings"][0]["citations"][0]["page"] = 9
    assert not score_result(task, result)["all_checks_passed"]


def test_extra_or_duplicate_answers_fail_complete_task_check():
    task, result = fixture()
    extra = deepcopy(result["findings"][0])
    extra["field"] = "unrequested"
    result["findings"].append(extra)
    assert not score_result(task, result)["all_checks_passed"]
    result["findings"][1]["field"] = "sram_capacity"
    assert not score_result(task, result)["all_checks_passed"]
