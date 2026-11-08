"""JUnit ports for T24: the covid test classes.

Mirrors java/src/test/java/org/mitre/synthea/modules/covid/:
C19VaccineAgeDistributionsTest, LateAdopterModelTest, and
C19ImmunizationModuleTest. Two of the module tests (currentlyHasCOVID,
vaccinate) reach `EncounterModule.createEncounter` (T22, still a
stub) through the health record, so they run here in component form
with `create_encounter_double` (tests/state_doubles.py, tests only)
and a mock provider, exactly as TestHelper.buildMockProvider does in
Java. The Java vaccinate test also relies on JVM test ordering to
have populated C19Vaccine.EUAs (via the process test's module
construction); here the setup initializes them explicitly.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import cast

import pytest

from synthea.helpers.utilities import Utilities
from synthea.modules.covid.c19_immunization_module import C19ImmunizationModule, VaccinationStatus
from synthea.modules.covid.c19_vaccine import C19Vaccine, EUASet
from synthea.modules.covid.c19_vaccine_age_distributions import (
    AgeRange,
    C19VaccineAgeDistributions,
)
from synthea.modules.covid.late_adopter_model import LateAdopterModel
from synthea.modules.encounter_module import EncounterModule
from synthea.modules.immunizations import Immunizations
from synthea.world.agents.payer_manager import PayerManager
from synthea.world.agents.person import Person
from synthea.world.concepts.health_record import EncounterType
from tests.covid_support import reset_covid_statics
from tests.state_doubles import create_encounter_double


def _timestamp(year: int, month: int, day: int) -> int:
    """Java: TestHelper.timestamp(year, month, day, 0, 0, 0)."""
    return int(datetime(year, month, day, tzinfo=UTC).timestamp() * 1000)


@pytest.fixture(autouse=True)
def _fresh_statics() -> None:
    # Each Java test class runs against effectively fresh statics for
    # these assertions; reset the Java-static maps before every test.
    reset_covid_statics()


class _MockProvider:
    """Stand-in for TestHelper.buildMockProvider."""

    def increment_encounters(self, type: object, year: int) -> None:
        pass

    def choose_clinician_list(self, specialty: object, person: object) -> None:
        return None


def _build_person(birthday: int) -> Person:
    """Mirror of C19ImmunizationModuleTest.buildPerson."""
    person = Person(0)
    person.attributes[Person.BIRTHDATE] = birthday
    provider = _MockProvider()
    for encounter_type in EncounterType:
        person.set_provider(encounter_type, provider)  # type: ignore[arg-type]
    return person


# C19VaccineAgeDistributionsTest


def test_load_raw_distribution() -> None:
    """Java: C19VaccineAgeDistributionsTest#loadRawDistribution."""
    C19VaccineAgeDistributions.load_raw_distribution()
    assert len(C19VaccineAgeDistributions.rawDistributions) == 8


def test_populate_distributions() -> None:
    """Java: C19VaccineAgeDistributionsTest#populateDistributions."""
    C19VaccineAgeDistributions.load_raw_distribution()
    C19VaccineAgeDistributions.populate_distributions()
    assert len(C19VaccineAgeDistributions.distributions) == 8


def test_age_range() -> None:
    """Java: C19VaccineAgeDistributionsTest#testAgeRange."""
    age_range = AgeRange("Ages_75+_yrs")
    assert age_range.min == 75
    age_range = AgeRange("Ages_12-15_yrs")
    assert age_range.min == 12
    assert age_range.max == 15


def test_load_shot_probabilities_by_age() -> None:
    """Java: C19VaccineAgeDistributionsTest#loadShotProbabilitiesByAge."""
    C19VaccineAgeDistributions.load_shot_probabilities_by_age()
    age_range = AgeRange("Ages_75+_yrs")
    prob = C19VaccineAgeDistributions.firstShotProbByAge[age_range]
    assert prob > 0.5


def test_select_shot_time() -> None:
    """Java: C19VaccineAgeDistributionsTest#selectShotTime."""
    C19VaccineAgeDistributions.load_raw_distribution()
    C19VaccineAgeDistributions.populate_distributions()
    december_fifteenth = _timestamp(2020, 12, 15)
    birthday = _timestamp(1978, 8, 1)
    person = Person(0)
    person.attributes[Person.BIRTHDATE] = birthday
    shot_time = C19VaccineAgeDistributions.select_shot_time(person, december_fifteenth)
    assert shot_time > _timestamp(2020, 12, 15)


# LateAdopterModelTest


def test_late_adopter_will_get_shot() -> None:
    """Java: LateAdopterModelTest#willGetShot."""
    birthday = _timestamp(1978, 8, 1)
    december_fifteenth = _timestamp(2020, 12, 15)
    person = Person(0)
    person.attributes[Person.BIRTHDATE] = birthday
    model = LateAdopterModel(person, december_fifteenth)
    assert model.get_chance_of_getting_shot() == pytest.approx(0.1, abs=0.001)
    january_one = _timestamp(2021, 1, 1)
    getting_shot = model.will_get_shot(person, january_one)
    if not getting_shot:
        assert model.get_chance_of_getting_shot() == pytest.approx(0.05, abs=0.001)


def test_late_adopter_is_not_getting_shot() -> None:
    """Java: LateAdopterModelTest#isNotGettingShot."""
    birthday = _timestamp(1978, 8, 1)
    december_fifteenth = _timestamp(2020, 12, 15)
    person = Person(0)
    person.attributes[Person.BIRTHDATE] = birthday
    model = LateAdopterModel(person, december_fifteenth)
    model.set_chance_of_getting_shot(0.0001)
    assert model.is_not_getting_shot()


