"""Java API skeleton: CardiovascularDiseaseModule.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Protocol

if TYPE_CHECKING:
    from synthea.engine.module import Module
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import Code

    class Inventory(Protocol):
        """Java boundary type: Inventory; external to the mapped Python port."""


class CardiovascularDiseaseModule:
    """Java: CardiovascularDiseaseModule; pending T23."""

    useFramingham: ClassVar[bool] = False
    tenYearsInMS: ClassVar[int] = 315360000000
    oneMonthInMS: ClassVar[int] = 2592000000

    def __init__(self) -> None:
        """Java: CardiovascularDiseaseModule#CardiovascularDiseaseModule.

        Java overloads:
        ()
        """
        raise NotImplementedError(
            "Java: CardiovascularDiseaseModule#CardiovascularDiseaseModule — pending T23"
        )

    def clone(self) -> Module:
        """Java: CardiovascularDiseaseModule#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CardiovascularDiseaseModule#clone — pending T23")

    def process(self, person: Person, time: int) -> bool:
        """Java: CardiovascularDiseaseModule#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: CardiovascularDiseaseModule#process — pending T23")

    @staticmethod
    def calculate_cardio_risk(person: Person, time: int) -> None:
        """Java: CardiovascularDiseaseModule#calculateCardioRisk.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError(
            "Java: CardiovascularDiseaseModule#calculateCardioRisk — pending T23"
        )

    @staticmethod
    def calculate_ascvd_risk(person: Person, time: int) -> None:
        """Java: CardiovascularDiseaseModule#calculateAscvdRisk.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError(
            "Java: CardiovascularDiseaseModule#calculateAscvdRisk — pending T23"
        )

    @staticmethod
    def calculate_atrial_fibrillation_risk(person: Person, time: int) -> None:
        """Java: CardiovascularDiseaseModule#calculateAtrialFibrillationRisk.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError(
            "Java: CardiovascularDiseaseModule#calculateAtrialFibrillationRisk — pending T23"
        )

    @staticmethod
    def calculate_stroke_risk(person: Person, time: int) -> None:
        """Java: CardiovascularDiseaseModule#calculateStrokeRisk.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError(
            "Java: CardiovascularDiseaseModule#calculateStrokeRisk — pending T23"
        )

    @staticmethod
    def get_all_codes() -> list[Code]:
        """Java: CardiovascularDiseaseModule#getAllCodes.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CardiovascularDiseaseModule#getAllCodes — pending T23")

    @staticmethod
    def inventory_attributes(attributes: dict[str, Inventory]) -> None:
        """Java: CardiovascularDiseaseModule#inventoryAttributes.

        Java overloads:
        (Map attributes)
        """
        raise NotImplementedError(
            "Java: CardiovascularDiseaseModule#inventoryAttributes — pending T23"
        )
