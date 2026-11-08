"""Java: Module#loadModules core registration and real processing (T19-fix, #77)."""

from __future__ import annotations

import pytest

from synthea.engine.module import Module
from synthea.helpers.config import Config
from synthea.javacompat.collections import JavaHashMap
from synthea.modules.cardiovascular_disease_module import CardiovascularDiseaseModule
from synthea.modules.covid.c19_immunization_module import C19ImmunizationModule
from synthea.modules.covid.c19_vaccine import C19Vaccine
from synthea.modules.covid.c19_vaccine_age_distributions import C19VaccineAgeDistributions
from synthea.modules.lifecycle_module import LifecycleModule
from synthea.modules.quality_of_life_module import QualityOfLifeModule
from synthea.modules.weight_loss_module import WeightLossModule
from synthea.world.agents.person import Person
from synthea.world.concepts.employment import Employment
from synthea.world.concepts.vital_sign import VitalSign


@pytest.fixture
def fresh_core_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Isolate real registry/COVID static initialization as in a fresh Java process."""
    monkeypatch.setattr(Module, "modules", None)
    for field in ("rawDistributions", "distributions", "firstShotProbByAge"):
        monkeypatch.setattr(C19VaccineAgeDistributions, field, JavaHashMap())
    monkeypatch.setattr(C19Vaccine, "EUAs", {})
    monkeypatch.setattr(C19Vaccine, "shotSelector", None)


def test_engine_core_registry_types_and_order(fresh_core_registry: None) -> None:
    """Java: Module#loadModules/getModules return real classes in TreeMap key order."""
    modules = Module.get_modules(lambda _: False)
    assert [type(module) for module in modules] == [
        C19ImmunizationModule,
        CardiovascularDiseaseModule,
        LifecycleModule,
        QualityOfLifeModule,
        WeightLossModule,
    ]
    assert [module.name for module in modules] == [
        "COVID-19 Immunization Module",
        "Cardiovascular Disease",
        "Lifecycle",
        "Quality of Life",
        "Weight Loss",
    ]
    repeated = Module.get_modules(lambda _: False)
    assert all(first is second for first, second in zip(modules, repeated, strict=True))
    assert all(not module.submodule for module in modules)


def test_engine_registry_lifecycle_processes_real_person(
    fresh_core_registry: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Java: the registered LifecycleModule executes real birth/growth and death dispatch."""
    monkeypatch.setattr(Config, "properties", dict(Config.properties))
    Config.set("generate.payers.loss_of_care", "false")
    for flag in (
        "ENABLE_DEATH_BY_NATURAL_CAUSES",
        "ENABLE_DEATH_BY_LOSS_OF_CARE",
        "ENABLE_PHYSIOLOGY_GENERATORS",
    ):
        monkeypatch.setattr(LifecycleModule, flag, False)
    module = next(m for m in Module.get_modules(lambda _: False) if m.name == "Lifecycle")
    assert isinstance(module, LifecycleModule)
    person = Person(77)
    person.attributes.update(
        {
            Person.GENDER: "F",
            Person.RACE: "white",
            Person.ETHNICITY: "nonhispanic",
            Person.FIRST_LANGUAGE: "english",
            Person.EDUCATION_LEVEL: 0.5,
            Person.IDENTIFIER_PASSPORT: "",
            Person.EMPLOYMENT_MODEL: Employment(0.08),
        }
    )
    birth, week = 946684800000, 604800000
    module.birth(person, birth)
    draws = person.get_count()
    assert module.process(person, birth + week) is False
    assert person.get_vital_sign(VitalSign.BMI, birth + week) > 0
    assert person.get_count() > draws
    person.record_death(birth + week, None)
    assert module.process(person, birth + 2 * week) is True


@pytest.mark.parametrize("direct_covid", [False, True])
def test_engine_core_initialization_is_reentrant(
    fresh_core_registry: None, monkeypatch: pytest.MonkeyPatch, direct_covid: bool
) -> None:
    """Java: Module class initialization creates C19 once, then a direct requested instance.

    The cold direct-C19 path has two distinct instances, as in CovidProbe's
    JVM: the registry instance and the caller's instance. Each initializes once.
    Reading the loaded registry must never initialize either one again.
    """
    calls: list[None] = []
    initialize = C19VaccineAgeDistributions.initialize

    def count_initialization() -> None:
        """Instrument the real initializer without replacing its behavior."""
        calls.append(None)
        initialize()

    monkeypatch.setattr(
        C19VaccineAgeDistributions, "initialize", staticmethod(count_initialization)
    )
    direct = C19ImmunizationModule() if direct_covid else None
    modules = Module.get_modules(lambda _: False)
    registered = next(m for m in modules if isinstance(m, C19ImmunizationModule))
    assert len(calls) == (2 if direct_covid else 1)
    assert isinstance(registered, Module)
    if direct is not None:
        assert direct is not registered
    repeated = Module.get_modules(lambda _: False)
    assert repeated[0] is registered
    assert len(calls) == (2 if direct_covid else 1)
