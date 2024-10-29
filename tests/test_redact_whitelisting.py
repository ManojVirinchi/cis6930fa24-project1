import pytest
from redactor import Redactor
def test_redaction_whitelisting():
    redactor = Redactor()
    text = "Content-Type is not to be redacted. John Doe and Mike are names."
    result = redactor.redact_names(text)
    # Ensure whitelisted words aren't redacted, but names are
    print(f"Got: {result}")
    assert "Content-Type" in result
    assert "John Doe" not in result
    assert redactor.stats["names"] == 2