"""Component parity for Person / ExpressedSymptom / ExpressedConditionRecord.

Mirrors PersonProbe scenario for scenario and compares the canonical dump
exactly. This is *component* parity (PORTING_GUIDE §10): Person's production
code calls its real collaborators, but CoverageRecord (T16), Provider (T13)
and State (T19) have not merged yet, and a real HealthRecord Encounter
cannot be constructed until Claim (T14) lands, so tests/parity/
person_doubles.py stand in for them, supplying only the state Person reads
or writes. Doubles used: HealthRecordDouble, CoverageRecordDouble,
ProviderDouble, StateDouble, CodeDouble.
"""

from __future__ import annotations

import importlib.util
import json
from collections.abc import Callable
from pathlib import Path

import pytest

import synthea.world.agents.person as person_module
from synthea.helpers.config import Config
from synthea.helpers.value_generator import ValueGenerator
from synthea.javacompat.collections import JavaHashMap
from synthea.javacompat.numbers import double_to_string
from synthea.modules.quality_of_life_module import QualityOfLifeModule
from synthea.world.agents.person import Person
from synthea.world.concepts.health_record import EncounterType
from synthea.world.concepts.vital_sign import VitalSign
from tests.parity.person_doubles import (
    CodeDouble,
    CoverageRecordDouble,
    HealthRecordDouble,
    ProviderDouble,
    StateDouble,
)

_spec = importlib.util.spec_from_file_location(
    "canonical_person", Path(__file__).parent / "canonical" / "person.py"
)
assert _spec is not None and _spec.loader is not None
canonical = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(canonical)


class FixedValueGenerator(ValueGenerator):
    """Java: PersonProbe.FixedValueGenerator (a fixed-value ValueGenerator)."""

    def __init__(self, person: Person, value: float) -> None:
        """Java: FixedValueGenerator(Person, double)."""
        super().__init__(person)
        self._value = value

    def get_value(self, time: int) -> float:
        """Java: FixedValueGenerator#getValue(long)."""
        return self._value


def _b(value: bool) -> str:
    """Java: Boolean.toString."""
    return "true" if value else "false"


def _n(value: object) -> str:
    """Java: String.valueOf for a nullable Long."""
    return "null" if value is None else str(value)


def _rng(out: dict[str, str], seed: int) -> None:
    p = Person(seed)
    lines = [
        f"rand={double_to_string(p.rand())}",
        f"rand={double_to_string(p.rand())}",
        f"randInt={p.rand_int()}",
        f"randInt(100)={p.rand_int(100)}",
        f"randGaussian={double_to_string(p.rand_gaussian())}",
        f"randLong={p.rand_long()}",
        f"randBoolean={_b(p.rand_boolean())}",
        f"randUUID={p.rand_uuid()}",
        # The probe calls the RandomNumberGenerator interface defaults
        # rand(double, double) and rand(double[]) on the Java Person; those
        # defaults live on T01's DefaultRandomNumberGenerator in the port
        # (Person#rand itself is arity-0), and the draws are identical.
        f"randRange={double_to_string(p.random.rand(2.0, 3.0))}",
        f"randArray={double_to_string(p.random.rand([5.0, 6.0]))}",
        f"count={p.get_count()}",
        f"seed={p.get_seed()}",
    ]
    out[f"rng:{seed}"] = "\n".join(lines) + "\n---\n" + canonical.dump(p)


def _age_log(p: Person, times: list[int]) -> str:
    log = ""
    for t in times:
        log += (
            f"t={t} period={p.age(t)} years={p.age_in_years(t)}"
            f" months={p.age_in_months(t)} dec={double_to_string(p.age_in_decimal_years(t))}"
            f" alive={_b(p.alive(t))}\n"
        )
    return log + "---\n" + canonical.dump(p)


