# Responsible-Use Notes

- **Simulated data only.** No real customer tickets were used. Do not train on real tickets without consent and a data-protection review.
- **PII masking.** E-mails, phone numbers and card numbers are masked before storage or logging. The model sees the cleaned text in memory only; only masked text is written to disk.
- **Human in the loop.** The system recommends; people decide for security, critical and low-confidence tickets. Reviewer corrections are recorded.
- **No silent failure.** Invalid input returns an explicit error; the UI shows confidence and reasons for review.
- **Bias / fairness.** Ticket language, dialect or typos should not change how fast someone is served. Character n-grams reduce typo sensitivity, but non-English tickets are not supported and would be mis-prioritised; they should be sent to human review in production.
- **Over-trust risk.** Confidence scores from logistic regression are not perfectly calibrated; treat them as a ranking signal.
- **Security.** The demo server binds to 127.0.0.1 only and has no authentication. Do not expose it to a network without adding authentication, HTTPS and rate limiting.
- **Auditability.** Routing is a plain lookup table; every review flag lists its reasons.
