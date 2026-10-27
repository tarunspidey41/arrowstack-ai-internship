import io
import pytest
import app as appmod


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(appmod, "LOG_FILE", tmp_path / "r.jsonl")
    appmod.RESULTS.clear()
    return appmod.app.test_client()


INV = ("INVOICE\nInvoice No: INV-1234\nInvoice Date: 2026-01-05\nDue Date: 2026-02-04\nVendor: Acme Traders Ltd\n"
       "Bill To: Beta Corp Inc\nTax: Rs. 100.00\nTotal: Rs. 1,000.00\nPayment is due within thirty days of the invoice date.")


def test_basics(client):
    assert client.get("/").status_code == 200
    assert client.get("/api/health").json["status"] == "ok"


def test_analyze_text_and_upload(client):
    r = client.post("/api/analyze", json={"text": INV})
    assert r.status_code == 200 and r.json["doc_type"] == "invoice"
    r = client.post("/api/analyze", data={"file": (io.BytesIO(INV.encode()), "inv.txt")}, content_type="multipart/form-data")
    assert r.status_code == 200 and r.json["record"]["invoice_number"] == "INV-1234"


@pytest.mark.parametrize("payload", [{}, {"text": ""}, {"text": 5}])
def test_no_input_400(client, payload):
    assert client.post("/api/analyze", json=payload).status_code == 400


def test_unsupported_file_400(client):
    r = client.post("/api/analyze", data={"file": (io.BytesIO(b"abc"), "x.exe")}, content_type="multipart/form-data")
    assert r.status_code == 400 and r.json["error"] == "unsupported_type"


def test_samples_and_path_traversal(client):
    assert client.post("/api/samples/sample_1_invoice.txt").status_code == 200
    assert client.post("/api/samples/..%2Frequirements.txt").status_code == 404
    assert client.post("/api/samples/nope.txt").status_code == 404


def test_review_correction_revalidates(client):
    d = client.post("/api/analyze", json={"text": INV}).json
    r = client.post(f"/api/review/{d['document_id']}", json={"corrections": {"vendor_name": "Acme Traders Pvt Ltd"}})
    assert r.json["review_status"] == "corrected" and r.json["record"]["vendor_name"] == "Acme Traders Pvt Ltd"
    assert client.post(f"/api/review/{d['document_id']}", json={"corrections": {"bogus": 1}}).status_code == 400
    assert client.post("/api/review/zzz", json={}).status_code == 404


def test_export(client):
    d = client.post("/api/analyze", json={"text": INV}).json
    r = client.get(f"/api/export/{d['document_id']}")
    assert r.status_code == 200 and "attachment" in r.headers["Content-Disposition"]
    assert client.get("/api/export/nope").status_code == 404


def test_contact_details_not_persisted(client, tmp_path):
    client.post("/api/analyze", json={"text": INV + "\nContact: priya@example.com 9876543210"})
    log = (tmp_path / "r.jsonl").read_text()
    assert "priya@example.com" not in log and "9876543210" not in log
