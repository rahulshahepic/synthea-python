"""JUnit port: GlobulinObservationTest (T20).

Each production comprehensive-metabolic-panel DiagnosticReport state
must generate its globulin observation (LOINC 10834-0) on the g/dL
scale: unit "g/dL" and value within [2.0, upperBound]. Mirrors the
Java setup: a directly started wellness encounter (no
EncounterModule), a mock insurance plan with zero deductible, a mock
provider, and the panel's other analytes supplied as vital signs.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from synthea.engine.module import Module
from synthea.world.agents.person import Person
from synthea.world.concepts.health_record import EncounterType
from synthea.world.concepts.healthinsurance.plan_record import PlanRecord
from synthea.world.concepts.vital_sign import VitalSign

TIME = 1577836800000  # 2020-01-01T00:00:00Z, as in the Java test

PANELS = [
    ("colorectal_cancer", "Record_CMP", 3.5),
    ("dialysis", "Record_CMP", 3.5),
    ("lung_cancer", "Record_CMP", 3.5),
    ("lung_cancer", "Record_CMP_2", 3.5),
    ("veteran_hyperlipidemia", "Record_CMP", 3.5),
    ("veteran_hyperlipidemia", "Record_CMP_2", 3.5),
    ("veteran_prostate_cancer", "Record_CMP", 3.5),
    ("gallstones", "Comprehensive_Metabolic_Panel", 4.0),
]

_VITAL_SIGNS = (
    VitalSign.GLUCOSE,
    VitalSign.UREA_NITROGEN,
    VitalSign.CREATININE,
    VitalSign.CALCIUM,
    VitalSign.SODIUM,
    VitalSign.POTASSIUM,
    VitalSign.CHLORIDE,
    VitalSign.CARBON_DIOXIDE,
)


class _MockPlan:
    """Stand-in for the Mockito InsurancePlan (deductible ZERO)."""

    def get_deductible(self) -> Decimal:
        return Decimal(0)


class _MockProvider:
    """Stand-in for the Mockito Provider."""

    def get_resource_id(self) -> str:
        return "Mock-UUID"

    def increment_prescriptions(self, year: int) -> None:
        pass

    def increment_procedures(self, year: int) -> None:
        pass

    def increment_labs(self, year: int) -> None:
        pass


@pytest.mark.parametrize(("module_path", "state_name", "upper_bound"), PANELS)
def test_globulin_unit_matches_generated_value(
    module_path: str, state_name: str, upper_bound: float
) -> None:
    """Java: GlobulinObservationTest#globulinUnitMatchesGeneratedValue."""
    module = Module.load_file(
        Path("modules") / f"{module_path}.json",
        submodule=False,
        overrides=None,
        local_files=False,
    )
    person = Person(1738)
    person.attributes[Person.BIRTHDATE] = TIME
    person.attributes[Person.GENDER] = "F"
    person.coverage.get_plan_history().add(
        PlanRecord(TIME, _MockPlan(), TIME + 1)  # type: ignore[arg-type]
    )
    person.set_provider(EncounterType.WELLNESS, _MockProvider())  # type: ignore[arg-type]
    encounter = person.record.encounter_start(TIME, EncounterType.WELLNESS)
    for vital_sign in _VITAL_SIGNS:
        person.set_vital_sign(vital_sign, 1.0)

    state = module.get_state(state_name)
    assert state is not None
    assert state.process(person, TIME) is True
    assert len(encounter.reports) == 1
    globulins = [
        observation
        for observation in encounter.reports[0].observations
        if any(code.system == "LOINC" and code.code == "10834-0" for code in observation.codes)
    ]
    assert len(globulins) == 1
    globulin = globulins[0]
    assert globulin.unit == "g/dL"
    value = float(globulin.value)  # type: ignore[arg-type]
    assert 2.0 <= value <= upper_bound
