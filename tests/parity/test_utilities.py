"""Exact parity for Utilities, TimeSeriesData and Telemedicine against
UtilitiesProbe goldens.

utilities.jsonl carries every case's inputs, so the Python side recomputes
each field and compares the whole record. Java exceptions are mirrored:
RuntimeException -> RuntimeError, IllegalArgumentException /
NumberFormatException / DateTimeParseException -> ValueError,
NullPointerException -> TypeError.
"""

from __future__ import annotations

import hashlib
import json
import struct
from collections.abc import Callable
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from synthea.helpers.default_random_number_generator import DefaultRandomNumberGenerator
from synthea.helpers.telemedicine import Telemedicine
from synthea.helpers.time_series_data import TimeSeriesData
from synthea.helpers.utilities import Utilities
from synthea.javacompat.numbers import double_to_string, float_to_string, parse_double

_ERR_TYPES: dict[str, type[Exception]] = {
    "RuntimeException": RuntimeError,
    "IllegalArgumentException": ValueError,
    "NumberFormatException": ValueError,
    "DateTimeParseException": ValueError,
    "NullPointerException": TypeError,
}


def _load(golden: Callable[[str], Path]) -> list[dict[str, Any]]:
    gdir = golden("UtilitiesProbe")
    rows: list[dict[str, Any]] = []
    with (gdir / "utilities.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            rows.append(json.loads(line))
    return rows


def _result_or_error(call: Callable[[], Any], fmt: Callable[[Any], str]) -> str:
    try:
        return fmt(call())
    except Exception as exc:
        for java_name, exc_type in _ERR_TYPES.items():
            if isinstance(exc, exc_type):
                return f"ERR:{java_name}"
        raise


class _FakePerson:
    """Person stand-in: Person(seed).rand() is DefaultRandomNumberGenerator(seed).rand()."""

    def __init__(self, seed: int) -> None:
        self._rng = DefaultRandomNumberGenerator(seed)

    def rand(self) -> float:
        return self._rng.rand()


@pytest.mark.parity
def test_utilities_probe(golden: Callable[[str], Path]) -> None:
    gdir = golden("UtilitiesProbe")
    rows = _load(golden)
    counts: dict[str, int] = {}
    freefile = gdir / "freefile.txt"
    dicom_stream: dict[str, Any] = {"rng": None, "index": 0}
    for row in rows:
        kind = row["kind"]
        counts[kind] = counts.get(kind, 0) + 1
        if kind == "ctLong":
            actual = _result_or_error(
                lambda row=row: Utilities.convert_time(row["units"], int(row["value"])), str
            )
            assert actual == row["result"], row
        elif kind == "ctDouble":
            actual = _result_or_error(
                lambda row=row: Utilities.convert_time(row["units"], parse_double(row["value"])),
                str,
            )
            assert actual == row["result"], row
        elif kind == "calYears":
            actual = _result_or_error(
                lambda row=row: Utilities.convert_calendar_years_to_time(row["year"]), str
            )
            assert actual == row["result"], row
        elif kind == "yearMonth":
            t = int(row["time"])
            assert _result_or_error(lambda t=t: Utilities.get_year(t), str) == row["year"], row
            assert _result_or_error(lambda t=t: Utilities.get_month(t), str) == row["month"], row
        elif kind == "localDate":
            d = date.fromisoformat(row["date"])
            ts = Utilities.local_date_to_timestamp(d)
            assert str(ts) == row["ts"], row
            assert Utilities.timestamp_to_local_date(ts).isoformat() == row["roundtrip"], row
        elif kind == "tsToDate":
            actual = Utilities.timestamp_to_local_date(int(row["time"])).isoformat()
            assert actual == row["date"], row
        elif kind == "anniversary":
            actual = _result_or_error(
                lambda row=row: Utilities.get_anniversary(int(row["time"]), row["anniversary"]),
                str,
            )
            assert actual == row["result"], row
        elif kind == "primitive":
            _check_primitive(row)
        elif kind == "risk3":
            actual = Utilities.convert_risk_to_timestep(
                parse_double(row["risk"]), parse_double(row["period"]), parse_double(row["step"])
            )
            # Compare via Double.toString (the probe's serialization): exact
            # for NaN and -0.0, where == is not.
            assert double_to_string(actual) == row["result"], row
        elif kind == "risk2":
            actual = Utilities.convert_risk_to_timestep(
                parse_double(row["risk"]), parse_double(row["period"])
            )
            assert double_to_string(actual) == row["result"], row
        elif kind == "compare":
            _check_compare(row)
        elif kind == "parseRange":
            _check_parse_range(row)
        elif kind == "resource":
            _check_resource(row, gdir, freefile)
        elif kind == "freefile":
            assert freefile.read_text(encoding="utf-8") == row["content"], row
        elif kind == "dicom":
            rng = DefaultRandomNumberGenerator(row["seed"])
            uid = Utilities.random_dicom_uid(rng, int(row["time"]), row["series"], row["instance"])
            assert uid == row["uid"], row
        elif kind == "dicomStream":
            if dicom_stream["rng"] is None:
                dicom_stream["rng"] = DefaultRandomNumberGenerator(row["seed"])
            i = dicom_stream["index"]
            dicom_stream["index"] = i + 1
            uid = Utilities.random_dicom_uid(dicom_stream["rng"], 1000 * i, i, i + 1)
            assert uid == row["uid"], row
        elif kind == "strToObject":
            _check_str_to_object(row)
        elif kind == "cleanMap":
            data: dict[object, object] = {}
            for entry in row["input"]:
                data[entry["k"]] = entry["v"]
            cleaned = Utilities.clean_map(data)
            actual = [[k, v] for k, v in cleaned.items()]
            expected = [[e["k"], e["v"]] for e in row["cleaned"]]
            assert actual == expected, row
        elif kind == "walk":
            tree = gdir / "walktree"
            found: list[str] = []

            def collect(p: Path, tree: Path = tree, found: list[str] = found) -> None:
                found.append(p.relative_to(tree).as_posix())

            Utilities.walk_all_modules(tree, collect)
            assert sorted(found) == row["files"], row
        elif kind == "timeSeries":
            ts = TimeSeriesData(2.5)
            expected_values = [parse_double(v) for v in row["values"]]
            for v in expected_values:
                assert ts.add_value(v) is True
            assert ts.get_period() == parse_double(row["period"]), row
            assert ts.get_values() == expected_values, row
            assert len(ts.get_values()) == row["size"], row
        elif kind == "timeSeriesList":
            backing = [1.0, 2.0, 3.0]
            ts = TimeSeriesData(backing, 0.5)
            backing.append(4.0)
            assert ts.get_period() == parse_double(row["period"]), row
            assert [double_to_string(v) for v in ts.get_values()] == row["values"], row
        elif kind == "timeSeriesCapacity":
            actual = _result_or_error(
                lambda row=row: _capacity_result(row["capacity"]),
                str,
            )
            assert actual == row["result"], row
        elif kind == "timeSeriesSetters":
            ts = TimeSeriesData(1.0)
            ts.set_period(9.75)
            ts.set_values([7.0, 8.0])
            assert ts.add_value(9.0) == row["added"], row
            assert ts.get_period() == parse_double(row["period"]), row
            assert [double_to_string(v) for v in ts.get_values()] == row["values"], row
        elif kind == "telemedicineConstants":
            assert double_to_string(Telemedicine.CURRENT_CHANCE) == row["current"], row
            assert double_to_string(Telemedicine.PREPANDEMIC_CHANCE) == row["prepandemic"], row
            assert str(Telemedicine.TELEMEDICINE_START_DATE) == row["start"], row
            assert str(Telemedicine.TELEMEDICINE_UPTAKE_DATE) == row["uptake"], row
        elif kind == "telemedicine":
            person = _FakePerson(row["seed"])
            actual = Telemedicine.should_encounter_be_virtual(person, int(row["time"]))
            assert actual == row["result"], row
        elif kind == "telemedicineStream":
            person = _FakePerson(row["seed"])
            actual = [
                Telemedicine.should_encounter_be_virtual(person, 1609459200000)
                for _ in row["results"]
            ]
            assert actual == row["results"], row
        else:  # pragma: no cover - probe added a kind this test does not know
            pytest.fail(f"unexpected utilities.jsonl kind: {kind}")
    # Acceptance criterion 1: >= 1000 inputs per ported method where applicable.
    assert counts["ctLong"] >= 1000
    assert counts["ctDouble"] >= 1000
    assert counts["calYears"] >= 1000
    assert counts["yearMonth"] >= 1000
    assert counts["compare"] >= 1000
    assert counts["parseRange"] >= 1000
    assert counts["telemedicine"] >= 1000
    assert counts["strToObject"] >= 1000


def _capacity_result(capacity: int) -> str:
    ts = TimeSeriesData(capacity, 1.25)
    return f"{len(ts.get_values())}:{double_to_string(ts.get_period())}"


def _check_primitive(row: dict[str, Any]) -> None:
    input_kind = row["inputKind"]
    raw = row["value"]
    if row["resultClass"] == "ERR":
        expected_err = row["result"].removeprefix("ERR:")
        with pytest.raises(_ERR_TYPES[expected_err]):
            Utilities.primitive(None)
        return
    value: Any
    if input_kind == "bool":
        value = raw == "true"
    elif input_kind in ("string", "char"):
        value = raw
    elif input_kind == "double":
        value = parse_double(raw)
    elif input_kind == "float":
        value = struct.unpack("f", struct.pack("f", parse_double(raw)))[0]
    elif input_kind in ("int", "long"):
        value = int(raw)
    else:  # pragma: no cover
        pytest.fail(f"unknown primitive inputKind {input_kind}")
    result = Utilities.primitive(value)
    result_class = row["resultClass"]
    if result_class == "Boolean":
        assert result is (row["result"] == "true"), row
    elif result_class == "Integer":
        assert isinstance(result, int) and not isinstance(result, bool), row
        assert result == int(row["result"]), row
    elif result_class == "Double":
        assert isinstance(result, float), row
        # Double.toString comparison: exact for NaN and -0.0, where == is not.
        assert double_to_string(result) == row["result"], row
    elif result_class == "String":
        assert result == row["result"], row
    elif result_class == "null":
        assert result is None, row
    else:  # pragma: no cover
        pytest.fail(f"unknown resultClass {result_class}")


def _typed_value(spec: dict[str, Any]) -> Any:
    t = spec["t"]
    v = spec["v"]
    if t == "null" or v is None:
        return None
    if t == "double":
        return parse_double(v)
    if t in ("int", "long"):
        return int(v)
    if t == "bool":
        return v == "true"
    if t == "string":
        return v
    if t == "code":
        system, code, display = v.split("|", 2)
        # HealthRecord.Code is a T08 stub; Utilities.compare only reads
        # system/code (Code.equals), so a namespace with the same fields
        # exercises it faithfully.
        return SimpleNamespace(system=system, code=code, display=display)
    raise AssertionError(t)  # pragma: no cover


def _check_compare(row: dict[str, Any]) -> None:
    lhs = _typed_value(row["lhs"])
    rhs = _typed_value(row["rhs"])
    actual = _result_or_error(
        lambda: Utilities.compare(lhs, rhs, row["op"]), lambda v: str(v).lower()
    )
    assert actual == row["result"], row


def _check_parse_range(row: dict[str, Any]) -> None:
    if "result" in row:
        expected_err = row["result"].removeprefix("ERR:")
        with pytest.raises(_ERR_TYPES[expected_err]):
            Utilities.parse_date_range(row["input"])
        return
    result = Utilities.parse_date_range(row["input"])
    assert str(result.minimum) == row["min"], row
    assert str(result.maximum) == row["max"], row


def _utf16_length(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def _check_resource(row: dict[str, Any], gdir: Path, freefile: Path) -> None:
    mode = row["mode"]
    name = row["name"]
    # Rows for the free file carry the generation machine's absolute path;
    # rebuild it inside this checkout's golden directory.
    if mode in ("orPath", "freeStrip", "freeNoStrip", "classpathOnlyFree"):
        name = str(freefile)
    elif mode == "orPathMissing":
        name = str(freefile) + ".missing"

    def call() -> str:
        if mode == "plain":
            return Utilities.read_resource(name)
        if mode == "stripBOM":
            return Utilities.read_resource_and_strip_bom(name)
        if mode == "orPath" or mode == "orPathMissing":
            return Utilities.read_resource_or_path(name)
        if mode == "freeStrip":
            return Utilities.read_resource(name, True, True)
        if mode == "freeNoStrip":
            return Utilities.read_resource(name, False, True)
        if mode == "classpathOnlyFree":
            return Utilities.read_resource(name)
        raise AssertionError(mode)  # pragma: no cover

    if "result" in row:
        expected_err = row["result"].removeprefix("ERR:")
        # Java's NoSuchFileException (an IOException) for a missing free
        # path is mirrored by Python's FileNotFoundError, an OSError.
        if expected_err in ("NoSuchFileException", "FileNotFoundException"):
            with pytest.raises(OSError):
                call()
            return
        with pytest.raises(_ERR_TYPES[expected_err]):
            call()
        return
    try:
        content = call()
    except ValueError:
        # version.txt is written into the resources tree by the Java build
        # (gitignored), so a golden generated by CI can hold content the
        # Python checkout legitimately does not have.
        assert row["name"] == "version.txt", row
        return
    assert _utf16_length(content) == row["length"], row
    assert hashlib.sha256(content.encode("utf-8")).hexdigest() == row["sha256"], row
    if "content" in row:
        assert content == row["content"], row


_CLASS_SIMPLE = {
    "boolean": "Boolean",
    "byte": "Byte",
    "short": "Short",
    "int": "Integer",
    "long": "Long",
    "float": "Float",
    "double": "Double",
}


def _check_str_to_object(row: dict[str, Any]) -> None:
    clazz = row["clazz"]
    if row["result"].startswith("ERR:"):
        expected_err = row["result"].removeprefix("ERR:")
        with pytest.raises(_ERR_TYPES[expected_err]):
            Utilities.str_to_object(clazz, row["value"])
        return
    result = Utilities.str_to_object(clazz, row["value"])
    simple = _CLASS_SIMPLE.get(clazz, clazz)
    if simple == "Boolean":
        actual = f"Boolean:{str(result).lower()}"
    elif simple == "Float":
        actual = f"Float:{float_to_string(float(result))}"  # type: ignore[arg-type]
    elif simple == "Double":
        actual = f"Double:{double_to_string(float(result))}"  # type: ignore[arg-type]
    else:
        actual = f"{simple}:{result}"
    assert actual == row["result"], row
