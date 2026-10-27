"""Generate SIMULATED evaluation documents + ground truth, and demo samples (txt + pdf).

Run:  python scripts/generate_data.py
Outputs: data/eval_docs/*.txt + *.json (ground truth) + index.csv, data/samples/*
"""
import csv
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from docassist import synth, config

EVAL = config.DATA_DIR / "eval_docs"
SAMPLES = config.DATA_DIR / "samples"


def write_pdf(path: Path, text: str):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(str(path), pagesize=A4)
    y = 800
    c.setFont("Courier", 9)
    for line in text.split("\n"):
        if y < 50:
            c.showPage(); c.setFont("Courier", 9); y = 800
        c.drawString(40, y, line[:105])
        y -= 13
    c.save()


def build_eval(n_per_type=40, n_other=30, seed=2024):
    EVAL.mkdir(parents=True, exist_ok=True)
    for f in EVAL.glob("*"):
        f.unlink()
    rng = random.Random(seed)
    rows = []
    k = 0
    for dt in ("invoice", "purchase_order", "service_agreement"):
        for i in range(n_per_type):
            style = ["colon", "spaced", "stacked"][i % 3]
            heldout = (i % 2 == 1)
            noise = 0.1 if (i % 4 in (2, 3)) else 0.0
            text, truth, meta = synth.generate(dt, rng, style=style, noise=noise, heldout=heldout)
            k += 1
            name = f"{dt}_{k:03d}"
            (EVAL / f"{name}.txt").write_text(text, encoding="utf-8")
            (EVAL / f"{name}.json").write_text(json.dumps({"doc_type": dt, "fields": truth}, indent=1))
            rows.append({"file": name, "doc_type": dt, "style": style, "heldout_labels": heldout, "label_noise": noise})
    for i in range(n_other):
        text, _, _ = synth.generate("other", rng)
        k += 1
        name = f"other_{k:03d}"
        (EVAL / f"{name}.txt").write_text(text, encoding="utf-8")
        (EVAL / f"{name}.json").write_text(json.dumps({"doc_type": "other", "fields": {}}))
        rows.append({"file": name, "doc_type": "other", "style": "n/a", "heldout_labels": False, "label_noise": 0})
    with open(EVAL / "index.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"wrote {len(rows)} evaluation documents -> {EVAL}")


def build_samples(seed=99):
    SAMPLES.mkdir(parents=True, exist_ok=True)
    for f in SAMPLES.glob("*"):
        f.unlink()
    rng = random.Random(seed)
    plan = [("invoice", "colon", ".txt"), ("invoice", "spaced", ".pdf"), ("purchase_order", "colon", ".txt"),
            ("purchase_order", "stacked", ".pdf"), ("service_agreement", "colon", ".txt"),
            ("service_agreement", "spaced", ".pdf")]
    for n, (dt, style, ext) in enumerate(plan, 1):
        text, _, _ = synth.generate(dt, rng, style=style, noise=0.0)
        path = SAMPLES / f"sample_{n}_{dt}{ext}"
        if ext == ".pdf":
            write_pdf(path, text)
        else:
            path.write_text(text, encoding="utf-8")
    # an unsupported document and a tricky one
    text, _, _ = synth.generate("other", rng)
    (SAMPLES / "sample_7_not_a_business_doc.txt").write_text(text, encoding="utf-8")
    text, _, _ = synth.generate("invoice", rng, style="spaced", heldout=True, noise=0.1)
    (SAMPLES / "sample_8_invoice_unusual_labels.txt").write_text(text, encoding="utf-8")
    print(f"wrote demo samples -> {SAMPLES}")


if __name__ == "__main__":
    build_eval()
    build_samples()
