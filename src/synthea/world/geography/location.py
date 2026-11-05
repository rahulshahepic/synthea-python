"""Java API skeleton: Location.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.helpers.random_number_generator import RandomNumberGenerator
    from synthea.world.agents.person import Person
    from synthea.world.geography.cms_state_code_mapper import CMSStateCodeMapper
    from synthea.world.geography.demographics import Demographics
    from synthea.world.geography.place import Place


class Location:
    """Java: Location; pending T10."""

    serialVersionUID: ClassVar[int] = 1
    stateAbbreviations: ClassVar[dict[str, str]]  # Java initialization deferred to T10.
    timezones: ClassVar[dict[str, str]]  # Java initialization deferred to T10.
    foreignPlacesOfBirth: ClassVar[dict[str, list[str]]]  # Java initialization deferred to T10.
    COUNTRY_CODE: ClassVar[str]  # Java initialization deferred to T10.
    cmsStateCodeMapper: ClassVar[CMSStateCodeMapper]  # Java initialization deferred to T10.

    def __init__(self, state: str, city: str) -> None:
        """Java: Location#Location.

        Java overloads:
        (String state, String city)
        """
        self.total_population: int
        self.population_by_city: dict[str, int]
        self.population_by_city_id: dict[str, int]
        self.zip_codes: dict[str, list[Place]]
        self.city: str
        self.fixed_city: Demographics
        self.state: str
        self.demographics: dict[str, Demographics]
        self.social_determinants_of_health: dict[str, dict[str, float]]
        raise NotImplementedError("Java: Location#Location — pending T10")

    def get_zip_code(self, city_name: str, random: RandomNumberGenerator) -> str:
        """Java: Location#getZipCode.

        Java overloads:
        (String cityName, RandomNumberGenerator random)
        """
        raise NotImplementedError("Java: Location#getZipCode — pending T10")

    def get_zip_codes(self, city_name: str) -> list[str]:
        """Java: Location#getZipCodes.

        Java overloads:
        (String cityName)
        """
        raise NotImplementedError("Java: Location#getZipCodes — pending T10")

    def get_population(self, city_name: str) -> int:
        """Java: Location#getPopulation.

        Java overloads:
        (String cityName)
        """
        raise NotImplementedError("Java: Location#getPopulation — pending T10")

    def random_city(self, random: RandomNumberGenerator) -> Demographics:
        """Java: Location#randomCity.

        Java overloads:
        (RandomNumberGenerator random)
        """
        raise NotImplementedError("Java: Location#randomCity — pending T10")

    def random_city_name(self, random: RandomNumberGenerator) -> str:
        """Java: Location#randomCityName.

        Java overloads:
        (RandomNumberGenerator random)
        """
        raise NotImplementedError("Java: Location#randomCityName — pending T10")

    def random_city_id(self, random: RandomNumberGenerator) -> str:
        """Java: Location#randomCityId.

        Java overloads:
        (RandomNumberGenerator random)
        """
        raise NotImplementedError("Java: Location#randomCityId — pending T10")

    def random_birth_place(self, random: RandomNumberGenerator) -> list[str]:
        """Java: Location#randomBirthPlace.

        Java overloads:
        (RandomNumberGenerator random)
        """
        raise NotImplementedError("Java: Location#randomBirthPlace — pending T10")

    def random_birthplace_by_language(
        self, random: RandomNumberGenerator, language: str
    ) -> list[str]:
        """Java: Location#randomBirthplaceByLanguage.

        Java overloads:
        (RandomNumberGenerator random, String language)
        """
        raise NotImplementedError("Java: Location#randomBirthplaceByLanguage — pending T10")

    def assign_point(self, person: Person, city_name: str) -> None:
        """Java: Location#assignPoint.

        Java overloads:
        (Person person, String cityName)
        """
        raise NotImplementedError("Java: Location#assignPoint — pending T10")

    def set_social_determinants(self, person: Person) -> None:
        """Java: Location#setSocialDeterminants.

        Java overloads:
        (Person person)
        """
        raise NotImplementedError("Java: Location#setSocialDeterminants — pending T10")

    @staticmethod
    def load_abbreviations() -> dict[str, str]:
        """Java: Location#loadAbbreviations.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Location#loadAbbreviations — pending T10")

    @staticmethod
    def get_abbreviation(state: str) -> str:
        """Java: Location#getAbbreviation.

        Java overloads:
        (String state)
        """
        raise NotImplementedError("Java: Location#getAbbreviation — pending T10")

    @staticmethod
    def get_index(state: str) -> int:
        """Java: Location#getIndex.

        Java overloads:
        (String state)
        """
        raise NotImplementedError("Java: Location#getIndex — pending T10")

    @staticmethod
    def get_state_name(abbreviation: str) -> str:
        """Java: Location#getStateName.

        Java overloads:
        (String abbreviation)
        """
        raise NotImplementedError("Java: Location#getStateName — pending T10")

    @staticmethod
    def load_timezones() -> dict[str, str]:
        """Java: Location#loadTimezones.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Location#loadTimezones — pending T10")

    @staticmethod
    def load_cities_by_language(resource: str | None = None) -> dict[str, list[str]]:
        """Java: Location#loadCitiesByLanguage.

        Java overloads:
        ()
        (String resource)
        """
        raise NotImplementedError("Java: Location#loadCitiesByLanguage — pending T10")

    @staticmethod
    def get_timezone_by_state(state: str) -> str:
        """Java: Location#getTimezoneByState.

        Java overloads:
        (String state)
        """
        raise NotImplementedError("Java: Location#getTimezoneByState — pending T10")

    @staticmethod
    def get_fips_code_by_zip_code(zip_code: str) -> str:
        """Java: Location#getFipsCodeByZipCode.

        Java overloads:
        (String zipCode)
        """
        raise NotImplementedError("Java: Location#getFipsCodeByZipCode — pending T10")
