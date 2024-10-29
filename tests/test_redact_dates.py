import pytest
from redactor import Redactor

def test_redact_dates():
    redactor = Redactor()
    input_text = "The event is on 18/06/2001 and 18 Jun 2001."
    expected_output = "The event is on ██████████ and ███████████."
    redacted_text = redactor.redact_dates(input_text)
    assert redacted_text == expected_output
