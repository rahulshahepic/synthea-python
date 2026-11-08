"""T24 integration parity: CovidProbe, real code end to end.

The direct sections (constants, AgeRange, EUA table, probabilities,
shot-time and vaccine sampling, LateAdopterModel, eligibility and
decideOnShot) call no T22 code and are compared exactly. Each
per-person process run is wrapped in `tests.dependency_gate.run_or_pending`
with #24's declared dependency (T22): a run that reaches
`EncounterModule.createEncounter` (still a stub) is pending until
T22 merges, and every other run must match the golden exactly.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from tests.covid_support import (
    SEEDS,
    direct_lines,
    reset_covid_statics,
    run_person,
    setup_process_runtime,
)
from tests.dependency_gate import Pending, report_pending, run_or_pending

pytestmark = pytest.mark.parity

DEPENDENCIES = ("T22",)
PROCESS_PREFIXES = {"T", "F", "I", "P"}


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def _split(lines: list[str]) -> tuple[list[str], dict[int, list[str]]]:
    direct: list[str] = []
    per_seed: dict[int, list[str]] = {}
    for line in lines:
        prefix = line.split("|", 1)[0]
        if prefix in PROCESS_PREFIXES:
            seed = int(line.split("|", 2)[1])
            per_seed.setdefault(seed, []).append(line)
        else:
            direct.append(line)
    return direct, per_seed


def test_covid_probe_runs(golden: Callable[[str], Path]) -> None:
    expected_direct, expected_per_seed = _split(_read_lines(golden("CovidProbe") / "run.txt"))
    assert len(expected_per_seed) == SEEDS

    reset_covid_statics()
    actual_direct, module = direct_lines()
    assert actual_direct == expected_direct

    setup_process_runtime()
    results = [
        run_or_pending(lambda seed=seed: run_person(module, seed), DEPENDENCIES)
        for seed in range(SEEDS)
    ]
    mismatches = [
        seed
        for seed, result in enumerate(results)
        if not isinstance(result, Pending) and result != expected_per_seed[seed]
    ]
    assert not mismatches, f"{len(mismatches)} process runs differ, first: {mismatches[:5]}"
    report_pending("CovidProbe process runs", results)
