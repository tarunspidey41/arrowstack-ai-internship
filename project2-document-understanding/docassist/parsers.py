"""Document parsers: .txt, text-based .pdf, and (optionally) images via OCR."""
import io
from pathlib import Path

from . import config


class UnsupportedDocument(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code, self.message = code, message


def ocr_available() -> bool:
    try:
        import pytesseract  # noqa: F401
        from PIL import Image  # noqa: F401
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def parse_bytes(data: bytes, filename: str):
    """Return (text, meta). Raises UnsupportedDocument for bad input."""
    if not data:
        raise UnsupportedDocument("empty_file", "The file is empty.")
    if len(data) > config.MAX_FILE_MB * 1024 * 1024:
        raise UnsupportedDocument("too_large", f"File exceeds {config.MAX_FILE_MB} MB.")
    ext = Path(filename or "").suffix.lower()
    if ext not in config.ALLOWED_EXTENSIONS:
        raise UnsupportedDocument("unsupported_type",
                                  f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(config.ALLOWED_EXTENSIONS))}")
    meta = {"parser": None, "pages": 1, "warnings": []}
    if ext == ".txt":
        meta["parser"] = "text"
        text = data.decode("utf-8", errors="replace")
    elif ext == ".pdf":
        meta["parser"] = "pypdf"
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(data))
            meta["pages"] = len(reader.pages)
            text = "\n".join((p.extract_text() or "") for p in reader.pages)
        except Exception as e:  # corrupt / encrypted pdf
            raise UnsupportedDocument("unreadable_pdf", f"Could not read PDF: {type(e).__name__}")
        if len(text.strip()) < config.MIN_TEXT_CHARS:
            meta["warnings"].append("PDF has almost no text layer - it may be a scan. OCR is required.")
    else:  # image
        meta["parser"] = "ocr"
        if not ocr_available():
            raise UnsupportedDocument("ocr_unavailable",
                                      "Image uploaded but the OCR engine (Tesseract + pytesseract) is not installed.")
        import pytesseract
        from PIL import Image
        text = pytesseract.image_to_string(Image.open(io.BytesIO(data)))
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\t", "    ")
    return text, meta
