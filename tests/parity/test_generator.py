"""Java: GeneratorProbe; demographic components and full real generation scenarios."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import cast

import pytest

import tests.parity.canonical as canonical
from synthea.engine.generator import Generator, GeneratorOptions
from synthea.export.exporter import Exporter
from synthea.helpers.config import Config
from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.helpers.random_number_generator import RandomNumberGenerator
from synthea.javacompat.collections import JavaHashMap
from synthea.javacompat.numbers import double_to_string
from synthea.world.agents.clinician import Clinician
from synthea.world.agents.payer_manager import PayerManager
from synthea.world.agents.person import Person
from synthea.world.agents.provider import Provider
from synthea.world.concepts.claim import Claim
from synthea.world.geography.location import Location
from tests.dependency_gate import Pending, report_pending, run_or_pending
from tests.parity.canonical import dump_record
from tests.parity.canonical.coverage import dump_coverage
from tests.parity.canonical.generator import claim, dump_person, enum_attributes
from tests.parity.canonical.person import render_value

STATES = ["Massachusetts", "California", "Texas"]
SEEDS = [42, 12345, 17]
TIME = 1735689600000
DEPENDENCIES = ("T16", "T19", "T21", "T22", "T23", "T24")
pytestmark = pytest.mark.parity


def options(group: int) -> GeneratorOptions:
    """Java: GeneratorProbe#options; fixed dates avoid wall-clock nondeterminism."""
    o = GeneratorOptions()
    o.population = 20
    o.seed = SEEDS[group]
    o.clinician_seed = 100 + SEEDS[group]
    o.reference_time = TIME
    o.end_time = TIME
    o.thread_pool_size = 1
    o.state = STATES[group]
    o.age_specified = True
    o.min_age = 0
    o.max_age = 3
    o.enabled_modules = []
    return o


@pytest.fixture
def generator_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Java: GeneratorProbe#configure; isolate registries and canonical encoders."""
    monkeypatch.setattr(Config, "properties", dict(Config.properties))
    for key in Config.all_property_names():
        if key.startswith("exporter.") and key.endswith(".export"):
            Config.set(key, "false")
    for key, value in {
        "exporter.years_of_history": "0",
        "exporter.enable_custom_exporters": "false",
        "exporter.split_records": "false",
        "generate.thread_pool_size": "1",
        "generate.log_patients.detail": "none",
        "generate.only_dead_patients": "false",
        "generate.only_alive_patients": "false",
        "generate.timestep": "604800000",
        "generate.max_attempts_to_keep_patient": "1000",
    }.items():
        Config.set(key, value)
    for name, replacement in [
        ("providerByUuid", JavaHashMap()),
        ("statesLoaded", set()),
        ("providerMap", Provider.providerMap),
        ("providerFinder", Provider.providerFinder),
        ("loaded", 0),
    ]:
        monkeypatch.setattr(Provider, name, replacement)
    for name, replacement in [
        ("payers", {}),
        ("statesLoaded", set()),
        ("planFinder", getattr(PayerManager, "planFinder", None)),
        ("noInsurance", getattr(PayerManager, "noInsurance", None)),
    ]:
        monkeypatch.setattr(PayerManager, name, replacement, raising=False)
    monkeypatch.setattr(canonical, "_ENCODERS", dict(canonical._ENCODERS))
    canonical.register_encoder(Claim, claim)
    canonical.register_encoder(Provider, lambda p: "provider:" + p.get_resource_id())
    canonical.register_encoder(Clinician, lambda c: "clinician:" + c.get_resource_id())
    monkeypatch.setattr(Exporter, "deferred_exports", [])


def generator_init_double(group: int) -> Generator:
    """Component-only Java Generator constructor field plumbing for demographic API tests.

    Provider/module initialization is irrelevant to the direct demographic method
    and belongs to the separate real-generation scenarios; all Location and RNG
    behavior here is real.
    """
    g = Generator.__new__(Generator)
    g.options = options(group)
    g.reference_time = TIME
    g.location = Location(STATES[group], None)
    g.only_veterans = False
    return g


@pytest.mark.parametrize("group", range(3))
def test_generator_component_demographics(
    golden: Callable[[str], Path], generator_config: None, group: int
) -> None:
    """Exact component parity: 600 demographic cases and 4,200 extra birthdate draws."""
    g = generator_init_double(group)
    rows = []
    for i in range(200):
        g.options.age_specified = i % 2 == 0
        g.options.min_age = i % 70
        g.options.max_age = 70 + i % 30
        g.options.gender = "F" if i % 5 == 0 else "M" if i % 5 == 1 else None
        g.only_veterans = i % 7 == 0
        random = DefaultRandomNumberGenerator(SEEDS[group] + i)
        attrs = g.random_demographics(cast(RandomNumberGenerator, random))
        row = {
            "attributes": {k: render_value(v) for k, v in attrs.items()},
            "count": str(random.get_count()),
        }
        row["birthdates"] = [
            str(g.birthdate_from_target_age(age, cast(RandomNumberGenerator, random)))
            for age in (0, 1, 18, 35, 85, 100, 140)
        ]
        row["final_count"] = str(random.get_count())
        rows.append(row)
    assert rows == json.loads((golden("GeneratorProbe") / f"demographics_{group}.json").read_text())


def person_snapshot(p: Person) -> dict[str, object]:
    """Java: GeneratorProbe#person, full canonical person/record/claim/coverage/vitals."""
    assert p.record is not None and p.current_modules is not None
    return {
        "person": dump_person(p),
        "enum_attributes": enum_attributes(p),
        "record": dump_record(p.record),
        "coverage": dump_coverage(p.coverage),
        "last_updated": str(p.last_updated),
        "population_seed": str(p.population_seed),
        "vitals": {
            sign.name: double_to_string(p.get_vital_sign(sign, p.last_updated))
            for sign in sorted(p.vital_signs, key=lambda sign: sign.name)
        },
        "modules": [m.name for m in p.current_modules],
    }


def population(group: int) -> dict[str, object]:
    """Java: GeneratorProbe#population; no doubles, real seeded generation and export."""
    Provider.clear()
    PayerManager.clear()
    g = Generator(options(group))
    g.internal_store = []
    g.run()
    return {
        "people": [person_snapshot(p) for p in g.internal_store],
        "alive": g.stats["alive"].get(),
        "dead": g.stats["dead"].get(),
        "total": g.total_generated_population.get(),
        "rng": str(g.population_random.get_count()),
        "clinician_rng": str(g.clinician_random.get_count()),
    }


def test_generator_integration_populations(
    golden: Callable[[str], Path], generator_config: None
) -> None:
    """Real integration: at least 20 generated persons in each of three seeds/states."""
    results = []
    for group in range(3):
        result = run_or_pending(lambda group=group: population(group), DEPENDENCIES)
        results.append(result)
        if not isinstance(result, Pending):
            expected = json.loads(
                (golden("GeneratorProbe") / f"population_{group}.json").read_text()
            )
            assert len(cast(list[object], expected["people"])) >= 20
            assert result == expected
    report_pending("Generator real populations", results)
