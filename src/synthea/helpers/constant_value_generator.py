"""Java: org.mitre.synthea.helpers.ConstantValueGenerator."""

from __future__ import annotations

from typing import TYPE_CHECKING

from synthea.helpers.value_generator import ValueGenerator

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class ConstantValueGenerator(ValueGenerator):
    """Java: org.mitre.synthea.helpers.ConstantValueGenerator."""

    def __init__(self, person: Person, value: float) -> None:
        """Java: ConstantValueGenerator#ConstantValueGenerator(Person, double)."""
        super().__init__(person)
        self.value: float = value

    def get_value(self, time: int) -> float:
        """Java: ConstantValueGenerator#getValue(long)."""
        return self.value
