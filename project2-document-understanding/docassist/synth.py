"""Synthetic business-document generator (NO real documents are used).

Every generated document comes with ground-truth field values, so extraction can be
measured objectively. Layout, labels, date formats and currency formats vary, because
real documents never use one single format.
"""
import random
from datetime import date, timedelta

VENDORS = ["Sunrise Traders Pvt Ltd", "Bluewave Logistics Ltd", "Orion Software Solutions Pvt Ltd",
           "Greenfield Agro Pvt Ltd", "Pioneer Steel Works Ltd", "Nova Stationers LLP",
           "Zenith Electronics Pvt Ltd", "Harbor Foods Inc", "Lotus Textiles Pvt Ltd",
           "Apex Consulting LLC", "Riverstone Hardware Ltd", "Crescent Packaging Pvt Ltd"]
CUSTOMERS = ["Madras Retail Corp", "Kaveri Healthcare Pvt Ltd", "Atlas Manufacturing Ltd",
             "Delta Education Trust", "Meridian Hotels Pvt Ltd", "Skyline Builders LLP",
             "Coastal Exports Inc", "Vertex Analytics Pvt Ltd", "Maple Finance Ltd", "Sapphire Clinics LLC"]
ITEMS = ["Office chairs", "Laptop batteries", "Printer cartridges", "Cloud hosting (monthly)",
         "Consulting hours", "Packaging boxes", "LED panels", "Steel brackets", "Software licence",
         "Maintenance visit", "Network cables", "Safety helmets"]
