import pytest
from redactor import Redactor

def test_redact_concepts():
    redactor = Redactor()
    input_text = "Artificial Intelligence is transforming industries."
    concepts = ["intelligence"]
    expected_output = "███████████████████████████████████████████████████"
    redacted_text = redactor.redact_concept(input_text, concepts)
    print(f"Expected: {expected_output}")
    print(f"Actual: {redacted_text}")
    assert redacted_text == expected_output
