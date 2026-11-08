"""Java: C19VaccineAgeDistributions.java."""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from datetime import time as dt_time
from typing import TYPE_CHECKING, ClassVar, cast

from synthea.helpers.config import Config
from synthea.helpers.simple_csv import SimpleCSV
from synthea.helpers.synced_enumerated_distro import SyncedEnumeratedDistro
from synthea.helpers.utilities import Utilities
from synthea.javacompat.collections import JavaHashMap
from synthea.javacompat.hashing import objects_hash

if TYPE_CHECKING:
    from synthea.world.agents.person import Person

_INT_MAX_VALUE = 2**31 - 1


def _parse_csv_date(value: str) -> date:
    """Java: CSV_DATE_FORMAT (DateTimeFormatter "M/d/yyyy") parse to LocalDate."""
    return datetime.strptime(value, "%m/%d/%Y").date()


def _noon_epoch_millis(day: date) -> int:
    """Java: LocalDateTime.of(day, LocalTime.NOON) at UTC to epoch milli."""
    moment = datetime.combine(day, dt_time(12, 0), tzinfo=UTC)
    return int(moment.timestamp() * 1000)


class C19VaccineAgeDistributions:
    """Java: C19VaccineAgeDistributions."""

    DOSE_RATES_FILE: ClassVar[str] = "covid_dose_rates.csv"
    FIRST_SHOT_PROBS_FILE: ClassVar[str] = "covid_first_shot_percentage_by_age.json"
    DATE_COLUMN_HEADER: ClassVar[str] = "date"
    EXPAND_AGE_TO_TWELVE: ClassVar[date] = date(2021, 5, 10)
    # Java: DateTimeFormatter.ofPattern("M/d/yyyy"); parsing goes through
    # _parse_csv_date, which implements that pattern.
    CSV_DATE_FORMAT: ClassVar[str] = "M/d/yyyy"
    rawDistributions: ClassVar[JavaHashMap[AgeRange, list[tuple[str, int]]]] = JavaHashMap()
    distributions: ClassVar[JavaHashMap[AgeRange, SyncedEnumeratedDistro[str]]] = JavaHashMap()
    firstShotProbByAge: ClassVar[JavaHashMap[AgeRange, float]] = JavaHashMap()

    def __init__(self) -> None:
        """Java: C19VaccineAgeDistributions#C19VaccineAgeDistributions.

        Java overloads:
        ()
        """

    @staticmethod
    def initialize() -> None:
        """Java: C19VaccineAgeDistributions#initialize.

        Java overloads:
        ()
        """
        C19VaccineAgeDistributions.load_raw_distribution()
        C19VaccineAgeDistributions.populate_distributions()
        C19VaccineAgeDistributions.load_shot_probabilities_by_age()

    @staticmethod
    def load_raw_distribution() -> None:
        """Java: C19VaccineAgeDistributions#loadRawDistribution.

        Java overloads:
        ()
        """
        file_name = Config.get("generate.lookup_tables")
        assert file_name is not None
        file_name = file_name + C19VaccineAgeDistributions.DOSE_RATES_FILE
        csv = Utilities.read_resource(file_name, True, True)
        raw_rates = SimpleCSV.parse(csv)
        raw_distributions = C19VaccineAgeDistributions.rawDistributions
        for row_map in raw_rates:
            date_value = row_map[C19VaccineAgeDistributions.DATE_COLUMN_HEADER]
            for name, value in row_map.items():
                if name != C19VaccineAgeDistributions.DATE_COLUMN_HEADER:
                    age_range = AgeRange(name)
                    distro_for_range = raw_distributions.get(age_range)
                    if distro_for_range is None:
                        distro_for_range = []
                        raw_distributions[age_range] = distro_for_range
                    distro_for_range.append((date_value, int(value)))
        # Special case for 12-15. While there were individuals under 16 who
        # received vaccinations prior to May 10, 2021, the numbers are pretty
        # small. This strips out that population for the sake of simplicity
        # in the simulation (Java comment).
        special_case_range = AgeRange("Ages_12-15_yrs")
        existing = raw_distributions[special_case_range]
        raw_distributions[special_case_range] = [
            pair
            for pair in existing
            if _parse_csv_date(pair[0]) > C19VaccineAgeDistributions.EXPAND_AGE_TO_TWELVE
        ]

    @staticmethod
    def populate_distributions() -> None:
        """Java: C19VaccineAgeDistributions#populateDistributions.

        Java overloads:
        ()
        """
        for age_range, day_info_list in C19VaccineAgeDistributions.rawDistributions.items():
            total_doses_for_range = sum(pair[1] for pair in day_info_list)
            pmf = [(day_info[0], day_info[1] / total_doses_for_range) for day_info in day_info_list]
            C19VaccineAgeDistributions.distributions[age_range] = SyncedEnumeratedDistro(pmf)

    @staticmethod
    def load_shot_probabilities_by_age() -> None:
        """Java: C19VaccineAgeDistributions#loadShotProbabilitiesByAge.

        Java overloads:
        ()
        """
        file_name = "covid19/" + C19VaccineAgeDistributions.FIRST_SHOT_PROBS_FILE
        try:
            raw_json = Utilities.read_resource(file_name)
        except ValueError as exc:
            raise RuntimeError("Couldn't load the shot probabilities file") from exc
        raw_shot_probs: dict[str, object] = json.loads(raw_json)
        for key, value in raw_shot_probs.items():
            age_range = AgeRange(key)
            probability = float(cast("str", value))  # Java: Double.parseDouble((String) value)
            probability = probability / 100
            C19VaccineAgeDistributions.firstShotProbByAge[age_range] = probability

    @staticmethod
    def _range_for_age(age: int) -> AgeRange:
        """Java: distributions.keySet().stream().filter(r -> r.in(age)).findFirst().get()."""
        for age_range in C19VaccineAgeDistributions.distributions:
            if age_range.in_(age):
                return age_range
        raise RuntimeError("No value present")

    @staticmethod
    def select_shot_time(person: Person, time: int) -> int:
        """Java: C19VaccineAgeDistributions#selectShotTime.

        Java overloads:
        (Person person, long time)
        """
        age = person.age_in_years(time)
        age_range = C19VaccineAgeDistributions._range_for_age(age)
        distro = C19VaccineAgeDistributions.distributions[age_range]
        shot_date = _parse_csv_date(distro.synced_reseeded_sample(person))
        return _noon_epoch_millis(shot_date)

    @staticmethod
    def chance_of_getting_shot(person: Person, time: int) -> float:
        """Java: C19VaccineAgeDistributions#chanceOfGettingShot.

        Java overloads:
        (Person person, long time)
        """
        age = person.age_in_years(time)
        age_range = C19VaccineAgeDistributions._range_for_age(age)
        return C19VaccineAgeDistributions.firstShotProbByAge[age_range]


