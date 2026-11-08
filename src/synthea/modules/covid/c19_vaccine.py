"""Java: C19Vaccine.java."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, ClassVar

from synthea.helpers.synced_enumerated_distro import SyncedEnumeratedDistro
from synthea.helpers.utilities import Utilities

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class C19Vaccine:
    """Java: C19Vaccine."""

    # Java: a TreeMap keyed by EUASet, so iteration is enum-ordinal order;
    # a plain dict preserves that order because initialize() inserts the
    # vaccines in ordinal order.
    EUAs: ClassVar[dict[EUASet, C19Vaccine]] = {}
    shotSelector: ClassVar[SyncedEnumeratedDistro[EUASet] | None] = None

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
        self.display: str = display
        self.cvx: str = cvx
        self.two_dose: bool = two_dose
        self.usage_percentage: float = usage_percentage
        self.time_between_doses: int = time_between_doses

    @staticmethod
    def initialize() -> None:
        """Java: C19Vaccine#initialize.

        Java overloads:
        ()
        """
        C19Vaccine.EUAs[EUASet.PFIZER] = C19Vaccine(
            "COVID-19, mRNA, LNP-S, PF, 30 mcg/0.3 mL dose",
            "208",
            True,
            0.531,
            Utilities.convert_time("days", 21),
        )
        C19Vaccine.EUAs[EUASet.MODERNA] = C19Vaccine(
            "COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5mL dose or 50 mcg/0.25mL dose",
            "207",
            True,
            0.398,
            Utilities.convert_time("days", 28),
        )
        C19Vaccine.EUAs[EUASet.JANSSEN] = C19Vaccine(
            "COVID-19 vaccine, vector-nr, rS-Ad26, PF, 0.5 mL",
            "212",
            False,
            0.071,
            0,
        )
        pmf = [(key, vaccine.get_usage_percentage()) for key, vaccine in C19Vaccine.EUAs.items()]
        C19Vaccine.shotSelector = SyncedEnumeratedDistro[EUASet](pmf)

    @staticmethod
    def select_shot(person: Person) -> EUASet:
        """Java: C19Vaccine#selectShot.

        Java overloads:
        (Person person)
        """
        if C19Vaccine.shotSelector is None:
            C19Vaccine.initialize()
        assert C19Vaccine.shotSelector is not None
        return C19Vaccine.shotSelector.synced_reseeded_sample(person)

    def get_display(self) -> str:
        """Java: C19Vaccine#getDisplay.

        Java overloads:
        ()
        """
        return self.display

    def set_display(self, display: str) -> None:
        """Java: C19Vaccine#setDisplay.

        Java overloads:
        (String display)
        """
        self.display = display

    def get_cvx(self) -> str:
        """Java: C19Vaccine#getCvx.

        Java overloads:
        ()
        """
        return self.cvx

    def set_cvx(self, cvx: str) -> None:
        """Java: C19Vaccine#setCvx.

        Java overloads:
        (String cvx)
        """
        self.cvx = cvx

    def is_two_dose(self) -> bool:
        """Java: C19Vaccine#isTwoDose.

        Java overloads:
        ()
        """
        return self.two_dose

    def set_two_dose(self, two_dose: bool) -> None:
        """Java: C19Vaccine#setTwoDose.

        Java overloads:
        (boolean twoDose)
        """
        self.two_dose = two_dose

    def get_usage_percentage(self) -> float:
        """Java: C19Vaccine#getUsagePercentage.

        Java overloads:
        ()
        """
        return self.usage_percentage

    def set_usage_percentage(self, usage_percentage: float) -> None:
        """Java: C19Vaccine#setUsagePercentage.

        Java overloads:
        (double usagePercentage)
        """
        self.usage_percentage = usage_percentage

    def get_time_between_doses(self) -> int:
        """Java: C19Vaccine#getTimeBetweenDoses.

        Java overloads:
        ()
        """
        return self.time_between_doses

    def set_time_between_doses(self, time_between_doses: int) -> None:
        """Java: C19Vaccine#setTimeBetweenDoses.

        Java overloads:
        (long timeBetweenDoses)
        """
        self.time_between_doses = time_between_doses


class EUASet(StrEnum):
    """Java: EUASet."""

    PFIZER = "PFIZER"
    MODERNA = "MODERNA"
    JANSSEN = "JANSSEN"


setattr(C19Vaccine, "EUASet", EUASet)  # noqa: B010
