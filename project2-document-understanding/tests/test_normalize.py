import pytest
from docassist.normalize import parse_date, parse_money


@pytest.mark.parametrize("raw,iso", [
    ("2026-03-14", "2026-03-14"), ("14/03/2026", "2026-03-14"), ("14 March 2026", "2026-03-14"),
    ("March 14, 2026", "2026-03-14"), ("14-Mar-2026", "2026-03-14"), ("1st Apr 2026", "2026-04-01"),
])
def test_date_formats(raw, iso):
    assert parse_date(raw)[0] == iso


def test_invalid_dates():
    assert parse_date("31/02/2026")[0] is None
    assert parse_date("hello")[0] is None
    assert parse_date("")[0] is None


def test_ambiguous_numeric_date_flagged():
    assert parse_date("05/03/2026") == ("2026-03-05", True)
    assert parse_date("25/03/2026")[1] is False


@pytest.mark.parametrize("raw,amt,cur", [
    ("Rs. 1,23,456.00", 123456.0, "INR"), ("$1,234.50", 1234.5, "USD"), ("EUR 99.00", 99.0, "EUR"),
    ("12,400.00 INR", 12400.0, "INR"), ("500", 500.0, None),
])
def test_money(raw, amt, cur):
    assert parse_money(raw) == (amt, cur)


def test_money_invalid():
    assert parse_money("none")[0] is None
