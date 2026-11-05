"""TimeSeriesData port.

Java: org.mitre.synthea.helpers.TimeSeriesData — a list of Double values
plus a sampling period in seconds.
"""

from __future__ import annotations


class TimeSeriesData:
    """Java: org.mitre.synthea.helpers.TimeSeriesData."""

    def __init__(
        self,
        period_or_values_or_initial_capacity: float | list[float] | int,
        period: float | None = None,
    ) -> None:
        """Java: TimeSeriesData#TimeSeriesData.

        Java overloads:
        (double period)
        (List values, double period) — the list is stored by reference.
        (int initialCapacity, double period) — capacity is a Java ArrayList
            sizing hint with no Python counterpart; a negative capacity
            raises ValueError (Java: IllegalArgumentException).
        """
        self.values: list[float]
        self.period: float
        if isinstance(period_or_values_or_initial_capacity, list):
            if period is None:
                raise TypeError("TimeSeriesData(List, double) requires a period")
            self.set_values(period_or_values_or_initial_capacity)
            self.set_period(period)
        elif period is not None:
            capacity = period_or_values_or_initial_capacity
            if not isinstance(capacity, int) or isinstance(capacity, bool):
                raise TypeError("TimeSeriesData(int, double) requires an int capacity")
            if capacity < 0:
                raise ValueError(f"Illegal Capacity: {capacity}")
            self.set_values([])
            self.set_period(period)
        else:
            self.set_values([])
            self.set_period(float(period_or_values_or_initial_capacity))

    def get_values(self) -> list[float]:
        """Java: TimeSeriesData#getValues.

        Java overloads:
        ()
        """
        return self.values

    def set_values(self, values: list[float]) -> None:
        """Java: TimeSeriesData#setValues.

        Java overloads:
        (List values)
        """
        self.values = values

    def get_period(self) -> float:
        """Java: TimeSeriesData#getPeriod.

        Java overloads:
        ()
        """
        return self.period

    def set_period(self, period: float) -> None:
        """Java: TimeSeriesData#setPeriod.

        Java overloads:
        (double period)
        """
        self.period = period

    def add_value(self, value: float) -> bool:
        """Java: TimeSeriesData#addValue — ArrayList.add, always true.

        Java overloads:
        (double value)
        """
        self.values.append(value)
        return True
