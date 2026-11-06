"""Java: org.mitre.synthea.engine.Logic (T17).

Logic represents any portion of a generic module that requires a logical
expression. Logic is stateless, and calling ``test`` on an instance must not
modify state, as instances of Logic within Modules are shared across the
population. (The one Java exception, reproduced faithfully: Observation
caches a ``value_code`` into its ``value`` field, and PriorState caches the
converted ``window``.)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import cast

from synthea.engine.components import DateInput, ExactWithUnit
from synthea.helpers.config import Config
from synthea.helpers.utilities import Utilities
from synthea.world.agents.person import Person
from synthea.world.concepts.health_record import (
    Allergy,
    CarePlan,
    Code,
    Entry,
    Medication,
)
from synthea.world.concepts.health_record import (
    Observation as RecordObservation,
)
from synthea.world.concepts.vital_sign import VitalSign as ConceptVitalSign


def _java_value_to_string(value: object) -> str:
    """Java ``String.valueOf(Object)`` as used in string concatenation."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        from synthea.javacompat.numbers import double_to_string

        return double_to_string(value)
    return str(value)


def _days_from_civil(year: int, month: int, day: int) -> int:
    """Days since 1970-01-01 for a proleptic Gregorian date (month in 1..12)."""
    y = year - (1 if month <= 2 else 0)
    era = (y if y >= 0 else y - 399) // 400
    yoe = y - era * 400
    mp = (month + 9) % 12
    doy = (153 * mp + 2) // 5 + day - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    return era * 146097 + doe - 719468


def _calendar_time_millis_utc(date: DateInput) -> int:
    """Java ``Calendar`` (UTC, lenient) ``getTimeInMillis`` for the fields that
    ``Logic.Date`` sets: year, month - 1, day, hour, minute, second, then
    MILLISECOND. Out-of-range fields roll over, as a lenient Calendar does.
    """
    month_index = date.month - 1
    year = date.year + month_index // 12
    month = month_index % 12 + 1
    days = _days_from_civil(year, month, 1) + (date.day - 1)
    return (
        days * 86400000
        + ((date.hour * 60 + date.minute) * 60 + date.second) * 1000
        + date.millisecond
    )


def _equals_ignore_case(left: str, right: str) -> bool:
    """Java ``String.equalsIgnoreCase``: per-character, case-insensitive."""
    if len(left) != len(right):
        return False
    return all(
        a == b or a.upper() == b.upper() or a.lower() == b.lower()
        for a, b in zip(left, right, strict=True)
    )


class Logic(ABC):
    """Java: Logic — abstract base for every module condition type."""

    def __init__(self) -> None:
        """Java: Logic#Logic (implicit default constructor)."""
        self.remarks: list[str] | None = None

    @abstractmethod
    def test(self, person: Person, time: int) -> bool:
        """Java: Logic#test — abstract; subclasses implement it.

        Java overloads:
        (Person person, long time)
        """

    @staticmethod
    def find_entry_from_history[T: Entry](
        person: Person, class_type: type[T], code: Code
    ) -> Entry | None:
        """Java: Logic#findEntryFromHistory (private in Java).

        Find the most recent entry (the history is newest-first) of a specific
        type of HealthRecord.Entry within the patient history. May return
        None.

        Java overloads:
        (Person person, Class classType, Code code)
        """
        entry: Entry | None = None
        if person.history is None:
            # Java: NullPointerException iterating a null history.
            raise TypeError("Cannot iterate a null person history")
        for state in person.history:
            if state.entry is not None and isinstance(state.entry, class_type):
                candidate = state.entry
                for candidate_code in candidate.codes:
                    if candidate_code == code:
                        entry = candidate
                        break
            if entry is not None:
                break
        return entry


