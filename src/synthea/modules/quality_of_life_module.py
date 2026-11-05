"""Java API skeleton: QualityOfLifeModule.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Protocol

if TYPE_CHECKING:
    from synthea.engine.module import Module
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import Entry

    class Inventory(Protocol):
        """Java boundary type: Inventory; external to the mapped Python port."""


class QualityOfLifeModule:
    """Java: QualityOfLifeModule; pending T23."""

    disabilityWeights: ClassVar[dict[str, DisabilityWeight]]  # Java initialization deferred to T23.
    QALY: ClassVar[str] = "QALY"
    DALY: ClassVar[str] = "DALY"
    QOLS: ClassVar[str] = "QOLS"

    def __init__(self) -> None:
        """Java: QualityOfLifeModule#QualityOfLifeModule.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: QualityOfLifeModule#QualityOfLifeModule — pending T23")

    def clone(self) -> Module:
        """Java: QualityOfLifeModule#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: QualityOfLifeModule#clone — pending T23")

    def process(self, person: Person, time: int) -> bool:
        """Java: QualityOfLifeModule#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: QualityOfLifeModule#process — pending T23")

    @staticmethod
    def load_disability_weights() -> dict[str, DisabilityWeight]:
        """Java: QualityOfLifeModule#loadDisabilityWeights.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: QualityOfLifeModule#loadDisabilityWeights — pending T23")

    @staticmethod
    def calculate(person: Person, stop: int) -> list[float]:
        """Java: QualityOfLifeModule#calculate.

        Java overloads:
        (Person person, long stop)
        """
        raise NotImplementedError("Java: QualityOfLifeModule#calculate — pending T23")

    @staticmethod
    def conditions_in_year(conditions: list[Entry], start: int, stop: int) -> list[Entry]:
        """Java: QualityOfLifeModule#conditionsInYear.

        Java overloads:
        (List conditions, long start, long stop)
        """
        raise NotImplementedError("Java: QualityOfLifeModule#conditionsInYear — pending T23")

    @staticmethod
    def weight(disability_weight: float, age: int) -> float:
        """Java: QualityOfLifeModule#weight.

        Java overloads:
        (double disabilityWeight, int age)
        """
        raise NotImplementedError("Java: QualityOfLifeModule#weight — pending T23")

    @staticmethod
    def inventory_attributes(attributes: dict[str, Inventory]) -> None:
        """Java: QualityOfLifeModule#inventoryAttributes.

        Java overloads:
        (Map attributes)
        """
        raise NotImplementedError("Java: QualityOfLifeModule#inventoryAttributes — pending T23")


class DisabilityWeight:
    """Java: DisabilityWeight; pending T23."""

    def __init__(self, values: dict[str, str]) -> None:
        """Java: DisabilityWeight#DisabilityWeight.

        Java overloads:
        (Map values)
        """
        self.low: float
        self.medium: float
        self.high: float
        raise NotImplementedError("Java: DisabilityWeight#DisabilityWeight — pending T23")

    def get_weight(self, percentage_of_covered_care: float) -> float:
        """Java: DisabilityWeight#getWeight.

        Java overloads:
        (double percentageOfCoveredCare)
        """
        raise NotImplementedError("Java: DisabilityWeight#getWeight — pending T23")

    def triangular_distribution(self, position: float) -> float:
        """Java: DisabilityWeight#triangularDistribution.

        Java overloads:
        (double position)
        """
        raise NotImplementedError("Java: DisabilityWeight#triangularDistribution — pending T23")

    def parse_double(self, value: str) -> float:
        """Java: DisabilityWeight#parseDouble.

        Java overloads:
        (String value)
        """
        raise NotImplementedError("Java: DisabilityWeight#parseDouble — pending T23")


setattr(QualityOfLifeModule, "DisabilityWeight", DisabilityWeight)  # noqa: B010
