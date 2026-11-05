"""Ports of UtilitiesTest (JUnit) plus T06 edge cases.

Java: java/src/test/java/org/mitre/synthea/helpers/UtilitiesTest.java
"""

from __future__ import annotations

import math
import re
from datetime import date
from types import SimpleNamespace

import pytest

from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.helpers.utilities import Utilities

UID_REGEX = r"[0-2](\.(0|[1-9][0-9]*))+"


def test_convert_time() -> None:
    # JUnit testConvertTime used Date(104, 0, 1) in the JVM default zone;
    # the parity JVM is UTC, so use the equivalent UTC timestamps.
    year = Utilities.convert_calendar_years_to_time(2005)
    jan_1_2004 = Utilities.local_date_to_timestamp(date(2004, 1, 1))
    jan_1_2006 = Utilities.local_date_to_timestamp(date(2006, 1, 1))
    assert jan_1_2004 <= year
    assert jan_1_2006 > year


def test_years() -> None:
    gap = 75
    time = Utilities.local_date_to_timestamp(date(2020, 2, 1))
    year = Utilities.get_year(time)
    earlier_time = time - Utilities.convert_time("years", gap)
    earlier_year = Utilities.get_year(earlier_time)
    assert gap == year - earlier_year


def test_fractional_durations() -> None:
    assert Utilities.convert_time("seconds", 0.5) == 500
    assert Utilities.convert_time("minutes", 0.5) == Utilities.convert_time("seconds", 30)
    assert Utilities.convert_time("hours", 0.5) == Utilities.convert_time("minutes", 30)
    assert Utilities.convert_time("days", 0.5) == Utilities.convert_time("hours", 12)
    assert Utilities.convert_time("weeks", 0.5) == Utilities.convert_time("days", 3)
    assert Utilities.convert_time("months", 0.5) == Utilities.convert_time("days", 15)
    assert Utilities.convert_time("years", 0.5) == Utilities.convert_time("weeks", 26)


def test_get_year() -> None:
    assert Utilities.get_year(0) == 1970
    assert Utilities.get_year(1504783221000) == 2017
    assert Utilities.get_year(1234567890000) == 2009


def test_compare_objects() -> None:
    assert Utilities.compare("foo", "foobar", "!=") is True


def test_compare_doubles() -> None:
    lhs, rhs = 1.2, 1.8
    assert Utilities.compare(lhs, rhs, "<") is True
    assert Utilities.compare(lhs, rhs, "<=") is True
    assert Utilities.compare(lhs, lhs, "==") is True
    assert Utilities.compare(lhs, rhs, "==") is False
    assert Utilities.compare(lhs, rhs, ">") is False
    assert Utilities.compare(lhs, rhs, ">=") is False
    assert Utilities.compare(lhs, rhs, "!=") is True
    assert Utilities.compare(lhs, rhs, "is not nil") is True
    assert Utilities.compare(rhs, lhs, "is not nil") is True
    assert Utilities.compare(lhs, rhs, "is nil") is False
    assert Utilities.compare(rhs, lhs, "is nil") is False
    # Object-overload semantics for a null lhs (see T06 porting notes).
    assert Utilities.compare(None, None, "is nil") is True
    assert Utilities.compare(None, None, "is not nil") is False
    assert Utilities.compare(None, None, "~=") is False


def test_compare_booleans() -> None:
    lhs, rhs = False, True
    assert Utilities.compare(lhs, rhs, "<") is True
    assert Utilities.compare(lhs, rhs, "<=") is True
    assert Utilities.compare(lhs, rhs, ">") is True
    assert Utilities.compare(lhs, rhs, ">=") is True
    assert Utilities.compare(lhs, rhs, "!=") is True
    assert Utilities.compare(lhs, rhs, "is nil") is False
    assert Utilities.compare(lhs, rhs, "is not nil") is True
    assert Utilities.compare(None, None, "is nil") is True
    assert Utilities.compare(None, None, "is not nil") is False
    assert Utilities.compare(None, None, "~=") is False


def test_compare_strings() -> None:
    lhs, rhs = "A", "Z"
    assert Utilities.compare(lhs, rhs, "<") is True
    assert Utilities.compare(lhs, rhs, "<=") is True
    assert Utilities.compare(lhs, lhs, "==") is True
    assert Utilities.compare(lhs, rhs, "==") is False
    assert Utilities.compare(lhs, rhs, ">") is False
    assert Utilities.compare(lhs, rhs, ">=") is False
    assert Utilities.compare(lhs, rhs, "!=") is True
    assert Utilities.compare(lhs, rhs, "is not nil") is True
    assert Utilities.compare(rhs, lhs, "is not nil") is True
    assert Utilities.compare(None, None, "is nil") is True
    assert Utilities.compare(None, None, "~=") is False


def test_compare_different_types_throws() -> None:
    with pytest.raises(RuntimeError):
        Utilities.compare(False, "Z", "==")


