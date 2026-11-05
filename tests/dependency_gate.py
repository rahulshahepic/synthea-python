"""Integration gate: run real production calls into tasks that are still T04 stubs.

A component task (e.g. T08) can be reviewed before the tasks it calls into have merged,
and sometimes before tasks that depend on it (a dependency cycle such as HealthRecord ↔
Person). Its integration scenarios still call the **real** production code. This module
decides, per scenario, what a `NotImplementedError` means:

* raised by a genuine T04 stub (a function whose whole body is
  ``raise NotImplementedError("Java: ... pending T<nn>")``) in a module that ``docs/port_map.toml``
  assigns to one of the scenario's declared dependency tasks, and that task still has pending
  stubs: the scenario is **pending** on that task. It is reported, never silently dropped;
* anything else (a stub of an undeclared task, an "out of scope" stub, a raise from test code,
  a partial port): re-raised, so the test fails.

Once every declared dependency is implemented, nothing can be pending and every scenario
must match exactly. That happens automatically, in the PR of the last dependency to land,
which is the integration task named in the issue. No skip, xfail or test double is involved.

Usage (see PORTING_GUIDE §10)::

    results = [run_or_pending(lambda: scenario(i), ("T09", "T14")) for i in cases]
    for expected, actual in zip(rows, results, strict=True):
        if not isinstance(actual, Pending):
            assert actual == expected
    report_pending("HealthRecord full records", results)
"""

from __future__ import annotations

import ast
import functools
import re
import tomllib
import warnings
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK_RE = re.compile(r"\bT\d{2}\b")


class PendingIntegrationWarning(UserWarning):
    """Scenarios that could not run yet because a declared dependency is still a stub."""


@dataclass(frozen=True)
class Pending:
    """A scenario stopped by a genuine pending stub of a declared dependency task."""

    task: str
    message: str
    where: str


def stub_message(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
    """Message of a T04 stub: docstring and bare field annotations, then one raise.

    The bare annotations (``self.x: int``) are how a stubbed ``__init__`` declares its fields.
    """
    body = [
        b
        for b in node.body
        if not (isinstance(b, ast.Expr) and isinstance(b.value, ast.Constant))
        and not (isinstance(b, ast.AnnAssign) and b.value is None)
    ]
    if len(body) != 1 or not isinstance(body[0], ast.Raise) or body[0].exc is None:
        return None
    exc = body[0].exc
    func = exc.func if isinstance(exc, ast.Call) else exc
    if not (isinstance(func, ast.Name) and func.id == "NotImplementedError"):
        return None
    if isinstance(exc, ast.Call) and exc.args and isinstance(exc.args[0], ast.Constant):
        return str(exc.args[0].value)
    return ""


@functools.cache
def port_map() -> tuple[dict[str, object], ...]:
    """The modules of docs/port_map.toml."""
    return tuple(tomllib.loads((ROOT / "docs/port_map.toml").read_text())["module"])


@functools.cache
def pending_stubs(python: str) -> frozenset[tuple[str, int, int, str]]:
    """(name, first line, last line, message) of every pending T04 stub left in a module."""
    path = ROOT / python
    if not path.is_file():
        return frozenset()
    found = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            msg = stub_message(node)
            if msg is not None and "pending" in msg:
                found.add((node.name, node.lineno, node.end_lineno or node.lineno, msg))
    return frozenset(found)


@functools.cache
def pending_tasks() -> frozenset[str]:
    """Tasks that still have at least one pending stub in a module they own."""
    tasks: set[str] = set()
    for entry in port_map():
        owners = set(entry["owners"])  # type: ignore[call-overload]
        for *_, msg in pending_stubs(str(entry["python"])):
            tasks |= owners & set(TASK_RE.findall(msg))
    return frozenset(tasks)


def _owners_of(path: Path) -> set[str]:
    try:
        rel = path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return set()
    for entry in port_map():
        if entry["python"] == rel:
            return set(entry["owners"])  # type: ignore[call-overload]
    return set()


def run_or_pending[T](scenario: Callable[[], T], dependencies: Iterable[str]) -> T | Pending:
    """Run one integration scenario; see the module docstring for what counts as pending."""
    allowed = set(dependencies)
    try:
        return scenario()
    except NotImplementedError as exc:
        tb = exc.__traceback__
        while tb is not None and tb.tb_next is not None:
            tb = tb.tb_next
        if tb is None:
            raise
        path = Path(tb.tb_frame.f_code.co_filename)
        rel = path.resolve().relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else ""
        msg = str(exc)
        named = set(TASK_RE.findall(msg)) & _owners_of(path) & allowed & pending_tasks()
        # Raised by the body of a genuine stub in that module, with that exact message.
        is_stub = any(
            fn == tb.tb_frame.f_code.co_name and first <= tb.tb_lineno <= last and msg == stub
            for fn, first, last, stub in pending_stubs(rel)
        )
        if not named or not is_stub:
            raise
        return Pending(min(named), msg, f"{rel}:{tb.tb_lineno}")


def report_pending(name: str, results: Sequence[object]) -> None:
    """Make pending scenarios visible in the pytest summary (never a silent pass)."""
    pending = [r for r in results if isinstance(r, Pending)]
    if pending:
        tasks = sorted({p.task for p in pending})
        warnings.warn(
            PendingIntegrationWarning(
                f"{name}: {len(pending)}/{len(results)} scenarios pending on unmerged "
                f"{', '.join(tasks)} (first: {pending[0].message} at {pending[0].where}); "
                f"{len(results) - len(pending)} compared exactly"
            ),
            stacklevel=2,
        )
