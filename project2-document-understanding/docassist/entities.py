"""Generic entity finder (regex based): organisations, e-mails, phones, amounts, dates."""
import re

from . import normalize

_ORG = re.compile(r"\b((?:[A-Z][A-Za-z&]+\s){1,4}(?:Pvt Ltd|Ltd|LLP|LLC|Inc|Corp|Trust))\b")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE = re.compile(r"(?<!\w)(?:\+?\d{1,3}[\s-]?)?\d{10}(?!\w)")
_MONEY = re.compile(r"(?:Rs\.?|INR|\$|USD|EUR)\s?\d[\d,]*(?:\.\d+)?|\d[\d,]*\.\d{2}\s?(?:INR|USD|EUR)")
_DATES = [re.compile(r"\b\d{4}-\d{2}-\d{2}\b"), re.compile(r"\b\d{1,2}/\d{1,2}/\d{4}\b"),
          re.compile(r"\b\d{1,2}[ -](?:[A-Z][a-z]{2,8})[ -,]+\d{4}\b"),
          re.compile(r"\b[A-Z][a-z]{2,8} \d{1,2}, \d{4}\b")]


def find_entities(text: str) -> dict:
    dates = []
    for rx in _DATES:
        dates += [m.group(0) for m in rx.finditer(text)]
    return {
        "organisations": sorted(set(m.group(1) for m in _ORG.finditer(text))),
        "emails": sorted(set(_EMAIL.findall(text))),
        "phones": sorted(set(_PHONE.findall(text))),
        "amounts": sorted(set(m.group(0).strip() for m in _MONEY.finditer(text))),
        "dates": sorted(set(dates)),
    }
