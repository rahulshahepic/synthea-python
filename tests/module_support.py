"""Shared support for the T19 Module tests.

Mirrors ``ModuleProbe`` exactly: the same scripted persons, the same
module-run loop (7-day steps, at most 200 process calls), the same
canonical attribute formatting (Java ``Double.toString`` /
``Boolean.toString`` / simple class names), and the same synthetic
local modules for the CallSubmodule / Death / Delay-rewind scenarios.
Keep this file and the probe in sync.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from synthea.engine.module import Module, ModuleSupplier
from synthea.engine.state import State
from synthea.engine.transition import (
    ComplexTransition,
    ConditionalTransition,
    DirectTransition,
    DistributedTransition,
    LookupTableTransition,
    Transition,
    TypeOfCareTransition,
)
from synthea.helpers.time_series_data import TimeSeriesData
from synthea.javacompat.numbers import double_to_string
from synthea.world.agents.person import Person
from synthea.world.concepts.vital_sign import VitalSign

TIME = 1609459200000  # 2021-01-01T00:00:00Z
WEEK = 7 * 24 * 3600 * 1000
SEEDS = 25
MAX_STEPS = 200
CONTROL_FLOW = {"Initial", "Terminal", "Simple", "Guard", "Delay", "SetAttribute", "Counter"}

# Python exception types -> the Java exception simple name the probe
# dumps for the corresponding failure (only used on the error path).
_JAVA_EXCEPTION_NAMES = {
    "RuntimeError": "RuntimeException",
    "TypeError": "NullPointerException",
    "ValueError": "IllegalArgumentException",
    "IndexError": "IndexOutOfBoundsException",
    "KeyError": "NullPointerException",
}


def _bool(value: bool) -> str:
    return "true" if value else "false"


def scripted_person(seed: int) -> Person:
    """Mirror of ModuleProbe.scriptedPerson — identical script."""
    person = Person(seed)
    birthdate = int(datetime(2021 - (1 + (seed % 80)), 1, 1, tzinfo=UTC).timestamp() * 1000)
    person.attributes[Person.BIRTHDATE] = birthdate
    person.attributes[Person.GENDER] = "M" if seed % 2 == 0 else "F"
    person.attributes["race"] = "White"
    person.attributes[Person.INCOME] = 10000 * (seed % 12)
    person.set_vital_sign(VitalSign.BMI, 18.0 + (seed % 25))
    return person


def canonical_value(value: object) -> str:
    """Mirror of ModuleProbe.canonicalValue."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return _bool(value)
    if isinstance(value, float):
        return double_to_string(value)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return value
    if isinstance(value, TimeSeriesData):
        return "TS[" + ",".join(double_to_string(v) for v in value.get_values()) + "]"
    if isinstance(value, list):
        return "List"
    if type(value).__name__ == "date":
        return "LocalDate"
    return type(value).__name__


def _targets(transition: Transition | None) -> str:
    """Mirror of ModuleProbe.transitionTargets."""
    if transition is None:
        return "none"
    kind = type(transition).__name__
    targets: list[str] = []
    if isinstance(transition, DirectTransition):
        targets.append(transition.transition)
    elif isinstance(
        transition, (DistributedTransition, ConditionalTransition, LookupTableTransition)
    ):
        targets.extend(option.transition for option in transition.transitions)
    elif isinstance(transition, ComplexTransition):
        for option in transition.transitions:
            if option.transition is not None:
                targets.append(option.transition)
            else:
                assert option.distributions is not None
                targets.extend(dist.transition for dist in option.distributions)
    elif isinstance(transition, TypeOfCareTransition):
        targets.extend([transition.ambulatory, transition.emergency, transition.telemedicine])
    else:
        targets.append("?" + kind)
    return kind + ":" + ",".join(targets)


def modules_lines() -> list[str]:
    """Mirror of ModuleProbe part 1 (modules.txt)."""
    lines: list[str] = []
    for supplier in Module.get_module_suppliers():
        module = supplier.get()
        lines.append(
            f"S|{supplier.path}|core={_bool(supplier.core)}|submodule={_bool(supplier.submodule)}"
        )
        remarks = "null" if module.remarks is None else str(len(module.remarks))
        lines.append(f"M|{module.name}|submodule={_bool(module.submodule)}|remarks={remarks}")
        for state_name in sorted(module.get_state_names()):
            state = module.get_state(state_name)
            assert state is not None
            lines.append(f"ST|{state_name}|{type(state).__name__}|{_targets(state._transition)}")
    return lines


