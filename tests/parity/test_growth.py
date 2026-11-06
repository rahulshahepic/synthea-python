"""Component parity for T12; only Person attributes and real RNG plumbing are doubled."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import cast

import pytest

from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.javacompat.collections import JavaConcurrentHashMap
from synthea.javacompat.numbers import double_to_string
from synthea.world.agents.person import Person
from synthea.world.concepts.birth_statistics import BirthStatistics
from synthea.world.concepts.growth_chart import ChartType, GrowthChart
from synthea.world.concepts.growth_chart_entry import GrowthChartEntry
from synthea.world.concepts.nhanes_sample import NHANESSample
from synthea.world.concepts.pediatric_growth_trajectory import PediatricGrowthTrajectory, Point
from tests.dependency_gate import Pending, report_pending, run_or_pending


class GrowthPerson_double(Person):  # noqa: N801
    """Test-only Person attributes/RNG; real T09 age methods remain inherited."""

    def __init__(self, seed: int) -> None:
        self.random = DefaultRandomNumberGenerator(seed)
        self.attributes = JavaConcurrentHashMap()

    def rand(self, *args: float) -> float:
        """Real RNG overload plumbing missing from Person until fix #54 merges."""
        if not args:
            return self.random.rand()
        return self.random.rand(*args)


def _point(point: Point | None) -> list[object] | None:
    if point is None:
        return None
    return [
        point.age_in_months,
        str(point.time_in_simulation),
        double_to_string(point.bmi),
        point.to_string(),
    ]


