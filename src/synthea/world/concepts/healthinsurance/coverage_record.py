"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/concepts/healthinsurance/CoverageRecord.java.
"""

from __future__ import annotations

import builtins
from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.healthinsurance.insurance_plan import InsurancePlan
    from synthea.world.concepts.healthinsurance.plan_record import PlanRecord


class CoverageRecord:
    """Java: CoverageRecord; pending T16."""

    serialVersionUID: ClassVar[int] = 771457063723016307

    def __init__(self, person: Person) -> None:
        """Java: CoverageRecord#CoverageRecord.

        Java overloads:
        (Person person)
        """
        self.person: Person
        self.plan_history: builtins.set[PlanRecord]
        self.next_enrollment_period: int
        raise NotImplementedError("Java: CoverageRecord#CoverageRecord — pending T16")

    def get_plan_history(self) -> builtins.set[PlanRecord]:
        """Java: CoverageRecord#getPlanHistory.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CoverageRecord#getPlanHistory — pending T16")

    def set_plan_at_time(
        self, time: int, new_plan: InsurancePlan, secondary_plan: InsurancePlan
    ) -> None:
        """Java: CoverageRecord#setPlanAtTime.

        Java overloads:
        (long time, InsurancePlan newPlan, InsurancePlan secondaryPlan)
        """
        raise NotImplementedError("Java: CoverageRecord#setPlanAtTime — pending T16")

    def set_plan_to_no_insurance(self, time: int) -> None:
        """Java: CoverageRecord#setPlanToNoInsurance.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: CoverageRecord#setPlanToNoInsurance — pending T16")

    def get_plan_record_at_time(self, time: int) -> PlanRecord:
        """Java: CoverageRecord#getPlanRecordAtTime.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: CoverageRecord#getPlanRecordAtTime — pending T16")

    def get_plan_at_time(self, time: int) -> InsurancePlan:
        """Java: CoverageRecord#getPlanAtTime.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: CoverageRecord#getPlanAtTime — pending T16")

    def get_last_plan_record(self) -> PlanRecord:
        """Java: CoverageRecord#getLastPlanRecord.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CoverageRecord#getLastPlanRecord — pending T16")

    def new_enrollment_period(self, time: int) -> bool:
        """Java: CoverageRecord#newEnrollmentPeriod.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: CoverageRecord#newEnrollmentPeriod — pending T16")

    def get_total_out_of_pocket_expenses(self) -> Decimal:
        """Java: CoverageRecord#getTotalOutOfPocketExpenses.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CoverageRecord#getTotalOutOfPocketExpenses — pending T16")

    def get_total_premium_expenses(self) -> Decimal:
        """Java: CoverageRecord#getTotalPremiumExpenses.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CoverageRecord#getTotalPremiumExpenses — pending T16")

    def get_total_coverage(self) -> Decimal:
        """Java: CoverageRecord#getTotalCoverage.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: CoverageRecord#getTotalCoverage — pending T16")

    def income_remaining(self, time: int) -> int:
        """Java: CoverageRecord#incomeRemaining.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: CoverageRecord#incomeRemaining — pending T16")

    def pay_monthly_premiums_at_time(self, time: int, employer_level: float, income: int) -> None:
        """Java: CoverageRecord#payMonthlyPremiumsAtTime.

        Java overloads:
        (long time, double employerLevel, int income)
        """
        raise NotImplementedError("Java: CoverageRecord#payMonthlyPremiumsAtTime — pending T16")

    def update_last_payer_qols(self, qols_for_year: float) -> None:
        """Java: CoverageRecord#updateLastPayerQols.

        Java overloads:
        (double qolsForYear)
        """
        raise NotImplementedError("Java: CoverageRecord#updateLastPayerQols — pending T16")
