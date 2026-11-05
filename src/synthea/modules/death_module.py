"""Java API skeleton: DeathModule.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Protocol

from synthea.world.concepts.health_record import Code

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import Code

    class Inventory(Protocol):
        """Java boundary type: Inventory; external to the mapped Python port."""


class DeathModule:
    """Java: DeathModule; pending T22."""

    DEATH_CERTIFICATION: ClassVar[Code]  # Java initialization deferred to T22.
    CAUSE_OF_DEATH_CODE: ClassVar[Code]  # Java initialization deferred to T22.
    DEATH_CERTIFICATE: ClassVar[Code]  # Java initialization deferred to T22.

    def __init__(self) -> None:
        """Java: DeathModule#DeathModule.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: DeathModule#DeathModule — pending T22")

    @staticmethod
    def process(person: Person, time: int) -> None:
        """Java: DeathModule#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: DeathModule#process — pending T22")

    @staticmethod
    def get_all_codes() -> list[Code]:
        """Java: DeathModule#getAllCodes.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: DeathModule#getAllCodes — pending T22")

    @staticmethod
    def inventory_attributes(attributes: dict[str, Inventory]) -> None:
        """Java: DeathModule#inventoryAttributes.

        Java overloads:
        (Map attributes)
        """
        raise NotImplementedError("Java: DeathModule#inventoryAttributes — pending T22")


# Java static data initialization; constructors remain stubs.
DeathModule.DEATH_CERTIFICATION = object.__new__(Code)
DeathModule.DEATH_CERTIFICATION.system = "SNOMED-CT"
DeathModule.DEATH_CERTIFICATION.code = "308646001"
DeathModule.DEATH_CERTIFICATION.display = "Death Certification"
DeathModule.DEATH_CERTIFICATION.version = None
DeathModule.DEATH_CERTIFICATION.value_set = None
DeathModule.CAUSE_OF_DEATH_CODE = object.__new__(Code)
DeathModule.CAUSE_OF_DEATH_CODE.system = "LOINC"
DeathModule.CAUSE_OF_DEATH_CODE.code = "69453-9"
DeathModule.CAUSE_OF_DEATH_CODE.display = "Cause of Death [US Standard Certificate of Death]"
DeathModule.CAUSE_OF_DEATH_CODE.version = None
DeathModule.CAUSE_OF_DEATH_CODE.value_set = None
DeathModule.DEATH_CERTIFICATE = object.__new__(Code)
DeathModule.DEATH_CERTIFICATE.system = "LOINC"
DeathModule.DEATH_CERTIFICATE.code = "69409-1"
DeathModule.DEATH_CERTIFICATE.display = "U.S. standard certificate of death - 2003 revision"
DeathModule.DEATH_CERTIFICATE.version = None
DeathModule.DEATH_CERTIFICATE.value_set = None