def _component(row: dict[str, object]) -> dict[str, object]:
    i = cast(int, row["i"])
    seed = int(cast(str, row["seed"]))
    sex = cast(str, row["sex"])
    age = cast(int, row["age"])
    percentile = float(cast(str, row["percentile"]))
    o: dict[str, object] = {
        "i": i,
        "seed": str(seed),
        "sex": sex,
        "age": age,
        "percentile": double_to_string(percentile),
    }

    def number(key: str, value: float) -> None:
        o[key] = double_to_string(value)

    number("z", GrowthChart.calculate_z_score(percentile))
    number("cdf", GrowthChart.zscore_to_percentile(GrowthChart.calculate_z_score(percentile)))
    number("privateCdf", PediatricGrowthTrajectory.cumulative_probability(percentile * 16 - 8))
    number("privatePpf", PediatricGrowthTrajectory.inverse_cumulative_probability(percentile))
    results = []
    for chart_type, chart in GrowthChart.load_charts().items():
        months = (
            age % 37
            if chart_type == ChartType.HEAD
            else 24 + age % 217
            if chart_type == ChartType.BMI
            else age
        )
        value = chart.look_up(months, sex, percentile)
        results.append(
            [
                chart_type.value,
                months,
                double_to_string(value),
                double_to_string(chart.percentile_for(months, sex, value)),
            ]
        )
    o["charts"] = results
    entry = GrowthChartEntry(0 if i % 3 == 0 else 0.5, 10 + percentile, 0.2)
    number("entryValue", entry.look_up(percentile))
    number("entryZ", entry.zscore_for_value(9 + percentile))
    number("entryPercentile", entry.percentile_for_value(9 + percentile))
    samples = NHANESSample.load_samples()
    o["sampleRow"] = samples[i % len(samples)].to_string()
    for code in range(3):
        dist = (
            NHANESSample.load_distribution()
            if code == 0
            else NHANESSample.load_distribution_by_sex(code)
        )
        dist.reseed_random_generator(seed)
        o[f"distribution{code}"] = dist.sample().to_string()
    fallback = NHANESSample.load_distribution_by_sex(99)
    fallback.reseed_random_generator(seed)
    o["distributionFallback"] = fallback.sample().to_string()
    birth = -631152000000
    trajectory = PediatricGrowthTrajectory(seed, birth, sex)
    legacy = PediatricGrowthTrajectory(seed, birth)
    o["initial"], o["legacy"] = _point(trajectory.tail()), _point(legacy.tail())
    o["selected"] = PediatricGrowthTrajectory.get_sample(seed, sex).to_string()
    t = trajectory.tail().time_in_simulation
    o["before"] = trajectory.before_initial_sample(t - 1)
    o["equalBefore"] = trajectory.before_initial_sample(t)
    o["noBefore"] = _point(trajectory.just_before(t))
    o["noAfter"] = _point(trajectory.just_after(t))
    months = 24 + age % 205
    sigma = PediatricGrowthTrajectory.sigma(sex, age / 12.0)
    number("sigma", sigma)
    bmi = PediatricGrowthTrajectory.percentile_to_bmi(percentile, months, sex, sigma)
    number("bmi", bmi)
    number("extended", PediatricGrowthTrajectory.extended_z_score(bmi, months, sex, sigma))
    assert trajectory.just_before(t) is None
    assert trajectory.just_after(t) is None
    trajectory.add_point(trajectory.tail().age_in_months + 12, t + 31536000000, 18 + percentile)
    o["beforePoint"], o["afterPoint"] = (
        _point(trajectory.just_before(t + 1)),
        _point(trajectory.just_after(t + 1)),
    )
    person = GrowthPerson_double(seed)
    person.attributes["birthdate"], person.attributes["gender"] = birth, sex
    number("interpolated", trajectory.current_bmi(person, t + 15768000000))
    trajectory.add_point_from_percentile(60, t + 2 * 31536000000, percentile, sex)
    o["percentilePoint"] = _point(trajectory.tail())
    with pytest.raises(ValueError, match="Must extend beyond"):
        trajectory.add_point(1, t, 1)
    o["invalid"] = True
    generated = PediatricGrowthTrajectory(seed, birth, sex)
    generated.generate_next_year_bmi(person, generated.tail().time_in_simulation + 31536000000 - 1)
    o["generated"] = _point(generated.tail())
    current = PediatricGrowthTrajectory(seed, birth, sex)
    number(
        "currentGenerated",
        current.current_bmi(person, current.tail().time_in_simulation + 31536000000 - 1),
    )
    current.add_point(240, t + 20 * 31536000000, 23)
    number("adult", current.current_bmi(person, t + 21 * 31536000000))
    o["correlations"] = len(PediatricGrowthTrajectory.load_correlations())
    mother = GrowthPerson_double(seed)
    mother.attributes["gender"] = "M" if i % 7 == 0 else "F"
    mother.attributes["ethnicity"] = "HiSpAnIc" if i % 3 == 0 else "nonhispanic"
    mother.attributes["pregnant"] = i % 5 != 0
    if i % 4 == 0:
        mother.attributes[BirthStatistics.BIRTH_SEX] = "F"
    BirthStatistics.set_birth_statistics(mother, birth)
    attrs = {}
    for key in (
        BirthStatistics.BIRTH_WEEK,
        BirthStatistics.BIRTH_DATE,
        BirthStatistics.BIRTH_WEIGHT,
        BirthStatistics.BIRTH_HEIGHT,
        BirthStatistics.BIRTH_SEX,
    ):
        if key in mother.attributes:
            value = mother.attributes[key]
            attrs[key] = double_to_string(value) if isinstance(value, float) else str(value)
    o["birth"] = attrs
    BirthStatistics.clear_birth_statistics(mother)
    o["cleared"] = BirthStatistics.BIRTH_SEX not in mother.attributes
    o["motherDraws"] = mother.get_count()
    return o


@pytest.mark.parity
def test_growth_component_public_methods(golden: Callable[[str], Path]) -> None:
    rows = [
        json.loads(line)
        for line in (golden("GrowthProbe") / "growth.jsonl").read_text().splitlines()
    ]
    assert len(rows) >= 1000
    for row in rows:
        actual = _component(row)
        differences = [(k, v, actual.get(k)) for k, v in row.items() if actual.get(k) != v]
        assert actual == row, f"seed={row['seed']}; differences={differences}"


@pytest.mark.parity
def test_growth_reverse_weight_integration(golden: Callable[[str], Path]) -> None:
    results = []
    for line in (golden("GrowthProbe") / "reverse.jsonl").read_text().splitlines():
        row = json.loads(line)

        def scenario(row: dict[str, str] = row) -> float:
            trajectory = PediatricGrowthTrajectory(int(row["seed"]), -631152000000, row["sex"])
            return trajectory.reverse_weight_percentile(row["sex"], float(row["percentile"]))

        result = run_or_pending(scenario, ("T11",))
        results.append(result)
        if not isinstance(result, Pending):
            assert double_to_string(result) == row["value"]
    report_pending("T12 reverse weight integration", results)
