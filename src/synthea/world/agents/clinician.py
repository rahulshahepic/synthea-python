"""Java: org.mitre.synthea.world.agents.Clinician."""

from __future__ import annotations

import hashlib
import math
from typing import TYPE_CHECKING, ClassVar

from synthea.javacompat.uuid import java_uuid
from synthea.world.agents.person import Person, Point2DDouble

if TYPE_CHECKING:
    from synthea.helpers.random_number_generator import RandomNumberGenerator
    from synthea.world.agents.provider import Provider
    from synthea.world.geography.quadtree.quad_tree_element import QuadTreeElement


def _name_uuid_from_bytes(data: bytes) -> str:
    """Java: UUID.nameUUIDFromBytes(byte[]) followed by UUID#toString.

    MD5 digest with the version-3 and variant bits forced, exactly as
    ``java.util.UUID.nameUUIDFromBytes`` does.
    """
    digest = bytearray(hashlib.md5(data).digest())
    digest[6] = (digest[6] & 0x0F) | 0x30
    digest[8] = (digest[8] & 0x3F) | 0x80
    msb = int.from_bytes(digest[0:8], "big", signed=False)
    lsb = int.from_bytes(digest[8:16], "big", signed=False)
    return java_uuid(msb, lsb)


class Clinician:
    """Java: org.mitre.synthea.world.agents.Clinician."""

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
        Provider organization)
        """
        org_npi = identifier if organization is None else organization.npi
        base = f"{clinician_seed}:{identifier}:{org_npi}:{clinician_rand.rand_long()}"
        self.identifier: int = identifier
        self.uuid: str = _name_uuid_from_bytes(base.encode("utf-8"))
        self.npi: str = Clinician.to_clinician_npi(self.identifier)
        # Java: attributes is a ConcurrentHashMap; only its lookups are used
        # by the ported code, and canonical dumps sort keys, so a plain dict
        # is used (PORTING_GUIDE §3).
        self.attributes: dict[str, object] = {}
        self.services_provided: list[str] = []
        self.organization: Provider = organization
        self.encounters: int = 0
        self.procedures: int = 0
        # Java: populationSeed is declared but never set by the constructor.
        self.population_seed: int = 0

    @staticmethod
    def to_clinician_npi(id: int) -> str:
        """Java: Clinician#toClinicianNPI.

        Java overloads:
        (long id)
        """
        # Function-local import breaks the Provider <-> Clinician cycle.
        from synthea.world.agents.provider import Provider

        if id > 999_999_999:
            raise ValueError(f"Supplied id ({id}) is too big, max is {999_999_999}")
        return Provider.to_npi(999_999_999 - id)

    def get_resource_id(self) -> str:
        """Java: Clinician#getResourceID.

        Java overloads:
        ()
        """
        return self.uuid

    def get_organization(self) -> Provider:
        """Java: Clinician#getOrganization.

        Java overloads:
        ()
        """
        return self.organization

    def get_fullname(self) -> str:
        """Java: Clinician#getFullname.

        Java overloads:
        ()
        """
        prefix = self.attributes.get(Clinician.NAME_PREFIX)
        name = self.attributes.get(Clinician.NAME)
        # Java string concatenation renders a missing attribute as "null".
        prefix_text = "null" if prefix is None else str(prefix)
        name_text = "null" if name is None else str(name)
        return prefix_text + " " + name_text

    def get_attributes(self) -> dict[str, object]:
        """Java: Clinician#getAttributes.

        Java overloads:
        ()
        """
        return self.attributes

    def has_service(self, service: str) -> bool:
        """Java: Clinician#hasService.

        Java overloads:
        (String service)
        """
        return service in self.services_provided

    def increment_encounters(self) -> int:
        """Java: Clinician#incrementEncounters.

        Java overloads:
        ()

        Java returns the pre-increment count (``encounters++``).
        """
        result = self.encounters
        self.encounters += 1
        return result

    def get_encounter_count(self) -> int:
        """Java: Clinician#getEncounterCount.

        Java overloads:
        ()
        """
        return self.encounters

    def increment_procedures(self) -> int:
        """Java: Clinician#incrementProcedures.

        Java overloads:
        ()

        Java returns the pre-increment count (``procedures++``).
        """
        result = self.procedures
        self.procedures += 1
        return result

    def get_procedure_count(self) -> int:
        """Java: Clinician#getProcedureCount.

        Java overloads:
        ()
        """
        return self.procedures

    def get_x(self) -> float:
        """Java: Clinician#getX.

        Java overloads:
        ()
        """
        return self.get_lon_lat().get_x()

    def get_y(self) -> float:
        """Java: Clinician#getY.

        Java overloads:
        ()
        """
        return self.get_lon_lat().get_y()

    def get_lon_lat(self) -> Point2DDouble:
        """Java: Clinician#getLonLat.

        Java overloads:
        ()
        """
        coordinate = self.attributes.get(Person.COORDINATE)
        if coordinate is None:
            raise TypeError("Java NullPointerException: COORDINATE attribute is not set")
        return coordinate  # type: ignore[return-value]

    def distance(self, element: QuadTreeElement) -> float:
        """Java: QuadTreeElement#distance (the interface default Clinician inherits)."""
        dx = self.get_x() - element.get_x()
        dy = self.get_y() - element.get_y()
        return math.sqrt(dx * dx + dy * dy)
