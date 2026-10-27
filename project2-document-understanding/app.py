"""Flask web app + REST API for the Document Understanding Assistant.

Run:  python app.py      (then open http://127.0.0.1:5002)
"""
import json
import threading

from flask import Flask, jsonify, render_template, request, Response

from docassist import config
from docassist.parsers import UnsupportedDocument
from docassist.pipeline import DocumentAnalyzer
from docassist.schemas import FIELD_SPECS

app = Flask(__name__)
app.json.sort_keys = False
app.config["MAX_CONTENT_LENGTH"] = (config.MAX_FILE_MB + 1) * 1024 * 1024
_analyzer = None
_lock = threading.Lock()
RESULTS = {}
LOG_FILE = config.RUNTIME_DIR / "results.jsonl"


def analyzer() -> DocumentAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = DocumentAnalyzer()
    return _analyzer


def _persist(obj: dict):
    config.RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    with _lock, open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def _store(res: dict) -> dict:
    res["review_status"] = "pending" if res["needs_human_review"] else "auto_accepted"
    RESULTS[res["document_id"]] = res
    safe = {k: v for k, v in res.items() if k != "entities"}   # privacy: contact details are not persisted
    _persist(safe)
    return res


@app.errorhandler(413)
def too_large(_):
    return jsonify(error="too_large", message=f"File exceeds {config.MAX_FILE_MB} MB."), 413


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify(status="ok", documents_processed=len(RESULTS))


@app.post("/api/analyze")
def api_analyze():
    try:
        if "file" in request.files:
            f = request.files["file"]
            res = analyzer().analyze_bytes(f.read(), f.filename)
        else:
            data = request.get_json(silent=True) or {}
            text = data.get("text")
            if not isinstance(text, str) or not text.strip():
                return jsonify(error="no_input", message="Upload a file or send JSON {\"text\": \"...\"}."), 400
            res = analyzer().analyze_text(text)
    except UnsupportedDocument as e:
        return jsonify(error=e.code, message=e.message), 400
    return jsonify(_store(res))


@app.get("/api/samples")
def api_samples():
    d = config.DATA_DIR / "samples"
    return jsonify(samples=sorted(p.name for p in d.glob("*") if p.is_file()) if d.exists() else [])


@app.post("/api/samples/<name>")
def api_sample(name):
    d = (config.DATA_DIR / "samples").resolve()
    p = (d / name).resolve()
    if d not in p.parents or not p.is_file():      # path-traversal guard
        return jsonify(error="not_found", message="Unknown sample."), 404
    try:
        return jsonify(_store(analyzer().analyze_bytes(p.read_bytes(), p.name)))
    except UnsupportedDocument as e:
        return jsonify(error=e.code, message=e.message), 400


@app.get("/api/results")
def api_results():
    return jsonify(results=[{k: r[k] for k in ("document_id", "filename", "doc_type", "needs_human_review",
                                               "review_status")} for r in list(RESULTS.values())[::-1]])


@app.get("/api/results/<doc_id>")
def api_result(doc_id):
    r = RESULTS.get(doc_id)
    return (jsonify(r) if r else (jsonify(error="not_found", message="Unknown document id."), 404))


@app.post("/api/review/<doc_id>")
def api_review(doc_id):
    """Human reviewer submits corrected field values; the corrected record is re-validated."""
    r = RESULTS.get(doc_id)
    if not r:
        return jsonify(error="not_found", message="Unknown document id."), 404
    data = request.get_json(silent=True) or {}
    corrections = data.get("corrections", {})
    specs = FIELD_SPECS.get(r["doc_type"], {})
    bad = [k for k in corrections if k not in specs and k != "currency"]
    if bad:
        return jsonify(error="unknown_field", message=f"Unknown field(s): {', '.join(bad)}"), 400
    record = dict(r["record"])
    for k, v in corrections.items():
        if v in (None, ""):
            record.pop(k, None)
        else:
            record[k] = v
    r["record"] = record
    r["validation"] = analyzer()._validate(r["doc_type"], record) if specs else r["validation"]
    r["review_status"] = "corrected" if corrections else "approved"
    r["corrections"] = corrections
    _persist({"event": "review", "document_id": doc_id, "status": r["review_status"], "corrections": corrections})
    return jsonify(r)


@app.get("/api/export/<doc_id>")
def api_export(doc_id):
    r = RESULTS.get(doc_id)
    if not r:
        return jsonify(error="not_found", message="Unknown document id."), 404
    out = {"document_id": r["document_id"], "filename": r["filename"], "doc_type": r["doc_type"],
           "record": r["record"], "summary": r["summary"], "validation": r["validation"],
           "review_status": r["review_status"]}
    return Response(json.dumps(out, indent=2), mimetype="application/json",
                    headers={"Content-Disposition": f"attachment; filename={doc_id}.json"})


if __name__ == "__main__":
    analyzer()
    app.run(host="127.0.0.1", port=config.PORT, debug=False)
