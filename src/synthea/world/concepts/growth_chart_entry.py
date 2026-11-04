"""Java API skeleton: GrowthChartEntry.java."""

from __future__ import annotations

from typing import ClassVar


class GrowthChartEntry:
    """Java: GrowthChartEntry; pending T12."""

    MAX_PERCENTILE: ClassVar[float] = 0.995

    def __init__(self, l_value: float, m: float, s: float) -> None:
        """Java: GrowthChartEntry#GrowthChartEntry.

        Java overloads:
        (double l, double m, double s)
        """
        self.lbox_cox: float
        self.median: float
        self.scov: float
        raise NotImplementedError("Java: GrowthChartEntry#GrowthChartEntry — pending T12")

    def zscore_for_value(self, value: float) -> float:
        """Java: GrowthChartEntry#zscoreForValue.

        Java overloads:
        (double value)
        """
        raise NotImplementedError("Java: GrowthChartEntry#zscoreForValue — pending T12")

    def percentile_for_value(self, value: float) -> float:
        """Java: GrowthChartEntry#percentileForValue.

        Java overloads:
        (double value)
        """
        raise NotImplementedError("Java: GrowthChartEntry#percentileForValue — pending T12")

    def look_up(self, percentile: float) -> float:
        """Java: GrowthChartEntry#lookUp.

        Java overloads:
        (double percentile)
        """
        raise NotImplementedError("Java: GrowthChartEntry#lookUp — pending T12")
