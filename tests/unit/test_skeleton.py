"""T04 skeleton contract: Java fields, enum members, typed callables, explicit stubs.

These hold for skeletons and implementations alike; nothing here requires a ported module
to stay a stub (stub-ness is detected from the code, see tests/dependency_gate.py).
"""

from __future__ import annotations

import ast
import functools
import re
import tomllib
from pathlib import Path

import pytest

from tests.dependency_gate import pending_stubs, pending_tasks, stub_message

ROOT = Path(__file__).resolve().parents[2]


def _clean(source: str) -> str:
    """Java: source lexical scan, preserving offsets while ignoring comments and literals."""
    source = re.sub(r"/\*[\s\S]*?\*/", lambda m: " " * len(m[0]), source)
    source = re.sub(r"//[^\n]*", lambda m: " " * len(m[0]), source)
    source = re.sub(r'"(?:\\.|[^"\\])*"', lambda m: " " * len(m[0]), source)
    return source


def _java_fields(source: str) -> list[tuple[str, str]]:
    """Java: class-level field declarations (not locals inside method bodies)."""
    clean = _clean(source)
    depth, start = 0, 0
    types: list[tuple[str, int, str]] = []
    fields: list[tuple[str, str]] = []
    for i, ch in enumerate(clean):
        if ch == "{":
            match = re.search(r"\b(class|interface|enum|record)\s+(\w+)", clean[start:i])
            if match:
                types.append((match[2], depth + 1, match[1]))
            depth += 1
            start = i + 1
        elif ch == "}":
            if types and types[-1][1] == depth:
                types.pop()
            depth -= 1
            start = i + 1
        elif ch == ";":
            if types and types[-1][1] == depth and types[-1][2] != "enum":
                statement = " ".join(clean[start:i].split())
                match = re.match(
                    r"(?:@\w+(?:\([^)]*\))?\s+)*"
                    r"(?:public|private|protected)\s+"
                    r"((?:(?:static|final|transient|volatile)\s+)*)"
                    r"[A-Za-z][A-Za-z0-9_<>?,. \[\]]*\s+(\w+)\s*(?:=.+)?$",
                    statement,
                )
                if match and "static" not in match[1]:
                    fields.append((types[-1][0], match[2]))
            start = i + 1
    return fields


def _java_enums(source: str) -> dict[str, set[str]]:
    """Java: enum constant declarations, including constants with constructor parameters."""
    clean = re.sub(r"/\*[\s\S]*?\*/|//[^\n]*", " ", source)
    result: dict[str, set[str]] = {}
    for match in re.finditer(r"\benum\s+(\w+)\s*\{", clean):
        start = match.end()
        end = clean.find(";", start)
        close = clean.find("}", start)
        if end < 0 or (close >= 0 and close < end):
            end = close
        if end < 0:
            continue
        section = clean[start:end]
        names = set(re.findall(r"(?:^|,)\s*([A-Z][A-Z0-9_]*)\b", section))
        if names:
            result[match[1]] = names
    return result


def _classes(tree: ast.Module) -> dict[str, ast.ClassDef]:
    return {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}


def _init_fields(cls: ast.ClassDef) -> set[str]:
    names: set[str] = set()
    for child in cls.body:
        if not isinstance(child, ast.FunctionDef) or child.name != "__init__":
            continue
        for node in ast.walk(child):
            if (
                isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Attribute)
                and isinstance(node.target.value, ast.Name)
                and node.target.value.id == "self"
            ):
                names.add(node.target.attr)
    return names


@pytest.mark.parametrize(
    "entry",
    [
        x
        for x in tomllib.loads((ROOT / "docs/port_map.toml").read_text())["module"]
        if not set(x["owners"]) & {"T01", "T02", "T03", "T05"} and x["java"]
    ],
    ids=lambda x: x["python"],
)
def test_skeleton_java_fields_and_enums(entry: dict[str, object]) -> None:
    """Every Java instance field is typed in Python and every enum member is present."""
    java = (ROOT / str(entry["java"])).read_text()
    py = ast.parse((ROOT / str(entry["python"])).read_text())
    classes = _classes(py)
    errors: list[str] = []
    for name, field in _java_fields(java):
        if name not in classes:
            errors.append(f"{name}: missing class")
            continue
        present = _init_fields(classes[name])
        snake = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", field).lower()
        if not ({field, snake, "_" + field} & present):
            errors.append(f"{name}.{field}: missing typed instance field")
    for name, members in _java_enums(java).items():
        if name not in classes:
            errors.append(f"{name}: missing enum")
            continue
        declared = {
            node.targets[0].id
            for node in classes[name].body
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        }
        for member in sorted(members - declared):
            errors.append(f"{name}.{member}: missing enum value")
    assert not errors, "\n".join(errors)


