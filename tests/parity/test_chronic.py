"""Java: ChronicModulesProbe; exact component parity over 50 adult lifetimes."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import pytest

import tests.parity.canonical as canonical
from synthea.engine.module import Module
from synthea.helpers.config import Config
from synthea.helpers.utilities import Utilities
from synthea.javacompat.numbers import double_to_string
from synthea.modules.calculators.ascvd import ASCVD, Inventory
from synthea.modules.calculators.framingham import Framingham
from synthea.modules.cardiovascular_disease_module import CardiovascularDiseaseModule
from synthea.modules.quality_of_life_module import QualityOfLifeModule
from synthea.modules.weight_loss_module import WeightLossModule
from synthea.world.agents.payer_manager import PayerManager
from synthea.world.agents.person import Person
from synthea.world.concepts.bmi import BMI
from synthea.world.concepts.claim import Claim
from synthea.world.concepts.health_record import Code, Encounter, Entry, HealthRecord
from synthea.world.concepts.vital_sign import VitalSign
from tests.dependency_gate import pending_tasks
from tests.parity.canonical import dump_record
from tests.parity.canonical.chronic import claim
from tests.parity.canonical.person import render_value

WEEK = 604800000
pytestmark = pytest.mark.parity


def date(year: int) -> int:
    """Java: ChronicModulesProbe#date."""
    return int(datetime(year, 1, 1, tzinfo=UTC).timestamp() * 1000)


def person(i: int, birth: int) -> Person:
    """Java: ChronicModulesProbe#person, real collaborators with scripted inputs."""
    p = Person(230000 + i)
    p.attributes.update(
        {
            "birthdate": birth,
            "gender": "F" if i % 2 == 0 else "M",
            "race": "black" if i % 3 == 0 else "white",
            "income": 100000,
            "smoker": i % 3 == 1,
            "diabetes": i % 4 == 0,
            "hypertension": i % 5 == 0,
            "blood_pressure_controlled": i % 3 == 0,
            "left_ventricular_hypertrophy": i % 11 == 0,
            "coronary_heart_disease": i % 7 == 0,
        }
    )
    if i % 13 == 0:
        p.attributes["atrial_fibrillation"] = False
    return p


def vitals(p: Person, i: int) -> None:
    """Java: ChronicModulesProbe#vitals."""
    for sign, value in [
        (VitalSign.SYSTOLIC_BLOOD_PRESSURE, 95 + (i * 17) % 115),
        (VitalSign.DIASTOLIC_BLOOD_PRESSURE, 55 + (i * 13) % 65),
        (VitalSign.TOTAL_CHOLESTEROL, 110 + (i * 23) % 240),
        (VitalSign.HDL, 25 + (i * 7) % 65),
        (VitalSign.HEIGHT, 160 + i % 30),
        (VitalSign.WEIGHT, 75 + i % 65),
        (VitalSign.BMI, BMI.calculate(160 + i % 30, 75 + i % 65)),
    ]:
        p.set_vital_sign(sign, float(value))


def condition(record: HealthRecord, time: int, years: int, code: str) -> None:
    """Java: ChronicModulesProbe#condition, real entries/claims without care-seeking."""
    encounter = record.new_entry(lambda: Encounter(time, "wellness"))
    record.encounters.append(encounter)
    c = record.new_entry(lambda: Entry(time, code))
    c.codes.append(Code("SNOMED-CT", code, "Fixture condition"))
    if years > 0:
        c.stop = time + Utilities.convert_time("years", years)
    encounter.conditions.append(c)


def snapshot(p: Person, time: int) -> dict[str, object]:
    """Java: ChronicModulesProbe#snapshot; integer-year map order included explicitly."""
    assert p.default_record is not None
    return {
        "attributes": {key: render_value(value) for key, value in p.attributes.items()},
        "rng_count": str(p.get_count()),
        "vitals": {
            sign.name: double_to_string(p.get_vital_sign(sign, time)) for sign in p.vital_signs
        },
        "record": dump_record(p.default_record),
        "loss_record": None
        if p.loss_of_care_record is None
        else dump_record(p.loss_of_care_record),
        "year_order": {
            key: [str(year) for year in cast(dict[int, float], p.attributes[key])]
            for key in ("QALY", "DALY", "QOLS")
            if key in p.attributes
        },
    }


