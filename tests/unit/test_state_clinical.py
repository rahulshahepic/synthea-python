"""Unit tests for the clinical States (T20), ported from the upstream
JUnit StateTest (java/src/test/java/org/mitre/synthea/engine/StateTest.java).

The tests that do not need EncounterModule.createEncounter (T22) run
against real code. The two whose record calls auto-create an
encounter (gmfTwoProcedure, gmfTwoObservation) are ported as
component tests (test_state_component_*) with create_encounter_double
(tests/state_doubles.py) standing in for the T22 stub; the remaining
encounter-driven StateTest tests drive Encounter states themselves
and belong to T22's integration surface. Where Java mocks the
HealthRecord to assert no interactions, the port asserts the real
record stays empty instead.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from synthea.engine.module import Module
from synthea.modules.encounter_module import EncounterModule
from synthea.world.agents.payer_manager import PayerManager
from synthea.world.agents.person import Person
from synthea.world.concepts import vital_sign as concepts_vital_sign
from synthea.world.concepts.health_record import EncounterType
from tests.state_doubles import create_encounter_double

GENERIC = Path(__file__).resolve().parents[2] / "java" / "src" / "test" / "resources" / "generic"

# Fixed base time (2021-01-01T00:00:00Z) instead of Java's
# System.currentTimeMillis(); see tests/unit/test_state.py.
TIME = 1609459200000


class _MockProvider:
    """Stand-in for the Mockito Provider in StateTest.setup."""

    def __init__(self) -> None:
        self.prescriptions: list[int] = []
        self.procedures: list[int] = []
        self.labs: list[int] = []

    def get_resource_id(self) -> str:
        return "Mock-UUID"

    def increment_prescriptions(self, year: int) -> None:
        self.prescriptions.append(year)

    def increment_procedures(self, year: int) -> None:
        self.procedures.append(year)

    def increment_labs(self, year: int) -> None:
        self.labs.append(year)

    def increment_encounters(self, encounter_type: object, year: int) -> None:
        self.procedures.append(year)

    def choose_clinician_list(self, specialty: object, person: object) -> None:
        return None


def _fixture(filename: str) -> Module:
    """Mirror of TestHelper.getFixture: parse + construct, no overrides."""
    definition = json.loads((GENERIC / filename).read_text(encoding="utf-8"))
    return Module(definition, submodule=False)


def _person() -> Person:
    """Mirror of StateTest.setup: attributes + mock providers."""
    person = Person(0)
    person.attributes[Person.GENDER] = "F"
    person.attributes[Person.FIRST_LANGUAGE] = "spanish"
    person.attributes[Person.RACE] = "other"
    person.attributes[Person.ETHNICITY] = "hispanic"
    person.attributes[Person.OCCUPATION_LEVEL] = 1.0
    person.attributes[Person.BIRTHDATE] = TIME - 35 * 365 * 24 * 3600 * 1000
    person.history = []
    # Mirror of setup's insurance lines: no-insurance plan from
    # birthdate through TIME + 20 years (PayerManager.loadPayers in
    # Java; the port's load_no_insurance registers the same plan).
    PayerManager.load_no_insurance()
    person.coverage.set_plan_to_no_insurance(person.attributes[Person.BIRTHDATE])  # type: ignore[arg-type]
    person.coverage.set_plan_to_no_insurance(TIME + 20 * 365 * 24 * 3600 * 1000)
    mock = _MockProvider()
    for encounter_type in (
        EncounterType.AMBULATORY,
        EncounterType.WELLNESS,
        EncounterType.EMERGENCY,
        EncounterType.INPATIENT,
    ):
        person.set_provider(encounter_type, mock)  # type: ignore[arg-type]
    return person


def test_condition_onset() -> None:
    """Java: StateTest#condition_onset."""
    person = _person()
    module = _fixture("condition_onset.json")
    condition = module.get_state("Diabetes")
    assert condition is not None
    # Should pass through this state immediately without calling the record
    assert condition.process(person, TIME) is True
    assert person.record is not None
    assert len(person.record.encounters) == 0
    assert len(person.record.present) == 0


def test_condition_onset_last_onset_time() -> None:
    """Java: StateTest#condition_onset_last_onset_time."""
    person = _person()
    module = _fixture("condition_onset.json")
    condition = module.get_state("Diabetes")
    assert condition is not None
    assert condition.process(person, TIME) is True
    onset_time = person.get_onset_condition_record().get_condition_last_onset_time_from_module(
        module.name, "Diabetes mellitus"
    )
    assert onset_time is not None
    # Ensure that it ignores the blank assign_to_attribute
    assert person.attributes.get("") is None
    assert onset_time == TIME


