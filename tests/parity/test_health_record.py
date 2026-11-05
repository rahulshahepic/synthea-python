"""Java: HealthRecordProbe; exact canonical comparisons, no skips or tolerances."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest

from synthea.helpers.random_code_generator import RandomCodeGenerator, _valid_url
from synthea.javacompat.collections import JavaHashMap
from synthea.world.agents.payer_manager import PayerManager
from synthea.world.agents.person import Person
from synthea.world.concepts.claim import Claim
from synthea.world.concepts.health_record import (
    Allergy,
    CarePlan,
    Code,
    Device,
    EncounterType,
    Entry,
    ImagingStudy,
    Immunization,
    Instance,
    Observation,
    Procedure,
    ReactionSeverity,
    Report,
    Series,
    Supply,
)
from tests.dependency_gate import Pending, report_pending, run_or_pending
from tests.parity.canonical import dump_code, dump_record, register_encoder
from tests.unit.test_health_record import person_double

pytestmark = pytest.mark.parity
URI = "http://example.org/ValueSet/offline"
FULL_RECORD_DEPENDENCIES = ("T09", "T14", "T15", "T16")


def code(value: str) -> Code:
    return Code("SNOMED-CT", value, "Display " + value)


def entry_scenario(i: int) -> dict[str, object]:
    record, rng = person_double(i - 32, household=i % 2 == 0)
    time = -2208988800000 + i * 86400000
    entry = record.new_entry(lambda: Entry(time, "condition"))
    entry.name, entry.note = "state", "note " + str(i)
    entry.merge_code_list([code("a"), code("a"), code("b")])
    record.present["condition"] = entry
    obs = record.new_entry(lambda: Observation(time + 1, "lab", -0.0 if i == 0 else i * 0.125))
    obs.unit, obs.category = "mg", "laboratory"
    obs.observations.append(record.new_entry(lambda: Observation(time + 2, "child", code("v"))))
    report = record.new_entry(lambda: Report(time + 3, "report", [obs]))
    obs.report = report
    record.present["lab"], record.present["report"] = obs, report
    allergy = record.new_entry(lambda: Allergy(time + 4, "allergy"))
    allergy.name, allergy.allergy_type, allergy.category = "allergy state", "allergy", "food"
    allergy.reactions = JavaHashMap()
    allergy.reactions[code("reaction1")] = ReactionSeverity.MILD
    allergy.reactions[code("reaction2")] = ReactionSeverity.SEVERE
    record.present["allergy"] = allergy
    procedure = record.new_entry(lambda: Procedure(time + 5, "procedure"))
    procedure.reasons.append(code("r"))
    procedure.merge_reason_list([code("r"), code("other"), code("other")])
    record.present["procedure"] = procedure
    vaccine = record.new_entry(lambda: Immunization(time + 6, "vaccine"))
    vaccine.series = i % 3
    record.present["vaccine"] = vaccine
    plan = record.new_entry(lambda: CarePlan(time + 7, "plan"))
    plan.activities.add(code("activity"))
    plan.activities.add(code("activity"))
    goal = {"target": i, "unit": "days"}
    plan.goals.add(goal)
    plan.goals.add(dict(goal))
    record.present["plan"] = plan
    device = record.new_entry(lambda: Device(time + 8, "device"))
    device.manufacturer, device.model = "Acme", "Model " + str(i)
    record.present["device"] = device
    supply = record.new_entry(lambda: Supply(time + 9, "supply"))
    supply.quantity = i
    record.present["supply"] = supply
    if i % 3 == 0:
        record.condition_end_by_state(time + 10, "state")
    if i % 3 == 1:
        record.allergy_end_by_state(time + 11, "allergy state")
    if i % 3 == 2:
        record.device_remove(time + 12, "device")
    if i % 5 == 0:
        record.death = time + 13
    onset = record.present_onset("condition")
    return {
        "i": i,
        "record": dump_record(record),
        "condition_active": record.condition_active("condition"),
        "allergy_active": record.allergy_active("allergy"),
        "onset": None if onset is None else str(onset),
        "last_encounter": str(record.last_encounter_time()),
        "since_wellness": str(record.time_since_last_wellness_encounter(time)),
        "summary": record.text_summary(),
        "entry_string": entry.to_string(),
        "rng_count": rng.get_count(),
    }


def full_scenario(i: int) -> dict[str, object]:
    """Mirror public Java record API, intentionally retaining real T09/T14/T06 calls."""
    person = Person(i - 32)
    record = person.record
    time = 1609459200000 + i * 86400000
    person.attributes[Person.BIRTHDATE] = time
    PayerManager.load_no_insurance()
    person.coverage.set_plan_to_no_insurance(time)
    kind = list(EncounterType)[i % len(EncounterType)]
    encounter = record.encounter_start(time, kind)
    record.observation(time + 1, "a", i * 0.125)
    record.observation(time + 2, "b", "text")
    encounter.add_observation(time + 3, "a", i * 0.25, "Second a")
    record.report(time + 4, "report", i % 5)
    record.multi_observation(time + 5, "panel", i % 4)
    condition = record.condition_start(time + 6, "condition")
    condition.name = "condition state"
    condition.codes.append(code("condition"))
    record.condition_start(time + 7, "condition")
    record.allergy_start(time + 8, "allergy").name = "allergy state"
    record.procedure(time + 9, "procedure").codes.append(code("procedure"))
    record.immunization(time + 10, "vaccine").series = 2
    med = record.medication_start(time + 11, "rx", i % 2 == 0)
    med.name = "rx state"
    med.codes.append(code("rx"))
    med.prescription_details = {
        "dosage": {"amount": 2, "frequency": 3, "period": 1, "unit": "days"},
        "duration": {"quantity": 2, "unit": "weeks"},
    }
    record.medication_start(time + 12, "rx", True)
    record.medication_administration(time + 13, "admin")
    plan = record.careplan_start(time + 14, "plan")
    plan.name = "plan state"
    plan.activities.add(code("activity"))
    record.careplan_start(time + 15, "plan")
    record.use_supply(time + 16, code("supply"), i + 1)
    record.device_implant(time + 17, "device").name = "device state"
    record.new_entry(lambda: ImagingStudy(person, time + 18, "prototype"))
    series, instance = Series(), Instance()
    instance.title, instance.sop_class = "Image", code("sop")
    series.instances = [instance]
    series.body_site, series.modality = code("body"), code("modality")
    record.imaging_study(time + 19, "image", [series])
    if i % 2 == 0:
        record.condition_end(time + 20, "condition")
        record.allergy_end(time + 21, "allergy")
        record.medication_end(time + 22, "rx", code("stop"))
        record.careplan_end(time + 23, "plan", code("stop"))
        record.device_remove(time + 24, "device")
    else:
        record.condition_end_by_state(time + 20, "condition state")
        record.allergy_end_by_state(time + 21, "allergy state")
        record.medication_end_by_state(time + 22, "rx state", code("stop"))
        record.careplan_end_by_state(time + 23, "plan state", code("stop"))
        record.device_remove_by_state(time + 24, "device state")
    encounter.end(time + 25)
    encounter.end(time + 26)
    second = record.encounter_start(time + 86400000, EncounterType.WELLNESS)
    previous = second.previous_encounter()
    assert previous is not None
    return {
        "i": i,
        "record": dump_record(record),
        "quantity": str(med.get_quantity()),
        "previous": str(previous.uuid),
        "current_before": str(record.current_encounter(time - 1).uuid),
        "current": str(record.current_encounter(time + 30).uuid),
        "last_encounter": str(record.last_encounter_time()),
        "since_wellness": str(record.time_since_last_wellness_encounter(time)),
        "providers": record.provider_count(),
        "rng_count": person.get_count(),
    }


def test_health_record_component_entries(golden: Callable[[str], Path]) -> None:
    """Component parity (Person test double: attributes + real T01 RNG)."""
    rows = [
        json.loads(line)
        for line in (golden("HealthRecordProbe") / "entries.jsonl").read_text().splitlines()
    ]
    assert len(rows) >= 50
    for expected in rows:
        assert entry_scenario(expected["i"]) == expected, expected["i"]


def test_public_record_scenarios(golden: Callable[[str], Path]) -> None:
    """Integration parity (real Person/Claim/coverage); required in full by T16 (#16)."""
    register_encoder(Claim, lambda claim: {"uuid": str(claim.uuid)})
    rows = [
        json.loads(line)
        for line in (golden("HealthRecordProbe") / "records.jsonl").read_text().splitlines()
    ]
    assert len(rows) >= 50
    results = [
        run_or_pending(lambda i=expected["i"]: full_scenario(i), FULL_RECORD_DEPENDENCIES)
        for expected in rows
    ]
    for expected, actual in zip(rows, results, strict=True):
        if not isinstance(actual, Pending):
            assert actual == expected, expected["i"]
    report_pending("HealthRecord full-record parity", results)


def test_offline_random_codes(golden: Callable[[str], Path]) -> None:
    RandomCodeGenerator.codeListCache.clear()
    RandomCodeGenerator.selectedCodes.clear()
    try:
        RandomCodeGenerator.load_value_set(
            None,
            {
                "url": URI,
                "compose": {
                    "include": [
                        {
                            "system": "SNOMED-CT",
                            "concept": [{"code": f"c{i}", "display": f"Display {i}"}],
                        }
                        for i in range(17)
                    ]
                },
            },
        )
        rows = [
            json.loads(line)
            for line in (golden("HealthRecordProbe") / "codes.jsonl").read_text().splitlines()
        ]
        assert len(rows) >= 5
        for expected in rows:
            seed = int(expected["seed"])
            actual = {
                "seed": expected["seed"],
                "two": dump_code(RandomCodeGenerator.get_code(URI, seed)),
                "three": dump_code(RandomCodeGenerator.get_code(URI, seed, code("fallback"))),
                "selected": len(RandomCodeGenerator.selectedCodes),
                "contains": RandomCodeGenerator.code_in_value_set(
                    Code("SNOMED-CT", "c0", "Changed display"), URI
                ),
            }
            assert actual == expected
    finally:
        RandomCodeGenerator.codeListCache.clear()
        RandomCodeGenerator.selectedCodes.clear()


def test_url_validator_parity(golden: Callable[[str], Path]) -> None:
    rows = [
        json.loads(line)
        for line in (golden("HealthRecordProbe") / "urls.jsonl").read_text().splitlines()
    ]
    assert len(rows) >= 150
    urls = {row["url"] for row in rows}
    assert None in urls and "" in urls
    module_urls: set[str] = set()

    def collect(value: object) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "value_set" and isinstance(child, str):
                    module_urls.add(child)
                collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)

    modules = Path(__file__).resolve().parents[2] / "java/src/main/resources/modules"
    for module in sorted(modules.rglob("*.json")):
        collect(json.loads(module.read_text()))
    assert module_urls <= urls
    for expected in rows:
        assert _valid_url(expected["url"]) == expected["valid"], expected


def test_health_record_component_json_codes(golden: Callable[[str], Path]) -> None:
    """Component parity: Gson primitive-to-string conversion and code identity."""
    for line in (golden("HealthRecordProbe") / "json_codes.jsonl").read_text().splitlines():
        expected = json.loads(line)
        value = Code(expected["definition"])
        equivalent = Code(value.system, value.code, value.display)
        assert {
            "definition": expected["definition"],
            "code": dump_code(value),
            "hash": value.hash_code(),
            "equals": value == equivalent,
            "compare": value.compare_to(equivalent),
        } == expected