class Gender(Logic):
    """Java: Logic.Gender — tests the patient's gender (M or F)."""

    def __init__(self) -> None:
        """Java: Gender#Gender (implicit default constructor)."""
        super().__init__()
        self.gender: str | None = None

    def test(self, person: Person, time: int) -> bool:
        """Java: Gender#test.

        Java overloads:
        (Person person, long time)
        """
        if self.gender is None:
            # Java: NullPointerException, gender.equals(...) on a null field.
            raise TypeError('Cannot invoke "String.equals(Object)" because "gender" is null')
        return self.gender == person.attributes.get(Person.GENDER)


class Age(Logic):
    """Java: Logic.Age — tests the patient's age, in a given unit."""

    def __init__(self) -> None:
        """Java: Age#Age (implicit default constructor)."""
        super().__init__()
        self.quantity: float | None = None
        self.unit: str | None = None
        self.operator: str | None = None

    def test(self, person: Person, time: int) -> bool:
        """Java: Age#test.

        Java overloads:
        (Person person, long time)
        """
        if self.unit is None:
            # Java: NullPointerException, switch on a null unit.
            raise TypeError("Cannot switch on a null unit")
        if self.unit == "years":
            age = float(person.age_in_years(time))
        elif self.unit == "months":
            age = float(person.age_in_months(time))
        else:
            # TODO - add more unit types if we determine they are necessary
            # Java: UnsupportedOperationException (a RuntimeException).
            raise RuntimeError("Units '" + self.unit + "' not currently supported in Age logic.")

        assert self.operator is not None
        return Utilities.compare(age, self.quantity, self.operator)


class Date(Logic):
    """Java: Logic.Date — tests the current year, month, or date being simulated."""

    def __init__(self) -> None:
        """Java: Date#Date (implicit default constructor)."""
        super().__init__()
        self.year: int | None = None
        self.month: int | None = None
        self.date: DateInput | None = None
        self.operator: str | None = None

    def test(self, person: Person, time: int) -> bool:
        """Java: Date#test.

        Java overloads:
        (Person person, long time)
        """
        assert self.operator is not None
        if self.year is not None:
            currentyear = Utilities.get_year(time)
            return Utilities.compare(currentyear, self.year, self.operator)
        elif self.month is not None:
            currentmonth = Utilities.get_month(time)
            return Utilities.compare(currentmonth, self.month, self.operator)
        elif self.date is not None:
            test_time = _calendar_time_millis_utc(self.date)
            return Utilities.compare(time, test_time, self.operator)
        else:
            # Java: UnsupportedOperationException (a RuntimeException).
            raise RuntimeError("Date type not currently supported in Date logic.")


class SocioeconomicStatus(Logic):
    """Java: Logic.SocioeconomicStatus — tests the patient's socioeconomic status
    ("High", "Middle", or "Low", based on income, education, and occupation)."""

    def __init__(self) -> None:
        """Java: SocioeconomicStatus#SocioeconomicStatus (implicit default constructor)."""
        super().__init__()
        self.category: str | None = None

    def test(self, person: Person, time: int) -> bool:
        """Java: SocioeconomicStatus#test.

        Java overloads:
        (Person person, long time)
        """
        if self.category is None:
            # Java: NullPointerException, category.equals(...) on a null field.
            raise TypeError('Cannot invoke "String.equals(Object)" because "category" is null')
        return self.category == person.attributes.get(Person.SOCIOECONOMIC_CATEGORY)


class Race(Logic):
    """Java: Logic.Race — tests a patient's race ("White", "Native", "Hispanic",
    "Black", "Asian", and "Other" are supported)."""

    def __init__(self) -> None:
        """Java: Race#Race (implicit default constructor)."""
        super().__init__()
        self.race: str | None = None

    def test(self, person: Person, time: int) -> bool:
        """Java: Race#test.

        Java overloads:
        (Person person, long time)
        """
        if self.race is None:
            # Java: NullPointerException, race.equalsIgnoreCase(...) on a null field.
            raise TypeError(
                'Cannot invoke "String.equalsIgnoreCase(String)" because "race" is null'
            )
        value = person.attributes.get(Person.RACE)
        if value is None:
            # Java: equalsIgnoreCase(null) is false.
            return False
        if not isinstance(value, str):
            # Java: ClassCastException casting the attribute to String.
            raise TypeError(f"Cannot cast {type(value).__name__} to String (Person.RACE)")
        return _equals_ignore_case(self.race, value)


