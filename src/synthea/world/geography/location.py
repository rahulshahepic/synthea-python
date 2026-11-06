"""Java: org.mitre.synthea.world.geography.Location."""

from __future__ import annotations

import json
import logging
from functools import cache, cmp_to_key
from typing import ClassVar

from synthea.helpers.config import Config
from synthea.helpers.random_number_generator import RandomNumberGenerator
from synthea.helpers.simple_csv import SimpleCSV
from synthea.helpers.utilities import Utilities
from synthea.javacompat.collections import JavaHashMap
from synthea.javacompat.hashing import string_compare_to_ignore_case
from synthea.world.agents.person import Person, Point2DDouble
from synthea.world.concepts.employment import Employment
from synthea.world.geography.cms_state_code_mapper import CMSStateCodeMapper
from synthea.world.geography.demographics import Demographics
from synthea.world.geography.place import Place


@cache
def _rows(filename: str) -> list[dict[str, str]]:
    """Java: Location resource reads, parsed lazily once per configured filename."""
    return SimpleCSV.parse(Utilities.read_resource(filename, True, True))


def _configured_rows(key: str, default: str | None = None) -> list[dict[str, str]]:
    """Java: Location configuration lookup followed by resource read."""
    filename = Config.get(key, default)
    if filename is None:
        raise ValueError(f"Missing {key}")
    return _rows(filename)


