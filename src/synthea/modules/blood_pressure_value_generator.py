"""Java API skeleton for blood_pressure_value_generator.py.
Java: org.mitre.synthea.modules.BloodPressureValueGenerator.
"""

from __future__ import annotations

from enum import StrEnum

from synthea.helpers.value_generator import ValueGenerator


class BloodPressureValueGenerator(ValueGenerator):
    """Java: BloodPressureValueGenerator; pending T21."""

    def __init__(self, person: object, sys_dias: SysDias) -> None:
        """Java: BloodPressureValueGenerator#BloodPressureValueGenerator; pending T21."""
        self.cachedValue: float | None = None
        self.cacheTime: int = 0
        self.sysDias: SysDias | None = None
        raise NotImplementedError("Java: BloodPressureValueGenerator — pending T21")

    def get_value(self, time: int) -> float:
        """Java: BloodPressureValueGenerator#getValue."""
        raise NotImplementedError("Java: getValue — pending T21")

    def get_drug_impact(self, *args: object, **kwargs: object) -> object:
        """Java: BloodPressureValueGenerator#getDrugImpact."""
        raise NotImplementedError("Java: getDrugImpact — pending T21")

    def calculate_baseline(self, *args: object, **kwargs: object) -> object:
        """Java: BloodPressureValueGenerator#calculateBaseline."""
        raise NotImplementedError("Java: calculateBaseline — pending T21")

    def get_lifestyle_impacts(self, *args: object, **kwargs: object) -> object:
        """Java: BloodPressureValueGenerator#getLifestyleImpacts."""
        raise NotImplementedError("Java: getLifestyleImpacts — pending T21")

    def get_medication_impacts(self, *args: object, **kwargs: object) -> object:
        """Java: BloodPressureValueGenerator#getMedicationImpacts."""
        raise NotImplementedError("Java: getMedicationImpacts — pending T21")

    def get_variation(self, *args: object, **kwargs: object) -> object:
        """Java: BloodPressureValueGenerator#getVariation."""
        raise NotImplementedError("Java: getVariation — pending T21")


class SysDias(StrEnum):
    """Java: BloodPressureValueGenerator.SysDias; pending T21."""

    SYSTOLIC = "SYSTOLIC"
    DIASTOLIC = "DIASTOLIC"
