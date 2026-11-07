"""Java: org.mitre.synthea.modules.EncounterModule."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar, Protocol, cast

from synthea.engine.module import Module
from synthea.helpers.utilities import Utilities
from synthea.javacompat.hashing import string_compare_to_ignore_case
from synthea.world.agents.person import Person
from synthea.world.agents.provider import Provider
from synthea.world.concepts.clinician_specialty import ClinicianSpecialty
from synthea.world.concepts.health_record import Code, Encounter, EncounterType

if TYPE_CHECKING:
    from synthea.helpers.random_number_generator import RandomNumberGenerator


class Inventory(Protocol):
    """Java boundary: Attributes.Inventory read/write/example collection fields."""

    read: dict[str, set[str]]
    write: dict[str, set[str]]
    example_values: set[str]


@dataclass
class _InventoryData:
    """Java: Attributes.Inventory's collection surface for this module's inventory entries."""

    read: dict[str, set[str]] = field(default_factory=dict)
    write: dict[str, set[str]] = field(default_factory=dict)
    example_values: set[str] = field(default_factory=set)


def _inventory(
    attributes: dict[str, Inventory],
    module: str,
    attribute: str,
    read: bool,
    write: bool,
    example: str | None,
) -> None:
    """Java boundary: Attributes#inventory, without Graphviz/reporting functionality."""
    item = attributes.setdefault(attribute, _InventoryData())
    if read:
        item.read.setdefault(module, set())
    if write:
        item.write.setdefault(module, set())
        if example is not None:
            item.example_values.add(example)


