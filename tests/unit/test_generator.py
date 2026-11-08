"""Java: GeneratorTest, plus Generator orchestration and criteria branch tests."""

from __future__ import annotations

import itertools
from pathlib import Path

import pytest

from synthea.engine.generator import AtomicInteger, CriteriaCheck, Generator, GeneratorOptions
from synthea.export.exporter import Exporter, ExporterRuntimeOptions
from synthea.helpers.config import Config
from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.helpers.random_number_generator import RandomNumberGenerator
from synthea.helpers.utilities import Utilities
from synthea.modules.lifecycle_module import LifecycleModule
from synthea.world.agents.person import Person
from tests.dependency_gate import report_pending, run_or_pending
from tests.parity.test_generator import DEPENDENCIES, TIME, generator_init_double, options
from tests.parity.test_generator import generator_config as generator_config


@pytest.mark.parametrize("flags", list(itertools.product((False, True), repeat=5)))
def test_generator_criteria_truth_table(flags: tuple[bool, ...]) -> None:
    """Java: CriteriaCheck#meetsCriteria/exportAnyway, exhaustive flag combinations."""
    check = CriteriaCheck()
    for name, value in zip(
        (
            "reject_dead_but_overflow",
            "is_alive_but_dead_required",
            "is_dead_but_alive_required",
            "insufficient_providers",
            "failed_keep_module",
        ),
        flags,
        strict=True,
    ):
        setattr(check, name, value)
    assert check.meets_criteria() == (not any(flags))
    assert check.export_anyway() == (not any(flags[1:]))


@pytest.mark.parametrize(
    "alive,only_alive,only_dead,overflow,has_provider",
    list(itertools.product((False, True), repeat=5)),
)
def test_generator_check_criteria(
    generator_config: None,
    alive: bool,
    only_alive: bool,
    only_dead: bool,
    overflow: bool,
    has_provider: bool,
) -> None:
    """Java: Generator#checkCriteria flags and provider minimum with real Person."""
    g = generator_init_double(0)
    g.only_alive_patients = only_alive
    g.only_dead_patients = only_dead
    g.options.overflow = overflow
    g.keep_patients_module = None
    p = Person(1)
    if has_provider:
        p.has_multiple_records = True
        assert p.record is not None
        p.records = {"scripted-provider": p.record}
    check = g.check_criteria(p, TIME, 0, alive)
    assert check.reject_dead_but_overflow == (not alive and not only_dead and overflow)
    assert check.is_alive_but_dead_required == (alive and only_dead)
    assert check.is_dead_but_alive_required == (not alive and only_alive)
    assert check.insufficient_providers == (not has_provider)


@pytest.mark.parametrize(
    "patterns,accepted,rejected",
    [
        (None, ["anything", "sub/Anything.json"], []),
        ([], [], ["anything"]),
        (["*.JSON", "asthma?"], ["sub/FOO.json", "ASTHMA1"], ["asthma", "asthma12"]),
        (["[foo]"], ["[foo]"], ["f", "o"]),
    ],
)
def test_generator_module_predicate(
    patterns: list[str] | None, accepted: list[str], rejected: list[str]
) -> None:
    """Java: WildcardFileFilter supports only * and ?, with case-insensitive matches."""
    g = generator_init_double(0)
    g.options.enabled_modules = patterns
    predicate = g.get_module_predicate()
    assert all(predicate(p) for p in accepted)
    assert not any(predicate(p) for p in rejected)


@pytest.mark.parametrize(
    "field",
    [
        "initial_population_snapshot_path",
        "updated_population_snapshot_path",
        "fixed_record_path",
        "keep_patients_module_path",
    ],
)
def test_generator_excluded_options(generator_config: None, field: str) -> None:
    """Java: issue-excluded optional Generator paths fail explicitly before initialization."""
    o = options(0)
    setattr(o, field, Path("unused"))
    with pytest.raises(NotImplementedError, match="out of scope"):
        Generator(o)


@pytest.mark.parametrize("flag", ["growtherrors", "exporter.cdw.export"])
def test_generator_excluded_config(generator_config: None, flag: str) -> None:
    """Java: PORTING_GUIDE section 8 rejects enabled editors and non-CSV exports."""
    Config.set(flag, "true")
    with pytest.raises(NotImplementedError, match="out of scope"):
        Generator(options(0))


def test_generator_default_options(generator_config: None) -> None:
    """Java: GeneratorOptions field initializers, using a bounded real wall-clock value."""
    o = GeneratorOptions()
    assert o.reference_time == o.end_time == o.run_start_time == o.seed == o.clinician_seed
    assert o.single_person_seed is None and o.overflow
    assert o.gender is None and not o.age_specified
    assert (o.min_age, o.max_age) == (0, 140)
    assert o.city is None and o.state is None
    assert o.enabled_modules is None and o.days_to_travel_forward == -1


def test_generator_counter_wraps() -> None:
    """Java: AtomicInteger incrementAndGet wraps signed 32-bit values."""
    counter = AtomicInteger(2147483647)
    assert counter.increment_and_get() == -2147483648
    assert counter.get() == int(counter) == -2147483648


