"""Java: org.mitre.synthea.helpers.ValueGenerator."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class ValueGenerator(ABC):
    """Java: org.mitre.synthea.helpers.ValueGenerator."""

    def __init__(self, person: Person) -> None:
        """Java: ValueGenerator#ValueGenerator(Person)."""
        self.person: Person = person

    @abstractmethod
    def get_value(self, time: int) -> float:
        """Java: ValueGenerator#getValue(long)."""
