"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/planfinder/PlanFinderRandom.
java.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from synthea.world.agents.behaviors.planfinder.i_plan_finder import IPlanFinder

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import EncounterType
    from synthea.world.concepts.healthinsurance.insurance_plan import InsurancePlan


class PlanFinderRandom(IPlanFinder):
    """Java: PlanFinderRandom."""

    def __init__(self) -> None:
        """Java: PlanFinderRandom#PlanFinderRandom.

        Java overloads:
        ()
        """
        pass

    def find(
        self, plans: list[InsurancePlan], person: Person, service: EncounterType, time: int
    ) -> InsurancePlan:
        """Java: PlanFinderRandom#find.

        Java overloads:
        (List plans, Person person, EncounterType service, long time)
        """
        eligible_plans = [
            plan
            for plan in plans
            if (
                plan.is_government_plan()
                or IPlanFinder.meets_affordability_requirements(plan, person, service, time)
            )
            and plan.accepts(person, time)
        ]
        return self.choose_random_plan(eligible_plans, person)
