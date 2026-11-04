"""Java port skeleton: java/src/main/java/org/mitre/synthea/world/agents/Person.java."""

from __future__ import annotations


class Person:
    """Java: Person; pending T09."""

    BIRTHDATE: str = "birthdate"
    BIRTHDATE_AS_LOCALDATE: str = "birthdate_as_localdate"
    DEATHDATE: str = "deathdate"
    FIRST_NAME: str = "first_name"
    MIDDLE_NAME: str = "middle_name"
    LAST_NAME: str = "last_name"
    MAIDEN_NAME: str = "maiden_name"
    NAME_PREFIX: str = "name_prefix"
    NAME_SUFFIX: str = "name_suffix"
    NAME: str = "name"
    RACE: str = "race"
    ETHNICITY: str = "ethnicity"
    FIRST_LANGUAGE: str = "first_language"
    GENDER: str = "gender"
    MULTIPLE_BIRTH_STATUS: str = "multiple_birth_status"
    TELECOM: str = "telecom"
    ID: str = "id"
    ADDRESS: str = "address"
    BIRTH_CITY: str = "birth_city"
    BIRTH_COUNTRY: str = "birth_country"
    BIRTH_STATE: str = "birth_state"
    BIRTHPLACE: str = "birthplace"
    CAUSE_OF_DEATH: str = "cause_of_death"
    CITY: str = "city"
    COUNTY: str = "county"
    STATE: str = "state"
    ZIP: str = "zip"
    FIPS: str = "fips"
    COORDINATE: str = "coordinate"
    NAME_MOTHER: str = "name_mother"
    NAME_FATHER: str = "name_father"
    MARITAL_STATUS: str = "marital_status"
    SOCIOECONOMIC_SCORE: str = "socioeconomic_score"
    SOCIOECONOMIC_CATEGORY: str = "socioeconomic_category"
    INCOME: str = "income"
    INCOME_LEVEL: str = "income_level"
    POVERTY_RATIO: str = "poverty_ratio"
    EDUCATION: str = "education"
    EDUCATION_LEVEL: str = "education_level"
    OCCUPATION_LEVEL: str = "occupation_level"
    SMOKER: str = "smoker"
    ALCOHOLIC: str = "alcoholic"
    ADHERENCE: str = "adherence"
    IDENTIFIER_SSN: str = "identifier_ssn"
    IDENTIFIER_DRIVERS: str = "identifier_drivers"
    IDENTIFIER_PASSPORT: str = "identifier_passport"
    IDENTIFIER_SITE: str = "identifier_site"
    IDENTIFIER_VARIANT_ID: str = "identifier_variant_id"
    IDENTIFIER_SEED_ID: str = "identifier_seed_id"
    CONTACT_FAMILY_NAME: str = "contact_family_name"
    CONTACT_GIVEN_NAME: str = "contact_given_name"
    CONTACT_EMAIL: str = "contact_email"
    SEXUAL_ORIENTATION: str = "sexual_orientation"
    LOCATION: str = "location"
    ACTIVE_WEIGHT_MANAGEMENT: str = "active_weight_management"
    BMI_PERCENTILE: str = "bmi_percentile"
    GROWTH_TRAJECTORY: str = "growth_trajectory"
    CURRENT_WEIGHT_LENGTH_PERCENTILE: str = "current_weight_length_percentile"
    HOUSEHOLD: str = "household"
    LINK_ID: str = "link_id"
    VETERAN: str = "veteran"
    BLINDNESS: str = "blindness"
    DISABLED: str = "disabled"
    HOUSEHOLD_ROLE: str = "household_role"
    TARGET_WEIGHT_LOSS: str = "target_weight_loss"
    KILOGRAMS_TO_GAIN: str = "kilograms_to_gain"
    ENTITY: str = "ENTITY"
    INSURANCE_STATUS: str = "insurance_status"
    FOOD_INSECURITY: str = "food_insecurity"
    SEVERE_HOUSING_COST_BURDEN: str = "severe_housing_cost_burden"
    UNEMPLOYED: str = "unemployed"
    EMPLOYMENT_MODEL: str = "employment_model"
    NO_VEHICLE_ACCESS: str = "no_vehicle_access"
    UNINSURED: str = "uninsured"
    LAST_MONTH_PAID: str = "last_month_paid"
    CURRENT_ENCOUNTER_MODULE: str = "current-encounter-module"
    CURRENTPROVIDER: str = "currentProvider"
    PREFERREDYPROVIDER: str = "preferredProvider"

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: Person constructor; pending T09."""
        self.random: object = None
        self.populationSeed: int = 0
        self.lastUpdated: int = 0
        self.currentModules: object = None
        self.attributes: str | None = None
        self.vitalSigns: object = None
        self.onsetConditionRecord: object = None
        self.chronicMedications: str | None = None
        self.record: object = None
        self.defaultRecord: object = None
        self.lossOfCareRecord: object = None
        self.lossOfCareEnabled: bool = False
        self.records: str | None = None
        self.hasMultipleRecords: bool = False
        self.history: object = None
        self.coverage: object = None
        raise NotImplementedError("Java: Person#constructor — pending T09")

    def initialize_default_health_records(self, *args: object, **kwargs: object) -> object:
        """Java: Person#initializeDefaultHealthRecords; pending T09."""
        raise NotImplementedError("Java: Person#initializeDefaultHealthRecords — pending T09")

    def rand(self, *args: object, **kwargs: object) -> object:
        """Java: Person#rand; pending T09."""
        raise NotImplementedError("Java: Person#rand — pending T09")

    def rand_boolean(self, *args: object, **kwargs: object) -> object:
        """Java: Person#randBoolean; pending T09."""
        raise NotImplementedError("Java: Person#randBoolean — pending T09")

    def rand_int(self, *args: object, **kwargs: object) -> object:
        """Java: Person#randInt; pending T09."""
        raise NotImplementedError("Java: Person#randInt — pending T09")

    def rand_gaussian(self, *args: object, **kwargs: object) -> object:
        """Java: Person#randGaussian; pending T09."""
        raise NotImplementedError("Java: Person#randGaussian — pending T09")

    def rand_long(self, *args: object, **kwargs: object) -> object:
        """Java: Person#randLong; pending T09."""
        raise NotImplementedError("Java: Person#randLong — pending T09")

    def rand_uuid(self, *args: object, **kwargs: object) -> object:
        """Java: Person#randUUID; pending T09."""
        raise NotImplementedError("Java: Person#randUUID — pending T09")

    def get_count(self, *args: object, **kwargs: object) -> object:
        """Java: Person#getCount; pending T09."""
        raise NotImplementedError("Java: Person#getCount — pending T09")

    def get_seed(self, *args: object, **kwargs: object) -> object:
        """Java: Person#getSeed; pending T09."""
        raise NotImplementedError("Java: Person#getSeed — pending T09")

    def age(self, *args: object, **kwargs: object) -> object:
        """Java: Person#age; pending T09."""
        raise NotImplementedError("Java: Person#age — pending T09")

    def age_in_decimal_years(self, *args: object, **kwargs: object) -> object:
        """Java: Person#ageInDecimalYears; pending T09."""
        raise NotImplementedError("Java: Person#ageInDecimalYears — pending T09")

    def age_in_months(self, *args: object, **kwargs: object) -> object:
        """Java: Person#ageInMonths; pending T09."""
        raise NotImplementedError("Java: Person#ageInMonths — pending T09")

    def age_in_years(self, *args: object, **kwargs: object) -> object:
        """Java: Person#ageInYears; pending T09."""
        raise NotImplementedError("Java: Person#ageInYears — pending T09")

    def alive(self, *args: object, **kwargs: object) -> object:
        """Java: Person#alive; pending T09."""
        raise NotImplementedError("Java: Person#alive — pending T09")

    def get_expressed_symptoms(self, *args: object, **kwargs: object) -> object:
        """Java: Person#getExpressedSymptoms; pending T09."""
        raise NotImplementedError("Java: Person#getExpressedSymptoms — pending T09")

    def get_onset_condition_record(self, *args: object, **kwargs: object) -> object:
        """Java: Person#getOnsetConditionRecord; pending T09."""
        raise NotImplementedError("Java: Person#getOnsetConditionRecord — pending T09")

    def provider_count(self, *args: object, **kwargs: object) -> object:
        """Java: Person#providerCount; pending T09."""
        raise NotImplementedError("Java: Person#providerCount — pending T09")

    def set_symptom(self, *args: object, **kwargs: object) -> object:
        """Java: Person#setSymptom; pending T09."""
        raise NotImplementedError("Java: Person#setSymptom — pending T09")

    def get_symptom_last_updated_time(self, *args: object, **kwargs: object) -> object:
        """Java: Person#getSymptomLastUpdatedTime; pending T09."""
        raise NotImplementedError("Java: Person#getSymptomLastUpdatedTime — pending T09")

    def get_symptom(self, *args: object, **kwargs: object) -> object:
        """Java: Person#getSymptom; pending T09."""
        raise NotImplementedError("Java: Person#getSymptom — pending T09")

    def get_symptoms(self, *args: object, **kwargs: object) -> object:
        """Java: Person#getSymptoms; pending T09."""
        raise NotImplementedError("Java: Person#getSymptoms — pending T09")

    def address_largest_symptom(self, *args: object, **kwargs: object) -> object:
        """Java: Person#addressLargestSymptom; pending T09."""
        raise NotImplementedError("Java: Person#addressLargestSymptom — pending T09")

    def get_vital_sign(self, *args: object, **kwargs: object) -> object:
        """Java: Person#getVitalSign; pending T09."""
        raise NotImplementedError("Java: Person#getVitalSign — pending T09")

    def set_vital_sign(self, *args: object, **kwargs: object) -> object:
        """Java: Person#setVitalSign; pending T09."""
        raise NotImplementedError("Java: Person#setVitalSign — pending T09")

    def record_death(self, *args: object, **kwargs: object) -> object:
        """Java: Person#recordDeath; pending T09."""
        raise NotImplementedError("Java: Person#recordDeath — pending T09")

    def symptom_total(self, *args: object, **kwargs: object) -> object:
        """Java: Person#symptomTotal; pending T09."""
        raise NotImplementedError("Java: Person#symptomTotal — pending T09")

    def had_prior_state(self, *args: object, **kwargs: object) -> object:
        """Java: Person#hadPriorState; pending T09."""
        raise NotImplementedError("Java: Person#hadPriorState — pending T09")

    def encounter_start(self, *args: object, **kwargs: object) -> object:
        """Java: Person#encounterStart; pending T09."""
        raise NotImplementedError("Java: Person#encounterStart — pending T09")

    def get_health_record(self, *args: object, **kwargs: object) -> object:
        """Java: Person#getHealthRecord; pending T09."""
        raise NotImplementedError("Java: Person#getHealthRecord — pending T09")

    def get_current_encounter_module(self, *args: object, **kwargs: object) -> object:
        """Java: Person#getCurrentEncounterModule; pending T09."""
        raise NotImplementedError("Java: Person#getCurrentEncounterModule — pending T09")

    def has_current_encounter(self, *args: object, **kwargs: object) -> object:
        """Java: Person#hasCurrentEncounter; pending T09."""
        raise NotImplementedError("Java: Person#hasCurrentEncounter — pending T09")

    def release_current_encounter(self, *args: object, **kwargs: object) -> object:
        """Java: Person#releaseCurrentEncounter; pending T09."""
        raise NotImplementedError("Java: Person#releaseCurrentEncounter — pending T09")

    def reserve_current_encounter(self, *args: object, **kwargs: object) -> object:
        """Java: Person#reserveCurrentEncounter; pending T09."""
        raise NotImplementedError("Java: Person#reserveCurrentEncounter — pending T09")

    def get_provider(self, *args: object, **kwargs: object) -> object:
        """Java: Person#getProvider; pending T09."""
        raise NotImplementedError("Java: Person#getProvider — pending T09")

    def set_provider(self, *args: object, **kwargs: object) -> object:
        """Java: Person#setProvider; pending T09."""
        raise NotImplementedError("Java: Person#setProvider — pending T09")

    def add_current_provider(self, *args: object, **kwargs: object) -> object:
        """Java: Person#addCurrentProvider; pending T09."""
        raise NotImplementedError("Java: Person#addCurrentProvider — pending T09")

    def remove_current_provider(self, *args: object, **kwargs: object) -> object:
        """Java: Person#removeCurrentProvider; pending T09."""
        raise NotImplementedError("Java: Person#removeCurrentProvider — pending T09")

    def get_current_provider(self, *args: object, **kwargs: object) -> object:
        """Java: Person#getCurrentProvider; pending T09."""
        raise NotImplementedError("Java: Person#getCurrentProvider — pending T09")

    def get_qalys(self, *args: object, **kwargs: object) -> object:
        """Java: Person#getQalys; pending T09."""
        raise NotImplementedError("Java: Person#getQalys — pending T09")

    def get_dalys(self, *args: object, **kwargs: object) -> object:
        """Java: Person#getDalys; pending T09."""
        raise NotImplementedError("Java: Person#getDalys — pending T09")

    def can_afford_plan(self, *args: object, **kwargs: object) -> object:
        """Java: Person#canAffordPlan; pending T09."""
        raise NotImplementedError("Java: Person#canAffordPlan — pending T09")

    def still_has_income(self, *args: object, **kwargs: object) -> object:
        """Java: Person#stillHasIncome; pending T09."""
        raise NotImplementedError("Java: Person#stillHasIncome — pending T09")

    def check_to_pay_monthly_premium(self, *args: object, **kwargs: object) -> object:
        """Java: Person#checkToPayMonthlyPremium; pending T09."""
        raise NotImplementedError("Java: Person#checkToPayMonthlyPremium — pending T09")

    def get_qols_for_year(self, *args: object, **kwargs: object) -> object:
        """Java: Person#getQolsForYear; pending T09."""
        raise NotImplementedError("Java: Person#getQolsForYear — pending T09")

    def get_x(self, *args: object, **kwargs: object) -> object:
        """Java: Person#getX; pending T09."""
        raise NotImplementedError("Java: Person#getX — pending T09")

    def get_y(self, *args: object, **kwargs: object) -> object:
        """Java: Person#getY; pending T09."""
        raise NotImplementedError("Java: Person#getY — pending T09")

    def get_lon_lat(self, *args: object, **kwargs: object) -> object:
        """Java: Person#getLonLat; pending T09."""
        raise NotImplementedError("Java: Person#getLonLat — pending T09")
