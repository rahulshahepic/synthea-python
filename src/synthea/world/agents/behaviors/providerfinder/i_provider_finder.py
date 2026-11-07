"""Java: org.mitre.synthea.world.agents.behaviors.providerfinder.IProviderFinder."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.agents.provider import Provider
    from synthea.world.concepts.health_record import EncounterType


class IProviderFinder(Protocol):
    """Java: IProviderFinder."""

    def find(
        self,
        providers: list[Provider],
        person: Person,
        service: EncounterType | None,
        time: int,
    ) -> Provider | None:
        """Java: IProviderFinder#find.

        Java overloads:
        (List providers, Person person, EncounterType service, long time)
        """
        ...
