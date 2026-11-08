"""Java: FraminghamTest, QualityOfLifeTest and WeightLossModuleTest assertions."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import pytest

from synthea.javacompat.numbers import double_to_string
from synthea.modules.calculators.framingham import Framingham
from synthea.modules.quality_of_life_module import DisabilityWeight, QualityOfLifeModule
from synthea.modules.weight_loss_module import WeightLossModule
from synthea.world.agents.person import Person
from synthea.world.concepts.bmi import BMI
from synthea.world.concepts.growth_chart import ChartType
from synthea.world.concepts.pediatric_growth_trajectory import PediatricGrowthTrajectory
from synthea.world.concepts.vital_sign import VitalSign
from tests.parity.test_chronic import chronic_config as chronic_config
from tests.parity.test_chronic import condition, date, person
from tests.parity.test_chronic import module_constructor_double as module_constructor_double


def timestamp(y: int, m: int = 1, d: int = 1) -> int:
    """Java: TestHelper#timestamp fixed UTC dates."""
    return int(datetime(y, m, d, tzinfo=UTC).timestamp() * 1000)


@pytest.mark.parametrize(
    "age,gender,chol,hdl,sbp,treated,smoker,diabetic,expected",
    [
        (61, "F", 180, 47, 124, False, True, False, 0.1),
        (53, "M", 161, 55, 125, True, False, True, 0.156),
    ],
)
def test_framingham_model_patients(
    age: int,
    gender: str,
    chol: int,
    hdl: int,
    sbp: int,
    treated: bool,
    smoker: bool,
    diabetic: bool,
    expected: float,
) -> None:
    """Java: FraminghamTest#testCvdModelPatient1/2; exact lookup risk instead of tolerance."""
    p = person(1, date(2020 - age))
    p.attributes.update(
        {
            "gender": gender,
            "blood_pressure_controlled": treated,
            "smoker": smoker,
            "diabetes": diabetic,
        }
    )
    for sign, value in [
        (VitalSign.TOTAL_CHOLESTEROL, chol),
        (VitalSign.HDL, hdl),
        (VitalSign.SYSTOLIC_BLOOD_PRESSURE, sbp),
    ]:
        p.set_vital_sign(sign, float(value))
    assert Framingham.cvd10_year(p, date(2020), False) == expected


@pytest.fixture
def quality_person(chronic_config: None) -> Person:
    """Java: QualityOfLifeTest#init; same dated conditions, with real record/claim APIs."""
    p = Person(0)
    p.attributes[Person.BIRTHDATE] = 0
    p.attributes[Person.INCOME] = 1000000
    p.coverage.set_plan_to_no_insurance(0)
    p.coverage.get_last_plan_record().update_stop_time(int(365.25 * 40) * 86400000)
    assert p.default_record is not None
    for code, name, start, stop in [
        ("192127007", "Child attention deficit disorder", 10, 15),
        ("195967001", "Asthma", 10, 25),
        ("44054006", "Diabetes", 20, 0),
    ]:
        condition(p.default_record, int(365.25 * start) * 86400000, 0, code)
        entry = p.default_record.encounters[-1].conditions[0]
        entry.name = name
        if stop:
            entry.stop = (int(365.25 * stop) - 1) * 86400000
    return p


def test_quality_living_and_deceased(quality_person: Person) -> None:
    """Java: QualityOfLifeTest#testCalculateLiving/testCalculateDeceased."""
    stop = (int(365.25 * 35) + 1) * 86400000
    values = QualityOfLifeModule.calculate(quality_person, stop)
    assert 1.2 < values[0] < 1.3
    assert 33 < values[1] < 34
    quality_person.record_death(int(365.25 * 35) * 86400000, None)
    values = QualityOfLifeModule.calculate(quality_person, stop)
    assert 53 < values[0] < 54
    assert 33 < values[1] < 34


def test_quality_conditions_in_year(quality_person: Person) -> None:
    """Java: QualityOfLifeTest#testConditionsInYear."""
    assert quality_person.default_record is not None
    conditions = [c for e in quality_person.default_record.encounters for c in e.conditions]

    def names(year: int) -> list[str | None]:
        return [
            c.name
            for c in QualityOfLifeModule.conditions_in_year(
                conditions, int(365.25 * year) * 86400000, int(365.25 * (year + 1)) * 86400000
            )
        ]

    assert names(5) == []
    assert names(10) == ["Child attention deficit disorder", "Asthma"]
    assert names(30) == ["Diabetes"]


def test_quality_weight() -> None:
    """Java: QualityOfLifeTest#testWeight, original interval assertion."""
    assert 0.614 < QualityOfLifeModule.weight(0.45, 15) < 0.615


