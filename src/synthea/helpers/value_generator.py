"""Java API skeleton: ValueGenerator.java."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class ValueGenerator:
    """Java: ValueGenerator; pending T07."""

    def __init__(self, person: Person) -> None:
        """Java: ValueGenerator#ValueGenerator.

        Java overloads:
        (Person person)
        """
        self.person: Person
        raise NotImplementedError("Java: ValueGenerator#ValueGenerator — pending T07")

    def get_value(self, time: int) -> float:
        """Java: ValueGenerator#getValue.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: ValueGenerator#getValue — pending T07")
