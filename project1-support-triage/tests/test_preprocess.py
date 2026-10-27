import pytest
from triage.preprocess import validate, mask_pii, InvalidTicket


@pytest.mark.parametrize("bad,code", [
    (None, "not_text"), (123, "not_text"), ("", "empty"), ("    ", "empty"),
    ("hi", "too_short"), ("a" * 6000, "too_long"), ("!!!! 1234 ???? 5678 ####", "not_natural_text"),
])
def test_invalid_inputs_rejected(bad, code):
    with pytest.raises(InvalidTicket) as e:
        validate(bad)
    assert e.value.code == code


def test_whitespace_normalised():
    assert validate("  my   app\n crashes  today ") == "my app crashes today"


def test_pii_masked():
    t = mask_pii("Mail me at jane.doe@example.com or call +91 98765 43210, card 4111 1111 1111 1111")
    assert "example.com" not in t and "98765" not in t and "4111" not in t
    assert "[EMAIL]" in t and "[PHONE]" in t and "[CARD]" in t
