"""Java API skeleton: C19Vaccine.java."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.helpers.synced_enumerated_distro import SyncedEnumeratedDistro
    from synthea.world.agents.person import Person


class C19Vaccine:
    """Java: C19Vaccine; pending T24."""

    EUAs: ClassVar[dict[EUASet, C19Vaccine]] = {}
    shotSelector: ClassVar[SyncedEnumeratedDistro[EUASet]]  # Java initialization deferred to T24.

    def __init__(
        self,
        display: str,
        cvx: str,
        two_dose: bool,
        usage_percentage: float,
        time_between_doses: int,
    ) -> None:
        """Java: C19Vaccine#C19Vaccine.

        Java overloads:
        (String display, String cvx, boolean twoDose, double usagePercentage, long
        timeBetweenDoses)
        """
        self.display: str
        self.cvx: str
        self.two_dose: bool
        self.usage_percentage: float
        self.time_between_doses: int
        raise NotImplementedError("Java: C19Vaccine#C19Vaccine — pending T24")

    @staticmethod
    def initialize() -> None:
        """Java: C19Vaccine#initialize.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: C19Vaccine#initialize — pending T24")

    @staticmethod
    def select_shot(person: Person) -> EUASet:
        """Java: C19Vaccine#selectShot.

        Java overloads:
        (Person person)
        """
        raise NotImplementedError("Java: C19Vaccine#selectShot — pending T24")

    def get_display(self) -> str:
        """Java: C19Vaccine#getDisplay.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: C19Vaccine#getDisplay — pending T24")

    def set_display(self, display: str) -> None:
        """Java: C19Vaccine#setDisplay.

        Java overloads:
        (String display)
        """
        raise NotImplementedError("Java: C19Vaccine#setDisplay — pending T24")

    def get_cvx(self) -> str:
        """Java: C19Vaccine#getCvx.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: C19Vaccine#getCvx — pending T24")

    def set_cvx(self, cvx: str) -> None:
        """Java: C19Vaccine#setCvx.

        Java overloads:
        (String cvx)
        """
        raise NotImplementedError("Java: C19Vaccine#setCvx — pending T24")

    def is_two_dose(self) -> bool:
        """Java: C19Vaccine#isTwoDose.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: C19Vaccine#isTwoDose — pending T24")

    def set_two_dose(self, two_dose: bool) -> None:
        """Java: C19Vaccine#setTwoDose.

        Java overloads:
        (boolean twoDose)
        """
        raise NotImplementedError("Java: C19Vaccine#setTwoDose — pending T24")

    def get_usage_percentage(self) -> float:
        """Java: C19Vaccine#getUsagePercentage.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: C19Vaccine#getUsagePercentage — pending T24")

    def set_usage_percentage(self, usage_percentage: float) -> None:
        """Java: C19Vaccine#setUsagePercentage.

        Java overloads:
        (double usagePercentage)
        """
        raise NotImplementedError("Java: C19Vaccine#setUsagePercentage — pending T24")

    def get_time_between_doses(self) -> int:
        """Java: C19Vaccine#getTimeBetweenDoses.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: C19Vaccine#getTimeBetweenDoses — pending T24")

    def set_time_between_doses(self, time_between_doses: int) -> None:
        """Java: C19Vaccine#setTimeBetweenDoses.

        Java overloads:
        (long timeBetweenDoses)
        """
        raise NotImplementedError("Java: C19Vaccine#setTimeBetweenDoses — pending T24")


class EUASet(StrEnum):
    """Java: EUASet; pending T24."""

    PFIZER = "PFIZER"
    MODERNA = "MODERNA"
    JANSSEN = "JANSSEN"


setattr(C19Vaccine, "EUASet", EUASet)  # noqa: B010
