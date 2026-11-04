"""Unit tests for javacompat.numbers, from documented JDK behaviour.

Every expected value here is a spec example from the JDK documentation or the
task issue — none is copied from generated goldens (the parity tests do that).
"""

from __future__ import annotations

import math

import pytest

from synthea.javacompat.numbers import (
    d2i,
    d2l,
    double_to_string,
    float_to_string,
    floor_div,
    floor_mod,
    idiv,
    irem,
    math_round,
    math_round_float,
    parse_boolean,
    parse_double,
    parse_int,
    parse_long,
    to_int32,
    to_int64,
)


def test_to_int32_wraps() -> None:
    assert to_int32(2**31) == -(2**31)
    assert to_int32(2**31 - 1) == 2**31 - 1
    assert to_int32(-(2**31) - 1) == 2**31 - 1
    assert to_int32(0) == 0


def test_to_int64_wraps() -> None:
    assert to_int64(2**63) == -(2**63)
    assert to_int64(-(2**63)) == -(2**63)
    assert to_int64(2**64 + 5) == 5


def test_idiv_truncates_toward_zero() -> None:
    assert idiv(7, 2) == 3
    assert idiv(-7, 2) == -3
    assert idiv(7, -2) == -3
    assert idiv(-7, -2) == 3
    with pytest.raises(ZeroDivisionError):
        idiv(1, 0)


def test_irem_sign_of_dividend() -> None:
    assert irem(7, 2) == 1
    assert irem(-7, 2) == -1
    assert irem(7, -2) == 1


def test_floor_div_mod() -> None:
    # Java Math.floorDiv / floorMod javadoc examples
    assert floor_div(-7, 2) == -4
    assert floor_mod(-7, 2) == 1
    assert floor_div(7, -2) == -4
    assert floor_mod(7, -2) == -1
    assert floor_div(6, 3) == 2
    assert floor_mod(6, 3) == 0


def test_d2i_saturates_and_truncates() -> None:
    assert d2i(3.99) == 3
    assert d2i(-3.99) == -3
    assert d2i(2147483647.9) == 2147483647
    assert d2i(1e30) == 2147483647
    assert d2i(-1e30) == -2147483648
    assert d2i(float("nan")) == 0
    assert d2i(float("inf")) == 2147483647


def test_d2l_saturates() -> None:
    assert d2l(1e30) == 9223372036854775807
    assert d2l(-1e30) == -9223372036854775808
    assert d2l(float("nan")) == 0
    assert d2l(-0.5) == 0


def test_math_round() -> None:
    # Math.round javadoc: floor(x + 0.5); ties go toward positive infinity
    assert math_round(2.5) == 3
    assert math_round(-2.5) == -2
    assert math_round(-0.5) == 0
    assert math_round(0.4) == 0
    assert math_round(float("nan")) == 0
    assert math_round(1e30) == 9223372036854775807
    assert math_round(-1e30) == -9223372036854775808


def test_math_round_float() -> None:
    assert math_round_float(2.5) == 3
    assert math_round_float(-2.5) == -2
    assert math_round_float(1e30) == 2147483647
    assert math_round_float(float("nan")) == 0


def test_parse_int() -> None:
    assert parse_int("42") == 42
    assert parse_int("+42") == 42
    assert parse_int("-2147483648") == -2147483648
    for bad in ("", " 42", "4 2", "42 ", "2147483648", "0x10", "--1", "+"):
        with pytest.raises(ValueError):
            parse_int(bad)


def test_parse_long() -> None:
    assert parse_long("9223372036854775807") == 9223372036854775807
    with pytest.raises(ValueError):
        parse_long("9223372036854775808")


def test_parse_double() -> None:
    assert parse_double("1.5") == 1.5
    assert parse_double("  2.5  ") == 2.5  # parseDouble trims whitespace
    assert parse_double("1d") == 1.0
    assert parse_double("1.5f") == 1.5
    assert parse_double("Infinity") == math.inf
    assert parse_double("-Infinity") == -math.inf
    assert math.isnan(parse_double("NaN"))
    assert math.isnan(parse_double("-NaN"))
    assert parse_double(".5") == 0.5
    assert parse_double("1e3") == 1000.0
    for bad in ("", "1_000", "nan", "infinity", "1.2.3", "e5"):
        with pytest.raises(ValueError):
            parse_double(bad)


def test_parse_boolean() -> None:
    assert parse_boolean("true") is True
    assert parse_boolean("TrUe") is True
    assert parse_boolean("yes") is False
    assert parse_boolean("") is False


def test_double_to_string_documented() -> None:
    # Double.toString javadoc / notation rules
    assert double_to_string(0.0) == "0.0"
    assert double_to_string(-0.0) == "-0.0"
    assert double_to_string(100.0) == "100.0"
    assert double_to_string(9999999.0) == "9999999.0"
    assert double_to_string(10000000.0) == "1.0E7"  # 10^7 switches to scientific
    assert double_to_string(0.001) == "0.001"  # 10^-3 still plain
    assert double_to_string(0.0001) == "1.0E-4"
    assert double_to_string(1e10) == "1.0E10"
    assert double_to_string(1.23e-5) == "1.23E-5"
    assert double_to_string(1 / 3) == "0.3333333333333333"
    assert double_to_string(float("nan")) == "NaN"
    assert double_to_string(float("inf")) == "Infinity"
    assert double_to_string(float("-inf")) == "-Infinity"


def test_float_to_string_documented() -> None:
    assert float_to_string(0.1) == "0.1"
    assert float_to_string(1 / 3) == "0.33333334"  # shortest float32 round-trip
    assert float_to_string(10000000.0) == "1.0E7"
    assert float_to_string(0.001) == "0.001"
    assert float_to_string(0.0001) == "1.0E-4"
    assert float_to_string(3.4028235e38) == "3.4028235E38"  # Float.MAX_VALUE
