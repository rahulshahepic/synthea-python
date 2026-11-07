"""Java: org.mitre.synthea.export.ExporterTest (CSV-relevant parts: all of it
is years_of_history record filtering), ported test for test.

Records are scripted on a Person double with the T14 Claim plumbing double
(tests/parity/export_doubles.py): Person's real constructor needs the T16
coverage chain, and every Encounter creates a Claim (T14, still a stub).
The code under test — Exporter.filter_for_export and its helpers — is the
real production code, as are HealthRecord's scripting methods.

Skipped: testExportFilterShouldKeepCauseOfDeath — it needs
DeathModule.process (T22, still a stub). The same scenario runs in the
parity suite, gated on T22 (tests/parity/test_export_helper.py).
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from synthea.export.exporter import Exporter
from synthea.helpers.utilities import Utilities
from synthea.world.agents.person import Person
from synthea.world.concepts.health_record import Code, EncounterType, HealthRecord
from tests.unit.test_health_record import person_double

TIME = 1700000000000
YEARS_TO_KEEP = 5
DUMMY_CODE = Code("", "", "")


def years(n: int) -> int:
    return Utilities.convert_time("years", n)


@pytest.fixture(autouse=True)
def _claim_double() -> Iterator[None]:
    import synthea.world.concepts.claim as claim_module
    from tests.parity.export_doubles import ClaimDouble

    real = claim_module.Claim
    claim_module.Claim = ClaimDouble  # type: ignore[misc]
    yield
    claim_module.Claim = real


@pytest.fixture
def patient() -> tuple[Person, HealthRecord]:
    record, _rng = person_double(12345)
    person = record.person
    person.record = record
    person.records = None
    person.has_multiple_records = False
    person.attributes[Person.BIRTHDATE] = TIME - years(30)
    # Give person an income to prevent null pointer (mirrors the JUnit setup).
    person.attributes[Person.INCOME] = 100000
    return person, record


def test_export_filter_simple_cutoff(patient: tuple[Person, HealthRecord]) -> None:
    person, record = patient
    record.encounter_start(TIME - years(8), EncounterType.WELLNESS)
    record.observation(TIME - years(8), "height", 64)

    record.encounter_start(TIME - years(4), EncounterType.WELLNESS)
    record.observation(TIME - years(4), "weight", 128)

    filtered = Exporter.filter_for_export(person, YEARS_TO_KEEP, TIME)
    assert isinstance(filtered, Person)

    encounter = filtered.record.current_encounter(TIME)  # type: ignore[union-attr]
    assert len(encounter.observations) == 1
    assert encounter.observations[0].type == "weight"
    assert encounter.observations[0].start == TIME - years(4)
    assert encounter.observations[0].value == 128


def test_export_filter_should_keep_old_active_medication(
    patient: tuple[Person, HealthRecord],
) -> None:
    person, record = patient
    code = Code("SNOMED-CT", "705129", "Fake Code")

    record.encounter_start(TIME - years(10), EncounterType.AMBULATORY)
    record.medication_start(TIME - years(10), "fakeitol", True)

    record.encounter_start(TIME - years(8), EncounterType.AMBULATORY)
    med = record.medication_start(TIME - years(8), "placebitol", True)
    med.codes.append(code)

    record.medication_end(TIME - years(6), "placebitol", DUMMY_CODE)

    filtered = Exporter.filter_for_export(person, YEARS_TO_KEEP, TIME)
    assert isinstance(filtered, Person)

    encounter = filtered.record.current_encounter(TIME)  # type: ignore[union-attr]
    assert len(encounter.medications) == 1
    assert encounter.medications[0].type == "fakeitol"
    assert encounter.medications[0].start == TIME - years(10)


def test_export_filter_should_keep_medication_that_ended_during_target(
    patient: tuple[Person, HealthRecord],
) -> None:
    person, record = patient
    code = Code("SNOMED-CT", "705129", "Fake Code")

    record.encounter_start(TIME - years(10), EncounterType.AMBULATORY)
    med = record.medication_start(TIME - years(10), "dimoxinil", False)
    med.codes.append(code)
    record.medication_end(TIME - years(9), "dimoxinil", DUMMY_CODE)

    record.encounter_start(TIME - years(8), EncounterType.AMBULATORY)
    med = record.medication_start(TIME - years(8), "placebitol", True)
    med.codes.append(code)

    record.medication_end(TIME - years(4), "placebitol", DUMMY_CODE)

    filtered = Exporter.filter_for_export(person, YEARS_TO_KEEP, TIME)
    assert isinstance(filtered, Person)

    encounter = filtered.record.current_encounter(TIME)  # type: ignore[union-attr]
    assert len(encounter.medications) == 1
    assert encounter.medications[0].type == "placebitol"
    assert encounter.medications[0].start == TIME - years(8)
    assert encounter.medications[0].stop == TIME - years(4)


def test_export_filter_should_keep_old_active_careplan(
    patient: tuple[Person, HealthRecord],
) -> None:
    person, record = patient
    record.encounter_start(TIME - years(10), EncounterType.WELLNESS)
    record.careplan_start(TIME - years(10), "stop_smoking")
    record.careplan_end(TIME - years(8), "stop_smoking", DUMMY_CODE)

    record.encounter_start(TIME - years(12), EncounterType.WELLNESS)
    record.careplan_start(TIME - years(12), "healthy_diet")

    filtered = Exporter.filter_for_export(person, YEARS_TO_KEEP, TIME)
    assert isinstance(filtered, Person)

    encounter = filtered.record.current_encounter(TIME)  # type: ignore[union-attr]
    assert len(encounter.careplans) == 1
    assert encounter.careplans[0].type == "healthy_diet"
    assert encounter.careplans[0].start == TIME - years(12)


def test_export_filter_should_keep_careplan_that_ended_during_target(
    patient: tuple[Person, HealthRecord],
) -> None:
    person, record = patient
    record.encounter_start(TIME - years(10), EncounterType.WELLNESS)
    record.careplan_start(TIME - years(10), "stop_smoking")
    record.careplan_end(TIME - years(1), "stop_smoking", DUMMY_CODE)

    filtered = Exporter.filter_for_export(person, YEARS_TO_KEEP, TIME)
    assert isinstance(filtered, Person)

    encounter = filtered.record.current_encounter(TIME)  # type: ignore[union-attr]
    assert len(encounter.careplans) == 1
    assert encounter.careplans[0].type == "stop_smoking"
    assert encounter.careplans[0].start == TIME - years(10)
    assert encounter.careplans[0].stop == TIME - years(1)


def test_export_filter_should_keep_old_active_conditions(
    patient: tuple[Person, HealthRecord],
) -> None:
    person, record = patient
    record.encounter_start(TIME - years(10), EncounterType.WELLNESS)
    record.condition_start(TIME - years(10), "fakitis")
    record.condition_end(TIME - years(8), "fakitis")

    record.encounter_start(TIME - years(10), EncounterType.WELLNESS)
    record.condition_start(TIME - years(10), "fakosis")

    filtered = Exporter.filter_for_export(person, YEARS_TO_KEEP, TIME)
    assert isinstance(filtered, Person)

    encounter = filtered.record.current_encounter(TIME)  # type: ignore[union-attr]
    assert len(encounter.conditions) == 1
    assert encounter.conditions[0].type == "fakosis"
    assert encounter.conditions[0].start == TIME - years(10)


def test_export_filter_should_keep_condition_that_ended_during_target(
    patient: tuple[Person, HealthRecord],
) -> None:
    person, record = patient
    record.encounter_start(TIME - years(10), EncounterType.WELLNESS)
    record.condition_start(TIME - years(10), "boneitis")
    record.condition_end(TIME - years(2), "boneitis")

    record.encounter_start(TIME - years(10), EncounterType.WELLNESS)
    record.condition_start(TIME - years(10), "smallpox")
    record.condition_end(TIME - years(9), "smallpox")

    filtered = Exporter.filter_for_export(person, YEARS_TO_KEEP, TIME)
    assert isinstance(filtered, Person)

    encounter = filtered.record.current_encounter(TIME)  # type: ignore[union-attr]
    assert len(encounter.conditions) == 1
    assert encounter.conditions[0].type == "boneitis"
    assert encounter.conditions[0].start == TIME - years(10)


@pytest.mark.skip(
    reason="needs DeathModule.process (T22, still a stub); the parity suite "
    "carries this scenario gated on T22"
)
def test_export_filter_should_keep_cause_of_death() -> None:
    """Java: ExporterTest#testExportFilterShouldKeepCauseOfDeath."""


