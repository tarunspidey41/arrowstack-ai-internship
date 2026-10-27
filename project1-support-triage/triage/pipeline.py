"""End-to-end triage workflow:

validate -> mask PII -> ML predict -> safety override -> routing -> guardrails (human review)
"""
import uuid
from datetime import datetime, timezone

from . import config, baseline, model as ml
from .preprocess import validate, mask_pii, InvalidTicket


class TriageEngine:
    def __init__(self, models=None):
        self.models = models or ml.load()

    def triage(self, text, ticket_id=None) -> dict:
        """Triage a single ticket. Raises InvalidTicket on bad input."""
        cleaned = validate(text)
        masked = mask_pii(cleaned)
        pred = ml.predict_with_confidence(self.models, cleaned)
        issue, issue_conf = pred["issue_type"]
        urgency, urg_conf = pred["urgency"]

        reasons, notes = [], []

        # Guardrail 1: safety override - never under-prioritise breach/outage language
        low = cleaned.lower()
        hit = [k for k in config.SAFETY_KEYWORDS if k in low]
        if hit and urgency in ("low", "medium"):
            notes.append(f"Urgency raised to 'high' by safety keyword(s): {', '.join(hit[:3])}")
            urgency = "high"
        if hit and issue not in ("security", "technical"):
            reasons.append("safety keywords present but issue type is not security/technical")

        # Guardrail 2: low confidence -> human review
        if issue_conf < config.CONFIDENCE_THRESHOLD:
            reasons.append(f"low issue-type confidence ({issue_conf:.2f})")
        if urg_conf < config.CONFIDENCE_THRESHOLD:
            reasons.append(f"low urgency confidence ({urg_conf:.2f})")

        # Guardrail 3: policy - security & critical tickets always need a human
        if issue == "security":
            reasons.append("policy: security tickets require human confirmation")
        if urgency == "critical":
            reasons.append("policy: critical tickets require human confirmation")

        route_to = baseline.route(issue, urgency)
        return {
            "ticket_id": ticket_id or uuid.uuid4().hex[:8],
            "issue_type": issue,
            "issue_confidence": round(issue_conf, 3),
            "urgency": urgency,
            "urgency_confidence": round(urg_conf, 3),
            "route_to": route_to,
            "sla_hours": config.SLA_HOURS[urgency],
            "needs_human_review": bool(reasons),
            "review_reasons": reasons,
            "notes": notes,
            "masked_text": masked,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }

    def triage_safe(self, text) -> dict:
        """Like triage() but returns an error dict instead of raising."""
        try:
            return self.triage(text)
        except InvalidTicket as e:
            return {"error": e.code, "message": e.message}
