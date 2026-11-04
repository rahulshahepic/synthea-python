"""Java API skeleton: Person.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Protocol
from uuid import UUID

if TYPE_CHECKING:
    from synthea.engine.expressed_condition_record import ExpressedConditionRecord
    from synthea.engine.expressed_symptom import ExpressedSymptom
    from synthea.engine.module import Module
    from synthea.engine.state import State
    from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
    from synthea.helpers.value_generator import ValueGenerator
    from synthea.world.agents.provider import Provider
    from synthea.world.concepts.health_record import Code, Encounter, EncounterType, HealthRecord
    from synthea.world.concepts.health_record import Medication as HealthRecordMedication
    from synthea.world.concepts.healthinsurance.coverage_record import CoverageRecord
    from synthea.world.concepts.healthinsurance.insurance_plan import InsurancePlan
    from synthea.world.concepts.vital_sign import VitalSign

    class Period(Protocol):
        """Java boundary type: Period; external to the mapped Python port."""


class Person:
    """Java: Person; pending T09."""

    serialVersionUID: ClassVar[int] = 4322116644425686379
    BIRTHDATE: ClassVar[str] = "birthdate"
    BIRTHDATE_AS_LOCALDATE: ClassVar[str] = "birthdate_as_localdate"
    DEATHDATE: ClassVar[str] = "deathdate"
    FIRST_NAME: ClassVar[str] = "first_name"
    MIDDLE_NAME: ClassVar[str] = "middle_name"
    LAST_NAME: ClassVar[str] = "last_name"
    MAIDEN_NAME: ClassVar[str] = "maiden_name"
    NAME_PREFIX: ClassVar[str] = "name_prefix"
    NAME_SUFFIX: ClassVar[str] = "name_suffix"
    NAME: ClassVar[str] = "name"
    RACE: ClassVar[str] = "race"
    ETHNICITY: ClassVar[str] = "ethnicity"
    FIRST_LANGUAGE: ClassVar[str] = "first_language"
    GENDER: ClassVar[str] = "gender"
    MULTIPLE_BIRTH_STATUS: ClassVar[str] = "multiple_birth_status"
    TELECOM: ClassVar[str] = "telecom"
    ID: ClassVar[str] = "id"
    ADDRESS: ClassVar[str] = "address"
    BIRTH_CITY: ClassVar[str] = "birth_city"
    BIRTH_COUNTRY: ClassVar[str] = "birth_country"
    BIRTH_STATE: ClassVar[str] = "birth_state"
    BIRTHPLACE: ClassVar[str] = "birthplace"
    CAUSE_OF_DEATH: ClassVar[str] = "cause_of_death"
    CITY: ClassVar[str] = "city"
    COUNTY: ClassVar[str] = "county"
    STATE: ClassVar[str] = "state"
    ZIP: ClassVar[str] = "zip"
    FIPS: ClassVar[str] = "fips"
    COORDINATE: ClassVar[str] = "coordinate"
    NAME_MOTHER: ClassVar[str] = "name_mother"
    NAME_FATHER: ClassVar[str] = "name_father"
    MARITAL_STATUS: ClassVar[str] = "marital_status"
    SOCIOECONOMIC_SCORE: ClassVar[str] = "socioeconomic_score"
    SOCIOECONOMIC_CATEGORY: ClassVar[str] = "socioeconomic_category"
    INCOME: ClassVar[str] = "income"
    INCOME_LEVEL: ClassVar[str] = "income_level"
    POVERTY_RATIO: ClassVar[str] = "poverty_ratio"
    EDUCATION: ClassVar[str] = "education"
    EDUCATION_LEVEL: ClassVar[str] = "education_level"
    OCCUPATION_LEVEL: ClassVar[str] = "occupation_level"
    SMOKER: ClassVar[str] = "smoker"
    ALCOHOLIC: ClassVar[str] = "alcoholic"
    ADHERENCE: ClassVar[str] = "adherence"
    IDENTIFIER_SSN: ClassVar[str] = "identifier_ssn"
    IDENTIFIER_DRIVERS: ClassVar[str] = "identifier_drivers"
    IDENTIFIER_PASSPORT: ClassVar[str] = "identifier_passport"
    IDENTIFIER_SITE: ClassVar[str] = "identifier_site"
    IDENTIFIER_VARIANT_ID: ClassVar[str] = "identifier_variant_id"
    IDENTIFIER_SEED_ID: ClassVar[str] = "identifier_seed_id"
    CONTACT_FAMILY_NAME: ClassVar[str] = "contact_family_name"
    CONTACT_GIVEN_NAME: ClassVar[str] = "contact_given_name"
    CONTACT_EMAIL: ClassVar[str] = "contact_email"
    SEXUAL_ORIENTATION: ClassVar[str] = "sexual_orientation"
    LOCATION: ClassVar[str] = "location"
    ACTIVE_WEIGHT_MANAGEMENT: ClassVar[str] = "active_weight_management"
    BMI_PERCENTILE: ClassVar[str] = "bmi_percentile"
    GROWTH_TRAJECTORY: ClassVar[str] = "growth_trajectory"
    CURRENT_WEIGHT_LENGTH_PERCENTILE: ClassVar[str] = "current_weight_length_percentile"
    HOUSEHOLD: ClassVar[str] = "household"
    LINK_ID: ClassVar[str] = "link_id"
    VETERAN: ClassVar[str] = "veteran"
    BLINDNESS: ClassVar[str] = "blindness"
    DISABLED: ClassVar[str] = "disabled"
    HOUSEHOLD_ROLE: ClassVar[str] = "household_role"
    TARGET_WEIGHT_LOSS: ClassVar[str] = "target_weight_loss"
    KILOGRAMS_TO_GAIN: ClassVar[str] = "kilograms_to_gain"
    ENTITY: ClassVar[str] = "ENTITY"
    INSURANCE_STATUS: ClassVar[str] = "insurance_status"
    FOOD_INSECURITY: ClassVar[str] = "food_insecurity"
    SEVERE_HOUSING_COST_BURDEN: ClassVar[str] = "severe_housing_cost_burden"
    UNEMPLOYED: ClassVar[str] = "unemployed"
    EMPLOYMENT_MODEL: ClassVar[str] = "employment_model"
    NO_VEHICLE_ACCESS: ClassVar[str] = "no_vehicle_access"
    UNINSURED: ClassVar[str] = "uninsured"
    LAST_MONTH_PAID: ClassVar[str] = "last_month_paid"
    CURRENT_ENCOUNTER_MODULE: ClassVar[str] = "current-encounter-module"
    CURRENTPROVIDER: ClassVar[str] = "currentProvider"
    PREFERREDYPROVIDER: ClassVar[str] = "preferredProvider"

    def __init__(self, seed: int) -> None:
        """Java: Person#Person.

        Java overloads:
        (long seed)
        """
        self.random: DefaultRandomNumberGenerator
        self.population_seed: int
        self.last_updated: int
        self.current_modules: list[Module]
        self.attributes: dict[str, object]
        self.vital_signs: dict[VitalSign, ValueGenerator]
        self.symptoms: dict[str, ExpressedSymptom]
        self.onset_condition_record: ExpressedConditionRecord
        self.chronic_medications: dict[str, HealthRecordMedication]
        self.record: HealthRecord
        self.default_record: HealthRecord
        self.loss_of_care_record: HealthRecord
        self.loss_of_care_enabled: bool
        self.records: dict[str, HealthRecord]
        self.has_multiple_records: bool
        self.history: list[State]
        self.coverage: CoverageRecord
        raise NotImplementedError("Java: Person#Person — pending T09")

    def initialize_default_health_records(self) -> None:
        """Java: Person#initializeDefaultHealthRecords.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Person#initializeDefaultHealthRecords — pending T09")

    def rand(self) -> float:
        """Java: Person#rand.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Person#rand — pending T09")

    def rand_boolean(self) -> bool:
        """Java: Person#randBoolean.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Person#randBoolean — pending T09")

    def rand_int(self, bound: int | None = None) -> int:
        """Java: Person#randInt.

        Java overloads:
        ()
        (int bound)
        """
        raise NotImplementedError("Java: Person#randInt — pending T09")

    def rand_gaussian(self) -> float:
        """Java: Person#randGaussian.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Person#randGaussian — pending T09")

    def rand_long(self) -> int:
        """Java: Person#randLong.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Person#randLong — pending T09")

    def rand_uuid(self) -> UUID:
        """Java: Person#randUUID.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Person#randUUID — pending T09")

    def get_count(self) -> int:
        """Java: Person#getCount.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Person#getCount — pending T09")

    def get_seed(self) -> int:
        """Java: Person#getSeed.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Person#getSeed — pending T09")

    def age(self, time: int) -> Period:
        """Java: Person#age.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: Person#age — pending T09")

    def age_in_decimal_years(self, time: int) -> float:
        """Java: Person#ageInDecimalYears.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: Person#ageInDecimalYears — pending T09")

    def age_in_months(self, time: int) -> int:
        """Java: Person#ageInMonths.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: Person#ageInMonths — pending T09")

    def age_in_years(self, time: int) -> int:
        """Java: Person#ageInYears.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: Person#ageInYears — pending T09")

    def alive(self, time: int) -> bool:
        """Java: Person#alive.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: Person#alive — pending T09")

    def get_expressed_symptoms(self) -> dict[str, ExpressedSymptom]:
        """Java: Person#getExpressedSymptoms.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Person#getExpressedSymptoms — pending T09")

    def get_onset_condition_record(self) -> ExpressedConditionRecord:
        """Java: Person#getOnsetConditionRecord.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Person#getOnsetConditionRecord — pending T09")

    def provider_count(self) -> int:
        """Java: Person#providerCount.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Person#providerCount — pending T09")

    def set_symptom(
        self, module: str, cause: str, type: str, time: int, value: int, addressed: bool
    ) -> None:
        """Java: Person#setSymptom.

        Java overloads:
        (String module, String cause, String type, long time, int value, Boolean
        addressed)
        """
        raise NotImplementedError("Java: Person#setSymptom — pending T09")

    def get_symptom_last_updated_time(self, module: str, symptom: str) -> int:
        """Java: Person#getSymptomLastUpdatedTime.

        Java overloads:
        (String module, String symptom)
        """
        raise NotImplementedError("Java: Person#getSymptomLastUpdatedTime — pending T09")

    def get_symptom(self, type: str) -> int:
        """Java: Person#getSymptom.

        Java overloads:
        (String type)
        """
        raise NotImplementedError("Java: Person#getSymptom — pending T09")

    def get_symptoms(self) -> list[str]:
        """Java: Person#getSymptoms.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Person#getSymptoms — pending T09")

    def address_largest_symptom(self) -> None:
        """Java: Person#addressLargestSymptom.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Person#addressLargestSymptom — pending T09")

    def get_vital_sign(self, vital_sign: VitalSign, time: int) -> float:
        """Java: Person#getVitalSign.

        Java overloads:
        (VitalSign vitalSign, long time)
        """
        raise NotImplementedError("Java: Person#getVitalSign — pending T09")

    def set_vital_sign(
        self, vital_sign: VitalSign, value_generator_or_value: ValueGenerator | float
    ) -> None:
        """Java: Person#setVitalSign.

        Java overloads:
        (VitalSign vitalSign, ValueGenerator valueGenerator)
        (VitalSign vitalSign, double value)
        """
        raise NotImplementedError("Java: Person#setVitalSign — pending T09")

    def record_death(self, time: int, cause: Code) -> None:
        """Java: Person#recordDeath.

        Java overloads:
        (long time, Code cause)
        """
        raise NotImplementedError("Java: Person#recordDeath — pending T09")

    def symptom_total(self) -> int:
        """Java: Person#symptomTotal.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Person#symptomTotal — pending T09")

    def had_prior_state(
        self, name: str, since: str | None = None, within: int | None = None
    ) -> bool:
        """Java: Person#hadPriorState.

        Java overloads:
        (String name)
        (String name, String since, Long within)
        """
        raise NotImplementedError("Java: Person#hadPriorState — pending T09")

    def encounter_start(self, time: int, type: EncounterType) -> Encounter:
        """Java: Person#encounterStart.

        Java overloads:
        (long time, EncounterType type)
        """
        raise NotImplementedError("Java: Person#encounterStart — pending T09")

    def get_health_record(self, provider: Provider, time: int) -> HealthRecord:
        """Java: Person#getHealthRecord.

        Java overloads:
        (Provider provider, long time)
        """
        raise NotImplementedError("Java: Person#getHealthRecord — pending T09")

    def get_current_encounter_module(self) -> str:
        """Java: Person#getCurrentEncounterModule.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Person#getCurrentEncounterModule — pending T09")

    def has_current_encounter(self) -> bool:
        """Java: Person#hasCurrentEncounter.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Person#hasCurrentEncounter — pending T09")

    def release_current_encounter(self, time: int, module: str) -> None:
        """Java: Person#releaseCurrentEncounter.

        Java overloads:
        (long time, String module)
        """
        raise NotImplementedError("Java: Person#releaseCurrentEncounter — pending T09")

    def reserve_current_encounter(self, time: int, module: str) -> bool:
        """Java: Person#reserveCurrentEncounter.

        Java overloads:
        (long time, String module)
        """
        raise NotImplementedError("Java: Person#reserveCurrentEncounter — pending T09")

    def get_provider(self, type: EncounterType, time: int) -> Provider:
        """Java: Person#getProvider.

        Java overloads:
        (EncounterType type, long time)
        """
        raise NotImplementedError("Java: Person#getProvider — pending T09")

    def set_provider(self, type: EncounterType, provider_or_time: Provider | int) -> None:
        """Java: Person#setProvider.

        Java overloads:
        (EncounterType type, Provider provider)
        (EncounterType type, long time)
        """
        raise NotImplementedError("Java: Person#setProvider — pending T09")

    def add_current_provider(self, context: str, provider: Provider) -> None:
        """Java: Person#addCurrentProvider.

        Java overloads:
        (String context, Provider provider)
        """
        raise NotImplementedError("Java: Person#addCurrentProvider — pending T09")

    def remove_current_provider(self, module: str) -> None:
        """Java: Person#removeCurrentProvider.

        Java overloads:
        (String module)
        """
        raise NotImplementedError("Java: Person#removeCurrentProvider — pending T09")

    def get_current_provider(self, module: str) -> Provider:
        """Java: Person#getCurrentProvider.

        Java overloads:
        (String module)
        """
        raise NotImplementedError("Java: Person#getCurrentProvider — pending T09")

    def get_qalys(self) -> float:
        """Java: Person#getQalys.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Person#getQalys — pending T09")

    def get_dalys(self) -> float:
        """Java: Person#getDalys.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Person#getDalys — pending T09")

    def can_afford_plan(self, plan: InsurancePlan) -> bool:
        """Java: Person#canAffordPlan.

        Java overloads:
        (InsurancePlan plan)
        """
        raise NotImplementedError("Java: Person#canAffordPlan — pending T09")

    def still_has_income(self, time: int) -> bool:
        """Java: Person#stillHasIncome.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: Person#stillHasIncome — pending T09")

    def check_to_pay_monthly_premium(self, time: int) -> None:
        """Java: Person#checkToPayMonthlyPremium.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: Person#checkToPayMonthlyPremium — pending T09")

    def get_qols_for_year(self, year: int) -> float:
        """Java: Person#getQolsForYear.

        Java overloads:
        (int year)
        """
        raise NotImplementedError("Java: Person#getQolsForYear — pending T09")

    def get_x(self) -> float:
        """Java: Person#getX.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Person#getX — pending T09")

    def get_y(self) -> float:
        """Java: Person#getY.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Person#getY — pending T09")

    def get_lon_lat(self) -> float:
        """Java: Person#getLonLat.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Person#getLonLat — pending T09")
