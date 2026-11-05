"""Java API skeleton: Claim.java."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar
from uuid import UUID

if TYPE_CHECKING:
    from synthea.world.agents.payer import Payer
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import Entry
    from synthea.world.concepts.healthinsurance.plan_record import PlanRecord


class Claim:
    """Java: Claim; pending T14."""

    serialVersionUID: ClassVar[int] = -3565704321813987656
    ZERO_CENTS: ClassVar[Decimal] = Decimal("0.00")

    def __init__(self, entry: Entry, person: Person) -> None:
        """Java: Claim#Claim.

        Java overloads:
        (Entry entry, Person person)
        """
        self.person: Person
        self.main_entry: ClaimEntry
        self.items: list[ClaimEntry]
        self.totals: ClaimEntry
        self.uuid: UUID
        self.plan_record: PlanRecord
        raise NotImplementedError("Java: Claim#Claim — pending T14")

    def add_line_item(self, entry: Entry) -> None:
        """Java: Claim#addLineItem.

        Java overloads:
        (Entry entry)
        """
        raise NotImplementedError("Java: Claim#addLineItem — pending T14")

    def assign_costs(self) -> None:
        """Java: Claim#assignCosts.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Claim#assignCosts — pending T14")

    def get_total_claim_cost(self) -> Decimal:
        """Java: Claim#getTotalClaimCost.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Claim#getTotalClaimCost — pending T14")

    def get_total_covered_cost(self) -> Decimal:
        """Java: Claim#getTotalCoveredCost.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Claim#getTotalCoveredCost — pending T14")

    def get_total_deductible_paid(self) -> Decimal:
        """Java: Claim#getTotalDeductiblePaid.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Claim#getTotalDeductiblePaid — pending T14")

    def get_total_copay_paid(self) -> Decimal:
        """Java: Claim#getTotalCopayPaid.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Claim#getTotalCopayPaid — pending T14")

    def get_total_paid_by_secondary_payer(self) -> Decimal:
        """Java: Claim#getTotalPaidBySecondaryPayer.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Claim#getTotalPaidBySecondaryPayer — pending T14")

    def get_total_adjustment(self) -> Decimal:
        """Java: Claim#getTotalAdjustment.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Claim#getTotalAdjustment — pending T14")

    def get_total_coinsurance_paid(self) -> Decimal:
        """Java: Claim#getTotalCoinsurancePaid.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Claim#getTotalCoinsurancePaid — pending T14")

    def get_total_patient_cost(self) -> Decimal:
        """Java: Claim#getTotalPatientCost.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Claim#getTotalPatientCost — pending T14")

    def covered_by_medicare(self) -> bool:
        """Java: Claim#coveredByMedicare.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Claim#coveredByMedicare — pending T14")

    def get_plan_record_member_id(self) -> str:
        """Java: Claim#getPlanRecordMemberId.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Claim#getPlanRecordMemberId — pending T14")

    def get_payer(self) -> Payer:
        """Java: Claim#getPayer.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Claim#getPayer — pending T14")

    def get_secondary_payer(self) -> Payer:
        """Java: Claim#getSecondaryPayer.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Claim#getSecondaryPayer — pending T14")


class ClaimCost:
    """Java: ClaimCost; pending T14."""

    serialVersionUID: ClassVar[int] = 1

    def __init__(self, other: ClaimCost | None = None) -> None:
        """Java: ClaimCost#ClaimCost.

        Java overloads:
        ()
        (ClaimCost other)
        """
        self.cost: Decimal
        self.copay_paid_by_patient: Decimal
        self.deductible_paid_by_patient: Decimal
        self.adjustment: Decimal
        self.coinsurance_paid_by_payer: Decimal
        self.paid_by_payer: Decimal
        self.paid_by_secondary_payer: Decimal
        self.patient_out_of_pocket: Decimal
        raise NotImplementedError("Java: ClaimCost#ClaimCost — pending T14")

    def reset(self) -> None:
        """Java: ClaimCost#reset.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ClaimCost#reset — pending T14")

    def add_costs(self, other: ClaimCost) -> None:
        """Java: ClaimCost#addCosts.

        Java overloads:
        (ClaimCost other)
        """
        raise NotImplementedError("Java: ClaimCost#addCosts — pending T14")

    def get_coinsurance_paid(self) -> Decimal:
        """Java: ClaimCost#getCoinsurancePaid.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ClaimCost#getCoinsurancePaid — pending T14")

    def get_total_claim_cost(self) -> Decimal:
        """Java: ClaimCost#getTotalClaimCost.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ClaimCost#getTotalClaimCost — pending T14")

    def get_covered_cost(self) -> Decimal:
        """Java: ClaimCost#getCoveredCost.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ClaimCost#getCoveredCost — pending T14")

    def get_deductible_paid(self) -> Decimal:
        """Java: ClaimCost#getDeductiblePaid.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ClaimCost#getDeductiblePaid — pending T14")

    def get_copay_paid(self) -> Decimal:
        """Java: ClaimCost#getCopayPaid.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ClaimCost#getCopayPaid — pending T14")

    def get_patient_cost(self) -> Decimal:
        """Java: ClaimCost#getPatientCost.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ClaimCost#getPatientCost — pending T14")


class ClaimEntry(ClaimCost):
    """Java: ClaimEntry; pending T14."""

    serialVersionUID: ClassVar[int] = 1871121895630816723

    def __init__(self, entry: Entry) -> None:
        """Java: ClaimEntry#ClaimEntry.

        Java overloads:
        (Entry entry)
        """
        self.entry: Entry
        raise NotImplementedError("Java: ClaimEntry#ClaimEntry — pending T14")

    def assign_costs(self, plan_record: PlanRecord) -> None:
        """Java: ClaimEntry#assignCosts.

        Java overloads:
        (PlanRecord planRecord)
        """
        raise NotImplementedError("Java: ClaimEntry#assignCosts — pending T14")


setattr(Claim, "ClaimCost", ClaimCost)  # noqa: B010
setattr(Claim, "ClaimEntry", ClaimEntry)  # noqa: B010
