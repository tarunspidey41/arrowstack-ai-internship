# Decision Log

| # | Decision | Alternatives | Reason / trade-off |
|---|---|---|---|
| D1 | Hybrid approach: ML document classifier + fuzzy label-value extraction | LLM API for everything; spaCy NER; layout model | Runs offline and free, deterministic, auditable (each field shows its source line and matched label). Trade-off: it only finds fields whose labels resemble the lexicon. An LLM extractor is the planned next step. |
| D2 | Parse text from PDFs with pypdf; OCR only if Tesseract is installed | require OCR always | OCR needs a separate Windows install. The app reports clearly when OCR is missing instead of failing. |
| D3 | Three candidate layouts (colon, spaced, stacked) | colon only | Real documents vary; a colon-only parser is the baseline. |
| D4 | Fuzzy label matching: abbreviation expansion + stop-words + string similarity, threshold 0.82 | exact match, embeddings | Handles "Inv. No.", "Invoice Dt", "Date of Invoice". Threshold chosen so "Subtotal" (0.77) never matches "Total" and "Due Date" never matches "Date". |
| D5 | Check value TYPE before accepting a match (date must parse, amount must parse, party must not look like a date) | trust the label | Prevents putting a quantity in a total field. |
| D6 | Greedy one-to-one assignment by score | independent per field | One line cannot fill two fields. |
| D7 | Numeric dates are read day-first (dd/mm/yyyy); when both parts <= 12 confidence drops to 0.75 and the document is flagged | assume mm/dd | Indian business convention; ambiguity is surfaced, not hidden. |
| D8 | Prefer "not found" over a guess | best-effort fill | A missing field is flagged; a wrong field can be posted silently. |
| D9 | Validate with JSON Schema (draft-07) and business rules | ad-hoc checks | Standard, reusable by downstream systems; required fields reported separately. |
| D10 | Extractive summary (TF-IDF centrality) + structured headline from the validated fields | abstractive LLM summary | No hallucinated facts; headline can only contain extracted values. |
| D11 | Evaluation uses held-out label wording and three baselines | random split | Shows generalisation rather than memorisation of the lexicon. |
| D12 | Only the record and summary are persisted; entities (emails, phones) are not | store everything | Privacy by default. |
