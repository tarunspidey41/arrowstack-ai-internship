"""Evaluate baseline vs AI (and AI + guardrails). Writes reports/.

Run:  python scripts/evaluate.py
"""
import json
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from triage import config, baseline, model as ml
from triage.pipeline import TriageEngine
from triage.preprocess import validate, InvalidTicket

ORDER = {u: i for i, u in enumerate(config.URGENCY_LEVELS)}


def metrics(y_true, y_pred):
    return {"accuracy": round(accuracy_score(y_true, y_pred), 4),
            "macro_f1": round(f1_score(y_true, y_pred, average="macro", zero_division=0), 4)}


def run(df, engine):
    rows = []
    for _, r in df.iterrows():
        b = baseline.predict(r["text"])
        a = engine.triage(r["text"])
        rows.append({
            "text": r["text"], "true_issue": r["issue_type"], "true_urgency": r["urgency"],
            "base_issue": b["issue_type"], "base_urgency": b["urgency"],
            "ai_issue": a["issue_type"], "ai_urgency": a["urgency"],
            "ai_issue_conf": a["issue_confidence"], "ai_urg_conf": a["urgency_confidence"],
            "needs_review": a["needs_human_review"], "route_ai": a["route_to"],
            "route_true": baseline.route(r["issue_type"], r["urgency"]),
            "route_base": b["route_to"],
        })
    return pd.DataFrame(rows)


def summarise(res):
    s = {}
    for name, ik, uk, rk in (("baseline", "base_issue", "base_urgency", "route_base"),
                             ("ai", "ai_issue", "ai_urgency", "route_ai")):
        s[name] = {
            "issue_type": metrics(res.true_issue, res[ik]),
            "urgency": metrics(res.true_urgency, res[uk]),
            "routing_accuracy": round(accuracy_score(res.route_true, res[rk]), 4),
        }
    # dangerous error: urgency under-estimated by 2+ levels or critical/high predicted as low
    for name, uk in (("baseline", "base_urgency"), ("ai", "ai_urgency")):
        under = sum(ORDER[t] - ORDER[p] >= 2 for t, p in zip(res.true_urgency, res[uk]))
        s[name]["severe_under_prioritised"] = int(under)
    auto = res[~res.needs_review]
    s["guardrails"] = {
        "tickets": len(res),
        "sent_to_human_review": int(res.needs_review.sum()),
        "auto_routed": len(auto),
        "auto_routed_routing_accuracy": round(accuracy_score(auto.route_true, auto.route_ai), 4) if len(auto) else None,
        "review_rate": round(res.needs_review.mean(), 4),
    }
    return s


def md_table(d):
    lines = ["| Metric | Baseline (rules) | AI (TF-IDF + LR) |", "|---|---|---|"]
    for k, label in (("issue_type", "Issue type"), ("urgency", "Urgency")):
        lines.append(f"| {label} accuracy | {d['baseline'][k]['accuracy']:.3f} | {d['ai'][k]['accuracy']:.3f} |")
        lines.append(f"| {label} macro-F1 | {d['baseline'][k]['macro_f1']:.3f} | {d['ai'][k]['macro_f1']:.3f} |")
    lines.append(f"| Routing accuracy | {d['baseline']['routing_accuracy']:.3f} | {d['ai']['routing_accuracy']:.3f} |")
    lines.append(f"| Severe urgency under-prioritisation (count) | {d['baseline']['severe_under_prioritised']} | {d['ai']['severe_under_prioritised']} |")
    return "\n".join(lines)


def main():
    REP = config.REPORT_DIR
    REP.mkdir(exist_ok=True)
    engine = TriageEngine(ml.train())  # retrain so report always matches data
    out = {}
    md = ["# Evaluation Report - Intelligent Support Triage", "",
          "All data is **simulated** (see `scripts/generate_data.py`). The eval set contains tickets with "
          "phrasing never seen in training (held-out templates) plus typos.", ""]
    for name, fname in (("eval", "eval.csv"), ("hard_cases", "hard_cases.csv")):
        df = pd.read_csv(config.DATA_DIR / fname)
        valid_mask = []
        for t in df["text"]:
            try:
                validate(t)
                valid_mask.append(True)
            except InvalidTicket:
                valid_mask.append(False)
        rejected = int(len(df) - sum(valid_mask))
        df = df[valid_mask].reset_index(drop=True)
        res = run(df, engine)
        res.to_csv(REP / f"predictions_{name}.csv", index=False)
        s = summarise(res)
        out[name] = s
        md += [f"## {name} set ({len(df)} tickets scored, {rejected} rejected by input validation)", "", md_table(s), "",
               "**Guardrails (AI + human review):**",
               f"- Sent to human review: {s['guardrails']['sent_to_human_review']} / {s['guardrails']['tickets']} "
               f"({s['guardrails']['review_rate']:.1%})",
               f"- Auto-routed tickets: {s['guardrails']['auto_routed']}, routing accuracy on those: "
               f"{s['guardrails']['auto_routed_routing_accuracy']}", ""]
        if name == "eval":
            for target, pred in (("issue_type", "ai_issue"), ("urgency", "ai_urgency")):
                labels = sorted(res[f"true_{'issue' if target == 'issue_type' else 'urgency'}"].unique())
                tcol = "true_issue" if target == "issue_type" else "true_urgency"
                md += [f"### Per-class report - {target} (AI)", "```",
                       classification_report(res[tcol], res[pred], zero_division=0), "```", "",
                       f"### Confusion matrix - {target} (rows = true, cols = predicted)", "```",
                       pd.DataFrame(confusion_matrix(res[tcol], res[pred], labels=labels),
                                    index=labels, columns=labels).to_string(), "```", ""]
        errs = res[(res.true_issue != res.ai_issue) | (res.true_urgency != res.ai_urgency)]
        errs.to_csv(REP / f"errors_{name}.csv", index=False)
        md += [f"Misclassified by AI: **{len(errs)}** tickets (saved to `reports/errors_{name}.csv`).", ""]
    (REP / "metrics.json").write_text(json.dumps(out, indent=2))
    (REP / "evaluation_report.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
