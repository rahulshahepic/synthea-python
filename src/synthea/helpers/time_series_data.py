"""Java API skeleton: TimeSeriesData.java."""

from __future__ import annotations


class TimeSeriesData:
    """Java: TimeSeriesData; pending T06."""

    def __init__(
        self,
        period_or_values_or_initial_capacity: float | list[float] | int,
        period: float | None = None,
    ) -> None:
        """Java: TimeSeriesData#TimeSeriesData.

        Java overloads:
        (double period)
        (List values, double period)
        (int initialCapacity, double period)
        """
        self.values: list[float]
        self.period: float
        raise NotImplementedError("Java: TimeSeriesData#TimeSeriesData — pending T06")

    def get_values(self) -> list[float]:
        """Java: TimeSeriesData#getValues.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: TimeSeriesData#getValues — pending T06")

    def set_values(self, values: list[float]) -> None:
        """Java: TimeSeriesData#setValues.

        Java overloads:
        (List values)
        """
        raise NotImplementedError("Java: TimeSeriesData#setValues — pending T06")

    def get_period(self) -> float:
        """Java: TimeSeriesData#getPeriod.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: TimeSeriesData#getPeriod — pending T06")

    def set_period(self, period: float) -> None:
        """Java: TimeSeriesData#setPeriod.

        Java overloads:
        (double period)
        """
        raise NotImplementedError("Java: TimeSeriesData#setPeriod — pending T06")

    def add_value(self, value: float) -> bool:
        """Java: TimeSeriesData#addValue.

        Java overloads:
        (double value)
        """
        raise NotImplementedError("Java: TimeSeriesData#addValue — pending T06")
