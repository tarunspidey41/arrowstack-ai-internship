# Responsible-Use Notes

- **Simulated data only.** No real company documents are included. Real invoices contain personal and financial data; use only with authorisation.
- **Human in the loop.** Missing, low-confidence, rule-violating, non-business and unreadable documents are flagged with reasons. Reviewers can correct values and the record is re-validated.
- **Abstain rather than guess.** The extractor returns "not found" instead of a low-quality value (0 wrong values in evaluation).
- **Privacy.** Uploaded text is analysed in memory. Only the record, summary and review decision are logged; emails and phone numbers found in the document are NOT persisted. Files are never executed; type and size limits apply; sample paths are protected against path traversal.
- **Financial risk.** Extracted amounts must not be posted without validation. Business rules and review flags reduce, not remove, the risk.
- **Bias / coverage.** Supports English, Latin-script documents and three currencies; other languages and formats will fail or be flagged.
- **Security.** The demo server binds to 127.0.0.1 and has no authentication; do not expose it to a network without authentication, HTTPS and rate limiting.
- **Accuracy claims.** Reported accuracy applies to simulated documents and must not be quoted as production accuracy.