class Symptom(Logic):
    """Java: Logic.Symptom — tests a patient's current symptoms (scale of 1-100;
    a symptom tracked for multiple conditions considers only the highest value)."""

    def __init__(self) -> None:
        """Java: Symptom#Symptom (implicit default constructor)."""
        super().__init__()
        self.symptom: str | None = None
        self.operator: str | None = None
        self.value: float = 0.0

    def test(self, person: Person, time: int) -> bool:
        """Java: Symptom#test.

        Java overloads:
        (Person person, long time)
        """
        assert self.symptom is not None and self.operator is not None
        return Utilities.compare(float(person.get_symptom(self.symptom)), self.value, self.operator)


class Observation(Logic):
    """Java: Logic.Observation — tests the most recent observation of a given
    type against a given value."""

    def __init__(self) -> None:
        """Java: Observation#Observation (implicit default constructor)."""
        super().__init__()
        self.operator: str | None = None
        self.codes: list[Code] | None = None
        self.referenced_by_attribute: str | None = None
        self.value: object = None
        self.value_code: Code | None = None

    def test(self, person: Person, time: int) -> bool:
        """Java: Observation#test.

        Java overloads:
        (Person person, long time)
        """
        observation: RecordObservation | None = None
        if self.codes is not None:
            assert person.record is not None
            for code in self.codes:
                # First, look in the current health record for the latest observation
                last = person.record.get_latest_observation(code.code)
                if person.loss_of_care_enabled:
                    if last is None:
                        # If the observation is not in the current record,
                        # it could be in the uncovered health record.
                        assert person.loss_of_care_record is not None
                        last = person.loss_of_care_record.get_latest_observation(code.code)
                    if last is None:
                        # If the observation still is not in the uncovered health record,
                        # it could be in the covered health record.
                        assert person.default_record is not None
                        last = person.default_record.get_latest_observation(code.code)
                if last is None and person.has_multiple_records:
                    # If the latest observation is not in the covered/uncovered
                    # health record, then look in the module history.
                    last = cast(
                        "RecordObservation | None",
                        Logic.find_entry_from_history(person, RecordObservation, code),
                    )
                    if Config.get_as_boolean("exporter.split_records.duplicate_data", False):
                        # Java adds `last` here even when the history search
                        # found nothing (a null entry in the observations list).
                        person.record.current_encounter(time).observations.append(
                            cast("RecordObservation", last)
                        )
                if last is not None:
                    observation = last
                    break
        elif self.referenced_by_attribute is not None:
            if self.referenced_by_attribute in person.attributes:
                observation = cast(
                    "RecordObservation",
                    person.attributes.get(self.referenced_by_attribute),
                )
            else:
                return False
        if self.value_code is not None:
            self.value = self.value_code
        if self.operator == "is nil":
            return observation is None
        elif self.operator == "is not nil":
            return observation is not None
        elif observation is None:
            if self.codes is not None:
                # TODO - This is a band-aid to try and swallow this exception and just
                # return false if using split records.
                # This issue occurs occasionally when using the split records feature -
                # see https://github.com/synthetichealth/synthea/issues/774.
                if Config.get_as_boolean("exporter.split_records", False):
                    return False
                # Original exception that should be thrown:
                # Java: NullPointerException, mirrored as TypeError.
                raise TypeError("Required observation " + str(self.codes) + " is null.")
            elif self.referenced_by_attribute is not None:
                raise TypeError(
                    'Required observation "' + self.referenced_by_attribute + '" is null.'
                )
            else:
                raise TypeError("Required observation is null.")
        else:
            assert self.operator is not None
            return Utilities.compare(observation.value, self.value, self.operator)


