import pytest
from redactor import Redactor

def test_redact_dates():
    redactor = Redactor()
    input_text = "The event is on 19/03/2001 and 20 Mar 2001."
    expected_output = "The event is on ██████████ and ███████████."
    redacted_text = redactor.redact_dates(input_text)
    assert redacted_text == expected_output
