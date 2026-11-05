"""Port of TelemedicineTest (JUnit).

Java: java/src/test/java/org/mitre/synthea/helpers/TelemedicineTest.java

The JUnit test constructs Person objects; Person(seed).rand() delegates to
a DefaultRandomNumberGenerator(seed), so the port's fake person wraps that
exact generator (the Person port itself is T09).
"""

from __future__ import annotations

from datetime import date

from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.helpers.telemedicine import Telemedicine
from synthea.helpers.utilities import Utilities


class _Person:
    def __init__(self, seed: int) -> None:
        self._rng = DefaultRandomNumberGenerator(seed)

    def rand(self) -> float:
        return self._rng.rand()


def _timestamp(year: int, month: int, day: int) -> int:
    # LocalDateTime.of(y, m, d, 12, 0).toInstant(UTC).toEpochMilli()
    return Utilities.local_date_to_timestamp(date(year, month, day)) + 43200000


def test_should_encounter_be_virtual() -> None:
    before_telemedicine = _timestamp(2015, 1, 1)
    assert Telemedicine.should_encounter_be_virtual(_Person(0), before_telemedicine) is False
    during_pandemic = _timestamp(2021, 1, 1)
    assert Telemedicine.should_encounter_be_virtual(_Person(8456), during_pandemic) is True


def test_no_draw_before_start() -> None:
    person = _Person(8456)
    assert Telemedicine.should_encounter_be_virtual(person, _timestamp(2015, 1, 1)) is False
    # The pre-start call must not consume randomness: the next draw is the
    # generator's first.
    assert person.rand() == DefaultRandomNumberGenerator(8456).rand()


def test_constants() -> None:
    assert Telemedicine.CURRENT_CHANCE == 0.15
    assert Telemedicine.PREPANDEMIC_CHANCE == 0.004
    assert _timestamp(2016, 1, 1) == Telemedicine.TELEMEDICINE_START_DATE
    assert _timestamp(2020, 4, 1) == Telemedicine.TELEMEDICINE_UPTAKE_DATE
