"""Support for the T24 CovidProbe parity comparisons.

Mirrors ``parity/probes/org/synthea/parity/probes/CovidProbe.java``
exactly: the same sections in the same order, the same scripted
persons, and the same dumps. Keep this file and the probe in sync.

The class-level distribution maps are reset before each run so every
run mirrors the probe's fresh JVM (Java's ``initialize()`` appends to
the static maps; without a reset a second run in the same pytest
process would double-load them, which no JVM ever does).
"""

from __future__ import annotations

from datetime import UTC, datetime

from synthea.engine.module import Module
from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.helpers.utilities import Utilities
from synthea.javacompat.collections import JavaHashMap
from synthea.javacompat.numbers import double_to_string
from synthea.modules.covid.c19_immunization_module import (
    C19ImmunizationModule,
    VaccinationStatus,
)
from synthea.modules.covid.c19_vaccine import C19Vaccine, EUASet
from synthea.modules.covid.c19_vaccine_age_distributions import (
    AgeRange,
    C19VaccineAgeDistributions,
)
from synthea.modules.covid.late_adopter_model import LateAdopterModel
from synthea.modules.immunizations import Immunizations
from synthea.world.agents.payer_manager import PayerManager
from synthea.world.agents.person import Person, Point2DDouble
from synthea.world.agents.provider import Provider
from synthea.world.geography.location import Location

START = int(datetime(2020, 12, 4, 12, 0, tzinfo=UTC).timestamp() * 1000)
END = int(datetime(2025, 12, 31, 12, 0, tzinfo=UTC).timestamp() * 1000)
WEEK = 7 * 24 * 3600 * 1000
JUNE_2021 = int(datetime(2021, 6, 1, 12, 0, tzinfo=UTC).timestamp() * 1000)
SEEDS = 200
DISPLAYS = [
    "Ages_12-15_yrs",
    "Ages_16-17_yrs",
    "Ages_18-29_yrs",
    "Ages_30-39_yrs",
    "Ages_40-49_yrs",
    "Ages_50-64_yrs",
    "Ages_65-74_yrs",
    "Ages_75+_yrs",
]

_JAVA_EXCEPTION_NAMES = {
    "RuntimeError": "RuntimeException",
    "ValueError": "IllegalArgumentException",
}


def _exception_name(exc: Exception) -> str:
    if isinstance(exc, RuntimeError) and str(exc) == "No value present":
        return "NoSuchElementException"
    return _JAVA_EXCEPTION_NAMES.get(type(exc).__name__, type(exc).__name__)


def _bool(value: bool) -> str:
    return "true" if value else "false"


def aged_person_at(seed: int, age: int, time: int) -> Person:
    """Mirror of CovidProbe.agedPersonAt."""
    person = Person(seed)
    moment = datetime.fromtimestamp(time / 1000, tz=UTC)
    birthdate = int(
        datetime(moment.year - age, moment.month, moment.day, tzinfo=UTC).timestamp() * 1000
    )
    person.attributes[Person.BIRTHDATE] = birthdate
    return person


def aged_person(seed: int, age: int) -> Person:
    """Mirror of CovidProbe.agedPerson."""
    return aged_person_at(seed, age, JUNE_2021)


def _snapshot(person: Person) -> str:
    """Mirror of CovidProbe.snapshot."""
    status = person.attributes.get(C19ImmunizationModule.C19_VACCINE_STATUS)
    vaccine = person.attributes.get(C19ImmunizationModule.C19_VACCINE)
    first = person.attributes.get(C19ImmunizationModule.C19_SCHEDULED_FIRST_SHOT)
    second = person.attributes.get(C19ImmunizationModule.C19_SCHEDULED_SECOND_SHOT)
    fully = person.attributes.get(C19ImmunizationModule.C19_FULLY_VACCINATED)
    model = person.attributes.get(C19ImmunizationModule.C19_LATE_ADOPTER_MODEL)
    status_s = status.name if isinstance(status, VaccinationStatus) else "null"
    vaccine_s = vaccine.name if isinstance(vaccine, EUASet) else "null"
    first_s = "null" if first is None else str(first)
    second_s = "null" if second is None else str(second)
    fully_s = "null" if fully is None else _bool(bool(fully))
    if isinstance(model, LateAdopterModel):
        late_s = (
            f"{double_to_string(model.get_chance_of_getting_shot())},{model.get_last_updated()}"
        )
    else:
        late_s = "null"
    return (
        f"status={status_s}|vaccine={vaccine_s}|first={first_s}|second={second_s}"
        f"|fully={fully_s}|late={late_s}"
    )


def setup_process_runtime() -> None:
    """Mirror of the probe's runtime setup before the process runs."""
    Provider.clear()
    Provider.load_providers(
        Location("Massachusetts", "Boston"), DefaultRandomNumberGenerator(12345)
    )
    PayerManager.load_no_insurance()


