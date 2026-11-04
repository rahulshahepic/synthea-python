"""Java API skeleton: GrowthChart.java."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.world.concepts.growth_chart_entry import GrowthChartEntry


class GrowthChart:
    """Java: GrowthChart; pending T12."""

    def __init__(
        self, chart_type: ChartType, raw_chart: dict[str, dict[str, dict[str, str]]]
    ) -> None:
        """Java: GrowthChart#GrowthChart.

        Java overloads:
        (ChartType chartType, Map rawChart)
        """
        self.chart_type: ChartType
        self.male_entries: dict[int, GrowthChartEntry]
        self.female_entries: dict[int, GrowthChartEntry]
        raise NotImplementedError("Java: GrowthChart#GrowthChart — pending T12")

    def look_up(self, age_in_months: int, gender: str, percentile: float) -> float:
        """Java: GrowthChart#lookUp.

        Java overloads:
        (int ageInMonths, String gender, double percentile)
        """
        raise NotImplementedError("Java: GrowthChart#lookUp — pending T12")

    def percentile_for(self, age_in_months: int, gender: str, value: float) -> float:
        """Java: GrowthChart#percentileFor.

        Java overloads:
        (int ageInMonths, String gender, double value)
        """
        raise NotImplementedError("Java: GrowthChart#percentileFor — pending T12")

    @staticmethod
    def calculate_z_score(percentile: float) -> float:
        """Java: GrowthChart#calculateZScore.

        Java overloads:
        (double percentile)
        """
        raise NotImplementedError("Java: GrowthChart#calculateZScore — pending T12")

    @staticmethod
    def zscore_to_percentile(zscore: float) -> float:
        """Java: GrowthChart#zscoreToPercentile.

        Java overloads:
        (double zscore)
        """
        raise NotImplementedError("Java: GrowthChart#zscoreToPercentile — pending T12")

    @staticmethod
    def load_charts() -> dict[ChartType, GrowthChart]:
        """Java: GrowthChart#loadCharts.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: GrowthChart#loadCharts — pending T12")


class ChartType(StrEnum):
    """Java: ChartType; pending T12."""

    HEIGHT = "HEIGHT"
    WEIGHT = "WEIGHT"
    BMI = "BMI"
    HEAD = "HEAD"


setattr(GrowthChart, "ChartType", ChartType)  # noqa: B010
