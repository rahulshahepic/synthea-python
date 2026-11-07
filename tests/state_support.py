"""Support for the T20 StateProbe parity comparison.

Mirrors parity/probes/org/synthea/parity/probes/StateProbe.java: every
top-level JSON module run for 20 scripted persons, with the outcome,
state history, canonical attributes, and a canonical health-record
summary (present entries, encounter count, symptom values) dumped
per person.
"""

from __future__ import annotations

from synthea.engine.module import Module, ModuleSupplier
from synthea.world.agents.person import Person
from tests.module_support import (
    _JAVA_EXCEPTION_NAMES,
    TIME,
    WEEK,
    _bool,
    canonical_value,
    scripted_person,
)

SEEDS = 20
MAX_STEPS = 200


def _run_one(lines: list[str], tag: str, path: str, supplier: ModuleSupplier, seed: int) -> None:
    """Mirror of StateProbe.runOne."""
    person: Person = scripted_person(seed)
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
    lines.append(f"E|{len(person.record.encounters)}")
    for key in sorted(person.record.present.keys()):
        entry = person.record.present[key]
        codes = ";".join(f"{c.system}:{c.code}:{c.display}" for c in entry.codes)
        name = "null" if entry.name is None else entry.name
        lines.append(f"R|{key}|{entry.type}|{name}|{entry.start}|{entry.stop}|{codes}")
    for symptom in sorted(person.get_symptoms()):
        lines.append(f"Y|{symptom}|{person.get_symptom(symptom)}")


def state_run_lines() -> list[str]:
    """Mirror of StateProbe.main (run.txt)."""
    lines: list[str] = []
    for supplier in Module.get_module_suppliers():
        if supplier.core:
            continue
        probe = supplier.get()
        if not probe.get_state_names():
            continue
        for seed in range(SEEDS):
            _run_one(lines, "RUN", supplier.path, supplier, seed)
    return lines
