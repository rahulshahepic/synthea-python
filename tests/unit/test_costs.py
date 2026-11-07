"""Unit tests for Costs and CostData (T14).

Exact seeded amounts are covered by tests/parity/test_costs.py; these tests
pin the branch structure: which entry types have costs, the default-cost
paths, location adjustment wiring, and CostData clamping.
"""

from __future__ import annotations

import pytest

import synthea.world.agents.person as person_module
from synthea.world.agents.person import Person
from synthea.world.concepts import costs as costs_module
from synthea.world.concepts.costs import CostData, Costs
from synthea.world.concepts.health_record import (
    Code,
    Device,
    Encounter,
    Immunization,
    Medication,
    Observation,
    Procedure,
    Report,
    Supply,
)
from tests.parity.costs_doubles import CoverageRecordDouble

BIRTHDATE = 946684800000
TIME = BIRTHDATE + 30 * 86400000


@pytest.fixture
def person(monkeypatch: pytest.MonkeyPatch) -> Person:
    monkeypatch.setattr(person_module, "CoverageRecord", CoverageRecordDouble)
    person = Person(42)
    person.attributes[Person.BIRTHDATE] = BIRTHDATE
    person.attributes[Person.STATE] = "Massachusetts"
    return person


def test_has_cost_by_entry_type(person: Person) -> None:
    record = person.record
    assert record is not None
    assert Costs.has_cost(record.new_entry(lambda: Procedure(TIME, "procedure")))
    assert Costs.has_cost(record.new_entry(lambda: Medication(TIME, "medication")))
    assert Costs.has_cost(record.new_entry(lambda: Encounter(TIME, "wellness")))
    assert Costs.has_cost(record.new_entry(lambda: Immunization(TIME, "immunization")))
    assert Costs.has_cost(record.new_entry(lambda: Report(TIME, "laboratory", [])))
    assert Costs.has_cost(record.new_entry(lambda: Device(TIME, "device")))
    assert Costs.has_cost(record.new_entry(lambda: Supply(TIME, "supply")))
    assert not Costs.has_cost(record.new_entry(lambda: Observation(TIME, "vital-signs", 1.0)))


def test_has_specified_cost() -> None:
    known = next(iter(Costs.PROCEDURE_COSTS))
    assert Costs.has_specified_cost(known)
    assert not Costs.has_specified_cost("999999999")


def test_unknown_code_uses_default_cost_times_location_factor(person: Person) -> None:
    record = person.record
    assert record is not None
    procedure = record.new_entry(lambda: Procedure(TIME, "procedure"))
    procedure.codes.append(Code("SNOMED-CT", "999999999", "Unknown procedure"))
    factor = Costs.PROCEDURES_ADJUSTMENT_FACTORS["MA"]
    assert Costs.determine_cost_of_entry(procedure, person) == 500.0 * factor


def test_empty_codes_uses_default_cost_times_location_factor(person: Person) -> None:
    record = person.record
    assert record is not None
    encounter = record.new_entry(lambda: Encounter(TIME, "wellness"))
    factor = Costs.ENCOUNTER_ADJUSTMENT_FACTORS["MA|wellness"]
    assert Costs.determine_cost_of_entry(encounter, person) == 125.0 * factor


def test_report_uses_default_lab_cost(person: Person) -> None:
    record = person.record
    assert record is not None
    report = record.new_entry(lambda: Report(TIME, "laboratory", []))
    factor = Costs.LAB_ADJUSTMENT_FACTORS["MA"]
    assert Costs.determine_cost_of_entry(report, person) == 100.0 * factor


def test_observation_has_no_cost(person: Person) -> None:
    record = person.record
    assert record is not None
    observation = record.new_entry(lambda: Observation(TIME, "vital-signs", 1.0))
    assert Costs.determine_cost_of_entry(observation, person) == 0.0


def test_no_state_means_no_adjustment(person: Person) -> None:
    person = Person(42)  # same patched fixture scope, but no STATE attribute
    person.attributes[Person.BIRTHDATE] = BIRTHDATE
    record = person.record
    assert record is not None
    procedure = record.new_entry(lambda: Procedure(TIME, "procedure"))
    procedure.codes.append(Code("SNOMED-CT", "999999999", "Unknown procedure"))
    assert Costs.determine_cost_of_entry(procedure, person) == 500.0


def test_cost_data_choose_cost_stays_within_bounds(person: Person) -> None:
    data = CostData(10.0, 20.0, 30.0)
    for _ in range(200):
        value = data.choose_cost(person)
        assert 10.0 <= value <= 30.0


def test_load_cost_data_is_a_no_op() -> None:
    assert Costs.load_cost_data() is None


def test_parse_csv_to_map_skips_non_numeric_rows(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    raw = "CODE,MIN,MODE,MAX,COMMENTS\n111,1,2,3,Ok\n222,x,2,3,Bad row\n"
    monkeypatch.setattr(costs_module.Utilities, "read_resource_and_strip_bom", lambda filename: raw)
    parsed = Costs.parse_csv_to_map("costs/fake.csv")
    assert list(parsed) == ["111"]
    assert parsed["111"].min == 1.0
    assert parsed["111"].mode == 2.0
    assert parsed["111"].max == 3.0
    err = capsys.readouterr().err
    assert "Invalid cost for code: '222'" in err
    assert "Code '222' will use the default cost" in err
