"""Java API skeleton: ConstantValueGenerator.java."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class ConstantValueGenerator:
    """Java: ConstantValueGenerator; pending T07."""

    def __init__(self, person: Person, value: float) -> None:
        """Java: ConstantValueGenerator#ConstantValueGenerator.

        Java overloads:
        (Person person, double value)
        """
        self.value: float
        raise NotImplementedError(
            "Java: ConstantValueGenerator#ConstantValueGenerator — pending T07"
        )

    def get_value(self, time: int) -> float:
        """Java: ConstantValueGenerator#getValue.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: ConstantValueGenerator#getValue — pending T07")
