"""Java: HealthRecordTest and entry behavior at unported dependency boundaries."""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from unittest.mock import patch
from uuid import UUID

import pytest

from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.javacompat.collections import JavaConcurrentHashMap, JavaHashMap
from synthea.world.agents.person import Person
from synthea.world.concepts.health_record import (
    Allergy,
    CarePlan,
    Code,
    Device,
    EncounterType,
    Entry,
    HealthRecord,
    Instance,
    Procedure,
    ReactionSeverity,
    Series,
)


def record_boundary(
    seed: int, household: bool = False
) -> tuple[HealthRecord, DefaultRandomNumberGenerator]:
    """Supply only Person's attributes/RNG boundary until T09 is merged.

    Calls the real T01 RNG; never replaces a T08 method or expected Java output.
    No Claim stand-in is used by parity tests.
    """
    person = object.__new__(Person)
    rng = DefaultRandomNumberGenerator(seed)
    person.attributes = JavaConcurrentHashMap()
    person.chronic_medications = JavaConcurrentHashMap()
    if household:
        person.attributes[Person.HOUSEHOLD] = "group"
        person.attributes["age"] = 7
    for name in (
        "rand",
        "rand_int",
        "rand_long",
        "rand_gaussian",
        "rand_boolean",
        "get_seed",
        "get_count",
    ):
        setattr(person, name, getattr(rng, name))
    # A per-instance boundary avoids patching the class globally during parity.
    person.rand_uuid = lambda: UUID(rng.rand_uuid())  # type: ignore[method-assign]
    return HealthRecord(person), rng


@pytest.fixture
def record() -> HealthRecord:
    return record_boundary(42)[0]


@pytest.fixture
def claimed_record(record: HealthRecord) -> Iterator[HealthRecord]:
    """Isolate T08 logic in unit tests; Claim's production stub remains unchanged."""
    with patch("synthea.world.concepts.claim.Claim", autospec=True):
        yield record


def test_code_identity_hash_and_json() -> None:
    a = Code({"system": "SNOMED", "code": "123", "display": "first"})
    b = Code("SNOMED", "123", "second")
    b.version, b.value_set = "v2", "http://example.org"
    assert a == b
    assert a.java_hash_code() == b.java_hash_code()
    assert a.compare_to(b) == 0
    assert a != Code("LOINC", "123", "first")
    assert not a.equals(None)
    assert str(a) == "system=SNOMED, code=123, display=first, version=null, valueSet=null"
    assert Code.from_json([{"system": "SNOMED", "code": "123", "display": "first"}]) == [a]
    assert a.compare_to(Code("SNOMED", "124", "next")) < 0
    assert list(JavaHashMap([(a, "value")]).values()) == ["value"]


def test_entry_merges_and_java_reason_quirk(record: HealthRecord) -> None:
    a, b = Code("s", "a", "A"), Code("s", "b", "B")
    procedure = record.new_entry(lambda: Procedure(-1, "proc"))
    procedure.merge_code_list([a, a, b])
    assert procedure.codes == [a, b]
    procedure.reasons.append(a)
    procedure.merge_reason_list([a, b, b])
    # Upstream bug: mergeReasonList appends to codes, not reasons; no dedup against codes.
    assert procedure.reasons == [a]
    assert procedure.codes == [a, b, b, b]
    assert procedure.contains_reason("a", "s")
    assert procedure.to_string() == "1969-12-31T23:59:59.999Z proc"
    assert procedure.stop == -1 + 900_000
    procedure.cost = Decimal("1.20")
    assert procedure.get_cost() == Decimal("1.20")


@pytest.mark.parametrize("time,count", [(0, 0), (-1, 1), (1000, 10)])
def test_active_entries_and_hash_order(record: HealthRecord, time: int, count: int) -> None:
    for i in range(count):
        entry = record.new_entry(lambda i=i: Entry(time, str(i)))
        entry.name = "same state"
        record.present[entry.type] = entry
    before = list(record.present)
    record.condition_end_by_state(123, "same state")
    assert list(record.present) == before[1:]
    assert record.present_onset("absent") is None
    for key in list(record.present):
        assert record.condition_active(key)
        assert record.present_onset(key) == time
        record.condition_end(222, key)
        assert not record.condition_active(key)


