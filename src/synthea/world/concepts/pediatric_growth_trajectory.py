"""Java API skeleton:
java/src/main/java/org/mitre/synthea/world/concepts/PediatricGrowthTrajectory.java.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Protocol

if TYPE_CHECKING:
    from synthea.world.agents.person import Person
    from synthea.world.concepts.growth_chart import ChartType as GrowthChartChartType
    from synthea.world.concepts.growth_chart import GrowthChart
    from synthea.world.concepts.nhanes_sample import NHANESSample

    class EnumeratedDistribution(Protocol):
        """Java boundary type: EnumeratedDistribution; external to the mapped Python port."""

    class NormalDistribution(Protocol):
        """Java boundary type: NormalDistribution; external to the mapped Python port."""


class PediatricGrowthTrajectory:
    """Java: PediatricGrowthTrajectory; pending T12."""

    SIGMA_FEMALE_A: ClassVar[float] = 0.0011
    SIGMA_FEMALE_B: ClassVar[float] = 0.3712
    SIGMA_FEMALE_C: ClassVar[float] = 0.8334
    SIGMA_MALE_A: ClassVar[float] = 0.0091
    SIGMA_MALE_B: ClassVar[float] = 0.5196
    SIGMA_MALE_C: ClassVar[float] = 0.3728
    ONE_YEAR: ClassVar[int] = 31536000000
    NINETEEN_YEARS_IN_MONTHS: ClassVar[int] = 228
    growthChart: ClassVar[
        dict[GrowthChartChartType, GrowthChart]
    ]  # Java initialization deferred to T12.
    yearCorrelations: ClassVar[dict[str, YearInformation]]  # Java initialization deferred to T12.
    normalDistribution: ClassVar[NormalDistribution]  # Java initialization deferred to T12.
    nhanesSamples: ClassVar[EnumeratedDistribution]  # Java initialization deferred to T12.
    nhanesMaleSamples: ClassVar[EnumeratedDistribution]  # Java initialization deferred to T12.
    nhanesFemaleSamples: ClassVar[EnumeratedDistribution]  # Java initialization deferred to T12.

    def __init__(self, person_seed: int, birth_time: int, sex: str | None = None) -> None:
        """Java: PediatricGrowthTrajectory#PediatricGrowthTrajectory.

        Java overloads:
        (long personSeed, long birthTime, String sex)
        (long personSeed, long birthTime)
        """
        self.initial_sample: NHANESSample
        self.trajectory: list[Point]
        self.seed: int
        raise NotImplementedError(
            "Java: PediatricGrowthTrajectory#PediatricGrowthTrajectory — pending T12"
        )

    @staticmethod
    def get_sample(person_seed: int, sex: str | None = None) -> NHANESSample:
        """Java: PediatricGrowthTrajectory#getSample.

        Java overloads:
        (long personSeed, String sex)
        (long personSeed)
        """
        raise NotImplementedError("Java: PediatricGrowthTrajectory#getSample — pending T12")

    def reverse_weight_percentile(self, sex: str, height_percentile: float) -> float:
        """Java: PediatricGrowthTrajectory#reverseWeightPercentile.

        Java overloads:
        (String sex, double heightPercentile)
        """
        raise NotImplementedError(
            "Java: PediatricGrowthTrajectory#reverseWeightPercentile — pending T12"
        )

    def generate_next_year_bmi(self, person: Person, time: int) -> None:
        """Java: PediatricGrowthTrajectory#generateNextYearBMI.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError(
            "Java: PediatricGrowthTrajectory#generateNextYearBMI — pending T12"
        )

    def tail(self) -> Point:
        """Java: PediatricGrowthTrajectory#tail.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: PediatricGrowthTrajectory#tail — pending T12")

    def just_before(self, time: int) -> Point:
        """Java: PediatricGrowthTrajectory#justBefore.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: PediatricGrowthTrajectory#justBefore — pending T12")

    def just_after(self, time: int) -> Point:
        """Java: PediatricGrowthTrajectory#justAfter.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: PediatricGrowthTrajectory#justAfter — pending T12")

    def before_initial_sample(self, time: int) -> bool:
        """Java: PediatricGrowthTrajectory#beforeInitialSample.

        Java overloads:
        (long time)
        """
        raise NotImplementedError(
            "Java: PediatricGrowthTrajectory#beforeInitialSample — pending T12"
        )

    def add_point(self, age_in_months: int, time_in_simulation: int, bmi: float) -> None:
        """Java: PediatricGrowthTrajectory#addPoint.

        Java overloads:
        (int ageInMonths, long timeInSimulation, double bmi)
        """
        raise NotImplementedError("Java: PediatricGrowthTrajectory#addPoint — pending T12")

    def add_point_from_percentile(
        self, age_in_months: int, time_in_simulation: int, percentile: float, sex: str
    ) -> None:
        """Java: PediatricGrowthTrajectory#addPointFromPercentile.

        Java overloads:
        (int ageInMonths, long timeInSimulation, double percentile, String sex)
        """
        raise NotImplementedError(
            "Java: PediatricGrowthTrajectory#addPointFromPercentile — pending T12"
        )

    def current_bmi(self, person: Person, time: int) -> float:
        """Java: PediatricGrowthTrajectory#currentBMI.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: PediatricGrowthTrajectory#currentBMI — pending T12")

    @staticmethod
    def cumulative_probability(value: float) -> float:
        """Java: PediatricGrowthTrajectory#cumulativeProbability.

        Java overloads:
        (double value)
        """
        raise NotImplementedError(
            "Java: PediatricGrowthTrajectory#cumulativeProbability — pending T12"
        )

    @staticmethod
    def inverse_cumulative_probability(value: float) -> float:
        """Java: PediatricGrowthTrajectory#inverseCumulativeProbability.

        Java overloads:
        (double value)
        """
        raise NotImplementedError(
            "Java: PediatricGrowthTrajectory#inverseCumulativeProbability — pending T12"
        )

    @staticmethod
    def percentile_to_bmi(percentile: float, age_in_months: int, sex: str, sigma: float) -> float:
        """Java: PediatricGrowthTrajectory#percentileToBMI.

        Java overloads:
        (double percentile, int ageInMonths, String sex, double sigma)
        """
        raise NotImplementedError("Java: PediatricGrowthTrajectory#percentileToBMI — pending T12")

    @staticmethod
    def extended_z_score(bmi: float, age_in_months: int, sex: str, sigma: float) -> float:
        """Java: PediatricGrowthTrajectory#extendedZScore.

        Java overloads:
        (double bmi, int ageInMonths, String sex, double sigma)
        """
        raise NotImplementedError("Java: PediatricGrowthTrajectory#extendedZScore — pending T12")

    @staticmethod
    def sigma(sex: str, age: float) -> float:
        """Java: PediatricGrowthTrajectory#sigma.

        Java overloads:
        (String sex, double age)
        """
        raise NotImplementedError("Java: PediatricGrowthTrajectory#sigma — pending T12")

    @staticmethod
    def load_correlations() -> dict[str, YearInformation]:
        """Java: PediatricGrowthTrajectory#loadCorrelations.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: PediatricGrowthTrajectory#loadCorrelations — pending T12")


class YearInformation:
    """Java: YearInformation; pending T12."""

    def __init__(self) -> None:
        """Java: YearInformation#YearInformation.

        Java overloads:
        ()
        """
        self.correlation: float
        self.diff: float
        raise NotImplementedError("Java: YearInformation#YearInformation — pending T12")


class Point:
    """Java: Point; pending T12."""

    def __init__(self) -> None:
        """Java: Point#Point.

        Java overloads:
        ()
        """
        self.age_in_months: int
        self.bmi: float
        self.time_in_simulation: int
        raise NotImplementedError("Java: Point#Point — pending T12")

    def to_string(self) -> str:
        """Java: Point#toString.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Point#toString — pending T12")


setattr(PediatricGrowthTrajectory, "YearInformation", YearInformation)  # noqa: B010
setattr(PediatricGrowthTrajectory, "Point", Point)  # noqa: B010
