from docassist import extractor, baseline


def test_label_fuzzy_matching():
    assert extractor.label_score("Inv. No.", "invoice number") == 1.0
    assert extractor.label_score("Invoice Dt", "invoice date") == 1.0
    assert extractor.label_score("Date of Invoice", "invoice date") == 1.0
    assert extractor.label_score("Due Date", "invoice date") < 0.82
    assert extractor.label_score("Subtotal", "total") < 0.82


def test_colon_layout():
    t = "INVOICE\nInvoice No: INV-1001\nInvoice Date: 2026-01-05\nDue Date: 2026-02-04\nVendor: Acme Traders Ltd\nBill To: Beta Corp Inc\nTotal: Rs. 1,000.00"
    f = extractor.extract(t, "invoice")
    assert f["invoice_number"]["value"] == "INV-1001"
    assert f["total_amount"]["value"] == 1000.0 and f["total_amount"]["currency"] == "INR"
    assert f["due_date"]["value"] == "2026-02-04"


def test_spaced_and_stacked_layouts():
    spaced = "Invoice No                INV-77\nDate                      5 March 2026"
    f = extractor.extract(spaced, "invoice")
    assert f["invoice_number"]["value"] == "INV-77" and f["invoice_date"]["value"] == "2026-03-05"
    stacked = "Invoice No\nINV-88\nDue Date\n14-Mar-2026"
    f = extractor.extract(stacked, "invoice")
    assert f["invoice_number"]["value"] == "INV-88" and f["due_date"]["value"] == "2026-03-14"


def test_due_date_not_confused_with_invoice_date():
    t = "Invoice Date: 2026-01-05\nDue Date: 2026-02-04"
    f = extractor.extract(t, "invoice")
    assert f["invoice_date"]["value"] == "2026-01-05" and f["due_date"]["value"] == "2026-02-04"


def test_never_returns_wrong_type_value():
    f = extractor.extract("Invoice Date: not a date\nTotal: abc", "invoice")
    assert "invoice_date" not in f and "total_amount" not in f


def test_ambiguous_date_lowers_confidence():
    f = extractor.extract("Invoice Date: 05/03/2026", "invoice")
    assert f["invoice_date"]["confidence"] < 0.85


def test_unknown_doc_type_returns_nothing():
    assert extractor.extract("Total: 5.00", "other") == {}


def test_baseline_is_colon_only():
    t = "Invoice No: INV-1\nInvoice Date: 2026-01-05"
    assert baseline.extract_rules(t, "invoice")["invoice_number"] == "INV-1"
    assert "invoice_number" not in baseline.extract_rules("Invoice No      INV-1", "invoice")
