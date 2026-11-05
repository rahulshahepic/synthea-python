"""Java: org.mitre.synthea.helpers.RandomValueGenerator."""

from __future__ import annotations

from typing import TYPE_CHECKING

from synthea.engine.distribution import Distribution, Kind
from synthea.helpers.value_generator import ValueGenerator

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class RandomValueGenerator(ValueGenerator):
    """Java: org.mitre.synthea.helpers.RandomValueGenerator."""

    def __init__(
        self, person: Person, low_or_distribution: float | Distribution, high: float | None = None
    ) -> None:
        """Java: RandomValueGenerator#RandomValueGenerator(Person,double,double)
        and RandomValueGenerator#RandomValueGenerator(Person,Distribution).
        """
        super().__init__(person)
        if isinstance(low_or_distribution, Distribution):
            if high is not None:
                raise TypeError("Distribution constructor does not accept high")
            self.distribution: Distribution = low_or_distribution
        else:
            if high is None:
                raise TypeError("Range constructor requires high")
            self.distribution = Distribution()
            self.distribution.kind = Kind.UNIFORM
            self.distribution.parameters = {"low": float(low_or_distribution), "high": high}

    def get_value(self, time: int) -> float:
        """Java: RandomValueGenerator#getValue(long)."""
        return self.distribution.generate(self.person)
