"""Java API skeleton: Employment.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from synthea.helpers.utilities import Utilities

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class Employment:
    """Java: org.mitre.synthea.world.concepts.Employment."""

    MIN_EMPLOYMENT_STATE_LENGTH: ClassVar[int] = 6

    def __init__(self, chance_of_unemployment: float) -> None:
        """Java: Employment#Employment.

        Java overloads:
        (double chanceOfUnemployment)
        """
        self.chance_of_unemployment: float
        self.next_time_to_check: int
        self.unemployed: bool
        self.chance_of_unemployment = chance_of_unemployment
        self.next_time_to_check = 0
        self.unemployed = False

    def check_employment(self, person: Person, time: int) -> None:
        """Java: Employment#checkEmployment.

        Java overloads:
        (Person person, long time)
        """
        if time >= self.next_time_to_check:
            if self.unemployed:
                self.unemployed = False
                person.attributes[person.UNEMPLOYED] = False
            elif person.rand() < self.chance_of_unemployment:
                self.unemployed = True
                person.attributes[person.UNEMPLOYED] = True
            self.next_time_to_check = time + Utilities.convert_time(
                "months", self.MIN_EMPLOYMENT_STATE_LENGTH
            )