@pytest.mark.parametrize("kind", list(EncounterType))
def test_encounter_duration_and_enum(claimed_record: HealthRecord, kind: EncounterType) -> None:
    encounter = claimed_record.encounter_start(100, kind)
    minutes = (
        60
        if kind == EncounterType.EMERGENCY
        else (
            1440
            if kind in (EncounterType.INPATIENT, EncounterType.HOSPICE, EncounterType.SNF)
            else 15
        )
    )
    assert encounter.stop == 100 + minutes * 60_000
    assert EncounterType.from_string(kind.to_string()) == kind
    assert kind.code() in ("AMB", "IMP", "EMER", "HH", "VR")
    assert EncounterType.from_string(None) == EncounterType.AMBULATORY
    assert EncounterType.from_string("super") == EncounterType.INPATIENT


def test_current_and_previous_encounters(claimed_record: HealthRecord) -> None:
    record = claimed_record
    assert record.last_encounter_time() == -(1 << 63)
    assert record.time_since_last_wellness_encounter(0) == (1 << 63) - 1
    first = record.encounter_start(100, EncounterType.WELLNESS)
    second = record.encounter_start(200, EncounterType.OUTPATIENT)
    assert record.current_encounter(0) is first
    assert record.current_encounter(150) is first
    assert record.current_encounter(200) is second
    assert first.previous_encounter() is None
    assert second.previous_encounter() is first
    assert record.last_wellness_encounter() is first
    assert record.time_since_last_wellness_encounter(50) == -50


@pytest.mark.parametrize(
    "count,expected", [(0, []), (2, ["B", "C"]), (3, ["A", "B", "C"]), (4, ["A", "B", "C"])]
)
def test_report_observations(claimed_record: HealthRecord, count: int, expected: list[str]) -> None:
    """Java: HealthRecordTest#testReportAllObs/testReportSomeObs/testReportTooManyObs."""
    encounter = claimed_record.encounter_start(0, EncounterType.WELLNESS)
    for text in ("A", "B", "C"):
        claimed_record.observation(0, text, text)
    report = claimed_record.report(0, "R", count)
    assert [o.value for o in report.observations] == expected
    assert len(encounter.observations) == 3
    assert all(o.report is report for o in report.observations)


def test_observations_reversed_panel_and_first_match(claimed_record: HealthRecord) -> None:
    record = claimed_record
    encounter = record.encounter_start(0, EncounterType.WELLNESS)
    a = encounter.add_observation(0, "a", 1.0)
    b = encounter.add_observation(1, "a", 2.0, None)
    assert a.codes == []
    assert b.codes[0].display is None
    assert record.get_latest_observation("a") is a
    panel = record.multi_observation(2, "panel", 2)
    assert panel.observations == [b, a]
    assert encounter.observations == [panel]
    assert record.multi_observation(3, "too many", 5).observations == []
    assert record.get_latest_observation("missing") is None


def test_encounter_end_times_idempotence_and_ignored_chronics(claimed_record: HealthRecord) -> None:
    record = claimed_record
    encounter = record.encounter_start(0, EncounterType.WELLNESS)
    observation = record.observation(1, "x", 4.0)
    observation.stop = 2_000_000
    condition = record.condition_start(2, "c")
    assert record.condition_start(3, "c") is condition
    condition.stop = 20_000_000
    record.encounter_start(3, EncounterType.OUTPATIENT)
    encounter.end(5)
    assert encounter.stop == 2_000_000
    assert encounter.ended_time == 5
    encounter.end(30_000_000)
    assert encounter.stop == 2_000_000
    assert record.provider_count() == 0
    assert "Encounters:      2\n" in record.text_summary()


