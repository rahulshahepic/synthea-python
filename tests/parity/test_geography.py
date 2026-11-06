"""Geography component parity: Person_double supplies attributes and the real T01 RNG.

Person construction still calls the unmerged T16 CoverageRecord constructor. The
Java probe uses real Person; this double contains no geography or employment behaviour.
"""

from __future__ import annotations

import json
from typing import cast

import pytest

from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.helpers.utilities import Utilities
from synthea.world.agents.person import Person, Point2DDouble
from synthea.world.concepts.employment import Employment
from synthea.world.geography.cms_state_code_mapper import CMSStateCodeMapper
from synthea.world.geography.location import Location
from synthea.world.geography.place import Place
from synthea.world.geography.quadtree.quad_tree import QuadTree


class Person_double:  # noqa: N801
    """Person state/RNG plumbing only; Java: Person#rand and attributes."""

    UNEMPLOYED = Person.UNEMPLOYED

    def __init__(self, seed: int) -> None:
        self.attributes: dict[str, object] = {}
        self.random = DefaultRandomNumberGenerator(seed)

    def rand(self, low: float | None = None, high: float | None = None) -> float:
        return self.random.rand() if low is None or high is None else self.random.rand(low, high)

    def rand_int(self, bound: int | None = None) -> int:
        return self.random.rand_int(bound)

    def get_count(self) -> int:
        return self.random.get_count()


def geography_draw(location: Location, cms: CMSStateCodeMapper, seed: int) -> dict[str, object]:
    """Drive T10 APIs in the same order as GeographyProbe, with no golden-derived values."""
    rng = DefaultRandomNumberGenerator(seed)
    person_double = Person_double(seed)
    person = cast(Person, person_double)
    d = location.random_city(rng)
    row: dict[str, object] = {
        "state": location.state,
        "seed": seed,
        "id": d.id,
        "city": d.city,
        "county": d.county,
        "population": str(d.population),
    }
    row["age"] = d.pick_age(rng)
    row["gender"] = d.pick_gender(rng)
    race = d.pick_race(rng)
    ethnicity = d.pick_ethnicity(rng)
    row["race"] = race
    row["ethnicity"] = ethnicity
    row["language"] = d.language_from_race_and_ethnicity(race, ethnicity, rng)
    income = d.pick_income(rng)
    row["income"] = income
    income_level = d.income_level(income)
    row["incomeLevel"] = income_level
    row["povertyRatio"] = d.poverty_ratio(income)
    education = d.pick_education(rng)
    row["education"] = education
    education_level = d.education_level(education, rng)
    row["educationLevel"] = education_level
    score = d.socioeconomic_score(income_level, education_level, rng.rand())
    row["score"] = score
    row["category"] = d.socioeconomic_category(score)
    zip_code = location.get_zip_code(d.city, rng)
    row["zip"] = zip_code
    row["zips"] = location.get_zip_codes(d.city)
    row["fips"] = Location.get_fips_code_by_zip_code(zip_code)
    ssa = cms.zip_to_county_code(zip_code)
    if ssa is not None:  # Gson omits null map values.
        row["ssa"] = ssa
    county_code = cms.state_county_name_to_county_code(
        location.state, d.county if seed % 2 == 0 else "Missing County", rng
    )
    if county_code is not None:
        row["countyCode"] = county_code
    row["birthplace"] = location.random_birthplace_by_language(
        rng, "spanish" if seed % 2 == 0 else "unknown-language"
    )
    point_city = None if seed % 4 == 0 else "Missing City" if seed % 4 == 1 else d.city
    if seed % 4 == 3:
        person.attributes[Person.ZIP] = zip_code
    location.assign_point(person, point_city)
    point = cast(Point2DDouble, person.attributes[Person.COORDINATE])
    row["x"], row["y"] = point.x, point.y
    if seed % 2 == 0:
        person.attributes[Person.COUNTY] = d.county
    location.set_social_determinants(person)
    row["sdoh"] = {
        key: person.attributes[key]
        for key in (
            Person.FOOD_INSECURITY,
            Person.SEVERE_HOUSING_COST_BURDEN,
            Person.UNEMPLOYED,
            Person.NO_VEHICLE_ACCESS,
            Person.UNINSURED,
        )
        if key in person.attributes
    }
    employment = Employment(0.35)
    states: list[object] = []
    interval = Utilities.convert_time("months", 6)
    for i in range(24):
        employment.check_employment(person, i * interval)
        states.append(person.attributes.get(Person.UNEMPLOYED))
        employment.check_employment(person, i * interval + 1)
        states.append(person.attributes.get(Person.UNEMPLOYED))
    row["employment"] = states
    row["rngCount"] = rng.get_count()
    row["personCount"] = person.get_count()
    row["nextRand"] = rng.rand()
    row["nextPersonRand"] = person.rand()
    return row


@pytest.mark.parity
def test_geography_component_draws(golden) -> None:
    """2,500 exact seeded draws: five states, including Massachusetts, 500 each."""
    rows = [
        json.loads(line)
        for line in (golden("GeographyProbe") / "draws.jsonl").read_text().splitlines()
    ]
    assert len(rows) == 2500
    cms = CMSStateCodeMapper()
    locations: dict[str, Location] = {}
    for expected in rows:
        state = expected["state"]
        if state not in locations:
            locations[state] = Location(state, None)
        actual = geography_draw(locations[state], cms, expected["seed"])
        assert actual == expected, (
            state,
            expected["seed"],
            {
                key: (actual.get(key), value)
                for key, value in expected.items()
                if actual.get(key) != value
            },
        )
    assert set(locations) == {"Massachusetts", "California", "Texas", "Ohio", "Hawaii"}


@pytest.mark.parity
def test_geography_component_quadtree(golden) -> None:
    """Exact insertion/query order across splits, outside points and radius boundaries."""
    points = [
        Place(
            {
                "USPS": "Test",
                "ST": "TS",
                "NAME": str(i),
                "ZCTA5": "00000",
                "LON": str((i * 37) % 400 - 200.0),
                "LAT": str((i * 19) % 400 - 200.0),
            }
        )
        for i in range(200)
    ]
    tree = QuadTree()
    for point in points:
        assert tree.insert(point)
    rows = [
        json.loads(line)
        for line in (golden("GeographyProbe") / "quadtree.jsonl").read_text().splitlines()
    ]
    assert len(rows) == 200
    for expected in rows:
        i = expected["index"]
        point = points[i]
        assert {
            "index": i,
            "bounds": tree.has_bounds_around(point),
            "errorBounds": tree.has_bounds_around(point, 50),
            "distance": point.distance(points[(i + 1) % len(points)]),
            "query": [cast(Place, p).name for p in tree.query(point, 0 if i % 3 == 0 else 75)],
            "size": tree.size(),
            "description": tree.to_string(),
        } == expected
