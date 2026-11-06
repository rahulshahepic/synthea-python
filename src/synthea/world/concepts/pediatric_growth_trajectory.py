"""Java: org.mitre.synthea.world.concepts.PediatricGrowthTrajectory."""

from __future__ import annotations

import json
import math
from typing import TYPE_CHECKING, ClassVar, cast

from synthea.helpers.utilities import Utilities
from synthea.javacompat.fmt import format as java_format
from synthea.resources import read_resource
from synthea.world.concepts.growth_chart import ChartType, GrowthChart, _normal_cdf, _normal_ppf
from synthea.world.concepts.nhanes_sample import NHANESSample

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class YearInformation:
    """Java: PediatricGrowthTrajectory.YearInformation."""

    def __init__(self) -> None:
        """Java: YearInformation#YearInformation."""
        self.correlation: float = 0.0
        self.diff: float = 0.0


class Point:
    """Java: PediatricGrowthTrajectory.Point."""

    def __init__(self) -> None:
        """Java: Point#Point."""
        self.age_in_months: int = 0
        self.bmi: float = 0.0
        self.time_in_simulation: int = 0

    def to_string(self) -> str:
        """Java: Point#toString."""
        return java_format(
            "{Age: %d, Time: %d, BMI: %f}", self.age_in_months, self.time_in_simulation, self.bmi
        )


