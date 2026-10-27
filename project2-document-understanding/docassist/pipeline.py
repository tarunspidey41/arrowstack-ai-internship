"""End-to-end workflow: parse -> classify -> extract -> normalise -> validate -> summarise -> review flags."""
import uuid
from datetime import datetime, timezone

from jsonschema import Draft7Validator

from . import classifier, config, extractor, entities, summarizer
from .parsers import parse_bytes, UnsupportedDocument
from .schemas import FIELD_SPECS, json_schema, business_rules


class DocumentAnalyzer:
    def __init__(self, clf=None):
        self.clf = clf or classifier.load()

    def analyze_bytes(self, data: bytes, filename: str) -> dict:
        text, meta = parse_bytes(data, filename)
        return self.analyze_text(text, filename=filename, meta=meta)

    def analyze_text(self, text: str, filename: str = "pasted_text", meta: dict = None) -> dict:
        meta = meta or {"parser": "text", "pages": 1, "warnings": []}
        reasons = list(meta.get("warnings", []))
        if len(text.strip()) < config.MIN_TEXT_CHARS:
            return self._result(filename, "unknown", 0.0, {}, {}, text, meta,
                                {"schema_valid": False, "errors": ["Document has too little text to analyse."],
                                 "rule_warnings": [], "missing_required": []},
                                reasons + ["Too little text - possibly scanned or empty document"])

        doc_type, conf = classifier.predict(self.clf, text)
        if conf < config.DOC_TYPE_CONFIDENCE_THRESHOLD:
            reasons.append(f"low document-type confidence ({conf:.2f})")
            doc_type_final = "unknown"
        else:
            doc_type_final = doc_type
        if doc_type_final in ("other", "unknown"):
            reasons.append("document is not a supported business document type")
            validation = {"schema_valid": True, "errors": [], "rule_warnings": [], "missing_required": []}
            return self._result(filename, doc_type_final, conf, {}, {}, text, meta, validation, reasons)

        fields = extractor.extract(text, doc_type_final)
        record = {"doc_type": doc_type_final}
        for name, f in fields.items():
            record[name] = f["value"]
            if f.get("currency"):
                record["currency"] = f["currency"]
        validation = self._validate(doc_type_final, record)
        # reasons for human review
        for name in validation["missing_required"]:
            reasons.append(f"required field not found: {name}")
        reasons += validation["rule_warnings"]
        for name, f in fields.items():
            if f["confidence"] < config.FIELD_CONFIDENCE_THRESHOLD:
                why = "ambiguous day/month order" if f["ambiguous_date"] else "weak label match"
                reasons.append(f"low confidence for {name} ({f['confidence']:.2f}, {why})")
        return self._result(filename, doc_type_final, conf, fields, record, text, meta, validation, reasons)

    def _validate(self, doc_type: str, record: dict) -> dict:
        errors = []
        for e in sorted(Draft7Validator(json_schema(doc_type)).iter_errors(record), key=lambda x: list(x.path)):
            if e.validator == "required":
                continue  # reported as missing_required
            errors.append(f"{'.'.join(map(str, e.path)) or 'record'}: {e.message}")
        missing = [n for n, s in FIELD_SPECS[doc_type].items() if s["required"] and n not in record]
        return {"schema_valid": not errors and not missing, "errors": errors,
                "rule_warnings": business_rules(doc_type, record), "missing_required": missing}

    def _result(self, filename, doc_type, conf, fields, record, text, meta, validation, reasons):
        summary = summarizer.summarize(text, doc_type, record) if doc_type not in ("unknown",) else \
            {"headline": "Document could not be classified.", "key_points": summarizer.key_points(text)}
        return {
            "document_id": uuid.uuid4().hex[:8],
            "filename": filename,
            "doc_type": doc_type,
            "doc_type_confidence": round(conf, 3),
            "fields": fields,
            "record": record,
            "entities": entities.find_entities(text),
            "summary": summary,
            "validation": validation,
            "needs_human_review": bool(reasons),
            "review_reasons": reasons,
            "parser": meta.get("parser"),
            "pages": meta.get("pages"),
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
