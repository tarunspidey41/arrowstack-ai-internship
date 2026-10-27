# Arrowstack AI Internship - Projects

Two portfolio projects completed for the Arrowstack 1-Month Artificial Intelligence Internship.
Each project runs locally on Windows with one click (`start.bat`) and stops with `stop.bat`.

| # | Project | What it does | Port | Tests |
|---|---|---|---|---|
| 1 | [Intelligent Support Triage](project1-support-triage) | Classifies support tickets by issue type and urgency, recommends routing, masks PII, sends uncertain/sensitive tickets to a human review queue | 5001 | 30 |
| 2 | [Document Understanding Assistant](project2-document-understanding) | Classifies business documents, extracts and validates fields (JSON Schema + business rules), summarises, flags uncertain documents | 5002 | 42 |

Both projects use only **simulated data**, include a baseline-vs-AI evaluation, error analysis, responsible-use notes,
a decision log, a dated work log, and viva/demo notes. Honest limitations are documented in each `docs/error_analysis.md`.

## Run
Install Python 3.10+, open a project folder and double-click `start.bat` (stop with `stop.bat`).
Manual commands are in each project's README.

## Requirement coverage (Arrowstack handbook)
Problem framing - Evaluation dataset - Baseline vs AI approach - Human review / guardrails - Error analysis and
responsible-use notes - README - tests - version-controlled repository.
