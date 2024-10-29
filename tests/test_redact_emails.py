import pytest
from redactor import Redactor

def test_redact_emails():
    redactor = Redactor()
    input_text = "Contact us at manj@gmail.com for details."
    expected_output = "Contact us at ██████████████ for details."
    redacted_text = redactor.redact_emails(input_text)
    assert redacted_text == expected_output
