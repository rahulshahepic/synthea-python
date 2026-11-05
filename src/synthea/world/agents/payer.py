"""Java API skeleton: Payer.java."""

from __future__ import annotations

import builtins
from decimal import Decimal
from typing import IO, TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from synthea.world.agents.behaviors.payeradjustment.i_payer_adjustment import IPayerAdjustment
    from synthea.world.agents.person import Person
    from synthea.world.concepts.claim import ClaimEntry
    from synthea.world.concepts.health_record import Entry
    from synthea.world.concepts.healthinsurance.insurance_plan import InsurancePlan

    class AtomicInteger(Protocol):
        """Java boundary type: AtomicInteger; external to the mapped Python port."""


class Payer:
    """Java: Payer; pending T15."""

    def __init__(
        self, name: str, id: int, states_covered: builtins.set[str], ownership: str
    ) -> None:
        """Java: Payer#Payer.

        Java overloads:
        (String name, int id, Set statesCovered, String ownership)
        """
        self.payer_adjustment: IPayerAdjustment
        self.attributes: dict[str, object]
        self.name: str
        self.uuid: str
        self.plans: list[InsurancePlan]
        self.ownership: str
        self.plan_link_id: int
        self.states_covered: builtins.set[str]
        self.revenue: Decimal
        self.costs_covered: Decimal
        self.costs_uncovered: Decimal
        self.total_qols: float
        self.customer_utilization: dict[str, AtomicInteger]
        self.entry_utilization: dict[int, str]
        raise NotImplementedError("Java: Payer#Payer — pending T15")

    def write_object(self, oos: IO[bytes]) -> None:
        """Java: Payer#writeObject.

        Java overloads:
        (ObjectOutputStream oos)
        """
        raise NotImplementedError("Java: Payer#writeObject — pending T15")

    def read_object(self, ois: IO[bytes]) -> None:
        """Java: Payer#readObject.

        Java overloads:
        (ObjectInputStream ois)
        """
        raise NotImplementedError("Java: Payer#readObject — pending T15")

    def add_plan(self, new_plan: InsurancePlan) -> None:
        """Java: Payer#addPlan.

        Java overloads:
        (InsurancePlan newPlan)
        """
        raise NotImplementedError("Java: Payer#addPlan — pending T15")

    def is_government_payer(self) -> bool:
        """Java: Payer#isGovernmentPayer.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Payer#isGovernmentPayer — pending T15")

    def get_resource_id(self) -> str:
        """Java: Payer#getResourceID.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Payer#getResourceID — pending T15")

    def get_name(self) -> str:
        """Java: Payer#getName.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Payer#getName — pending T15")

    def get_ownership(self) -> str:
        """Java: Payer#getOwnership.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Payer#getOwnership — pending T15")

    def get_attributes(self) -> dict[str, object]:
        """Java: Payer#getAttributes.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Payer#getAttributes — pending T15")

    def get_plans(self) -> list[InsurancePlan]:
        """Java: Payer#getPlans.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Payer#getPlans — pending T15")

    def covers_care(self, entry: Entry) -> bool:
        """Java: Payer#coversCare.

        Java overloads:
        (Entry entry)
        """
        raise NotImplementedError("Java: Payer#coversCare — pending T15")

    def adjust_claim(self, claim_entry: ClaimEntry, person: Person) -> Decimal:
        """Java: Payer#adjustClaim.

        Java overloads:
        (ClaimEntry claimEntry, Person person)
        """
        raise NotImplementedError("Java: Payer#adjustClaim — pending T15")

    def increment_customers(self, person_id: str) -> None:
        """Java: Payer#incrementCustomers.

        Java overloads:
        (String personId)
        """
        raise NotImplementedError("Java: Payer#incrementCustomers — pending T15")

    def increment_covered_entries(self, entry: Entry) -> None:
        """Java: Payer#incrementCoveredEntries.

        Java overloads:
        (Entry entry)
        """
        raise NotImplementedError("Java: Payer#incrementCoveredEntries — pending T15")

    def increment_uncovered_entries(self, entry: Entry) -> None:
        """Java: Payer#incrementUncoveredEntries.

        Java overloads:
        (Entry entry)
        """
        raise NotImplementedError("Java: Payer#incrementUncoveredEntries — pending T15")

    def get_entry_type(self, entry: Entry) -> str:
        """Java: Payer#getEntryType.

        Java overloads:
        (Entry entry)
        """
        raise NotImplementedError("Java: Payer#getEntryType — pending T15")

    def increment_entries(self, year: int, key: str) -> None:
        """Java: Payer#incrementEntries.

        Java overloads:
        (Integer year, String key)
        """
        raise NotImplementedError("Java: Payer#incrementEntries — pending T15")

    def add_covered_cost(self, cost_to_payer: Decimal) -> None:
        """Java: Payer#addCoveredCost.

        Java overloads:
        (BigDecimal costToPayer)
        """
        raise NotImplementedError("Java: Payer#addCoveredCost — pending T15")

    def add_uncovered_cost(self, cost_to_patient: Decimal) -> None:
        """Java: Payer#addUncoveredCost.

        Java overloads:
        (BigDecimal costToPatient)
        """
        raise NotImplementedError("Java: Payer#addUncoveredCost — pending T15")

    def add_qols(self, qols: float) -> None:
        """Java: Payer#addQols.

        Java overloads:
        (double qols)
        """
        raise NotImplementedError("Java: Payer#addQols — pending T15")

    def get_revenue(self) -> Decimal:
        """Java: Payer#getRevenue.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Payer#getRevenue — pending T15")

    def get_customer_utilization(self, person_id: str) -> int:
        """Java: Payer#getCustomerUtilization.

        Java overloads:
        (String personId)
        """
        raise NotImplementedError("Java: Payer#getCustomerUtilization — pending T15")

    def get_unique_customers(self) -> int:
        """Java: Payer#getUniqueCustomers.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Payer#getUniqueCustomers — pending T15")

    def get_num_years_covered(self) -> int:
        """Java: Payer#getNumYearsCovered.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Payer#getNumYearsCovered — pending T15")

    def get_encounters_covered_count(self) -> int:
        """Java: Payer#getEncountersCoveredCount.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Payer#getEncountersCoveredCount — pending T15")

    def get_encounters_uncovered_count(self) -> int:
        """Java: Payer#getEncountersUncoveredCount.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Payer#getEncountersUncoveredCount — pending T15")

    def get_medications_covered_count(self) -> int:
        """Java: Payer#getMedicationsCoveredCount.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Payer#getMedicationsCoveredCount — pending T15")

    def get_medications_uncovered_count(self) -> int:
        """Java: Payer#getMedicationsUncoveredCount.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Payer#getMedicationsUncoveredCount — pending T15")

    def get_procedures_covered_count(self) -> int:
        """Java: Payer#getProceduresCoveredCount.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Payer#getProceduresCoveredCount — pending T15")

    def get_procedures_uncovered_count(self) -> int:
        """Java: Payer#getProceduresUncoveredCount.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Payer#getProceduresUncoveredCount — pending T15")

    def get_immunizations_covered_count(self) -> int:
        """Java: Payer#getImmunizationsCoveredCount.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Payer#getImmunizationsCoveredCount — pending T15")

    def get_immunizations_uncovered_count(self) -> int:
        """Java: Payer#getImmunizationsUncoveredCount.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Payer#getImmunizationsUncoveredCount — pending T15")

    def get_amount_covered(self) -> Decimal:
        """Java: Payer#getAmountCovered.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Payer#getAmountCovered — pending T15")

    def get_amount_uncovered(self) -> Decimal:
        """Java: Payer#getAmountUncovered.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Payer#getAmountUncovered — pending T15")

    def get_qols_average(self) -> float:
        """Java: Payer#getQolsAverage.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Payer#getQolsAverage — pending T15")

    def hash_code(self) -> int:
        """Java: Payer#hashCode.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Payer#hashCode — pending T15")

    def equals(self, obj: object) -> bool:
        """Java: Payer#equals.

        Java overloads:
        (Object obj)
        """
        raise NotImplementedError("Java: Payer#equals — pending T15")

    def set_payer_adjustment(self, payer_adjustment: IPayerAdjustment) -> None:
        """Java: Payer#setPayerAdjustment.

        Java overloads:
        (IPayerAdjustment payerAdjustment)
        """
        raise NotImplementedError("Java: Payer#setPayerAdjustment — pending T15")

    def add_revenue(self, additional_revenue: Decimal) -> None:
        """Java: Payer#addRevenue.

        Java overloads:
        (BigDecimal additionalRevenue)
        """
        raise NotImplementedError("Java: Payer#addRevenue — pending T15")

    def get_government_payer_plan(self) -> InsurancePlan:
        """Java: Payer#getGovernmentPayerPlan.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Payer#getGovernmentPayerPlan — pending T15")

    def add_attribute(self, key: str, value: str) -> None:
        """Java: Payer#addAttribute.

        Java overloads:
        (String key, String value)
        """
        raise NotImplementedError("Java: Payer#addAttribute — pending T15")

    def is_no_insurance(self) -> bool:
        """Java: Payer#isNoInsurance.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Payer#isNoInsurance — pending T15")

    def get_plan_link_id(self) -> int:
        """Java: Payer#getPlanLinkId.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Payer#getPlanLinkId — pending T15")


class UtilizationBean:
    """Java: UtilizationBean; pending T15."""

    def __init__(self, year: int, type: str, count: AtomicInteger) -> None:
        """Java: UtilizationBean#UtilizationBean.

        Java overloads:
        (Integer year, String type, AtomicInteger count)
        """
        self.year: int
        self.type: str
        self.count: AtomicInteger
        raise NotImplementedError("Java: UtilizationBean#UtilizationBean — pending T15")


setattr(Payer, "UtilizationBean", UtilizationBean)  # noqa: B010