def test_allergy_onset() -> None:
    """Java: StateTest#allergy_onset."""
    person = _person()
    module = _fixture("allergies.json")
    allergy = module.get_state("Allergy_to_Eggs")
    assert allergy is not None
    # Should pass through this state immediately without calling the record
    assert allergy.process(person, TIME) is True
    assert person.record is not None
    assert len(person.record.encounters) == 0
    assert len(person.record.present) == 0


def test_gmf_two_vital_sign() -> None:
    """Java: StateTest#gmfTwoVitalSign."""
    person = _person()
    module = _fixture("gmf_two_point_oh.json")
    vital_sign_state = module.get_state("VitalSign")
    assert vital_sign_state is not None
    vital_sign = vital_sign_state.clone()
    assert vital_sign.process(person, TIME) is True
    value = person.get_vital_sign(concepts_vital_sign.VitalSign.SYSTOLIC_BLOOD_PRESSURE, TIME)
    assert 110 <= value <= 130


def test_vitalsign() -> None:
    """Java: StateTest#vitalsign."""
    person = _person()
    module = _fixture("observation.json")
    vital_sign_state = module.get_state("VitalSign")
    assert vital_sign_state is not None
    vital_sign = vital_sign_state.clone()
    assert vital_sign.process(person, TIME) is True
    assert (
        person.get_vital_sign(concepts_vital_sign.VitalSign.SYSTOLIC_BLOOD_PRESSURE, TIME) == 120.0
    )


def test_symptoms_last_updated_time() -> None:
    """Java: StateTest#symptoms_last_updated_time."""
    person = _person()
    module = _fixture("symptom.json")
    symptom1 = module.get_state("SymptomOnset")
    assert symptom1 is not None
    assert symptom1.process(person, TIME) is True
    updated_time = person.get_symptom_last_updated_time(module.name, "Chest Pain")
    assert updated_time is not None
    assert updated_time == TIME


def test_gmf_two_symptom() -> None:
    """Java: StateTest#gmfTwoSymptom."""
    person = _person()
    module = _fixture("gmf_two_point_oh.json")
    symptom1 = module.get_state("SymptomOnset")
    assert symptom1 is not None
    assert symptom1.process(person, TIME) is True
    symptom_value = person.get_symptom("Chest Pain")
    assert 1 <= symptom_value <= 10


def test_symptoms() -> None:
    """Java: StateTest#symptoms."""
    person = _person()
    module = _fixture("symptom.json")
    symptom1 = module.get_state("SymptomOnset")
    assert symptom1 is not None
    assert symptom1.process(person, TIME) is True
    symptom_value = person.get_symptom("Chest Pain")
    assert 1 <= symptom_value <= 10

    symptom2 = module.get_state("SymptomWorsen")
    assert symptom2 is not None
    assert symptom2.process(person, TIME) is True
    assert person.get_symptom("Chest Pain") == 96


def test_symptoms50() -> None:
    """Java: StateTest#symptoms50."""
    person = _person()
    module = _fixture("symptom50.json")
    symptom50 = module.get_state("Symptom50")
    assert symptom50 is not None
    assert symptom50.process(person, TIME) is True


@pytest.fixture
def _encounter_double() -> object:
    original = EncounterModule.create_encounter
    EncounterModule.create_encounter = staticmethod(create_encounter_double)  # type: ignore[method-assign]
    try:
        yield
    finally:
        EncounterModule.create_encounter = original  # type: ignore[method-assign]


@pytest.mark.usefixtures("_encounter_double")
def test_state_component_gmf_two_procedure() -> None:
    """Java: StateTest#gmfTwoProcedure (component: createEncounter_double)."""
    person = _person()
    person.attributes.pop("Most Recent Surgery", None)
    module = _fixture("gmf_two_point_oh.json")
    appendectomy = module.get_state("Appendectomy")
    assert appendectomy is not None
    appendectomy.process(person, TIME)

    procedure = person.attributes.get("Most Recent Surgery")
    assert procedure is not None
    assert procedure.start == TIME  # type: ignore[attr-defined]
    code = procedure.codes[0]  # type: ignore[attr-defined]
    assert code.code == "6025007"
    assert code.display == "Laparoscopic appendectomy"


@pytest.mark.usefixtures("_encounter_double")
def test_state_component_gmf_two_observation() -> None:
    """Java: StateTest#gmfTwoObservation (component: createEncounter_double)."""
    person = _person()
    module = _fixture("gmf_two_point_oh.json")
    observation_state = module.get_state("Observation")
    assert observation_state is not None
    assert observation_state.process(person, TIME) is True

    assert person.record is not None
    observation = person.record.encounters[0].observations[0]
    assert observation.unit == "mg/dL"
    obs_value = float(observation.value)  # type: ignore[arg-type]
    assert obs_value > 0
    assert obs_value < 400
