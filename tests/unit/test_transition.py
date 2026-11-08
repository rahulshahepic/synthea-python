"""Unit tests for Transition (T18), ported from the upstream JUnit tests
TransitionTest and LookupTableTransitionTest.

The JUnit tests drive whole Modules (Module.process) and assert on the
resulting record. Module/State are the rest of this bundle (#19/#20); here
the same fixtures and persons drive the transitions directly, which the
parity probe (tests/parity/test_transition.py) shows consumes identical
RNG draws: the distributed and type-of-care counts below are the exact
JUnit assertions. The LookupTableTransitionTest scenario tests assert
which lookuptablitis condition became active; the fixture CSV gives that
condition probability 1, so the transition's chosen target state is the
same assertion at transition level.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterator
from pathlib import Path

import pytest

from synthea.engine.transition import (
    DistributedTransitionOption,
    IntRange,
    LookupTableKey,
    LookupTableMap,
    LookupTableTransition,
)
from synthea.helpers.config import Config
from synthea.helpers.utilities import Utilities
from synthea.world.agents.payer_manager import PayerManager
from synthea.world.agents.person import Person
from tests.transition_support import build_transition

GENERIC = Path(__file__).resolve().parents[2] / "java" / "src" / "test" / "resources" / "generic"
TIME_2021 = 1609459200000  # TestHelper.timestamp(2021, 1, 1, 0, 0, 0) in UTC


def _option(name: str) -> DistributedTransitionOption:
    option = DistributedTransitionOption()
    option.transition = name
    return option


def _fixture_state(fixture: str, state: str = "Initial") -> dict[str, object]:
    module = json.loads((GENERIC / fixture).read_text(encoding="utf-8"))
    return module["states"][state]


def _transition_person() -> Person:
    """TransitionTest.setup: Person(19), birthdate 0, no-insurance coverage."""
    PayerManager.load_no_insurance()
    person = Person(19)
    person.attributes[Person.BIRTHDATE] = 0
    person.coverage.set_plan_to_no_insurance(0)
    person.coverage.set_plan_to_no_insurance(TIME_2021 + 1)
    return person


# --- TransitionTest -------------------------------------------------------


def test_distributed_transition() -> None:
    person = _transition_person()
    transition = build_transition("distributed", _fixture_state("distributed_transition.json"))
    counts = Counter(transition.follow(person, 0) for _ in range(100))
    assert counts["Terminal1"] == 15
    assert counts["Terminal2"] == 55
    assert counts["Terminal3"] == 30


def test_distributed_transition_with_attributes() -> None:
    person = _transition_person()
    person.attributes["probability1"] = 1.0
    transition = build_transition(
        "distributed", _fixture_state("distributed_transition_with_attrs.json")
    )
    counts = Counter(transition.follow(person, 0) for _ in range(100))
    assert counts["Terminal1"] == 100
    assert counts["Terminal2"] == 0
    assert counts["Terminal3"] == 0

    person.attributes["probability1"] = 0.0
    person.attributes["probability2"] = 0.0
    person.attributes["probability3"] = 1.0
    counts = Counter(transition.follow(person, 0) for _ in range(100))
    assert counts["Terminal1"] == 0
    assert counts["Terminal2"] == 0
    assert counts["Terminal3"] == 100


def test_type_of_care_transition() -> None:
    person = _transition_person()
    transition = build_transition(
        "type_of_care", _fixture_state("virtual_medicine_transition.json")
    )
    counts = Counter(transition.follow(person, TIME_2021) for _ in range(100))
    assert counts["Terminal1"] == 76
    assert counts["Terminal2"] == 8
    assert counts["Terminal3"] == 16


# --- LookupTableTransitionTest: LookupTableKey ----------------------------


def test_key_with_ages_match() -> None:
    silver = LookupTableKey(["foo", "bar"], 20, None)
    gold = LookupTableKey(["foo", "bar"], IntRange(0, 30), None)
    assert silver.equals(gold)
    assert gold.equals(silver)
    assert silver in {gold}


def test_key_with_ages_match_high() -> None:
    silver = LookupTableKey(["foo", "bar"], 30, None)
    gold = LookupTableKey(["foo", "bar"], IntRange(0, 30), None)
    assert silver.equals(gold)
    assert gold.equals(silver)
    assert silver in {gold}


def test_key_with_ages_match_low() -> None:
    silver = LookupTableKey(["foo", "bar"], 0, None)
    gold = LookupTableKey(["foo", "bar"], IntRange(0, 30), None)
    assert silver.equals(gold)
    assert gold.equals(silver)
    assert silver in {gold}


def test_key_correct_match() -> None:
    yellow = LookupTableKey(["foo", "bar"], 20, None)
    grey = LookupTableKey(["foo", "bar"], 50, None)
    gold = LookupTableKey(["foo", "bar"], IntRange(0, 30), None)
    platinum = LookupTableKey(["foo", "bar"], IntRange(31, 60), None)
    assert yellow.equals(gold)
    assert gold.equals(yellow)
    assert grey.equals(platinum)
    assert platinum.equals(grey)
    assert not grey.equals(gold)
    assert not yellow.equals(platinum)
    assert not gold.equals(platinum)
    assert not yellow.equals(grey)

    table = LookupTableMap()
    table.put(gold, [_option("gold")])
    table.put(platinum, [_option("platinum")])
    assert table.get(yellow)[0].transition == "gold"
    assert table.get(grey)[0].transition == "platinum"


def test_key_with_ages_no_match_age() -> None:
    silver = LookupTableKey(["foo", "bar"], 40, None)
    gold = LookupTableKey(["foo", "bar"], IntRange(0, 30), None)
    assert not silver.equals(gold)
    assert not gold.equals(silver)
    assert silver not in {gold}


def test_key_with_ages_no_match_other() -> None:
    silver = LookupTableKey(["foo", "bar"], 20, None)
    gold = LookupTableKey(["foo", "baz"], IntRange(0, 30), None)
    assert not silver.equals(gold)
    assert not gold.equals(silver)
    assert silver not in {gold}


def test_key_without_ages_match() -> None:
    silver = LookupTableKey(["foo", "bar"], None, None)
    gold = LookupTableKey(["foo", "bar"], None, None)
    assert silver.equals(gold)
    assert gold.equals(silver)
    assert silver in {gold}


def test_key_without_ages_no_match() -> None:
    silver = LookupTableKey(["foo", "bar"], None, None)
    gold = LookupTableKey(["foo", "baz"], None, None)
    assert not silver.equals(gold)
    assert not gold.equals(silver)
    assert silver not in {gold}


# --- LookupTableTransitionTest: scenarios ---------------------------------


@pytest.fixture()
def lookup_config() -> Iterator[None]:
    """LookupTableTransitionTest.setup: test lookup-table directory, and a
    clean static table cache (the Java test class resets via new JVM)."""
    previous = Config.get("generate.lookup_tables")
    Config.set("generate.lookup_tables", "java/src/test/resources/generic/lookup_tables/")
    LookupTableTransition.lookupTables.clear()
    PayerManager.load_no_insurance()
    yield
    Config.set("generate.lookup_tables", previous)
    LookupTableTransition.lookupTables.clear()


def _lookup_person(ethnicity: str, gender: str, state: str) -> Person:
    person = Person(0)
    person.attributes[Person.BIRTHDATE] = 0
    person.attributes[Person.ETHNICITY] = ethnicity
    person.attributes[Person.GENDER] = gender
    person.attributes[Person.STATE] = state
    return person


def _follow_fixture(fixture: str, person: Person, time: int) -> str:
    transition = build_transition("lookup_table", _fixture_state(fixture, "Determine_Condition"))
    return transition.follow(person, time)


@pytest.mark.parametrize(
    ("ethnicity", "gender", "state", "years", "expected"),
    [
        ("english", "F", "Massachusetts", 45, "Moderate_Lookuptablitis"),
        ("english", "F", "Massachusetts", 55, "Mild_Lookuptablitis"),
        ("english", "M", "Massachusetts", 55, "Extreme_Lookuptablitis"),
        ("irish", "M", "Massachusetts", 1, "Moderate_Lookuptablitis"),
        ("irish", "F", "Massachusetts", 53, "Moderate_Lookuptablitis"),
        ("italian", "M", "Arizona", 65, "Moderate_Lookuptablitis"),
        ("italian", "F", "Arizona", 15, "Extreme_Lookuptablitis"),
        ("spanish", "F", "Arizona", 15, "Extreme_Lookuptablitis"),
        ("english", "F", "Alaska", 15, "Extreme_Lookuptablitis"),
    ],
)
def test_lookuptable_scenarios(
    lookup_config: None,
    ethnicity: str,
    gender: str,
    state: str,
    years: int,
    expected: str,
) -> None:
    person = _lookup_person(ethnicity, gender, state)
    result = _follow_fixture(
        "lookuptable_test.json", person, Utilities.convert_time("years", years)
    )
    assert result == expected


@pytest.mark.parametrize(
    ("gender", "state", "time", "expected"),
    [
        ("M", "Massachusetts", 500, "Moderate_Lookuptablitis"),
        ("F", "Massachusetts", 500, "Mild_Lookuptablitis"),
        ("M", "New Hampshire", 500, "Extreme_Lookuptablitis"),
        ("M", "Massachusetts", 1500, "Extreme_Lookuptablitis"),
        ("F", "Massachusetts", 1500, "Moderate_Lookuptablitis"),
    ],
)
def test_lookuptable_time_range_scenarios(
    lookup_config: None, gender: str, state: str, time: int, expected: str
) -> None:
    person = _lookup_person("english", gender, state)
    result = _follow_fixture("lookuptable_timerangetest.json", person, time)
    assert result == expected


def test_invalid_csv_age_range(lookup_config: None) -> None:
    with pytest.raises(RuntimeError, match="Age Range must be in the form: 'ageLow-ageHigh'"):
        _follow_fixture(
            "lookuptable_agerangetest.json", _lookup_person("english", "F", "Massachusetts"), 0
        )


def test_json_to_csv_no_transition_match(lookup_config: None) -> None:
    with pytest.raises(RuntimeError, match="does not match a JSON state to transition to in CSV"):
        _follow_fixture(
            "lookuptable_nomatchcolumn.json", _lookup_person("english", "F", "Massachusetts"), 0
        )


@pytest.mark.parametrize(("flag", "expected"), [(True, "Yes"), (False, "No")])
def test_lookuptable_boolean_attribute_matches_java_to_string(
    tmp_path: Path, flag: bool, expected: str
) -> None:
    """Java: the key uses Object#toString, so a Boolean attribute is "true"/"false".

    Python's str(True) is "True", which matched no row and fell back to the
    default probabilities (found by the T28 end-to-end trace, vhd_*.csv tables).
    """
    (tmp_path / "flag_test.csv").write_text("flag,Yes,No\ntrue,1,0\nfalse,0,1\n", encoding="utf-8")
    previous = Config.get("generate.lookup_tables")
    Config.set("generate.lookup_tables", str(tmp_path) + "/")
    LookupTableTransition.lookupTables.clear()
    try:
        person = Person(0)
        person.attributes[Person.BIRTHDATE] = 0
        person.attributes["flag"] = flag
        transition = build_transition(
            "lookup_table",
            {
                "lookup_table_transition": [
                    {
                        "transition": "Yes",
                        "default_probability": 0,
                        "lookup_table_name": "flag_test.csv",
                    },
                    {
                        "transition": "No",
                        "default_probability": 1,
                        "lookup_table_name": "flag_test.csv",
                    },
                ]
            },
        )
        assert transition.follow(person, TIME_2021) == expected
    finally:
        Config.set("generate.lookup_tables", previous)
        LookupTableTransition.lookupTables.clear()
