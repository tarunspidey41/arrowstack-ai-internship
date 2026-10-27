"""Summaries: a structured headline from extracted fields + extractive key sentences (TF-IDF centrality)."""
import re

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

_PAIR = re.compile(r"^[^:]{2,40}:\s*\S|\S.{0,38}\S\s{2,}\S")


def money_str(amount, currency):
    if amount is None:
        return None
    return f"{currency + ' ' if currency else ''}{amount:,.2f}"


def headline(doc_type: str, r: dict) -> str:
    g = lambda k: r.get(k)
    total = money_str(g("total_amount"), g("currency"))
    if doc_type == "invoice":
        parts = [f"Invoice {g('invoice_number') or '(number not found)'}"]
        if g("vendor_name"): parts.append(f"from {g('vendor_name')}")
        if g("customer_name"): parts.append(f"to {g('customer_name')}")
        if total: parts.append(f"for {total}")
        if g("due_date"): parts.append(f"due {g('due_date')}")
        return " ".join(parts) + "."
    if doc_type == "purchase_order":
        parts = [f"Purchase order {g('po_number') or '(number not found)'}"]
        if g("buyer_name"): parts.append(f"from {g('buyer_name')}")
        if g("supplier_name"): parts.append(f"to {g('supplier_name')}")
        if total: parts.append(f"worth {total}")
        if g("delivery_date"): parts.append(f"for delivery by {g('delivery_date')}")
        return " ".join(parts) + "."
    if doc_type == "service_agreement":
        parts = [f"Service agreement {g('contract_number') or '(number not found)'}"]
        if g("provider_name"): parts.append(f"between {g('provider_name')}")
        if g("client_name"): parts.append(f"and {g('client_name')}")
        val = money_str(g("contract_value"), g("currency"))
        if val: parts.append(f"valued at {val}")
        if g("effective_date") and g("end_date"): parts.append(f"running {g('effective_date')} to {g('end_date')}")
        return " ".join(parts) + "."
    return "Document type not recognised as a supported business document."


def prose_sentences(text: str):
    sents = []
    for line in text.split("\n"):
        s = line.strip()
        if not s or _PAIR.match(s) or len(s.split()) < 6:
            continue
        s = re.sub(r"^\d+\.\s*", "", s)
        sents += [x.strip() for x in re.split(r"(?<=[.!?])\s+", s) if len(x.split()) >= 6]
    return sents


def key_points(text: str, n: int = 2):
    sents = prose_sentences(text)
    if len(sents) <= n:
        return sents
    try:
        m = TfidfVectorizer(stop_words="english").fit_transform(sents)
        sim = (m @ m.T).toarray()
        score = sim.sum(axis=1) - 1.0
    except ValueError:
        return sents[:n]
    idx = np.argsort(-score)[:n]
    return [sents[i] for i in sorted(idx)]


def summarize(text: str, doc_type: str, record: dict) -> dict:
    return {"headline": headline(doc_type, record), "key_points": key_points(text)}
