"""Java: org.mitre.synthea.world.agents.behaviors.providerfinder.ProviderFinderNearest."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.world.agents.person import Person, Point2DDouble
    from synthea.world.agents.provider import Provider
    from synthea.world.concepts.health_record import EncounterType


def _point_distance(point: Point2DDouble, other: Point2DDouble) -> float:
    """Java: Point2D#distance(Point2D) (JDK 21 java.awt.geom.Point2D).

    ``px = other.getX() - this.getX(); py = other.getY() - this.getY();
    return Math.sqrt(px * px + py * py)``.
    """
    px = other.get_x() - point.get_x()
    py = other.get_y() - point.get_y()
    return math.sqrt(px * px + py * py)


class ProviderFinderNearest:
    """Java: ProviderFinderNearest."""

    def __init__(self) -> None:
        """Java: ProviderFinderNearest#ProviderFinderNearest.

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
        """Java: ProviderFinderNearest#find.

        Java overloads:
        (List providers, Person person, EncounterType service, long time)
        """
        # Function-local imports break the Person <-> Provider cycle.
        from synthea.world.agents.person import Person
        from synthea.world.agents.provider import ProviderType
        from synthea.world.concepts.health_record import EncounterType

        # Find providers that accept the person
        options = [p for p in providers if p.accepts(person, time)]

        # Find providers with the requested service, if one is given
        if service is not None:
            options = [p for p in options if p.has_service(service)]

        # If it's not an emergency
        if service is None or service not in (
            EncounterType.URGENTCARE,
            EncounterType.EMERGENCY,
        ):
            # Filter to only VA Facilities if the person is a veteran
            if Person.VETERAN in person.attributes:
                # Java streams over the ORIGINAL providers list here.
                if any(p.type == ProviderType.VETERAN for p in providers):
                    options = [p for p in options if p.type == ProviderType.VETERAN]
            elif person.attributes.get(Person.RACE) != "native":
                # Filter out IHS facilities if someone is not Native American
                options = [p for p in options if p.type != ProviderType.IHS]

        # Sort by distance: Java groupingBy keeps encounter order for both
        # the groups and their members; the minimum key is by Double.compare.
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
