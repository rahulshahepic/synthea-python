"""Java: org.mitre.synthea.modules.QualityOfLifeModule."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, ClassVar, cast

from synthea.engine.module import Module
from synthea.helpers.simple_csv import SimpleCSV
from synthea.helpers.utilities import Utilities
from synthea.javacompat.collections import JavaHashMap
from synthea.modules.calculators.ascvd import Inventory, _inventory
from synthea.world.concepts.growth_chart_entry import _java_exp, _java_pow

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import Entry, HealthRecord


class DisabilityWeight:
    """Java: QualityOfLifeModule.DisabilityWeight."""

    def __init__(self, values: dict[str, str]) -> None:
        """Java: DisabilityWeight#DisabilityWeight."""
        self.low: float = self.parse_double(values.get("LOW", "0.0"))
        self.medium: float = self.parse_double(values.get("MED", "0.0"))
        self.high: float = self.parse_double(values.get("HIGH", "0.0"))

    def get_weight(self, percentage_of_covered_care: float) -> float:
        """Java: DisabilityWeight#getWeight."""
        return self.triangular_distribution(1 - percentage_of_covered_care)

    def triangular_distribution(self, position: float) -> float:
        """Java: DisabilityWeight#triangularDistribution, with IEEE division for equal bounds."""
        numerator, denominator = self.medium - self.low, self.high - self.low
        f = (
            numerator / denominator
            if denominator != 0
            else (math.nan if numerator == 0 else math.copysign(math.inf, numerator))
        )
        if position < f:
            radicand = position * (self.high - self.low) * (self.medium - self.low)
            return self.low + (math.sqrt(radicand) if radicand >= 0 else math.nan)
        radicand = (1 - position) * (self.high - self.low) * (self.high - self.medium)
        return self.high - (math.sqrt(radicand) if radicand >= 0 else math.nan)

    def parse_double(self, value: str | None) -> float:
        """Java: DisabilityWeight#parseDouble."""
        return 0.0 if value is None or value == "" else float(value)


class QualityOfLifeModule(Module):
    """Java: QualityOfLifeModule annual QALY/DALY/QOLS calculation."""

    disabilityWeights: ClassVar[dict[str, DisabilityWeight]]
    QALY: ClassVar[str] = "QALY"
    DALY: ClassVar[str] = "DALY"
    QOLS: ClassVar[str] = "QOLS"

    def __init__(self) -> None:
        """Java: QualityOfLifeModule#QualityOfLifeModule."""
        super().__init__()
        self.name = "Quality of Life"

    def clone(self) -> Module:
        """Java: QualityOfLifeModule#clone."""
        return self

    def process(self, person: Person, time: int) -> bool:  # type: ignore[override]
        """Java: QualityOfLifeModule#process; LinkedHashMap integer years retain insertion order."""
        c = QualityOfLifeModule
        if c.QALY not in person.attributes:
            for name in (c.QALY, c.DALY, c.QOLS):
                person.attributes[name] = {}
        qalys = cast(dict[int, float], person.attributes[c.QALY])
        dalys = cast(dict[int, float], person.attributes[c.DALY])
        qols = cast(dict[int, float], person.attributes[c.QOLS])
        year = Utilities.get_year(time)
        if year not in qalys:
            values = c.calculate(person, time)
            dalys[year], qalys[year], qols[year] = values
            person.attributes["most-recent-daly"] = values[0]
            person.attributes["most-recent-qaly"] = values[1]
        return False

    @staticmethod
    def load_disability_weights() -> dict[str, DisabilityWeight]:
        """Java: QualityOfLifeModule#loadDisabilityWeights."""
        result: dict[str, DisabilityWeight] = cast(
            dict[str, DisabilityWeight], JavaHashMap[str, DisabilityWeight]()
        )
        for row in SimpleCSV.parse_line_by_line(
            Utilities.read_resource("gbd_disability_weights.csv")
        ):
            result[row["CODE"]] = DisabilityWeight(row)
        return result

    @staticmethod
    def calculate(person: Person, stop: int) -> list[float]:
        """Java: QualityOfLifeModule#calculate, including integer division of care counts."""
        c = QualityOfLifeModule
        age = person.age_in_years(stop)
        birthdate = cast(int, person.attributes["birthdate"])
        yll, yld = 0.0, 0.0
        if not person.alive(stop):
            yll = (
                (0.00006 * _java_pow(age, 3))
                - (0.0054 * _java_pow(age, 2))
                - (0.8502 * age)
                + 86.16
            )
        conditions: list[Entry] = []

        def collect(record: HealthRecord) -> int:
            """Java: calculate's covered/uncovered record accumulation loops."""
            medications = procedures = immunizations = encounters = 0
            for encounter in record.encounters:
                conditions.extend(encounter.conditions)
                medications += len(encounter.medications)
                procedures += len(encounter.procedures)
                immunizations += len(encounter.immunizations)
                encounters += 1
            return encounters + medications + procedures + immunizations

        assert person.default_record is not None
        covered = collect(person.default_record)
        uncovered = 0
        if person.loss_of_care_enabled:
            assert person.loss_of_care_record is not None
            uncovered = collect(person.loss_of_care_record)
        covered = max(covered, 1)
        fraction = float(covered // (covered + uncovered))
        disability_weight = 0.0
        for i in range(age + 1):
            start = birthdate + int(365.25 * i) * 86400000
            end = birthdate + int(365.25 * (i + 1) - 1) * 86400000
            disability_weight = 0.0
            for condition in c.conditions_in_year(conditions, start, end):
                disability_weight += c.disabilityWeights[condition.codes[0].code].get_weight(
                    fraction
                )
            disability_weight = min(1.0, c.weight(disability_weight, i + 1))
            yld += disability_weight
        return [yll + yld, age - yld, 1 - disability_weight]

    @staticmethod
    def conditions_in_year(conditions: list[Entry], start: int, stop: int) -> list[Entry]:
        """Java: QualityOfLifeModule#conditionsInYear; preserves its start comparison."""
        return [
            condition
            for condition in conditions
            if condition.codes[0].code in QualityOfLifeModule.disabilityWeights
            and start >= condition.start
            and condition.start <= stop
            and (condition.stop > start or condition.stop == 0)
        ]

    @staticmethod
    def weight(disability_weight: float, age: int) -> float:
        """Java: QualityOfLifeModule#weight, preserving multiplication order."""
        return (0.1658 * age * _java_exp(-0.04 * age)) * disability_weight

    @staticmethod
    def inventory_attributes(attributes: dict[str, Inventory]) -> None:
        """Java: QualityOfLifeModule#inventoryAttributes."""
        for key in (QualityOfLifeModule.QALY, QualityOfLifeModule.DALY, QualityOfLifeModule.QOLS):
            _inventory(
                attributes, "QualityOfLifeModule", key, True, True, "LinkedHashMap<Integer, Double>"
            )
        _inventory(attributes, "QualityOfLifeModule", "birthdate", True, False, None)
        for key in ("most-recent-daly", "most-recent-qaly"):
            _inventory(attributes, "QualityOfLifeModule", key, False, True, "Numeric")


QualityOfLifeModule.disabilityWeights = QualityOfLifeModule.load_disability_weights()
setattr(QualityOfLifeModule, "DisabilityWeight", DisabilityWeight)  # noqa: B010