def test_generator_demographic_retry(
    generator_config: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Java: GeneratorTest#testDemographicsRetry; isolated retry control-flow inputs.

    create_person_double supplies only explicit alive/dead Person state and RNG;
    no clinical behavior or lifetime parity is claimed by this unit test.
    """
    g = generator_init_double(0)
    g.timestep = 604800000
    g.only_alive_patients = False
    g.only_dead_patients = False
    g.keep_patients_module = None
    g.max_attempts_to_keep_patient = 1000
    g.options.overflow = True
    g.log_level = "none"
    g.internal_store = []
    g.stats = {"alive": AtomicInteger(), "dead": AtomicInteger()}
    g.total_generated_population = AtomicInteger()
    g.exporter_runtime_options = ExporterRuntimeOptions()
    attempts: list[tuple[int, dict[str, object]]] = []

    def create_person_double(seed: int, attrs: dict[str, object]) -> Person:
        """Unit-only predeclared terminal Person state, with real RNG/provider bookkeeping."""
        p = Person(seed)
        p.attributes.update(attrs)
        p.last_updated = TIME
        p.has_multiple_records = True
        assert p.record is not None
        p.records = {"scripted-provider": p.record}
        if len(attempts) < 2:
            p.attributes[Person.DEATHDATE] = TIME
        attempts.append((seed, dict(attrs)))
        return p

    exported = []

    def export_person_double(p: Person, time: int, opts: ExporterRuntimeOptions) -> bool:
        """Unit-only export plumbing records calls without changing clinical state or RNG."""
        exported.append(p.get_seed())
        return True

    monkeypatch.setattr(g, "create_person", create_person_double)
    monkeypatch.setattr(Exporter, "export", export_person_double)
    result = g.generate_person(0, 42)
    assert len(attempts) == len(exported) == 3
    assert attempts[0][1] == attempts[1][1] == attempts[2][1]
    assert attempts[1][0] == DefaultRandomNumberGenerator(42).rand_long()
    assert attempts[2][0] == DefaultRandomNumberGenerator(attempts[1][0]).rand_long()
    assert result is g.internal_store[-1]
    assert g.stats["dead"].get() == 2 and g.stats["alive"].get() == 1
    assert g.total_generated_population.get() == 3


@pytest.mark.parametrize(
    "case",
    [
        "creates_people",
        "detailed_log",
        "only_alive",
        "only_dead",
        "both_flags",
        "default_location",
        "locations",
        "update_after_creation",
    ],
)
def test_generator_upstream_integration(
    generator_config: None, case: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Java: GeneratorTest scoped real generation assertions; no clinical doubles."""

    def scenario() -> None:
        o = options(0)
        o.population = 2
        if case == "detailed_log":
            Config.set("generate.log_patients.detail", "detailed")
        if case in ("only_alive", "both_flags"):
            Config.set("generate.only_alive_patients", "true")
        if case in ("only_dead", "both_flags"):
            Config.set("generate.only_dead_patients", "true")
        if case == "locations":
            o.state = "California"
            o.city = "South Gate"
        generator_type = Generator
        if case == "only_dead":
            # GeneratorTest#testOnlyDeadPatients selects senior patients. Natural
            # mortality supplies real deaths with this fixture's empty module filter.
            o.age_specified = True
            o.min_age = 50
            o.max_age = 140
            Config.set("lifecycle.death_by_natural_causes", "true")
            # Match a fresh JVM's config-backed static initialization in this shared interpreter.
            monkeypatch.setattr(
                LifecycleModule,
                "ENABLE_DEATH_BY_NATURAL_CAUSES",
                Config.get_as_boolean("lifecycle.death_by_natural_causes"),
            )

            class PassportInputGenerator(Generator):
                """Java: Generator#randomDemographics; input excludes T21 passport generation."""

                def random_demographics(self, random: RandomNumberGenerator) -> dict[str, object]:
                    """Supply the authorized existing-empty-passport fixture input."""
                    attributes = super().random_demographics(random)
                    attributes[Person.IDENTIFIER_PASSPORT] = ""
                    return attributes

            generator_type = PassportInputGenerator
        g = generator_type(o)
        g.internal_store = []
        g.run()
        assert g.stats["dead" if case == "only_dead" else "alive"].get() == 2
        if case == "only_dead":
            assert g.stats["alive"].get() == 0
        if case == "only_alive":
            assert g.stats["dead"].get() == 0
        if case == "both_flags":
            assert Config.get("generate.only_alive_patients") == "false"
            assert Config.get("generate.only_dead_patients") == "false"
        for p in g.internal_store:
            assert p.attributes[Person.STATE] == o.state
            if o.city is not None:
                assert p.attributes[Person.CITY] == o.city
                assert p.attributes[Person.ZIP] in g.location.get_zip_codes(o.city)
        if case == "update_after_creation":
            g.stop += Utilities.convert_time("years", 1)
            for p in g.internal_store:
                before = p.last_updated
                g.update_person(p)
                assert p.last_updated > before

    report_pending("GeneratorTest " + case, [run_or_pending(scenario, DEPENDENCIES)])
