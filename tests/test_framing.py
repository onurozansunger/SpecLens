import pytest

from speclens.framing import complete_json_object


@pytest.mark.parametrize(
    "text", ['{"a":', '{"a": [1,2}', 'Here is {"a": 1}', "```json\n{}", '{"a": "unterminated}']
)
def test_stream_framing_does_not_repair_invalid_or_incomplete_output(text):
    assert complete_json_object(text) is None


def test_stream_framing_ignores_braces_inside_strings_and_stops_at_root():
    value = '{"a": "a } brace and \\"quote", "nested": {"b": 1}}'
    assert complete_json_object(value + '"') == value
    assert complete_json_object('{"a": [1, {"b": 2}]}') == '{"a": [1, {"b": 2}]}'
