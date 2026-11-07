"""Java: org.mitre.synthea.world.agents.Provider."""

from __future__ import annotations

import builtins
import hashlib
import math
import re
import sys
import traceback
import uuid as uuid_module
from enum import StrEnum
from typing import IO, TYPE_CHECKING, ClassVar, cast

from synthea.helpers.config import Config
from synthea.helpers.simple_csv import SimpleCSV
from synthea.helpers.utilities import Utilities
from synthea.javacompat.collections import JavaHashMap
from synthea.javacompat.hashing import string_compare_to_ignore_case
from synthea.javacompat.uuid import java_uuid
from synthea.world.concepts.clinician_specialty import ClinicianSpecialty
from synthea.world.concepts.names import Names
from synthea.world.geography.quadtree.quad_tree import QuadTree

if TYPE_CHECKING:
    from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
    from synthea.helpers.random_number_generator import RandomNumberGenerator
    from synthea.world.agents.behaviors.providerfinder.i_provider_finder import IProviderFinder
    from synthea.world.agents.clinician import Clinician
    from synthea.world.agents.person import Person, Point2DDouble
    from synthea.world.concepts.health_record import EncounterType
    from synthea.world.geography.location import Location
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


def _equals_ignore_case(left: str | None, right: str | None) -> bool:
    """Java: String#equalsIgnoreCase (a null argument is simply not equal)."""
    if left is None or right is None:
        return False
    return string_compare_to_ignore_case(left, right) == 0


def _java_trim(value: str) -> str:
    """Java: String#trim — strip leading/trailing chars <= U+0020."""
    lo, hi = 0, len(value)
    while lo < hi and ord(value[lo]) <= 0x20:
        lo += 1
    while hi > lo and ord(value[hi - 1]) <= 0x20:
        hi -= 1
    return value[lo:hi]


_JAVA_INTEGER = re.compile(r"^[+-]?\d+$")


def _parse_long_java(value: str | None) -> int:
    """Java: Long.parseLong — optional sign and digits only, no whitespace."""
    if value is None or not _JAVA_INTEGER.match(value):
        raise ValueError(f'For input string: "{value}"')
    return int(value)


def _parse_int_java(value: str | None) -> int:
    """Java: Integer.parseInt — optional sign and digits only, no whitespace."""
    return _parse_long_java(value)


def _parse_double_java(value: str | None) -> float:
    """Java: Double.parseDouble (decimal forms; raises for null/garbage)."""
    if value is None:
        raise TypeError("Java NullPointerException: Double.parseDouble(null)")
    return float(value)


