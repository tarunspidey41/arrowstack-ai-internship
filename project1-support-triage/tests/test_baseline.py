from triage import baseline


def test_baseline_issue_rules():
    assert baseline.predict_issue("I was charged twice for the invoice") == "billing"
    assert baseline.predict_issue("Someone hacked my account") == "security"
    assert baseline.predict_issue("hello there friend") == "general_inquiry"


def test_baseline_urgency_rules():
    assert baseline.predict_urgency("This is an emergency") == "critical"
    assert baseline.predict_urgency("no rush at all") == "low"
    assert baseline.predict_urgency("something happened") == "medium"


def test_routing_critical_technical_goes_to_oncall():
    assert baseline.route("technical", "critical") == "Engineering On-Call"
    assert baseline.route("technical", "low") == "Technical Support (L2)"
