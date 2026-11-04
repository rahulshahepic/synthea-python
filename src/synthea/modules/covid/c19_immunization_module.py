"""Java API skeleton: C19ImmunizationModule.java."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, ClassVar, Protocol

if TYPE_CHECKING:
    from synthea.engine.module import Module
    from synthea.modules.covid.c19_vaccine import EUASet as C19VaccineEUASet
    from synthea.world.agents.person import Person

    class Inventory(Protocol):
        """Java boundary type: Inventory; external to the mapped Python port."""


class C19ImmunizationModule:
    """Java: C19ImmunizationModule; pending T24."""

    COVID_CODE: ClassVar[str] = "840539006"
    FIRST_POSSIBLE_SHOT_TIME: ClassVar[int] = 1607688000000
    MODERNA_APPROVED: ClassVar[int] = 1608292800000
    JANSSEN_APPROVED: ClassVar[int] = 1614427200000
    EXPAND_AGE_TO_TWELVE: ClassVar[int] = 1620648000000
    LATE_ADOPTION_START_TIME: ClassVar[int] = 1631620800000
    FIRST_ELIGIBLE_AGE: ClassVar[int] = 16
    EXPANDED_ELIGIBLE_AGE: ClassVar[int] = 12
    C19_VACCINE_STATUS: ClassVar[str] = "C19_VACCINE_STATUS"
    C19_VACCINE: ClassVar[str] = "C19_VACCINE"
    C19_SCHEDULED_FIRST_SHOT: ClassVar[str] = "C19_SCHEDULED_FIRST_SHOT"
    C19_SCHEDULED_SECOND_SHOT: ClassVar[str] = "C19_SCHEDULED_SECOND_SHOT"
    C19_LATE_ADOPTER_MODEL: ClassVar[str] = "C19_LATE_ADOPTER_MODEL"
    C19_FULLY_VACCINATED: ClassVar[str] = "C19_FULLY_VACCINATED"
    C19_PERSON_ATTRS_KEY: ClassVar[str] = "covid19"

    def __init__(self) -> None:
        """Java: C19ImmunizationModule#C19ImmunizationModule.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: C19ImmunizationModule#C19ImmunizationModule — pending T24")

    def clone(self) -> Module:
        """Java: C19ImmunizationModule#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: C19ImmunizationModule#clone — pending T24")

    @staticmethod
    def currently_has_covid(person: Person) -> bool:
        """Java: C19ImmunizationModule#currentlyHasCOVID.

        Java overloads:
        (Person person)
        """
        raise NotImplementedError("Java: C19ImmunizationModule#currentlyHasCOVID — pending T24")

    @staticmethod
    def eligible_for_shot(person: Person, time: int) -> bool:
        """Java: C19ImmunizationModule#eligibleForShot.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: C19ImmunizationModule#eligibleForShot — pending T24")

    @staticmethod
    def decide_on_shot(person: Person, time: int) -> bool:
        """Java: C19ImmunizationModule#decideOnShot.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: C19ImmunizationModule#decideOnShot — pending T24")

    @staticmethod
    def select_vaccine(person: Person, time: int) -> C19VaccineEUASet:
        """Java: C19ImmunizationModule#selectVaccine.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: C19ImmunizationModule#selectVaccine — pending T24")

    @staticmethod
    def vaccinate(person: Person, time: int, series: int) -> None:
        """Java: C19ImmunizationModule#vaccinate.

        Java overloads:
        (Person person, long time, int series)
        """
        raise NotImplementedError("Java: C19ImmunizationModule#vaccinate — pending T24")

    def process(self, person: Person, time: int) -> bool:
        """Java: C19ImmunizationModule#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: C19ImmunizationModule#process — pending T24")

    @staticmethod
    def inventory_attributes(attributes: dict[str, Inventory]) -> None:
        """Java: C19ImmunizationModule#inventoryAttributes.

        Java overloads:
        (Map attributes)
        """
        raise NotImplementedError("Java: C19ImmunizationModule#inventoryAttributes — pending T24")


class VaccinationStatus(StrEnum):
    """Java: VaccinationStatus; pending T24."""

    NOT_ELIGIBLE = "NOT_ELIGIBLE"
    WAITING_FOR_SHOT = "WAITING_FOR_SHOT"
    POTENTIAL_LATE_ADOPTER = "POTENTIAL_LATE_ADOPTER"
    NEVER_GOING_TO_GET_SHOT = "NEVER_GOING_TO_GET_SHOT"
    FIRST_SHOT = "FIRST_SHOT"
    FULLY_VACCINATED = "FULLY_VACCINATED"


setattr(C19ImmunizationModule, "VaccinationStatus", VaccinationStatus)  # noqa: B010