class Provider:
    """Java: org.mitre.synthea.world.agents.Provider."""

    ENCOUNTERS: ClassVar[str] = "encounters"
    PROCEDURES: ClassVar[str] = "procedures"
    LABS: ClassVar[str] = "labs"
    PRESCRIPTIONS: ClassVar[str] = "prescriptions"
    NEAREST: ClassVar[str] = "nearest"
    RANDOM: ClassVar[str] = "random"
    NETWORK: ClassVar[str] = "network"
    MEDICARE: ClassVar[str] = "medicare"
    # Java static initializers, in Java class-load (textual) order.
    USE_HOSPITAL_AS_DEFAULT: ClassVar[bool] = Config.get_as_boolean(
        "generate.providers.default_to_hospital_on_failure", True
    )
    providerByUuid: ClassVar[JavaHashMap[str, Provider]] = JavaHashMap()
    providerMap: ClassVar[QuadTree] = QuadTree()
    statesLoaded: ClassVar[builtins.set[str | None]] = set()
    loaded: ClassVar[int] = 0
    MAX_PROVIDER_SEARCH_DISTANCE: ClassVar[float] = Config.get_as_double(
        "generate.providers.maximum_search_distance", 2
    )
    providerFinder: ClassVar[IProviderFinder]  # set at module bottom, Java order

    def __init__(self) -> None:
        """Java: Provider#Provider.

        Java overloads:
        ()
        """
        # Function-local import breaks the Person <-> Provider cycle.
        from synthea.world.agents.person import Point2DDouble

        # The uuid fields are reinitialized by csvLineToProvider. Java uses
        # UUID.randomUUID() here, which is nondeterministic in Java too and
        # never observable before csvLineToProvider overwrites both fields,
        # so uuid4() is the faithful equivalent (see T13 porting notes).
        self.uuid: str = str(uuid_module.uuid4())
        self.location_uuid: str = str(uuid_module.uuid4())
        self.attributes: dict[str, object] = {}
        self.revenue: float = 0.0
        # Java: Guava HashBasedTable<Integer, String, AtomicInteger>; modelled
        # as a dict keyed by (year, key) holding the counter's int value.
        self.utilization: dict[tuple[int, str], int] = {}
        self.services_provided: builtins.set[EncounterType] = set()
        self.clinician_map: dict[str, list[Clinician]] = {}
        self.coordinates: Point2DDouble = Point2DDouble()
        self.id: str | None = None
        self.npi: str | None = None
        self.cms_provider_num: str | None = None
        self.cms_pin: str | None = None
        self.cms_upin: str | None = None
        self.cms_category: str | None = None
        self.cms_provider_type: str | None = None
        self.cms_region: str | None = None
        self.clia_number: str | None = None
        self.bed_count: int | None = None
        self.name: str | None = None
        self.location: Location | None = None
        self.address: str | None = None
        self.city: str | None = None
        self.state: str | None = None
        self.zip: str | None = None
        self.fips_county_code: str | None = None
        self.phone: str | None = None
        self.type: ProviderType | None = None
        self.ownership: str | None = None
        self.institutional: bool = False

    def write_object(self, oos: IO[bytes]) -> None:
        """Java: Provider#writeObject.

        Java overloads:
        (ObjectOutputStream oos)
        """
        raise NotImplementedError("Java Provider serialization (writeObject) is out of scope")

    def read_object(self, ois: IO[bytes]) -> None:
        """Java: Provider#readObject.

        Java overloads:
        (ObjectInputStream ois)
        """
        raise NotImplementedError("Java Provider serialization (readObject) is out of scope")

    @staticmethod
    def build_provider_finder() -> IProviderFinder:
        """Java: Provider#buildProviderFinder.

        Java overloads:
        ()
        """
        # Function-local imports break the Provider <-> finder cycle.
        from synthea.world.agents.behaviors.providerfinder.provider_finder_nearest import (
            ProviderFinderNearest,
        )
        from synthea.world.agents.behaviors.providerfinder.provider_finder_nearest_medicare import (
            ProviderFinderNearestMedicare,
        )
        from synthea.world.agents.behaviors.providerfinder.provider_finder_random import (
            ProviderFinderRandom,
        )

        behavior = Config.get("generate.providers.selection_behavior", "nearest")
        assert behavior is not None
        behavior = behavior.lower()
        finder: IProviderFinder
        if behavior in (Provider.RANDOM, Provider.NETWORK):
            finder = ProviderFinderRandom()
        elif behavior == Provider.MEDICARE:
            finder = ProviderFinderNearestMedicare()
        else:  # NEAREST and the Java default branch
            finder = ProviderFinderNearest()
        return finder

    def get_resource_id(self) -> str:
        """Java: Provider#getResourceID.

        Java overloads:
        ()
        """
        return self.uuid

    def get_resource_location_id(self) -> str:
        """Java: Provider#getResourceLocationID.

        Java overloads:
        ()
        """
        return self.location_uuid

    def get_attributes(self) -> dict[str, object]:
        """Java: Provider#getAttributes.

        Java overloads:
        ()
        """
        return self.attributes

    def has_service(self, service: EncounterType) -> bool:
        """Java: Provider#hasService.

        Java overloads:
        (EncounterType service)
        """
        return service in self.services_provided

    def increment_encounters(self, service: EncounterType, year: int) -> None:
        """Java: Provider#incrementEncounters.

        Java overloads:
        (EncounterType service, int year)
        """
        self.increment(year, Provider.ENCOUNTERS)
        # Java string concatenation calls EncounterType#toString (lowercase).
        self.increment(year, Provider.ENCOUNTERS + "-" + service.to_string())

    def increment_procedures(self, year: int) -> None:
        """Java: Provider#incrementProcedures.

        Java overloads:
        (int year)
        """
        self.increment(year, Provider.PROCEDURES)

    def increment_labs(self, year: int) -> None:
        """Java: Provider#incrementLabs.

        Java overloads:
        (int year)
        """
        self.increment(year, Provider.LABS)

    def increment_prescriptions(self, year: int) -> None:
        """Java: Provider#incrementPrescriptions.

        Java overloads:
        (int year)
        """
        self.increment(year, Provider.PRESCRIPTIONS)

    def increment(self, year: int, key: str) -> None:
        """Java: Provider#increment.

        Java overloads:
        (Integer year, String key)
        """
        if self.utilization is not None:
            cell = (year, key)
            if cell not in self.utilization:
                self.utilization[cell] = 0
            self.utilization[cell] += 1

    def get_utilization(self) -> dict[tuple[int, str], int]:
        """Java: Provider#getUtilization.

        Java overloads:
        ()
        """
        return self.utilization

    def get_bed_count(self) -> int | None:
        """Java: Provider#getBedCount.

        Java overloads:
        ()
        """
        return self.bed_count

    def accepts(self, person: Person, time: int) -> bool:
        """Java: Provider#accepts.

        Java overloads:
        (Person person, long time)
        """
        # Function-local import breaks the Person <-> Provider cycle.
        from synthea.world.agents.person import Person

        if self.type is None:
            return True
        if self.type == ProviderType.VETERAN:
            return Person.VETERAN in person.attributes
        if self.type == ProviderType.IHS:
            return person.attributes.get(Person.RACE) == "native"
        return True

    def add_revenue(self, cost_of_care: float) -> None:
        """Java: Provider#addRevenue.

        Java overloads:
        (double costOfCare)
        """
        self.revenue += cost_of_care

    def get_revenue(self) -> float:
        """Java: Provider#getRevenue.

        Java overloads:
        ()
        """
        return self.revenue

    @staticmethod
    def find_service(person: Person, service: EncounterType, time: int) -> Provider | None:
        """Java: Provider#findService.

        Java overloads:
        (Person person, EncounterType service, long time)
        """
        max_distance = Provider.MAX_PROVIDER_SEARCH_DISTANCE
        degrees = 0.125
        provider: Provider | None = None
        while degrees <= max_distance:
            options = Provider.find_providers_by_location(person, degrees)
            provider = Provider.providerFinder.find(options, person, service, time)
            if provider is not None:
                return provider
            degrees *= 2.0
        return None

    @staticmethod
    def find_service_new_provider(
        person: Person, service: EncounterType, time: int, taken_ids: list[str]
    ) -> Provider | None:
        """Java: Provider#findServiceNewProvider.

        Java overloads:
        (Person person, EncounterType service, long time, List takenIds)
        """
        max_distance = Provider.MAX_PROVIDER_SEARCH_DISTANCE
        degrees = 0.125
        provider: Provider | None = None
        while degrees <= max_distance:
            options = Provider.find_new_providers_by_location(person, degrees, taken_ids)
            provider = Provider.providerFinder.find(options, person, service, time)
            if provider is not None and provider.uuid not in taken_ids:
                return provider
            degrees *= 2.0
        return None

    @staticmethod
    def find_providers_by_location(person: Person, distance: float) -> list[Provider]:
        """Java: Provider#findProvidersByLocation.

        Java overloads:
        (Person person, double distance)
        """
        results = Provider.providerMap.query(person, distance)  # type: ignore[arg-type]
        return [cast("Provider", item) for item in results]

    @staticmethod
    def find_new_providers_by_location(
        person: Person, distance: float, taken_ids: list[str]
    ) -> list[Provider]:
        """Java: Provider#findNewProvidersByLocation.

        Java overloads:
        (Person person, double distance, List takenIds)
        """
        results = Provider.providerMap.query(person, distance)  # type: ignore[arg-type]
        providers: list[Provider] = []
        for item in results:
            provider = cast("Provider", item)
            if provider.uuid not in taken_ids:
                providers.append(provider)
        return providers

    @staticmethod
    def clear() -> None:
        """Java: Provider#clear.

        Java overloads:
        ()
        """
        Provider.providerByUuid.clear()
        Provider.statesLoaded.clear()
        Provider.providerMap = Provider.generate_quad_tree()
        Provider.providerFinder = Provider.build_provider_finder()
        Provider.loaded = 0

    @staticmethod
    def generate_quad_tree() -> QuadTree:
        """Java: Provider#generateQuadTree.

        Java overloads:
        ()
        """
        return QuadTree()

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
        servicesProvided, RandomNumberGenerator random, boolean optional)
        """
        if isinstance(random_or_filename, str):
            assert provider_type is not None
            assert services_provided is not None
            assert random is not None
            assert optional is not None
            Provider._load_providers_from_file(
                location,
                random_or_filename,
                provider_type,
                services_provided,
                random,
                optional,
            )
        else:
            Provider._load_providers_for_location(location, random_or_filename)

    @staticmethod
    def _load_providers_for_location(
        location: Location, random_source: DefaultRandomNumberGenerator
    ) -> None:
        """Java: Provider#loadProviders(Location, DefaultRandomNumberGenerator)."""
        # Function-local imports break the Location/EncounterType cycles.
        from synthea.world.concepts.health_record import EncounterType
        from synthea.world.geography.location import Location

        random: RandomNumberGenerator = cast("RandomNumberGenerator", random_source)

        if (
            location.state not in Provider.statesLoaded
            or Location.get_abbreviation(location.state) not in Provider.statesLoaded
            or Location.get_state_name(location.state) not in Provider.statesLoaded
        ):
            try:
                services: builtins.set[EncounterType] = {
                    EncounterType.AMBULATORY,
                    EncounterType.OUTPATIENT,
                    EncounterType.INPATIENT,
                }
                hospital_file = Config.get("generate.providers.hospitals.default_file")
                assert hospital_file is not None
                Provider.load_providers(
                    location, hospital_file, ProviderType.HOSPITAL, services, random, False
                )
                ihs_hospital_file = Config.get("generate.providers.ihs.hospitals.default_file")
                assert ihs_hospital_file is not None
                Provider.load_providers(
                    location, ihs_hospital_file, ProviderType.IHS, services, random, True
                )
                services.add(EncounterType.WELLNESS)
                va_file = Config.get("generate.providers.veterans.default_file")
                assert va_file is not None
                Provider.load_providers(
                    location, va_file, ProviderType.VETERAN, services, random, False
                )
                services.clear()
                services.add(EncounterType.WELLNESS)
                primary_care_file = Config.get("generate.providers.primarycare.default_file")
                assert primary_care_file is not None
                Provider.load_providers(
                    location, primary_care_file, ProviderType.PRIMARY, services, random, False
                )
                ihs_pc_file = Config.get("generate.providers.ihs.primarycare.default_file")
                assert ihs_pc_file is not None
                Provider.load_providers(
                    location, ihs_pc_file, ProviderType.IHS, services, random, True
                )
                services.clear()
                services.add(EncounterType.URGENTCARE)
                urgentcare_file = Config.get("generate.providers.urgentcare.default_file")
                assert urgentcare_file is not None
                Provider.load_providers(
                    location, urgentcare_file, ProviderType.URGENT, services, random, False
                )
                Provider.statesLoaded.add(location.state)
                Provider.statesLoaded.add(Location.get_abbreviation(location.state))
                Provider.statesLoaded.add(Location.get_state_name(location.state))
            except (OSError, ValueError):
                # Java catches IOException and prints the stack trace.
                print(
                    "ERROR: unable to load providers for state: " + str(location.state),
                    file=sys.stderr,
                )
                traceback.print_exc()

            # Additional types of optional facilities
            try:
                optional_services: builtins.set[EncounterType] = set()
                optional_services.clear()
                optional_services.add(EncounterType.HOME)
                home_health_file = Config.get("generate.providers.homehealth.default_file")
                assert home_health_file is not None
                Provider.load_providers(
                    location,
                    home_health_file,
                    ProviderType.HOME_HEALTH,
                    optional_services,
                    random,
                    True,
                )
                optional_services.clear()
                optional_services.add(EncounterType.HOSPICE)
                hospice_file = Config.get("generate.providers.hospice.default_file")
                assert hospice_file is not None
                Provider.load_providers(
                    location,
                    hospice_file,
                    ProviderType.HOSPICE,
                    optional_services,
                    random,
                    True,
                )
                optional_services.clear()
                optional_services.add(EncounterType.SNF)
                nursing_file = Config.get("generate.providers.nursing.default_file")
                assert nursing_file is not None
                Provider.load_providers(
                    location,
                    nursing_file,
                    ProviderType.NURSING,
                    optional_services,
                    random,
                    True,
                )
            except (OSError, ValueError):
                print(
                    "WARNING: unable to load optional providers in: " + str(location.state),
                    file=sys.stderr,
                )

    @staticmethod
    def _load_providers_from_file(
        location: Location,
        filename: str,
        provider_type: ProviderType,
        services_provided: builtins.set[EncounterType],
        random: RandomNumberGenerator,
        optional: bool,
    ) -> None:
        """Java: Provider#loadProviders(Location, String, ProviderType, Set,
        RandomNumberGenerator, boolean)."""
        # Function-local imports break the Location/EncounterType cycles.
        from synthea.world.concepts.health_record import EncounterType
        from synthea.world.geography.location import Location

        if optional and (filename is None or len(filename) == 0):
            return

        resource = Utilities.read_resource(filename, True, True)
        csv = SimpleCSV.parse_line_by_line(resource)

        for row in csv:
            curr_state = row.get("state")
            abbreviation = Location.get_abbreviation(location.state)

            # for now, only allow one state at a time
            if (
                location.state is None
                or _equals_ignore_case(location.state, curr_state)
                or _equals_ignore_case(abbreviation, curr_state)
            ):
                parsed = Provider.csv_line_to_provider(row)
                parsed.type = provider_type
                parsed.institutional = provider_type in (
                    ProviderType.HOSPITAL,
                    ProviderType.NURSING,
                )
                parsed.services_provided.update(services_provided)

                emergency = row.pop("emergency", None)
                if _equals_ignore_case(emergency, "Yes") or _equals_ignore_case(emergency, "true"):
                    parsed.services_provided.add(EncounterType.EMERGENCY)

                # add any remaining columns we didn't explicitly map to
                # first-class fields into the attributes table
                for key, value in row.items():
                    parsed.attributes[key] = value

                parsed.location = location

                has_specialties = row.get("hasSpecialties")
                if has_specialties is None or _equals_ignore_case(has_specialties, "false"):
                    parsed.clinician_map[ClinicianSpecialty.GENERAL_PRACTICE] = (
                        parsed.generate_clinician_list(
                            1, ClinicianSpecialty.GENERAL_PRACTICE, random
                        )
                    )
                else:
                    for specialty in ClinicianSpecialty.get_specialties():
                        specialty_count = row.get(specialty)
                        if (
                            specialty_count is not None
                            and _java_trim(specialty_count) != ""
                            and _java_trim(specialty_count) != "0"
                        ):
                            parsed.clinician_map[specialty] = parsed.generate_clinician_list(
                                _parse_int_java(row.get(specialty)),
                                specialty,
                                random,
                            )
                    if row.get(ClinicianSpecialty.GENERAL_PRACTICE) == "0":
                        parsed.clinician_map[ClinicianSpecialty.GENERAL_PRACTICE] = (
                            parsed.generate_clinician_list(
                                1, ClinicianSpecialty.GENERAL_PRACTICE, random
                            )
                        )

                Provider.insert_into_provider_map(parsed)

    @staticmethod
    def insert_into_provider_map(provider: Provider) -> None:
        """Java: Provider#insertIntoProviderMap.

        Java overloads:
        (Provider provider)
        """
        if provider.uuid in Provider.providerByUuid:
            existing = Provider.providerByUuid[provider.uuid]
            existing.merge(provider)
        else:
            Provider.providerByUuid[provider.uuid] = provider
            inserted = Provider.providerMap.insert(provider)
            if not inserted:
                raise RuntimeError(
                    "Provider QuadTree Full! Dropping # "
                    + str(Provider.loaded)
                    + ": "
                    + str(provider.name)
                    + " @ "
                    + str(provider.city)
                )
            Provider.loaded += 1

    def generate_clinician_list(
        self, num_clinicians: int, specialty: str, random: RandomNumberGenerator
    ) -> list[Clinician]:
        """Java: Provider#generateClinicianList.

        Java overloads:
        (int numClinicians, String specialty, RandomNumberGenerator random)
        """
        # Function-local import breaks the Clinician <-> Provider cycle.
        from synthea.world.agents.clinician import Clinician

        clinicians: list[Clinician] = []
        for i in range(num_clinicians):
            # Java: Long.parseLong(loaded + "" + i) — string concatenation of
            # the CURRENT static loaded count and the loop index.
            clinician = self.generate_clinician(
                random.get_seed(), int(str(Provider.loaded) + str(i)), random
            )
            clinician.attributes[Clinician.SPECIALTY] = specialty
            clinicians.append(clinician)
        return clinicians

    def generate_clinician(
        self, clinician_seed: int, clinician_identifier: int, random: RandomNumberGenerator
    ) -> Clinician:
        """Java: Provider#generateClinician.

        Java overloads:
        (long clinicianSeed, long clinicianIdentifier, RandomNumberGenerator random)
        """
        # Function-local imports break the Person/Clinician cycles.
        from synthea.world.agents.clinician import Clinician
        from synthea.world.agents.person import Person

        doc = Person(clinician_identifier)
        location = self.location
        if location is None:
            raise TypeError("Java NullPointerException: provider location is not set")
        city_demographics = location.random_city(cast("RandomNumberGenerator", doc))
        out: dict[str, object] = {}

        race = city_demographics.pick_race(random)
        out[Person.RACE] = race
        ethnicity = city_demographics.pick_ethnicity(random)
        out[Person.ETHNICITY] = ethnicity
        language = city_demographics.language_from_race_and_ethnicity(race, ethnicity, random)
        out[Person.FIRST_LANGUAGE] = language
        gender = city_demographics.pick_gender(random)
        if _equals_ignore_case(gender, "male") or _equals_ignore_case(gender, "M"):
            gender = "M"
        else:
            gender = "F"
        out[Person.GENDER] = gender

        clinician = Clinician(
            clinician_seed, cast("RandomNumberGenerator", doc), clinician_identifier, self
        )
        clinician.attributes.update(out)
        clinician.attributes[Person.ADDRESS] = self.address
        clinician.attributes[Person.CITY] = self.city
        clinician.attributes[Person.STATE] = self.state
        clinician.attributes[Person.ZIP] = self.zip
        clinician.attributes[Person.COORDINATE] = self.coordinates

        first_name = Names.fake_first_name(gender, language, doc)
        last_name = Names.fake_last_name(language, doc)
        clinician.attributes[Clinician.FIRST_NAME] = first_name
        clinician.attributes[Clinician.LAST_NAME] = last_name
        clinician.attributes[Clinician.NAME] = first_name + " " + last_name
        clinician.attributes[Clinician.NAME_PREFIX] = "Dr."
        # Degree's beyond a bachelors degree are not currently tracked.
        clinician.attributes[Clinician.EDUCATION] = "bs_degree"
        ssn = "999-" + str(doc.rand_int(90) + 10) + "-" + str(doc.rand_int(9000) + 1000)
        clinician.attributes[Person.IDENTIFIER_SSN] = ssn
        return clinician

    def choose_clinician_list(self, specialty: str, rand: RandomNumberGenerator) -> Clinician:
        """Java: Provider#chooseClinicianList.

        Java overloads:
        (String specialty, RandomNumberGenerator rand)
        """
        clinicians = self.clinician_map.get(specialty)
        if clinicians is None or len(clinicians) == 0:
            clinicians = self.clinician_map.get(ClinicianSpecialty.GENERAL_PRACTICE)
        if clinicians is None:
            raise TypeError("Java NullPointerException: no clinicians for specialty " + specialty)
        doc = clinicians[rand.rand_int(len(clinicians))]
        doc.increment_encounters()
        return doc

    @staticmethod
    def to_provider_npi(id_str: str, default_id: int) -> str:
        """Java: Provider#toProviderNPI.

        Java overloads:
        (String idStr, long defaultId)
        """
        id_value = default_id
        try:
            id_value = _parse_long_java(id_str)
        except ValueError:
            id_value = default_id  # ignore, use default value instead
        if id_value > 888_888_888:
            raise ValueError(f"Supplied id ({id_value}) is too big, max is {888_888_888}")
        return Provider.to_npi(888_888_888 - id_value)

    @staticmethod
    def to_npi(id: int) -> str:
        """Java: Provider#toNPI.

        Java overloads:
        (long id)
        """
        if id < 100_000_000 or id > 999_999_999:
            raise ValueError(f"Supplied identifier ({id}) should be exactly 9 digits")
        check_digit = 24
        remaining_digits = id
        npi_without_check_digit = remaining_digits
        even = True
        while remaining_digits > 0:
            digit = remaining_digits % 10
            if even:
                digit = digit * 2
            check_digit += digit % 10
            if digit >= 10:
                check_digit += 1
            remaining_digits //= 10
            even = not even
        check_digit = 0 if check_digit % 10 == 0 else ((check_digit // 10) + 1) * 10 - check_digit
        return str(npi_without_check_digit * 10 + check_digit)

    @staticmethod
    def csv_line_to_provider(line: dict[str, str]) -> Provider:
        """Java: Provider#csvLineToProvider.

        Java overloads:
        (Map line)
        """
        d = Provider()
        # using 'remove' instead of 'get' so that we can iterate over the
        # remaining keys later (Python dict.pop mirrors Map.remove)
        d.id = line.pop("id", None)
        d.npi = line.pop("npi", None)
        if d.npi is None:
            d.npi = Provider.to_provider_npi(d.id, Provider.loaded)  # type: ignore[arg-type]
        if d.id is None:
            d.id = d.npi
        d.name = line.pop("name", None)
        if d.name is None or d.name == "":
            d.name = d.id
        base = str(d.npi) + str(d.name)
        d.uuid = _name_uuid_from_bytes(base.encode("utf-8"))
        # Java: new StringBuilder(base).reverse() reverses UTF-16 code units;
        # provider names are BMP in practice (see T13 porting notes).
        reversed_base = base[::-1]
        d.location_uuid = _name_uuid_from_bytes(reversed_base.encode("utf-8"))
        d.address = line.pop("address", None)
        d.city = line.pop("city", None)
        d.state = line.pop("state", None)
        d.zip = line.pop("zip", None)
        d.fips_county_code = line.pop("fips_county", None)
        d.phone = line.pop("phone", None)
        d.ownership = line.pop("ownership", None)

        d.cms_category = line.pop("category", None)
        d.cms_provider_type = line.pop("provider_type_code", None)
        d.cms_provider_num = line.pop("provider_num", None)
        d.cms_pin = line.pop("pin", None)
        if d.cms_pin is not None and len(d.cms_pin) > 14:
            d.cms_pin = None  # the pin is too long and is probably garbage
        d.cms_upin = line.pop("upin", None)
        if d.cms_upin is not None and len(d.cms_upin) > 12:
            d.cms_upin = None  # the pin is too long and is probably garbage
        d.cms_region = line.pop("region_code", None)
        d.clia_number = line.pop("clia_lab_number", None)

        bed_count = line.pop("bed_count", None)
        if bed_count is not None:
            try:
                d.bed_count = _parse_int_java(bed_count)
            except ValueError:
                d.bed_count = None  # Ignore, this is an optional field.

        slat: str | None = None
        slon: str | None = None
        if "lat" in line:
            slat = line.pop("lat")
        elif "LAT" in line:
            slat = line.pop("LAT")
        if "lon" in line:
            slon = line.pop("lon")
        elif "LON" in line:
            slon = line.pop("LON")
        try:
            lat = _parse_double_java(slat)
            lon = _parse_double_java(slon)
            # Java: coordinates.setLocation(lon, lat) — x is longitude.
            d.coordinates.x = lon
            d.coordinates.y = lat
        except (TypeError, ValueError):
            d.coordinates.x = 0.0
            d.coordinates.y = 0.0
        return d

    def get_lon_lat(self) -> Point2DDouble:
        """Java: Provider#getLonLat.

        Java overloads:
        ()
        """
        return self.coordinates

    @staticmethod
    def get_provider_list() -> list[Provider]:
        """Java: Provider#getProviderList.

        Java overloads:
        ()
        """
        return list(Provider.providerByUuid.values())

    def merge(self, other: Provider) -> None:
        """Java: Provider#merge.

        Java overloads:
        (Provider other)
        """
        if self.uuid is None:
            self.uuid = other.uuid
        if self.id is None:
            self.id = other.id
        if self.npi is None:
            self.npi = other.npi
        if self.cms_provider_num is None:
            self.cms_provider_num = other.cms_provider_num
        if self.cms_pin is None:
            self.cms_pin = other.cms_pin
        if self.cms_upin is None:
            self.cms_upin = other.cms_upin
        if self.cms_category is None:
            self.cms_category = other.cms_category
        if self.cms_provider_type is None:
            self.cms_provider_type = other.cms_provider_type
        if self.cms_region is None:
            self.cms_region = other.cms_region
        if self.clia_number is None:
            self.clia_number = other.clia_number
        if self.bed_count is None:
            self.bed_count = other.bed_count
        if self.name is None:
            self.name = other.name
        if self.address is None:
            self.address = other.address
        if self.city is None:
            self.city = other.city
        if self.state is None:
            self.state = other.state
        if self.zip is None:
            self.zip = other.zip
        if self.fips_county_code is None:
            self.fips_county_code = other.fips_county_code
        if self.phone is None:
            self.phone = other.phone
        if self.type is None:
            self.type = other.type
        if self.ownership is None:
            self.ownership = other.ownership
        # This is the most important piece of the merge function: we need to
        # ensure that the de-duplicated provider offers all intended services.
        if self.services_provided is None:
            self.services_provided = other.services_provided
        else:
            self.services_provided.update(other.services_provided)

        # Merge utilization tables
        if self.utilization is None:
            self.utilization = other.utilization
        elif other.utilization is not None:
            for cell, other_value in other.utilization.items():
                if cell in self.utilization:
                    self.utilization[cell] += other_value
                else:
                    self.utilization[cell] = other_value

    def get_x(self) -> float:
        """Java: Provider#getX.

        Java overloads:
        ()
        """
        return self.coordinates.get_x()

    def get_y(self) -> float:
        """Java: Provider#getY.

        Java overloads:
        ()
        """
        return self.coordinates.get_y()

    def distance(self, element: QuadTreeElement) -> float:
        """Java: QuadTreeElement#distance (the interface default Provider inherits)."""
        dx = self.get_x() - element.get_x()
        dy = self.get_y() - element.get_y()
        return math.sqrt(dx * dx + dy * dy)


class ProviderType(StrEnum):
    """Java: ProviderType."""

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

# Java static initialization, last in class-load order:
# private static IProviderFinder providerFinder = buildProviderFinder();
Provider.providerFinder = Provider.build_provider_finder()
