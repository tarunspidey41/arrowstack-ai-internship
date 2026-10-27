"""Central configuration: labels, routing table, SLAs and thresholds."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
MODEL_DIR = ROOT / "models"
REPORT_DIR = ROOT / "reports"
RUNTIME_DIR = DATA_DIR / "runtime"
MODEL_PATH = MODEL_DIR / "triage_model.joblib"

ISSUE_TYPES = [
    "billing",
    "technical",
    "account_access",
    "security",
    "feature_request",
    "general_inquiry",
]
URGENCY_LEVELS = ["low", "medium", "high", "critical"]

# Routing recommendation = f(issue_type, urgency)
ROUTING_TABLE = {
    "billing": "Billing & Payments",
    "technical": "Technical Support (L2)",
    "account_access": "Identity & Access Support",
    "security": "Security Operations",
    "feature_request": "Product Management",
    "general_inquiry": "Customer Support (L1)",
}
CRITICAL_TECHNICAL_ROUTE = "Engineering On-Call"

# Target first-response time (hours) per urgency
SLA_HOURS = {"critical": 1, "high": 4, "medium": 24, "low": 72}

# Guardrail thresholds
CONFIDENCE_THRESHOLD = 0.55      # below this -> human review
MIN_CHARS = 10
MIN_WORDS = 3
MAX_CHARS = 5000
MAX_BATCH = 100

# Keywords that must never be under-prioritised (safety override)
SAFETY_KEYWORDS = [
    "data breach", "breach", "hacked", "leaked", "leak", "exposed",
    "unauthorised", "unauthorized", "production down", "system is down",
    "ransom", "stolen", "compromised",
]

PORT = 5001
