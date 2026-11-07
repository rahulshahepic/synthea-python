"""T19 parity tests: Module loading/processing + control-flow States.

Compares the Python port against ModuleProbe goldens, exactly:
* modules.txt — every registered module: name, states, state types and
  transition targets;
* run.txt — the 10 modules that only use control-flow states, run for
  25 scripted persons each: completion, state histories and attribute
  snapshots;
* synthetic.txt — local modules exercising CallSubmodule (nested
  submodule history merging), Death and Delay time-rewinding.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from tests.module_support import modules_lines, run_lines, synthetic_lines

pytestmark = pytest.mark.parity


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def test_module_registry_and_states(golden: Callable[[str], Path]) -> None:
    expected = _read_lines(golden("ModuleProbe") / "modules.txt")
    assert modules_lines() == expected


def test_control_flow_module_runs(golden: Callable[[str], Path]) -> None:
    expected = _read_lines(golden("ModuleProbe") / "run.txt")
    assert run_lines() == expected


def test_synthetic_modules(golden: Callable[[str], Path], tmp_path: Path) -> None:
    expected = _read_lines(golden("ModuleProbe") / "synthetic.txt")
    assert synthetic_lines(tmp_path) == expected