class AgeRange:
    """Java: AgeRange."""

    def __init__(self, display: str) -> None:
        """Java: AgeRange#AgeRange.

        Java overloads:
        (String display)
        """
        self.display: str = display
        length = len(display)
        if length == 12:
            # Example: Ages_75+_yrs
            self.min: int = int(display[5:7])
            self.max: int = _INT_MAX_VALUE
        elif length == 14:
            # Example: Ages_40-49_yrs
            self.min = int(display[5:7])
            self.max = int(display[8:10])
        else:
            raise ValueError("Display should be 12 or 14 characters long.")

    def equals(self, o: object) -> bool:
        """Java: AgeRange#equals.

        Java overloads:
        (Object o)
        """
        if self is o:
            return True
        if o is None or type(o) is not AgeRange:
            return False
        return self.min == o.min and self.max == o.max

    def hash_code(self) -> int:
        """Java: AgeRange#hashCode.

        Java overloads:
        ()
        """
        return objects_hash(self.min, self.max)

    def java_hash_code(self) -> int:
        """Java: AgeRange#hashCode; javacompat collection boundary."""
        return self.hash_code()

    def __eq__(self, other: object) -> bool:
        """Java: AgeRange#equals."""
        return self.equals(other)

    def __hash__(self) -> int:
        """Java: AgeRange#hashCode."""
        return self.hash_code()

    def in_(self, age: int) -> bool:
        """Java: AgeRange#in.

        Java overloads:
        (int age)
        """
        return age >= self.min and age <= self.max


setattr(C19VaccineAgeDistributions, "AgeRange", AgeRange)  # noqa: B010
setattr(AgeRange, "in", AgeRange.in_)
