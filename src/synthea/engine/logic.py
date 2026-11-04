"""Java API skeleton: Logic.java."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synthea.engine.components import DateInput, ExactWithUnit
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import Code, Entry
    from synthea.world.concepts.health_record import Code as HealthRecordCode
    from synthea.world.concepts.health_record import Entry as HealthRecordEntry
    from synthea.world.concepts.vital_sign import VitalSign as ConceptVitalSign


class Logic:
    """Java: Logic; pending T17."""

    def __init__(self) -> None:
        """Java: Logic#Logic.

        Java overloads:
        ()
        """
        self.remarks: list[str]
        raise NotImplementedError("Java: Logic#Logic — pending T17")

    def test(self, person: Person, time: int) -> bool:
        """Java: Logic#test.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Logic#test — pending T17")

    @staticmethod
    def find_entry_from_history[T](
        person: Person, class_type: type[T], code: Code
    ) -> HealthRecordEntry:
        """Java: Logic#findEntryFromHistory.

        Java overloads:
        (Person person, Class classType, Code code)
        """
        raise NotImplementedError("Java: Logic#findEntryFromHistory — pending T17")


class Gender(Logic):
    """Java: Gender; pending T17."""

    def __init__(self) -> None:
        """Java: Gender#Gender.

        Java overloads:
        ()
        """
        self.gender: str
        raise NotImplementedError("Java: Gender#Gender — pending T17")

    def test(self, person: Person, time: int) -> bool:
        """Java: Gender#test.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Gender#test — pending T17")


class Age(Logic):
    """Java: Age; pending T17."""

    def __init__(self) -> None:
        """Java: Age#Age.

        Java overloads:
        ()
        """
        self.quantity: float
        self.unit: str
        self.operator: str
        raise NotImplementedError("Java: Age#Age — pending T17")

    def test(self, person: Person, time: int) -> bool:
        """Java: Age#test.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Age#test — pending T17")


class Date(Logic):
    """Java: Date; pending T17."""

    def __init__(self) -> None:
        """Java: Date#Date.

        Java overloads:
        ()
        """
        self.year: int
        self.month: int
        self.date: DateInput
        self.operator: str
        raise NotImplementedError("Java: Date#Date — pending T17")

    def test(self, person: Person, time: int) -> bool:
        """Java: Date#test.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Date#test — pending T17")


class SocioeconomicStatus(Logic):
    """Java: SocioeconomicStatus; pending T17."""

    def __init__(self) -> None:
        """Java: SocioeconomicStatus#SocioeconomicStatus.

        Java overloads:
        ()
        """
        self.category: str
        raise NotImplementedError("Java: SocioeconomicStatus#SocioeconomicStatus — pending T17")

    def test(self, person: Person, time: int) -> bool:
        """Java: SocioeconomicStatus#test.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: SocioeconomicStatus#test — pending T17")


class Race(Logic):
    """Java: Race; pending T17."""

    def __init__(self) -> None:
        """Java: Race#Race.

        Java overloads:
        ()
        """
        self.race: str
        raise NotImplementedError("Java: Race#Race — pending T17")

    def test(self, person: Person, time: int) -> bool:
        """Java: Race#test.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Race#test — pending T17")


class Symptom(Logic):
    """Java: Symptom; pending T17."""

    def __init__(self) -> None:
        """Java: Symptom#Symptom.

        Java overloads:
        ()
        """
        self.symptom: str
        self.operator: str
        self.value: float
        raise NotImplementedError("Java: Symptom#Symptom — pending T17")

    def test(self, person: Person, time: int) -> bool:
        """Java: Symptom#test.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Symptom#test — pending T17")


