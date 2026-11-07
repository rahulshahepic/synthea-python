"""Unit tests for Claim / ClaimCost / ClaimEntry (T14).

Ports the cost arithmetic of the upstream CSVExporterClaimsTest's subject
matter at the unit level: that JUnit test itself is an end-to-end exporter
test (Generator + CSVExporter + payer loading, owned by T25/T15/T16) and is
not ported here; it is listed as skipped in the PR body with that reason.

ClaimEntry.assignCosts branch coverage uses test-local fake plan objects:
the branch structure and BigDecimal arithmetic under test are Claim's own,
while InsurancePlan/PlanRecord behaviour belongs to T15/T16.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import synthea.world.agents.person as person_module
from synthea.javacompat import bigdecimal
from synthea.world.agents.person import Person
from synthea.world.concepts.claim import Claim, ClaimCost, ClaimEntry
from synthea.world.concepts.health_record import Encounter, Medication, Procedure

TIME = 949276800000  # BIRTHDATE + 30 days, as in the parity probe


def _bd(value: Decimal) -> str:
    return bigdecimal.to_string(value)


class FakePayer:
    """Java: Payer, reduced to the name Claim reads."""

    def __init__(self, name: str) -> None:
        self._name = name

    def get_name(self) -> str:
        return self._name


class FakePlan:
    """Java: InsurancePlan, with scripted answers for ClaimEntry.assignCosts."""

    def __init__(
        self,
        *,
        covers: bool = True,
        max_oop: Decimal = Decimal("1000000.00"),
        copay: Decimal = Decimal("0.00"),
        adjustment: Decimal = Decimal("0.00"),
        patient_coinsurance: Decimal = Decimal("0.00"),
        no_insurance: bool = False,
        payer_name: str = "Fake Payer",
    ) -> None:
        self._covers = covers
        self._max_oop = max_oop
        self._copay = copay
        self._adjustment = adjustment
        self._patient_coinsurance = patient_coinsurance
        self._no_insurance = no_insurance
        self._payer = FakePayer(payer_name)
        self.covered_entries = 0
        self.uncovered_entries = 0

    def covers_service(self, entry: object) -> bool:
        return self._covers

    def increment_covered_entries(self, entry: object) -> None:
        self.covered_entries += 1

    def increment_uncovered_entries(self, entry: object) -> None:
        self.uncovered_entries += 1

    def get_max_oop(self) -> Decimal:
        return self._max_oop

    def determine_copay(self, entry_type: str, entry_start: int) -> Decimal:
        return self._copay

    def adjust_claim(self, claim_entry: ClaimEntry, person: Person) -> Decimal:
        return self._adjustment

    def get_patient_coinsurance(self) -> Decimal:
        return self._patient_coinsurance

    def is_no_insurance(self) -> bool:
        return self._no_insurance

    def get_payer(self) -> FakePayer:
        return self._payer


class FakePlanRecord:
    """Java: PlanRecord, reduced to what Claim and ClaimEntry read/write."""

    def __init__(self, plan: FakePlan, secondary: FakePlan) -> None:
        self.id = "member-1"
        self.plan = plan
        self.secondary_plan = secondary
        self.remaining_deductible = Decimal("0.00")
        self.out_of_pocket_expenses = Decimal("0.00")
        self.primary_coverage = Decimal("0.00")
        self.secondary_coverage = Decimal("0.00")

    def get_plan(self) -> FakePlan:
        return self.plan

    def get_secondary_plan(self) -> FakePlan:
        return self.secondary_plan

    def get_out_of_pocket_expenses(self) -> Decimal:
        return self.out_of_pocket_expenses

    def increment_out_of_pocket_expenses(self, expenses: Decimal) -> None:
        self.out_of_pocket_expenses = bigdecimal.add(self.out_of_pocket_expenses, expenses)

    def increment_primary_coverage(self, coverage: Decimal) -> None:
        self.primary_coverage = bigdecimal.add(self.primary_coverage, coverage)

    def increment_secondary_coverage(self, coverage: Decimal) -> None:
        self.secondary_coverage = bigdecimal.add(self.secondary_coverage, coverage)


class FakeCoverage:
    """CoverageRecord stand-in returning the test's plan record (T16 plumbing)."""

    def __init__(self, plan_record: FakePlanRecord) -> None:
        self.plan_record = plan_record

    def get_plan_record_at_time(self, time: int) -> FakePlanRecord:
        return self.plan_record

    def get_last_plan_record(self) -> FakePlanRecord:
        return self.plan_record


@pytest.fixture
def claim_setup(monkeypatch: pytest.MonkeyPatch) -> tuple[Person, FakePlanRecord]:
    plan_record = FakePlanRecord(FakePlan(), FakePlan(no_insurance=True))
    coverage = FakeCoverage(plan_record)
    monkeypatch.setattr(person_module, "CoverageRecord", lambda person: coverage)
    person = Person(1234)
    person.attributes[Person.BIRTHDATE] = TIME - 30 * 86400000
    return person, plan_record


