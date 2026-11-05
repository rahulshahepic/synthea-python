"""Exact parity for Config, SimpleCSV and SimpleYML against ConfigProbe goldens.

config.jsonl is replayed as a script in order (Config is static, cumulative
state in Java): "default"/"tricky"/"file"/"getAs" lines are assertions,
"set" lines are applied, and the load markers trigger the same loads the
probe performed, from the exact input files the probe saved next to the
goldens. csv.jsonl carries every case's input (or, for dedicated unparse
cases, its rows), so the Python side recomputes each field and compares the
whole record. yml.jsonl similarly carries the class name and
``String.valueOf`` for every value, which the Python side reproduces from
the ported types.
"""

from __future__ import annotations

import importlib.util
import io
import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from synthea.helpers.config import Config
from synthea.helpers.simple_csv import SimpleCSV
from synthea.helpers.simple_yml import SimpleYML
from synthea.javacompat.numbers import double_to_string
from synthea.resources import resource_path, resources_dir

_spec = importlib.util.spec_from_file_location(
    "canonical_config", Path(__file__).parent / "canonical" / "config.py"
)
assert _spec is not None and _spec.loader is not None
canonical = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(canonical)

# Python exception type name -> the Java exception it mirrors, per area.
_CONFIG_ERR = {"TypeError": "NullPointerException", "ValueError": "NumberFormatException"}
_YML_ERR = {"AttributeError": "NullPointerException", "TypeError": "ClassCastException"}
_UNPARSE_ERR = {"IndexError": "IndexOutOfBoundsException"}


def _num(call: Callable[[], float | int], fmt: Callable[[Any], str]) -> str:
    try:
        return fmt(call())
    except (TypeError, ValueError) as exc:
        return "ERR:" + _CONFIG_ERR[type(exc).__name__]


def _get_as(key: str) -> dict[str, Any]:
    """Rebuild one getAs record from the Python Config."""
    return {
        "get": Config.get(key),
        "getDef": Config.get(key, "DEF"),
        "double": _num(lambda: Config.get_as_double(key), double_to_string),
        "doubleDef": _num(lambda: Config.get_as_double(key, 9.25), double_to_string),
        "int": _num(lambda: Config.get_as_integer(key), str),
        "intDef": _num(lambda: Config.get_as_integer(key, -7), str),
        "long": _num(lambda: Config.get_as_long(key), str),
        "longDef": _num(lambda: Config.get_as_long(key, -9), str),
        "bool": str(Config.get_as_boolean(key)).lower(),
        "boolDef": str(Config.get_as_boolean(key, True)).lower(),
    }


