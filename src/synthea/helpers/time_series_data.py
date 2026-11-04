"""Java API skeleton: org/mitre/synthea/helpers/TimeSeriesData.java."""

from __future__ import annotations


class TimeSeriesData:
    """Java: TimeSeriesData.java#TimeSeriesData."""

    def __init__(
        self, values_or_period: list[float] | float | int, period: float | None = None
    ) -> None:
        """Java: TimeSeriesData#TimeSeriesData; pending T06."""
        self.values: list[object] = []
        self.period: float = 0.0
        raise NotImplementedError("Java: TimeSeriesData#TimeSeriesData — pending T06")

    def get_values(self) -> list[float]:
        """Java: TimeSeriesData#getValues; pending T06."""
        raise NotImplementedError("Java: TimeSeriesData#getValues — pending T06")

    def set_values(self, values: list[float]) -> None:
        """Java: TimeSeriesData#setValues; pending T06."""
        raise NotImplementedError("Java: TimeSeriesData#setValues — pending T06")

    def get_period(self) -> float:
        """Java: TimeSeriesData#getPeriod; pending T06."""
        raise NotImplementedError("Java: TimeSeriesData#getPeriod — pending T06")

    def set_period(self, period: float) -> None:
        """Java: TimeSeriesData#setPeriod; pending T06."""
        raise NotImplementedError("Java: TimeSeriesData#setPeriod — pending T06")

    def add_value(self, value: float) -> bool:
        """Java: TimeSeriesData#addValue; pending T06."""
        raise NotImplementedError("Java: TimeSeriesData#addValue — pending T06")
