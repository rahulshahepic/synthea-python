"""Java: org.mitre.synthea.world.concepts.Claim."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar
from uuid import UUID

from synthea.javacompat.bigdecimal import ONE as BIGDECIMAL_ONE
from synthea.javacompat.bigdecimal import RoundingMode
from synthea.javacompat.bigdecimal import add as _add
from synthea.javacompat.bigdecimal import multiply as _multiply
from synthea.javacompat.bigdecimal import set_scale as _set_scale
from synthea.javacompat.bigdecimal import subtract as _subtract

if TYPE_CHECKING:
    from synthea.world.agents.payer import Payer
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import Entry
    from synthea.world.concepts.healthinsurance.plan_record import PlanRecord


class Claim:
    """Java: Claim."""

    serialVersionUID: ClassVar[int] = -3565704321813987656
    ZERO_CENTS: ClassVar[Decimal] = Decimal("0.00")

    def __init__(self, entry: Entry, person: Person) -> None:
        """Java: Claim#Claim.

        Java overloads:
        (Entry entry, Person person)
        """
        from synthea.world.concepts.health_record import Encounter, Medication

        # Set the Entry.
        if isinstance(entry, (Encounter, Medication)):
            self.main_entry: ClaimEntry = self._new_claim_entry(entry)
        else:
            raise RuntimeError("A Claim can only be made with entry types Encounter or Medication.")
        # Set the Person.
        self.person: Person = person
        # Set the plan record.
        if person.alive(entry.start):
            self.plan_record: PlanRecord = self.person.coverage.get_plan_record_at_time(entry.start)
        else:
            # Rarely, an encounter (such as death certification), after a person is dead can
            # result in a missing plan record. Account for this by using the last plan record.
            self.plan_record = self.person.coverage.get_last_plan_record()
        self.items: list[ClaimEntry] = []
        self.totals: ClaimEntry = self._new_claim_entry(entry)
        self.uuid: UUID = self.person.rand_uuid()

    def _new_claim_entry(self, entry: Entry) -> ClaimEntry:
        """Create a ClaimEntry bound to this Claim (Java: ClaimEntry is an inner class)."""
        claim_entry = ClaimEntry(entry)
        claim_entry.claim = self
        return claim_entry

    def add_line_item(self, entry: Entry) -> None:
        """Java: Claim#addLineItem.

        Java overloads:
        (Entry entry)
        """
        claim_entry = self._new_claim_entry(entry)
        self.items.append(claim_entry)

    def assign_costs(self) -> None:
        """Java: Claim#assignCosts.

        Java overloads:
        ()
        """
        self.main_entry.assign_costs(self.plan_record)
        self.totals = self._new_claim_entry(self.main_entry.entry)
        self.totals.add_costs(self.main_entry)
        for item in self.items:
            item.assign_costs(self.plan_record)
            self.totals.add_costs(item)

        self.plan_record.increment_out_of_pocket_expenses(self.get_total_patient_cost())
        self.plan_record.increment_primary_coverage(self.get_total_covered_cost())
        self.plan_record.increment_secondary_coverage(self.get_total_paid_by_secondary_payer())

    def get_total_claim_cost(self) -> Decimal:
        """Java: Claim#getTotalClaimCost.

        Java overloads:
        ()
        """
        return self.totals.get_total_claim_cost()

    def get_total_covered_cost(self) -> Decimal:
        """Java: Claim#getTotalCoveredCost.

        Java overloads:
        ()
        """
        return self.totals.get_covered_cost()

    def get_total_deductible_paid(self) -> Decimal:
        """Java: Claim#getTotalDeductiblePaid.

        Java overloads:
        ()
        """
        return self.totals.get_deductible_paid()

    def get_total_copay_paid(self) -> Decimal:
        """Java: Claim#getTotalCopayPaid.

        Java overloads:
        ()
        """
        return self.totals.get_copay_paid()

    def get_total_paid_by_secondary_payer(self) -> Decimal:
        """Java: Claim#getTotalPaidBySecondaryPayer.

        Java overloads:
        ()
        """
        return self.totals.paid_by_secondary_payer

    def get_total_adjustment(self) -> Decimal:
        """Java: Claim#getTotalAdjustment.

        Java overloads:
        ()
        """
        return self.totals.adjustment

    def get_total_coinsurance_paid(self) -> Decimal:
        """Java: Claim#getTotalCoinsurancePaid.

        Java overloads:
        ()
        """
        return self.totals.get_coinsurance_paid()

    def get_total_patient_cost(self) -> Decimal:
        """Java: Claim#getTotalPatientCost.

        Java overloads:
        ()
        """
        return self.totals.get_patient_cost()

    def covered_by_medicare(self) -> bool:
        """Java: Claim#coveredByMedicare.

        Java overloads:
        ()
        """
        from synthea.world.agents.payer_manager import PayerManager

        payer_name = self.get_payer().get_name()
        return payer_name == PayerManager.MEDICARE or payer_name == PayerManager.DUAL_ELIGIBLE

    def get_plan_record_member_id(self) -> str:
        """Java: Claim#getPlanRecordMemberId.

        Java overloads:
        ()
        """
        return self.plan_record.id

    def get_payer(self) -> Payer:
        """Java: Claim#getPayer.

        Java overloads:
        ()
        """
        return self.plan_record.get_plan().get_payer()

    def get_secondary_payer(self) -> Payer:
        """Java: Claim#getSecondaryPayer.

        Java overloads:
        ()
        """
        return self.plan_record.get_secondary_plan().get_payer()


class ClaimCost:
    """Java: ClaimCost."""

    serialVersionUID: ClassVar[int] = 1

    def __init__(self, other: ClaimCost | None = None) -> None:
        """Java: ClaimCost#ClaimCost.

        Java overloads:
        ()
        (ClaimCost other)
        """
        if other is None:
            self.cost: Decimal = Claim.ZERO_CENTS
            self.copay_paid_by_patient: Decimal = Claim.ZERO_CENTS
            self.deductible_paid_by_patient: Decimal = Claim.ZERO_CENTS
            self.adjustment: Decimal = Claim.ZERO_CENTS
            self.coinsurance_paid_by_payer: Decimal = Claim.ZERO_CENTS
            self.paid_by_payer: Decimal = Claim.ZERO_CENTS
            self.paid_by_secondary_payer: Decimal = Claim.ZERO_CENTS
            self.patient_out_of_pocket: Decimal = Claim.ZERO_CENTS
        else:
            self.cost = other.cost
            self.copay_paid_by_patient = other.copay_paid_by_patient
            self.deductible_paid_by_patient = other.deductible_paid_by_patient
            self.adjustment = other.adjustment
            self.coinsurance_paid_by_payer = other.coinsurance_paid_by_payer
            self.paid_by_payer = other.paid_by_payer
            self.paid_by_secondary_payer = other.paid_by_secondary_payer
            self.patient_out_of_pocket = other.patient_out_of_pocket

    def reset(self) -> None:
        """Java: ClaimCost#reset.

        Java overloads:
        ()
        """
        self.cost = Claim.ZERO_CENTS
        self.copay_paid_by_patient = Claim.ZERO_CENTS
        self.deductible_paid_by_patient = Claim.ZERO_CENTS
        self.adjustment = Claim.ZERO_CENTS
        self.coinsurance_paid_by_payer = Claim.ZERO_CENTS
        self.paid_by_payer = Claim.ZERO_CENTS
        self.paid_by_secondary_payer = Claim.ZERO_CENTS
        self.patient_out_of_pocket = Claim.ZERO_CENTS

    def add_costs(self, other: ClaimCost) -> None:
        """Java: ClaimCost#addCosts.

        Java overloads:
        (ClaimCost other)
        """
        self.cost = _add(self.cost, other.cost)
        self.copay_paid_by_patient = _add(self.copay_paid_by_patient, other.copay_paid_by_patient)
        self.deductible_paid_by_patient = _add(
            self.deductible_paid_by_patient, other.deductible_paid_by_patient
        )
        self.adjustment = _add(self.adjustment, other.adjustment)
        self.coinsurance_paid_by_payer = _add(
            self.coinsurance_paid_by_payer, other.coinsurance_paid_by_payer
        )
        self.paid_by_payer = _add(self.paid_by_payer, other.paid_by_payer)
        self.paid_by_secondary_payer = _add(
            self.paid_by_secondary_payer, other.paid_by_secondary_payer
        )
        self.patient_out_of_pocket = _add(self.patient_out_of_pocket, other.patient_out_of_pocket)

    def get_coinsurance_paid(self) -> Decimal:
        """Java: ClaimCost#getCoinsurancePaid.

        Java overloads:
        ()
        """
        if self.paid_by_secondary_payer > Claim.ZERO_CENTS:
            return self.paid_by_secondary_payer
        elif self.coinsurance_paid_by_payer > Claim.ZERO_CENTS:
            return self.patient_out_of_pocket
        return Claim.ZERO_CENTS

    def get_total_claim_cost(self) -> Decimal:
        """Java: ClaimCost#getTotalClaimCost.

        Java overloads:
        ()
        """
        return self.cost

    def get_covered_cost(self) -> Decimal:
        """Java: ClaimCost#getCoveredCost.

        Java overloads:
        ()
        """
        return _add(self.coinsurance_paid_by_payer, self.paid_by_payer)

    def get_deductible_paid(self) -> Decimal:
        """Java: ClaimCost#getDeductiblePaid.

        Java overloads:
        ()
        """
        return self.deductible_paid_by_patient

    def get_copay_paid(self) -> Decimal:
        """Java: ClaimCost#getCopayPaid.

        Java overloads:
        ()
        """
        return self.copay_paid_by_patient

    def get_patient_cost(self) -> Decimal:
        """Java: ClaimCost#getPatientCost.

        Java overloads:
        ()
        """
        return _add(
            _add(self.patient_out_of_pocket, self.copay_paid_by_patient),
            self.deductible_paid_by_patient,
        )


class ClaimEntry(ClaimCost):
    """Java: ClaimEntry."""

    serialVersionUID: ClassVar[int] = 1871121895630816723

    def __init__(self, entry: Entry) -> None:
        """Java: ClaimEntry#ClaimEntry.

        Java overloads:
        (Entry entry)
        """
        super().__init__()
        self.entry: Entry = entry
        # The enclosing Claim instance (Java inner-class reference). Set by
        # Claim when it creates the entry; a standalone ClaimEntry has none,
        # and assign_costs needs the Claim's person, exactly as in Java.
        self.claim: Claim | None = None

    def assign_costs(self, plan_record: PlanRecord) -> None:
        """Java: ClaimEntry#assignCosts.

        Java overloads:
        (PlanRecord planRecord)
        """
        from synthea.world.concepts.health_record import Encounter, Medication

        assert self.claim is not None
        person = self.claim.person
        self.reset()
        self.cost = self.entry.get_cost()
        remaining_balance = self.cost

        plan = plan_record.get_plan()

        if not plan.covers_service(self.entry):
            plan.increment_uncovered_entries(self.entry)
            # Payer does not cover care
            self.patient_out_of_pocket = remaining_balance
            return

        plan.increment_covered_entries(self.entry)

        if plan_record.get_out_of_pocket_expenses() > plan.get_max_oop():
            # TODO - This will only trigger after a person has already paid more than their
            # Max OOP. An accurate implementation would require a Max OOP check for every
            # time a patient is assigned costs in this method.
            # The person has already paid their maximum out-of-pocket costs.
            self.paid_by_payer = remaining_balance
            remaining_balance = Claim.ZERO_CENTS

        # Apply copay to Encounters and Medication claims only
        if isinstance(self.entry, (Encounter, Medication)):
            self.copay_paid_by_patient = plan.determine_copay(self.entry.type, self.entry.start)
            if self.copay_paid_by_patient > remaining_balance:
                self.copay_paid_by_patient = remaining_balance
            remaining_balance = _subtract(remaining_balance, self.copay_paid_by_patient)
        # Check if the patient has remaining deductible
        if (
            remaining_balance > Claim.ZERO_CENTS
            and plan_record.remaining_deductible > Claim.ZERO_CENTS
        ):
            if plan_record.remaining_deductible >= remaining_balance:
                self.deductible_paid_by_patient = remaining_balance
            else:
                self.deductible_paid_by_patient = plan_record.remaining_deductible
            remaining_balance = _subtract(remaining_balance, self.deductible_paid_by_patient)
            plan_record.remaining_deductible = _subtract(
                plan_record.remaining_deductible, self.deductible_paid_by_patient
            )
        if remaining_balance > Claim.ZERO_CENTS:
            # Check if the payer has an adjustment
            adjustment = plan.adjust_claim(self, person)
            remaining_balance = _subtract(remaining_balance, adjustment)
        if remaining_balance > Claim.ZERO_CENTS:
            # Check if the patient has coinsurance
            patient_coinsurance = plan.get_patient_coinsurance()
            if patient_coinsurance > Claim.ZERO_CENTS:
                payer_coinsurance = _subtract(BIGDECIMAL_ONE, patient_coinsurance)
                # Payer covers some
                self.coinsurance_paid_by_payer = _set_scale(
                    _multiply(payer_coinsurance, remaining_balance), 2, RoundingMode.HALF_EVEN
                )
                remaining_balance = _subtract(remaining_balance, self.coinsurance_paid_by_payer)
            else:
                # Payer covers all
                self.paid_by_payer = remaining_balance
                remaining_balance = Claim.ZERO_CENTS
        if remaining_balance > Claim.ZERO_CENTS:  # noqa: SIM102 — Java cascade kept
            # If secondary insurance, payer covers remainder, not patient.
            if not plan_record.get_secondary_plan().is_no_insurance():
                self.paid_by_secondary_payer = remaining_balance
                remaining_balance = _subtract(remaining_balance, self.paid_by_secondary_payer)
        if remaining_balance > Claim.ZERO_CENTS:
            # Patient amount
            self.patient_out_of_pocket = remaining_balance
            remaining_balance = _subtract(remaining_balance, self.patient_out_of_pocket)


setattr(Claim, "ClaimCost", ClaimCost)  # noqa: B010
setattr(Claim, "ClaimEntry", ClaimEntry)  # noqa: B010
