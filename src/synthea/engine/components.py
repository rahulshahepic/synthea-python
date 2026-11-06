"""Java: org.mitre.synthea.engine.Components (T17).

Various components used in the generic module framework. All components are
defined within this class in Java; here they are module-level classes, also
attached to ``Components`` as attributes to mirror the Java nesting.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Protocol, cast

if TYPE_CHECKING:
    from synthea.helpers.time_series_data import TimeSeriesData
    from synthea.world.agents.person import Person

    class PersonChartConfig(Protocol):
        """Java boundary type: ChartRenderer.PersonChartConfig; chart rendering
        is out of scope for the Python port (PORTING_GUIDE §8)."""


class Components:
    """Java: org.mitre.synthea.engine.Components.

    Abstract holder class in Java; it is never instantiated.
    """

    def __init__(self) -> None:
        """Java: Components#Components (implicit default constructor)."""
        raise TypeError("Components is abstract (Java: abstract class Components)")


class Range[R: int | float | Decimal]:
    """Java: Components.Range — a range of values, with a low and a high."""

    def __init__(self) -> None:
        """Java: Range#Range (implicit default constructor; fields default to null)."""
        self.low: R | None = None
        self.high: R | None = None
        self.decimals: int | None = None


class RangeWithUnit[R: int | float | Decimal](Range[R]):
    """Java: Components.RangeWithUnit — a Range where a unit is required."""

    def __init__(self) -> None:
        """Java: RangeWithUnit#RangeWithUnit (implicit default constructor)."""
        super().__init__()
        self.unit: str | None = None


class Exact[T]:
    """Java: Components.Exact — a single fixed value (not necessarily numeric)."""

    def __init__(self) -> None:
        """Java: Exact#Exact (implicit default constructor; field defaults to null)."""
        self.quantity: T | None = None


class ExactWithUnit[T](Exact[T]):
    """Java: Components.ExactWithUnit — an Exact where a unit is required."""

    def __init__(self) -> None:
        """Java: ExactWithUnit#ExactWithUnit (implicit default constructor)."""
        super().__init__()
        self.unit: str | None = None


class DateInput:
    """Java: Components.DateInput — a date input with detailed time components."""

    def __init__(self) -> None:
        """Java: DateInput#DateInput (implicit default constructor; int fields default to 0)."""
        self.year: int = 0
        self.month: int = 0
        self.day: int = 0
        self.hour: int = 0
        self.minute: int = 0
        self.second: int = 0
        self.millisecond: int = 0


class SampledData:
    """Java: Components.SampledData — sampled data with attributes and series."""

    def __init__(self, other: SampledData | None = None) -> None:
        """Java: SampledData#SampledData.

        Java overloads:
        ()
        (SampledData other)

        Java quirk, reproduced: the copy constructor does NOT copy
        ``decimalFormat`` (it is left null on the copy).
        """
        self.origin_value: float = 0.0
        self.factor: float | None = None
        self.lower_limit: float | None = None
        self.upper_limit: float | None = None
        self.attributes: list[str] | None = None
        self.series: list[TimeSeriesData] | None = None
        self.decimal_format: str | None = None
        if other is not None:
            self.origin_value = other.origin_value
            self.factor = other.factor
            self.lower_limit = other.lower_limit
            self.upper_limit = other.upper_limit
            self.attributes = other.attributes
            self.series = other.series

    def set_series_data(self, person: Person) -> None:
        """Java: SampledData#setSeriesData.

        Java overloads:
        (Person person)

        Retrieves the actual data lists from the given Person according to
        the ``attributes`` values, verifying that every series has the same
        length and period (Java: IllegalArgumentException, mirrored as
        ValueError). Java quirk, reproduced: the first series is detected by
        ``dataLen == 0``, so a leading zero-length series makes the next
        series the reference series too.
        """
        assert self.attributes is not None
        data_len = 0
        data_period = 0.0
        self.series = []

        for attr in self.attributes:
            data = cast("TimeSeriesData", person.attributes.get(attr))
            if data is None:
                # Java: NullPointerException on data.getValues().
                raise TypeError(f"Cannot invoke getValues() on null TimeSeriesData for '{attr}'")
            if data_len == 0:
                data_len = len(data.get_values())
                data_period = data.get_period()
            else:
                # Verify that each series is consistent in length
                if len(data.get_values()) != data_len:
                    raise ValueError(
                        "Provided series ["
                        + ", ".join(self.attributes)
                        + "] have inconsistent lengths!"
                    )

                # Verify that each series has identical period
                if data.get_period() != data_period:
                    raise ValueError(
                        "Provided series ["
                        + ", ".join(self.attributes)
                        + "] have inconsistent periods!"
                    )
            self.series.append(data)