def test_convert_time_fortnights_throws() -> None:
    with pytest.raises(RuntimeError):
        Utilities.convert_time("fortnights", 1)


def test_json_primitive_booleans() -> None:
    assert Utilities.primitive(True) is True
    assert Utilities.primitive(False) is False


def test_json_primitive_strings() -> None:
    assert Utilities.primitive("Foo") == "Foo"


def test_json_primitive_doubles() -> None:
    for d in (1.2, 1.5, 1.501, 1.7):
        assert Utilities.primitive(d) == d


def test_json_primitive_integers() -> None:
    for d in (-1, 0, 1):
        result = Utilities.primitive(float(d))
        assert result == d
        assert isinstance(result, int)


def test_str_to_object() -> None:
    assert Utilities.str_to_object("Boolean", "true") is True
    assert Utilities.str_to_object("boolean", "true") is True
    assert Utilities.str_to_object("Byte", "2") == 2
    assert Utilities.str_to_object("byte", "2") == 2
    assert Utilities.str_to_object("Short", "3") == 3
    assert Utilities.str_to_object("short", "3") == 3
    assert Utilities.str_to_object("Integer", "5") == 5
    assert Utilities.str_to_object("int", "5") == 5
    assert Utilities.str_to_object("Long", "7") == 7
    assert Utilities.str_to_object("long", "7") == 7
    assert Utilities.str_to_object("Float", "2.5") == 2.5
    assert Utilities.str_to_object("float", "2.5") == 2.5
    assert Utilities.str_to_object("Double", "4.8") == 4.8
    assert Utilities.str_to_object("double", "4.8") == 4.8
    # Python type objects map to Boolean/Integer/Double.
    assert Utilities.str_to_object(bool, "true") is True
    assert Utilities.str_to_object(int, "5") == 5
    assert Utilities.str_to_object(float, "4.8") == 4.8


def test_invalid_str_to_object() -> None:
    with pytest.raises(ValueError):
        Utilities.str_to_object("Date", "oops")


def test_dicom_uid() -> None:
    # The JUnit test uses a Person (a RandomNumberGenerator); the port's
    # DefaultRandomNumberGenerator is the same RNG a Person delegates to.
    uid = Utilities.random_dicom_uid(DefaultRandomNumberGenerator(0), 0, 0, 0)
    assert re.fullmatch(UID_REGEX, uid)
    uid = Utilities.random_dicom_uid(DefaultRandomNumberGenerator(0), -1, -1, -1)
    assert re.fullmatch(UID_REGEX, uid)
    uid = Utilities.random_dicom_uid(DefaultRandomNumberGenerator(0), 1, 2, 3)
    assert re.fullmatch(UID_REGEX, uid)
    uid = Utilities.random_dicom_uid(
        DefaultRandomNumberGenerator(0), 9223372036854775807, 2147483647, 2147483647
    )
    assert re.fullmatch(UID_REGEX, uid)


def test_parse_date_range() -> None:
    start = Utilities.local_date_to_timestamp(date(2020, 9, 5))
    end = Utilities.local_date_to_timestamp(date(2021, 8, 4)) - 1
    result = Utilities.parse_date_range("2020-09-05-2021-08-03")
    assert result.minimum == start
    assert result.maximum == end
    result = Utilities.parse_date_range("1599264000000-1628035199999")
    assert result.minimum == start
    assert result.maximum == end
    with pytest.raises(ValueError):
        Utilities.parse_date_range("silliness")


def test_local_date_to_timestamp_roundtrip() -> None:
    for day_of_year in range(1, 367):
        orig = date(2020, 1, 1).fromordinal(date(2020, 1, 1).toordinal() + day_of_year - 1)
        timestamp = Utilities.local_date_to_timestamp(orig)
        assert Utilities.timestamp_to_local_date(timestamp) == orig
    one_day = Utilities.convert_time("days", 1)
    for day_of_year in range(366):
        orig_timestamp = 1577836800000 + day_of_year * one_day
        local = Utilities.timestamp_to_local_date(orig_timestamp)
        assert Utilities.local_date_to_timestamp(local) == orig_timestamp


# ------------------------------------------------------------- T06 extras


def test_convert_time_saturation_and_wrap() -> None:
    # TimeUnit.toMillis saturates.
    assert Utilities.convert_time("days", 9223372036854775807) == 9223372036854775807
    assert Utilities.convert_time("hours", -9223372036854775808) == -9223372036854775808
    # The long "years" overload multiplies by (long) 365.25 == 365 first.
    assert Utilities.convert_time("years", 1) == 365 * 86400000
    # The double "years" overload uses 365.25 before truncating.
    assert Utilities.convert_time("years", 2.0) == 730 * 86400000


