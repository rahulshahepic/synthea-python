"""Unit tests for the T20-fix in issue #81: runtime use of
TYPE_CHECKING-only names in ``src/synthea/engine/state.py``.

``MedicationEnd.process`` did ``cast(Medication, ...)`` with ``Medication``
imported only under ``TYPE_CHECKING``; ``cast()`` evaluates its first
argument at runtime, so the first MedicationEnd state with
``referenced_by_attribute`` raised ``NameError`` (seen ~40s into the
``-s 42 -p 10 Massachusetts`` end-to-end scenario, PR #80).
"""

from __future__ import annotations

import ast
import builtins
from pathlib import Path

import synthea.engine.state as state_module
from synthea.engine.state import MedicationEnd
from synthea.world.agents.payer_manager import PayerManager
from synthea.world.agents.person import Person, Point2DDouble
from synthea.world.concepts.health_record import Medication

TIME = 1609459200000  # 2021-01-01T00:00:00Z
BIRTH = TIME - 35 * 365 * 24 * 3600 * 1000


def _person() -> Person:
    """Person with a no-insurance plan, so a Medication's Claim can bind.

    Mirrors the explicit person fixture in tests/unit/test_csv_exporter.py:
    a bare Person has no insurance history and Claim construction raises.
    """
    PayerManager.load_no_insurance()
    person = Person(0)
    person.attributes.update(
        {
            Person.BIRTHDATE: BIRTH,
            Person.ID: "person-0",
            Person.INCOME: 0,
            Person.COORDINATE: Point2DDouble(0.0, 0.0),
        }
    )
    person.coverage.set_plan_to_no_insurance(BIRTH)
    person.coverage.get_last_plan_record().update_stop_time(TIME + 86400000)
    return person


def test_medication_end_referenced_by_attribute() -> None:
    """Java: MedicationEnd#process with referencedByAttribute set.

    Executes the branch that raised NameError before the fix: the
    medication stored under the named attribute is stopped at ``time``
    and removed from the record's present medications.
    """
    person = _person()
    record = person.record
    assert record is not None
    medication = record.new_entry(lambda: Medication(TIME, "medication"))
    record.present[medication.type] = medication
    person.attributes["current_medication"] = medication

    state = MedicationEnd()
    state.medication_order = None
    state.referenced_by_attribute = "current_medication"
    state.codes = None

    assert state.process(person, TIME + 1000) is True
    assert medication.stop == TIME + 1000
    assert medication.type not in record.present


def _type_checking_only_names(tree: ast.Module) -> set[str]:
    """Names imported under ``if TYPE_CHECKING:`` and nowhere at runtime."""
    tc_names: set[str] = set()
    runtime_names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.If):
            target = (
                tc_names
                if isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING"
                else None
            )
            if target is None:
                continue
            for sub in ast.walk(node):
                if isinstance(sub, ast.ImportFrom):
                    target.update(a.asname or a.name for a in sub.names)
                elif isinstance(sub, ast.Import):
                    target.update((a.asname or a.name).split(".")[0] for a in sub.names)
        elif isinstance(node, ast.ImportFrom):
            runtime_names.update(a.asname or a.name for a in node.names)
        elif isinstance(node, ast.Import):
            runtime_names.update((a.asname or a.name).split(".")[0] for a in node.names)
    return tc_names - runtime_names


def _bound_names(func: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    """Names bound inside a function: params, assignments, local imports."""
    bound: set[str] = set()
    args = func.args
    for arg in [*args.posonlyargs, *args.args, *args.kwonlyargs]:
        bound.add(arg.arg)
    if args.vararg:
        bound.add(args.vararg.arg)
    if args.kwarg:
        bound.add(args.kwarg.arg)
    for sub in ast.walk(func):
        if isinstance(sub, ast.ImportFrom):
            bound.update(a.asname or a.name for a in sub.names)
        elif isinstance(sub, ast.Import):
            bound.update((a.asname or a.name).split(".")[0] for a in sub.names)
        elif isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Store):
            bound.add(sub.id)
        elif isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bound.add(sub.name)
    return bound


def test_no_runtime_use_of_type_checking_only_names() -> None:
    """Regression scan for issue #81, acceptance criterion 2.

    Every Load of a TYPE_CHECKING-only name in state.py outside an
    annotation must be bound at runtime (module-level name or a local
    binding in the enclosing function); ``from __future__ import
    annotations`` makes annotation positions lazy, so they are skipped.
    """
    source = Path(state_module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    tc_only = _type_checking_only_names(tree)
    module_names = set(dir(state_module)) | set(dir(builtins))
    violations: list[str] = []

    class Scanner(ast.NodeVisitor):
        def __init__(self) -> None:
            self.scopes: list[set[str]] = []

        def _check(self, node: ast.Name) -> None:
            if node.id not in tc_only:
                return
            if any(node.id in scope for scope in self.scopes):
                return
            if node.id in module_names:
                return
            violations.append(f"{node.id} at line {node.lineno}")

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            for decorator in node.decorator_list:
                self.visit(decorator)
            for default in node.args.defaults:
                self.visit(default)
            self.scopes.append(_bound_names(node))
            for stmt in node.body:
                self.visit(stmt)
            self.scopes.pop()

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
            self.visit(node.target)
            if node.value is not None:
                self.visit(node.value)

        def visit_Name(self, node: ast.Name) -> None:
            if isinstance(node.ctx, ast.Load):
                self._check(node)

    Scanner().visit(tree)
    assert not violations, "runtime-evaluated TYPE_CHECKING-only names in state.py: " + ", ".join(
        violations
    )
