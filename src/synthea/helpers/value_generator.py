"""Java: org.mitre.synthea.helpers.ValueGenerator."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.engine.distribution import RandomSource


class ValueGenerator(ABC):
    """Java: org.mitre.synthea.helpers.ValueGenerator."""

    def __init__(self, person: RandomSource) -> None:
        """Java: ValueGenerator#ValueGenerator(Person)."""
        self.person: RandomSource = person

    @abstractmethod
    def get_value(self, time: int) -> float:
        """Java: ValueGenerator#getValue(long)."""
