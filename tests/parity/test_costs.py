"""Parity for Costs and Claim (T14).

Mirrors CostsProbe case for case and compares the dump exactly.

The lookups cases are *component* parity (PORTING_GUIDE §10): Costs reads
only a Person's ``STATE`` attribute and RNG, but a real Python Person cannot
yet be constructed without T16's CoverageRecord, so
tests/parity/costs_doubles.py stands in for CoverageRecord/PlanRecord,
supplying only the plumbing Person's and Claim's constructors store. No
probe output depends on the doubles' behaviour. Doubles used:
CoverageRecordDouble, PlanRecordDouble.

The claims cases are *integration* parity: they call the real Claim,
CoverageRecord (T16), PlanRecord (T16) and InsurancePlan (T15) code end to
end, exercising the no-insurance path the issue scopes for T14. Until T15
and T16 land, each scenario is reported pending by the dependency gate;
afterwards every scenario must match exactly.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from decimal import Decimal
from pathlib import Path
from typing import cast

import pytest

import synthea.world.agents.person as person_module
from synthea.helpers.simple_csv import SimpleCSV
from synthea.javacompat import bigdecimal
from synthea.javacompat.numbers import double_to_string
from synthea.world.agents.payer_manager import PayerManager
from synthea.world.agents.person import Person
from synthea.world.concepts.claim import Claim, ClaimEntry
from synthea.world.concepts.costs import Costs
from synthea.world.concepts.health_record import (
    Code,
    Device,
    Encounter,
    EncounterType,
    Entry,
    HealthRecord,
    Immunization,
    Medication,
    Observation,
    Procedure,
    Report,
    Supply,
)
from tests.dependency_gate import Pending, report_pending, run_or_pending
from tests.parity.costs_doubles import CoverageRecordDouble

BIRTHDATE = 946684800000  # 2000-01-01T00:00:00Z
TIME = BIRTHDATE + 30 * 86400000
STATES = ["Massachusetts", "California", "Texas", "Wyoming"]
SEEDS = [42, 12345]
STRIDE = 53

RESOURCES = Path(__file__).resolve().parents[2] / "java" / "src" / "main" / "resources"


def _cost_rows(resource: str) -> list[tuple[str, str]]:
    raw = (RESOURCES / resource).read_text(encoding="utf-8")
    return [(line["CODE"], line["COMMENTS"]) for line in SimpleCSV.parse(raw)]


PROCEDURES = _cost_rows("costs/procedures.csv")
MEDICATIONS = _cost_rows("costs/medications.csv")
ENCOUNTERS = _cost_rows("costs/encounters.csv")
DEVICES = _cost_rows("costs/devices.csv")
SUPPLIES = _cost_rows("costs/supplies.csv")


def _load_cases(golden: Callable[[str], Path]) -> dict[str, str]:
    path = golden("CostsProbe") / "costs.jsonl"
    cases: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        cases[row["case"]] = row["out"]
    return cases


def _new_person(seed: int, state: str | None) -> Person:
    person = Person(seed)
    person.attributes[Person.BIRTHDATE] = BIRTHDATE
    if state is not None:
        person.attributes[Person.STATE] = state
    return person


def _indices(size: int, full: bool) -> list[int]:
    if full:
        return list(range(size))
    idx = list(range(0, size, STRIDE))
    if idx[-1] != size - 1:
        idx.append(size - 1)
    return idx


def _lookup(tag: str, entry: Entry, person: Person) -> str:
    cost = Costs.determine_cost_of_entry(entry, person)
    return f"{tag} -> {double_to_string(cost)} count={person.get_count()}"


def _b(value: bool) -> str:
    """Java: Boolean.toString."""
    return "true" if value else "false"


def _lookups_case(state: str, seed: int, full: bool) -> str:
    person = _new_person(seed, state)
    record = cast(HealthRecord, person.record)
    lines = [f"state={state} seed={seed} full={_b(full)}"]

    for i in _indices(len(PROCEDURES), full):
        code, display = PROCEDURES[i]
        entry = record.new_entry(lambda: Procedure(TIME, "procedure"))
        entry.codes.append(Code("SNOMED-CT", code, display))
        lines.append(_lookup(f"P {code}", entry, person))
    for i in _indices(len(MEDICATIONS), full):
        code, display = MEDICATIONS[i]
        entry = record.new_entry(lambda: Medication(TIME, "medication"))
        entry.codes.append(Code("RxNorm", code, display))
        lines.append(_lookup(f"M {code}", entry, person))
    types = list(EncounterType)
    for i in _indices(len(ENCOUNTERS), full):
        code, display = ENCOUNTERS[i]
        entry = record.new_entry(lambda i=i: Encounter(TIME, types[i % len(types)].to_string()))
        entry.codes.append(Code("SNOMED-CT", code, display))
        lines.append(_lookup(f"E {code}", entry, person))
    for i in _indices(len(DEVICES), full):
        code, display = DEVICES[i]
        entry = record.new_entry(lambda: Device(TIME, "device"))
        entry.codes.append(Code("SNOMED-CT", code, display))
        lines.append(_lookup(f"D {code}", entry, person))
    for i in _indices(len(SUPPLIES), full):
        code, display = SUPPLIES[i]
        entry = record.new_entry(lambda: Supply(TIME, "supply"))
        entry.codes.append(Code("SNOMED-CT", code, display))
        lines.append(_lookup(f"S {code}", entry, person))

    unknown_proc = record.new_entry(lambda: Procedure(TIME, "procedure"))
    unknown_proc.codes.append(Code("SNOMED-CT", "999999999", "Unknown procedure"))
    lines.append(_lookup("X P unknown", unknown_proc, person))
    unknown_med = record.new_entry(lambda: Medication(TIME, "medication"))
    unknown_med.codes.append(Code("RxNorm", "999999999", "Unknown medication"))
    lines.append(_lookup("X M unknown", unknown_med, person))
    unknown_enc = record.new_entry(lambda: Encounter(TIME, "wellness"))
    unknown_enc.codes.append(Code("SNOMED-CT", "999999999", "Unknown encounter"))
    lines.append(_lookup("X E unknown", unknown_enc, person))
    unknown_imm = record.new_entry(lambda: Immunization(TIME, "immunization"))
    unknown_imm.codes.append(Code("CVX", "999999999", "Unknown immunization"))
    lines.append(_lookup("X I unknown", unknown_imm, person))
    unknown_dev = record.new_entry(lambda: Device(TIME, "device"))
    unknown_dev.codes.append(Code("SNOMED-CT", "999999999", "Unknown device"))
    lines.append(_lookup("X D unknown", unknown_dev, person))
    unknown_sup = record.new_entry(lambda: Supply(TIME, "supply"))
    unknown_sup.codes.append(Code("SNOMED-CT", "999999999", "Unknown supply"))
    lines.append(_lookup("X S unknown", unknown_sup, person))

    lines.append(
        _lookup("X P empty", record.new_entry(lambda: Procedure(TIME, "procedure")), person)
    )
    lines.append(
        _lookup("X M empty", record.new_entry(lambda: Medication(TIME, "medication")), person)
    )
    lines.append(
        _lookup("X E empty", record.new_entry(lambda: Encounter(TIME, "wellness")), person)
    )
    lines.append(
        _lookup("X I empty", record.new_entry(lambda: Immunization(TIME, "immunization")), person)
    )
    lines.append(_lookup("X D empty", record.new_entry(lambda: Device(TIME, "device")), person))
    lines.append(_lookup("X S empty", record.new_entry(lambda: Supply(TIME, "supply")), person))

    for i, display in enumerate(["Dialysis", "DIALYSIS TREATMENT", "hemodialysis session"]):
        entry = record.new_entry(lambda: Procedure(TIME, "procedure"))
        entry.codes.append(Code("SNOMED-CT", PROCEDURES[0][0], display))
        lines.append(_lookup(f"X P dialysis{i}", entry, person))

    first_med_code, first_med_display = MEDICATIONS[0]
    administered = record.new_entry(lambda: Medication(TIME, "medication"))
    administered.codes.append(Code("RxNorm", first_med_code, first_med_display))
    administered.administration = True
    lines.append(_lookup("X M admin", administered, person))
    detailed = record.new_entry(lambda: Medication(TIME, "medication"))
    detailed.codes.append(Code("RxNorm", first_med_code, first_med_display))
    detailed.prescription_details = {
        "dosage": {"amount": 2, "frequency": 3, "period": 1, "unit": "days"},
        "duration": {"quantity": 2, "unit": "months"},
    }
    lines.append(_lookup("X M details", detailed, person))

    report_with_code = record.new_entry(lambda: Report(TIME, "laboratory", []))
    report_with_code.codes.append(Code("LOINC", "123456", "Some lab panel"))
    lines.append(_lookup("X R code", report_with_code, person))
    lines.append(
        _lookup("X R empty", record.new_entry(lambda: Report(TIME, "laboratory", [])), person)
    )

    observation = record.new_entry(lambda: Observation(TIME, "vital-signs", 1.0))
    lines.append(_lookup("X O", observation, person))

    lines.append(
        "hasCost"
        f" P={_b(Costs.has_cost(unknown_proc))}"
        f" M={_b(Costs.has_cost(unknown_med))}"
        f" E={_b(Costs.has_cost(unknown_enc))}"
        f" I={_b(Costs.has_cost(unknown_imm))}"
        f" D={_b(Costs.has_cost(unknown_dev))}"
        f" S={_b(Costs.has_cost(unknown_sup))}"
        f" R={_b(Costs.has_cost(report_with_code))}"
        f" O={_b(Costs.has_cost(observation))}"
    )
    for code, _display in [PROCEDURES[0], MEDICATIONS[0], ENCOUNTERS[0], DEVICES[0], SUPPLIES[0]]:
        lines.append(f"hasSpecifiedCost {code}={_b(Costs.has_specified_cost(code))}")
    lines.append(f"hasSpecifiedCost 999999999={_b(Costs.has_specified_cost('999999999'))}")
    return "\n".join(lines)


def _nostate_case() -> str:
    person = _new_person(42, None)
    record = cast(HealthRecord, person.record)
    lines = ["state=null seed=42"]
    for i in _indices(len(PROCEDURES), False):
        code, display = PROCEDURES[i]
        entry = record.new_entry(lambda: Procedure(TIME, "procedure"))
        entry.codes.append(Code("SNOMED-CT", code, display))
        lines.append(_lookup(f"P {code}", entry, person))
    for i in _indices(len(MEDICATIONS), False):
        code, display = MEDICATIONS[i]
        entry = record.new_entry(lambda: Medication(TIME, "medication"))
        entry.codes.append(Code("RxNorm", code, display))
        lines.append(_lookup(f"M {code}", entry, person))
    unknown_proc = record.new_entry(lambda: Procedure(TIME, "procedure"))
    unknown_proc.codes.append(Code("SNOMED-CT", "999999999", "Unknown procedure"))
    lines.append(_lookup("X P unknown", unknown_proc, person))
    lines.append(
        _lookup("X P empty", record.new_entry(lambda: Procedure(TIME, "procedure")), person)
    )
    lines.append(
        _lookup("X E empty", record.new_entry(lambda: Encounter(TIME, "wellness")), person)
    )
    lines.append(
        _lookup("X R empty", record.new_entry(lambda: Report(TIME, "laboratory", [])), person)
    )
    return "\n".join(lines)


def _nullperson_case() -> str:
    scratch = _new_person(7, "Massachusetts")
    record = cast(HealthRecord, scratch.record)
    lines = ["person=null"]
    unknown_proc = record.new_entry(lambda: Procedure(TIME, "procedure"))
    unknown_proc.codes.append(Code("SNOMED-CT", "999999999", "Unknown procedure"))
    nobody = cast(Person, None)
    lines.append(
        f"NP P unknown -> {double_to_string(Costs.determine_cost_of_entry(unknown_proc, nobody))}"
    )
    empty_proc = record.new_entry(lambda: Procedure(TIME, "procedure"))
    lines.append(
        f"NP P empty -> {double_to_string(Costs.determine_cost_of_entry(empty_proc, nobody))}"
    )
    empty_enc = record.new_entry(lambda: Encounter(TIME, "wellness"))
    lines.append(
        f"NP E empty -> {double_to_string(Costs.determine_cost_of_entry(empty_enc, nobody))}"
    )
    report = record.new_entry(lambda: Report(TIME, "laboratory", []))
    report.codes.append(Code("LOINC", "123456", "Some lab panel"))
    lines.append(f"NP R code -> {double_to_string(Costs.determine_cost_of_entry(report, nobody))}")
    return "\n".join(lines)


def test_costs_probe(golden: Callable[[str], Path], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(person_module, "CoverageRecord", CoverageRecordDouble)
    cases = _load_cases(golden)
    for state in STATES:
        for seed in SEEDS:
            full = (state == "Massachusetts" and seed == 42) or (state == "Texas" and seed == 12345)
            name = f"lookups:{state}:{seed}"
            assert _lookups_case(state, seed, full) == cases[name], name
    assert _nostate_case() == cases["nostate:42"]
    assert _nullperson_case() == cases["nullperson"]


# --- Claim assembly: integration parity, gated on T15/T16. ---


def _bd(value: Decimal) -> str:
    """Java: BigDecimal.toString."""
    return bigdecimal.to_string(value)


def _dump_claim_entry(label: str, entry: ClaimEntry) -> str:
    return (
        f"{label} cost={_bd(entry.cost)}"
        f" copay={_bd(entry.copay_paid_by_patient)}"
        f" deductible={_bd(entry.deductible_paid_by_patient)}"
        f" adjustment={_bd(entry.adjustment)}"
        f" coinsurance={_bd(entry.coinsurance_paid_by_payer)}"
        f" paid={_bd(entry.paid_by_payer)}"
        f" secondaryPaid={_bd(entry.paid_by_secondary_payer)}"
        f" oop={_bd(entry.patient_out_of_pocket)}"
        f" patientCost={_bd(entry.get_patient_cost())}"
        f" coveredCost={_bd(entry.get_covered_cost())}"
        f" coinsurancePaid={_bd(entry.get_coinsurance_paid())}"
    )


def _dump_claim(person: Person, claim: Claim) -> str:
    member_id = claim.get_plan_record_member_id()
    lines = [
        f"uuid={claim.uuid}",
        f"payer={claim.get_payer().get_name()}"
        f" secondary={claim.get_secondary_payer().get_name()}"
        f" medicare={_b(claim.covered_by_medicare())}"
        f" memberId={'null' if member_id is None else member_id}",
        _dump_claim_entry("main", claim.main_entry),
    ]
    for i, item in enumerate(claim.items):
        lines.append(_dump_claim_entry(f"item{i}", item))
    lines.append(_dump_claim_entry("totals", claim.totals))
    lines.append(
        f"getters totalClaim={_bd(claim.get_total_claim_cost())}"
        f" totalCovered={_bd(claim.get_total_covered_cost())}"
        f" totalDeductible={_bd(claim.get_total_deductible_paid())}"
        f" totalCopay={_bd(claim.get_total_copay_paid())}"
        f" totalSecondary={_bd(claim.get_total_paid_by_secondary_payer())}"
        f" totalAdjustment={_bd(claim.get_total_adjustment())}"
        f" totalCoinsurance={_bd(claim.get_total_coinsurance_paid())}"
        f" totalPatient={_bd(claim.get_total_patient_cost())}"
    )
    plan_record = person.coverage.get_plan_record_at_time(TIME)
    lines.append(
        f"plan oop={_bd(plan_record.get_out_of_pocket_expenses())}"
        f" covered={_bd(plan_record.get_covered_expenses())}"
        f" insurance={_bd(plan_record.get_insurance_expenses())}"
        f" remainingDeductible={_bd(plan_record.remaining_deductible)}"
    )
    lines.append(f"count={person.get_count()}")
    return "\n".join(lines)


def _claim_person(seed: int) -> Person:
    person = Person(seed)
    person.attributes[Person.BIRTHDATE] = BIRTHDATE
    person.attributes[Person.STATE] = "Massachusetts"
    person.coverage.set_plan_to_no_insurance(BIRTHDATE)
    return person


def _claim_encounter_case() -> str:
    person = _claim_person(4242)
    record = cast(HealthRecord, person.record)
    encounter = record.new_entry(lambda: Encounter(TIME, "wellness"))
    encounter.codes.append(Code("SNOMED-CT", ENCOUNTERS[0][0], ENCOUNTERS[0][1]))
    claim = Claim(encounter, person)
    procedure = record.new_entry(lambda: Procedure(TIME, "procedure"))
    procedure.codes.append(Code("SNOMED-CT", PROCEDURES[0][0], PROCEDURES[0][1]))
    claim.add_line_item(procedure)
    immunization = record.new_entry(lambda: Immunization(TIME, "immunization"))
    immunization.codes.append(Code("CVX", "90732", "Pneumococcal vaccine"))
    claim.add_line_item(immunization)
    device = record.new_entry(lambda: Device(TIME, "device"))
    device.codes.append(Code("SNOMED-CT", DEVICES[0][0], DEVICES[0][1]))
    claim.add_line_item(device)
    supply = record.new_entry(lambda: Supply(TIME, "supply"))
    supply.codes.append(Code("SNOMED-CT", SUPPLIES[0][0], SUPPLIES[0][1]))
    claim.add_line_item(supply)
    report = record.new_entry(lambda: Report(TIME, "laboratory", []))
    report.codes.append(Code("LOINC", "123456", "Some lab panel"))
    claim.add_line_item(report)
    unknown = record.new_entry(lambda: Procedure(TIME, "procedure"))
    unknown.codes.append(Code("SNOMED-CT", "999999999", "Unknown procedure"))
    claim.add_line_item(unknown)
    claim.assign_costs()
    return "claim=encounter seed=4242\n" + _dump_claim(person, claim)


def _claim_medication_case() -> str:
    person = _claim_person(777)
    record = cast(HealthRecord, person.record)
    medication = record.new_entry(lambda: Medication(TIME, "medication"))
    medication.codes.append(Code("RxNorm", MEDICATIONS[0][0], MEDICATIONS[0][1]))
    claim = Claim(medication, person)
    procedure = record.new_entry(lambda: Procedure(TIME, "procedure"))
    procedure.codes.append(Code("SNOMED-CT", PROCEDURES[0][0], PROCEDURES[0][1]))
    claim.add_line_item(procedure)
    claim.assign_costs()
    return "claim=medication seed=777\n" + _dump_claim(person, claim)


def _claim_medicationclaim_case() -> str:
    person = _claim_person(778)
    record = cast(HealthRecord, person.record)
    medication = record.new_entry(lambda: Medication(TIME, "medication"))
    medication.codes.append(Code("RxNorm", MEDICATIONS[0][0], MEDICATIONS[0][1]))
    medication.claim.assign_costs()
    return "claim=medicationclaim seed=778\n" + _dump_claim(person, medication.claim)


def _claim_dead_case() -> str:
    person = _claim_person(999)
    person.attributes[Person.DEATHDATE] = TIME - 1000
    record = cast(HealthRecord, person.record)
    encounter = record.new_entry(lambda: Encounter(TIME, "emergency"))
    encounter.codes.append(Code("SNOMED-CT", ENCOUNTERS[1][0], ENCOUNTERS[1][1]))
    claim = Claim(encounter, person)
    procedure = record.new_entry(lambda: Procedure(TIME, "procedure"))
    procedure.codes.append(Code("SNOMED-CT", PROCEDURES[0][0], PROCEDURES[0][1]))
    claim.add_line_item(procedure)
    claim.assign_costs()
    return "claim=dead seed=999\n" + _dump_claim(person, claim)


def test_costs_claims(golden: Callable[[str], Path]) -> None:
    cases = _load_cases(golden)
    # Java: CostsProbe.main calls PayerManager.loadNoInsurance() before all
    # cases; the claim scenarios call coverage.setPlanToNoInsurance, which
    # needs it. (Setup only — every comparison below is unchanged.)
    PayerManager.load_no_insurance()
    builders = {
        "claims:encounter": _claim_encounter_case,
        "claims:medication": _claim_medication_case,
        "claims:medicationclaim": _claim_medicationclaim_case,
        "claims:dead": _claim_dead_case,
    }
    results = [run_or_pending(builders[name], ("T15", "T16")) for name in builders]
    for name, result in zip(builders, results, strict=True):
        if not isinstance(result, Pending):
            assert result == cases[name], name
    report_pending("CostsProbe claim assembly", results)
