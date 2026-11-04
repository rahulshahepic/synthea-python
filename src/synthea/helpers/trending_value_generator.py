"""Java API skeleton: TrendingValueGenerator.java."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class TrendingValueGenerator:
    """Java: TrendingValueGenerator; pending T07."""

    def __init__(
        self,
        person: Person,
        standard_deviation: float,
        begin_mean: float,
        end_mean: float,
        begin_time: int,
        end_time: int,
        minimum_value: float,
        maximum_value: float,
    ) -> None:
        """Java: TrendingValueGenerator#TrendingValueGenerator.

        Java overloads:
        (Person person, double standardDeviation, double beginMean, double endMean, long
        beginTime, long endTime, Double minimumValue, Double maximumValue)
        """
        self.standard_deviation: float
        self.minimum_value: float
        self.maximum_value: float
        self.begin_mean: float
        self.end_mean: float
        self.begin_time: int
        self.end_time: int
        raise NotImplementedError(
            "Java: TrendingValueGenerator#TrendingValueGenerator — pending T07"
        )

    def get_begin_time(self) -> int:
        """Java: TrendingValueGenerator#getBeginTime.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: TrendingValueGenerator#getBeginTime — pending T07")

    def get_end_time(self) -> int:
        """Java: TrendingValueGenerator#getEndTime.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: TrendingValueGenerator#getEndTime — pending T07")

    def get_value(self, time: int) -> float:
        """Java: TrendingValueGenerator#getValue.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: TrendingValueGenerator#getValue — pending T07")

    def next_value(self, mean: float) -> float:
        """Java: TrendingValueGenerator#nextValue.

        Java overloads:
        (double mean)
        """
        raise NotImplementedError("Java: TrendingValueGenerator#nextValue — pending T07")

    def to_string(self) -> str:
        """Java: TrendingValueGenerator#toString.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: TrendingValueGenerator#toString — pending T07")