def chronic_module_constructor_double(
    self: Module, definition: object = None, submodule: object = None
) -> None:
    """Java: Module#Module() empty constructor plumbing, unmerged T19 component boundary."""
    assert definition is None and submodule is None


@pytest.fixture
def chronic_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Isolate configuration and payer initialization from other task fixtures."""
    monkeypatch.setattr(canonical, "_ENCODERS", dict(canonical._ENCODERS))
    canonical.register_encoder(Claim, claim)
    monkeypatch.setattr(Config, "properties", dict(Config.properties))
    Config.set("generate.timestep", str(WEEK))
    Config.set("generate.payers.loss_of_care", "false")
    monkeypatch.setattr(
        PayerManager, "noInsurance", getattr(PayerManager, "noInsurance", None), raising=False
    )
    monkeypatch.setattr(CardiovascularDiseaseModule, "useFramingham", False)
    PayerManager.load_no_insurance()


@pytest.fixture
def module_constructor_double(monkeypatch: pytest.MonkeyPatch) -> None:
    """Component-only constructor double; no module behavior is replaced."""
    if "T19" in pending_tasks():
        monkeypatch.setattr(Module, "__init__", chronic_module_constructor_double)


def adult(i: int) -> list[dict[str, object]]:
    """Java: ChronicModulesProbe#lifetime; all three real module behaviors, weekly."""
    Config.set("generate.payers.loss_of_care", str(i % 3 == 0).lower())
    birth, start, end = date(1920 + i), date(1940 + i), date(1982 + i)
    p = person(i, birth)
    vitals(p, i)
    p.coverage.set_plan_to_no_insurance(birth)
    p.coverage.get_last_plan_record().update_stop_time(end + WEEK)
    assert p.default_record is not None
    condition(p.default_record, start, 0, "44054006")
    condition(p.default_record, start, 15, "195967001")
    condition(p.default_record, start, 5, "192127007")
    if p.loss_of_care_enabled:
        assert p.loss_of_care_record is not None
        condition(p.loss_of_care_record, start, 0, "44054006")
    cardio, qol, weight = CardiovascularDiseaseModule(), QualityOfLifeModule(), WeightLossModule()
    CardiovascularDiseaseModule.useFramingham = i % 2 == 1
    rows = []
    year = -1
    for t in range(start, end, WEEK):
        if Utilities.get_year(t) != year:
            year = Utilities.get_year(t)
            if (year - (1940 + i)) % 9 == 0:
                p.attributes[WeightLossModule.TRIGGER_WEIGHT_LOSS] = True
        cardio.process(p, t)
        qol.process(p, t)
        weight.process(p, t)
        if t + WEEK >= end or Utilities.get_year(t + WEEK) != year:
            rows.append(snapshot(p, t))
    p.record_death(end, Code("SNOMED-CT", "12345", "Fixture death"))
    last = snapshot(p, end)
    last["cardio_stopped"] = cardio.process(p, end)
    last["weight_stopped"] = weight.process(p, end)
    qol.process(p, end)
    last["dead_qol"] = QualityOfLifeModule.calculate(p, end)
    rows.append(last)
    return rows


@pytest.mark.parametrize("i", range(50))
def test_chronic_component_adults(
    golden: Callable[[str], Path], chronic_config: None, module_constructor_double: None, i: int
) -> None:
    """Component parity: 50 seeded adults, 42 years each, all three module behaviors."""
    expected = json.loads((golden("ChronicModulesProbe") / f"adult_{i}.json").read_text())
    assert adult(i) == expected


def test_chronic_component_direct_risks(
    golden: Callable[[str], Path], chronic_config: None
) -> None:
    """Component parity: 2,400 direct inputs, five calculators, both conversion modes."""
    lines = (golden("ChronicModulesProbe") / "risks.jsonl").read_text().splitlines()
    assert len(lines) >= 1000
    functions = [
        ASCVD.ascvd10_year,
        Framingham.chd10_year,
        Framingham.cvd10_year,
        Framingham.atrial_fibrillation10_year,
        Framingham.stroke10_year,
    ]
    for i, line in enumerate(lines):
        age = 15 + i % 86
        p = person(i, date(2020 - age))
        vitals(p, i)
        values = [
            double_to_string(f(p, date(2020), per)) for per in (False, True) for f in functions
        ]
        assert values == json.loads(line), i


