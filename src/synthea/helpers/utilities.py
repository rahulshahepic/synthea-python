"""Java API skeleton: Utilities.java."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Protocol

if TYPE_CHECKING:
    from synthea.engine.components import Range
    from synthea.helpers.random_number_generator import RandomNumberGenerator
    from synthea.world.concepts.health_record import Code

    class Resource(Protocol):
        """Java: org.hl7.fhir.dstu3.model.Resource; external FHIR boundary type."""

    class BiConsumer(Protocol):
        """Java boundary type: BiConsumer; external to the mapped Python port."""

    class Gson(Protocol):
        """Java boundary type: Gson; external to the mapped Python port."""

    class JsonPrimitive(Protocol):
        """Java boundary type: JsonPrimitive; external to the mapped Python port."""

    class URI(Protocol):
        """Java boundary type: URI; external to the mapped Python port."""


class Utilities:
    """Java: Utilities; pending T06."""

    SYNTHEA_VERSION: ClassVar[str]  # Java initialization deferred to T06.

    def __init__(self) -> None:
        """Java: Utilities#Utilities.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Utilities#Utilities — pending T06")

    @staticmethod
    def convert_time(units: str, value: int | float) -> int:
        """Java: Utilities#convertTime.

        Java overloads:
        (String units, long value)
        (String units, double value)
        """
        raise NotImplementedError("Java: Utilities#convertTime — pending T06")

    @staticmethod
    def convert_calendar_years_to_time(years: int) -> int:
        """Java: Utilities#convertCalendarYearsToTime.

        Java overloads:
        (int years)
        """
        raise NotImplementedError("Java: Utilities#convertCalendarYearsToTime — pending T06")

    @staticmethod
    def get_year(time: int) -> int:
        """Java: Utilities#getYear.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: Utilities#getYear — pending T06")

    @staticmethod
    def get_month(time: int) -> int:
        """Java: Utilities#getMonth.

        Java overloads:
        (long time)
        """
        raise NotImplementedError("Java: Utilities#getMonth — pending T06")

    @staticmethod
    def local_date_to_timestamp(date: date) -> int:
        """Java: Utilities#localDateToTimestamp.

        Java overloads:
        (LocalDate date)
        """
        raise NotImplementedError("Java: Utilities#localDateToTimestamp — pending T06")

    @staticmethod
    def timestamp_to_local_date(timestamp: int) -> date:
        """Java: Utilities#timestampToLocalDate.

        Java overloads:
        (long timestamp)
        """
        raise NotImplementedError("Java: Utilities#timestampToLocalDate — pending T06")

    @staticmethod
    def get_anniversary(date: int, anniversary: int) -> int:
        """Java: Utilities#getAnniversary.

        Java overloads:
        (long date, int anniversary)
        """
        raise NotImplementedError("Java: Utilities#getAnniversary — pending T06")

    @staticmethod
    def primitive(p: JsonPrimitive) -> object:
        """Java: Utilities#primitive.

        Java overloads:
        (JsonPrimitive p)
        """
        raise NotImplementedError("Java: Utilities#primitive — pending T06")

    @staticmethod
    def convert_risk_to_timestep(
        risk: float, original_period_in_ms: float, new_time_step_in_ms: float | None = None
    ) -> float:
        """Java: Utilities#convertRiskToTimestep.

        Java overloads:
        (double risk, double originalPeriodInMS)
        (double risk, double originalPeriodInMS, double newTimeStepInMS)
        """
        raise NotImplementedError("Java: Utilities#convertRiskToTimestep — pending T06")

    @staticmethod
    def compare(
        lhs: object | float | bool | str | int | Code,
        rhs: object | float | bool | str | int | Code,
        operator: str,
    ) -> bool:
        """Java: Utilities#compare.

        Java overloads:
        (Object lhs, Object rhs, String operator)
        (Double lhs, Double rhs, String operator)
        (Boolean lhs, Boolean rhs, String operator)
        (String lhs, String rhs, String operator)
        (Integer lhs, Integer rhs, String operator)
        (Code lhs, Code rhs, String operator)
        """
        raise NotImplementedError("Java: Utilities#compare — pending T06")

    @staticmethod
    def get_synthea_version() -> str:
        """Java: Utilities#getSyntheaVersion.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Utilities#getSyntheaVersion — pending T06")

    @staticmethod
    def parse_date_range(range: str) -> Range[int]:
        """Java: Utilities#parseDateRange.

        Java overloads:
        (String range)
        """
        raise NotImplementedError("Java: Utilities#parseDateRange — pending T06")

    @staticmethod
    def read_resource(
        filename: str, strip_bom: bool | None = None, allow_free_path: bool | None = None
    ) -> str:
        """Java: Utilities#readResource.

        Java overloads:
        (String filename)
        (String filename, boolean stripBOM, boolean allowFreePath)
        """
        raise NotImplementedError("Java: Utilities#readResource — pending T06")

    @staticmethod
    def read_resource_or_path(filename: str) -> str:
        """Java: Utilities#readResourceOrPath.

        Java overloads:
        (String filename)
        """
        raise NotImplementedError("Java: Utilities#readResourceOrPath — pending T06")

    @staticmethod
    def read_resource_and_strip_bom(filename: str) -> str:
        """Java: Utilities#readResourceAndStripBOM.

        Java overloads:
        (String filename)
        """
        raise NotImplementedError("Java: Utilities#readResourceAndStripBOM — pending T06")

    @staticmethod
    def get_gson() -> Gson:
        """Java: Utilities#getGson.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Utilities#getGson — pending T06")

    @staticmethod
    def random_dicom_uid(
        random: RandomNumberGenerator, time: int, series_no: int, instance_no: int
    ) -> str:
        """Java: Utilities#randomDicomUid.

        Java overloads:
        (RandomNumberGenerator random, long time, int seriesNo, int instanceNo)
        """
        raise NotImplementedError("Java: Utilities#randomDicomUid — pending T06")

    @staticmethod
    def random_dicom_uid_salt(random: RandomNumberGenerator) -> str:
        """Java: Utilities#randomDicomUidSalt.

        Java overloads:
        (RandomNumberGenerator random)
        """
        raise NotImplementedError("Java: Utilities#randomDicomUidSalt — pending T06")

    @staticmethod
    def str_to_object(clazz: type[object], value: str) -> object:
        """Java: Utilities#strToObject.

        Java overloads:
        (Class clazz, String value)
        """
        raise NotImplementedError("Java: Utilities#strToObject — pending T06")

    @staticmethod
    def walk_all_modules(
        action_or_modules_path: BiConsumer | Path, action: Callable[[Path], None] | None = None
    ) -> None:
        """Java: Utilities#walkAllModules.

        Java overloads:
        (BiConsumer action)
        (Path modulesPath, Consumer action)
        """
        raise NotImplementedError("Java: Utilities#walkAllModules — pending T06")

    @staticmethod
    def clean_map(input: dict[object, object]) -> dict[object, object]:
        """Java: Utilities#cleanMap.

        Java overloads:
        (Map input)
        """
        raise NotImplementedError("Java: Utilities#cleanMap — pending T06")

    @staticmethod
    def enable_reading_uri_from_jar(uri: URI) -> None:
        """Java: Utilities#enableReadingURIFromJar.

        Java overloads:
        (URI uri)
        """
        raise NotImplementedError("Java: Utilities#enableReadingURIFromJar — pending T06")

    @staticmethod
    def parse_yaml_to_resources[T: Resource](
        yaml: list[dict[str, object]], resource_class: type[T]
    ) -> list[T]:
        """Java: Utilities#parseYamlToResources.

        Java overloads:
        (List yaml, Class resourceClass)
        """
        raise NotImplementedError("Java: Utilities#parseYamlToResources — pending T06")
