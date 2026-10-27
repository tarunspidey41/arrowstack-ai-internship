# Error Analysis

Numbers from `reports/evaluation_report.md` (150 simulated documents: 40 per business type + 30 non-business).

## Headline results
| Metric | Naive baseline | Rule baseline | Assistant |
|---|---|---|---|
| Document-type accuracy | 0.733 (keywords) | - | 1.000 |
| Field accuracy | 0.029 | 0.205 (given the true type) | 0.859 (end-to-end) |

**Read these numbers carefully.**
- The baselines are intentionally limited to the easy `Label: value` layout. About two thirds of the evaluation
  documents use other layouts, which is why they score so low. The fairest comparison is the three
  `style=colon, heldout_labels=False` rows: rule baseline 0.75-0.84 vs assistant 1.00.
- The 1.000 on known labels is expected: the lexicon was written knowing those label spellings. The honest
  generalisation test is the **held-out label** rows: **0.70-0.74**.
- The documents are simulated. Real documents are messier, so real-world accuracy would be lower.

## What kind of errors?
All **130 field errors are omissions (field not found); there were 0 wrong values.** The type check, the 0.82 label
threshold and the one-to-one assignment make the extractor abstain instead of guess. Omissions are caught by the
required-field check and sent to a human.

129 of the 130 omissions occurred in documents that use held-out label wording. Main causes:
1. **Party labels with a different meaning-word** (the largest group): "Seller", "Sold To", "Supplied By",
   "Service Recipient", "Ordering Company", "Billing Name", "Issued By". String similarity cannot know these
   mean vendor/customer.
2. **Reference-style ID labels**: "Agreement Ref No", "Contract Ref", "Invoice Ref No", "Order Ref". After
   abbreviation expansion ("reference") they fall below the 0.82 threshold against "number"-style synonyms.
3. **OCR-like label noise** in a held-out label ("Sellcr") - one case; noise on known labels was almost always
   recovered by fuzzy matching (stacked, noise 0.1: 0.989).

Weakest fields: invoice vendor/customer names (0.65), contract number (0.65), contract value and currency (0.75).

## Guardrail results
- 94 of 150 documents were sent to review (62.7%). 30 of them are the non-business documents, which is correct.
  Of the 120 business documents, 64 (53%) were flagged. The rate is high because half the evaluation set was
  deliberately built with unseen label wording.
- 56 business documents were auto-accepted and **98.2% were fully correct** (target: 95%).
- One document had an error that was not flagged: a missing *optional* field (`governing_law`). Optional fields
  are not flagged by design; this is a documented trade-off.
- Ambiguous numeric dates (for example 05/03/2026) are accepted with confidence 0.75 and flagged.

## Summary quality
The headline contained the correct counterparty and amount in 68.3% of business documents. The shortfall equals
missing fields, because the headline is built only from extracted values (no hallucination). The check measures
fact coverage, not fluency.

## Limitations
- Lexicon-based: new wording needs new synonyms or an LLM fallback.
- No table / line-item extraction; totals are not recomputed from line items.
- Day-first date assumption.
- Scanned documents need Tesseract OCR, which is optional and untested on real scans here.
- Layouts are text only (no coordinates), so multi-column PDFs may interleave lines.
- Currency symbols supported: Rs./INR, $/USD, EUR.

## Recommended next improvements
1. LLM or embedding fallback for labels below the threshold, still validated by the same schema.
2. Learn synonyms from reviewer corrections (corrections are already stored).
3. Line-item table extraction and total cross-check (sum of lines + tax = total).
4. Layout-aware PDF parsing and OCR evaluation on real scans.
5. Monitoring: review rate, correction rate per field, drift in label vocabulary.
