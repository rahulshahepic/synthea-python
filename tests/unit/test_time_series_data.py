"""Unit tests for TimeSeriesData.

The upstream TimeSeriesDataTest is an empty class, so these cover the
Java class's constructors, accessors and addValue directly.
Java: org.mitre.synthea.helpers.TimeSeriesData
"""

from __future__ import annotations

import pytest

from synthea.helpers.time_series_data import TimeSeriesData


def test_period_constructor() -> None:
    ts = TimeSeriesData(2.5)
    assert ts.get_period() == 2.5
    assert ts.get_values() == []


def test_values_constructor_keeps_reference() -> None:
    backing = [1.0, 2.0]
    ts = TimeSeriesData(backing, 0.5)
    assert ts.get_period() == 0.5
    backing.append(3.0)
    assert ts.get_values() == [1.0, 2.0, 3.0]


def test_capacity_constructor() -> None:
    ts = TimeSeriesData(10, 1.25)
    assert ts.get_values() == []
    assert ts.get_period() == 1.25
    with pytest.raises(ValueError):
        TimeSeriesData(-1, 1.0)


def test_add_value_and_setters() -> None:
    ts = TimeSeriesData(1.0)
    assert ts.add_value(4.5) is True
    assert ts.add_value(-2.25) is True
    assert ts.get_values() == [4.5, -2.25]
    ts.set_period(9.75)
    assert ts.get_period() == 9.75
    assert ts.period == 9.75
    ts.set_values([7.0])
    assert ts.values == [7.0]
