"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/providerfinder/IProviderFind
er.java.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.agents.provider import Provider
    from synthea.world.concepts.health_record import EncounterType


class IProviderFinder(Protocol):
    """Java: IProviderFinder; pending T13."""

    def __init__(self) -> None:
        """Java: IProviderFinder#IProviderFinder.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: IProviderFinder#IProviderFinder — pending T13")

    def find(
        self, providers: list[Provider], person: Person, service: EncounterType, time: int
    ) -> Provider:
        """Java: IProviderFinder#find.

        Java overloads:
        (List providers, Person person, EncounterType service, long time)
        """
        raise NotImplementedError("Java: IProviderFinder#find — pending T13")
