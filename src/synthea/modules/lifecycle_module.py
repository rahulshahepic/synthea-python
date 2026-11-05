"""Java API skeleton: LifecycleModule.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Protocol

from synthea.world.concepts.health_record import Code

if TYPE_CHECKING:
    from synthea.engine.module import Module
    from synthea.helpers.random_collection import RandomCollection
    from synthea.world.agents.behaviors.planeligibility import (
        qualifying_condition_codes_eligibility as condition_eligibility,
    )
    from synthea.world.agents.person import Person
    from synthea.world.concepts.growth_chart import ChartType as GrowthChartChartType
    from synthea.world.concepts.growth_chart import GrowthChart
    from synthea.world.concepts.health_record import Code

    class Inventory(Protocol):
        """Java boundary type: Inventory; external to the mapped Python port."""


class LifecycleModule:
    """Java: LifecycleModule; pending T21."""

    growthChart: ClassVar[
        dict[GrowthChartChartType, GrowthChart]
    ]  # Java initialization deferred to T21.
    weightForLengthChart: ClassVar[list[dict[str, str]]]  # Java initialization deferred to T21.
    disabilityCriteria: ClassVar[
        condition_eligibility.QualifyingConditionCodesEligibility
    ]  # Java initialization deferred to T21.
    AGE: ClassVar[str] = "AGE"
    AGE_MONTHS: ClassVar[str] = "AGE_MONTHS"
    DAYS_UNTIL_DEATH: ClassVar[str] = "days_until_death"
    QUIT_SMOKING_PROBABILITY: ClassVar[str] = "quit smoking probability"
    QUIT_SMOKING_AGE: ClassVar[str] = "quit smoking age"
    QUIT_ALCOHOLISM_PROBABILITY: ClassVar[str] = "quit alcoholism probability"
    QUIT_ALCOHOLISM_AGE: ClassVar[str] = "quit alcoholism age"
    ADHERENCE_PROBABILITY: ClassVar[str] = "adherence probability"
    COUNTRY_CODE: ClassVar[str]  # Java initialization deferred to T21.
    MIDDLE_NAME_PROBABILITY: ClassVar[float]  # Java initialization deferred to T21.
    sexualOrientationData: ClassVar[RandomCollection[str]]  # Java initialization deferred to T21.
    ADULT_MAX_WEIGHT_AGE: ClassVar[int]  # Java initialization deferred to T21.
    GERIATRIC_WEIGHT_LOSS_AGE: ClassVar[int]  # Java initialization deferred to T21.
    ADULT_WEIGHT_GAIN_RANGE: ClassVar[list[float]]  # Java initialization deferred to T21.
    GERIATRIC_WEIGHT_LOSS_RANGE: ClassVar[list[float]]  # Java initialization deferred to T21.
    DIABETES_DRUG_HBA1C_IMPACTS: ClassVar[dict[str, float]] = {
        "860975": -1.5,
        "897122": -0.5,
        "1373463": -0.5,
        "106892": -3.0,
        "865098": -6.0,
    }
    CHOLESTEROL_RANGE: ClassVar[list[int]]  # Java initialization deferred to T21.
    TRIGLYCERIDES_RANGE: ClassVar[list[int]]  # Java initialization deferred to T21.
    HDL_RANGE: ClassVar[list[int]]  # Java initialization deferred to T21.
    GLUCOSE_RANGE: ClassVar[list[int]]  # Java initialization deferred to T21.
    UREA_NITROGEN_RANGE: ClassVar[list[int]]  # Java initialization deferred to T21.
    CALCIUM_RANGE: ClassVar[list[float]]  # Java initialization deferred to T21.
    MILD_KIDNEY_DMG_CC_RANGE: ClassVar[list[int]]  # Java initialization deferred to T21.
    MODERATE_KIDNEY_DMG_CC_RANGE: ClassVar[list[int]]  # Java initialization deferred to T21.
    SEVERE_KIDNEY_DMG_CC_RANGE: ClassVar[list[int]]  # Java initialization deferred to T21.
    ESRD_CC_RANGE: ClassVar[list[int]]  # Java initialization deferred to T21.
    NORMAL_FEMALE_CC_RANGE: ClassVar[list[int]]  # Java initialization deferred to T21.
    NORMAL_MALE_CC_RANGE: ClassVar[list[int]]  # Java initialization deferred to T21.
    NORMAL_MCR_RANGE: ClassVar[list[int]]  # Java initialization deferred to T21.
    CONTROLLED_MCR_RANGE: ClassVar[list[int]]  # Java initialization deferred to T21.
    UNCONTROLLED_MCR_RANGE: ClassVar[list[int]]  # Java initialization deferred to T21.
    PROTEINURIA_MCR_RANGE: ClassVar[list[int]]  # Java initialization deferred to T21.
    CHLORIDE_RANGE: ClassVar[list[float]]  # Java initialization deferred to T21.
    POTASSIUM_RANGE: ClassVar[list[float]]  # Java initialization deferred to T21.
    CO2_RANGE: ClassVar[list[float]]  # Java initialization deferred to T21.
    SODIUM_RANGE: ClassVar[list[float]]  # Java initialization deferred to T21.
    BLOOD_OXYGEN_SATURATION_NORMAL: ClassVar[list[int]]  # Java initialization deferred to T21.
    BLOOD_OXYGEN_SATURATION_HYPOXEMIA: ClassVar[list[int]]  # Java initialization deferred to T21.
    HEART_RATE_NORMAL: ClassVar[list[float]]  # Java initialization deferred to T21.
    RESPIRATION_RATE_NORMAL: ClassVar[list[float]]  # Java initialization deferred to T21.
    ENABLE_DEATH_BY_NATURAL_CAUSES: ClassVar[bool]  # Java initialization deferred to T21.
    ENABLE_DEATH_BY_LOSS_OF_CARE: ClassVar[bool]  # Java initialization deferred to T21.
    ENABLE_PHYSIOLOGY_GENERATORS: ClassVar[bool]  # Java initialization deferred to T21.
    NATURAL_CAUSES: ClassVar[Code]  # Java initialization deferred to T21.
    LOSS_OF_CARE: ClassVar[Code]  # Java initialization deferred to T21.

    def __init__(self) -> None:
        """Java: LifecycleModule#LifecycleModule.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: LifecycleModule#LifecycleModule — pending T21")

    @staticmethod
    def load_weight_for_length_chart() -> list[dict[str, str]]:
        """Java: LifecycleModule#loadWeightForLengthChart.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: LifecycleModule#loadWeightForLengthChart — pending T21")

    @staticmethod
    def load_sexual_orientation_data() -> RandomCollection[str]:
        """Java: LifecycleModule#loadSexualOrientationData.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: LifecycleModule#loadSexualOrientationData — pending T21")

    @staticmethod
    def load_disability_data() -> condition_eligibility.QualifyingConditionCodesEligibility:
        """Java: LifecycleModule#loadDisabilityData.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: LifecycleModule#loadDisabilityData — pending T21")

    def clone(self) -> Module:
        """Java: LifecycleModule#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: LifecycleModule#clone — pending T21")

    def process(self, person: Person, time: int) -> bool:
        """Java: LifecycleModule#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: LifecycleModule#process — pending T21")

    @staticmethod
    def birth(person: Person, time: int) -> None:
        """Java: LifecycleModule#birth.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: LifecycleModule#birth — pending T21")

    @staticmethod
    def setup_vital_sign_generators(person: Person) -> None:
        """Java: LifecycleModule#setupVitalSignGenerators.

        Java overloads:
        (Person person)
        """
        raise NotImplementedError("Java: LifecycleModule#setupVitalSignGenerators — pending T21")

    @staticmethod
    def age(person: Person, time: int) -> bool:
        """Java: LifecycleModule#age.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: LifecycleModule#age — pending T21")

    @staticmethod
    def grow(person: Person, time: int) -> None:
        """Java: LifecycleModule#grow.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: LifecycleModule#grow — pending T21")

    @staticmethod
    def child_height_growth(person: Person, time: int) -> float:
        """Java: LifecycleModule#childHeightGrowth.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: LifecycleModule#childHeightGrowth — pending T21")

    @staticmethod
    def child_head_circumference(person: Person, time: int) -> float:
        """Java: LifecycleModule#childHeadCircumference.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: LifecycleModule#childHeadCircumference — pending T21")

    @staticmethod
    def adjust_weight(person: Person, time: int) -> float:
        """Java: LifecycleModule#adjustWeight.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: LifecycleModule#adjustWeight — pending T21")

    @staticmethod
    def lookup_growth_chart(
        chart_type: str, gender: str, age_in_months: int, percentile: float
    ) -> float:
        """Java: LifecycleModule#lookupGrowthChart.

        Java overloads:
        (String chartType, String gender, int ageInMonths, double percentile)
        """
        raise NotImplementedError("Java: LifecycleModule#lookupGrowthChart — pending T21")

    @staticmethod
    def percentile_for_bmi(bmi: float, gender: str, age_in_months: int) -> float:
        """Java: LifecycleModule#percentileForBMI.

        Java overloads:
        (double bmi, String gender, int ageInMonths)
        """
        raise NotImplementedError("Java: LifecycleModule#percentileForBMI — pending T21")

    @staticmethod
    def set_current_weight_for_length_percentile(person: Person, time: int) -> None:
        """Java: LifecycleModule#setCurrentWeightForLengthPercentile.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError(
            "Java: LifecycleModule#setCurrentWeightForLengthPercentile — pending T21"
        )

    @staticmethod
    def create_drug_impacts_map() -> dict[str, float]:
        """Java: LifecycleModule#createDrugImpactsMap.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: LifecycleModule#createDrugImpactsMap — pending T21")

    @staticmethod
    def calculate_vital_signs(person: Person, time: int) -> None:
        """Java: LifecycleModule#calculateVitalSigns.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: LifecycleModule#calculateVitalSigns — pending T21")

    @staticmethod
    def estimate_hb_a1c(bmi: float, prediabetes: bool, diabetes: bool, p: Person) -> float:
        """Java: LifecycleModule#estimateHbA1c.

        Java overloads:
        (double bmi, boolean prediabetes, boolean diabetes, Person p)
        """
        raise NotImplementedError("Java: LifecycleModule#estimateHbA1c — pending T21")

    @staticmethod
    def reverse_calculate_creatinine(person: Person, crcl: float, time: int) -> float:
        """Java: LifecycleModule#reverseCalculateCreatinine.

        Java overloads:
        (Person person, double crcl, long time)
        """
        raise NotImplementedError("Java: LifecycleModule#reverseCalculateCreatinine — pending T21")

    @staticmethod
    def death(person: Person, time: int) -> None:
        """Java: LifecycleModule#death.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: LifecycleModule#death — pending T21")

    @staticmethod
    def likelihood_of_death(age: int) -> float:
        """Java: LifecycleModule#likelihoodOfDeath.

        Java overloads:
        (int age)
        """
        raise NotImplementedError("Java: LifecycleModule#likelihoodOfDeath — pending T21")

    @staticmethod
    def death_from_loss_of_care(person: Person) -> bool:
        """Java: LifecycleModule#deathFromLossOfCare.

        Java overloads:
        (Person person)
        """
        raise NotImplementedError("Java: LifecycleModule#deathFromLossOfCare — pending T21")

    @staticmethod
    def start_smoking(person: Person, time: int) -> None:
        """Java: LifecycleModule#startSmoking.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: LifecycleModule#startSmoking — pending T21")

    @staticmethod
    def likelihood_of_being_a_smoker(year: int) -> float:
        """Java: LifecycleModule#likelihoodOfBeingASmoker.

        Java overloads:
        (int year)
        """
        raise NotImplementedError("Java: LifecycleModule#likelihoodOfBeingASmoker — pending T21")

    @staticmethod
    def start_alcoholism(person: Person, time: int) -> None:
        """Java: LifecycleModule#startAlcoholism.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: LifecycleModule#startAlcoholism — pending T21")

    @staticmethod
    def quit_smoking(person: Person, time: int) -> None:
        """Java: LifecycleModule#quitSmoking.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: LifecycleModule#quitSmoking — pending T21")

    @staticmethod
    def quit_alcoholism(person: Person, time: int) -> None:
        """Java: LifecycleModule#quitAlcoholism.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: LifecycleModule#quitAlcoholism — pending T21")

    @staticmethod
    def adherence(person: Person, time: int) -> None:
        """Java: LifecycleModule#adherence.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: LifecycleModule#adherence — pending T21")

    def calculate_fall_risk(self, person: Person, time: int) -> None:
        """Java: LifecycleModule#calculateFallRisk.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: LifecycleModule#calculateFallRisk — pending T21")

    @staticmethod
    def is_disabled(person: Person, time: int) -> bool:
        """Java: LifecycleModule#isDisabled.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: LifecycleModule#isDisabled — pending T21")

    @staticmethod
    def get_earliest_disability_diagnosis_time(person: Person) -> int:
        """Java: LifecycleModule#getEarliestDisabilityDiagnosisTime.

        Java overloads:
        (Person person)
        """
        raise NotImplementedError(
            "Java: LifecycleModule#getEarliestDisabilityDiagnosisTime — pending T21"
        )

    @staticmethod
    def get_all_codes() -> list[Code]:
        """Java: LifecycleModule#getAllCodes.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: LifecycleModule#getAllCodes — pending T21")

    @staticmethod
    def inventory_attributes(attributes: dict[str, Inventory]) -> None:
        """Java: LifecycleModule#inventoryAttributes.

        Java overloads:
        (Map attributes)
        """
        raise NotImplementedError("Java: LifecycleModule#inventoryAttributes — pending T21")


# Java static data initialization; constructors remain stubs.
LifecycleModule.NATURAL_CAUSES = object.__new__(Code)
LifecycleModule.NATURAL_CAUSES.system = "SNOMED-CT"
LifecycleModule.NATURAL_CAUSES.code = "9855000"
LifecycleModule.NATURAL_CAUSES.display = "Natural death with unknown cause"
LifecycleModule.NATURAL_CAUSES.version = None
LifecycleModule.NATURAL_CAUSES.value_set = None
LifecycleModule.LOSS_OF_CARE = object.__new__(Code)
LifecycleModule.LOSS_OF_CARE.system = "SNOMED-CT"
LifecycleModule.LOSS_OF_CARE.code = "397709008"
LifecycleModule.LOSS_OF_CARE.display = "Death due to Uncovered and Unreceived Treatment"
LifecycleModule.LOSS_OF_CARE.version = None
LifecycleModule.LOSS_OF_CARE.value_set = None
