import pytest
from BlueLLMTeam.utils.text import extract_json_from_text

def test_valid_json_square_brackets():
    text = "Some text before [ { \"key1\": \"value1\" }, { \"key2\": \"value2\" } ] some text after"
    expected = [{"key1": "value1"}, {"key2": "value2"}]
    assert extract_json_from_text(text) == expected

def test_valid_json_curly_brackets():
    text = "Some text before { \"key1\": \"value1\", \"key2\": \"value2\" } some text after"
    expected = {"key1": "value1", "key2": "value2"}
    assert extract_json_from_text(text) == expected

def test_invalid_json():
    text = "Some text before [ { \"key1\": \"value1\", { \"key2\": \"value2\" } some text after"
    with pytest.raises(ValueError, match="Invalid JSON data"):
        extract_json_from_text(text)

def test_no_json_data():
    text = "Some text before and after with no JSON data"
    with pytest.raises(ValueError, match="No opening bracket found"):
        extract_json_from_text(text)

def test_json_with_extra_text_inside():
    text = "Some text before [ { \"key1\": \"value1\" } ] and { \"key2\": \"value2\" } some text after"
    with pytest.raises(ValueError, match="Invalid JSON data"):
        extract_json_from_text(text)

def test_empty_brackets():
    text = "Some text before [] some text after"
    expected = []
    assert extract_json_from_text(text) == expected

def test_empty_curly_brackets():
    text = "Some text before {} some text after"
    expected = {}
    assert extract_json_from_text(text) == expected
