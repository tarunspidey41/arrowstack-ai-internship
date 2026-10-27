"""Evaluate baseline (strict regex) vs assistant (classifier + fuzzy extraction + guardrails).

Run:  python scripts/evaluate.py     (needs data/eval_docs; run scripts/generate_data.py first)
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from docassist import baseline, classifier, config
from docassist.pipeline import DocumentAnalyzer

EVAL = config.DATA_DIR / "eval_docs"


def same(a, b):
    if a is None or b is None:
        return False
    if isinstance(b, float) or isinstance(a, float):
        try:
            return abs(float(a) - float(b)) < 0.01
        except (TypeError, ValueError):
            return False
    return str(a).strip().casefold() == str(b).strip().casefold()


def pct(n, d):
    return round(n / d, 4) if d else None


def main():
    config.REPORT_DIR.mkdir(exist_ok=True)
    analyzer = DocumentAnalyzer(classifier.train())
    index = list(csv.DictReader(open(EVAL / "index.csv")))

    SYS = ("naive", "rules", "assistant")
    cls = {"naive": 0, "assistant": 0}
    tot = {k: [0, 0] for k in SYS}                                 # fields correct / total
    cond = defaultdict(lambda: {k: [0, 0] for k in SYS})
    review = {"docs": 0, "reviewed": 0, "auto": 0, "auto_all_correct": 0,
              "wrong_and_unflagged_docs": 0, "all_correct_docs": 0}
    summ = [0, 0]
    per_field = defaultdict(lambda: {k: [0, 0] for k in SYS})
    errors = []

    for row in index:
        text = (EVAL / f"{row['file']}.txt").read_text(encoding="utf-8")
        gt = json.loads((EVAL / f"{row['file']}.json").read_text())
        truth, true_type = gt["fields"], gt["doc_type"]
        b = baseline.analyze(text)
        a = analyzer.analyze_text(text, filename=row["file"])
        cls["naive"] += b["doc_type"] == true_type
        cls["assistant"] += a["doc_type"] == true_type
        review["docs"] += 1
        review["reviewed"] += a["needs_human_review"]
        if true_type == "other":
            if not a["needs_human_review"]:
                errors.append({"file": row["file"], "issue": "non-business document not flagged"})
            continue
        key = f"style={row['style']} | heldout_labels={row['heldout_labels']} | noise={row['label_noise']}"
        all_ok = True
        for field, tv in truth.items():
            nv = b["fields"].get(field) if b["doc_type"] == true_type else None
            rv = baseline.extract_rules(text, true_type).get(field)   # generous: told the true doc type
            av = a["record"].get(field) if a["doc_type"] == true_type else None
            for name, got in (("naive", nv), ("rules", rv), ("assistant", av)):
                ok = same(got, tv)
                tot[name][0] += ok; tot[name][1] += 1
                cond[key][name][0] += ok; cond[key][name][1] += 1
                per_field[f"{true_type}.{field}"][name][0] += ok
                per_field[f"{true_type}.{field}"][name][1] += 1
                if name == "assistant" and not ok:
                    all_ok = False
                    errors.append({"file": row["file"], "field": field, "expected": tv, "got": got,
                                   "flagged_for_review": a["needs_human_review"]})
        if all_ok:
            review["all_correct_docs"] += 1
        if not a["needs_human_review"]:
            review["auto"] += 1
            review["auto_all_correct"] += all_ok
        if (not all_ok) and (not a["needs_human_review"]):
            review["wrong_and_unflagged_docs"] += 1
        # summary key-fact coverage: headline mentions the true counterparty and the total
        h = a["summary"]["headline"]
        party = truth.get("vendor_name") or truth.get("supplier_name") or truth.get("provider_name")
        amt = truth.get("total_amount") or truth.get("contract_value")
        summ[1] += 1
        summ[0] += (party in h) and (f"{amt:,.2f}" in h)

    n_biz = sum(1 for r in index if r["doc_type"] != "other")
    m = {
        "documents": len(index),
        "doc_type_accuracy": {"keyword_baseline": pct(cls["naive"], len(index)), "assistant": pct(cls["assistant"], len(index))},
        "field_accuracy_end_to_end": {k: pct(*v) for k, v in tot.items()},
        "field_counts": tot,
        "by_condition": {k: {n: pct(*v) for n, v in d.items()} for k, d in sorted(cond.items())},
        "by_field": {k: {n: pct(*v) for n, v in d.items()} for k, d in sorted(per_field.items())},
        "human_review": {
            "documents_sent_to_review": review["reviewed"],
            "review_rate": pct(review["reviewed"], review["docs"]),
            "auto_accepted_business_docs": review["auto"],
            "auto_accepted_fully_correct": pct(review["auto_all_correct"], review["auto"]),
            "wrong_but_unflagged_docs": review["wrong_and_unflagged_docs"],
            "fully_correct_docs_overall": pct(review["all_correct_docs"], n_biz),
        },
        "summary_key_fact_coverage": pct(*summ),
    }
    (config.REPORT_DIR / "metrics.json").write_text(json.dumps(m, indent=2))
    with open(config.REPORT_DIR / "errors.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["file", "field", "expected", "got", "flagged_for_review", "issue"])
        w.writeheader(); w.writerows(errors)

    md = ["# Evaluation Report - Document Understanding Assistant", "",
          f"All {len(index)} documents are **simulated** (`scripts/generate_data.py`). Eval layouts include "
          "stacked layouts, five date formats, three currencies, OCR-like label noise, and "
          "**label wording not present in the extractor lexicon** (held-out labels).", "",
          "## Overall", "", "| Metric | Naive baseline (canonical label only) | Rule baseline (all label spellings, exact) | Assistant |", "|---|---|---|---|",
          f"| Document-type accuracy (4 classes) | {m['doc_type_accuracy']['keyword_baseline']:.3f} (keywords) | n/a | {m['doc_type_accuracy']['assistant']:.3f} |",
          f"| Field accuracy | {m['field_accuracy_end_to_end']['naive']:.3f} | {m['field_accuracy_end_to_end']['rules']:.3f} (given true doc type) | {m['field_accuracy_end_to_end']['assistant']:.3f} (end-to-end) |",
          "", f"Fields scored: {tot['assistant'][1]} across {n_biz} business documents.", "",
          "## Accuracy by condition", "", "| Condition | Naive | Rules | Assistant |", "|---|---|---|---|"]
    for k, d in m["by_condition"].items():
        md.append(f"| {k.replace(' | ', ', ')} | {d['naive']:.3f} | {d['rules']:.3f} | {d['assistant']:.3f} |")
    md += ["", "## Accuracy by field", "", "| Field | Naive | Rules | Assistant |", "|---|---|---|---|"]
    for k, d in m["by_field"].items():
        md.append(f"| {k.replace(' | ', ', ')} | {d['naive']:.3f} | {d['rules']:.3f} | {d['assistant']:.3f} |")
    hr = m["human_review"]
    md += ["", "## Human-review guardrail", "",
           f"- Documents sent to human review: **{hr['documents_sent_to_review']} / {len(index)}** ({hr['review_rate']:.1%})",
           f"- Auto-accepted business documents: {hr['auto_accepted_business_docs']}, of which fully correct: "
           f"**{hr['auto_accepted_fully_correct']}**",
           f"- Documents with at least one wrong field that were NOT flagged: **{hr['wrong_but_unflagged_docs']}**",
           f"- Business documents with every field correct: {hr['fully_correct_docs_overall']:.1%}", "",
           "## Summary quality", "",
           f"Headline contains the correct counterparty AND amount in **{m['summary_key_fact_coverage']:.1%}** of business documents "
           "(a fact-coverage check, not a fluency score).", "",
           f"Errors listed in `reports/errors.csv` ({len(errors)} rows)."]
    (config.REPORT_DIR / "evaluation_report.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
