"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/concepts/healthinsurance/InsurancePlan.java.
"""

from __future__ import annotations

import builtins
from decimal import Decimal
from typing import TYPE_CHECKING

from synthea.helpers.config import Config
from synthea.helpers.utilities import Utilities
from synthea.javacompat import bigdecimal as bd
from synthea.javacompat.hashing import string_compare_to_ignore_case
from synthea.world.agents.behaviors.planeligibility.plan_eligibility_finder import (
    PlanEligibilityFinder,
)

if TYPE_CHECKING:
    from synthea.world.agents.behaviors.planeligibility.i_plan_eligibility import IPlanEligibility
    from synthea.world.agents.payer import Payer
    from synthea.world.agents.person import Person
    from synthea.world.concepts.claim import ClaimEntry
    from synthea.world.concepts.health_record import Entry


class InsurancePlan:
    """Java: InsurancePlan."""

    def __init__(
        self,
        id: int,
        payer: Payer,
        services_covered: builtins.set[str],
        deductible: Decimal,
        default_coinsurance: Decimal,
        default_copay: Decimal,
        monthly_premium: Decimal,
        max_out_of_pocket: Decimal,
        medicare_supplement: bool,
        is_aca: bool,
        income_based_premium: bool,
        active_year_start: int,
        active_year_end: int,
        priority: int,
        eligibility_name: str,
    ) -> None:
        """Java: InsurancePlan#InsurancePlan.

        Java overloads:
        (int id, Payer payer, Set servicesCovered, BigDecimal deductible, BigDecimal
        defaultCoinsurance, BigDecimal defaultCopay, BigDecimal monthlyPremium,
        BigDecimal
        maxOutOfPocket, boolean medicareSupplement, boolean isACA, boolean
        incomeBasedPremium,
        int activeYearStart, int activeYearEnd, int priority, String eligibilityName)
        """
        self.id: int = id
        self.payer: Payer = payer
        self.deductible: Decimal = deductible
        self.default_copay: Decimal = default_copay
        self.default_coinsurance: Decimal = default_coinsurance
        self.monthly_premium: Decimal = monthly_premium
        self.max_out_of_pocket: Decimal = max_out_of_pocket
        self.priority: int = priority
        self.services_covered: builtins.set[str] = services_covered
        self.medicare_supplement: bool = medicare_supplement
        self.is_aca: bool = is_aca
        self.income_based_premium: bool = income_based_premium
        if income_based_premium and monthly_premium > Decimal(1):
            raise RuntimeError(
                "Income based premium plans must have premiums in"
                " range 0.0 - 1.0, a percentage of a patient's income. Given "
                + bd.to_string(monthly_premium)
                + "."
            )
        if active_year_start >= active_year_end:
            raise RuntimeError(
                "Plan start year cannot be after its end year. "
                f"Given start year: {active_year_start} and end year {active_year_end}."
            )
        start = Utilities.convert_calendar_years_to_time(active_year_start)
        end = (
            (1 << 63) - 1
            if active_year_end == (1 << 31) - 1
            else Utilities.convert_calendar_years_to_time(active_year_end)
        )
        self.active_time_range: tuple[int, int] = (min(start, end), max(start, end))
        self.plan_eligibility: IPlanEligibility = PlanEligibilityFinder.get_eligibility_algorithm(
            eligibility_name
        )
        self.insurance_status: str = self.determine_insurance_status()

    def is_active(self, time: int) -> bool:
        """Java: InsurancePlan#isActive.

        Java overloads:
        (long time)
        """
        return self.active_time_range[0] <= time <= self.active_time_range[1]

    def determine_copay(self, entry_type: str, entry_start: int) -> Decimal:
        """Java: InsurancePlan#determineCopay.

        Java overloads:
        (String entryType, long entryStart)
        """
        from synthea.modules.health_insurance_module import HealthInsuranceModule
        from synthea.world.concepts.claim import Claim

        if (
            string_compare_to_ignore_case(entry_type, "wellness") == 0
            and entry_start > HealthInsuranceModule.mandateTime
        ):
            return Claim.ZERO_CENTS
        return self.default_copay

    def get_monthly_premium(self, income: int) -> Decimal:
        """Java: InsurancePlan#getMonthlyPremium.

        Java overloads:
        (int income)
        """
        if self.income_based_premium:
            return bd.divide_round(
                bd.multiply(
                    bd.set_scale(self.monthly_premium, 2, bd.RoundingMode.HALF_UP), Decimal(income)
                ),
                Decimal(12),
                bd.RoundingMode.HALF_UP,
            )
        return self.monthly_premium

    def get_deductible(self) -> Decimal:
        """Java: InsurancePlan#getDeductible.

        Java overloads:
        ()
        """
        return self.deductible

    def get_payer_coinsurance(self) -> Decimal:
        """Java: InsurancePlan#getPayerCoinsurance.

        Java overloads:
        ()
        """
        return self.default_coinsurance

    def get_patient_coinsurance(self) -> Decimal:
        """Java: InsurancePlan#getPatientCoinsurance.

        Java overloads:
        ()
        """
        coinsurance = bd.subtract(Decimal(1), self.default_coinsurance)
        return coinsurance if coinsurance < Decimal(1) else Decimal(0)

    def pay_monthly_premium(self, employer_level: float, income: int) -> Decimal:
        """Java: InsurancePlan#payMonthlyPremium.

        Java overloads:
        (double employerLevel, int income)
        """
        price = self.get_monthly_premium(income)
        self.payer.add_revenue(price)
        if (
            employer_level > Config.get_as_double("generate.insurance.mandate.occupation")
            and not self.payer.is_government_payer()
            and not self.is_aca
        ):
            contribution = 1.0 - Config.get_as_double("generate.insurance.employer_coverage", 0.83)
            price = bd.multiply(price, bd.value_of(contribution))
        return price

    def get_payer(self) -> Payer:
        """Java: InsurancePlan#getPayer.

        Java overloads:
        ()
        """
        return self.payer

    def determine_insurance_status(self) -> str:
        """Java: InsurancePlan#determineInsuranceStatus.

        Java overloads:
        ()
        """
        if self.is_no_insurance():
            return "none"
        if self.payer.is_government_payer():
            return self.payer.get_name().lower()
        return "private"

    def get_insurance_status(self) -> str:
        """Java: InsurancePlan#getInsuranceStatus.

        Java overloads:
        ()
        """
        return self.insurance_status

    def increment_customers(self, person_id: str) -> None:
        """Java: InsurancePlan#incrementCustomers.

        Java overloads:
        (String personId)
        """
        self.payer.increment_customers(person_id)

    def increment_covered_entries(self, entry: Entry) -> None:
        """Java: InsurancePlan#incrementCoveredEntries.

        Java overloads:
        (Entry entry)
        """
        self.payer.increment_covered_entries(entry)

    def increment_uncovered_entries(self, entry: Entry) -> None:
        """Java: InsurancePlan#incrementUncoveredEntries.

        Java overloads:
        (Entry entry)
        """
        self.payer.increment_uncovered_entries(entry)

    def covers_service(self, entry: Entry | None) -> bool:
        """Java: InsurancePlan#coversService.

        Java overloads:
        (Entry entry)
        """
        return (
            entry is None
            or entry.type is None
            or entry.type in self.services_covered
            or "*" in self.services_covered
        )

    def add_covered_cost(self, covered_costs: Decimal) -> None:
        """Java: InsurancePlan#addCoveredCost.

        Java overloads:
        (BigDecimal coveredCosts)
        """
        self.payer.add_covered_cost(covered_costs)

    def add_uncovered_cost(self, uncovered_costs: Decimal) -> None:
        """Java: InsurancePlan#addUncoveredCost.

        Java overloads:
        (BigDecimal uncoveredCosts)
        """
        self.payer.add_uncovered_cost(uncovered_costs)

    def adjust_claim(self, claim_entry: ClaimEntry, person: Person) -> Decimal:
        """Java: InsurancePlan#adjustClaim.

        Java overloads:
        (ClaimEntry claimEntry, Person person)
        """
        return self.payer.adjust_claim(claim_entry, person)

    def get_yearly_cost(self, income: int) -> Decimal:
        """Java: InsurancePlan#getYearlyCost.

        Java overloads:
        (int income)
        """
        return bd.set_scale(
            bd.multiply(self.get_monthly_premium(income), Decimal(12)), 0, bd.RoundingMode.HALF_EVEN
        )

    def accepts(self, person: Person, time: int) -> bool:
        """Java: InsurancePlan#accepts.

        Java overloads:
        (Person person, long time)
        """
        return self.plan_eligibility.is_person_eligible(person, time)

    def is_no_insurance(self) -> bool:
        """Java: InsurancePlan#isNoInsurance.

        Java overloads:
        ()
        """
        return self.payer.is_no_insurance()

    def is_government_plan(self) -> bool:
        """Java: InsurancePlan#isGovernmentPlan.

        Java overloads:
        ()
        """
        return self.payer.is_government_payer()

    def may_purchase_supplement(self) -> bool:
        """Java: InsurancePlan#mayPurchaseSupplement.

        Java overloads:
        ()
        """
        return self.get_payer().get_name() == "Medicare"

    def is_medicare_supplement_plan(self) -> bool:
        """Java: InsurancePlan#isMedicareSupplementPlan.

        Java overloads:
        ()
        """
        return self.medicare_supplement

    def get_priority(self) -> int:
        """Java: InsurancePlan#getPriority.

        Java overloads:
        ()
        """
        return self.priority

    def is_copay_based(self) -> bool:
        """Java: InsurancePlan#isCopayBased.

        Java overloads:
        ()
        """
        return self.default_copay > Decimal(0)

    def get_max_oop(self) -> Decimal:
        """Java: InsurancePlan#getMaxOop.

        Java overloads:
        ()
        """
        return self.max_out_of_pocket

    def to_string(self) -> str:
        """Java: InsurancePlan#toString.

        Java overloads:
        ()
        """
        return (
            f"InsurancePlan [payer={self.payer.get_name()}"
            f", deductible={bd.to_string(self.deductible)}"
            f", defaultCopay={bd.to_string(self.default_copay)}"
            f", defaultCoinsurance={bd.to_string(self.default_coinsurance)}"
            f", monthlyPremium={bd.to_string(self.monthly_premium)}"
            f", medicareSupplement={str(self.medicare_supplement).lower()}"
            f", insuranceStatus={self.insurance_status}"
            f", planEligibility={self.plan_eligibility}"
            f", activeTimeRange=[{self.active_time_range[0]}..{self.active_time_range[1]}]]"
        )
