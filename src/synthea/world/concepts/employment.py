"""Java API skeleton: Employment.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class Employment:
    """Java: Employment; pending T10."""

    MIN_EMPLOYMENT_STATE_LENGTH: ClassVar[int] = 6

    def __init__(self, chance_of_unemployment: float) -> None:
        """Java: Employment#Employment.

        Java overloads:
        (double chanceOfUnemployment)
        """
        self.chance_of_unemployment: float
        self.next_time_to_check: int
        self.unemployed: bool
        raise NotImplementedError("Java: Employment#Employment — pending T10")

    def check_employment(self, person: Person, time: int) -> None:
        """Java: Employment#checkEmployment.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Employment#checkEmployment — pending T10")
