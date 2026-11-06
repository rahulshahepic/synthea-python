"""Java: org.mitre.synthea.world.agents.Person."""

from __future__ import annotations

import math
from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar, cast

from synthea.engine.expressed_condition_record import ExpressedConditionRecord
from synthea.engine.expressed_symptom import ExpressedSymptom
from synthea.helpers.config import Config
from synthea.helpers.constant_value_generator import ConstantValueGenerator
from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.helpers.utilities import Utilities
from synthea.helpers.value_generator import ValueGenerator
from synthea.javacompat import bigdecimal
from synthea.javacompat.collections import JavaConcurrentHashMap, JavaHashMap
from synthea.javacompat.numbers import double_to_string
from synthea.modules.quality_of_life_module import QualityOfLifeModule
from synthea.world.agents.provider import Provider
from synthea.world.concepts.health_record import (
    Code,
    Encounter,
    EncounterType,
    HealthRecord,
)
from synthea.world.concepts.health_record import (
    Medication as HealthRecordMedication,
)
from synthea.world.concepts.healthinsurance.coverage_record import CoverageRecord
from synthea.world.concepts.healthinsurance.insurance_plan import InsurancePlan
from synthea.world.concepts.vital_sign import VITAL_SIGN_DISPLAY_NAMES, VitalSign

if TYPE_CHECKING:
    from synthea.engine.distribution import RandomSource
    from synthea.engine.module import Module
    from synthea.engine.state import State

_EPOCH = date(1970, 1, 1)
_MILLIS_PER_DAY = 86_400_000


