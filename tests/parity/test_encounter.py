"""Java: EncounterProbe; exact T22 component and gated real lifetime integration."""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest

import tests.parity.canonical as canonical
from synthea.engine.module import Module
from synthea.helpers.config import Config
from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.javacompat.collections import JavaHashMap
from synthea.modules.death_module import DeathModule
from synthea.modules.encounter_module import EncounterModule, Inventory
from synthea.modules.immunizations import Immunizations
from synthea.modules.lifecycle_module import LifecycleModule
from synthea.world.agents.clinician import Clinician
from synthea.world.agents.payer_manager import PayerManager
from synthea.world.agents.person import Person
from synthea.world.agents.provider import Provider
from synthea.world.concepts.claim import Claim
from synthea.world.concepts.clinician_specialty import ClinicianSpecialty
from synthea.world.concepts.employment import Employment
from synthea.world.concepts.health_record import Code, EncounterType, Medication
from tests.dependency_gate import Pending, report_pending, run_or_pending
from tests.parity.canonical.encounter import claim, person_snapshot

WEEK = 604800000
DEPENDENCIES = ("T13", "T20", "T21")
pytestmark = pytest.mark.parity


def date(year: int, month: int = 1, day: int = 1) -> int:
    """Java: EncounterProbe#date (UTC)."""
    return int(datetime(year, month, day, tzinfo=UTC).timestamp() * 1000)


