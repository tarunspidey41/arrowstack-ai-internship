"""Value normalisers: dates -> ISO 8601, money -> (float, currency)."""
import re
from datetime import date

MONTHS = {m: i + 1 for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august", "september",
     "october", "november", "december"])}
MONTHS.update({k[:3]: v for k, v in list(MONTHS.items())})
MONTHS["sept"] = 9

_ISO = re.compile(r"^\s*(\d{4})-(\d{1,2})-(\d{1,2})\s*$")
_NUM = re.compile(r"^\s*(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})\s*$")
_DMY_TXT = re.compile(r"^\s*(\d{1,2})(?:st|nd|rd|th)?[\s\-]+([A-Za-z]{3,9})\.?,?[\s\-]+(\d{4})\s*$")
_MDY_TXT = re.compile(r"^\s*([A-Za-z]{3,9})\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\s*$")


def _mk(y, m, d):
    try:
        return date(int(y), int(m), int(d)).isoformat()
    except ValueError:
        return None


def parse_date(raw: str):
    """Return (iso_date or None, ambiguous: bool). Numeric dates are read DAY-FIRST (dd/mm/yyyy)."""
    if not raw:
        return None, False
    m = _ISO.match(raw)
    if m:
        return _mk(*m.groups()), False
    m = _NUM.match(raw)
    if m:
        d, mo, y = m.groups()
        iso = _mk(y, mo, d)
        ambiguous = iso is not None and int(d) <= 12 and int(mo) <= 12 and d != mo
        return iso, ambiguous
    m = _DMY_TXT.match(raw)
    if m and m.group(2).lower() in MONTHS:
        return _mk(m.group(3), MONTHS[m.group(2).lower()], m.group(1)), False
    m = _MDY_TXT.match(raw)
    if m and m.group(1).lower() in MONTHS:
        return _mk(m.group(3), MONTHS[m.group(1).lower()], m.group(2)), False
    return None, False


_AMOUNT = re.compile(r"(\d[\d,]*(?:\.\d+)?)")


def parse_money(raw: str):
    """Return (amount float or None, currency or None)."""
    if not raw:
        return None, None
    low = raw.lower()
    currency = None
    if re.search(r"\brs\b\.?|\binr\b|\u20b9", low):
        currency = "INR"
    elif "$" in raw or re.search(r"\busd\b", low):
        currency = "USD"
    elif re.search(r"\beur\b|\u20ac", low):
        currency = "EUR"
    m = _AMOUNT.search(raw)
    if not m:
        return None, currency
    try:
        return float(m.group(1).replace(",", "")), currency
    except ValueError:
        return None, currency


def clean_text_value(raw: str) -> str:
    return re.sub(r"\s+", " ", raw or "").strip(" \t.,;")
