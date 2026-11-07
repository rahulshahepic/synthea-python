"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/planfinder/PlanFinderPriorit
y.java.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from synthea.world.agents.behaviors.planfinder.i_plan_finder import IPlanFinder

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import EncounterType
    from synthea.world.concepts.healthinsurance.insurance_plan import InsurancePlan


class PlanFinderPriority(IPlanFinder):
    """Java: PlanFinderPriority."""

    def __init__(self) -> None:
        """Java: PlanFinderPriority#PlanFinderPriority.

        Java overloads:
        ()
        """
        pass

    def find(
        self, plans: list[InsurancePlan], person: Person, service: EncounterType | None, time: int
    ) -> InsurancePlan:
        """Java: PlanFinderPriority#find.

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
        if len(eligible_plans) > 1:
            priority = min(plan.get_priority() for plan in eligible_plans)
            eligible_plans = [plan for plan in eligible_plans if plan.get_priority() == priority]
        return self.choose_random_plan(eligible_plans, person)
