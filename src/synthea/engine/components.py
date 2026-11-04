"""Java API skeleton: Components.java."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from synthea.helpers.time_series_data import TimeSeriesData
    from synthea.world.agents.person import Person

    class PersonChartConfig(Protocol):
        """Java boundary type: PersonChartConfig; external to the mapped Python port."""


class Components:
    """Java: Components; pending T17."""

    def __init__(self) -> None:
        """Java: Components#Components.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Components#Components — pending T17")


class Range[R]:
    """Java: Range; pending T17."""

    def __init__(self) -> None:
        """Java: Range#Range.

        Java overloads:
        ()
        """
        self.low: R
        self.high: R
        self.decimals: int
        raise NotImplementedError("Java: Range#Range — pending T17")


class RangeWithUnit[R](Range[R]):
    """Java: RangeWithUnit; pending T17."""

    def __init__(self) -> None:
        """Java: RangeWithUnit#RangeWithUnit.

        Java overloads:
        ()
        """
        self.unit: str
        raise NotImplementedError("Java: RangeWithUnit#RangeWithUnit — pending T17")


class Exact[T]:
    """Java: Exact; pending T17."""

    def __init__(self) -> None:
        """Java: Exact#Exact.

        Java overloads:
        ()
        """
        self.quantity: T
        raise NotImplementedError("Java: Exact#Exact — pending T17")


class ExactWithUnit[T](Exact[T]):
    """Java: ExactWithUnit; pending T17."""

    def __init__(self) -> None:
        """Java: ExactWithUnit#ExactWithUnit.

        Java overloads:
        ()
        """
        self.unit: str
        raise NotImplementedError("Java: ExactWithUnit#ExactWithUnit — pending T17")


class DateInput:
    """Java: DateInput; pending T17."""

    def __init__(self) -> None:
        """Java: DateInput#DateInput.

        Java overloads:
        ()
        """
        self.year: int
        self.month: int
        self.day: int
        self.hour: int
        self.minute: int
        self.second: int
        self.millisecond: int
        raise NotImplementedError("Java: DateInput#DateInput — pending T17")


class SampledData:
    """Java: SampledData; pending T17."""

    def __init__(self, other: SampledData | None = None) -> None:
        """Java: SampledData#SampledData.

        Java overloads:
        ()
        (SampledData other)
        """
        self.origin_value: float
        self.factor: float
        self.lower_limit: float
        self.upper_limit: float
        self.attributes: list[str]
        self.series: list[TimeSeriesData]
        self.decimal_format: str
        raise NotImplementedError("Java: SampledData#SampledData — pending T17")

    def set_series_data(self, person: Person) -> None:
        """Java: SampledData#setSeriesData.

        Java overloads:
        (Person person)
        """
        raise NotImplementedError("Java: SampledData#setSeriesData — pending T17")


class Attachment:
    """Java: Attachment; pending T17."""

    def __init__(self, other: Attachment | None = None) -> None:
        """Java: Attachment#Attachment.

        Java overloads:
        ()
        (Attachment other)
        """
        self.content_type: str
        self.language: str
        self.data: str
        self.url: str
        self.size: int
        self.hash: str
        self.title: str
        self.creation: str
        self.height: int
        self.width: int
        self.frames: int
        self.duration: float
        self.pages: int
        self.chart: PersonChartConfig
        self.validated: bool
        raise NotImplementedError("Java: Attachment#Attachment — pending T17")

    def process(self, person: Person) -> None:
        """Java: Attachment#process.

        Java overloads:
        (Person person)
        """
        raise NotImplementedError("Java: Attachment#process — pending T17")

    def validate(self) -> None:
        """Java: Attachment#validate.

        Java overloads:
        ()
        """
        raise NotImplementedError("Java: Attachment#validate — pending T17")


setattr(Components, "Range", Range)  # noqa: B010
setattr(Components, "RangeWithUnit", RangeWithUnit)  # noqa: B010
setattr(Components, "Exact", Exact)  # noqa: B010
setattr(Components, "ExactWithUnit", ExactWithUnit)  # noqa: B010
setattr(Components, "DateInput", DateInput)  # noqa: B010
setattr(Components, "SampledData", SampledData)  # noqa: B010
setattr(Components, "Attachment", Attachment)  # noqa: B010
