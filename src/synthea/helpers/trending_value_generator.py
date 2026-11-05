"""Java: org.mitre.synthea.helpers.TrendingValueGenerator."""

from __future__ import annotations

from typing import TYPE_CHECKING

from synthea.engine.distribution import _java_divide
from synthea.helpers.value_generator import ValueGenerator
from synthea.javacompat.numbers import double_to_string, to_int64

if TYPE_CHECKING:
    from synthea.engine.distribution import RandomSource


class TrendingValueGenerator(ValueGenerator):
    """Java: org.mitre.synthea.helpers.TrendingValueGenerator."""

    def __init__(
        self,
        person: RandomSource,
        standard_deviation: float,
        begin_mean: float,
        end_mean: float,
        begin_time: int,
        end_time: int,
        minimum_value: float | None,
        maximum_value: float | None,
    ) -> None:
        """Java: TrendingValueGenerator#TrendingValueGenerator (bounded Gaussian trend)."""
        super().__init__(person)
        if not standard_deviation >= 0 or (
            minimum_value is not None
            and maximum_value is not None
            and not minimum_value <= maximum_value
        ):
            raise ValueError("invalid trending generator arguments")
        self.standard_deviation: float = standard_deviation
        self.begin_mean: float = begin_mean
        self.end_mean: float = end_mean
        self.begin_time: int = begin_time
        self.end_time: int = end_time
        self.minimum_value: float | None = minimum_value
        self.maximum_value: float | None = maximum_value

    def get_begin_time(self) -> int:
        """Java: TrendingValueGenerator#getBeginTime()."""
        return self.begin_time

    def get_end_time(self) -> int:
        """Java: TrendingValueGenerator#getEndTime()."""
        return self.end_time

    def get_value(self, time: int) -> float:
        """Java: TrendingValueGenerator#getValue(long)."""
        if time < self.begin_time:
            return self.next_value(self.begin_mean)
        if time > self.end_time:
            return self.next_value(self.end_mean)
        mean = self.begin_mean + _java_divide(
            (self.end_mean - self.begin_mean) * to_int64(time - self.begin_time),
            float(to_int64(self.end_time - self.begin_time)),
        )
        return self.next_value(mean)

    def next_value(self, mean: float) -> float:
        """Java: TrendingValueGenerator#nextValue(double); rejection sampling."""
        while True:
            value = self.person.rand_gaussian() * self.standard_deviation + mean
            if (self.minimum_value is None or value >= self.minimum_value) and (
                self.maximum_value is None or value <= self.maximum_value
            ):
                return value

    def to_string(self) -> str:
        """Java: TrendingValueGenerator#toString()."""

        def fmt(value: float | None) -> str:
            return "null" if value is None else double_to_string(value)

        return (
            "TrendingValueGenerator {"
            f"standardDeviation={fmt(self.standard_deviation)}, "
            f"beginMean={fmt(self.begin_mean)}, "
            f"endMean={fmt(self.end_mean)}, "
            f"beginTime={self.begin_time}, endTime={self.end_time}, "
            f"minimumValue={fmt(self.minimum_value)}, "
            f"maximumValue={fmt(self.maximum_value)}"
            "}"
        )
