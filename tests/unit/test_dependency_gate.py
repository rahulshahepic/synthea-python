"""The integration gate in tests/dependency_gate.py accepts only genuine pending stubs."""

from __future__ import annotations

import importlib
import inspect
import warnings

import pytest

from tests.dependency_gate import (
    Pending,
    PendingIntegrationWarning,
    pending_stubs,
    pending_tasks,
    port_map,
    report_pending,
    run_or_pending,
)


def _pending_init_stubs() -> list[tuple[str, type]]:
    """(owner task, class) for single-owner classes whose __init__ is still a T04 stub."""
    found = []
    for entry in port_map():
        owners = list(entry["owners"])  # type: ignore[call-overload]
        python = str(entry["python"])
        if len(owners) != 1 or owners[0] not in pending_tasks():
            continue
        names = {name for name, *_ in pending_stubs(python)}
        if "__init__" not in names:
            continue
        module = importlib.import_module(
            python.removeprefix("src/").removesuffix(".py").replace("/", ".")
        )
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ == module.__name__ and "__init__" in vars(cls):
                found.append((owners[0], cls))
                break
    return found


def _call_init(cls: type) -> object:
    obj = cls.__new__(cls)
    params = list(inspect.signature(cls.__init__).parameters)[1:]
    return cls.__init__(obj, *[None] * len(params))  # type: ignore[misc]


def test_pending_tasks_are_backed_by_real_stubs() -> None:
    for task in pending_tasks():
        assert any(
            task in entry["owners"] and pending_stubs(str(entry["python"]))  # type: ignore[operator]
            for entry in port_map()
        ), task


def test_returns_results_when_nothing_is_pending() -> None:
    assert run_or_pending(lambda: 42, ["T09"]) == 42


@pytest.mark.parametrize("task,cls", _pending_init_stubs()[:3], ids=lambda x: str(x))
def test_genuine_stub_of_declared_dependency_is_pending(task: str, cls: type) -> None:
    result = run_or_pending(lambda: _call_init(cls), [task])
    assert isinstance(result, Pending) and result.task == task
    assert f"pending {task}" in result.message or task in result.message


@pytest.mark.parametrize("task,cls", _pending_init_stubs()[:3], ids=lambda x: str(x))
def test_stub_of_undeclared_task_fails(task: str, cls: type) -> None:
    with pytest.raises(NotImplementedError):
        run_or_pending(lambda: _call_init(cls), ["T99"])


def test_raise_outside_a_stub_fails() -> None:
    task = min(pending_tasks() or {"T28"})

    def fake() -> None:
        raise NotImplementedError(f"Java: Fake#fake — pending {task}")

    with pytest.raises(NotImplementedError):
        run_or_pending(fake, [task])
    with pytest.raises(NotImplementedError, match="out of scope"):
        run_or_pending(lambda: (_ for _ in ()).throw(NotImplementedError("out of scope")), [task])


def test_pending_scenarios_are_reported() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        report_pending("demo", [1, Pending("T09", "Java: Person#Person — pending T09", "x:1")])
        report_pending("none pending", [1, 2])
    assert len(caught) == 1 and issubclass(caught[0].category, PendingIntegrationWarning)
    assert "1/2 scenarios pending on unmerged T09" in str(caught[0].message)
