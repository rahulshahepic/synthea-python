"""Java API skeleton: Provider.java."""

from __future__ import annotations

import builtins
from enum import StrEnum
from typing import IO, TYPE_CHECKING, ClassVar, Protocol

if TYPE_CHECKING:
    from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
    from synthea.helpers.random_number_generator import RandomNumberGenerator
    from synthea.world.agents.behaviors.providerfinder.i_provider_finder import IProviderFinder
    from synthea.world.agents.clinician import Clinician
    from synthea.world.agents.person import Person
    from synthea.world.concepts.health_record import EncounterType
    from synthea.world.geography.location import Location
    from synthea.world.geography.quadtree.quad_tree import QuadTree

    class AtomicInteger(Protocol):
        """Java boundary type: AtomicInteger; external to the mapped Python port."""


class Provider:
    """Java: Provider; pending T13."""

    ENCOUNTERS: ClassVar[str] = "encounters"
    PROCEDURES: ClassVar[str] = "procedures"
    LABS: ClassVar[str] = "labs"
    PRESCRIPTIONS: ClassVar[str] = "prescriptions"
    NEAREST: ClassVar[str] = "nearest"
    RANDOM: ClassVar[str] = "random"
    NETWORK: ClassVar[str] = "network"
    MEDICARE: ClassVar[str] = "medicare"
    USE_HOSPITAL_AS_DEFAULT: ClassVar[bool]  # Java initialization deferred to T13.
    providerByUuid: ClassVar[dict[str, Provider]] = {}
    providerMap: ClassVar[QuadTree]  # Java initialization deferred to T13.
    statesLoaded: ClassVar[builtins.set[str]] = set()
    loaded: ClassVar[int] = 0
    MAX_PROVIDER_SEARCH_DISTANCE: ClassVar[float]  # Java initialization deferred to T13.
    providerFinder: ClassVar[IProviderFinder]  # Java initialization deferred to T13.

    def __init__(self) -> None:
        """Java: Provider#Provider.

        Java overloads:
        ()
        """
        self.attributes: dict[str, object]
        self.uuid: str
        self.location_uuid: str
        self.id: str
        self.npi: str
        self.cms_provider_num: str
        self.cms_pin: str
        self.cms_upin: str
        self.cms_category: str
        self.cms_provider_type: str
        self.cms_region: str
        self.clia_number: str
        self.bed_count: int
        self.name: str
        self.location: Location
        self.address: str
        self.city: str
        self.state: str
        self.zip: str
        self.fips_county_code: str
        self.phone: str
        self.type: ProviderType
        self.ownership: str
        self.institutional: bool
        self.revenue: float
        self.coordinates: float
        self.services_provided: builtins.set[EncounterType]
        self.clinician_map: dict[str, list[Clinician]]
        self.utilization: dict[int, str]
        raise NotImplementedError("Java: Provider#Provider — pending T13")

    def write_object(self, oos: IO[bytes]) -> None:
        """Java: Provider#writeObject.

        Java overloads:
        (ObjectOutputStream oos)
        """
        raise NotImplementedError("Java: Provider#writeObject — pending T13")

    def read_object(self, ois: IO[bytes]) -> None:
        """Java: Provider#readObject.

        Java overloads:
        (ObjectInputStream ois)
        """
        raise NotImplementedError("Java: Provider#readObject — pending T13")

    @staticmethod
    def build_provider_finder() -> IProviderFinder:
        """Java: Provider#buildProviderFinder.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Provider#buildProviderFinder — pending T13")

    def get_resource_id(self) -> str:
        """Java: Provider#getResourceID.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Provider#getResourceID — pending T13")

    def get_resource_location_id(self) -> str:
        """Java: Provider#getResourceLocationID.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Provider#getResourceLocationID — pending T13")

    def get_attributes(self) -> dict[str, object]:
        """Java: Provider#getAttributes.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Provider#getAttributes — pending T13")

    def has_service(self, service: EncounterType) -> bool:
        """Java: Provider#hasService.

        Java overloads:
        (EncounterType service)
        """
        raise NotImplementedError("Java: Provider#hasService — pending T13")

    def increment_encounters(self, service: EncounterType, year: int) -> None:
        """Java: Provider#incrementEncounters.

        Java overloads:
        (EncounterType service, int year)
        """
        raise NotImplementedError("Java: Provider#incrementEncounters — pending T13")

    def increment_procedures(self, year: int) -> None:
        """Java: Provider#incrementProcedures.

        Java overloads:
        (int year)
        """
        raise NotImplementedError("Java: Provider#incrementProcedures — pending T13")

    def increment_labs(self, year: int) -> None:
        """Java: Provider#incrementLabs.

        Java overloads:
        (int year)
        """
        raise NotImplementedError("Java: Provider#incrementLabs — pending T13")

    def increment_prescriptions(self, year: int) -> None:
        """Java: Provider#incrementPrescriptions.

        Java overloads:
        (int year)
        """
        raise NotImplementedError("Java: Provider#incrementPrescriptions — pending T13")

    def increment(self, year: int, key: str) -> None:
        """Java: Provider#increment.

        Java overloads:
        (Integer year, String key)
        """
        raise NotImplementedError("Java: Provider#increment — pending T13")

    def get_utilization(self) -> dict[int, str]:
        """Java: Provider#getUtilization.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Provider#getUtilization — pending T13")

    def get_bed_count(self) -> int:
        """Java: Provider#getBedCount.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Provider#getBedCount — pending T13")

    def accepts(self, person: Person, time: int) -> bool:
        """Java: Provider#accepts.

        Java overloads:
        (Person person, long time)
        """
        raise NotImplementedError("Java: Provider#accepts — pending T13")

    def add_revenue(self, cost_of_care: float) -> None:
        """Java: Provider#addRevenue.

        Java overloads:
        (double costOfCare)
        """
        raise NotImplementedError("Java: Provider#addRevenue — pending T13")

    def get_revenue(self) -> float:
        """Java: Provider#getRevenue.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Provider#getRevenue — pending T13")

    @staticmethod
    def find_service(person: Person, service: EncounterType, time: int) -> Provider:
        """Java: Provider#findService.

        Java overloads:
        (Person person, EncounterType service, long time)
        """
        raise NotImplementedError("Java: Provider#findService — pending T13")

    @staticmethod
    def find_service_new_provider(
        person: Person, service: EncounterType, time: int, taken_ids: list[str]
    ) -> Provider:
        """Java: Provider#findServiceNewProvider.

        Java overloads:
        (Person person, EncounterType service, long time, List takenIds)
        """
        raise NotImplementedError("Java: Provider#findServiceNewProvider — pending T13")

    @staticmethod
    def find_providers_by_location(person: Person, distance: float) -> list[Provider]:
        """Java: Provider#findProvidersByLocation.

        Java overloads:
        (Person person, double distance)
        """
        raise NotImplementedError("Java: Provider#findProvidersByLocation — pending T13")

    @staticmethod
    def find_new_providers_by_location(
        person: Person, distance: float, taken_ids: list[str]
    ) -> list[Provider]:
        """Java: Provider#findNewProvidersByLocation.

        Java overloads:
        (Person person, double distance, List takenIds)
        """
        raise NotImplementedError("Java: Provider#findNewProvidersByLocation — pending T13")

    @staticmethod
    def clear() -> None:
        """Java: Provider#clear.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Provider#clear — pending T13")

    @staticmethod
    def generate_quad_tree() -> QuadTree:
        """Java: Provider#generateQuadTree.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Provider#generateQuadTree — pending T13")

    @staticmethod
    def load_providers(
        location: Location,
        random_or_filename: DefaultRandomNumberGenerator | str,
        provider_type: ProviderType | None = None,
        services_provided: builtins.set[EncounterType] | None = None,
        random: RandomNumberGenerator | None = None,
        optional: bool | None = None,
    ) -> None:
        """Java: Provider#loadProviders.

        Java overloads:
        (Location location, DefaultRandomNumberGenerator random)
        (Location location, String filename, ProviderType providerType, Set
        servicesProvided,
        RandomNumberGenerator random, boolean optional)
        """
        raise NotImplementedError("Java: Provider#loadProviders — pending T13")

    @staticmethod
    def insert_into_provider_map(provider: Provider) -> None:
        """Java: Provider#insertIntoProviderMap.

        Java overloads:
        (Provider provider)
        """
        raise NotImplementedError("Java: Provider#insertIntoProviderMap — pending T13")

    def generate_clinician_list(
        self, num_clinicians: int, specialty: str, random: RandomNumberGenerator
    ) -> list[Clinician]:
        """Java: Provider#generateClinicianList.

        Java overloads:
        (int numClinicians, String specialty, RandomNumberGenerator random)
        """
        raise NotImplementedError("Java: Provider#generateClinicianList — pending T13")

    def generate_clinician(
        self, clinician_seed: int, clinician_identifier: int, random: RandomNumberGenerator
    ) -> Clinician:
        """Java: Provider#generateClinician.

        Java overloads:
        (long clinicianSeed, long clinicianIdentifier, RandomNumberGenerator random)
        """
        raise NotImplementedError("Java: Provider#generateClinician — pending T13")

    def choose_clinician_list(self, specialty: str, rand: RandomNumberGenerator) -> Clinician:
        """Java: Provider#chooseClinicianList.

        Java overloads:
        (String specialty, RandomNumberGenerator rand)
        """
        raise NotImplementedError("Java: Provider#chooseClinicianList — pending T13")

    @staticmethod
    def to_provider_npi(id_str: str, default_id: int) -> str:
        """Java: Provider#toProviderNPI.

        Java overloads:
        (String idStr, long defaultId)
        """
        raise NotImplementedError("Java: Provider#toProviderNPI — pending T13")

    @staticmethod
    def to_npi(id: int) -> str:
        """Java: Provider#toNPI.

        Java overloads:
        (long id)
        """
        raise NotImplementedError("Java: Provider#toNPI — pending T13")

    @staticmethod
    def csv_line_to_provider(line: dict[str, str]) -> Provider:
        """Java: Provider#csvLineToProvider.

        Java overloads:
        (Map line)
        """
        raise NotImplementedError("Java: Provider#csvLineToProvider — pending T13")

    def get_lon_lat(self) -> float:
        """Java: Provider#getLonLat.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Provider#getLonLat — pending T13")

    @staticmethod
    def get_provider_list() -> list[Provider]:
        """Java: Provider#getProviderList.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Provider#getProviderList — pending T13")

    def merge(self, other: Provider) -> None:
        """Java: Provider#merge.

        Java overloads:
        (Provider other)
        """
        raise NotImplementedError("Java: Provider#merge — pending T13")

    def get_x(self) -> float:
        """Java: Provider#getX.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Provider#getX — pending T13")

    def get_y(self) -> float:
        """Java: Provider#getY.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Provider#getY — pending T13")


class ProviderType(StrEnum):
    """Java: ProviderType; pending T13."""

    DIALYSIS = "DIALYSIS"
    HOME_HEALTH = "HOME_HEALTH"
    HOSPICE = "HOSPICE"
    HOSPITAL = "HOSPITAL"
    LONG_TERM = "LONG_TERM"
    NURSING = "NURSING"
    PRIMARY = "PRIMARY"
    REHAB = "REHAB"
    URGENT = "URGENT"
    VETERAN = "VETERAN"
    PHARMACY = "PHARMACY"
    IHS = "IHS"


setattr(Provider, "ProviderType", ProviderType)  # noqa: B010
