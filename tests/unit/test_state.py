"""Unit tests for the control-flow States (T19), ported from the
upstream JUnit StateTest (java/src/test/java/org/mitre/synthea/engine/
StateTest.java).

Only the tests covering T19-owned states are ported: Initial, Terminal,
Guard, Counter, Delay (exact/range/gaussian), SetAttribute (value,
no-value, expression, series data, bad series data) and Death timing
inside a delay. The clinical-state tests (ConditionOnset, Procedure,
Observation, VitalSign, Symptom, ...) belong to T20 and are listed as
skipped in the PR body.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from synthea.engine.module import Module
from synthea.world.agents.person import Person

GENERIC = Path(__file__).resolve().parents[2] / "java" / "src" / "test" / "resources" / "generic"

# Fixed base time (2021-01-01T00:00:00Z) instead of Java's
# System.currentTimeMillis(); none of the assertions depend on the
# wall clock, and a fixed base keeps the month/year delay cases stable.
TIME = 1609459200000


def _fixture(filename: str) -> Module:
    """Mirror of TestHelper.getFixture: parse + construct, no overrides."""
    definition = json.loads((GENERIC / filename).read_text(encoding="utf-8"))
    return Module(definition, submodule=False)


def _person() -> Person:
    """Mirror of StateTest.setup's attribute script (subset the
    control-flow states read)."""
    person = Person(0)
    person.attributes[Person.GENDER] = "F"
    person.attributes[Person.BIRTHDATE] = TIME - 35 * 365 * 24 * 3600 * 1000
    person.history = []
    return person


def test_initial_always_passes() -> None:
    """Java: StateTest#initial_always_passes."""
    module = _fixture("initial_to_terminal.json")
    initial = module.get_state("Initial")
    assert initial is not None
    assert initial.process(_person(), TIME) is True


def test_terminal_never_passes() -> None:
    """Java: StateTest#terminal_never_passes."""
    module = _fixture("initial_to_terminal.json")
    terminal = module.get_state("Terminal")
    assert terminal is not None
    person = _person()
    assert terminal.process(person, TIME) is False
    assert terminal.process(person, TIME + 7 * 24 * 3600 * 1000) is False


def test_guard_passes_when_condition_is_met() -> None:
    """Java: StateTest#guard_passes_when_condition_is_met."""
    module = _fixture("guard.json")
    guard = module.get_state("Gender_Guard")
    assert guard is not None
    person = _person()
    person.attributes[Person.GENDER] = "F"
    assert guard.process(person, TIME) is True


def test_guard_blocks_when_condition_isnt_met() -> None:
    """Java: StateTest#guard_blocks_when_condition_isnt_met."""
    module = _fixture("guard.json")
    guard = module.get_state("Gender_Guard")
    assert guard is not None
    person = _person()
    person.attributes[Person.GENDER] = "M"
    assert guard.process(person, TIME) is False


def test_counter() -> None:
    """Java: StateTest#counter — increment by 1, then decrement by 2."""
    module = _fixture("counter.json")
    person = _person()
    assert person.attributes.get("loop_index") is None

    counter = module.get_state("Counter")
    assert counter is not None
    for expected in (1.0, 2.0, 3.0):
        assert counter.process(person, TIME) is True
        assert person.attributes.get("loop_index") == expected

    decrement = module.get_state("Counter_Decrement_by_2")
    assert decrement is not None
    for expected in (1.0, -1.0):
        assert decrement.process(person, TIME) is True
        assert person.attributes.get("loop_index") == expected


