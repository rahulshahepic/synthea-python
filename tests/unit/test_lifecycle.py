"""Java: LifecycleModuleTest, with deterministic dates and exact Java probe expectations."""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from pathlib import Path

import pytest

from synthea.javacompat.numbers import double_to_string
from synthea.modules.blood_pressure_value_generator import BloodPressureValueGenerator, SysDias
from synthea.modules.lifecycle_module import LifecycleModule
from synthea.world.agents.person import Person
from synthea.world.concepts.health_record import Code, Entry
from synthea.world.concepts.vital_sign import VitalSign
from synthea.world.geography.location import Location
from tests.parity.test_lifecycle import BIRTH, newborn
from tests.parity.test_lifecycle import lifecycle_config as lifecycle_config
from tests.parity.test_lifecycle import module_constructor_double as module_constructor_double

TIME = 1577836800000


def test_lifecycle_death_by_natural_causes(lifecycle_config: None) -> None:
    """Java: LifecycleModuleTest#testDeathByNaturalCauses; same 100000 trials, fixed date."""
    LifecycleModule.ENABLE_DEATH_BY_NATURAL_CAUSES = True
    p = Person(0)
    p.attributes[Person.BIRTHDATE] = BIRTH
    for _ in range(100000):
        LifecycleModule.death(p, TIME)
    assert not p.alive(TIME)
    assert p.attributes[LifecycleModule.DAYS_UNTIL_DEATH] == 0


def test_lifecycle_likelihood_of_death_inputs(lifecycle_config: None) -> None:
    """Java: LifecycleModuleTest#testLikelihoodOfDeathInputs."""
    assert all(LifecycleModule.likelihood_of_death(age) >= 0 for age in range(100))


def test_lifecycle_adherence_fade(lifecycle_config: None) -> None:
    """Java: LifecycleModuleTest#testAdherenceFade, including its baseline clamp."""
    p = Person(0)
    p.attributes[Person.ADHERENCE] = True
    p.attributes[LifecycleModule.ADHERENCE_PROBABILITY] = 1.0
    for _ in range(5):
        before = p.attributes[LifecycleModule.ADHERENCE_PROBABILITY]
        LifecycleModule.adherence(p, TIME)
        assert p.attributes[LifecycleModule.ADHERENCE_PROBABILITY] < before
    p.attributes[LifecycleModule.ADHERENCE_PROBABILITY] = 0.001
    LifecycleModule.adherence(p, TIME)
    assert p.attributes[LifecycleModule.ADHERENCE_PROBABILITY] == 0.05


def test_lifecycle_upstream_growth_chart_inputs(golden: Callable[[str], Path]) -> None:
    """Java: testPercentileForBMI / lookupGrowthChart / lookupHeadCircumference, exact goldens."""
    expected = json.loads((golden("LifecycleProbe") / "scalars.json").read_text())
    assert (
        double_to_string(LifecycleModule.percentile_for_bmi(18.37736191, "M", 26))
        == expected["bmi_percentile"]
    )
    assert (
        double_to_string(LifecycleModule.lookup_growth_chart("height", "M", 24, 0.5))
        == expected["height"]
    )
    assert (
        double_to_string(LifecycleModule.lookup_growth_chart("head", "F", 36, 0.9))
        == expected["head"]
    )
    for invalid in ("HEIGHT", "unknown", ""):
        with pytest.raises(ValueError, match="Unknown chart type"):
            LifecycleModule.lookup_growth_chart(invalid, "M", 24, 0.5)


def test_lifecycle_physiology_enabled_out_of_scope(lifecycle_config: None) -> None:
    """Java: testPhysiologyEnabled; issue #21 explicitly excludes physiology generators."""
    LifecycleModule.ENABLE_PHYSIOLOGY_GENERATORS = True
    with pytest.raises(NotImplementedError, match="out of scope"):
        newborn(0, 0)


