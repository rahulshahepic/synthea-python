"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/planfinder/IPlanFinder.java.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from synthea.helpers.random_number_generator import RandomNumberGenerator
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import EncounterType
    from synthea.world.concepts.healthinsurance.insurance_plan import InsurancePlan


class IPlanFinder(Protocol):
    """Java: IPlanFinder; pending T15."""

    def __init__(self) -> None:
        """Java: IPlanFinder#IPlanFinder.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: IPlanFinder#IPlanFinder — pending T15")

    def find(
        self, plans: list[InsurancePlan], person: Person, service: EncounterType, time: int
    ) -> InsurancePlan:
        """Java: IPlanFinder#find.

        Java overloads:
        (List plans, Person person, EncounterType service, long time)
        """
        raise NotImplementedError("Java: IPlanFinder#find — pending T15")

    @staticmethod
    def meets_affordability_requirements(
        plan: InsurancePlan, person: Person, service: EncounterType, time: int
    ) -> bool:
        """Java: IPlanFinder#meetsAffordabilityRequirements.

        Java overloads:
        (InsurancePlan plan, Person person, EncounterType service, long time)
        """
        raise NotImplementedError("Java: IPlanFinder#meetsAffordabilityRequirements — pending T15")

    def choose_random_plan(
        self, options: list[InsurancePlan], rand: RandomNumberGenerator
    ) -> InsurancePlan:
        """Java: IPlanFinder#chooseRandomPlan.

        Java overloads:
        (List options, RandomNumberGenerator rand)
        """
        raise NotImplementedError("Java: IPlanFinder#chooseRandomPlan — pending T15")