# C19ImmunizationModuleTest


def test_eligible_for_shot() -> None:
    """Java: C19ImmunizationModuleTest#eligibleForShot."""
    december_fifteenth = _timestamp(2020, 12, 15)
    birthday = _timestamp(1978, 8, 1)
    person = _build_person(birthday)
    assert C19ImmunizationModule.eligible_for_shot(person, december_fifteenth)
    eleven = _timestamp(2009, 8, 1)
    person.attributes[Person.BIRTHDATE] = eleven
    if Person.BIRTHDATE_AS_LOCALDATE in person.attributes:
        del person.attributes[Person.BIRTHDATE_AS_LOCALDATE]
    assert not C19ImmunizationModule.eligible_for_shot(person, december_fifteenth)


def test_select_vaccine() -> None:
    """Java: C19ImmunizationModuleTest#selectVaccine."""
    december_fifteenth = _timestamp(2020, 12, 15)
    birthday = _timestamp(1978, 8, 1)
    person = _build_person(birthday)
    assert C19ImmunizationModule.select_vaccine(person, december_fifteenth) == EUASet.PFIZER
    january_one = _timestamp(2021, 1, 1)
    assert C19ImmunizationModule.select_vaccine(person, january_one) != EUASet.JANSSEN


def test_process() -> None:
    """Java: C19ImmunizationModuleTest#process."""
    december_first = _timestamp(2020, 12, 1)
    birthday = _timestamp(2010, 8, 1)
    person = _build_person(birthday)
    module = C19ImmunizationModule()
    module.process(person, december_first)
    assert person.attributes.get(C19ImmunizationModule.C19_VACCINE_STATUS) is None
    january_one = _timestamp(2021, 1, 1)
    module.process(person, january_one)
    assert (
        person.attributes.get(C19ImmunizationModule.C19_VACCINE_STATUS)
        == VaccinationStatus.NOT_ELIGIBLE
    )
    new_birthday = _timestamp(1978, 8, 1)
    person.attributes[Person.BIRTHDATE] = new_birthday
    if Person.BIRTHDATE_AS_LOCALDATE in person.attributes:
        del person.attributes[Person.BIRTHDATE_AS_LOCALDATE]
    module.process(person, january_one)
    status = person.attributes.get(C19ImmunizationModule.C19_VACCINE_STATUS)
    assert status in (
        VaccinationStatus.WAITING_FOR_SHOT,
        VaccinationStatus.POTENTIAL_LATE_ADOPTER,
    )


@pytest.fixture()
def _encounter_double() -> None:
    # Save the raw class-dict descriptor: reading the attribute through
    # the class unwraps a staticmethod to a plain function, and putting
    # that back would leave create_encounter a plain function (the
    # skeleton signature test reads the descriptor itself).
    original = vars(EncounterModule)["create_encounter"]
    EncounterModule.create_encounter = staticmethod(create_encounter_double)  # type: ignore[method-assign]
    try:
        yield
    finally:
        EncounterModule.create_encounter = original  # type: ignore[method-assign]


def _insured_person(birthday: int, shot_time: int) -> Person:
    # Mirror of the Java tests' insurance setup: no-insurance plan from
    # the birthday, a new enrollment period every year, and the plan
    # re-set at the shot time.
    person = _build_person(birthday)
    PayerManager.load_no_insurance()
    person.coverage.set_plan_to_no_insurance(birthday)
    years = (shot_time - birthday) // Utilities.convert_time("years", 1) + 2
    for i in range(1, years + 1):
        person.coverage.new_enrollment_period(birthday + Utilities.convert_time("years", i))
    person.coverage.set_plan_to_no_insurance(shot_time)
    return person


@pytest.mark.usefixtures("_encounter_double")
def test_currently_has_covid_component() -> None:
    """Java: C19ImmunizationModuleTest#currentlyHasCOVID (component form)."""
    birthday = _timestamp(1978, 8, 1)
    december_fifteenth = _timestamp(2020, 12, 15)
    person = _insured_person(birthday, december_fifteenth)
    assert not C19ImmunizationModule.currently_has_covid(person)
    record = person.record
    assert record is not None
    record.condition_start(december_fifteenth, C19ImmunizationModule.COVID_CODE)
    assert C19ImmunizationModule.currently_has_covid(person)


@pytest.mark.usefixtures("_encounter_double")
def test_vaccinate_component() -> None:
    """Java: C19ImmunizationModuleTest#vaccinate (component form)."""
    december_fifteenth = _timestamp(2020, 12, 15)
    birthday = _timestamp(1978, 8, 1)
    C19Vaccine.initialize()
    person = _insured_person(birthday, december_fifteenth)
    person.attributes[C19ImmunizationModule.C19_VACCINE] = EUASet.PFIZER
    C19ImmunizationModule.vaccinate(person, december_fifteenth, 1)
    record = person.record
    assert record is not None
    assert len(record.encounters) == 1
    assert len(record.encounters[0].immunizations) == 1
    immunization = record.encounters[0].immunizations[0]
    assert immunization.series == 1
    assert [code.code for code in immunization.codes] == ["208"]
    history = cast("dict[str, list[int]]", person.attributes.get(Immunizations.IMMUNIZATIONS))
    shot_time = history[C19ImmunizationModule.C19_PERSON_ATTRS_KEY][0]
    assert shot_time == december_fifteenth