def _age(out: dict[str, str], seed: int) -> None:
    p = Person(seed)
    birth = 631152000000 + seed * 31536000000 + seed * 86400000
    p.attributes[Person.BIRTHDATE] = birth
    times = [
        birth - 86400000,
        birth,
        birth + 86400000,
        birth + 568036800000,
        birth + 1234567890000,
        1767225600000,
    ]
    out[f"age:{seed}"] = _age_log(p, times)


def _age_edges(out: dict[str, str]) -> None:
    leap = Person(999)
    leap.attributes[Person.BIRTHDATE] = 1709164800000
    out["age-edge:leap"] = _age_log(
        leap, [1709251200000, 1740700800000, 1740787200000, 1835395200000]
    )
    month_end = Person(998)
    month_end.attributes[Person.BIRTHDATE] = 1738281600000
    out["age-edge:month-end"] = _age_log(month_end, [1738368000000, 1740700800000, 1743379200000])
    pre_epoch = Person(997)
    pre_epoch.attributes[Person.BIRTHDATE] = -126230400000
    out["age-edge:pre-epoch"] = _age_log(pre_epoch, [-126316800000, 0, 126230400000])
    no_birth = Person(996)
    out["age-edge:none"] = _age_log(no_birth, [1700000000000])


def _symptoms(out: dict[str, str], seed: int) -> None:
    p = Person(seed)
    modules = ["modA", "modB"]
    for i in range(6):
        module = modules[i % 2]
        type_name = "fever" if i % 3 == 0 else "pain"
        time = 1000000 + i * 100000 + seed
        value = (seed * 7 + i * 30) % 120
        p.set_symptom(module, f"cause{i}", type_name, time, value, i == 4)
    record = p.get_onset_condition_record()
    lines = [
        f"pain={p.get_symptom('pain')}",
        f"fever={p.get_symptom('fever')}",
        f"missing={p.get_symptom('missing')}",
        f"symptoms=[{', '.join(p.get_symptoms())}]",
        f"total={p.symptom_total()}",
        f"lastPainModA={_n(p.get_symptom_last_updated_time('modA', 'pain'))}",
        f"lastPainModX={_n(p.get_symptom_last_updated_time('modX', 'pain'))}",
    ]
    record.on_condition_onset("modA", "stateA", "diabetes", 900000 + seed)
    record.on_condition_onset("modA", "stateA2", "diabetes", 1500000 + seed)
    record.on_condition_end("modA", "diabetes", 1800000 + seed)
    record.on_condition_onset("modB", "stateB", "asthma", 1100000 + seed)
    onset = record.get_condition_last_onset_time_from_module("modA", "diabetes")
    lines.append(f"onsetDiabetesModA={_n(onset)}")
    end = record.get_condition_last_end_time_from_module("modA", "diabetes")
    lines.append(f"endDiabetesModA={_n(end)}")
    lines.append(f"fromState={_n(record.get_condition_from_state('modA', 'stateA2'))}")
    lines.append(f"fromStateMissing={_n(record.get_condition_from_state('modX', 'stateA'))}")
    p.address_largest_symptom()
    lines.append(f"painAfterAddress={p.get_symptom('pain')}")
    lines.append(f"totalAfterAddress={p.symptom_total()}")
    out[f"symptoms:{seed}"] = "\n".join(lines) + "\n---\n" + canonical.dump(p)


