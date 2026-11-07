"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/agents/behaviors/planfinder/PlanFinderBestRat
es.java.
"""

from __future__ import annotations

import calendar
import sys
from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, cast

from synthea.javacompat import bigdecimal as bd
from synthea.world.agents.behaviors.planfinder.i_plan_finder import IPlanFinder

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import EncounterType, HealthRecord
    from synthea.world.concepts.healthinsurance.insurance_plan import InsurancePlan


class PlanFinderBestRates(IPlanFinder):
    """Java: PlanFinderBestRates."""

    def __init__(self) -> None:
        """Java: PlanFinderBestRates#PlanFinderBestRates.

        Java overloads:
        ()
        """
        pass

    def find(
        self, plans: list[InsurancePlan], person: Person, service: EncounterType, time: int
    ) -> InsurancePlan:
        """Java: PlanFinderBestRates#find.

        Java overloads:
        (List plans, Person person, EncounterType service, long time)
        """
        from synthea.world.agents.payer_manager import PayerManager
        from synthea.world.agents.person import Person

        count = 0
        if person.has_multiple_records:
            for record in person.records.values():
                count += self.twelve_month_encounter_count(record, time)
        else:
            count = self.twelve_month_encounter_count(person.default_record, time)
        best_plan = PayerManager.get_no_insurance_plan()
        best_rate = bd.value_of(sys.float_info.max)
        for plan in plans:
            if (
                plan.is_government_plan()
                or IPlanFinder.meets_affordability_requirements(plan, person, service, time)
            ) and plan.accepts(person, time):
                rate = bd.set_scale(
                    bd.multiply(
                        plan.get_monthly_premium(cast(int, person.attributes[Person.INCOME])),
                        Decimal(12),
                    ),
                    2,
                    bd.RoundingMode.HALF_EVEN,
                )
                rate = bd.set_scale(
                    bd.add(
                        rate, bd.multiply(plan.determine_copay("ambulatory", time), Decimal(count))
                    ),
                    2,
                    bd.RoundingMode.HALF_EVEN,
                )
                if rate < best_rate:
                    best_rate = rate
                    best_plan = plan
        return best_plan

    def twelve_month_encounter_count(self, record: HealthRecord, time: int) -> int:
        """Java: PlanFinderBestRates#twelveMonthEncounterCount.

        Java overloads:
        (HealthRecord record, long time)
        """
        date = datetime.fromtimestamp(time // 1000, UTC)
        previous_year = date.year - 1
        day = min(date.day, calendar.monthrange(previous_year, date.month)[1])
        previous = date.replace(year=previous_year, day=day)
        one_year_ago = int(previous.timestamp()) * 1000 + time % 1000
        count = 0
        for encounter in reversed(record.encounters):
            if encounter.start >= one_year_ago:
                count += 1
            else:
                break
        return count
