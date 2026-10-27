"""Input validation and PII masking (privacy guardrail)."""
import re
from . import config

_CARD = re.compile(r"\b(?:\d[ -]?){13,19}\b")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE = re.compile(r"(?<!\w)(?:\+?\d{1,3}[\s-]?)?(?:\d[\s-]?){9,11}\d(?!\w)")


class InvalidTicket(ValueError):
    """Raised when a ticket fails validation."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def validate(text) -> str:
    """Return cleaned text or raise InvalidTicket."""
    if text is None or not isinstance(text, str):
        raise InvalidTicket("not_text", "Ticket must be a text string.")
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        raise InvalidTicket("empty", "Ticket is empty.")
    if len(cleaned) > config.MAX_CHARS:
        raise InvalidTicket("too_long", f"Ticket exceeds {config.MAX_CHARS} characters.")
    if len(cleaned) < config.MIN_CHARS or len(cleaned.split()) < config.MIN_WORDS:
        raise InvalidTicket(
            "too_short",
            f"Ticket too short (need at least {config.MIN_WORDS} words / {config.MIN_CHARS} characters).",
        )
    if sum(c.isalpha() for c in cleaned) < 0.4 * len(cleaned):
        raise InvalidTicket("not_natural_text", "Ticket does not look like natural-language text.")
    return cleaned


def mask_pii(text: str) -> str:
    """Mask card numbers, emails and phone numbers before logging/storing."""
    text = _CARD.sub("[CARD]", text)
    text = _EMAIL.sub("[EMAIL]", text)
    text = _PHONE.sub("[PHONE]", text)
    return text