def test_medication_lifecycle(claimed_record: HealthRecord) -> None:
    record = claimed_record
    record.encounter_start(0, EncounterType.WELLNESS)
    reason = Code("s", "end", "End")
    med = record.medication_start(1, "rx", False)
    med.name = "rx state"
    assert record.medication_start(2, "rx", True) is med
    assert not med.chronic  # adding to chronic map doesn't alter original flag
    assert record.person.chronic_medications["rx"] is med
    assert record.medication_active("rx")
    admin = record.medication_administration(3, "rx")
    assert admin.administration and admin.stop == admin.start
    assert record.present["rx"] is med
    assert med.get_quantity() == 30
    assert admin.get_quantity() == 1
    record.medication_end_by_state(4, "rx state", reason)
    assert med.stop == 4 and med.stop_reason is reason
    assert "rx" not in record.person.chronic_medications
    assert not record.medication_active("rx")


def test_careplans_allergies_supplies_and_immunizations(claimed_record: HealthRecord) -> None:
    record = claimed_record
    encounter = record.encounter_start(0, EncounterType.WELLNESS)
    reason = Code("s", "r", "Reason")
    allergy = record.allergy_start(1, "a")
    assert record.allergy_start(2, "a") is allergy
    allergy.name = "allergy state"
    assert record.allergy_active("a")
    record.allergy_end_by_state(3, "allergy state")
    assert allergy.stop == 3 and not record.allergy_active("a")
    cp = record.careplan_start(1, "cp")
    assert record.careplan_start(2, "cp") is cp
    cp.name = "plan state"
    cp.activities.add(reason)
    cp.activities.add(Code("s", "r", "Alternate display"))
    cp.goals.add({"b": 2, "a": 1})
    cp.goals.add({"a": 1, "b": 2})
    assert len(cp.activities) == len(cp.goals) == 1
    assert record.careplan_active("cp")
    record.careplan_end_by_state(3, "plan state", reason)
    assert cp.stop_reason is reason and not record.careplan_active("cp")
    supply = record.use_supply(4, Code("s", "gauze", "Gauze"), 6)
    assert supply.type == "Gauze" and supply.quantity == 6
    assert encounter.supplies == [supply]
    assert record.immunization(5, "vaccine").series == -1
    assert ReactionSeverity.MODERATE.code == "6736007"
    assert ReactionSeverity.MILD.display == "Mild"


def test_snapshot_serialization_explicitly_excluded(record: HealthRecord) -> None:
    from io import BytesIO

    careplan = record.new_entry(lambda: CarePlan(0, "cp"))
    with pytest.raises(NotImplementedError, match="out of scope"):
        careplan.write_object(BytesIO())
    with pytest.raises(NotImplementedError, match="out of scope"):
        careplan.read_object(BytesIO())


def test_clones_are_shallow_and_defaults_match_java(record: HealthRecord) -> None:
    series = Series()
    series.instances = [Instance()]
    series.body_site = Code("s", "b", "Body")
    clone = series.clone()
    assert clone is not series and clone.instances is series.instances
    assert clone.body_site is series.body_site
    instance = series.instances[0]
    instance.sop_class = Code("s", "c", "Class")
    assert instance.clone().sop_class is instance.sop_class
    assert record.new_entry(lambda: Allergy(0, "a")).reactions is None
    device = record.new_entry(lambda: Device(0, "d"))
    assert device.udi_date(1451606400000) == "160101"
    assert device.udi_date(1514678400000) == "181231"
    assert device.trim_long(-(1 << 63), 14) == "92233720368547"


def test_costs_delegate_and_truncate_toward_zero(record: HealthRecord) -> None:
    entry = record.new_entry(lambda: Entry(0, "costed"))
    with patch(
        "synthea.world.concepts.costs.Costs.determine_cost_of_entry", return_value=-1.239
    ) as cost:
        assert entry.get_cost() == Decimal("-1.23")
        assert entry.get_cost() == Decimal("-1.23")
        cost.assert_called_once_with(entry, record.person)