class Location:
    """Java: org.mitre.synthea.world.geography.Location."""

    serialVersionUID: ClassVar[int] = 1
    stateAbbreviations: ClassVar[dict[str, str] | None] = None
    timezones: ClassVar[dict[str, str] | None] = None
    foreignPlacesOfBirth: ClassVar[dict[str, list[str]] | None] = None
    COUNTRY_CODE: ClassVar[str | None] = None
    cmsStateCodeMapper: ClassVar[CMSStateCodeMapper | None] = None

    def __init__(self, state: str, city: str | None) -> None:
        """Java: Location#Location."""
        self._initialize()
        self.city: str | None = city
        self.state: str = state
        self.fixed_city: Demographics | None = None
        self.demographics: JavaHashMap[str, Demographics] = JavaHashMap(
            Demographics.load(state).get(state, {})
        )
        if not self.demographics:
            raise ValueError(f"The state {state} was not found in the demographics file.")
        if city is not None and not any(
            string_compare_to_ignore_case(d.city, city) == 0 for d in self.demographics.values()
        ):
            raise ValueError(
                f"The city {city} was not found in the demographics file for state {state}."
            )
        self.total_population: int = 0
        self.population_by_city: dict[str, int] = {}
        self.population_by_city_id: dict[str, int] = {}
        for d in sorted(self.demographics.values(), key=cmp_to_key(Demographics.compare_to)):
            self.total_population += d.population
            self.population_by_city[d.city] = self.population_by_city.get(d.city, 0) + d.population
            self.population_by_city_id[d.id] = d.population
        self.zip_codes: JavaHashMap[str, list[Place]] = JavaHashMap()
        for row in _configured_rows("generate.geography.zipcodes.default_file"):
            place = Place(row)
            if place.same_state(state):
                self.zip_codes.setdefault(place.name, []).append(place)
        self.social_determinants_of_health: JavaHashMap[str, JavaHashMap[str, float]] = (
            JavaHashMap()
        )
        try:
            for source in _configured_rows(
                "generate.geography.sdoh.default_file", "geography/sdoh.csv"
            ):
                row = source.copy()
                if string_compare_to_ignore_case(row.pop("STATE"), state) != 0:
                    continue
                row.pop("FIPS_CODE")
                row.pop("COUNTY_CODE")
                county = row.pop("COUNTY")
                row.pop("ST")
                sdoh: JavaHashMap[str, float] = JavaHashMap()
                for attribute, text_probability in row.items():
                    sdoh[attribute.lower()] = float(text_probability)
                self.social_determinants_of_health[county] = sdoh
        except Exception:
            logging.getLogger(__name__).warning("Unable to load SDoH csv", exc_info=True)
        averages: JavaHashMap[str, float] = JavaHashMap()
        if self.social_determinants_of_health:
            for determinants in self.social_determinants_of_health.values():
                for determinant, probability in determinants.items():
                    averages[determinant] = probability + averages.get(determinant, 0.0)
            for determinant in averages:
                averages[determinant] /= len(self.social_determinants_of_health)
        else:
            for determinant in (
                Person.FOOD_INSECURITY,
                Person.SEVERE_HOUSING_COST_BURDEN,
                Person.UNEMPLOYED,
                Person.NO_VEHICLE_ACCESS,
                Person.UNINSURED,
            ):
                averages[determinant] = 0.5
        self.social_determinants_of_health["AVERAGE"] = averages

    @classmethod
    def _initialize(cls) -> None:
        """Java: Location static initialization, deferred to first public use."""
        if cls.stateAbbreviations is None:
            cls.stateAbbreviations = cls.load_abbreviations()
            cls.timezones = cls.load_timezones()
            cls.foreignPlacesOfBirth = cls.load_cities_by_language()
            cls.COUNTRY_CODE = Config.get("generate.geography.country_code")
            cls.cmsStateCodeMapper = CMSStateCodeMapper()

    def get_zip_code(self, city_name: str, random: RandomNumberGenerator) -> str:
        """Java: Location#getZipCode."""
        zips = self.get_zip_codes(city_name)
        return zips[random.rand_int(len(zips))] if len(zips) > 1 else zips[0]

    def get_zip_codes(self, city_name: str) -> list[str]:
        """Java: Location#getZipCodes."""
        places = self.zip_codes.get(city_name)
        if places is None:
            places = self.zip_codes.get(city_name + " Town")
        result = [p.postal_code for p in places or [] if p.postal_code]
        return result or ["00000"]

    def get_population(self, city_name: str) -> int:
        """Java: Location#getPopulation."""
        return self.population_by_city.get(city_name, 0)

    def random_city(self, random: RandomNumberGenerator) -> Demographics:
        """Java: Location#randomCity; sorted ascending despite Java's 'largest' comment."""
        if self.city is not None:
            if self.fixed_city is None:
                self.fixed_city = sorted(
                    (
                        d
                        for d in self.demographics.values()
                        if string_compare_to_ignore_case(d.city, self.city) == 0
                    ),
                    key=cmp_to_key(Demographics.compare_to),
                )[0]
            return self.fixed_city
        return self.demographics[self.random_city_id(random)]

    def random_city_name(self, random: RandomNumberGenerator) -> str:
        """Java: Location#randomCityName."""
        return self.demographics[self.random_city_id(random)].city

    def random_city_id(self, random: RandomNumberGenerator) -> str:
        """Java: Location#randomCityId."""
        target = int(float(random.rand()) * self.total_population)
        for city, population in self.population_by_city_id.items():
            target -= population
            if target < 0:
                return city
        raise RuntimeError("Unable to select a random city id.")

    def random_birth_place(self, random: RandomNumberGenerator) -> list[str]:
        """Java: Location#randomBirthPlace."""
        self._initialize()
        result = [self.random_city_name(random), self.state, self.COUNTRY_CODE or "null"]
        return [*result, ", ".join(result)]

    def random_birthplace_by_language(
        self, random: RandomNumberGenerator, language: str
    ) -> list[str]:
        """Java: Location#randomBirthplaceByLanguage."""
        self._initialize()
        assert self.foreignPlacesOfBirth is not None
        cities = self.foreignPlacesOfBirth.get(language.lower())
        if cities:
            city = cities[random.rand_int(len(cities))]
            parts = city.split(",")
            while parts and not parts[-1]:
                parts.pop()
            if len(parts) == 3:
                return [*parts, city.replace(",", ", ")]
        return self.random_birth_place(random)

    def assign_point(self, person: Person, city_name: str | None) -> None:
        """Java: Location#assignPoint; eager orElse fallback consumes its random draw."""
        if city_name is None:
            city_name = list(self.zip_codes)[person.rand_int(len(self.zip_codes))]
        places = self.zip_codes.get(city_name)
        if places is None:
            places = self.zip_codes.get(city_name + " Town")
        if places is not None and len(places) == 1:
            place = places[0]
        elif places is not None:
            person_zip = person.attributes.get(Person.ZIP)
            fallback = places[person.rand_int(len(places))]
            place = (
                fallback
                if person_zip is None
                else next((p for p in places if person_zip == p.postal_code), fallback)
            )
        else:
            key = list(self.zip_codes)[person.rand_int(len(self.zip_codes))]
            place = self.zip_codes[key][person.rand_int(len(self.zip_codes[key]))]
        # Java: RandomNumberGenerator#rand(double,double), exposed by Person.
        dx = person.rand(-0.05, 0.05)  # type: ignore[call-arg]
        dy = person.rand(-0.05, 0.05)  # type: ignore[call-arg]
        person.attributes[Person.COORDINATE] = Point2DDouble(
            place.coordinate.x + dx, place.coordinate.y + dy
        )

    def set_social_determinants(self, person: Person) -> None:
        """Java: Location#setSocialDeterminants."""
        county = person.attributes.get(Person.COUNTY)
        if not isinstance(county, str) or county not in self.social_determinants_of_health:
            county = "AVERAGE"
        sdoh = self.social_determinants_of_health.get(county)
        if sdoh is not None:
            for determinant, probability in sdoh.items():
                if determinant == Person.UNEMPLOYED:
                    person.attributes[Person.UNEMPLOYED] = False
                    person.attributes[Person.EMPLOYMENT_MODEL] = Employment(probability)
                person.attributes[determinant] = person.rand() <= probability

    @staticmethod
    def load_abbreviations() -> dict[str, str]:
        """Java: Location#loadAbbreviations."""
        abbreviations: dict[str, str] = {}
        try:
            for row in _configured_rows("generate.geography.zipcodes.default_file"):
                abbreviations[row["USPS"]] = row["ST"]
        except Exception:
            logging.getLogger(__name__).error("Unable to load zips csv", exc_info=True)
        return abbreviations

    @staticmethod
    def get_abbreviation(state: str) -> str | None:
        """Java: Location#getAbbreviation."""
        Location._initialize()
        assert Location.stateAbbreviations is not None
        return Location.stateAbbreviations.get(state)

    @staticmethod
    def get_index(state: str) -> int:
        """Java: Location#getIndex."""
        Location._initialize()
        assert Location.stateAbbreviations is not None
        for index, name in enumerate(Location.stateAbbreviations):
            if name == state:
                return index
        return len(Location.stateAbbreviations)

    @staticmethod
    def get_state_name(abbreviation: str) -> str | None:
        """Java: Location#getStateName."""
        Location._initialize()
        assert Location.stateAbbreviations is not None
        return next(
            (
                name
                for name, abbr in Location.stateAbbreviations.items()
                if string_compare_to_ignore_case(abbr, abbreviation) == 0
            ),
            None,
        )

    @staticmethod
    def load_timezones() -> dict[str, str]:
        """Java: Location#loadTimezones."""
        try:
            return {
                row["STATE"]: row["TIMEZONE"]
                for row in _configured_rows("generate.geography.timezones.default_file")
            }
        except Exception:
            logging.getLogger(__name__).error("Unable to load timezones csv", exc_info=True)
            return {}

    @staticmethod
    def load_cities_by_language(resource: str | None = None) -> dict[str, list[str]]:
        """Java: Location#loadCitiesByLanguage."""
        if resource is None:
            resource = Config.get(
                "generate.geography.foreign.birthplace.default_file",
                "geography/foreign_birthplace.json",
            )
        try:
            assert resource is not None
            result: dict[str, list[str]] = json.loads(Utilities.read_resource_or_path(resource))
            return result
        except Exception:
            logging.getLogger(__name__).error(
                "Unable to load foreign places of birth", exc_info=True
            )
            return {}

    @staticmethod
    def get_timezone_by_state(state: str) -> str | None:
        """Java: Location#getTimezoneByState."""
        Location._initialize()
        assert Location.timezones is not None
        return Location.timezones.get(state)

    @staticmethod
    def get_fips_code_by_zip_code(zip_code: str) -> str:
        """Java: Location#getFipsCodeByZipCode."""
        Location._initialize()
        assert Location.cmsStateCodeMapper is not None
        return Location.cmsStateCodeMapper.zip_to_fips_county_code(zip_code)
