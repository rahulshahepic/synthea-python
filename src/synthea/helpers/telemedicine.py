"""Telemedicine port.

Java: org.mitre.synthea.helpers.Telemedicine — the chance an encounter is
virtual, before/after the COVID-19 uptake date.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class Telemedicine:
    """Java: org.mitre.synthea.helpers.Telemedicine."""

    CURRENT_CHANCE: ClassVar[float] = 0.15
    PREPANDEMIC_CHANCE: ClassVar[float] = 0.004
    # LocalDateTime.of(2016, 1, 1, 12, 0).toInstant(UTC).toEpochMilli()
    TELEMEDICINE_START_DATE: ClassVar[int] = 1451649600000
    # LocalDateTime.of(2020, 4, 1, 12, 0).toInstant(UTC).toEpochMilli()
    TELEMEDICINE_UPTAKE_DATE: ClassVar[int] = 1585742400000

    def __init__(self) -> None:
        """Java: Telemedicine#Telemedicine.

        Java overloads:
        ()
        """

    @staticmethod
    def should_encounter_be_virtual(person: Person, time: int) -> bool:
        """Java: Telemedicine#shouldEncounterBeVirtual.

        Java overloads:
        (Person person, long time)

        Before TELEMEDICINE_START_DATE no random draw is made at all —
        the person's RNG stream is untouched, which parity depends on.
        """
        if time < Telemedicine.TELEMEDICINE_START_DATE:
            return False
        if time < Telemedicine.TELEMEDICINE_UPTAKE_DATE:
            return person.rand() <= Telemedicine.PREPANDEMIC_CHANCE
        return person.rand() <= Telemedicine.CURRENT_CHANCE
