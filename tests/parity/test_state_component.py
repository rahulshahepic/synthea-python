"""T20 component parity: StateProbe with a createEncounter double.

Component form (AGENTS.md §4): every StateProbe block — all 4,840
(module, seed) runs, including the 1,625 whose modules call
`EncounterModule.createEncounter` (T22, still a stub) — runs with
`create_encounter_double` (tests/state_doubles.py, tests only)
standing in for that one collaborator. The double implements only
the Java method's state/RNG plumbing (reserve the encounter slot,
start the encounter on the real HealthRecord, attach the code,
assign a real provider and clinician); everything else — states,
transitions, record, costs — is production code. Blocks are
compared exactly against the StateProbe golden, which was generated
by the real Java EncounterModule: the double is faithful wherever
the probe output can observe it.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from pathlib import Path

import pytest

from synthea.modules.encounter_module import EncounterModule
from synthea.world.agents.provider import Provider
from tests.state_doubles import create_encounter_double
from tests.state_support import blocks, state_run_lines

pytestmark = pytest.mark.parity


@pytest.fixture(autouse=True)
def _create_encounter_double() -> Iterator[None]:
    # The double reads Provider's global registry; the Java probe ran
    # in a fresh JVM with it empty. Other parity tests (test_provider)
    # leave it loaded, so clear it for the run and again on teardown.
    Provider.clear()
    original = EncounterModule.create_encounter
    EncounterModule.create_encounter = staticmethod(create_encounter_double)  # type: ignore[method-assign]
    try:
        yield
    finally:
        EncounterModule.create_encounter = original  # type: ignore[method-assign]
        Provider.clear()


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def test_state_component_probe_runs(golden: Callable[[str], Path]) -> None:
    expected = blocks(_read_lines(golden("StateProbe") / "run.txt"))
    actual = blocks(state_run_lines())
    assert set(actual.keys()) == set(expected.keys())
    mismatches = [key for key, block in expected.items() if actual[key] != block]
    assert not mismatches, f"{len(mismatches)} blocks differ, first: {mismatches[:5]}"
