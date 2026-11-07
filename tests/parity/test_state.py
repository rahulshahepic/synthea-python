"""T20 integration parity: clinical States via StateProbe, real code.

Every StateProbe block whose module does not call
`EncounterModule.createEncounter` (T22 — still a stub, and not a
dependency #20 declares) runs here end to end with real objects,
each scenario wrapped in `tests.dependency_gate.run_or_pending`
with #20's declared dependencies (T13, T14, T19), and compared
exactly against the StateProbe golden. The encounter-dependent
blocks (94 modules, 1,880 blocks) are covered by the component form
in tests/parity/test_state_component.py, which uses a tests-only
`create_encounter_double`; they are counted exactly below so the
partition cannot silently grow or shrink.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from tests.dependency_gate import Pending, report_pending, run_or_pending
from tests.state_support import (
    ENCOUNTER_DEPENDENT_MODULES,
    SEEDS,
    blocks,
    probe_suppliers,
    run_block,
)

pytestmark = pytest.mark.parity

DEPENDENCIES = ("T13", "T14", "T19")
TOTAL_BLOCKS = 4840
# Blocks belonging to ENCOUNTER_DEPENDENT_MODULES (all 20 seeds of
# each): covered by the component form. 1,625 of them raise the T22
# stub today; the rest run stub-free but stay with their module.
ENCOUNTER_DEPENDENT_BLOCKS = 1880
INTEGRATION_BLOCKS = TOTAL_BLOCKS - ENCOUNTER_DEPENDENT_BLOCKS


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def test_state_probe_runs(golden: Callable[[str], Path]) -> None:
    expected = blocks(_read_lines(golden("StateProbe") / "run.txt"))
    assert len(expected) == TOTAL_BLOCKS
    gated = [key for key in expected if key[0] in ENCOUNTER_DEPENDENT_MODULES]
    assert len(gated) == ENCOUNTER_DEPENDENT_BLOCKS

    results: list[list[str] | Pending] = []
    keys: list[tuple[str, str]] = []
    for supplier in probe_suppliers():
        if supplier.path in ENCOUNTER_DEPENDENT_MODULES:
            continue
        for seed in range(SEEDS):
            keys.append((supplier.path, str(seed)))
            results.append(
                run_or_pending(
                    lambda supplier=supplier, seed=seed: run_block(supplier, seed),
                    DEPENDENCIES,
                )
            )
    assert len(results) == INTEGRATION_BLOCKS
    mismatches = [
        key
        for key, result in zip(keys, results, strict=True)
        if not isinstance(result, Pending) and result != expected[key]
    ]
    assert not mismatches, f"{len(mismatches)} blocks differ, first: {mismatches[:5]}"
    report_pending("StateProbe integration", results)