class Attribute(Logic):
    """Java: Logic.Attribute — tests a named attribute on the patient entity."""

    def __init__(self) -> None:
        """Java: Attribute#Attribute (implicit default constructor)."""
        super().__init__()
        self.attribute: str | None = None
        self.operator: str | None = None
        self.value: object = None

    def test(self, person: Person, time: int) -> bool:
        """Java: Attribute#test.

        Java overloads:
        (Person person, long time)
        """
        try:
            assert self.attribute is not None and self.operator is not None
            return Utilities.compare(
                person.attributes.get(self.attribute), self.value, self.operator
            )
        except Exception as e:
            message = (
                "Attribute Logic error: "
                + _java_value_to_string(self.attribute)
                + " "
                + _java_value_to_string(self.operator)
                + " "
                + _java_value_to_string(self.value)
            )
            message += ": " + _java_value_to_string(str(e) if str(e) else None)
            raise RuntimeError(message) from e


class GroupedCondition(Logic):
    """Java: Logic.GroupedCondition — parent class for Logic that aggregates
    multiple conditions. It should never be used directly in a JSON file."""

    def __init__(self) -> None:
        """Java: GroupedCondition#GroupedCondition (implicit default constructor)."""
        super().__init__()
        self.conditions: list[Logic] | None = None


class And(GroupedCondition):
    """Java: Logic.And — tests that a set of sub-conditions are all true."""

    def __init__(self) -> None:
        """Java: And#And (implicit default constructor)."""
        super().__init__()

    def test(self, person: Person, time: int) -> bool:
        """Java: And#test (stream allMatch: short-circuits on the first false).

        Java overloads:
        (Person person, long time)
        """
        assert self.conditions is not None
        return all(condition.test(person, time) for condition in self.conditions)


class Or(GroupedCondition):
    """Java: Logic.Or — tests that at least one of its sub-conditions is true."""

    def __init__(self) -> None:
        """Java: Or#Or (implicit default constructor)."""
        super().__init__()

    def test(self, person: Person, time: int) -> bool:
        """Java: Or#test (stream anyMatch: short-circuits on the first true).

        Java overloads:
        (Person person, long time)
        """
        assert self.conditions is not None
        return any(condition.test(person, time) for condition in self.conditions)


class Not(Logic):
    """Java: Logic.Not — negates its sub-condition."""

    def __init__(self) -> None:
        """Java: Not#Not (implicit default constructor)."""
        super().__init__()
        self.condition: Logic | None = None

    def test(self, person: Person, time: int) -> bool:
        """Java: Not#test.

        Java overloads:
        (Person person, long time)
        """
        assert self.condition is not None
        return not self.condition.test(person, time)


class AtLeast(GroupedCondition):
    """Java: Logic.AtLeast — tests that a minimum number of conditions from a
    set of sub-conditions are true."""

    def __init__(self) -> None:
        """Java: AtLeast#AtLeast (implicit default constructor)."""
        super().__init__()
        self.minimum: int | None = None

    def test(self, person: Person, time: int) -> bool:
        """Java: AtLeast#test (stream filter + count: evaluates every condition).

        Java overloads:
        (Person person, long time)
        """
        assert self.conditions is not None and self.minimum is not None
        return (
            sum(1 for condition in self.conditions if condition.test(person, time)) >= self.minimum
        )


class AtMost(GroupedCondition):
    """Java: Logic.AtMost — tests that a maximum number of conditions from a
    set of sub-conditions are true."""

    def __init__(self) -> None:
        """Java: AtMost#AtMost (implicit default constructor)."""
        super().__init__()
        self.maximum: int | None = None

    def test(self, person: Person, time: int) -> bool:
        """Java: AtMost#test (stream filter + count: evaluates every condition).

        Java overloads:
        (Person person, long time)
        """
        assert self.conditions is not None and self.maximum is not None
        return (
            sum(1 for condition in self.conditions if condition.test(person, time)) <= self.maximum
        )


