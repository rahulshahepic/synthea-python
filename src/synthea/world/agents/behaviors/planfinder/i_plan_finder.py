"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/planfinder/IPlanFinder.java.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, cast

if TYPE_CHECKING:
    from synthea.helpers.random_number_generator import RandomNumberGenerator
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import EncounterType
    from synthea.world.concepts.healthinsurance.insurance_plan import InsurancePlan


class IPlanFinder(Protocol):
    """Java: IPlanFinder."""

    def __init__(self) -> None:
        """Java: IPlanFinder#IPlanFinder.

        Java overloads:
        ()
        """
        pass

    def find(
        self, plans: list[InsurancePlan], person: Person, service: EncounterType, time: int
    ) -> InsurancePlan:
        """Java: IPlanFinder#find.

        Java overloads:
        (List plans, Person person, EncounterType service, long time)
        """
        ...

    @staticmethod
    def meets_affordability_requirements(
        plan: InsurancePlan, person: Person, service: EncounterType, time: int
    ) -> bool:
        """Java: IPlanFinder#meetsAffordabilityRequirements.

        Java overloads:
        (InsurancePlan plan, Person person, EncounterType service, long time)
        """
        from synthea.modules.health_insurance_module import HealthInsuranceModule
        from synthea.world.agents.person import Person

        occupation = float(cast(float, person.attributes[Person.OCCUPATION_LEVEL]))
        return (
            person.can_afford_plan(plan)
            or (
                time >= HealthInsuranceModule.mandateTime
                and occupation >= HealthInsuranceModule.mandateOccupation
            )
        ) and plan.covers_service(None)

    def choose_random_plan(
        self, options: list[InsurancePlan], rand: RandomNumberGenerator
    ) -> InsurancePlan:
        """Java: IPlanFinder#chooseRandomPlan.

        Java overloads:
        (List options, RandomNumberGenerator rand)
        """
        from synthea.world.agents.payer_manager import PayerManager

        if not options:
            return PayerManager.get_no_insurance_plan()
        return options[rand.rand_int(len(options))]