def _encounter(person: Person, cost: str) -> Encounter:
    record = person.record
    assert record is not None
    encounter = record.new_entry(lambda: Encounter(TIME, "wellness"))
    encounter.cost = Decimal(cost)
    return encounter


def _entry(person: Person, claim: Claim, cost: str) -> ClaimEntry:
    claim_entry = ClaimEntry(_encounter(person, cost))
    claim_entry.claim = claim
    return claim_entry


def test_claim_cost_defaults_are_zero_cents() -> None:
    cost = ClaimCost()
    for field in (
        cost.cost,
        cost.copay_paid_by_patient,
        cost.deductible_paid_by_patient,
        cost.adjustment,
        cost.coinsurance_paid_by_payer,
        cost.paid_by_payer,
        cost.paid_by_secondary_payer,
        cost.patient_out_of_pocket,
    ):
        assert _bd(field) == "0.00"
    assert _bd(Claim.ZERO_CENTS) == "0.00"


def test_claim_cost_copy_and_add_and_reset() -> None:
    cost = ClaimCost()
    cost.cost = Decimal("10.10")
    cost.copay_paid_by_patient = Decimal("1.00")
    copy = ClaimCost(cost)
    assert _bd(copy.cost) == "10.10"
    assert _bd(copy.copay_paid_by_patient) == "1.00"

    other = ClaimCost()
    other.cost = Decimal("0.20")
    other.patient_out_of_pocket = Decimal("3.33")
    copy.add_costs(other)
    assert _bd(copy.cost) == "10.30"
    assert _bd(copy.patient_out_of_pocket) == "3.33"

    copy.reset()
    assert _bd(copy.cost) == "0.00"
    assert _bd(copy.patient_out_of_pocket) == "0.00"


def test_claim_cost_derived_amounts() -> None:
    cost = ClaimCost()
    cost.coinsurance_paid_by_payer = Decimal("40.00")
    cost.paid_by_payer = Decimal("10.00")
    cost.patient_out_of_pocket = Decimal("5.00")
    cost.copay_paid_by_patient = Decimal("2.00")
    cost.deductible_paid_by_patient = Decimal("1.00")
    assert _bd(cost.get_covered_cost()) == "50.00"
    assert _bd(cost.get_patient_cost()) == "8.00"
    assert _bd(cost.get_total_claim_cost()) == "0.00"
    # Secondary payer zero, coinsurance positive -> patient's out of pocket.
    assert _bd(cost.get_coinsurance_paid()) == "5.00"
    cost.paid_by_secondary_payer = Decimal("7.00")
    assert _bd(cost.get_coinsurance_paid()) == "7.00"
    cost.paid_by_secondary_payer = Decimal("0.00")
    cost.coinsurance_paid_by_payer = Decimal("0.00")
    assert _bd(cost.get_coinsurance_paid()) == "0.00"


def test_assign_costs_uncovered_goes_to_patient(
    claim_setup: tuple[Person, FakePlanRecord],
) -> None:
    person, plan_record = claim_setup
    plan_record.plan._covers = False
    claim = Claim(_encounter(person, "100.00"), person)
    entry = _entry(person, claim, "100.00")
    entry.assign_costs(plan_record)
    assert _bd(entry.patient_out_of_pocket) == "100.00"
    assert _bd(entry.paid_by_payer) == "0.00"
    assert plan_record.plan.uncovered_entries == 1
    assert plan_record.plan.covered_entries == 0


def test_assign_costs_after_max_oop_payer_pays_all(
    claim_setup: tuple[Person, FakePlanRecord],
) -> None:
    person, plan_record = claim_setup
    plan_record.out_of_pocket_expenses = Decimal("200.00")
    plan_record.plan._max_oop = Decimal("100.00")
    plan_record.plan._copay = Decimal("25.00")
    claim = Claim(_encounter(person, "100.00"), person)
    entry = _entry(person, claim, "100.00")
    entry.assign_costs(plan_record)
    assert _bd(entry.paid_by_payer) == "100.00"
    assert _bd(entry.copay_paid_by_patient) == "0.00"
    assert _bd(entry.patient_out_of_pocket) == "0.00"


def test_assign_costs_copay_capped_at_balance(
    claim_setup: tuple[Person, FakePlanRecord],
) -> None:
    person, plan_record = claim_setup
    plan_record.plan._copay = Decimal("250.00")
    claim = Claim(_encounter(person, "100.00"), person)
    entry = _entry(person, claim, "100.00")
    entry.assign_costs(plan_record)
    assert _bd(entry.copay_paid_by_patient) == "100.00"
    assert _bd(entry.paid_by_payer) == "0.00"
    assert _bd(entry.patient_out_of_pocket) == "0.00"


