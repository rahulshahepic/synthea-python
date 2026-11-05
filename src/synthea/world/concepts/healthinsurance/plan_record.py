"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/concepts/healthinsurance/PlanRecord.java.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.healthinsurance.insurance_plan import InsurancePlan


class PlanRecord:
    """Java: PlanRecord; pending T16."""

    serialVersionUID: ClassVar[int] = -547445624583743525

    def __init__(self, time: int, plan: InsurancePlan, next_enrollment_period: int) -> None:
        """Java: PlanRecord#PlanRecord.

        Java overloads:
        (long time, InsurancePlan plan, long nextEnrollmentPeriod)
        """
        self.id: str
        self.start: int
        self.stop: int
        self.plan: InsurancePlan
        self.secondary_plan: InsurancePlan
        self.ownership: str
        self.owner_name: str
        self.covered_expenses: Decimal
        self.remaining_deductible: Decimal
        self.out_of_pocket_expenses: Decimal
        self.insurance_expenses: Decimal
        raise NotImplementedError("Java: PlanRecord#PlanRecord — pending T16")

    def pay_monthly_premiums(self, employer_level: float, income: int) -> Decimal:
        """Java: PlanRecord#payMonthlyPremiums.

        Java overloads:
        (double employerLevel, int income)
        """
        raise NotImplementedError("Java: PlanRecord#payMonthlyPremiums — pending T16")

    def update_stop_time(self, updated_stop_time: int) -> None:
        """Java: PlanRecord#updateStopTime.

        Java overloads:
        (long updatedStopTime)
        """
        raise NotImplementedError("Java: PlanRecord#updateStopTime — pending T16")

    def to_string(self) -> str:
        """Java: PlanRecord#toString.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: PlanRecord#toString — pending T16")

    def increment_out_of_pocket_expenses(self, expenses: Decimal) -> None:
        """Java: PlanRecord#incrementOutOfPocketExpenses.

        Java overloads:
        (BigDecimal expenses)
        """
        raise NotImplementedError("Java: PlanRecord#incrementOutOfPocketExpenses — pending T16")

    def increment_primary_coverage(self, coverage: Decimal) -> None:
        """Java: PlanRecord#incrementPrimaryCoverage.

        Java overloads:
        (BigDecimal coverage)
        """
        raise NotImplementedError("Java: PlanRecord#incrementPrimaryCoverage — pending T16")

    def increment_secondary_coverage(self, coverage: Decimal) -> None:
        """Java: PlanRecord#incrementSecondaryCoverage.

        Java overloads:
        (BigDecimal coverage)
        """
        raise NotImplementedError("Java: PlanRecord#incrementSecondaryCoverage — pending T16")

    def get_out_of_pocket_expenses(self) -> Decimal:
        """Java: PlanRecord#getOutOfPocketExpenses.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: PlanRecord#getOutOfPocketExpenses — pending T16")

    def get_covered_expenses(self) -> Decimal:
        """Java: PlanRecord#getCoveredExpenses.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: PlanRecord#getCoveredExpenses — pending T16")

    def get_insurance_expenses(self) -> Decimal:
        """Java: PlanRecord#getInsuranceExpenses.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: PlanRecord#getInsuranceExpenses — pending T16")

    def get_plan(self) -> InsurancePlan:
        """Java: PlanRecord#getPlan.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: PlanRecord#getPlan — pending T16")

    def determine_plan_ownership(self, time: int, person: Person, prev_record: PlanRecord) -> None:
        """Java: PlanRecord#determinePlanOwnership.

        Java overloads:
        (long time, Person person, PlanRecord prevRecord)
        """
        raise NotImplementedError("Java: PlanRecord#determinePlanOwnership — pending T16")

    def get_start_time(self) -> int:
        """Java: PlanRecord#getStartTime.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: PlanRecord#getStartTime — pending T16")

    def get_stop_time(self) -> int:
        """Java: PlanRecord#getStopTime.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: PlanRecord#getStopTime — pending T16")

    def set_secondary_plan(self, secondary_plan: InsurancePlan) -> None:
        """Java: PlanRecord#setSecondaryPlan.

        Java overloads:
        (InsurancePlan secondaryPlan)
        """
        raise NotImplementedError("Java: PlanRecord#setSecondaryPlan — pending T16")

    def get_secondary_plan(self) -> InsurancePlan:
        """Java: PlanRecord#getSecondaryPlan.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: PlanRecord#getSecondaryPlan — pending T16")
