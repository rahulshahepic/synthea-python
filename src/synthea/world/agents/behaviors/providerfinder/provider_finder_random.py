"""Java: org.mitre.synthea.world.agents.behaviors.providerfinder.ProviderFinderRandom."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.agents.provider import Provider
    from synthea.world.concepts.health_record import EncounterType


class ProviderFinderRandom:
    """Java: ProviderFinderRandom."""

    def __init__(self) -> None:
        """Java: ProviderFinderRandom#ProviderFinderRandom.

        Java overloads:
        ()
        """

    def find(
        self,
        providers: list[Provider],
        person: Person,
        service: EncounterType | None,
        time: int,
    ) -> Provider | None:
        """Java: ProviderFinderRandom#find.

        Java overloads:
        (List providers, Person person, EncounterType service, long time)
        """
        options: list[Provider] = []
        for provider in providers:
            if provider.accepts(person, time) and (
                service is None or provider.has_service(service)
            ):
                options.append(provider)

        if not options:
            return None
        if len(options) == 1:
            return options[0]
        # there are a few equally good options, pick one randomly.
        return options[person.rand_int(len(options))]
