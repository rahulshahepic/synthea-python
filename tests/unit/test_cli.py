"""Unit tests for the CLI port (T28, Java: App).

The Generator and its options are T27's; here they are replaced with test
doubles in the ``synthea.cli`` namespace only, so the argument parsing,
config handling and validation can be tested without the generator.
Production code always constructs the real classes.
"""

from __future__ import annotations

import time
from pathlib import Path
from types import SimpleNamespace
from typing import ClassVar

import pytest

import synthea.cli as cli
from synthea.cli import App
from synthea.helpers.config import Config


class _FakeOptions:
    """Stand-in for GeneratorOptions (T27) with the fields App touches."""

    def __init__(self) -> None:
        self.population = 1
        self.thread_pool_size = -1
        self.reference_time = 0
        self.end_time = 0
        self.seed = 0
        self.clinician_seed = 0
        self.single_person_seed: int | None = None
        self.overflow = True
        self.gender: str | None = None
        self.age_specified = False
        self.min_age = 0
        self.max_age = 140
        self.city: str | None = None
        self.state: str | None = None
        self.enabled_modules: list[str] | None = None


class _FakeExportOptions:
    def __init__(self) -> None:
        self.years_of_history = 10
        self.terminology_service = False


class _FakeGenerator:
    instances: ClassVar[list[_FakeGenerator]] = []

    def __init__(self, options: _FakeOptions, export_options: _FakeExportOptions) -> None:
        self.options = options
        self.export_options = export_options
        self.ran = False
        _FakeGenerator.instances.append(self)

    def run(self) -> None:
        self.ran = True


@pytest.fixture(autouse=True)
def _patched_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    _FakeGenerator.instances = []
    monkeypatch.setattr(cli, "GeneratorOptions", _FakeOptions)
    monkeypatch.setattr(cli, "ExporterRuntimeOptions", _FakeExportOptions)
    monkeypatch.setattr(cli, "Generator", _FakeGenerator)
    saved = dict(Config.properties)
    yield
    Config.properties.clear()
    Config.properties.update(saved)


def test_usage_prints_first_line(capsys: pytest.CaptureFixture[str]) -> None:
    App.usage()
    assert capsys.readouterr().out.splitlines()[0] == "Usage: run_synthea [options] [state [city]]"


def test_parse_yyyymmdd_exact() -> None:
    assert cli._parse_yyyymmdd("20250101") == 1735689600000


def test_parse_yyyymmdd_lenient_rollover() -> None:
    # Java SimpleDateFormat is lenient: month 13 rolls into the next year.
    assert cli._parse_yyyymmdd("20251301") == 1767225600000


def test_main_parses_args_and_runs_generator() -> None:
    App.main(
        [
            "-s",
            "42",
            "-cs",
            "7",
            "-p",
            "3",
            "-r",
            "20250101",
            "-e",
            "20250101",
            "Massachusetts",
        ]
    )
    assert len(_FakeGenerator.instances) == 1
    generator = _FakeGenerator.instances[0]
    assert generator.ran
    options = generator.options
    assert options.seed == 42
    assert options.clinician_seed == 7
    assert options.population == 3
    assert options.reference_time == 1735689600000
    assert options.end_time == 1735689600000
    assert options.state == "Massachusetts"
    assert Config.get("generate.default_population") == "3"


def test_main_state_and_city() -> None:
    App.main(["Washington", "Seattle"])
    assert _FakeGenerator.instances[0].options.state == "Washington"
    assert _FakeGenerator.instances[0].options.city == "Seattle"


def test_main_invalid_gender_does_not_run(capsys: pytest.CaptureFixture[str]) -> None:
    App.main(["-g", "X"])
    assert _FakeGenerator.instances == []
    assert "Usage: run_synthea" in capsys.readouterr().out


def test_main_help_returns_without_running(capsys: pytest.CaptureFixture[str]) -> None:
    App.main(["-h"])
    assert _FakeGenerator.instances == []
    assert "Usage: run_synthea" in capsys.readouterr().out


@pytest.mark.parametrize(
    "args",
    [
        ["-t", "5"],
        ["-u", "snapshot.json"],
        ["-fm", "mapping.json"],
    ],
)
def test_out_of_scope_options_raise(args: list[str]) -> None:
    with pytest.raises(NotImplementedError, match="out of scope"):
        App.main(args)


def test_out_of_scope_i_with_existing_file(tmp_path: Path) -> None:
    snapshot = tmp_path / "snapshot.json"
    snapshot.write_text("{}", encoding="utf-8")
    with pytest.raises(NotImplementedError, match="out of scope"):
        App.main(["-i", str(snapshot)])


def test_out_of_scope_f_with_existing_file(tmp_path: Path) -> None:
    fixed = tmp_path / "fixed.json"
    fixed.write_text("{}", encoding="utf-8")
    with pytest.raises(NotImplementedError, match="out of scope"):
        App.main(["-f", str(fixed)])


def test_out_of_scope_k_with_resource_module() -> None:
    with pytest.raises(NotImplementedError, match="out of scope"):
        App.main(["-k", "keep_diabetes.json"])


def test_validate_config_future_end_time() -> None:
    future = SimpleNamespace(end_time=int(time.time() * 1000) + 20 * 366 * 86_400_000)
    assert App.validate_config(future, False) is False  # type: ignore[arg-type]
    assert App.validate_config(future, True) is True  # type: ignore[arg-type]


def test_validate_config_past_end_time() -> None:
    past = SimpleNamespace(end_time=1735689600000)
    assert App.validate_config(past, False) is True  # type: ignore[arg-type]


def test_fail_if_physiology_enabled() -> None:
    App.fail_if_physiology_enabled("-i")  # disabled by default: no raise
    Config.set("physiology.generators.enabled", "true")
    with pytest.raises(ValueError, match="physiology"):
        App.fail_if_physiology_enabled("-i")