class Observation(Logic):
    """Java: Observation; pending T17."""

    def __init__(self) -> None:
        """Java: Observation#Observation.

        Java overloads:
        ()
        """
        self.operator: str
        self.codes: list[Code]
        self.referenced_by_attribute: str
        self.value: object
        self.value_code: Code
        raise NotImplementedError("Java: Observation#Observation — pending T17")

    def test(self, person: Person, time: int) -> bool:
        """Java: Observation#test.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Observation#test — pending T17")


class Attribute(Logic):
    """Java: Attribute; pending T17."""

    def __init__(self) -> None:
        """Java: Attribute#Attribute.

        Java overloads:
        ()
        """
        self.attribute: str
        self.operator: str
        self.value: object
        raise NotImplementedError("Java: Attribute#Attribute — pending T17")

    def test(self, person: Person, time: int) -> bool:
        """Java: Attribute#test.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Attribute#test — pending T17")


class GroupedCondition(Logic):
    """Java: GroupedCondition; pending T17."""

    def __init__(self) -> None:
        """Java: GroupedCondition#GroupedCondition.

        Java overloads:
        ()
        """
        self.conditions: list[Logic]
        raise NotImplementedError("Java: GroupedCondition#GroupedCondition — pending T17")


class And(GroupedCondition):
    """Java: And; pending T17."""

    def __init__(self) -> None:
        """Java: And#And.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: And#And — pending T17")

    def test(self, person: Person, time: int) -> bool:
        """Java: And#test.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: And#test — pending T17")


class Or(GroupedCondition):
    """Java: Or; pending T17."""

    def __init__(self) -> None:
        """Java: Or#Or.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Or#Or — pending T17")

    def test(self, person: Person, time: int) -> bool:
        """Java: Or#test.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Or#test — pending T17")


class Not(Logic):
    """Java: Not; pending T17."""

    def __init__(self) -> None:
        """Java: Not#Not.

        Java overloads:
        ()
        """
        self.condition: Logic
        raise NotImplementedError("Java: Not#Not — pending T17")

    def test(self, person: Person, time: int) -> bool:
        """Java: Not#test.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Not#test — pending T17")


class AtLeast(GroupedCondition):
    """Java: AtLeast; pending T17."""

    def __init__(self) -> None:
        """Java: AtLeast#AtLeast.

        Java overloads:
        ()
        """
        self.minimum: int
        raise NotImplementedError("Java: AtLeast#AtLeast — pending T17")

    def test(self, person: Person, time: int) -> bool:
        """Java: AtLeast#test.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: AtLeast#test — pending T17")


class AtMost(GroupedCondition):
    """Java: AtMost; pending T17."""

    def __init__(self) -> None:
        """Java: AtMost#AtMost.

        Java overloads:
        ()
        """
        self.maximum: int
        raise NotImplementedError("Java: AtMost#AtMost — pending T17")

    def test(self, person: Person, time: int) -> bool:
        """Java: AtMost#test.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: AtMost#test — pending T17")


class TrueLogic(Logic):
    """Java: True; pending T17."""

    def __init__(self) -> None:
        """Java: True#True.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: True#True — pending T17")

    def test(self, person: Person, time: int) -> bool:
        """Java: True#test.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: True#test — pending T17")


class FalseLogic(Logic):
    """Java: False; pending T17."""

    def __init__(self) -> None:
        """Java: False#False.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: False#False — pending T17")

    def test(self, person: Person, time: int) -> bool:
        """Java: False#test.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: False#test — pending T17")


class PriorState(Logic):
    """Java: PriorState; pending T17."""

    def __init__(self) -> None:
        """Java: PriorState#PriorState.

        Java overloads:
        ()
        """
        self.name: str
        self.since: str
        self.within: ExactWithUnit[float]
        self.window: int
        raise NotImplementedError("Java: PriorState#PriorState — pending T17")

    def test(self, person: Person, time: int) -> bool:
        """Java: PriorState#test.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: PriorState#test — pending T17")