def thirty_year_old() -> Person:
    """Java: WeightLossModuleTest#thirtyYearOld."""
    p = Person(0)
    p.attributes.update(
        {
            Person.BIRTHDATE: date(1970),
            Person.GENDER: "M",
            WeightLossModule.WEIGHT_MANAGEMENT_START: date(2000),
            WeightLossModule.WEIGHT_LOSS_PERCENTAGE: 0.1,
            WeightLossModule.PRE_MANAGEMENT_WEIGHT: 136.0,
        }
    )
    for sign, value in [
        (VitalSign.WEIGHT_PERCENTILE, 0.9),
        (VitalSign.WEIGHT, 136.0),
        (VitalSign.HEIGHT, 175.0),
        (VitalSign.BMI, BMI.calculate(175, 136)),
    ]:
        p.set_vital_sign(sign, value)
    return p


@pytest.fixture
def weight_module(module_constructor_double: None) -> WeightLossModule:
    """Java: WeightLossModuleTest#before; only empty Module constructor is doubled."""
    return WeightLossModule()


def test_weight_management_periods(weight_module: WeightLossModule) -> None:
    """Java: WeightLossModuleTest#testFirstYearOfManagement/testFirstFiveYearsOfManagement."""
    p = thirty_year_old()
    assert weight_module.first_year_of_management(p, timestamp(2000, 2))
    assert not weight_module.first_year_of_management(p, timestamp(2001, 2))
    assert weight_module.first_five_years_of_management(p, timestamp(2001, 2))
    assert not weight_module.first_year_of_management(p, timestamp(2005, 2))
    start = date(2000)
    assert weight_module.first_year_of_management(p, start + WeightLossModule.ONE_YEAR)
    assert not weight_module.first_year_of_management(p, start + WeightLossModule.ONE_YEAR + 1)
    assert weight_module.first_five_years_of_management(p, start + 5 * WeightLossModule.ONE_YEAR)
    assert not weight_module.first_five_years_of_management(
        p, start + 5 * WeightLossModule.ONE_YEAR + 1
    )


def test_weight_adult_loss_and_regression(weight_module: WeightLossModule) -> None:
    """Java: WeightLossModuleTest#testAdultWeightLoss/testAdultRegression, exact arithmetic."""
    p = thirty_year_old()
    p.attributes[WeightLossModule.PRE_MANAGEMENT_WEIGHT] = 200.0
    assert weight_module.adult_weight_loss(p, timestamp(2000, 7)) == 190.02739726027397
    assert weight_module.adult_regression(p, date(2002)) == 185.01369863013699


def pediatric_setup() -> tuple[Person, PediatricGrowthTrajectory]:
    """Java: WeightLossModuleTest pediatric setup shared by vector/process tests."""
    p = Person(0)
    p.attributes.update(
        {
            Person.BIRTHDATE: date(1990),
            Person.GENDER: "M",
            WeightLossModule.WEIGHT_MANAGEMENT_START: date(2000),
            WeightLossModule.WEIGHT_LOSS_BMI_PERCENTILE_CHANGE: 0.01,
        }
    )
    pgt = PediatricGrowthTrajectory(0, date(1990))
    chart = WeightLossModule.growthChart[ChartType.BMI]
    for time in (timestamp(1999, 7, 2), timestamp(2000, 2)):
        age = p.age_in_months(time)
        pgt.add_point(age, time, chart.look_up(age, "M", 0.9))
    p.attributes[Person.GROWTH_TRAJECTORY] = pgt
    return p, pgt


@pytest.mark.parametrize("repeat", [False, True])
def test_weight_adjust_vector(weight_module: WeightLossModule, repeat: bool) -> None:
    """Java: adjustBMIVectorForSuccessfulManagement and its RunOnce test; exact point equality."""
    p, pgt = pediatric_setup()
    age = pgt.tail().age_in_months + 12
    expected = WeightLossModule.growthChart[ChartType.BMI].look_up(age, "M", 0.89)
    weight_module.adjust_bmi_vector_for_successful_management(p)
    assert pgt.tail().age_in_months == age
    assert pgt.tail().bmi == expected
    if repeat:
        weight_module.adjust_bmi_vector_for_successful_management(p)
        assert pgt.tail().age_in_months == age
        assert pgt.tail().bmi == expected


def test_weight_pediatric_regression(
    weight_module: WeightLossModule, golden: Callable[[str], Path]
) -> None:
    """Java: WeightLossModuleTest#testPediatricRegression, exact chart output."""
    p, pgt = pediatric_setup()
    chart = WeightLossModule.growthChart[ChartType.BMI]
    low = pgt.tail().age_in_months + 12
    pgt.add_point(
        low,
        pgt.tail().time_in_simulation + WeightLossModule.ONE_YEAR,
        chart.look_up(low, "M", 0.89),
    )
    weight_module.pediatric_regression(p, timestamp(2002, 3))
    assert pgt.tail().age_in_months == low + 12
    expected = json.loads((golden("ChronicModulesProbe") / "upstream.json").read_text())
    assert double_to_string(pgt.tail().bmi) == expected["regression_bmi"]


