"""Java: org.mitre.synthea.modules.BloodPressureValueGenerator."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, ClassVar, cast

from synthea.engine.components import Range
from synthea.helpers.simple_csv import SimpleCSV
from synthea.helpers.utilities import Utilities
from synthea.helpers.value_generator import ValueGenerator
from synthea.javacompat.numbers import idiv
from synthea.world.concepts.biometrics_config import BiometricsConfig
from synthea.world.concepts.health_record import CarePlan

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class SysDias(StrEnum):
    """Java: BloodPressureValueGenerator.SysDias."""

    SYSTOLIC = "SYSTOLIC"
    DIASTOLIC = "DIASTOLIC"


def _load_drug_impacts() -> dict[str, dict[SysDias, Range[float]]]:
    """Java: BloodPressureValueGenerator static initializer (Guava LinkedHashMap rows)."""
    impacts: dict[str, dict[SysDias, Range[float]]] = {}
    for row in SimpleCSV.parse(Utilities.read_resource("htn_drugs.csv")):
        code = row["RxNorm"]
        for kind, prefix in ((SysDias.SYSTOLIC, "Systolic"), (SysDias.DIASTOLIC, "Diastolic")):
            span = Range[float]()
            span.low = float(row[prefix + " Impact Minimum"])
            span.high = float(row[prefix + " Impact Maximum"])
            impacts.setdefault(code, {})[kind] = span
    return impacts


class BloodPressureValueGenerator(ValueGenerator):
    """Java: org.mitre.synthea.modules.BloodPressureValueGenerator."""

    HYPERTENSIVE_SYS_BP_RANGE: ClassVar[list[int]] = BiometricsConfig.ints(
        "metabolic.blood_pressure.hypertensive.systolic"
    )
    HYPERTENSIVE_DIA_BP_RANGE: ClassVar[list[int]] = BiometricsConfig.ints(
        "metabolic.blood_pressure.hypertensive.diastolic"
    )
    NORMAL_SYS_BP_RANGE: ClassVar[list[int]] = BiometricsConfig.ints(
        "metabolic.blood_pressure.normal.systolic"
    )
    NORMAL_DIA_BP_RANGE: ClassVar[list[int]] = BiometricsConfig.ints(
        "metabolic.blood_pressure.normal.diastolic"
    )
    HTN_DRUG_IMPACTS: ClassVar[dict[str, dict[SysDias, Range[float]]]] = _load_drug_impacts()
    ONE_YEAR: ClassVar[int] = Utilities.convert_time("years", 1)
    CYCLE_TIME: ClassVar[int] = Utilities.convert_time("hours", 12)

    def __init__(self, person: Person, sys_dias: SysDias) -> None:
        """Java: BloodPressureValueGenerator#BloodPressureValueGenerator."""
        super().__init__(person)
        self.cached_value: float | None = None
        self.cache_time: int = 0
        self.sys_dias: SysDias = sys_dias

    def get_value(self, time: int) -> float:
        """Java: BloodPressureValueGenerator#getValue; one-timestamp cache."""
        if self.cache_time == time and self.cached_value is not None:
            return self.cached_value
        person = cast("Person", self.person)
        baseline = self.calculate_baseline(person)
        self.cached_value = (
            baseline
            + self.get_medication_impacts(person)
            + self.get_lifestyle_impacts(person, baseline, time)
            + self.get_variation(person, time)
        )
        self.cache_time = time
        return self.cached_value

    @staticmethod
    def get_drug_impact(
        person: Person, drug: str, sys_dias: SysDias, impact_range: Range[float]
    ) -> float:
        """Java: BloodPressureValueGenerator#getDrugImpact; bounds intentionally reversed."""
        impacts = cast(
            dict[tuple[str, SysDias], float] | None, person.attributes.get("htn_drug_impacts")
        )
        if impacts is None:
            impacts = {}
            person.attributes["htn_drug_impacts"] = impacts
        key = (drug, sys_dias)
        if key in impacts:
            return impacts[key]
        assert impact_range.high is not None and impact_range.low is not None
        impact = person.rand(impact_range.high, impact_range.low)
        impacts[key] = impact
        return impact

    def calculate_baseline(self, person: Person) -> float:
        """Java: BloodPressureValueGenerator#calculateBaseline."""
        hypertension = cast(bool, person.attributes.get("hypertension", False))
        severe = cast(bool, person.attributes.get("hypertension_severe", False))
        key = f"bp_baseline_{str(hypertension).lower()}_{self.sys_dias}"
        if key in person.attributes:
            return cast(float, person.attributes[key])
        if self.sys_dias == SysDias.SYSTOLIC:
            if hypertension:
                start = 1 if severe else 0
                baseline = person.rand(
                    self.HYPERTENSIVE_SYS_BP_RANGE[start], self.HYPERTENSIVE_SYS_BP_RANGE[start + 1]
                )
            else:
                baseline = person.rand(self.NORMAL_SYS_BP_RANGE)
        elif hypertension:
            baseline = person.rand(self.HYPERTENSIVE_DIA_BP_RANGE)
        else:
            baseline = person.rand(self.NORMAL_DIA_BP_RANGE)
        baseline += 1 if person.attributes.get(person.GENDER) == "M" else -1
        person.attributes[key] = baseline
        return baseline

    def get_lifestyle_impacts(self, person: Person, baseline: float, time: int) -> float:
        """Java: BloodPressureValueGenerator#getLifestyleImpacts."""
        if self.sys_dias == SysDias.SYSTOLIC:
            max_drop = -min(abs(baseline - 124), 14.0)
        else:
            max_drop = -min(abs(baseline - 78), 8.0)
        assert person.record is not None
        for code in ("443402002",):
            careplan = person.record.present.get(code)
            if careplan is not None and careplan.stop == 0:
                assert isinstance(careplan, CarePlan)
                key = "htn_trial_" + code + "_careplan_adherent"
                if key in person.attributes:
                    adherent = cast(bool, person.attributes[key])
                else:
                    adherent = person.rand() < 0.15
                    person.attributes[key] = adherent
                if adherent:
                    start = careplan.start
                    if time > start + self.ONE_YEAR:
                        return max_drop
                    if time < start:
                        return 0.0
                    return float(time - start) / float(self.ONE_YEAR) * max_drop
        return 0.0

    def get_medication_impacts(self, person: Person) -> float:
        """Java: BloodPressureValueGenerator#getMedicationImpacts; CSV row order."""
        delta = 0.0
        assert person.record is not None
        for code, spans in self.HTN_DRUG_IMPACTS.items():
            if person.record.medication_active(code):
                delta += self.get_drug_impact(person, code, self.sys_dias, spans[self.sys_dias])
        return delta

    def get_variation(self, person: Person, time: int) -> float:
        """Java: BloodPressureValueGenerator#getVariation; signed truncating division."""
        sd = 8 if self.sys_dias == SysDias.SYSTOLIC else 5
        magnitude = abs(person.rand_gaussian()) * sd
        sign = 1 if idiv(time, self.CYCLE_TIME) % 2 == 0 else -1
        return sign * magnitude


setattr(BloodPressureValueGenerator, "SysDias", SysDias)  # noqa: B010
