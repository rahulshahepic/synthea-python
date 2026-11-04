"""Java API skeleton for provider.py.
Java: org.mitre.synthea.world.agents.Provider.
"""

from __future__ import annotations

from enum import StrEnum


class Provider:
    """Java: Provider; pending T13."""

    ENCOUNTERS: str = "encounters"
    PROCEDURES: str = "procedures"
    LABS: str = "labs"
    PRESCRIPTIONS: str = "prescriptions"
    NEAREST: str = "nearest"
    RANDOM: str = "random"
    NETWORK: str = "network"
    MEDICARE: str = "medicare"

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: Provider constructor; pending T13."""
        self.attributes: dict[str, object] = {}
        self.uuid: str | None = None
        self.locationUuid: str | None = None
        self.id: str | None = None
        self.npi: str | None = None
        self.cmsProviderNum: str | None = None
        self.cmsPin: str | None = None
        self.cmsUpin: str | None = None
        self.cmsCategory: str | None = None
        self.cmsProviderType: str | None = None
        self.cmsRegion: str | None = None
        self.cliaNumber: str | None = None
        self.bedCount: int | None = None
        self.name: str | None = None
        self.location: object | None = None
        self.address: str | None = None
        self.city: str | None = None
        self.state: str | None = None
        self.zip: str | None = None
        self.fipsCountyCode: str | None = None
        self.phone: str | None = None
        self.type: ProviderType | None = None
        self.ownership: str | None = None
        self.institutional: bool = False
        self.revenue: float = 0.0
        self.coordinates: object | None = None
        self.servicesProvided: set[object] = set()
        self.clinicianMap: dict[str, list[object]] = {}
        self.utilization: object | None = None
        raise NotImplementedError("Java: Provider — pending T13")

    def write_object(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#writeObject."""
        raise NotImplementedError("Java: writeObject — pending T13")

    def read_object(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#readObject."""
        raise NotImplementedError("Java: readObject — pending T13")

    def build_provider_finder(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#buildProviderFinder."""
        raise NotImplementedError("Java: buildProviderFinder — pending T13")

    def get_resource_id(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#getResourceID."""
        raise NotImplementedError("Java: getResourceID — pending T13")

    def get_resource_location_id(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#getResourceLocationID."""
        raise NotImplementedError("Java: getResourceLocationID — pending T13")

    def get_attributes(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#getAttributes."""
        raise NotImplementedError("Java: getAttributes — pending T13")

    def has_service(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#hasService."""
        raise NotImplementedError("Java: hasService — pending T13")

    def increment_encounters(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#incrementEncounters."""
        raise NotImplementedError("Java: incrementEncounters — pending T13")

    def increment_procedures(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#incrementProcedures."""
        raise NotImplementedError("Java: incrementProcedures — pending T13")

    def increment_labs(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#incrementLabs."""
        raise NotImplementedError("Java: incrementLabs — pending T13")

    def increment_prescriptions(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#incrementPrescriptions."""
        raise NotImplementedError("Java: incrementPrescriptions — pending T13")

    def increment(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#increment."""
        raise NotImplementedError("Java: increment — pending T13")

    def get_utilization(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#getUtilization."""
        raise NotImplementedError("Java: getUtilization — pending T13")

    def get_bed_count(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#getBedCount."""
        raise NotImplementedError("Java: getBedCount — pending T13")

    def accepts(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#accepts."""
        raise NotImplementedError("Java: accepts — pending T13")

    def add_revenue(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#addRevenue."""
        raise NotImplementedError("Java: addRevenue — pending T13")

    def get_revenue(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#getRevenue."""
        raise NotImplementedError("Java: getRevenue — pending T13")

    def find_service(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#findService."""
        raise NotImplementedError("Java: findService — pending T13")

    def find_service_new_provider(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#findServiceNewProvider."""
        raise NotImplementedError("Java: findServiceNewProvider — pending T13")

    def find_providers_by_location(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#findProvidersByLocation."""
        raise NotImplementedError("Java: findProvidersByLocation — pending T13")

    def find_new_providers_by_location(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#findNewProvidersByLocation."""
        raise NotImplementedError("Java: findNewProvidersByLocation — pending T13")

    def clear(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#clear."""
        raise NotImplementedError("Java: clear — pending T13")

    def generate_quad_tree(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#generateQuadTree."""
        raise NotImplementedError("Java: generateQuadTree — pending T13")

    def load_providers(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#loadProviders."""
        raise NotImplementedError("Java: loadProviders — pending T13")

    def insert_into_provider_map(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#insertIntoProviderMap."""
        raise NotImplementedError("Java: insertIntoProviderMap — pending T13")

    def generate_clinician_list(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#generateClinicianList."""
        raise NotImplementedError("Java: generateClinicianList — pending T13")

    def generate_clinician(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#generateClinician."""
        raise NotImplementedError("Java: generateClinician — pending T13")

    def choose_clinician_list(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#chooseClinicianList."""
        raise NotImplementedError("Java: chooseClinicianList — pending T13")

    def to_provider_npi(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#toProviderNPI."""
        raise NotImplementedError("Java: toProviderNPI — pending T13")

    def to_npi(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#toNPI."""
        raise NotImplementedError("Java: toNPI — pending T13")

    def csv_line_to_provider(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#csvLineToProvider."""
        raise NotImplementedError("Java: csvLineToProvider — pending T13")

    def get_lon_lat(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#getLonLat."""
        raise NotImplementedError("Java: getLonLat — pending T13")

    def get_provider_list(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#getProviderList."""
        raise NotImplementedError("Java: getProviderList — pending T13")

    def get_x(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#getX."""
        raise NotImplementedError("Java: getX — pending T13")

    def get_y(self, *args: object, **kwargs: object) -> object:
        """Java: Provider#getY."""
        raise NotImplementedError("Java: getY — pending T13")


class ProviderType(StrEnum):
    """Java: ProviderType; pending T13."""
