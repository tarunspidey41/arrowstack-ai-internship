# Decision Log

| # | Decision | Alternatives | Reason / trade-off |
|---|---|---|---|
| D1 | Local TF-IDF + Logistic Regression instead of an LLM API | OpenAI/Claude API, fine-tuned transformer | Works offline, free, deterministic, fast, explainable, no customer text leaves the machine. Trade-off: weaker on unseen phrasing than an LLM. The `TriageEngine` can be swapped for an LLM classifier later. |
| D2 | Word n-grams + character n-grams | words only | Character n-grams make the model tolerant to typos ("sing in", "profiile"). |
| D3 | Two separate classifiers (issue type, urgency) | one 24-class model | Each target has its own signal and fewer classes; errors are easier to analyse. |
| D4 | Routing is rule-based from the two predictions | learn routing directly | Routing is business policy, not something to learn; it must be auditable. |
| D5 | Simulated data with held-out templates | random train/test split | A random split of templated data leaks phrasing and gives inflated scores. Eval uses phrasing never seen in training, plus typos. |
| D6 | Human-review guardrails: confidence < 0.55, all security, all critical | auto-route everything | Wrong routing of a security ticket is costly; reviewers only see about half the volume. |
| D7 | Safety-keyword override raises urgency to at least high | trust the model | The model can miss a breach phrased casually; over-escalating is cheaper than under-escalating. |
| D8 | Mask PII before storing | store raw text | Privacy by default; only masked text is persisted in `data/runtime/`. |
| D9 | Reject inputs that are empty, too short, too long or not text | classify anything | Avoids confident nonsense on "hi" or random characters. |
| D10 | Flask + single HTML page | React / Streamlit | Smallest dependency footprint, easy to start and stop with a .bat file. |
