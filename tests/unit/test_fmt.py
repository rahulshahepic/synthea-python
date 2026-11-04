"""Unit tests for javacompat.fmt, from documented JDK Formatter behaviour.

Expected values are the examples called out in the task issue and the
``java.util.Formatter`` documentation — none is copied from goldens.
"""

from __future__ import annotations

import pytest

from synthea.javacompat.fmt import format


def test_float_rounding_half_up_on_shortest_repr() -> None:
    # The issue's canonical examples: Python's f"{x:.2f}" gives 0.12/1.00/2.67.
    assert format("%.2f", 0.125) == "0.13"
    assert format("%.2f", 1.005) == "1.01"
    assert format("%.2f", 2.675) == "2.68"
    assert format("%.0f", 2.5) == "3"
    assert format("%f", 1.5) == "1.500000"


def test_grouping() -> None:
    assert format("%,d", 1234567) == "1,234,567"
    assert format("%,d", -1234567) == "-1,234,567"
    assert format("%,.2f", 1234567.891) == "1,234,567.89"


def test_zero_padding_after_sign() -> None:
    assert format("%05d", -42) == "-0042"
    assert format("%05d", 42) == "00042"
    assert format("%08.2f", -3.14159) == "-0003.14"


def test_sign_flags() -> None:
    assert format("%+d", 42) == "+42"
    assert format("% d", 42) == " 42"
    assert format("%(d", -42) == "(42)"
    assert format("%(d", 42) == "42"
    assert format("%(.2f", -1.5) == "(1.50)"


def test_scientific() -> None:
    assert format("%e", 12345.678) == "1.234568e+04"
    assert format("%.3e", 12345.678) == "1.235e+04"
    assert format("%e", 0.0) == "0.000000e+00"
    assert format("%.0e", 12345.678) == "1e+04"


def test_hex() -> None:
    assert format("%x", 255) == "ff"
    assert format("%x", -1) == "ffffffff"  # Integer two's complement
    assert format("%x", -2147483648) == "80000000"
    assert format("%#x", 255) == "0xff"


def test_width_and_justify() -> None:
    assert format("%10.3f", 3.14159) == "     3.142"
    assert format("%6.2f", 3.14159) == "  3.14"
    assert format("%-10s|", "hi") == "hi        |"
    assert format("%5d|", 42) == "   42|"


def test_string_conversion_java_valueof() -> None:
    assert format("%s", None) == "null"
    assert format("%s", True) == "true"
    assert format("%s", False) == "false"
    assert format("%s", 1e7) == "1.0E7"  # Double.toString, not repr
    assert format("%.3s", "abcdef") == "abc"


def test_special_floats() -> None:
    assert format("%f", float("inf")) == "Infinity"
    assert format("%f", float("-inf")) == "-Infinity"
    assert format("%f", float("nan")) == "NaN"


def test_newline_and_percent() -> None:
    assert format("a%nb") == "a\nb"
    assert format("100%%") == "100%"


def test_argument_indexes() -> None:
    assert format("%2$s %1$s", "a", "b") == "b a"
    assert format("%s %<s", "x") == "x x"


def test_errors() -> None:
    with pytest.raises(ValueError):
        format("%q", 1)  # unsupported conversion
    with pytest.raises(ValueError):
        format("%d", True)  # Java throws for Boolean with %d
    with pytest.raises(ValueError):
        format("%d", "text")
    with pytest.raises(ValueError):
        format("%s %s", "only-one")