def test_lifecycle_passport_format(lifecycle_config: None) -> None:
    """Java: testPassportFormatIsAlwaysEightDigits; age 20 may issue a passport.

    Java formats a passport as 'X' + 8 digits + 'X' (Passport.MAX_PASSPORT =
    10**8 - 1); the RIF identifier classes are not ported, so LifecycleModule
    formats the value inline.
    """
    p = newborn(0, 0)
    del p.attributes[Person.IDENTIFIER_PASSPORT]
    # Repeated age-20 calls eventually take Java's issuance branch; no fake seed-specific path.
    birthday = -1577836800000  # 1920-01-01
    for _ in range(100):
        LifecycleModule.age(p, birthday)
        passport = p.attributes.get(Person.IDENTIFIER_PASSPORT)
        if passport is not None:
            assert re.fullmatch(r"X\d{8}X", str(passport))
            break
    else:
        pytest.fail("No passport issuance branch reached")


@pytest.mark.parametrize("kind", list(SysDias))
def test_lifecycle_bp_single_time_cache(lifecycle_config: None, kind: SysDias) -> None:
    """Java: BloodPressureValueGenerator#getValue; cache calls must not consume RNG."""
    p = newborn(42, 0)
    bp = BloodPressureValueGenerator(p, kind)
    first = bp.get_value(TIME)
    count = p.get_count()
    assert bp.get_value(TIME) == first
    assert p.get_count() == count
    bp.get_value(TIME + 1)
    assert p.get_count() > count
    previous = p.get_count()
    bp.get_value(TIME)
    assert p.get_count() > previous  # A -> B -> A is deliberately not a multi-value cache


def test_lifecycle_bp_baseline_cache_key(lifecycle_config: None) -> None:
    """Java: calculateBaseline caches hypertension status and SysDias, but not severity."""
    p = newborn(42, 0)
    bp = BloodPressureValueGenerator(p, SysDias.SYSTOLIC)
    p.attributes["hypertension"] = True
    first = bp.calculate_baseline(p)
    count = p.get_count()
    p.attributes["hypertension_severe"] = True
    assert bp.calculate_baseline(p) == first
    assert p.get_count() == count
    p.attributes["hypertension"] = False
    bp.calculate_baseline(p)
    assert p.get_count() > count
    assert "bp_baseline_true_SYSTOLIC" in p.attributes
    assert "bp_baseline_false_SYSTOLIC" in p.attributes


