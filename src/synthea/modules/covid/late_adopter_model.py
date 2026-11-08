"""Java: LateAdopterModel.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from synthea.helpers.utilities import Utilities

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class LateAdopterModel:
    """Java: LateAdopterModel."""

    LOWEST_CHANCE_THRESHOLD: ClassVar[float] = 0.001

    def __init__(self, person: Person, time: int) -> None:
        """Java: LateAdopterModel#LateAdopterModel.

        Java overloads:
        (Person person, long time)
        """
        age = person.age_in_years(time)
        # Totally made up guesses as to how likely someone is to get a COVID-19
        # vaccine in the period of time after we have actual data (Java comment).
        if age <= 15:
            self.chance_of_getting_shot: float = 0.4
        elif age <= 40:
            self.chance_of_getting_shot = 0.2
        else:
            self.chance_of_getting_shot = 0.1
        self.last_updated: int = time

    def get_chance_of_getting_shot(self) -> float:
        """Java: LateAdopterModel#getChanceOfGettingShot.

        Java overloads:
        ()
        """
        return self.chance_of_getting_shot

    def set_chance_of_getting_shot(self, chance_of_getting_shot: float) -> None:
        """Java: LateAdopterModel#setChanceOfGettingShot.

        Java overloads:
        (double chanceOfGettingShot)
        """
        self.chance_of_getting_shot = chance_of_getting_shot

    def get_last_updated(self) -> int:
        """Java: LateAdopterModel#getLastUpdated.

        Java overloads:
        ()
        """
        return self.last_updated

    def set_last_updated(self, last_updated: int) -> None:
        """Java: LateAdopterModel#setLastUpdated.

        Java overloads:
        (long lastUpdated)
        """
        self.last_updated = last_updated

    def will_get_shot(self, person: Person, time: int) -> bool:
        """Java: LateAdopterModel#willGetShot.

        Java overloads:
        (Person person, long time)
        """
        if time <= (self.last_updated + Utilities.convert_time("weeks", 2)):
            return False
        else:
            if person.rand() <= self.chance_of_getting_shot:
                return True
            else:
                self.chance_of_getting_shot = self.chance_of_getting_shot / 2
                self.last_updated = time
                return False

    def is_not_getting_shot(self) -> bool:
        """Java: LateAdopterModel#isNotGettingShot.

        Java overloads:
        ()
        """
        return self.chance_of_getting_shot < LateAdopterModel.LOWEST_CHANCE_THRESHOLD