@pytest.fixture
def encounter_config(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Keep participant registries and canonical encoders local to T22 tests."""
    monkeypatch.setattr(Config, "properties", dict(Config.properties))
    Config.set("generate.timestep", str(WEEK))
    Config.set("generate.payers.loss_of_care", "false")
    monkeypatch.setattr(Provider, "providerByUuid", JavaHashMap())
    monkeypatch.setattr(
        PayerManager, "noInsurance", getattr(PayerManager, "noInsurance", None), raising=False
    )
    monkeypatch.setattr(canonical, "_ENCODERS", dict(canonical._ENCODERS))
    canonical.register_encoder(Claim, claim)
    canonical.register_encoder(Provider, lambda p: "provider:" + p.get_resource_id())
    canonical.register_encoder(Clinician, lambda c: "clinician:" + c.get_resource_id())
    for flag in (
        "ENABLE_DEATH_BY_NATURAL_CAUSES",
        "ENABLE_DEATH_BY_LOSS_OF_CARE",
        "ENABLE_PHYSIOLOGY_GENERATORS",
    ):
        monkeypatch.setattr(LifecycleModule, flag, False, raising=False)
    PayerManager.load_no_insurance()
    yield


def encounter_module_init_double(
    self: Module, definition: object = None, submodule: object = None
) -> None:
    """Java: Module#Module() is empty; only that unmerged T19 constructor boundary is doubled."""
    assert definition is None and submodule is None


@pytest.fixture
def module_constructor_double(monkeypatch: pytest.MonkeyPatch) -> None:
    """Component-only constructor plumbing; integration scenarios never use it."""
    monkeypatch.setattr(Module, "__init__", encounter_module_init_double)


def participants(
    i: int, integration: bool = False
) -> tuple[Person, Provider, list[Clinician], int, int]:
    """Java: EncounterProbe#scenario setup; real objects with explicit fixture inputs."""
    seed = (190000 if integration else 90000) + i
    birth, end = date(1950 + i), date(1990 + i, 1, 8)
    org = Provider()
    org.uuid, org.npi = "encounter-org", "1234567893"
    rng = DefaultRandomNumberGenerator(42)
    clinicians = [Clinician(42, rng, 100 + j, org) for j in range(3)]
    org.clinician_map[ClinicianSpecialty.GENERAL_PRACTICE] = clinicians
    Provider.providerByUuid.clear()
    Provider.providerByUuid[org.uuid] = org
    p = Person(seed)
    p.attributes.update(
        {
            Person.ID: f"encounter-person-{i}",
            Person.BIRTHDATE: birth,
            Person.GENDER: "F" if i % 2 == 0 else "M",
            Person.RACE: "white",
            Person.ETHNICITY: "nonhispanic",
            Person.FIRST_LANGUAGE: "english",
            Person.INCOME: 100000,
            Person.STATE: "Massachusetts",
            Person.EDUCATION_LEVEL: 0.6,
            Person.IDENTIFIER_PASSPORT: "",
            Person.EMPLOYMENT_MODEL: Employment(0.08),
        }
    )
    for kind in EncounterType:
        p.set_provider(kind, org)
    p.coverage.set_plan_to_no_insurance(birth)
    p.coverage.get_last_plan_record().update_stop_time(end + WEEK)
    return p, org, clinicians, birth, end


def scenario(i: int, integration: bool) -> dict[str, object]:
    """Java: EncounterProbe#scenario; >40 years, symptom thresholds and retained death lock."""
    p, org, clinicians, birth, end = participants(i, integration)
    lifecycle = None
    if integration:
        lifecycle = LifecycleModule()
        LifecycleModule.birth(p, birth)
    module = EncounterModule()
    added_chronic = False
    for step, time in enumerate(range(birth, end, WEEK)):
        if lifecycle is not None:
            lifecycle.process(p, time)
        if step % 251 == 0:
            severities = (300, 301, 350, 351, 500, 501)
            p.set_symptom(
                "Fixture", "cause", "pain", time, severities[(step // 251 + i) % 6], False
            )
        if not added_chronic and p.age_in_years(time) >= 30 and i % 2 == 0:
            assert p.record is not None
            med = p.record.new_entry(lambda time=time: Medication(time, "chronic"))
            med.codes.append(Code("RxNorm", "chronic", "Scripted chronic medication"))
            p.chronic_medications["chronic"] = med
            added_chronic = True
        module.process(p, time)
        module.process(p, time)
        module.end_encounter_module_encounters(p, time + 3600000)
    p.record_death(end, Code("SNOMED-CT", "12345", "Scripted cause"))
    DeathModule.process(p, end)
    result = person_snapshot(p, org, clinicians)
    result["stopped"] = module.process(p, end)
    return result


@pytest.mark.parametrize("i", range(50))
def test_encounter_component_lifetimes(
    golden: Callable[[str], Path], encounter_config: None, module_constructor_double: None, i: int
) -> None:
    """50 component lifetimes with scripted demographics; no Lifecycle behavior is doubled."""
    expected = json.loads((golden("EncounterProbe") / f"component_{i}.json").read_text())
    assert scenario(i, False) == expected, f"component person {i}"


def test_encounter_integration_lifetimes(
    golden: Callable[[str], Path], encounter_config: None
) -> None:
    """50 real Lifecycle/Encounter/Immunizations/Death timelines, gated on dependencies."""
    results = []
    for i in range(50):
        expected = json.loads((golden("EncounterProbe") / f"integration_{i}.json").read_text())
        actual = run_or_pending(lambda i=i: scenario(i, True), DEPENDENCIES)
        results.append(actual)
        if not isinstance(actual, Pending):
            assert actual == expected, f"integration person {i}"
    report_pending("Encounter Lifecycle integration", results)


def test_encounter_immunization_due_matrix(
    golden: Callable[[str], Path], encounter_config: None
) -> None:
    """Every vaccine across historical/window ages and three history sizes; exact code order."""
    root = golden("EncounterProbe")
    lines = (root / "doses.jsonl").read_text().splitlines()
    assert len(lines) >= 1000
    for line in lines:
        row = json.loads(line)
        p = Person(0)
        p.attributes[Person.BIRTHDATE] = date(2000)
        history = [date(2000) + j * 2592000000 for j in range(row["prior"])]
        months = row["months"]
        time = date(2000 + months // 12, 1 + months % 12)
        assert (
            Immunizations.immunization_due(row["name"], p, time, {row["name"]: history})
            == row["series"]
        ), row
    assert [canonical.dump_code(code) for code in Immunizations.get_all_codes()] == json.loads(
        (root / "codes.json").read_text()
    )


def test_encounter_inventory(golden: Callable[[str], Path]) -> None:
    """Exact combined inventory for all three T22 classes."""
    inventory: dict[str, Inventory] = {}
    for cls in (EncounterModule, DeathModule, Immunizations):
        cls.inventory_attributes(inventory)
    actual = {
        key: {
            "read": {k: sorted(v) for k, v in item.read.items()},
            "write": {k: sorted(v) for k, v in item.write.items()},
            "exampleValues": sorted(item.example_values),
        }
        for key, item in inventory.items()
    }
    assert actual == json.loads((golden("EncounterProbe") / "inventory.json").read_text())
