"""Ports of DemographicsTest, LocationTest, EmploymentTest, plus geography edges.

Person_double is the component boundary for the unmerged T16 constructor; it
supplies only attributes and T01 RNG, never geography/employment decisions.
"""

from __future__ import annotations

from collections import Counter
from typing import cast

import pytest

from synthea.helpers.config import Config
from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.helpers.random_number_generator import RandomNumberGenerator
from synthea.helpers.simple_csv import SimpleCSV
from synthea.helpers.utilities import Utilities
from synthea.javacompat.collections import JavaHashMap
from synthea.resources import REPO_ROOT
from synthea.world.agents.person import Person, Point2DDouble
from synthea.world.concepts.employment import Employment
from synthea.world.geography.cms_state_code_mapper import CMSStateCodeMapper
from synthea.world.geography.demographics import Demographics
from synthea.world.geography.location import Location
from synthea.world.geography.place import Place
from tests.parity.test_geography import Person_double

TEST_RESOURCES = REPO_ROOT / "java/src/test/resources"


@pytest.fixture(scope="module")
def location() -> Location:
    """Java: LocationTest#createLocation."""
    return Location("Massachusetts", None)


@pytest.fixture
def philly() -> Demographics:
    """Java: DemographicsTest#setUp; restore config after loading the fixture."""
    original = Config.get("generate.demographics.default_file")
    try:
        Config.set(
            "generate.demographics.default_file",
            str(TEST_RESOURCES / "geography/test_demographics.csv"),
        )
        return Demographics.load("Pennsylvania")["Pennsylvania"]["27237"]
    finally:
        assert original is not None
        Config.set("generate.demographics.default_file", original)


def test_demographics_upstream_race_and_ethnicity(philly: Demographics) -> None:
    """Java: DemographicsTest#pickRace, #pickEthnicity."""
    random = DefaultRandomNumberGenerator(0)
    races = Counter(philly.pick_race(random) for _ in range(10000))
    assert 4300 < races["white"] < 4800
    assert 4100 < races["black"] < 4700
    assert 500 < races["asian"] < 900
    hispanic = sum(philly.pick_ethnicity(random) == "hispanic" for _ in range(10000))
    assert 1000 < hispanic < 1600


def test_demographics_upstream_languages(philly: Demographics) -> None:
    """Java: DemographicsTest#languageFromRaceAndEthnicity."""
    random = DefaultRandomNumberGenerator(0)
    hispanic = Counter(
        philly.language_from_race_and_ethnicity("white", "hispanic", random) for _ in range(10000)
    )
    assert 4600 < hispanic["english"] < 5000
    assert 4900 < hispanic["spanish"] < 5300
    white = Counter(
        philly.language_from_race_and_ethnicity("white", "nonhispanic", random)
        for _ in range(10000)
    )
    assert white["english"] > 9500
    asian = Counter(
        philly.language_from_race_and_ethnicity("asian", "nonhispanic", random)
        for _ in range(10000)
    )
    assert 6400 < asian["english"] < 7000
    assert 900 < asian["chinese"] < 1900


def test_location_upstream_metadata_and_zips(location: Location) -> None:
    """Java: LocationTest abbreviation/population/zip/FIPS/timezone tests."""
    abbreviation = Location.get_abbreviation("Massachusetts")
    assert abbreviation is not None and abbreviation != "Massachusetts"
    assert Location.get_state_name(abbreviation) == "Massachusetts"
    assert location.get_population("Bedford") > 0
    assert location.get_zip_code(
        "Bedford", DefaultRandomNumberGenerator(1)
    ) in location.get_zip_codes("Bedford")
    assert Location.get_fips_code_by_zip_code(location.get_zip_codes("Bedford")[0])
    assert Location.get_timezone_by_state("Massachusetts") is not None
    missing = "The Lost City of Atlantis"
    assert location.get_population(missing) == 0
    assert location.get_zip_codes(missing) == ["00000"]
    assert Location.get_fips_code_by_zip_code("00000") == ""


def test_location_upstream_missing_state_and_city() -> None:
    """Java: LocationTest#testStateThatDoesNotExist and city validation."""
    with pytest.raises(ValueError, match="The state The Lost State of Atlantis was not found"):
        Location("The Lost State of Atlantis", None)
    with pytest.raises(ValueError, match="The city Atlantis was not found"):
        Location("Massachusetts", "Atlantis")


@pytest.mark.parametrize("town", ["Bedford", "The Lost City of Atlantis"])
def test_location_component_upstream_assign_point(location: Location, town: str) -> None:
    """Java: LocationTest#testAssignPointInMultiZipCodeCity / missing city."""
    person_double = Person_double(1)
    person = cast(Person, person_double)
    person.attributes[Person.ZIP] = location.get_zip_code(town, cast(RandomNumberGenerator, person))
    location.assign_point(person, town)
    assert isinstance(person.attributes[Person.COORDINATE], Point2DDouble)


