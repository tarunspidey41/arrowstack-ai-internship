import pytest
from triage.pipeline import TriageEngine
from triage.preprocess import InvalidTicket


@pytest.fixture(scope="module")
def eng():
    return TriageEngine()


def test_output_schema(eng):
    r = eng.triage("I was charged twice for my Pro subscription this month. No rush at all.")
    for k in ("ticket_id", "issue_type", "urgency", "route_to", "sla_hours", "needs_human_review",
              "review_reasons", "masked_text", "issue_confidence", "urgency_confidence"):
        assert k in r
    assert r["issue_type"] == "billing"


def test_security_always_goes_to_human(eng):
    r = eng.triage("My API key was exposed in a public repository, please help.")
    assert r["issue_type"] == "security"
    assert r["needs_human_review"] is True
    assert r["route_to"] == "Security Operations"


def test_safety_override_raises_urgency(eng):
    r = eng.triage("Just a minor thing, no rush: customer data was leaked to another tenant.")
    assert r["urgency"] in ("high", "critical")


def test_pii_not_in_masked_text(eng):
    r = eng.triage("Please refund me, my email is rahul@test.com and phone 9876543210.")
    assert "rahul@test.com" not in r["masked_text"] and "9876543210" not in r["masked_text"]


def test_invalid_input_raises_and_safe_variant_returns_error(eng):
    with pytest.raises(InvalidTicket):
        eng.triage("")
    assert eng.triage_safe("hi")["error"] == "too_short"


def test_gibberish_goes_to_human_review(eng):
    r = eng.triage("zzqx wvvt plmk qqqq rrrr ssss")
    assert r["needs_human_review"] is True


def test_deterministic(eng):
    t = "The dashboard has been loading very slowly since this morning."
    a, b = eng.triage(t), eng.triage(t)
    assert (a["issue_type"], a["urgency"]) == (b["issue_type"], b["urgency"])
