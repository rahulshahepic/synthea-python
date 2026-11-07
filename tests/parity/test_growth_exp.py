"""Exact Math.exp parity, including native libm and StrictMath rounding differences."""

import json
import math
import struct
from collections.abc import Callable
from pathlib import Path

import pytest

from synthea.world.concepts.growth_chart_entry import _java_exp


@pytest.mark.parity
def test_growth_exp_matches_actual_jdk(golden: Callable[[str], Path]) -> None:
    """Java: Math#exp; all bits must match, with only NaN payload canonicalization."""
    rows = (golden("GrowthExpProbe") / "exp.jsonl").read_text().splitlines()
    assert len(rows) == 30015
    for i, line in enumerate(rows):
        row = json.loads(line)
        x = struct.unpack(">d", int(row["x"], 16).to_bytes(8, "big"))[0]
        actual = _java_exp(x)
        bits = (
            0x7FF8000000000000
            if math.isnan(actual)
            else struct.unpack(">Q", struct.pack(">d", actual))[0]
        )
        assert bits == int(row["math"], 16), (
            f"row={i}, x={x.hex()}, actual={actual.hex()}, "
            f"Math={row['math']}, StrictMath={row['strict']}"
        )
