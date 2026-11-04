"""Java API skeleton: Clinician.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.helpers.random_number_generator import RandomNumberGenerator
    from synthea.world.agents.provider import Provider


class Clinician:
    """Java: Clinician; pending T13."""

    serialVersionUID: ClassVar[int] = 1370111157423846567
    WELLNESS: ClassVar[str] = "wellness"
    AMBULATORY: ClassVar[str] = "ambulatory"
    INPATIENT: ClassVar[str] = "inpatient"
    EMERGENCY: ClassVar[str] = "emergency"
    URGENTCARE: ClassVar[str] = "urgent care"
    FIRST_NAME: ClassVar[str] = "first_name"
    LAST_NAME: ClassVar[str] = "last_name"
    NAME_PREFIX: ClassVar[str] = "name_prefix"
    NAME_SUFFIX: ClassVar[str] = "name_suffix"
    NAME: ClassVar[str] = "name"
    FIRST_LANGUAGE: ClassVar[str] = "first_language"
    GENDER: ClassVar[str] = "gender"
    EDUCATION: ClassVar[str] = "education"
    SPECIALTY: ClassVar[str] = "specialty"
    ADDRESS: ClassVar[str] = "address"
    CITY: ClassVar[str] = "city"
    STATE: ClassVar[str] = "state"
    ZIP: ClassVar[str] = "zip"
    LOCATION: ClassVar[str] = "location"

    def __init__(
        self,
        clinician_seed: int,
        clinician_rand: RandomNumberGenerator,
        identifier: int,
        organization: Provider,
    ) -> None:
        """Java: Clinician#Clinician.

        Java overloads:
        (long clinicianSeed, RandomNumberGenerator clinicianRand, long identifier,
        Provider
        organization)
        """
        self.identifier: int
        self.uuid: str
        self.npi: str
        self.attributes: dict[str, object]
        self.services_provided: list[str]
        self.organization: Provider
        self.encounters: int
        self.procedures: int
        self.population_seed: int
        raise NotImplementedError("Java: Clinician#Clinician — pending T13")

    @staticmethod
    def to_clinician_npi(id: int) -> str:
        """Java: Clinician#toClinicianNPI.

        Java overloads:
        (long id)
        """
        raise NotImplementedError("Java: Clinician#toClinicianNPI — pending T13")

    def get_resource_id(self) -> str:
        """Java: Clinician#getResourceID.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Clinician#getResourceID — pending T13")

    def get_organization(self) -> Provider:
        """Java: Clinician#getOrganization.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Clinician#getOrganization — pending T13")

    def get_fullname(self) -> str:
        """Java: Clinician#getFullname.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Clinician#getFullname — pending T13")

    def get_attributes(self) -> dict[str, object]:
        """Java: Clinician#getAttributes.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Clinician#getAttributes — pending T13")

    def has_service(self, service: str) -> bool:
        """Java: Clinician#hasService.

        Java overloads:
        (String service)
        """
        raise NotImplementedError("Java: Clinician#hasService — pending T13")

    def increment_encounters(self) -> int:
        """Java: Clinician#incrementEncounters.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Clinician#incrementEncounters — pending T13")

    def get_encounter_count(self) -> int:
        """Java: Clinician#getEncounterCount.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Clinician#getEncounterCount — pending T13")

    def increment_procedures(self) -> int:
        """Java: Clinician#incrementProcedures.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Clinician#incrementProcedures — pending T13")

    def get_procedure_count(self) -> int:
        """Java: Clinician#getProcedureCount.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Clinician#getProcedureCount — pending T13")

    def get_x(self) -> float:
        """Java: Clinician#getX.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Clinician#getX — pending T13")

    def get_y(self) -> float:
        """Java: Clinician#getY.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Clinician#getY — pending T13")

    def get_lon_lat(self) -> float:
        """Java: Clinician#getLonLat.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Clinician#getLonLat — pending T13")
