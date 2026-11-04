"""Java API skeleton: RandomCollection.java."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.helpers.random_number_generator import RandomNumberGenerator


class RandomCollection[E]:
    """Java: RandomCollection; pending T07."""

    def __init__(self) -> None:
        """Java: RandomCollection#RandomCollection.

        Java overloads:
        ()
        """
        self.map: dict[float, E]
        self.total: float
        raise NotImplementedError("Java: RandomCollection#RandomCollection — pending T07")

    def add(self, weight: float, result: E) -> None:
        """Java: RandomCollection#add.

        Java overloads:
        (double weight, E result)
        """
        raise NotImplementedError("Java: RandomCollection#add — pending T07")

    def add_all(self, other: RandomCollection[E]) -> None:
        """Java: RandomCollection#addAll.

        Java overloads:
        (RandomCollection other)
        """
        raise NotImplementedError("Java: RandomCollection#addAll — pending T07")

    def next(self, random_or_value: RandomNumberGenerator | float) -> E:
        """Java: RandomCollection#next.

        Java overloads:
        (RandomNumberGenerator random)
        (double value)
        """
        raise NotImplementedError("Java: RandomCollection#next — pending T07")
