"""Unit tests for pythonbeid.parser — no hardware required."""
import pytest
from datetime import datetime

from pythonbeid.parser import parse_tlv, parse_french_date


# ── Helpers ────────────────────────────────────────────────────────────────

def _tlv(*fields: str) -> list[int]:
    """Build a minimal TLV buffer from a sequence of string values.

    Each field is encoded as [tag=0x01, length, utf-8 bytes].
    """
    buf: list[int] = []
    for i, text in enumerate(fields, start=1):
        raw = text.encode("utf-8")
        buf += [i, len(raw)] + list(raw)
    return buf


# ── parse_tlv ─────────────────────────────────────────────────────────────

class TestParseTlv:
    def test_basic(self):
        data = _tlv("hello", "world", "foo")
        assert parse_tlv(data, 3) == ["hello", "world", "foo"]

    def test_stops_at_num_fields(self):
        data = _tlv("a", "b", "c", "d")
        result = parse_tlv(data, 2)
        assert result == ["a", "b"]
        assert len(result) == 2

    def test_unicode(self):
        data = _tlv("Ébène", "Müller")
        assert parse_tlv(data, 2) == ["Ébène", "Müller"]

    def test_empty_field(self):
        # A field with length 0 should produce an empty string.
        buf = [0x01, 0x00]  # tag=1, len=0
        assert parse_tlv(buf, 1) == [""]

    def test_truncated_buffer_no_crash(self):
        # Buffer is cut in the middle of a value — must not raise IndexError.
        buf = [0x01, 0x05, 0x41, 0x42]  # tag=1, length=5, only 2 bytes of value
        result = parse_tlv(buf, 1)
        assert result == []

    def test_buffer_too_short_for_tag_length(self):
        # Only one byte available — cannot read tag + length.
        result = parse_tlv([0x01], 1)
        assert result == []

    def test_empty_buffer(self):
        assert parse_tlv([], 5) == []

    def test_invalid_utf8_becomes_empty_string(self):
        # 0xFF is not valid UTF-8.
        buf = [0x01, 0x02, 0xFF, 0xFE]
        result = parse_tlv(buf, 1)
        assert result == [""]


# ── parse_french_date ─────────────────────────────────────────────────────

class TestParseFrenchDate:
    @pytest.mark.parametrize("abbr,expected_month", [
        ("JANV", 1), ("JAN", 1),
        ("FEVR", 2), ("FEV", 2),
        ("MARS", 3), ("MAR", 3),
        ("AVRI", 4), ("AVR", 4),
        ("MAI",  5),
        ("JUIN", 6),
        ("JUIL", 7),
        ("AOUT", 8), ("AOU", 8),
        ("SEPT", 9), ("SEP", 9),
        ("OCTO", 10), ("OCT", 10),
        ("NOVE", 11), ("NOV", 11),
        ("DECE", 12), ("DEC", 12),
    ])
    def test_all_month_abbreviations(self, abbr: str, expected_month: int):
        result = parse_french_date(f"15 {abbr} 2000")
        assert result == datetime(2000, expected_month, 15)

    def test_lowercase_accepted(self):
        # Abbreviations should be case-insensitive.
        assert parse_french_date("01 janv 1990") == datetime(1990, 1, 1)

    def test_unknown_month_falls_back_to_january(self):
        result = parse_french_date("10 UNKN 2005")
        assert result.month == 1
        assert result.day == 10
        assert result.year == 2005

    def test_wrong_format_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_french_date("not-a-date")

    def test_returns_datetime(self):
        result = parse_french_date("03 MAR 1985")
        assert isinstance(result, datetime)
        assert result == datetime(1985, 3, 3)