def test_weight_maintain_percentile(weight_module: WeightLossModule) -> None:
    """Java: WeightLossModuleTest#testMaintainBMIPercentile."""
    p = Person(0)
    p.attributes.update({Person.BIRTHDATE: date(1990), Person.GENDER: "M"})
    pgt = PediatricGrowthTrajectory(0, date(1990))
    chart = WeightLossModule.growthChart[ChartType.BMI]
    pgt.add_point(120, date(2000), chart.look_up(120, "M", 0.9))
    p.attributes[Person.GROWTH_TRAJECTORY] = pgt
    weight_module.maintain_bmi_percentile(p, timestamp(2000, 2))
    assert pgt.tail().age_in_months == 132
    assert pgt.tail().bmi == chart.look_up(132, "M", 0.9)


def test_weight_process(weight_module: WeightLossModule) -> None:
    """Java: WeightLossModuleTest#testProcess, adults and pediatric vector."""
    p = thirty_year_old()
    p.attributes.update(
        {
            WeightLossModule.ACTIVE_WEIGHT_MANAGEMENT: True,
            WeightLossModule.WEIGHT_LOSS_ADHERENCE: True,
            WeightLossModule.LONG_TERM_WEIGHT_LOSS: True,
        }
    )
    weight_module.process(p, timestamp(2000, 7, 2))
    assert p.get_vital_sign(VitalSign.WEIGHT, timestamp(2000, 7, 2)) == 129.2
    weight_module.process(p, timestamp(2000, 12, 31))
    weight_module.process(p, date(2006))
    assert p.get_vital_sign(VitalSign.WEIGHT, date(2006)) == 122.4
    p = thirty_year_old()
    p.attributes.update(
        {
            WeightLossModule.ACTIVE_WEIGHT_MANAGEMENT: True,
            WeightLossModule.WEIGHT_LOSS_ADHERENCE: False,
            WeightLossModule.LONG_TERM_WEIGHT_LOSS: True,
        }
    )
    weight_module.process(p, timestamp(2000, 7, 2))
    assert p.get_vital_sign(VitalSign.WEIGHT, timestamp(2000, 7, 2)) == 136.0
    p, pgt = pediatric_setup()
    p.attributes.update(
        {
            WeightLossModule.ACTIVE_WEIGHT_MANAGEMENT: True,
            WeightLossModule.WEIGHT_LOSS_ADHERENCE: True,
            WeightLossModule.LONG_TERM_WEIGHT_LOSS: True,
        }
    )
    age = pgt.tail().age_in_months + 12
    expected = WeightLossModule.growthChart[ChartType.BMI].look_up(age, "M", 0.89)
    weight_module.process(p, timestamp(2000, 3))
    assert pgt.tail().age_in_months == age
    assert pgt.tail().bmi == expected


def test_weight_thresholds(weight_module: WeightLossModule) -> None:
    """Java: WeightLossModuleTest#testMeetsWeightManagementThresholds."""
    p = Person(0)
    p.attributes.update({Person.BIRTHDATE: date(1990), Person.GENDER: "M"})
    p.set_vital_sign(VitalSign.BMI, BMI.calculate(139, 50))
    assert weight_module.meets_weight_management_thresholds(p, date(2000))
    p.set_vital_sign(VitalSign.BMI, BMI.calculate(139, 35))
    assert not weight_module.meets_weight_management_thresholds(p, date(2000))
    assert weight_module.meets_weight_management_thresholds(thirty_year_old(), date(2000))
    p = thirty_year_old()
    p.set_vital_sign(VitalSign.BMI, BMI.calculate(175, 85))
    assert not weight_module.meets_weight_management_thresholds(p, date(2000))
    assert not weight_module.meets_weight_management_thresholds(p, date(1989))


@pytest.mark.parametrize("position,expected", [(0.0, 0.0), (0.5, 0.5), (1.0, 1.0)])
def test_disability_triangular(position: float, expected: float) -> None:
    """Java: DisabilityWeight#triangularDistribution endpoints and mode."""
    assert (
        DisabilityWeight({"LOW": "0", "MED": "0.5", "HIGH": "1"}).triangular_distribution(position)
        == expected
    )


def test_weight_transition_regression(
    weight_module: WeightLossModule, golden: Callable[[str], Path]
) -> None:
    """Java: WeightLossModuleTest#transitionRegression, compared exactly with Java."""
    p = Person(0)
    p.attributes.update(
        {
            Person.BIRTHDATE: date(1990),
            Person.GENDER: "M",
            WeightLossModule.WEIGHT_MANAGEMENT_START: timestamp(2003, 12, 2),
            WeightLossModule.WEIGHT_LOSS_BMI_PERCENTILE_CHANGE: 0.01,
        }
    )
    p.set_vital_sign(VitalSign.HEIGHT_PERCENTILE, 0.75)
    pgt = PediatricGrowthTrajectory(0, date(1990))
    for year in range(1993, 2010):
        pgt.current_bmi(p, date(year))
    p.attributes[Person.GROWTH_TRAJECTORY] = pgt
    expected = json.loads((golden("ChronicModulesProbe") / "upstream.json").read_text())
    assert (
        double_to_string(weight_module.transition_regression(p, date(2010)))
        == expected["transition_weight"]
    )
