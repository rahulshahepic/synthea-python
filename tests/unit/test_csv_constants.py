"""Unit tests for CSVConstants against the Java header lines."""

from __future__ import annotations

from synthea.export.csv_constants import CSVConstants

KEYS = [
    CSVConstants.PATIENT_KEY,
    CSVConstants.ALLERGY_KEY,
    CSVConstants.MEDICATION_KEY,
    CSVConstants.CONDITION_KEY,
    CSVConstants.CAREPLAN_KEY,
    CSVConstants.OBSERVATION_KEY,
    CSVConstants.PROCEDURE_KEY,
    CSVConstants.IMMUNIZATION_KEY,
    CSVConstants.ENCOUNTER_KEY,
    CSVConstants.IMAGING_STUDY_KEY,
    CSVConstants.DEVICE_KEY,
    CSVConstants.SUPPLY_KEY,
    CSVConstants.ORGANIZATION_KEY,
    CSVConstants.PROVIDER_KEY,
    CSVConstants.PAYER_KEY,
    CSVConstants.PAYER_TRANSITION_KEY,
    CSVConstants.CLAIM_KEY,
    CSVConstants.CLAIM_TRANSACTION_KEY,
    CSVConstants.PATIENT_EXPENSE_KEY,
]


def test_header_map_covers_all_keys() -> None:
    header_map = CSVConstants.initialize_header_map()
    assert set(header_map.keys()) == set(KEYS)
    assert len(header_map) == 19
    assert dict(header_map) == dict(CSVConstants.HEADER_LINE_MAP)


def test_headers_end_with_newline() -> None:
    assert CSVConstants.NEWLINE == "\n"
    for key in KEYS:
        assert CSVConstants.HEADER_LINE_MAP[key].endswith("\n"), key


def test_specific_headers() -> None:
    assert CSVConstants.PATIENT_HEADER_LINE.startswith("Id,BIRTHDATE,DEATHDATE,SSN,")
    assert CSVConstants.CONDITION_HEADER_LINE == (
        "START,STOP,PATIENT,ENCOUNTER,SYSTEM,CODE,DESCRIPTION\n"
    )
    assert CSVConstants.HEADER_LINE_MAP[CSVConstants.CLAIM_KEY].startswith(
        "Id,PATIENTID,PROVIDERID,PRIMARYPATIENTINSURANCEID,"
    )
    assert CSVConstants.HEADER_LINE_MAP[CSVConstants.PATIENT_EXPENSE_KEY] == (
        "PATIENT_ID,YEAR,PAYER_ID,HEALTHCARE_EXPENSES,INSURANCE_COSTS,COVERED_COSTS\n"
    )


def test_header_map_is_unmodifiable() -> None:
    import pytest

    with pytest.raises(TypeError):
        CSVConstants.HEADER_LINE_MAP["x"] = "y"  # type: ignore[index]