def _local_date_of_epoch_milli(time: int) -> date:
    """Java: Instant.ofEpochMilli(time).atZone(ZoneOffset.UTC).toLocalDate()."""
    return _EPOCH + timedelta(days=time // _MILLIS_PER_DAY)


def _length_of_month(year: int, month: int) -> int:
    """Java: LocalDate.lengthOfMonth for the given year/month."""
    if month == 12:
        return (_EPOCH.replace(year=year + 1, month=1, day=1) - date(year, 12, 1)).days
    return (date(year, month + 1, 1) - date(year, month, 1)).days


def _plus_months(day: date, months: int) -> date:
    """Java: LocalDate.plusMonths(months), clamping the day to the target month."""
    total = (day.year * 12 + (day.month - 1)) + months
    year, month0 = divmod(total, 12)
    month = month0 + 1
    dom = min(day.day, _length_of_month(year, month))
    return date(year, month, dom)


class Period:
    """Java: java.time.Period (as returned by Person#age)."""

    def __init__(self, years: int, months: int, days: int) -> None:
        """Java: Period.of(years, months, days)."""
        self.years: int = years
        self.months: int = months
        self.days: int = days

    def get_years(self) -> int:
        """Java: Period#getYears."""
        return self.years

    def get_months(self) -> int:
        """Java: Period#getMonths."""
        return self.months

    def get_days(self) -> int:
        """Java: Period#getDays."""
        return self.days

    def to_total_months(self) -> int:
        """Java: Period#toTotalMonths."""
        return self.years * 12 + self.months

    def __str__(self) -> str:
        """Java: Period#toString, e.g. "P1Y2M3D"; zero is "P0D"."""
        if self.years == 0 and self.months == 0 and self.days == 0:
            return "P0D"
        out = "P"
        if self.years != 0:
            out += f"{self.years}Y"
        if self.months != 0:
            out += f"{self.months}M"
        if self.days != 0:
            out += f"{self.days}D"
        return out


def _period_between(start: date, end: date) -> Period:
    """Java: Period.between(start, end), following java.time's exact algorithm."""
    total_months = (end.year * 12 + (end.month - 1)) - (start.year * 12 + (start.month - 1))
    days = end.day - start.day
    if total_months > 0 and days < 0:
        total_months -= 1
        days = (end - _plus_months(start, total_months)).days
    elif total_months < 0 and days > 0:
        total_months += 1
        days -= _length_of_month(end.year, end.month)
    years = total_months // 12 if total_months >= 0 else -((-total_months) // 12)
    months = total_months - years * 12
    return Period(years, months, days)


def _as_int(value: object, what: str) -> int:
    """Java: unboxing cast of an Integer attribute; ClassCastException otherwise."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"Java ClassCastException: {what} attribute is not an Integer")
    return value


def _as_float(value: object, what: str) -> float:
    """Java: unboxing cast of a Double attribute; ClassCastException otherwise."""
    if not isinstance(value, float):
        raise TypeError(f"Java ClassCastException: {what} attribute is not a Double")
    return value


class Point2DDouble:
    """Java: java.awt.geom.Point2D.Double (the Person COORDINATE attribute type)."""

    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        """Java: Point2D.Double#Point2D.Double(double, double)."""
        self.x: float = x
        self.y: float = y

    def get_x(self) -> float:
        """Java: Point2D#getX."""
        return self.x

    def get_y(self) -> float:
        """Java: Point2D#getY."""
        return self.y


class Person:
    """Java: org.mitre.synthea.world.agents.Person; implements RandomNumberGenerator."""

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
        """Java: Person#Person(long)."""
        self.random: DefaultRandomNumberGenerator = DefaultRandomNumberGenerator(seed)
        self.population_seed: int = 0
        self.last_updated: int = 0
        self.current_modules: list[Module] | None = None
        self.attributes: JavaConcurrentHashMap[str, object] = JavaConcurrentHashMap()
        self.vital_signs: JavaConcurrentHashMap[VitalSign, ValueGenerator] = JavaConcurrentHashMap()
        self.symptoms: JavaConcurrentHashMap[str, ExpressedSymptom] = JavaConcurrentHashMap()
        self.onset_condition_record: ExpressedConditionRecord = ExpressedConditionRecord(self)
        self.chronic_medications: JavaConcurrentHashMap[str, HealthRecordMedication] = (
            JavaConcurrentHashMap()
        )
        self.record: HealthRecord | None = None
        self.default_record: HealthRecord | None = None
        self.loss_of_care_record: HealthRecord | None = None
        self.loss_of_care_enabled: bool = False
        self.records: JavaConcurrentHashMap[str, HealthRecord] | None = None
        self.has_multiple_records: bool = Config.get_as_boolean("exporter.split_records", False)
        if self.has_multiple_records:
            self.records = JavaConcurrentHashMap()
        self.history: list[State] | None = None
        self.initialize_default_health_records()
        self.coverage: CoverageRecord = CoverageRecord(self)

    def initialize_default_health_records(self) -> None:
        """Java: Person#initializeDefaultHealthRecords."""
        self.default_record = HealthRecord(self)
        self.record = self.default_record
        self.loss_of_care_enabled = Config.get_as_boolean("generate.payers.loss_of_care", False)
        if self.loss_of_care_enabled:
            self.loss_of_care_record = HealthRecord(self)

    def rand(self) -> float:
        """Java: Person#rand."""
        return self.random.rand()

    def rand_boolean(self) -> bool:
        """Java: Person#randBoolean."""
        return self.random.rand_boolean()

    def rand_int(self, bound: int | None = None) -> int:
        """Java: Person#randInt() and #randInt(int)."""
        return self.random.rand_int(bound)

    def rand_gaussian(self) -> float:
        """Java: Person#randGaussian."""
        return self.random.rand_gaussian()

    def rand_long(self) -> int:
        """Java: Person#randLong."""
        return self.random.rand_long()

    def rand_uuid(self) -> str:
        """Java: Person#randUUID (the T01 port represents UUIDs as strings)."""
        return self.random.rand_uuid()

    def get_count(self) -> int:
        """Java: Person#getCount."""
        return self.random.get_count()

    def get_seed(self) -> int:
        """Java: Person#getSeed."""
        return self.random.get_seed()

    def age(self, time: int) -> Period:
        """Java: Person#age(long)."""
        age = Period(0, 0, 0)
        if Person.BIRTHDATE in self.attributes:
            now = _local_date_of_epoch_milli(time)
            birthdate = self.attributes.get(Person.BIRTHDATE_AS_LOCALDATE)
            if birthdate is None:
                birthdate = _local_date_of_epoch_milli(
                    _as_int(self.attributes[Person.BIRTHDATE], "birthdate")
                )
                self.attributes[Person.BIRTHDATE_AS_LOCALDATE] = birthdate
            age = _period_between(cast(date, birthdate), now)
        return age

    def age_in_decimal_years(self, time: int) -> float:
        """Java: Person#ageInDecimalYears(long)."""
        age_period = self.age(time)
        years = (
            age_period.get_years()
            + age_period.get_months() / 12.0
            + age_period.get_days() / 365.2425
        )
        if years < 0:
            years = 0.0
        return years

    def age_in_months(self, time: int) -> int:
        """Java: Person#ageInMonths(long)."""
        months = self.age(time).to_total_months()
        if months < 0:
            months = 0
        return months

    def age_in_years(self, time: int) -> int:
        """Java: Person#ageInYears(long)."""
        years = self.age(time).get_years()
        if years < 0:
            years = 0
        return years

    def alive(self, time: int) -> bool:
        """Java: Person#alive(long)."""
        born = Person.BIRTHDATE in self.attributes
        died = self.attributes.get(Person.DEATHDATE)
        return born and (died is None or died > time)  # type: ignore[operator]

    def get_expressed_symptoms(self) -> JavaConcurrentHashMap[str, ExpressedSymptom]:
        """Java: Person#getExpressedSymptoms."""
        return self.symptoms

    def get_onset_condition_record(self) -> ExpressedConditionRecord:
        """Java: Person#getOnsetConditionRecord."""
        return self.onset_condition_record

    def provider_count(self) -> int:
        """Java: Person#providerCount."""
        count = 1
        if self.has_multiple_records:
            records = self.records
            if records is None:
                raise TypeError("Java NullPointerException: records is null")
            count = len(set(records.keys()))
        else:
            record = self.record
            if record is None:
                raise TypeError("Java NullPointerException: record is null")
            count = record.provider_count()
        return count

    def set_symptom(
        self, module: str, cause: str, type: str, time: int, value: int, addressed: bool | None
    ) -> None:
        """Java: Person#setSymptom(String, String, String, long, int, Boolean)."""
        if type not in self.symptoms:
            self.symptoms[type] = ExpressedSymptom(type)
        expressed_symptom = self.symptoms[type]
        expressed_symptom.on_set(module, cause, time, value, addressed)

    def get_symptom_last_updated_time(self, module: str, symptom: str) -> int | None:
        """Java: Person#getSymptomLastUpdatedTime(String, String)."""
        result: int | None = None
        if symptom in self.symptoms:
            result = self.symptoms[symptom].get_symptom_last_updated_time(module)
        return result

    def get_symptom(self, type: str) -> int:
        """Java: Person#getSymptom(String)."""
        max_value = 0
        if type in self.symptoms:
            max_value = self.symptoms[type].get_symptom()
        return max_value

    def get_symptoms(self) -> list[str]:
        """Java: Person#getSymptoms."""
        pairs = [(type_name, self.get_symptom(type_name)) for type_name in self.symptoms]
        # Java's stream sorted() is stable: severity descending, ties keep
        # ConcurrentHashMap keySet iteration order.
        pairs.sort(key=lambda pair: -pair[1])
        return [type_name for type_name, severity in pairs if severity >= 20]

    def address_largest_symptom(self) -> None:
        """Java: Person#addressLargestSymptom."""
        highest_type = ""
        highest_cause = ""
        max_value = 0
        for type_name in self.symptoms:
            expressed_symptom = self.symptoms[type_name]
            cause = expressed_symptom.get_source_with_high_value()
            if cause is not None:
                value = expressed_symptom.get_value_from_source(cause)
                if value is not None and value > max_value:
                    max_value = value
                    highest_cause = cause
                    highest_type = type_name
        target = self.symptoms.get(highest_type)
        if target is None:
            # Java: symptoms.get("").addressSource(...) on an empty map.
            raise TypeError("Java NullPointerException: no symptoms to address")
        target.address_source(highest_cause)

    def get_vital_sign(self, vital_sign: VitalSign, time: int) -> float:
        """Java: Person#getVitalSign(VitalSign, long)."""
        value_generator = self.vital_signs.get(vital_sign)
        if value_generator is None:
            valid = ", ".join(VITAL_SIGN_DISPLAY_NAMES[key] for key in self.vital_signs)
            raise TypeError(
                f"Vital sign '{VITAL_SIGN_DISPLAY_NAMES[vital_sign]}' not set. "
                f"Valid vital signs: [{valid}]"
            )
        value = value_generator.get_value(time)
        if vital_sign in (
            VitalSign.DIASTOLIC_BLOOD_PRESSURE,
            VitalSign.SYSTOLIC_BLOOD_PRESSURE,
            VitalSign.HEART_RATE,
            VitalSign.RESPIRATION_RATE,
        ):
            decimal_places = 0
        elif vital_sign in (VitalSign.HEIGHT, VitalSign.WEIGHT):
            decimal_places = 1
        else:
            decimal_places = 2
        ret_val = value
        if math.isfinite(value):
            # Java: BigDecimal.valueOf(value).setScale(dp, HALF_UP).doubleValue();
            # valueOf throws NumberFormatException for NaN/infinity, which Java
            # catches and ignores, returning the raw value.
            ret_val = bigdecimal.double_value(
                bigdecimal.set_scale(
                    bigdecimal.value_of(value), decimal_places, bigdecimal.RoundingMode.HALF_UP
                )
            )
        return ret_val

    def set_vital_sign(
        self, vital_sign: VitalSign, value_generator_or_value: ValueGenerator | float
    ) -> None:
        """Java: Person#setVitalSign(VitalSign, ValueGenerator) and
        #setVitalSign(VitalSign, double)."""
        if isinstance(value_generator_or_value, ValueGenerator):
            self.vital_signs[vital_sign] = value_generator_or_value
            return
        value = float(value_generator_or_value)
        if not math.isfinite(value):
            raise ValueError(
                f"Vital signs must have finite values - {double_to_string(value)} is invalid"
            )
        self.set_vital_sign(vital_sign, ConstantValueGenerator(cast("RandomSource", self), value))

    def record_death(self, time: int, cause: Code | None) -> None:
        """Java: Person#recordDeath(long, Code)."""
        if self.alive(time):
            death_time = time
            self.attributes[Person.DEATHDATE] = death_time
            if cause is None:
                self.attributes.pop(Person.CAUSE_OF_DEATH, None)
            else:
                self.attributes[Person.CAUSE_OF_DEATH] = cause
            record = self.record
            if record is None:
                raise TypeError("Java NullPointerException: record is null")
            record.death = death_time

    def symptom_total(self) -> int:
        """Java: Person#symptomTotal."""
        total = 0
        for type_name in self.symptoms:
            total += self.get_symptom(type_name)
        return total

    def had_prior_state(
        self, name: str, since: str | None = None, within: int | None = None
    ) -> bool:
        """Java: Person#hadPriorState(String) and #hadPriorState(String, String, Long)."""
        if self.history is None:
            return False
        for state in self.history:
            if within is not None and state.exited is not None and state.exited <= within:
                return False
            if since is not None and state.name == since:
                return False
            if state.name == name:
                return True
        return False

    def encounter_start(self, time: int, type: EncounterType) -> Encounter:
        """Java: Person#encounterStart(long, EncounterType)."""
        provider = self.get_provider(type, time)
        record = self.get_health_record(provider, time)
        self.record = record
        return record.encounter_start(time, type)

    def get_health_record(self, provider: Provider, time: int) -> HealthRecord:
        """Java: Person#getHealthRecord(Provider, long)."""
        if self.loss_of_care_enabled and not self.still_has_income(time):
            loss_record = self.loss_of_care_record
            if loss_record is None:
                raise TypeError("Java NullPointerException: lossOfCareRecord is null")
            return loss_record
        return_value = self.default_record
        if return_value is None:
            raise TypeError("Java NullPointerException: defaultRecord is null")
        if self.has_multiple_records:
            records = self.records
            if records is None:
                raise TypeError("Java NullPointerException: records is null")
            key = provider.get_resource_id()
            if key not in records:
                new_record: HealthRecord
                if self.record is not None and self.record.provider is None:
                    new_record = self.record
                else:
                    new_record = HealthRecord(self)
                new_record.provider = provider
                records[key] = new_record
            return_value = records[key]
        return return_value

    def get_current_encounter_module(self) -> str | None:
        """Java: Person#getCurrentEncounterModule."""
        return self.attributes.get(Person.CURRENT_ENCOUNTER_MODULE)  # type: ignore[return-value]

    def has_current_encounter(self) -> bool:
        """Java: Person#hasCurrentEncounter."""
        return Person.CURRENT_ENCOUNTER_MODULE in self.attributes

    def release_current_encounter(self, time: int, module: str) -> None:
        """Java: Person#releaseCurrentEncounter(long, String)."""
        self.attributes.pop(Person.CURRENT_ENCOUNTER_MODULE, None)

    def reserve_current_encounter(self, time: int, module: str) -> bool:
        """Java: Person#reserveCurrentEncounter(long, String)."""
        if self.has_current_encounter():
            return False
        self.attributes[Person.CURRENT_ENCOUNTER_MODULE] = module
        return True

    def get_provider(self, type: EncounterType, time: int) -> Provider:
        """Java: Person#getProvider(EncounterType, long)."""
        key = Person.PREFERREDYPROVIDER + type
        if key not in self.attributes:
            self.set_provider(type, time)
        else:
            entity = self.attributes.get(Person.ENTITY)
            if entity is not None:
                # Fixed records / identity are out of scope (PORTING_GUIDE §8);
                # the issue for this task keeps ENTITY unset (None).
                raise NotImplementedError(
                    "identity.Entity fixed-record provider check is out of scope"
                )
        return self.attributes[key]  # type: ignore[return-value]

    def set_provider(self, type: EncounterType, provider_or_time: Provider | int) -> None:
        """Java: Person#setProvider(EncounterType, Provider) and
        #setProvider(EncounterType, long)."""
        if isinstance(provider_or_time, int) and not isinstance(provider_or_time, bool):
            found = Provider.find_service(self, type, provider_or_time)
            if found is None and Provider.USE_HOSPITAL_AS_DEFAULT:
                found = Provider.find_service(self, EncounterType.INPATIENT, provider_or_time)
            if found is None:
                raise RuntimeError(f"Unable to find provider: {type.name}")
            provider_or_time = found
        if provider_or_time is None:
            raise RuntimeError(f"Unable to find provider: {type.name}")
        key = Person.PREFERREDYPROVIDER + type
        self.attributes[key] = provider_or_time

    def add_current_provider(self, context: str, provider: Provider) -> None:
        """Java: Person#addCurrentProvider(String, Provider)."""
        current_providers = self.attributes.get(Person.CURRENTPROVIDER)
        if current_providers is None:
            created: JavaHashMap[str, Provider] = JavaHashMap()
            created[context] = provider
            current_providers = created
        # Java quirk: when the map already exists, the new entry is NOT added.
        self.attributes[Person.CURRENTPROVIDER] = current_providers

    def remove_current_provider(self, module: str) -> None:
        """Java: Person#removeCurrentProvider(String)."""
        current_providers = self.attributes.get(Person.CURRENTPROVIDER)
        if current_providers is not None:
            cast("JavaHashMap[str, Provider]", current_providers).pop(module, None)

    def get_current_provider(self, module: str) -> Provider | None:
        """Java: Person#getCurrentProvider(String)."""
        current_providers = self.attributes.get(Person.CURRENTPROVIDER)
        if current_providers is None:
            return None
        return cast("JavaHashMap[str, Provider]", current_providers).get(module)

    def get_qalys(self) -> float:
        """Java: Person#getQalys."""
        qalys = self.attributes.get(QualityOfLifeModule.QALY)
        if qalys is None:
            raise TypeError("Java NullPointerException: QALY attribute is not set")
        total = 0.0
        for curr_qaly in qalys.values():  # type: ignore[attr-defined]
            total += curr_qaly
        return total

    def get_dalys(self) -> float:
        """Java: Person#getDalys."""
        dalys = self.attributes.get(QualityOfLifeModule.DALY)
        if dalys is None:
            raise TypeError("Java NullPointerException: DALY attribute is not set")
        total = 0.0
        for curr_daly in dalys.values():  # type: ignore[attr-defined]
            total += curr_daly
        return total

    def can_afford_plan(self, plan: InsurancePlan) -> bool:
        """Java: Person#canAffordPlan(InsurancePlan)."""
        income_percentage = Config.get_as_double(
            "generate.payers.insurance_plans.income_premium_ratio"
        )
        income = self.attributes.get(Person.INCOME)
        if not isinstance(income, int) or isinstance(income, bool):
            raise TypeError("Java ClassCastException: INCOME attribute is not an Integer")
        yearly_cost: Decimal = plan.get_yearly_cost(income)
        return (
            bigdecimal.compare_to(
                bigdecimal.multiply(
                    bigdecimal.value_of(float(income)), bigdecimal.value_of(income_percentage)
                ),
                yearly_cost,
            )
            >= 0
        )

    def still_has_income(self, time: int) -> bool:
        """Java: Person#stillHasIncome(long)."""
        income_remaining = self.coverage.income_remaining(time)
        still_has = income_remaining > 0
        if not still_has and not self.coverage.get_plan_at_time(time).is_no_insurance():
            self.coverage.set_plan_to_no_insurance(time)
        return still_has

    def check_to_pay_monthly_premium(self, time: int) -> None:
        """Java: Person#checkToPayMonthlyPremium(long)."""
        if Person.LAST_MONTH_PAID not in self.attributes:
            self.attributes[Person.LAST_MONTH_PAID] = 0
        current_month = Utilities.get_month(time)
        last_month_paid = self.attributes[Person.LAST_MONTH_PAID]
        if current_month > last_month_paid or (  # type: ignore[operator]
            current_month == 1 and last_month_paid == 12
        ):
            self.coverage.pay_monthly_premiums_at_time(
                time,
                _as_float(self.attributes[Person.OCCUPATION_LEVEL], "occupation_level"),
                _as_int(self.attributes[Person.INCOME], "income"),
            )
            self.attributes[Person.LAST_MONTH_PAID] = current_month
            self.still_has_income(time)

    def get_qols_for_year(self, year: int) -> float:
        """Java: Person#getQolsForYear(int)."""
        ret_val = 0.0
        qols = self.attributes.get(QualityOfLifeModule.QOLS)
        if qols is not None and year in qols:  # type: ignore[operator]
            ret_val = qols[year]  # type: ignore[index]
        return ret_val

    def get_x(self) -> float:
        """Java: Person#getX (QuadTreeElement)."""
        return self.get_lon_lat().get_x()

    def get_y(self) -> float:
        """Java: Person#getY (QuadTreeElement)."""
        return self.get_lon_lat().get_y()

    def get_lon_lat(self) -> Point2DDouble:
        """Java: Person#getLonLat."""
        coordinate = self.attributes.get(Person.COORDINATE)
        if coordinate is None:
            raise TypeError("Java NullPointerException: COORDINATE attribute is not set")
        return coordinate  # type: ignore[return-value]