def _vitals(out: dict[str, str], seed: int) -> None:
    p = Person(seed)
    p.set_vital_sign(VitalSign.HEART_RATE, 60.0 + seed)
    p.set_vital_sign(VitalSign.HEIGHT, 170.04)
    p.set_vital_sign(VitalSign.WEIGHT, 65.25)
    p.set_vital_sign(VitalSign.BMI, 22.005)
    p.set_vital_sign(VitalSign.SYSTOLIC_BLOOD_PRESSURE, 120.49)
    p.set_vital_sign(VitalSign.DIASTOLIC_BLOOD_PRESSURE, 80.5)
    t = 123456789
    log = ""
    for vs in (
        VitalSign.HEART_RATE,
        VitalSign.HEIGHT,
        VitalSign.WEIGHT,
        VitalSign.BMI,
        VitalSign.SYSTOLIC_BLOOD_PRESSURE,
        VitalSign.DIASTOLIC_BLOOD_PRESSURE,
    ):
        log += f"{vs.name}={double_to_string(p.get_vital_sign(vs, t))}\n"
    try:
        p.get_vital_sign(VitalSign.RESPIRATION_RATE, t)
        log += "RESPIRATION_RATE=NO-ERROR\n"
    except TypeError:
        log += "RESPIRATION_RATE=ERR:NullPointerException\n"
    p.set_vital_sign(VitalSign.OXYGEN_SATURATION, FixedValueGenerator(p, float("nan")))
    oxygen = double_to_string(p.get_vital_sign(VitalSign.OXYGEN_SATURATION, t))
    log += f"OXYGEN_SATURATION={oxygen}\n"
    p.set_vital_sign(VitalSign.BLOOD_GLUCOSE, FixedValueGenerator(p, float("inf")))
    log += f"BLOOD_GLUCOSE={double_to_string(p.get_vital_sign(VitalSign.BLOOD_GLUCOSE, t))}"
    out[f"vitals:{seed}"] = log + "\n---\n" + canonical.dump(p)


def _records(out: dict[str, str], seed: int) -> None:
    Config.set("exporter.split_records", "true")
    try:
        p = Person(seed)
        p.attributes[Person.BIRTHDATE] = 1000000
        # Mirror of the probe: enrol at birth (age 0). Java's Claim
        # constructor (run for every Encounter) throws when no plan record
        # covers the encounter time; the double supplies only this plumbing.
        p.coverage.set_plan_to_no_insurance(1000000)  # type: ignore[attr-defined]
        p1 = ProviderDouble(f"prov-{seed}-a")
        p2 = ProviderDouble(f"prov-{seed}-b")
        p.set_provider(EncounterType.WELLNESS, p1)  # type: ignore[arg-type]
        e1 = p.encounter_start(5000000 + seed, EncounterType.WELLNESS)
        log = f"enc1: start={e1.start} type={e1.type} uuid={e1.uuid}\n"  # type: ignore[attr-defined]
        p.set_provider(EncounterType.AMBULATORY, p2)  # type: ignore[arg-type]
        e2 = p.encounter_start(6000000 + seed, EncounterType.AMBULATORY)
        log += f"enc2: start={e2.start} type={e2.type} uuid={e2.uuid}\n"  # type: ignore[attr-defined]
        log += f"providerCount={p.provider_count()}\n"
        active = p.record
        assert active is not None and active.provider is not None
        log += f"activeProvider={active.provider.get_resource_id()}\n"  # type: ignore[attr-defined]
        death = 7000000 + seed
        log += f"aliveBeforeDeath={_b(p.alive(death - 1))}\n"
        p.record_death(death, CodeDouble("SNOMED", "12345", "Test cause"))  # type: ignore[arg-type]
        log += f"aliveAtDeath={_b(p.alive(death))}\n"
        log += f"count={p.get_count()}"
        out[f"records:{seed}"] = log + "\n---\n" + canonical.dump(p)
    finally:
        Config.set("exporter.split_records", "false")


def _qol(out: dict[str, str], seed: int) -> None:
    p = Person(seed)
    qalys: JavaHashMap[int, float] = JavaHashMap()
    qalys[2019] = 0.5
    qalys[2020] = 0.25
    qalys[2021] = 1e16
    qalys[2022] = 1.0
    qalys[2023] = -1e16
    p.attributes[QualityOfLifeModule.QALY] = qalys
    dalys: JavaHashMap[int, float] = JavaHashMap()
    dalys[2020] = 2.0
    dalys[2021] = 3.5
    p.attributes[QualityOfLifeModule.DALY] = dalys
    qols: JavaHashMap[int, float] = JavaHashMap()
    qols[2019] = 0.9
    qols[2020] = 0.8
    p.attributes[QualityOfLifeModule.QOLS] = qols
    lines = [
        f"qalys={double_to_string(p.get_qalys())}",
        f"dalys={double_to_string(p.get_dalys())}",
        f"qols2019={double_to_string(p.get_qols_for_year(2019))}",
        f"qols2050={double_to_string(p.get_qols_for_year(2050))}",
    ]
    out[f"qol:{seed}"] = "\n".join(lines) + "\n---\n" + canonical.dump(p)


