# Demo Script (5 minutes) and Viva Answers

## Demo flow
1. Run `start.bat`; the browser opens the UI.
2. Click "Example: security" -> show issue type, urgency, route, SLA, confidence and the human-review flag.
3. Click "Example: billing" -> note it is auto-routed (only if confidence is high).
4. Paste a ticket containing an e-mail and phone number -> show the masked stored text.
5. Submit "hi" -> show the validation error.
6. In the review queue change a label and Confirm -> show the statistics line (corrected count).
7. Open `reports/evaluation_report.md` -> baseline vs AI table and the error analysis.
8. Run `stop.bat`.

## Viva questions
**Problem and success?** Route support tickets to the right team and surface urgent ones. Success = beats the keyword baseline, no severe under-prioritisation, auto-routed tickets >= 95% correct, security/critical always reviewed.

**Biggest decision?** Evaluating on held-out phrasing and adding the human-review guardrail. The first prevents inflated numbers; the second turns a 74% classifier into a safe workflow (98.7% on the auto-routed part).

**Validation?** Baseline vs AI on a held-out set and a hard set, per-class report, confusion matrices, error CSVs, 30 unit/API tests.

**Edge cases / risks?** Empty, tiny, huge, non-text input; PII; mixed issues; sarcasm; non-English; typos; casual breach wording.

**10x scale?** Move the model behind a queue worker, batch predictions, store tickets in a database, monitor review rate and drift, add retraining from reviewer corrections, add auth and rate limiting.

**Non-technical explanation?** It reads each ticket like a junior agent, suggests the team and how fast to reply, and says "please check this one" when it is unsure or when the ticket is sensitive.

**Most independent problem-solving?** Discovering that a random split gave misleadingly high scores and redesigning the data split; finding and fixing the validation-order bug where a 6000-character single word was reported as too short.
