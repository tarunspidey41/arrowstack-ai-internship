"""Central configuration for the Document Understanding Assistant."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
MODEL_DIR = ROOT / "models"
REPORT_DIR = ROOT / "reports"
RUNTIME_DIR = DATA_DIR / "runtime"
MODEL_PATH = MODEL_DIR / "doctype_model.joblib"

DOC_TYPES = ["invoice", "purchase_order", "service_agreement", "other"]

DOC_TYPE_CONFIDENCE_THRESHOLD = 0.60   # below -> treated as unknown, human review
FIELD_CONFIDENCE_THRESHOLD = 0.85      # any extracted field below -> human review
LABEL_MATCH_THRESHOLD = 0.82           # minimum fuzzy label similarity

MAX_FILE_MB = 5
MIN_TEXT_CHARS = 30                    # below -> probably scanned / empty document
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".png", ".jpg", ".jpeg"}

PORT = 5002
