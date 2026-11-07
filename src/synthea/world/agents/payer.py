"""Java API skeleton: Payer.java."""

from __future__ import annotations

import builtins
import hashlib
import math
from decimal import Decimal
from typing import IO, TYPE_CHECKING, Protocol
from uuid import UUID

from synthea.helpers.utilities import Utilities
from synthea.javacompat import bigdecimal as bd
from synthea.javacompat.collections import JavaHashMap
from synthea.javacompat.hashing import (
    double_hash_code,
    double_to_long_bits,
    java_hash_code,
    string_hash_code,
)
from synthea.javacompat.numbers import to_int32

if TYPE_CHECKING:
    from synthea.world.agents.behaviors.payeradjustment.i_payer_adjustment import IPayerAdjustment
    from synthea.world.agents.person import Person
    from synthea.world.concepts.claim import ClaimEntry
    from synthea.world.concepts.health_record import Entry
    from synthea.world.concepts.healthinsurance.insurance_plan import InsurancePlan

    class AtomicInteger(Protocol):
        """Java boundary type: AtomicInteger; external to the mapped Python port."""


class Payer:
    """Java: Payer."""

    def __init__(
        self, name: str, id: int, states_covered: builtins.set[str], ownership: str
    ) -> None:
        """Java: Payer#Payer.

        Java overloads:
        (String name, int id, Set statesCovered, String ownership)
        """
        if name is None or not name:
            raise RuntimeError(f"ERROR: Payer must have a non-null name. Payer ID: {id}.")
        from synthea.world.concepts.claim import Claim

        self.payer_adjustment: IPayerAdjustment
        self.attributes: dict[str, object] = {}
        self.name: str = name
        self.uuid: str = str(
            UUID(
                bytes=hashlib.md5((str(id) + name).encode("utf-8"), usedforsecurity=False).digest(),
                version=3,
            )
        )
        self.plans: list[InsurancePlan] = []
        self.ownership: str = ownership
        self.plan_link_id: int = id
        self.states_covered: builtins.set[str] = states_covered
        self.revenue: Decimal = Claim.ZERO_CENTS
        self.costs_covered: Decimal = Claim.ZERO_CENTS
        self.costs_uncovered: Decimal = Claim.ZERO_CENTS
        self.total_qols: float = 0.0
        self.customer_utilization: JavaHashMap[str, int] = JavaHashMap()
        self.entry_utilization: JavaHashMap[int, JavaHashMap[str, int]] = JavaHashMap()

    def write_object(self, oos: IO[bytes]) -> None:
        """Java: Payer#writeObject.

        Java overloads:
        (ObjectOutputStream oos)
        """
        raise NotImplementedError("Java serialization is out of scope")

    def read_object(self, ois: IO[bytes]) -> None:
        """Java: Payer#readObject.

        Java overloads:
        (ObjectInputStream ois)
        """
        raise NotImplementedError("Java serialization is out of scope")

    def add_plan(self, new_plan: InsurancePlan) -> None:
        """Java: Payer#addPlan.

        Java overloads:
        (InsurancePlan newPlan)
        """
        self.plans.append(new_plan)

    def is_government_payer(self) -> bool:
        """Java: Payer#isGovernmentPayer.

        Java overloads:
        ()
        """
        from synthea.world.agents.payer_manager import PayerManager

        return self.ownership == PayerManager.GOV_OWNERSHIP

    def get_resource_id(self) -> str:
        """Java: Payer#getResourceID.

        Java overloads:
        ()
        """
        return self.uuid

    def get_name(self) -> str:
        """Java: Payer#getName.

        Java overloads:
        ()
        """
        return self.name

    def get_ownership(self) -> str:
        """Java: Payer#getOwnership.

        Java overloads:
        ()
        """
        return self.ownership

    def get_attributes(self) -> dict[str, object]:
        """Java: Payer#getAttributes.

        Java overloads:
        ()
        """
        return self.attributes

    def get_plans(self) -> list[InsurancePlan]:
        """Java: Payer#getPlans.

        Java overloads:
        ()
        """
        return self.plans

    def covers_care(self, entry: Entry) -> bool:
        """Java: Payer#coversCare.

        Java overloads:
        (Entry entry)
        """
        return self.plans[0].covers_service(entry)

    def adjust_claim(self, claim_entry: ClaimEntry, person: Person) -> Decimal:
        """Java: Payer#adjustClaim.

        Java overloads:
        (ClaimEntry claimEntry, Person person)
        """
        return self.payer_adjustment.adjust_claim(claim_entry, person)

    def increment_customers(self, person_id: str) -> None:
        """Java: Payer#incrementCustomers.

        Java overloads:
        (String personId)
        """
        self.customer_utilization[person_id] = to_int32(
            self.customer_utilization.get(person_id, 0) + 1
        )

    def increment_covered_entries(self, entry: Entry) -> None:
        """Java: Payer#incrementCoveredEntries.

        Java overloads:
        (Entry entry)
        """
        entry_type = self.get_entry_type(entry)
        year = Utilities.get_year(entry.start)
        self.increment_entries(year, "covered-" + entry_type)
        self.increment_entries(
            year, "covered-" + entry_type + "-" + ("null" if entry.type is None else entry.type)
        )

    def increment_uncovered_entries(self, entry: Entry) -> None:
        """Java: Payer#incrementUncoveredEntries.

        Java overloads:
        (Entry entry)
        """
        entry_type = self.get_entry_type(entry)
        year = Utilities.get_year(entry.start)
        self.increment_entries(year, "uncovered-" + entry_type)
        self.increment_entries(
            year, "uncovered-" + entry_type + "-" + ("null" if entry.type is None else entry.type)
        )

    def get_entry_type(self, entry: Entry) -> str:
        """Java: Payer#getEntryType.

        Java overloads:
        (Entry entry)
        """
        from synthea.world.concepts.health_record import (
            Encounter,
            HealthRecord,
            Immunization,
            Medication,
            Procedure,
        )

        if isinstance(entry, Encounter):
            return HealthRecord.ENCOUNTERS
        if isinstance(entry, Medication):
            return HealthRecord.MEDICATIONS
        if isinstance(entry, Procedure):
            return HealthRecord.PROCEDURES
        if isinstance(entry, Immunization):
            return HealthRecord.IMMUNIZATIONS
        return "no_cost"

    def increment_entries(self, year: int, key: str) -> None:
        """Java: Payer#incrementEntries.

        Java overloads:
        (Integer year, String key)
        """
        if year not in self.entry_utilization:
            self.entry_utilization[year] = JavaHashMap()
        counts = self.entry_utilization[year]
        counts[key] = to_int32(counts.get(key, 0) + 1)

    def add_covered_cost(self, cost_to_payer: Decimal) -> None:
        """Java: Payer#addCoveredCost.

        Java overloads:
        (BigDecimal costToPayer)
        """
        self.costs_covered = bd.add(self.costs_covered, cost_to_payer)

    def add_uncovered_cost(self, cost_to_patient: Decimal) -> None:
        """Java: Payer#addUncoveredCost.

        Java overloads:
        (BigDecimal costToPatient)
        """
        self.costs_uncovered = bd.add(self.costs_uncovered, cost_to_patient)

    def add_qols(self, qols: float) -> None:
        """Java: Payer#addQols.

        Java overloads:
        (double qols)
        """
        self.total_qols += qols

    def get_revenue(self) -> Decimal:
        """Java: Payer#getRevenue.

        Java overloads:
        ()
        """
        return self.revenue

    def get_customer_utilization(self, person_id: str) -> int:
        """Java: Payer#getCustomerUtilization.

        Java overloads:
        (String personId)
        """
        return self.customer_utilization.get(person_id, 0)

    def get_unique_customers(self) -> int:
        """Java: Payer#getUniqueCustomers.

        Java overloads:
        ()
        """
        return len(self.customer_utilization)

    def get_num_years_covered(self) -> int:
        """Java: Payer#getNumYearsCovered.

        Java overloads:
        ()
        """
        return to_int32(sum(self.customer_utilization.values()))

    def get_encounters_covered_count(self) -> int:
        """Java: Payer#getEncountersCoveredCount.

        Java overloads:
        ()
        """
        return to_int32(
            sum(counts.get("covered-encounters", 0) for counts in self.entry_utilization.values())
        )

    def get_encounters_uncovered_count(self) -> int:
        """Java: Payer#getEncountersUncoveredCount.

        Java overloads:
        ()
        """
        return to_int32(
            sum(counts.get("uncovered-encounters", 0) for counts in self.entry_utilization.values())
        )

    def get_medications_covered_count(self) -> int:
        """Java: Payer#getMedicationsCoveredCount.

        Java overloads:
        ()
        """
        return to_int32(
            sum(counts.get("covered-medications", 0) for counts in self.entry_utilization.values())
        )

    def get_medications_uncovered_count(self) -> int:
        """Java: Payer#getMedicationsUncoveredCount.

        Java overloads:
        ()
        """
        return to_int32(
            sum(
                counts.get("uncovered-medications", 0) for counts in self.entry_utilization.values()
            )
        )

    def get_procedures_covered_count(self) -> int:
        """Java: Payer#getProceduresCoveredCount.

        Java overloads:
        ()
        """
        return to_int32(
            sum(counts.get("covered-procedures", 0) for counts in self.entry_utilization.values())
        )

    def get_procedures_uncovered_count(self) -> int:
        """Java: Payer#getProceduresUncoveredCount.

        Java overloads:
        ()
        """
        return to_int32(
            sum(counts.get("uncovered-procedures", 0) for counts in self.entry_utilization.values())
        )

    def get_immunizations_covered_count(self) -> int:
        """Java: Payer#getImmunizationsCoveredCount.

        Java overloads:
        ()
        """
        return to_int32(
            sum(
                counts.get("covered-immunizations", 0) for counts in self.entry_utilization.values()
            )
        )

    def get_immunizations_uncovered_count(self) -> int:
        """Java: Payer#getImmunizationsUncoveredCount.

        Java overloads:
        ()
        """
        return to_int32(
            sum(
                counts.get("uncovered-immunizations", 0)
                for counts in self.entry_utilization.values()
            )
        )

    def get_amount_covered(self) -> Decimal:
        """Java: Payer#getAmountCovered.

        Java overloads:
        ()
        """
        return self.costs_covered

    def get_amount_uncovered(self) -> Decimal:
        """Java: Payer#getAmountUncovered.

        Java overloads:
        ()
        """
        return self.costs_uncovered

    def get_qols_average(self) -> float:
        """Java: Payer#getQolsAverage.

        Java overloads:
        ()
        """
        years = self.get_num_years_covered()
        if years == 0:
            return (
                math.nan
                if self.total_qols == 0.0 or math.isnan(self.total_qols)
                else math.copysign(math.inf, self.total_qols)
            )
        return self.total_qols / years

    def hash_code(self) -> int:
        """Java: Payer#hashCode.

        Java overloads:
        ()
        """
        hash_value = 7
        attributes_hash = to_int32(
            sum(
                to_int32(java_hash_code(key) ^ java_hash_code(value))
                for key, value in self.attributes.items()
            )
        )
        values = [
            attributes_hash,
            string_hash_code(self.name),
            string_hash_code(self.uuid),
            string_hash_code(self.ownership),
            to_int32(sum(string_hash_code(state) for state in self.states_covered)),
            _decimal_hash(self.revenue),
            _decimal_hash(self.costs_covered),
            _decimal_hash(self.costs_uncovered),
            double_hash_code(self.total_qols),
        ]
        for value in values:
            hash_value = to_int32(53 * hash_value + value)
        return hash_value

    def equals(self, obj: object) -> bool:
        """Java: Payer#equals.

        Java overloads:
        (Object obj)
        """
        if self is obj:
            return True
        if type(obj) is not type(self):
            return False
        assert isinstance(obj, Payer)
        return (
            bd.equals(self.revenue, obj.revenue)
            and bd.equals(self.costs_covered, obj.costs_covered)
            and bd.equals(self.costs_uncovered, obj.costs_uncovered)
            and double_to_long_bits(self.total_qols) == double_to_long_bits(obj.total_qols)
            and self.plans == obj.plans
            and self.name == obj.name
            and self.uuid == obj.uuid
            and self.ownership == obj.ownership
            and self.attributes == obj.attributes
            and self.states_covered == obj.states_covered
        )

    def set_payer_adjustment(self, payer_adjustment: IPayerAdjustment) -> None:
        """Java: Payer#setPayerAdjustment.

        Java overloads:
        (IPayerAdjustment payerAdjustment)
        """
        self.payer_adjustment = payer_adjustment

    def add_revenue(self, additional_revenue: Decimal) -> None:
        """Java: Payer#addRevenue.

        Java overloads:
        (BigDecimal additionalRevenue)
        """
        self.revenue = bd.add(self.revenue, additional_revenue)

    def get_government_payer_plan(self) -> InsurancePlan:
        """Java: Payer#getGovernmentPayerPlan.

        Java overloads:
        ()
        """
        if not self.is_government_payer():
            raise RuntimeError("Only government payers can call getGovernmentPayerPlan().")
        return self.plans[0]

    def add_attribute(self, key: str, value: str) -> None:
        """Java: Payer#addAttribute.

        Java overloads:
        (String key, String value)
        """
        self.attributes[key] = value

    def is_no_insurance(self) -> bool:
        """Java: Payer#isNoInsurance.

        Java overloads:
        ()
        """
        from synthea.world.agents.payer_manager import PayerManager

        return self.name == PayerManager.NO_INSURANCE

    def get_plan_link_id(self) -> int:
        """Java: Payer#getPlanLinkId.

        Java overloads:
        ()
        """
        return self.plan_link_id


class UtilizationBean:
    """Java: UtilizationBean."""

    def __init__(self, year: int, type: str, count: int) -> None:
        """Java: UtilizationBean#UtilizationBean.

        Java overloads:
        (Integer year, String type, AtomicInteger count)
        """
        self.year: int = year
        self.type: str = type
        self.count: int = count


setattr(Payer, "UtilizationBean", UtilizationBean)  # noqa: B010


def _decimal_hash(value: Decimal) -> int:
    """Java: BigDecimal#hashCode, including arbitrary BigInteger magnitude."""
    sign, digits, _ = value.as_tuple()
    magnitude = int("".join(str(digit) for digit in digits))
    words = []
    while magnitude:
        words.append(magnitude & 0xFFFFFFFF)
        magnitude >>= 32
    hashed = 0
    for word in reversed(words):
        hashed = to_int32(31 * hashed + word)
    if sign:
        hashed = to_int32(-hashed)
    return to_int32(31 * hashed + bd.scale_of(value))
