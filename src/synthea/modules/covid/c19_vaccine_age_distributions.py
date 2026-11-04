"""Java API skeleton:
java/src/main/java/org/mitre/synthea/modules/covid/C19VaccineAgeDistributions.java.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, ClassVar, Protocol

if TYPE_CHECKING:
    from synthea.helpers.synced_enumerated_distro import SyncedEnumeratedDistro
    from synthea.world.agents.person import Person

    class DateTimeFormatter(Protocol):
        """Java boundary type: DateTimeFormatter; external to the mapped Python port."""

    class Pair(Protocol):
        """Java boundary type: Pair; external to the mapped Python port."""


class C19VaccineAgeDistributions:
    """Java: C19VaccineAgeDistributions; pending T24."""

    DOSE_RATES_FILE: ClassVar[str] = "covid_dose_rates.csv"
    FIRST_SHOT_PROBS_FILE: ClassVar[str] = "covid_first_shot_percentage_by_age.json"
    DATE_COLUMN_HEADER: ClassVar[str] = "date"
    EXPAND_AGE_TO_TWELVE: ClassVar[date] = date(2021, 5, 10)
    CSV_DATE_FORMAT: ClassVar[DateTimeFormatter]  # Java initialization deferred to T24.
    rawDistributions: ClassVar[dict[AgeRange, list[Pair]]] = {}
    distributions: ClassVar[dict[AgeRange, SyncedEnumeratedDistro[str]]] = {}
    firstShotProbByAge: ClassVar[dict[AgeRange, float]] = {}

    def __init__(self) -> None:
        """Java: C19VaccineAgeDistributions#C19VaccineAgeDistributions.

        Java overloads:
        ()
        """
        raise NotImplementedError(
            "Java: C19VaccineAgeDistributions#C19VaccineAgeDistributions — pending T24"
        )

    @staticmethod
    def initialize() -> None:
        """Java: C19VaccineAgeDistributions#initialize.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: C19VaccineAgeDistributions#initialize — pending T24")

    @staticmethod
    def load_raw_distribution() -> None:
        """Java: C19VaccineAgeDistributions#loadRawDistribution.

        Java overloads:
        ()
        """
        raise NotImplementedError(
            "Java: C19VaccineAgeDistributions#loadRawDistribution — pending T24"
        )

    @staticmethod
    def populate_distributions() -> None:
        """Java: C19VaccineAgeDistributions#populateDistributions.

        Java overloads:
        ()
        """
        raise NotImplementedError(
            "Java: C19VaccineAgeDistributions#populateDistributions — pending T24"
        )

    @staticmethod
    def load_shot_probabilities_by_age() -> None:
        """Java: C19VaccineAgeDistributions#loadShotProbabilitiesByAge.

        Java overloads:
        ()
        """
        raise NotImplementedError(
            "Java: C19VaccineAgeDistributions#loadShotProbabilitiesByAge — pending T24"
        )

    @staticmethod
    def select_shot_time(person: Person, time: int) -> int:
        """Java: C19VaccineAgeDistributions#selectShotTime.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: C19VaccineAgeDistributions#selectShotTime — pending T24")

    @staticmethod
    def chance_of_getting_shot(person: Person, time: int) -> float:
        """Java: C19VaccineAgeDistributions#chanceOfGettingShot.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError(
            "Java: C19VaccineAgeDistributions#chanceOfGettingShot — pending T24"
        )


class AgeRange:
    """Java: AgeRange; pending T24."""

    def __init__(self, display: str) -> None:
        """Java: AgeRange#AgeRange.

        Java overloads:
        (String display)
        """
        self.min: int
        self.max: int
        self.display: str
        raise NotImplementedError("Java: AgeRange#AgeRange — pending T24")

    def equals(self, o: object) -> bool:
        """Java: AgeRange#equals.

        Java overloads:
        (Object o)
        """
        raise NotImplementedError("Java: AgeRange#equals — pending T24")

    def hash_code(self) -> int:
        """Java: AgeRange#hashCode.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: AgeRange#hashCode — pending T24")

    def in_(self, age: int) -> bool:
        """Java: AgeRange#in.

        Java overloads:
        (int age)
        """
        raise NotImplementedError("Java: AgeRange#in — pending T24")


setattr(C19VaccineAgeDistributions, "AgeRange", AgeRange)  # noqa: B010
setattr(AgeRange, "in", AgeRange.in_)
