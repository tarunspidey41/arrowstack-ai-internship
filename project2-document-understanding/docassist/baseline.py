"""Baseline: strict regexes on the CANONICAL label only, ISO or dd/mm/yyyy dates, simple money."""
import re

from . import classifier, normalize
from .schemas import FIELD_SPECS

CANONICAL = {
    "invoice": {"invoice_number": "Invoice No", "invoice_date": "Invoice Date", "due_date": "Due Date",
                "vendor_name": "Vendor", "customer_name": "Bill To", "tax_amount": "Tax", "total_amount": "Total"},
    "purchase_order": {"po_number": "PO Number", "order_date": "Order Date", "delivery_date": "Delivery Date",
                       "buyer_name": "Buyer", "supplier_name": "Supplier", "total_amount": "Total"},
    "service_agreement": {"contract_number": "Agreement No", "effective_date": "Effective Date",
                          "end_date": "End Date", "provider_name": "Service Provider",
                          "client_name": "Client", "contract_value": "Contract Value",
                          "governing_law": "Governing Law"},
}
_DATE = re.compile(r"^(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})$")
_MONEY = re.compile(r"^(?:Rs\.?|INR|\$|USD|EUR)?\s*([\d,]+\.\d{2})\s*(?:INR|USD|EUR)?$")


def extract(text: str, doc_type: str) -> dict:
    out = {}
    for field, label in CANONICAL.get(doc_type, {}).items():
        m = re.search(rf"^{re.escape(label)}\s*:\s*(.+)$", text, re.M)
        if not m:
            continue
        raw = m.group(1).strip()
        ftype = FIELD_SPECS[doc_type][field]["type"]
        if ftype == "date":
            if _DATE.match(raw):
                out[field] = normalize.parse_date(raw)[0]
        elif ftype == "money":
            mm = _MONEY.match(raw)
            if mm:
                amt, cur = normalize.parse_money(raw)
                out[field] = amt
                out["currency"] = cur
        else:
            out[field] = raw
    return out


def analyze(text: str) -> dict:
    dt = classifier.baseline_predict(text)
    return {"doc_type": dt, "fields": extract(text, dt)}


def extract_rules(text: str, doc_type: str) -> dict:
    """Stronger rule baseline: EVERY known label spelling (exact, case-insensitive), 'Label: value' layout only,
    ISO or dd/mm/yyyy dates, simple money. No fuzzy matching, no spaced/stacked layouts, no date-format handling."""
    out = {}
    for field, spec in FIELD_SPECS.get(doc_type, {}).items():
        for syn in spec["synonyms"]:
            m = re.search(rf"^{re.escape(syn)}\s*:\s*(.+)$", text, re.M | re.I)
            if not m:
                continue
            raw = m.group(1).strip()
            if spec["type"] == "date":
                if _DATE.match(raw):
                    out[field] = normalize.parse_date(raw)[0]
                    break
            elif spec["type"] == "money":
                if _MONEY.match(raw):
                    amt, cur = normalize.parse_money(raw)
                    out[field] = amt
                    out["currency"] = cur
                    break
            else:
                out[field] = raw
                break
    return out