class TrueLogic(Logic):
    """Java: Logic.True — always returns true. Mainly used for testing."""

    def __init__(self) -> None:
        """Java: True#True (implicit default constructor)."""
        super().__init__()

    def test(self, person: Person, time: int) -> bool:
        """Java: True#test.

        Java overloads:
        (Person person, long time)
        """
        return True


class FalseLogic(Logic):
    """Java: Logic.False — always returns false. Mainly used for testing."""

    def __init__(self) -> None:
        """Java: False#False (implicit default constructor)."""
        super().__init__()

    def test(self, person: Person, time: int) -> bool:
        """Java: False#test.

        Java overloads:
        (Person person, long time)
        """
        return False


class PriorState(Logic):
    """Java: Logic.PriorState — tests whether a specific state has already been
    processed (it is in the module's state history), optionally limited by
    time or by the name of another state."""

    def __init__(self) -> None:
        """Java: PriorState#PriorState (implicit default constructor)."""
        super().__init__()
        self.name: str | None = None
        self.since: str | None = None
        self.within: ExactWithUnit[float] | None = None
        self.window: int | None = None

    def test(self, person: Person, time: int) -> bool:
        """Java: PriorState#test.

        Java overloads:
        (Person person, long time)
        """
        since_time: int | None = None

        if self.within is not None:
            if self.window is None:
                # cache the value since it doesn't depend on person or time
                assert self.within.unit is not None and self.within.quantity is not None
                self.window = Utilities.convert_time(self.within.unit, self.within.quantity)
            since_time = time - self.window

        assert self.name is not None
        return person.had_prior_state(self.name, self.since, since_time)


class ActiveLogic(Logic):
    """Java: Logic.ActiveLogic — parent class for logics that look up "active"
    things. This class should never be referenced directly."""

    def __init__(self) -> None:
        """Java: ActiveLogic#ActiveLogic (implicit default constructor)."""
        super().__init__()
        self.codes: list[Code] | None = None
        self.referenced_by_attribute: str | None = None

    @abstractmethod
    def check_code(self, person: Person, code: Code) -> bool:
        """Java: ActiveLogic#checkCode — abstract.

        Java overloads:
        (Person person, HealthRecord.Code code)
        """

    @abstractmethod
    def check_attribute(self, person: Person, entry: Entry) -> bool:
        """Java: ActiveLogic#checkAttribute — abstract.

        Java overloads:
        (Person person, HealthRecord.Entry entry)
        """

    @abstractmethod
    def find_item_when_multiple_records(self, person: Person, code: Code) -> Entry | None:
        """Java: ActiveLogic#findItemWhenMultipleRecords — abstract.

        Java overloads:
        (Person person, HealthRecord.Code code)
        """

    @abstractmethod
    def add_item_when_data_is_duplicated(self, person: Person, time: int, entry: Entry) -> None:
        """Java: ActiveLogic#addItemWhenDataIsDuplicated — abstract.

        Java overloads:
        (Person person, long time, HealthRecord.Entry entry)
        """

    def test(self, person: Person, time: int) -> bool:
        """Java: ActiveLogic#test.

        Java overloads:
        (Person person, long time)
        """
        if self.codes is not None:
            for code in self.codes:
                if self.check_code(person, code):
                    return True
                if person.has_multiple_records:
                    entry = self.find_item_when_multiple_records(person, code)
                    if entry is not None and entry.stop == 0:
                        if Config.get_as_boolean("exporter.split_records.duplicate_data", False):
                            self.add_item_when_data_is_duplicated(person, time, entry)
                        return True
            return False
        elif self.referenced_by_attribute is not None:
            if self.referenced_by_attribute in person.attributes:
                return self.check_attribute(
                    person,
                    cast(Entry, person.attributes.get(self.referenced_by_attribute)),
                )
            else:
                return False

        raise RuntimeError(f"{type(self).__name__} logic must be specified by code or attribute")