def test_location_upstream_all_demographics_have_locations() -> None:
    """Java: LocationTest#testAllDemographicsHaveLocations."""
    demographics = SimpleCSV.parse(
        Utilities.read_resource("geography/demographics.csv", True, True)
    )
    zips = SimpleCSV.parse(Utilities.read_resource("geography/zipcodes.csv", True, True))
    demo_locations = {(row["NAME"] + ", " + row["STNAME"]).upper() for row in demographics}
    zip_locations = {(row["NAME"] + ", " + row["USPS"]).upper() for row in zips}
    assert demo_locations == zip_locations


def test_location_upstream_foreign_birthplace_load() -> None:
    """Java: LocationTest valid/missing/malformed foreign file tests."""
    cities = Location.load_cities_by_language(
        str(TEST_RESOURCES / "geography/foreign_birthplace_simple.json")
    )
    assert set(cities) == {"german", "west_indian"}
    assert all(len(values) == 1 for values in cities.values())
    assert Location.load_cities_by_language("geography/this_isnt_a_file.json") == {}
    assert (
        Location.load_cities_by_language(
            str(TEST_RESOURCES / "geography/malformed_foreign_birthplace.json.txt")
        )
        == {}
    )


@pytest.mark.parametrize(
    "language",
    ["german", "too_many_elements", "not_enough_elements", "unknown_ethnicity", "empty_ethnicity"],
)
def test_location_upstream_birthplace_formats(
    location: Location, language: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Java: LocationTest five randomBirthplaceByLanguage validity tests."""
    monkeypatch.setattr(
        Location,
        "foreignPlacesOfBirth",
        Location.load_cities_by_language(str(TEST_RESOURCES / "geography/foreign_birthplace.json")),
    )
    birthplace = location.random_birthplace_by_language(DefaultRandomNumberGenerator(0), language)
    assert len(birthplace) == 4
    assert all(part is not None and part in birthplace[-1] for part in birthplace)


@pytest.mark.parametrize("county", [None, "Middlesex County", "Nowhere County"])
def test_location_component_upstream_social_determinants(
    location: Location, county: str | None
) -> None:
    """Java: LocationTest#testSocialDeterminantsOfHealth."""
    person_double = Person_double(0)
    person = cast(Person, person_double)
    if county is not None:
        person.attributes[Person.COUNTY] = county
    before = len(person.attributes)
    location.set_social_determinants(person)
    assert len(person.attributes) > before
    assert isinstance(person.attributes[Person.EMPLOYMENT_MODEL], Employment)


def test_employment_component_upstream_check() -> None:
    """Java: EmploymentTest#testCheckEmployment."""
    employment = Employment(0.75)
    person_double = Person_double(0)
    person = cast(Person, person_double)
    person.attributes[Person.UNEMPLOYED] = False
    for time in (0, 1000, 2000):
        employment.check_employment(person, time)
        assert person.attributes[Person.UNEMPLOYED] is True
    employment.check_employment(person, 15552000001)
    assert person.attributes[Person.UNEMPLOYED] is False


def test_geography_nonzero_and_range_cache() -> None:
    """Java: Demographics#nonZeroDefaults and #parseRange edge branches."""
    values = JavaHashMap({"a": float("nan"), "b": 0.0})
    Demographics.non_zero_defaults(values)
    assert dict(values) == {"a": 0.5, "b": 0.5}
    values["a"] = 0.25
    values["b"] = float("nan")
    Demographics.non_zero_defaults(values)
    assert dict(values) == {"a": 0.25, "b": 0.0}
    assert Demographics.parse_range("-10..25") == [-10, 25]
    assert Demographics.parse_range("-10..25") is Demographics.parse_range("-10..25")


def test_geography_place_and_fixed_city(location: Location) -> None:
    """Java: Place and Location#randomCity fixed-city path consumes no draw."""
    place = Place(
        {
            "USPS": "Massachusetts",
            "ST": "MA",
            "NAME": "Boston",
            "ZCTA5": "02108",
            "LAT": "42.0",
            "LON": "-71.0",
        }
    )
    assert place.same_state("massachusetts") and place.same_state("ma")
    assert not place.same_state("CA")
    assert (place.get_x(), place.get_y()) == (-71.0, 42.0)
    fixed = Location("Massachusetts", "bEdFoRd")
    random = DefaultRandomNumberGenerator(1)
    city = fixed.random_city(random)
    assert city.city == "Bedford"
    assert fixed.random_city(random) is city
    assert random.get_count() == 0
    assert Location.get_index("Massachusetts") >= 0
    assert Location.get_state_name("invalid") is None
    assert Location.get_abbreviation("invalid") is None


def test_geography_cms_codes() -> None:
    """Java: CMSStateCodeMapper lookup and unknown fallbacks."""
    cms = CMSStateCodeMapper()
    assert cms.get_state_code("MA") == cms.get_state_code("Massachusetts") == "22"
    assert cms.get_state_code("ma") == "22"
    assert cms.get_state_code("Unknown") == "NONE"
    assert cms.change_state_format("massachusetts") == "MA"
    assert cms.change_state_format("ZZ") is None
    assert cms.zip_to_county_code("invalid") is None
    assert cms.zip_to_fips_county_code("invalid") == ""
    assert (
        cms.state_county_name_to_county_code("Unknown", "Unknown", DefaultRandomNumberGenerator(0))
        is None
    )
