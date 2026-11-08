"""Java: org.mitre.synthea.modules.WeightLossModule."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, cast

from synthea.engine.module import Module
from synthea.helpers.utilities import Utilities
from synthea.world.concepts.biometrics_config import BiometricsConfig
from synthea.world.concepts.bmi import BMI
from synthea.world.concepts.growth_chart import ChartType, GrowthChart
from synthea.world.concepts.pediatric_growth_trajectory import PediatricGrowthTrajectory
from synthea.world.concepts.vital_sign import VitalSign

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class WeightLossModule(Module):
    """Java: WeightLossModule; adherence, loss, maintenance and regression."""

    ONE_YEAR: ClassVar[int] = 31536000000
    TW0_YEARS_IN_MONTHS: ClassVar[int] = 24
    TWENTY_YEARS_IN_MONTHS: ClassVar[int] = 240
    growthChart: ClassVar[dict[ChartType, GrowthChart]]  # Java initialization deferred to T23.
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
        """Java: WeightLossModule#WeightLossModule."""
        super().__init__()
        self.name = "Weight Loss"

    def clone(self) -> Module:
        """Java: WeightLossModule#clone."""
        return self

    def process(self, person: Person, time: int) -> bool:  # type: ignore[override]
        """Java: WeightLossModule#process (declared two-argument overload)."""
        if not person.alive(time):
            return True
        if (
            person.attributes.get(self.ACTIVE_WEIGHT_MANAGEMENT) is not None
            and person.attributes[self.ACTIVE_WEIGHT_MANAGEMENT]
        ):
            success = person.attributes[self.LONG_TERM_WEIGHT_LOSS]
            age = person.age_in_years(time)
            if self.first_year_of_management(person, time):
                self.manage_first_year_weight(person, time)
            elif self.first_five_years_of_management(person, time):
                self.manage_year_two_through_five(person, time)
            elif success:
                if age < 20:
                    self.maintain_bmi_percentile(person, time)
            else:
                self.stop_weight_management(person)
        elif self.will_start_weight_management(person, time):
            self.start_weight_management(person, time)
        return False

    def manage_first_year_weight(self, person: Person, time: int) -> None:
        """Java: WeightLossModule#manageFirstYearWeight."""
        follows = person.attributes[self.WEIGHT_LOSS_ADHERENCE]
        age = person.age_in_years(time)
        if age < 20:
            if follows:
                self.adjust_bmi_vector_for_successful_management(person)
        else:
            weight = (
                self.adult_weight_loss(person, time)
                if follows
                else person.get_vital_sign(VitalSign.WEIGHT, time)
            )
            height = person.get_vital_sign(VitalSign.HEIGHT, time)
            person.set_vital_sign(VitalSign.WEIGHT, weight)
            person.set_vital_sign(VitalSign.BMI, BMI.calculate(height, weight))

    def manage_year_two_through_five(self, person: Person, time: int) -> None:
        """Java: WeightLossModule#manageYearTwoThroughFive."""
        follows = person.attributes[self.WEIGHT_LOSS_ADHERENCE]
        success = person.attributes[self.LONG_TERM_WEIGHT_LOSS]
        age = person.age_in_years(time)
        gender = cast(str, person.attributes["gender"])
        if follows:
            if success:
                if age < 20:
                    self.maintain_bmi_percentile(person, time)
            elif age < 20:
                self.pediatric_regression(person, time)
            else:
                start = cast(int, person.attributes[self.WEIGHT_MANAGEMENT_START])
                if person.age_in_years(start) < 20:
                    height = self.growthChart[ChartType.HEIGHT].look_up(
                        240, gender, person.get_vital_sign(VitalSign.HEIGHT_PERCENTILE, time)
                    )
                    weight = self.transition_regression(person, time)
                else:
                    height = person.get_vital_sign(VitalSign.HEIGHT, time)
                    weight = self.adult_regression(person, time)
                person.set_vital_sign(VitalSign.HEIGHT, height)
                person.set_vital_sign(VitalSign.WEIGHT, weight)
                person.set_vital_sign(VitalSign.BMI, BMI.calculate(height, weight))

    def stop_weight_management(self, person: Person) -> None:
        """Java: WeightLossModule#stopWeightManagement."""
        for key in (
            self.WEIGHT_MANAGEMENT_START,
            self.WEIGHT_LOSS_PERCENTAGE,
            self.WEIGHT_LOSS_ADHERENCE,
            self.WEIGHT_LOSS_BMI_PERCENTILE_CHANGE,
            self.PRE_MANAGEMENT_WEIGHT,
            self.LONG_TERM_WEIGHT_LOSS,
            self.TRIGGER_WEIGHT_LOSS,
        ):
            person.attributes.pop(key, None)
        person.attributes[self.ACTIVE_WEIGHT_MANAGEMENT] = False

    def first_year_of_management(self, person: Person, time: int) -> bool:
        """Java: WeightLossModule#firstYearOfManagement; inclusive boundary."""
        return cast(
            int, person.attributes[self.WEIGHT_MANAGEMENT_START]
        ) >= time - Utilities.convert_time("years", 1)

    def first_five_years_of_management(self, person: Person, time: int) -> bool:
        """Java: WeightLossModule#firstFiveYearsOfManagement; inclusive boundary."""
        return cast(
            int, person.attributes[self.WEIGHT_MANAGEMENT_START]
        ) >= time - Utilities.convert_time("years", 5)

    def adult_weight_loss(self, person: Person, time: int) -> float:
        """Java: WeightLossModule#adultWeightLoss."""
        start = cast(int, person.attributes[self.WEIGHT_MANAGEMENT_START])
        year = float(Utilities.convert_time("years", 1))
        percent = (time - start) / year
        weight = cast(float, person.attributes[self.PRE_MANAGEMENT_WEIGHT])
        loss = cast(float, person.attributes[self.WEIGHT_LOSS_PERCENTAGE])
        return weight - (weight * loss * percent)

    def adult_regression(self, person: Person, time: int) -> float:
        """Java: WeightLossModule#adultRegression."""
        start = cast(int, person.attributes[self.WEIGHT_MANAGEMENT_START])
        elapsed = (time - start - Utilities.convert_time("years", 1)) / float(
            Utilities.convert_time("years", 4)
        )
        weight = cast(float, person.attributes[self.PRE_MANAGEMENT_WEIGHT])
        loss = cast(float, person.attributes[self.WEIGHT_LOSS_PERCENTAGE])
        minimum = weight - (weight * loss)
        return weight - ((weight - minimum) * (1 - elapsed))

    def pediatric_regression(self, person: Person, time: int) -> None:
        """Java: WeightLossModule#pediatricRegression."""
        pgt = cast(PediatricGrowthTrajectory, person.attributes["growth_trajectory"])
        start = cast(int, person.attributes[self.WEIGHT_MANAGEMENT_START])
        start_age = person.age_in_months(start)
        if time + self.ONE_YEAR > pgt.tail().time_in_simulation:
            chart = self.growthChart[ChartType.BMI]
            gender = cast(str, person.attributes["gender"])
            original = chart.percentile_for(start_age, gender, pgt.current_bmi(person, start))
            change = cast(float, person.attributes[self.WEIGHT_LOSS_BMI_PERCENTILE_CHANGE])
            next_age = min(pgt.tail().age_in_months + 12, 240)
            next_time = pgt.tail().time_in_simulation + self.ONE_YEAR
            years = int((next_age - start_age - self.TW0_YEARS_IN_MONTHS) / 12)
            percentile = original - change * (1.0 - (years / 5.0))
            pgt.add_point_from_percentile(next_age, next_time, percentile, gender)

    def transition_regression(self, person: Person, time: int) -> float:
        """Java: WeightLossModule#transitionRegression."""
        chart = self.growthChart[ChartType.BMI]
        pgt = cast(PediatricGrowthTrajectory, person.attributes["growth_trajectory"])
        start = cast(int, person.attributes[self.WEIGHT_MANAGEMENT_START])
        start_age = person.age_in_months(start)
        bmi_at_start = pgt.current_bmi(person, start)
        gender = cast(str, person.attributes["gender"])
        original = chart.percentile_for(start_age, gender, bmi_at_start)
        bmi_at_twenty = chart.look_up(240, gender, original)
        height = self.growthChart[ChartType.HEIGHT].look_up(
            240, gender, person.get_vital_sign(VitalSign.HEIGHT_PERCENTILE, time)
        )
        target = BMI.weight_for_height_and_bmi(height, bmi_at_twenty)
        end_age = int(start_age / 12) + 7
        denominator = end_age - 20
        if denominator == 0:
            denominator = 1
        elapsed = (person.age_in_decimal_years(time) - 20) / denominator
        weight_at_twenty = BMI.weight_for_height_and_bmi(height, pgt.tail().bmi)
        return weight_at_twenty + (elapsed * (target - weight_at_twenty))

    def adjust_bmi_vector_for_successful_management(self, person: Person) -> None:
        """Java: WeightLossModule#adjustBMIVectorForSuccessfulManagement."""
        chart = self.growthChart[ChartType.BMI]
        gender = cast(str, person.attributes["gender"])
        start = cast(int, person.attributes[self.WEIGHT_MANAGEMENT_START])
        age = person.age_in_months(start)
        pgt = cast(PediatricGrowthTrajectory, person.attributes["growth_trajectory"])
        change = cast(float, person.attributes[self.WEIGHT_LOSS_BMI_PERCENTILE_CHANGE])
        bmi = pgt.current_bmi(person, start)
        start_percentile = chart.percentile_for(age, gender, bmi)
        tail_age = pgt.tail().age_in_months
        tail_bmi = pgt.tail().bmi
        tail_percentile = chart.percentile_for(tail_age, gender, tail_bmi)
        if tail_percentile <= start_percentile:
            return
        target = tail_percentile - change
        tail_time = pgt.tail().time_in_simulation
        months = 12
        if tail_age + months > self.TWENTY_YEARS_IN_MONTHS:
            months = self.TWENTY_YEARS_IN_MONTHS - tail_age
            target = tail_percentile - (change * float(months) / 12)
        target_bmi = chart.look_up(tail_age + months, gender, target)
        pgt.add_point(
            tail_age + months, tail_time + Utilities.convert_time("months", months), target_bmi
        )

    def maintain_bmi_percentile(self, person: Person, time: int) -> None:
        """Java: WeightLossModule#maintainBMIPercentile."""
        chart = self.growthChart[ChartType.BMI]
        pgt = cast(PediatricGrowthTrajectory, person.attributes["growth_trajectory"])
        age = person.age_in_months(time)
        tail = pgt.tail()
        if age < self.TWENTY_YEARS_IN_MONTHS and tail.age_in_months <= age:
            gender = cast(str, person.attributes["gender"])
            months = 12
            if tail.age_in_months + months > self.TWENTY_YEARS_IN_MONTHS:
                months = self.TWENTY_YEARS_IN_MONTHS - tail.age_in_months
            percentile = chart.percentile_for(tail.age_in_months, gender, tail.bmi)
            bmi = chart.look_up(tail.age_in_months + months, gender, percentile)
            pgt.add_point(
                tail.age_in_months + months,
                tail.time_in_simulation + Utilities.convert_time("months", months),
                bmi,
            )

    def start_weight_management(self, person: Person, time: int) -> None:
        """Java: WeightLossModule#startWeightManagement; forced adherence still consumes RNG."""
        start_weight = person.get_vital_sign(VitalSign.WEIGHT, time)
        person.attributes[self.ACTIVE_WEIGHT_MANAGEMENT] = True
        person.attributes[self.PRE_MANAGEMENT_WEIGHT] = start_weight
        person.attributes[self.WEIGHT_MANAGEMENT_START] = time
        follows = person.rand() <= self.adherence
        trigger = False
        if person.attributes.get(self.TRIGGER_WEIGHT_LOSS) is not None:
            trigger = bool(person.attributes[self.TRIGGER_WEIGHT_LOSS])
            follows = trigger
        person.attributes[self.WEIGHT_LOSS_ADHERENCE] = follows
        if follows:
            if person.age_in_years(time) >= 20:
                person.attributes[self.WEIGHT_LOSS_PERCENTAGE] = person.rand(
                    self.minLoss, self.maxLoss
                )
            else:
                person.attributes[self.WEIGHT_LOSS_BMI_PERCENTILE_CHANGE] = (
                    person.rand() * self.maxPedPercentileChange
                )
            success = person.rand() <= self.maintenance
            if trigger:
                success = True
                person.attributes[self.TRIGGER_WEIGHT_LOSS] = False
            person.attributes[self.LONG_TERM_WEIGHT_LOSS] = success
        else:
            person.attributes[self.LONG_TERM_WEIGHT_LOSS] = False

    def will_start_weight_management(self, person: Person, time: int) -> bool:
        """Java: WeightLossModule#willStartWeightManagement."""
        gain = person.attributes.get("kilograms_to_gain")
        if gain is not None and cast(float, gain) > 0.0:
            return False
        if (
            person.attributes.get(self.TRIGGER_WEIGHT_LOSS) is not None
            and person.attributes[self.TRIGGER_WEIGHT_LOSS]
        ):
            return True
        if self.meets_weight_management_thresholds(person, time):
            return person.rand() <= self.startWeightManagementProb
        return False

    def meets_weight_management_thresholds(self, person: Person, time: int) -> bool:
        """Java: WeightLossModule#meetsWeightManagementThresholds; age nineteen excluded."""
        age = person.age_in_years(time)
        if age == 19:
            return False
        bmi = person.get_vital_sign(VitalSign.BMI, time)
        cutoff = 500.0
        if 2 <= age < 20:
            months = person.age_in_months(time)
            gender = cast(str, person.attributes["gender"])
            cutoff = self.growthChart[ChartType.BMI].look_up(months, gender, self.startPercentile)
        return age >= self.managementStartAge and (
            (bmi >= self.startBMI and age >= 20) or (age < 20 and bmi >= cutoff)
        )


WeightLossModule.growthChart = GrowthChart.load_charts()
WeightLossModule.managementStartAge = cast(int, BiometricsConfig.get("min_age", 5))
WeightLossModule.startWeightManagementProb = cast(float, BiometricsConfig.get("start_prob", 0.493))
WeightLossModule.adherence = cast(float, BiometricsConfig.get("adherence", 0.605))
WeightLossModule.startBMI = cast(float, BiometricsConfig.get("start_bmi", 30.0))
WeightLossModule.startPercentile = cast(float, BiometricsConfig.get("start_percentile", 0.95))
WeightLossModule.minLoss = cast(float, BiometricsConfig.get("min_loss", 0.07))
WeightLossModule.maxLoss = cast(float, BiometricsConfig.get("max_loss", 0.1))
WeightLossModule.maintenance = cast(float, BiometricsConfig.get("maintenance", 0.2))
WeightLossModule.maxPedPercentileChange = cast(
    float, BiometricsConfig.get("max_ped_percentile_change", 0.1)
)
