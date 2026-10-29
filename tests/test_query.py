from speclens.query import expand_query


def test_expansion_keeps_original_question_numbers_and_identifiers():
    query = "ABX00083 için 24 V giriş gerilimi uygun mu?"
    expanded = expand_query(query)
    assert expanded.startswith(query)
    assert "input" in expanded and "voltage" in expanded
    assert "48" not in expanded


def test_technical_english_question_does_not_get_irrelevant_translation():
    query = "What is the VIN voltage range?"
    assert expand_query(query) == query
