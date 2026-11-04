"""Focused unit tests for the JDK and Synthea RNG contracts."""

from __future__ import annotations

import math

import pytest

from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.javacompat.random import JavaRandom
from synthea.javacompat.uuid import java_uuid


def test_java_random_known_sequence() -> None:
    """Java: java.util.Random#nextInt, well-known first draws for seed 0."""
    rng = JavaRandom(0)
    assert [rng.next_int() for _ in range(3)] == [-1155484576, -723955400, 1033096058]


def test_java_random_reset_seed_and_gaussian_cache() -> None:
    """Java: java.util.Random#setSeed clears the cached nextGaussian draw."""
    rng = JavaRandom(42)
    first = rng.next_gaussian()
    rng.next_gaussian()
    rng.set_seed(42)
    assert first == rng.next_gaussian()


@pytest.mark.parametrize("bound", [1, 2, 3, 7, 31, 1024, 1073741824, 2147483647])
def test_java_random_bounds(bound: int) -> None:
    """Java: java.util.Random#nextInt(int) stays in the requested half-open range."""
    rng = JavaRandom(123)
    assert all(0 <= rng.next_int(bound) < bound for _ in range(1000))


@pytest.mark.parametrize("bound", [0, -1, 2147483648])
def test_java_random_invalid_bound(bound: int) -> None:
    """Java: java.util.Random#nextInt(int) rejects non-positive/out-of-int bounds."""
    with pytest.raises(ValueError):
        JavaRandom(5).next_int(bound)


def test_java_uuid_signed_longs() -> None:
    """Java: java.util.UUID#UUID and #toString preserve all 128 bits."""
    assert java_uuid(-1, -1) == "ffffffff-ffff-ffff-ffff-ffffffffffff"
    assert java_uuid(0, 0) == "00000000-0000-0000-0000-000000000000"
    assert java_uuid(0x123456789ABCDEF0, 0xFEDCBA9876543210) == (
        "12345678-9abc-def0-fedc-ba9876543210"
    )


def test_synthea_counting_and_choices() -> None:
    """Java: DefaultRandomNumberGenerator#getCount tracks methods, not internal draws."""
    rng = DefaultRandomNumberGenerator(0)
    assert rng.get_count() == 0
    assert rng.rand() >= 0
    assert rng.get_count() == 1
    assert -2 <= rng.rand([-2, 3]) < 3
    assert rng.get_count() == 2
    assert rng.rand("a", "b", "c") in {"a", "b", "c"}
    assert rng.get_count() == 3
    assert isinstance(rng.rand_uuid(), str)
    assert rng.get_count() == 4
    assert math.isfinite(rng.rand_gaussian())
    assert rng.get_count() == 5


def test_range_validation() -> None:
    """Java: RandomNumberGenerator#rand(double[]) rejects invalid ranges."""
    rng = DefaultRandomNumberGenerator(0)
    with pytest.raises(ValueError):
        rng.rand([2.0])
    with pytest.raises(ValueError):
        rng.rand([3.0, 2.0])
    assert rng.get_count() == 0


def test_half_up_range_rounding() -> None:
    """Java: RandomNumberGenerator#rand(low, high, decimals) rounds HALF_UP."""
    rng = DefaultRandomNumberGenerator(0)
    rounded = rng.rand(0, 1, 2)
    assert rounded == pytest.approx(round(rounded, 2))
    assert rng.get_count() == 1
