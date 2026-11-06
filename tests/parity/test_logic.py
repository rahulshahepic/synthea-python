"""Parity for LogicProbe: every Logic condition type used in the module JSON,
evaluated against 60 scripted persons, compared exactly.

This is *component* parity (PORTING_GUIDE §10): the Java probe runs the real
classes, while on the Python side Claim (T14) and CoverageRecord (T16) are
test doubles and State (T19) is a field-only double — see
tests/logic_support.py. The doubles supply only plumbing (claim line items,
coverage) and state fields that Logic/Person read; every value the results
depend on comes from the real T08 HealthRecord / T09 Person code.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest

import synthea.world.agents.person as person_module
import synthea.world.concepts.claim as claim_module
from synthea.engine.logic import Logic
from synthea.helpers.config import Config
from synthea.javacompat.collections import JavaConcurrentHashMap
from synthea.world.agents.person import Person
from synthea.world.concepts.health_record import (
    Allergy,
    CarePlan,
    Code,
    EncounterType,
    Entry,
    HealthRecord,
    Medication,
)
from synthea.world.concepts.health_record import (
    Observation as RecordObservation,
)
from synthea.world.concepts.vital_sign import VitalSign
from tests.logic_support import ClaimDouble, LogicStateDouble, build_logic
from tests.parity.person_doubles import CoverageRecordDouble

pytestmark = pytest.mark.parity

TIME = 1474416000000  # 2016-09-21 00:00:00 UTC, the LogicTest reference time

MMSE = Code("LOINC", "72107-6", "Mini Mental State Examination")
DIABETES = Code("SNOMED-CT", "73211009", "Diabetes mellitus")
ALZHEIMERS = Code("SNOMED-CT", "26929004", "Alzheimer's disease (disorder)")
PENICILLIN = Code("RxNorm", "7984", "Penicillin V")
MED_CODE = Code("RxNorm", "617314", "Metformin")
CAREPLAN_CODE = Code("SNOMED-CT", "698360004", "Diabetes self management plan")
MED_TYPE = "617314"
CAREPLAN_TYPE = "698360004"


@pytest.fixture(autouse=True)
def _doubles(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(person_module, "CoverageRecord", CoverageRecordDouble)
    monkeypatch.setattr(claim_module, "Claim", ClaimDouble)
    Config.set("exporter.split_records", "false")
    Config.set("exporter.split_records.duplicate_data", "false")


def _state(name: str, exited: int, entry: Entry | None = None) -> LogicStateDouble:
    return LogicStateDouble(name, entered=exited, exited=exited, entry=entry)


def scripted_person(i: int) -> Person:
    """Mirror of LogicProbe.scriptedPerson — identical index-driven script."""
    loss_of_care = i % 22 == 10 or i % 22 == 21
    if loss_of_care:
        Config.set("generate.payers.loss_of_care", "true")
    p = Person(i)
    if loss_of_care:
        Config.set("generate.payers.loss_of_care", "false")
    time = TIME
    p.attributes[Person.INCOME] = 10000000

    age_slot = i % 12
    if age_slot == 1:
        birth = time - (i % 24 + 1) * 2592000000  # 30-day "months"
    else:
        ages = [0, 0, 2, 5, 12, 17, 18, 35, 40, 41, 65, 90]
        birth = time - ages[age_slot] * 31557600000  # 365.25-day years
    p.attributes[Person.BIRTHDATE] = birth
    # Enrol in the no-insurance plan from birth, so Claim construction
    # (inside every Encounter/Medication) finds a plan record.
    p.coverage.set_plan_to_no_insurance(birth)
    # A base encounter so record.current_encounter(time) never has to create
    # one. It must not predate the birthdate: Claim construction requires a
    # plan record, and a not-yet-born person has no insurance history.
    assert p.record is not None
    p.record.encounter_start(max(time - 1000, birth), EncounterType.WELLNESS)

    if i % 3 == 0:
        p.attributes[Person.GENDER] = "M"
    elif i % 3 == 1:
        p.attributes[Person.GENDER] = "F"
    if i % 13 != 12:
        races = ["white", "black", "asian", "hispanic", "native", "other", "White", "WHITE"]
        p.attributes[Person.RACE] = races[i % 8]
    if i % 4 != 3:
        ses = ["High", "Middle", "Low"]
        p.attributes[Person.SOCIOECONOMIC_CATEGORY] = ses[i % 4]
    test_attribute = {
        1: "TestValue",
        2: "Wrong Value",
        3: 120,
        4: 100.5,
        5: True,
    }.get(i % 6)
    if test_attribute is not None:
        p.attributes["Test_Attribute_Key"] = test_attribute
    p.attributes["score"] = (i * 7) % 100

    pain = [0, 10, 50, 60, 80, 100]
    p.set_symptom("Module1", "Appendicitis", "PainLevel", time, pain[i % 6], False)
    if i % 3 == 0:
        p.set_symptom("Module2", "Appendicitis", "PainLevel", time, 30, False)
    if i % 4 == 0:
        p.set_symptom("Module1", "Appendicitis", "LackOfAppetite", time, 100, False)

    if i % 4 != 0:
        systolic = [0, 90, 120, 140]
        p.set_vital_sign(VitalSign.SYSTOLIC_BLOOD_PRESSURE, float(systolic[i % 4]))
    if i % 5 == 0:
        p.set_vital_sign(VitalSign.DIASTOLIC_BLOOD_PRESSURE, 80.0)

    mmse_slot = i % 4
    if mmse_slot != 0:
        mmse_values = [0, 12, 22, 29]
        obs = p.record.observation(time, MMSE.code, mmse_values[mmse_slot])
        obs.codes.append(MMSE)
    if i % 5 == 1:
        value_code = Code("LOINC", "72107-7" if i % 2 == 0 else "72107-8", "Some Observation Value")
        obs = p.record.observation(time, "99999-9", value_code)
        obs.codes.append(Code("LOINC", "99999-9", "Value Code Test"))
    if i % 3 == 0:
        obs = p.record.observation(time, "Glucose Panel", "12345")
        p.attributes["Diabetes Test Performed"] = obs
    if i % 3 == 1:
        obs = p.record.observation(time, "Blood Panel", "blah blah")
        p.attributes["Blood Test Performed"] = obs

    if i % 3 == 0:
        p.record.condition_start(time, DIABETES.code)
    if i % 3 == 1:
        p.record.condition_start(time, DIABETES.code)
        p.record.condition_end(time + 1000, DIABETES.code)
    if i % 4 == 0:
        cond = p.record.condition_start(time, ALZHEIMERS.code)
        p.attributes["Alzheimer's Variant"] = cond
    if i % 3 == 0:
        p.record.allergy_start(time, PENICILLIN.code)
    if i % 3 == 2:
        p.record.allergy_start(time, PENICILLIN.code)
        p.record.allergy_end(time + 1000, PENICILLIN.code)
    if i % 3 == 0:
        p.record.medication_start(time, MED_TYPE, False)
    if i % 3 == 1:
        p.record.medication_start(time, MED_TYPE, False)
        p.record.medication_end(time + 1000, MED_TYPE, Code("SNOMED-CT", "123", "reason"))
    if i % 5 == 0:
        med = p.record.medication_start(time, "555555", False)
        p.attributes["Current Medication"] = med
    if i % 3 == 0:
        cp = p.record.careplan_start(time, CAREPLAN_TYPE)
        cp.codes.append(CAREPLAN_CODE)
    if i % 4 == 1:
        cp = p.record.careplan_start(time, CAREPLAN_TYPE)
        cp.codes.append(CAREPLAN_CODE)
        p.attributes["Angina_CarePlan"] = cp

    history: list[LogicStateDouble] = []
    shape = i % 4
    if shape == 1:
        history.append(_state("CarePlan", time))
    elif shape == 2:
        history.append(_state("DoctorVisit", time))
        history.append(_state("CarePlan", time))
    elif shape == 3:
        history.append(_state("CarePlan", time))
        history.append(_state("DoctorVisit", time - 2 * 31557600000))
        history.append(_state("CarePlan", time - 5 * 31557600000))
    p.history = history  # type: ignore[assignment]

    if i % 7 == 6:
        # Split records: the current record is fresh (switched provider), and
        # the earlier entries survive only in the module history.
        p.has_multiple_records = True
        p.records = JavaConcurrentHashMap()
        record = p.record
        condition = record.new_entry(lambda: Entry(time, DIABETES.code))
        condition.codes.append(DIABETES)
        obs_entry = record.new_entry(lambda: RecordObservation(time, MMSE.code, 25))
        obs_entry.codes.append(MMSE)
        med_entry = record.new_entry(lambda: Medication(time, MED_TYPE))
        med_entry.codes.append(MED_CODE)
        cp_entry = record.new_entry(lambda: CarePlan(time, CAREPLAN_TYPE))
        cp_entry.codes.append(CAREPLAN_CODE)
        allergy_entry = record.new_entry(lambda: Allergy(time, PENICILLIN.code))
        allergy_entry.codes.append(PENICILLIN)
        split_states = [
            _state("ConditionState", time, condition),
            _state("ObservationState", time, obs_entry),
            _state("MedicationState", time, med_entry),
            _state("CarePlanState", time, cp_entry),
            _state("AllergyState", time, allergy_entry),
        ]
        history[0:0] = split_states
        p.record = HealthRecord(p)
        p.record.encounter_start(max(time - 1000, birth), EncounterType.WELLNESS)

    if loss_of_care:
        # The current record is fresh; the panel observation lives only in the
        # loss-of-care record (i % 22 == 10) or the default record (== 21).
        p.record = HealthRecord(p)
        p.record.encounter_start(max(time - 1000, birth), EncounterType.WELLNESS)
        if i % 22 == 10:
            assert p.loss_of_care_record is not None
            p.loss_of_care_record.encounter_start(max(time - 1000, birth), EncounterType.WELLNESS)
            obs = p.loss_of_care_record.observation(time, "88888-8", 33)
            obs.codes.append(Code("LOINC", "88888-8", "Loss Panel"))
        else:
            assert p.default_record is not None
            obs = p.default_record.observation(time, "88888-8", 17)
            obs.codes.append(Code("LOINC", "88888-8", "Loss Panel"))
    return p


def _evaluate(logics: list[Logic], person: Person) -> str:
    results = []
    for logic in logics:
        try:
            results.append("T" if logic.test(person, TIME) else "F")
        except Exception:
            results.append("X")
    return "".join(results)


def test_logic_probe(golden: Callable[[str], Path]) -> None:
    golden_dir = golden("LogicProbe")
    definitions = json.loads((golden_dir / "definitions.json").read_text(encoding="utf-8"))
    logics = [build_logic(d) for d in definitions]

    expected = {}
    for line in (golden_dir / "logic.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        expected[row["case"]] = row["results"]

    for i in range(60):
        actual = _evaluate(logics, scripted_person(i))
        assert actual == expected[f"person:{i}"], f"person {i}"

    Config.set("exporter.split_records.duplicate_data", "true")
    try:
        for i in range(60):
            if i % 7 != 6:
                continue
            actual = _evaluate(logics, scripted_person(i))
            assert actual == expected[f"dup:{i}"], f"dup person {i}"
    finally:
        Config.set("exporter.split_records.duplicate_data", "false")
