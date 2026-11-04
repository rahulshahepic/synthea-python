"""Java API skeleton: WeightLossModule.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.engine.module import Module
    from synthea.world.agents.person import Person
    from synthea.world.concepts.growth_chart import ChartType as GrowthChartChartType
    from synthea.world.concepts.growth_chart import GrowthChart


class WeightLossModule:
    """Java: WeightLossModule; pending T23."""

    ONE_YEAR: ClassVar[int] = 31536000000
    TW0_YEARS_IN_MONTHS: ClassVar[int] = 24
    TWENTY_YEARS_IN_MONTHS: ClassVar[int] = 240
    growthChart: ClassVar[
        dict[GrowthChartChartType, GrowthChart]
    ]  # Java initialization deferred to T23.
    ACTIVE_WEIGHT_MANAGEMENT: ClassVar[str] = "active_weight_management"
    PRE_MANAGEMENT_WEIGHT: ClassVar[str] = "pre_management_weight"
    WEIGHT_MANAGEMENT_START: ClassVar[str] = "weight_management_start"
    WEIGHT_LOSS_PERCENTAGE: ClassVar[str] = "weight_loss_percentage"
    WEIGHT_LOSS_BMI_PERCENTILE_CHANGE: ClassVar[str] = "weight_loss_bmi_percentile_change"
    LONG_TERM_WEIGHT_LOSS: ClassVar[str] = "long_term_weight_loss"
    WEIGHT_LOSS_ADHERENCE: ClassVar[str] = "weight_loss_adherence"
    TRIGGER_WEIGHT_LOSS: ClassVar[str] = "trigger_weight_loss"
    managementStartAge: ClassVar[int]  # Java initialization deferred to T23.
    startWeightManagementProb: ClassVar[float]  # Java initialization deferred to T23.
    adherence: ClassVar[float]  # Java initialization deferred to T23.
    startBMI: ClassVar[float]  # Java initialization deferred to T23.
    startPercentile: ClassVar[float]  # Java initialization deferred to T23.
    minLoss: ClassVar[float]  # Java initialization deferred to T23.
    maxLoss: ClassVar[float]  # Java initialization deferred to T23.
    maintenance: ClassVar[float]  # Java initialization deferred to T23.
    maxPedPercentileChange: ClassVar[float]  # Java initialization deferred to T23.

    def __init__(self) -> None:
        """Java: WeightLossModule#WeightLossModule.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: WeightLossModule#WeightLossModule — pending T23")

    def clone(self) -> Module:
        """Java: WeightLossModule#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: WeightLossModule#clone — pending T23")

    def process(self, person: Person, time: int) -> bool:
        """Java: WeightLossModule#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: WeightLossModule#process — pending T23")

    def manage_first_year_weight(self, person: Person, time: int) -> None:
        """Java: WeightLossModule#manageFirstYearWeight.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: WeightLossModule#manageFirstYearWeight — pending T23")

    def manage_year_two_through_five(self, person: Person, time: int) -> None:
        """Java: WeightLossModule#manageYearTwoThroughFive.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: WeightLossModule#manageYearTwoThroughFive — pending T23")

    def stop_weight_management(self, person: Person) -> None:
        """Java: WeightLossModule#stopWeightManagement.

        Java overloads:
        (Person person)
        """
        raise NotImplementedError("Java: WeightLossModule#stopWeightManagement — pending T23")

    def first_year_of_management(self, person: Person, time: int) -> bool:
        """Java: WeightLossModule#firstYearOfManagement.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: WeightLossModule#firstYearOfManagement — pending T23")

    def first_five_years_of_management(self, person: Person, time: int) -> bool:
        """Java: WeightLossModule#firstFiveYearsOfManagement.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: WeightLossModule#firstFiveYearsOfManagement — pending T23")

    def adult_weight_loss(self, person: Person, time: int) -> float:
        """Java: WeightLossModule#adultWeightLoss.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: WeightLossModule#adultWeightLoss — pending T23")

    def adult_regression(self, person: Person, time: int) -> float:
        """Java: WeightLossModule#adultRegression.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: WeightLossModule#adultRegression — pending T23")

    def pediatric_regression(self, person: Person, time: int) -> None:
        """Java: WeightLossModule#pediatricRegression.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: WeightLossModule#pediatricRegression — pending T23")

    def transition_regression(self, person: Person, time: int) -> float:
        """Java: WeightLossModule#transitionRegression.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: WeightLossModule#transitionRegression — pending T23")

    def adjust_bmi_vector_for_successful_management(self, person: Person) -> None:
        """Java: WeightLossModule#adjustBMIVectorForSuccessfulManagement.

        Java overloads:
        (Person person)
        """
        raise NotImplementedError(
            "Java: WeightLossModule#adjustBMIVectorForSuccessfulManagement — pending T23"
        )

    def maintain_bmi_percentile(self, person: Person, time: int) -> None:
        """Java: WeightLossModule#maintainBMIPercentile.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: WeightLossModule#maintainBMIPercentile — pending T23")

    def start_weight_management(self, person: Person, time: int) -> None:
        """Java: WeightLossModule#startWeightManagement.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: WeightLossModule#startWeightManagement — pending T23")

    def will_start_weight_management(self, person: Person, time: int) -> bool:
        """Java: WeightLossModule#willStartWeightManagement.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: WeightLossModule#willStartWeightManagement — pending T23")

    def meets_weight_management_thresholds(self, person: Person, time: int) -> bool:
        """Java: WeightLossModule#meetsWeightManagementThresholds.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError(
            "Java: WeightLossModule#meetsWeightManagementThresholds — pending T23"
        )
