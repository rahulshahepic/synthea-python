"""Sanity check that the Java→golden pipeline produced output in CI."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest


@pytest.mark.parity
def test_java_random_golden_exists(golden: Callable[[str], Path]) -> None:
    assert (golden("JavaRandomProbe") / "random.jsonl").stat().st_size > 0


@pytest.mark.parity
def test_e2e_scenario_golden_exists(golden: Callable[[str], Path]) -> None:
    csv_dir = golden("scenarios") / "ma_seed42_p10" / "csv"
    assert (csv_dir / "patients.csv").stat().st_size > 0
