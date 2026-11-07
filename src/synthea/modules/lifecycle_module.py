"""Java: org.mitre.synthea.modules.LifecycleModule."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar, cast

from synthea.engine.module import Module
from synthea.helpers.config import Config
from synthea.helpers.random_collection import RandomCollection
from synthea.helpers.simple_csv import SimpleCSV
from synthea.helpers.trending_value_generator import TrendingValueGenerator
from synthea.helpers.utilities import Utilities
from synthea.javacompat.collections import JavaHashMap
from synthea.javacompat.numbers import idiv, to_int64
from synthea.modules.blood_pressure_value_generator import BloodPressureValueGenerator, SysDias
from synthea.world.agents.behaviors.planeligibility.qualifying_condition_codes_eligibility import (
    QualifyingConditionCodesEligibility,
)
from synthea.world.agents.person import Person
from synthea.world.concepts.biometrics_config import BiometricsConfig
from synthea.world.concepts.birth_statistics import BirthStatistics
from synthea.world.concepts.bmi import BMI
from synthea.world.concepts.employment import Employment
from synthea.world.concepts.growth_chart import ChartType, GrowthChart
from synthea.world.concepts.growth_chart_entry import GrowthChartEntry
from synthea.world.concepts.health_record import Code, EncounterType
from synthea.world.concepts.names import Names
from synthea.world.concepts.pediatric_growth_trajectory import PediatricGrowthTrajectory
from synthea.world.concepts.vital_sign import VitalSign
from synthea.world.geography.location import Location

if TYPE_CHECKING:
    from synthea.helpers.random_number_generator import RandomNumberGenerator


@dataclass
class Inventory:
    """Java boundary: Attributes.Inventory, the read/write/example collection surface."""

    read: dict[str, set[str]] = field(default_factory=dict)
    write: dict[str, set[str]] = field(default_factory=dict)
    example_values: set[str] = field(default_factory=set)


class LifecycleModule(Module):
    """Java: org.mitre.synthea.modules.LifecycleModule."""

    growthChart: ClassVar[dict[ChartType, GrowthChart]]
    weightForLengthChart: ClassVar[list[dict[str, str]]]
    disabilityCriteria: ClassVar[QualifyingConditionCodesEligibility | None]
    AGE: ClassVar[str] = "AGE"
    AGE_MONTHS: ClassVar[str] = "AGE_MONTHS"
    DAYS_UNTIL_DEATH: ClassVar[str] = "days_until_death"
    QUIT_SMOKING_PROBABILITY: ClassVar[str] = "quit smoking probability"
    QUIT_SMOKING_AGE: ClassVar[str] = "quit smoking age"
    QUIT_ALCOHOLISM_PROBABILITY: ClassVar[str] = "quit alcoholism probability"
    QUIT_ALCOHOLISM_AGE: ClassVar[str] = "quit alcoholism age"
    ADHERENCE_PROBABILITY: ClassVar[str] = "adherence probability"
    COUNTRY_CODE: ClassVar[str | None] = Config.get("generate.geography.country_code")
    MIDDLE_NAME_PROBABILITY: ClassVar[float] = Config.get_as_double("generate.middle_names", 0.80)
    sexualOrientationData: ClassVar[RandomCollection[str]]
    ADULT_MAX_WEIGHT_AGE: ClassVar[int] = cast(
        int, BiometricsConfig.get("lifecycle.adult_max_weight_age", 49)
    )
    GERIATRIC_WEIGHT_LOSS_AGE: ClassVar[int] = cast(
        int, BiometricsConfig.get("lifecycle.geriatric_weight_loss_age", 60)
    )

    DIABETES_DRUG_HBA1C_IMPACTS: ClassVar[JavaHashMap[str, float]]
    ENABLE_DEATH_BY_NATURAL_CAUSES: ClassVar[bool] = Config.get_as_boolean(
        "lifecycle.death_by_natural_causes"
    )
    ENABLE_DEATH_BY_LOSS_OF_CARE: ClassVar[bool] = Config.get_as_boolean(
        "lifecycle.death_by_loss_of_care"
    )
    ENABLE_PHYSIOLOGY_GENERATORS: ClassVar[bool] = Config.get_as_boolean(
        "physiology.generators.enabled", False
    )
    NATURAL_CAUSES: ClassVar[Code] = Code(
        "SNOMED-CT", "9855000", "Natural death with unknown cause"
    )
    LOSS_OF_CARE: ClassVar[Code] = Code(
        "SNOMED-CT", "397709008", "Death due to Uncovered and Unreceived Treatment"
    )
    ADULT_WEIGHT_GAIN_RANGE: ClassVar[list[float]] = BiometricsConfig.doubles(
        "lifecycle.adult_weight_gain"
    )
    GERIATRIC_WEIGHT_LOSS_RANGE: ClassVar[list[float]] = BiometricsConfig.doubles(
        "lifecycle.geriatric_weight_loss"
    )
    CHOLESTEROL_RANGE: ClassVar[list[int]] = BiometricsConfig.ints(
        "metabolic.lipid_panel.cholesterol"
    )
    TRIGLYCERIDES_RANGE: ClassVar[list[int]] = BiometricsConfig.ints(
        "metabolic.lipid_panel.triglycerides"
    )
    HDL_RANGE: ClassVar[list[int]] = BiometricsConfig.ints("metabolic.lipid_panel.hdl")
    GLUCOSE_RANGE: ClassVar[list[int]] = BiometricsConfig.ints("metabolic.basic_panel.glucose")
    UREA_NITROGEN_RANGE: ClassVar[list[int]] = BiometricsConfig.ints(
        "metabolic.basic_panel.normal.urea_nitrogen"
    )
    CALCIUM_RANGE: ClassVar[list[float]] = BiometricsConfig.doubles(
        "metabolic.basic_panel.normal.calcium"
    )
    MILD_KIDNEY_DMG_CC_RANGE: ClassVar[list[int]] = BiometricsConfig.ints(
        "metabolic.basic_panel.creatinine_clearance.mild_kidney_damage"
    )
    MODERATE_KIDNEY_DMG_CC_RANGE: ClassVar[list[int]] = BiometricsConfig.ints(
        "metabolic.basic_panel.creatinine_clearance.moderate_kidney_damage"
    )
    SEVERE_KIDNEY_DMG_CC_RANGE: ClassVar[list[int]] = BiometricsConfig.ints(
        "metabolic.basic_panel.creatinine_clearance.severe_kidney_damage"
    )
    ESRD_CC_RANGE: ClassVar[list[int]] = BiometricsConfig.ints(
        "metabolic.basic_panel.creatinine_clearance.esrd"
    )
    NORMAL_FEMALE_CC_RANGE: ClassVar[list[int]] = BiometricsConfig.ints(
        "metabolic.basic_panel.creatinine_clearance.normal.female"
    )
    NORMAL_MALE_CC_RANGE: ClassVar[list[int]] = BiometricsConfig.ints(
        "metabolic.basic_panel.creatinine_clearance.normal.male"
    )
    NORMAL_MCR_RANGE: ClassVar[list[int]] = BiometricsConfig.ints(
        "metabolic.basic_panel.microalbumin_creatinine_ratio.normal"
    )
    CONTROLLED_MCR_RANGE: ClassVar[list[int]] = BiometricsConfig.ints(
        "metabolic.basic_panel.microalbumin_creatinine_ratio.microalbuminuria_controlled"
    )
    UNCONTROLLED_MCR_RANGE: ClassVar[list[int]] = BiometricsConfig.ints(
        "metabolic.basic_panel.microalbumin_creatinine_ratio.microalbuminuria_uncontrolled"
    )
    PROTEINURIA_MCR_RANGE: ClassVar[list[int]] = BiometricsConfig.ints(
        "metabolic.basic_panel.microalbumin_creatinine_ratio.proteinuria"
    )
    CHLORIDE_RANGE: ClassVar[list[float]] = BiometricsConfig.doubles(
        "metabolic.basic_panel.normal.chloride"
    )
    POTASSIUM_RANGE: ClassVar[list[float]] = BiometricsConfig.doubles(
        "metabolic.basic_panel.normal.potassium"
    )
    CO2_RANGE: ClassVar[list[float]] = BiometricsConfig.doubles(
        "metabolic.basic_panel.normal.carbon_dioxide"
    )
    SODIUM_RANGE: ClassVar[list[float]] = BiometricsConfig.doubles(
        "metabolic.basic_panel.normal.sodium"
    )
    BLOOD_OXYGEN_SATURATION_NORMAL: ClassVar[list[int]] = BiometricsConfig.ints(
        "cardiovascular.oxygen_saturation.normal"
    )
    BLOOD_OXYGEN_SATURATION_HYPOXEMIA: ClassVar[list[int]] = BiometricsConfig.ints(
        "cardiovascular.oxygen_saturation.hypoxemia"
    )
    HEART_RATE_NORMAL: ClassVar[list[float]] = BiometricsConfig.doubles(
        "cardiovascular.heart_rate.normal"
    )
    RESPIRATION_RATE_NORMAL: ClassVar[list[float]] = BiometricsConfig.doubles(
        "respiratory.respiration_rate.normal"
    )

    def __init__(self) -> None:
        """Java: LifecycleModule#LifecycleModule."""
        super().__init__()
        self.name = "Lifecycle"

    @staticmethod
    def load_weight_for_length_chart() -> list[dict[str, str]]:
        """Java: LifecycleModule#loadWeightForLengthChart."""
        return list(SimpleCSV.parse(Utilities.read_resource("cdc_wtleninf.csv")))

    @staticmethod
    def load_sexual_orientation_data() -> RandomCollection[str]:
        """Java: LifecycleModule#loadSexualOrientationData."""
        distribution = RandomCollection[str]()
        percentages = BiometricsConfig.doubles("lifecycle.sexual_orientation")
        for weight, value in zip(
            percentages, ("heterosexual", "homosexual", "bisexual"), strict=False
        ):
            distribution.add(weight, value)
        return distribution

    @staticmethod
    def load_disability_data() -> QualifyingConditionCodesEligibility | None:
        """Java: LifecycleModule#loadDisabilityData; a failed optional file yields null."""
        try:
            return QualifyingConditionCodesEligibility(
                "payers/eligibility_input_files/ssd_eligibility.csv"
            )
        except Exception as error:
            print(f"ERROR: unable to load disability csv: {error}", file=sys.stderr)
            return None

    def clone(self) -> Module:
        """Java: LifecycleModule#clone; stateless module shares its instance."""
        return self

    def process(self, person: Person, time: int, terminate_on_death: bool | None = None) -> bool:
        """Java: LifecycleModule#process."""
        if not person.alive(time):
            return True
        if self.age(person, time):
            self.grow(person, time)
        self.start_smoking(person, time)
        self.start_alcoholism(person, time)
        self.quit_smoking(person, time)
        self.quit_alcoholism(person, time)
        self.adherence(person, time)
        self.calculate_vital_signs(person, time)
        self.calculate_fall_risk(person, time)
        person.attributes[Person.DISABLED] = self.is_disabled(person, time)
        if person.age_in_years(time) >= 18:
            cast(Employment, person.attributes[Person.EMPLOYMENT_MODEL]).check_employment(
                person, time
            )
        self.death(person, time)
        return False

    @staticmethod
    def birth(person: Person, time: int) -> None:
        """Java: LifecycleModule#birth; retain every demographic and mother RNG draw."""
        attributes = person.attributes
        attributes[Person.ID] = str(person.rand_uuid())
        language = cast(str | None, attributes.get(Person.FIRST_LANGUAGE))
        gender = cast(str, attributes.get(Person.GENDER))
        if attributes.get(Person.ENTITY) is None:
            attributes[Person.BIRTHDATE] = time
            first = Names.fake_first_name(gender, language, person)
            last = Names.fake_last_name(language, person)
            attributes[Person.FIRST_NAME] = first
            if person.rand() <= LifecycleModule.MIDDLE_NAME_PROBABILITY:
                attributes[Person.MIDDLE_NAME] = Names.fake_first_name(gender, language, person)
            attributes[Person.LAST_NAME] = last
            attributes[Person.NAME] = first + " " + last
            attributes[Person.TELECOM] = (
                f"555-{person.rand_int(900) + 100}-{person.rand_int(9000) + 1000}"
            )
            line2 = person.rand() < 0.5
            attributes[Person.ADDRESS] = Names.fake_address(line2, person)
        mother_first = Names.fake_first_name("F", language, person)
        mother_last = Names.fake_last_name(language, person)
        attributes[Person.NAME_MOTHER] = mother_first + " " + mother_last
        father_first = Names.fake_first_name("M", language, person)
        attributes[Person.NAME_FATHER] = (
            father_first + " " + cast(str, attributes[Person.LAST_NAME])
        )
        prevalence = cast(float, BiometricsConfig.get("lifecycle.prevalence_of_twins", 0.02))
        if person.rand() < prevalence:
            attributes[Person.MULTIPLE_BIRTH_STATUS] = person.rand_int(3) + 1
        attributes[Person.IDENTIFIER_SSN] = (
            f"999-{person.rand_int(90) + 10}-{person.rand_int(9000) + 1000}"
        )
        city = cast(str, attributes.get(Person.CITY))
        location = cast(Location | None, attributes.get(Person.LOCATION))
        if location is not None:
            location.assign_point(person, city)
            zip_code = location.get_zip_code(city, cast("RandomNumberGenerator", person))
            attributes[Person.ZIP] = zip_code
            attributes[Person.FIPS] = Location.get_fips_code_by_zip_code(zip_code)
            if language is not None and language.lower() == "english":
                place = location.random_birth_place(cast("RandomNumberGenerator", person))
            else:
                place = location.random_birthplace_by_language(
                    cast("RandomNumberGenerator", person), cast(str, language)
                )
            for key, value in zip(
                (Person.BIRTH_CITY, Person.BIRTH_STATE, Person.BIRTH_COUNTRY, Person.BIRTHPLACE),
                place,
                strict=True,
            ):
                attributes[key] = value
        attributes[Person.ACTIVE_WEIGHT_MANAGEMENT] = False
        height_percentile = person.rand()
        trajectory = PediatricGrowthTrajectory(person.get_seed(), time, gender)
        weight_percentile = trajectory.reverse_weight_percentile(gender, height_percentile)
        head_percentile = height_percentile + person.rand(0.025, 0.025)
        if head_percentile < 0.01:
            head_percentile = 0.01
        elif head_percentile > 1:
            head_percentile = 1.0
        head_percentile = 100.0 * head_percentile
        person.set_vital_sign(VitalSign.HEIGHT_PERCENTILE, height_percentile)
        person.set_vital_sign(VitalSign.WEIGHT_PERCENTILE, weight_percentile)
        person.set_vital_sign(VitalSign.HEAD_PERCENTILE, head_percentile)
        attributes[Person.GROWTH_TRAJECTORY] = trajectory
        mother = Person(person.rand_long())
        mother.attributes[Person.GENDER] = "F"
        mother.attributes["pregnant"] = True
        mother.attributes[Person.RACE] = attributes.get(Person.RACE)
        mother.attributes[Person.ETHNICITY] = attributes.get(Person.ETHNICITY)
        mother.attributes[BirthStatistics.BIRTH_SEX] = attributes.get(Person.GENDER)
        BirthStatistics.set_birth_statistics(mother, time)
        person.set_vital_sign(
            VitalSign.HEIGHT, cast(float, mother.attributes[BirthStatistics.BIRTH_HEIGHT])
        )
        person.set_vital_sign(
            VitalSign.WEIGHT, cast(float, mother.attributes[BirthStatistics.BIRTH_WEIGHT])
        )
        person.set_vital_sign(
            VitalSign.HEAD, LifecycleModule.child_head_circumference(person, time)
        )
        attributes[LifecycleModule.AGE] = 0
        attributes[LifecycleModule.AGE_MONTHS] = 0
        attributes["RH_NEG"] = person.rand() < 0.15
        attributes[LifecycleModule.ADHERENCE_PROBABILITY] = Config.get_as_double(
            "lifecycle.adherence.baseline", 0.05
        )
        LifecycleModule.grow(person, time)
        LifecycleModule.calculate_vital_signs(person, time)
        attributes[Person.SEXUAL_ORIENTATION] = LifecycleModule.sexualOrientationData.next(person)
        LifecycleModule.setup_vital_sign_generators(person)

    @staticmethod
    def setup_vital_sign_generators(person: Person) -> None:
        """Java: LifecycleModule#setupVitalSignGenerators."""
        person.set_vital_sign(
            VitalSign.SYSTOLIC_BLOOD_PRESSURE, BloodPressureValueGenerator(person, SysDias.SYSTOLIC)
        )
        person.set_vital_sign(
            VitalSign.DIASTOLIC_BLOOD_PRESSURE,
            BloodPressureValueGenerator(person, SysDias.DIASTOLIC),
        )
        if LifecycleModule.ENABLE_PHYSIOLOGY_GENERATORS:
            raise NotImplementedError("Physiology generators are out of scope")

    @staticmethod
    def age(person: Person, time: int) -> bool:
        """Java: LifecycleModule#age."""
        a = person.attributes
        prev_age, prev_months = (
            cast(int, a[LifecycleModule.AGE]),
            cast(int, a[LifecycleModule.AGE_MONTHS]),
        )
        age, months = person.age_in_years(time), person.age_in_months(time)
        a[LifecycleModule.AGE], a[LifecycleModule.AGE_MONTHS] = age, months
        if age == 16:
            if a.get(Person.IDENTIFIER_DRIVERS) is None:
                a[Person.IDENTIFIER_DRIVERS] = "S999" + str(person.rand_int(90000) + 10000)
        elif age == 18:
            if a.get(Person.NAME_PREFIX) is None:
                a[Person.NAME_PREFIX] = "Mr." if a.get(Person.GENDER) == "M" else "Ms."
        elif age == 20:
            if a.get(Person.IDENTIFIER_PASSPORT) is None and person.rand() < 0.5:
                raise NotImplementedError("Passport/RIF identifiers are out of scope")
            if a.get("veteran") is not None and a.get("veteran_provider_reset") is None:
                a.pop(Person.CURRENTPROVIDER, None)
                for kind in EncounterType:
                    a.pop(Person.PREFERREDYPROVIDER + kind.to_string(), None)
                a["veteran_provider_reset"] = True
        elif age == 28:
            if a.get(Person.MARITAL_STATUS) is None:
                if person.rand() < 0.8:
                    a[Person.MARITAL_STATUS] = "M"
                    if a.get(Person.GENDER) == "F":
                        a[Person.NAME_PREFIX] = "Mrs."
                        a[Person.MAIDEN_NAME] = a.get(Person.LAST_NAME)
                        first = cast(str, a.get(Person.FIRST_NAME))
                        middle = cast(str | None, a.get(Person.MIDDLE_NAME))
                        last = Names.fake_last_name(
                            cast(str | None, a.get(Person.FIRST_LANGUAGE)), person
                        )
                        a[Person.LAST_NAME] = last
                        a[Person.NAME] = (
                            first + " " + ((middle + " ") if middle is not None else "") + last
                        )
                else:
                    a[Person.MARITAL_STATUS] = "S"
        elif age == 30:
            if (
                a.get(Person.NAME_SUFFIX) is None
                and cast(float, a.get(Person.EDUCATION_LEVEL)) >= 0.95
            ):
                a[Person.NAME_SUFFIX] = ("PhD", "JD", "MD")[person.rand_int(3)]
        elif age in (35, 45, 55):
            decade = str(age // 10)
            key = Person.MARITAL_STATUS + "Decade" + decade
            if a.get(key) is None:
                if a[Person.MARITAL_STATUS] == "M":
                    check = person.rand()
                    widow, divorce = {35: (0.02, 0.20), 45: (0.03, 0.05), 55: (0.06, 0.11)}[age]
                    if check < widow:
                        a[Person.MARITAL_STATUS] = "W"
                    elif check < divorce:
                        a[Person.MARITAL_STATUS] = "D"
                a[key] = True
        return age > prev_age if age >= 20 else months > prev_months

    @staticmethod
    def grow(person: Person, time: int) -> None:
        """Java: LifecycleModule#grow."""
        age = person.age_in_years(time)
        months = 0
        height = person.get_vital_sign(VitalSign.HEIGHT, time)
        if age < 20:
            height = LifecycleModule.child_height_growth(person, time)
            months = person.age_in_months(time)
        weight = LifecycleModule.adjust_weight(person, time)
        person.set_vital_sign(VitalSign.HEIGHT, height)
        person.set_vital_sign(VitalSign.WEIGHT, weight)
        bmi = BMI.calculate(height, weight)
        person.set_vital_sign(VitalSign.BMI, bmi)
        if age <= 3:
            LifecycleModule.set_current_weight_for_length_percentile(person, time)
            if months <= 36:
                person.set_vital_sign(
                    VitalSign.HEAD, LifecycleModule.child_head_circumference(person, time)
                )
        if 2 <= age < 20:
            gender = cast(str, person.attributes[Person.GENDER])
            percentile = LifecycleModule.percentile_for_bmi(bmi, gender, months)
            person.attributes[Person.BMI_PERCENTILE] = percentile * 100.0

    @staticmethod
    def child_height_growth(person: Person, time: int) -> float:
        """Java: LifecycleModule#childHeightGrowth."""
        return LifecycleModule.lookup_growth_chart(
            "height",
            cast(str, person.attributes[Person.GENDER]),
            person.age_in_months(time),
            person.get_vital_sign(VitalSign.HEIGHT_PERCENTILE, time),
        )

    @staticmethod
    def child_head_circumference(person: Person, time: int) -> float:
        """Java: LifecycleModule#childHeadCircumference."""
        return LifecycleModule.lookup_growth_chart(
            "head",
            cast(str, person.attributes[Person.GENDER]),
            person.age_in_months(time),
            person.get_vital_sign(VitalSign.HEAD_PERCENTILE, time) / 100.0,
        )

    @staticmethod
    def adjust_weight(person: Person, time: int) -> float:
        """Java: LifecycleModule#adjustWeight."""
        weight = person.get_vital_sign(VitalSign.WEIGHT, time)
        gender = cast(str, person.attributes[Person.GENDER])
        height_percentile = person.get_vital_sign(VitalSign.HEIGHT_PERCENTILE, time)
        trajectory = cast(PediatricGrowthTrajectory, person.attributes[Person.GROWTH_TRAJECTORY])
        age, months = person.age_in_years(time), person.age_in_months(time)
        if age < 3 and trajectory.before_initial_sample(time):
            weight = LifecycleModule.lookup_growth_chart(
                "weight", gender, months, person.get_vital_sign(VitalSign.WEIGHT_PERCENTILE, time)
            )
        elif age < 20:
            bmi = trajectory.current_bmi(person, time)
            height = LifecycleModule.growthChart[ChartType.HEIGHT].look_up(
                months, gender, height_percentile
            )
            weight = BMI.weight_for_height_and_bmi(height, bmi)
        else:
            management = person.attributes.get(Person.ACTIVE_WEIGHT_MANAGEMENT)
            if management is not None and not management:
                if age <= LifecycleModule.ADULT_MAX_WEIGHT_AGE:
                    weight += person.rand(LifecycleModule.ADULT_WEIGHT_GAIN_RANGE)
                elif age >= LifecycleModule.GERIATRIC_WEIGHT_LOSS_AGE:
                    weight -= person.rand(LifecycleModule.GERIATRIC_WEIGHT_LOSS_RANGE)
            to_gain = cast(float | None, person.attributes.get(Person.KILOGRAMS_TO_GAIN))
            if to_gain is not None and to_gain > 0.0:
                gain = person.rand(LifecycleModule.ADULT_WEIGHT_GAIN_RANGE)
                weight += gain
                person.attributes[Person.KILOGRAMS_TO_GAIN] = to_gain - gain
        return weight

    @staticmethod
    def lookup_growth_chart(
        chart_type: str, gender: str, age_in_months: int, percentile: float
    ) -> float:
        """Java: LifecycleModule#lookupGrowthChart."""
        try:
            kind = {
                "height": ChartType.HEIGHT,
                "weight": ChartType.WEIGHT,
                "bmi": ChartType.BMI,
                "head": ChartType.HEAD,
            }[chart_type]
        except KeyError as error:
            raise ValueError("Unknown chart type: " + chart_type) from error
        return LifecycleModule.growthChart[kind].look_up(age_in_months, gender, percentile)

    @staticmethod
    def percentile_for_bmi(bmi: float, gender: str, age_in_months: int) -> float:
        """Java: LifecycleModule#percentileForBMI."""
        return LifecycleModule.growthChart[ChartType.BMI].percentile_for(age_in_months, gender, bmi)

    @staticmethod
    def set_current_weight_for_length_percentile(person: Person, time: int) -> None:
        """Java: LifecycleModule#setCurrentWeightForLengthPercentile; do not remove stale values."""
        if person.age_in_months(time) <= 36:
            height = person.get_vital_sign(VitalSign.HEIGHT, time)
            weight = person.get_vital_sign(VitalSign.WEIGHT, time)
            gender = person.attributes[Person.GENDER]
            row = next(
                (
                    row
                    for row in LifecycleModule.weightForLengthChart
                    if row["Sex"] == gender and height < float(row["Length"])
                ),
                None,
            )
            if row is None:
                person.attributes[Person.CURRENT_WEIGHT_LENGTH_PERCENTILE] = 99.0
            else:
                z = GrowthChartEntry(
                    float(row["L"]), float(row["M"]), float(row["S"])
                ).zscore_for_value(weight)
                person.attributes[Person.CURRENT_WEIGHT_LENGTH_PERCENTILE] = (
                    GrowthChart.zscore_to_percentile(z) * 100.0
                )

    @staticmethod
    def create_drug_impacts_map() -> JavaHashMap[str, float]:
        """Java: LifecycleModule#createDrugImpactsMap; HashMap iteration affects floating sums."""
        impacts: JavaHashMap[str, float] = JavaHashMap()
        for code, impact in (
            ("860975", -1.5),
            ("897122", -0.5),
            ("1373463", -0.5),
            ("106892", -3.0),
            ("865098", -6.0),
        ):
            impacts[code] = impact
        return impacts

    @staticmethod
    def calculate_vital_signs(person: Person, time: int) -> None:
        """Java: LifecycleModule#calculateVitalSigns."""
        a = person.attributes
        index = cast(int, a.get("diabetes_severity", 1)) if "diabetes_severity" in a else 0
        triglycerides = person.rand(
            LifecycleModule.TRIGLYCERIDES_RANGE[index],
            LifecycleModule.TRIGLYCERIDES_RANGE[index + 1],
        )
        if index == 0:
            if "low_hdl" in a:
                low_hdl = cast(bool, a["low_hdl"])
                high_total = cast(bool, a["high_total_chol"])
            else:
                chance = 0.085 if a.get(Person.GENDER) == "F" else 0.266
                low_hdl = person.rand() < chance
                a["low_hdl"] = low_hdl
                high_total = person.rand() < 0.114
                a["high_total_chol"] = high_total
            hdl = 3 * person.rand_gaussian() + 30 if low_hdl else 5 * person.rand_gaussian() + 55
            total = (
                20 * person.rand_gaussian() + 280
                if high_total
                else 30 * person.rand_gaussian() + 170
            )
        else:
            total = person.rand(
                LifecycleModule.CHOLESTEROL_RANGE[index],
                LifecycleModule.CHOLESTEROL_RANGE[index + 1],
            )
            hdl = person.rand(
                LifecycleModule.HDL_RANGE[index], LifecycleModule.HDL_RANGE[index + 1]
            )
        ldl = total - hdl - (0.2 * triglycerides)
        person.set_vital_sign(VitalSign.TOTAL_CHOLESTEROL, total)
        person.set_vital_sign(VitalSign.TRIGLYCERIDES, triglycerides)
        person.set_vital_sign(VitalSign.HDL, hdl)
        person.set_vital_sign(VitalSign.LDL, ldl)
        bmi = person.get_vital_sign(VitalSign.BMI, time)
        prediabetes, diabetes = (
            cast(bool, a.get("prediabetes", False)),
            cast(bool, a.get("diabetes", False)),
        )
        hba1c = LifecycleModule.estimate_hb_a1c(bmi, prediabetes, diabetes, person)
        assert person.record is not None
        if prediabetes or diabetes:
            for code, impact in LifecycleModule.DIABETES_DRUG_HBA1C_IMPACTS.items():
                if person.record.medication_active(code):
                    hba1c += impact
        person.set_vital_sign(VitalSign.BLOOD_GLUCOSE, hba1c)
        oxygen = (
            LifecycleModule.BLOOD_OXYGEN_SATURATION_HYPOXEMIA
            if "chf" in a
            else LifecycleModule.BLOOD_OXYGEN_SATURATION_NORMAL
        )
        person.set_vital_sign(VitalSign.OXYGEN_SATURATION, float(int(person.rand(oxygen))))
        damage = cast(int, a.get("ckd", 0))
        ranges = {
            1: (LifecycleModule.MILD_KIDNEY_DMG_CC_RANGE, LifecycleModule.NORMAL_MCR_RANGE),
            2: (LifecycleModule.MODERATE_KIDNEY_DMG_CC_RANGE, LifecycleModule.CONTROLLED_MCR_RANGE),
            3: (LifecycleModule.SEVERE_KIDNEY_DMG_CC_RANGE, LifecycleModule.UNCONTROLLED_MCR_RANGE),
            4: (LifecycleModule.ESRD_CC_RANGE, LifecycleModule.PROTEINURIA_MCR_RANGE),
        }
        normal = (
            LifecycleModule.NORMAL_FEMALE_CC_RANGE
            if a.get(Person.GENDER) == "F"
            else LifecycleModule.NORMAL_MALE_CC_RANGE
        )
        cc_range, mcr_range = ranges.get(damage, (normal, LifecycleModule.NORMAL_MCR_RANGE))
        clearance = person.rand(cc_range)
        person.set_vital_sign(VitalSign.EGFR, clearance)
        person.set_vital_sign(VitalSign.MICROALBUMIN_CREATININE_RATIO, person.rand(mcr_range))
        person.set_vital_sign(
            VitalSign.CREATININE,
            LifecycleModule.reverse_calculate_creatinine(person, clearance, time),
        )
        person.set_vital_sign(
            VitalSign.UREA_NITROGEN, person.rand(LifecycleModule.UREA_NITROGEN_RANGE)
        )
        person.set_vital_sign(VitalSign.CALCIUM, person.rand(LifecycleModule.CALCIUM_RANGE))
        index = min(index, 2)
        glucose = person.rand(
            LifecycleModule.GLUCOSE_RANGE[index], LifecycleModule.GLUCOSE_RANGE[index + 1]
        )
        person.set_vital_sign(VitalSign.GLUCOSE, glucose)
        person.set_vital_sign(VitalSign.CHLORIDE, person.rand(LifecycleModule.CHLORIDE_RANGE))
        person.set_vital_sign(VitalSign.POTASSIUM, person.rand(LifecycleModule.POTASSIUM_RANGE))
        person.set_vital_sign(VitalSign.CARBON_DIOXIDE, person.rand(LifecycleModule.CO2_RANGE))
        person.set_vital_sign(VitalSign.SODIUM, person.rand(LifecycleModule.SODIUM_RANGE))
        timestep = Config.get_as_long("generate.timestep")
        heart_start, heart_end = (
            person.rand(LifecycleModule.HEART_RATE_NORMAL),
            person.rand(LifecycleModule.HEART_RATE_NORMAL),
        )
        person.set_vital_sign(
            VitalSign.HEART_RATE,
            TrendingValueGenerator(
                person,
                1.0,
                heart_start,
                heart_end,
                time,
                to_int64(time + timestep),
                LifecycleModule.HEART_RATE_NORMAL[0],
                LifecycleModule.HEART_RATE_NORMAL[1],
            ),
        )
        respiration_start, respiration_end = (
            person.rand(LifecycleModule.RESPIRATION_RATE_NORMAL),
            person.rand(LifecycleModule.RESPIRATION_RATE_NORMAL),
        )
        person.set_vital_sign(
            VitalSign.RESPIRATION_RATE,
            TrendingValueGenerator(
                person,
                1.0,
                respiration_start,
                respiration_end,
                time,
                to_int64(time + timestep),
                LifecycleModule.RESPIRATION_RATE_NORMAL[0],
                LifecycleModule.RESPIRATION_RATE_NORMAL[1],
            ),
        )

    @staticmethod
    def estimate_hb_a1c(bmi: float, prediabetes: bool, diabetes: bool, p: Person) -> float:
        """Java: LifecycleModule#estimateHbA1c."""
        if diabetes:
            if bmi > 48.0:
                return 12.0
            if bmi <= 27.0:
                return 6.6
            return bmi / 4.0
        if prediabetes:
            return p.rand(5.8, 6.4)
        return p.rand(5.0, 5.7)

    @staticmethod
    def reverse_calculate_creatinine(person: Person, crcl: float, time: int) -> float:
        """Java: LifecycleModule#reverseCalculateCreatinine; missing vitals yield 1.0."""
        try:
            age = person.age_in_years(time)
            female = person.attributes.get(Person.GENDER) == "F"
            weight = person.get_vital_sign(VitalSign.WEIGHT, time)
            crcl = max(1.0, min(crcl, 100.0))
            creatinine = ((140.0 - age) * weight) / (72.0 * crcl)
            if female:
                creatinine *= 0.85
            return creatinine
        except Exception:
            return 1.0

    @staticmethod
    def death(person: Person, time: int) -> None:
        """Java: LifecycleModule#death."""
        if LifecycleModule.ENABLE_DEATH_BY_NATURAL_CAUSES:
            roll = person.rand()
            likelihood = LifecycleModule.likelihood_of_death(person.age_in_years(time))
            if roll < likelihood:
                person.record_death(time, LifecycleModule.NATURAL_CAUSES)
        if LifecycleModule.ENABLE_DEATH_BY_LOSS_OF_CARE and LifecycleModule.death_from_loss_of_care(
            person
        ):
            person.record_death(time, LifecycleModule.LOSS_OF_CARE)
        if Person.DEATHDATE in person.attributes:
            diff = to_int64(cast(int, person.attributes[Person.DEATHDATE]) - time)
            person.attributes[LifecycleModule.DAYS_UNTIL_DEATH] = idiv(diff, 86400000)

    @staticmethod
    def likelihood_of_death(age: int) -> float:
        """Java: LifecycleModule#likelihoodOfDeath."""
        if age < 1:
            yearly = 508.1
        elif age <= 4:
            yearly = 15.6
        elif age <= 14:
            yearly = 10.6
        elif age <= 24:
            yearly = 56.4
        elif age <= 34:
            yearly = 74.7
        elif age <= 44:
            yearly = 145.7
        elif age <= 54:
            yearly = 326.5
        elif age <= 64:
            yearly = 737.8
        elif age <= 74:
            yearly = 1817.0
        elif age <= 84:
            yearly = 4877.3
        elif age <= 94:
            yearly = 13499.4
        else:
            yearly = 50000.0
        return Utilities.convert_risk_to_timestep(yearly / 100000.0, float(365 * 86400000))

    @staticmethod
    def death_from_loss_of_care(person: Person) -> bool:
        """Java: LifecycleModule#deathFromLossOfCare."""
        if person.loss_of_care_enabled:
            assert person.loss_of_care_record is not None
            for encounter in person.loss_of_care_record.encounters:
                for procedure in encounter.procedures:
                    for code in procedure.codes:
                        if code.code == "33195004":
                            return person.rand() < 0.6
        return False

    @staticmethod
    def start_smoking(person: Person, time: int) -> None:
        """Java: LifecycleModule#startSmoking."""
        if person.attributes.get(Person.SMOKER) is None and person.age_in_years(time) == 16:
            smoker = person.rand() < LifecycleModule.likelihood_of_being_a_smoker(
                Utilities.get_year(time)
            )
            person.attributes[Person.SMOKER] = smoker
            person.attributes[LifecycleModule.QUIT_SMOKING_PROBABILITY] = Config.get_as_double(
                "lifecycle.quit_smoking.baseline", 0.01
            )

    @staticmethod
    def likelihood_of_being_a_smoker(year: int) -> float:
        """Java: LifecycleModule#likelihoodOfBeingASmoker."""
        return 0.424 if year < 1965 else ((year * -0.4865) + 996.41) / 100.0

    @staticmethod
    def start_alcoholism(person: Person, time: int) -> None:
        """Java: LifecycleModule#startAlcoholism."""
        if person.attributes.get(Person.ALCOHOLIC) is None and person.age_in_years(time) == 25:
            person.attributes[Person.ALCOHOLIC] = person.rand() < 0.025
            person.attributes[LifecycleModule.QUIT_ALCOHOLISM_PROBABILITY] = Config.get_as_double(
                "lifecycle.quit_alcoholism.baseline", 0.05
            )

    @staticmethod
    def quit_smoking(person: Person, time: int) -> None:
        """Java: LifecycleModule#quitSmoking."""
        if person.attributes.get(Person.SMOKER) is True:
            probability = cast(float, person.attributes[LifecycleModule.QUIT_SMOKING_PROBABILITY])
            if person.rand() < probability:
                person.attributes[Person.SMOKER] = False
                person.attributes[LifecycleModule.QUIT_SMOKING_AGE] = person.age_in_years(time)
            else:
                baseline = Config.get_as_double("lifecycle.quit_smoking.baseline", 0.01)
                probability += Config.get_as_double("lifecycle.quit_smoking.timestep_delta", -0.1)
                if probability < baseline:
                    probability = baseline
                person.attributes[LifecycleModule.QUIT_SMOKING_PROBABILITY] = probability

    @staticmethod
    def quit_alcoholism(person: Person, time: int) -> None:
        """Java: LifecycleModule#quitAlcoholism."""
        if person.attributes.get(Person.ALCOHOLIC) is True:
            probability = cast(
                float, person.attributes[LifecycleModule.QUIT_ALCOHOLISM_PROBABILITY]
            )
            if person.rand() < probability:
                person.attributes[Person.ALCOHOLIC] = False
                person.attributes[LifecycleModule.QUIT_ALCOHOLISM_AGE] = person.age_in_years(time)
            else:
                baseline = Config.get_as_double("lifecycle.quit_alcoholism.baseline", 0.01)
                probability += Config.get_as_double(
                    "lifecycle.quit_alcoholism.timestep_delta", -0.1
                )
                if probability < baseline:
                    probability = baseline
                person.attributes[LifecycleModule.QUIT_ALCOHOLISM_PROBABILITY] = probability

    @staticmethod
    def adherence(person: Person, time: int) -> None:
        """Java: LifecycleModule#adherence."""
        if Person.ADHERENCE in person.attributes:
            probability = cast(float, person.attributes[LifecycleModule.ADHERENCE_PROBABILITY])
            baseline = Config.get_as_double("lifecycle.adherence.baseline", 0.05)
            probability += Config.get_as_double("lifecycle.adherence.timestep_delta", -0.01)
            if probability < baseline:
                probability = baseline
            person.attributes[LifecycleModule.ADHERENCE_PROBABILITY] = probability

    def calculate_fall_risk(self, person: Person, time: int) -> None:
        """Java: LifecycleModule#calculateFallRisk."""
        if person.age_in_years(time) >= 65:
            baseline = 0.06 if person.attributes.get("osteoporosis", False) else 0.035
            interventions = 0
            assert person.record is not None
            if person.record.careplan_active(
                "Physical therapy procedure"
            ) or person.record.careplan_active("Physical activity target light exercise"):
                interventions += 1
            if person.record.medication_active("Cholecalciferol 600 UNT"):
                interventions += 1
            if person.record.condition_active("Osteoporosis (disorder)"):
                interventions += 1
            person.attributes["probability_of_fall_injury"] = baseline * (1 - 0.02 * interventions)

    @staticmethod
    def is_disabled(person: Person, time: int) -> bool:
        """Java: LifecycleModule#isDisabled."""
        criteria = LifecycleModule.disabilityCriteria
        return criteria.is_person_eligible(person, time) if criteria is not None else False

    @staticmethod
    def get_earliest_disability_diagnosis_time(person: Person) -> int:
        """Java: LifecycleModule#getEarliestDisabilityDiagnosisTime."""
        criteria = LifecycleModule.disabilityCriteria
        return (
            criteria.get_earliest_diagnosis(person) if criteria is not None else 9223372036854775807
        )

    @staticmethod
    def get_all_codes() -> list[Code]:
        """Java: LifecycleModule#getAllCodes."""
        return [LifecycleModule.NATURAL_CAUSES]

    @staticmethod
    def inventory_attributes(attributes: dict[str, Inventory]) -> None:
        """Java: LifecycleModule#inventoryAttributes, collecting only this module's entries."""
        for attribute, read, write, example in _INVENTORY:
            item = attributes.setdefault(attribute, Inventory())
            if read:
                item.read.setdefault("LifecycleModule", set())
            if write:
                item.write.setdefault("LifecycleModule", set())
                if example is not None:
                    item.example_values.add(example)


LifecycleModule.growthChart = GrowthChart.load_charts()
LifecycleModule.weightForLengthChart = LifecycleModule.load_weight_for_length_chart()
LifecycleModule.disabilityCriteria = LifecycleModule.load_disability_data()
LifecycleModule.sexualOrientationData = LifecycleModule.load_sexual_orientation_data()
LifecycleModule.DIABETES_DRUG_HBA1C_IMPACTS = LifecycleModule.create_drug_impacts_map()

_INVENTORY: list[tuple[str, bool, bool, str | None]] = [
    (Person.ADHERENCE, True, False, None),
    (LifecycleModule.ADHERENCE_PROBABILITY, True, False, "1.0"),
    (LifecycleModule.AGE, True, False, None),
    (LifecycleModule.AGE_MONTHS, True, False, None),
    (Person.ALCOHOLIC, True, False, None),
    ("ckd", True, False, None),
    ("diabetes", True, False, None),
    ("diabetes_severity", True, False, None),
    (Person.EDUCATION_LEVEL, True, False, None),
    (Person.ETHNICITY, True, False, None),
    (Person.FIRST_NAME, True, False, None),
    (Person.FIRST_LANGUAGE, True, False, None),
    (Person.GENDER, True, False, "M"),
    (Person.IDENTIFIER_DRIVERS, True, False, None),
    (Person.IDENTIFIER_PASSPORT, True, False, None),
    (Person.LAST_NAME, True, False, None),
    (Person.NAME_PREFIX, True, False, None),
    (Person.NAME_SUFFIX, True, False, None),
    (Person.MARITAL_STATUS, True, False, None),
    (Person.MIDDLE_NAME, True, True, None),
    ("osteoporosis", True, False, None),
    ("prediabetes", True, False, None),
    (LifecycleModule.QUIT_ALCOHOLISM_PROBABILITY, True, False, None),
    (LifecycleModule.QUIT_SMOKING_PROBABILITY, True, False, None),
    (Person.RACE, True, False, None),
    (Person.SMOKER, True, False, "Boolean"),
    (Person.DEATHDATE, True, False, "1046327126000"),
    ("pregnant", False, True, "Boolean"),
    ("probability_of_fall_injury", False, True, "1.0"),
    ("RH_NEG", False, True, "Boolean"),
    (LifecycleModule.ADHERENCE_PROBABILITY, False, True, "1.0"),
    (LifecycleModule.AGE, False, True, "Numeric"),
    (LifecycleModule.AGE_MONTHS, False, True, "Numeric"),
    (BirthStatistics.BIRTH_SEX, False, True, "M"),
    (LifecycleModule.QUIT_SMOKING_PROBABILITY, False, True, "1.0"),
    (Person.ADDRESS, False, True, None),
    (Person.ALCOHOLIC, False, True, "Boolean"),
    (Person.BIRTH_CITY, False, True, "Bedford"),
    (Person.BIRTH_COUNTRY, False, True, LifecycleModule.COUNTRY_CODE),
    (Person.BIRTH_STATE, False, True, "Massachusetts"),
    (Person.BIRTHDATE, False, True, None),
    (Person.BIRTHPLACE, False, True, "Boston"),
    (Person.ETHNICITY, False, True, None),
    (Person.FIRST_NAME, False, True, None),
    (Person.GENDER, False, True, "F"),
    (Person.ID, False, True, None),
    (Person.IDENTIFIER_DRIVERS, False, True, None),
    (Person.IDENTIFIER_PASSPORT, False, True, None),
    (Person.IDENTIFIER_SSN, False, True, "999-99-9999"),
    (Person.LAST_NAME, False, True, None),
    (Person.MAIDEN_NAME, False, True, None),
    (Person.MARITAL_STATUS, False, True, "M"),
    (Person.MULTIPLE_BIRTH_STATUS, False, True, "Boolean"),
    (Person.NAME, False, True, None),
    (Person.NAME_FATHER, False, True, None),
    (Person.NAME_MOTHER, False, True, None),
    (Person.NAME_PREFIX, False, True, None),
    (Person.NAME_SUFFIX, False, True, None),
    (Person.RACE, False, True, None),
    (Person.SEXUAL_ORIENTATION, False, True, None),
    (Person.SMOKER, False, True, "Boolean"),
    (Person.TELECOM, False, True, "555-555-5555"),
    (Person.ZIP, False, True, "01730"),
    (LifecycleModule.QUIT_ALCOHOLISM_AGE, False, True, "Numeric"),
    (LifecycleModule.QUIT_ALCOHOLISM_PROBABILITY, False, True, "1.0"),
    (LifecycleModule.QUIT_SMOKING_AGE, False, True, "Numeric"),
    (LifecycleModule.QUIT_SMOKING_PROBABILITY, False, True, "1.0"),
    (LifecycleModule.DAYS_UNTIL_DEATH, False, True, "42"),
]
