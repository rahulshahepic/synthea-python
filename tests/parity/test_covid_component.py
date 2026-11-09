"""T24 component parity: CovidProbe with a createEncounter double.

Component form (AGENTS.md §4): every CovidProbe line — including all
200 per-person process runs, whose vaccinations call
`EncounterModule.createEncounter` (T22, still a stub) — runs with
`create_encounter_double` (tests/state_doubles.py, tests only)
standing in for that one collaborator. The double implements only
the Java method's state/RNG plumbing; everything else — the COVID
module, distributions, record, costs — is production code. Lines are
compared exactly against the CovidProbe golden, which was generated
by the real Java EncounterModule.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from pathlib import Path

import pytest

from synthea.modules.encounter_module import EncounterModule
from tests.covid_support import covid_run_lines, isolated_globals
from tests.state_doubles import create_encounter_double

pytestmark = pytest.mark.parity


@pytest.fixture(autouse=True)
def _create_encounter_double() -> Iterator[None]:
    # The double reads Provider's global registry; the Java probe ran
    # in a fresh JVM with it empty. isolated_globals gives the run a
    # fresh registry and restores the caller's afterwards (#84).
    # Save the raw class-dict descriptor: reading the attribute through
    # the class unwraps a staticmethod to a plain function, and putting
    # that back would leave create_encounter a plain function (the
    # skeleton signature test reads the descriptor itself).
    original = vars(EncounterModule)["create_encounter"]
    EncounterModule.create_encounter = staticmethod(create_encounter_double)  # type: ignore[method-assign]
    try:
        with isolated_globals():
            yield
    finally:
        EncounterModule.create_encounter = original  # type: ignore[method-assign]


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def test_covid_component_probe_runs(golden: Callable[[str], Path]) -> None:
    expected = _read_lines(golden("CovidProbe") / "run.txt")
    actual = covid_run_lines()
    assert actual == expected
