"""Unit tests for ExportHelper statics and Exporter file/options plumbing.

Exact parity for these methods (including a broad input sweep) lives in
tests/parity/test_export_helper.py; these are small direct checks plus the
flag/warning/file behaviours that a probe cannot observe.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from synthea.export.export_helper import ExportHelper
from synthea.export.exporter import Exporter, ExporterRuntimeOptions, SupportedFhirVersion
from synthea.helpers.config import Config
from synthea.world.agents.person import Person
from tests.unit.test_health_record import person_double


@pytest.fixture(autouse=True)
def _config_snapshot() -> Iterator[None]:
    saved = dict(Config.properties)
    yield
    Config.properties.clear()
    Config.properties.update(saved)


def test_date_and_iso() -> None:
    assert ExportHelper.date_from_timestamp(1700000000000) == "2023-11-14"
    assert ExportHelper.iso8601_timestamp(1700000000000) == "2023-11-14T22:13:20Z"
    assert ExportHelper.date_from_timestamp(0) == "1970-01-01"
    assert ExportHelper.date_from_timestamp(-1) == "1969-12-31"


def test_next_friday() -> None:
    # 2023-11-14 is a Tuesday; next Friday is 2023-11-17, time of day kept.
    assert ExportHelper.next_friday(1700000000000) == 1700259200000
    # A Friday maps to the Friday of the following week.
    friday = 1700259200000
    assert ExportHelper.next_friday(friday) == friday + 7 * 86400000


def test_system_uri_round_trip() -> None:
    for name in (
        "SNOMED-CT",
        "LOINC",
        "RxNorm",
        "CVX",
        "DICOM-DCM",
        "CDT",
        "ICD9",
        "ICD10",
        "ICD10-CM",
        "CPT",
    ):
        assert ExportHelper.get_system_from_uri(ExportHelper.get_system_uri(name)) == name
    assert ExportHelper.get_system_uri("something-else") == "something-else"
    assert ExportHelper.get_system_from_uri("http://example.org") == "Unknown"


def test_build_uuid_deterministic_and_person_overload() -> None:
    from tests.parity.test_export_helper import new_patient

    a = ExportHelper.build_uuid(12345, 1700000000000, "Condition")
    b = ExportHelper.build_uuid(12345, 1700000000000, "Condition")
    assert a == b
    assert a != ExportHelper.build_uuid(12345, 1700000000000, "Other")
    person, _record = new_patient()
    assert ExportHelper.build_uuid(person, 1700000000000, "Condition") == a


def test_runtime_options_defaults_and_copy() -> None:
    Config.set("exporter.years_of_history", "7")
    options = ExporterRuntimeOptions()
    assert options.years_of_history == 7
    assert options.defer_exports is False
    assert options.terminology_service is False
    assert options.is_queue_enabled() is False
    assert options.is_record_queue_empty() is True
    assert options.get_next_record() is None

    options.enable_queue(SupportedFhirVersion.R4)
    assert options.is_queue_enabled() is True
    assert options.queued_fhir_version() == SupportedFhirVersion.R4
    assert options.is_record_queue_empty() is True

    copy = ExporterRuntimeOptions(options)
    assert copy.years_of_history == 7
    assert copy.is_queue_enabled() is True
    assert copy.queued_fhir_version() == SupportedFhirVersion.R4


def test_write_and_append_files(tmp_path: Path) -> None:
    target = tmp_path / "out.txt"
    Exporter.write_new_file(target, "first")
    assert target.read_text(encoding="utf-8") == "first\n"
    # CREATE_NEW: a second write to the same path fails in Java and is swallowed.
    Exporter.write_new_file(target, "second")
    assert target.read_text(encoding="utf-8") == "first\n"

    Exporter.overwrite_file(target, "overwritten")
    assert target.read_text(encoding="utf-8") == "overwritten\n"

    Exporter.append_to_file(target, "appended")
    Exporter.append_to_file(target, "again")
    Exporter.close_open_files()
    assert target.read_text(encoding="utf-8") == "overwritten\nappended\nagain\n"


def _export_test_person() -> Person:
    record, _rng = person_double(99)
    person = record.person
    person.record = record
    person.records = None
    person.has_multiple_records = False
    person.attributes[Person.BIRTHDATE] = 1000000000000
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
    Config.set("generate.terminology_service_url", "")
    return person


def test_fhir_flag_ignored_with_one_time_warning(capsys: pytest.CaptureFixture[str]) -> None:
    person = _export_test_person()
    Config.set("exporter.fhir.export", "true")
    Exporter._warned_ignored.clear()
    options = ExporterRuntimeOptions()
    options.years_of_history = 0
    assert Exporter.export(person, 1700000000000, options) is True
    assert Exporter.export(person, 1700000000000, options) is True
    err = capsys.readouterr().err
    assert err.count("exporter.fhir.export") == 1
    assert "ignored" in err


def test_non_csv_flag_raises_out_of_scope() -> None:
    person = _export_test_person()
    Config.set("exporter.ccda.export", "true")
    options = ExporterRuntimeOptions()
    options.years_of_history = 0
    with pytest.raises(NotImplementedError, match="out of scope"):
        Exporter.export(person, 1700000000000, options)


def test_load_code_mappers_empty() -> None:
    Exporter.load_code_mappers()
    assert Exporter.get_code_mappers() == {}
    assert Exporter.get_code_mapper("ICD10") is None
    Config.set("exporter.code_map.icd_10", "export/some_map.json")
    with pytest.raises(NotImplementedError, match="out of scope"):
        Exporter.load_code_mappers()


def test_load_custom_exporters_disabled_is_noop() -> None:
    Config.set("exporter.enable_custom_exporters", "false")
    Exporter.load_custom_exporters()
    assert Exporter.patient_exporters is None
    Config.set("exporter.enable_custom_exporters", "true")
    with pytest.raises(NotImplementedError, match="out of scope"):
        Exporter.load_custom_exporters()
