# Project 1 - Intelligent Support Triage (Arrowstack AI Internship)

An AI-assisted ticket triage workflow. It classifies **issue type** and **urgency**, recommends a **routing team**,
masks personal data, and sends uncertain or sensitive tickets to a **human review queue**. Uses simulated data only.

## Quick start (Windows)
1. Install Python 3.10+ (tick "Add Python to PATH").
2. Double-click **`start.bat`** - it creates a virtual environment, installs packages, trains the model on first run,
   starts the server and opens http://127.0.0.1:5001
3. Double-click **`stop.bat`** to shut the server down.

## Manual commands (any OS)
```bash
python -m venv .venv && .venv/Scripts/activate      # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_data.py   # simulated data -> data/
python scripts/train.py           # model -> models/
python scripts/evaluate.py        # baseline vs AI -> reports/
python -m pytest                  # 30 tests
python app.py                     # http://127.0.0.1:5001
```

## How it works
```
ticket text -> validate -> mask PII -> TF-IDF + Logistic Regression (issue type, urgency)
            -> safety-keyword override -> routing table + SLA -> guardrails -> auto-route OR human review
```

## Results (simulated held-out eval set, 300 tickets)
| Metric | Keyword baseline | AI model |
|---|---|---|
| Issue-type accuracy | 0.553 | 0.743 |
| Urgency accuracy | 0.717 | 0.953 |
| Routing accuracy | 0.553 | 0.743 |
| Severe under-prioritisation | 7 | 0 |

With guardrails, 50.3% of tickets go to a human and the 149 auto-routed tickets are 98.7% correct.
Full details and honest limitations: `reports/evaluation_report.md`, `docs/error_analysis.md`.

## API
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/triage` | `{"text": "..."}` -> triage result |
| POST | `/api/triage/batch` | `{"texts": [...]}` (max 100) |
| GET | `/api/queue` | tickets waiting for human review |
| POST | `/api/review/<id>` | `{"issue_type": "...", "urgency": "..."}` approve/correct |
| GET | `/api/stats`, `/api/health` | statistics / health check |

## Folder structure
```
app.py, start.bat, stop.bat, requirements.txt
triage/      config, preprocess (validation + PII), baseline, model, pipeline
scripts/     generate_data.py, train.py, evaluate.py
data/        train.csv, eval.csv, hard_cases.csv (simulated)
reports/     evaluation_report.md, metrics.json, predictions/errors CSVs
docs/        requirements, decision_log, error_analysis, responsible_use, work_log, presentation_and_viva
tests/       pytest suite
```

## Limitations
Simulated, templated data; English only; no authentication on the demo server; reviewer corrections are stored
but not yet used for retraining. See `docs/error_analysis.md`.
