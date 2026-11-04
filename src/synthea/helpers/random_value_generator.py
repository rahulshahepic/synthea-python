"""Java port skeleton: java/src/main/java/org/mitre/synthea/helpers/RandomValueGenerator.java."""

from __future__ import annotations


from typing import TYPE_CHECKING

from synthea.helpers.value_generator import ValueGenerator

if TYPE_CHECKING:
    from synthea.engine.distribution import Distribution


class RandomValueGenerator(ValueGenerator):
    """Java: RandomValueGenerator; pending T07."""

    def __init__(
        self, person: object, low_or_distribution: float | Distribution, high: float | None = None
    ) -> None:
        """Java: RandomValueGenerator#RandomValueGenerator(Person,double,double|Distribution)."""
        self.distribution: Distribution | None = None
        raise NotImplementedError("Java: RandomValueGenerator#constructor — pending T07")

    def get_value(self, time: int) -> float:
        """Java: RandomValueGenerator#getValue; pending T07."""
        raise NotImplementedError("Java: RandomValueGenerator#getValue — pending T07")
