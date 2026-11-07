"""Java: Person inherited RandomNumberGenerator default overload regressions."""

from __future__ import annotations

import pytest

import synthea.world.agents.person as person_module
from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.world.agents.person import Person
from tests.parity.person_doubles import CoverageRecordDouble, HealthRecordDouble


@pytest.mark.parametrize("seed", [0, 1, 42, -1, 123456789, -(2**63), 2**63 - 1])
def test_person_component_rng_overloads_match_delegate(
    seed: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Java: Person RNG defaults preserve values, counts, and next draw (100 each)."""
    monkeypatch.setattr(person_module, "HealthRecord", HealthRecordDouble)
    monkeypatch.setattr(person_module, "CoverageRecord", CoverageRecordDouble)
    person = Person(seed)
    reference = DefaultRandomNumberGenerator(seed)

    def draw(rng: Person | DefaultRandomNumberGenerator) -> list[float | str]:
        return [
            rng.rand(),
            rng.rand(0, 10),
            rng.rand(-12.5, 91.25),
            rng.rand(-12.5, 91.25, 0),
            rng.rand(-12.5, 91.25, 2),
            rng.rand(-125.0, 912.5, -1),
            rng.rand(-12.5, 91.25, None),
            rng.rand([-12.5, 91.25]),
            rng.rand([-12, 91]),
            rng.rand("single"),
            rng.rand("a", "b"),
            rng.rand("a", "b", "c", "d", "e"),
        ]

    for _ in range(100):
        assert draw(person) == draw(reference)
        assert person.get_count() == reference.get_count()
        assert person.rand_long() == reference.rand_long()
    assert person.get_seed() == reference.get_seed() == seed


@pytest.mark.parametrize("bounds", [[], [1], [1, 2, 3], [2, 1]])
def test_person_component_invalid_ranges_do_not_consume_rng(
    bounds: list[int], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Java: invalid numeric ranges throw before drawing from Person's RNG."""
    monkeypatch.setattr(person_module, "HealthRecord", HealthRecordDouble)
    monkeypatch.setattr(person_module, "CoverageRecord", CoverageRecordDouble)
    person = Person(42)
    with pytest.raises(ValueError):
        person.rand(bounds)
    assert person.get_count() == 0
    assert person.rand() == DefaultRandomNumberGenerator(42).rand()
