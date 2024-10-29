import pytest
from redactor import Redactor

def test_redact_address():
    redactor = Redactor()
    text = "The office is located at Main St, Gainesville, FL 32601."
    expected_output = "The office is located at ███████, ███████████, ██ 32601."
    redacted_text = redactor.redact_address(text)
    assert redacted_text == expected_output
    assert redactor.stats["addresses"] == 3