def test_assign_costs_deductible_partial_and_full(
    claim_setup: tuple[Person, FakePlanRecord],
) -> None:
    person, plan_record = claim_setup
    plan_record.remaining_deductible = Decimal("30.00")
    claim = Claim(_encounter(person, "100.00"), person)
    entry = _entry(person, claim, "100.00")
    entry.assign_costs(plan_record)
    assert _bd(entry.deductible_paid_by_patient) == "30.00"
    assert _bd(plan_record.remaining_deductible) == "0.00"
    # No coinsurance: the payer covers the rest.
    assert _bd(entry.paid_by_payer) == "70.00"

    plan_record.remaining_deductible = Decimal("500.00")
    entry2 = _entry(person, claim, "100.00")
    entry2.assign_costs(plan_record)
    assert _bd(entry2.deductible_paid_by_patient) == "100.00"
    assert _bd(plan_record.remaining_deductible) == "400.00"
    assert _bd(entry2.paid_by_payer) == "0.00"


def test_assign_costs_adjustment_reduces_balance_but_is_not_stored(
    claim_setup: tuple[Person, FakePlanRecord],
) -> None:
    # Java parity quirk: assignCosts subtracts plan.adjustClaim's return from
    # the balance but never assigns it to the entry's adjustment field.
    person, plan_record = claim_setup
    plan_record.plan._adjustment = Decimal("20.00")
    claim = Claim(_encounter(person, "100.00"), person)
    entry = _entry(person, claim, "100.00")
    entry.assign_costs(plan_record)
    assert _bd(entry.adjustment) == "0.00"
    assert _bd(entry.paid_by_payer) == "80.00"


def test_assign_costs_coinsurance_half_even(
    claim_setup: tuple[Person, FakePlanRecord],
) -> None:
    person, plan_record = claim_setup
    plan_record.plan._patient_coinsurance = Decimal("0.25")
    claim = Claim(_encounter(person, "10.30"), person)
    entry = _entry(person, claim, "10.30")
    entry.assign_costs(plan_record)
    # Payer share: 0.75 * 10.30 = 7.725 -> HALF_EVEN scale 2 -> 7.72.
    assert _bd(entry.coinsurance_paid_by_payer) == "7.72"
    assert _bd(entry.patient_out_of_pocket) == "2.58"

    entry2 = _entry(person, claim, "10.10")
    entry2.assign_costs(plan_record)
    # 0.75 * 10.10 = 7.575 -> HALF_EVEN -> 7.58.
    assert _bd(entry2.coinsurance_paid_by_payer) == "7.58"
    assert _bd(entry2.patient_out_of_pocket) == "2.52"


def test_assign_costs_secondary_payer_takes_remainder(
    claim_setup: tuple[Person, FakePlanRecord],
) -> None:
    person, plan_record = claim_setup
    plan_record.plan._patient_coinsurance = Decimal("0.25")
    plan_record.secondary_plan._no_insurance = False
    claim = Claim(_encounter(person, "100.00"), person)
    entry = _entry(person, claim, "100.00")
    entry.assign_costs(plan_record)
    assert _bd(entry.coinsurance_paid_by_payer) == "75.00"
    assert _bd(entry.paid_by_secondary_payer) == "25.00"
    assert _bd(entry.patient_out_of_pocket) == "0.00"


def test_claim_totals_and_plan_record_increments(
    claim_setup: tuple[Person, FakePlanRecord],
) -> None:
    person, plan_record = claim_setup
    plan_record.plan._copay = Decimal("10.00")
    claim = Claim(_encounter(person, "100.00"), person)
    record = person.record
    assert record is not None
    procedure = record.new_entry(lambda: Procedure(TIME, "procedure"))
    procedure.cost = Decimal("50.00")
    claim.add_line_item(procedure)
    claim.assign_costs()
    # Main: copay 10 (encounter), payer pays 90. Procedure: no copay
    # (not an Encounter/Medication), payer pays 50.
    assert _bd(claim.get_total_claim_cost()) == "150.00"
    assert _bd(claim.get_total_copay_paid()) == "10.00"
    assert _bd(claim.get_total_covered_cost()) == "140.00"
    assert _bd(claim.get_total_patient_cost()) == "10.00"
    assert _bd(plan_record.out_of_pocket_expenses) == "10.00"
    assert _bd(plan_record.primary_coverage) == "140.00"
    assert _bd(plan_record.secondary_coverage) == "0.00"
    assert claim.get_plan_record_member_id() == "member-1"
    assert claim.get_payer().get_name() == "Fake Payer"


def test_claim_rejects_non_encounter_medication_main_entry(
    claim_setup: tuple[Person, FakePlanRecord],
) -> None:
    person, _plan_record = claim_setup
    record = person.record
    assert record is not None
    procedure = record.new_entry(lambda: Procedure(TIME, "procedure"))
    with pytest.raises(
        RuntimeError,
        match=r"A Claim can only be made with entry types Encounter or Medication\.",
    ):
        Claim(procedure, person)


def test_claim_accepts_medication_main_entry(
    claim_setup: tuple[Person, FakePlanRecord],
) -> None:
    person, _plan_record = claim_setup
    record = person.record
    assert record is not None
    medication = record.new_entry(lambda: Medication(TIME, "medication"))
    claim = Claim(medication, person)
    assert claim.main_entry.entry is medication
    assert claim.items == []
