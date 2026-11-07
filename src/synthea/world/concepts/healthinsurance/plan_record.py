"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/concepts/healthinsurance/PlanRecord.java.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar, cast

from synthea.javacompat import bigdecimal as bd
from synthea.world.concepts.claim import Claim

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.healthinsurance.insurance_plan import InsurancePlan


class PlanRecord:
    """Java: PlanRecord."""

    serialVersionUID: ClassVar[int] = -547445624583743525

    def __init__(self, time: int, plan: InsurancePlan, next_enrollment_period: int) -> None:
        """Java: PlanRecord#PlanRecord.

        Java overloads:
        (long time, InsurancePlan plan, long nextEnrollmentPeriod)
        """
        # Java: id, secondaryPlan, ownership and ownerName start out null.
        # The T04 skeleton types them non-optional and merged code (T14's
        # Claim) is written against that contract, so the nulls are cast.
        self.id: str = cast("str", None)
        self.start: int = time
        self.stop: int = next_enrollment_period
        self.plan: InsurancePlan = plan
        self.secondary_plan: InsurancePlan = cast("InsurancePlan", None)
        self.ownership: str = cast("str", None)
        self.owner_name: str = cast("str", None)
        self.covered_expenses: Decimal = Claim.ZERO_CENTS
        self.remaining_deductible: Decimal = plan.get_deductible()
        self.out_of_pocket_expenses: Decimal = Claim.ZERO_CENTS
        self.insurance_expenses: Decimal = Claim.ZERO_CENTS

    def pay_monthly_premiums(self, employer_level: float, income: int) -> Decimal:
        """Java: PlanRecord#payMonthlyPremiums.

        Java overloads:
        (double employerLevel, int income)
        """
        # Java dereferences secondaryPlan unconditionally (NullPointerException
        # if it was never set); CoverageRecord.setPlanAtTime always sets it.
        premium_paid = bd.add(
            self.plan.pay_monthly_premium(employer_level, income),
            self.secondary_plan.pay_monthly_premium(employer_level, income),
        )
        self.insurance_expenses = bd.add(self.insurance_expenses, premium_paid)
        return premium_paid

    def update_stop_time(self, updated_stop_time: int) -> None:
        """Java: PlanRecord#updateStopTime.

        Java overloads:
        (long updatedStopTime)
        """
        self.stop = updated_stop_time

    def to_string(self) -> str:
        """Java: PlanRecord#toString.

        Java overloads:
        ()
        """
        return (
            "{PlanRecord:"
            + " Start: "
            + str(self.start)
            + " Stop: "
            + str(self.stop)
            + " Payer: "
            + self.plan.get_payer().get_name()
            + "}"
        )

    def __str__(self) -> str:
        """Java: PlanRecord#toString."""
        return self.to_string()

    def increment_out_of_pocket_expenses(self, expenses: Decimal) -> None:
        """Java: PlanRecord#incrementOutOfPocketExpenses.

        Java overloads:
        (BigDecimal expenses)
        """
        self.out_of_pocket_expenses = bd.add(self.out_of_pocket_expenses, expenses)
        self.plan.add_uncovered_cost(expenses)

    def increment_primary_coverage(self, coverage: Decimal) -> None:
        """Java: PlanRecord#incrementPrimaryCoverage.

        Java overloads:
        (BigDecimal coverage)
        """
        self.covered_expenses = bd.add(self.covered_expenses, coverage)
        self.plan.add_covered_cost(coverage)

    def increment_secondary_coverage(self, coverage: Decimal) -> None:
        """Java: PlanRecord#incrementSecondaryCoverage.

        Java overloads:
        (BigDecimal coverage)
        """
        self.covered_expenses = bd.add(self.covered_expenses, coverage)
        self.secondary_plan.add_covered_cost(coverage)

    def get_out_of_pocket_expenses(self) -> Decimal:
        """Java: PlanRecord#getOutOfPocketExpenses.

        Java overloads:
        ()
        """
        return self.out_of_pocket_expenses

    def get_covered_expenses(self) -> Decimal:
        """Java: PlanRecord#getCoveredExpenses.

        Java overloads:
        ()
        """
        return self.covered_expenses

    def get_insurance_expenses(self) -> Decimal:
        """Java: PlanRecord#getInsuranceExpenses.

        Java overloads:
        ()
        """
        return self.insurance_expenses

    def get_plan(self) -> InsurancePlan:
        """Java: PlanRecord#getPlan.

        Java overloads:
        ()
        """
        return self.plan

    def determine_plan_ownership(
        self, time: int, person: Person, prev_record: PlanRecord | None
    ) -> None:
        """Java: PlanRecord#determinePlanOwnership.

        Java overloads:
        (long time, Person person, PlanRecord prevRecord)

        InsurancePlan has no Java equals override, so the prevRecord plan
        comparison is identity, mirrored here with ``is``.
        """
        from synthea.world.agents.person import Person

        payer = self.plan.get_payer()

        age = person.age_in_years(time)
        # Keep previous year's ownership if payer is unchanged and person has
        # not just turned 18.
        if (
            prev_record is not None
            and self.plan is prev_record.plan
            and prev_record.ownership is not None
            and prev_record.ownership == "Guardian"
            and age <= 18
        ):
            self.ownership = prev_record.ownership
            self.owner_name = prev_record.owner_name
            self.id = prev_record.id
            return
        if payer.is_no_insurance():
            # No owner for no insurance.
            self.ownership = cast("str", None)
            self.owner_name = cast("str", None)
            self.id = cast("str", None)
            return
        # New Id is required since this is not the same as the previous insurance.
        self.id = str(person.rand_uuid())
        if age < 18 and payer.is_government_payer():
            # If a person is a minor and is on government insurance, they own
            # their own insurance.
            self.ownership = "Self"
            self.owner_name = cast("str", person.attributes.get(Person.NAME))
            return
        if age < 18:
            # If a person is a minor, their Guardian owns their health plan
            # unless it is government.
            self.ownership = "Guardian"
            if person.rand_boolean():
                self.owner_name = cast("str", person.attributes.get(Person.NAME_MOTHER))
            else:
                self.owner_name = cast("str", person.attributes.get(Person.NAME_FATHER))
            return
        if (Person.MARITAL_STATUS in person.attributes) and person.attributes[
            Person.MARITAL_STATUS
        ] == "M":
            # If a person is married, there is a 50% chance their spouse owns
            # their insurance.
            if person.rand_boolean():
                self.ownership = "Spouse"
                if person.attributes[Person.SEXUAL_ORIENTATION] == "homosexual":
                    if person.attributes[Person.GENDER] == "M":
                        self.owner_name = "Mr. "
                    else:
                        self.owner_name = "Mrs. "
                else:
                    if person.attributes[Person.GENDER] == "M":
                        self.owner_name = "Mrs. "
                    else:
                        self.owner_name = "Mr. "
                self.owner_name += cast("str", person.attributes[Person.LAST_NAME])
            else:
                self.ownership = "Self"
                self.owner_name = cast("str", person.attributes.get(Person.NAME))
            return
        # If a person is unmarried and over 18, they own their insurance.
        self.ownership = "Self"
        self.owner_name = cast("str", person.attributes.get(Person.NAME))

    def get_start_time(self) -> int:
        """Java: PlanRecord#getStartTime.

        Java overloads:
        ()
        """
        return self.start

    def get_stop_time(self) -> int:
        """Java: PlanRecord#getStopTime.

        Java overloads:
        ()
        """
        return self.stop

    def set_secondary_plan(self, secondary_plan: InsurancePlan) -> None:
        """Java: PlanRecord#setSecondaryPlan.

        Java overloads:
        (InsurancePlan secondaryPlan)
        """
        self.secondary_plan = secondary_plan

    def get_secondary_plan(self) -> InsurancePlan:
        """Java: PlanRecord#getSecondaryPlan.

        Java overloads:
        ()
        """
        return self.secondary_plan