def test_calendar_cutover() -> None:
    # GregorianCalendar cutover: Julian 1582-10-04 is followed by
    # Gregorian 1582-10-15, consecutive epoch days.
    julian_last = -141428 * 86400000
    greg_first = -141427 * 86400000
    assert Utilities.get_year(julian_last) == 1582
    assert Utilities.get_month(julian_last) == 10
    assert Utilities.timestamp_to_local_date(greg_first) == date(1582, 10, 15)
    assert Utilities.get_year(greg_first) == 1582
    # LocalDate is proleptic: 1582-10-10 exists there but not in Calendar.
    assert Utilities.local_date_to_timestamp(date(1582, 10, 10)) == -141432 * 86400000


def test_get_year_bc() -> None:
    # Calendar.YEAR has no year zero: astronomical year 0 reads back as
    # 1 (BC), astronomical -5 as 6 (BC). JDK-verified values.
    assert Utilities.convert_calendar_years_to_time(0) == -62167392000000
    assert Utilities.get_year(-62167392000000) == 1
    assert Utilities.get_year(-62325158400000) == 6


def test_anniversary_leap_day() -> None:
    feb29 = Utilities.local_date_to_timestamp(date(2020, 2, 29))
    assert Utilities.timestamp_to_local_date(Utilities.get_anniversary(feb29, 1)) == date(
        2021, 3, 1
    )
    assert Utilities.timestamp_to_local_date(Utilities.get_anniversary(feb29, 4)) == date(
        2024, 2, 29
    )


def test_compare_codes() -> None:
    a = SimpleNamespace(system="SNOMED", code="123", display="A")
    b = SimpleNamespace(system="SNOMED", code="123", display="B")
    c = SimpleNamespace(system="SNOMED", code="124", display="A")
    # Code.equals compares system and code only, not display.
    assert Utilities.compare(a, b, "==") is True
    assert Utilities.compare(a, c, "!=") is True
    assert Utilities.compare(a, c, "<") is False  # unsupported for Code


def test_primitive_edges() -> None:
    assert Utilities.primitive(2147483648.0) == 2147483647  # (int) cast saturates
    assert Utilities.primitive(-2147483649.0) == -2147483648
    result = Utilities.primitive(math.nan)
    assert isinstance(result, float) and math.isnan(result)
    with pytest.raises(TypeError):
        Utilities.primitive(None)


def test_read_resource_and_bom(tmp_path: object, monkeypatch: pytest.MonkeyPatch) -> None:
    from pathlib import Path

    root = Path(str(tmp_path))
    (root / "bom.txt").write_bytes(b"\xef\xbb\xbfhello")
    (root / "plain.txt").write_text("world", encoding="utf-8")
    monkeypatch.setenv("SYNTHEA_RESOURCES_DIR", str(root))
    assert Utilities.read_resource("bom.txt") == "\ufeffhello"
    assert Utilities.read_resource_and_strip_bom("bom.txt") == "hello"
    assert Utilities.read_resource("plain.txt") == "world"
    with pytest.raises(ValueError):
        Utilities.read_resource("missing.txt")
    assert Utilities.read_resource_or_path("plain.txt") == "world"
    free = root / "elsewhere.txt"
    free.write_text("free", encoding="utf-8")
    assert Utilities.read_resource_or_path(str(free)) == "free"
    with pytest.raises(ValueError):
        Utilities.read_resource(str(free))


def test_synthea_version(tmp_path: object, monkeypatch: pytest.MonkeyPatch) -> None:
    from pathlib import Path

    # No version.txt in the checkout (it is a gitignored build artifact).
    assert Utilities.SYNTHEA_VERSION == "synthea-java"
    root = Path(str(tmp_path))
    (root / "version.txt").write_text("v9-test", encoding="utf-8")
    monkeypatch.setenv("SYNTHEA_RESOURCES_DIR", str(root))
    assert Utilities.get_synthea_version() == "v9-test"
    (root / "version.txt").write_text("", encoding="utf-8")
    assert Utilities.get_synthea_version() == "synthea-java"


def test_clean_map() -> None:
    data: dict[object, object] = {"a": 1, "b": None, "c": "x", "d": None}
    result = Utilities.clean_map(data)
    assert result is data
    assert data == {"a": 1, "c": "x"}


def test_walk_all_modules(tmp_path: object) -> None:
    from pathlib import Path

    root = Path(str(tmp_path))
    (root / "sub").mkdir()
    (root / "a.json").write_text("{}")
    (root / "b.txt").write_text("x")
    (root / "sub" / "c.json").write_text("{}")
    found: list[Path] = []
    Utilities.walk_all_modules(root, found.append)
    assert sorted(p.relative_to(root).as_posix() for p in found) == ["a.json", "sub/c.json"]
    with pytest.raises(NotImplementedError):
        Utilities.walk_all_modules(lambda a, b: None)


def test_convert_risk_to_timestep() -> None:
    assert Utilities.convert_risk_to_timestep(0.0, 1000.0, 500.0) == 0.0
    assert Utilities.convert_risk_to_timestep(1.0, 1000.0, 500.0) == 1.0
    # Default timestep from Config (generate.timestep = 604800000).
    assert Utilities.convert_risk_to_timestep(0.5, 604800000.0) == pytest.approx(0.5)