_BASE64_ALPHABET = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")


def _is_base64(value: str) -> bool:
    """Apache Commons Codec ``Base64.isBase64(String)``: every byte must be in
    the base64 alphabet or the padding character (whitespace is not allowed)."""
    return all(ch in _BASE64_ALPHABET for ch in value)


class Attachment:
    """Java: Components.Attachment — inline image data, base64 data, or a URL."""

    def __init__(self, other: Attachment | None = None) -> None:
        """Java: Attachment#Attachment.

        Java overloads:
        ()
        (Attachment other)

        The default constructor sets ``validated`` to false; all other fields
        take Java defaults (null / 0 / 0.0).
        """
        self.content_type: str | None = None
        self.language: str | None = None
        self.data: str | None = None
        self.url: str | None = None
        self.size: int = 0
        self.hash: str | None = None
        self.title: str | None = None
        self.creation: str | None = None
        self.height: int = 0
        self.width: int = 0
        self.frames: int = 0
        self.duration: float = 0.0
        self.pages: int = 0
        self.chart: PersonChartConfig | None = None
        self.validated: bool = False
        if other is not None:
            self.content_type = other.content_type
            self.language = other.language
            self.data = other.data
            self.url = other.url
            self.size = other.size
            self.hash = other.hash
            self.title = other.title
            self.creation = other.creation
            self.height = other.height
            self.width = other.width
            self.frames = other.frames
            self.duration = other.duration
            self.pages = other.pages
            self.chart = other.chart
            self.validated = other.validated

    def process(self, person: Person) -> None:
        """Java: Attachment#process.

        Java overloads:
        (Person person)

        With no chart configuration this is a no-op in Java (the rendered
        chart is null, so no data/size/hash is populated). Chart rendering
        via ChartRenderer is out of scope for this task (see the T17 issue).
        """
        if self.chart is not None:
            raise NotImplementedError(
                "Java: Attachment#process — ChartRenderer chart generation is out of scope for T17"
            )

    def validate(self) -> None:
        """Java: Attachment#validate.

        Java overloads:
        ()

        Validates that the attachment parameters are valid; Java throws
        RuntimeException, mirrored here as RuntimeError.
        """
        if self.validated:
            # Nothing to do if it has already been validated
            return
        # Module should define one, and only one, of "chart", "url", or "data"
        if self.chart is None and self.url is None and self.data is None:
            raise RuntimeError(
                "Attachments must provide one of:\n"
                '1. "chart": a chart rendering configuration\n'
                '2. "url": media location URL\n'
                '3. "data": base64 encoded binary data'
            )

        if self.chart is not None and (self.url is not None or self.data is not None):  # noqa: SIM114 — Java if/else-if structure kept
            raise RuntimeError('Only 1 of "chart", "url", or "data" must be defined.')
        elif self.url is not None and self.data is not None:
            raise RuntimeError('Only 1 of "chart", "url", or "data" must be defined.')

        if self.data is not None and not _is_base64(self.data):
            raise RuntimeError(
                'Invalid Attachment data "'
                + self.data
                + '". If provided, this must be a Base64 encoded string.'
            )


setattr(Components, "Range", Range)  # noqa: B010
setattr(Components, "RangeWithUnit", RangeWithUnit)  # noqa: B010
setattr(Components, "Exact", Exact)  # noqa: B010
setattr(Components, "ExactWithUnit", ExactWithUnit)  # noqa: B010
setattr(Components, "DateInput", DateInput)  # noqa: B010
setattr(Components, "SampledData", SampledData)  # noqa: B010
setattr(Components, "Attachment", Attachment)  # noqa: B010
