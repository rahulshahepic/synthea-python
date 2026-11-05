"""Java API skeleton: Telemedicine.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class Telemedicine:
    """Java: Telemedicine; pending T06."""

    CURRENT_CHANCE: ClassVar[float] = 0.15
    PREPANDEMIC_CHANCE: ClassVar[float] = 0.004
    TELEMEDICINE_START_DATE: ClassVar[int] = 1451649600000
    TELEMEDICINE_UPTAKE_DATE: ClassVar[int] = 1585742400000

    def __init__(self) -> None:
        """Java: Telemedicine#Telemedicine.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Telemedicine#Telemedicine — pending T06")

    @staticmethod
    def should_encounter_be_virtual(person: Person, time: int) -> bool:
        """Java: Telemedicine#shouldEncounterBeVirtual.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Telemedicine#shouldEncounterBeVirtual — pending T06")
