# Requirements & Acceptance Criteria - Document Understanding Assistant

## 1. Problem framing
Back-office teams receive invoices, purchase orders and contracts in many layouts. Staff retype key fields into
systems and skim long documents. The assistant turns a document into a validated JSON record plus a short summary.

| Item | Definition |
|---|---|
| Primary stakeholder | Accounts-payable / procurement team lead |
| Other users | Clerks who review flagged documents, auditors who need traceable fields |
| Input | `.txt`, text-based `.pdf` (images only when Tesseract OCR is installed), or pasted text; max 5 MB |
| Output | document type + confidence, fields with confidence and source line, entities, summary, schema validation, review flag + reasons |
| Decision enabled | Which documents can be posted automatically and which need a human |
| Measurable benefit | Fewer fields typed by hand; reviewers only open uncertain documents |

## 2. Scope
In scope: 3 document types (invoice, purchase order, service agreement) + "other", 7 fields per type, three layouts
(`Label: value`, column-spaced, label-above-value), five date formats, INR/USD/EUR, JSON-Schema validation,
business-rule checks, extractive summary, human review and correction, web UI and REST API.

Out of scope: handwriting, tables with line-item extraction, multi-language documents, scanned PDFs without OCR,
real company documents.

## 3. Success metrics (defined BEFORE evaluation)
| Metric | Target |
|---|---|
| Document-type accuracy | > keyword baseline |
| Field accuracy on documents with known labels | >= 95% |
| Field accuracy with unseen label wording | reported honestly; failures must be flagged, not silent |
| Wrong values returned confidently | 0 (prefer "not found" to a wrong value) |
| Auto-accepted documents fully correct | >= 95% |
| Non-business / empty / corrupt input | handled with a clear message, never a crash |

## 4. Functional requirements
FR1 parse txt/pdf/(image with OCR) with size and type limits; FR2 classify document type; FR3 extract fields with
confidence; FR4 normalise dates to ISO-8601 and amounts to number + currency; FR5 validate with JSON Schema;
FR6 apply business rules (due date after invoice date, etc.); FR7 summarise; FR8 flag for human review with reasons;
FR9 let a reviewer correct values (re-validated); FR10 export JSON; FR11 UI + API; FR12 evaluation vs baselines.

## 5. Acceptance criteria -> evidence
| Criterion | Evidence |
|---|---|
| Core requirements complete | `docassist/`, `app.py`, `templates/` |
| Reproducible | README, `start.bat`, `scripts/generate_data.py`, `train.py`, `evaluate.py` |
| Quality documented and issues disclosed | `reports/evaluation_report.md`, `docs/error_analysis.md` |
| Tests | `tests/` (42 tests) |
| Can explain decisions | `docs/decision_log.md`, `docs/presentation_and_viva.md` |
