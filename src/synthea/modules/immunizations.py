"""Java API skeleton: Immunizations.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Protocol

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import Code

    class Inventory(Protocol):
        """Java boundary type: Inventory; external to the mapped Python port."""


class Immunizations:
    """Java: Immunizations; pending T22."""

    IMMUNIZATIONS: ClassVar[str] = "immunizations"
    immunizationSchedule: ClassVar[
        dict[str, dict[object, object]]
    ]  # Java initialization deferred to T22.

    def __init__(self) -> None:
        """Java: Immunizations#Immunizations.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Immunizations#Immunizations — pending T22")

    @staticmethod
    def load_immunization_schedule() -> dict[object, object]:
        """Java: Immunizations#loadImmunizationSchedule.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Immunizations#loadImmunizationSchedule — pending T22")

    @staticmethod
    def perform_encounter(person: Person, time: int) -> None:
        """Java: Immunizations#performEncounter.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Immunizations#performEncounter — pending T22")

    @staticmethod
    def immunization_due(
        immunization: str, person: Person, time: int, immunizations_given: dict[str, list[int]]
    ) -> int:
        """Java: Immunizations#immunizationDue.

        Java overloads:
        (String immunization, Person person, long time, Map immunizationsGiven)
        """
        raise NotImplementedError("Java: Immunizations#immunizationDue — pending T22")

    @staticmethod
    def get_all_codes() -> list[Code]:
        """Java: Immunizations#getAllCodes.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Immunizations#getAllCodes — pending T22")

    @staticmethod
    def get_maximum_doses(code: str) -> int:
        """Java: Immunizations#getMaximumDoses.

        Java overloads:
        (String code)
        """
        raise NotImplementedError("Java: Immunizations#getMaximumDoses — pending T22")

    @staticmethod
    def inventory_attributes(attributes: dict[str, Inventory]) -> None:
        """Java: Immunizations#inventoryAttributes.

        Java overloads:
        (Map attributes)
        """
        raise NotImplementedError("Java: Immunizations#inventoryAttributes — pending T22")