def test_delay_passes_after_exact_time() -> None:
    """Java: StateTest#delay_passes_after_exact_time (all units) and
    #gmfTwoDelayExactTime (same shape on the GMF 2.0 fixture)."""
    module = _fixture("delay.json")
    person = _person()
    units = [
        ("2_Second_Delay", 1000),
        ("2_Minute_Delay", 60 * 1000),
        ("2_Hour_Delay", 3600 * 1000),
        ("2_Day_Delay", 24 * 3600 * 1000),
        ("2_Week_Delay", 7 * 24 * 3600 * 1000),
        ("2_Month_Delay", 30 * 24 * 3600 * 1000),
        ("2_Year_Delay", 365 * 24 * 3600 * 1000),
    ]
    for state_name, unit_ms in units:
        delay = module.get_state(state_name)
        assert delay is not None
        delay.entered = TIME
        assert delay.process(person, TIME) is False
        assert delay.process(person, TIME + unit_ms) is False
        assert delay.process(person, TIME + 2 * unit_ms) is True
        assert delay.process(person, TIME + 3 * unit_ms) is True


def test_gaussian_delay_never_negative() -> None:
    """Java: StateTest#gausian_delay_never_negative — a cloned delay's
    computed end is never before its entry time."""
    module = _fixture("gaussian_distro_delay.json")
    person = _person()
    delay = module.get_state("1 Mean Delay")
    assert delay is not None
    for _ in range(100):
        clone = delay.clone()
        clone.entered = TIME
        clone.process(person, TIME)
        assert clone.next is not None and clone.next >= TIME


def test_set_attribute_with_value() -> None:
    """Java: StateTest#setAttribute_with_value."""
    module = _fixture("set_attribute.json")
    person = _person()
    person.attributes.pop("Current Opioid Prescription", None)
    state = module.get_state("Set_Attribute_1")
    assert state is not None
    assert state.process(person, TIME) is True
    assert person.attributes.get("Current Opioid Prescription") == "Vicodin"


def test_set_attribute_without_value() -> None:
    """Java: StateTest#setAttribute_without_value — no value clears the attribute."""
    module = _fixture("set_attribute.json")
    person = _person()
    person.attributes["Current Opioid Prescription"] = "Vicodin"
    state = module.get_state("Set_Attribute_2")
    assert state is not None
    assert state.process(person, TIME) is True
    assert person.attributes.get("Current Opioid Prescription") is None


def test_set_attribute_with_expression() -> None:
    """Java: StateTest#setAttribute_with_expression — 220 - age(35) = 185."""
    module = _fixture("set_attribute.json")
    person = _person()
    state = module.get_state("Set_Attribute_3")
    assert state is not None
    assert state.process(person, TIME) is True
    value = person.attributes.get("Maximum Heart Rate")
    assert value is not None
    assert abs(float(value) - 185) <= 0.1  # type: ignore[arg-type]


def test_set_attribute_with_series_data() -> None:
    """Java: StateTest#setAttribute_with_seriesData."""
    from synthea.helpers.time_series_data import TimeSeriesData

    module = _fixture("set_attribute.json")
    person = _person()
    state = module.get_state("Set_Attribute_4")
    assert state is not None
    assert state.process(person, TIME) is True
    data = person.attributes.get("ECG")
    assert isinstance(data, TimeSeriesData)
    values = data.get_values()
    assert len(values) == 10
    assert abs(values[0] - 2041) <= 0.0001


def test_death() -> None:
    """Java: StateTest#death — a Death state with no reason records the
    death at the current time."""
    module = _fixture("death.json")
    person = _person()
    death = module.get_state("Death")
    assert death is not None
    assert person.alive(TIME)
    assert death.process(person, TIME) is True
    assert not person.alive(TIME)
    assert person.record is not None
    assert person.record.death == TIME


def test_set_attribute_with_bad_series_data() -> None:
    """Java: StateTest#setAttribute_with_bad_seriesData."""
    module = _fixture("set_attribute.json")
    person = _person()
    state = module.get_state("Set_Attribute_5")
    assert state is not None
    with pytest.raises(RuntimeError) as excinfo:
        state.process(person, TIME)
    assert 'unable to parse "invalid" in SetAttribute state for "ECG"' in str(excinfo.value)