def run_person(module: C19ImmunizationModule, seed: int) -> list[str]:
    """Mirror of CovidProbe.runPerson for one seed."""
    lines: list[str] = []
    age = seed % 100
    person = Person(seed)
    birthdate = int(datetime(2021 - age, 1, 1, tzinfo=UTC).timestamp() * 1000)
    person.attributes[Person.BIRTHDATE] = birthdate
    person.attributes[Person.COORDINATE] = Point2DDouble(-71.0589, 42.3601)
    person.coverage.set_plan_to_no_insurance(birthdate)
    years = (END - birthdate) // Utilities.convert_time("years", 1) + 2
    for i in range(1, years + 1):
        person.coverage.new_enrollment_period(birthdate + Utilities.convert_time("years", i))
    person.coverage.set_plan_to_no_insurance(START)
    try:
        previous = _snapshot(person)
        time = START
        while time <= END:
            module.process(person, time)
            current = _snapshot(person)
            if current != previous:
                lines.append(f"T|{seed}|{time}|{current}")
                previous = current
            time += WEEK
        history = person.attributes.get(Immunizations.IMMUNIZATIONS)
        covid_history = None
        if history is not None:
            covid_history = history.get(C19ImmunizationModule.C19_PERSON_ATTRS_KEY)
        hist = "null" if covid_history is None else ",".join(str(t) for t in covid_history)
        record = person.record
        assert record is not None
        lines.append(f"F|{seed}|{_snapshot(person)}|hist={hist}|encs={len(record.encounters)}")
        for encounter in record.encounters:
            for imm in encounter.immunizations:
                codes = ";".join(f"{c.system},{c.code},{c.display}" for c in imm.codes)
                lines.append(f"I|{seed}|{imm.start}|{imm.series}|{codes}")
    except NotImplementedError:
        # A stub raise (e.g. EncounterModule.createEncounter, T22) is
        # not a probe outcome: the Java probe runs the real code. Let
        # it propagate so tests.dependency_gate can classify it.
        raise
    except Exception as exc:
        lines.append(f"P|{seed}|ERROR|{_exception_name(exc)}")
    return lines


