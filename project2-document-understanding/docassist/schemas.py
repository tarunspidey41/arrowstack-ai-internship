"""Field specifications (domain lexicon), JSON Schemas and business rules."""
FIELD_SPECS = {
    "invoice": {
        "invoice_number": {"type": "id", "required": True,
                           "synonyms": ["invoice number", "invoice no", "invoice #", "inv no", "bill no", "bill number"]},
        "invoice_date": {"type": "date", "required": True,
                         "synonyms": ["invoice date", "date of issue", "issued on", "date", "issue date"]},
        "due_date": {"type": "date", "required": True,
                     "synonyms": ["due date", "payment due", "pay by", "due on"]},
        "vendor_name": {"type": "party", "required": True,
                        "synonyms": ["vendor", "from", "billed by", "supplier", "vendor name"]},
        "customer_name": {"type": "party", "required": True,
                          "synonyms": ["bill to", "customer", "billed to", "client", "customer name"]},
        "tax_amount": {"type": "money", "required": False,
                       "synonyms": ["tax", "gst", "vat", "tax amount", "total tax"]},
        "total_amount": {"type": "money", "required": True,
                         "synonyms": ["total", "total amount", "amount due", "grand total", "total payable", "invoice total"]},
    },
    "purchase_order": {
        "po_number": {"type": "id", "required": True,
                      "synonyms": ["po number", "po no", "purchase order no", "purchase order number", "order #", "order number"]},
        "order_date": {"type": "date", "required": True,
                       "synonyms": ["order date", "po date", "date ordered", "date of order"]},
        "delivery_date": {"type": "date", "required": True,
                          "synonyms": ["delivery date", "deliver by", "expected delivery", "date of delivery", "required by"]},
        "buyer_name": {"type": "party", "required": True,
                       "synonyms": ["buyer", "ordered by", "bill to", "buyer name", "purchaser"]},
        "supplier_name": {"type": "party", "required": True,
                          "synonyms": ["supplier", "vendor", "ship from", "supplier name", "vendor name"]},
        "total_amount": {"type": "money", "required": True,
                         "synonyms": ["total", "total amount", "order total", "grand total", "total order value", "order value"]},
    },
    "service_agreement": {
        "contract_number": {"type": "id", "required": True,
                            "synonyms": ["agreement no", "contract no", "reference", "agreement number", "contract number"]},
        "effective_date": {"type": "date", "required": True,
                           "synonyms": ["effective date", "commencement date", "start date", "date of commencement"]},
        "end_date": {"type": "date", "required": True,
                     "synonyms": ["end date", "expiry date", "termination date", "date of expiry"]},
        "provider_name": {"type": "party", "required": True,
                          "synonyms": ["service provider", "provider", "party a", "contractor", "provider name"]},
        "client_name": {"type": "party", "required": True,
                        "synonyms": ["client", "customer", "party b", "client name", "customer name"]},
        "contract_value": {"type": "money", "required": True,
                           "synonyms": ["contract value", "total fees", "total consideration", "contract amount", "total contract value"]},
        "governing_law": {"type": "text", "required": False,
                          "synonyms": ["governing law", "jurisdiction", "applicable law", "governing jurisdiction"]},
    },
}

DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"


def json_schema(doc_type: str) -> dict:
    """JSON Schema used to validate the extracted record."""
    props = {"doc_type": {"const": doc_type}}
    required = ["doc_type"]
    has_money = False
    for name, spec in FIELD_SPECS[doc_type].items():
        t = spec["type"]
        if t == "date":
            props[name] = {"type": "string", "pattern": DATE_PATTERN}
        elif t == "money":
            props[name] = {"type": "number", "minimum": 0}
            has_money = True
        else:
            props[name] = {"type": "string", "minLength": 2, "maxLength": 120}
        if spec["required"]:
            required.append(name)
    if has_money:
        props["currency"] = {"enum": ["INR", "USD", "EUR"]}
    return {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object",
            "properties": props, "required": required, "additionalProperties": False}


# (earlier_field, later_field, description)
DATE_ORDER_RULES = {
    "invoice": [("invoice_date", "due_date", "due date must not be before invoice date")],
    "purchase_order": [("order_date", "delivery_date", "delivery date must not be before order date")],
    "service_agreement": [("effective_date", "end_date", "end date must be after effective date")],
}


def business_rules(doc_type: str, record: dict) -> list:
    warnings = []
    for a, b, msg in DATE_ORDER_RULES.get(doc_type, []):
        if a in record and b in record and record[b] < record[a]:
            warnings.append(f"Rule violated: {msg} ({record[a]} / {record[b]})")
    if doc_type == "invoice" and "tax_amount" in record and "total_amount" in record:
        if record["tax_amount"] > record["total_amount"]:
            warnings.append("Rule violated: tax amount is larger than total amount")
    return warnings