@pytest.mark.parity
def test_config_probe(golden: Callable[[str], Path]) -> None:
    """Replay ConfigProbe's config.jsonl against the Python Config, in order."""
    gdir = golden("ConfigProbe")
    Config.properties.clear()
    Config.load(io.BytesIO(resource_path("synthea.properties").read_bytes()))
    defaults: list[str] = []
    snapshot: set[str] | None = None
    counts: dict[str, int] = {}
    with (gdir / "config.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            kind = row["kind"]
            counts[kind] = counts.get(kind, 0) + 1
            if kind == "default":
                defaults.append(row["key"])
                assert Config.get(row["key"]) == row["value"], row
            elif kind == "set":
                if defaults:
                    # The defaults snapshot is complete and exactly the
                    # initially loaded key set, in String.compareTo order.
                    assert defaults == sorted(defaults)
                    assert set(defaults) == Config.all_property_names()
                    defaults = []
                Config.set(row["key"], row["value"])
            elif kind == "getAs":
                expected = {k: row[k] for k in _get_as(row["key"])}
                assert _get_as(row["key"]) == expected, row
            elif kind == "loadTricky":
                Config.load(io.BytesIO((gdir / "tricky.properties").read_bytes()))
            elif kind == "tricky":
                assert Config.get(row["key"]) == row["value"], row
            elif kind == "malformed":
                data = (gdir / f"malformed-{row['name']}.properties").read_bytes()
                with pytest.raises(ValueError) as excinfo:
                    Config.load(io.BytesIO(data))
                # Java's IllegalArgumentException is mirrored as ValueError.
                assert type(excinfo.value).__name__ == "ValueError"
                assert row["error"] == "IllegalArgumentException"
            elif kind == "loadFile":
                Config.load(gdir / "file-utf8.properties")
            elif kind == "file":
                assert Config.get(row["key"]) == row["value"], row
            elif kind == "setRemove":
                if row["step"] == "before":
                    snapshot = Config.all_property_names()
                    assert ("bing.bong.do" in snapshot) == row["contains"]
                    Config.set("bing.bong.do", "true")
                elif row["step"] == "afterSet":
                    assert ("bing.bong.do" in Config.all_property_names()) == row["contains"]
                    assert Config.get("bing.bong.do") == row["value"]
                    Config.remove("bing.bong.do")
                elif row["step"] == "afterRemove":
                    assert ("bing.bong.do" in Config.all_property_names()) == row["contains"]
                    assert snapshot is not None
                    assert ("bing.bong.do" in snapshot) == row["snapshotContains"]
            else:  # pragma: no cover - probe added a kind this test does not know
                pytest.fail(f"unexpected config.jsonl kind: {kind}")
    assert counts["default"] > 100
    assert counts["tricky"] == 28
    assert counts["getAs"] == 17


def _items(rows: list[dict[str, str]]) -> list[list[list[str]]]:
    """Rows as ordered [key, value] pair lists (map order is significant)."""
    return [[[k, v] for k, v in row.items()] for row in rows]


def _gold_items(rows: list[dict[str, Any]]) -> list[list[list[Any]]]:
    return [[[k, v] for k, v in row.items()] for row in rows]


def _unparse_or_err(call: Callable[[], str]) -> str:
    try:
        return call()
    except Exception as exc:
        name = _UNPARSE_ERR.get(type(exc).__name__, type(exc).__name__)
        return f"ERR:{name}"


@pytest.mark.parity
def test_csv_probe_files(golden: Callable[[str], Path]) -> None:
    """Every CSV resource parses identically (row count, columns, hash, edges)."""
    gdir = golden("ConfigProbe")
    seen = 0
    with (gdir / "csv.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if row["kind"] != "file":
                continue
            seen += 1
            content = (resources_dir() / row["path"]).read_bytes().decode("utf-8")
            if "error" in row:
                with pytest.raises(Exception) as excinfo:
                    SimpleCSV.parse(content)
                assert type(excinfo.value).__name__ == row["error"], row["path"]
                continue
            rows = SimpleCSV.parse(content)
            assert len(rows) == row["rows"], row["path"]
            assert (list(rows[0].keys()) if rows else []) == row["cols"], row["path"]
            assert canonical.rows_sha256(rows) == row["sha256"], row["path"]
            assert _items(rows[:3]) == _gold_items(row["first"]), row["path"]
            assert _items(rows[-3:]) == _gold_items(row["last"]), row["path"]
    assert seen == 127


@pytest.mark.parity
def test_csv_probe_cases(golden: Callable[[str], Path]) -> None:
    """Every tricky CSV case recomputes to the exact golden record."""
    gdir = golden("ConfigProbe")
    seen = 0
    with (gdir / "csv.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if row["kind"] != "case":
                continue
            seen += 1
            actual: dict[str, Any] = {}
            if row["input"] is not None:
                data: str = row["input"]
                sep = row["sep"]
                rows: list[dict[str, str]] | None
                try:
                    rows = SimpleCSV.parse(data, sep) if sep else SimpleCSV.parse(data)
                    actual["parse"] = _items(rows)
                except Exception as exc:
                    rows = None
                    actual["parse"] = f"ERR:{type(exc).__name__}"
                if rows is None:
                    actual["unparse"] = None
                    actual["unparseSep"] = None
                else:
                    actual["unparse"] = _unparse_or_err(lambda rows=rows: SimpleCSV.unparse(rows))
                    actual["unparseSep"] = _unparse_or_err(
                        lambda rows=rows: SimpleCSV.unparse(rows, "|")
                    )
                actual["valid"] = SimpleCSV.is_valid(data)
                actual["validSep"] = (
                    SimpleCSV.is_valid(data, sep) if sep else SimpleCSV.is_valid(data)
                )
                try:
                    actual["lineByLine"] = _items(list(SimpleCSV.parse_line_by_line(data)))
                except Exception as exc:
                    actual["lineByLine"] = f"ERR:{type(exc).__name__}"
            else:
                rows = [dict(obj) for obj in row["rows"]]
                actual["parse"] = None
                actual["unparse"] = _unparse_or_err(lambda rows=rows: SimpleCSV.unparse(rows))
                actual["unparseSep"] = _unparse_or_err(
                    lambda rows=rows: SimpleCSV.unparse(rows, "|")
                )
                actual["valid"] = None
                actual["validSep"] = None
                actual["lineByLine"] = None
            for field in ("parse", "unparse", "unparseSep", "valid", "validSep", "lineByLine"):
                expected = row[field]
                if field in ("parse", "lineByLine") and isinstance(expected, list):
                    expected = _gold_items(expected)
                assert actual[field] == expected, f"{row['name']}.{field}"
    assert seen == 44


_WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _java_class(value: object) -> str:
    """The Java runtime class simple name for a ported SimpleYML value."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "Boolean"
    if isinstance(value, int):
        if -(2**31) <= value < 2**31:
            return "Integer"
        if -(2**63) <= value < 2**63:
            return "Long"
        return "BigInteger"
    if isinstance(value, float):
        return "Double"
    if isinstance(value, str):
        return "String"
    if isinstance(value, datetime):
        return "Date"
    if isinstance(value, list):
        return "ArrayList"
    if isinstance(value, dict):
        return "LinkedHashMap"
    raise AssertionError(f"no Java class mapping for {type(value)}")


def _java_str(value: object) -> str:
    """Java String.valueOf for a ported SimpleYML value."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return double_to_string(value)
    if isinstance(value, str):
        return value
    if isinstance(value, datetime):
        dt = value.astimezone(UTC)
        return (
            f"{_WEEKDAYS[dt.weekday()]} {_MONTHS[dt.month - 1]} {dt.day:02d} "
            f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d} UTC {dt.year}"
        )
    if isinstance(value, list):
        return "[" + ", ".join(_java_str(v) for v in value) + "]"
    if isinstance(value, dict):
        return "{" + ", ".join(f"{k}={_java_str(v)}" for k, v in value.items()) + "}"
    raise AssertionError(f"no String.valueOf mapping for {type(value)}")


@pytest.mark.parity
def test_yml_probe(golden: Callable[[str], Path]) -> None:
    """SnakeYAML typing, SimpleYML.get paths and resource gets match exactly."""
    gdir = golden("ConfigProbe")
    synthetic = SimpleYML((gdir / "synthetic.yml").read_text(encoding="utf-8"))
    assert synthetic.internal_map is not None
    docs: dict[str, SimpleYML] = {
        "nested": SimpleYML(
            "foo:\n  bar: 2\n  baz: 4\n  qux:\n    corge: 9\n    grault: -1\nplugh: 7\n"
        ),
        "empty": SimpleYML(""),
    }
    resource_docs: dict[str, SimpleYML] = {}
    scalar_keys: list[str] = []
    with (gdir / "yml.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            kind = row["kind"]
            if kind == "scalar":
                scalar_keys.append(row["key"])
                value = synthetic.internal_map[row["key"]]
                assert _java_class(value) == row["class"], row
                assert _java_str(value) == row["value"], row
            elif kind == "get":
                doc = docs[row["doc"]]
                try:
                    value = doc.get(row["path"])
                except (AttributeError, TypeError) as exc:
                    assert row.get("error") == _YML_ERR[type(exc).__name__], row
                else:
                    assert _java_class(value) == row["class"], row
                    assert _java_str(value) == row["value"], row
            elif kind == "construct":
                with pytest.raises(TypeError) as excinfo:
                    SimpleYML("- a\n- b\n")
                assert _YML_ERR[type(excinfo.value).__name__] == row["error"], row
            elif kind == "resourceGet":
                doc = resource_docs.setdefault(
                    row["file"],
                    SimpleYML(resource_path(row["file"]).read_text(encoding="utf-8")),
                )
                value = doc.get(row["path"])
                assert _java_class(value) == row["class"], row
                assert _java_str(value) == row["value"], row
            else:  # pragma: no cover - probe added a kind this test does not know
                pytest.fail(f"unexpected yml.jsonl kind: {kind}")
    assert scalar_keys == list(synthetic.internal_map.keys())
