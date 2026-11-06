"""Unit tests for the Components port (T17).

There is no upstream ComponentsTest; these tests pin the Java field
defaults, the copy constructors (including the SampledData quirk that
decimalFormat is not copied), SampledData.setSeriesData validation, and
Attachment.validate/process behaviour directly from Components.java.
"""

from __future__ import annotations

import pytest

from synthea.engine.components import (
    Attachment,
    DateInput,
    Exact,
    ExactWithUnit,
    Range,
    RangeWithUnit,
    SampledData,
)
from synthea.helpers.time_series_data import TimeSeriesData
from synthea.world.agents.person import Person
from tests.logic_support import patched_person


def test_range_defaults() -> None:
    r: Range[float] = Range()
    assert r.low is None and r.high is None and r.decimals is None
    rwu: RangeWithUnit[float] = RangeWithUnit()
    assert rwu.unit is None and rwu.low is None


def test_exact_defaults() -> None:
    e: Exact[str] = Exact()
    assert e.quantity is None
    ewu: ExactWithUnit[float] = ExactWithUnit()
    assert ewu.quantity is None and ewu.unit is None


def test_date_input_defaults() -> None:
    d = DateInput()
    assert (d.year, d.month, d.day, d.hour, d.minute, d.second, d.millisecond) == (
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    )


def test_sampled_data_defaults_and_copy() -> None:
    data = SampledData()
    assert data.origin_value == 0.0
    assert data.factor is None and data.lower_limit is None and data.upper_limit is None
    assert data.attributes is None and data.series is None and data.decimal_format is None

    data.origin_value = 1.5
    data.factor = 2.0
    data.attributes = ["a"]
    data.decimal_format = "0.00"
    copy = SampledData(data)
    assert copy.origin_value == 1.5 and copy.factor == 2.0 and copy.attributes == ["a"]
    # Java quirk: the copy constructor does not copy decimalFormat.
    assert copy.decimal_format is None


def _series(values: list[float], period: float) -> TimeSeriesData:
    return TimeSeriesData(values, period)


def test_set_series_data(person: Person) -> None:
    person.attributes["s1"] = _series([1.0, 2.0, 3.0], 1.0)
    person.attributes["s2"] = _series([4.0, 5.0, 6.0], 1.0)
    data = SampledData()
    data.attributes = ["s1", "s2"]
    data.set_series_data(person)
    assert data.series is not None and len(data.series) == 2
    assert data.series[0] is person.attributes["s1"]


def test_set_series_data_inconsistent_lengths(person: Person) -> None:
    person.attributes["s1"] = _series([1.0, 2.0, 3.0], 1.0)
    person.attributes["s2"] = _series([4.0, 5.0], 1.0)
    data = SampledData()
    data.attributes = ["s1", "s2"]
    with pytest.raises(ValueError, match="inconsistent lengths"):
        data.set_series_data(person)


def test_set_series_data_inconsistent_periods(person: Person) -> None:
    person.attributes["s1"] = _series([1.0, 2.0], 1.0)
    person.attributes["s2"] = _series([4.0, 5.0], 2.0)
    data = SampledData()
    data.attributes = ["s1", "s2"]
    with pytest.raises(ValueError, match="inconsistent periods"):
        data.set_series_data(person)


def test_set_series_data_missing_attribute(person: Person) -> None:
    data = SampledData()
    data.attributes = ["missing"]
    with pytest.raises(TypeError):
        data.set_series_data(person)


def test_attachment_defaults_and_copy() -> None:
    att = Attachment()
    assert att.validated is False
    assert att.content_type is None and att.data is None and att.url is None
    assert att.size == 0 and att.height == 0 and att.width == 0 and att.frames == 0
    assert att.duration == 0.0 and att.pages == 0 and att.chart is None

    att.url = "https://example.org/x.png"
    att.size = 42
    att.validated = True
    copy = Attachment(att)
    assert copy.url == "https://example.org/x.png"
    assert copy.size == 42 and copy.validated is True


def test_attachment_validate_requires_one_source() -> None:
    with pytest.raises(RuntimeError, match="Attachments must provide one of"):
        Attachment().validate()


def test_attachment_validate_rejects_multiple_sources() -> None:
    att = Attachment()
    att.url = "https://example.org/x.png"
    att.data = "aGVsbG8="
    with pytest.raises(RuntimeError, match='Only 1 of "chart", "url", or "data"'):
        att.validate()


def test_attachment_validate_rejects_bad_base64() -> None:
    att = Attachment()
    att.data = "not base64!!"
    with pytest.raises(RuntimeError, match="Invalid Attachment data"):
        att.validate()


def test_attachment_validate_accepts_url_and_base64() -> None:
    att = Attachment()
    att.url = "https://example.org/x.png"
    att.validate()
    att2 = Attachment()
    att2.data = "aGVsbG8="
    att2.validate()


def test_attachment_validate_noop_when_validated() -> None:
    att = Attachment()
    att.validated = True
    att.validate()  # nothing defined, but already validated: no error


def test_attachment_process_without_chart_is_noop(person: Person) -> None:
    att = Attachment()
    att.data = "aGVsbG8="
    att.process(person)
    assert att.data == "aGVsbG8=" and att.hash is None


def test_attachment_process_with_chart_is_out_of_scope(person: Person) -> None:
    att = Attachment()
    att.chart = object()  # type: ignore[assignment]
    with pytest.raises(NotImplementedError, match="out of scope"):
        att.process(person)


@pytest.fixture
def person() -> Person:
    with patched_person(0) as p:
        yield p
