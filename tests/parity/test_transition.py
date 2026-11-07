"""Parity for Transition (T18).

Mirrors TransitionProbe case for case: every transition in
``resources/modules/**`` is built the way State builds it (via
tests.transition_support, which mirrors the Gson field filling), followed
with 25 scripted persons, and the result — a target state name, or the
``X`` category when the Java code throws — is compared exactly, line by
line, with the golden.

This is *integration* parity for the transition kinds themselves: real
Person (T09), real Logic (T17), real CoverageRecord/InsurancePlan (T15/T16)
and real TelemedicineConfig (T11) objects end to end, no doubles.
"""

from __future__ import annotations

import copy
import json
from collections.abc import Callable
from pathlib import Path

import pytest

from synthea.engine.transition import LookupTableTransition, Transition
from synthea.helpers.config import Config
from synthea.helpers.simple_csv import SimpleCSV
from synthea.helpers.utilities import Utilities
from synthea.resources import resource_path
from synthea.world.agents.payer_manager import PayerManager
from synthea.world.agents.person import Person
from tests.transition_support import (
    PRE_TIME,
    SEEDS,
    TIME,
    build_transition,
    script_definition_attributes,
    scripted_person,
    transition_kind,
)

pytestmark = pytest.mark.parity


def _follow_catching(transition: Transition, person: Person, time: int) -> str:
    try:
        return transition.follow(person, time)
    except Exception:
        return "X"


def _normalize(result: str) -> str:
    """Golden lines record X:<Java exception>; both-threw is the X category."""
    return "X" if result.startswith("X:") else result


def _module_files() -> list[tuple[str, Path]]:
    modules_dir = resource_path("modules")
    files = sorted(
        modules_dir.rglob("*.json"),
        key=lambda p: p.relative_to(modules_dir).as_posix(),
    )
    return [(p.relative_to(modules_dir).as_posix(), p) for p in files]


def test_transition_parity(golden: Callable[[str], Path]) -> None:
    # The Java probe runs in a fresh JVM: LookupTableTransition's static
    # table cache starts empty, so the probe's own constructions load
    # (and set `attributes` on) each table. Other tests in this process
    # may have loaded the tables already, leaving later constructions
    # with attributes unset; reset to the probe's conditions.
    LookupTableTransition.lookupTables.clear()
    PayerManager.load_no_insurance()
    golden_lines = (
        (golden("TransitionProbe") / "transitions.jsonl").read_text(encoding="utf-8").splitlines()
    )
    actual: list[str] = []
    followed_tables: set[str] = set()
    shared_persons: dict[int, Person] = {}

    for rel, path in _module_files():
        module = json.loads(path.read_text(encoding="utf-8"))
        states = module.get("states")
        if not isinstance(states, dict):
            continue
        for state_name, state in states.items():
            kind = transition_kind(state)
            if kind is None:
                continue
            prefix = f"{rel}|{state_name}|{kind}"
            # The probe scripts persons from a pristine copy of the state
            # taken before construction (the Gson Logic adapters mutate the
            # JSON they deserialize from); mirror that here.
            pristine_state = copy.deepcopy(state)
            try:
                transition = build_transition(kind, state)
            except Exception:
                actual.append(f"{prefix}|-1|ctor\tX")
                continue
            actual.append(f"{prefix}|-1|ctor\tOK")
            if kind == "lookup_table":
                _follow_lookup(actual, rel, state_name, transition, followed_tables)
            elif kind == "type_of_care":
                for seed in range(SEEDS):
                    person = scripted_person(seed)
                    person.coverage.set_plan_to_no_insurance(0)
                    person.coverage.set_plan_to_no_insurance(TIME + 1)
                    actual.append(
                        f"{rel}|{state_name}|type_of_care|{seed}|t2021\t"
                        + _follow_catching(transition, person, TIME)
                    )
                    pre_person = scripted_person(seed)
                    pre_person.coverage.set_plan_to_no_insurance(0)
                    pre_person.coverage.set_plan_to_no_insurance(TIME + 1)
                    actual.append(
                        f"{rel}|{state_name}|type_of_care|{seed}|t2019\t"
                        + _follow_catching(transition, pre_person, PRE_TIME)
                    )
            elif kind == "direct":
                # DirectTransition.follow ignores the person entirely; reuse
                # one scripted person per seed (the Java probe builds a fresh
                # one, which cannot change the result).
                for seed in range(SEEDS):
                    if seed not in shared_persons:
                        shared_persons[seed] = scripted_person(seed)
                    actual.append(
                        f"{prefix}|{seed}|main\t"
                        + _follow_catching(transition, shared_persons[seed], TIME)
                    )
            else:
                for seed in range(SEEDS):
                    person = scripted_person(seed)
                    script_definition_attributes(person, seed, pristine_state)
                    actual.append(
                        f"{prefix}|{seed}|main\t" + _follow_catching(transition, person, TIME)
                    )

    assert len(actual) == len(golden_lines), (
        f"case count differs: python {len(actual)} vs golden {len(golden_lines)}"
    )
    for i, (mine, gold) in enumerate(zip(actual, golden_lines, strict=True)):
        gold_case, _, gold_result = gold.partition("\t")
        assert mine.partition("\t")[0] == gold_case, f"case {i}: {mine} vs {gold}"
        assert _normalize(mine.partition("\t")[2]) == _normalize(gold_result), (
            f"case {i} ({gold_case}): python {mine.partition(chr(9))[2]!r} "
            f"vs golden {gold_result!r}"
        )


def _follow_lookup(
    actual: list[str],
    rel: str,
    state_name: str,
    transition: Transition,
    followed_tables: set[str],
) -> None:
    assert isinstance(transition, LookupTableTransition)
    table_name = transition.lookup_table_name
    if table_name in followed_tables:
        return  # a later instance shares the table but has null attributes
    followed_tables.add(table_name)
    file_name = str(Config.get("generate.lookup_tables")) + table_name
    csv = Utilities.read_resource(file_name, True, True)
    rows = SimpleCSV.parse(csv)
    headers = list(rows[0].keys())
    attribute_headers = headers[0 : len(headers) - len(transition.transitions)]

    from tests.transition_support import _epoch_millis

    for seed in range(SEEDS):
        row = rows[seed % len(rows)]
        person = scripted_person(seed)
        follow_time = TIME
        for header in attribute_headers:
            if header.lower() == "age":
                cell = row[header]
                low = int(cell[0 : cell.index("-")])
                person.attributes[Person.BIRTHDATE] = _epoch_millis(2021 - low, 1, 1)
            elif header.lower() == "time":
                follow_time = Utilities.parse_date_range(row[header]).minimum
            else:
                person.attributes[header] = row[header]
        actual.append(
            f"{rel}|{state_name}|lookup_table|{seed}|row\t"
            + _follow_catching(transition, person, follow_time)
        )

        def_person = scripted_person(seed)
        for header in attribute_headers:
            if header.lower() == "age":
                def_person.attributes[Person.BIRTHDATE] = _epoch_millis(2021 - 150, 1, 1)
            elif header.lower() != "time":
                def_person.attributes[header] = "ZZZ_NO_MATCH"
        actual.append(
            f"{rel}|{state_name}|lookup_table|{seed}|default\t"
            + _follow_catching(transition, def_person, TIME)
        )
