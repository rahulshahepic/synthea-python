"""Java: org.mitre.synthea.modules.DeathModule."""

from __future__ import annotations

from typing import ClassVar, cast

from synthea.modules.encounter_module import EncounterModule, Inventory, _inventory
from synthea.world.agents.person import Person
from synthea.world.concepts.clinician_specialty import ClinicianSpecialty
from synthea.world.concepts.health_record import Code, EncounterType


class DeathModule:
    """Java: org.mitre.synthea.modules.DeathModule."""

    DEATH_CERTIFICATION: ClassVar[Code] = Code("SNOMED-CT", "308646001", "Death Certification")
    CAUSE_OF_DEATH_CODE: ClassVar[Code] = Code(
        "LOINC", "69453-9", "Cause of Death [US Standard Certificate of Death]"
    )
    DEATH_CERTIFICATE: ClassVar[Code] = Code(
        "LOINC", "69409-1", "U.S. standard certificate of death - 2003 revision"
    )

    def __init__(self) -> None:
        """Java: DeathModule#DeathModule (implicit constructor)."""

    @staticmethod
    def process(person: Person, time: int) -> None:
        """Java: DeathModule#process; retain the final encounter reservation."""
        if not person.alive(time) and Person.CAUSE_OF_DEATH in person.attributes:
            cause = cast(Code, person.attributes[Person.CAUSE_OF_DEATH])
            person.release_current_encounter(time, "DeathModule")
            encounter = EncounterModule.create_encounter(
                person,
                time,
                EncounterType.WELLNESS,
                ClinicianSpecialty.GENERAL_PRACTICE,
                DeathModule.DEATH_CERTIFICATION,
                "DeathModule",
            )
            encounter.reason = cause
            assert person.record is not None
            observation = person.record.observation(
                time, DeathModule.CAUSE_OF_DEATH_CODE.code, cause
            )
            observation.codes.append(DeathModule.CAUSE_OF_DEATH_CODE)
            observation.category = "exam"
            report = person.record.report(time, DeathModule.DEATH_CERTIFICATE.code, 1)
            report.codes.append(DeathModule.DEATH_CERTIFICATE)
            person.record.encounter_end(time, EncounterType.WELLNESS)

    @staticmethod
    def get_all_codes() -> list[Code]:
        """Java: DeathModule#getAllCodes."""
        return [
            DeathModule.DEATH_CERTIFICATION,
            DeathModule.CAUSE_OF_DEATH_CODE,
            DeathModule.DEATH_CERTIFICATE,
        ]

    @staticmethod
    def inventory_attributes(attributes: dict[str, Inventory]) -> None:
        """Java: DeathModule#inventoryAttributes."""
        _inventory(attributes, "DeathModule", Person.CAUSE_OF_DEATH, True, False, None)
