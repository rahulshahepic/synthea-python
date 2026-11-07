"""Java: CSVExporterTest, CSVExporterNpiTest and CSVExporterClaimsTest assertions.

Use real scripted records because Generator (T27) is outside this task's dependencies.
"""

from __future__ import annotations

import csv
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from synthea.export.csv_exporter import ClaimTransaction, ClaimTransactionType, CSVExporter, _money
from synthea.helpers.config import Config
from synthea.world.agents.payer_manager import PayerManager
from synthea.world.agents.person import Person, Point2DDouble
from synthea.world.concepts.health_record import Code, EncounterType, Medication
from tests.parity.test_csv_exporter import BIRTH, TIME, scripted_population
from tests.parity.test_csv_exporter import csv_config as csv_config


def rows(directory: Path, resource: str) -> list[dict[str, str]]:
    """Java: SimpleCSV#parse on the emitted CSV, by its declared header names."""
    with (directory / "csv" / f"{resource}.csv").open(newline="") as stream:
        return list(csv.DictReader(stream))


def patient(seed: int = 0) -> Person:
    """Java: CSVExporterTest's explicit person fixture."""
    PayerManager.load_no_insurance()
    p = Person(seed)
    p.attributes.update(
        {
            Person.BIRTHDATE: BIRTH,
            Person.ID: f"person-{seed}",
            Person.INCOME: 0,
            Person.COORDINATE: Point2DDouble(0.0, 0.0),
        }
    )
    p.coverage.set_plan_to_no_insurance(BIRTH)
    p.coverage.get_last_plan_record().update_stop_time(TIME + 86400000)
    for metric in ("QALY", "DALY", "QOLS"):
        p.attributes[metric] = {}
    return p


def test_csv_exporter_secondary_payer_columns_and_member_references(csv_config: Path) -> None:
    """Java: CSVExporterClaimsTest and testClaimTransactionsReferenceExportedPayerTransitions."""
    scripted_population(CSVExporter.get_instance())
    claims = rows(csv_config, "claims")
    assert claims
    with_secondary = 0
    for claim in claims:
        if claim["SECONDARYPATIENTINSURANCEID"]:
            with_secondary += 1
            assert claim["STATUS1"] == claim["STATUS2"]
            assert claim["OUTSTANDING2"]
            assert claim["LASTBILLEDDATE2"]
            assert claim["HEALTHCARECLAIMTYPEID1"] == claim["HEALTHCARECLAIMTYPEID2"]
        else:
            assert claim["STATUS2"] == claim["OUTSTANDING2"] == claim["LASTBILLEDDATE2"] == ""
            assert claim["HEALTHCARECLAIMTYPEID2"] == "0"
    assert with_secondary > 0
    members = {(r["PATIENT"], r["MEMBERID"]) for r in rows(csv_config, "payer_transitions")}
    for transaction in rows(csv_config, "claims_transactions"):
        if transaction["PATIENTINSURANCEID"]:
            assert (transaction["PATIENTID"], transaction["PATIENTINSURANCEID"]) in members


def test_csv_exporter_npi(csv_config: Path) -> None:
    """Java: CSVExporterNpiTest#testOrganizationAndProviderNpiExport."""
    scripted_population(CSVExporter.get_instance())
    for resource in ("organizations", "providers"):
        records = rows(csv_config, resource)
        assert records
        for record in records:
            npi = record["NPI"]
            assert len(npi) == 10 and npi.isdigit()
            total = 24
            for i, char in enumerate(reversed(npi[:9])):
                digit = int(char) * (2 if i % 2 == 0 else 1)
                total += digit - 9 if digit >= 10 else digit
            assert int(npi[-1]) == (10 - total % 10) % 10


@pytest.mark.parametrize("enabled", [True, False])
def test_csv_exporter_quality_of_life(csv_config: Path, enabled: bool) -> None:
    """Java: testQualityOfLifeObservationsIncludedByDefault / CanBeExcluded."""
    if not enabled:
        Config.set("exporter.csv.include_quality_of_life_observations", "false")
    scripted_population(CSVExporter.get_instance())
    observations = rows(csv_config, "observations")
    clinical = [row for row in observations if row["CODE"] not in ("QALY", "DALY", "QOLS")]
    qol = [row for row in observations if row["CODE"] in ("QALY", "DALY", "QOLS")]
    assert clinical and all(row["ENCOUNTER"] for row in clinical)
    assert bool(qol) == enabled
    assert all(row["ENCOUNTER"] == "" for row in qol)


def test_csv_exporter_unset_stops(csv_config: Path) -> None:
    """Java: testClaimTransactionToDateEmptyWhenStopUnset and payer-transition equivalent."""
    p = patient()
    assert p.record is not None
    e = p.record.encounter_start(TIME, EncounterType.EMERGENCY)
    e.codes.append(Code("system", "code", "display"))
    med = p.record.new_entry(lambda: Medication(TIME, "medication"))
    med.codes.append(Code("system", "code", "display"))
    assert med.stop == 0
    t = ClaimTransaction(e, "encounter", med.claim, "claim", 0, med.claim.main_entry, p)
    t.type = ClaimTransactionType.CHARGE
    t.set_amount(med.claim.main_entry.cost)
    t.department_id, t.diagnosis_codes, t.transfer_type = "", [None] * 8, "p"
    from synthea.export.csv_constants import CSVConstants

    parsed = list(
        csv.DictReader((CSVConstants.CLAIM_TRANSACTION_HEADER_LINE + t.to_string()).splitlines())
    )
    assert len(parsed) == 1 and parsed[0]["TODATE"] == ""
    p.record.encounters.clear()
    p.coverage.get_last_plan_record().update_stop_time(0)
    CSVExporter.get_instance().export(p, TIME)
    assert rows(csv_config, "payer_transitions")[0]["END_DATE"] == ""