def _states(out: dict[str, str], seed: int) -> None:
    p = Person(seed)
    p.history = [  # type: ignore[list-item]
        StateDouble("A", 100),
        StateDouble("B", None),
        StateDouble("A", 50),
    ]
    lines = [
        f"priorA={_b(p.had_prior_state('A'))}",
        f"priorB={_b(p.had_prior_state('B'))}",
        f"priorC={_b(p.had_prior_state('C'))}",
        f"priorASinceB={_b(p.had_prior_state('A', 'B', None))}",
        f"priorAWithin75={_b(p.had_prior_state('A', None, 75))}",
        f"priorAWithin150={_b(p.had_prior_state('A', None, 150))}",
        f"priorBSinceA={_b(p.had_prior_state('B', 'A', None))}",
    ]
    out[f"states:{seed}"] = "\n".join(lines) + "\n---\n" + canonical.dump(p)


def _providers(out: dict[str, str], seed: int) -> None:
    p = Person(seed)
    lines = [f"reserve1={_b(p.reserve_current_encounter(1000, 'mod1'))}"]
    lines.append(f"reserve2={_b(p.reserve_current_encounter(1001, 'mod2'))}")
    lines.append(f"currentModule={_n(p.get_current_encounter_module())}")
    p.release_current_encounter(1002, "mod1")
    lines.append(f"hasAfterRelease={_b(p.has_current_encounter())}")
    p1 = ProviderDouble(f"cur-{seed}")
    p2 = ProviderDouble(f"cur2-{seed}")
    p.add_current_provider("ctx1", p1)  # type: ignore[arg-type]
    p.add_current_provider("ctx2", p2)  # type: ignore[arg-type]
    got1 = p.get_current_provider("ctx1")
    lines.append(f"currentCtx1={got1.get_resource_id() if got1 is not None else 'null'}")
    got2 = p.get_current_provider("ctx2")
    lines.append(f"currentCtx2={got2.get_resource_id() if got2 is not None else 'null'}")
    p.remove_current_provider("ctx1")
    lines.append(
        f"currentCtx1AfterRemove={'null' if p.get_current_provider('ctx1') is None else 'present'}"
    )
    p.attributes[Person.COORDINATE] = person_module.Point2DDouble(1.5, -2.25)
    lines.append(f"x={double_to_string(p.get_x())}")
    lines.append(f"y={double_to_string(p.get_y())}")
    lines.append(f"lonLat={canonical.render_value(p.get_lon_lat())}")
    out[f"providers:{seed}"] = "\n".join(lines) + "\n---\n" + canonical.dump(p)


@pytest.mark.parity
def test_person_component_probe(
    golden: Callable[[str], Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every PersonProbe case matches the Java canonical dump exactly (component)."""
    monkeypatch.setattr(person_module, "HealthRecord", HealthRecordDouble)
    monkeypatch.setattr(person_module, "CoverageRecord", CoverageRecordDouble)
    actual: dict[str, str] = {}
    for seed in range(25):
        _rng(actual, seed)
        _age(actual, seed)
        _symptoms(actual, seed)
        _vitals(actual, seed)
    _age_edges(actual)
    for seed in range(5):
        _records(actual, seed)
        _qol(actual, seed)
        _states(actual, seed)
        _providers(actual, seed)
    golden_path = golden("PersonProbe") / "person.jsonl"
    rows = [
        json.loads(line)
        for line in golden_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert [row["case"] for row in rows] == list(actual.keys())
    for row in rows:
        assert actual[row["case"]] == row["out"], row["case"]
