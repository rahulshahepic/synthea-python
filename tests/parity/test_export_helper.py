"""Java: ExportHelperProbe; exact comparisons, no skips or tolerances.

Component parity for T25: ExportHelper statics are recomputed from the inputs
recorded in the golden; Exporter record filtering runs on scripted records
built on a Person double (attributes/RNG/record plumbing only — Person's own
constructor is T09/T16 territory and its coverage chain is still a stub; all
filtering code under test is the real production code). The cause-of-death
scenario calls DeathModule.process (T22) and is gated accordingly.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest

from synthea.engine.components import Attachment, SampledData
from synthea.export.export_helper import ExportHelper, FhirCondition
from synthea.export.exporter import Exporter, ExporterRuntimeOptions
from synthea.helpers.config import Config
from synthea.helpers.time_series_data import TimeSeriesData
from synthea.helpers.utilities import Utilities
from synthea.modules.death_module import DeathModule
from synthea.world.agents.person import Person
from synthea.world.concepts.health_record import (
    Code,
    EncounterType,
    Entry,
    HealthRecord,
    Observation,
)
from tests.dependency_gate import Pending, report_pending, run_or_pending
from tests.parity.canonical import dump_record, register_encoder
from tests.parity.canonical.export import dump_claim  # (importing registers encoders)
from tests.parity.export_doubles import ClaimDouble
from tests.unit.test_health_record import person_double

pytestmark = pytest.mark.parity

register_encoder(ClaimDouble, dump_claim)  # type: ignore[arg-type]


@pytest.fixture(autouse=True)
def _claim_double() -> object:
    """Swap the T14-stub Claim for the plumbing double while building records."""
    import synthea.world.concepts.claim as claim_module

    real = claim_module.Claim
    claim_module.Claim = ClaimDouble  # type: ignore[misc]
    yield
    claim_module.Claim = real


TIME = 1700000000000
YEARS = 5
DUMMY_CODE = Code("", "", "")


def years(n: int) -> int:
    return Utilities.convert_time("years", n)


def load_cases(golden: Callable[[str], Path]) -> list[dict[str, object]]:
    path = golden("ExportHelperProbe") / "export_helper.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def by_case(cases: list[dict[str, object]], kind: str) -> list[dict[str, object]]:
    return [c for c in cases if c["case"] == kind]


def new_patient() -> tuple[Person, HealthRecord]:
    """A Person-shaped double carrying a real HealthRecord (see module docstring)."""
    record, _rng = person_double(12345)
    person = record.person
    person.record = record
    person.records = None
    person.has_multiple_records = False
    person.attributes[Person.BIRTHDATE] = TIME - years(30)
    person.attributes[Person.INCOME] = 100000
    return person, record


def test_dates(golden: Callable[[str], Path]) -> None:
    for case in by_case(load_cases(golden), "dates"):
        t = int(case["time"])  # type: ignore[arg-type]
        assert ExportHelper.date_from_timestamp(t) == case["date"]
        assert ExportHelper.iso8601_timestamp(t) == case["iso"]


def test_next_friday(golden: Callable[[str], Path]) -> None:
    for case in by_case(load_cases(golden), "next_friday"):
        t = int(case["time"])  # type: ignore[arg-type]
        assert ExportHelper.next_friday(t) == int(case["result"])  # type: ignore[arg-type]


def test_systems(golden: Callable[[str], Path]) -> None:
    for case in by_case(load_cases(golden), "system_uri"):
        assert ExportHelper.get_system_uri(case["in"]) == case["out"]  # type: ignore[arg-type]
    for case in by_case(load_cases(golden), "system_from_uri"):
        assert ExportHelper.get_system_from_uri(case["in"]) == case["out"]  # type: ignore[arg-type]
    for case in by_case(load_cases(golden), "unduplicated"):
        assert case["values"] == ExportHelper.UNDUPLICATED_FHIR_RESOURCES


def test_fhir_urls(golden: Callable[[str], Path]) -> None:
    for case in by_case(load_cases(golden), "fhir_url"):
        assert (
            ExportHelper.build_fhir_search_url(case["resource"], case["id"]) == case["out"]  # type: ignore[arg-type]
        )
    for case in by_case(load_cases(golden), "fhir_npi_url"):
        from synthea.world.agents.clinician import Clinician

        clinician = object.__new__(Clinician)
        clinician.npi = case["npi"]
        assert ExportHelper.build_fhir_npi_search_url(clinician) == case["out"]
    for case in by_case(load_cases(golden), "fhir_npi_url_null"):
        assert ExportHelper.build_fhir_npi_search_url(None) == case["out"]


def test_uuids(golden: Callable[[str], Path]) -> None:
    for case in by_case(load_cases(golden), "uuid"):
        result = ExportHelper.build_uuid(
            int(case["seed"]),  # type: ignore[arg-type]
            int(case["time"]),  # type: ignore[arg-type]
            case["key"],  # type: ignore[arg-type]
        )
        assert result == case["out"]
    for case in by_case(load_cases(golden), "uuid_person"):
        person, _record = new_patient()
        result = ExportHelper.build_uuid(person, int(case["time"]), case["key"])  # type: ignore[arg-type]
        assert result == case["out"]


def _obs(record: HealthRecord, value: object) -> Observation:
    observation = record.new_entry(lambda: Observation(TIME, "test", value))
    observation.codes.append(Code("SNOMED-CT", "1234", "Test Code"))
    return observation


def _sampled(pattern: str | None, series_values: list[list[float]]) -> SampledData:
    sampled = object.__new__(SampledData)
    sampled.series = [TimeSeriesData(values, 1.0) for values in series_values]
    sampled.decimal_format = pattern
    return sampled


def _attachment(data: str | None, url: str | None) -> Attachment:
    attachment = object.__new__(Attachment)
    attachment.data = data
    attachment.url = url
    return attachment


def _obs_builders() -> dict[str, Callable[[HealthRecord], object]]:
    doubles = [
        0.0,
        -0.0,
        1.05,
        1.15,
        2.675,
        0.125,
        123.456,
        -7.25,
        1e20,
        float("nan"),
        float("inf"),
        float("-inf"),
        0.05,
        0.25,
        99.95,
    ]
    builders: dict[str, Callable[[HealthRecord], object]] = {
        "code": lambda r: Code("SNOMED-CT", "705129", "Fake Code Display"),
        "string": lambda r: "some text",
        "boolean_true": lambda r: True,
        "boolean_false": lambda r: False,
        "integer": lambda r: 42,
        "long": lambda r: 123456789012345,
        "null": lambda r: None,
        "fhir_condition": lambda r: FhirCondition(),
        "sampled_wrapped": lambda r: _sampled("0.00", [[1.005, 2.675]]),
        "attachment_data": lambda r: _attachment("data payload", None),
        "attachment_url": lambda r: _attachment(None, "http://example.org/file"),
        "attachment_both": lambda r: _attachment("d", "u"),
        "attachment_none": lambda r: _attachment(None, None),
    }
    for d in doubles:
        from synthea.javacompat.numbers import double_to_string

        builders["double_" + double_to_string(d)] = lambda r, d=d: d
    return builders


def test_observation_values(golden: Callable[[str], Path]) -> None:
    builders = _obs_builders()
    _person, record = new_patient()
    for case in by_case(load_cases(golden), "obs_value"):
        name = case["name"]
        observation = _obs(record, builders[name](record))  # type: ignore[operator,index]
        if case["result"] == "ERR:ClassCastException":
            with pytest.raises(TypeError):
                ExportHelper.get_observation_value(observation)
        else:
            assert ExportHelper.get_observation_value(observation) == case["result"], name
        assert ExportHelper.get_observation_type(observation) == case["type"], name


def test_observation_by_code(golden: Callable[[str], Path]) -> None:
    _person, record = new_patient()
    panel = record.new_entry(lambda: Observation(TIME, "panel", "panel value"))
    panel.codes.append(Code("SNOMED-CT", "panel-code", "Panel"))
    child_a = record.new_entry(lambda: Observation(TIME, "child", 42.5))
    child_a.codes.append(Code("SNOMED-CT", "child-a", "Child A"))
    grand = record.new_entry(lambda: Observation(TIME, "grandchild", "deep"))
    grand.codes.append(Code("SNOMED-CT", "grand", "Grandchild"))
    child_a.observations.append(grand)
    child_b = record.new_entry(lambda: Observation(TIME, "child", "b text"))
    child_b.codes.append(Code("SNOMED-CT", "child-b", "Child B"))
    child_a2 = record.new_entry(lambda: Observation(TIME, "child", "second a"))
    child_a2.codes.append(Code("SNOMED-CT", "child-a", "Child A2"))
    panel.observations.extend([child_a, child_b, child_a2])
    for case in by_case(load_cases(golden), "obs_by_code"):
        result = ExportHelper.get_observation_value(panel, case["code"])  # type: ignore[arg-type]
        assert result == case["result"]


def test_sampled_data(golden: Callable[[str], Path]) -> None:
    builders: dict[str, SampledData] = {
        "default_two_series": _sampled(
            None, [[1.2345, 1234567.891, 0.0005], [2.675, 0.125, 999.9999]]
        ),
        "pattern_0.00": _sampled("0.00", [[2.675, 1.005, 0.125]]),
        "pattern_0.0": _sampled("0.0", [[2.65, 2.75, -0.05]]),
        "pattern_hash": _sampled("#.##", [[0.5, 0.05, 123.456]]),
        "pattern_grouped": _sampled("#,##0.00", [[1234567.891, 42.0]]),
        "pattern_0": _sampled("0", [[2.5, 3.5, 4.5]]),
        "default_special": _sampled(None, [[float("nan"), float("inf"), float("-inf")]]),
    }
    for case in by_case(load_cases(golden), "sampled"):
        result = ExportHelper.sampled_data_to_value_string(builders[case["name"]])  # type: ignore[index]
        assert result == case["result"], case["name"]


# --- Exporter record filtering ---------------------------------------------


def _script_simple_cutoff(record: HealthRecord) -> None:
    record.encounter_start(TIME - years(8), EncounterType.WELLNESS)
    record.observation(TIME - years(8), "height", 64)
    record.encounter_start(TIME - years(4), EncounterType.WELLNESS)
    record.observation(TIME - years(4), "weight", 128)


def _script_keep_old_active_medication(record: HealthRecord) -> None:
    code = Code("SNOMED-CT", "705129", "Fake Code")
    record.encounter_start(TIME - years(10), EncounterType.AMBULATORY)
    record.medication_start(TIME - years(10), "fakeitol", True)
    record.encounter_start(TIME - years(8), EncounterType.AMBULATORY)
    med = record.medication_start(TIME - years(8), "placebitol", True)
    med.codes.append(code)
    record.medication_end(TIME - years(6), "placebitol", DUMMY_CODE)


def _script_medication_ended_during_target(record: HealthRecord) -> None:
    code = Code("SNOMED-CT", "705129", "Fake Code")
    record.encounter_start(TIME - years(10), EncounterType.AMBULATORY)
    med = record.medication_start(TIME - years(10), "dimoxinil", False)
    med.codes.append(code)
    record.medication_end(TIME - years(9), "dimoxinil", DUMMY_CODE)
    record.encounter_start(TIME - years(8), EncounterType.AMBULATORY)
    med = record.medication_start(TIME - years(8), "placebitol", True)
    med.codes.append(code)
    record.medication_end(TIME - years(4), "placebitol", DUMMY_CODE)


def _script_keep_old_active_careplan(record: HealthRecord) -> None:
    record.encounter_start(TIME - years(10), EncounterType.WELLNESS)
    record.careplan_start(TIME - years(10), "stop_smoking")
    record.careplan_end(TIME - years(8), "stop_smoking", DUMMY_CODE)
    record.encounter_start(TIME - years(12), EncounterType.WELLNESS)
    record.careplan_start(TIME - years(12), "healthy_diet")


def _script_careplan_ended_during_target(record: HealthRecord) -> None:
    record.encounter_start(TIME - years(10), EncounterType.WELLNESS)
    record.careplan_start(TIME - years(10), "stop_smoking")
    record.careplan_end(TIME - years(1), "stop_smoking", DUMMY_CODE)


def _script_keep_old_active_conditions(record: HealthRecord) -> None:
    record.encounter_start(TIME - years(10), EncounterType.WELLNESS)
    record.condition_start(TIME - years(10), "fakitis")
    record.condition_end(TIME - years(8), "fakitis")
    record.encounter_start(TIME - years(10), EncounterType.WELLNESS)
    record.condition_start(TIME - years(10), "fakosis")


def _script_condition_ended_during_target(record: HealthRecord) -> None:
    record.encounter_start(TIME - years(10), EncounterType.WELLNESS)
    record.condition_start(TIME - years(10), "boneitis")
    record.condition_end(TIME - years(2), "boneitis")
    record.encounter_start(TIME - years(10), EncounterType.WELLNESS)
    record.condition_start(TIME - years(10), "smallpox")
    record.condition_end(TIME - years(9), "smallpox")


def _script_not_keep_old_stuff(record: HealthRecord) -> None:
    record.encounter_start(TIME - years(18), EncounterType.EMERGENCY)
    record.procedure(TIME - years(20), "appendectomy")
    record.immunization(TIME - years(12), "flu_shot")
    record.observation(TIME - years(10), "weight", 123)


def _script_keep_old_active_stuff(record: HealthRecord) -> None:
    record.encounter_start(TIME - years(18), EncounterType.EMERGENCY)
    record.condition_start(TIME - years(18), "diabetes")


def _script_filter_claim_items(record: HealthRecord) -> None:
    record.encounter_start(TIME - years(10), EncounterType.EMERGENCY)
    record.condition_start(TIME - years(10), "something_permanent")
    record.procedure(TIME - years(10), "xray")


def _script_not_keep_old_same_type(record: HealthRecord) -> None:
    one_week = Utilities.convert_time("weeks", 1)
    for i in range(3):
        record.encounter_start(TIME - years(10 - i), EncounterType.EMERGENCY)
        record.condition_start(TIME - years(10 - i), "viral_sinusitis")
        record.condition_end(TIME - years(10 - i) + one_week, "viral_sinusitis")
    record.encounter_start(TIME - one_week, EncounterType.EMERGENCY)
    record.condition_start(TIME - one_week, "viral_sinusitis")


def _script_future_entries(record: HealthRecord) -> None:
    record.encounter_start(TIME - years(1), EncounterType.WELLNESS)
    record.observation(TIME + 1000, "future_obs", 1)
    record.encounter_start(TIME - years(10), EncounterType.WELLNESS)
    condition = record.condition_start(TIME - years(10), "long_condition")
    condition.stop = TIME + years(5)
    record.encounter_start(TIME - years(10), EncounterType.WELLNESS)
    record.allergy_start(TIME - years(10), "peanuts")
    record.immunization(TIME - years(10), "flu_shot")


def _script_cause_of_death(person: Person, record: HealthRecord) -> None:
    cause = Code("SNOMED-CT", "Todo-lookup-code", "Rabies")
    person.record_death(TIME - years(20), cause)
    DeathModule.process(person, TIME - years(20))


_FILTER_SCRIPTS: dict[str, Callable[[HealthRecord], None]] = {
    "simple_cutoff": _script_simple_cutoff,
    "keep_old_active_medication": _script_keep_old_active_medication,
    "medication_ended_during_target": _script_medication_ended_during_target,
    "keep_old_active_careplan": _script_keep_old_active_careplan,
    "careplan_ended_during_target": _script_careplan_ended_during_target,
    "keep_old_active_conditions": _script_keep_old_active_conditions,
    "condition_ended_during_target": _script_condition_ended_during_target,
    "not_keep_old_stuff": _script_not_keep_old_stuff,
    "keep_old_active_stuff": _script_keep_old_active_stuff,
    "filter_claim_items": _script_filter_claim_items,
    "not_keep_old_same_type": _script_not_keep_old_same_type,
    "future_entries": _script_future_entries,
}


def _filtered_dump(name: str) -> dict[str, object]:
    person, record = new_patient()
    if name == "keep_cause_of_death":
        _script_cause_of_death(person, record)
    else:
        _FILTER_SCRIPTS[name](record)
    filtered = Exporter.filter_for_export(person, YEARS, TIME)
    assert isinstance(filtered, Person)
    return dump_record(filtered.record)  # type: ignore[arg-type]


def test_filter_scenarios(golden: Callable[[str], Path]) -> None:
    results = []
    for case in by_case(load_cases(golden), "filter"):
        name = case["name"]  # type: ignore[assignment]
        if name == "keep_cause_of_death":
            result = run_or_pending(lambda name=name: _filtered_dump(name), ("T22",))
            results.append(result)
            if not isinstance(result, Pending):
                assert result == case["record"], name
        else:
            assert _filtered_dump(name) == case["record"], name
    report_pending("Exporter filter cause-of-death scenario", results)


def test_entry_within_time_range(golden: Callable[[str], Path]) -> None:
    _person, record = new_patient()
    cutoff = TIME - years(YEARS)
    for case in by_case(load_cases(golden), "entry_within_range"):
        start = int(case["start"])  # type: ignore[arg-type]
        entry = record.new_entry(lambda start=start: Entry(start, "x"))
        entry.stop = int(case["stop"])  # type: ignore[arg-type]
        result = Exporter.entry_within_time_range(entry, cutoff, TIME)
        assert result == case["result"]
        assert entry.stop == int(case["stop_after"])  # type: ignore[arg-type]


def test_filter_after_death(golden: Callable[[str], Path]) -> None:
    person, record = new_patient()
    death = TIME - 5000
    person.attributes[Person.DEATHDATE] = death
    record.encounter_start(death - 1000, EncounterType.WELLNESS)
    record.encounter_start(death + 1000, EncounterType.WELLNESS)
    cert = record.encounter_start(death + 2000, EncounterType.WELLNESS)
    cert.codes.append(DeathModule.DEATH_CERTIFICATION)
    Exporter.filter_after_death(person)
    for case in by_case(load_cases(golden), "filter_after_death"):
        assert [str(e.start) for e in record.encounters] == case["encounter_starts"]


def _set_all_exporter_flags_false() -> None:
    for flag in (
        "exporter.fhir_stu3.export",
        "exporter.fhir_dstu2.export",
        "exporter.fhir.export",
        "exporter.ccda.export",
        "exporter.json.export",
        "exporter.csv.export",
        "exporter.bfd.export",
        "exporter.cpcds.export",
        "exporter.text.export",
        "exporter.text.per_encounter_export",
        "exporter.symptoms.csv.export",
        "exporter.symptoms.text.export",
        "exporter.cdw.export",
        "exporter.clinical_note.export",
    ):
        Config.set(flag, "false")


@pytest.fixture
def config_snapshot() -> Callable[[], None]:
    saved = dict(Config.properties)

    def restore() -> None:
        Config.properties.clear()
        Config.properties.update(saved)

    return restore


def test_export_scenarios(
    golden: Callable[[str], Path], config_snapshot: Callable[[], None]
) -> None:
    try:
        _set_all_exporter_flags_false()
        cases = load_cases(golden)

        person, record = new_patient()
        record.encounter_start(TIME - years(8), EncounterType.WELLNESS)
        record.observation(TIME - years(8), "height", 64)
        options = ExporterRuntimeOptions()
        options.years_of_history = 0
        options.defer_exports = True
        result = Exporter.export(person, TIME, options)
        case = by_case(cases, "export_defer")[0]
        assert result == case["result"]
        assert len(Exporter.deferred_exports) == case["deferred_size"]
        assert len(record.encounters) == case["encounters"]
        Exporter.deferred_exports.clear()

        person, record = new_patient()
        record.encounter_start(TIME - years(8), EncounterType.WELLNESS)
        record.observation(TIME - years(8), "height", 64)
        options = ExporterRuntimeOptions()
        options.years_of_history = 0
        result = Exporter.export(person, TIME, options)
        case = by_case(cases, "export_plain")[0]
        assert result == case["result"]
        assert len(record.encounters) == case["encounters"]

        person, record = new_patient()
        death = TIME - 5000
        person.attributes[Person.DEATHDATE] = death
        record.encounter_start(death - 1000, EncounterType.WELLNESS)
        record.encounter_start(death + 1000, EncounterType.WELLNESS)
        options = ExporterRuntimeOptions()
        options.years_of_history = 0
        result = Exporter.export(person, TIME, options)
        case = by_case(cases, "export_after_death")[0]
        assert result == case["result"]
        assert len(record.encounters) == case["encounters"]

        person, record = new_patient()
        _script_simple_cutoff(record)
        options = ExporterRuntimeOptions()
        options.years_of_history = YEARS
        result = Exporter.export(person, TIME, options)
        case = by_case(cases, "export_filtered")[0]
        assert result == case["result"]
        assert dump_record(record) == case["record"]
    finally:
        config_snapshot()


def test_filename_and_output_folder(
    golden: Callable[[str], Path], tmp_path: Path, config_snapshot: Callable[[], None]
) -> None:
    try:
        cases = load_cases(golden)
        person, _record = new_patient()
        person.attributes[Person.NAME] = "Jane Q Public"
        person.attributes[Person.ID] = "abcdef-1234"
        for case in by_case(cases, "filename"):
            Config.set("exporter.use_uuid_filenames", "true" if case["uuid"] else "false")
            assert Exporter.filename(person, "", "json") == case["out"]
            assert Exporter.filename(person, "0", "json") == case["out_tagged"]
        base = tmp_path / "outbase"
        Config.set("exporter.baseDirectory", str(base))
        for case in by_case(cases, "output_folder"):
            Config.set(
                "exporter.subfolders_by_id_substring", "true" if case["subfolders"] else "false"
            )
            folder = Exporter.get_output_folder("csv", person if case["subfolders"] else None)
            assert str(folder.relative_to(base)) == case["out"]
    finally:
        config_snapshot()
