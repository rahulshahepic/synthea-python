"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/concepts/healthinsurance/CoverageRecord.java.
"""

from __future__ import annotations

import builtins
from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar, cast

from synthea.helpers.config import Config
from synthea.helpers.utilities import Utilities
from synthea.javacompat import bigdecimal as bd
from synthea.world.concepts.claim import Claim
from synthea.world.concepts.healthinsurance.plan_record import PlanRecord

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.healthinsurance.insurance_plan import InsurancePlan


def _add_one_calendar_year(time: int) -> int:
    """java.util.Calendar.add(Calendar.YEAR, 1) on a UTC GregorianCalendar.

    Calendar.add pins an invalid day-of-month to the last day of the target
    month (Feb 29 + 1 year is Feb 28), unlike the lenient field-set semantics
    of Utilities.get_anniversary. Millis within the day are preserved.
    """
    day = Utilities.timestamp_to_local_date(time)
    millis_of_day = time - Utilities.local_date_to_timestamp(day)
    try:
        next_day = day.replace(year=day.year + 1)
    except ValueError:
        next_day = day.replace(year=day.year + 1, day=28)
    return Utilities.local_date_to_timestamp(next_day) + millis_of_day


class CoverageRecord:
    """Java: CoverageRecord."""

    serialVersionUID: ClassVar[int] = 771457063723016307

    def __init__(self, person: Person) -> None:
        """Java: CoverageRecord#CoverageRecord.

        Java overloads:
        (Person person)
        """
        self.person: Person = person
        self.plan_history: builtins.set[PlanRecord] = set()
        self.next_enrollment_period: int | None = None

    def get_plan_history(self) -> builtins.set[PlanRecord]:
        """Java: CoverageRecord#getPlanHistory.

        Java overloads:
        ()
        """
        return self.plan_history

    def set_plan_at_time(
        self, time: int, new_plan: InsurancePlan, secondary_plan: InsurancePlan
    ) -> None:
        """Java: CoverageRecord#setPlanAtTime.

        Java overloads:
        (long time, InsurancePlan newPlan, InsurancePlan secondaryPlan)
        """
        from synthea.world.agents.person import Person

        if not self.plan_history:
            if self.person.age_in_decimal_years(time) >= 1.0:
                raise RuntimeError(
                    "Person was greater than the age"
                    " of 1 when recieving their initial insurance plan."
                )
            # If this is the person's first plan, set the start date to their birthdate.
            time = cast(int, self.person.attributes[Person.BIRTHDATE])
            self.new_enrollment_period(time)
        else:
            # Set the new stop date of the last insurance plan to prevent any gaps.
            plan_record = self.get_last_plan_record()
            plan_record.update_stop_time(time)

        plan_record = PlanRecord(time, new_plan, cast(int, self.next_enrollment_period))
        plan_record.set_secondary_plan(secondary_plan)
        prev_plan_record = None
        if self.plan_history:
            prev_plan_record = self.get_last_plan_record()
        plan_record.determine_plan_ownership(time, self.person, prev_plan_record)
        self.plan_history.add(plan_record)
        # Set the person's insurance status.
        self.person.attributes[Person.INSURANCE_STATUS] = new_plan.get_insurance_status()

    def set_plan_to_no_insurance(self, time: int) -> None:
        """Java: CoverageRecord#setPlanToNoInsurance.

        Java overloads:
        (long time)
        """
        from synthea.world.agents.payer_manager import PayerManager

        self.set_plan_at_time(
            time, PayerManager.get_no_insurance_plan(), PayerManager.get_no_insurance_plan()
        )

    def get_plan_record_at_time(self, time: int) -> PlanRecord:
        """Java: CoverageRecord#getPlanRecordAtTime.

        Java overloads:
        (long time)
        """
        for plan_record in self.plan_history:
            if plan_record.get_start_time() <= time < plan_record.get_stop_time():
                return plan_record
        raise RuntimeError("Person does not have insurance at time " + str(time) + ".")

    def get_plan_at_time(self, time: int) -> InsurancePlan:
        """Java: CoverageRecord#getPlanAtTime.

        Java overloads:
        (long time)
        """
        return self.get_plan_record_at_time(time).get_plan()

    def get_last_plan_record(self) -> PlanRecord:
        """Java: CoverageRecord#getLastPlanRecord.

        Java overloads:
        ()
        """
        if not self.plan_history:
            raise RuntimeError(
                "Invalid attempt to get previous insurance plan for a"
                " patient with no insurance history."
            )
        return max(self.plan_history, key=lambda plan: plan.get_stop_time())

    def new_enrollment_period(self, time: int) -> bool:
        """Java: CoverageRecord#newEnrollmentPeriod.

        Java overloads:
        (long time)
        """
        from synthea.world.agents.person import Person

        if self.next_enrollment_period is None:
            # Initialize enrollment.
            self.next_enrollment_period = cast(int, self.person.attributes[Person.BIRTHDATE])
        if time >= self.next_enrollment_period:
            self.next_enrollment_period = _add_one_calendar_year(self.next_enrollment_period)
            return True
        return False

    def get_total_out_of_pocket_expenses(self) -> Decimal:
        """Java: CoverageRecord#getTotalOutOfPocketExpenses.

        Java overloads:
        ()
        """
        total = Decimal(0)  # Java: BigDecimal.ZERO (scale 0 matters for toString).
        for plan_record in self.plan_history:
            total = bd.add(total, plan_record.get_out_of_pocket_expenses())
        return total

    def get_total_premium_expenses(self) -> Decimal:
        """Java: CoverageRecord#getTotalPremiumExpenses.

        Java overloads:
        ()
        """
        total = Claim.ZERO_CENTS
        for plan in self.plan_history:
            total = bd.add(total, plan.get_insurance_expenses())
        return total

    def get_total_coverage(self) -> Decimal:
        """Java: CoverageRecord#getTotalCoverage.

        Java overloads:
        ()
        """
        total = Claim.ZERO_CENTS
        for plan_record in self.plan_history:
            total = bd.add(total, plan_record.get_covered_expenses())
        return total

    def income_remaining(self, time: int) -> int:
        """Java: CoverageRecord#incomeRemaining.

        Java overloads:
        (long time)
        """
        from synthea.world.agents.person import Person

        income = cast(int, self.person.attributes[Person.INCOME])
        timestep = Config.get_as_long("generate.timestep")
        birth_date = cast(int, self.person.attributes[Person.BIRTHDATE])
        if (not self.plan_history and time <= (birth_date + timestep)) or not self.person.alive(
            time
        ):
            # Too young to have incurred any expenses yet or they are dead.
            return income
        current_plan_record = self.get_plan_record_at_time(time)
        current_yearly_expenses = Decimal(0)  # Java: BigDecimal.ZERO.
        current_yearly_expenses = bd.add(
            current_yearly_expenses, current_plan_record.get_out_of_pocket_expenses()
        )
        current_yearly_expenses = bd.add(
            current_yearly_expenses, current_plan_record.get_insurance_expenses()
        )

        # Java: BigDecimal.valueOf(long income) — scale 0.
        return bd.int_value(bd.subtract(Decimal(income), current_yearly_expenses))

    def pay_monthly_premiums_at_time(self, time: int, employer_level: float, income: int) -> None:
        """Java: CoverageRecord#payMonthlyPremiumsAtTime.

        Java overloads:
        (long time, double employerLevel, int income)
        """
        self.get_plan_record_at_time(time).pay_monthly_premiums(employer_level, income)

    def update_last_payer_qols(self, qols_for_year: float) -> None:
        """Java: CoverageRecord#updateLastPayerQols.

        Java overloads:
        (double qolsForYear)
        """
        if self.plan_history:
            self.get_last_plan_record().get_plan().get_payer().add_qols(qols_for_year)
