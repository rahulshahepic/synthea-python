"""Java API skeleton: BloodPressureValueGenerator.java."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.engine.components import Range
    from synthea.world.agents.person import Person


class BloodPressureValueGenerator:
    """Java: BloodPressureValueGenerator; pending T21."""

    HYPERTENSIVE_SYS_BP_RANGE: ClassVar[list[int]]  # Java initialization deferred to T21.
    HYPERTENSIVE_DIA_BP_RANGE: ClassVar[list[int]]  # Java initialization deferred to T21.
    NORMAL_SYS_BP_RANGE: ClassVar[list[int]]  # Java initialization deferred to T21.
    NORMAL_DIA_BP_RANGE: ClassVar[list[int]]  # Java initialization deferred to T21.
    HTN_DRUG_IMPACTS: ClassVar[dict[str, SysDias]]  # Java initialization deferred to T21.
    ONE_YEAR: ClassVar[int] = 31536000000
    CYCLE_TIME: ClassVar[int] = 43200000

    def __init__(self, person: Person, sys_dias: SysDias) -> None:
        """Java: BloodPressureValueGenerator#BloodPressureValueGenerator.

        Java overloads:
        (Person person, SysDias sysDias)
        """
        self.cached_value: float
        self.cache_time: int
        self.sys_dias: SysDias
        raise NotImplementedError(
            "Java: BloodPressureValueGenerator#BloodPressureValueGenerator — pending T21"
        )

    def get_value(self, time: int) -> float:
        """Java: BloodPressureValueGenerator#getValue.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: BloodPressureValueGenerator#getValue — pending T21")

    @staticmethod
    def get_drug_impact(
        person: Person, drug: str, sys_dias: SysDias, impact_range: Range[float]
    ) -> float:
        """Java: BloodPressureValueGenerator#getDrugImpact.

        Java overloads:
        (Person person, String drug, SysDias sysDias, Range impactRange)
        """
        raise NotImplementedError("Java: BloodPressureValueGenerator#getDrugImpact — pending T21")

    def calculate_baseline(self, person: Person) -> float:
        """Java: BloodPressureValueGenerator#calculateBaseline.

        Java overloads:
        (Person person)
        """
        raise NotImplementedError(
            "Java: BloodPressureValueGenerator#calculateBaseline — pending T21"
        )

    def get_lifestyle_impacts(self, person: Person, baseline: float, time: int) -> float:
        """Java: BloodPressureValueGenerator#getLifestyleImpacts.

        Java overloads:
        (Person person, double baseline, long time)
        """
        raise NotImplementedError(
            "Java: BloodPressureValueGenerator#getLifestyleImpacts — pending T21"
        )

    def get_medication_impacts(self, person: Person) -> float:
        """Java: BloodPressureValueGenerator#getMedicationImpacts.

        Java overloads:
        (Person person)
        """
        raise NotImplementedError(
            "Java: BloodPressureValueGenerator#getMedicationImpacts — pending T21"
        )

    def get_variation(self, person: Person, time: int) -> float:
        """Java: BloodPressureValueGenerator#getVariation.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: BloodPressureValueGenerator#getVariation — pending T21")


class SysDias(StrEnum):
    """Java: SysDias; pending T21."""

    SYSTOLIC = "SYSTOLIC"
    DIASTOLIC = "DIASTOLIC"


setattr(BloodPressureValueGenerator, "SysDias", SysDias)  # noqa: B010
