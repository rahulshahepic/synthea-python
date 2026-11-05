"""Java API skeleton: Distribution.java."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class Distribution:
    """Java: Distribution; pending T07."""

    def __init__(self) -> None:
        """Java: Distribution#Distribution.

        Java overloads:
        ()
        """
        self.kind: Kind
        self.round: bool
        self.parameters: dict[str, float]
        raise NotImplementedError("Java: Distribution#Distribution — pending T07")

    def generate(self, person: Person) -> float:
        """Java: Distribution#generate.

        Java overloads:
        (Person person)
        """
        raise NotImplementedError("Java: Distribution#generate — pending T07")

    def validate(self) -> bool:
        """Java: Distribution#validate.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Distribution#validate — pending T07")


class Kind(StrEnum):
    """Java: Kind; pending T07."""

    EXACT = "EXACT"
    GAUSSIAN = "GAUSSIAN"
    UNIFORM = "UNIFORM"
    EXPONENTIAL = "EXPONENTIAL"
    TRIANGULAR = "TRIANGULAR"


setattr(Distribution, "Kind", Kind)  # noqa: B010
