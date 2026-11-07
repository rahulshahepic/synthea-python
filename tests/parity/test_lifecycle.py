"""Java: LifecycleProbe; lifetime integration plus isolated T21 component parity.

The only component double replaces Module's empty no-argument constructor while
T19 is unmerged. All Persons, records, trajectories, RNGs and other collaborators
are real. The separate integration test keeps the real call and the dependency gate.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest

from synthea.engine.module import Module
from synthea.helpers.config import Config
from synthea.modules.blood_pressure_value_generator import BloodPressureValueGenerator, SysDias
from synthea.modules.lifecycle_module import Inventory, LifecycleModule
from synthea.world.agents.payer_manager import PayerManager
from synthea.world.agents.person import Person
from synthea.world.concepts.employment import Employment
from synthea.world.concepts.health_record import Code, EncounterType
from tests.dependency_gate import Pending, report_pending, run_or_pending
from tests.parity.canonical.lifecycle import person_snapshot

BIRTH = -2208988800000
WEEK = 604800000
DEPENDENCIES = ("T10", "T11", "T12", "T19")
pytestmark = pytest.mark.parity


@pytest.fixture
def lifecycle_config(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Keep flags, global resources and configuration isolated between parity scenarios."""
    monkeypatch.setattr(Config, "properties", dict(Config.properties))
    Config.set("generate.timestep", str(WEEK))
    monkeypatch.setattr(LifecycleModule, "ENABLE_DEATH_BY_NATURAL_CAUSES", False)
    monkeypatch.setattr(LifecycleModule, "ENABLE_DEATH_BY_LOSS_OF_CARE", False)
    monkeypatch.setattr(LifecycleModule, "ENABLE_PHYSIOLOGY_GENERATORS", False)
    monkeypatch.setattr(
        PayerManager, "noInsurance", getattr(PayerManager, "noInsurance", None), raising=False
    )
    yield


def lifecycle_module_init_double(
    self: Module, definition: object = None, submodule: object = None
) -> None:
    """Java: Module#Module() is empty; double only that unmerged T19 plumbing boundary."""
    assert definition is None and submodule is None


@pytest.fixture
def module_constructor_double(monkeypatch: pytest.MonkeyPatch) -> None:
    """Component-only double; never used by the gated integration scenario."""
    monkeypatch.setattr(Module, "__init__", lifecycle_module_init_double)


def newborn(seed: int, i: int) -> Person:
    """Java: LifecycleProbe#newborn; a real seeded person with scripted starting attributes."""
    p = Person(seed)
    p.attributes.update(
        {
            Person.GENDER: "F" if i % 2 == 0 else "M",
            Person.RACE: "black" if i % 3 == 0 else "white",
            Person.ETHNICITY: "hispanic" if i % 4 == 0 else "nonhispanic",
            Person.FIRST_LANGUAGE: "spanish" if i % 4 == 0 else "english",
            Person.EDUCATION_LEVEL: (i % 10) / 10.0 + 0.05,
            Person.EMPLOYMENT_MODEL: Employment((i % 5) * 0.04),
            Person.IDENTIFIER_PASSPORT: "",  # out-of-scope identifier generation, in both fixtures
        }
    )
    LifecycleModule.birth(p, BIRTH)
    return p


def lifetime(i: int) -> list[dict[str, object]]:
    """Java: LifecycleProbe#lifetime; weekly updates, annual and terminal snapshots."""
    LifecycleModule.ENABLE_DEATH_BY_NATURAL_CAUSES = i >= 50
    p = newborn(1000 + i, i)
    module = LifecycleModule()
    result = [person_snapshot(p, BIRTH)]
    last_age = 0
    end = int(datetime(1991, 1, 1, tzinfo=UTC).timestamp() * 1000)
    for time in range(BIRTH + WEEK, end, WEEK):
        module.process(p, time)
        age = p.age_in_years(time)
        if age > last_age or not p.alive(time):
            result.append(person_snapshot(p, time))
            last_age = age
        if not p.alive(time):
            break
    return result


def load_lifetime(golden: Callable[[str], Path], i: int) -> list[dict[str, object]]:
    """Read only Java-produced expectations."""
    file = golden("LifecycleProbe") / f"life_{i}.jsonl"
    return [json.loads(line) for line in file.read_text().splitlines()]


@pytest.mark.parametrize("i", range(60))
def test_lifecycle_component_lifetimes(
    golden: Callable[[str], Path], lifecycle_config: None, module_constructor_double: None, i: int
) -> None:
    """Component parity across 60 seeds; 50 are followed through their 90th birthday."""
    expected = load_lifetime(golden, i)
    if i < 50:
        assert len(expected) == 91
    actual = lifetime(i)
    assert len(actual) == len(expected)
    for year, (got, want) in enumerate(zip(actual, expected, strict=True)):
        assert got == want, f"person {i}, snapshot {year}"


