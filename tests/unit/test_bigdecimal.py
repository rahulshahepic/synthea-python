"""Unit tests for javacompat.bigdecimal, from documented JDK behaviour.

Expected values are from the ``java.math.BigDecimal`` documentation and the
task issue — none is copied from goldens.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from synthea.javacompat import bigdecimal as bd


def test_to_string_notation_rules() -> None:
    # BigDecimal.toString javadoc: scientific when scale < 0 or adjusted
    # exponent < -6; the exponent sign is shown only when positive.
    assert bd.to_string(bd.from_string("1E+7")) == "1E+7"
    assert bd.to_string(bd.from_string("1E-7")) == "1E-7"
    assert bd.to_string(bd.from_string("0.000001")) == "0.000001"  # adjusted exp -6: plain
    assert bd.to_string(bd.from_string("0.0000001")) == "1E-7"  # adjusted exp -7: scientific
    assert bd.to_string(bd.from_string("1.00")) == "1.00"  # scale is preserved
    assert bd.to_string(bd.from_string("123456789")) == "123456789"
    assert bd.to_string(bd.from_string("1.23E+8")) == "1.23E+8"


def test_to_plain_string() -> None:
    assert bd.to_plain_string(bd.from_string("1E+7")) == "10000000"
    assert bd.to_plain_string(bd.from_string("1E-7")) == "0.0000001"
    assert bd.to_plain_string(bd.from_string("1.00")) == "1.00"


def test_from_double_exact_expansion() -> None:
    # new BigDecimal(0.1) is the exact binary expansion (BigDecimal javadoc).
    assert bd.to_string(bd.from_double_exact(0.1)) == (
        "0.1000000000000000055511151231257827021181583404541015625"
    )
    # BigDecimal.valueOf uses Double.toString, so it stays short.
    assert bd.value_of(0.1) == Decimal("0.1")
    assert bd.to_string(bd.value_of(0.1)) == "0.1"


def test_add_subtract_result_scale_is_max() -> None:
    assert bd.to_string(bd.add(bd.from_string("1.0"), bd.from_string("1.00"))) == "2.00"
    assert bd.to_string(bd.subtract(bd.from_string("1.00"), bd.from_string("1.0"))) == "0.00"


def test_multiply_result_scale_is_sum() -> None:
    assert bd.to_string(bd.multiply(bd.from_string("1.0"), bd.from_string("1.00"))) == "1.000"
    assert bd.to_string(bd.multiply(bd.from_string("2"), bd.from_string("3"))) == "6"


def test_divide_with_scale_and_mode() -> None:
    one, three = bd.from_string("1"), bd.from_string("3")
    assert bd.to_string(bd.divide(one, three, 10, bd.RoundingMode.HALF_UP)) == "0.3333333333"
    assert bd.to_string(bd.divide(one, three, 0, bd.RoundingMode.HALF_UP)) == "0"
    assert bd.to_string(bd.divide(bd.from_string("2"), three, 0, bd.RoundingMode.HALF_UP)) == "1"
    # 1/8 at scale 2: exactly 0.125, HALF_UP -> 0.13, HALF_EVEN -> 0.12
    one_eighth = (bd.from_string("1"), bd.from_string("8"))
    assert bd.to_string(bd.divide(*one_eighth, 2, bd.RoundingMode.HALF_UP)) == "0.13"
    assert bd.to_string(bd.divide(*one_eighth, 2, bd.RoundingMode.HALF_EVEN)) == "0.12"
    assert bd.to_string(bd.divide(*one_eighth, 2, bd.RoundingMode.DOWN)) == "0.12"
    assert bd.to_string(bd.divide(*one_eighth, 2, bd.RoundingMode.CEILING)) == "0.13"


def test_set_scale_including_negative() -> None:
    assert bd.to_string(bd.set_scale(bd.from_string("12345"), -2, bd.RoundingMode.HALF_UP)) == (
        "1.23E+4"
    )
    assert bd.to_string(bd.set_scale(bd.from_string("1.005"), 2, bd.RoundingMode.HALF_UP)) == "1.01"
    assert bd.to_string(bd.set_scale(bd.from_string("1"), 3, bd.RoundingMode.UNNECESSARY)) == (
        "1.000"
    )
    with pytest.raises(ValueError):
        bd.set_scale(bd.from_string("1.5"), 0, bd.RoundingMode.UNNECESSARY)


def test_compare_to_ignores_scale() -> None:
    assert bd.compare_to(bd.from_string("1.0"), bd.from_string("1.00")) == 0
    assert bd.compare_to(bd.from_string("2"), bd.from_string("10")) == -1
    assert bd.compare_to(bd.from_string("10"), bd.from_string("2")) == 1
    assert bd.compare_to(bd.from_string("-1"), bd.from_string("1")) == -1


def test_from_string_rejects_garbage() -> None:
    for bad in ("", "abc", "1.2.3", "NaN", "Infinity"):
        with pytest.raises(ValueError):
            bd.from_string(bad)
