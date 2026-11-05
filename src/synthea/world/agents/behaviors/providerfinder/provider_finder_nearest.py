"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/providerfinder/Pr
oviderFinderNearest.java.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.agents.provider import Provider
    from synthea.world.concepts.health_record import EncounterType


class ProviderFinderNearest:
    """Java: ProviderFinderNearest; pending
    T13.
    """

    def __init__(self) -> None:
        """Java: ProviderFinderNearest#ProviderFinderNearest.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ProviderFinderNearest#ProviderFinderNearest — pending T13")

    def find(
        self, providers: list[Provider], person: Person, service: EncounterType, time: int
    ) -> Provider:
        """Java: ProviderFinderNearest#find.

        Java overloads:
        (List providers, Person person, EncounterType service, long time)
        """
        raise NotImplementedError("Java: ProviderFinderNearest#find — pending T13")
