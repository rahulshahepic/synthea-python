"""Java API skeleton: BirthStatistics.java."""

from __future__ import annotations

from typing import IO, TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from synthea.world.agents.person import Person


class BirthStatistics:
    """Java: BirthStatistics; pending T12."""

    BIRTH_WEEK: ClassVar[str] = "pregnancy_birth_week"
    BIRTH_DATE: ClassVar[str] = "pregnancy_birth_date"
    BIRTH_WEIGHT: ClassVar[str] = "pregnancy_birth_weight"
    BIRTH_HEIGHT: ClassVar[str] = "pregnancy_birth_height"
    BIRTH_SEX: ClassVar[str] = "pregnancy_birth_sex"
    DEFAULT_WEIGHT: ClassVar[float] = 3.5
    DEFAULT_HEIGHT: ClassVar[float] = 51.0
    LOG_OUTPUT: ClassVar[bool]  # Java initialization deferred to T12.
    OUTPUT: ClassVar[IO[str]]  # Java initialization deferred to T12.
    WEIGHT_DATA: ClassVar[list[dict[str, str]]]  # Java initialization deferred to T12.

    def __init__(self) -> None:
        """Java: BirthStatistics#BirthStatistics.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: BirthStatistics#BirthStatistics — pending T12")

    @staticmethod
    def open_file() -> IO[str]:
        """Java: BirthStatistics#openFile.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: BirthStatistics#openFile — pending T12")

    @staticmethod
    def load_data() -> list[dict[str, str]]:
        """Java: BirthStatistics#loadData.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: BirthStatistics#loadData — pending T12")

    @staticmethod
    def clear_birth_statistics(mother: Person) -> None:
        """Java: BirthStatistics#clearBirthStatistics.

        Java overloads:
        (Person mother)
        """
        raise NotImplementedError("Java: BirthStatistics#clearBirthStatistics — pending T12")

    @staticmethod
    def set_birth_statistics(mother: Person, time: int) -> None:
        """Java: BirthStatistics#setBirthStatistics.

        Java overloads:
        (Person mother, long time)
        """
        raise NotImplementedError("Java: BirthStatistics#setBirthStatistics — pending T12")

    @staticmethod
    def is_hispanic(mother: Person) -> bool:
        """Java: BirthStatistics#isHispanic.

        Java overloads:
        (Person mother)
        """
        raise NotImplementedError("Java: BirthStatistics#isHispanic — pending T12")
