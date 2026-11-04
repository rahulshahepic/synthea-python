"""Java API skeleton: RandomValueGenerator.java."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.engine.distribution import Distribution
    from synthea.world.agents.person import Person


class RandomValueGenerator:
    """Java: RandomValueGenerator; pending T07."""

    def __init__(
        self, person: Person, low_or_distribution: float | Distribution, high: float | None = None
    ) -> None:
        """Java: RandomValueGenerator#RandomValueGenerator.

        Java overloads:
        (Person person, double low, double high)
        (Person person, Distribution distribution)
        """
        self.distribution: Distribution
        raise NotImplementedError("Java: RandomValueGenerator#RandomValueGenerator — pending T07")

    def get_value(self, time: int) -> float:
        """Java: RandomValueGenerator#getValue.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: RandomValueGenerator#getValue — pending T07")
