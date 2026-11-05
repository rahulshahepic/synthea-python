"""Check that T04 skeletons preserve Java instance fields and enum members."""

from __future__ import annotations

import ast
import re
import tomllib
from pathlib import Path

import pytest

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
        if not set(x["owners"]) & {"T01", "T02", "T03", "T05", "T06"} and x["java"]
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


@pytest.mark.parametrize(
    "entry",
    [
        x
        for x in tomllib.loads((ROOT / "docs/port_map.toml").read_text())["module"]
        if not set(x["owners"]) & {"T01", "T02", "T03", "T05", "T06"} and x["java"]
    ],
    ids=lambda x: x["python"],
)
def test_skeleton_explicit_typed_stubs(entry: dict[str, object]) -> None:
    """A skeleton preserves the callable contract and fails with its actual owner task."""
    tree = ast.parse((ROOT / str(entry["python"])).read_text())
    owners = entry["owners"]
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        label = f"{entry['python']}:{node.lineno} {node.name}"
        assert node.args.vararg is None and node.args.kwarg is None, label
        assert node.returns is not None, label
        assert all(
            arg.annotation is not None
            for arg in node.args.posonlyargs + node.args.args + node.args.kwonlyargs
            if arg.arg not in {"self", "cls"}
        ), label
        assert "Java:" in (ast.get_docstring(node) or ""), label
        raises = [child for child in ast.walk(node) if isinstance(child, ast.Raise)]
        assert len(raises) == 1, label
        exc = raises[0].exc
        assert isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name), label
        assert exc.func.id == "NotImplementedError", label
        assert len(exc.args) == 1 and isinstance(exc.args[0], ast.Constant), label
        message = exc.args[0].value
        assert isinstance(message, str) and "Java:" in message and "#" in message, label
        assert "pending" in message and all(owner in message for owner in owners), label


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
