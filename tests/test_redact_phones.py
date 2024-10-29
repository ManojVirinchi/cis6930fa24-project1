import pytest
from redactor import Redactor

def test_redact_phones():
    redactor = Redactor()
    input_text = "Call me at 352-769-7890."
    expected_output = "Call me at ████████████."
    redacted_text = redactor.redact_phones(input_text)
    assert redacted_text == expected_output
