"""Java API skeleton: PayerManager.java."""

from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.world.agents.behaviors.payeradjustment.i_payer_adjustment import IPayerAdjustment
    from synthea.world.agents.behaviors.planfinder.i_plan_finder import IPlanFinder
    from synthea.world.agents.payer import Payer
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import EncounterType
    from synthea.world.concepts.healthinsurance.insurance_plan import InsurancePlan
    from synthea.world.geography.location import Location


class PayerManager:
    """Java: PayerManager; pending T15."""

    NONE: ClassVar[str] = "none"
    FIXED: ClassVar[str] = "fixed"
    RANDOM: ClassVar[str] = "random"
    BEST_RATE: ClassVar[str] = "best_rate"
    PRIORITY: ClassVar[str] = "priority"
    NAME: ClassVar[str] = "Name"
    ID: ClassVar[str] = "Id"
    PRIORITY_LEVEL: ClassVar[str] = "Priority Level"
    STATES_COVERED: ClassVar[str] = "States Covered"
    OWNERSHIP: ClassVar[str] = "Ownership"
    PAYER_ID: ClassVar[str] = "Payer Id"
    PLAN_ID: ClassVar[str] = "Plan Id"
    SERVICES_COVERED: ClassVar[str] = "Services Covered"
    DEDUCTIBLE: ClassVar[str] = "Deductible"
    COINSURANCE: ClassVar[str] = "Default Coinsurance"
    COPAY: ClassVar[str] = "Default Copay"
    MONTHLY_PREMIUM: ClassVar[str] = "Monthly Premium"
    MAX_OOP: ClassVar[str] = "Max Out of Pocket"
    MEDICARE_SUPPLEMENT: ClassVar[str] = "Medicare Supplement"
    ACA: ClassVar[str] = "Is ACA Plan"
    INCOME_BASED_PREMIUM: ClassVar[str] = "Income Based Premium"
    START_YEAR: ClassVar[str] = "Start Year"
    END_YEAR: ClassVar[str] = "End Year"
    ELIGIBILITY_POLICY: ClassVar[str] = "Eligibility Policy"
    GOV_OWNERSHIP: ClassVar[str] = "GOVERNMENT"
    PRIVATE_OWNERSHIP: ClassVar[str] = "PRIVATE"
    NO_INSURANCE: ClassVar[str] = "NO_INSURANCE"
    MEDICARE: ClassVar[str]  # Java initialization deferred to T15.
    MEDICAID: ClassVar[str]  # Java initialization deferred to T15.
    DUAL_ELIGIBLE: ClassVar[str]  # Java initialization deferred to T15.
    payers: ClassVar[dict[int, Payer]] = {}
    noInsurance: ClassVar[Payer]  # Java initialization deferred to T15.
    statesLoaded: ClassVar[builtins.set[str]] = set()
    planFinder: ClassVar[IPlanFinder]  # Java initialization deferred to T15.

    def __init__(self) -> None:
        """Java: PayerManager#PayerManager.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: PayerManager#PayerManager — pending T15")

    @staticmethod
    def load_payers(location: Location, file_name: str | None = None) -> None:
        """Java: PayerManager#loadPayers.

        Java overloads:
        (Location location)
        (Location location, String fileName)
        """
        raise NotImplementedError("Java: PayerManager#loadPayers — pending T15")

    @staticmethod
    def load_plans() -> None:
        """Java: PayerManager#loadPlans.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: PayerManager#loadPlans — pending T15")

    @staticmethod
    def build_plan_finder() -> IPlanFinder:
        """Java: PayerManager#buildPlanFinder.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: PayerManager#buildPlanFinder — pending T15")

    @staticmethod
    def build_payer_adjustment() -> IPayerAdjustment:
        """Java: PayerManager#buildPayerAdjustment.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: PayerManager#buildPayerAdjustment — pending T15")

    @staticmethod
    def csv_line_to_payer(line: dict[str, str]) -> Payer:
        """Java: PayerManager#csvLineToPayer.

        Java overloads:
        (Map line)
        """
        raise NotImplementedError("Java: PayerManager#csvLineToPayer — pending T15")

    @staticmethod
    def csv_line_to_plan(line: dict[str, str]) -> None:
        """Java: PayerManager#csvLineToPlan.

        Java overloads:
        (Map line)
        """
        raise NotImplementedError("Java: PayerManager#csvLineToPlan — pending T15")

    @staticmethod
    def comma_separated_string_to_hash_set(field: str) -> builtins.set[str]:
        """Java: PayerManager#commaSeparatedStringToHashSet.

        Java overloads:
        (String field)
        """
        raise NotImplementedError("Java: PayerManager#commaSeparatedStringToHashSet — pending T15")

    @staticmethod
    def load_no_insurance() -> None:
        """Java: PayerManager#loadNoInsurance.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: PayerManager#loadNoInsurance — pending T15")

    @staticmethod
    def get_all_payers() -> list[Payer]:
        """Java: PayerManager#getAllPayers.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: PayerManager#getAllPayers — pending T15")

    @staticmethod
    def clear() -> None:
        """Java: PayerManager#clear.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: PayerManager#clear — pending T15")

    @staticmethod
    def find_plan(person: Person, service: EncounterType, time: int) -> InsurancePlan:
        """Java: PayerManager#findPlan.

        Java overloads:
        (Person person, EncounterType service, long time)
        """
        raise NotImplementedError("Java: PayerManager#findPlan — pending T15")

    @staticmethod
    def get_active_plans(payers: list[Payer], time: int) -> list[InsurancePlan]:
        """Java: PayerManager#getActivePlans.

        Java overloads:
        (List payers, long time)
        """
        raise NotImplementedError("Java: PayerManager#getActivePlans — pending T15")

    @staticmethod
    def get_no_insurance_plan() -> InsurancePlan:
        """Java: PayerManager#getNoInsurancePlan.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: PayerManager#getNoInsurancePlan — pending T15")

    @staticmethod
    def find_medicare_supplement(
        person: Person, service: EncounterType, time: int
    ) -> InsurancePlan:
        """Java: PayerManager#findMedicareSupplement.

        Java overloads:
        (Person person, EncounterType service, long time)
        """
        raise NotImplementedError("Java: PayerManager#findMedicareSupplement — pending T15")
