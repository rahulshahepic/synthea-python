"""Parity for Provider / Clinician / provider finders (T13).

Mirrors ProviderProbe case for case and compares the canonical dump exactly.

This is *component* parity in one respect (PORTING_GUIDE §10): a real Python
``Person`` cannot yet be constructed without T16's CoverageRecord (and T08's
HealthRecord pulls in T14's Claim on encounter start), so — exactly as in
tests/parity/test_person_component.py — ``tests/parity/person_doubles.py``
stand in for HealthRecord and CoverageRecord, supplying only the state
Person's constructor reads. Provider production code itself calls the real
Person, Location, Demographics, Names and QuadTree throughout.

Two T09 gaps are bridged in the test only, and listed in the PR body under
"Problems found": Person has no ``distance`` method (Java Person inherits
QuadTreeElement's default, which QuadTree.query calls), so query persons in
the ops case get the interface-default distance as an instance attribute.
"""

from __future__ import annotations

import importlib.util
import json
import math
from collections.abc import Callable
from pathlib import Path

import pytest

import synthea.world.agents.person as person_module
from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.world.agents.person import Person, Point2DDouble
from synthea.world.agents.provider import Provider
from synthea.world.concepts.health_record import EncounterType
from synthea.world.geography.location import Location
from tests.parity.person_doubles import CoverageRecordDouble, HealthRecordDouble

_spec = importlib.util.spec_from_file_location(
    "canonical_provider", Path(__file__).parent / "canonical" / "provider.py"
)
assert _spec is not None and _spec.loader is not None
canonical = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(canonical)

STATES = ["Massachusetts", "California", "Texas"]
SEEDS = [42, 12345]


def _quad_tree_distance(person: Person, element: object) -> float:
    """Java: QuadTreeElement#distance default (T09 person gap; see docstring)."""
    dx = person.get_x() - element.get_x()  # type: ignore[attr-defined]
    dy = person.get_y() - element.get_y()  # type: ignore[attr-defined]
    return math.sqrt(dx * dx + dy * dy)


def _query_person(seed: int, x: float, y: float) -> Person:
    person = Person(seed)
    person.attributes[Person.COORDINATE] = Point2DDouble(x, y)
    # Test-only bridge for the missing QuadTreeElement default on Person.
    person.distance = lambda element: _quad_tree_distance(person, element)  # type: ignore[attr-defined]
    return person


def _load_case(out: dict[str, str], state: str, seed: int) -> None:
    Provider.clear()
    location = Location(state, None)
    Provider.load_providers(location, DefaultRandomNumberGenerator(seed))
    providers = Provider.get_provider_list()
    text = f"state={state} seed={seed}" + f"\nloaded={len(providers)}"
    for provider in providers:
        text += "\n---\n" + canonical.dump(provider)
    out[f"load:{state}:{seed}"] = text


def _ops_case(out: dict[str, str], state: str, seed: int) -> None:
    # Continues on the load performed by _load_case for the same state/seed.
    providers = Provider.get_provider_list()
    first = providers[0]
    lines: list[str] = []
    choose_rand = DefaultRandomNumberGenerator(99)
    chosen = first.choose_clinician_list("GENERAL PRACTICE", choose_rand)
    lines.append(f"choose1={chosen.uuid} encountersAfter={chosen.get_encounter_count()}")
    chosen_again = first.choose_clinician_list("GENERAL PRACTICE", choose_rand)
    lines.append(
        f"choose2={chosen_again.uuid} encountersAfter={chosen_again.get_encounter_count()}"
    )
    fallback_rand = DefaultRandomNumberGenerator(100)
    fallback = first.choose_clinician_list("CARDIOLOGY", fallback_rand)
    lines.append(f"chooseFallback={fallback.uuid} encountersAfter={fallback.get_encounter_count()}")
    lines.append(f"chooseRandCount={choose_rand.get_count()}")
    first.increment_encounters(EncounterType.WELLNESS, 2020)
    first.increment_encounters(EncounterType.WELLNESS, 2020)
    first.increment_procedures(2020)
    first.increment_labs(2021)
    first.increment_prescriptions(2021)
    first.add_revenue(123.45)
    first.add_revenue(0.05)
    types = list(EncounterType)
    for i in range(25):
        target = providers[i]
        lon_lat = target.get_lon_lat()
        person = _query_person(6000 + i, lon_lat.get_x(), lon_lat.get_y())
        service = types[i % len(types)]
        found = Provider.find_service(person, service, 0)
        lines.append(
            f"findService{i} {service.name} -> "
            f"{found.uuid if found is not None else 'null'} count={person.get_count()}"
        )
    taken = [providers[0].uuid, providers[1].uuid]
    for i in range(10):
        target = providers[i]
        lon_lat = target.get_lon_lat()
        person = _query_person(7000 + i, lon_lat.get_x(), lon_lat.get_y())
        service = types[(i * 3) % len(types)]
        found = Provider.find_service_new_provider(person, service, 0, taken)
        lines.append(
            f"findNew{i} {service.name} -> "
            f"{found.uuid if found is not None else 'null'} count={person.get_count()}"
        )
    out[f"ops:{state}:{seed}"] = "\n".join(lines) + "\n---\n" + canonical.dump(first)