@pytest.mark.parametrize(
    "include,exclude",
    [
        ("patients.csv,medications.csv", "procedures.csv,observations.csv"),
        ("patients.csv,medications.csv", ""),
        ("", "patients.csv,medications.csv"),
        ("", ""),
    ],
)
def test_csv_exporter_file_selection_no_overlap(
    csv_config: Path, include: str, exclude: str
) -> None:
    """Java: CSVExporterTest#doesNotThrowWhen* configuration cases."""
    Config.set("exporter.csv.included_files", include)
    Config.set("exporter.csv.excluded_files", exclude)
    CSVExporter.get_instance().init()


def test_csv_exporter_file_selection_overlap(csv_config: Path) -> None:
    """Java: CSVExporterTest#throwsExceptionWhenFileIncludedAndExcluded."""
    Config.set("exporter.csv.included_files", "patients.csv,medications.csv")
    Config.set("exporter.csv.excluded_files", "medications.csv,procedures.csv")
    with pytest.raises(
        ValueError, match=r"cannot include and exclude the same file: medications\.csv"
    ):
        CSVExporter.get_instance().init()


@pytest.mark.parametrize("include,exclude", [("patients.csv", ""), ("", "patients.csv")])
def test_csv_exporter_includes_excludes(csv_config: Path, include: str, exclude: str) -> None:
    """Java: CSVExporterTest#testCSVExportIncludes / Excludes, via scripted population."""
    Config.set("exporter.csv.included_files", include)
    Config.set("exporter.csv.excluded_files", exclude)
    scripted_population(CSVExporter.get_instance())
    files = {file.name for file in (csv_config / "csv").iterdir()}
    if include:
        assert files == {"patients.csv"}
        assert len(rows(csv_config, "patients")) == 32
    else:
        assert "patients.csv" not in files
        assert "encounters.csv" in files


def test_csv_exporter_split_append_and_digits(csv_config: Path) -> None:
    """Java: testCSVExportMultipleFiles / AppendMultipleFiles / FileNumberDigits."""
    Config.set("exporter.csv.included_files", "patients.csv")
    Config.set("exporter.csv.max_lines_per_file", "2")
    Config.set("exporter.csv.file_number_digits", "3")
    exporter = CSVExporter.get_instance()
    for i in range(3):
        exporter.export(patient(i), TIME)
    assert sorted(p.name for p in (csv_config / "csv").iterdir()) == [
        "patients-001.csv",
        "patients-002.csv",
    ]
    Config.set("exporter.csv.append_mode", "true")
    exporter.init()
    for i in range(3, 5):
        exporter.export(patient(i), TIME)
    assert [len(rows(csv_config, f"patients-{i:03d}")) for i in (1, 2, 3)] == [2, 2, 1]
    assert not (csv_config / "csv" / "patients-004.csv").exists()


@pytest.mark.parametrize(
    "source,expected",
    [
        (None, ""),
        (" a,b\r\nc\rd\ne ", "a b c d e"),
        ("\u00a0x\u00a0", "\u00a0x\u00a0"),
        ("\x00\tvalue\x1f", "value"),
    ],
)
def test_csv_exporter_clean_java_trim(source: str | None, expected: str) -> None:
    """Java: CSVExporter#clean; preserve Unicode spaces Java trim does not remove."""
    assert CSVExporter.clean(source) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        ("1.005", "1.01"),
        ("-1.005", "-1.01"),
        ("0", "0.00"),
        ("99999999999999999999.995", "100000000000000000000.00"),
    ],
)
def test_csv_exporter_decimal_format(value: str, expected: str) -> None:
    """Java: Formatter BigDecimal uses decimal HALF_UP without a double conversion."""
    assert _money(Decimal(value)) == expected


def test_csv_exporter_qol_strict_cutoff_and_leap_birthday(csv_config: Path) -> None:
    """Java: Calendar YEAR normalization and strict before/after conditions."""
    p = patient()
    p.attributes[Person.BIRTHDATE] = int(datetime(2000, 2, 29, tzinfo=UTC).timestamp() * 1000)
    p.attributes["QALY"] = {2001: 0.5, 2004: 0.75}
    CSVExporter.get_instance().export_quality_of_life_observations(
        "person", p, datetime(2001, 3, 1, tzinfo=UTC)
    )
    CSVExporter.get_instance().file_manager.flush_writer("observations")
    result = rows(csv_config, "observations")
    assert len(result) == 1
    # Calendar's first normalization moved the birthday to March 1, retained in the next year.
    assert result[0]["DATE"] == "2004-03-01T00:00:00Z"
