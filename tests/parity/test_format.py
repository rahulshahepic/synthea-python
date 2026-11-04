"""Parity tests for javacompat numerics (T03) against JavaFormatProbe goldens.

Streams ``format.jsonl``, reconstructs each input exactly (doubles/floats from
their raw bit patterns, which travel as strings), calls the Python port, and
asserts exact equality with the JDK-produced result, line by line.
"""

from __future__ import annotations

import json
import struct
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from synthea.javacompat import bigdecimal as bd
from synthea.javacompat.fmt import format
from synthea.javacompat.numbers import (
    d2i,
    d2l,
    double_to_string,
    float_to_string,
    math_round,
    math_round_float,
    parse_double,
    parse_int,
    parse_long,
)


def _double(bits: str) -> float:
    return struct.unpack("d", struct.pack("q", int(bits)))[0]


def _float(fbits: str) -> float:
    return struct.unpack("f", struct.pack("i", int(fbits)))[0]


def _bits_of(x: float) -> int:
    return struct.unpack("q", struct.pack("d", x))[0]


def _arg(spec: dict[str, Any]) -> object:
    kind = spec["t"]
    if kind == "double":
        return _double(spec["bits"])
    if kind in ("int", "long"):
        return int(spec["v"])
    if kind == "string":
        return spec["v"]
    if kind == "null":
        return None
    if kind == "bool":
        return spec["v"] == "true"
    raise AssertionError(f"unknown arg type {kind}")


def _check_bigdecimal(line: dict[str, Any], actual: bd.Decimal) -> None:
    assert bd.to_string(actual) == line["ts"], line
    assert bd.to_plain_string(actual) == line["ps"], line


@pytest.mark.parity
def test_format_probe(golden: Callable[[str], Path]) -> None:
    path = golden("JavaFormatProbe") / "format.jsonl"
    double_lines = 0
    with path.open(encoding="utf-8") as fh:
        for raw in fh:
            line = json.loads(raw)
            op = line["op"]
            if op == "doubleToString":
                double_lines += 1
                assert double_to_string(_double(line["bits"])) == line["v"], line
            elif op == "floatToString":
                assert float_to_string(_float(line["fbits"])) == line["v"], line
            elif op == "format":
                args = [_arg(a) for a in line["args"]]
                assert format(line["pattern"], *args) == line["v"], line
            elif op == "mathRound":
                assert math_round(_double(line["bits"])) == int(line["v"]), line
            elif op == "mathRoundFloat":
                assert math_round_float(_float(line["fbits"])) == int(line["v"]), line
            elif op == "d2i":
                assert d2i(_double(line["bits"])) == int(line["v"]), line
            elif op == "d2l":
                assert d2l(_double(line["bits"])) == int(line["v"]), line
            elif op == "parseDouble":
                if line["v"] == "ERROR":
                    with pytest.raises(ValueError):
                        parse_double(line["s"])
                else:
                    assert _bits_of(parse_double(line["s"])) == int(line["v"]), line
            elif op == "parseInt":
                if line["v"] == "ERROR":
                    with pytest.raises(ValueError):
                        parse_int(line["s"])
                else:
                    assert parse_int(line["s"]) == int(line["v"]), line
            elif op == "parseLong":
                if line["v"] == "ERROR":
                    with pytest.raises(ValueError):
                        parse_long(line["s"])
                else:
                    assert parse_long(line["s"]) == int(line["v"]), line
            elif op == "bdValueOf":
                _check_bigdecimal(line, bd.value_of(_double(line["bits"])))
            elif op == "bdExactDouble":
                _check_bigdecimal(line, bd.from_double_exact(_double(line["bits"])))
            elif op == "bdFromString":
                _check_bigdecimal(line, bd.from_string(line["a"]))
            elif op == "bdAdd":
                _check_bigdecimal(
                    line, bd.add(bd.from_string(line["a"]), bd.from_string(line["b"]))
                )
            elif op == "bdSubtract":
                _check_bigdecimal(
                    line, bd.subtract(bd.from_string(line["a"]), bd.from_string(line["b"]))
                )
            elif op == "bdMultiply":
                _check_bigdecimal(
                    line, bd.multiply(bd.from_string(line["a"]), bd.from_string(line["b"]))
                )
            elif op == "bdDivide":
                result = bd.divide(
                    bd.from_string(line["a"]),
                    bd.from_string(line["b"]),
                    line["scale"],
                    bd.RoundingMode[line["mode"]],
                )
                _check_bigdecimal(line, result)
            elif op == "bdSetScale":
                if line["ts"] == "ERROR":
                    with pytest.raises(ValueError):
                        bd.set_scale(
                            bd.from_string(line["a"]),
                            line["scale"],
                            bd.RoundingMode[line["mode"]],
                        )
                else:
                    result = bd.set_scale(
                        bd.from_string(line["a"]),
                        line["scale"],
                        bd.RoundingMode[line["mode"]],
                    )
                    _check_bigdecimal(line, result)
            elif op == "bdCompareTo":
                actual = bd.compare_to(bd.from_string(line["a"]), bd.from_string(line["b"]))
                assert actual == int(line["v"]), line
            else:
                raise AssertionError(f"unknown op {op}")
    assert double_lines >= 20000, f"double corpus too small: {double_lines}"
