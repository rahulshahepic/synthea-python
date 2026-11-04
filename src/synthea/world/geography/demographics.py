"""Java API skeleton: Demographics.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.helpers.random_collection import RandomCollection
    from synthea.helpers.random_number_generator import RandomNumberGenerator


class Demographics:
    """Java: Demographics; pending T10."""

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
        """Java: Demographics#Demographics.

        Java overloads:
        ()
        """
        self.population: int
        self.id: str
        self.city: str
        self.state: str
        self.county: str
        self.ages: dict[str, float]
        self.age_distribution: RandomCollection[str]
        self.gender: dict[str, float]
        self.gender_distribution: RandomCollection[str]
        self.race: dict[str, float]
        self.race_distribution: RandomCollection[str]
        self.ethnicity: float
        self.ethnicity_distribution: RandomCollection[str]
        self.income: dict[str, float]
        self.income_distribution: RandomCollection[str]
        self.education: dict[str, float]
        self.education_distribution: RandomCollection[str]
        raise NotImplementedError("Java: Demographics#Demographics — pending T10")

    def pick_age(self, random: RandomNumberGenerator) -> int:
        """Java: Demographics#pickAge.

        Java overloads:
        (RandomNumberGenerator random)
        """
        raise NotImplementedError("Java: Demographics#pickAge — pending T10")

    def pick_gender(self, random: RandomNumberGenerator) -> str:
        """Java: Demographics#pickGender.

        Java overloads:
        (RandomNumberGenerator random)
        """
        raise NotImplementedError("Java: Demographics#pickGender — pending T10")

    def pick_race(self, random: RandomNumberGenerator) -> str:
        """Java: Demographics#pickRace.

        Java overloads:
        (RandomNumberGenerator random)
        """
        raise NotImplementedError("Java: Demographics#pickRace — pending T10")

    def pick_ethnicity(self, random: RandomNumberGenerator) -> str:
        """Java: Demographics#pickEthnicity.

        Java overloads:
        (RandomNumberGenerator random)
        """
        raise NotImplementedError("Java: Demographics#pickEthnicity — pending T10")

    def language_from_race_and_ethnicity(
        self, race: str, ethnicity: str, random: RandomNumberGenerator
    ) -> str:
        """Java: Demographics#languageFromRaceAndEthnicity.

        Java overloads:
        (String race, String ethnicity, RandomNumberGenerator random)
        """
        raise NotImplementedError("Java: Demographics#languageFromRaceAndEthnicity — pending T10")

    def pick_income(self, random: RandomNumberGenerator) -> int:
        """Java: Demographics#pickIncome.

        Java overloads:
        (RandomNumberGenerator random)
        """
        raise NotImplementedError("Java: Demographics#pickIncome — pending T10")

    def income_level(self, income: int) -> float:
        """Java: Demographics#incomeLevel.

        Java overloads:
        (int income)
        """
        raise NotImplementedError("Java: Demographics#incomeLevel — pending T10")

    def poverty_ratio(self, income: int) -> float:
        """Java: Demographics#povertyRatio.

        Java overloads:
        (int income)
        """
        raise NotImplementedError("Java: Demographics#povertyRatio — pending T10")

    def pick_education(self, random: RandomNumberGenerator) -> str:
        """Java: Demographics#pickEducation.

        Java overloads:
        (RandomNumberGenerator random)
        """
        raise NotImplementedError("Java: Demographics#pickEducation — pending T10")

    def education_level(self, level: str, random: RandomNumberGenerator) -> float:
        """Java: Demographics#educationLevel.

        Java overloads:
        (String level, RandomNumberGenerator random)
        """
        raise NotImplementedError("Java: Demographics#educationLevel — pending T10")

    def socioeconomic_score(self, income: float, education: float, occupation: float) -> float:
        """Java: Demographics#socioeconomicScore.

        Java overloads:
        (double income, double education, double occupation)
        """
        raise NotImplementedError("Java: Demographics#socioeconomicScore — pending T10")

    def socioeconomic_category(self, score: float) -> str:
        """Java: Demographics#socioeconomicCategory.

        Java overloads:
        (double score)
        """
        raise NotImplementedError("Java: Demographics#socioeconomicCategory — pending T10")

    @staticmethod
    def load(state: str) -> dict[str, str]:
        """Java: Demographics#load.

        Java overloads:
        (String state)
        """
        raise NotImplementedError("Java: Demographics#load — pending T10")

    @staticmethod
    def csv_line_to_demographics(line: dict[str, str]) -> Demographics:
        """Java: Demographics#csvLineToDemographics.

        Java overloads:
        (Map line)
        """
        raise NotImplementedError("Java: Demographics#csvLineToDemographics — pending T10")

    @staticmethod
    def non_zero_defaults(map: dict[str, float]) -> None:
        """Java: Demographics#nonZeroDefaults.

        Java overloads:
        (Map map)
        """
        raise NotImplementedError("Java: Demographics#nonZeroDefaults — pending T10")

    @staticmethod
    def parse_range(range: str) -> list[int]:
        """Java: Demographics#parseRange.

        Java overloads:
        (String range)
        """
        raise NotImplementedError("Java: Demographics#parseRange — pending T10")

    @staticmethod
    def build_random_collection_from_map(map: dict[str, float]) -> RandomCollection[str]:
        """Java: Demographics#buildRandomCollectionFromMap.

        Java overloads:
        (Map map)
        """
        raise NotImplementedError("Java: Demographics#buildRandomCollectionFromMap — pending T10")

    def compare_to(self, o: Demographics) -> int:
        """Java: Demographics#compareTo.

        Java overloads:
        (Demographics o)
        """
        raise NotImplementedError("Java: Demographics#compareTo — pending T10")
