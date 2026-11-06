"""Java: org.mitre.synthea.world.concepts.BirthStatistics."""

from __future__ import annotations

import csv
import io
from typing import IO, TYPE_CHECKING, ClassVar, cast

from synthea.helpers.config import Config
from synthea.helpers.random_number_generator import RandomNumberGenerator
from synthea.helpers.utilities import Utilities
from synthea.javacompat.numbers import double_to_string
from synthea.resources import read_resource

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class BirthStatistics:
    """Java: BirthStatistics."""

    BIRTH_WEEK: ClassVar[str] = "pregnancy_birth_week"
    BIRTH_DATE: ClassVar[str] = "pregnancy_birth_date"
    BIRTH_WEIGHT: ClassVar[str] = "pregnancy_birth_weight"
    BIRTH_HEIGHT: ClassVar[str] = "pregnancy_birth_height"
    BIRTH_SEX: ClassVar[str] = "pregnancy_birth_sex"
    DEFAULT_WEIGHT: ClassVar[float] = 3.5
    DEFAULT_HEIGHT: ClassVar[float] = 51.0
    LOG_OUTPUT: ClassVar[bool] = Config.get_as_boolean("generate.birthweights.logging", False)
    OUTPUT: ClassVar[IO[str] | None]
    WEIGHT_DATA: ClassVar[list[dict[str, str]] | None]

    def __init__(self) -> None:
        """Java: BirthStatistics#BirthStatistics (implicit default constructor)."""

    @staticmethod
    def open_file() -> IO[str] | None:
        """Java: BirthStatistics#openFile."""
        if not BirthStatistics.LOG_OUTPUT:
            return None
        from synthea.export.exporter import Exporter

        folder = Exporter.get_output_folder("", cast("Person", None))
        folder.mkdir(parents=True, exist_ok=True)
        return (folder / "birth_statistics.csv").open("w")

    @staticmethod
    def load_data() -> list[dict[str, str]] | None:
        """Java: BirthStatistics#loadData."""
        filename = Config.get("generate.birthweights.default_file")
        try:
            return list(csv.DictReader(io.StringIO(read_resource(cast(str, filename)))))
        except (OSError, TypeError):
            return None

    @staticmethod
    def clear_birth_statistics(mother: Person) -> None:
        """Java: BirthStatistics#clearBirthStatistics."""
        for key in (
            BirthStatistics.BIRTH_DATE,
            BirthStatistics.BIRTH_HEIGHT,
            BirthStatistics.BIRTH_SEX,
            BirthStatistics.BIRTH_WEEK,
            BirthStatistics.BIRTH_WEIGHT,
        ):
            mother.attributes.pop(key, None)

    @staticmethod
    def set_birth_statistics(mother: Person, time: int) -> None:
        """Java: BirthStatistics#setBirthStatistics."""
        cls = BirthStatistics
        attrs = mother.attributes
        if attrs.get("gender") == "M" or not attrs.get("pregnant", False):
            return
        sex = (
            attrs[cls.BIRTH_SEX]
            if cls.BIRTH_SEX in attrs
            else ("M" if mother.rand_boolean() else "F")
        )
        attrs[cls.BIRTH_SEX] = sex
        if cls.WEIGHT_DATA is None:
            attrs[cls.BIRTH_WEEK] = 40
            attrs[cls.BIRTH_HEIGHT] = cls.DEFAULT_HEIGHT
            attrs[cls.BIRTH_WEIGHT] = cls.DEFAULT_WEIGHT
            return
        hispanic = cls.is_hispanic(mother)
        max_value = 0.0
        for row in cls.WEIGHT_DATA:
            x = float(row["sum"])
            if (
                (row["hispanic_mother"].lower() == "true") == hispanic
                and row["baby_sex"] == sex
                and x > max_value
            ):
                max_value = x
        data = None
        roll = cast(float, cast(RandomNumberGenerator, mother).rand(0, max_value))
        for row in cls.WEIGHT_DATA:
            if (
                (row["hispanic_mother"].lower() == "true") == hispanic
                and row["baby_sex"] == sex
                and roll < float(row["sum"])
                and data is None
            ):
                data = row
        assert data is not None
        week = int(data["lmp_gestational_age"])
        attrs[cls.BIRTH_WEEK] = week
        attrs[cls.BIRTH_DATE] = time + Utilities.convert_time("weeks", week)
        roll = cast(float, cast(RandomNumberGenerator, mother).rand(0, float(data["weight"])))
        weights = sorted(
            set(data) - {"hispanic_mother", "baby_sex", "lmp_gestational_age", "weight", "sum"}
        )
        for weight in weights:
            roll = roll - float(data[weight])
            attrs[cls.BIRTH_WEIGHT] = float(weight) / 1000
            if roll < 0:
                break
        attrs[cls.BIRTH_HEIGHT] = cls.DEFAULT_HEIGHT
        if cls.LOG_OUTPUT:
            assert cls.OUTPUT is not None
            cls.OUTPUT.write(
                f"{str(hispanic).lower()},{sex},{week},"
                f"{double_to_string(cast(float, attrs[cls.BIRTH_WEIGHT]))}\n"
            )
            cls.OUTPUT.flush()

    @staticmethod
    def is_hispanic(mother: Person) -> bool:
        """Java: BirthStatistics#isHispanic."""
        return cast(str, mother.attributes.get("ethnicity")).lower() == "hispanic"


BirthStatistics.OUTPUT = BirthStatistics.open_file()
BirthStatistics.WEIGHT_DATA = BirthStatistics.load_data()