def test_lifecycle_integration_lifetimes(
    golden: Callable[[str], Path], lifecycle_config: None
) -> None:
    """Real Module constructor; 60 pending scenarios become mandatory when T19 merges."""
    results = []
    for i in range(60):
        expected = load_lifetime(golden, i)
        actual = run_or_pending(lambda i=i: lifetime(i), DEPENDENCIES)
        results.append(actual)
        if not isinstance(actual, Pending):
            assert actual == expected, f"person {i}"
    report_pending("Lifecycle birth-to-90 integration", results)


def direct(i: int) -> dict[str, object]:
    """Java: LifecycleProbe#direct; real medication/careplan records and generator cache cases."""
    LifecycleModule.ENABLE_DEATH_BY_NATURAL_CAUSES = False
    time = 1577836800000
    p = newborn(9000 + i, i)
    p.coverage.set_plan_to_no_insurance(BIRTH)
    p.coverage.get_last_plan_record().update_stop_time(time + 10 * 31536000000)
    assert p.record is not None
    p.record.encounter_start(time, EncounterType.WELLNESS)
    p.attributes.update(
        {
            "hypertension": i % 3 > 0,
            "hypertension_severe": i % 3 == 2,
            "diabetes_severity": i % 4,
            "prediabetes": i % 3 == 1,
            "diabetes": i % 3 == 2,
            "ckd": i % 5,
        }
    )
    if i % 2 == 0:
        p.attributes["chf"] = False
    record = p.record
    assert record is not None
    if i % 4 == 0:
        for code in ("197499", "314076", "860975", "865098"):
            med = record.medication_start(time - 1000, code, False)
            med.codes.append(Code("RxNorm", code, "scripted"))
    cp = record.careplan_start(time - (i % 4) * 15768000000, "443402002")
    cp.codes.append(Code("SNOMED-CT", "443402002", "Hypertension plan"))
    if i % 4 == 1:
        cp.stop = time - 1
    if i % 5 != 0:
        p.attributes["htn_trial_443402002_careplan_adherent"] = i % 2 == 0
    LifecycleModule.calculate_vital_signs(p, time)
    systolic = BloodPressureValueGenerator(p, SysDias.SYSTOLIC)
    diastolic = BloodPressureValueGenerator(p, SysDias.DIASTOLIC)
    from synthea.javacompat.numbers import double_to_string

    values = []
    for instant in (time, time, time + 43200000, -43200001, -1, 0, time):
        values.extend(
            [
                double_to_string(systolic.get_value(instant)),
                double_to_string(diastolic.get_value(instant)),
            ]
        )
    return {"bp": values, "snapshot": person_snapshot(p, time)}


def test_lifecycle_metabolic_and_bp_parity(
    golden: Callable[[str], Path], lifecycle_config: None
) -> None:
    """CKD/diabetes severities, drug impacts, adherence, signed cycles and timestamp caching."""
    expected = [
        json.loads(line)
        for line in (golden("LifecycleProbe") / "direct.jsonl").read_text().splitlines()
    ]
    assert len(expected) == 120
    PayerManager.load_no_insurance()
    for i, want in enumerate(expected):
        assert direct(i) == want, f"direct case {i}"


def test_lifecycle_mortality_and_inventory(
    golden: Callable[[str], Path], lifecycle_config: None
) -> None:
    """Death-risk boundaries and the complete Java attribute inventory."""
    from synthea.javacompat.numbers import double_to_string

    root = golden("LifecycleProbe")
    for line in (root / "mortality.jsonl").read_text().splitlines():
        row = json.loads(line)
        assert double_to_string(LifecycleModule.likelihood_of_death(row["age"])) == row["risk"]
    inventory: dict[str, Inventory] = {}
    LifecycleModule.inventory_attributes(inventory)
    actual = {
        key: {
            "read": {k: sorted(v) for k, v in item.read.items()},
            "write": {k: sorted(v) for k, v in item.write.items()},
            "exampleValues": sorted(item.example_values),
        }
        for key, item in inventory.items()
    }
    assert actual == json.loads((root / "inventory.json").read_text())


def test_lifecycle_birth_geography_parity(
    golden: Callable[[str], Path], lifecycle_config: None
) -> None:
    """Java: LifecycleProbe birth cases with real locations, native/foreign birthplaces and ZIPs."""
    from synthea.world.geography.location import Location

    expected = [
        json.loads(line)
        for line in (golden("LifecycleProbe") / "birth_geography.jsonl").read_text().splitlines()
    ]
    states = ("Massachusetts", "California", "Texas")
    cities = ("Bedford", "Los Angeles", "Houston")
    assert len(expected) == 6
    for i, want in enumerate(expected):
        p = Person(8800 + i)
        p.attributes.update(
            {
                Person.GENDER: "F" if i % 2 == 0 else "M",
                Person.RACE: "white",
                Person.ETHNICITY: "hispanic" if i % 2 == 0 else "nonhispanic",
                Person.FIRST_LANGUAGE: "spanish" if i % 2 == 0 else "english",
                Person.LOCATION: Location(states[i % 3], cities[i % 3]),
                Person.CITY: cities[i % 3],
            }
        )
        LifecycleModule.birth(p, BIRTH)
        assert person_snapshot(p, BIRTH) == want, f"geography birth {i}"