class ActiveLogic(Logic):
    """Java: ActiveLogic; pending T17."""

    def __init__(self) -> None:
        """Java: ActiveLogic#ActiveLogic.

        Java overloads:
        ()
        """
        self.codes: list[Code]
        self.referenced_by_attribute: str
        raise NotImplementedError("Java: ActiveLogic#ActiveLogic — pending T17")

    def check_code(self, person: Person, code: HealthRecordCode) -> bool:
        """Java: ActiveLogic#checkCode.

        Java overloads:
        (Person person, HealthRecord.Code code)
        """
        raise NotImplementedError("Java: ActiveLogic#checkCode — pending T17")

    def check_attribute(self, person: Person, entry: HealthRecordEntry) -> bool:
        """Java: ActiveLogic#checkAttribute.

        Java overloads:
        (Person person, HealthRecord.Entry entry)
        """
        raise NotImplementedError("Java: ActiveLogic#checkAttribute — pending T17")

    def find_item_when_multiple_records(
        self, person: Person, code: HealthRecordCode
    ) -> HealthRecordEntry:
        """Java: ActiveLogic#findItemWhenMultipleRecords.

        Java overloads:
        (Person person, HealthRecord.Code code)
        """
        raise NotImplementedError("Java: ActiveLogic#findItemWhenMultipleRecords — pending T17")

    def add_item_when_data_is_duplicated(
        self, person: Person, time: int, entry: HealthRecordEntry
    ) -> None:
        """Java: ActiveLogic#addItemWhenDataIsDuplicated.

        Java overloads:
        (Person person, long time, HealthRecord.Entry entry)
        """
        raise NotImplementedError("Java: ActiveLogic#addItemWhenDataIsDuplicated — pending T17")

    def test(self, person: Person, time: int) -> bool:
        """Java: ActiveLogic#test.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: ActiveLogic#test — pending T17")


class ActiveCondition(ActiveLogic):
    """Java: ActiveCondition; pending T17."""

    def __init__(self) -> None:
        """Java: ActiveCondition#ActiveCondition.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ActiveCondition#ActiveCondition — pending T17")

    def check_code(self, person: Person, code: Code) -> bool:
        """Java: ActiveCondition#checkCode.

        Java overloads:
        (Person person, Code code)
        """
        raise NotImplementedError("Java: ActiveCondition#checkCode — pending T17")

    def check_attribute(self, person: Person, entry: Entry) -> bool:
        """Java: ActiveCondition#checkAttribute.

        Java overloads:
        (Person person, Entry entry)
        """
        raise NotImplementedError("Java: ActiveCondition#checkAttribute — pending T17")

    def find_item_when_multiple_records(self, person: Person, code: Code) -> Entry:
        """Java: ActiveCondition#findItemWhenMultipleRecords.

        Java overloads:
        (Person person, Code code)
        """
        raise NotImplementedError("Java: ActiveCondition#findItemWhenMultipleRecords — pending T17")

    def add_item_when_data_is_duplicated(self, person: Person, time: int, entry: Entry) -> None:
        """Java: ActiveCondition#addItemWhenDataIsDuplicated.

        Java overloads:
        (Person person, long time, Entry entry)
        """
        raise NotImplementedError("Java: ActiveCondition#addItemWhenDataIsDuplicated — pending T17")