def test_lifecycle_bp_careplan_curve(lifecycle_config: None) -> None:
    """Java: getLifestyleImpacts; before, halfway, full-year, stopped and non-adherent."""
    p = newborn(42, 0)
    assert p.record is not None
    from synthea.world.concepts.health_record import CarePlan

    cp = p.record.new_entry(lambda: CarePlan(TIME, "443402002"))
    p.record.present["443402002"] = cp
    p.attributes["htn_trial_443402002_careplan_adherent"] = True
    bp = BloodPressureValueGenerator(p, SysDias.SYSTOLIC)
    assert bp.get_lifestyle_impacts(p, 150.0, TIME - 1) == 0.0
    assert bp.get_lifestyle_impacts(p, 150.0, TIME + bp.ONE_YEAR // 2) == -7.0
    assert bp.get_lifestyle_impacts(p, 150.0, TIME + bp.ONE_YEAR) == -14.0
    assert bp.get_lifestyle_impacts(p, 150.0, TIME + bp.ONE_YEAR + 1) == -14.0
    cp.stop = TIME + 1
    assert bp.get_lifestyle_impacts(p, 150.0, TIME + bp.ONE_YEAR) == 0.0
    cp.stop = 0
    p.attributes["htn_trial_443402002_careplan_adherent"] = False
    assert bp.get_lifestyle_impacts(p, 150.0, TIME + bp.ONE_YEAR) == 0.0


def test_lifecycle_weight_length_stale_attribute(lifecycle_config: None) -> None:
    """Java: setCurrentWeightForLengthPercentile keeps the old attribute after 36 months."""
    p = newborn(42, 0)
    key = Person.CURRENT_WEIGHT_LENGTH_PERCENTILE
    value = p.attributes[key]
    LifecycleModule.set_current_weight_for_length_percentile(p, TIME)
    assert p.attributes[key] == value


@pytest.mark.parametrize(
    "bmi,expected", [(20.0, 6.6), (27.0, 6.6), (40.0, 10.0), (48.0, 12.0), (49.0, 12.0)]
)
def test_lifecycle_diabetic_hba1c_bounds(bmi: float, expected: float) -> None:
    """Java: estimateHbA1c diabetes is deterministic and consumes no RNG."""
    p = Person(0)
    count = p.get_count()
    assert LifecycleModule.estimate_hb_a1c(bmi, True, True, p) == expected
    assert p.get_count() == count


def test_lifecycle_creatinine_fallback_and_clamp(lifecycle_config: None) -> None:
    """Java: reverseCalculateCreatinine handles missing weight and clamps clearance."""
    p = Person(0)
    p.attributes.update({Person.BIRTHDATE: BIRTH, Person.GENDER: "F"})
    assert LifecycleModule.reverse_calculate_creatinine(p, 50.0, TIME) == 1.0
    p.set_vital_sign(VitalSign.WEIGHT, 60.0)
    assert LifecycleModule.reverse_calculate_creatinine(
        p, 0.0, TIME
    ) == LifecycleModule.reverse_calculate_creatinine(p, 1.0, TIME)
    assert LifecycleModule.reverse_calculate_creatinine(
        p, 101.0, TIME
    ) == LifecycleModule.reverse_calculate_creatinine(p, 100.0, TIME)


def test_lifecycle_disability_and_fall_interventions(
    lifecycle_config: None, module_constructor_double: None
) -> None:
    """Java: isDisabled, earliest diagnosis and three fall-risk interventions on real entries."""
    p = newborn(42, 0)
    assert p.record is not None
    assert not LifecycleModule.is_disabled(p, TIME)
    criteria = LifecycleModule.disabilityCriteria
    assert criteria is not None
    code = criteria.qualifying_codes[0]
    condition = p.record.new_entry(lambda: Entry(TIME - 1000, code))
    condition.codes.append(Code("SNOMED-CT", code, "qualifying"))
    p.record.present[code] = condition
    assert LifecycleModule.is_disabled(p, TIME)
    assert LifecycleModule.get_earliest_disability_diagnosis_time(p) == TIME - 1000
    for key in ("Physical therapy procedure", "Cholecalciferol 600 UNT", "Osteoporosis (disorder)"):
        p.record.present[key] = condition
    p.attributes["osteoporosis"] = True
    module = LifecycleModule()
    assert module.clone() is module
    module.calculate_fall_risk(p, TIME)
    assert p.attributes["probability_of_fall_injury"] == 0.06 * (1 - 0.02 * 3)
    p.attributes[Person.DEATHDATE] = TIME - 1
    count = p.get_count()
    assert module.process(p, TIME) is True
    assert p.get_count() == count


@pytest.mark.parametrize("language", ["english", "spanish"])
def test_lifecycle_birth_location(lifecycle_config: None, language: str) -> None:
    """Java: LifecycleModule#birth location, zip/FIPS and native/foreign birthplace branches."""
    p = Person(42)
    p.attributes.update(
        {
            Person.GENDER: "F",
            Person.RACE: "white",
            Person.ETHNICITY: "hispanic",
            Person.FIRST_LANGUAGE: language,
            Person.CITY: "Bedford",
            Person.LOCATION: Location("Massachusetts", "Bedford"),
        }
    )
    LifecycleModule.birth(p, BIRTH)
    assert p.attributes[Person.ZIP]
    assert len(p.attributes[Person.FIPS]) == 5
    assert all(
        p.attributes[key]
        for key in (Person.BIRTH_CITY, Person.BIRTH_STATE, Person.BIRTH_COUNTRY, Person.BIRTHPLACE)
    )
