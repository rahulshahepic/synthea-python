"""Java: CSVExporterProbe; integration parity for 32 real scripted persons, all CSVs."""

from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal
from pathlib import Path

import pytest

from synthea.export.csv_constants import CSVConstants
from synthea.export.csv_exporter import CSVExporter, SingletonHolder
from synthea.helpers.config import Config
from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.javacompat.collections import JavaHashMap
from synthea.world.agents.clinician import Clinician
from synthea.world.agents.payer import Payer
from synthea.world.agents.payer_manager import PayerManager
from synthea.world.agents.person import Person, Point2DDouble
from synthea.world.agents.provider import Provider
from synthea.world.concepts.claim import Claim
from synthea.world.concepts.health_record import (
    Code,
    EncounterType,
    Entry,
    ImagingStudy,
    Instance,
    Observation,
    ReactionSeverity,
    Series,
)
from synthea.world.concepts.healthinsurance.insurance_plan import InsurancePlan

BIRTH = -631152000000
TIME = 1577836800000


def code(value: str) -> Code:
    """Java: CSVExporterProbe#code."""
    return Code("SNOMED-CT", value, " Display,with\r\ncommas ")


def entry(item: Entry, value: str, i: int) -> None:
    """Java: CSVExporterProbe#entry; scripted inputs, never expected CSV values."""
    item.codes.append(code(value))
    item.stop = 0 if i % 2 == 0 else item.start + 60000
    item.cost = Decimal("123.45")


def plan(payer: Payer, identifier: int) -> InsurancePlan:
    """Java: CSVExporterProbe#plan."""
    result = InsurancePlan(
        identifier,
        payer,
        {"*"},
        Decimal("0.00"),
        Decimal("0.80"),
        Decimal("10.00"),
        Decimal("20.00"),
        Decimal("8700.00"),
        False,
        False,
        False,
        1900,
        2100,
        1,
        "GENERIC",
    )
    payer.add_plan(result)
    return result


def costs(claim: Claim, i: int) -> None:
    """Java: CSVExporterProbe#costs; directly scripted claim allocations."""
    for item in claim.items:
        item.cost = Decimal("123.45")
    item = claim.main_entry
    item.cost = Decimal("123.45")
    if i % 4 != 0:
        item.copay_paid_by_patient = Decimal("150.00" if i % 7 == 0 else "10.00")
        item.adjustment = Decimal("150.00" if i % 7 == 1 else "3.45")
        item.paid_by_payer = Decimal("40.00")
        item.coinsurance_paid_by_payer = Decimal("10.00")
        if i % 4 == 2:
            item.paid_by_secondary_payer = Decimal("20.00")
    claim.totals.reset()
    claim.totals.add_costs(item)
    for item in claim.items:
        claim.totals.add_costs(item)


@pytest.fixture
def csv_config(tmp_path: Path) -> object:
    """Java: CSVExporterTest#setUpExportDir; isolate global configuration and singleton."""
    keys = {
        "exporter.baseDirectory": str(tmp_path),
        "exporter.csv.folder_per_run": "false",
        "exporter.csv.append_mode": "false",
        "exporter.csv.included_files": "",
        "exporter.csv.excluded_files": "",
        "exporter.csv.max_lines_per_file": "0",
        "exporter.years_of_history": "0",
        "exporter.csv.include_quality_of_life_observations": "true",
    }
    old = {key: Config.get(key) for key in keys}
    previous = SingletonHolder.instance
    for key, value in keys.items():
        Config.set(key, value)
    SingletonHolder.instance = None
    yield tmp_path
    SingletonHolder.instance = previous
    for key, value in old.items():
        if value is None:
            Config.remove(key)
        else:
            Config.set(key, value)