class ActiveCondition(ActiveLogic):
    """Java: Logic.ActiveCondition — tests whether a given condition is
    currently diagnosed and active on the patient."""

    def __init__(self) -> None:
        """Java: ActiveCondition#ActiveCondition (implicit default constructor)."""
        super().__init__()

    def check_code(self, person: Person, code: Code) -> bool:
        """Java: ActiveCondition#checkCode.

        Java overloads:
        (Person person, Code code)
        """
        assert person.record is not None
        return code.code in person.record.present

    def check_attribute(self, person: Person, entry: Entry) -> bool:
        """Java: ActiveCondition#checkAttribute.

        Java overloads:
        (Person person, Entry entry)
        """
        assert person.record is not None
        return entry.type in person.record.present

    def find_item_when_multiple_records(self, person: Person, code: Code) -> Entry | None:
        """Java: ActiveCondition#findItemWhenMultipleRecords.

        Java overloads:
        (Person person, Code code)
        """
        return Logic.find_entry_from_history(person, Entry, code)

    def add_item_when_data_is_duplicated(self, person: Person, time: int, entry: Entry) -> None:
        """Java: ActiveCondition#addItemWhenDataIsDuplicated.

        Java overloads:
        (Person person, long time, Entry entry)
        """
        assert person.record is not None
        person.record.current_encounter(time).conditions.append(entry)


class ActiveAllergy(ActiveLogic):
    """Java: Logic.ActiveAllergy — tests whether a given allergy is active."""

    def __init__(self) -> None:
        """Java: ActiveAllergy#ActiveAllergy (implicit default constructor)."""
        super().__init__()

    def check_code(self, person: Person, code: Code) -> bool:
        """Java: ActiveAllergy#checkCode.

        Java overloads:
        (Person person, Code code)
        """
        assert person.record is not None
        return code.code in person.record.present

    def check_attribute(self, person: Person, entry: Entry) -> bool:
        """Java: ActiveAllergy#checkAttribute.

        Java overloads:
        (Person person, Entry entry)
        """
        assert person.record is not None
        return entry.type in person.record.present

    def find_item_when_multiple_records(self, person: Person, code: Code) -> Entry | None:
        """Java: ActiveAllergy#findItemWhenMultipleRecords.

        Java overloads:
        (Person person, Code code)
        """
        return Logic.find_entry_from_history(person, Allergy, code)

    def add_item_when_data_is_duplicated(self, person: Person, time: int, entry: Entry) -> None:
        """Java: ActiveAllergy#addItemWhenDataIsDuplicated.

        Java overloads:
        (Person person, long time, Entry entry)
        """
        assert person.record is not None
        person.record.current_encounter(time).allergies.append(cast(Allergy, entry))


class ActiveMedication(ActiveLogic):
    """Java: Logic.ActiveMedication — tests whether a given medication is
    currently prescribed and active for the patient."""

    def __init__(self) -> None:
        """Java: ActiveMedication#ActiveMedication (implicit default constructor)."""
        super().__init__()

    def check_code(self, person: Person, code: Code) -> bool:
        """Java: ActiveMedication#checkCode.

        Java overloads:
        (Person person, Code code)
        """
        assert person.record is not None
        return person.record.medication_active(code.code)

    def check_attribute(self, person: Person, entry: Entry) -> bool:
        """Java: ActiveMedication#checkAttribute.

        Java overloads:
        (Person person, Entry entry)
        """
        assert person.record is not None
        return person.record.medication_active(entry.type)

    def find_item_when_multiple_records(self, person: Person, code: Code) -> Entry | None:
        """Java: ActiveMedication#findItemWhenMultipleRecords.

        Java overloads:
        (Person person, Code code)
        """
        return Logic.find_entry_from_history(person, Medication, code)

    def add_item_when_data_is_duplicated(self, person: Person, time: int, entry: Entry) -> None:
        """Java: ActiveMedication#addItemWhenDataIsDuplicated.

        Java overloads:
        (Person person, long time, Entry entry)
        """
        assert person.record is not None
        person.record.current_encounter(time).medications.append(cast(Medication, entry))