LAWS = ["Tamil Nadu, India", "Karnataka, India", "Delaware, USA", "England and Wales", "Maharashtra, India"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December"]

LABELS = {
    "invoice": {
        "invoice_number": ["Invoice No", "Invoice Number", "Invoice #", "Inv. No.", "Bill No"],
        "invoice_date": ["Invoice Date", "Date of Issue", "Issued On", "Date"],
        "due_date": ["Due Date", "Payment Due", "Pay By", "Due On"],
        "vendor_name": ["Vendor", "From", "Billed By", "Supplier"],
        "customer_name": ["Bill To", "Customer", "Billed To", "Client"],
        "tax_amount": ["Tax", "GST", "VAT", "Tax Amount"],
        "total_amount": ["Total", "Total Amount", "Amount Due", "Grand Total", "Total Payable"],
    },
    "purchase_order": {
        "po_number": ["PO Number", "PO No", "Purchase Order No", "Order #"],
        "order_date": ["Order Date", "PO Date", "Date Ordered"],
        "delivery_date": ["Delivery Date", "Deliver By", "Expected Delivery"],
        "buyer_name": ["Buyer", "Ordered By", "Bill To"],
        "supplier_name": ["Supplier", "Vendor", "Ship From"],
        "total_amount": ["Total", "Total Amount", "Order Total", "Grand Total"],
    },
    "service_agreement": {
        "contract_number": ["Agreement No", "Contract No", "Reference"],
        "effective_date": ["Effective Date", "Commencement Date", "Start Date"],
        "end_date": ["End Date", "Expiry Date", "Termination Date"],
        "provider_name": ["Service Provider", "Provider", "Party A"],
        "client_name": ["Client", "Customer", "Party B"],
        "contract_value": ["Contract Value", "Total Fees", "Total Consideration"],
        "governing_law": ["Governing Law", "Jurisdiction"],
    },
}

# Label variants used ONLY in the evaluation set (never in the extractor lexicon verbatim)
LABELS_HELDOUT = {
    "invoice": {
        "invoice_number": ["Invoice Num", "Invoice Ref No", "Inv Number"],
        "invoice_date": ["Invoice Dt", "Inv Date", "Date of Invoice"],
        "due_date": ["Payment Due Date", "Due Dt", "Date Due"],
        "vendor_name": ["Seller", "Issued By", "Vendor Name"],
        "customer_name": ["Sold To", "Customer Name", "Billing Name"],
        "tax_amount": ["Tax Amt", "GST Amount", "Total Tax"],
        "total_amount": ["Amount Payable", "Total Amt", "Invoice Total"],
    },
    "purchase_order": {
        "po_number": ["PO Num", "Purchase Order Number", "Order Ref"],
        "order_date": ["Date of Order", "PO Dt", "Order Dt"],
        "delivery_date": ["Delivery Dt", "Date of Delivery", "Required By"],
        "buyer_name": ["Purchaser", "Buyer Name", "Ordering Company"],
        "supplier_name": ["Vendor Name", "Supplied By", "Seller"],
        "total_amount": ["Total Amt", "Order Value", "Total Order Value"],
    },
    "service_agreement": {
        "contract_number": ["Agreement Number", "Contract Ref", "Agreement Ref No"],
        "effective_date": ["Date of Commencement", "Effective Dt", "Starts On"],
        "end_date": ["Date of Expiry", "Expiry Dt", "Ends On"],
        "provider_name": ["Service Provider Name", "Contractor", "Provider Name"],
        "client_name": ["Client Name", "Customer Name", "Service Recipient"],
        "contract_value": ["Total Contract Value", "Contract Amount", "Fees Payable"],
        "governing_law": ["Governing Jurisdiction", "Applicable Law", "Law"],
    },
}
_HELDOUT = {"on": False}


def _labels(doc_type):
    return LABELS_HELDOUT[doc_type] if _HELDOUT["on"] else LABELS[doc_type]

TITLES = {
    "invoice": ["INVOICE", "Tax Invoice", "Invoice"],
    "purchase_order": ["PURCHASE ORDER", "Purchase Order", "Order Form - Purchase Order"],
    "service_agreement": ["SERVICE AGREEMENT", "Master Service Agreement", "Services Contract Agreement"],
}


# ---------- value formatting ----------
def fmt_date(d: date, style: int) -> str:
    return [d.isoformat(), d.strftime("%d/%m/%Y"), f"{d.day} {MONTHS[d.month - 1]} {d.year}",
            f"{MONTHS[d.month - 1]} {d.day}, {d.year}", d.strftime("%d-%b-%Y")][style % 5]


def indian_group(n: float) -> str:
    s = f"{n:.2f}"
    whole, frac = s.split(".")
    if len(whole) > 3:
        head, tail = whole[:-3], whole[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        whole = ",".join(parts + [tail])
    return f"{whole}.{frac}"


def fmt_money(amount: float, currency: str, rng: random.Random) -> str:
    if currency == "INR":
        num = indian_group(amount) if rng.random() < 0.4 else f"{amount:,.2f}"
        return rng.choice([f"Rs. {num}", f"INR {num}", f"{num} INR"])
    num = f"{amount:,.2f}"
    if currency == "USD":
        return rng.choice([f"${num}", f"USD {num}", f"{num} USD"])
    return rng.choice([f"EUR {num}", f"{num} EUR"])


def ocr_noise(text: str, rng: random.Random) -> str:
    """Simulate OCR/typing errors on LABEL text only (values stay intact so ground truth is valid)."""
    subs = {"I": "l", "o": "0", "l": "1", "e": "c"}
    out = []
    for ch in text:
        if ch in subs and rng.random() < 0.08:
            out.append(subs[ch])
        else:
            out.append(ch)
    return "".join(out)


def render_pairs(pairs, style: str, rng: random.Random, noise: float) -> list:
    lines = []
    for label, value in pairs:
        if rng.random() < noise:
            label = ocr_noise(label, rng)
        if style == "colon":
            lines.append(f"{label}: {value}")
        elif style == "spaced":
            lines.append(f"{label:<26}{value}")
        else:  # stacked
            lines.append(label)
            lines.append(value)
    return lines


# ---------- document builders ----------
def _dates(rng, base_year=2026):
    d0 = date(base_year, 1, 1) + timedelta(days=rng.randint(0, 330))
    return d0


def make_invoice(rng, style, date_style, noise):
    vendor, customer = rng.sample(VENDORS, 1)[0], rng.choice(CUSTOMERS)
    currency = rng.choices(["INR", "USD", "EUR"], [0.6, 0.3, 0.1])[0]
    inv_date = _dates(rng)
    due = inv_date + timedelta(days=rng.choice([15, 30, 45]))
    items = [(rng.choice(ITEMS), rng.randint(1, 20), rng.choice([250, 480, 1250, 3200, 7800])) for _ in range(rng.randint(2, 4))]
    subtotal = float(sum(q * p for _, q, p in items))
    tax = round(subtotal * rng.choice([0.05, 0.12, 0.18]), 2)
    total = round(subtotal + tax, 2)
    number = f"INV-{rng.randint(1000, 9999)}"
    L = {k: rng.choice(v) for k, v in _labels("invoice").items()}
    pairs = [(L["invoice_number"], number), (L["invoice_date"], fmt_date(inv_date, date_style)),
             (L["due_date"], fmt_date(due, date_style)), (L["vendor_name"], vendor),
             (L["customer_name"], customer)]
    pairs2 = [(L["tax_amount"], fmt_money(tax, currency, rng)), (L["total_amount"], fmt_money(total, currency, rng))]
    body = [rng.choice(TITLES["invoice"]), ""]
    body += render_pairs(pairs, style, rng, noise)
    body += ["", "Description                     Qty   Unit Price"]
    body += [f"{n:<30}  {q:<4}  {p}" for n, q, p in items]
    body += ["", f"Subtotal  {subtotal:,.2f}"]
    body += render_pairs(pairs2, style, rng, noise)
    body += ["", rng.choice([
        "Payment terms: payment is due within the period shown above. Late payments attract interest of 1.5 percent per month.",
        "Please remit payment by bank transfer. Late payments may incur a penalty fee and suspension of services.",
    ]), "This invoice refers to purchase order " + f"PO-{rng.randint(1000, 9999)}" + " and the related delivery note.",
        "Thank you for your business."]
    truth = {"invoice_number": number, "invoice_date": inv_date.isoformat(), "due_date": due.isoformat(),
             "vendor_name": vendor, "customer_name": customer, "tax_amount": tax, "total_amount": total,
             "currency": currency}
    return "\n".join(body), truth


def make_po(rng, style, date_style, noise):
    buyer, supplier = rng.choice(CUSTOMERS), rng.choice(VENDORS)
    currency = rng.choices(["INR", "USD", "EUR"], [0.6, 0.3, 0.1])[0]
    odate = _dates(rng)
    ddate = odate + timedelta(days=rng.choice([7, 14, 21, 30]))
    items = [(rng.choice(ITEMS), rng.randint(5, 100), rng.choice([120, 340, 900, 2100])) for _ in range(rng.randint(2, 4))]
    total = float(sum(q * p for _, q, p in items))
    number = f"PO-{rng.randint(1000, 9999)}"
    L = {k: rng.choice(v) for k, v in _labels("purchase_order").items()}
    pairs = [(L["po_number"], number), (L["order_date"], fmt_date(odate, date_style)),
             (L["delivery_date"], fmt_date(ddate, date_style)), (L["buyer_name"], buyer),
             (L["supplier_name"], supplier)]
    body = [rng.choice(TITLES["purchase_order"]), ""]
    body += render_pairs(pairs, style, rng, noise)
    body += ["", "Item                            Qty   Unit Price"]
    body += [f"{n:<30}  {q:<4}  {p}" for n, q, p in items]
    body += [""] + render_pairs([(L["total_amount"], fmt_money(total, currency, rng))], style, rng, noise)
    body += ["", rng.choice([
        "Goods must be delivered to the main warehouse during working hours. Partial shipments require written approval.",
        "The supplier must confirm this order within two working days. Items that do not match the specification will be returned.",
    ]), "Invoices for this order must quote the purchase order number above."]
    truth = {"po_number": number, "order_date": odate.isoformat(), "delivery_date": ddate.isoformat(),
             "buyer_name": buyer, "supplier_name": supplier, "total_amount": total, "currency": currency}
    return "\n".join(body), truth


CLAUSES = [
    "The Service Provider shall deliver the services described in Schedule A with reasonable skill and care.",
    "The Client shall pay all undisputed invoices within thirty days of receipt.",
    "Each party shall keep the other party's confidential information secret and use it only for this Agreement.",
    "Either party may terminate this Agreement with thirty days written notice if the other party commits a material breach.",
    "Neither party is liable for delays caused by events beyond its reasonable control.",
]


def make_contract(rng, style, date_style, noise):
    provider, client = rng.choice(VENDORS), rng.choice(CUSTOMERS)
    currency = rng.choices(["INR", "USD", "EUR"], [0.5, 0.35, 0.15])[0]
    start = _dates(rng)
    end = start + timedelta(days=rng.choice([180, 365, 730]))
    value = float(rng.choice([250000, 480000, 1250000, 3600000]))
    number = f"AGR-{rng.randint(100, 999)}/{rng.choice([2025, 2026])}"
    law = rng.choice(LAWS)
    L = {k: rng.choice(v) for k, v in _labels("service_agreement").items()}
    pairs = [(L["contract_number"], number), (L["effective_date"], fmt_date(start, date_style)),
             (L["end_date"], fmt_date(end, date_style)), (L["provider_name"], provider),
             (L["client_name"], client), (L["contract_value"], fmt_money(value, currency, rng)),
             (L["governing_law"], law)]
    body = [rng.choice(TITLES["service_agreement"]), ""]
    body += render_pairs(pairs, style, rng, noise)
    body += ["", "Terms and conditions"]
    body += [f"{i + 1}. {c}" for i, c in enumerate(rng.sample(CLAUSES, 4))]
    body += ["Invoices will be raised monthly and each invoice shall quote the agreement number."]
    truth = {"contract_number": number, "effective_date": start.isoformat(), "end_date": end.isoformat(),
             "provider_name": provider, "client_name": client, "contract_value": value,
             "currency": currency, "governing_law": law}
    return "\n".join(body), truth


OTHER_TEXTS = [
    "Meeting notes\n\nAttendees: Arun, Priya, Karthik\nDate: next Monday\nWe discussed the website redesign and agreed that the team will review the mock-ups by Friday. Action items were assigned to everyone. The next meeting is planned after the festival break.",
    "Dear Hiring Manager,\n\nI am writing to apply for the junior developer position advertised on your careers page. I am a final-year student with experience in Python and web development. I would welcome the opportunity to discuss how I can contribute to your team.\n\nSincerely,\nA. Student",
    "Weekly newsletter\n\nThis week we launched a new help centre, fixed several bugs and published a guide on getting started. Our community call is on Thursday. Thank you to everyone who sent feedback about the mobile app.",
    "Notice to residents\n\nThe water supply will be interrupted on Saturday between 9 am and 1 pm for tank cleaning. Please store enough water in advance. We apologise for the inconvenience.",
    "Travel itinerary\n\nFlight to Bengaluru departs at 7:15. Hotel check-in after 2 pm. Dinner reservation for four people at the rooftop restaurant. Remember to carry your identity card.",
    "Recipe: vegetable pulao\n\nWash the rice and soak for twenty minutes. Fry onions, add chopped vegetables and spices, then add rice and water. Cook until the rice is soft. Serve hot with raita.",
]


def make_other(rng):
    t = rng.choice(OTHER_TEXTS)
    # light variation so the class is not 6 identical strings
    extra = rng.choice(["", "\nPlease reply at your convenience.", "\nThis message was sent automatically.", "\nRegards, Team"])
    return t + extra, {}


MAKERS = {"invoice": make_invoice, "purchase_order": make_po, "service_agreement": make_contract}


def generate(doc_type: str, rng: random.Random, style: str = None, date_style: int = None,
             noise: float = None, heldout: bool = False):
    """Return (text, ground_truth, meta). heldout=True uses label variants unseen by the extractor lexicon."""
    _HELDOUT["on"] = heldout
    if doc_type == "other":
        _HELDOUT["on"] = False
        text, truth = make_other(rng)
        return text, truth, {"style": "n/a"}
    style = style or rng.choice(["colon", "spaced"])
    date_style = rng.randrange(5) if date_style is None else date_style
    noise = 0.0 if noise is None else noise
    text, truth = MAKERS[doc_type](rng, style, date_style, noise)
    _HELDOUT["on"] = False
    return text, truth, {"style": style, "date_style": date_style, "noise": noise, "heldout_labels": heldout}


def training_corpus(n_per_class: int = 150, seed: int = 1):
    """Corpus for the document-type classifier (mixed layouts, light noise)."""
    rng = random.Random(seed)
    texts, labels = [], []
    for dt in ["invoice", "purchase_order", "service_agreement", "other"]:
        for _ in range(n_per_class):
            text, _, _ = generate(dt, rng, style=rng.choice(["colon", "spaced", "stacked"]),
                                  noise=rng.choice([0.0, 0.1]))
            texts.append(text)
            labels.append(dt)
    return texts, labels
