"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/planfinder/PlanFinderBestRat
es.java.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import EncounterType, HealthRecord
    from synthea.world.concepts.healthinsurance.insurance_plan import InsurancePlan


class PlanFinderBestRates:
    """Java: PlanFinderBestRates; pending T15."""

    def __init__(self) -> None:
        """Java: PlanFinderBestRates#PlanFinderBestRates.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: PlanFinderBestRates#PlanFinderBestRates — pending T15")

    def find(
        self, plans: list[InsurancePlan], person: Person, service: EncounterType, time: int
    ) -> InsurancePlan:
        """Java: PlanFinderBestRates#find.

        Java overloads:
        (List plans, Person person, EncounterType service, long time)
        """
        raise NotImplementedError("Java: PlanFinderBestRates#find — pending T15")

    def twelve_month_encounter_count(self, record: HealthRecord, time: int) -> int:
        """Java: PlanFinderBestRates#twelveMonthEncounterCount.

        Java overloads:
        (HealthRecord record, long time)
        """
        raise NotImplementedError(
            "Java: PlanFinderBestRates#twelveMonthEncounterCount — pending T15"
        )