class ActiveCarePlan(ActiveLogic):
    """Java: Logic.ActiveCarePlan — tests whether a given care plan is
    currently prescribed and active for the patient."""

    def __init__(self) -> None:
        """Java: ActiveCarePlan#ActiveCarePlan (implicit default constructor)."""
        super().__init__()

    def check_code(self, person: Person, code: Code) -> bool:
        """Java: ActiveCarePlan#checkCode.

        Java overloads:
        (Person person, Code code)
        """
        assert person.record is not None
        return person.record.careplan_active(code.code)

    def check_attribute(self, person: Person, entry: Entry) -> bool:
        """Java: ActiveCarePlan#checkAttribute.

        Java overloads:
        (Person person, Entry entry)
        """
        assert person.record is not None
        return person.record.careplan_active(entry.type)

    def find_item_when_multiple_records(self, person: Person, code: Code) -> Entry | None:
        """Java: ActiveCarePlan#findItemWhenMultipleRecords.

        Java overloads:
        (Person person, Code code)
        """
        return Logic.find_entry_from_history(person, CarePlan, code)

    def add_item_when_data_is_duplicated(self, person: Person, time: int, entry: Entry) -> None:
        """Java: ActiveCarePlan#addItemWhenDataIsDuplicated.

        Java overloads:
        (Person person, long time, Entry entry)
        """
        assert person.record is not None
        person.record.current_encounter(time).careplans.append(cast(CarePlan, entry))


class VitalSign(Logic):
    """Java: Logic.VitalSign — tests a patient's current vital signs."""

    def __init__(self) -> None:
        """Java: VitalSign#VitalSign (implicit default constructor)."""
        super().__init__()
        self.vital_sign: ConceptVitalSign | None = None
        self.operator: str | None = None
        self.value: float = 0.0

    def test(self, person: Person, time: int) -> bool:
        """Java: VitalSign#test.

        Java overloads:
        (Person person, long time)
        """
        assert self.vital_sign is not None and self.operator is not None
        return Utilities.compare(
            person.get_vital_sign(self.vital_sign, time), self.value, self.operator
        )


setattr(Logic, "Gender", Gender)  # noqa: B010
setattr(Logic, "Age", Age)  # noqa: B010
setattr(Logic, "Date", Date)  # noqa: B010
setattr(Logic, "SocioeconomicStatus", SocioeconomicStatus)  # noqa: B010
setattr(Logic, "Race", Race)  # noqa: B010
setattr(Logic, "Symptom", Symptom)  # noqa: B010
setattr(Logic, "Observation", Observation)  # noqa: B010
setattr(Logic, "Attribute", Attribute)  # noqa: B010
setattr(Logic, "GroupedCondition", GroupedCondition)  # noqa: B010
setattr(Logic, "And", And)  # noqa: B010
setattr(Logic, "Or", Or)  # noqa: B010
setattr(Logic, "Not", Not)  # noqa: B010
setattr(Logic, "AtLeast", AtLeast)  # noqa: B010
setattr(Logic, "AtMost", AtMost)  # noqa: B010
setattr(Logic, "True", TrueLogic)
setattr(Logic, "False", FalseLogic)
setattr(Logic, "PriorState", PriorState)  # noqa: B010
setattr(Logic, "ActiveLogic", ActiveLogic)  # noqa: B010
setattr(Logic, "ActiveCondition", ActiveCondition)  # noqa: B010
setattr(Logic, "ActiveAllergy", ActiveAllergy)  # noqa: B010
setattr(Logic, "ActiveMedication", ActiveMedication)  # noqa: B010
setattr(Logic, "ActiveCarePlan", ActiveCarePlan)  # noqa: B010
setattr(Logic, "VitalSign", VitalSign)  # noqa: B010
FalseLogic.__name__ = "False"
globals()["False"] = FalseLogic
TrueLogic.__name__ = "True"
globals()["True"] = TrueLogic