def scripted_population(exporter: CSVExporter) -> list[Person]:
    """Java: CSVExporterProbe#main; same real API calls in the same RNG order."""
    PayerManager.clear()
    PayerManager.load_no_insurance()
    primary = Payer("Scripted Primary", 701, {"*"}, "PRIVATE")
    secondary = Payer("Scripted Secondary", 702, {"*"}, "PRIVATE")
    primary_plan, supplement = plan(primary, 701), plan(secondary, 702)
    org = Provider()
    org.uuid = "scripted-organization"
    org.name, org.address, org.city = " Hospital,Name ", " Road\r\nName ", "Boston"
    org.state, org.zip, org.phone, org.npi = "MA", "02110", "123", Provider.to_npi(123456789)
    org.add_revenue(1234.5)
    clinician = Clinician(42, DefaultRandomNumberGenerator(42), 123, org)
    clinician.attributes[Clinician.NAME] = " Doctor,Name "
    clinician.attributes[Person.COORDINATE] = Point2DDouble(-71.0, 42.0)
    people = []
    for i in range(32):
        p = Person(42 + i)
        p.attributes.update(
            {
                Person.ID: f"person-{i}",
                Person.BIRTHDATE: BIRTH,
                Person.FIRST_NAME: " First,Name ",
                Person.LAST_NAME: "Last\nName",
                Person.GENDER: "F" if i % 2 == 0 else "M",
                Person.INCOME: 45000 + i,
                Person.MARITAL_STATUS: "S",
                Person.COORDINATE: Point2DDouble(-71.0, 42.0),
            }
        )
        p.coverage.set_plan_to_no_insurance(BIRTH)
        while p.coverage.new_enrollment_period(TIME):
            pass
        p.coverage.set_plan_at_time(
            TIME,
            PayerManager.get_no_insurance_plan() if i % 4 == 0 else primary_plan,
            supplement if i % 4 == 2 else PayerManager.get_no_insurance_plan(),
        )
        pr = p.coverage.get_last_plan_record()
        pr.update_stop_time(TIME + 366 * 86400000)
        pr.increment_out_of_pocket_expenses(Decimal("12.34"))
        pr.increment_primary_coverage(Decimal("56.78"))
        for metric in ("QALY", "DALY", "QOLS"):
            values: JavaHashMap[int, float] = JavaHashMap()
            values[2000], values[2004] = 0.75, 1.005
            p.attributes[metric] = values
        record = p.record
        assert record is not None
        e = record.encounter_start(TIME, list(EncounterType)[i % len(EncounterType)])
        entry(e, "enc", i)
        if i % 3 != 0:
            e.provider, e.clinician = org, clinician
        org.institutional = i % 2 == 0
        c = record.condition_start(TIME, "condition")
        entry(c, "condition", i)
        if i % 2 == 0:
            e.reason = c.codes[0]
        a = record.allergy_start(TIME, "allergy")
        entry(a, "allergy", i)
        a.allergy_type, a.category, a.reactions = "allergy", "food", JavaHashMap()
        for j in range(i % 4):
            a.reactions[code(f"reaction-{j}")] = list(ReactionSeverity)[j]
        o = record.observation(TIME, "observation", 1.005 if i % 2 == 0 else "a,b\nc")
        o.codes.append(code("observation"))
        o.category, o.unit = "vital-signs", "mg"
        panel = record.observation(TIME, "panel", None)
        child = record.new_entry(lambda: Observation(TIME, "child", code("value")))
        child.codes.append(code("child"))
        panel.observations = [child]
        proc = record.procedure(TIME, "procedure")
        entry(proc, "procedure", i)
        if i % 2 == 0:
            proc.reasons.append(code("reason"))
        med = record.medication_start(TIME, "medication", False)
        entry(med, "medication", i)
        med.prescription_details = {}
        if i % 3 == 0:
            med.prescription_details["refills"] = i % 5
        elif i % 3 == 1:
            med.prescription_details["duration"] = {"quantity": 2, "unit": "days"}
        if i % 2 == 0:
            med.reasons.append(code("reason"))
        imm = record.immunization(TIME, "immunization")
        entry(imm, "immunization", i)
        care = record.careplan_start(TIME, "care")
        entry(care, "care", i)
        care.codes[0] = Code("SNOMED-CT", "care", "Care plan")
        if i % 2 == 0:
            care.reasons.append(code("reason"))
        study = record.new_entry(lambda p=p: ImagingStudy(p, TIME, "image"))
        study.codes.append(code("image"))
        for j in range(2):
            series = Series()
            series.dicom_uid = f"series-{j}"
            series.body_site, series.modality = (
                Code("SNOMED-CT", "body", "Body"),
                Code("DICOM", "CT", "CT"),
            )
            series.instances = []
            for k in range(2):
                inst = Instance()
                inst.dicom_uid, inst.sop_class = f"instance-{k}", Code("DICOM", "sop", "SOP")
                series.instances.append(inst)
            study.series.append(series)
        e.imaging_studies.append(study)
        dev = record.device_implant(TIME, "device")
        entry(dev, "device", i)
        dev.udi = "udi-123"
        record.use_supply(TIME, code("supply"), i + 1)
        costs(e.claim, i)
        costs(med.claim, i)
        if i % 5 == 0:
            p.attributes[Person.DEATHDATE] = TIME + 1
        if i == 0:
            pr.update_stop_time(0)
        if i % 4 == 0:
            e.conditions.clear()
            e.reason = None
        exporter.export(p, TIME if i % 3 == 0 else TIME + 86400000)
        exporter.export_patient(p, TIME)
        people.append(p)
    exporter.export_organization(org, 32)
    exporter.export_provider(clinician, org.uuid)
    for payer in (primary, secondary, PayerManager.get_no_insurance_plan().get_payer()):
        exporter.export_payer(payer)
    for key in CSVConstants.HEADER_LINE_MAP:
        exporter.file_manager.flush_writer(key)
    return people


@pytest.mark.parity
def test_csv_exporter_integration_all_files(
    golden: Callable[[str], Path], csv_config: Path
) -> None:
    """Every emitted CSV must match the Java probe byte-for-byte, including its file set."""
    expected = golden("CSVExporterProbe") / "csv"
    scripted_population(CSVExporter.get_instance())
    actual = csv_config / "csv"
    assert sorted(p.name for p in actual.iterdir()) == sorted(p.name for p in expected.iterdir())
    for file in sorted(expected.iterdir()):
        assert (actual / file.name).read_bytes() == file.read_bytes(), file.name
