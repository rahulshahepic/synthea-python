"""Java: org.mitre.synthea.world.concepts.GrowthChartEntry."""

from __future__ import annotations

import math
from typing import ClassVar

from synthea.world.concepts.growth_chart import GrowthChart


class GrowthChartEntry:
    """Java: GrowthChartEntry."""

    MAX_PERCENTILE: ClassVar[float] = 0.995

    def __init__(self, l: float, m: float, s: float) -> None:  # noqa: E741
        """Java: GrowthChartEntry#GrowthChartEntry."""
        self.lbox_cox = l
        self.median = m
        self.scov = s

    def zscore_for_value(self, value: float) -> float:
        """Java: GrowthChartEntry#zscoreForValue."""
        if self.lbox_cox == 0:
            return math.log(value / self.median) / self.scov
        return (math.pow(value / self.median, self.lbox_cox) - 1) / (self.lbox_cox * self.scov)

    def percentile_for_value(self, value: float) -> float:
        """Java: GrowthChartEntry#percentileForValue."""
        return GrowthChart.zscore_to_percentile(self.zscore_for_value(value))

    def look_up(self, percentile: float) -> float:
        """Java: GrowthChartEntry#lookUp."""
        percentile_to_use = self.MAX_PERCENTILE if percentile > self.MAX_PERCENTILE else percentile
        z = GrowthChart.calculate_z_score(percentile_to_use)
        if self.lbox_cox == 0:
            return self.median * math.exp(self.scov * z)
        expression_term = self.lbox_cox * self.scov * z
        return self.median * math.pow(1 + expression_term, 1.0 / self.lbox_cox)
