"""Flask web app + REST API for the Support Triage workflow.

Run:  python app.py      (then open http://127.0.0.1:5001)
"""
import json
import threading
from collections import Counter

from flask import Flask, jsonify, render_template, request

from triage import config
from triage.pipeline import TriageEngine
from triage.preprocess import InvalidTicket

app = Flask(__name__)
app.json.sort_keys = False
_engine = None
_lock = threading.Lock()
TICKETS = {}          # ticket_id -> result (masked text only)
LOG_FILE = config.RUNTIME_DIR / "tickets.jsonl"


def engine() -> TriageEngine:
    global _engine
    if _engine is None:
        _engine = TriageEngine()
    return _engine


def _persist(record: dict):
    config.RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    with _lock, open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _store(result: dict) -> dict:
    result["review_status"] = "pending" if result["needs_human_review"] else "auto_routed"
    TICKETS[result["ticket_id"]] = result
    _persist(result)  # NOTE: only masked text is stored
    return result


@app.get("/")
def index():
    return render_template("index.html", issue_types=config.ISSUE_TYPES, urgency_levels=config.URGENCY_LEVELS)


@app.get("/api/health")
def health():
    return jsonify(status="ok", tickets_processed=len(TICKETS))


@app.post("/api/triage")
def api_triage():
    data = request.get_json(silent=True) or {}
    try:
        res = engine().triage(data.get("text"))
    except InvalidTicket as e:
        return jsonify(error=e.code, message=e.message), 400
    return jsonify(_store(res))


@app.post("/api/triage/batch")
def api_batch():
    data = request.get_json(silent=True) or {}
    texts = data.get("texts")
    if not isinstance(texts, list) or not texts:
        return jsonify(error="invalid_batch", message="Provide a non-empty list under 'texts'."), 400
    if len(texts) > config.MAX_BATCH:
        return jsonify(error="batch_too_large", message=f"Max {config.MAX_BATCH} tickets per batch."), 400
    results = []
    for i, t in enumerate(texts):
        try:
            results.append(_store(engine().triage(t)))
        except InvalidTicket as e:
            results.append({"index": i, "error": e.code, "message": e.message})
    return jsonify(results=results)


@app.get("/api/queue")
def api_queue():
    pending = [t for t in TICKETS.values() if t["review_status"] == "pending"]
    return jsonify(pending=pending[::-1])


@app.get("/api/tickets")
def api_tickets():
    return jsonify(tickets=list(TICKETS.values())[::-1][:200])


@app.post("/api/review/<ticket_id>")
def api_review(ticket_id):
    """Human reviewer approves or corrects the AI suggestion."""
    t = TICKETS.get(ticket_id)
    if not t:
        return jsonify(error="not_found", message="Unknown ticket id."), 404
    data = request.get_json(silent=True) or {}
    issue = data.get("issue_type", t["issue_type"])
    urgency = data.get("urgency", t["urgency"])
    if issue not in config.ISSUE_TYPES or urgency not in config.URGENCY_LEVELS:
        return jsonify(error="invalid_label", message="Unknown issue_type or urgency."), 400
    from triage.baseline import route
    corrected = (issue, urgency) != (t["issue_type"], t["urgency"])
    t.update(final_issue_type=issue, final_urgency=urgency, final_route=route(issue, urgency),
             review_status="corrected" if corrected else "approved")
    _persist({"event": "review", "ticket_id": ticket_id, "status": t["review_status"],
              "final_issue_type": issue, "final_urgency": urgency})
    return jsonify(t)


@app.get("/api/stats")
def api_stats():
    ts = list(TICKETS.values())
    return jsonify(
        total=len(ts),
        by_issue=Counter(t["issue_type"] for t in ts),
        by_urgency=Counter(t["urgency"] for t in ts),
        by_status=Counter(t["review_status"] for t in ts),
        human_corrections=sum(t["review_status"] == "corrected" for t in ts),
    )


if __name__ == "__main__":
    engine()  # load/train model before serving
    app.run(host="127.0.0.1", port=config.PORT, debug=False)
