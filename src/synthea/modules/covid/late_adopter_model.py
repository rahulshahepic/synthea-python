"""Java API skeleton: LateAdopterModel.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class LateAdopterModel:
    """Java: LateAdopterModel; pending T24."""

    LOWEST_CHANCE_THRESHOLD: ClassVar[float] = 0.001

    def __init__(self, person: Person, time: int) -> None:
        """Java: LateAdopterModel#LateAdopterModel.

        Java overloads:
        (Person person, long time)
        """
        self.chance_of_getting_shot: float
        self.last_updated: int
        raise NotImplementedError("Java: LateAdopterModel#LateAdopterModel — pending T24")

    def get_chance_of_getting_shot(self) -> float:
        """Java: LateAdopterModel#getChanceOfGettingShot.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: LateAdopterModel#getChanceOfGettingShot — pending T24")

    def set_chance_of_getting_shot(self, chance_of_getting_shot: float) -> None:
        """Java: LateAdopterModel#setChanceOfGettingShot.

        Java overloads:
        (double chanceOfGettingShot)
        """
        raise NotImplementedError("Java: LateAdopterModel#setChanceOfGettingShot — pending T24")

    def get_last_updated(self) -> int:
        """Java: LateAdopterModel#getLastUpdated.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: LateAdopterModel#getLastUpdated — pending T24")

    def set_last_updated(self, last_updated: int) -> None:
        """Java: LateAdopterModel#setLastUpdated.

        Java overloads:
        (long lastUpdated)
        """
        raise NotImplementedError("Java: LateAdopterModel#setLastUpdated — pending T24")

    def will_get_shot(self, person: Person, time: int) -> bool:
        """Java: LateAdopterModel#willGetShot.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: LateAdopterModel#willGetShot — pending T24")

    def is_not_getting_shot(self) -> bool:
        """Java: LateAdopterModel#isNotGettingShot.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: LateAdopterModel#isNotGettingShot — pending T24")
