"""Java: RandomNumberGenerator#rand(double,double,Integer), BigDecimal zero semantics."""

import math

import pytest

from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.helpers.random_number_generator import RandomNumberGeneratorDefaults


@pytest.mark.parametrize("use_defaults", [False, True])
@pytest.mark.parametrize("decimals", [-1, 0, 2, 6])
def test_rounded_negative_zero_is_positive(use_defaults: bool, decimals: int) -> None:
    """Exercise both real rounding implementations on negative draws, without mocks."""
    rng = DefaultRandomNumberGenerator(42)
    for _ in range(100):
        value = (
            RandomNumberGeneratorDefaults.rand(rng, -1e-12, -1e-13, decimals)
            if use_defaults
            else rng.rand(-1e-12, -1e-13, decimals)
        )
        assert value == 0.0
        assert math.copysign(1.0, value) == 1.0
    assert rng.get_count() == 100


@pytest.mark.parametrize("use_defaults", [False, True])
def test_unrounded_negative_values_remain_negative(use_defaults: bool) -> None:
    """Only BigDecimal rounding removes the sign; the ordinary range path keeps it."""
    rng = DefaultRandomNumberGenerator(42)
    value = (
        RandomNumberGeneratorDefaults.rand(rng, -1e-12, -1e-13)
        if use_defaults
        else rng.rand(-1e-12, -1e-13)
    )
    assert value < 0.0
    assert rng.get_count() == 1
