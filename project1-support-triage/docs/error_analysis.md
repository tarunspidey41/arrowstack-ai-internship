# Error Analysis

Numbers come from `reports/evaluation_report.md` (re-generate with `python scripts/evaluate.py`).

## Headline results (300 simulated eval tickets, half with unseen phrasing and typos)
| | Baseline | AI |
|---|---|---|
| Issue-type accuracy | 0.553 | 0.743 |
| Urgency accuracy | 0.717 | 0.953 |
| Routing accuracy | 0.553 | 0.743 |
| Severe under-prioritisation | 7 | 0 |

With guardrails 50.3% of tickets go to a human and the remaining 149 auto-routed tickets are 98.7% correct.
The trade-off is explicit: more automation means lower accuracy; more review means higher accuracy and more human work.

## Where the model fails
1. **Technical vs everything else.** Technical has the lowest F1 (0.45). Held-out technical phrasing such as
   "search box returns blank results" or "screen freezes" shares few words with training examples, so the model
   falls back to other classes (billing, general inquiry).
2. **Security phrased without security words.** "Someone has been sending messages from my profile..." was
   predicted as technical (13 security tickets became technical). The training vocabulary for security is
   dominated by words like exposed, phishing, vulnerability.
3. **Account access vs feature request.** "Unable to get into my profile, the page keeps sending me back to the
   sign in screen" became feature_request (8 cases) because "profile" and "page" appear in feature templates.
4. **Typos.** Character n-grams help, but two typos in the key word can still cause a miss.

## Hard hand-written cases (19 scored, 1 rejected as too short)
Issue accuracy 0.737, urgency accuracy 0.632 (baseline 0.421 / 0.474). Typical failures:
- Mixed issues ("charged twice AND cannot log in") - the label is subjective, the model picks one.
- Contradictory cues ("Not urgent but our entire production environment is down") - classified correctly here, but this relies on the word 'production' and is fragile.
- "Where do I report a bug that lets anyone read other users' files?" - a security question phrased as a how-to,
  predicted with low urgency. It was still sent to human review because every security ticket requires a human.
- Very short text ("Not able to access") - not enough signal.

## What the guardrails caught
- All security and critical tickets are forced to human review (policy rule).
- On the hard set, 13 of 19 tickets went to review; the 6 auto-routed ones were 83% correct.
- The safety-keyword override raises urgency when words like breach, leaked or exposed appear.

## Limitations
- Data is simulated and templated; real tickets are longer, noisier and multilingual. Reported accuracy must not be
  read as production accuracy.
- Labels for urgency without a cue use a type default, which is an assumption.
- Hard-case set is small (20 tickets), so its percentages are indicative only.
- No online learning yet: human corrections are stored but not used for retraining.

## Recommended next improvements
1. Collect reviewer corrections (already stored in `data/runtime/tickets.jsonl`) and retrain monthly.
2. Add an LLM or sentence-embedding model as a second opinion and compare against this baseline.
3. Add multilingual support (Tamil/Hindi tickets).
4. Calibrate the confidence threshold using cost of a mis-route vs cost of a review.
5. Add monitoring: share of tickets sent to review, correction rate, drift in vocabulary.
