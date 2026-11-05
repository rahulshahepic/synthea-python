"""Java API skeleton: EncounterModule.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Protocol

from synthea.world.concepts.health_record import Code

if TYPE_CHECKING:
    from synthea.engine.module import Module
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import Code, Encounter, EncounterType

    class Inventory(Protocol):
        """Java boundary type: Inventory; external to the mapped Python port."""


class EncounterModule:
    """Java: EncounterModule; pending T22."""

    ACTIVE_WELLNESS_ENCOUNTER: ClassVar[str] = "active_wellness_encounter"
    ACTIVE_URGENT_CARE_ENCOUNTER: ClassVar[str] = "active_urgent_care_encounter"
    ACTIVE_EMERGENCY_ENCOUNTER: ClassVar[str] = "active_emergency_encounter"
    NAME: ClassVar[str] = "Encounter"
    PCP_SYMPTOM_THRESHOLD: ClassVar[int] = 300
    URGENT_CARE_SYMPTOM_THRESHOLD: ClassVar[int] = 350
    EMERGENCY_SYMPTOM_THRESHOLD: ClassVar[int] = 500
    LAST_VISIT_SYMPTOM_TOTAL: ClassVar[str] = "last_visit_symptom_total"
    ENCOUNTER_CHECKUP: ClassVar[Code]  # Java initialization deferred to T22.
    ENCOUNTER_EMERGENCY: ClassVar[Code]  # Java initialization deferred to T22.
    WELL_CHILD_VISIT: ClassVar[Code]  # Java initialization deferred to T22.
    GENERAL_EXAM: ClassVar[Code]  # Java initialization deferred to T22.
    ENCOUNTER_URGENTCARE: ClassVar[Code]  # Java initialization deferred to T22.

    def __init__(self) -> None:
        """Java: EncounterModule#EncounterModule.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: EncounterModule#EncounterModule — pending T22")

    def clone(self) -> Module:
        """Java: EncounterModule#clone.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: EncounterModule#clone — pending T22")

    def process(self, person: Person, time: int) -> bool:
        """Java: EncounterModule#process.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: EncounterModule#process — pending T22")

    @staticmethod
    def create_encounter(
        person: Person, time: int, type: EncounterType, specialty: str, code: Code, module: str
    ) -> Encounter:
        """Java: EncounterModule#createEncounter.

        Java overloads:
        (Person person, long time, EncounterType type, String specialty, Code code,
        String
        module)
        """
        raise NotImplementedError("Java: EncounterModule#createEncounter — pending T22")

    @staticmethod
    def get_wellness_visit_code(person: Person, time: int) -> Code:
        """Java: EncounterModule#getWellnessVisitCode.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: EncounterModule#getWellnessVisitCode — pending T22")

    def recommended_time_between_wellness_visits(self, person: Person, time: int) -> int:
        """Java: EncounterModule#recommendedTimeBetweenWellnessVisits.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError(
            "Java: EncounterModule#recommendedTimeBetweenWellnessVisits — pending T22"
        )

    def end_encounter_module_encounters(self, person: Person, time: int) -> None:
        """Java: EncounterModule#endEncounterModuleEncounters.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError(
            "Java: EncounterModule#endEncounterModuleEncounters — pending T22"
        )

    @staticmethod
    def get_all_codes() -> list[Code]:
        """Java: EncounterModule#getAllCodes.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: EncounterModule#getAllCodes — pending T22")

    @staticmethod
    def inventory_attributes(attributes: dict[str, Inventory]) -> None:
        """Java: EncounterModule#inventoryAttributes.

        Java overloads:
        (Map attributes)
        """
        raise NotImplementedError("Java: EncounterModule#inventoryAttributes — pending T22")


# Java static data initialization; constructors remain stubs.
EncounterModule.ENCOUNTER_CHECKUP = object.__new__(Code)
EncounterModule.ENCOUNTER_CHECKUP.system = "SNOMED-CT"
EncounterModule.ENCOUNTER_CHECKUP.code = "185349003"
EncounterModule.ENCOUNTER_CHECKUP.display = "Encounter for check up (procedure)"
EncounterModule.ENCOUNTER_CHECKUP.version = None
EncounterModule.ENCOUNTER_CHECKUP.value_set = None
EncounterModule.ENCOUNTER_EMERGENCY = object.__new__(Code)
EncounterModule.ENCOUNTER_EMERGENCY.system = "SNOMED-CT"
EncounterModule.ENCOUNTER_EMERGENCY.code = "50849002"
EncounterModule.ENCOUNTER_EMERGENCY.display = "Emergency room admission (procedure)"
EncounterModule.ENCOUNTER_EMERGENCY.version = None
EncounterModule.ENCOUNTER_EMERGENCY.value_set = None
EncounterModule.WELL_CHILD_VISIT = object.__new__(Code)
EncounterModule.WELL_CHILD_VISIT.system = "SNOMED-CT"
EncounterModule.WELL_CHILD_VISIT.code = "410620009"
EncounterModule.WELL_CHILD_VISIT.display = "Well child visit (procedure)"
EncounterModule.WELL_CHILD_VISIT.version = None
EncounterModule.WELL_CHILD_VISIT.value_set = None
EncounterModule.GENERAL_EXAM = object.__new__(Code)
EncounterModule.GENERAL_EXAM.system = "SNOMED-CT"
EncounterModule.GENERAL_EXAM.code = "162673000"
EncounterModule.GENERAL_EXAM.display = "General examination of patient (procedure)"
EncounterModule.GENERAL_EXAM.version = None
EncounterModule.GENERAL_EXAM.value_set = None
EncounterModule.ENCOUNTER_URGENTCARE = object.__new__(Code)
EncounterModule.ENCOUNTER_URGENTCARE.system = "SNOMED-CT"
EncounterModule.ENCOUNTER_URGENTCARE.code = "702927004"
EncounterModule.ENCOUNTER_URGENTCARE.display = "Urgent care clinic (environment)"
EncounterModule.ENCOUNTER_URGENTCARE.version = None
EncounterModule.ENCOUNTER_URGENTCARE.value_set = None
