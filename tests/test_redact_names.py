import pytest
from redactor import Redactor

def test_redact_names():
    redactor = Redactor()
    text = "Manoj Virinc and Chester Bennington are performing in the concert."
    expected_output = "████████████ and ██████████████████ are performing in the concert."
    redacted_text = redactor.redact_names(text)
    assert redacted_text == expected_output
    assert redactor.stats["names"] == 2
