"""Port of the upstream JUnit test org.mitre.synthea.engine.LogicTest.

The Java test builds each Logic object with Gson from
``java/src/test/resources/generic/logic.json``; this port loads the same file
and builds the same objects with tests.logic_support.build_logic (the Gson
mirror). Java's Mockito Provider mocks and PayerManager/coverage enrolment
exist only so that Encounter/Claim construction inside Module processing
does not fail; the Python setup instead pre-seeds one real encounter and
uses the Claim/CoverageRecord doubles (see tests/logic_support.py), which
supply plumbing only.

Not ported (listed in the PR body): test_logic_with_split_record_no_duplicates
and test_logic_with_split_record_with_duplicates — both drive
Module.process with the switching_provider fixture, and Module is T19
(not yet merged). The split-record Logic behaviour they exercise is covered
by the LogicProbe parity test (tests/parity/test_logic.py).

Java's NullPointerException expectations map to TypeError in the Python
port (the same convention as Person.get_vital_sign, T09); Java's
RuntimeException expectations map to RuntimeError.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from synthea.helpers.config import Config
from synthea.helpers.utilities import Utilities
from synthea.world.agents.person import Person
from synthea.world.concepts.health_record import Code, EncounterType
from synthea.world.concepts.vital_sign import VitalSign
from tests.logic_support import LogicStateDouble, build_logic, patched_person

LOGIC_JSON = (
    Path(__file__).resolve().parents[2]
    / "java"
    / "src"
    / "test"
    / "resources"
    / "generic"
    / "logic.json"
)
TESTS = json.loads(LOGIC_JSON.read_text(encoding="utf-8"))

# Fixed reference time (2016-09-21 00:00:00 UTC); the Java test uses the wall
# clock, but every assertion is relative to `time`, so a fixed value is
# equivalent and deterministic.
TIME = 1474416000000


@pytest.fixture
def env() -> tuple[Person, int]:
    Config.set("exporter.split_records", "false")
    with patched_person(0) as person:
        # Give person an income to prevent null pointer.
        person.attributes[Person.INCOME] = 10000000
        person.attributes[Person.BIRTHDATE] = 0
        assert person.record is not None
        person.record.encounter_start(TIME, EncounterType.WELLNESS)
        yield person, TIME


def do_test(person: Person, time: int, test_name: str) -> bool:
    logic = build_logic(TESTS[test_name])
    return logic.test(person, time)


def clear_record(person: Person, time: int) -> None:
    """Java: clearRecord — initializeDefaultHealthRecords + releaseCurrentEncounter."""
    person.initialize_default_health_records()
    person.release_current_encounter(0, "")  # Java passes null; the port ignores it
    assert person.record is not None
    person.record.encounter_start(time, EncounterType.WELLNESS)


def set_patient_age(person: Person, time: int, age: int) -> None:
    now = datetime.fromtimestamp(time / 1000, tz=UTC)
    try:
        bday = now.replace(year=now.year - age)
    except ValueError:  # Feb 29 -> Feb 28, as LocalDateTime.minus(Years) does
        bday = now.replace(year=now.year - age, day=28)
    birthdate = int(bday.timestamp() * 1000)
    person.attributes[Person.BIRTHDATE] = birthdate
    person.attributes.pop(Person.BIRTHDATE_AS_LOCALDATE, None)


def test_true(env: tuple[Person, int]) -> None:
    person, time = env
    assert do_test(person, time, "trueTest") is True


def test_false(env: tuple[Person, int]) -> None:
    person, time = env
    assert do_test(person, time, "falseTest") is False


def test_gender_condition(env: tuple[Person, int]) -> None:
    person, time = env
    person.attributes[Person.GENDER] = "M"
    assert do_test(person, time, "genderIsMaleTest") is True

    person.attributes[Person.GENDER] = "F"
    assert do_test(person, time, "genderIsMaleTest") is False


def test_age_conditions_on_age_35(env: tuple[Person, int]) -> None:
    person, time = env
    set_patient_age(person, time, 35)
    assert do_test(person, time, "ageLt40Test") is True
    assert do_test(person, time, "ageLte40Test") is True
    assert do_test(person, time, "ageEq40Test") is False
    assert do_test(person, time, "ageGte40Test") is False
    assert do_test(person, time, "ageGt40Test") is False
    assert do_test(person, time, "ageNe40Test") is True


def test_age_conditions_on_age_40(env: tuple[Person, int]) -> None:
    person, time = env
    set_patient_age(person, time, 40)
    assert do_test(person, time, "ageLt40Test") is False
    assert do_test(person, time, "ageLte40Test") is True
    assert do_test(person, time, "ageEq40Test") is True
    assert do_test(person, time, "ageGte40Test") is True
    assert do_test(person, time, "ageGt40Test") is False
    assert do_test(person, time, "ageNe40Test") is False


def test_age_conditions_on_age_45(env: tuple[Person, int]) -> None:
    person, time = env
    set_patient_age(person, time, 45)
    assert do_test(person, time, "ageLt40Test") is False
    assert do_test(person, time, "ageLte40Test") is False
    assert do_test(person, time, "ageEq40Test") is False
    assert do_test(person, time, "ageGte40Test") is True
    assert do_test(person, time, "ageGt40Test") is True
    assert do_test(person, time, "ageNe40Test") is True


def test_race_exists(env: tuple[Person, int]) -> None:
    person, time = env
    person.attributes[Person.RACE] = "white"
    assert do_test(person, time, "raceExistsTest") is True

    person.attributes[Person.RACE] = "native"
    assert do_test(person, time, "raceDoesNotExistTest") is False


def _timestamp(year: int, month: int, day: int) -> int:
    """Java: TestHelper.timestamp(year, month, day, 0, 0, 0) (UTC)."""
    return int(datetime(year, month, day, tzinfo=UTC).timestamp() * 1000)


def test_date(env: tuple[Person, int]) -> None:
    person, _ = env
    time = _timestamp(2016, 9, 21)
    assert do_test(person, time, "before2016Test") is False
    assert do_test(person, time, "after2000Test") is True

    time = _timestamp(1981, 4, 28)
    assert do_test(person, time, "before2016Test") is True
    assert do_test(person, time, "after2000Test") is False

    time = _timestamp(2002, 2, 22)
    assert do_test(person, time, "before2016Test") is True
    assert do_test(person, time, "after2000Test") is True

    time = _timestamp(2000, 12, 10)
    assert do_test(person, time, "beforeSeptemberTest") is False
    assert do_test(person, time, "afterAprilTest") is True
    assert do_test(person, time, "inJulyTest") is False

    time = _timestamp(2004, 2, 8)
    assert do_test(person, time, "beforeSeptemberTest") is True
    assert do_test(person, time, "afterAprilTest") is False
    assert do_test(person, time, "inJulyTest") is False

    time = _timestamp(2012, 7, 17)
    assert do_test(person, time, "beforeSeptemberTest") is True
    assert do_test(person, time, "afterAprilTest") is True
    assert do_test(person, time, "inJulyTest") is True

    time = _timestamp(2016, 12, 30)
    assert do_test(person, time, "beforeChristmas2016Test") is False
    assert do_test(person, time, "afterIndependenceDay2000Test") is True
    assert do_test(person, time, "isHalloween2007Test") is False

    time = _timestamp(2000, 4, 4)
    assert do_test(person, time, "beforeChristmas2016Test") is True
    assert do_test(person, time, "afterIndependenceDay2000Test") is False
    assert do_test(person, time, "isHalloween2007Test") is False

    time = _timestamp(2007, 10, 31)
    assert do_test(person, time, "beforeChristmas2016Test") is True
    assert do_test(person, time, "afterIndependenceDay2000Test") is True
    assert do_test(person, time, "isHalloween2007Test") is True


def test_attribute(env: tuple[Person, int]) -> None:
    person, time = env
    attribute = "Test_Attribute_Key"

    person.attributes.pop(attribute, None)
    assert do_test(person, time, "attributeEqualTo_TestValue_Test") is False
    assert do_test(person, time, "attributeLt_String_Test") is False
    assert do_test(person, time, "attributeNilTest") is True
    assert do_test(person, time, "attributeNotNilTest") is False

    person.attributes[attribute] = "Wrong Value"
    assert do_test(person, time, "attributeEqualTo_TestValue_Test") is False
    assert do_test(person, time, "attributeLt_String_Test") is False
    assert do_test(person, time, "attributeNilTest") is False
    assert do_test(person, time, "attributeNotNilTest") is True

    person.attributes[attribute] = "TestValue"
    assert do_test(person, time, "attributeEqualTo_TestValue_Test") is True
    assert do_test(person, time, "attributeLt_String_Test") is True
    assert do_test(person, time, "attributeNilTest") is False
    assert do_test(person, time, "attributeNotNilTest") is True

    person.attributes[attribute] = 120
    assert do_test(person, time, "attributeGt100Test") is True
    assert do_test(person, time, "attributeNilTest") is False
    assert do_test(person, time, "attributeNotNilTest") is True


def test_attribute_expected_numeric_exception(env: tuple[Person, int]) -> None:
    person, time = env
    person.attributes["Test_Attribute_Key"] = "TestValue"
    with pytest.raises(RuntimeError):
        do_test(person, time, "attributeGt100Test")


def test_attribute_expected_string_exception(env: tuple[Person, int]) -> None:
    person, time = env
    person.attributes["Test_Attribute_Key"] = 120
    with pytest.raises(RuntimeError):
        do_test(person, time, "attributeEqualTo_TestValue_Test")


def test_symptoms(env: tuple[Person, int]) -> None:
    person, time = env
    person.set_symptom("Module1", "Appendicitis", "PainLevel", time, 60, False)
    assert do_test(person, time, "symptomPainLevelGt50") is True
    assert do_test(person, time, "symptomPainLevelLte80") is True

    # painlevel still 60 here
    person.set_symptom("Module2", "Appendicitis", "LackOfAppetite", time, 100, False)
    assert do_test(person, time, "symptomPainLevelGt50") is True
    assert do_test(person, time, "symptomPainLevelLte80") is True

    person.set_symptom("Module1", "Appendicitis", "PainLevel", time, 10, False)
    assert do_test(person, time, "symptomPainLevelGt50") is False
    assert do_test(person, time, "symptomPainLevelLte80") is True

    person.set_symptom("Module3", "Appicitis", "PainLevel", time, 100, False)
    assert do_test(person, time, "symptomPainLevelGt50") is True
    assert do_test(person, time, "symptomPainLevelLte80") is False


def test_vital_signs(env: tuple[Person, int]) -> None:
    person, time = env
    person.set_vital_sign(VitalSign.SYSTOLIC_BLOOD_PRESSURE, 100.0)
    assert do_test(person, time, "SystolicBloodPressureGt120") is False

    person.set_vital_sign(VitalSign.SYSTOLIC_BLOOD_PRESSURE, 140.0)
    assert do_test(person, time, "SystolicBloodPressureGt120") is True


def test_vital_sign_missing(env: tuple[Person, int]) -> None:
    person, time = env
    # starts out vital signs clear; Java expects NullPointerException
    with pytest.raises(TypeError):
        do_test(person, time, "SystolicBloodPressureGt120")


def test_missing_observation(env: tuple[Person, int]) -> None:
    person, time = env
    # starts out with no observations; Java expects NullPointerException
    with pytest.raises(TypeError):
        do_test(person, time, "mmseObservationGt22")


def test_observations(env: tuple[Person, int]) -> None:
    person, time = env
    assert person.record is not None
    mmse_code = Code("LOINC", "72107-6", "Mini Mental State Examination")

    obs = person.record.observation(time, mmse_code.code, 12)
    obs.codes.append(mmse_code)
    assert do_test(person, time, "mmseObservationGt22") is False

    clear_record(person, time)
    assert person.record is not None

    obs = person.record.observation(time, mmse_code.code, 29)
    obs.codes.append(mmse_code)
    assert do_test(person, time, "mmseObservationGt22") is True

    clear_record(person, time)
    assert person.record is not None

    value_code_false = Code("LOINC", "72107-8", "Other Observation Value")

    obs = person.record.observation(time, mmse_code.code, value_code_false)
    obs.codes.append(mmse_code)
    assert do_test(person, time, "ObservationEqValueCode") is False

    clear_record(person, time)
    assert person.record is not None

    value_code_true = Code("LOINC", "72107-7", "Some Observation Value")

    obs = person.record.observation(time, mmse_code.code, value_code_true)
    obs.codes.append(mmse_code)
    assert do_test(person, time, "ObservationEqValueCode") is True

    clear_record(person, time)
    assert person.record is not None
    assert do_test(person, time, "hasDiabetesObservation") is False

    obs = person.record.observation(time, "Blood Panel", "blah blah")
    person.attributes["Blood Test Performed"] = obs
    assert do_test(person, time, "hasDiabetesObservation") is False

    obs = person.record.observation(time, "Glucose Panel", "12345")
    person.attributes["Diabetes Test Performed"] = obs
    assert do_test(person, time, "hasDiabetesObservation") is True


def test_condition_condition(env: tuple[Person, int]) -> None:
    person, time = env
    clear_record(person, time)
    assert person.record is not None
    assert do_test(person, time, "diabetesConditionTest") is False
    assert do_test(person, time, "alzheimersConditionTest") is False

    diabetes_code = Code("SNOMED-CT", "73211009", "Diabetes mellitus")

    person.record.condition_start(time, diabetes_code.code)
    assert do_test(person, time, "diabetesConditionTest") is True
    assert do_test(person, time, "alzheimersConditionTest") is False

    time += Utilities.convert_time("years", 10)

    person.record.condition_end(time, diabetes_code.code)
    assert do_test(person, time, "diabetesConditionTest") is False

    alz_code = Code("SNOMED-CT", "26929004", "Alzheimer's disease (disorder)")

    cond = person.record.condition_start(time, alz_code.code)
    person.attributes["Alzheimer's Variant"] = cond

    assert do_test(person, time, "alzheimersConditionTest") is True


def test_allergy_condition(env: tuple[Person, int]) -> None:
    person, time = env
    clear_record(person, time)
    assert person.record is not None
    assert do_test(person, time, "penicillinAllergyTest") is False

    penicillin_code = Code("RxNorm", "7984", "Penicillin V")

    person.record.allergy_start(time, penicillin_code.code)
    assert do_test(person, time, "penicillinAllergyTest") is True

    time += Utilities.convert_time("years", 10)

    person.record.allergy_end(time, penicillin_code.code)
    assert do_test(person, time, "penicillinAllergyTest") is False


def test_careplan_condition(env: tuple[Person, int]) -> None:
    person, time = env
    assert person.record is not None
    diabetes_code = Code("SNOMED-CT", "698360004", "Diabetes self management plan")

    clear_record(person, time)
    assert person.record is not None
    assert do_test(person, time, "diabetesCarePlanTest") is False
    assert do_test(person, time, "anginaCarePlanTest") is False

    dcp = person.record.careplan_start(time, diabetes_code.code)
    dcp.codes.append(diabetes_code)
    assert do_test(person, time, "diabetesCarePlanTest") is True
    assert do_test(person, time, "anginaCarePlanTest") is False

    time += Utilities.convert_time("years", 10)

    person.record.careplan_end(
        time,
        diabetes_code.code,
        Code("SNOMED-CT", "444110003", "Type II Diabetes Mellitus Well Controlled"),
    )
    assert do_test(person, time, "diabetesCarePlanTest") is False

    angina_code = Code("SNOMED-CT", "698360004", "Diabetes self management plan")

    acp = person.record.careplan_start(time, angina_code.code)
    acp.codes.append(angina_code)
    person.attributes["Angina_CarePlan"] = acp
    assert do_test(person, time, "anginaCarePlanTest") is True


def test_ses_category(env: tuple[Person, int]) -> None:
    person, time = env
    person.attributes[Person.SOCIOECONOMIC_CATEGORY] = "High"
    assert do_test(person, time, "sesHighTest") is True
    assert do_test(person, time, "sesMiddleTest") is False
    assert do_test(person, time, "sesLowTest") is False

    person.attributes[Person.SOCIOECONOMIC_CATEGORY] = "Middle"
    assert do_test(person, time, "sesHighTest") is False
    assert do_test(person, time, "sesMiddleTest") is True
    assert do_test(person, time, "sesLowTest") is False

    person.attributes[Person.SOCIOECONOMIC_CATEGORY] = "Low"
    assert do_test(person, time, "sesHighTest") is False
    assert do_test(person, time, "sesMiddleTest") is False
    assert do_test(person, time, "sesLowTest") is True


def test_prior_state(env: tuple[Person, int]) -> None:
    person, time = env
    person.history = []  # type: ignore[assignment]
    assert do_test(person, time, "priorStateDoctorVisitTest") is False
    assert do_test(person, time, "priorStateCarePlanSinceDoctorVisitTest") is False
    assert do_test(person, time, "priorStateDoctorVisitWithin3YearsTest") is False
    assert do_test(person, time, "priorStateCarePlanSinceDoctorVisitWithin3YearsTest") is False

    state = LogicStateDouble("CarePlan", entered=time, exited=time)
    person.history.insert(0, state)  # type: ignore[arg-type]
    assert do_test(person, time, "priorStateDoctorVisitTest") is False
    assert do_test(person, time, "priorStateCarePlanSinceDoctorVisitTest") is True
    assert do_test(person, time, "priorStateDoctorVisitWithin3YearsTest") is False
    assert do_test(person, time, "priorStateCarePlanSinceDoctorVisitWithin3YearsTest") is True

    state = LogicStateDouble("DoctorVisit", entered=time, exited=time)
    person.history.insert(0, state)  # type: ignore[arg-type]
    assert do_test(person, time, "priorStateDoctorVisitTest") is True
    assert do_test(person, time, "priorStateCarePlanSinceDoctorVisitTest") is False
    assert do_test(person, time, "priorStateDoctorVisitWithin3YearsTest") is True
    assert do_test(person, time, "priorStateCarePlanSinceDoctorVisitWithin3YearsTest") is False

    time += Utilities.convert_time("years", 2)

    state = LogicStateDouble("CarePlan", entered=time, exited=time)
    person.history.insert(0, state)  # type: ignore[arg-type]
    assert do_test(person, time, "priorStateDoctorVisitTest") is True
    assert do_test(person, time, "priorStateCarePlanSinceDoctorVisitTest") is True
    assert do_test(person, time, "priorStateDoctorVisitWithin3YearsTest") is True
    assert do_test(person, time, "priorStateCarePlanSinceDoctorVisitWithin3YearsTest") is True

    time += Utilities.convert_time("years", 5)

    assert do_test(person, time, "priorStateDoctorVisitTest") is True
    assert do_test(person, time, "priorStateCarePlanSinceDoctorVisitTest") is True
    assert do_test(person, time, "priorStateDoctorVisitWithin3YearsTest") is False
    assert do_test(person, time, "priorStateCarePlanSinceDoctorVisitWithin3YearsTest") is False


def test_and_conditions(env: tuple[Person, int]) -> None:
    person, time = env
    assert do_test(person, time, "andAllTrueTest") is True
    assert do_test(person, time, "andOneFalseTest") is False
    assert do_test(person, time, "andAllFalseTest") is False


def test_or_conditions(env: tuple[Person, int]) -> None:
    person, time = env
    assert do_test(person, time, "orAllTrueTest") is True
    assert do_test(person, time, "orOneTrueTest") is True
    assert do_test(person, time, "orAllFalseTest") is False


def test_at_least_condition(env: tuple[Person, int]) -> None:
    person, time = env
    assert do_test(person, time, "atLeast3_AllTrueTest") is True
    assert do_test(person, time, "atLeast3_3TrueTest") is True
    assert do_test(person, time, "atLeast3_2TrueTest") is False
    assert do_test(person, time, "atLeast3_NoneTrueTest") is False


def test_at_most_condition(env: tuple[Person, int]) -> None:
    person, time = env
    assert do_test(person, time, "atMost2_AllTrueTest") is False
    assert do_test(person, time, "atMost2_3TrueTest") is False
    assert do_test(person, time, "atMost2_2TrueTest") is True
    assert do_test(person, time, "atMost2_NoneTrueTest") is True


def test_not_conditions(env: tuple[Person, int]) -> None:
    person, time = env
    assert do_test(person, time, "notTrueTest") is False
    assert do_test(person, time, "notFalseTest") is True
