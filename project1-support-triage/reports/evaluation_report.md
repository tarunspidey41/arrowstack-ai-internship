# Evaluation Report - Intelligent Support Triage

All data is **simulated** (see `scripts/generate_data.py`). The eval set contains tickets with phrasing never seen in training (held-out templates) plus typos.

## eval set (300 tickets scored, 0 rejected by input validation)

| Metric | Baseline (rules) | AI (TF-IDF + LR) |
|---|---|---|
| Issue type accuracy | 0.553 | 0.743 |
| Issue type macro-F1 | 0.571 | 0.746 |
| Urgency accuracy | 0.717 | 0.953 |
| Urgency macro-F1 | 0.710 | 0.962 |
| Routing accuracy | 0.553 | 0.743 |
| Severe urgency under-prioritisation (count) | 7 | 0 |

**Guardrails (AI + human review):**
- Sent to human review: 151 / 300 (50.3%)
- Auto-routed tickets: 149, routing accuracy on those: 0.9866

### Per-class report - issue_type (AI)
```
                 precision    recall  f1-score   support

 account_access       0.87      0.80      0.83        50
        billing       0.83      1.00      0.91        50
feature_request       0.76      0.76      0.76        50
general_inquiry       0.82      0.74      0.78        50
       security       0.85      0.66      0.74        50
      technical       0.42      0.50      0.45        50

       accuracy                           0.74       300
      macro avg       0.76      0.74      0.75       300
   weighted avg       0.76      0.74      0.75       300

```

### Confusion matrix - issue_type (rows = true, cols = predicted)
```
                 account_access  billing  feature_request  general_inquiry  security  technical
account_access               40        0                8                0         0          2
billing                       0       50                0                0         0          0
feature_request               0        0               38                1         0         11
general_inquiry               0        0                4               37         0          9
security                      4        0                0                0        33         13
technical                     2       10                0                7         6         25
```

### Per-class report - urgency (AI)
```
              precision    recall  f1-score   support

    critical       1.00      1.00      1.00        26
        high       0.95      0.95      0.95        63
         low       0.96      0.96      0.96        99
      medium       0.94      0.94      0.94       112

    accuracy                           0.95       300
   macro avg       0.96      0.96      0.96       300
weighted avg       0.95      0.95      0.95       300

```

### Confusion matrix - urgency (rows = true, cols = predicted)
```
          critical  high  low  medium
critical        26     0    0       0
high             0    60    0       3
low              0     0   95       4
medium           0     3    4     105
```

Misclassified by AI: **81** tickets (saved to `reports/errors_eval.csv`).

## hard_cases set (19 tickets scored, 1 rejected by input validation)

| Metric | Baseline (rules) | AI (TF-IDF + LR) |
|---|---|---|
| Issue type accuracy | 0.421 | 0.737 |
| Issue type macro-F1 | 0.361 | 0.712 |
| Urgency accuracy | 0.474 | 0.632 |
| Urgency macro-F1 | 0.451 | 0.622 |
| Routing accuracy | 0.421 | 0.737 |
| Severe urgency under-prioritisation (count) | 3 | 1 |

**Guardrails (AI + human review):**
- Sent to human review: 13 / 19 (68.4%)
- Auto-routed tickets: 6, routing accuracy on those: 0.8333

Misclassified by AI: **10** tickets (saved to `reports/errors_hard_cases.csv`).
