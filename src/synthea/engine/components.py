"""Java API skeleton for components.py.
Java: org.mitre.synthea.engine.Components.
"""

from __future__ import annotations


class Components:
    """Java: Components; pending T17."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: Components constructor; pending T17."""
        raise NotImplementedError("Java: Components — pending T17")

    def set_series_data(self, *args: object, **kwargs: object) -> object:
        """Java: Components#setSeriesData."""
        raise NotImplementedError("Java: setSeriesData — pending T17")

    def process(self, *args: object, **kwargs: object) -> object:
        """Java: Components#process."""
        raise NotImplementedError("Java: process — pending T17")

    def validate(self, *args: object, **kwargs: object) -> object:
        """Java: Components#validate."""
        raise NotImplementedError("Java: validate — pending T17")


class Range:
    """Java: Range; pending T17."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: Range constructor; pending T17."""
        self.low: object | None = None
        self.high: object | None = None
        self.decimals: object | None = None
        raise NotImplementedError("Java: Range — pending T17")


class RangeWithUnit:
    """Java: RangeWithUnit; pending T17."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: RangeWithUnit constructor; pending T17."""
        self.unit: str | None = None
        raise NotImplementedError("Java: RangeWithUnit — pending T17")


class Exact:
    """Java: Exact; pending T17."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: Exact constructor; pending T17."""
        self.quantity: object | None = None
        raise NotImplementedError("Java: Exact — pending T17")


class ExactWithUnit:
    """Java: ExactWithUnit; pending T17."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: ExactWithUnit constructor; pending T17."""
        self.unit: str | None = None
        raise NotImplementedError("Java: ExactWithUnit — pending T17")


class DateInput:
    """Java: DateInput; pending T17."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: DateInput constructor; pending T17."""
        self.year: int = 0
        self.month: int = 0
        self.day: int = 0
        self.hour: int = 0
        self.minute: int = 0
        self.second: int = 0
        self.millisecond: int = 0
        raise NotImplementedError("Java: DateInput — pending T17")


class SampledData:
    """Java: SampledData; pending T17."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: SampledData constructor; pending T17."""
        self.originValue: float = 0.0
        self.factor: object | None = None
        self.lowerLimit: object | None = None
        self.upperLimit: object | None = None
        self.attributes: list[object] = []
        self.series: list[object] = []
        self.decimalFormat: str | None = None
        raise NotImplementedError("Java: SampledData — pending T17")


class Attachment:
    """Java: Attachment; pending T17."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Java: Attachment constructor; pending T17."""
        self.contentType: str | None = None
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
        self.chart: object | None = None
        self.validated: object | None = None
        raise NotImplementedError("Java: Attachment — pending T17")