def direct_lines() -> tuple[list[str], C19ImmunizationModule]:
    """All CovidProbe sections except the per-person process runs.

    Returns the lines and the probe's single C19ImmunizationModule
    (constructed mid-way, as in the probe, which initializes the
    distributions exactly once).
    """
    lines: list[str] = []
    lines.append(
        "C|FIRST="
        + str(C19ImmunizationModule.FIRST_POSSIBLE_SHOT_TIME)
        + "|MODERNA="
        + str(C19ImmunizationModule.MODERNA_APPROVED)
        + "|JANSSEN="
        + str(C19ImmunizationModule.JANSSEN_APPROVED)
        + "|EXPAND="
        + str(C19ImmunizationModule.EXPAND_AGE_TO_TWELVE)
        + "|LATE="
        + str(C19ImmunizationModule.LATE_ADOPTION_START_TIME)
    )

    in_ages = [0, 11, 12, 15, 16, 17, 29, 39, 49, 64, 74, 75, 100]
    for display in DISPLAYS:
        age_range = AgeRange(display)
        in_s = "".join("1" if age_range.in_(age) else "0" for age in in_ages)
        lines.append(
            f"AR|{display}|{age_range.min}|{age_range.max}|{age_range.hash_code()}|{in_s}"
            f"|eqSame={_bool(age_range.equals(AgeRange(display)))}"
            f"|eqOther={_bool(age_range.equals(AgeRange('Ages_18-29_yrs')))}"
            f"|eqNull={_bool(age_range.equals(None))}"
        )
    try:
        AgeRange("Ages_5-9_yrs")
        lines.append("AR|bad|no-error")
    except ValueError:
        lines.append("AR|bad|ERROR|IllegalArgumentException")

    module = C19ImmunizationModule()
    lines.append(f"M|{module.name}")
    for key, vaccine in C19Vaccine.EUAs.items():
        lines.append(
            f"EUA|{key.name}|{vaccine.get_display()}|{vaccine.get_cvx()}"
            f"|{_bool(vaccine.is_two_dose())}|{double_to_string(vaccine.get_usage_percentage())}"
            f"|{vaccine.get_time_between_doses()}"
        )

    prob_ages = [
        0,
        5,
        11,
        12,
        13,
        15,
        16,
        17,
        18,
        25,
        29,
        30,
        39,
        40,
        49,
        50,
        64,
        65,
        74,
        75,
        90,
        120,
    ]
    for age in prob_ages:
        person = aged_person(1000 + age, age)
        try:
            chance = C19VaccineAgeDistributions.chance_of_getting_shot(person, JUNE_2021)
            lines.append(f"PROB|{age}|{double_to_string(chance)}")
        except Exception as exc:
            lines.append(f"PROB|{age}|ERROR|{_exception_name(exc)}")

    shot_ages = [12, 14, 16, 17, 20, 29, 35, 45, 55, 70, 80, 95]
    for age in shot_ages:
        for k in range(10):
            person = aged_person(777000 + age * 100 + k, age)
            try:
                shot_time = C19VaccineAgeDistributions.select_shot_time(person, JUNE_2021)
                lines.append(f"ST|{age}|{k}|{shot_time}")
            except Exception as exc:
                lines.append(f"ST|{age}|{k}|ERROR|{_exception_name(exc)}")

    for k in range(100):
        person = aged_person(555000 + k, 40)
        lines.append(f"SS|{k}|{C19Vaccine.select_shot(person).name}")

    vaccine_times = [
        C19ImmunizationModule.FIRST_POSSIBLE_SHOT_TIME - 1,
        C19ImmunizationModule.FIRST_POSSIBLE_SHOT_TIME,
        C19ImmunizationModule.MODERNA_APPROVED - 1,
        C19ImmunizationModule.MODERNA_APPROVED,
        C19ImmunizationModule.JANSSEN_APPROVED,
        C19ImmunizationModule.JANSSEN_APPROVED + 1,
        JUNE_2021,
    ]
    vaccine_time_labels = [
        "FIRST-1",
        "FIRST",
        "MODERNA-1",
        "MODERNA",
        "JANSSEN",
        "JANSSEN+1",
        "JUNE2021",
    ]
    for t, time in enumerate(vaccine_times):
        for k in range(20):
            person = aged_person(444000 + t * 100 + k, 40)
            try:
                lines.append(
                    f"SV|{vaccine_time_labels[t]}|{k}|"
                    f"{C19ImmunizationModule.select_vaccine(person, time).name}"
                )
            except Exception as exc:
                lines.append(f"SV|{vaccine_time_labels[t]}|{k}|ERROR|{_exception_name(exc)}")

    late_start = C19ImmunizationModule.LATE_ADOPTION_START_TIME
    for age in [10, 15, 16, 40, 41, 70]:
        person = aged_person_at(333000 + age, age, late_start)
        model = LateAdopterModel(person, late_start)
        lines.append(
            f"LA|{age}|init|{double_to_string(model.get_chance_of_getting_shot())}"
            f"|{model.get_last_updated()}"
        )
        time = late_start
        for step in range(40):
            time += WEEK
            will = model.will_get_shot(person, time)
            lines.append(
                f"LA|{age}|{step}|{time}|{_bool(will)}"
                f"|{double_to_string(model.get_chance_of_getting_shot())}"
                f"|{_bool(model.is_not_getting_shot())}"
            )
            if will or model.is_not_getting_shot():
                break

    elig_times = [
        C19ImmunizationModule.FIRST_POSSIBLE_SHOT_TIME - 1,
        C19ImmunizationModule.FIRST_POSSIBLE_SHOT_TIME,
        C19ImmunizationModule.EXPAND_AGE_TO_TWELVE - 1,
        C19ImmunizationModule.EXPAND_AGE_TO_TWELVE,
        int(datetime(2022, 1, 1, 12, 0, tzinfo=UTC).timestamp() * 1000),
    ]
    elig_labels = ["FIRST-1", "FIRST", "EXPAND-1", "EXPAND", "Y2022"]
    for age in [0, 11, 12, 15, 16, 17, 65]:
        for t, time in enumerate(elig_times):
            person = aged_person_at(888000 + age, age, time)
            lines.append(
                f"EL|{age}|{elig_labels[t]}|"
                f"{_bool(C19ImmunizationModule.eligible_for_shot(person, time))}"
            )

    for age in [12, 16, 20, 35, 50, 70, 85]:
        for k in range(20):
            person = aged_person(222000 + age * 100 + k, age)
            lines.append(
                f"DC|{age}|{k}|{_bool(C19ImmunizationModule.decide_on_shot(person, JUNE_2021))}"
            )

    return lines, module


def reset_covid_statics() -> None:
    """Reset the Java-static maps so a run mirrors a fresh JVM.

    Also unloads the Module registry: in the probe's fresh JVM the
    registry loads during the probe's C19ImmunizationModule
    construction, which is what makes that construction initialize
    the distributions twice (see the production __init__).
    """
    C19VaccineAgeDistributions.rawDistributions = JavaHashMap()
    C19VaccineAgeDistributions.distributions = JavaHashMap()
    C19VaccineAgeDistributions.firstShotProbByAge = JavaHashMap()
    C19Vaccine.EUAs = {}
    C19Vaccine.shotSelector = None
    Module.modules = None


def covid_run_lines() -> list[str]:
    """Full CovidProbe mirror: direct sections, then all process runs."""
    reset_covid_statics()
    lines, module = direct_lines()
    setup_process_runtime()
    for seed in range(SEEDS):
        lines.extend(run_person(module, seed))
    return lines
