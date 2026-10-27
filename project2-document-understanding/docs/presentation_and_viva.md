# Demo Script (5 minutes) and Viva Answers

## Demo flow
1. Run `start.bat`; the browser opens http://127.0.0.1:5002.
2. Pick `sample_1_invoice.txt` -> show document type, extracted fields with confidence and source line, headline and key points.
3. Pick `sample_2_invoice.pdf` -> same result from a PDF.
4. Pick `sample_8_invoice_unusual_labels.txt` -> fields not found, "Human review required" with reasons.
5. Edit a field value and press Confirm -> status becomes corrected; download the JSON.
6. Pick `sample_7_not_a_business_doc.txt` -> flagged as unsupported.
7. Open `reports/evaluation_report.md` -> baselines vs assistant, by condition.
8. Run `stop.bat`.

## Viva questions
**Problem and success?** Turn invoices, POs and contracts into validated structured data. Success: beat baselines, >= 95% correct on auto-accepted documents, never return confident wrong values, flag everything uncertain.

**Biggest decision?** Prefer "not found" over a guess, combined with type checks and a review flag. In evaluation every error was an omission and 98.2% of auto-accepted documents were fully correct.

**Validation?** Ground-truth evaluation on 150 simulated documents, three systems compared, results split by layout / label wording / noise, error list, 42 automated tests, JSON-Schema and business-rule validation.

**Edge cases / risks?** Ambiguous dd/mm dates, Indian number grouping, missing fields, non-business documents, corrupt PDFs, scans without a text layer, oversized files, unsupported types, path traversal in sample loading.

**10x scale?** Queue + workers, store documents and results in a database/object storage, batch classification, cache the model, add monitoring of review and correction rates, learn synonyms from corrections, add authentication and rate limits.

**Non-technical explanation?** It reads a document like a clerk: decides what kind it is, copies out the important facts, checks they make sense, writes a one-line summary, and hands anything doubtful to a person.

**Most independent problem-solving?** My first baseline scored 2.9%, which made the comparison meaningless. I built a fairer rule baseline, separated results by layout and label wording, and reported that the unseen-label accuracy (about 0.7) is the real generalisation number.
