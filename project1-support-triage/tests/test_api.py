import pytest
import app as appmod


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(appmod, "LOG_FILE", tmp_path / "t.jsonl")
    appmod.TICKETS.clear()
    return appmod.app.test_client()


def test_health_and_index(client):
    assert client.get("/api/health").json["status"] == "ok"
    assert client.get("/").status_code == 200


def test_triage_ok(client):
    r = client.post("/api/triage", json={"text": "I forgot my password and the reset email never arrives."})
    assert r.status_code == 200 and r.json["issue_type"] == "account_access"


@pytest.mark.parametrize("payload", [{}, {"text": ""}, {"text": "hi"}, {"text": 5}])
def test_triage_bad_input_400(client, payload):
    assert client.post("/api/triage", json=payload).status_code == 400


def test_non_json_body_is_400(client):
    assert client.post("/api/triage", data="not json").status_code == 400


def test_batch_mixed(client):
    r = client.post("/api/triage/batch", json={"texts": ["It would be great to have a dark mode.", "hi"]})
    res = r.json["results"]
    assert "issue_type" in res[0] and res[1]["error"] == "too_short"


def test_batch_limits(client):
    assert client.post("/api/triage/batch", json={"texts": []}).status_code == 400
    assert client.post("/api/triage/batch", json={"texts": ["valid ticket text here"] * 101}).status_code == 400


def test_review_flow(client):
    t = client.post("/api/triage", json={"text": "My API key was exposed in a public repository."}).json
    assert t["review_status"] == "pending"
    assert len(client.get("/api/queue").json["pending"]) == 1
    r = client.post(f"/api/review/{t['ticket_id']}", json={"issue_type": "technical", "urgency": "high"})
    assert r.json["review_status"] == "corrected"
    assert client.get("/api/queue").json["pending"] == []
    assert client.get("/api/stats").json["human_corrections"] == 1


def test_review_validation(client):
    assert client.post("/api/review/nope", json={}).status_code == 404
    t = client.post("/api/triage", json={"text": "My API key was exposed in a public repository."}).json
    assert client.post(f"/api/review/{t['ticket_id']}", json={"issue_type": "banana"}).status_code == 400
