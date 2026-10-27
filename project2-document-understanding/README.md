# Project 2 - Document Understanding Assistant (Arrowstack AI Internship)

A pipeline that reads business documents (invoice, purchase order, service agreement), extracts and validates
key fields, produces a summary, and flags uncertain documents for human review. Simulated documents only.

## Quick start (Windows)
1. Install Python 3.10+ (tick "Add Python to PATH").
2. Double-click **`start.bat`** - creates a virtual environment, installs packages, trains the classifier on first run,
   starts the server and opens http://127.0.0.1:5002
3. Double-click **`stop.bat`** to shut it down.

## Manual commands (any OS)
```bash
python -m venv .venv && .venv/Scripts/activate      # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_data.py   # simulated eval docs + demo samples -> data/
python scripts/train.py           # document-type model -> models/
python scripts/evaluate.py        # baselines vs assistant -> reports/
python -m pytest                  # 42 tests
python app.py                     # http://127.0.0.1:5002
```

## How it works
```
file/text -> parse (txt, pdf, optional OCR) -> classify type (TF-IDF + LR) -> extract fields
  (colon / spaced / stacked layouts, fuzzy label match, value-type check) -> normalise (ISO dates, amount + currency)
  -> JSON-Schema + business-rule validation -> entities + summary -> auto-accept OR human review (with reasons)
```

## Results (150 simulated documents)
| Metric | Naive baseline | Rule baseline | Assistant |
|---|---|---|---|
| Document-type accuracy | 0.733 | - | 1.000 |
| Field accuracy | 0.029 | 0.205 | 0.859 |

Important context: baselines handle only the `Label: value` layout. On documents with known labels the assistant
scores 1.00; on **unseen label wording it scores about 0.70-0.74**. All 130 errors were "not found" (0 wrong values),
and 98.2% of auto-accepted documents were fully correct. See `reports/evaluation_report.md` and `docs/error_analysis.md`.

## API
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/analyze` | multipart `file` or JSON `{"text": "..."}` |
| GET / POST | `/api/samples`, `/api/samples/<name>` | list / analyse bundled samples |
| GET | `/api/results`, `/api/results/<id>` | history / one result |
| POST | `/api/review/<id>` | `{"corrections": {"field": "value"}}` |
| GET | `/api/export/<id>` | download validated JSON |

## Folder structure
```
app.py, start.bat, stop.bat, requirements.txt
docassist/   config, parsers, classifier, extractor, normalize, schemas, summarizer, entities, baseline, pipeline, synth
scripts/     generate_data.py, train.py, evaluate.py
data/        samples/ (demo txt + pdf), eval_docs/ (150 docs + ground truth)
reports/     evaluation_report.md, metrics.json, errors.csv
docs/        requirements, decision_log, error_analysis, responsible_use, work_log, presentation_and_viva
tests/       pytest suite
```

## Limitations
Simulated, English-only documents; lexicon-based extraction (new label wording is missed and flagged); no
line-item tables; OCR optional (install Tesseract + `pip install pytesseract pillow`); demo server has no authentication.
