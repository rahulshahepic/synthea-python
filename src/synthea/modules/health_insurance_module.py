"""Java API skeleton: HealthInsuranceModule.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Protocol

if TYPE_CHECKING:
    from synthea.engine.module import Module
    from synthea.world.agents.person import Person

    class Inventory(Protocol):
        """Java boundary type: Inventory; external to the mapped Python port."""


class HealthInsuranceModule:
    """Java: HealthInsuranceModule; pending T16."""

    mandateTime: ClassVar[int]  # Java initialization deferred to T16.
    mandateOccupation: ClassVar[float]  # Java initialization deferred to T16.
    povertyLevel: ClassVar[float]  # Java initialization deferred to T16.

    def __init__(self) -> None:
        """Java: HealthInsuranceModule#HealthInsuranceModule.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: HealthInsuranceModule#HealthInsuranceModule — pending T16")

    def clone(self) -> Module:
        """Java: HealthInsuranceModule#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: HealthInsuranceModule#clone — pending T16")

    def process(self, person: Person, time: int) -> bool:
        """Java: HealthInsuranceModule#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: HealthInsuranceModule#process — pending T16")

    def update_insurance(self, person: Person, time: int) -> None:
        """Java: HealthInsuranceModule#updateInsurance.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: HealthInsuranceModule#updateInsurance — pending T16")

    @staticmethod
    def inventory_attributes(attributes: dict[str, Inventory]) -> None:
        """Java: HealthInsuranceModule#inventoryAttributes.

        Java overloads:
        (Map attributes)
        """
        raise NotImplementedError("Java: HealthInsuranceModule#inventoryAttributes — pending T16")
