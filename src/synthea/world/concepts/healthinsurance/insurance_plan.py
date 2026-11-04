"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/concepts/healthinsurance/InsurancePlan.java.
"""

from __future__ import annotations

import builtins
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.engine.components import Range
    from synthea.world.agents.behaviors.planeligibility.i_plan_eligibility import IPlanEligibility
    from synthea.world.agents.payer import Payer
    from synthea.world.agents.person import Person
    from synthea.world.concepts.claim import ClaimEntry
    from synthea.world.concepts.health_record import Entry


class InsurancePlan:
    """Java: InsurancePlan; pending T15."""

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
        self.id: int
        self.payer: Payer
        self.deductible: Decimal
        self.default_copay: Decimal
        self.default_coinsurance: Decimal
        self.monthly_premium: Decimal
        self.max_out_of_pocket: Decimal
        self.priority: int
        self.services_covered: builtins.set[str]
        self.medicare_supplement: bool
        self.is_aca: bool
        self.income_based_premium: bool
        self.insurance_status: str
        self.plan_eligibility: IPlanEligibility
        self.active_time_range: Range[int]
        raise NotImplementedError("Java: InsurancePlan#InsurancePlan — pending T15")

    def is_active(self, time: int) -> bool:
        """Java: InsurancePlan#isActive.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: InsurancePlan#isActive — pending T15")

    def determine_copay(self, entry_type: str, entry_start: int) -> Decimal:
        """Java: InsurancePlan#determineCopay.

        Java overloads:
        (String entryType, long entryStart)
        """
        raise NotImplementedError("Java: InsurancePlan#determineCopay — pending T15")

    def get_monthly_premium(self, income: int) -> Decimal:
        """Java: InsurancePlan#getMonthlyPremium.

        Java overloads:
        (int income)
        """
        raise NotImplementedError("Java: InsurancePlan#getMonthlyPremium — pending T15")

    def get_deductible(self) -> Decimal:
        """Java: InsurancePlan#getDeductible.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: InsurancePlan#getDeductible — pending T15")

    def get_payer_coinsurance(self) -> Decimal:
        """Java: InsurancePlan#getPayerCoinsurance.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: InsurancePlan#getPayerCoinsurance — pending T15")

    def get_patient_coinsurance(self) -> Decimal:
        """Java: InsurancePlan#getPatientCoinsurance.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: InsurancePlan#getPatientCoinsurance — pending T15")

    def pay_monthly_premium(self, employer_level: float, income: int) -> Decimal:
        """Java: InsurancePlan#payMonthlyPremium.

        Java overloads:
        (double employerLevel, int income)
        """
        raise NotImplementedError("Java: InsurancePlan#payMonthlyPremium — pending T15")

    def get_payer(self) -> Payer:
        """Java: InsurancePlan#getPayer.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: InsurancePlan#getPayer — pending T15")

    def determine_insurance_status(self) -> str:
        """Java: InsurancePlan#determineInsuranceStatus.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: InsurancePlan#determineInsuranceStatus — pending T15")

    def get_insurance_status(self) -> str:
        """Java: InsurancePlan#getInsuranceStatus.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: InsurancePlan#getInsuranceStatus — pending T15")

    def increment_customers(self, person_id: str) -> None:
        """Java: InsurancePlan#incrementCustomers.

        Java overloads:
        (String personId)
        """
        raise NotImplementedError("Java: InsurancePlan#incrementCustomers — pending T15")

    def increment_covered_entries(self, entry: Entry) -> None:
        """Java: InsurancePlan#incrementCoveredEntries.

        Java overloads:
        (Entry entry)
        """
        raise NotImplementedError("Java: InsurancePlan#incrementCoveredEntries — pending T15")

    def increment_uncovered_entries(self, entry: Entry) -> None:
        """Java: InsurancePlan#incrementUncoveredEntries.

        Java overloads:
        (Entry entry)
        """
        raise NotImplementedError("Java: InsurancePlan#incrementUncoveredEntries — pending T15")

    def covers_service(self, entry: Entry) -> bool:
        """Java: InsurancePlan#coversService.

        Java overloads:
        (Entry entry)
        """
        raise NotImplementedError("Java: InsurancePlan#coversService — pending T15")

    def add_covered_cost(self, covered_costs: Decimal) -> None:
        """Java: InsurancePlan#addCoveredCost.

        Java overloads:
        (BigDecimal coveredCosts)
        """
        raise NotImplementedError("Java: InsurancePlan#addCoveredCost — pending T15")

    def add_uncovered_cost(self, uncovered_costs: Decimal) -> None:
        """Java: InsurancePlan#addUncoveredCost.

        Java overloads:
        (BigDecimal uncoveredCosts)
        """
        raise NotImplementedError("Java: InsurancePlan#addUncoveredCost — pending T15")

    def adjust_claim(self, claim_entry: ClaimEntry, person: Person) -> Decimal:
        """Java: InsurancePlan#adjustClaim.

        Java overloads:
        (ClaimEntry claimEntry, Person person)
        """
        raise NotImplementedError("Java: InsurancePlan#adjustClaim — pending T15")

    def get_yearly_cost(self, income: int) -> Decimal:
        """Java: InsurancePlan#getYearlyCost.

        Java overloads:
        (int income)
        """
        raise NotImplementedError("Java: InsurancePlan#getYearlyCost — pending T15")

    def accepts(self, person: Person, time: int) -> bool:
        """Java: InsurancePlan#accepts.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: InsurancePlan#accepts — pending T15")

    def is_no_insurance(self) -> bool:
        """Java: InsurancePlan#isNoInsurance.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: InsurancePlan#isNoInsurance — pending T15")

    def is_government_plan(self) -> bool:
        """Java: InsurancePlan#isGovernmentPlan.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: InsurancePlan#isGovernmentPlan — pending T15")

    def may_purchase_supplement(self) -> bool:
        """Java: InsurancePlan#mayPurchaseSupplement.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: InsurancePlan#mayPurchaseSupplement — pending T15")

    def is_medicare_supplement_plan(self) -> bool:
        """Java: InsurancePlan#isMedicareSupplementPlan.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: InsurancePlan#isMedicareSupplementPlan — pending T15")

    def get_priority(self) -> int:
        """Java: InsurancePlan#getPriority.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: InsurancePlan#getPriority — pending T15")

    def is_copay_based(self) -> bool:
        """Java: InsurancePlan#isCopayBased.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: InsurancePlan#isCopayBased — pending T15")

    def get_max_oop(self) -> Decimal:
        """Java: InsurancePlan#getMaxOop.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: InsurancePlan#getMaxOop — pending T15")

    def to_string(self) -> str:
        """Java: InsurancePlan#toString.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: InsurancePlan#toString — pending T15")