CONTRACT_MODULES = [
    x
    for x in tomllib.loads((ROOT / "docs/port_map.toml").read_text())["module"]
    if not set(x["owners"]) & {"T01", "T02", "T03", "T05"} and x["java"]
]


def _functions(tree: ast.Module) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)]


def _is_public(name: str) -> bool:
    return not name.startswith("_") or (name.startswith("__") and name.endswith("__"))


@pytest.mark.parametrize("entry", CONTRACT_MODULES, ids=lambda x: x["python"])
def test_skeleton_typed_callable_contract(entry: dict[str, object]) -> None:
    """Stubs and implementations alike keep the T04 callable contract (AGENTS.md §9.4-5).

    Every function is fully annotated with no catch-all ``*args``/``**kwargs`` (Java overloads
    are explicit), and every public one cites its Java origin. Python-only private and local
    helpers of an implementation need no Java citation.
    """
    tree = ast.parse((ROOT / str(entry["python"])).read_text())
    errors: list[str] = []
    local = {
        id(inner)
        for outer in _functions(tree)
        for inner in ast.walk(outer)
        if inner is not outer and isinstance(inner, ast.FunctionDef | ast.AsyncFunctionDef)
    }
    for node in _functions(tree):
        label = f"{entry['python']}:{node.lineno} {node.name}"
        inherited_rng = (
            entry["python"] == "src/synthea/world/agents/person.py" and node.name == "rand"
        )
        if (node.args.vararg is not None and not inherited_rng) or node.args.kwarg is not None:
            errors.append(f"{label}: *args/**kwargs")
        if node.returns is None:
            errors.append(f"{label}: missing return annotation")
        if any(
            arg.annotation is None
            for arg in node.args.posonlyargs + node.args.args + node.args.kwonlyargs
            if arg.arg not in {"self", "cls"}
        ):
            errors.append(f"{label}: unannotated parameter")
        if (
            id(node) not in local
            and _is_public(node.name)
            and "Java:" not in (ast.get_docstring(node) or "")
        ):
            errors.append(f"{label}: docstring does not cite Java")
    assert not errors, "\n".join(errors)


@pytest.mark.parametrize("entry", CONTRACT_MODULES, ids=lambda x: x["python"])
def test_skeleton_stubs_are_explicit_and_name_their_owner(entry: dict[str, object]) -> None:
    """Every remaining stub fails loudly with its Java origin and its owner task.

    A stub is a docstring plus one ``raise NotImplementedError("Java: X#y — pending T<nn>")``
    (or an "out of scope" message, PORTING_GUIDE §8). A "pending" raise anywhere else (inside
    a partly ported body) is forbidden: it would hide an unported path from --no-stubs.
    """
    tree = ast.parse((ROOT / str(entry["python"])).read_text())
    owners = [str(o) for o in entry["owners"]]  # type: ignore[attr-defined]
    errors: list[str] = []
    for node in _functions(tree):
        label = f"{entry['python']}:{node.lineno} {node.name}"
        message = stub_message(node)
        if message is not None:
            if "out of scope" in message.lower():
                continue
            if not ("Java:" in message and "#" in message and "pending" in message):
                errors.append(f"{label}: stub message must be 'Java: X#y — pending T<nn>'")
            elif not all(owner in message for owner in owners):
                errors.append(f"{label}: stub message must name {owners}")
            continue
        for child in ast.walk(node):
            if (
                isinstance(child, ast.Raise)
                and isinstance(child.exc, ast.Call)
                and isinstance(child.exc.func, ast.Name)
                and child.exc.func.id == "NotImplementedError"
                and any(
                    isinstance(a, ast.Constant) and "pending" in str(a.value)
                    for a in child.exc.args
                )
            ):
                errors.append(f"{label}:{child.lineno}: 'pending' raise inside an implementation")
    assert not errors, "\n".join(errors)