def test_quantity_exact_decimal_arithmetic(claimed_record: HealthRecord) -> None:
    """Java: HealthRecordTest#testMedicationDetailedQuantity and exact division edge cases."""
    claimed_record.encounter_start(0, EncounterType.WELLNESS)
    med = claimed_record.medication_start(1, "rx", False)
    med.prescription_details = {
        "dosage": {"amount": "0.5", "frequency": 3, "period": 1, "unit": "days"},
        "duration": {"quantity": 2, "unit": "weeks"},
    }
    with patch(
        "synthea.helpers.utilities.Utilities.convert_time", side_effect=[86_400_000, 1_209_600_000]
    ):
        assert med.get_quantity() == 21
    with (
        patch("synthea.helpers.utilities.Utilities.convert_time", side_effect=[3, 1]),
        pytest.raises(ArithmeticError),
    ):
        med.get_quantity()


def test_encounter_end_delegates_cost_assignment(claimed_record: HealthRecord) -> None:
    record = claimed_record
    encounter = record.encounter_start(0, EncounterType.WELLNESS)
    with patch.object(encounter, "determine_cost") as cost:
        record.encounter_end(1000, EncounterType.OUTPATIENT)
        assert not encounter.ended
        record.encounter_end(1000, EncounterType.WELLNESS)
        assert encounter.ended and encounter.ended_time == 1000
        cost.assert_called_once()
        encounter.claim.assign_costs.assert_called_once()


def test_current_encounter_empty_record_calls_encounter_module(record: HealthRecord) -> None:
    with patch("synthea.modules.encounter_module.EncounterModule.create_encounter") as create:
        create.return_value.start = 0
        encounter = record.current_encounter(0)
        assert encounter is create.return_value
        assert encounter.name == "First Wellness"
        assert create.call_args.args[:3] == (record.person, 0, EncounterType.WELLNESS)


def test_device_draw_order_at_utilities_boundary(record: HealthRecord) -> None:
    rng = DefaultRandomNumberGenerator(42)
    reference = DefaultRandomNumberGenerator(42)
    device = record.new_entry(lambda: Device(1600000000000, "device"))
    with patch(
        "synthea.helpers.utilities.Utilities.convert_time",
        side_effect=[1_814_400_000, 788_940_000_000],
    ):
        device.generate_udi(rng)
    expected_identifier = str(reference.rand_long()).removeprefix("-")[:14]
    lot = str(reference.rand_long()).removeprefix("-")
    lot_length = int(reference.rand(4, 20))
    serial = str(reference.rand_long()).removeprefix("-")
    serial_length = int(reference.rand(4, 20))
    assert device.device_identifier == expected_identifier
    assert device.lot_number == lot[:lot_length]
    assert device.serial_number == serial[:serial_length]
    assert rng.get_count() == reference.get_count() == 5


def test_careplan_json_goal_equality_distinguishes_boolean_from_number(
    record: HealthRecord,
) -> None:
    plan = record.new_entry(lambda: CarePlan(0, "plan"))
    plan.goals.add({"target": True})
    plan.goals.add({"target": 1})
    plan.goals.add({"target": 1.0})
    assert list(plan.goals) == [{"target": True}, {"target": 1}]
    plan.goals.discard({"target": 1})
    assert list(plan.goals) == [{"target": True}]


def test_outer_instance_binding_is_nested_and_exception_safe() -> None:
    first, _ = record_boundary(1)
    second, _ = record_boundary(2)
    inner = first.new_entry(lambda: second.new_entry(lambda: Entry(0, "inner")))
    assert inner.record is second
    with pytest.raises(LookupError):
        Entry(0, "unbound")

    def failing_factory() -> Entry:
        entry = Entry(0, "before failure")
        assert entry.record is first
        raise ValueError("construction failed")

    with pytest.raises(ValueError, match="construction failed"):
        first.new_entry(failing_factory)
    with pytest.raises(LookupError):
        Entry(0, "still unbound")
