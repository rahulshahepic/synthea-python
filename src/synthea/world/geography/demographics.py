"""Java: org.mitre.synthea.world.geography.Demographics."""

from __future__ import annotations

import math
from collections.abc import MutableMapping
from functools import cache
from typing import ClassVar

from synthea.helpers.config import Config
from synthea.helpers.random_collection import RandomCollection
from synthea.helpers.random_number_generator import RandomNumberGenerator
from synthea.helpers.simple_csv import SimpleCSV
from synthea.helpers.utilities import Utilities
from synthea.javacompat.collections import JavaHashMap
from synthea.javacompat.hashing import string_compare_to_ignore_case
from synthea.javacompat.numbers import to_int32


@cache
def _demographic_rows(filename: str) -> list[dict[str, str]]:
    """Java: Demographics#load resource parsing, shared lazily by filename."""
    return SimpleCSV.parse(Utilities.read_resource(filename, True, True))


class Demographics:
    """Java: org.mitre.synthea.world.geography.Demographics."""

    RANGE_CACHE: ClassVar[dict[str, list[int]]] = {}
    CSV_AGE_GROUPS: ClassVar[list[str]] = [
        "0..4",
        "5..9",
        "10..14",
        "15..19",
        "20..24",
        "25..29",
        "30..34",
        "35..39",
        "40..44",
        "45..49",
        "50..54",
        "55..59",
        "60..64",
        "65..69",
        "70..74",
        "75..79",
        "80..84",
        "85..110",
    ]
    CSV_RACES: ClassVar[list[str]] = ["WHITE", "BLACK", "ASIAN", "NATIVE", "OTHER"]
    CSV_INCOMES: ClassVar[list[str]] = [
        "00..10",
        "10..15",
        "15..25",
        "25..35",
        "35..50",
        "50..75",
        "75..100",
        "100..150",
        "150..200",
        "200..999",
    ]
    CSV_EDUCATIONS: ClassVar[list[str]] = ["LESS_THAN_HS", "HS_DEGREE", "SOME_COLLEGE", "BS_DEGREE"]
    CSV_ETHNICITY: ClassVar[str] = "HISPANIC"

    def __init__(self) -> None:
        """Java: Demographics#Demographics (implicit constructor)."""
        self.population: int = 0
        self.id: str = ""
        self.city: str = ""
        self.state: str = ""
        self.county: str = ""
        self.ages: MutableMapping[str, float] = JavaHashMap()
        self.gender: MutableMapping[str, float] = JavaHashMap()
        self.race: MutableMapping[str, float] = JavaHashMap()
        self.income: MutableMapping[str, float] = JavaHashMap()
        self.education: MutableMapping[str, float] = JavaHashMap()
        self.ethnicity: float = 0.0
        self.age_distribution: RandomCollection[str] | None = None
        self.gender_distribution: RandomCollection[str] | None = None
        self.race_distribution: RandomCollection[str] | None = None
        self.income_distribution: RandomCollection[str] | None = None
        self.education_distribution: RandomCollection[str] | None = None
        self.ethnicity_distribution: RandomCollection[str] | None = None

    def pick_age(self, random: RandomNumberGenerator) -> int:
        """Java: Demographics#pickAge."""
        if self.age_distribution is None:
            self.age_distribution = self.build_random_collection_from_map(self.ages)
        low, high = self.parse_range(
            self.age_distribution.next(float(random.rand()) * self.age_distribution.total)
        )
        return random.rand_int(high - low + 1) + low

    def pick_gender(self, random: RandomNumberGenerator) -> str:
        """Java: Demographics#pickGender."""
        if self.gender_distribution is None:
            self.gender_distribution = self.build_random_collection_from_map(self.gender)
        return self.gender_distribution.next(float(random.rand()) * self.gender_distribution.total)

    def pick_race(self, random: RandomNumberGenerator) -> str:
        """Java: Demographics#pickRace."""
        if self.race_distribution is None:
            self.race_distribution = self.build_random_collection_from_map(self.race)
        return self.race_distribution.next(float(random.rand()) * self.race_distribution.total)

    def pick_ethnicity(self, random: RandomNumberGenerator) -> str:
        """Java: Demographics#pickEthnicity."""
        if self.ethnicity_distribution is None:
            self.ethnicity_distribution = RandomCollection()
            self.ethnicity_distribution.add(self.ethnicity, "hispanic")
            self.ethnicity_distribution.add(1 - self.ethnicity, "nonhispanic")
        return self.ethnicity_distribution.next(
            float(random.rand()) * self.ethnicity_distribution.total
        )

    def language_from_race_and_ethnicity(
        self, race: str, ethnicity: str, random: RandomNumberGenerator
    ) -> str:
        """Java: Demographics#languageFromRaceAndEthnicity."""
        if ethnicity == "hispanic":
            languages = [(48.85, "english"), (51.15, "spanish")]
        elif race == "white":
            languages = [
                (0.002, "italian"),
                (0.004, "french"),
                (0.003, "german"),
                (0.001, "polish"),
                (0.002, "portuguese"),
                (0.003, "russian"),
                (0.001, "greek"),
                (0.984, "english"),
            ]
        elif race == "black":
            languages = [(0.004, "french"), (0.026, "spanish"), (0.97, "english")]
        elif race == "asian":
            languages = [
                (0.147, "chinese"),
                (0.022, "japanese"),
                (0.056, "korean"),
                (0.07, "vietnamese"),
                (0.033, "hindi"),
                (0.67, "english"),
            ]
        elif race == "hawaiian":
            languages = [(0.891, "english"), (0.109, "hawaiian")]
        elif race == "other":
            languages = [(0.065, "arabic"), (0.935, "english")]
        else:
            return "english"
        distribution: RandomCollection[str] = RandomCollection()
        for weight, language in languages:
            distribution.add(weight, language)
        return distribution.next(float(random.rand()) * distribution.total)

    def pick_income(self, random: RandomNumberGenerator) -> int:
        """Java: Demographics#pickIncome; HashMap copy changes capacity/order."""
        if self.income_distribution is None:
            income = JavaHashMap(self.income)
            income.pop("mean", None)
            income.pop("median", None)
            self.income_distribution = self.build_random_collection_from_map(income)
        low, high = self.parse_range(
            self.income_distribution.next(float(random.rand()) * self.income_distribution.total)
        )
        return random.rand_int((high - low) * 1000 + 1) + low * 1000

    def income_level(self, income: int) -> float:
        """Java: Demographics#incomeLevel."""
        poverty = Config.get_as_double("generate.demographics.socioeconomic.income.poverty", 11000)
        high = Config.get_as_double("generate.demographics.socioeconomic.income.high", 75000)
        if income >= high:
            return 1.0
        if income <= poverty:
            return 0.0
        return (income - poverty) / (high - poverty)

    def poverty_ratio(self, income: int) -> float:
        """Java: Demographics#povertyRatio."""
        return income / Config.get_as_double(
            "generate.demographics.socioeconomic.income.poverty", 11000
        )

    def pick_education(self, random: RandomNumberGenerator) -> str:
        """Java: Demographics#pickEducation."""
        if self.education_distribution is None:
            self.education_distribution = self.build_random_collection_from_map(self.education)
        return self.education_distribution.next(
            float(random.rand()) * self.education_distribution.total
        )

    def education_level(self, level: str, random: RandomNumberGenerator) -> float:
        """Java: Demographics#educationLevel."""
        bounds = {
            "less_than_hs": (0.0, 0.5),
            "hs_degree": (0.1, 0.75),
            "some_college": (0.3, 0.85),
            "bs_degree": (0.5, 1.0),
        }
        # Java reads all eight configuration values before selecting the level.
        configured = {
            key: (
                Config.get_as_double(
                    f"generate.demographics.socioeconomic.education.{key}.min", low
                ),
                Config.get_as_double(
                    f"generate.demographics.socioeconomic.education.{key}.max", high
                ),
            )
            for key, (low, high) in bounds.items()
        }
        if level not in configured:
            return 0.0
        return float(random.rand(*configured[level]))

    def socioeconomic_score(self, income: float, education: float, occupation: float) -> float:
        """Java: Demographics#socioeconomicScore."""
        prefix = "generate.demographics.socioeconomic.weights."
        return (
            income * Config.get_as_double(prefix + "income")
            + education * Config.get_as_double(prefix + "education")
            + occupation * Config.get_as_double(prefix + "occupation")
        )

    def socioeconomic_category(self, score: float) -> str:
        """Java: Demographics#socioeconomicCategory."""
        high = Config.get_as_double("generate.demographics.socioeconomic.score.high")
        middle = Config.get_as_double("generate.demographics.socioeconomic.score.middle")
        return "High" if score >= high else "Middle" if score >= middle else "Low"

    @staticmethod
    def load(state: str | None) -> dict[str, dict[str, Demographics]]:
        """Java: Demographics#load; HashBasedTable uses insertion-ordered rows."""
        filename = Config.get("generate.demographics.default_file")
        if filename is None:
            raise ValueError("Missing generate.demographics.default_file")
        table: dict[str, dict[str, Demographics]] = {}
        for row in _demographic_rows(filename):
            if state is not None and string_compare_to_ignore_case(state, row["STNAME"]) == 0:
                table.setdefault(row["STNAME"], {})[row["ID"]] = (
                    Demographics.csv_line_to_demographics(row)
                )
        return table

    @staticmethod
    def csv_line_to_demographics(line: dict[str, str]) -> Demographics:
        """Java: Demographics#csvLineToDemographics."""
        d = Demographics()
        d.population = int(float(line["POPESTIMATE2015"]))
        d.id, d.city, d.state, d.county = (line[k] for k in ("ID", "NAME", "STNAME", "CTYNAME"))
        for i, group in enumerate(d.CSV_AGE_GROUPS, 1):
            d.ages[group] = float(line[str(i)])
        d.non_zero_defaults(d.ages)
        d.gender["male"] = float(line["TOT_MALE"])
        d.gender["female"] = float(line["TOT_FEMALE"])
        d.non_zero_defaults(d.gender)
        total = 0.0
        for race in d.CSV_RACES:
            percentage = float(line[race])
            d.race[race.lower()] = percentage
            total += percentage
        if total < 1.0:
            remainder = 1.0 - total
            hawaiian = 0.5 * remainder
            d.race["hawaiian"] = hawaiian
            d.race["other"] = remainder - hawaiian
        else:
            d.race["hawaiian"] = d.race["other"] = 0.0
        d.non_zero_defaults(d.race)
        for income in d.CSV_INCOMES:
            d.income[income] = 0.01 if not line[income] else float(line[income])
        d.non_zero_defaults(d.income)
        for education in d.CSV_EDUCATIONS:
            d.education[education.lower()] = 0.01 if not line[education] else float(line[education])
        d.non_zero_defaults(d.education)
        d.ethnicity = float(line[d.CSV_ETHNICITY])
        return d

    @staticmethod
    def non_zero_defaults(map: MutableMapping[str, float]) -> None:
        """Java: Demographics#nonZeroDefaults."""
        for key, value in map.items():
            if value is None or math.isnan(value):
                map[key] = 0.0
        if all(value == 0 for value in map.values()):
            value = 1.0 / len(map)
            for key in map:
                map[key] = value

    @staticmethod
    def parse_range(range: str) -> list[int]:
        """Java: Demographics#parseRange."""
        if range not in Demographics.RANGE_CACHE:
            Demographics.RANGE_CACHE[range] = [int(part) for part in range.split("..")]
        return Demographics.RANGE_CACHE[range]

    @staticmethod
    def build_random_collection_from_map(map: MutableMapping[str, float]) -> RandomCollection[str]:
        """Java: Demographics#buildRandomCollectionFromMap."""
        distribution: RandomCollection[str] = RandomCollection()
        for key, weight in map.items():
            distribution.add(weight, key)
        return distribution

    def compare_to(self, o: Demographics) -> int:
        """Java: Demographics#compareTo (narrowing long subtraction to int)."""
        return to_int32(self.population - o.population)
