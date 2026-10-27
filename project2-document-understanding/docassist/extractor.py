"""Field extraction.

AI/NLP approach ("assistant"): build (label, value) candidates from three layouts
(colon, column-spaced, stacked), match labels to the schema lexicon with FUZZY matching
(abbreviation expansion + string similarity), validate the value TYPE, assign greedily by
score, then normalise values. Every field carries a confidence.
"""
import difflib
import re

from . import config, normalize
from .schemas import FIELD_SPECS

ABBREV = {"dt": "date", "amt": "amount", "num": "number", "no": "number", "inv": "invoice",
          "ref": "reference", "nr": "number"}
STOP = {"of", "the", "a", "an"}

_COLON = re.compile(r"^(?P<label>[^:]{2,40}?)\s*:\s*(?P<value>\S.*)$")
_SPACED = re.compile(r"^(?P<label>\S.{0,38}?\S)\s{2,}(?P<value>\S.*)$")


def norm_label(label: str) -> str:
    s = label.lower().replace("#", " number ")
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    toks = [ABBREV.get(t, t) for t in s.split() if t not in STOP]
    return " ".join(toks)


def label_score(label: str, synonym: str) -> float:
    a, b = norm_label(label), norm_label(synonym)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    seq = difflib.SequenceMatcher(None, a, b).ratio()
    sa, sb = set(a.split()), set(b.split())
    jac = len(sa & sb) / len(sa | sb)
    sorted_ratio = difflib.SequenceMatcher(None, " ".join(sorted(sa)), " ".join(sorted(sb))).ratio()
    return max(seq, jac, sorted_ratio)


def candidates(text: str):
    """Yield (label, value, line_no) candidates from all three layouts."""
    lines = [l.rstrip() for l in text.split("\n")]
    out = []
    for i, raw in enumerate(lines):
        s = raw.strip()
        if not s:
            continue
        m = _COLON.match(s)
        if m:
            out.append((m.group("label").strip(), m.group("value").strip(), i))
            continue
        m = _SPACED.match(s)
        if m:
            out.append((m.group("label").strip(), m.group("value").strip(), i))
            continue
        # stacked: short label line, value on the next non-empty line
        if len(s) <= 40 and not any(c.isdigit() for c in s[:3]):
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                out.append((s, lines[j].strip(), i))
    return out


def value_ok(ftype: str, value: str):
    """Return (valid, parsed, ambiguous)."""
    if ftype == "date":
        iso, amb = normalize.parse_date(value)
        return iso is not None, iso, amb
    if ftype == "money":
        amt, cur = normalize.parse_money(value)
        # a money value must contain a currency marker OR a decimal amount, never a bare short integer list
        ok = amt is not None and (cur is not None or "." in value or "," in value)
        return ok, (amt, cur), False
    v = normalize.clean_text_value(value)
    if ftype == "id":
        return bool(re.search(r"\d", v)) and len(v) <= 30 and len(v.split()) <= 2, v, False
    if ftype == "party":
        bad = normalize.parse_date(v)[0] is not None or normalize.parse_money(v)[0] is not None
        return (not bad) and 3 <= len(v) <= 80 and bool(re.search(r"[A-Za-z]{3}", v)), v, False
    return 2 <= len(v) <= 80, v, False  # text


def extract(text: str, doc_type: str) -> dict:
    """Return {field: {"value","raw","confidence","line"}} (+ 'currency' handled by caller)."""
    specs = FIELD_SPECS.get(doc_type, {})
    cands = candidates(text)
    scored = []
    for field, spec in specs.items():
        for ci, (label, value, line) in enumerate(cands):
            score = max(label_score(label, syn) for syn in spec["synonyms"])
            if score < config.LABEL_MATCH_THRESHOLD:
                continue
            ok, parsed, amb = value_ok(spec["type"], value)
            if not ok:
                continue
            scored.append((score, field, ci, parsed, amb, value, line, label))
    scored.sort(key=lambda x: (-x[0], x[6]))
    used_fields, used_cands, result = set(), set(), {}
    for score, field, ci, parsed, amb, raw, line, label in scored:
        if field in used_fields or ci in used_cands:
            continue
        used_fields.add(field)
        used_cands.add(ci)
        conf = round(score * (0.75 if amb else 1.0), 3)
        entry = {"raw": raw, "label_found": label, "confidence": conf, "line": line + 1,
                 "ambiguous_date": amb}
        if specs[field]["type"] == "money":
            entry["value"], entry["currency"] = parsed
        else:
            entry["value"] = parsed
        result[field] = entry
    return result