@pytest.mark.parametrize(
    "entry",
    [x for x in CONTRACT_MODULES if len(x["owners"]) == 1],
    ids=lambda x: x["python"],
)
def test_module_is_skeleton_or_fully_implemented(entry: dict[str, object]) -> None:
    """A single-owner module is either still the T04 skeleton or completely ported.

    Implemented: no pending stub remains (the --no-stubs rule) and at least one unit or
    parity test imports the module. Skeleton: every function is still a pending stub. A mix
    means a half-merged port. Multi-owner modules (e.g. State: T19 then T20) are exempt.
    """
    python = str(entry["python"])
    tree = ast.parse((ROOT / python).read_text())
    functions = _functions(tree)
    pending = pending_stubs(python)
    if pending:
        implemented = [
            f"{n.name}:{n.lineno}"
            for n in functions
            if (n.name, n.lineno) not in {(name, line) for name, line, *_ in pending}
            and stub_message(n) is None
        ]
        assert not implemented, f"{python}: partly ported; still pending: {len(pending)}"
        return
    module = python.removeprefix("src/").removesuffix(".py").replace("/", ".")
    covered = _covered_modules()
    assert module in covered, (
        f"{python}: implemented, but no unit or parity test imports {module} "
        "(directly or through another covered module)"
    )


def _imports(path: Path) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
        elif isinstance(node, ast.Import):
            names.update(a.name for a in node.names)
    return names


@functools.cache
def _covered_modules() -> frozenset[str]:
    """Modules a test imports, closed over what those src modules import in turn."""
    covered: set[str] = set()
    for test in (ROOT / "tests").rglob("test_*.py"):
        if test.name != "test_skeleton.py":
            covered |= _imports(test)
    frontier = set(covered)
    while frontier:
        name = frontier.pop()
        path = ROOT / "src" / (name.replace(".", "/") + ".py")
        if path.is_file():
            new = _imports(path) - covered
            covered |= new
            frontier |= new
    return frozenset(covered)


def test_skeleton_nested_members_belong_to_their_java_class() -> None:
    """Java: HealthRecord.Code, HealthRecord.Entry, State.Delay and Components.Range."""
    import inspect

    from synthea.engine.components import Components, Range, RangeWithUnit
    from synthea.engine.state import Delay, Delayable, State
    from synthea.world.concepts.health_record import Code, Entry, HealthRecord, Medication

    assert HealthRecord.Code is Code
    assert HealthRecord.Entry is Entry
    assert "from_json" in vars(Code) and "from_json" not in vars(HealthRecord)
    assert "get_cost" in vars(Entry) and "get_cost" not in vars(HealthRecord)
    assert "get_quantity" in vars(Medication)
    assert isinstance(vars(Code)["from_json"], staticmethod)
    assert issubclass(Medication, Entry)
    assert State.Delay is Delay and issubclass(Delay, Delayable)
    assert Components.Range is Range and issubclass(RangeWithUnit, Range)
    params = inspect.signature(Code).parameters
    assert len(params) == 3
    assert next(iter(params.values())).default is inspect.Parameter.empty
    assert all(p.default is None for p in list(params.values())[1:])


def test_skeleton_overload_shapes_and_cli_failure() -> None:
    """Java: TimeSeriesData constructors, SimpleCSV#parse, and App#main."""
    import inspect

    from synthea.cli import main
    from synthea.helpers.simple_csv import SimpleCSV
    from synthea.helpers.time_series_data import TimeSeriesData

    params = list(inspect.signature(TimeSeriesData).parameters.values())
    assert len(params) == 2
    assert params[0].default is inspect.Parameter.empty
    assert params[1].default is None
    assert "float" in str(params[0].annotation)
    assert "list[float]" in str(params[0].annotation)
    assert "int" in str(params[0].annotation)
    assert isinstance(vars(SimpleCSV)["parse"], staticmethod)
    if "T28" in pending_tasks():  # the CLI stub fails loudly until T28 ports it
        with pytest.raises(NotImplementedError, match=r"Java: App#main.*pending T28"):
            main([])


def test_skeleton_constant_scale_and_readonly_maps() -> None:
    """Java: Claim#ZERO_CENTS and Collections.unmodifiableMap data declarations."""
    from decimal import Decimal

    from synthea.export.csv_constants import CSVConstants
    from synthea.world.concepts.claim import Claim
    from synthea.world.concepts.race_and_ethnicity import RaceAndEthnicity

    assert Decimal("0.00") == Claim.ZERO_CENTS
    assert Claim.ZERO_CENTS.as_tuple().exponent == -2
    for mapping in [
        CSVConstants.HEADER_LINE_MAP,
        RaceAndEthnicity.LOOK_UP_CDC_RACE,
        RaceAndEthnicity.LOOK_UP_CDC_ETHNICITY_CODE,
        RaceAndEthnicity.LOOK_UP_CDC_ETHNICITY_DISPLAY,
    ]:
        with pytest.raises(TypeError):
            mapping["new_key"] = "must fail"
