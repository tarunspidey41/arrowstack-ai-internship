# Evaluation Report - Document Understanding Assistant

All 150 documents are **simulated** (`scripts/generate_data.py`). Eval layouts include stacked layouts, five date formats, three currencies, OCR-like label noise, and **label wording not present in the extractor lexicon** (held-out labels).

## Overall

| Metric | Naive baseline (canonical label only) | Rule baseline (all label spellings, exact) | Assistant |
|---|---|---|---|
| Document-type accuracy (4 classes) | 0.733 (keywords) | n/a | 1.000 |
| Field accuracy | 0.029 | 0.205 (given true doc type) | 0.859 (end-to-end) |

Fields scored: 920 across 120 business documents.

## Accuracy by condition

| Condition | Naive | Rules | Assistant |
|---|---|---|---|
| style=colon, heldout_labels=False, noise=0.0 | 0.152 | 0.837 | 1.000 |
| style=colon, heldout_labels=False, noise=0.1 | 0.188 | 0.754 | 1.000 |
| style=colon, heldout_labels=True, noise=0.0 | 0.000 | 0.362 | 0.739 |
| style=colon, heldout_labels=True, noise=0.1 | 0.000 | 0.380 | 0.728 |
| style=spaced, heldout_labels=False, noise=0.0 | 0.000 | 0.000 | 1.000 |
| style=spaced, heldout_labels=False, noise=0.1 | 0.000 | 0.000 | 1.000 |
| style=spaced, heldout_labels=True, noise=0.0 | 0.000 | 0.000 | 0.728 |
| style=spaced, heldout_labels=True, noise=0.1 | 0.000 | 0.000 | 0.696 |
| style=stacked, heldout_labels=False, noise=0.0 | 0.000 | 0.000 | 1.000 |
| style=stacked, heldout_labels=False, noise=0.1 | 0.000 | 0.000 | 0.989 |
| style=stacked, heldout_labels=True, noise=0.0 | 0.000 | 0.000 | 0.725 |
| style=stacked, heldout_labels=True, noise=0.1 | 0.000 | 0.000 | 0.696 |

## Accuracy by field

| Field | Naive | Rules | Assistant |
|---|---|---|---|
| invoice.currency | 0.000 | 0.300 | 0.925 |
| invoice.customer_name | 0.000 | 0.225 | 0.650 |
| invoice.due_date | 0.000 | 0.075 | 0.850 |
| invoice.invoice_date | 0.000 | 0.075 | 1.000 |
| invoice.invoice_number | 0.000 | 0.125 | 0.875 |
| invoice.tax_amount | 0.000 | 0.250 | 0.850 |
| invoice.total_amount | 0.000 | 0.225 | 0.825 |
| invoice.vendor_name | 0.000 | 0.200 | 0.650 |
| purchase_order.buyer_name | 0.100 | 0.325 | 0.875 |
| purchase_order.currency | 0.025 | 0.325 | 1.000 |
| purchase_order.delivery_date | 0.025 | 0.075 | 1.000 |
| purchase_order.order_date | 0.000 | 0.075 | 1.000 |
| purchase_order.po_number | 0.100 | 0.250 | 0.900 |
| purchase_order.supplier_name | 0.050 | 0.250 | 0.725 |
| purchase_order.total_amount | 0.025 | 0.325 | 1.000 |
| service_agreement.client_name | 0.075 | 0.225 | 0.750 |
| service_agreement.contract_number | 0.000 | 0.200 | 0.650 |
| service_agreement.contract_value | 0.050 | 0.275 | 0.750 |
| service_agreement.currency | 0.050 | 0.275 | 0.750 |
| service_agreement.effective_date | 0.000 | 0.025 | 0.850 |
| service_agreement.end_date | 0.025 | 0.025 | 0.925 |
| service_agreement.governing_law | 0.100 | 0.350 | 0.950 |
| service_agreement.provider_name | 0.050 | 0.250 | 1.000 |

## Human-review guardrail

- Documents sent to human review: **94 / 150** (62.7%)
- Auto-accepted business documents: 56, of which fully correct: **0.9821**
- Documents with at least one wrong field that were NOT flagged: **1**
- Business documents with every field correct: 54.2%

## Summary quality

Headline contains the correct counterparty AND amount in **68.3%** of business documents (a fact-coverage check, not a fluency score).

Errors listed in `reports/errors.csv` (130 rows).