def test_export_filter_should_not_keep_old_stuff(patient: tuple[Person, HealthRecord]) -> None:
    person, record = patient
    record.encounter_start(TIME - years(18), EncounterType.EMERGENCY)
    record.procedure(TIME - years(20), "appendectomy")
    record.immunization(TIME - years(12), "flu_shot")
    record.observation(TIME - years(10), "weight", 123)

    filtered = Exporter.filter_for_export(person, YEARS_TO_KEEP, TIME)
    assert isinstance(filtered, Person)
    assert filtered.record.encounters == []  # type: ignore[union-attr]


def test_export_filter_should_keep_old_active_stuff(patient: tuple[Person, HealthRecord]) -> None:
    person, record = patient
    # create an old encounter with a diagnosis that isn't ended
    record.encounter_start(TIME - years(18), EncounterType.EMERGENCY)
    record.condition_start(TIME - years(18), "diabetes")

    filtered = Exporter.filter_for_export(person, YEARS_TO_KEEP, TIME)
    assert isinstance(filtered, Person)
    encounters = filtered.record.encounters  # type: ignore[union-attr]
    assert len(encounters) == 1
    assert len(encounters[0].conditions) == 1
    assert encounters[0].conditions[0].type == "diabetes"


def test_export_filter_should_filter_claim_items(patient: tuple[Person, HealthRecord]) -> None:
    person, record = patient
    record.encounter_start(TIME - years(10), EncounterType.EMERGENCY)
    record.condition_start(TIME - years(10), "something_permanent")
    record.procedure(TIME - years(10), "xray")

    assert len(record.encounters) == 1
    assert len(record.encounters[0].claim.items) == 2  # 1 condition, 1 procedure

    filtered = Exporter.filter_for_export(person, YEARS_TO_KEEP, TIME)
    assert isinstance(filtered, Person)
    # filter removes the procedure but keeps the open condition
    encounters = filtered.record.encounters  # type: ignore[union-attr]
    assert len(encounters) == 1
    assert len(encounters[0].conditions) == 1
    assert encounters[0].conditions[0].type == "something_permanent"
    assert len(record.encounters[0].claim.items) == 1
    assert record.encounters[0].claim.items[0].entry.type == "something_permanent"


def test_export_filter_should_not_keep_old_stuff_when_active_of_same_type(
    patient: tuple[Person, HealthRecord],
) -> None:
    person, record = patient
    # create old encounters with the same repeated condition, ended
    one_week = Utilities.convert_time("weeks", 1)
    for i in range(3):
        record.encounter_start(TIME - years(10 - i), EncounterType.EMERGENCY)
        record.condition_start(TIME - years(10 - i), "viral_sinusitis")
        record.condition_end(TIME - years(10 - i) + one_week, "viral_sinusitis")

    # create a recent encounter with the same condition, still active
    record.encounter_start(TIME - one_week, EncounterType.EMERGENCY)
    record.condition_start(TIME - one_week, "viral_sinusitis")

    filtered = Exporter.filter_for_export(person, YEARS_TO_KEEP, TIME)
    assert isinstance(filtered, Person)
    encounters = filtered.record.encounters  # type: ignore[union-attr]
    assert len(encounters) == 1
    assert len(encounters[0].conditions) == 1
    assert encounters[0].conditions[0].type == "viral_sinusitis"
