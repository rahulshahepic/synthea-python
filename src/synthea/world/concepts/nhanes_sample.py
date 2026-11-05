"""Java API skeleton: NHANESSample.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:

    class EnumeratedDistribution(Protocol):
        """Java boundary type: EnumeratedDistribution; external to the mapped Python port."""


class NHANESSample:
    """Java: NHANESSample; pending T12."""

    def __init__(self) -> None:
        """Java: NHANESSample#NHANESSample.

        Java overloads:
        ()
        """
        self.id: int
        self.sex: int
        self.agem: int
        self.wt: float
        self.ht: float
        self.swt: float
        self.racec: str
        self.bmi: float
        self.prob: float
        raise NotImplementedError("Java: NHANESSample#NHANESSample — pending T12")

    def to_string(self) -> str:
        """Java: NHANESSample#toString.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: NHANESSample#toString — pending T12")

    @staticmethod
    def load_samples() -> list[NHANESSample]:
        """Java: NHANESSample#loadSamples.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: NHANESSample#loadSamples — pending T12")

    @staticmethod
    def load_distribution() -> EnumeratedDistribution:
        """Java: NHANESSample#loadDistribution.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: NHANESSample#loadDistribution — pending T12")

    @staticmethod
    def load_distribution_by_sex(sex_code: int) -> EnumeratedDistribution:
        """Java: NHANESSample#loadDistributionBySex.

        Java overloads:
        (int sexCode)
        """
        raise NotImplementedError("Java: NHANESSample#loadDistributionBySex — pending T12")
