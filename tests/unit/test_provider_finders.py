"""Unit tests for the provider finders (T13).

Ports java/src/test/.../behaviors/ProviderFinderTest.java case for case,
plus Medicare-finder cases (no upstream test exists for
ProviderFinderNearestMedicare).
"""

from __future__ import annotations

import pytest

import synthea.world.agents.person as person_module
from synthea.world.agents.behaviors.providerfinder.provider_finder_nearest import (
    ProviderFinderNearest,
)
from synthea.world.agents.behaviors.providerfinder.provider_finder_nearest_medicare import (
    ProviderFinderNearestMedicare,
)
from synthea.world.agents.behaviors.providerfinder.provider_finder_random import (
    ProviderFinderRandom,
)
from synthea.world.agents.person import Person, Point2DDouble
from synthea.world.agents.provider import Provider, ProviderType
from synthea.world.concepts.health_record import EncounterType
from tests.parity.person_doubles import CoverageRecordDouble, HealthRecordDouble


@pytest.fixture(autouse=True)
def _person_doubles(monkeypatch: pytest.MonkeyPatch) -> None:
    """Allow real Person construction while T16/T14 are unmerged."""
    monkeypatch.setattr(person_module, "HealthRecord", HealthRecordDouble)
    monkeypatch.setattr(person_module, "CoverageRecord", CoverageRecordDouble)


@pytest.fixture
def person() -> Person:
    """Upstream setup: a person at (0, 0)."""
    result = Person(0)
    result.attributes[Person.COORDINATE] = Point2DDouble(0.0, 0.0)
    return result


@pytest.fixture
def providers() -> list[Provider]:
    """Upstream setup: three WELLNESS providers at (i, i) for i = 1..3."""
    result = []
    for i in (1, 2, 3):
        provider = Provider()
        provider.id = str(i)
        provider.get_lon_lat().x = float(i)
        provider.get_lon_lat().y = float(i)
        provider.services_provided.add(EncounterType.WELLNESS)
        result.append(provider)
    return result


def test_nearest(person: Person, providers: list[Provider]) -> None:
    found = ProviderFinderNearest().find(providers, person, EncounterType.WELLNESS, 0)
    assert found is not None
    assert found.id == "1"


def test_veteran_nearest(person: Person, providers: list[Provider]) -> None:
    providers[1].type = ProviderType.VETERAN
    person.attributes[Person.VETERAN] = "Civil War"
    found = ProviderFinderNearest().find(providers, person, EncounterType.WELLNESS, 0)
    assert found is not None
    assert found.id == "2"


def test_non_eligible_ihs_nearest(person: Person, providers: list[Provider]) -> None:
    providers[0].type = ProviderType.IHS
    person.attributes[Person.RACE] = "white"
    found = ProviderFinderNearest().find(providers, person, EncounterType.WELLNESS, 0)
    assert found is not None
    assert found.id == "2"


def test_any_nearest(person: Person, providers: list[Provider]) -> None:
    found = ProviderFinderNearest().find(providers, person, None, 0)
    assert found is not None
    assert found.id == "1"


def test_many_nearest(person: Person, providers: list[Provider]) -> None:
    options = providers + providers
    found = ProviderFinderNearest().find(options, person, EncounterType.WELLNESS, 0)
    assert found is not None
    assert found.id == "1"


def test_no_nearest(person: Person) -> None:
    assert ProviderFinderNearest().find([], person, EncounterType.WELLNESS, 0) is None


def test_random(person: Person, providers: list[Provider]) -> None:
    found = ProviderFinderRandom().find(providers, person, EncounterType.WELLNESS, 0)
    assert found is not None


def test_any_random(person: Person, providers: list[Provider]) -> None:
    found = ProviderFinderRandom().find(providers, person, None, 0)
    assert found is not None


def test_no_random(person: Person) -> None:
    assert ProviderFinderRandom().find([], person, EncounterType.WELLNESS, 0) is None


def test_medicare_nearest_skips_non_medicare(person: Person, providers: list[Provider]) -> None:
    # Only the farthest provider has a CMS provider number.
    providers[2].cms_provider_num = "123456"
    found = ProviderFinderNearestMedicare().find(providers, person, EncounterType.WELLNESS, 0)
    assert found is not None
    assert found.id == "3"


def test_medicare_blank_provider_num_is_not_medicare(
    person: Person, providers: list[Provider]
) -> None:
    # String.isBlank: a whitespace-only CMS number does not count.
    providers[0].cms_provider_num = "   "
    providers[1].cms_provider_num = "654321"
    found = ProviderFinderNearestMedicare().find(providers, person, EncounterType.WELLNESS, 0)
    assert found is not None
    assert found.id == "2"


def test_medicare_none_when_no_medicare_providers(
    person: Person, providers: list[Provider]
) -> None:
    found = ProviderFinderNearestMedicare().find(providers, person, EncounterType.WELLNESS, 0)
    assert found is None
