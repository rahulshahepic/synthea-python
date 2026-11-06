"""Exact Java BigDecimal rounding parity for both T01 RNG implementations."""

import json
from collections.abc import Callable
from pathlib import Path

import pytest

from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.helpers.random_number_generator import RandomNumberGeneratorDefaults


@pytest.mark.parity
def test_random_rounded_zero_parity(golden: Callable[[str], Path]) -> None:
    """Match Java value bits, zero sign, draw counts and following RNG draws."""
    rows = [
        json.loads(line)
        for line in (golden("RandomRoundingProbe") / "rounding.jsonl").read_text().splitlines()
    ]
    assert len(rows) == 3200
    for use_defaults in (False, True):
        generators: dict[int, DefaultRandomNumberGenerator] = {}
        for row in rows:
            seed = int(row["seed"])
            rng = generators.setdefault(seed, DefaultRandomNumberGenerator(seed))
            decimals = int(row["decimals"])
            value = (
                RandomNumberGeneratorDefaults.rand(rng, -1e-12, -1e-13, decimals)
                if use_defaults
                else rng.rand(-1e-12, -1e-13, decimals)
            )
            assert value.hex() == float(row["value"]).hex()
            assert rng.get_count() == int(row["count"])
            assert str(rng.rand_long()) == row["nextLong"]
