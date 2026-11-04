"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/planfinder/PlanFinderPriorit
y.java.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import EncounterType
    from synthea.world.concepts.healthinsurance.insurance_plan import InsurancePlan


class PlanFinderPriority:
    """Java: PlanFinderPriority; pending T15."""

    def __init__(self) -> None:
        """Java: PlanFinderPriority#PlanFinderPriority.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: PlanFinderPriority#PlanFinderPriority — pending T15")

    def find(
        self, plans: list[InsurancePlan], person: Person, service: EncounterType, time: int
    ) -> InsurancePlan:
        """Java: PlanFinderPriority#find.

        Java overloads:
        (List plans, Person person, EncounterType service, long time)
        """
        raise NotImplementedError("Java: PlanFinderPriority#find — pending T15")