def run_one(lines: list[str], tag: str, path: str, supplier: ModuleSupplier, seed: int) -> None:
    """Mirror of ModuleProbe.runOne."""
    person = scripted_person(seed)
    module = supplier.get()
    time = TIME
    completed = False
    steps = 0
    try:
        while steps < MAX_STEPS:
            completed = module.process(person, time)
            steps += 1
            if completed:
                break
            time += WEEK
    except Exception as e:  # Java: catch (RuntimeException)
        java_name = _JAVA_EXCEPTION_NAMES.get(type(e).__name__, type(e).__name__)
        lines.append(f"{tag}|{path}|{seed}|ERROR|{java_name}")
        return
    lines.append(f"{tag}|{path}|{seed}|completed={_bool(completed)}|steps={steps}")
    if person.history is not None:
        for i, state in enumerate(person.history):
            entered = "null" if state.entered is None else str(state.entered)
            exited = "null" if state.exited is None else str(state.exited)
            lines.append(f"H|{i}|{state.name}|{entered}|{exited}")
    for key in sorted(person.attributes.keys()):
        lines.append(f"A|{key}|{canonical_value(person.attributes.get(key))}")


def run_lines() -> list[str]:
    """Mirror of ModuleProbe part 2 (run.txt)."""
    lines: list[str] = []
    for supplier in Module.get_module_suppliers():
        if supplier.core:
            continue
        probe = supplier.get()
        state_names = probe.get_state_names()
        if not state_names:
            continue
        control_flow_only = all(
            type(cast(State, probe.get_state(name))).__name__ in CONTROL_FLOW
            for name in state_names
        )
        if not control_flow_only:
            continue
        for seed in range(SEEDS):
            run_one(lines, "RUN", supplier.path, supplier, seed)
    return lines


CHILD_MODULE: dict[str, object] = {
    "name": "child",
    "states": {
        "Initial": {"type": "Initial", "direct_transition": "Mark"},
        "Mark": {
            "type": "SetAttribute",
            "attribute": "child_ran",
            "value": "yes",
            "direct_transition": "Count",
        },
        "Count": {
            "type": "Counter",
            "attribute": "child_count",
            "action": "increment",
            "direct_transition": "Done",
        },
        "Done": {"type": "Terminal"},
    },
}

PARENT_MODULE: dict[str, object] = {
    "name": "parent",
    "states": {
        "Initial": {"type": "Initial", "direct_transition": "CallChild"},
        "CallChild": {
            "type": "CallSubmodule",
            "submodule": "sub/child",
            "direct_transition": "Die",
        },
        "Die": {
            "type": "Death",
            "codes": [{"system": "SNOMED-CT", "code": "44054006", "display": "Diabetes"}],
            "direct_transition": "Terminal",
        },
        "Terminal": {"type": "Terminal"},
    },
}

DELAYER_MODULE: dict[str, object] = {
    "name": "delayer",
    "states": {
        "Initial": {"type": "Initial", "direct_transition": "Wait"},
        "Wait": {
            "type": "Delay",
            "exact": {"quantity": 10, "unit": "days"},
            "direct_transition": "Terminal",
        },
        "Terminal": {"type": "Terminal"},
    },
}


def write_synthetic_modules(directory: Path) -> None:
    """Mirror of ModuleProbe.writeSyntheticModules."""
    (directory / "sub").mkdir(parents=True, exist_ok=True)
    (directory / "sub" / "child.json").write_text(json.dumps(CHILD_MODULE), encoding="utf-8")
    (directory / "parent.json").write_text(json.dumps(PARENT_MODULE), encoding="utf-8")
    (directory / "delayer.json").write_text(json.dumps(DELAYER_MODULE), encoding="utf-8")


def synthetic_lines(directory: Path) -> list[str]:
    """Mirror of ModuleProbe part 3 (synthetic.txt). The added registry
    entries are removed again afterwards so other tests in the same
    process still see the pristine registry."""
    write_synthetic_modules(directory)
    Module.add_modules(directory)
    lines: list[str] = []
    try:
        suppliers = {s.path: s for s in Module.get_module_suppliers()}
        for path in ("delayer", "parent"):
            for seed in range(5):
                run_one(lines, "SYN", path, suppliers[path], seed)
    finally:
        registry = Module._registry()
        for key in ("delayer", "parent", "sub/child"):
            registry.pop(key, None)
    return lines