class EncounterModule(Module):
    """Java: org.mitre.synthea.modules.EncounterModule."""

    ACTIVE_WELLNESS_ENCOUNTER: ClassVar[str] = "active_wellness_encounter"
    ACTIVE_URGENT_CARE_ENCOUNTER: ClassVar[str] = "active_urgent_care_encounter"
    ACTIVE_EMERGENCY_ENCOUNTER: ClassVar[str] = "active_emergency_encounter"
    NAME: ClassVar[str] = "Encounter"
    PCP_SYMPTOM_THRESHOLD: ClassVar[int] = 300
    URGENT_CARE_SYMPTOM_THRESHOLD: ClassVar[int] = 350
    EMERGENCY_SYMPTOM_THRESHOLD: ClassVar[int] = 500
    LAST_VISIT_SYMPTOM_TOTAL: ClassVar[str] = "last_visit_symptom_total"
    ENCOUNTER_CHECKUP: ClassVar[Code] = Code(
        "SNOMED-CT", "185349003", "Encounter for check up (procedure)"
    )
    ENCOUNTER_EMERGENCY: ClassVar[Code] = Code(
        "SNOMED-CT", "50849002", "Emergency room admission (procedure)"
    )
    WELL_CHILD_VISIT: ClassVar[Code] = Code(
        "SNOMED-CT", "410620009", "Well child visit (procedure)"
    )
    GENERAL_EXAM: ClassVar[Code] = Code(
        "SNOMED-CT", "162673000", "General examination of patient (procedure)"
    )
    ENCOUNTER_URGENTCARE: ClassVar[Code] = Code(
        "SNOMED-CT", "702927004", "Urgent care clinic (environment)"
    )

    def __init__(self) -> None:
        """Java: EncounterModule#EncounterModule."""
        super().__init__()
        self.name = self.NAME

    def clone(self) -> Module:
        """Java: EncounterModule#clone; stateless module shares its instance."""
        return self

    # Java declares only this two-argument overload, unlike Module's separate third argument.
    def process(self, person: Person, time: int) -> bool:  # type: ignore[override]
        """Java: EncounterModule#process."""
        from synthea.modules.immunizations import Immunizations

        if not person.alive(time):
            return True
        if person.has_current_encounter():
            return False
        started = False
        assert person.record is not None
        if person.record.time_since_last_wellness_encounter(
            time
        ) >= self.recommended_time_between_wellness_visits(person, time):
            code = self.get_wellness_visit_code(person, time)
            encounter = self.create_encounter(
                person,
                time,
                EncounterType.WELLNESS,
                ClinicianSpecialty.GENERAL_PRACTICE,
                code,
                self.name,
            )
            encounter.name = "Encounter Module Scheduled Wellness"
            person.attributes[self.ACTIVE_WELLNESS_ENCOUNTER] = True
            started = True
        elif person.symptom_total() > self.EMERGENCY_SYMPTOM_THRESHOLD:
            if self.LAST_VISIT_SYMPTOM_TOTAL not in person.attributes:
                person.attributes[self.LAST_VISIT_SYMPTOM_TOTAL] = 0
            if person.symptom_total() != person.attributes[self.LAST_VISIT_SYMPTOM_TOTAL]:
                person.attributes[self.LAST_VISIT_SYMPTOM_TOTAL] = person.symptom_total()
                person.address_largest_symptom()
                encounter = self.create_encounter(
                    person,
                    time,
                    EncounterType.EMERGENCY,
                    ClinicianSpecialty.GENERAL_PRACTICE,
                    self.ENCOUNTER_EMERGENCY,
                    self.name,
                )
                encounter.name = "Encounter Module Symptom Driven"
                person.attributes[self.ACTIVE_EMERGENCY_ENCOUNTER] = True
                started = True
        elif person.symptom_total() > self.URGENT_CARE_SYMPTOM_THRESHOLD:
            if self.LAST_VISIT_SYMPTOM_TOTAL not in person.attributes:
                person.attributes[self.LAST_VISIT_SYMPTOM_TOTAL] = 0
            if person.symptom_total() != person.attributes[self.LAST_VISIT_SYMPTOM_TOTAL]:
                person.attributes[self.LAST_VISIT_SYMPTOM_TOTAL] = person.symptom_total()
                person.address_largest_symptom()
                encounter = self.create_encounter(
                    person,
                    time,
                    EncounterType.URGENTCARE,
                    ClinicianSpecialty.GENERAL_PRACTICE,
                    self.ENCOUNTER_URGENTCARE,
                    self.name,
                )
                encounter.name = "Encounter Module Symptom Driven"
                person.attributes[self.ACTIVE_URGENT_CARE_ENCOUNTER] = True
                started = True
        elif person.symptom_total() > self.PCP_SYMPTOM_THRESHOLD:
            if self.LAST_VISIT_SYMPTOM_TOTAL not in person.attributes:
                person.attributes[self.LAST_VISIT_SYMPTOM_TOTAL] = 0
            if person.symptom_total() != person.attributes[self.LAST_VISIT_SYMPTOM_TOTAL]:
                person.attributes[self.LAST_VISIT_SYMPTOM_TOTAL] = person.symptom_total()
                person.address_largest_symptom()
                encounter = self.create_encounter(
                    person,
                    time,
                    EncounterType.OUTPATIENT,
                    ClinicianSpecialty.GENERAL_PRACTICE,
                    self.ENCOUNTER_CHECKUP,
                    self.name,
                )
                encounter.name = "Encounter Module Symptom Driven"
                person.attributes[self.ACTIVE_WELLNESS_ENCOUNTER] = True
                started = True
        if started:
            Immunizations.perform_encounter(person, time)
        return False

    @staticmethod
    def create_encounter(
        person: Person,
        time: int,
        type: EncounterType,
        specialty: str,
        code: Code | None,
        module: str,
    ) -> Encounter:
        """Java: EncounterModule#createEncounter; Java's nullable result keeps the API boundary."""
        if person.has_current_encounter():
            return cast(Encounter, None)
        year = Utilities.get_year(time)
        person.reserve_current_encounter(time, module)
        encounter = person.encounter_start(time, type)
        if code is not None:
            encounter.codes.append(code)
        if string_compare_to_ignore_case(specialty, ClinicianSpecialty.CARDIOLOGY) == 0:
            provider = Provider.get_provider_list()[0]
        else:
            provider = person.get_provider(type, time)
        provider.increment_encounters(type, year)
        encounter.provider = provider
        encounter.clinician = provider.choose_clinician_list(
            specialty, cast("RandomNumberGenerator", person)
        )
        return encounter

    @staticmethod
    def get_wellness_visit_code(person: Person, time: int) -> Code:
        """Java: EncounterModule#getWellnessVisitCode."""
        return (
            EncounterModule.WELL_CHILD_VISIT
            if person.age_in_years(time) < 18
            else EncounterModule.GENERAL_EXAM
        )

    def recommended_time_between_wellness_visits(self, person: Person, time: int) -> int:
        """Java: EncounterModule#recommendedTimeBetweenWellnessVisits."""
        age = person.age_in_years(time)
        chronic = bool(person.chronic_medications)
        if age <= 3:
            months = person.age_in_months(time)
            if months <= 1:
                interval = Utilities.convert_time("months", 1)
            elif months <= 5:
                interval = Utilities.convert_time("months", 2)
            elif months <= 17:
                interval = Utilities.convert_time("months", 3)
            else:
                interval = Utilities.convert_time("months", 6)
        elif age <= 19:
            interval = Utilities.convert_time("years", 1)
        elif age <= 39:
            interval = Utilities.convert_time("years", 3)
        elif age <= 49:
            interval = Utilities.convert_time("years", 2)
        else:
            interval = Utilities.convert_time("years", 1)
        if chronic and interval > Utilities.convert_time("years", 1):
            interval = Utilities.convert_time("years", 1)
        return interval

    def end_encounter_module_encounters(self, person: Person, time: int) -> None:
        """Java: EncounterModule#endEncounterModuleEncounters."""
        if person.has_current_encounter() and person.get_current_encounter_module() == self.name:
            assert person.record is not None
            if person.attributes.get(self.ACTIVE_WELLNESS_ENCOUNTER) is not None:
                person.record.encounter_end(time, EncounterType.WELLNESS)
                person.record.encounter_end(time, EncounterType.OUTPATIENT)
                person.attributes.pop(self.ACTIVE_WELLNESS_ENCOUNTER, None)
            if person.attributes.get(self.ACTIVE_EMERGENCY_ENCOUNTER) is not None:
                person.record.encounter_end(time, EncounterType.EMERGENCY)
                person.attributes.pop(self.ACTIVE_EMERGENCY_ENCOUNTER, None)
            if person.attributes.get(self.ACTIVE_URGENT_CARE_ENCOUNTER) is not None:
                person.record.encounter_end(time, EncounterType.URGENTCARE)
                person.attributes.pop(self.ACTIVE_URGENT_CARE_ENCOUNTER, None)
            person.release_current_encounter(time, self.name)

    @staticmethod
    def get_all_codes() -> list[Code]:
        """Java: EncounterModule#getAllCodes."""
        return [
            EncounterModule.ENCOUNTER_CHECKUP,
            EncounterModule.ENCOUNTER_EMERGENCY,
            EncounterModule.WELL_CHILD_VISIT,
            EncounterModule.GENERAL_EXAM,
            EncounterModule.ENCOUNTER_URGENTCARE,
        ]

    @staticmethod
    def inventory_attributes(attributes: dict[str, Inventory]) -> None:
        """Java: EncounterModule#inventoryAttributes."""
        _inventory(
            attributes,
            "EncounterModule",
            EncounterModule.LAST_VISIT_SYMPTOM_TOTAL,
            True,
            True,
            "Integer",
        )
        for key in (
            EncounterModule.ACTIVE_WELLNESS_ENCOUNTER,
            EncounterModule.ACTIVE_URGENT_CARE_ENCOUNTER,
            EncounterModule.ACTIVE_EMERGENCY_ENCOUNTER,
        ):
            _inventory(attributes, "EncounterModule", key, False, True, "Boolean")