def test_chronic_component_inventory(golden: Callable[[str], Path]) -> None:
    """Java: combined T23 attribute inventory."""
    inventory: dict[str, Inventory] = {}
    for cls in (ASCVD, Framingham, CardiovascularDiseaseModule, QualityOfLifeModule):
        cls.inventory_attributes(inventory)
    actual = {
        key: {
            "read": {m: sorted(s) for m, s in v.read.items()},
            "write": {m: sorted(s) for m, s in v.write.items()},
            "exampleValues": sorted(v.example_values),
        }
        for key, v in inventory.items()
    }
    assert actual == json.loads((golden("ChronicModulesProbe") / "inventory.json").read_text())


def test_chronic_component_pediatric(
    golden: Callable[[str], Path], chronic_config: None, module_constructor_double: None
) -> None:
    """Exact parity: 250 pediatric adjustment, repeat, maintenance, regression and process cases."""
    from synthea.world.concepts.growth_chart import ChartType
    from synthea.world.concepts.pediatric_growth_trajectory import PediatricGrowthTrajectory

    chart = WeightLossModule.growthChart[ChartType.BMI]
    module = WeightLossModule()

    def trajectory(pgt: PediatricGrowthTrajectory) -> list[list[object]]:
        """Java: ChronicModulesProbe#trajectory, every point and full-precision BMI."""
        return [
            [point.age_in_months, str(point.time_in_simulation), double_to_string(point.bmi)]
            for point in pgt.trajectory
        ]

    cases = []
    for i in range(50):
        for action in range(5):
            birth, start = date(1990), date(1998 + i % 11)
            p = person(i, birth)
            gender = cast(str, p.attributes["gender"])
            p.attributes[WeightLossModule.WEIGHT_MANAGEMENT_START] = start
            p.attributes[WeightLossModule.WEIGHT_LOSS_BMI_PERCENTILE_CHANGE] = (
                0.01 + (i % 5) * 0.005
            )
            p.set_vital_sign(VitalSign.HEIGHT_PERCENTILE, 0.75)
            pgt = PediatricGrowthTrajectory(i, birth)
            before = start - Utilities.convert_time("months", 6)
            after = start + Utilities.convert_time("months", 1)
            before_age, after_age = p.age_in_months(before), p.age_in_months(after)
            pgt.add_point(before_age, before, chart.look_up(before_age, gender, 0.90))
            pgt.add_point(after_age, after, chart.look_up(after_age, gender, 0.90))
            p.attributes[Person.GROWTH_TRAJECTORY] = pgt
            row: dict[str, object] = {}
            if action == 0:
                module.adjust_bmi_vector_for_successful_management(p)
                row["first"] = trajectory(pgt)
                module.adjust_bmi_vector_for_successful_management(p)
            if action == 1:
                module.maintain_bmi_percentile(p, after + Utilities.convert_time("months", 1))
            if action == 2:
                module.adjust_bmi_vector_for_successful_management(p)
                module.pediatric_regression(p, start + Utilities.convert_time("years", 2))
            if action == 3:
                for year in range(1993, 2010):
                    pgt.current_bmi(p, date(year))
                row["weight"] = double_to_string(module.transition_regression(p, date(2010)))
            if action == 4:
                p.attributes[WeightLossModule.ACTIVE_WEIGHT_MANAGEMENT] = True
                p.attributes[WeightLossModule.WEIGHT_LOSS_ADHERENCE] = True
                p.attributes[WeightLossModule.LONG_TERM_WEIGHT_LOSS] = True
                module.process(p, start + Utilities.convert_time("months", 2))
            row["trajectory"] = trajectory(pgt)
            row["rng"] = str(p.get_count())
            cases.append(row)
    assert cases == json.loads((golden("ChronicModulesProbe") / "pediatric.json").read_text())
