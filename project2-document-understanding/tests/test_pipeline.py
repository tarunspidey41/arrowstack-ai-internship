import random
import pytest
from docassist import synth
from docassist.parsers import parse_bytes, UnsupportedDocument
from docassist.pipeline import DocumentAnalyzer


@pytest.fixture(scope="module")
def an():
    return DocumentAnalyzer()


@pytest.mark.parametrize("dt", ["invoice", "purchase_order", "service_agreement"])
def test_clean_document_end_to_end(an, dt):
    text, truth, _ = synth.generate(dt, random.Random(11), style="colon", date_style=0, noise=0.0)
    r = an.analyze_text(text)
    assert r["doc_type"] == dt
    assert r["validation"]["schema_valid"]
    for k, v in truth.items():
        got = r["record"].get(k)
        assert got == v or (isinstance(v, float) and abs(got - v) < 0.01), k


def test_non_business_document_flagged(an):
    r = an.analyze_text("Dear Hiring Manager, I am writing to apply for the junior developer position advertised on your page.")
    assert r["doc_type"] in ("other", "unknown") and r["needs_human_review"] and r["record"] == {}


def test_too_little_text(an):
    r = an.analyze_text("hello")
    assert r["doc_type"] == "unknown" and r["needs_human_review"]


def test_missing_required_field_flagged(an):
    text = "INVOICE\nInvoice No: INV-1234\nVendor: Acme Traders Ltd\nBill To: Beta Corp Inc\nTotal: Rs. 1,000.00\nPayment is due within thirty days of the invoice date."
    r = an.analyze_text(text)
    assert r["needs_human_review"]
    assert "invoice_date" in r["validation"]["missing_required"]


def test_business_rule_date_order(an):
    text = ("INVOICE\nInvoice No: INV-1234\nInvoice Date: 2026-05-10\nDue Date: 2026-04-01\nVendor: Acme Traders Ltd\n"
            "Bill To: Beta Corp Inc\nTotal: Rs. 1,000.00\nPayment is due within thirty days of the invoice date.")
    r = an.analyze_text(text)
    assert any("due date must not be before" in w for w in r["validation"]["rule_warnings"])
    assert r["needs_human_review"]


def test_summary_headline_mentions_facts(an):
    text, truth, _ = synth.generate("invoice", random.Random(3), style="colon", date_style=0)
    h = an.analyze_text(text)["summary"]["headline"]
    assert truth["invoice_number"] in h and truth["vendor_name"] in h


def test_parse_txt_pdf_and_errors():
    assert parse_bytes(b"hello world this is a text file for testing purposes", "a.txt")[0].startswith("hello")
    for data, name, code in [(b"", "a.txt", "empty_file"), (b"x", "a.exe", "unsupported_type"),
                             (b"not a pdf", "a.pdf", "unreadable_pdf")]:
        with pytest.raises(UnsupportedDocument) as e:
            parse_bytes(data, name)
        assert e.value.code == code


def test_pdf_roundtrip(an):
    from pathlib import Path
    p = Path(__file__).resolve().parent.parent / "data" / "samples" / "sample_2_invoice.pdf"
    r = an.analyze_bytes(p.read_bytes(), p.name)
    assert r["doc_type"] == "invoice" and r["parser"] == "pypdf"
