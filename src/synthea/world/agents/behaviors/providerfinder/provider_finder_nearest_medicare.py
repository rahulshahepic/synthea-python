"""Java: org.mitre.synthea.world.agents.behaviors.providerfinder.ProviderFinderNearestMedicare."""

from __future__ import annotations

from typing import TYPE_CHECKING

from synthea.world.agents.behaviors.providerfinder.provider_finder_nearest import (
    _point_distance,
)

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.agents.provider import Provider
    from synthea.world.concepts.health_record import EncounterType


class ProviderFinderNearestMedicare:
    """Java: ProviderFinderNearestMedicare."""

    def __init__(self) -> None:
        """Java: ProviderFinderNearestMedicare#ProviderFinderNearestMedicare.

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
        """Java: ProviderFinderNearestMedicare#find.

        Java overloads:
        (List providers, Person person, EncounterType service, long time)
        """
        # Find providers that accept the person
        options = [p for p in providers if p.accepts(person, time)]

        # Find providers with the requested service, if one is given
        if service is not None:
            options = [p for p in options if p.has_service(service)]

        # Filter to only Medicare providers (String.isBlank: whitespace-only
        # counts as blank).
        options = [
            p
            for p in options
            if p.cms_provider_num is not None and p.cms_provider_num.strip() != ""
        ]

        # Sort by distance (groupingBy encounter order, min by Double.compare).
        grouped_by_distance: dict[float, list[Provider]] = {}
        for provider in options:
            distance = _point_distance(provider.get_lon_lat(), person.get_lon_lat())
            grouped_by_distance.setdefault(distance, []).append(provider)
        if grouped_by_distance:
            min_distance = min(grouped_by_distance)
            closest = grouped_by_distance[min_distance]
            if len(closest) > 1:
                return closest[person.rand_int(len(closest))]
            return closest[0]
        return None
