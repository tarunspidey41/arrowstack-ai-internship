"""Rule-based baseline: keyword matching. Used as the comparison for the ML model."""
import re
from . import config

ISSUE_KEYWORDS = {
    "security": ["phishing", "suspicious", "vulnerab", "breach", "hacked", "unauthori", "leak",
                 "exposed", "stolen", "compromis", "malware"],
    "billing": ["invoice", "charged", "refund", "payment", "billing", "bill ", "subscription",
                "discount", "credit card", "price", "renewal"],
    "account_access": ["password", "login", "log in", "locked", "credentials", "two-factor",
                       "2fa", "sign in", "access"],
    "technical": ["crash", "error", "bug", "slow", "not working", "fails", "timeout",
                  "sync", "loading", "broken"],
    "feature_request": ["feature", "would be great", "please add", "suggest", "wish",
                        "support for", "can you add", "consider adding"],
    "general_inquiry": ["how do i", "what are", "do you have", "where can i", "which", "demo", "hours"],
}
# Order matters: first match wins (security first for safety)
ISSUE_ORDER = ["security", "billing", "account_access", "technical", "feature_request", "general_inquiry"]

URGENCY_KEYWORDS = {
    "critical": ["emergency", "production", "all our users", "everyone", "right now", "losing revenue", "breach"],
    "high": ["urgent", "asap", "deadline", "blocking", "cannot work", "can't work", "immediately", "today"],
    "low": ["no rush", "whenever", "minor", "not urgent", "at your convenience"],
}


def predict_issue(text: str) -> str:
    t = text.lower()
    for label in ISSUE_ORDER:
        if any(k in t for k in ISSUE_KEYWORDS[label]):
            return label
    return "general_inquiry"


def predict_urgency(text: str) -> str:
    t = text.lower()
    for label in ("critical", "high", "low"):
        if any(re.search(re.escape(k), t) for k in URGENCY_KEYWORDS[label]):
            return label
    return "medium"


def route(issue: str, urgency: str) -> str:
    if issue == "technical" and urgency == "critical":
        return config.CRITICAL_TECHNICAL_ROUTE
    return config.ROUTING_TABLE[issue]


def predict(text: str) -> dict:
    issue, urgency = predict_issue(text), predict_urgency(text)
    return {"issue_type": issue, "urgency": urgency, "route_to": route(issue, urgency)}
