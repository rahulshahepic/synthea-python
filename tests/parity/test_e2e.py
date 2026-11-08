"""End-to-end CSV parity (T28): the Python CLI against the Java App's scenarios.

For every ``parity/scenarios/*.args`` file, run the Python CLI with the same
arguments into a temp dir (with ``--exporter.baseDirectory`` appended, exactly
as ``parity/gen_golden.sh`` does for the Java run) and diff every CSV in
``csv/`` against ``parity/golden/scenarios/<name>/csv/`` byte-for-byte.

The scenarios exercise the Generator (T27), which is a declared dependency of
this task: until T27 merges, a scenario that stops at a genuine T27 stub is
reported pending by the dependency gate, never skipped or dropped.
"""

from __future__ import annotations

import os
import tempfile
from collections.abc import Callable
from pathlib import Path

import pytest

from synthea.cli import App
from synthea.helpers.config import Config
from tests.dependency_gate import Pending, report_pending, run_or_pending

REPO_ROOT = Path(__file__).resolve().parents[2]
SCENARIOS_DIR = REPO_ROOT / "parity" / "scenarios"
DEPENDENCIES = ("T26", "T27")


def _scenario_args(path: Path) -> list[str]:
    """One argument per line; ``#`` comments and blank lines are dropped."""
    args = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            args.append(stripped)
    return args


def _csv_bytes(root: Path) -> dict[str, bytes]:
    csv_dir = root / "csv"
    if not csv_dir.is_dir():
        return {}
    return {
        path.relative_to(csv_dir).as_posix(): path.read_bytes()
        for path in sorted(csv_dir.rglob("*.csv"))
    }


def _run_scenario(name: str, golden_root: Path) -> None:
    """Run one scenario end to end and require byte-identical CSVs."""
    args = _scenario_args(SCENARIOS_DIR / f"{name}.args")
    saved_properties = dict(Config.properties)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            App.main([*args, f"--exporter.baseDirectory={out_dir}/"])
            actual = _csv_bytes(out_dir)
    finally:
        Config.properties.clear()
        Config.properties.update(saved_properties)
    expected = _csv_bytes(golden_root / name)
    assert expected, f"no golden CSVs for scenario {name}"
    assert sorted(actual) == sorted(expected), (
        f"scenario {name}: CSV file sets differ: "
        f"only-python={sorted(set(actual) - set(expected))}, "
        f"only-golden={sorted(set(expected) - set(actual))}"
    )
    for filename in sorted(expected):
        if actual[filename] != expected[filename]:
            actual_lines = actual[filename].splitlines()
            expected_lines = expected[filename].splitlines()
            first_diff = next(
                (
                    i
                    for i, (a, e) in enumerate(zip(actual_lines, expected_lines, strict=False))
                    if a != e
                ),
                min(len(actual_lines), len(expected_lines)),
            )
            actual_line = actual_lines[first_diff] if first_diff < len(actual_lines) else b"<eof>"
            golden_line = (
                expected_lines[first_diff] if first_diff < len(expected_lines) else b"<eof>"
            )
            raise AssertionError(
                f"scenario {name}: {filename} differs at line {first_diff + 1}: "
                f"python={actual_line!r} golden={golden_line!r}"
            )


@pytest.mark.parity
def test_e2e_scenarios(golden: Callable[[str], Path]) -> None:
    """Every scenario in parity/scenarios matches its golden CSVs exactly."""
    golden_root = golden("scenarios")
    names = sorted(path.stem for path in SCENARIOS_DIR.glob("*.args"))
    assert names, "no scenarios found"
    if os.environ.get("PARITY_REQUIRED") == "1":
        for name in names:
            assert (golden_root / name / "csv").is_dir(), f"golden CSVs missing for {name}"
    results = [
        run_or_pending(lambda name=name: _run_scenario(name, golden_root), DEPENDENCIES)
        for name in names
    ]
    for name, result in zip(names, results, strict=True):
        if not isinstance(result, Pending):
            assert result is None, f"scenario {name} returned unexpectedly"
    report_pending("T28 end-to-end scenarios", results)
