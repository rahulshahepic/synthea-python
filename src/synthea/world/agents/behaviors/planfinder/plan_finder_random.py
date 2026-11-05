"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/planfinder/PlanFinderRandom.
java.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import EncounterType
    from synthea.world.concepts.healthinsurance.insurance_plan import InsurancePlan


class PlanFinderRandom:
    """Java: PlanFinderRandom; pending T15."""

    def __init__(self) -> None:
        """Java: PlanFinderRandom#PlanFinderRandom.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: PlanFinderRandom#PlanFinderRandom — pending T15")

    def find(
        self, plans: list[InsurancePlan], person: Person, service: EncounterType, time: int
    ) -> InsurancePlan:
        """Java: PlanFinderRandom#find.

        Java overloads:
        (List plans, Person person, EncounterType service, long time)
        """
        raise NotImplementedError("Java: PlanFinderRandom#find — pending T15")