def _run_finder_queries(
    lines: list[str], finder_name: str, providers: list[Provider], types: list[EncounterType]
) -> None:
    # Function-local imports: the finders are T13's own classes.
    from synthea.world.agents.behaviors.providerfinder.provider_finder_nearest import (
        ProviderFinderNearest,
    )
    from synthea.world.agents.behaviors.providerfinder.provider_finder_nearest_medicare import (
        ProviderFinderNearestMedicare,
    )
    from synthea.world.agents.behaviors.providerfinder.provider_finder_random import (
        ProviderFinderRandom,
    )

    lines.append(f"finder={finder_name}")
    for i in range(500):
        target = providers[(i * 37) % len(providers)]
        lon_lat = target.get_lon_lat()
        person = Person(5000 + i)
        x = lon_lat.get_x() + ((i % 7) - 3) * 0.01
        y = lon_lat.get_y() + ((i % 5) - 2) * 0.01
        person.attributes[Person.COORDINATE] = Point2DDouble(x, y)
        if i % 11 == 0:
            person.attributes[Person.VETERAN] = "vietnam"
        if i % 13 == 0:
            person.attributes[Person.RACE] = "native"
        elif i % 7 == 0:
            person.attributes[Person.RACE] = "white"
        service = None if i % 6 == 5 else types[i % len(types)]
        if finder_name == "nearest":
            found = ProviderFinderNearest().find(providers, person, service, 0)
        elif finder_name == "medicare":
            found = ProviderFinderNearestMedicare().find(providers, person, service, 0)
        else:
            found = ProviderFinderRandom().find(providers, person, service, 0)
        lines.append(
            f"q{i} service={service.name if service is not None else 'null'} -> "
            f"{found.uuid if found is not None else 'null'} count={person.get_count()}"
        )


def _finder_case(out: dict[str, str], state: str) -> None:
    Provider.clear()
    location = Location(state, None)
    Provider.load_providers(location, DefaultRandomNumberGenerator(42))
    providers = Provider.get_provider_list()
    types = list(EncounterType)
    lines = [f"state={state} providers={len(providers)}"]
    _run_finder_queries(lines, "nearest", providers, types)
    _run_finder_queries(lines, "medicare", providers, types)
    _run_finder_queries(lines, "random", providers, types)
    out[f"finders:{state}"] = "\n".join(lines)


@pytest.mark.parity
def test_provider_probe(golden: Callable[[str], Path], monkeypatch: pytest.MonkeyPatch) -> None:
    """Every ProviderProbe case matches the Java canonical dump exactly."""
    monkeypatch.setattr(person_module, "HealthRecord", HealthRecordDouble)
    monkeypatch.setattr(person_module, "CoverageRecord", CoverageRecordDouble)
    actual: dict[str, str] = {}
    for state in STATES:
        for seed in SEEDS:
            _load_case(actual, state, seed)
            _ops_case(actual, state, seed)
    for state in STATES:
        _finder_case(actual, state)
    golden_path = golden("ProviderProbe") / "provider.jsonl"
    rows = [
        json.loads(line)
        for line in golden_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert [row["case"] for row in rows] == list(actual.keys())
    for row in rows:
        assert actual[row["case"]] == row["out"], row["case"]
