# Requirements & Acceptance Criteria - Intelligent Support Triage

## 1. Problem framing
A support desk receives free-text tickets. Agents lose time reading, tagging and forwarding them, and urgent or
security-related tickets can wait in the same queue as feature requests.

| Item | Definition |
|---|---|
| Primary stakeholder | Support team lead (owns queue health and response-time targets) |
| Other users | L1/L2 agents (receive routed tickets), Security Operations (receive security tickets) |
| Input | One free-text ticket (10-5000 chars, at least 3 words) |
| Output | issue type, urgency, recommended team, target response time, confidence scores, human-review flag + reasons |
| Decision enabled | Which team gets the ticket and how fast it must be answered |
| Measurable benefit | Fewer mis-routed tickets, urgent tickets surfaced first, agents only look at tickets the model is unsure about |

## 2. Scope
In scope: classification of 6 issue types x 4 urgency levels, routing recommendation, PII masking, human review queue,
batch + single API, web UI, evaluation against a rule-based baseline.

Out of scope: sending replies, integration with a real ticketing system, multi-language support, training on real customer data.

## 3. Success metrics (defined BEFORE evaluation)
| Metric | Target |
|---|---|
| Issue-type accuracy on held-out phrasing | beat the keyword baseline |
| Urgency accuracy | beat the keyword baseline |
| Severe under-prioritisation (urgency off by 2+ levels) | 0 on the eval set |
| Accuracy of auto-routed tickets (no human review) | >= 95% routing accuracy |
| Security and critical tickets | 100% sent to a human |
| Invalid / empty input | rejected with a clear error, never a crash |

## 4. Functional requirements
- FR1 Validate input (type, empty, length, natural text).
- FR2 Mask e-mails, phone numbers and card numbers before anything is stored or logged.
- FR3 Predict issue type and urgency with confidence.
- FR4 Recommend a routing team and SLA from issue type + urgency.
- FR5 Flag tickets for human review (low confidence, security, critical, conflicting safety keywords).
- FR6 Let a reviewer approve or correct the AI suggestion; keep the correction.
- FR7 Provide a web UI and a REST API (single + batch).
- FR8 Compare against a baseline and publish an evaluation report.

## 5. Non-functional requirements
Runs locally on Windows with Python 3.10+, no paid API key, response < 1 s per ticket, deterministic output,
one-click start.bat / stop.bat.

## 6. Acceptance criteria -> evidence
| Criterion | Evidence |
|---|---|
| Core requirements complete | `triage/`, `app.py`, `templates/index.html` |
| Reproducible by a mentor | README + `start.bat`, `python scripts/generate_data.py`, `train.py`, `evaluate.py` |
| Quality documented, issues disclosed | `reports/evaluation_report.md`, `docs/error_analysis.md` |
| Tests | `tests/` (30 tests, `python -m pytest`) |
| Can explain decisions | `docs/decision_log.md`, `docs/presentation_and_viva.md` |