class ActiveAllergy(ActiveLogic):
    """Java: ActiveAllergy; pending T17."""

    def __init__(self) -> None:
        """Java: ActiveAllergy#ActiveAllergy.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ActiveAllergy#ActiveAllergy — pending T17")

    def check_code(self, person: Person, code: Code) -> bool:
        """Java: ActiveAllergy#checkCode.

        Java overloads:
        (Person person, Code code)
        """
        raise NotImplementedError("Java: ActiveAllergy#checkCode — pending T17")

    def check_attribute(self, person: Person, entry: Entry) -> bool:
        """Java: ActiveAllergy#checkAttribute.

        Java overloads:
        (Person person, Entry entry)
        """
        raise NotImplementedError("Java: ActiveAllergy#checkAttribute — pending T17")

    def find_item_when_multiple_records(self, person: Person, code: Code) -> Entry:
        """Java: ActiveAllergy#findItemWhenMultipleRecords.

        Java overloads:
        (Person person, Code code)
        """
        raise NotImplementedError("Java: ActiveAllergy#findItemWhenMultipleRecords — pending T17")

    def add_item_when_data_is_duplicated(self, person: Person, time: int, entry: Entry) -> None:
        """Java: ActiveAllergy#addItemWhenDataIsDuplicated.

        Java overloads:
        (Person person, long time, Entry entry)
        """
        raise NotImplementedError("Java: ActiveAllergy#addItemWhenDataIsDuplicated — pending T17")


class ActiveMedication(ActiveLogic):
    """Java: ActiveMedication; pending T17."""

    def __init__(self) -> None:
        """Java: ActiveMedication#ActiveMedication.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ActiveMedication#ActiveMedication — pending T17")

    def check_code(self, person: Person, code: Code) -> bool:
        """Java: ActiveMedication#checkCode.

        Java overloads:
        (Person person, Code code)
        """
        raise NotImplementedError("Java: ActiveMedication#checkCode — pending T17")

    def check_attribute(self, person: Person, entry: Entry) -> bool:
        """Java: ActiveMedication#checkAttribute.

        Java overloads:
        (Person person, Entry entry)
        """
        raise NotImplementedError("Java: ActiveMedication#checkAttribute — pending T17")

    def find_item_when_multiple_records(self, person: Person, code: Code) -> Entry:
        """Java: ActiveMedication#findItemWhenMultipleRecords.

        Java overloads:
        (Person person, Code code)
        """
        raise NotImplementedError(
            "Java: ActiveMedication#findItemWhenMultipleRecords — pending T17"
        )

    def add_item_when_data_is_duplicated(self, person: Person, time: int, entry: Entry) -> None:
        """Java: ActiveMedication#addItemWhenDataIsDuplicated.

        Java overloads:
        (Person person, long time, Entry entry)
        """
        raise NotImplementedError(
            "Java: ActiveMedication#addItemWhenDataIsDuplicated — pending T17"
        )


class ActiveCarePlan(ActiveLogic):
    """Java: ActiveCarePlan; pending T17."""

    def __init__(self) -> None:
        """Java: ActiveCarePlan#ActiveCarePlan.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: ActiveCarePlan#ActiveCarePlan — pending T17")

    def check_code(self, person: Person, code: Code) -> bool:
        """Java: ActiveCarePlan#checkCode.

        Java overloads:
        (Person person, Code code)
        """
        raise NotImplementedError("Java: ActiveCarePlan#checkCode — pending T17")

    def check_attribute(self, person: Person, entry: Entry) -> bool:
        """Java: ActiveCarePlan#checkAttribute.

        Java overloads:
        (Person person, Entry entry)
        """
        raise NotImplementedError("Java: ActiveCarePlan#checkAttribute — pending T17")

    def find_item_when_multiple_records(self, person: Person, code: Code) -> Entry:
        """Java: ActiveCarePlan#findItemWhenMultipleRecords.

        Java overloads:
        (Person person, Code code)
        """
        raise NotImplementedError("Java: ActiveCarePlan#findItemWhenMultipleRecords — pending T17")

    def add_item_when_data_is_duplicated(self, person: Person, time: int, entry: Entry) -> None:
        """Java: ActiveCarePlan#addItemWhenDataIsDuplicated.

        Java overloads:
        (Person person, long time, Entry entry)
        """
        raise NotImplementedError("Java: ActiveCarePlan#addItemWhenDataIsDuplicated — pending T17")


class VitalSign(Logic):
    """Java: VitalSign; pending T17."""

    def __init__(self) -> None:
        """Java: VitalSign#VitalSign.

        Java overloads:
        ()
        """
        self.vital_sign: ConceptVitalSign
        self.operator: str
        self.value: float
        raise NotImplementedError("Java: VitalSign#VitalSign — pending T17")

    def test(self, person: Person, time: int) -> bool:
        """Java: VitalSign#test.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: VitalSign#test — pending T17")


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
