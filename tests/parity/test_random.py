"""Exact value parity against Java-produced random goldens."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest

from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.javacompat.random import JavaRandom

SEEDS = (0, 1, 42, -1, 123456789, (1 << 63) - 1, -(1 << 63), 1735689600000)


def _check_value(actual: float | int | bool | str, expected: str) -> None:
    """Compare the exact binary floating-point value or Java primitive spelling."""
    if isinstance(actual, float):
        assert actual.hex() == float(expected).hex()
    elif isinstance(actual, bool):
        assert str(actual).lower() == expected
    else:
        assert str(actual) == expected


@pytest.mark.parity
def test_java_random_probe(golden: Callable[[str], Path]) -> None:
    """Every JavaRandomProbe operation matches the Java RNG value exactly."""
    states: dict[int, JavaRandom] = {}
    uuids: dict[int, DefaultRandomNumberGenerator] = {}
    with (golden("JavaRandomProbe") / "random.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            seed = int(row["seed"])
            rng = states.setdefault(seed, JavaRandom(seed))
            op = row["op"]
            if op == "nextDouble":
                value: float | int | bool | str = rng.next_double()
            elif op == "nextInt":
                value = rng.next_int()
            elif op.startswith("nextInt("):
                bound = (1 << 30) if op == "nextInt(1<<30)" else int(op[8:-1])
                value = rng.next_int(bound)
            elif op == "nextLong":
                value = rng.next_long()
            elif op == "nextBoolean":
                value = rng.next_boolean()
            elif op == "nextGaussian":
                value = rng.next_gaussian()
            elif op == "randUUID":
                value = uuids.setdefault(seed, DefaultRandomNumberGenerator(seed)).rand_uuid()
            else:
                pytest.fail(f"unexpected JavaRandomProbe op: {op}")
            _check_value(value, row["v"])


@pytest.mark.parity
def test_generator_probe(golden: Callable[[str], Path]) -> None:
    """All 12 default-method variants match Java, including draw-count bookkeeping."""
    generators = {seed: DefaultRandomNumberGenerator(seed) for seed in SEEDS}
    seen: dict[str, int] = {}
    with (golden("RandomNumberGeneratorProbe") / "generator.jsonl").open(
        encoding="utf-8"
    ) as stream:
        for line in stream:
            row = json.loads(line)
            rng = generators[int(row["seed"])]
            op = row["op"]
            i = int(row["i"])
            if op == "rand":
                value = rng.rand()
            elif op == "randRange":
                value = rng.rand(-7.25, 21.5)
            elif op == "randRound":
                value = rng.rand(-7.25, 21.5, 2)
            elif op == "randDoubleArray":
                value = rng.rand([-2.5, 6.25])
            elif op == "randIntArray":
                value = rng.rand([-3, 7])
            elif op == "randChoices":
                value = rng.rand("alpha", "beta", "gamma", "delta")
            elif op == "randBoolean":
                value = rng.rand_boolean()
            elif op == "randGaussian":
                value = rng.rand_gaussian()
            elif op == "randInt":
                value = rng.rand_int()
            elif op == "randIntBound":
                value = rng.rand_int(1 + (i * 7919) % 1000)
            elif op == "randLong":
                value = rng.rand_long()
            elif op == "randUUID":
                value = rng.rand_uuid()
            else:
                pytest.fail(f"unexpected generator op: {op}")
            _check_value(value, row["v"])
            assert rng.get_count() == int(row["count"])
            seen[op] = seen.get(op, 0) + 1
    assert len(seen) == 12
    assert all(n >= 800 for n in seen.values())
