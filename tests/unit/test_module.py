"""Unit tests for Module (T19), ported from the upstream JUnit
ModuleTest (java/src/test/java/org/mitre/synthea/engine/ModuleTest.java).

Only the tests that exercise T19 scope (registry, loading, GMF version
gate, local module folders) are ported here; ModuleTest.targetEncounters
drives Encounter states (T20) and is listed as skipped in the PR body.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from synthea.engine.module import Module

GENERIC = Path(__file__).resolve().parents[2] / "java" / "src" / "test" / "resources" / "generic"


def _fixture(filename: str) -> Module:
    """Mirror of TestHelper.getFixture: parse + construct, no overrides."""
    definition = json.loads((GENERIC / filename).read_text(encoding="utf-8"))
    return Module(definition, submodule=False)


def test_get_modules() -> None:
    """Java: ModuleTest#getModules — the registry loads and core modules exist."""
    modules = Module.get_modules()
    # Java prints "Scanned 90 modules and 157 submodules" at load:
    # 85 JSON modules + 5 core shells in the port's registry.
    assert len(modules) >= 90
    names = {module.name for module in modules}
    # Core (hand-written Java) modules are present as shells in the port.
    assert "Lifecycle" in names
    assert "Cardiovascular Disease" in names


def test_all_modules_must_be_named() -> None:
    """Java: ModuleTest#allModulesMustBeNamed."""
    for module in Module.get_modules():
        assert module.name is not None and module.name != ""


def test_get_modules_in_predictable_order() -> None:
    """Java: ModuleTest#getModulesInPredictableOrder — TreeMap ordering
    makes repeated calls return the same sequence."""
    first = [module.name for module in Module.get_modules()]
    second = [module.name for module in Module.get_modules()]
    assert first == second


def test_get_module_by_path() -> None:
    """Java: ModuleTest#getModuleByPath."""
    module = Module.get_module_by_path("appendicitis")
    assert module is not None
    assert module.name == "Appendicitis Module"


def test_get_module_by_path_missing() -> None:
    """Java: ModuleTest#getModuleByPath_missingModule."""
    assert Module.get_module_by_path("this/module/does/not/exist") is None


def test_relative_path() -> None:
    """Java: Module.relativePath strips the folder and .json suffix."""
    folder = Path("/tmp/modules")
    assert Module.relative_path(folder / "a" / "b.json", folder) == "a/b"
    assert Module.relative_path(folder / "top.json", folder) == "top"


def test_reject_modules_from_future_versions() -> None:
    """Java: ModuleTest#rejectModulesFromFutureVersions — a module whose
    gmf_version exceeds the known GMF version is rejected at load."""
    definition = {
        "name": "future",
        "gmf_version": Module.GMF_VERSION + 1.0,
        "states": {
            "Initial": {"type": "Initial", "direct_transition": "Terminal"},
            "Terminal": {"type": "Terminal"},
        },
    }
    with pytest.raises(RuntimeError):
        Module(definition, submodule=False)


def test_state_without_transition_rejected() -> None:
    """Java: StateTest#stateMustHaveTransition lives here too: building a
    module whose non-terminal state has no transition raises."""
    with pytest.raises(RuntimeError, match="has no transition"):
        _fixture("state_without_transition.json")


def test_add_local_modules(tmp_path: Path) -> None:
    """Java: ModuleTest#addLocalModules — a folder of local module JSON
    becomes loadable by path; the registry entries are removed again so
    other tests see the pristine registry."""
    (tmp_path / "localmod.json").write_text(
        json.dumps(
            {
                "name": "localmod",
                "states": {
                    "Initial": {"type": "Initial", "direct_transition": "Terminal"},
                    "Terminal": {"type": "Terminal"},
                },
            }
        ),
        encoding="utf-8",
    )
    try:
        Module.add_modules(tmp_path)
        module = Module.get_module_by_path("localmod")
        assert module is not None
        assert module.name == "localmod Module"
    finally:
        Module._registry().pop("localmod", None)


def _contains(superset: list[Module], subset: list[Module]) -> bool:
    """Java ModuleTest.contains: manual comparison, since Modules are
    clones and not identical objects."""
    for subset_module in subset:
        if not any(
            superset_module.name == subset_module.name
            and superset_module.submodule == subset_module.submodule
            and superset_module.remarks == subset_module.remarks
            for superset_module in superset
        ):
            return False
    return True


def test_get_modules_with_predicate() -> None:
    """Java: ModuleTest#getModules (predicate half) — filtering by path
    substring keeps Dermatitis, drops COPD."""
    all_modules = Module.get_modules()
    some_modules = Module.get_modules(lambda path: "ti" in path)
    assert _contains(all_modules, some_modules)
    assert not _contains(some_modules, all_modules)
    assert len(all_modules) > len(some_modules) > 0
    assert any("COPD" in (m.name or "") for m in all_modules)
    assert any("Dermatitis" in (m.name or "") for m in some_modules)
    assert not any("COPD" in (m.name or "") for m in some_modules)


def test_reject_modules_with_bad_distributions() -> None:
    """Java: ModuleTest#rejectModulesWithBadDistributions."""
    resources = GENERIC.parent / "busted_distribution" / "module_with_bad_distribution.json"
    definition = json.loads(resources.read_text(encoding="utf-8"))
    with pytest.raises(RuntimeError) as excinfo:
        Module(definition, submodule=False)
    assert str(excinfo.value).startswith("State 2_Second_Delay contains an invalid distribution")


def test_get_module_by_path_bad_module() -> None:
    """Java: ModuleTest#getModuleByPath_badModule — a loader fault is
    rethrown as RuntimeError with the fault as its cause, and restoring
    the supplier makes the path loadable again.

    Adaptation: the fault is injected into the existing "copd" supplier
    (the Java original's "bad_module" restoration relies on JUnit test
    ordering against addLocalModules)."""
    from synthea.engine.module import ModuleSupplier

    registry = Module._registry()
    fault = OSError("Deliberate failure")
    original = registry["copd"]

    def faulty_loader() -> Module:
        raise fault

    registry["copd"] = ModuleSupplier(False, "copd", faulty_loader)
    try:
        with pytest.raises(RuntimeError) as excinfo:
            Module.get_module_by_path("copd")
        assert excinfo.value.__cause__ is fault
    finally:
        registry["copd"] = original
    assert Module.get_module_by_path("copd") is not None


def test_apply_overrides() -> None:
    """Java: Module#applyOverrides (no direct JUnit test; behaviour from
    the Java source: only the named module's file is rewritten, values
    become doubles)."""
    json_string = json.dumps({"name": "x", "states": {"S": {"type": "Simple", "probability": 1}}})
    overrides = {"x.json::$.states.S.probability": "0.25", "other.json::$.a": "1"}
    result = json.loads(Module.apply_overrides(json_string, overrides, "x.json"))
    assert result["states"]["S"]["probability"] == 0.25
    assert "a" not in result