class PediatricGrowthTrajectory:
    """Java: PediatricGrowthTrajectory."""

    SIGMA_FEMALE_A: ClassVar[float] = 0.0011
    SIGMA_FEMALE_B: ClassVar[float] = 0.3712
    SIGMA_FEMALE_C: ClassVar[float] = 0.8334
    SIGMA_MALE_A: ClassVar[float] = 0.0091
    SIGMA_MALE_B: ClassVar[float] = 0.5196
    SIGMA_MALE_C: ClassVar[float] = 0.3728
    ONE_YEAR: ClassVar[int] = Utilities.convert_time("years", 1)
    NINETEEN_YEARS_IN_MONTHS: ClassVar[int] = 228
    growthChart = GrowthChart.load_charts()
    yearCorrelations: ClassVar[dict[str, YearInformation]]
    nhanesSamples = NHANESSample.load_distribution()
    nhanesMaleSamples = NHANESSample.load_distribution_by_sex(1)
    nhanesFemaleSamples = NHANESSample.load_distribution_by_sex(2)

    def __init__(self, person_seed: int, birth_time: int, sex: str | None = None) -> None:
        """Java: PediatricGrowthTrajectory#PediatricGrowthTrajectory (both overloads)."""
        self.seed: int = person_seed
        self.initial_sample: NHANESSample = self.get_sample(person_seed, sex)
        p = Point()
        p.age_in_months = self.initial_sample.agem
        p.bmi = self.initial_sample.bmi
        p.time_in_simulation = birth_time + Utilities.convert_time("months", p.age_in_months)
        self.trajectory: list[Point] = [p]

    @staticmethod
    def get_sample(person_seed: int, sex: str | None = None) -> NHANESSample:
        """Java: PediatricGrowthTrajectory#getSample (both overloads)."""
        cls = PediatricGrowthTrajectory
        dist = (
            cls.nhanesMaleSamples
            if sex == "M"
            else cls.nhanesFemaleSamples
            if sex == "F"
            else cls.nhanesSamples
        )
        dist.reseed_random_generator(person_seed)
        return dist.sample()

    def reverse_weight_percentile(self, sex: str, height_percentile: float) -> float:
        """Java: PediatricGrowthTrajectory#reverseWeightPercentile."""
        from synthea.world.concepts.bmi import BMI

        height = self.growthChart[ChartType.HEIGHT].look_up(
            self.initial_sample.agem, sex, height_percentile
        )
        weight = BMI.weight_for_height_and_bmi(height, self.initial_sample.bmi)
        return self.growthChart[ChartType.WEIGHT].percentile_for(
            self.initial_sample.agem, sex, weight
        )

    def generate_next_year_bmi(self, person: Person, time: int) -> None:
        """Java: PediatricGrowthTrajectory#generateNextYearBMI."""
        age = person.age_in_decimal_years(time)
        next_age_year = age + 1
        sex = cast(str, person.attributes["gender"])
        yi = self.yearCorrelations[str(math.floor(next_age_year))]
        sig = self.sigma(sex, age)
        last = self.tail()
        ez = self.extended_z_score(last.bmi, last.age_in_months, sex, sig)
        mean = yi.correlation * ez + yi.diff
        sd = math.sqrt(1 - math.pow(yi.correlation, 2))
        next_z = person.rand_gaussian() * sd + mean
        percentile = GrowthChart.zscore_to_percentile(next_z)
        bmi = self.percentile_to_bmi(
            percentile, last.age_in_months + 12, sex, self.sigma(sex, next_age_year)
        )
        self.add_point(last.age_in_months + 12, last.time_in_simulation + self.ONE_YEAR, bmi)

    def tail(self) -> Point:
        """Java: PediatricGrowthTrajectory#tail."""
        return self.trajectory[-1]

    def just_before(self, time: int) -> Point | None:
        """Java: PediatricGrowthTrajectory#justBefore."""
        p = None
        for point in self.trajectory:
            if point.time_in_simulation < time:
                p = point
            else:
                return p
        return p

    def just_after(self, time: int) -> Point | None:
        """Java: PediatricGrowthTrajectory#justAfter."""
        for point in self.trajectory:
            if point.time_in_simulation > time:
                return point
        return None

    def before_initial_sample(self, time: int) -> bool:
        """Java: PediatricGrowthTrajectory#beforeInitialSample."""
        return self.trajectory[0].time_in_simulation > time

    def add_point(self, age_in_months: int, time_in_simulation: int, bmi: float) -> None:
        """Java: PediatricGrowthTrajectory#addPoint."""
        p = Point()
        p.age_in_months, p.time_in_simulation, p.bmi = age_in_months, time_in_simulation, bmi
        if self.tail().time_in_simulation > time_in_simulation:
            raise ValueError("Must extend beyond end of current trajectory")
        self.trajectory.append(p)

    def add_point_from_percentile(
        self, age_in_months: int, time_in_simulation: int, percentile: float, sex: str
    ) -> None:
        """Java: PediatricGrowthTrajectory#addPointFromPercentile."""
        sig = self.sigma(sex, age_in_months / 12.0)
        self.add_point(
            age_in_months,
            time_in_simulation,
            self.percentile_to_bmi(percentile, age_in_months, sex, sig),
        )

    def current_bmi(self, person: Person, time: int) -> float:
        """Java: PediatricGrowthTrajectory#currentBMI."""
        last = self.tail()
        if last.time_in_simulation <= time:
            if last.age_in_months > self.NINETEEN_YEARS_IN_MONTHS:
                return last.bmi
            self.generate_next_year_bmi(person, time)
        previous, next_point = self.just_before(time), self.just_after(time)
        assert previous is not None and next_point is not None
        elapsed = (float(time) - previous.time_in_simulation) / (
            next_point.time_in_simulation - previous.time_in_simulation
        )
        difference = next_point.bmi - previous.bmi
        return previous.bmi + difference * elapsed

    @staticmethod
    def cumulative_probability(value: float) -> float:
        """Java: PediatricGrowthTrajectory#cumulativeProbability."""
        return _normal_cdf(value)

    @staticmethod
    def inverse_cumulative_probability(value: float) -> float:
        """Java: PediatricGrowthTrajectory#inverseCumulativeProbability."""
        return _normal_ppf(value)

    @staticmethod
    def percentile_to_bmi(percentile: float, age_in_months: int, sex: str, sigma: float) -> float:
        """Java: PediatricGrowthTrajectory#percentileToBMI."""
        chart = PediatricGrowthTrajectory.growthChart[ChartType.BMI]
        if percentile < 0.95:
            return chart.look_up(age_in_months, sex, percentile)
        ninety_fifth = chart.look_up(age_in_months, sex, 0.95)
        return ninety_fifth + _normal_ppf((percentile - 0.9) * 10) * sigma

    @staticmethod
    def extended_z_score(bmi: float, age_in_months: int, sex: str, sigma: float) -> float:
        """Java: PediatricGrowthTrajectory#extendedZScore."""
        chart = PediatricGrowthTrajectory.growthChart[ChartType.BMI]
        current = chart.percentile_for(age_in_months, sex, bmi)
        if current < 0.95:
            return GrowthChart.calculate_z_score(current)
        ninety_fifth = chart.look_up(age_in_months, sex, 0.95)
        percentile = 90 + 10 * _normal_cdf((bmi - ninety_fifth) / sigma)
        return _normal_ppf(percentile / 100)

    @staticmethod
    def sigma(sex: str, age: float) -> float:
        """Java: PediatricGrowthTrajectory#sigma."""
        cls = PediatricGrowthTrajectory
        if sex == "M":
            return cls.SIGMA_MALE_C + cls.SIGMA_MALE_B * age - cls.SIGMA_MALE_A * math.pow(age, 2)
        return cls.SIGMA_FEMALE_C + cls.SIGMA_FEMALE_B * age - cls.SIGMA_FEMALE_A * math.pow(age, 2)

    @staticmethod
    def load_correlations() -> dict[str, YearInformation]:
        """Java: PediatricGrowthTrajectory#loadCorrelations."""
        result = {}
        for age, values in json.loads(read_resource("bmi_correlations.json")).items():
            info = YearInformation()
            info.correlation, info.diff = values["correlation"], values["diff"]
            result[age] = info
        return result


PediatricGrowthTrajectory.yearCorrelations = PediatricGrowthTrajectory.load_correlations()
setattr(PediatricGrowthTrajectory, "Point", Point)  # noqa: B010
setattr(PediatricGrowthTrajectory, "YearInformation", YearInformation)  # noqa: B010
